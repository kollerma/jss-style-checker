# Data Model: VS Code Extension

**Phase**: 1
**Spec**: [spec.md](spec.md)
**Plan**: [plan.md](plan.md)

## 1. Settings

The five settings under the `jssStyleChecker` namespace, with
`package.json` `contributes.configuration` shapes:

| Setting                        | Type                                | Default     | Semantics                                                  |
| ------------------------------ | ----------------------------------- | ----------- | ---------------------------------------------------------- |
| `jssStyleChecker.python.path`  | `string`                            | `""`        | Override Python interpreter; empty falls back to discovery (research §2). |
| `jssStyleChecker.severityOverrides` | `object<string, "error"|"warning"|"info">` | `{}`  | Per-rule severity override.                                |
| `jssStyleChecker.ignoreRules`  | `string[]`                          | `[]`        | Rule ids to suppress.                                      |
| `jssStyleChecker.codeWidth`    | `number`                            | `80`        | Maximum line width for `JSS-WIDTH-001`.                    |
| `jssStyleChecker.runOn`        | `"save" \| "change"`                | `"change"`  | When to re-lint.                                           |

Settings are propagated to the LSP server via
`workspace/didChangeConfiguration`. The server (spec 011)
applies them as in-memory config overrides.

## 2. Commands

Two commands registered under the `jss-lint` palette
prefix:

| Command id                | Title                            | Behaviour                                                            |
| ------------------------- | -------------------------------- | -------------------------------------------------------------------- |
| `jss-lint.runInit`        | `jss-lint: Run init`             | Spawns `<python> -m texlint.cli init` in the workspace folder.       |
| `jss-lint.applyAllFixes`  | `jss-lint: Apply all fixes`      | Sends `workspace/executeCommand` with `jss-lint.applyAllFixes`.      |

The `runInit` command spawns a child process; the
`applyAllFixes` command goes through the LSP client.

## 3. Status-bar item

```ts
const statusBar = vscode.window.createStatusBarItem(
  vscode.StatusBarAlignment.Right, 100
);
statusBar.command = 'workbench.actions.view.problems';
statusBar.text = `jss-lint: ${count}`;
statusBar.show();
```

Updated on `vscode.languages.onDidChangeDiagnostics` for the
active editor only.

## 4. LanguageClient configuration

```ts
const serverOptions: ServerOptions = {
  command: pythonPath,
  args: ['-m', 'texlint.cli', 'lsp'],
  transport: TransportKind.stdio,
};

const clientOptions: LanguageClientOptions = {
  documentSelector: [
    { scheme: 'file', language: 'latex' },
    { scheme: 'file', language: 'tex' },
    { scheme: 'file', language: 'rnoweb' },
    { scheme: 'file', language: 'rmd' },
  ],
  synchronize: {
    fileEvents: vscode.workspace.createFileSystemWatcher('**/.jss-lint.toml'),
    configurationSection: 'jssStyleChecker',
  },
};
```

The `synchronize.configurationSection` glue is what makes
LSP `workspace/configuration` carry our five settings.

## 5. Activation events

```json
"activationEvents": [
  "onLanguage:latex",
  "onLanguage:tex",
  "onLanguage:rnoweb",
  "onLanguage:rmd",
  "onCommand:jss-lint.runInit",
  "onCommand:jss-lint.applyAllFixes"
]
```

The extension does NOT activate on `*` startup; it activates
only when a supported file is opened or one of its commands
is invoked.

## 6. Extension package

| `package.json` field          | Value                                                  |
| ----------------------------- | ------------------------------------------------------ |
| `name`                        | `jss-style-checker`                                    |
| `publisher`                   | `kollerma`                                             |
| `version`                     | bumped manually in PRs that touch the extension        |
| `engines.vscode`              | `^1.85.0`                                              |
| `categories`                  | `["Linters"]`                                          |
| `activationEvents`            | (per §5)                                               |
| `contributes.configuration`   | (per §1)                                               |
| `contributes.commands`        | (per §2)                                               |
| `repository`                  | `https://github.com/kollerma/jss-style-checker`         |
| `bugs`                        | `https://github.com/kollerma/jss-style-checker/issues`  |

## 7. CI workflow

```yaml
# .github/workflows/vscode-publish.yml
name: vscode-publish
on:
  push:
    tags:
      - 'v*-vscode'
jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: npm ci --prefix vscode-extension
      - run: npm run build --prefix vscode-extension
      - run: npx vsce publish --packagePath jss-style-checker.vsix
        env: { VSCE_PAT: '${{ secrets.VSCE_PAT }}' }
      - run: npx ovsx publish jss-style-checker.vsix
        env: { OVSX_PAT: '${{ secrets.OVSX_PAT }}' }
```

The two `PAT` secrets are configured in repo settings;
without them, the workflow exits with a clear error.

## 8. Out of scope

| Item                                            | Reason                                                                  |
| ----------------------------------------------- | ----------------------------------------------------------------------- |
| Bundled Python                                  | Out per Clarifications §2.                                              |
| Overleaf integration                            | Out per Clarifications §3.                                              |
| Custom UI panel beyond status-bar item          | Out — status bar + Problems pane suffice.                               |
| Per-rule fix-on-save                            | Out — `runOn: save` covers it via the existing apply-all command.       |
| Telemetry                                       | Out — extension is privacy-preserving by default.                       |
