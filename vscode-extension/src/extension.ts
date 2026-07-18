// VS Code extension entry point.
//
// Runs the JSS style checker entirely in-process via its WebAssembly build
// (`jsslint-wasm`, bundled at <extension>/wasm/). No Python, no native
// binary, no language-server subprocess: one universal VSIX for every
// platform. The engine exposes `render` (lint → report) and `fix` (apply
// auto-fixes → changed file contents); this module wires those to VS Code
// diagnostics and commands.

import * as path from "path";
import {
  workspace,
  window,
  commands,
  languages,
  ExtensionContext,
  TextDocument,
  Diagnostic,
  DiagnosticSeverity,
  DiagnosticCollection,
  Range,
  Position,
  StatusBarItem,
  StatusBarAlignment,
  WorkspaceEdit,
  Uri,
} from "vscode";

interface WasmModule {
  render(request: unknown): string;
  fix(request: unknown): Array<[string, string]>;
}

let wasm: WasmModule | undefined;
let diagnostics: DiagnosticCollection;
let statusBar: StatusBarItem;
const debounce = new Map<string, NodeJS.Timeout>();

const SUPPORTED = /\.(tex|ltx|Rnw|rnw|Rmd|rmd|bib)$/i;

function loadWasm(context: ExtensionContext): WasmModule | undefined {
  try {
    // Dynamic require so TypeScript doesn't try to resolve the (build-time
    // generated) module, and so the path is anchored to the install dir.
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    const mod = require(path.join(context.extensionPath, "wasm", "jsslint_wasm.js"));
    return mod as WasmModule;
  } catch (err) {
    window.showErrorMessage(
      `JSS Style Checker: failed to load the bundled engine (${err}). ` +
        "Try reinstalling the extension."
    );
    return undefined;
  }
}

// Build the shared request object from a document + user settings.
function requestFor(doc: TextDocument): Record<string, unknown> {
  const cfg = workspace.getConfiguration("jssStyleChecker");
  return {
    files: [[path.basename(doc.fileName), doc.getText()]],
    ignoreRules: (cfg.get<string[]>("ignoreRules") ?? []).join(","),
    codeWidth: cfg.get<number>("codeWidth"),
    severityOverrides: cfg.get<Record<string, string>>("severityOverrides"),
  };
}

function severityFor(level: string): DiagnosticSeverity {
  if (level === "error") return DiagnosticSeverity.Error;
  if (level === "warning") return DiagnosticSeverity.Warning;
  return DiagnosticSeverity.Information;
}

function lint(doc: TextDocument): void {
  if (!wasm || doc.uri.scheme !== "file" || !SUPPORTED.test(doc.fileName)) {
    return;
  }
  let results: Array<Record<string, any>>;
  try {
    const sarif = JSON.parse(wasm.render({ ...requestFor(doc), output: "sarif" }));
    results = sarif.runs?.[0]?.results ?? [];
  } catch {
    // Unparseable source (e.g. mid-edit) — clear stale diagnostics, wait.
    diagnostics.delete(doc.uri);
    return;
  }

  const diags: Diagnostic[] = [];
  for (const r of results) {
    const region = r.locations?.[0]?.physicalLocation?.region ?? {};
    const line = Math.max(0, (region.startLine ?? 1) - 1);
    if (line >= doc.lineCount) continue;
    const lineText = doc.lineAt(line);
    const col = Math.min(Math.max(0, (region.startColumn ?? 1) - 1), lineText.text.length);
    const range = new Range(new Position(line, col), lineText.range.end);
    const d = new Diagnostic(range, r.message?.text ?? "", severityFor(r.level));
    d.source = "jss-lint";
    d.code = r.ruleId;
    diags.push(d);
  }
  diagnostics.set(doc.uri, diags);
}

function scheduleLint(doc: TextDocument): void {
  const key = doc.uri.toString();
  const existing = debounce.get(key);
  if (existing) clearTimeout(existing);
  debounce.set(
    key,
    setTimeout(() => {
      debounce.delete(key);
      lint(doc);
    }, 250)
  );
}

async function applyAllFixes(): Promise<void> {
  const editor = window.activeTextEditor;
  if (!wasm || !editor) return;
  const doc = editor.document;
  if (!SUPPORTED.test(doc.fileName)) {
    window.showWarningMessage("jss-lint: the active file is not a supported manuscript.");
    return;
  }
  let changed: Array<[string, string]>;
  try {
    changed = wasm.fix(requestFor(doc));
  } catch (err) {
    window.showErrorMessage(`jss-lint: fix failed (${err}).`);
    return;
  }
  if (changed.length === 0) {
    window.showInformationMessage("jss-lint: nothing to fix.");
    return;
  }
  const [, newText] = changed[0];
  const end = doc.lineAt(doc.lineCount - 1).range.end;
  const edit = new WorkspaceEdit();
  edit.replace(doc.uri, new Range(new Position(0, 0), end), newText);
  await workspace.applyEdit(edit);
  window.showInformationMessage("jss-lint: applied auto-fixes.");
  lint(doc);
}

async function runInit(): Promise<void> {
  const folder = workspace.workspaceFolders?.[0];
  if (!folder) {
    window.showWarningMessage("jss-lint: no workspace folder open.");
    return;
  }
  const uri = Uri.joinPath(folder.uri, ".jss-lint.toml");
  const template =
    "# jss-lint configuration. See the project README for all keys.\n" +
    '# min_confidence = "medium"   # low | medium | high\n' +
    '# fail_on = "error"           # error | warning | info\n' +
    "# ignore_rules = []\n" +
    "# [severity_overrides]\n" +
    '# JSS-CAP-003 = "info"\n';
  try {
    await workspace.fs.stat(uri);
    window.showInformationMessage("jss-lint: .jss-lint.toml already exists.");
    return;
  } catch {
    // does not exist — create it
  }
  await workspace.fs.writeFile(uri, Buffer.from(template, "utf8"));
  window.showInformationMessage("jss-lint: wrote .jss-lint.toml");
}

function refreshStatus(): void {
  const editor = window.activeTextEditor;
  if (!editor || !SUPPORTED.test(editor.document.fileName)) {
    statusBar.text = "jss-lint: -";
    return;
  }
  const ours = languages
    .getDiagnostics(editor.document.uri)
    .filter((d: Diagnostic) => d.source === "jss-lint");
  statusBar.text = `jss-lint: ${ours.length}`;
}

export function activate(context: ExtensionContext): void {
  wasm = loadWasm(context);
  if (!wasm) return;

  diagnostics = languages.createDiagnosticCollection("jss-lint");
  context.subscriptions.push(diagnostics);

  statusBar = window.createStatusBarItem(StatusBarAlignment.Right, 100);
  statusBar.command = "workbench.actions.view.problems";
  statusBar.show();
  context.subscriptions.push(statusBar);

  const runOn = () =>
    workspace.getConfiguration("jssStyleChecker").get<string>("runOn", "change");

  context.subscriptions.push(
    workspace.onDidOpenTextDocument((doc) => lint(doc)),
    workspace.onDidChangeTextDocument((e) => {
      if (runOn() === "change") scheduleLint(e.document);
    }),
    workspace.onDidSaveTextDocument((doc) => lint(doc)),
    workspace.onDidCloseTextDocument((doc) => diagnostics.delete(doc.uri)),
    workspace.onDidChangeConfiguration((e) => {
      if (e.affectsConfiguration("jssStyleChecker")) {
        workspace.textDocuments.forEach((doc) => lint(doc));
      }
    }),
    languages.onDidChangeDiagnostics(refreshStatus),
    window.onDidChangeActiveTextEditor(refreshStatus),
    commands.registerCommand("jss-lint.applyAllFixes", applyAllFixes),
    commands.registerCommand("jss-lint.runInit", runInit)
  );

  // Lint whatever is already open.
  workspace.textDocuments.forEach((doc) => lint(doc));
  refreshStatus();
}

export function deactivate(): void {
  for (const t of debounce.values()) clearTimeout(t);
  debounce.clear();
  diagnostics?.dispose();
}
