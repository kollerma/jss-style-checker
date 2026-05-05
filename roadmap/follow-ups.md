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
- [x] Multi-fixture golden files
      (`tests/fixtures/sarif/golden_*.sarif`). (Shipped: four
      scenarios — clean / single warning / parse error /
      multi-file — under
      `tests/integration/test_cli_sarif_goldens.py`. Volatile
      fields (version + full rule catalogue) are masked. Regen
      via `JSSLINT_REGEN_GOLDENS=1 pytest`.)

## Feature 007 — JSS-guide rule mapping

- [x] **Full catalogue backfill** —
      `specs/003-jss-rule-catalogue/catalogue.yaml`. (Shipped:
      all 58 rules carry guide_section + guide_url; index.json
      grew by 6 sections — Structure, Typography, Mathematical
      notation, Cross-references, Abbreviations, House style.)
- [x] Update the spec-007 contract test to fail (not warn) when
      a citable rule lacks `guide_section` / `guide_url`.
      (Shipped: `test_every_citable_rule_is_backfilled`.)
- [x] Plumb `guide_section` into the terminal renderer's
      `(see <section>)` suffix and into the HTML renderer as an
      `<a href="...">` anchor. (Shipped: terminal appends
      `(see §<section>)` for citable rules; HTML gains a Section
      column with anchor links; sentinel rules render plain.)

## Feature 008 — Auto-fix

- [x] **SARIF `fixes[]` projection** —
      `src/texlint/output/sarif.py`. When a violation has a `Fix`,
      emit `runs[0].results[].fixes[]` per spec-006 §C-11 +
      spec-008 §3.7.
- [x] **Rule-side `Fix` migrations** — pick three mechanical
      catalogue rules (`JSS-CITE-003`, `JSS-NAME-001`,
      `JSS-CAP-002` are the spec-008 baseline candidates) and
      emit `Fix(...)` payloads on their violations. (Shipped:
      JSS-CITE-003 and JSS-NAME-001 emit safe-confidence fixes;
      JSS-CAP-002 deferred — no stable byte range without a
      rule-body rewrite.)
- [x] `before.tex` / `after.tex` golden fixture pairs under
      `tests/fixtures/auto-fix/` for each migrated rule.
      (Shipped for JSS-CITE-003 and JSS-NAME-001.)
- [x] Integration test for `--apply` interactive prompt
      (stdin scripted with `y\nn\na\n`) — covered by unit tests
      today; end-to-end via the CLI runner is the missing piece.
      (Shipped: `tests/integration/test_cli_fix_apply.py`
      `TestApplyInteractive` scripts `y\n` and `n\n` over stdin
      against the JSS-CITE-003 fixture; `y` rewrites the file to
      match `after.tex` byte-for-byte, `n` leaves it untouched.)
- [x] Regression-rollback CLI integration test (a fixture rule
      whose fix re-trips its own rule; CLI exits 2 with the
      file unchanged). (Shipped:
      `tests/integration/test_cli_fix_apply.py`
      `TestRegressionRollback` registers a synthetic `regression`
      journal via `monkeypatch` on `importlib.metadata.entry_points`;
      its only rule emits a no-op `Fix` whose replacement equals the
      matched token, so the rule re-fires on re-validate and the
      engine rolls back to the pre-fix bytes — the test asserts
      exit 2, byte-identical file content, and that the rollback
      message names the rule id.)

## Feature 009 — `jss-lint explain`

- [x] CLI subcommand wiring — `jss-lint explain RULE-ID
      [--format {terminal,markdown}]` dispatches into
      `texlint.explain.render`; listing view (no rule id) supported;
      unknown rule id exits 2 with did-you-mean suggestions.
      (Shipped in the spec-009/010/015/016 CLI subcommand batch.)
- [x] Catalogue extension: add `explanation: str`,
      `example_bad: str | None`, `example_good: str | None` to
      every rule entry in `catalogue.yaml`. (Shipped: every rule
      carries a non-empty `explanation` (minimum-viable
      one-liner derived from message_template + guide_section);
      `example_bad` / `example_good` are independently optional
      OPTIONAL keys in the validator.)
- [x] `test_every_rule_has_explanation` contract test in
      `tests/unit/journals/jss/test_catalogue_citations.py`.
      (Shipped.)

## Feature 010 — `jss-lint init`

- [x] CLI subcommand wiring — `jss-lint init [PATH] [--force]
      [--dry-run] [--threshold T]` dispatches into
      `texlint.init.run`. Refusal-without-force exits 2; dry-run
      writes nothing. (Shipped.)
- [x] Precision-DB-aware suppression: query
      `eval/precision-history.db` per rule and emit suppressions
      for any rule below the `--threshold` (default 0.90).
      (Shipped: `texlint.init.run` reads the latest iteration's
      full-scope precision per rule and adds below-threshold rules
      to `ignore_rules` with audit-trail comments. Missing DB and
      NULL-precision rules fall back to no suppression.)
- [ ] Promote `tomli_w` from "hand-rolled TOML rendering" to a
      proper runtime dependency once the generated config gains
      structures (severity overrides, table-of-table sections)
      that the hand-roller can't easily produce.

## Feature 011 — Language Server

- [x] Add `pygls>=1.3` under a new `[project.optional-
      dependencies] lsp = [...]` group. (Shipped.)
- [x] `src/texlint/lsp/server.py` — pygls `LanguageServer`
      factory implementing didOpen / didChange (200ms debounce) /
      didSave / didClose / codeAction handlers plus the
      `jss-lint.applyAllFixes` workspace command. (Shipped.)
- [x] `src/texlint/lsp/cache.py` — `DocumentCache` keyed by
      `(uri, textDocument.version)`. (Shipped: 12 unit tests.)
- [x] `src/texlint/lsp/config_watch.py` — `reload(state, path,
      log)` handler invoked by the
      `workspace/didChangeWatchedFiles` feature. Malformed
      reloads keep the previous config + surface a
      `window/showMessage`. (Shipped.)
- [x] `tests/integration/test_lsp_session.py` — handler-level
      smoke tests (registered features, URI parsing, didOpen
      publishes, didClose clears, codeAction empty on cache
      miss). pygls 2.x doesn't ship a synchronous in-process
      test driver, so we exercise registered handlers
      directly. (Shipped: 10 tests.)
- [x] `jss-lint lsp` CLI subcommand. Lazy-imports pygls so the
      core CLI keeps working without the `[lsp]` extra; missing
      extra exits 2 with an install hint. (Shipped.)

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
      *Deferred*: JSS-ABBR-001 is a text-pattern rule with no
      cross-file scoping (no "definition on first use"
      semantics); a `check_project` body would be a trivial
      iterate-over-documents loop with no behavioural change.
      Will land alongside a real cross-file abbreviation
      sub-rule. Note added to
      `src/texlint/journals/jss/rules/abbreviations.py`.
- [x] `--no-resolve` CLI flag in `cli.py` — passes a
      `ParsedDocument` rather than auto-resolving.
      (Shipped as a reserved flag: it is wired through
      `cli_overrides` but has no observable effect today
      because the CLI does not currently auto-resolve. Lets
      users script against the flag ahead of the auto-resolve
      bridge.)
- [x] `JSS-PROJECT-001` (cycle) and `JSS-PROJECT-002`
      (missing reference) tool-side rules emitted by the
      resolver. (Shipped at
      `src/texlint/journals/jss/rules/project.py`.
      JSS-PROJECT-001 detects cycles by DFS over
      `ParsedProject.tree`; JSS-PROJECT-002 is a documented
      no-op stub until the resolver → ParsedProject bridge
      threads `missing` through. Not registered in the
      catalogue YAML — these are tool-side diagnostics.)

## Feature 014 — GitHub Action

- [ ] Action source repo — push the `action/` contents to a
      dedicated `kollerma/jss-style-checker-action` repository
      whose tags drive the marketplace listing. The release
      workflow at `.github/workflows/release-action.yml`
      handles the rolling-tag update once the dedicated repo
      exists.
- [x] Live smoke-test workflow at
      `.github/workflows/test-action.yml` — runs the action
      against `docs/jss-template/` and asserts SARIF presence +
      violation count. (Shipped: `uses: ./action`, runs on every
      PR + push to main, asserted by the YAML lint test.)
- [x] `--source-root` integration: forward the GitHub Actions
      checkout root to the spec-006 flag so SARIF URIs resolve
      to repo-relative paths in the Security tab. (Shipped: the
      composite action's lint step now passes
      `--source-root "$GITHUB_WORKSPACE"`; contract test at
      `tests/integration/test_action_manifest.py` guards the wiring.)

## Feature 015 — Conformance report

- [x] PDF rendering via WeasyPrint (gated behind
      `[project.optional-dependencies] pdf = ["weasyprint>=60"]`).
      (Shipped: `render_report(..., fmt="pdf")` returns PDF
      bytes; `report --format pdf --out FILE` writes the file;
      missing WeasyPrint raises `PdfNotAvailable` which the CLI
      converts into an install-hint.)
- [x] HTML rendering via the existing Jinja2 stack
      (`output/html_output.py` shares its template loader).
      (Shipped: `render_report(..., fmt="html")` renders the
      six-section template at
      `src/texlint/output/templates/conformance.html.j2`; covered
      by `tests/unit/test_report_html.py`.)
- [x] CLI subcommand `jss-lint report PATH [--format md]
      [--out FILE] [--title T] [--author A]` dispatches into
      `texlint.report.render_report`. (Shipped.)
- [x] Manuscript-metadata extraction from `\title{}` /
      `\author{}` / `\Plainauthor{}` macros at preamble parse
      time. (Shipped: `texlint.report.extract_metadata` walks the
      tex AST; the `report` subcommand uses extracted values when
      `--title` / `--author` are omitted; `\Plainauthor{}` wins
      over `\author{}` when both present.)

## Feature 016 — `jss-lint diff`

- [x] CLI subcommand `jss-lint diff OLD.json NEW.json
      [--ignore-line-drift]` dispatches into `texlint.diff.compare`.
      Schema mismatch on input exits 2; introduced > 0 exits 1.
      (Shipped.)
      (depends on Click sub-group migration).
- [x] Renderers: `--format terminal` (plain-text grouped
      sections), `--format markdown` (GitHub-flavoured
      CommonMark with H2 sub-sections), `--format json`
      (deterministic `{summary, fixed, introduced, unchanged}`
      shape via `sort_keys`). (Shipped.)
- [x] Schema validation of input JSON against the spec-001
      shape; mismatch exits 2. (Shipped: top-level keys +
      per-violation required keys via `texlint.diff.SchemaMismatch`
      + `validate_payload`.)
- [x] Populate `docs/jss-guide/rule-renames.json` with
      historical renames as they happen. (Shipped: a `_history`
      note explains why the map is empty — the two retired
      catalogue rules JSS-CITE-001 and JSS-ABBR-002 are
      RETIREMENTS, not renames, and belong in
      `retired_rule_ids`. Future spec PRs add real renames here.)

## Feature 017 — Recall evaluation

- [ ] **Hand-annotate the first 10 JSS papers** under
      `eval/recall-corpus/<paper-id>/`. The annotation TOML
      schema is documented in
      `eval/recall-corpus/README.md`. This is the most
      labour-intensive deferred item — read each paper end-
      to-end, identify every JSS-guide violation, record
      `(rule_id, file, line)` per FR-002.
- [x] `eval-jss recall` CLI subcommand with `--gate` and
      `--validate` flags. (Shipped: also `--corpus`,
      `--format {terminal|json}`, `--history-db`, `--no-record`.
      Empty corpus exits 0 with a friendly note. Persists each
      run to the recall_history table.)
- [x] `recall_history` SQLite table schema in
      `eval/precision-history.db` per data-model §3. (Shipped:
      schema + `record_recall()` / `latest_recall_per_rule()`
      helpers in `eval/history.py`.)
- [x] Combined precision + recall report column in
      `eval/report.py`. (Shipped: `eval-jss report --with-recall`
      adds Recall + F1 columns plus an aggregate footer row.)
- [x] `eval/badge.py` — emits shields.io endpoint JSON for
      the precision and recall badges. (Shipped: also covers F1.
      Has a CLI: `python -m eval.badge {precision|recall|f1} V`.)
- [x] `.github/workflows/publish-badges.yml` — push
      regenerated badge JSON to the `gh-pages` branch on
      every push to main. (Shipped: workflow renders via
      `python -m eval.badge`; pushes to gh-pages with the default
      GITHUB_TOKEN. Goes live the first time it runs on main.)
- [x] Update README to display the three badges
      (precision / recall / F1). (Shipped: README header carries
      shields.io endpoint badges pointing at
      `kollerma.github.io/jss-style-checker/badges/*.json`. The
      JSONs are populated by the deferred gh-pages workflow.)

## Tracking

This file is hand-edited. When a follow-up lands, check its
box and link to the PR. When new follow-ups surface during
implementation, add them under the relevant feature.
