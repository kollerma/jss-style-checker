# JSS Style Checker — VS Code Extension

Lint LaTeX / Sweave / R Markdown manuscripts against the JSS style
guide directly inside VS Code, as you type.

The checker runs entirely inside the extension via WebAssembly — no Python, no
separate binary, nothing to install. Manuscripts never leave your machine.

## Install

```sh
code --install-extension kollerma.jss-style-checker
```

Or find "JSS Style Checker" in the VS Code Marketplace / Open VSX. That's it —
the engine is bundled.

## Settings

| Setting                                | Default      | Description                                                |
| -------------------------------------- | ------------ | ---------------------------------------------------------- |
| `jssStyleChecker.severityOverrides`    | `{}`         | Per-rule severity override map.                             |
| `jssStyleChecker.ignoreRules`          | `[]`         | Rule ids to suppress.                                       |
| `jssStyleChecker.codeWidth`            | `80`         | Max line width for `JSS-WIDTH-001`.                         |
| `jssStyleChecker.runOn`                | `"change"`   | When to re-lint: `"save"` or `"change"`.                    |

## Commands

- **jss-lint: Run init** — write a starter `.jss-lint.toml` in the
  workspace folder.
- **jss-lint: Apply all fixes** — apply every available auto-fix to the
  active file.

## Develop

```sh
cd vscode-extension
npm install
npm run build:wasm   # compile the Rust engine to WASM (needs Rust + wasm-pack)
npm run watch        # incremental TS build
```

In a separate VS Code window, press `F5` to launch the Extension
Development Host.

## License

MIT.
