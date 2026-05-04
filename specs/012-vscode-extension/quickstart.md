# Quickstart: VS Code Extension

## For an end user

### Install

Search "JSS Style Checker" in the VS Code Extensions panel,
or run:

```sh
code --install-extension kollerma.jss-style-checker
```

For Cursor / Codium / Theia, install from Open VSX
(automatic in those editors when you search by name).

### Set up Python

The extension needs a Python interpreter that has
`jss-lint[lsp]` installed. The extension auto-discovers (in
order):
1. The VS Code Python extension's selected interpreter.
2. The `jssStyleChecker.python.path` setting.
3. `python` on PATH.

If discovery fails, the extension surfaces a notification
with two buttons:
- **Set Python path** — opens the setting.
- **Install jss-lint** — opens an integrated terminal and
  runs `pip install --user "jss-lint[lsp]"`.

### Use it

Open a `.tex` / `.Rnw` / `.Rmd` file. You should see:
- Inline squiggles under each violation.
- A **jss-lint: N** item in the status bar.
- Quick-fix lightbulbs on rules that have an auto-fix.
- Two commands in the palette: **jss-lint: Run init**,
  **jss-lint: Apply all fixes**.

### Settings

Open VS Code's Settings (`Cmd-,`), search "jss-lint", and
adjust:
- **Python Path** — explicit interpreter override.
- **Severity Overrides** — bump or quiet specific rules.
- **Ignore Rules** — rule ids to silence.
- **Code Width** — line-width threshold.
- **Run On** — `save` or `change` (default).

Settings changes apply immediately; no VS Code reload.

## For a contributor

### Where things live

```text
vscode-extension/
├── package.json                  # extension manifest
├── tsconfig.json
├── esbuild.config.mjs
├── src/
│   ├── extension.ts              # entry point
│   ├── client.ts                 # LanguageClient setup
│   ├── statusBar.ts              # violation count
│   ├── commands.ts               # palette commands
│   └── pythonDiscovery.ts        # interpreter resolution
└── tests/
    ├── extension.test.ts         # smoke tests
    └── fixtures/
```

### Develop locally

```sh
cd vscode-extension
npm install
npm run watch  # incremental TypeScript build
```

In a separate VS Code window, press `F5` to launch the
Extension Development Host. Open a fixture file inside the
host window; squiggles should appear.

### Run the tests

```sh
cd vscode-extension
npm test         # @vscode/test-electron headless run
```

### Package and publish

For a release:

```sh
cd vscode-extension
npx vsce package           # produces jss-style-checker-X.Y.Z.vsix

# manual publish (first release / debugging)
npx vsce publish --packagePath jss-style-checker-X.Y.Z.vsix
npx ovsx publish jss-style-checker-X.Y.Z.vsix
```

For automated release:

```sh
git tag v0.5.0-vscode
git push origin v0.5.0-vscode
# GitHub Actions runs the publish workflow
```

### Common pitfalls

- **Forgetting to bump `version` in `package.json`**: the
  publish workflow uses the manifest version, NOT the git
  tag. The tag is the trigger; the version is the
  manifest. Bump them in lockstep.
- **Importing Node-built-in modules without bundling**:
  `vsce package` includes `node_modules` by default. Use
  esbuild with `bundle: true` to ship one JS file instead.
- **Forgetting the `engines.vscode` constraint**: VS Code
  rejects extensions whose declared engine is newer than
  the running VS Code.
- **Spawning Python with shell injection**: pass arguments
  as an array, never as a concatenated shell string.
- **Activation on `"*"`**: do NOT add the wildcard
  activation event. The narrow `onLanguage:*` events are
  sufficient and avoid noisy activation in unrelated
  workspaces.
