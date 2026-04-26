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

Closed by iteration 2. Key numbers:

- **Total violations**: 3848 → 2422 (**-37%**).
- **JSS-MARKUP-003** (inline-code / function-call names): 961 → 165 (**-83%**) — driven by P1 (Rmd ```…``` strip).
- **JSS-REFS-003** (missing DOI): 581 → 170 (**-71%**) — driven by the cited-only bib scope (separate commit, not in the original P1/P6 plan).
- **JSS-BIBTEX-003** (required fields): 84 → 45 (-46%); **JSS-REFS-001** (year): 76 → 45 (-41%); **JSS-REFS-006** dropped out of the top 10.
- **JSS-MARKUP-001**: 706 → 764 (**+8%**) — net +58 is Stan-as-a-language (added per reviewer note); backtick stripping removed most of the legacy FP pool but Stan TPs outnumber the savings.

Not yet shipped from the original plan: P6 (case-insensitive bib field lookup — `YEAR` vs `year`), P2 (REFS-006 `\pkg{…}:` carve-out), P3 (`!r` YAML tag), P4 (soft-fail bibtexparser duplicates), P7 (CITE-002 `seen` set). These are queued for iteration 3.

## Iteration 2 — 2026-04-24T19:09:49Z — post-baseline

- **Corpus size:** 50 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=25, pinned=11

**Note:** Iteration 1 close. Implemented P1 (strip Rmd inline code spans), plus 5 FP-killers from human-review comments: R^2 exemption, SweaveOpts/VignetteIndexEntry meta macros, \code{}-identifier pass-through, scientific-notation mask in CODE-003, Stan added to LANGUAGES. Also scoped bib rules to cited-only entries. Total 3848 → 2422 (-37%).

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 4 | 2 | 68 | 66.67% | FAIL |
| citation | JSS-CITE-003 | 0 | 0 | 1 | — | NOT MEASURED |
| citation | JSS-CITE-004 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 0 | 0 | 5 | — | NOT MEASURED |
| unknown | JSS-BIBTEX-002 | 0 | 0 | 1 | — | NOT MEASURED |
| unknown | JSS-BIBTEX-003 | 0 | 0 | 45 | — | NOT MEASURED |
| unknown | JSS-BIBTEX-004 | 0 | 0 | 6 | — | NOT MEASURED |
| unknown | JSS-CAP-001 | 0 | 0 | 8 | — | NOT MEASURED |
| unknown | JSS-CAP-002 | 0 | 0 | 132 | — | NOT MEASURED |
| unknown | JSS-CAP-003 | 0 | 0 | 16 | — | NOT MEASURED |
| unknown | JSS-CODE-001 | 0 | 0 | 1 | — | NOT MEASURED |
| unknown | JSS-CODE-003 | 0 | 0 | 36 | — | NOT MEASURED |
| unknown | JSS-HOUSE-001 | 5 | 0 | 162 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 0 | 0 | 1 | — | NOT MEASURED |
| unknown | JSS-HOUSE-003 | 0 | 0 | 11 | — | NOT MEASURED |
| unknown | JSS-MARKUP-001 | 11 | 0 | 753 | 100.00% | PASS |
| unknown | JSS-MARKUP-002 | 0 | 0 | 239 | — | NOT MEASURED |
| unknown | JSS-MARKUP-003 | 0 | 0 | 165 | — | NOT MEASURED |
| unknown | JSS-MARKUP-004 | 0 | 0 | 93 | — | NOT MEASURED |
| unknown | JSS-NAME-001 | 0 | 0 | 20 | — | NOT MEASURED |
| unknown | JSS-NAME-002 | 0 | 0 | 4 | — | NOT MEASURED |
| unknown | JSS-OPER-001 | 5 | 0 | 29 | 100.00% | PASS |
| unknown | JSS-OPER-002 | 0 | 0 | 36 | — | NOT MEASURED |
| unknown | JSS-OPER-003 | 0 | 0 | 37 | — | NOT MEASURED |
| unknown | JSS-OPER-004 | 0 | 0 | 10 | — | NOT MEASURED |
| unknown | JSS-PRE-001 | 1 | 0 | 28 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 0 | 0 | 4 | — | NOT MEASURED |
| unknown | JSS-PRE-003 | 0 | 0 | 13 | — | NOT MEASURED |
| unknown | JSS-PRE-006 | 0 | 0 | 3 | — | NOT MEASURED |
| unknown | JSS-PRE-007 | 0 | 0 | 20 | — | NOT MEASURED |
| unknown | JSS-REFS-001 | 0 | 0 | 45 | — | NOT MEASURED |
| unknown | JSS-REFS-003 | 4 | 4 | 162 | 50.00% | FAIL |
| unknown | JSS-REFS-004 | 0 | 0 | 13 | — | NOT MEASURED |
| unknown | JSS-REFS-005 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 0 | 0 | 31 | — | NOT MEASURED |
| unknown | JSS-STRUCT-001 | 1 | 0 | 20 | 100.00% | PASS |
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
| citation | JSS-CITE-002 | 4 | 2 | 35 | 66.67% | FAIL |
| unknown | JSS-ABBR-001 | 0 | 0 | 2 | — | NOT MEASURED |
| unknown | JSS-BIBTEX-002 | 0 | 0 | 1 | — | NOT MEASURED |
| unknown | JSS-BIBTEX-003 | 0 | 0 | 45 | — | NOT MEASURED |
| unknown | JSS-BIBTEX-004 | 0 | 0 | 6 | — | NOT MEASURED |
| unknown | JSS-CAP-001 | 0 | 0 | 3 | — | NOT MEASURED |
| unknown | JSS-CAP-002 | 0 | 0 | 12 | — | NOT MEASURED |
| unknown | JSS-CAP-003 | 0 | 0 | 5 | — | NOT MEASURED |
| unknown | JSS-CODE-003 | 0 | 0 | 7 | — | NOT MEASURED |
| unknown | JSS-HOUSE-001 | 0 | 0 | 33 | — | NOT MEASURED |
| unknown | JSS-HOUSE-002 | 0 | 0 | 1 | — | NOT MEASURED |
| unknown | JSS-HOUSE-003 | 0 | 0 | 2 | — | NOT MEASURED |
| unknown | JSS-MARKUP-001 | 2 | 0 | 274 | 100.00% | PASS |
| unknown | JSS-MARKUP-002 | 0 | 0 | 127 | — | NOT MEASURED |
| unknown | JSS-MARKUP-003 | 0 | 0 | 9 | — | NOT MEASURED |
| unknown | JSS-MARKUP-004 | 0 | 0 | 21 | — | NOT MEASURED |
| unknown | JSS-NAME-001 | 0 | 0 | 5 | — | NOT MEASURED |
| unknown | JSS-NAME-002 | 0 | 0 | 4 | — | NOT MEASURED |
| unknown | JSS-OPER-001 | 0 | 0 | 9 | — | NOT MEASURED |
| unknown | JSS-OPER-002 | 0 | 0 | 27 | — | NOT MEASURED |
| unknown | JSS-OPER-003 | 0 | 0 | 20 | — | NOT MEASURED |
| unknown | JSS-PRE-001 | 0 | 0 | 8 | — | NOT MEASURED |
| unknown | JSS-PRE-002 | 0 | 0 | 4 | — | NOT MEASURED |
| unknown | JSS-PRE-003 | 0 | 0 | 6 | — | NOT MEASURED |
| unknown | JSS-PRE-006 | 0 | 0 | 2 | — | NOT MEASURED |
| unknown | JSS-PRE-007 | 0 | 0 | 8 | — | NOT MEASURED |
| unknown | JSS-REFS-001 | 0 | 0 | 45 | — | NOT MEASURED |
| unknown | JSS-REFS-003 | 4 | 4 | 162 | 50.00% | FAIL |
| unknown | JSS-REFS-004 | 0 | 0 | 13 | — | NOT MEASURED |
| unknown | JSS-REFS-005 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 0 | 0 | 31 | — | NOT MEASURED |
| unknown | JSS-STRUCT-001 | 1 | 0 | 8 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 0 | 0 | 1 | — | NOT MEASURED |
| unknown | JSS-STRUCT-005 | 0 | 0 | 2 | — | NOT MEASURED |
| unknown | JSS-TYPO-001 | 0 | 0 | 11 | — | NOT MEASURED |
| unknown | JSS-TYPO-003 | 0 | 0 | 1 | — | NOT MEASURED |
| unknown | JSS-XREF-001 | 0 | 0 | 4 | — | NOT MEASURED |
| unknown | JSS-XREF-002 | 0 | 0 | 25 | — | NOT MEASURED |
| unknown | JSS-XREF-004 | 0 | 0 | 17 | — | NOT MEASURED |

### Delta vs. previous iteration

**Full corpus**

- `JSS-CITE-002`: tp +1→4 (+3), fp +0→2 (+2), pending 73→68 (-5)
- `JSS-CITE-004`: tp +0→1 (+1), fp +0→0 (+0), pending 1→0 (-1)
- `JSS-BIBTEX-003`: tp +0→0 (+0), fp +0→0 (+0), pending 84→45 (-39)
- `JSS-BIBTEX-004`: tp +0→0 (+0), fp +0→0 (+0), pending 18→6 (-12)
- `JSS-CODE-003`: tp +0→0 (+0), fp +0→0 (+0), pending 52→36 (-16)
- `JSS-HOUSE-001`: tp +0→5 (+5), fp +0→0 (+0), pending 164→162 (-2)
- `JSS-HOUSE-002`: tp +0→0 (+0), fp +0→0 (+0), pending 4→1 (-3)
- `JSS-MARKUP-001`: tp +0→11 (+11), fp +0→0 (+0), pending 706→753 (+47)
- `JSS-MARKUP-002`: tp +0→0 (+0), fp +0→0 (+0), pending 248→239 (-9)
- `JSS-MARKUP-003`: tp +0→0 (+0), fp +0→0 (+0), pending 961→165 (-796)
- `JSS-NAME-001`: tp +0→0 (+0), fp +0→0 (+0), pending 24→20 (-4)
- `JSS-NAME-002`: tp +0→0 (+0), fp +0→0 (+0), pending 26→4 (-22)
- `JSS-OPER-001`: tp +0→5 (+5), fp +0→0 (+0), pending 34→29 (-5)
- `JSS-PRE-001`: tp +0→1 (+1), fp +0→0 (+0), pending 29→28 (-1)
- `JSS-REFS-001`: tp +0→0 (+0), fp +0→0 (+0), pending 76→45 (-31)
- `JSS-REFS-003`: tp +0→4 (+4), fp +0→4 (+4), pending 581→162 (-419)
- `JSS-REFS-004`: tp +0→0 (+0), fp +0→0 (+0), pending 68→13 (-55)
- `JSS-REFS-005`: tp +0→2 (+2), fp +0→0 (+0), pending 7→0 (-7)
- `JSS-REFS-006`: tp +0→0 (+0), fp +0→0 (+0), pending 103→31 (-72)
- `JSS-STRUCT-001`: tp +0→1 (+1), fp +0→0 (+0), pending 21→20 (-1)

**Pinned only**

- `JSS-CITE-002`: tp +1→4 (+3), fp +0→2 (+2), pending 40→35 (-5)
- `JSS-BIBTEX-003`: tp +0→0 (+0), fp +0→0 (+0), pending 84→45 (-39)
- `JSS-BIBTEX-004`: tp +0→0 (+0), fp +0→0 (+0), pending 18→6 (-12)
- `JSS-CODE-003`: tp +0→0 (+0), fp +0→0 (+0), pending 23→7 (-16)
- `JSS-HOUSE-002`: tp +0→0 (+0), fp +0→0 (+0), pending 4→1 (-3)
- `JSS-MARKUP-001`: tp +0→2 (+2), fp +0→0 (+0), pending 238→274 (+36)
- `JSS-MARKUP-002`: tp +0→0 (+0), fp +0→0 (+0), pending 130→127 (-3)
- `JSS-MARKUP-003`: tp +0→0 (+0), fp +0→0 (+0), pending 203→9 (-194)
- `JSS-NAME-001`: tp +0→0 (+0), fp +0→0 (+0), pending 7→5 (-2)
- `JSS-NAME-002`: tp +0→0 (+0), fp +0→0 (+0), pending 26→4 (-22)
- `JSS-REFS-001`: tp +0→0 (+0), fp +0→0 (+0), pending 76→45 (-31)
- `JSS-REFS-003`: tp +0→4 (+4), fp +0→4 (+4), pending 581→162 (-419)
- `JSS-REFS-004`: tp +0→0 (+0), fp +0→0 (+0), pending 68→13 (-55)
- `JSS-REFS-005`: tp +0→2 (+2), fp +0→0 (+0), pending 7→0 (-7)
- `JSS-REFS-006`: tp +0→0 (+0), fp +0→0 (+0), pending 103→31 (-72)
- `JSS-STRUCT-001`: tp +0→1 (+1), fp +0→0 (+0), pending 9→8 (-1)

### Findings / suggestions

Iteration 2 was a close-out record for iteration 1's plan, not a fresh
analysis pass. Carry-over candidates from iteration 1's unfinished plan:

| # | change | notes |
|---|---|---|
| P6 | Case-insensitive bib field lookup | BibTeX allows `YEAR`/`DOI`/`AUTHOR`; rules currently `entry.fields_dict.get("year")` and miss uppercase. Re-verify impact under the new cited-only scope. |
| P2 | REFS-006 carve-out for `\pkg{…}:` titles | First-word-caps check currently trips on package names after `_strip_latex` removes the wrapper. |
| P3 | `!r` / `!expr` YAML tag in Rmd frontmatter | Unblocks `cran_brms` whose fenced chunks use `!r` — currently emits `JSS-PARSE-000`. |
| P4 | Soft-fail bibtexparser duplicate-key error | Duplicate keys still blow up the whole bib parse; convert to an info-severity rule so the rest of the bib is still lintable. |
| P7 | Hoist `JSS-CITE-002` `seen` set above the per-tex loop | Rmd-only FP: each prose block re-asks for a citation on the same `\pkg{X}`. |

### Plan

Next iteration (3) starts with a corpus expansion (`/eval-add-corpus`),
then cycles through the steps. Carry forward P6/P2/P3/P4/P7 above as the
candidate list to refine after human review of the new batch.

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 3 — 2026-04-25T11:18:15Z — post-iter2

- **Corpus size:** 50 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=25, pinned=11

**Note:** P6 case-insensitive bib fields, P7 CITE-002 seen-set hoist, CAP sentence-case heuristic upgrade (sub-sentence boundaries + abbreviation/mixed-case carve-outs), OPER-003/TYPO-004 narrowed to .tex. BIBTEX-003 22% → small-sample, REFS-001 44% → 100%, CAP-002 76% → 88%, CAP-003 8 of 15 FPs eliminated.

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 27 | 9 | 26 | 75.00% | FAIL |
| citation | JSS-CITE-003 | 1 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 4 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 1 | 1 | 0 | 50.00% | FAIL |
| unknown | JSS-BIBTEX-004 | 4 | 0 | 2 | 100.00% | PASS |
| unknown | JSS-CAP-001 | 1 | 7 | 0 | 12.50% | FAIL |
| unknown | JSS-CAP-002 | 99 | 14 | 0 | 87.61% | FAIL |
| unknown | JSS-CAP-003 | 0 | 7 | 1 | 0.00% | FAIL |
| unknown | JSS-CODE-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 33 | 2 | 1 | 94.29% | PASS |
| unknown | JSS-HOUSE-001 | 166 | 1 | 0 | 99.40% | PASS |
| unknown | JSS-HOUSE-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 10 | 1 | 0 | 90.91% | PASS |
| unknown | JSS-MARKUP-001 | 540 | 18 | 206 | 96.77% | PASS |
| unknown | JSS-MARKUP-002 | 183 | 48 | 8 | 79.22% | FAIL |
| unknown | JSS-MARKUP-003 | 63 | 4 | 98 | 94.03% | PASS |
| unknown | JSS-MARKUP-004 | 74 | 5 | 14 | 93.67% | PASS |
| unknown | JSS-NAME-001 | 4 | 16 | 0 | 20.00% | FAIL |
| unknown | JSS-NAME-002 | 3 | 1 | 2 | 75.00% | FAIL |
| unknown | JSS-OPER-001 | 32 | 1 | 1 | 96.97% | PASS |
| unknown | JSS-OPER-002 | 14 | 22 | 0 | 38.89% | FAIL |
| unknown | JSS-OPER-004 | 7 | 0 | 3 | 100.00% | PASS |
| unknown | JSS-PRE-001 | 29 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 2 | 1 | 10 | 66.67% | FAIL |
| unknown | JSS-PRE-006 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 8 | 1 | 11 | 88.89% | FAIL |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 140 | 30 | 0 | 82.35% | FAIL |
| unknown | JSS-REFS-004 | 11 | 2 | 3 | 84.62% | FAIL |
| unknown | JSS-REFS-005 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 31 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 14 | 7 | 0 | 66.67% | FAIL |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 2 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 11 | 1 | 0 | 91.67% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 5 | 0 | 3 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 71 | 6 | 0 | 92.21% | PASS |
| unknown | JSS-XREF-004 | 11 | 0 | 10 | 100.00% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 15 | 7 | 13 | 68.18% | FAIL |
| unknown | JSS-ABBR-001 | 1 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 1 | 1 | 0 | 50.00% | FAIL |
| unknown | JSS-BIBTEX-004 | 4 | 0 | 2 | 100.00% | PASS |
| unknown | JSS-CAP-001 | 0 | 3 | 0 | 0.00% | FAIL |
| unknown | JSS-CAP-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-003 | 0 | 3 | 0 | 0.00% | FAIL |
| unknown | JSS-CODE-003 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-001 | 33 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 1 | 1 | 0 | 50.00% | FAIL |
| unknown | JSS-MARKUP-001 | 208 | 1 | 67 | 99.52% | PASS |
| unknown | JSS-MARKUP-002 | 106 | 19 | 2 | 84.80% | FAIL |
| unknown | JSS-MARKUP-003 | 6 | 0 | 3 | 100.00% | PASS |
| unknown | JSS-MARKUP-004 | 18 | 1 | 2 | 94.74% | PASS |
| unknown | JSS-NAME-001 | 2 | 3 | 0 | 40.00% | FAIL |
| unknown | JSS-NAME-002 | 3 | 1 | 2 | 75.00% | FAIL |
| unknown | JSS-OPER-001 | 7 | 1 | 1 | 87.50% | FAIL |
| unknown | JSS-OPER-002 | 12 | 15 | 0 | 44.44% | FAIL |
| unknown | JSS-PRE-001 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 2 | 0 | 4 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 3 | 1 | 4 | 75.00% | FAIL |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 140 | 30 | 0 | 82.35% | FAIL |
| unknown | JSS-REFS-004 | 11 | 2 | 3 | 84.62% | FAIL |
| unknown | JSS-REFS-005 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 31 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 6 | 3 | 0 | 66.67% | FAIL |
| unknown | JSS-STRUCT-004 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 10 | 1 | 0 | 90.91% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 3 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 19 | 6 | 0 | 76.00% | FAIL |
| unknown | JSS-XREF-004 | 10 | 0 | 7 | 100.00% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-CITE-002`: tp +4→27 (+23), fp +2→9 (+7), pending 68→26 (-42)
- `JSS-CITE-003`: tp +0→1 (+1), fp +0→0 (+0), pending 1→0 (-1)
- `JSS-ABBR-001`: tp +0→4 (+4), fp +0→0 (+0), pending 5→1 (-4)
- `JSS-BIBTEX-002`: tp +0→1 (+1), fp +0→0 (+0), pending 1→0 (-1)
- `JSS-BIBTEX-003`: tp +0→1 (+1), fp +0→1 (+1), pending 45→0 (-45)
- `JSS-BIBTEX-004`: tp +0→4 (+4), fp +0→0 (+0), pending 6→2 (-4)
- `JSS-CAP-001`: tp +0→1 (+1), fp +0→7 (+7), pending 8→0 (-8)
- `JSS-CAP-002`: tp +0→99 (+99), fp +0→14 (+14), pending 132→0 (-132)
- `JSS-CAP-003`: tp +0→0 (+0), fp +0→7 (+7), pending 16→1 (-15)
- `JSS-CODE-001`: tp +0→1 (+1), fp +0→0 (+0), pending 1→0 (-1)
- `JSS-CODE-003`: tp +0→33 (+33), fp +0→2 (+2), pending 36→1 (-35)
- `JSS-HOUSE-001`: tp +5→166 (+161), fp +0→1 (+1), pending 162→0 (-162)
- `JSS-HOUSE-002`: tp +0→1 (+1), fp +0→0 (+0), pending 1→0 (-1)
- `JSS-HOUSE-003`: tp +0→10 (+10), fp +0→1 (+1), pending 11→0 (-11)
- `JSS-MARKUP-001`: tp +11→540 (+529), fp +0→18 (+18), pending 753→206 (-547)
- `JSS-MARKUP-002`: tp +0→183 (+183), fp +0→48 (+48), pending 239→8 (-231)
- `JSS-MARKUP-003`: tp +0→63 (+63), fp +0→4 (+4), pending 165→98 (-67)
- `JSS-MARKUP-004`: tp +0→74 (+74), fp +0→5 (+5), pending 93→14 (-79)
- `JSS-NAME-001`: tp +0→4 (+4), fp +0→16 (+16), pending 20→0 (-20)
- `JSS-NAME-002`: tp +0→3 (+3), fp +0→1 (+1), pending 4→2 (-2)
- `JSS-OPER-001`: tp +5→32 (+27), fp +0→1 (+1), pending 29→1 (-28)
- `JSS-OPER-002`: tp +0→14 (+14), fp +0→22 (+22), pending 36→0 (-36)
- `JSS-OPER-004`: tp +0→7 (+7), fp +0→0 (+0), pending 10→3 (-7)
- `JSS-PRE-001`: tp +1→29 (+28), fp +0→0 (+0), pending 28→0 (-28)
- `JSS-PRE-002`: tp +0→4 (+4), fp +0→0 (+0), pending 4→0 (-4)
- `JSS-PRE-003`: tp +0→2 (+2), fp +0→1 (+1), pending 13→10 (-3)
- `JSS-PRE-006`: tp +0→3 (+3), fp +0→0 (+0), pending 3→0 (-3)
- `JSS-PRE-007`: tp +0→8 (+8), fp +0→1 (+1), pending 20→11 (-9)
- `JSS-REFS-001`: tp +0→1 (+1), fp +0→0 (+0), pending 45→0 (-45)
- `JSS-REFS-003`: tp +4→140 (+136), fp +4→30 (+26), pending 162→0 (-162)
- `JSS-REFS-004`: tp +0→11 (+11), fp +0→2 (+2), pending 13→3 (-10)
- `JSS-REFS-006`: tp +0→31 (+31), fp +0→0 (+0), pending 31→0 (-31)
- `JSS-STRUCT-001`: tp +1→14 (+13), fp +0→7 (+7), pending 20→0 (-20)
- `JSS-STRUCT-004`: tp +0→2 (+2), fp +0→0 (+0), pending 2→0 (-2)
- `JSS-STRUCT-005`: tp +0→2 (+2), fp +0→0 (+0), pending 3→1 (-2)
- `JSS-TYPO-001`: tp +0→11 (+11), fp +0→1 (+1), pending 12→0 (-12)
- `JSS-TYPO-003`: tp +0→1 (+1), fp +0→0 (+0), pending 1→0 (-1)
- `JSS-XREF-001`: tp +0→5 (+5), fp +0→0 (+0), pending 8→3 (-5)
- `JSS-XREF-002`: tp +0→71 (+71), fp +0→6 (+6), pending 77→0 (-77)
- `JSS-XREF-004`: tp +0→11 (+11), fp +0→0 (+0), pending 21→10 (-11)

**Pinned only**

- `JSS-CITE-002`: tp +4→15 (+11), fp +2→7 (+5), pending 35→13 (-22)
- `JSS-ABBR-001`: tp +0→1 (+1), fp +0→0 (+0), pending 2→1 (-1)
- `JSS-BIBTEX-002`: tp +0→1 (+1), fp +0→0 (+0), pending 1→0 (-1)
- `JSS-BIBTEX-003`: tp +0→1 (+1), fp +0→1 (+1), pending 45→0 (-45)
- `JSS-BIBTEX-004`: tp +0→4 (+4), fp +0→0 (+0), pending 6→2 (-4)
- `JSS-CAP-001`: tp +0→0 (+0), fp +0→3 (+3), pending 3→0 (-3)
- `JSS-CAP-002`: tp +0→4 (+4), fp +0→0 (+0), pending 12→0 (-12)
- `JSS-CAP-003`: tp +0→0 (+0), fp +0→3 (+3), pending 5→0 (-5)
- `JSS-CODE-003`: tp +0→7 (+7), fp +0→0 (+0), pending 7→0 (-7)
- `JSS-HOUSE-001`: tp +0→33 (+33), fp +0→0 (+0), pending 33→0 (-33)
- `JSS-HOUSE-002`: tp +0→1 (+1), fp +0→0 (+0), pending 1→0 (-1)
- `JSS-HOUSE-003`: tp +0→1 (+1), fp +0→1 (+1), pending 2→0 (-2)
- `JSS-MARKUP-001`: tp +2→208 (+206), fp +0→1 (+1), pending 274→67 (-207)
- `JSS-MARKUP-002`: tp +0→106 (+106), fp +0→19 (+19), pending 127→2 (-125)
- `JSS-MARKUP-003`: tp +0→6 (+6), fp +0→0 (+0), pending 9→3 (-6)
- `JSS-MARKUP-004`: tp +0→18 (+18), fp +0→1 (+1), pending 21→2 (-19)
- `JSS-NAME-001`: tp +0→2 (+2), fp +0→3 (+3), pending 5→0 (-5)
- `JSS-NAME-002`: tp +0→3 (+3), fp +0→1 (+1), pending 4→2 (-2)
- `JSS-OPER-001`: tp +0→7 (+7), fp +0→1 (+1), pending 9→1 (-8)
- `JSS-OPER-002`: tp +0→12 (+12), fp +0→15 (+15), pending 27→0 (-27)
- `JSS-PRE-001`: tp +0→8 (+8), fp +0→0 (+0), pending 8→0 (-8)
- `JSS-PRE-002`: tp +0→4 (+4), fp +0→0 (+0), pending 4→0 (-4)
- `JSS-PRE-003`: tp +0→2 (+2), fp +0→0 (+0), pending 6→4 (-2)
- `JSS-PRE-006`: tp +0→2 (+2), fp +0→0 (+0), pending 2→0 (-2)
- `JSS-PRE-007`: tp +0→3 (+3), fp +0→1 (+1), pending 8→4 (-4)
- `JSS-REFS-001`: tp +0→1 (+1), fp +0→0 (+0), pending 45→0 (-45)
- `JSS-REFS-003`: tp +4→140 (+136), fp +4→30 (+26), pending 162→0 (-162)
- `JSS-REFS-004`: tp +0→11 (+11), fp +0→2 (+2), pending 13→3 (-10)
- `JSS-REFS-006`: tp +0→31 (+31), fp +0→0 (+0), pending 31→0 (-31)
- `JSS-STRUCT-001`: tp +1→6 (+5), fp +0→3 (+3), pending 8→0 (-8)
- `JSS-STRUCT-004`: tp +0→1 (+1), fp +0→0 (+0), pending 1→0 (-1)
- `JSS-STRUCT-005`: tp +0→2 (+2), fp +0→0 (+0), pending 2→0 (-2)
- `JSS-TYPO-001`: tp +0→10 (+10), fp +0→1 (+1), pending 11→0 (-11)
- `JSS-TYPO-003`: tp +0→1 (+1), fp +0→0 (+0), pending 1→0 (-1)
- `JSS-XREF-001`: tp +0→3 (+3), fp +0→0 (+0), pending 4→1 (-3)
- `JSS-XREF-002`: tp +0→19 (+19), fp +0→6 (+6), pending 25→0 (-25)
- `JSS-XREF-004`: tp +0→10 (+10), fp +0→0 (+0), pending 17→7 (-10)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 4 — 2026-04-25T12:56:40Z — post-cap-fixes

- **Corpus size:** 50 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=25, pinned=11

**Note:** Continued iteration 2 close: CAP family now passes. CAP-001 12.5% → 100%, CAP-002 87.6% → 98.0%, CAP-003 no longer fires on previously-FP rows. Five mechanisms: restored hyphen split, skip single-letter caps, expanded proper-noun list (nationalities + eponyms + corpus names), markup-macro args excluded from plain-text scan, CAP-001 skips stopword-only/known-pkg/function-call titles.

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 27 | 9 | 26 | 75.00% | FAIL |
| citation | JSS-CITE-003 | 1 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 4 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 1 | 1 | 0 | 50.00% | FAIL |
| unknown | JSS-BIBTEX-004 | 4 | 0 | 2 | 100.00% | PASS |
| unknown | JSS-CAP-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 99 | 2 | 1 | 98.02% | PASS |
| unknown | JSS-CAP-003 | 0 | 0 | 2 | — | NOT MEASURED |
| unknown | JSS-CODE-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 33 | 2 | 1 | 94.29% | PASS |
| unknown | JSS-HOUSE-001 | 166 | 1 | 0 | 99.40% | PASS |
| unknown | JSS-HOUSE-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 10 | 1 | 0 | 90.91% | PASS |
| unknown | JSS-MARKUP-001 | 540 | 18 | 206 | 96.77% | PASS |
| unknown | JSS-MARKUP-002 | 183 | 48 | 8 | 79.22% | FAIL |
| unknown | JSS-MARKUP-003 | 63 | 4 | 98 | 94.03% | PASS |
| unknown | JSS-MARKUP-004 | 74 | 5 | 14 | 93.67% | PASS |
| unknown | JSS-NAME-001 | 4 | 16 | 0 | 20.00% | FAIL |
| unknown | JSS-NAME-002 | 3 | 1 | 2 | 75.00% | FAIL |
| unknown | JSS-OPER-001 | 32 | 1 | 1 | 96.97% | PASS |
| unknown | JSS-OPER-002 | 14 | 22 | 0 | 38.89% | FAIL |
| unknown | JSS-OPER-004 | 7 | 0 | 3 | 100.00% | PASS |
| unknown | JSS-PRE-001 | 29 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 2 | 1 | 10 | 66.67% | FAIL |
| unknown | JSS-PRE-006 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 8 | 1 | 11 | 88.89% | FAIL |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 140 | 30 | 0 | 82.35% | FAIL |
| unknown | JSS-REFS-004 | 11 | 2 | 3 | 84.62% | FAIL |
| unknown | JSS-REFS-005 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 31 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 14 | 7 | 0 | 66.67% | FAIL |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 2 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 11 | 1 | 0 | 91.67% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 5 | 0 | 3 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 71 | 6 | 0 | 92.21% | PASS |
| unknown | JSS-XREF-004 | 11 | 0 | 10 | 100.00% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 15 | 7 | 13 | 68.18% | FAIL |
| unknown | JSS-ABBR-001 | 1 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 1 | 1 | 0 | 50.00% | FAIL |
| unknown | JSS-BIBTEX-004 | 4 | 0 | 2 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 4 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-001 | 33 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 1 | 1 | 0 | 50.00% | FAIL |
| unknown | JSS-MARKUP-001 | 208 | 1 | 67 | 99.52% | PASS |
| unknown | JSS-MARKUP-002 | 106 | 19 | 2 | 84.80% | FAIL |
| unknown | JSS-MARKUP-003 | 6 | 0 | 3 | 100.00% | PASS |
| unknown | JSS-MARKUP-004 | 18 | 1 | 2 | 94.74% | PASS |
| unknown | JSS-NAME-001 | 2 | 3 | 0 | 40.00% | FAIL |
| unknown | JSS-NAME-002 | 3 | 1 | 2 | 75.00% | FAIL |
| unknown | JSS-OPER-001 | 7 | 1 | 1 | 87.50% | FAIL |
| unknown | JSS-OPER-002 | 12 | 15 | 0 | 44.44% | FAIL |
| unknown | JSS-PRE-001 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 2 | 0 | 4 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 3 | 1 | 4 | 75.00% | FAIL |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 140 | 30 | 0 | 82.35% | FAIL |
| unknown | JSS-REFS-004 | 11 | 2 | 3 | 84.62% | FAIL |
| unknown | JSS-REFS-005 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 31 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 6 | 3 | 0 | 66.67% | FAIL |
| unknown | JSS-STRUCT-004 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 10 | 1 | 0 | 90.91% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 3 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 19 | 6 | 0 | 76.00% | FAIL |
| unknown | JSS-XREF-004 | 10 | 0 | 7 | 100.00% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-CAP-001`: tp +1→1 (+0), fp +7→0 (-7), pending 0→0 (+0)
- `JSS-CAP-002`: tp +99→99 (+0), fp +14→2 (-12), pending 0→1 (+1)
- `JSS-CAP-003`: tp +0→0 (+0), fp +7→0 (-7), pending 1→2 (+1)

**Pinned only**

- `JSS-CAP-002`: tp +4→4 (+0), fp +0→0 (+0), pending 0→1 (+1)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 5 — 2026-04-25T19:05:25Z — post-spot-check

- **Corpus size:** 50 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=25, pinned=11

**Note:** Coverage spot-check on six AI-only rules. JSS-REFS-006 rubber-stamping uncovered: 5 of 6 human re-verifications flipped from TP to FP. Other five rules confirmed AI correct on human sample.

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 32 | 11 | 19 | 74.42% | FAIL |
| citation | JSS-CITE-003 | 1 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 4 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 1 | 1 | 0 | 50.00% | FAIL |
| unknown | JSS-BIBTEX-004 | 4 | 2 | 0 | 66.67% | FAIL |
| unknown | JSS-CAP-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 99 | 3 | 0 | 97.06% | PASS |
| unknown | JSS-CAP-003 | 0 | 2 | 0 | 0.00% | FAIL |
| unknown | JSS-CODE-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 34 | 2 | 0 | 94.44% | PASS |
| unknown | JSS-HOUSE-001 | 159 | 1 | 0 | 99.38% | PASS |
| unknown | JSS-HOUSE-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 10 | 1 | 0 | 90.91% | PASS |
| unknown | JSS-MARKUP-001 | 485 | 16 | 255 | 96.81% | PASS |
| unknown | JSS-MARKUP-002 | 74 | 27 | 121 | 73.27% | FAIL |
| unknown | JSS-MARKUP-003 | 66 | 8 | 91 | 89.19% | FAIL |
| unknown | JSS-MARKUP-004 | 79 | 6 | 8 | 92.94% | PASS |
| unknown | JSS-NAME-001 | 1 | 1 | 0 | 50.00% | FAIL |
| unknown | JSS-NAME-002 | 5 | 1 | 0 | 83.33% | FAIL |
| unknown | JSS-OPER-001 | 32 | 1 | 1 | 96.97% | PASS |
| unknown | JSS-OPER-002 | 36 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 9 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-PRE-001 | 29 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 6 | 1 | 6 | 85.71% | FAIL |
| unknown | JSS-PRE-006 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 12 | 1 | 7 | 92.31% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 140 | 30 | 0 | 82.35% | FAIL |
| unknown | JSS-REFS-004 | 12 | 2 | 2 | 85.71% | FAIL |
| unknown | JSS-REFS-005 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 26 | 5 | 0 | 83.87% | FAIL |
| unknown | JSS-STRUCT-001 | 10 | 1 | 4 | 90.91% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 11 | 1 | 0 | 91.67% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 5 | 0 | 3 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 72 | 5 | 0 | 93.51% | PASS |
| unknown | JSS-XREF-004 | 13 | 0 | 8 | 100.00% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 17 | 9 | 9 | 65.38% | FAIL |
| unknown | JSS-ABBR-001 | 1 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 1 | 1 | 0 | 50.00% | FAIL |
| unknown | JSS-BIBTEX-004 | 4 | 2 | 0 | 66.67% | FAIL |
| unknown | JSS-CAP-002 | 4 | 1 | 0 | 80.00% | FAIL |
| unknown | JSS-CODE-003 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-001 | 29 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 1 | 1 | 0 | 50.00% | FAIL |
| unknown | JSS-MARKUP-001 | 165 | 1 | 108 | 99.40% | PASS |
| unknown | JSS-MARKUP-002 | 14 | 1 | 101 | 93.33% | PASS |
| unknown | JSS-MARKUP-003 | 7 | 0 | 2 | 100.00% | PASS |
| unknown | JSS-MARKUP-004 | 19 | 1 | 1 | 95.00% | PASS |
| unknown | JSS-NAME-002 | 5 | 1 | 0 | 83.33% | FAIL |
| unknown | JSS-OPER-001 | 7 | 1 | 1 | 87.50% | FAIL |
| unknown | JSS-OPER-002 | 27 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-001 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 4 | 0 | 2 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 4 | 1 | 3 | 80.00% | FAIL |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 140 | 30 | 0 | 82.35% | FAIL |
| unknown | JSS-REFS-004 | 12 | 2 | 2 | 85.71% | FAIL |
| unknown | JSS-REFS-005 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 26 | 5 | 0 | 83.87% | FAIL |
| unknown | JSS-STRUCT-001 | 4 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 10 | 1 | 0 | 90.91% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 3 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 20 | 5 | 0 | 80.00% | FAIL |
| unknown | JSS-XREF-004 | 11 | 0 | 6 | 100.00% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-CITE-002`: tp +27→32 (+5), fp +9→11 (+2), pending 26→19 (-7)
- `JSS-BIBTEX-004`: tp +4→4 (+0), fp +0→2 (+2), pending 2→0 (-2)
- `JSS-CAP-002`: tp +99→99 (+0), fp +2→3 (+1), pending 1→0 (-1)
- `JSS-CAP-003`: tp +0→0 (+0), fp +0→2 (+2), pending 2→0 (-2)
- `JSS-CODE-003`: tp +33→34 (+1), fp +2→2 (+0), pending 1→0 (-1)
- `JSS-HOUSE-001`: tp +166→159 (-7), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-MARKUP-001`: tp +540→485 (-55), fp +18→16 (-2), pending 206→255 (+49)
- `JSS-MARKUP-002`: tp +183→74 (-109), fp +48→27 (-21), pending 8→121 (+113)
- `JSS-MARKUP-003`: tp +63→66 (+3), fp +4→8 (+4), pending 98→91 (-7)
- `JSS-MARKUP-004`: tp +74→79 (+5), fp +5→6 (+1), pending 14→8 (-6)
- `JSS-NAME-001`: tp +4→1 (-3), fp +16→1 (-15), pending 0→0 (+0)
- `JSS-NAME-002`: tp +3→5 (+2), fp +1→1 (+0), pending 2→0 (-2)
- `JSS-OPER-002`: tp +14→36 (+22), fp +22→0 (-22), pending 0→0 (+0)
- `JSS-OPER-004`: tp +7→9 (+2), fp +0→0 (+0), pending 3→1 (-2)
- `JSS-PRE-003`: tp +2→6 (+4), fp +1→1 (+0), pending 10→6 (-4)
- `JSS-PRE-007`: tp +8→12 (+4), fp +1→1 (+0), pending 11→7 (-4)
- `JSS-REFS-004`: tp +11→12 (+1), fp +2→2 (+0), pending 3→2 (-1)
- `JSS-REFS-006`: tp +31→26 (-5), fp +0→5 (+5), pending 0→0 (+0)
- `JSS-STRUCT-001`: tp +14→10 (-4), fp +7→1 (-6), pending 0→4 (+4)
- `JSS-STRUCT-005`: tp +2→3 (+1), fp +0→0 (+0), pending 1→0 (-1)
- `JSS-XREF-002`: tp +71→72 (+1), fp +6→5 (-1), pending 0→0 (+0)
- `JSS-XREF-004`: tp +11→13 (+2), fp +0→0 (+0), pending 10→8 (-2)

**Pinned only**

- `JSS-CITE-002`: tp +15→17 (+2), fp +7→9 (+2), pending 13→9 (-4)
- `JSS-BIBTEX-004`: tp +4→4 (+0), fp +0→2 (+2), pending 2→0 (-2)
- `JSS-CAP-002`: tp +4→4 (+0), fp +0→1 (+1), pending 1→0 (-1)
- `JSS-HOUSE-001`: tp +33→29 (-4), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-MARKUP-001`: tp +208→165 (-43), fp +1→1 (+0), pending 67→108 (+41)
- `JSS-MARKUP-002`: tp +106→14 (-92), fp +19→1 (-18), pending 2→101 (+99)
- `JSS-MARKUP-003`: tp +6→7 (+1), fp +0→0 (+0), pending 3→2 (-1)
- `JSS-MARKUP-004`: tp +18→19 (+1), fp +1→1 (+0), pending 2→1 (-1)
- `JSS-NAME-002`: tp +3→5 (+2), fp +1→1 (+0), pending 2→0 (-2)
- `JSS-OPER-002`: tp +12→27 (+15), fp +15→0 (-15), pending 0→0 (+0)
- `JSS-PRE-003`: tp +2→4 (+2), fp +0→0 (+0), pending 4→2 (-2)
- `JSS-PRE-007`: tp +3→4 (+1), fp +1→1 (+0), pending 4→3 (-1)
- `JSS-REFS-004`: tp +11→12 (+1), fp +2→2 (+0), pending 3→2 (-1)
- `JSS-REFS-006`: tp +31→26 (-5), fp +0→5 (+5), pending 0→0 (+0)
- `JSS-STRUCT-001`: tp +6→4 (-2), fp +3→0 (-3), pending 0→1 (+1)
- `JSS-XREF-002`: tp +19→20 (+1), fp +6→5 (-1), pending 0→0 (+0)
- `JSS-XREF-004`: tp +10→11 (+1), fp +0→0 (+0), pending 7→6 (-1)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 6 — 2026-04-25T19:18:28Z — post-jss-corpus-filter

- **Corpus size:** 50 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=25, pinned=11

**Note:** Landed (w) JSS-only filter for corpus suggest. Tried (o) REFS-006 \pkg{X}: carve-out, rolled back; labels restored via apply-orphans.

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 32 | 11 | 19 | 74.42% | FAIL |
| citation | JSS-CITE-003 | 1 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 4 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 1 | 1 | 0 | 50.00% | FAIL |
| unknown | JSS-BIBTEX-004 | 4 | 2 | 0 | 66.67% | FAIL |
| unknown | JSS-CAP-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 99 | 3 | 0 | 97.06% | PASS |
| unknown | JSS-CAP-003 | 0 | 2 | 0 | 0.00% | FAIL |
| unknown | JSS-CODE-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 34 | 2 | 0 | 94.44% | PASS |
| unknown | JSS-HOUSE-001 | 159 | 1 | 0 | 99.38% | PASS |
| unknown | JSS-HOUSE-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 10 | 1 | 0 | 90.91% | PASS |
| unknown | JSS-MARKUP-001 | 485 | 16 | 255 | 96.81% | PASS |
| unknown | JSS-MARKUP-002 | 74 | 27 | 121 | 73.27% | FAIL |
| unknown | JSS-MARKUP-003 | 66 | 8 | 91 | 89.19% | FAIL |
| unknown | JSS-MARKUP-004 | 79 | 6 | 8 | 92.94% | PASS |
| unknown | JSS-NAME-001 | 1 | 1 | 0 | 50.00% | FAIL |
| unknown | JSS-NAME-002 | 5 | 1 | 0 | 83.33% | FAIL |
| unknown | JSS-OPER-001 | 32 | 1 | 1 | 96.97% | PASS |
| unknown | JSS-OPER-002 | 36 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 9 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-PRE-001 | 29 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 6 | 1 | 6 | 85.71% | FAIL |
| unknown | JSS-PRE-006 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 12 | 1 | 7 | 92.31% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 140 | 30 | 0 | 82.35% | FAIL |
| unknown | JSS-REFS-004 | 12 | 2 | 2 | 85.71% | FAIL |
| unknown | JSS-REFS-005 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 26 | 5 | 0 | 83.87% | FAIL |
| unknown | JSS-STRUCT-001 | 10 | 1 | 4 | 90.91% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 11 | 1 | 0 | 91.67% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 5 | 0 | 3 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 72 | 5 | 0 | 93.51% | PASS |
| unknown | JSS-XREF-004 | 13 | 0 | 8 | 100.00% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 17 | 9 | 9 | 65.38% | FAIL |
| unknown | JSS-ABBR-001 | 1 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 1 | 1 | 0 | 50.00% | FAIL |
| unknown | JSS-BIBTEX-004 | 4 | 2 | 0 | 66.67% | FAIL |
| unknown | JSS-CAP-002 | 4 | 1 | 0 | 80.00% | FAIL |
| unknown | JSS-CODE-003 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-001 | 29 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 1 | 1 | 0 | 50.00% | FAIL |
| unknown | JSS-MARKUP-001 | 165 | 1 | 108 | 99.40% | PASS |
| unknown | JSS-MARKUP-002 | 14 | 1 | 101 | 93.33% | PASS |
| unknown | JSS-MARKUP-003 | 7 | 0 | 2 | 100.00% | PASS |
| unknown | JSS-MARKUP-004 | 19 | 1 | 1 | 95.00% | PASS |
| unknown | JSS-NAME-002 | 5 | 1 | 0 | 83.33% | FAIL |
| unknown | JSS-OPER-001 | 7 | 1 | 1 | 87.50% | FAIL |
| unknown | JSS-OPER-002 | 27 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-001 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 4 | 0 | 2 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 4 | 1 | 3 | 80.00% | FAIL |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 140 | 30 | 0 | 82.35% | FAIL |
| unknown | JSS-REFS-004 | 12 | 2 | 2 | 85.71% | FAIL |
| unknown | JSS-REFS-005 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 26 | 5 | 0 | 83.87% | FAIL |
| unknown | JSS-STRUCT-001 | 4 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 10 | 1 | 0 | 90.91% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 3 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 20 | 5 | 0 | 80.00% | FAIL |
| unknown | JSS-XREF-004 | 11 | 0 | 6 | 100.00% | PASS |

### Delta vs. previous iteration

**Full corpus**

_(no rule-level changes)_

**Pinned only**

_(no rule-level changes)_

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 7 — 2026-04-26T14:00:49Z — post-jss-corpus-expansion

- **Corpus size:** 66 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=38, pinned=17

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 44 | 20 | 17 | 68.75% | FAIL |
| citation | JSS-CITE-003 | 5 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 3 | 2 | 0 | 60.00% | FAIL |
| unknown | JSS-ABBR-001 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 3 | 1 | 0 | 75.00% | FAIL |
| unknown | JSS-BIBTEX-004 | 13 | 2 | 1 | 86.67% | FAIL |
| unknown | JSS-CAP-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 99 | 12 | 0 | 89.19% | FAIL |
| unknown | JSS-CAP-003 | 4 | 24 | 0 | 14.29% | FAIL |
| unknown | JSS-CAP-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 64 | 5 | 0 | 92.75% | PASS |
| unknown | JSS-HOUSE-001 | 184 | 1 | 1 | 99.46% | PASS |
| unknown | JSS-HOUSE-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 22 | 2 | 0 | 91.67% | PASS |
| unknown | JSS-MARKUP-001 | 681 | 41 | 103 | 94.32% | PASS |
| unknown | JSS-MARKUP-002 | 186 | 31 | 14 | 85.71% | FAIL |
| unknown | JSS-MARKUP-003 | 158 | 13 | 2 | 92.40% | PASS |
| unknown | JSS-MARKUP-004 | 98 | 7 | 2 | 93.33% | PASS |
| unknown | JSS-NAME-001 | 1 | 1 | 0 | 50.00% | FAIL |
| unknown | JSS-NAME-002 | 10 | 6 | 0 | 62.50% | FAIL |
| unknown | JSS-OPER-001 | 56 | 1 | 0 | 98.25% | PASS |
| unknown | JSS-OPER-002 | 37 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 9 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-PRE-001 | 40 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 16 | 1 | 5 | 94.12% | PASS |
| unknown | JSS-PRE-006 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 14 | 2 | 12 | 87.50% | FAIL |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 320 | 31 | 0 | 91.17% | PASS |
| unknown | JSS-REFS-004 | 56 | 2 | 0 | 96.55% | PASS |
| unknown | JSS-REFS-005 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 104 | 5 | 0 | 95.41% | PASS |
| unknown | JSS-REFS-007 | 17 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 22 | 1 | 0 | 95.65% | PASS |
| unknown | JSS-STRUCT-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 18 | 1 | 0 | 94.74% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-WIDTH-001 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 12 | 2 | 4 | 85.71% | FAIL |
| unknown | JSS-XREF-002 | 90 | 5 | 0 | 94.74% | PASS |
| unknown | JSS-XREF-004 | 54 | 0 | 10 | 100.00% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 25 | 16 | 9 | 60.98% | FAIL |
| citation | JSS-CITE-003 | 3 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 0 | 2 | 0 | 0.00% | FAIL |
| unknown | JSS-ABBR-001 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 3 | 1 | 0 | 75.00% | FAIL |
| unknown | JSS-BIBTEX-004 | 13 | 2 | 1 | 86.67% | FAIL |
| unknown | JSS-CAP-002 | 4 | 6 | 0 | 40.00% | FAIL |
| unknown | JSS-CAP-003 | 1 | 12 | 0 | 7.69% | FAIL |
| unknown | JSS-CAP-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 30 | 1 | 0 | 96.77% | PASS |
| unknown | JSS-HOUSE-001 | 31 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 3 | 1 | 0 | 75.00% | FAIL |
| unknown | JSS-MARKUP-001 | 237 | 19 | 45 | 92.58% | PASS |
| unknown | JSS-MARKUP-002 | 104 | 3 | 12 | 97.20% | PASS |
| unknown | JSS-MARKUP-003 | 9 | 1 | 0 | 90.00% | PASS |
| unknown | JSS-MARKUP-004 | 20 | 1 | 0 | 95.24% | PASS |
| unknown | JSS-NAME-002 | 10 | 6 | 0 | 62.50% | FAIL |
| unknown | JSS-OPER-001 | 12 | 1 | 0 | 92.31% | PASS |
| unknown | JSS-OPER-002 | 27 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-001 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 6 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 1 | 3 | 83.33% | FAIL |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 320 | 31 | 0 | 91.17% | PASS |
| unknown | JSS-REFS-004 | 56 | 2 | 0 | 96.55% | PASS |
| unknown | JSS-REFS-005 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 104 | 5 | 0 | 95.41% | PASS |
| unknown | JSS-REFS-007 | 17 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 12 | 1 | 0 | 92.31% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 7 | 0 | 2 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 30 | 5 | 0 | 85.71% | FAIL |
| unknown | JSS-XREF-004 | 37 | 0 | 7 | 100.00% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-CITE-002`: tp +32→44 (+12), fp +11→20 (+9), pending 19→17 (-2)
- `JSS-CITE-003`: tp +1→5 (+4), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-CITE-004`: tp +1→3 (+2), fp +0→2 (+2), pending 0→0 (+0)
- `JSS-ABBR-001`: tp +4→7 (+3), fp +0→0 (+0), pending 1→0 (-1)
- `JSS-BIBTEX-003`: tp +1→3 (+2), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-BIBTEX-004`: tp +4→13 (+9), fp +2→2 (+0), pending 0→1 (+1)
- `JSS-CAP-002`: tp +99→99 (+0), fp +3→12 (+9), pending 0→0 (+0)
- `JSS-CAP-003`: tp +0→4 (+4), fp +2→24 (+22), pending 0→0 (+0)
- **new** `JSS-CAP-004`: tp=4 fp=0 pending=0
- `JSS-CODE-003`: tp +34→64 (+30), fp +2→5 (+3), pending 0→0 (+0)
- `JSS-HOUSE-001`: tp +159→184 (+25), fp +1→1 (+0), pending 0→1 (+1)
- `JSS-HOUSE-002`: tp +1→2 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-HOUSE-003`: tp +10→22 (+12), fp +1→2 (+1), pending 0→0 (+0)
- `JSS-MARKUP-001`: tp +485→681 (+196), fp +16→41 (+25), pending 255→103 (-152)
- `JSS-MARKUP-002`: tp +74→186 (+112), fp +27→31 (+4), pending 121→14 (-107)
- `JSS-MARKUP-003`: tp +66→158 (+92), fp +8→13 (+5), pending 91→2 (-89)
- `JSS-MARKUP-004`: tp +79→98 (+19), fp +6→7 (+1), pending 8→2 (-6)
- `JSS-NAME-002`: tp +5→10 (+5), fp +1→6 (+5), pending 0→0 (+0)
- `JSS-OPER-001`: tp +32→56 (+24), fp +1→1 (+0), pending 1→0 (-1)
- `JSS-OPER-002`: tp +36→37 (+1), fp +0→0 (+0), pending 0→0 (+0)
- **new** `JSS-OPER-003`: tp=2 fp=0 pending=0
- `JSS-PRE-001`: tp +29→40 (+11), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-PRE-002`: tp +4→4 (+0), fp +0→0 (+0), pending 0→1 (+1)
- `JSS-PRE-003`: tp +6→16 (+10), fp +1→1 (+0), pending 6→5 (-1)
- `JSS-PRE-006`: tp +3→10 (+7), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-PRE-007`: tp +12→14 (+2), fp +1→2 (+1), pending 7→12 (+5)
- `JSS-REFS-003`: tp +140→320 (+180), fp +30→31 (+1), pending 0→0 (+0)
- `JSS-REFS-004`: tp +12→56 (+44), fp +2→2 (+0), pending 2→0 (-2)
- `JSS-REFS-006`: tp +26→104 (+78), fp +5→5 (+0), pending 0→0 (+0)
- **new** `JSS-REFS-007`: tp=17 fp=0 pending=0
- `JSS-STRUCT-001`: tp +10→22 (+12), fp +1→1 (+0), pending 4→0 (-4)
- **new** `JSS-STRUCT-002`: tp=1 fp=0 pending=0
- `JSS-TYPO-001`: tp +11→18 (+7), fp +1→1 (+0), pending 0→0 (+0)
- **new** `JSS-WIDTH-001`: tp=4 fp=0 pending=0
- `JSS-XREF-001`: tp +5→12 (+7), fp +0→2 (+2), pending 3→4 (+1)
- `JSS-XREF-002`: tp +72→90 (+18), fp +5→5 (+0), pending 0→0 (+0)
- `JSS-XREF-004`: tp +13→54 (+41), fp +0→0 (+0), pending 8→10 (+2)

**Pinned only**

- `JSS-CITE-002`: tp +17→25 (+8), fp +9→16 (+7), pending 9→9 (+0)
- **new** `JSS-CITE-003`: tp=3 fp=0 pending=0
- **new** `JSS-CITE-004`: tp=0 fp=2 pending=0
- `JSS-ABBR-001`: tp +1→4 (+3), fp +0→0 (+0), pending 1→0 (-1)
- `JSS-BIBTEX-003`: tp +1→3 (+2), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-BIBTEX-004`: tp +4→13 (+9), fp +2→2 (+0), pending 0→1 (+1)
- `JSS-CAP-002`: tp +4→4 (+0), fp +1→6 (+5), pending 0→0 (+0)
- **new** `JSS-CAP-003`: tp=1 fp=12 pending=0
- **new** `JSS-CAP-004`: tp=4 fp=0 pending=0
- `JSS-CODE-003`: tp +7→30 (+23), fp +0→1 (+1), pending 0→0 (+0)
- `JSS-HOUSE-001`: tp +29→31 (+2), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-HOUSE-002`: tp +1→2 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-HOUSE-003`: tp +1→3 (+2), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-MARKUP-001`: tp +165→237 (+72), fp +1→19 (+18), pending 108→45 (-63)
- `JSS-MARKUP-002`: tp +14→104 (+90), fp +1→3 (+2), pending 101→12 (-89)
- `JSS-MARKUP-003`: tp +7→9 (+2), fp +0→1 (+1), pending 2→0 (-2)
- `JSS-MARKUP-004`: tp +19→20 (+1), fp +1→1 (+0), pending 1→0 (-1)
- `JSS-NAME-002`: tp +5→10 (+5), fp +1→6 (+5), pending 0→0 (+0)
- `JSS-OPER-001`: tp +7→12 (+5), fp +1→1 (+0), pending 1→0 (-1)
- `JSS-PRE-001`: tp +8→9 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-PRE-002`: tp +4→4 (+0), fp +0→0 (+0), pending 0→1 (+1)
- `JSS-PRE-003`: tp +4→6 (+2), fp +0→0 (+0), pending 2→1 (-1)
- `JSS-PRE-006`: tp +2→6 (+4), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-PRE-007`: tp +4→5 (+1), fp +1→1 (+0), pending 3→3 (+0)
- `JSS-REFS-003`: tp +140→320 (+180), fp +30→31 (+1), pending 0→0 (+0)
- `JSS-REFS-004`: tp +12→56 (+44), fp +2→2 (+0), pending 2→0 (-2)
- `JSS-REFS-006`: tp +26→104 (+78), fp +5→5 (+0), pending 0→0 (+0)
- **new** `JSS-REFS-007`: tp=17 fp=0 pending=0
- `JSS-STRUCT-001`: tp +4→6 (+2), fp +0→0 (+0), pending 1→0 (-1)
- **new** `JSS-STRUCT-002`: tp=1 fp=0 pending=0
- `JSS-TYPO-001`: tp +10→12 (+2), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-XREF-001`: tp +3→7 (+4), fp +0→0 (+0), pending 1→2 (+1)
- `JSS-XREF-002`: tp +20→30 (+10), fp +5→5 (+0), pending 0→0 (+0)
- `JSS-XREF-004`: tp +11→37 (+26), fp +0→0 (+0), pending 6→7 (+1)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 8 — 2026-04-26T14:04:59Z — post-cite-002-title

- **Corpus size:** 66 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=38, pinned=17

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 43 | 9 | 23 | 82.69% | FAIL |
| citation | JSS-CITE-003 | 5 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 3 | 2 | 0 | 60.00% | FAIL |
| unknown | JSS-ABBR-001 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 3 | 1 | 0 | 75.00% | FAIL |
| unknown | JSS-BIBTEX-004 | 13 | 2 | 1 | 86.67% | FAIL |
| unknown | JSS-CAP-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 99 | 12 | 0 | 89.19% | FAIL |
| unknown | JSS-CAP-003 | 4 | 24 | 0 | 14.29% | FAIL |
| unknown | JSS-CAP-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 64 | 5 | 0 | 92.75% | PASS |
| unknown | JSS-HOUSE-001 | 184 | 1 | 1 | 99.46% | PASS |
| unknown | JSS-HOUSE-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 22 | 2 | 0 | 91.67% | PASS |
| unknown | JSS-MARKUP-001 | 681 | 41 | 103 | 94.32% | PASS |
| unknown | JSS-MARKUP-002 | 186 | 31 | 14 | 85.71% | FAIL |
| unknown | JSS-MARKUP-003 | 158 | 13 | 2 | 92.40% | PASS |
| unknown | JSS-MARKUP-004 | 98 | 7 | 2 | 93.33% | PASS |
| unknown | JSS-NAME-001 | 1 | 1 | 0 | 50.00% | FAIL |
| unknown | JSS-NAME-002 | 10 | 6 | 0 | 62.50% | FAIL |
| unknown | JSS-OPER-001 | 56 | 1 | 0 | 98.25% | PASS |
| unknown | JSS-OPER-002 | 37 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 9 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-PRE-001 | 40 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 16 | 1 | 5 | 94.12% | PASS |
| unknown | JSS-PRE-006 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 14 | 2 | 12 | 87.50% | FAIL |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 320 | 31 | 0 | 91.17% | PASS |
| unknown | JSS-REFS-004 | 56 | 2 | 0 | 96.55% | PASS |
| unknown | JSS-REFS-005 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 104 | 5 | 0 | 95.41% | PASS |
| unknown | JSS-REFS-007 | 17 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 22 | 1 | 0 | 95.65% | PASS |
| unknown | JSS-STRUCT-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 18 | 1 | 0 | 94.74% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-WIDTH-001 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 12 | 2 | 4 | 85.71% | FAIL |
| unknown | JSS-XREF-002 | 90 | 5 | 0 | 94.74% | PASS |
| unknown | JSS-XREF-004 | 54 | 0 | 10 | 100.00% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 24 | 7 | 15 | 77.42% | FAIL |
| citation | JSS-CITE-003 | 3 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 0 | 2 | 0 | 0.00% | FAIL |
| unknown | JSS-ABBR-001 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 3 | 1 | 0 | 75.00% | FAIL |
| unknown | JSS-BIBTEX-004 | 13 | 2 | 1 | 86.67% | FAIL |
| unknown | JSS-CAP-002 | 4 | 6 | 0 | 40.00% | FAIL |
| unknown | JSS-CAP-003 | 1 | 12 | 0 | 7.69% | FAIL |
| unknown | JSS-CAP-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 30 | 1 | 0 | 96.77% | PASS |
| unknown | JSS-HOUSE-001 | 31 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 3 | 1 | 0 | 75.00% | FAIL |
| unknown | JSS-MARKUP-001 | 237 | 19 | 45 | 92.58% | PASS |
| unknown | JSS-MARKUP-002 | 104 | 3 | 12 | 97.20% | PASS |
| unknown | JSS-MARKUP-003 | 9 | 1 | 0 | 90.00% | PASS |
| unknown | JSS-MARKUP-004 | 20 | 1 | 0 | 95.24% | PASS |
| unknown | JSS-NAME-002 | 10 | 6 | 0 | 62.50% | FAIL |
| unknown | JSS-OPER-001 | 12 | 1 | 0 | 92.31% | PASS |
| unknown | JSS-OPER-002 | 27 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-001 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 6 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 1 | 3 | 83.33% | FAIL |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 320 | 31 | 0 | 91.17% | PASS |
| unknown | JSS-REFS-004 | 56 | 2 | 0 | 96.55% | PASS |
| unknown | JSS-REFS-005 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 104 | 5 | 0 | 95.41% | PASS |
| unknown | JSS-REFS-007 | 17 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 12 | 1 | 0 | 92.31% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 7 | 0 | 2 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 30 | 5 | 0 | 85.71% | FAIL |
| unknown | JSS-XREF-004 | 37 | 0 | 7 | 100.00% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-CITE-002`: tp +44→43 (-1), fp +20→9 (-11), pending 17→23 (+6)

**Pinned only**

- `JSS-CITE-002`: tp +25→24 (-1), fp +16→7 (-9), pending 9→15 (+6)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 9 — 2026-04-26T15:16:13Z — post-bibtex-004-cite-site

- **Corpus size:** 66 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=38, pinned=17

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 43 | 9 | 23 | 82.69% | FAIL |
| citation | JSS-CITE-003 | 5 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 3 | 2 | 0 | 60.00% | FAIL |
| unknown | JSS-ABBR-001 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 3 | 1 | 0 | 75.00% | FAIL |
| unknown | JSS-BIBTEX-004 | 11 | 2 | 2 | 84.62% | FAIL |
| unknown | JSS-CAP-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 99 | 12 | 0 | 89.19% | FAIL |
| unknown | JSS-CAP-003 | 4 | 24 | 0 | 14.29% | FAIL |
| unknown | JSS-CAP-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 64 | 5 | 0 | 92.75% | PASS |
| unknown | JSS-HOUSE-001 | 184 | 1 | 1 | 99.46% | PASS |
| unknown | JSS-HOUSE-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 22 | 2 | 0 | 91.67% | PASS |
| unknown | JSS-MARKUP-001 | 681 | 41 | 103 | 94.32% | PASS |
| unknown | JSS-MARKUP-002 | 186 | 31 | 14 | 85.71% | FAIL |
| unknown | JSS-MARKUP-003 | 158 | 13 | 2 | 92.40% | PASS |
| unknown | JSS-MARKUP-004 | 98 | 7 | 2 | 93.33% | PASS |
| unknown | JSS-NAME-001 | 1 | 1 | 0 | 50.00% | FAIL |
| unknown | JSS-NAME-002 | 10 | 6 | 0 | 62.50% | FAIL |
| unknown | JSS-OPER-001 | 56 | 1 | 0 | 98.25% | PASS |
| unknown | JSS-OPER-002 | 37 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 9 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-PRE-001 | 40 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 16 | 1 | 5 | 94.12% | PASS |
| unknown | JSS-PRE-006 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 14 | 2 | 12 | 87.50% | FAIL |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 320 | 31 | 0 | 91.17% | PASS |
| unknown | JSS-REFS-004 | 56 | 2 | 0 | 96.55% | PASS |
| unknown | JSS-REFS-005 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 104 | 5 | 0 | 95.41% | PASS |
| unknown | JSS-REFS-007 | 17 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 22 | 1 | 0 | 95.65% | PASS |
| unknown | JSS-STRUCT-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 18 | 1 | 0 | 94.74% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-WIDTH-001 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 12 | 2 | 4 | 85.71% | FAIL |
| unknown | JSS-XREF-002 | 90 | 5 | 0 | 94.74% | PASS |
| unknown | JSS-XREF-004 | 54 | 0 | 10 | 100.00% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 24 | 7 | 15 | 77.42% | FAIL |
| citation | JSS-CITE-003 | 3 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 0 | 2 | 0 | 0.00% | FAIL |
| unknown | JSS-ABBR-001 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 3 | 1 | 0 | 75.00% | FAIL |
| unknown | JSS-BIBTEX-004 | 7 | 0 | 2 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 4 | 6 | 0 | 40.00% | FAIL |
| unknown | JSS-CAP-003 | 1 | 12 | 0 | 7.69% | FAIL |
| unknown | JSS-CAP-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 30 | 1 | 0 | 96.77% | PASS |
| unknown | JSS-HOUSE-001 | 31 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 3 | 1 | 0 | 75.00% | FAIL |
| unknown | JSS-MARKUP-001 | 237 | 19 | 45 | 92.58% | PASS |
| unknown | JSS-MARKUP-002 | 104 | 3 | 12 | 97.20% | PASS |
| unknown | JSS-MARKUP-003 | 9 | 1 | 0 | 90.00% | PASS |
| unknown | JSS-MARKUP-004 | 20 | 1 | 0 | 95.24% | PASS |
| unknown | JSS-NAME-002 | 10 | 6 | 0 | 62.50% | FAIL |
| unknown | JSS-OPER-001 | 12 | 1 | 0 | 92.31% | PASS |
| unknown | JSS-OPER-002 | 27 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-001 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 6 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 1 | 3 | 83.33% | FAIL |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 320 | 31 | 0 | 91.17% | PASS |
| unknown | JSS-REFS-004 | 56 | 2 | 0 | 96.55% | PASS |
| unknown | JSS-REFS-005 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 104 | 5 | 0 | 95.41% | PASS |
| unknown | JSS-REFS-007 | 17 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 12 | 1 | 0 | 92.31% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 7 | 0 | 2 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 30 | 5 | 0 | 85.71% | FAIL |
| unknown | JSS-XREF-004 | 37 | 0 | 7 | 100.00% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-BIBTEX-004`: tp +13→11 (-2), fp +2→2 (+0), pending 1→2 (+1)

**Pinned only**

- `JSS-BIBTEX-004`: tp +13→7 (-6), fp +2→0 (-2), pending 1→2 (+1)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_
