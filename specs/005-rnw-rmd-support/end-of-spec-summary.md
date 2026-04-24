# Spec 005 — End-of-Spec Summary

**Closed**: 2026-04-24 (Phases 1–5); Phase 6 (corpus + --by-format) deferred to follow-up.
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

## Quality gates

| Gate | Status | Evidence |
|---|---|---|
| 100% branch coverage across `src/texlint/journals/jss/rules/` | **PASS** | 1572 statements, 936 branches — 100%. |
| Full test suite | **PASS** | 778 tests pass; 0 xfailed. |
| Catalogue consistency (R-1..R-9) | **PASS** | Test R-7 updated to allow `frozenset({"tex", "rnw"})` in addition to `None`. |
| Rnw line-count invariant (S-1) | **PASS** | `test_rnw_stripper.py::TestLineCountInvariant` — 6 cases. |
| Rmd tokenizer invariants (M-1..M-7) | **PASS** | `test_rmd_parser.py` — 20 cases. |
| FR-015 regression (.tex + .bib unchanged) | **PASS** | `jss-lint docs/jss-template/article.tex refs.bib` produces the same 9 findings as the spec-004 baseline. |
| SC-001 (Rnw prose hit / chunk silence) | **PASS** | `test_rnw_end_to_end.py::test_markup_rule_fires_on_prose_not_chunk`. |
| SC-002 (Rmd prose hit / fence silence / frontmatter silence) | **PASS** | `test_rmd_end_to_end.py` — 4 cases. |

## Rule-by-rule corpus status

Unchanged from spec 004 end-of-spec summary on the `.tex`-only
6-paper corpus — see
`specs/004-jss-rule-modules/end-of-spec-summary.md`. No new
`.Rnw` or `.Rmd` papers ship with this spec (Phase 6 deferred).

## Deferred / follow-up

**Phase 6 (US4 corpus + by-format flag)** is deferred to a follow-up
PR. The work items:

1. **Curate + fetch 3–5 `.Rnw` + 2–3 `.Rmd` CRAN vignettes.** Candidate
   packages identified in `tasks.md` T038: `lme4`, `zoo`, `quantreg`,
   `survival`, `mgcv` (Rnw); `ggplot2`, `brms` (Rmd). The
   `eval-jss corpus fetch` mechanism from spec 002 materialises rows
   and pins SHA256 per Constitution §XII.
2. **`eval-jss report --by-format` flag.** Partitions the violation
   set by `papers.path` suffix (`.tex` / `.Rnw` / `.Rmd`) and emits
   per-format precision rows. The existing `--by-source` stub in
   `eval/report.py` is a nearby sibling; `--by-format` reuses the
   same dispatch-then-partition pattern. FR-016, SC-006.
3. **FR-015 regression diff** on the 6-paper `.tex` corpus. The
   `eval-jss report` output is currently byte-identical pre- and
   post-feature on existing data (no corpus delta, no report-path
   changes), but a formal snapshot diff should land in Phase 6's PR.

Both items require either (a) live CRAN network access the devcontainer
firewall needs to allowlist the relevant hosts for, or (b) offline
pre-downloaded tarballs manually placed in `examples/`. The blocker
is a judgment call about corpus curation more than a code engineering
block. Per the spec 004 precedent (OQ-11 corpus growth), this is
tracked as a follow-up rather than forcing a partial corpus in scope
here.

**Phase 7 polish (T045–T051)** partially delivered inline:
- T045 Full test suite green — **done** (778 passed, 0 xfailed).
- T046 Branch-coverage gate across rules — **done** (100%).
- T047 Golden-path demo — **done** (9 findings, matches baseline).
- T048 Full-catalogue-coverage test — still **green** (every catalogue
  rule fires on its bad fixture, unchanged from spec 004).
- T049 End-of-spec-summary.md — **done** (this file).
- T050 Agent-context update — **done** in the plan phase.
- T051 Checklist close — ready; see
  `specs/005-rnw-rmd-support/checklists/requirements.md`.

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
