# Eval-improve log

Each section below is one iteration of the eval-improve loop (see
`eval/README.md`). Stats are snapshots taken at record time; the
machine-readable copy lives in `eval/precision-history.db`.

## Iteration 1 — 2026-04-24T14:39:31Z — baseline

- **Corpus size:** 50 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=25, pinned=11

**Note:** Iteration 1: 50 CRAN papers, pre-loop baseline. 2 labels (from placeholder corpus); 3846 pending across full scope.

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 1 | 0 | 73 | 100.00% | PASS |
| citation | JSS-CITE-003 | 0 | 0 | 1 | — | NOT MEASURED |
| citation | JSS-CITE-004 | 0 | 0 | 1 | — | NOT MEASURED |
| unknown | JSS-ABBR-001 | 0 | 0 | 5 | — | NOT MEASURED |
| unknown | JSS-BIBTEX-002 | 0 | 0 | 1 | — | NOT MEASURED |
| unknown | JSS-BIBTEX-003 | 0 | 0 | 84 | — | NOT MEASURED |
| unknown | JSS-BIBTEX-004 | 0 | 0 | 18 | — | NOT MEASURED |
| unknown | JSS-CAP-001 | 0 | 0 | 8 | — | NOT MEASURED |
| unknown | JSS-CAP-002 | 0 | 0 | 132 | — | NOT MEASURED |
| unknown | JSS-CAP-003 | 0 | 0 | 16 | — | NOT MEASURED |
| unknown | JSS-CODE-001 | 0 | 0 | 1 | — | NOT MEASURED |
| unknown | JSS-CODE-003 | 0 | 0 | 52 | — | NOT MEASURED |
| unknown | JSS-HOUSE-001 | 0 | 0 | 164 | — | NOT MEASURED |
| unknown | JSS-HOUSE-002 | 0 | 0 | 4 | — | NOT MEASURED |
| unknown | JSS-HOUSE-003 | 0 | 0 | 11 | — | NOT MEASURED |
| unknown | JSS-MARKUP-001 | 0 | 0 | 706 | — | NOT MEASURED |
| unknown | JSS-MARKUP-002 | 0 | 0 | 248 | — | NOT MEASURED |
| unknown | JSS-MARKUP-003 | 0 | 0 | 961 | — | NOT MEASURED |
| unknown | JSS-MARKUP-004 | 0 | 0 | 93 | — | NOT MEASURED |
| unknown | JSS-NAME-001 | 0 | 0 | 24 | — | NOT MEASURED |
| unknown | JSS-NAME-002 | 0 | 0 | 26 | — | NOT MEASURED |
| unknown | JSS-OPER-001 | 0 | 0 | 34 | — | NOT MEASURED |
| unknown | JSS-OPER-002 | 0 | 0 | 36 | — | NOT MEASURED |
| unknown | JSS-OPER-003 | 0 | 0 | 37 | — | NOT MEASURED |
| unknown | JSS-OPER-004 | 0 | 0 | 10 | — | NOT MEASURED |
| unknown | JSS-PRE-001 | 0 | 0 | 29 | — | NOT MEASURED |
| unknown | JSS-PRE-002 | 0 | 0 | 4 | — | NOT MEASURED |
| unknown | JSS-PRE-003 | 0 | 0 | 13 | — | NOT MEASURED |
| unknown | JSS-PRE-006 | 0 | 0 | 3 | — | NOT MEASURED |
| unknown | JSS-PRE-007 | 0 | 0 | 20 | — | NOT MEASURED |
| unknown | JSS-REFS-001 | 0 | 0 | 76 | — | NOT MEASURED |
| unknown | JSS-REFS-002 | 0 | 0 | 1 | — | NOT MEASURED |
| unknown | JSS-REFS-003 | 0 | 0 | 581 | — | NOT MEASURED |
| unknown | JSS-REFS-004 | 0 | 0 | 68 | — | NOT MEASURED |
| unknown | JSS-REFS-005 | 0 | 0 | 7 | — | NOT MEASURED |
| unknown | JSS-REFS-006 | 0 | 0 | 103 | — | NOT MEASURED |
| unknown | JSS-REFS-007 | 0 | 0 | 11 | — | NOT MEASURED |
| unknown | JSS-STRUCT-001 | 0 | 0 | 21 | — | NOT MEASURED |
| unknown | JSS-STRUCT-004 | 0 | 0 | 2 | — | NOT MEASURED |
| unknown | JSS-STRUCT-005 | 0 | 0 | 3 | — | NOT MEASURED |
| unknown | JSS-TYPO-001 | 0 | 0 | 12 | — | NOT MEASURED |
| unknown | JSS-TYPO-003 | 0 | 0 | 1 | — | NOT MEASURED |
| unknown | JSS-TYPO-004 | 0 | 0 | 15 | — | NOT MEASURED |
| unknown | JSS-XREF-001 | 0 | 0 | 8 | — | NOT MEASURED |
| unknown | JSS-XREF-002 | 0 | 0 | 77 | — | NOT MEASURED |
| unknown | JSS-XREF-004 | 0 | 0 | 21 | — | NOT MEASURED |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 1 | 0 | 40 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 0 | 0 | 2 | — | NOT MEASURED |
| unknown | JSS-BIBTEX-002 | 0 | 0 | 1 | — | NOT MEASURED |
| unknown | JSS-BIBTEX-003 | 0 | 0 | 84 | — | NOT MEASURED |
| unknown | JSS-BIBTEX-004 | 0 | 0 | 18 | — | NOT MEASURED |
| unknown | JSS-CAP-001 | 0 | 0 | 3 | — | NOT MEASURED |
| unknown | JSS-CAP-002 | 0 | 0 | 12 | — | NOT MEASURED |
| unknown | JSS-CAP-003 | 0 | 0 | 5 | — | NOT MEASURED |
| unknown | JSS-CODE-003 | 0 | 0 | 23 | — | NOT MEASURED |
| unknown | JSS-HOUSE-001 | 0 | 0 | 33 | — | NOT MEASURED |
| unknown | JSS-HOUSE-002 | 0 | 0 | 4 | — | NOT MEASURED |
| unknown | JSS-HOUSE-003 | 0 | 0 | 2 | — | NOT MEASURED |
| unknown | JSS-MARKUP-001 | 0 | 0 | 238 | — | NOT MEASURED |
| unknown | JSS-MARKUP-002 | 0 | 0 | 130 | — | NOT MEASURED |
| unknown | JSS-MARKUP-003 | 0 | 0 | 203 | — | NOT MEASURED |
| unknown | JSS-MARKUP-004 | 0 | 0 | 21 | — | NOT MEASURED |
| unknown | JSS-NAME-001 | 0 | 0 | 7 | — | NOT MEASURED |
| unknown | JSS-NAME-002 | 0 | 0 | 26 | — | NOT MEASURED |
| unknown | JSS-OPER-001 | 0 | 0 | 9 | — | NOT MEASURED |
| unknown | JSS-OPER-002 | 0 | 0 | 27 | — | NOT MEASURED |
| unknown | JSS-OPER-003 | 0 | 0 | 20 | — | NOT MEASURED |
| unknown | JSS-PRE-001 | 0 | 0 | 8 | — | NOT MEASURED |
| unknown | JSS-PRE-002 | 0 | 0 | 4 | — | NOT MEASURED |
| unknown | JSS-PRE-003 | 0 | 0 | 6 | — | NOT MEASURED |
| unknown | JSS-PRE-006 | 0 | 0 | 2 | — | NOT MEASURED |
| unknown | JSS-PRE-007 | 0 | 0 | 8 | — | NOT MEASURED |
| unknown | JSS-REFS-001 | 0 | 0 | 76 | — | NOT MEASURED |
| unknown | JSS-REFS-002 | 0 | 0 | 1 | — | NOT MEASURED |
| unknown | JSS-REFS-003 | 0 | 0 | 581 | — | NOT MEASURED |
| unknown | JSS-REFS-004 | 0 | 0 | 68 | — | NOT MEASURED |
| unknown | JSS-REFS-005 | 0 | 0 | 7 | — | NOT MEASURED |
| unknown | JSS-REFS-006 | 0 | 0 | 103 | — | NOT MEASURED |
| unknown | JSS-REFS-007 | 0 | 0 | 11 | — | NOT MEASURED |
| unknown | JSS-STRUCT-001 | 0 | 0 | 9 | — | NOT MEASURED |
| unknown | JSS-STRUCT-004 | 0 | 0 | 1 | — | NOT MEASURED |
| unknown | JSS-STRUCT-005 | 0 | 0 | 2 | — | NOT MEASURED |
| unknown | JSS-TYPO-001 | 0 | 0 | 11 | — | NOT MEASURED |
| unknown | JSS-TYPO-003 | 0 | 0 | 1 | — | NOT MEASURED |
| unknown | JSS-XREF-001 | 0 | 0 | 4 | — | NOT MEASURED |
| unknown | JSS-XREF-002 | 0 | 0 | 25 | — | NOT MEASURED |
| unknown | JSS-XREF-004 | 0 | 0 | 17 | — | NOT MEASURED |

### Delta vs. previous iteration

**Full corpus**

_(no prior iteration — baseline)_

**Pinned only**

_(no prior iteration — baseline)_

### Findings / suggestions

Unlabelled batch-of-50 analysis surfaced nine candidate improvements, ranked by
leverage:

| # | change | impact | surface | risk |
|---|---|---|---|---|
| P1 | Strip Markdown `` `…` `` inline code spans in Rmd prose | ~500–800 FPs in MARKUP-001/002/003 | `core/rmd_parser.py` | low |
| P6 | Case-insensitive bib field lookup (`year`/`YEAR`, `doi`/`DOI`) | ~60–100 TP→FP flips on .bib | 6 rule files | low |
| P3 | Register `!r`/`!expr` YAML constructor for Rmd frontmatter | unblocks `cran_brms` parse | `core/rmd_parser.py` | low |
| P4 | Soft-fail bibtexparser duplicates → info rule | unblocks `cran_rpart`, `cran_robustbase` bibs | `core/parser.py` + new rule | medium |
| P2 | REFS-006 first-word-caps carve-out for `\pkg{…}:` titles | ~30–50 FPs | `references.py::_strip_latex` | low |
| P7 | Hoist `JSS-CITE-002` `seen` set above the `for tex` loop | 12 Rmd FPs | `citations.py:74` | low |
| P5 | Rephrase REFS-003 message ("where one is available") | noise reduction | catalogue data | trivial |

Bib-scoped rules that now fire via `--pinned-only`: REFS-001, REFS-003, REFS-004,
REFS-005, REFS-006, REFS-007, BIBTEX-002/003/004 — bib files sit alongside the
pinned vignette on disk and the `--pinned-only` filter includes them.

### Plan

Order for the next iteration: P1 first (biggest volume, mechanical), then P6
(widespread correctness bug affecting bib rules). Re-scan and re-measure before
touching P2/P3/P4/P7. P5 is trivial and can ride with P6.

Todos:
- [ ] P1: strip `` `…` `` code spans from Rmd prose in `core/rmd_parser.py`
- [ ] P6: introduce `_lc_fields(entry)` helper and replace case-sensitive lookups in `rules/{references,bibtex,house_style,naming}.py`
- [ ] Re-scan with `--force` and `eval-jss iterate record` as "post-P1+P6"

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_
