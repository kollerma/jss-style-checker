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
  extensions,
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

function canRunServer(python: string): Promise<boolean> {
  // A candidate interpreter qualifies iff it exists AND has the
  // texlint package (`pip install "jss-lint[lsp]"`).
  return new Promise((resolve) => {
    cp.execFile(python, ["-c", "import texlint"], (err) => resolve(!err));
  });
}

async function resolvePython(): Promise<string | undefined> {
  // Four-layer discovery (research §2):
  //   1. `jssStyleChecker.python.path` setting — explicit, validated;
  //      a broken value surfaces an error instead of being silently
  //      replaced by a fallback the user did not choose.
  //   2. The VS Code Python extension's selected interpreter.
  //   3. `python3` on PATH (modern macOS / most Linux distros ship no
  //      bare `python`).
  //   4. `python` on PATH.
  const setting = workspace
    .getConfiguration("jssStyleChecker")
    .get<string>("python.path");
  if (setting) {
    if (await canRunServer(setting)) {
      return setting;
    }
    window.showErrorMessage(
      `JSS Style Checker: "jssStyleChecker.python.path" (${setting}) ` +
        `is not a Python interpreter with jss-lint installed. ` +
        `Install with: ${setting} -m pip install "jss-lint[lsp]"`
    );
    return undefined;
  }

  const candidates: string[] = [];
  const pythonExt = extensions.getExtension("ms-python.python");
  if (pythonExt) {
    try {
      const api = await pythonExt.activate();
      // Modern environments API (2023+), then the legacy settings API.
      const active = api?.environments?.getActiveEnvironmentPath?.();
      if (active?.path) {
        candidates.push(active.path);
      }
      const exec = api?.settings?.getExecutionDetails?.()?.execCommand;
      if (Array.isArray(exec) && exec.length > 0) {
        candidates.push(exec[0]);
      }
    } catch {
      // Python extension misbehaving — fall through to PATH probing.
    }
  }
  candidates.push("python3", "python");

  for (const candidate of candidates) {
    if (await canRunServer(candidate)) {
      return candidate;
    }
  }
  window.showErrorMessage(
    'JSS Style Checker: no Python interpreter with jss-lint found ' +
      `(tried: ${candidates.join(", ")}). Install the server with ` +
      '`pip install "jss-lint[lsp]"` or point ' +
      '"jssStyleChecker.python.path" at the right interpreter.'
  );
  return undefined;
}

export async function activate(context: ExtensionContext): Promise<void> {
  const pythonPath = await resolvePython();
  if (!pythonPath) {
    // No usable interpreter — the error message above tells the user
    // how to fix it; starting a doomed client would only add noise.
    return;
  }

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
      // Pattern fallback: bind by filename so the LSP still lints
      // when no sibling LaTeX language pack is installed (the file
      // resolves as `plaintext`, but the extension still activates
      // and diagnostics flow). Spec 012 v1 originally relied on
      // LaTeX Workshop registering the `rnoweb` / `latex` ids; this
      // pattern entry makes the extension self-sufficient.
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

  // Commands. Only register ids the LSP server does NOT declare in
  // its `executeCommandProvider.commands` capability — vscode-
  // languageclient auto-registers a VS Code command for each of
  // those, and registering them again here would throw "command X
  // already exists", crashing the LSP startup.
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
    })
  );
}

export function deactivate(): Thenable<void> | undefined {
  return client?.stop();
}
