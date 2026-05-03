# 011 — Language Server (LSP)

**Phase:** Editor experience
**Depends on:** 006 (SARIF — same diagnostic shape), 008 (fix
actions)
**Unblocks:** 012 (VS Code extension)

## Why

Inline squiggles + click-to-fix in the editor are why `eslint` and
`ruff` are indispensable. Running the linter via `jss-lint` after
each save is not the same experience. The LSP daemon is the missing
foundation for any real-time editor integration.

## /speckit.specify prompt

Implement an LSP server exposed as `jss-lint lsp` (stdio transport;
`--socket PORT` for TCP). The server speaks LSP 3.17 and supports:
`initialize`, `initialized`, `shutdown`, `exit`,
`textDocument/didOpen`, `textDocument/didChange` (debounced 200 ms),
`textDocument/didSave`, `textDocument/didClose`,
`textDocument/publishDiagnostics`, `textDocument/codeAction` (one
CodeAction per `Fix` from spec 008), and
`workspace/executeCommand` for "apply all fixes". Diagnostics use
the SARIF severity mapping from spec 006. Per-document AST cache so
re-lint on character-level edits doesn't re-parse from scratch when
the change is local. The daemon respects the project's
`.jss-lint.toml` and watches it for changes.

## /speckit.clarify prompt

Probe: (a) which LSP library — `pygls` (well-maintained,
opinionated) or hand-rolled JSON-RPC? (b) is multi-root workspace
support in scope v1? (c) does the cache key on file mtime, content
hash, or both? (d) how do we handle very large files (>1 MB) — full
reparse, partial reparse, or skip? (e) what's the protocol for
surfacing rule explanations (spec 009) in hover-over diagnostics?

## /speckit.plan prompt

Use `pygls` (proven LSP framework). Add `pygls>=1.3` as an optional
dependency under a new `[project.optional-dependencies] lsp = [...]`
group so non-LSP users don't pay for it. New module
`src/texlint/lsp/server.py` with the protocol handlers, plus
`src/texlint/lsp/cache.py` for the per-document AST cache. Reuse
existing `parse_document()` from `core/engine.py`. Add a Click
subcommand `jss-lint lsp` that bootstraps the server. Add
`tests/unit/lsp/test_server.py` using `pygls.test`. Document
protocol support level in
`specs/011-language-server/contracts/lsp.md`.
