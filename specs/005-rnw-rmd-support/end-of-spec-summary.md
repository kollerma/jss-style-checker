# Spec 005 — End-of-Spec Summary

**Closed**: 2026-04-24 (Phases 1–6 all complete; corpus grown to 50 papers).
**Branch**: `005-rnw-rmd-support`

## Scope delivered

- `.Rnw` manuscripts (Sweave / knitr) lint end-to-end. R code chunks
  are stripped to equivalent-length whitespace before pylatexenc runs;
  line numbers remain source-authoritative.
- `.Rmd` manuscripts (R Markdown) lint end-to-end. A hand-rolled
  tokenizer (no `markdown-it-py` / `mistune` dep) segments frontmatter
  / headings / prose / fenced code blocks; prose blocks are
  additionally parsed as raw-LaTeX islands so math-masking and
  citation-macro rules fire on inline `$math$`, `\ref{...}`,
  `\citep{...}`, etc.
- Line-number translation for Rmd fragments is handled via an
  `_OffsetWalker` proxy around pylatexenc's walker — violations
  report back in source-space on the `.Rmd` file.
- `Rule.formats` semantics extended from file-suffix filter to
  input-format filter (`"tex"` / `"rnw"` / `"rmd"` / `"bib"`).
- Preamble category rules (JSS-PRE-001..008) narrowed to
  `{"tex", "rnw"}` per FR-020; they surface in
  `ComplianceReport.skipped_rules` when running against `.Rmd`.
- `--verbose` terminal output renders a skipped-rules table; JSON
  output always includes a `skipped_rules` key (back-compat additive).
- Rule-module audit: markup, naming, crossrefs, code_style, citations,
  structure, typography, house_style, abbreviations, capitalization,
  operators migrated from `doc.tex_files` to `doc.all_tex_like()` so
  they lint Rmd prose fragments alongside native `.tex` files.
- **Phase 6 (US4) — corpus expansion + `--by-format`:**
  - `eval-jss report --by-format` partitions precision rows by the
    violating file's suffix (`tex` / `rnw` / `rmd` / `bib`). Mutually
    exclusive with `--by-source`. Per-format rows are informational;
    only overall rows gate the 90% threshold.
  - New `violations.file_suffix` column (idempotent migration in
    `db.init`); `scan._persist_violations` populates it from the
    linter JSON's `file` field.
  - `eval.scan._tex_and_bib` → `_source_files`: now accepts
    `.Rnw` / `.Rmd` and recurses into `vignettes/` when the paper
    dir has no top-level source files (CRAN tarballs nest this way).
  - Fragment-level `JSS-PARSE-000` emitted from Rmd prose blocks is
    now silenced at parse time. pylatexenc is strict; prose that
    discusses regex or shell syntax often contains stray `$` or `{`
    that are not authoring errors. Tokenizer-level parse failures
    (unterminated fence, malformed frontmatter) still fire.
- **Corpus expansion (50 papers):** `eval/corpus-manifest.csv` grew
  from 6 manual rows to 50 rows (6 manual + 44 CRAN; 18 `.Rnw` + 26
  `.Rmd` on the CRAN side). All CRAN rows SHA256-pinned and
  reproducible via `eval-jss corpus fetch`. Payloads are
  `.gitignore`d under `examples/cran_*/`.

## Quality gates

| Gate | Status | Evidence |
|---|---|---|
| 100% branch coverage across `src/texlint/journals/jss/rules/` | **PASS** | 1572 statements, 936 branches — 100%. |
| Full test suite | **PASS** | 783 tests pass; 0 xfailed. |
| Catalogue consistency (R-1..R-9) | **PASS** | Test R-7 updated to allow `frozenset({"tex", "rnw"})` in addition to `None`. |
| Rnw line-count invariant (S-1) | **PASS** | `test_rnw_stripper.py::TestLineCountInvariant` — 6 cases. |
| Rmd tokenizer invariants (M-1..M-7) | **PASS** | `test_rmd_parser.py` — 20 cases. |
| FR-015 regression (.tex + .bib unchanged) | **PASS** | On the 6-paper `.tex`-only corpus the violation set is byte-identical pre- and post-spec-005 (32 rows, zero delta). `jss-lint docs/jss-template/article.tex refs.bib` still produces the same 9 findings as the spec-004 baseline. |
| SC-001 (Rnw prose hit / chunk silence) | **PASS** | `test_rnw_end_to_end.py::test_markup_rule_fires_on_prose_not_chunk`. |
| SC-002 (Rmd prose hit / fence silence / frontmatter silence) | **PASS** | `test_rmd_end_to_end.py` — 4 cases. |
| SC-006 (per-format precision partitioning) | **PASS** | `test_report.py` — 5 new by-format cases. |

## Rule-by-rule corpus status

The `.tex`-only 6-paper corpus behaves identically to the spec 004
end-of-spec summary (see `specs/004-jss-rule-modules/end-of-spec-summary.md`).

The corpus now also includes 44 CRAN vignettes (18 `.Rnw` + 26
`.Rmd`) sourced from `lme4`, `Matrix`, `car`, `AER`, `partykit`,
`betareg`, `sandwich`, `effects`, `lattice`, `survey`, `mvtnorm`,
`np`, `xts`, `pls`, `multcomp`, `robustbase`, `strucchange`, `zoo`,
`rpart`, `stringr`, `ggplot2`, `forecast`, `plm`, `dplyr`, `tidyr`,
`purrr`, `tibble`, `readr`, `lubridate`, `broom`, `fs`, `knitr`,
`DBI`, `forcats`, `glue`, `xml2`, `httr`, `rvest`, `data.table`,
`brms`, `rstanarm`, `glmnet`, `caret`, `rstan`. A full
`eval-jss scan --force` runs in ~11s and produces ~2,700 violations
(1523 Rmd + 1186 Rnw + 966 bib + 28 tex). 39 papers scan cleanly;
11 hit parser-level failures — see "Corpus-surfaced follow-ups" below.

## Corpus-surfaced follow-ups

The expanded corpus revealed 11 parse failures that are **not**
spec-005 regressions but are worth tracking as separate backlog:

- **`brms` — PyYAML `!r` custom tag rejection.** `brms` Rmd
  vignettes declare `params: EVAL: !r identical(...)`. PyYAML's
  `safe_load` rejects unknown tags by design. Fix: swap to a loader
  that ignores unknown YAML tags (coerce to string). Low-effort.
- **`rstanarm` — unterminated fenced code block.** Legitimate
  tokenizer-level parse failure (the Rmd source itself has an
  unclosed fence). May be a real author-side bug worth reporting
  upstream.
- **`sandwich` / `effects` / `robustbase` — Sweave `Sinput`/`Soutput`
  environments.** These environments appear in raw `.Rnw` when
  authors hand-edit verbatim output for demonstration. They are
  absent from pylatexenc's macro spec. Fix: either strip them like
  R chunks, or register them with pylatexenc's environment spec.
- **`partykit` / `strucchange` / `zoo` / `betareg` — brace /
  environment mismatches.** These compile under `pdflatex` but
  pylatexenc's strict AST parser rejects them. Likely candidates
  for `tolerant_parsing=True` on the Rnw path (or targeted macro
  additions).
- **`rpart` / `robustbase` — duplicate bib keys.** Real source-side
  issues (`Chen07` duplicated in `rpart/refer.bib`; `url` field
  duplicated in `robustbase/xtraR/refs.bib`). These are legitimate
  findings the harness should surface — but they currently get
  reported as `JSS-PARSE-000` rather than routed through a dedicated
  bib-hygiene rule.

## Deferred / follow-up

All Phase 6 items (T038–T044) landed in this spec. No blocking
follow-ups remain. The parser-level backlog above is tracked as
independent low-priority work that doesn't affect shipping this
spec.

**Phase 7 polish (T045–T051)** delivered inline:
- T045 Full test suite green — **done** (783 passed, 0 xfailed).
- T046 Branch-coverage gate across rules — **done** (100%).
- T047 Golden-path demo — **done** (9 findings, matches baseline).
- T048 Full-catalogue-coverage test — still **green** (every catalogue
  rule fires on its bad fixture, unchanged from spec 004).
- T049 End-of-spec-summary.md — **done** (this file).
- T050 Agent-context update — **done** in the plan phase.
- T051 Checklist close — **done**;
  `specs/005-rnw-rmd-support/checklists/requirements.md` — 0 open items.

## Spec drift reconciled

1. **Markdown parser choice**: Q1 of `/speckit.clarify` recorded
   `markdown-it-py`. The `/speckit.plan` input superseded this with
   "hand-roll a small tokenizer; avoid `markdown-it-py` / `mistune`".
   The hand-rolled state machine in `core/rmd_parser.py` matches the
   plan input; spec Clarifications + Assumptions were annotated to
   reflect the supersession. See `research.md §2`.

## Artefacts shipped

- `src/texlint/core/parser.py` — `strip_rnw_chunks`, `parse_rnw_file`,
  `parse_tex_source`, `parse_rmd_file`.
- `src/texlint/core/rmd_parser.py` — new module, ~260 lines.
- `src/texlint/core/engine.py` — `parse_document` dispatch,
  `UnsupportedSuffixError`, `run()` populates `skipped_rules`.
- `src/texlint/api.py` — `ParsedRmdFile` + 3 helper dataclasses,
  `SkippedRule`, `ParsedDocument.rmd_files` + `all_tex_like()`,
  `ComplianceReport.skipped_rules`, `Rule.formats` docstring update,
  `_file_format()` helper.
- `src/texlint/output/terminal.py` — verbose skipped-rules table.
- `src/texlint/output/json_output.py` — `skipped_rules` top-level key.
- `src/texlint/journals/jss/rules/preamble.py` — 8 rules narrowed to
  `formats={"tex", "rnw"}`; `_rule()` helper accepts `formats` kwarg.
- 11 other rule modules — migrated from `doc.tex_files` to
  `doc.all_tex_like()`.
- `tests/fixtures/compliant/minimal.Rnw`, `minimal.Rmd`.
- `tests/fixtures/violations/rnw/JSS-MARKUP-002-bad.Rnw`.
- `tests/fixtures/violations/rmd/JSS-MARKUP-002-bad.Rmd` + 3
  malformed fixtures.
- `tests/unit/test_rnw_stripper.py` — 12 tests.
- `tests/unit/test_rmd_parser.py` — 20 tests.
- `tests/integration/test_rnw_end_to_end.py` — 4 acceptance tests.
- `tests/integration/test_rmd_end_to_end.py` — 7 acceptance tests.
- `tests/integration/test_skipped_rules.py` — 5 skipped-rule tests.
- `pyproject.toml` — `PyYAML>=6.0` promoted to runtime dep.
- `eval/corpus-manifest.csv` — 44 CRAN rows added (SHA256-pinned).
- `eval/schema.sql` + `eval/db.py` — `violations.file_suffix` column
  with idempotent `ALTER TABLE ... ADD COLUMN` migration.
- `eval/scan.py` — `_source_files` accepts `.Rnw` / `.Rmd` with
  `vignettes/` subdir fallback; persists `file_suffix`.
- `eval/report.py` — `compute_precision_by_format`, `--by-format`
  rendering, `PrecisionTable.breakdown` field.
- `eval/cli.py` — `--by-format` flag (mutually exclusive with
  `--by-source`).
- `tests/eval/test_report.py` — 5 new by-format tests.
- `.gitignore` — `examples/cran_*/` (payloads reproducible from
  manifest), `.claude/scheduled_tasks.lock`.
