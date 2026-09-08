// Node test for the browser zip reader (spec 027 item E, SC-013).
//
// Run: node web/zip.test.mjs
//
// The reader is the one piece of the Overleaf drop that can be wrong in
// ways a human would not notice — a silently skipped entry looks exactly
// like a clean project. Node ships the same `DecompressionStream` the
// browser does, so the real code path is exercised here rather than
// mocked.

import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { mkdtempSync, readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { test } from "node:test";

import { decompressionSupported, readZip } from "./zip.js";

const SUFFIXES = [".tex", ".ltx", ".bib", ".rnw", ".rmd"];

function isLintablePath(path) {
  const lower = path.toLowerCase();
  if (lower.startsWith("__macosx/") || lower.includes("/__macosx/")) return false;
  if (path.split("/").pop().startsWith("._")) return false;
  return SUFFIXES.some((suffix) => lower.endsWith(suffix));
}

/** An Overleaf-shaped project: sources, a figure, a resource fork. */
function buildProject() {
  const root = mkdtempSync(join(tmpdir(), "jsslint-zip-"));
  const project = join(root, "project");
  mkdirSync(join(project, "sections"), { recursive: true });
  mkdirSync(join(project, "__MACOSX"), { recursive: true });
  writeFileSync(
    join(project, "main.tex"),
    "\\documentclass[article]{jss}\n\\begin{document}\n" +
      "\\input{sections/intro}\n\\end{document}\n"
  );
  writeFileSync(join(project, "sections", "intro.tex"), "\\section{Intro}\n");
  writeFileSync(join(project, "refs.bib"), "@Article{k, year = {2020}}\n");
  writeFileSync(join(project, "figure.png"), Buffer.alloc(2048, 7));
  writeFileSync(join(project, "__MACOSX", "._main.tex"), "resource fork");
  return { root, project };
}

function zipUp(root, name, extraArgs = []) {
  const archive = join(root, name);
  execFileSync("zip", ["-q", "-r", ...extraArgs, archive, "project"], {
    cwd: root,
  });
  const buffer = readFileSync(archive);
  return buffer.buffer.slice(
    buffer.byteOffset,
    buffer.byteOffset + buffer.byteLength
  );
}

test("DecompressionStream is available", () => {
  assert.ok(decompressionSupported());
});

test("reads deflated entries, keeping project paths", async () => {
  const { root } = buildProject();
  const pairs = await readZip(zipUp(root, "deflated.zip"), isLintablePath);
  const paths = pairs.map(([p]) => p).sort();
  // Paths are kept verbatim so `\input{sections/intro}` resolves and the
  // report's headings match the project layout.
  assert.deepEqual(paths, [
    "project/main.tex",
    "project/refs.bib",
    "project/sections/intro.tex",
  ]);
  assert.match(pairs.find(([p]) => p.endsWith("main.tex"))[1], /documentclass/);
});

test("reads stored (uncompressed) entries identically", async () => {
  const { root } = buildProject();
  const deflated = await readZip(zipUp(root, "d.zip"), isLintablePath);
  const stored = await readZip(zipUp(root, "s.zip", ["-0"]), isLintablePath);
  assert.deepEqual(stored.sort(), deflated.sort());
});

test("skips figures and macOS resource forks", async () => {
  const { root } = buildProject();
  const paths = (await readZip(zipUp(root, "p.zip"), isLintablePath)).map(
    ([p]) => p
  );
  assert.ok(!paths.some((p) => p.endsWith(".png")));
  assert.ok(!paths.some((p) => p.includes("__MACOSX")));
  assert.ok(!paths.some((p) => p.split("/").pop().startsWith("._")));
});

test("a truncated archive fails loudly", async () => {
  const { root } = buildProject();
  const truncated = zipUp(root, "t.zip").slice(0, 400);
  await assert.rejects(() => readZip(truncated, isLintablePath), /zip/);
});
