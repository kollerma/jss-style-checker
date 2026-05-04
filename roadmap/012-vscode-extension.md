# 012 — VS Code extension

**Phase:** Editor experience
**Depends on:** 011 (Language Server)
**Unblocks:** —

## Why

Most JSS authors edit in VS Code or Overleaf. A published VS Code
extension is the single highest-leverage way to put the tool in
front of users — install once, lint forever, no terminal needed.

## /speckit.specify prompt

Ship a VS Code extension `kollerma.jss-style-checker` published to
the marketplace. The extension activates on `.tex`, `.ltx`, `.rnw`,
`.rmd` files; spawns the spec-011 LSP server (`jss-lint lsp`) using
the user's configured Python interpreter; exposes the standard LSP
UX (squiggles, hover, code-action lightbulb, Problems pane).
Settings (mapped to LSP `workspace/configuration`):
`jssStyleChecker.python.path`,
`jssStyleChecker.severityOverrides`,
`jssStyleChecker.ignoreRules`,
`jssStyleChecker.codeWidth`,
`jssStyleChecker.runOn` (`save` | `change`).
Status-bar item shows violation count and links to the Problems
pane. Bundle a "Run jss-lint init" command (spec 010).

## /speckit.clarify prompt

Probe: (a) where does the extension source live — same repo
(`vscode-extension/`) or sibling repo
(`kollerma/jss-style-checker-vscode`)? (b) bundle a Python
interpreter or require user-managed venv? (c) support Overleaf via
the same extension or a sibling browser extension? (d) which
marketplace (only the public VS Code marketplace, or also Open VSX
for Cursor / Codium)? (e) automated marketplace publish via GitHub
Actions on tag push?

## /speckit.plan prompt

Create a new top-level directory `vscode-extension/` containing a
TypeScript extension scaffolded with `yo code`. Use
`vscode-languageclient` to talk to the spec-011 LSP server. Build
via `vsce package` / `vsce publish`. Add
`.github/workflows/vscode-publish.yml` triggered on `v*-vscode` git
tags. Document in `specs/012-vscode-extension/quickstart.md`.
Add a README badge linking to the marketplace listing.
