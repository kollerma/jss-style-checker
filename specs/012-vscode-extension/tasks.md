---
description: "Tasks for VS Code extension"
---

# Tasks: VS Code Extension

## Phase 1: Scaffold

- [ ] T001 Create `vscode-extension/` skeleton: `package.json`,
      `tsconfig.json`, `src/extension.ts`, `README.md`.
- [ ] T002 The extension activates on `.tex/.ltx/.Rnw/.Rmd` and
      spawns `python -m texlint.cli lsp` (depends on the deferred
      spec-011 server).

## Phase 2: Workflow

- [ ] T003 `.github/workflows/vscode-publish.yml` — tag-triggered
      publish workflow.

## Implementation Strategy

**MVP (this PR)**: Scaffold the extension package + manifest +
README so `vsce package` would build it. Live publish requires
the spec-011 LSP server to ship first; this PR ships the
extension shell, ready to be wired up post-LSP.
