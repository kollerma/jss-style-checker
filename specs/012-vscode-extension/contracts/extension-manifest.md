# Contract: VS Code Extension Manifest

**Spec**: [../spec.md](../spec.md)
**Plan**: [../plan.md](../plan.md)

This contract documents the invariants of the
`vscode-extension/package.json` manifest and its surrounding
package surfaces.

## C-1 Identity

- `name = "jss-style-checker"`.
- `publisher = "kollerma"`.
- `displayName = "JSS Style Checker"`.
- `engines.vscode = "^1.85.0"` (or higher; never lower).

## C-2 Activation

`activationEvents` MUST include:
- `onLanguage:latex`
- `onLanguage:tex`
- `onLanguage:rnoweb`
- `onLanguage:rmd`
- `onCommand:jss-lint.runInit`
- `onCommand:jss-lint.applyAllFixes`

`activationEvents` MUST NOT include `*` (which would activate
the extension in every workspace, regardless of relevance).

## C-3 Settings

`contributes.configuration.properties` MUST contain exactly the
five `jssStyleChecker.*` keys per data-model §1, with the
documented types and defaults.

## C-4 Commands

`contributes.commands` MUST contain exactly two entries per
data-model §2, with `category = "jss-lint"` so they appear
under that prefix in the palette.

## C-5 LSP server invocation

The extension MUST invoke the LSP server via:

```
<python-interpreter> -m texlint.cli lsp
```

over stdio transport. TCP transport is reserved for testing.

## C-6 Error handling

When LSP server startup fails (missing interpreter, missing
`jss-lint[lsp]`, port collision in TCP test mode), the
extension MUST:
- Log the failure to the extension's output channel.
- Show a notification with actionable buttons (per
  data-model §pythonDiscovery flow).
- NOT throw an unhandled exception.

## C-7 Status bar

Exactly one `vscode.StatusBarItem` MUST be created per
window. The item MUST update on every diagnostic-change event
for the active editor. The item's text MUST match the regex
`jss-lint: \d+`. Clicking MUST open the Problems pane.

## C-8 Settings round-trip

A change to any of the five settings MUST reach the LSP server
within 1 second of the user committing the change in VS
Code's settings UI. The LSP server applies the new
configuration to its in-memory state without restart.

## C-9 No telemetry

The extension MUST NOT emit telemetry of any kind. No usage
events, no error reports, no analytics. Adding telemetry
requires a follow-up spec with explicit user consent
discussion.

## C-10 Marketplace assets

The published `.vsix` MUST contain:
- `package.json`
- Bundled JS (single file via esbuild, ideally `<200 KB`).
- `README.md` (the marketplace listing copy).
- `LICENSE` (project license).
- `CHANGELOG.md` (per-version release notes).

It MUST NOT contain:
- `node_modules/` (replaced by the bundle).
- `tests/`
- Any Python source.

## C-11 Publish workflow

The `vscode-publish.yml` workflow MUST:
- Trigger on tags matching `v*-vscode`.
- Build the extension with the same command developers use
  locally (`npm run build`).
- Publish to BOTH the VS Code marketplace and Open VSX.
- Exit with a non-zero code if either publish fails.
- Refer to `VSCE_PAT` and `OVSX_PAT` repo secrets; absence of
  either is a clear-error fail (no silent skip).

## C-12 Repository layout invariant

The extension's source MUST live entirely under
`vscode-extension/`. NO Python source under `src/texlint/`
references the extension; the extension references the
Python LSP server only via the documented CLI subcommand
(`jss-lint lsp`). This boundary lets the Python package be
shipped on PyPI independently of the extension on the
marketplace.
