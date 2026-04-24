# Spec 004 — End-of-Spec Summary

**Closed**: 2026-04-24
**Branch**: `004-jss-rule-modules`

## Scope delivered

- 15 rule modules (one per `catalogue.yaml` category) under
  `src/texlint/journals/jss/rules/`, implementing all **58 active rules**
  from spec 003's frozen catalogue.
- 3 smoke-rule retrofits completed: `cite_001_emph.py` retired (JSS-CITE-001
  was a catalogue retirement, not a retrofit), `bib_001_year.py` retrofitted
  as JSS-REFS-001, `src_001_width.py` retrofitted as JSS-WIDTH-001 with a
  configurable `ToolConfig.code_width` limit.
- Single-source-of-truth architecture: `tools/generate_catalogue_data.py`
  emits `src/texlint/journals/jss/_catalogue_data.py` from `catalogue.yaml`;
  rule modules import metadata from the generated file. `Severity.INFO`
  extension (API-additive) landed in the foundational PR to support the 4
  info-severity catalogue rules.
- Shared helpers in `rules/_helpers.py` (`_walk`, `_walk_with_ancestors`,
  `_walk_with_context`, `_iter_with_parent`, `_macro_args_text`,
  `_lineno_col`, `_is_inside_verbatim`, `_is_inside_comment`,
  `_is_inside_math`, `_is_in_prose_context`) — 100% branch coverage.
- `eval/review-skip-list.toml` extended with the 14 pre-populated
  `[[rules]]` entries listed in `contracts/ai-skip-list.md`.
- `scripts/eval-category.sh` + `human-review` UX (clickable
  `path:line:col` locators, progress counter, verdict legend, `b`-to-back
  undo).

## Quality gates

| Gate | Status | Evidence |
|---|---|---|
| 100% branch coverage across `src/texlint/journals/jss/rules/` | **PASS** | `pytest --cov=texlint.journals.jss.rules --cov-branch --cov-fail-under=100` — 1571 stmts, 936 branches, 100%. |
| Full test suite | **PASS** | 662 passed, 0 xfailed. |
| Catalogue consistency (R-1..R-9) | **PASS** | `tests/unit/journals/jss/test_catalogue_registration.py` fully green (no `xfail` markers remain). |
| Catalogue drift check | **PASS** | `tests/unit/journals/jss/test_catalogue_data_fresh.py`. |
| One-bad-fixture-per-rule (SC-001) | **PASS** | `tests/integration/test_full_catalogue_coverage.py` — every catalogue rule_id fires on its bad fixture. |
| Golden-path demo on `docs/jss-template/article.tex + refs.bib` (SC-002) | **9 warnings** | See "Golden-path findings" below. |
| Precision gate (SC-010) on the N≥10 floor | **NOT MEASURED** | See "Per-rule status" below. |

## Golden-path findings (`jss-lint docs/jss-template/...`)

Nine warnings fire on the canonical JSS template:

- `MARKUP-002` × 2 — "sandwich" mentioned unwrapped in prose.
- `CITE-002` × 1 — `\pkg{knitr}` lacks a same-paragraph citation.
- `CODE-003` × 1 — missing spaces around operators in a `\code{}` sample.
- `STRUCT-001` × 1 — no summary / discussion section before `\bibliography{}`.
- `REFS-003` × 3 (info) — three bib entries lack a `doi` field.
- `REFS-006` × 1 — one bib title's first word is lowercase.

All appear to be legitimate style issues in the template rather than
false positives. Exit code is 0 because none are `error` severity; per
the spec contract, these are reported but not suppressed.

## Per-rule corpus status (6-paper `examples/` corpus)

| Rule | Category | Hits | TP | FP | Unlabelled | Status |
|---|---|---:|---:|---:|---:|---|
| JSS-CITE-002 | citations | 1 | 1 | 0 | 0 | NOT MEASURED (N<10) |
| JSS-CITE-003 | citations | 0 | 0 | 0 | 0 | NOT MEASURED (N<10) |
| JSS-CITE-004 | citations | 0 | 0 | 0 | 0 | NOT MEASURED (N<10); in skip-list |
| JSS-REFS-001 | references | 1 | 0 | 0 | 1 | NOT MEASURED (N<10) |
| JSS-REFS-002 | references | 0 | 0 | 0 | 0 | NOT MEASURED; in skip-list |
| JSS-REFS-003 | references | 8 | 0 | 0 | 8 | NOT MEASURED (N<10) |
| JSS-REFS-004 | references | 0 | 0 | 0 | 0 | NOT MEASURED |
| JSS-REFS-005 | references | 0 | 0 | 0 | 0 | NOT MEASURED; in skip-list |
| JSS-REFS-006 | references | 1 | 0 | 0 | 1 | NOT MEASURED; in skip-list |
| JSS-REFS-007 | references | 0 | 0 | 0 | 0 | NOT MEASURED |
| JSS-BIBTEX-001 | bibtex | 0 | 0 | 0 | 0 | NOT MEASURED |
| JSS-BIBTEX-002 | bibtex | 0 | 0 | 0 | 0 | NOT MEASURED |
| JSS-BIBTEX-003 | bibtex | 1 | 0 | 0 | 1 | NOT MEASURED |
| JSS-BIBTEX-004 | bibtex | 0 | 0 | 0 | 0 | NOT MEASURED |
| JSS-PRE-001 | preamble | 0 | 0 | 0 | 0 | NOT MEASURED |
| JSS-PRE-002 | preamble | 4 | 0 | 0 | 4 | NOT MEASURED (N<10) |
| JSS-PRE-003..008 | preamble | various | | | | NOT MEASURED; PRE-007 has 4 hits |
| JSS-STRUCT-001..006 | structure | 1 total | 0 | 0 | 1 | NOT MEASURED |
| JSS-MARKUP-001 | markup | 0 | 0 | 0 | 0 | NOT MEASURED; in skip-list |
| JSS-MARKUP-002 | markup | 2 | 0 | 0 | 2 | NOT MEASURED |
| JSS-MARKUP-003..004 | markup | 0 | | | | NOT MEASURED |
| JSS-CODE-001..002 | code_style | 0 | | | | NOT MEASURED |
| JSS-CODE-003 | code_style | 8 | 0 | 0 | 8 | NOT MEASURED (N<10); in skip-list |
| JSS-WIDTH-001 | code_width | 0 | 0 | 0 | 0 | NOT MEASURED |
| JSS-NAME-001..002, JSS-TYPO-001..004, JSS-CAP-001..004, JSS-XREF-001..004, JSS-OPER-001..004, JSS-ABBR-001, JSS-HOUSE-001..003 | (various) | 0 | | | | NOT MEASURED |

**Summary**: 11 of 58 rules fired on the toy corpus. **Zero rules reach
the N=10 labelled-violation floor.** Every rule ships as NOT MEASURED
per FR-013.

## Re-measurement plan (SC-010)

Every rule is at "NOT MEASURED" because the corpus is still at 6 example
papers (5 Step-1 placeholders + 1 JSS template article). The unblocking
action is **corpus expansion to ~50 real JSS papers** — tracked as OQ-11
in `specs/003-jss-rule-catalogue/checklists/rule-catalogue-review.md`.

**What was attempted for corpus expansion** (deferred, not shipped in
spec 004):

- CRAN archive (`/src/contrib/Archive/<pkg>/<pkg>_<ver>.tar.gz`) is
  reachable; most packages ship `.Rnw` (Sweave) which jss-lint does not
  scan. A minority ship pre-built `.bib` (useful for future
  references/bibtex precision signal) and very few ship `.tex`/`.ltx`
  directly.
- arXiv e-prints (`http://arxiv.org/e-print/<id>`) ship real `.tex` but
  are typically not JSS-class (`llncs.cls` / other class files); they
  would not exercise JSS-specific rules.
- **JSS archive** (`jstatsoft.org`) is reachable. URL pattern for
  replication tarballs: scrape galley IDs from the article HTML (look
  for `/article/view/<vol>/<galleyId>`), download
  `/article/view/<vol>/<galleyId>`, filter for tarballs, and extract
  `.ltx` files under `<pkg>/inst/doc/`. Verified against `brms` (v080i01):
  `brms/inst/doc/brms_overview.ltx` is a real JSS paper with
  `\documentclass[article, nojss]{jss}`.

The galley-based JSS archive fetcher is the right next step — it
requires ~1.5–2 hours of work plus human curation of ~8 papers with
diverse citation / preamble / structure patterns. Track as a follow-up
PR titled "corpus: fetch real JSS papers via the galley URL pattern".

## Artefacts shipped

- `src/texlint/journals/jss/rules/` — 15 rule modules + `_helpers.py`.
- `src/texlint/journals/jss/_catalogue_data.py` — generated source of truth.
- `src/texlint/journals/jss/__init__.py` — `JSSJournal.categories()`
  returns 15 `RuleCategory`s in `ROLLOUT_ORDER`.
- `src/texlint/journals/jss/terms.py` — extended with
  `PUBLISHER_CANONICAL` / `JOURNAL_CANONICAL` for JSS-NAME-002.
- `src/texlint/api.py` — `Severity.INFO` added.
- `tools/generate_catalogue_data.py` — codegen.
- `tests/unit/rules/test_<category>.py` — 15 test modules.
- `tests/unit/journals/jss/rules/test_helpers.py` — helpers unit tests.
- `tests/unit/journals/jss/test_catalogue_registration.py` — R-1..R-9.
- `tests/unit/journals/jss/test_catalogue_data_fresh.py` — drift check.
- `tests/integration/test_full_catalogue_coverage.py` — SC-001.
- `tests/fixtures/violations/<category>/` — 116+ bad/good fixture pairs.
- `scripts/eval-category.sh` — per-category precision-gate wrapper.
- `eval/review-skip-list.toml` — 14 pre-populated `[[rules]]` entries.
- `eval/review.py` — skip-list loader extended to handle both formats.
- `eval/human_review.py` — UX: clickable locator, progress, verdict
  legend, back/undo.

## Deferred / follow-up

1. **Corpus expansion to ~50 papers (OQ-11)** — the dominant follow-up.
   JSS-archive galley-based fetch is the validated approach.
2. **Precision-gate measurements** — every rule flagged NOT MEASURED;
   the `--cov-fail-under=100` on the rule modules is the structural
   safety net until corpus data exists.
3. **Template-allowlist (SC-002)** — the golden-path demo shows 9
   legitimate warnings on the template; decide whether to address them
   in `docs/jss-template/` or add the rules to a template-allowlist
   that `jss-lint --template-mode` honours. Not blocking spec 004 close.
