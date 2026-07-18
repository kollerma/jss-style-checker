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
  OutputChannel,
  CodeAction,
  CodeActionKind,
  CodeActionContext,
} from "vscode";

interface WasmFix {
  start: number;
  end: number;
  replacement: string;
  description: string;
}

interface WasmViolation {
  ruleId: string;
  severity: "error" | "warning" | "info";
  message: string;
  line: number; // 1-based
  column: number | null; // 1-based, or null for line-granularity rules
  fix?: WasmFix;
}

interface WasmModule {
  render(request: unknown): string;
  fix(request: unknown): Array<[string, string]>;
  analyze(request: unknown): WasmViolation[];
}

let wasm: WasmModule | undefined;
let diagnostics: DiagnosticCollection;
let statusBar: StatusBarItem;
let output: OutputChannel | undefined;
const debounce = new Map<string, NodeJS.Timeout>();
// Per document (uri string): the fix for each fixable diagnostic, keyed by
// `${line}:${character}:${ruleId}` of its diagnostic range start.
const fixIndex = new Map<string, Map<string, WasmFix>>();

const SUPPORTED = /\.(tex|ltx|Rnw|rnw|Rmd|rmd|bib)$/i;

function log(message: string): void {
  output?.appendLine(message);
}

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
  let violations: WasmViolation[];
  try {
    violations = wasm.analyze(requestFor(doc));
  } catch (err) {
    // Unparseable source (e.g. mid-edit) — clear stale diagnostics, wait.
    log(`analyze failed for ${doc.fileName}: ${err}`);
    diagnostics.delete(doc.uri);
    fixIndex.delete(doc.uri.toString());
    return;
  }

  const diags: Diagnostic[] = [];
  const fixes = new Map<string, WasmFix>();
  for (const v of violations) {
    const line = Math.max(0, v.line - 1);
    if (line >= doc.lineCount) continue;
    const lineText = doc.lineAt(line);
    const col =
      v.column != null
        ? Math.min(Math.max(0, v.column - 1), lineText.text.length)
        : 0;
    const range = new Range(new Position(line, col), lineText.range.end);
    const d = new Diagnostic(range, v.message, severityFor(v.severity));
    d.source = "jss-lint";
    d.code = v.ruleId;
    diags.push(d);
    if (v.fix) fixes.set(`${line}:${col}:${v.ruleId}`, v.fix);
  }
  diagnostics.set(doc.uri, diags);
  fixIndex.set(doc.uri.toString(), fixes);
  log(
    `linted ${path.basename(doc.fileName)}: ${diags.length} diagnostic(s), ` +
      `${fixes.size} auto-fixable`
  );
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

function provideCodeActions(
  doc: TextDocument,
  _range: Range,
  context: CodeActionContext
): CodeAction[] {
  const fixes = fixIndex.get(doc.uri.toString());
  const actions: CodeAction[] = [];
  let anyOurs = false;
  for (const d of context.diagnostics) {
    if (d.source !== "jss-lint") continue;
    anyOurs = true;
    const fix = fixes?.get(`${d.range.start.line}:${d.range.start.character}:${d.code}`);
    if (!fix) continue;
    const action = new CodeAction(fix.description, CodeActionKind.QuickFix);
    action.edit = new WorkspaceEdit();
    action.edit.replace(
      doc.uri,
      new Range(doc.positionAt(fix.start), doc.positionAt(fix.end)),
      fix.replacement
    );
    action.diagnostics = [d];
    action.isPreferred = true;
    actions.push(action);
  }
  // Offer a whole-file fix whenever any of our diagnostics are present.
  if (anyOurs) {
    const all = new CodeAction(
      "Fix all JSS style issues in this file",
      CodeActionKind.QuickFix
    );
    all.command = {
      command: "jss-lint.applyAllFixes",
      title: "Fix all JSS style issues",
    };
    actions.push(all);
  }
  return actions;
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
  output = window.createOutputChannel("JSS Style Checker");
  context.subscriptions.push(output);
  log("JSS Style Checker activating…");

  wasm = loadWasm(context);
  if (!wasm) {
    log("WASM engine failed to load — see the error notification.");
    return;
  }
  log("WASM engine loaded.");

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
    languages.registerCodeActionsProvider(
      { scheme: "file", pattern: "**/*.{tex,ltx,Rnw,rnw,Rmd,rmd,bib}" },
      { provideCodeActions },
      { providedCodeActionKinds: [CodeActionKind.QuickFix] }
    ),
    commands.registerCommand("jss-lint.applyAllFixes", applyAllFixes),
    commands.registerCommand("jss-lint.runInit", runInit)
  );

  // Lint whatever is already open.
  const open = workspace.textDocuments.filter((d) => SUPPORTED.test(d.fileName));
  log(`activated; ${open.length} supported document(s) already open.`);
  open.forEach((doc) => lint(doc));
  refreshStatus();
}

export function deactivate(): void {
  for (const t of debounce.values()) clearTimeout(t);
  debounce.clear();
  fixIndex.clear();
  diagnostics?.dispose();
}
