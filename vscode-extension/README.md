# JSS Style Checker — VS Code Extension

Lint LaTeX / Sweave / R Markdown manuscripts against the JSS style
guide directly inside VS Code, as you type.

The extension runs the JSS style checker's language server — the standalone
Rust `jsslint` binary. No Python required. It uses `jsslint` on your PATH, or
you can point it at a specific binary with `jssStyleChecker.serverPath`.

## Install

```sh
cargo install jsslint-cli          # provides the `jsslint` binary
code --install-extension kollerma.jss-style-checker
```

Alternatively, download a prebuilt `jsslint` binary from the project's
[GitHub releases](https://github.com/kollerma/jss-style-checker/releases) and
set `jssStyleChecker.serverPath` to its path.

## Settings

| Setting                                | Default      | Description                                                |
| -------------------------------------- | ------------ | ---------------------------------------------------------- |
| `jssStyleChecker.serverPath`           | `""`         | Path to the `jsslint` binary (default: `jsslint` on PATH).  |
| `jssStyleChecker.severityOverrides`    | `{}`         | Per-rule severity override map.                             |
| `jssStyleChecker.ignoreRules`          | `[]`         | Rule ids to suppress.                                       |
| `jssStyleChecker.codeWidth`            | `80`         | Max line width for `JSS-WIDTH-001`.                         |
| `jssStyleChecker.runOn`                | `"change"`   | When to re-lint: `"save"` or `"change"`.                    |

## Commands

- **jss-lint: Run init** — generate `.jss-lint.toml` for the
  workspace folder.
- **jss-lint: Apply all fixes** — apply every safe-confidence
  auto-fix across open buffers.

## Develop

```sh
cd vscode-extension
npm install
npm run watch    # incremental TS build
```

In a separate VS Code window, press `F5` to launch the Extension
Development Host.

## License

MIT.
