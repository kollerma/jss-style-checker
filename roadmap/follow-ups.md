# Roadmap follow-ups

Each feature on the 12-spec roadmap shipped its core correctness
surface (engine + tests, ≥95% test coverage on new modules) plus a
documented set of deferrals. This file is the single tracker for
that deferred work, grouped by feature in roadmap order.

The shape of each item:

```
- [ ] **Feature 0NN** — short title (file/path) — one-line scope.
```

Order within each feature is roughly highest-to-lowest priority.
Items can land in any order; some unblock each other (noted
inline).

## Cross-cutting (touches multiple features)

- [x] **Click sub-group migration** (`src/texlint/cli.py`) — convert
      `jss-lint` from a single `@click.command` to a
      `@click.group(invoke_without_command=True, ...)` so subcommands
      can be added without breaking the existing positional-PATHS
      invocation. Unblocks the CLI surfaces of features 009, 010,
      011, 015, 016. (Shipped: every existing CLI integration test
      passes byte-identically; smoke tests at
      `tests/integration/test_cli_group_shape.py`.)

## Feature 006 — SARIF output

- [x] Renderer + tests + CLI flag (shipped).
- [x] Vendor the official SARIF 2.1.0 JSON schema at
      `tests/fixtures/sarif-2.1.0-schema.json` and add a contract
      test that validates every golden via
      `jsonschema.Draft202012Validator`. (Shipped: vendored from
      SchemaStore mirror as Draft 7; four parametrised scenarios.)
- [ ] Multi-fixture golden files
      (`tests/fixtures/sarif/golden_*.sarif`). Current tests assert
      structural invariants instead of byte-equality goldens.

## Feature 007 — JSS-guide rule mapping

- [ ] **Full catalogue backfill** —
      `specs/003-jss-rule-catalogue/catalogue.yaml`. Add
      `guide_section` and `guide_url` to the remaining 57 rules
      (only `JSS-CITE-002` is backfilled in v1). Mechanical pass:
      one entry per rule, sourced from
      `docs/jss-guide/index.json`. After backfill, tighten the
      `test_backfilled_rules_resolve_through_index` test and the
      validator to mark these fields REQUIRED for citable
      categories.
- [ ] Update the spec-007 contract test to fail (not warn) when
      a citable rule lacks `guide_section` / `guide_url`.
- [ ] Plumb `guide_section` into the terminal renderer's
      `(see <section>)` suffix and into the HTML renderer as an
      `<a href="...">` anchor.

## Feature 008 — Auto-fix

- [x] **SARIF `fixes[]` projection** —
      `src/texlint/output/sarif.py`. When a violation has a `Fix`,
      emit `runs[0].results[].fixes[]` per spec-006 §C-11 +
      spec-008 §3.7.
- [ ] **Rule-side `Fix` migrations** — pick three mechanical
      catalogue rules (`JSS-CITE-003`, `JSS-NAME-001`,
      `JSS-CAP-002` are the spec-008 baseline candidates) and
      emit `Fix(...)` payloads on their violations.
- [ ] `before.tex` / `after.tex` golden fixture pairs under
      `tests/fixtures/auto-fix/` for each migrated rule.
- [ ] Integration test for `--apply` interactive prompt
      (stdin scripted with `y\nn\na\n`) — covered by unit tests
      today; end-to-end via the CLI runner is the missing piece.
- [ ] Regression-rollback CLI integration test (a fixture rule
      whose fix re-trips its own rule; CLI exits 2 with the
      file unchanged).

## Feature 009 — `jss-lint explain`

- [ ] CLI subcommand wiring — depends on the cross-cutting Click
      sub-group migration. Once that lands, the `jss-lint explain
      RULE-ID [--example] [--format {terminal,markdown}]` surface
      dispatches into the existing `texlint.explain.render` API.
- [ ] Catalogue extension: add `explanation: str`,
      `example_bad: str | None`, `example_good: str | None` to
      every rule entry in `catalogue.yaml`. The `tomli_w`-style
      regenerator already accepts unknown OPTIONAL keys; adding
      the three fields is a one-line schema addition.
- [ ] `test_every_rule_has_explanation` contract test in
      `tests/unit/journals/jss/test_catalogue_citations.py`.

## Feature 010 — `jss-lint init`

- [ ] CLI subcommand wiring (depends on Click sub-group
      migration).
- [ ] Precision-DB-aware suppression: query
      `eval/precision-history.db` per rule and emit suppressions
      for any rule below the `--threshold` (default 0.90).
- [ ] Promote `tomli_w` from "hand-rolled TOML rendering" to a
      proper runtime dependency once the generated config gains
      structures (severity overrides, table-of-table sections)
      that the hand-roller can't easily produce.

## Feature 011 — Language Server

- [ ] Add `pygls>=1.3` under a new `[project.optional-
      dependencies] lsp = [...]` group.
- [ ] `src/texlint/lsp/server.py` — `pygls.LanguageServer`
      subclass implementing the 10 LSP method handlers.
- [ ] `src/texlint/lsp/cache.py` — per-document AST cache
      keyed by `(uri, textDocument.version)`.
- [ ] `src/texlint/lsp/config_watch.py` — handler for
      `workspace/didChangeWatchedFiles` covering
      `.jss-lint.toml` edits.
- [ ] `tests/integration/test_lsp_session.py` using
      `pygls.test` (initialize → didOpen → didChange (debounced)
      → codeAction → executeCommand → shutdown).
- [ ] `jss-lint lsp` CLI subcommand (depends on Click sub-group
      migration).

## Feature 012 — VS Code extension

- [ ] `vscode-extension/` build verification — `npm install`,
      `npm run compile`, `vsce package` produces a `.vsix`.
      Requires Node 20+ in CI.
- [ ] Live publish to the VS Code marketplace and Open VSX —
      requires `VSCE_PAT` and `OVSX_PAT` secrets in the repo;
      the workflow at `.github/workflows/vscode-publish.yml`
      runs on `v*-vscode` tags.
- [ ] End-to-end smoke test inside a headless VS Code instance
      using `@vscode/test-electron`. Depends on the spec-011
      LSP server shipping first.

## Feature 013 — Multi-file projects

- [x] **`ParsedProject` public type** in `texlint.api` —
      wraps a tuple of `ParsedDocument`s, the root `Path`, and
      the project graph. (Shipped.)
- [x] **`Rule.check_project: Callable | None`** — additive
      field on the public `Rule` dataclass. (Shipped.)
- [x] Engine dispatch in `core/engine.py::run` — accept
      `ParsedDocument | ParsedProject`, route per-rule.
      (Shipped.)
- [ ] Migrate the abbreviations rule from `check` to
      `check_project` (the canonical cross-file rule).
- [ ] `--no-resolve` CLI flag in `cli.py` — passes a
      `ParsedDocument` rather than auto-resolving.
- [ ] `JSS-PROJECT-001` (cycle) and `JSS-PROJECT-002`
      (missing reference) tool-side rules emitted by the
      resolver.

## Feature 014 — GitHub Action

- [ ] Action source repo — push the `action/` contents to a
      dedicated `kollerma/jss-style-checker-action` repository
      whose tags drive the marketplace listing. The release
      workflow at `.github/workflows/release-action.yml`
      handles the rolling-tag update once the dedicated repo
      exists.
- [ ] Live smoke-test workflow at
      `.github/workflows/test-action.yml` — runs the action
      against `docs/jss-template/` (or the recall corpus once
      it ships) and asserts SARIF presence + violation count.
- [x] `--source-root` integration: forward the GitHub Actions
      checkout root to the spec-006 flag so SARIF URIs resolve
      to repo-relative paths in the Security tab. (Shipped: the
      composite action's lint step now passes
      `--source-root "$GITHUB_WORKSPACE"`; contract test at
      `tests/integration/test_action_manifest.py` guards the wiring.)

## Feature 015 — Conformance report

- [ ] PDF rendering via WeasyPrint (gated behind
      `[project.optional-dependencies] pdf = ["weasyprint>=60"]`).
- [ ] HTML rendering via the existing Jinja2 stack
      (`output/html_output.py` shares its template loader).
- [ ] CLI subcommand `jss-lint report PATH` (depends on Click
      sub-group migration).
- [ ] Manuscript-metadata extraction from `\title{}` /
      `\author{}` / `\Plainauthor{}` macros at preamble parse
      time. v1 uses the `--title` / `--author` overrides only.

## Feature 016 — `jss-lint diff`

- [ ] CLI subcommand `jss-lint diff OLD.json NEW.json`
      (depends on Click sub-group migration).
- [ ] Renderers: `--format terminal` (reuses
      reviewer-mode), `--format markdown` (GitHub-flavoured
      CommonMark), `--format json` (deterministic
      `{summary, fixed, introduced, unchanged}` shape).
- [ ] Schema validation of input JSON against the spec-001
      JSON Schema; mismatch exits 2.
- [ ] Populate `docs/jss-guide/rule-renames.json` with
      historical renames as they happen (currently empty).

## Feature 017 — Recall evaluation

- [ ] **Hand-annotate the first 10 JSS papers** under
      `eval/recall-corpus/<paper-id>/`. The annotation TOML
      schema is documented in
      `eval/recall-corpus/README.md`. This is the most
      labour-intensive deferred item — read each paper end-
      to-end, identify every JSS-guide violation, record
      `(rule_id, file, line)` per FR-002.
- [ ] `eval-jss recall` CLI subcommand with `--gate` and
      `--validate` flags.
- [ ] `recall_history` SQLite table schema in
      `eval/precision-history.db` per data-model §3.
- [ ] Combined precision + recall report column in
      `eval/report.py`.
- [ ] `eval/badge.py` — emits shields.io endpoint JSON for
      the precision and recall badges.
- [ ] `.github/workflows/publish-badges.yml` — push
      regenerated badge JSON to the `gh-pages` branch on
      every CI run.
- [ ] Update README to display the three badges
      (precision / recall / F1).

## Tracking

This file is hand-edited. When a follow-up lands, check its
box and link to the PR. When new follow-ups surface during
implementation, add them under the relevant feature.
