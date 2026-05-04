// Spec 012 — VS Code extension entry point.
//
// The extension activates on .tex/.ltx/.Rnw/.Rmd files and spawns the
// spec-011 LSP server (`<python> -m texlint.cli lsp`) using the user's
// configured Python interpreter. The actual LSP wire is handled by
// `vscode-languageclient`; this module is the thin orchestration layer.

import * as path from "path";
import * as cp from "child_process";
import {
  workspace,
  window,
  commands,
  ExtensionContext,
  StatusBarItem,
  StatusBarAlignment,
  Diagnostic,
  Uri,
  languages,
} from "vscode";
import {
  LanguageClient,
  LanguageClientOptions,
  ServerOptions,
  TransportKind,
} from "vscode-languageclient/node";

let client: LanguageClient | undefined;
let statusBar: StatusBarItem;

function discoverPythonPath(): string {
  // Three-layer discovery (research §2):
  //   1. `jssStyleChecker.python.path` setting.
  //   2. The VS Code Python extension's selected interpreter.
  //   3. `python` on PATH.
  const setting = workspace
    .getConfiguration("jssStyleChecker")
    .get<string>("python.path");
  if (setting) {
    return setting;
  }
  // (2) requires a runtime probe via the Python extension API; we keep
  // it simple in v1 and fall through to (3).
  return "python";
}

export function activate(context: ExtensionContext): void {
  const pythonPath = discoverPythonPath();

  const serverOptions: ServerOptions = {
    command: pythonPath,
    args: ["-m", "texlint.cli", "lsp"],
    transport: TransportKind.stdio,
  };

  const clientOptions: LanguageClientOptions = {
    documentSelector: [
      { scheme: "file", language: "latex" },
      { scheme: "file", language: "tex" },
      { scheme: "file", language: "rnoweb" },
      { scheme: "file", language: "rmd" },
    ],
    synchronize: {
      configurationSection: "jssStyleChecker",
      fileEvents: workspace.createFileSystemWatcher("**/.jss-lint.toml"),
    },
  };

  client = new LanguageClient(
    "jssStyleChecker",
    "JSS Style Checker",
    serverOptions,
    clientOptions
  );
  client.start().catch((err) => {
    window.showErrorMessage(
      `JSS Style Checker: failed to start LSP server (${err}). ` +
        `Verify the Python interpreter has jss-lint[lsp] installed.`
    );
  });

  // Status bar — violation count for the active editor.
  statusBar = window.createStatusBarItem(StatusBarAlignment.Right, 100);
  statusBar.command = "workbench.actions.view.problems";
  statusBar.show();
  context.subscriptions.push(statusBar);

  const refreshStatus = () => {
    const editor = window.activeTextEditor;
    if (!editor) {
      statusBar.text = "jss-lint: -";
      return;
    }
    const diagnostics = languages.getDiagnostics(editor.document.uri);
    const ours = diagnostics.filter((d: Diagnostic) => d.source === "jss-lint");
    statusBar.text = `jss-lint: ${ours.length}`;
  };

  context.subscriptions.push(
    languages.onDidChangeDiagnostics(refreshStatus),
    window.onDidChangeActiveTextEditor(refreshStatus)
  );
  refreshStatus();

  // Commands.
  context.subscriptions.push(
    commands.registerCommand("jss-lint.runInit", async () => {
      const folder = workspace.workspaceFolders?.[0];
      if (!folder) {
        window.showWarningMessage("jss-lint: no workspace folder open.");
        return;
      }
      const cwd = folder.uri.fsPath;
      cp.execFile(
        pythonPath,
        ["-m", "texlint.cli", "init"],
        { cwd },
        (err, stdout, stderr) => {
          if (err) {
            window.showErrorMessage(`jss-lint init failed: ${stderr || err.message}`);
            return;
          }
          window.showInformationMessage("jss-lint: wrote .jss-lint.toml");
        }
      );
    }),
    commands.registerCommand("jss-lint.applyAllFixes", async () => {
      if (!client) {
        return;
      }
      await client.sendRequest("workspace/executeCommand", {
        command: "jss-lint.applyAllFixes",
      });
    })
  );
}

export function deactivate(): Thenable<void> | undefined {
  return client?.stop();
}
