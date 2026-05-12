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

## Rule catalogue follow-ups surfaced by recall annotation

New rule proposals and existing-rule behaviour fixes discovered
while hand-annotating the v1 recall corpus (`eval/recall-corpus/`).
Each item has reviewer/style-guide provenance and a concrete
corpus carrier so the change can be test-driven from real text.

- [ ] **JSS-PRE-009 — preamble must not undefine or redefine
      jss.cls-provided code environments** (`Code`, `CodeInput`,
      `CodeOutput`, `Sinput`, `Soutput`). Detect via
      `\let\Code\@undefined` (or `\renewenvironment{Code}`,
      `\lstnewenvironment{Code}`, `\let\CodeInput=\@undefined`,
      etc.) on any of the JSS-provided code env names.
      **Why**: jss.cls supplies a fancyvrb-based Code/CodeInput/
      CodeOutput / Sinput / Soutput stack so all submissions
      render code uniformly. Replacing them with a custom
      listings-based stack bypasses the JSS house style and
      structurally hides the manuscript's code from CODE-001/002/
      003 and WIDTH-001 (which target the JSS env names). No
      published JSS paper does this — the only carriers in the
      precision corpus are four CRAN vignettes from a single
      author group (pmclust, pbdMPI, pbdSLAP, MixfMRI), none of
      which appear in `eval/jss-archive.json`.
      **Carriers**: `pmclust/pmclust-include/00-preamble.tex:18-26`
      is the canonical example (`\let\Code\@undefined` followed
      by `\lstnewenvironment{Code}{...}`).
      **Severity**: error (replaces the JSS code surface entirely).
      **Authority**: §4.2 Code style + jss.cls (the env names
      themselves).

- [ ] **Bib-side rules should skip uncited entries**
      (`src/texlint/journals/jss/rules/references.py`,
      `bibtex.py`). `JSS-REFS-002/003/004/005/006/007` and
      `JSS-BIBTEX-002/003/004` currently walk every entry returned
      by `_iter_entries()`, regardless of whether any
      `\cite{}` / `\citep{}` / `\citet{}` / `\citealt{}` /
      `\citealp{}` actually references the entry's key. Uncited
      entries don't appear in the printed bibliography (BibTeX/
      biblatex filters them out), so reviewers never see them and
      annotators correctly skip them — but the linter still fires,
      which inflates precision-side FP counts on the precision
      corpus and clutters the report.
      **Fix**: build the `\cite*{...}`-referenced key set per
      ParsedDocument once (helper in `_helpers.py`), then have
      each bib rule short-circuit when `entry.key not in
      cited_keys`. Keep `JSS-BIBTEX-001` (empty key) and the
      key-uniqueness check `JSS-BIBTEX-002` walking all entries —
      those are bib-hygiene rules independent of citation use.
      **Carrier**: pmclust's `pmclust-include/pmclust.bib`
      contains several entries (e.g. unreferenced book chapters)
      that fire `JSS-REFS-003` / `REFS-007` despite being absent
      from the printed bibliography.
      **Severity**: existing rule severity; behaviour fix only.

- [ ] **`JSS-CAP-002` should walk the optional `[short]` arg of
      `\section{...}` / `\subsection{...}` / `\subsubsection{...}`**
      (`src/texlint/journals/jss/rules/capitalization.py`). The rule
      currently only inspects the mandatory `{long}` arg, so titles
      written as `\subsection[Quick Start]{Quick Start}` go unflagged
      even when the long form is title-style instead of sentence-style.
      **Carriers**: pmclust `01-introduction.tex:38` (`System
      Requirement`), `:67` (`Quick Start`); robustlmm
      `simulationStudies.Rnw:290, 321, 379, 381, 449, 702, 704, 752,
      791` — 9 instances in a single paper. Both papers exhibit
      the same pattern.
      **Fix**: when the macro carries a `[<short>]` arg, lint *both*
      the short and long form (each is independently visible in the
      ToC vs body and either can violate sentence-style).
      **Severity**: existing CAP-002 severity (warning).

- [ ] **`JSS-MARKUP-002` / `JSS-MARKUP-003` should also flag known
      package / function names wrapped in `\texttt{}`**
      (`src/texlint/journals/jss/rules/markup.py`). Both rules
      currently inspect prose only; bare names wrapped in the wrong
      macro (`\texttt{MASS}` instead of `\pkg{MASS}`,
      `\texttt{hubers}` instead of `\code{hubers}`) are invisible.
      **Carrier**: robustlmm `simulationStudies.Rnw:591` — both
      defects on a single line. Likely common across the corpus
      (authors reach for `\texttt{}` because it renders the same).
      **Fix**: extend the rules to also walk `\texttt{...}` /
      `\verb|...|` arguments, matching the inner token against the
      same package-name / R-function lookups already used for prose.
      **Severity**: existing rule severity (warning each).

- [ ] **`JSS-REFS-006` brace-defeats-`_starts_with_package_idiom`
      exemption** (`src/texlint/journals/jss/rules/references.py`).
      The exemption is meant to allow `vegan: Community Ecology
      Package` style titles where the lowercase word before `:` is
      the package name. When the package name is wrapped in `{}`
      to preserve case (`{robustlmm}: An ...`,
      `{robustvarComp}: Robust ...`), the exemption no longer
      matches and REFS-006 false-fires.
      **Carriers**: robustlmm `simulationStudies.bib:18` (robustlmm
      itself), `:94` (robustvarComp).
      **Fix**: strip `{...}` wrapping from the leading token before
      checking the package-idiom exemption.
      **Severity**: existing rule severity (warning).

- [ ] **`JSS-CAP-003` is over-eager on technical identifiers in
      captions** (`src/texlint/journals/jss/rules/capitalization.py`).
      Captions of the form `Convergence simulation study, N/N case,
      bias, ...` get flagged because tokens like `N/N`, `RSEn`,
      `lme`, `t3/t3` look like non-sentence-case violations. These
      are technical identifiers / short variable / package names
      and shouldn't be lower-cased.
      **Carriers**: robustlmm `simulationStudies.Rnw:608`, `:654`
      (and likely many other technical-stats papers).
      **Fix**: extend the sentence-style check to skip tokens that
      already appear inside `\code{}` / `\pkg{}` / `\proglang{}` /
      `\texttt{}` macros within the same caption, AND tokens that
      contain mixed case + a digit (e.g. `t3`, `RSEn`) or a `/`
      separator (e.g. `N/N`).
      **Severity**: existing rule severity (warning).

- [ ] **`JSS-REFS-003` (DOI advisory) entry-type coverage is too
      narrow + DOI-in-wrong-field anti-pattern is missed**
      (`src/texlint/journals/jss/rules/references.py`).
      Two related gaps:

      *(a) Entry-type filter.* The rule currently fires on a small
      subset of entries — pmclust (6/15 fire; 9 missed), robustlmm
      (5/16 fire; 11 missed), CARBayesST (37/65 fire; 28 missed)
      all showed real DOI-missing entries that didn't trigger.
      Likely scoped to `@ARTICLE` with a `journal` field set,
      ignoring `@MISC`, `@Manual`, `@incollection`, `@book` etc.
      that legitimately have DOIs.
      **Carriers**: pmclust `pmclust.bib` (Chen2012pmclustpackage,
      Chen2012pbdMPIpackage, Schmidt2013pbdDEMOpackage, Rcore,
      Yu2010 etc.); robustlmm `simulationStudies.bib` (most
      package-archive @Manual / @MISC entries); CARBayesST
      `JSS2728.bib` (~28 entries spanning JSS articles, Wiley /
      Springer / Elsevier journal articles, Springer & Chapman
      books, R-package @Manuals).

      *(b) DOI in wrong field.* When a DOI exists but is recorded
      inside `pages = "..."` or `url = "..."` instead of a proper
      `doi = "..."` field, the rule misses it (it only looks at
      `doi=`). This is a real anti-pattern: `pages` ends up in
      the rendered bibliography in unexpected ways, and `url=`
      with a `dx.doi.org` link is non-canonical.
      **Carriers**: CARBayesST `JSS2728.bib` — `haining2010`
      (`pages = "123-131, DOI:10.1016/j.sste.2010.03.006"`),
      `lee2022` (`pages = "https://doi.org/10.1016/j.spasta.2021.100508"`),
      `leroux2000` (`url = "http://dx.doi.org/10.1007/978-1-4612-1284-3_4"`).

      **Fix**: drop the entry-type filter — *any* entry whose
      published form has a DOI on Crossref should be flagged when
      `doi` is missing. Additionally scan `pages` and `url` for
      embedded DOIs (regex `10\.\d+/\S+`); when found, fire a
      distinct sub-message ("DOI exists but is recorded in the
      wrong field; move to `doi=`") so the author knows the
      defect is field-placement, not absence.
      **Severity**: info (advisory) — unchanged.

- [ ] **`JSS-REFS-004` (proglang / pkg / code markup in bib titles)
      scope is incomplete** (`src/texlint/journals/jss/rules/references.py`).
      The rule fires on a fraction of real cases: pmclust caught
      3 of 11 cases the annotator marked; robustlmm caught 5 of 14.
      Common miss pattern: `note = {R package version 0.1-5}` and
      similar where `R` should be `\proglang{R}` or the package
      name in `title=` should be `\pkg{name}`.
      **Carriers**: pmclust `pmclust.bib:1, 77, 104, 112, 127,
      134, 141, 177`; robustlmm `simulationStudies.bib:18, 29,
      66, 74, 85, 94, 113, 121, 129`.
      **Fix**: extend the rule to also inspect the `note=` field
      and to recognise the canonical R-package-name lookup that
      MARKUP-002 already maintains.
      **Severity**: existing rule severity (warning).

- [ ] **JSS-PRE-010 — Sweave/knitr preamble sets the JSS-standard
      ``options()`` in an early hidden chunk**. The JSS author
      template (`docs/jss-template/article.Rnw`) prescribes:

      ```r
      <<preliminaries, echo=FALSE, results=hide>>=
      options(prompt = "R> ", continue = "+  ",
              width = 70, useFancyQuotes = FALSE)
      @
      ```

      Each option has a concrete house-style consequence:
      `prompt`/`continue` produce the canonical "R>"/"+ " prompts
      in Sinput blocks; `width = 70` (or any value ≤77) keeps
      rendered Soutput inside the JSS text width — directly
      affecting JSS-WIDTH-001 recall on the rendered .tex (without
      it, R defaults to 80 and routinely overflows);
      `useFancyQuotes = FALSE` suppresses curly Unicode quotes in
      Soutput, which clash with the JSS monospace font and break
      copy-paste of code.

      **Carriers** (5 of 10 fully missing, 2 partial across the v1
      recall corpus): clifford `clifford.Rnw`, cusp `Cusp-JSS.Rnw`,
      mdsOpt `mdsOpt.ltx`, pmclust `pmclust-guide.Rnw`, rstpm2
      `multistate.Rnw` set neither; CARBayesST sets prompt but not
      width; robustlmm sets width but not prompt.

      **Detection**: scan `.Rnw`/`.Rmd` for an early chunk (before
      `\begin{document}` or within the first ~3 chunks of the
      manuscript body) that calls `options(...)` with all four
      keys above set to JSS values (`prompt="R> "`, `continue="+  "`,
      `width <= 77`, `useFancyQuotes = FALSE`). Fire one violation
      per missing key, or a single composite violation listing the
      keys that are absent.

      **Severity**: warning.
      **Surfaces**: `.Rnw`, `.Rmd` only — non-Sweave manuscripts
      can't run R `options()` and shouldn't be flagged.

- [ ] **JSS-CITE-005 — every `\cite*{key}` resolves to a `@type{key,...}`
      in the document's `\bibliography{}`-referenced files**. LaTeX
      itself reports an "undefined citation" warning at typeset
      time and renders the unresolved citation as `?`, but the
      defect frequently slips through author proofreading (rendered
      `?` is easy to miss in a busy paragraph) and lands in submitted
      manuscripts.
      **Carrier**: clifford `clifford.Rnw:406` —
      `\cite{chisholm2012}`; the bib has `chisolm2012` (missing
      second 'h'). One typo, but a clear shape: cite key not in
      the union of bib-entry keys collected from every `.bib` in
      the same `ParsedDocument`.
      **Detection**: build the bib-key set per `ParsedDocument`
      (same helper as the "skip uncited entries" follow-up needs);
      walk every `\cite` / `\citet` / `\citep` / `\citealt` /
      `\citealp` / `\citeauthor` / `\citeyear` / `\nocite` /
      `\shortcites` argument; split on commas; for each key not
      in the set, fire one violation at the cite-macro line.
      **Severity**: error — the rendered manuscript visibly breaks.
      **Authority**: §3.2 Citations + general LaTeX hygiene.

- [ ] **JSS-XREF-005 — every `\ref{X}` / `\eqref{X}` / `\pageref{X}`
      resolves to a `\label{X}` somewhere in the document**. Same
      class of defect as JSS-CITE-005 but on the cross-reference
      side: LaTeX renders an unresolved reference as `??`, which
      is also easy to miss. JSS-XREF-001 / JSS-XREF-004 currently
      only check that figures / tables / equations carry labels
      (label *presence*); they don't check the inverse direction
      (reference *resolution*).
      **Carrier**: not yet observed in the v1 recall corpus, but
      the check is symmetric with JSS-CITE-005 and the same
      ParsedDocument scan trivially produces it.
      **Detection**: collect the union of `\label{X}` arguments
      across all `tex_files`; walk every `\ref`/`\eqref`/`\pageref`/
      `\autoref`/`\Cref`/`\cref` argument; flag any key not in
      the label set.
      **Severity**: error.
      **Authority**: §4.5 Cross-references + general LaTeX hygiene.

## Tracking

This file is hand-edited. When a follow-up lands, check its
box and link to the PR. When new follow-ups surface during
implementation, add them under the relevant feature.
