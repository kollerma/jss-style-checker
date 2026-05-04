# Implementation Plan: VS Code Extension

**Branch**: `012-vscode-extension` | **Date**: 2026-05-03 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/012-vscode-extension/spec.md`

## Summary

Build a TypeScript VS Code extension at `vscode-extension/` (in
this repo, per Clarifications §1) that wires the spec-011 LSP
server into the VS Code editor. The extension is a thin client
— ~500 LOC of TypeScript — covering:

- Activation on `.tex` / `.ltx` / `.Rnw` / `.Rmd` files.
- Spawning `jss-lint lsp` via the configured Python interpreter.
- A `vscode-languageclient` LanguageClient instance that handles
  every LSP method.
- Five settings under the `jssStyleChecker` namespace, propagated
  via `workspace/configuration`.
- A status-bar item that reflects per-file violation counts.
- Two command-palette commands (`Run init`, `Apply all fixes`).
- A graceful "missing Python / missing jss-lint" diagnostic UI.

Publishing: a single `.vsix` artefact published to both the VS
Code marketplace and Open VSX (Clarifications §4). Trigger:
`v*-vscode` git tags (Clarifications §5).

## Technical Context

**Language/Version**: TypeScript ≥5.0 (extension), targeting
Node 20 (the VS Code-bundled runtime). The Python side is
unchanged (spec 011's LSP server).

**Primary Dependencies** (extension, devDeps):
- `vscode-languageclient@^9` — LSP client.
- `@types/vscode@^1.85` — VS Code API types.
- TypeScript toolchain + esbuild for bundling.
- `vsce@^2` — packaging / publishing.

No runtime dependencies on the Python side.

**Storage**: None.

**Testing**: VS Code's `@vscode/test-electron` runs the
extension in a headless VS Code instance. Tests under
`vscode-extension/tests/` open fixture files and assert
diagnostic counts / status-bar text. The Python-side LSP
server is exercised by spec 011's tests; this spec does NOT
re-test it.

**Target Platform**: VS Code 1.85+ on Linux, macOS, Windows.
Open VSX consumers (Cursor, Codium, Theia) inherit
compatibility automatically.

**Project Type**: Multi-language repo — adds a top-level
TypeScript project alongside the existing Python package.

**Performance Goals**:
- Activation in <200 ms on a cold open (extension JS load only;
  the LSP server's start time is ~1 s and is asynchronous).
- Status-bar updates within 1 second of every diagnostic
  refresh (SC-002).

**Constraints**:
- Constitution §I determinism: the extension is a thin
  pass-through; determinism is delegated to the LSP server.
- Constitution §III non-fatal: a missing Python / missing
  `jss-lint[lsp]` produces a notification, not a crash.
- Constitution §IV zero core edits for journals: this spec
  adds a new top-level directory `vscode-extension/`. NO
  Python source under `src/texlint/` is modified.
- Constitution §V authority cited: the extension's hover UI
  surfaces `Rule.guide_url` via standard LSP rendering;
  no extension-side prose duplicates the catalogue.
- Constitution §VI precision gate: N/A.
- Constitution §VII safe auto-fix: code actions are LSP
  `WorkspaceEdit`s; VS Code's edit-application path is the
  source of truth for the on-disk write.
- Constitution §VIII TDD: extension-side smoke tests land
  before the extension code body.
- Constitution §IX 100% branch coverage on rule modules:
  unchanged.
- Constitution §X small surface: a thin TypeScript shim
  around `vscode-languageclient`. No business logic in the
  extension (it lives in the LSP server).
- Constitution §XI cross-cutting work: this spec is
  cross-cutting (touches a new language), justifying the
  spec-kit invocation.
- Constitution §XII reproducible corpus: N/A.

**Scale/Scope**: 1 new top-level directory
(`vscode-extension/`). ~500 LOC of TypeScript. 1 GitHub
Actions workflow file. 1 README badge. The Python side is
unchanged.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **§I Determinism** — extension is a thin client.
      **PASS**.
- [x] **§II AST-First** — N/A; client. **PASS**.
- [x] **§III Non-Fatal Parse** — missing Python /
      `jss-lint` surface as notifications. **PASS**.
- [x] **§IV Zero Core Edits for Journals** — no
      `src/texlint/` source is modified. New `vscode-
      extension/` top-level directory. **PASS**.
- [x] **§V Authority Cited** — `guide_url` plumbed via
      LSP. **PASS**.
- [x] **§VI ≥90% Precision Gate** — N/A. **PASS**.
- [x] **§VII Safe Auto-Fix** — VS Code applies edits.
      **PASS**.
- [x] **§VIII TDD** — extension smoke tests land first.
      **PASS by task ordering**.
- [x] **§IX 100% Branch Coverage on Rule Modules** —
      unchanged. **PASS**.
- [x] **§X Small Surface** — thin client; no business
      logic. **PASS**.
- [x] **§XII Reproducible Corpus** — N/A. **PASS**.

All gates PASS. No amendments required (§IV is satisfied
because no Python-side core file is touched).

Post-Phase-1 re-check: gates still PASS.

## Project Structure

### Documentation (this feature)

```text
specs/012-vscode-extension/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── extension-manifest.md
└── checklists/
    └── requirements.md
```

### Source Code (repository root)

```text
vscode-extension/                                  # NEW top-level directory
├── package.json                                   # extension manifest
├── tsconfig.json
├── esbuild.config.mjs
├── src/
│   ├── extension.ts                               # entry point
│   ├── client.ts                                  # LanguageClient wiring
│   ├── statusBar.ts                               # per-file violation count
│   ├── commands.ts                                # palette commands
│   └── pythonDiscovery.ts                         # Python path resolution
├── tests/
│   ├── extension.test.ts                          # smoke test
│   └── fixtures/
│       └── one_violation.tex
└── README.md                                      # marketplace listing copy

.github/workflows/
└── vscode-publish.yml                             # NEW — tag-triggered publish

README.md                                          # MODIFIED — add marketplace badge
```

**Structure Decision**: A new top-level directory
`vscode-extension/` keeps the TypeScript code physically
separate from the Python package, satisfying §IV (no core
edits) without adding a sibling repo. The extension's CI
job runs alongside the Python tests in the existing matrix
but with a Node setup; the workflow file documents the
boundary.

## Complexity Tracking

No amendments. The §IV gate passes cleanly because no
Python-side `src/texlint/` file is modified.
