# Quickstart: Running and Extending the LSP Server

## For an editor user

### Install

```sh
pip install "jss-lint[lsp]"
```

The bracketed extra brings in `pygls`. A non-extra install does
not include LSP support.

### Configure your editor

#### Neovim (with `nvim-lspconfig`)

```lua
require('lspconfig').jss_lint = {
  default_config = {
    cmd = { 'jss-lint', 'lsp' },
    filetypes = { 'tex', 'rnoweb', 'rmarkdown' },
    root_dir = function(fname)
      return require('lspconfig.util').root_pattern('.jss-lint.toml')(fname)
    end,
  },
}
```

#### Helix

```toml
# .helix/languages.toml
[[language]]
name = "latex"
language-servers = [{ command = "jss-lint", args = ["lsp"] }]
```

#### VS Code

Use the spec-012 extension once it ships.

### Run

Open a `.tex`, `.Rnw`, or `.Rmd` file. The editor connects to
the LSP server automatically. You should see:

- Inline squiggles under each violation.
- A "Quick Fix" menu on rules that ship a `Fix` (spec 008).
- A `jss-lint: Apply all fixes` command in the editor's
  command palette.

## For a contributor

### Where things live

```text
src/texlint/lsp/server.py            # pygls subclass + handlers
src/texlint/lsp/cache.py             # AST cache
src/texlint/lsp/conversions.py       # type projections
src/texlint/lsp/config_watch.py      # .jss-lint.toml watcher
src/texlint/cli.py                   # `jss-lint lsp` subcommand
tests/unit/lsp/                      # unit tests
tests/integration/test_lsp_session.py # end-to-end session
```

### Run the LSP tests

```sh
pip install -e ".[lsp,dev]"
pytest tests/unit/lsp/ tests/integration/test_lsp_session.py -v
```

### Add a new LSP method handler

1. Pick the method (e.g., `textDocument/hover`). Verify it
   appears in the LSP 3.17 spec.
2. Add the corresponding capability to `server.capabilities`
   in the `initialize` response (`data-model.md §6`).
3. Add the handler in `server.py`. Use `@server.feature("...")`
   to register it.
4. Project any data shapes via `conversions.py`.
5. Add unit tests under `tests/unit/lsp/`.
6. Add a slice of the integration session test under
   `tests/integration/test_lsp_session.py`.

### Common pitfalls

- **Off-by-one in line/column**: LSP is 0-based; the linter is
  1-based. Every projection in `conversions.py` does this
  translation. Don't move the translation outside that
  module.
- **UTF-16 vs. UTF-8 columns**: research §7. We project byte
  columns directly to LSP "characters". For ASCII content
  this is correct; for multibyte content it's an
  approximation. If a user reports a multibyte-character
  offset bug, tighten the projection.
- **Cache invalidation on config reload**: `cache.py`
  invalidates by `config_hash`. If you forget to bump the
  hash when the config changes, stale lints leak through.
- **Debounce task leaks**: each `didChange` cancels the
  pending task. If you add a new code path that schedules
  parsing, use the same cancel-and-reschedule idiom — don't
  fire-and-forget.
- **Forgetting `pygls` is optional**: every import of
  `pygls` lives under `src/texlint/lsp/`. Do not import
  it from any module outside that tree. The CLI checks
  for the import inside the `lsp` subcommand handler and
  emits the install-extra error if missing.
