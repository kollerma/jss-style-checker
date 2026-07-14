# JSS Style Checker — VS Code Extension

Lint LaTeX / Sweave / R Markdown manuscripts against the JSS style
guide directly inside VS Code.

> **Status (spec 012):** scaffolded. The extension is built on top of
> the spec-011 LSP server which is staged but not yet shipped; once
> the server lands, this extension wires up to it via
> `vscode-languageclient`. See
> `specs/011-language-server/spec.md` and
> `specs/012-vscode-extension/spec.md` for the full design.

## Install (once the LSP server ships)

```sh
pip install "jss-style-checker[lsp]"
code --install-extension kollerma.jss-style-checker
```

## Settings

| Setting                                | Default      | Description                                                |
| -------------------------------------- | ------------ | ---------------------------------------------------------- |
| `jssStyleChecker.python.path`          | `""`         | Override Python interpreter (default: discover).            |
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
