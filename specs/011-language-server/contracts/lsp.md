# Contract: LSP 3.17 Server

**Spec**: [../spec.md](../spec.md)
**Plan**: [../plan.md](../plan.md)

This contract documents the protocol-level invariants of the
`jss-lint lsp` server.

## C-1 Protocol version

The server speaks LSP 3.17. The `serverInfo.name` in the
`initialize` response is `"jss-lint"`; the `version` matches
`texlint.__version__`.

## C-2 Supported methods

The server MUST handle these methods (errors `MethodNotFound`
elsewhere):

- Lifecycle: `initialize`, `initialized`, `shutdown`, `exit`.
- Document sync: `textDocument/didOpen`,
  `textDocument/didChange`, `textDocument/didSave`,
  `textDocument/didClose`.
- Diagnostics: `textDocument/publishDiagnostics` (server →
  client).
- Code actions: `textDocument/codeAction`.
- Workspace: `workspace/executeCommand` (with command id
  `jss-lint.applyAllFixes`),
  `workspace/didChangeWatchedFiles`.

## C-3 Capabilities advertised

Per data-model §6:

```json
{
  "textDocumentSync": {"openClose": true, "change": 2},
  "codeActionProvider": {"codeActionKinds": ["quickfix"]},
  "executeCommandProvider": {"commands": ["jss-lint.applyAllFixes"]}
}
```

## C-4 Diagnostic equivalence with SARIF

For any input file F and config C, the set of diagnostics
published by the LSP server MUST be byte-equivalent to the
`runs[0].results[]` produced by `jss-lint --output sarif`,
modulo:
- 0-based vs. 1-based coordinates.
- LSP `severity` integer vs. SARIF `level` string.
- LSP `code` vs. SARIF `ruleId`.

The contract test uses the same fixture for both renderers and
asserts equivalence.

## C-5 Debounce

`textDocument/didChange` debounces 200 ms per document.
A `didChange` arriving within the window cancels the pending
lint and restarts the timer. The next debounce window starts
on the new edit.

## C-6 Cache key

The AST cache key is `(uri, textDocument.version)`. The cache
MUST be invalidated when either component changes, AND
invalidated for ALL documents when `.jss-lint.toml` reloads.

## C-7 Code action invariants

For each diagnostic D published by the server:
- If the corresponding `Violation.fix is None`, a
  `textDocument/codeAction` query for D's range returns an
  empty list.
- If `Violation.fix is not None`, the response contains
  exactly one `CodeAction` of kind `quickfix` whose `edit`
  is a `WorkspaceEdit` reflecting the fix.

The action's `title` equals `Fix.description`. The action's
`diagnostics` field references D.

## C-8 `apply-all-fixes` invariants

`workspace/executeCommand` with `command =
"jss-lint.applyAllFixes"` returns a `WorkspaceEdit`:
- Aggregating one `TextEdit` per safe-confidence `Fix`
  across the requested document URIs (default: all open).
- Pre-running the spec-008 conflict resolution; only winners
  are emitted.
- Sorted: edits within each document are emitted in
  reverse-position order so the client applying them does
  not need to recompute offsets.

## C-9 Optional dependency gating

`jss-lint lsp` MUST exit 2 with stderr `LSP support not
installed; install with pip install "jss-lint[lsp]"` when
`pygls` is not importable. The check is performed inside the
subcommand handler; importing `texlint.lsp.*` from outside
the subcommand is forbidden (research §0 of code review).

## C-10 Lifecycle

The server MUST:
- Wait for `initialize` before processing other requests.
  Earlier requests fail with `ServerNotInitialized`.
- Publish empty diagnostics on `didClose` (clearing stale
  squiggles in the editor).
- Honour `shutdown` by stopping all asyncio tasks and
  flushing pending writes.
- Honour `exit` by terminating the process within 1 second.

## C-11 No filesystem mutation

The server MUST NOT mutate any file on disk. Code actions and
the apply-all command return `WorkspaceEdit`s; the EDITOR
applies them. This is the LSP contract; we follow it.

## C-12 Determinism

For the same `(input file content, config)`, two LSP sessions
that open + lint the file MUST publish byte-identical
diagnostics.

## C-13 Backwards compatibility with the CLI

The pre-spec-011 CLI behaviour is unchanged. The new
subcommand is opt-in; users without the `[lsp]` extra
continue to use `jss-lint <PATHS>` and `jss-lint init` /
`jss-lint explain` exactly as before.
