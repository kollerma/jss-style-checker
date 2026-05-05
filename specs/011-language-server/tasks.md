---
description: "Tasks for Language Server (LSP)"
---

# Tasks: Language Server (LSP)

## Phase 1: Foundational

- [x] T001 `src/texlint/lsp/conversions.py` — pure-Python helpers
      that project Violation → LSP Diagnostic and Fix → LSP
      WorkspaceEdit. Reusable independent of pygls.
- [x] T002 Tests for conversions (`tests/unit/lsp/test_conversions.py`).

## Phase 2: Deferred — pygls server

- [x] T003 (deferred) Add `pygls>=1.3` as optional dep `[lsp]`.
- [x] T004 (deferred) Implement `src/texlint/lsp/server.py` with the
      10 LSP method handlers per data-model §6.
- [x] T005 (deferred) `tests/integration/test_lsp_session.py` using
      `pygls.test`.

## Implementation Strategy

**MVP (this PR)**: Conversions module + tests. The
type-projection logic between texlint's own types and the LSP wire
shapes is the substantive correctness surface; the pygls server
itself is glue around it. Ship the conversions; ship the server in
a follow-up.
