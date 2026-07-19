# jsslint-wasm

A browser / Node.js WASM build of the
[JSS style checker](https://github.com/kollerma/jss-style-checker) — a linter
for LaTeX / Sweave / R Markdown manuscripts
(`.tex`/`.ltx`/`.Rnw`/`.Rmd` + `.bib`) submitted to the
[Journal of Statistical Software](https://www.jstatsoft.org/) (JSS).

It runs **entirely client-side**: no network access is linked into this
package at all (not even behind a flag), so manuscripts never leave the
machine — by construction. This is the engine behind the
[in-browser checker](https://kollerma.github.io/jss-style-checker/) and the
project's VS Code extension.

## Install

```sh
npm install jsslint-wasm
```

## Usage

Three exports, all taking the same request object (camelCase keys) and
throwing on a malformed request or unparseable input:

```js
import { render, fix, analyze } from "jsslint-wasm";

// Lint and render a report string:
const report = render({
  files: [["paper.tex", texSource], ["refs.bib", bibSource]],
  output: "json",           // "terminal" | "json" | "sarif" | "html"
  mode: "reviewer",         // "author" | "reviewer"
  ignoreRules: "JSS-SRC-001,JSS-MARKUP-001",
  minConfidence: "medium",  // "low" | "medium" | "high"
  failOn: "error",          // "error" | "warning" | "info"
});

// Apply every safe auto-fix in memory; returns [path, fixedContents]
// pairs for the files that changed (`output` is ignored):
const changed = fix({ files: [["paper.tex", texSource]] });

// Structured violations, each with its fix payload when one exists
// ({start, end, replacement, description} character offsets) — what the
// VS Code extension's per-diagnostic quick fixes are built on:
const violations = analyze({ files: [["paper.tex", texSource]] });
```

`files` is an array of `[path, contents]` pairs; every field except `files`
is optional. There is no `.jss-lint.toml` filesystem lookup on this target
(no real filesystem in WASM) — pass any overrides explicitly. Note that
`render(output: "json")` reports `fix: null` per violation by design (byte
parity with the Python JSON contract) — use `analyze()` when you need the
fix payloads.

The package is built with `wasm-pack`; the default export targets bundlers
(webpack/vite/rollup) and needs no manual init step. See
[`rust/README.md`](https://github.com/kollerma/jss-style-checker/blob/main/rust/README.md)
for the Node (`--target nodejs`) variant and build instructions, and the
[project README](https://github.com/kollerma/jss-style-checker) for the full
rule catalogue.

## License

MIT.
