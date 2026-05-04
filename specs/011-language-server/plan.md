# Implementation Plan: Language Server (LSP)

**Branch**: `011-language-server` | **Date**: 2026-05-03 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/011-language-server/spec.md`

## Summary

Implement an LSP 3.17 server using `pygls>=1.3` (Clarifications §1).
The server lives under `src/texlint/lsp/`, exposed as the `jss-lint
lsp` subcommand (third subcommand after `explain` (009) and `init`
(010)). The server reuses the existing `core/engine.py::run` for
linting and `core/parser.py::parse_document` for parsing.

Architectural shape:

- `src/texlint/lsp/server.py` — `pygls.LanguageServer` subclass
  with handlers for the 10 LSP methods listed in spec FR-002.
- `src/texlint/lsp/cache.py` — per-document AST cache, keyed by
  `DocumentUri` and `textDocument.version`.
- `src/texlint/lsp/conversions.py` — `Violation → Diagnostic`,
  `Fix → CodeAction → WorkspaceEdit`, byte-offset → LSP
  position translation.
- `src/texlint/lsp/config_watch.py` — handler for
  `workspace/didChangeWatchedFiles` covering `.jss-lint.toml`
  edits.

The optional dependency model: `[project.optional-dependencies]
lsp = ["pygls>=1.3"]`. A non-LSP user can `pip install jss-lint`
without `pygls`. Invoking `jss-lint lsp` without the extra emits
a stderr message and exits 2.

## Technical Context

**Language/Version**: Python ≥3.10, unchanged.

**Primary Dependencies**:
- Runtime (core): unchanged.
- Runtime (`[lsp]` extra): `pygls>=1.3`.
- Test: `pygls>=1.3` (re-uses the same dep — tests run with the
  extra installed).

**Storage**: None.

**Testing**:
- `tests/unit/lsp/test_server.py` — handler-by-handler tests
  using `pygls.test`.
- `tests/unit/lsp/test_cache.py` — AST cache behaviour.
- `tests/unit/lsp/test_conversions.py` — coordinate translation,
  diagnostic projection, code-action projection.
- `tests/integration/test_lsp_session.py` — end-to-end LSP
  session: initialize → didOpen → didChange (debounced) →
  codeAction → executeCommand → shutdown.

**Target Platform**: POSIX primary; Windows likely works via
`pygls`'s built-in transport handling (untested in this spec).

**Project Type**: Library + CLI; gains an LSP daemon entry-point.

**Performance Goals**: SC-001's 95th-percentile <100 ms for
single-character `didChange` round trip on a 5,000-line fixture.

**Constraints**:
- Constitution §I determinism: the LSP server's diagnostics are
  byte-equivalent to the SARIF output (spec 006), modulo
  coordinate-system translation. SC-002 enforces this.
- Constitution §III non-fatal: parse failures surface as
  `JSS-PARSE-000` diagnostics; the server never crashes.
- Constitution §IV zero core edits for journals: this spec adds
  one new module tree (`src/texlint/lsp/`) plus one CLI
  subcommand. NOT a journal addition. The server reuses the
  engine without modifying it.
- Constitution §V authority cited: diagnostics carry
  `codeDescription.href = Rule.guide_url` (Clarifications §5).
- Constitution §VI precision gate: N/A.
- Constitution §VII safe auto-fix: code actions translate
  `Fix` payloads into `WorkspaceEdit`s; the editor (not the
  server) commits the edit. Atomic write semantics are the
  editor's responsibility once the edit returns to the editor.
- Constitution §VIII TDD: handler tests + cache tests + a small
  integration session land before the server body.
- Constitution §IX 100% branch coverage on rule modules:
  unchanged.
- Constitution §X small surface: one CLI subcommand, one new
  module tree, one new optional dep. The dep is gated behind
  `[lsp]` so the core install size is unaffected.
- Constitution §XII reproducible corpus: N/A.

**Scale/Scope**: 4 new modules under `src/texlint/lsp/` (~700
LOC total). 1 new CLI subcommand. 1 optional dep (`pygls`).
4 new test modules. 1 contract document.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **§I Determinism** — diagnostics byte-equivalent to SARIF
      modulo coordinate translation. **PASS**.
- [x] **§II AST-First** — server reuses the existing AST-first
      pipeline. **PASS**.
- [x] **§III Non-Fatal Parse** — parse failures become
      `JSS-PARSE-000` diagnostics; server does not crash on
      malformed input. **PASS**.
- [x] **§IV Zero Core Edits for Journals** — new module tree
      `src/texlint/lsp/`; one new CLI subcommand. NOT a
      journal addition. **PASS with documented amendment**.
- [x] **§V Authority Cited** — `codeDescription.href` plumbs
      `guide_url` through. **PASS**.
- [x] **§VI ≥90% Precision Gate** — N/A. **PASS**.
- [x] **§VII Safe Auto-Fix** — code actions return
      `WorkspaceEdit`s; the editor applies them. The server
      does NOT touch the filesystem on behalf of the user.
      **PASS**.
- [x] **§VIII TDD** — handler tests land before the server
      body. **PASS by task ordering**.
- [x] **§IX 100% Branch Coverage on Rule Modules** —
      unchanged. **PASS**.
- [x] **§X Small Surface** — one optional dep, one module
      tree. The dep is gated behind `[lsp]` so the core
      install is unaffected. **PASS**.
- [x] **§XII Reproducible Corpus** — N/A. **PASS**.

All gates PASS. One documented amendment under §IV.

Post-Phase-1 re-check: gates still PASS.

## Project Structure

### Documentation (this feature)

```text
specs/011-language-server/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── lsp.md
└── checklists/
    └── requirements.md
```

### Source Code (repository root)

```text
src/texlint/lsp/
├── __init__.py
├── server.py                                      # NEW — pygls.LanguageServer subclass
├── cache.py                                       # NEW — per-document AST cache
├── conversions.py                                 # NEW — Violation/Fix → LSP types
└── config_watch.py                                # NEW — .jss-lint.toml watcher

src/texlint/cli.py                                 # MODIFIED — register `lsp` subcommand

pyproject.toml                                     # MODIFIED:
                                                   #   [project.optional-dependencies]
                                                   #   lsp = ["pygls>=1.3"]

tests/
├── unit/
│   └── lsp/
│       ├── test_cache.py                          # NEW
│       ├── test_conversions.py                    # NEW
│       └── test_server.py                         # NEW
├── integration/
│   └── test_lsp_session.py                        # NEW
└── fixtures/
    └── lsp/
        ├── small_one_violation.tex                # for didOpen / didChange tests
        └── large_5k_lines.tex                     # for SC-001 latency measurement
```

**Structure Decision**: One module tree
(`src/texlint/lsp/`), one CLI subcommand, one optional dep.
The 10 LSP method handlers split across `server.py`
(orchestration) and `conversions.py` (data shape mapping)
keep the server module under ~300 LOC. The cache lives in
its own module so its tests don't need a full LSP session.

## Complexity Tracking

One documented amendment.

| Amendment | Why Needed | Alternative Rejected |
|-----------|------------|---------------------|
| New module tree `src/texlint/lsp/` and a new CLI subcommand `jss-lint lsp` (§IV) | §IV prohibits core edits when *adding a journal*. This spec adds an editor-integration surface that operates on top of the existing engine; no journal is registered. | **Implement LSP as a separate package** — would still need an entry-point in the main CLI for discoverability; net-zero benefit. **Hand-roll JSON-RPC** — Constitution §X allows the `pygls` dep when the alternative is ~1k LOC of hand-rolled framing + lifecycle code. Rejected per Clarifications §1. |
