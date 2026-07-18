// VS Code extension entry point.
//
// The extension activates on .tex/.ltx/.Rnw/.Rmd files and spawns the
// standalone Rust language server (`jsslint lsp`). No Python is involved.
// The actual LSP wire is handled by `vscode-languageclient`; this module is
// the thin orchestration layer.

import * as cp from "child_process";
import {
  workspace,
  window,
  commands,
  ExtensionContext,
  StatusBarItem,
  StatusBarAlignment,
  Diagnostic,
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

const INSTALL_HINT =
  "Install it with `cargo install jsslint-cli`, or download the `jsslint` " +
  "binary from the project's GitHub releases and set " +
  '"jssStyleChecker.serverPath" to its location.';

function canRunServer(binary: string): Promise<boolean> {
  // A candidate qualifies iff it runs and reports a version — cheap and
  // side-effect-free, unlike actually starting the `lsp` server.
  return new Promise((resolve) => {
    cp.execFile(binary, ["--version"], (err) => resolve(!err));
  });
}

async function resolveServer(): Promise<string | undefined> {
  //   1. `jssStyleChecker.serverPath` — explicit; a broken value surfaces an
  //      error instead of being silently replaced by a fallback.
  //   2. `jsslint` on PATH.
  const configured = workspace
    .getConfiguration("jssStyleChecker")
    .get<string>("serverPath");
  if (configured) {
    if (await canRunServer(configured)) {
      return configured;
    }
    window.showErrorMessage(
      `JSS Style Checker: "jssStyleChecker.serverPath" (${configured}) is not ` +
        `a runnable jsslint binary. ${INSTALL_HINT}`
    );
    return undefined;
  }

  if (await canRunServer("jsslint")) {
    return "jsslint";
  }
  window.showErrorMessage(
    `JSS Style Checker: the \`jsslint\` binary was not found on PATH. ${INSTALL_HINT}`
  );
  return undefined;
}

export async function activate(context: ExtensionContext): Promise<void> {
  const server = await resolveServer();
  if (!server) {
    // No usable binary — the error message above tells the user how to fix
    // it; starting a doomed client would only add noise.
    return;
  }

  const serverOptions: ServerOptions = {
    command: server,
    args: ["lsp"],
    transport: TransportKind.stdio,
  };

  const clientOptions: LanguageClientOptions = {
    documentSelector: [
      { scheme: "file", language: "latex" },
      { scheme: "file", language: "tex" },
      { scheme: "file", language: "rnoweb" },
      { scheme: "file", language: "rmd" },
      // Pattern fallback: bind by filename so the LSP still lints when no
      // sibling LaTeX language pack is installed (the file resolves as
      // `plaintext`, but the extension still activates and diagnostics flow).
      { scheme: "file", pattern: "**/*.{tex,ltx,Rnw,rnw,Rmd,rmd,bib}" },
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
      `JSS Style Checker: failed to start the jsslint LSP server (${err}). ` +
        INSTALL_HINT
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

  // Commands. Only register ids the LSP server does NOT declare in its
  // `executeCommandProvider.commands` capability — vscode-languageclient
  // auto-registers a VS Code command for each of those, and registering them
  // again here would throw "command X already exists", crashing LSP startup.
  //
  // Server-side (auto-registered by vscode-languageclient):
  //   - jss-lint.applyAllFixes
  // Client-side (must register here):
  //   - jss-lint.runInit
  context.subscriptions.push(
    commands.registerCommand("jss-lint.runInit", async () => {
      const folder = workspace.workspaceFolders?.[0];
      if (!folder) {
        window.showWarningMessage("jss-lint: no workspace folder open.");
        return;
      }
      const cwd = folder.uri.fsPath;
      cp.execFile(server, ["init"], { cwd }, (err, _stdout, stderr) => {
        if (err) {
          window.showErrorMessage(`jss-lint init failed: ${stderr || err.message}`);
          return;
        }
        window.showInformationMessage("jss-lint: wrote .jss-lint.toml");
      });
    })
  );
}

export function deactivate(): Thenable<void> | undefined {
  return client?.stop();
}
