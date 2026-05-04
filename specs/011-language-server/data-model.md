# Data Model: Language Server (LSP)

**Phase**: 1
**Spec**: [spec.md](spec.md)
**Plan**: [plan.md](plan.md)

## 1. AST cache

```python
@dataclass(frozen=True)
class CachedDocument:
    uri: str
    version: int
    parsed: ParsedTexFile | ParsedRmdFile  # spec-005 union
    config_hash: str
```

Cache type: `dict[str, CachedDocument]` keyed by `uri`.
Invalidation: replace on `didChange` (new `version`) or on
config reload (new `config_hash`). Eviction: pop on
`didClose`.

## 2. `Violation → Diagnostic` projection

| LSP `Diagnostic` field           | Source                                                    |
| -------------------------------- | --------------------------------------------------------- |
| `range.start.line`               | `Violation.line - 1`                                      |
| `range.start.character`          | `Violation.column - 1` (UTF-16 caveat — research §7)      |
| `range.end.line`                 | `Violation.end_line - 1` (or `range.start.line`)          |
| `range.end.character`            | `Violation.end_column - 1` (or `range.start.character`)   |
| `severity`                       | `1` / `2` / `3` per spec 006 SARIF map                    |
| `code`                           | `Violation.rule_id`                                       |
| `source`                         | `"jss-lint"`                                              |
| `message`                        | `Violation.message`                                       |
| `codeDescription.href`           | `Rule.guide_url` (when non-`None`)                        |

For sentinel rules (`guide_url is None`), `codeDescription` is
omitted from the diagnostic.

## 3. `Fix → CodeAction` projection

| LSP `CodeAction` field     | Source                                                                   |
| -------------------------- | ------------------------------------------------------------------------ |
| `title`                    | `Fix.description`                                                        |
| `kind`                     | `"quickfix"`                                                             |
| `diagnostics`              | `[<the diagnostic this action fixes>]`                                   |
| `edit.changes[uri]`        | `[TextEdit(range=byte_range_to_lsp_range(fix.start, fix.end), newText=fix.replacement)]` |

`byte_range_to_lsp_range` reads the cached source bytes,
counts newlines up to `fix.start`, and computes line / column
positions on both ends.

## 4. `apply-all-fixes` workspace command

Command id: `jss-lint.applyAllFixes`. Arguments: optional
`{ uris?: string[] }` to scope to specific documents.

Return value: a `WorkspaceEdit` aggregating one `TextEdit`
per safe-confidence fix across the requested URIs (or all
open documents if `uris` is unset).

The conflict-resolution step from spec 008 §1 runs over the
aggregated fix list before the `WorkspaceEdit` is built.
Skipped fixes are NOT included in the response.

## 5. CLI surface

```text
Usage: jss-lint lsp [OPTIONS]

Options:
  --socket PORT     Use TCP transport on PORT instead of stdio.
  -h, --help        Show this message and exit.
```

When `pygls` is not installed, the subcommand exits 2 with
stderr `LSP support not installed; install with pip install
"jss-lint[lsp]"`.

## 6. LSP server capabilities

Reported in the `initialize` response under
`server.capabilities`:

```json
{
  "textDocumentSync": {
    "openClose": true,
    "change": 2 // Incremental
  },
  "codeActionProvider": {"codeActionKinds": ["quickfix"]},
  "executeCommandProvider": {"commands": ["jss-lint.applyAllFixes"]},
  "diagnosticProvider": null
}
```

`textDocumentSync.change = 2` (Incremental) tells clients we
accept incremental edits in `didChange`. The cache layer
re-applies them to the document text before re-parsing.

## 7. `.jss-lint.toml` watch

Registered via dynamic capability `workspace/
didChangeWatchedFiles` for the glob
`**/.jss-lint.toml`. On change, the server:
1. Loads the new config via the existing
   `load_config(...)` from spec 001.
2. If the load fails, logs a `window/logMessage` (severity
   Error) with the parse error; keeps the previous config.
3. Otherwise, replaces the active config and re-lints every
   open document, publishing fresh diagnostics for each.

## 8. Out of scope

| Item                                            | Reason                                                                          |
| ----------------------------------------------- | ------------------------------------------------------------------------------- |
| Partial reparse for >1 MB files                 | Out per research §4.                                                             |
| Per-folder `.jss-lint.toml` in multi-root       | Out per Clarifications §2.                                                       |
| `textDocument/hover` for inline explanation     | Out per Clarifications §5.                                                       |
| `textDocument/formatting`                       | Out — `jss-lint` is a linter, not a formatter.                                    |
| Workspace symbols / references                  | Out — irrelevant for a style linter.                                              |
| Daemon mode (long-lived background server)      | Out — editors spawn a server per connection.                                     |
| Multi-client multiplexing                       | Out — one client per server process.                                              |
