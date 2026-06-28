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

## Iteration 10 — 2026-04-26T15:41:45Z — post-cap-003-runs

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
| unknown | JSS-CAP-003 | 4 | 8 | 0 | 33.33% | FAIL |
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
| unknown | JSS-CAP-003 | 1 | 2 | 0 | 33.33% | FAIL |
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

- `JSS-CAP-003`: tp +4→4 (+0), fp +24→8 (-16), pending 0→0 (+0)

**Pinned only**

- `JSS-CAP-003`: tp +1→1 (+0), fp +12→2 (-10), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 11 — 2026-04-27T18:29:01Z — post-iter11-batch

- **Corpus size:** 82 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=53, pinned=28

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 80 | 18 | 0 | 81.63% | FAIL |
| citation | JSS-CITE-003 | 5 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 4 | 2 | 0 | 66.67% | FAIL |
| unknown | JSS-ABBR-001 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 3 | 1 | 0 | 75.00% | FAIL |
| unknown | JSS-BIBTEX-004 | 13 | 3 | 0 | 81.25% | FAIL |
| unknown | JSS-CAP-001 | 1 | 1 | 0 | 50.00% | FAIL |
| unknown | JSS-CAP-002 | 124 | 14 | 0 | 89.86% | FAIL |
| unknown | JSS-CAP-003 | 4 | 18 | 0 | 18.18% | FAIL |
| unknown | JSS-CAP-004 | 6 | 2 | 0 | 75.00% | FAIL |
| unknown | JSS-CODE-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 81 | 12 | 0 | 87.10% | FAIL |
| unknown | JSS-HOUSE-001 | 216 | 4 | 0 | 98.18% | PASS |
| unknown | JSS-HOUSE-002 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 27 | 2 | 0 | 93.10% | PASS |
| unknown | JSS-MARKUP-001 | 795 | 64 | 0 | 92.55% | PASS |
| unknown | JSS-MARKUP-002 | 208 | 33 | 0 | 86.31% | FAIL |
| unknown | JSS-MARKUP-003 | 162 | 15 | 0 | 91.53% | PASS |
| unknown | JSS-MARKUP-004 | 109 | 9 | 0 | 92.37% | PASS |
| unknown | JSS-NAME-001 | 1 | 1 | 0 | 50.00% | FAIL |
| unknown | JSS-NAME-002 | 12 | 6 | 0 | 66.67% | FAIL |
| unknown | JSS-OPER-001 | 56 | 1 | 0 | 98.25% | PASS |
| unknown | JSS-OPER-002 | 37 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-003 | 3 | 2 | 0 | 60.00% | FAIL |
| unknown | JSS-OPER-004 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-001 | 43 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 2 | 0 | 66.67% | FAIL |
| unknown | JSS-PRE-003 | 21 | 1 | 0 | 95.45% | PASS |
| unknown | JSS-PRE-006 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 24 | 4 | 0 | 85.71% | FAIL |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 383 | 46 | 0 | 89.28% | FAIL |
| unknown | JSS-REFS-004 | 72 | 4 | 0 | 94.74% | PASS |
| unknown | JSS-REFS-005 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 111 | 51 | 0 | 68.52% | FAIL |
| unknown | JSS-REFS-007 | 21 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 22 | 2 | 0 | 91.67% | PASS |
| unknown | JSS-STRUCT-002 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 24 | 1 | 0 | 96.00% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 7 | 5 | 0 | 58.33% | FAIL |
| unknown | JSS-WIDTH-001 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 18 | 2 | 0 | 90.00% | PASS |
| unknown | JSS-XREF-002 | 111 | 9 | 0 | 92.50% | PASS |
| unknown | JSS-XREF-004 | 77 | 0 | 0 | 100.00% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 48 | 12 | 0 | 80.00% | FAIL |
| citation | JSS-CITE-003 | 3 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 0 | 2 | 0 | 0.00% | FAIL |
| unknown | JSS-ABBR-001 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 3 | 1 | 0 | 75.00% | FAIL |
| unknown | JSS-BIBTEX-004 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-CAP-002 | 22 | 7 | 0 | 75.86% | FAIL |
| unknown | JSS-CAP-003 | 1 | 8 | 0 | 11.11% | FAIL |
| unknown | JSS-CAP-004 | 6 | 1 | 0 | 85.71% | FAIL |
| unknown | JSS-CODE-003 | 35 | 6 | 0 | 85.37% | FAIL |
| unknown | JSS-HOUSE-001 | 39 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 5 | 1 | 0 | 83.33% | FAIL |
| unknown | JSS-MARKUP-001 | 281 | 26 | 0 | 91.53% | PASS |
| unknown | JSS-MARKUP-002 | 115 | 4 | 0 | 96.64% | PASS |
| unknown | JSS-MARKUP-003 | 13 | 1 | 0 | 92.86% | PASS |
| unknown | JSS-MARKUP-004 | 28 | 3 | 0 | 90.32% | PASS |
| unknown | JSS-NAME-002 | 12 | 6 | 0 | 66.67% | FAIL |
| unknown | JSS-OPER-001 | 12 | 1 | 0 | 92.31% | PASS |
| unknown | JSS-OPER-002 | 27 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 1 | 0 | 80.00% | FAIL |
| unknown | JSS-PRE-003 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 383 | 46 | 0 | 89.28% | FAIL |
| unknown | JSS-REFS-004 | 72 | 4 | 0 | 94.74% | PASS |
| unknown | JSS-REFS-005 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 111 | 51 | 0 | 68.52% | FAIL |
| unknown | JSS-REFS-007 | 21 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 6 | 1 | 0 | 85.71% | FAIL |
| unknown | JSS-STRUCT-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 15 | 1 | 0 | 93.75% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 41 | 5 | 0 | 89.13% | FAIL |
| unknown | JSS-XREF-004 | 49 | 0 | 0 | 100.00% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-CITE-002`: tp +43→80 (+37), fp +9→18 (+9), pending 23→0 (-23)
- `JSS-CITE-004`: tp +3→4 (+1), fp +2→2 (+0), pending 0→0 (+0)
- `JSS-ABBR-001`: tp +7→8 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-BIBTEX-004`: tp +11→13 (+2), fp +2→3 (+1), pending 2→0 (-2)
- `JSS-CAP-001`: tp +1→1 (+0), fp +0→1 (+1), pending 0→0 (+0)
- `JSS-CAP-002`: tp +99→124 (+25), fp +12→14 (+2), pending 0→0 (+0)
- `JSS-CAP-003`: tp +4→4 (+0), fp +8→18 (+10), pending 0→0 (+0)
- `JSS-CAP-004`: tp +4→6 (+2), fp +0→2 (+2), pending 0→0 (+0)
- `JSS-CODE-003`: tp +64→81 (+17), fp +5→12 (+7), pending 0→0 (+0)
- `JSS-HOUSE-001`: tp +184→216 (+32), fp +1→4 (+3), pending 1→0 (-1)
- `JSS-HOUSE-002`: tp +2→3 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-HOUSE-003`: tp +22→27 (+5), fp +2→2 (+0), pending 0→0 (+0)
- `JSS-MARKUP-001`: tp +681→795 (+114), fp +41→64 (+23), pending 103→0 (-103)
- `JSS-MARKUP-002`: tp +186→208 (+22), fp +31→33 (+2), pending 14→0 (-14)
- `JSS-MARKUP-003`: tp +158→162 (+4), fp +13→15 (+2), pending 2→0 (-2)
- `JSS-MARKUP-004`: tp +98→109 (+11), fp +7→9 (+2), pending 2→0 (-2)
- `JSS-NAME-002`: tp +10→12 (+2), fp +6→6 (+0), pending 0→0 (+0)
- `JSS-OPER-003`: tp +2→3 (+1), fp +0→2 (+2), pending 0→0 (+0)
- `JSS-OPER-004`: tp +9→13 (+4), fp +0→0 (+0), pending 1→0 (-1)
- `JSS-PRE-001`: tp +40→43 (+3), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-PRE-002`: tp +4→4 (+0), fp +0→2 (+2), pending 1→0 (-1)
- `JSS-PRE-003`: tp +16→21 (+5), fp +1→1 (+0), pending 5→0 (-5)
- `JSS-PRE-006`: tp +10→15 (+5), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-PRE-007`: tp +14→24 (+10), fp +2→4 (+2), pending 12→0 (-12)
- `JSS-REFS-003`: tp +320→383 (+63), fp +31→46 (+15), pending 0→0 (+0)
- `JSS-REFS-004`: tp +56→72 (+16), fp +2→4 (+2), pending 0→0 (+0)
- `JSS-REFS-006`: tp +104→111 (+7), fp +5→51 (+46), pending 0→0 (+0)
- `JSS-REFS-007`: tp +17→21 (+4), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-STRUCT-001`: tp +22→22 (+0), fp +1→2 (+1), pending 0→0 (+0)
- `JSS-STRUCT-002`: tp +1→3 (+2), fp +0→0 (+0), pending 0→0 (+0)
- **new** `JSS-STRUCT-006`: tp=2 fp=0 pending=0
- `JSS-TYPO-001`: tp +18→24 (+6), fp +1→1 (+0), pending 0→0 (+0)
- **new** `JSS-TYPO-004`: tp=7 fp=5 pending=0
- `JSS-XREF-001`: tp +12→18 (+6), fp +2→2 (+0), pending 4→0 (-4)
- `JSS-XREF-002`: tp +90→111 (+21), fp +5→9 (+4), pending 0→0 (+0)
- `JSS-XREF-004`: tp +54→77 (+23), fp +0→0 (+0), pending 10→0 (-10)

**Pinned only**

- `JSS-CITE-002`: tp +24→48 (+24), fp +7→12 (+5), pending 15→0 (-15)
- `JSS-ABBR-001`: tp +4→5 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-BIBTEX-004`: tp +7→8 (+1), fp +0→1 (+1), pending 2→0 (-2)
- `JSS-CAP-002`: tp +4→22 (+18), fp +6→7 (+1), pending 0→0 (+0)
- `JSS-CAP-003`: tp +1→1 (+0), fp +2→8 (+6), pending 0→0 (+0)
- `JSS-CAP-004`: tp +4→6 (+2), fp +0→1 (+1), pending 0→0 (+0)
- `JSS-CODE-003`: tp +30→35 (+5), fp +1→6 (+5), pending 0→0 (+0)
- `JSS-HOUSE-001`: tp +31→39 (+8), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-HOUSE-002`: tp +2→3 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-HOUSE-003`: tp +3→5 (+2), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-MARKUP-001`: tp +237→281 (+44), fp +19→26 (+7), pending 45→0 (-45)
- `JSS-MARKUP-002`: tp +104→115 (+11), fp +3→4 (+1), pending 12→0 (-12)
- `JSS-MARKUP-003`: tp +9→13 (+4), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-MARKUP-004`: tp +20→28 (+8), fp +1→3 (+2), pending 0→0 (+0)
- `JSS-NAME-002`: tp +10→12 (+2), fp +6→6 (+0), pending 0→0 (+0)
- **new** `JSS-OPER-004`: tp=3 fp=0 pending=0
- `JSS-PRE-001`: tp +9→10 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-PRE-002`: tp +4→4 (+0), fp +0→1 (+1), pending 1→0 (-1)
- `JSS-PRE-003`: tp +6→7 (+1), fp +0→0 (+0), pending 1→0 (-1)
- `JSS-PRE-006`: tp +6→9 (+3), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-PRE-007`: tp +5→8 (+3), fp +1→1 (+0), pending 3→0 (-3)
- `JSS-REFS-003`: tp +320→383 (+63), fp +31→46 (+15), pending 0→0 (+0)
- `JSS-REFS-004`: tp +56→72 (+16), fp +2→4 (+2), pending 0→0 (+0)
- `JSS-REFS-006`: tp +104→111 (+7), fp +5→51 (+46), pending 0→0 (+0)
- `JSS-REFS-007`: tp +17→21 (+4), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-STRUCT-001`: tp +6→6 (+0), fp +0→1 (+1), pending 0→0 (+0)
- `JSS-STRUCT-002`: tp +1→2 (+1), fp +0→0 (+0), pending 0→0 (+0)
- **new** `JSS-STRUCT-006`: tp=1 fp=0 pending=0
- `JSS-TYPO-001`: tp +12→15 (+3), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-XREF-001`: tp +7→10 (+3), fp +0→0 (+0), pending 2→0 (-2)
- `JSS-XREF-002`: tp +30→41 (+11), fp +5→5 (+0), pending 0→0 (+0)
- `JSS-XREF-004`: tp +37→49 (+12), fp +0→0 (+0), pending 7→0 (-7)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 12 — 2026-04-27T18:46:00Z — post-refs-006-pkg-markup

- **Corpus size:** 82 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=53, pinned=28

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 63 | 17 | 10 | 78.75% | FAIL |
| citation | JSS-CITE-003 | 5 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 4 | 2 | 0 | 66.67% | FAIL |
| unknown | JSS-ABBR-001 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 3 | 1 | 0 | 75.00% | FAIL |
| unknown | JSS-BIBTEX-004 | 13 | 3 | 0 | 81.25% | FAIL |
| unknown | JSS-CAP-001 | 1 | 1 | 0 | 50.00% | FAIL |
| unknown | JSS-CAP-002 | 124 | 14 | 0 | 89.86% | FAIL |
| unknown | JSS-CAP-003 | 4 | 18 | 0 | 18.18% | FAIL |
| unknown | JSS-CAP-004 | 6 | 2 | 0 | 75.00% | FAIL |
| unknown | JSS-CODE-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 81 | 12 | 0 | 87.10% | FAIL |
| unknown | JSS-HOUSE-001 | 216 | 4 | 0 | 98.18% | PASS |
| unknown | JSS-HOUSE-002 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 27 | 2 | 0 | 93.10% | PASS |
| unknown | JSS-MARKUP-001 | 795 | 64 | 0 | 92.55% | PASS |
| unknown | JSS-MARKUP-002 | 208 | 33 | 0 | 86.31% | FAIL |
| unknown | JSS-MARKUP-003 | 162 | 15 | 0 | 91.53% | PASS |
| unknown | JSS-MARKUP-004 | 109 | 9 | 0 | 92.37% | PASS |
| unknown | JSS-NAME-001 | 1 | 1 | 0 | 50.00% | FAIL |
| unknown | JSS-NAME-002 | 12 | 6 | 0 | 66.67% | FAIL |
| unknown | JSS-OPER-001 | 56 | 1 | 0 | 98.25% | PASS |
| unknown | JSS-OPER-002 | 37 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-003 | 3 | 2 | 0 | 60.00% | FAIL |
| unknown | JSS-OPER-004 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-001 | 43 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 2 | 0 | 66.67% | FAIL |
| unknown | JSS-PRE-003 | 21 | 1 | 0 | 95.45% | PASS |
| unknown | JSS-PRE-006 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 24 | 4 | 0 | 85.71% | FAIL |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 383 | 46 | 0 | 89.28% | FAIL |
| unknown | JSS-REFS-004 | 72 | 4 | 0 | 94.74% | PASS |
| unknown | JSS-REFS-005 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 42 | 4 | 0 | 91.30% | PASS |
| unknown | JSS-REFS-007 | 21 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 22 | 2 | 0 | 91.67% | PASS |
| unknown | JSS-STRUCT-002 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 24 | 1 | 0 | 96.00% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 7 | 5 | 0 | 58.33% | FAIL |
| unknown | JSS-WIDTH-001 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 18 | 2 | 0 | 90.00% | PASS |
| unknown | JSS-XREF-002 | 111 | 9 | 0 | 92.50% | PASS |
| unknown | JSS-XREF-004 | 77 | 0 | 0 | 100.00% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 35 | 11 | 7 | 76.09% | FAIL |
| citation | JSS-CITE-003 | 3 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 0 | 2 | 0 | 0.00% | FAIL |
| unknown | JSS-ABBR-001 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 3 | 1 | 0 | 75.00% | FAIL |
| unknown | JSS-BIBTEX-004 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-CAP-002 | 22 | 7 | 0 | 75.86% | FAIL |
| unknown | JSS-CAP-003 | 1 | 8 | 0 | 11.11% | FAIL |
| unknown | JSS-CAP-004 | 6 | 1 | 0 | 85.71% | FAIL |
| unknown | JSS-CODE-003 | 35 | 6 | 0 | 85.37% | FAIL |
| unknown | JSS-HOUSE-001 | 39 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 5 | 1 | 0 | 83.33% | FAIL |
| unknown | JSS-MARKUP-001 | 281 | 26 | 0 | 91.53% | PASS |
| unknown | JSS-MARKUP-002 | 115 | 4 | 0 | 96.64% | PASS |
| unknown | JSS-MARKUP-003 | 13 | 1 | 0 | 92.86% | PASS |
| unknown | JSS-MARKUP-004 | 28 | 3 | 0 | 90.32% | PASS |
| unknown | JSS-NAME-002 | 12 | 6 | 0 | 66.67% | FAIL |
| unknown | JSS-OPER-001 | 12 | 1 | 0 | 92.31% | PASS |
| unknown | JSS-OPER-002 | 27 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 1 | 0 | 80.00% | FAIL |
| unknown | JSS-PRE-003 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 383 | 46 | 0 | 89.28% | FAIL |
| unknown | JSS-REFS-004 | 72 | 4 | 0 | 94.74% | PASS |
| unknown | JSS-REFS-005 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 42 | 4 | 0 | 91.30% | PASS |
| unknown | JSS-REFS-007 | 21 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 6 | 1 | 0 | 85.71% | FAIL |
| unknown | JSS-STRUCT-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 15 | 1 | 0 | 93.75% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 41 | 5 | 0 | 89.13% | FAIL |
| unknown | JSS-XREF-004 | 49 | 0 | 0 | 100.00% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-CITE-002`: tp +80→63 (-17), fp +18→17 (-1), pending 0→10 (+10)
- `JSS-REFS-006`: tp +111→42 (-69), fp +51→4 (-47), pending 0→0 (+0)

**Pinned only**

- `JSS-CITE-002`: tp +48→35 (-13), fp +12→11 (-1), pending 0→7 (+7)
- `JSS-REFS-006`: tp +111→42 (-69), fp +51→4 (-47), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 13 — 2026-04-28T11:25:28Z — post-fp-cluster-cleanup

- **Corpus size:** 82 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=15, pinned=11

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 54 | 7 | 107 | 88.52% | FAIL |
| citation | JSS-CITE-003 | 5 | 0 | 3 | 100.00% | PASS |
| citation | JSS-CITE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 8 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 3 | 1 | 4 | 75.00% | FAIL |
| unknown | JSS-BIBTEX-004 | 13 | 3 | 10 | 81.25% | FAIL |
| unknown | JSS-CAP-001 | 1 | 1 | 2 | 50.00% | FAIL |
| unknown | JSS-CAP-002 | 124 | 14 | 17 | 89.86% | FAIL |
| unknown | JSS-CAP-003 | 4 | 18 | 9 | 18.18% | FAIL |
| unknown | JSS-CAP-004 | 6 | 2 | 3 | 75.00% | FAIL |
| unknown | JSS-CODE-001 | 1 | 0 | 14 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 71 | 8 | 18 | 89.87% | FAIL |
| unknown | JSS-HOUSE-001 | 216 | 4 | 45 | 98.18% | PASS |
| unknown | JSS-HOUSE-002 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 27 | 2 | 13 | 93.10% | PASS |
| unknown | JSS-MARKUP-001 | 788 | 58 | 64 | 93.14% | PASS |
| unknown | JSS-MARKUP-002 | 177 | 18 | 74 | 90.77% | PASS |
| unknown | JSS-MARKUP-003 | 160 | 9 | 10 | 94.67% | PASS |
| unknown | JSS-MARKUP-004 | 109 | 9 | 13 | 92.37% | PASS |
| unknown | JSS-NAME-001 | 1 | 1 | 0 | 50.00% | FAIL |
| unknown | JSS-NAME-002 | 12 | 6 | 20 | 66.67% | FAIL |
| unknown | JSS-OPER-001 | 56 | 1 | 0 | 98.25% | PASS |
| unknown | JSS-OPER-002 | 37 | 0 | 7 | 100.00% | PASS |
| unknown | JSS-OPER-003 | 3 | 2 | 4 | 60.00% | FAIL |
| unknown | JSS-OPER-004 | 13 | 0 | 8 | 100.00% | PASS |
| unknown | JSS-PRE-001 | 43 | 0 | 11 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 2 | 3 | 66.67% | FAIL |
| unknown | JSS-PRE-003 | 21 | 1 | 4 | 95.45% | PASS |
| unknown | JSS-PRE-006 | 15 | 0 | 8 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 24 | 4 | 4 | 85.71% | FAIL |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 383 | 46 | 311 | 89.28% | FAIL |
| unknown | JSS-REFS-004 | 72 | 4 | 44 | 94.74% | PASS |
| unknown | JSS-REFS-005 | 2 | 0 | 3 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 42 | 4 | 55 | 91.30% | PASS |
| unknown | JSS-REFS-007 | 21 | 0 | 22 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 22 | 2 | 11 | 91.67% | PASS |
| unknown | JSS-STRUCT-002 | 3 | 0 | 4 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 24 | 1 | 10 | 96.00% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 1 | 0 | 23 | 100.00% | PASS |
| unknown | JSS-WIDTH-001 | 4 | 0 | 6 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 18 | 2 | 8 | 90.00% | PASS |
| unknown | JSS-XREF-002 | 111 | 9 | 29 | 92.50% | PASS |
| unknown | JSS-XREF-004 | 77 | 0 | 32 | 100.00% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 30 | 5 | 20 | 85.71% | FAIL |
| citation | JSS-CITE-003 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 5 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 3 | 1 | 4 | 75.00% | FAIL |
| unknown | JSS-BIBTEX-004 | 8 | 1 | 8 | 88.89% | FAIL |
| unknown | JSS-CAP-002 | 22 | 7 | 10 | 75.86% | FAIL |
| unknown | JSS-CAP-003 | 1 | 8 | 4 | 11.11% | FAIL |
| unknown | JSS-CAP-004 | 6 | 1 | 2 | 85.71% | FAIL |
| unknown | JSS-CODE-001 | 0 | 0 | 12 | — | NOT MEASURED |
| unknown | JSS-CODE-003 | 31 | 4 | 11 | 88.57% | FAIL |
| unknown | JSS-HOUSE-001 | 39 | 0 | 19 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 5 | 1 | 5 | 83.33% | FAIL |
| unknown | JSS-MARKUP-001 | 278 | 24 | 39 | 92.05% | PASS |
| unknown | JSS-MARKUP-002 | 115 | 4 | 1 | 96.64% | PASS |
| unknown | JSS-MARKUP-003 | 13 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-MARKUP-004 | 28 | 3 | 5 | 90.32% | PASS |
| unknown | JSS-NAME-002 | 12 | 6 | 20 | 66.67% | FAIL |
| unknown | JSS-OPER-001 | 12 | 1 | 0 | 92.31% | PASS |
| unknown | JSS-OPER-002 | 27 | 0 | 6 | 100.00% | PASS |
| unknown | JSS-OPER-003 | 0 | 0 | 4 | — | NOT MEASURED |
| unknown | JSS-OPER-004 | 3 | 0 | 8 | 100.00% | PASS |
| unknown | JSS-PRE-001 | 10 | 0 | 4 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 1 | 0 | 80.00% | FAIL |
| unknown | JSS-PRE-003 | 7 | 0 | 2 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 9 | 0 | 3 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 8 | 1 | 2 | 88.89% | FAIL |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 383 | 46 | 311 | 89.28% | FAIL |
| unknown | JSS-REFS-004 | 72 | 4 | 44 | 94.74% | PASS |
| unknown | JSS-REFS-005 | 2 | 0 | 3 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 42 | 4 | 55 | 91.30% | PASS |
| unknown | JSS-REFS-007 | 21 | 0 | 22 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 6 | 1 | 5 | 85.71% | FAIL |
| unknown | JSS-STRUCT-002 | 2 | 0 | 2 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 15 | 1 | 9 | 93.75% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 0 | 0 | 16 | — | NOT MEASURED |
| unknown | JSS-WIDTH-001 | 0 | 0 | 5 | — | NOT MEASURED |
| unknown | JSS-XREF-001 | 10 | 0 | 7 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 41 | 5 | 23 | 89.13% | FAIL |
| unknown | JSS-XREF-004 | 49 | 0 | 28 | 100.00% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-CITE-002`: tp +63→54 (-9), fp +17→7 (-10), pending 10→107 (+97)
- `JSS-CITE-003`: tp +5→5 (+0), fp +0→0 (+0), pending 0→3 (+3)
- `JSS-CITE-004`: tp +4→4 (+0), fp +2→0 (-2), pending 0→0 (+0)
- `JSS-ABBR-001`: tp +8→8 (+0), fp +0→0 (+0), pending 0→1 (+1)
- `JSS-BIBTEX-003`: tp +3→3 (+0), fp +1→1 (+0), pending 0→4 (+4)
- `JSS-BIBTEX-004`: tp +13→13 (+0), fp +3→3 (+0), pending 0→10 (+10)
- `JSS-CAP-001`: tp +1→1 (+0), fp +1→1 (+0), pending 0→2 (+2)
- `JSS-CAP-002`: tp +124→124 (+0), fp +14→14 (+0), pending 0→17 (+17)
- `JSS-CAP-003`: tp +4→4 (+0), fp +18→18 (+0), pending 0→9 (+9)
- `JSS-CAP-004`: tp +6→6 (+0), fp +2→2 (+0), pending 0→3 (+3)
- `JSS-CODE-001`: tp +1→1 (+0), fp +0→0 (+0), pending 0→14 (+14)
- `JSS-CODE-003`: tp +81→71 (-10), fp +12→8 (-4), pending 0→18 (+18)
- `JSS-HOUSE-001`: tp +216→216 (+0), fp +4→4 (+0), pending 0→45 (+45)
- `JSS-HOUSE-003`: tp +27→27 (+0), fp +2→2 (+0), pending 0→13 (+13)
- `JSS-MARKUP-001`: tp +795→788 (-7), fp +64→58 (-6), pending 0→64 (+64)
- `JSS-MARKUP-002`: tp +208→177 (-31), fp +33→18 (-15), pending 0→74 (+74)
- `JSS-MARKUP-003`: tp +162→160 (-2), fp +15→9 (-6), pending 0→10 (+10)
- `JSS-MARKUP-004`: tp +109→109 (+0), fp +9→9 (+0), pending 0→13 (+13)
- `JSS-NAME-002`: tp +12→12 (+0), fp +6→6 (+0), pending 0→20 (+20)
- `JSS-OPER-002`: tp +37→37 (+0), fp +0→0 (+0), pending 0→7 (+7)
- `JSS-OPER-003`: tp +3→3 (+0), fp +2→2 (+0), pending 0→4 (+4)
- `JSS-OPER-004`: tp +13→13 (+0), fp +0→0 (+0), pending 0→8 (+8)
- `JSS-PRE-001`: tp +43→43 (+0), fp +0→0 (+0), pending 0→11 (+11)
- `JSS-PRE-002`: tp +4→4 (+0), fp +2→2 (+0), pending 0→3 (+3)
- `JSS-PRE-003`: tp +21→21 (+0), fp +1→1 (+0), pending 0→4 (+4)
- `JSS-PRE-006`: tp +15→15 (+0), fp +0→0 (+0), pending 0→8 (+8)
- `JSS-PRE-007`: tp +24→24 (+0), fp +4→4 (+0), pending 0→4 (+4)
- `JSS-REFS-003`: tp +383→383 (+0), fp +46→46 (+0), pending 0→311 (+311)
- `JSS-REFS-004`: tp +72→72 (+0), fp +4→4 (+0), pending 0→44 (+44)
- `JSS-REFS-005`: tp +2→2 (+0), fp +0→0 (+0), pending 0→3 (+3)
- `JSS-REFS-006`: tp +42→42 (+0), fp +4→4 (+0), pending 0→55 (+55)
- `JSS-REFS-007`: tp +21→21 (+0), fp +0→0 (+0), pending 0→22 (+22)
- `JSS-STRUCT-001`: tp +22→22 (+0), fp +2→2 (+0), pending 0→11 (+11)
- `JSS-STRUCT-002`: tp +3→3 (+0), fp +0→0 (+0), pending 0→4 (+4)
- `JSS-TYPO-001`: tp +24→24 (+0), fp +1→1 (+0), pending 0→10 (+10)
- `JSS-TYPO-004`: tp +7→1 (-6), fp +5→0 (-5), pending 0→23 (+23)
- `JSS-WIDTH-001`: tp +4→4 (+0), fp +0→0 (+0), pending 0→6 (+6)
- `JSS-XREF-001`: tp +18→18 (+0), fp +2→2 (+0), pending 0→8 (+8)
- `JSS-XREF-002`: tp +111→111 (+0), fp +9→9 (+0), pending 0→29 (+29)
- `JSS-XREF-004`: tp +77→77 (+0), fp +0→0 (+0), pending 0→32 (+32)

**Pinned only**

- `JSS-CITE-002`: tp +35→30 (-5), fp +11→5 (-6), pending 7→20 (+13)
- `JSS-ABBR-001`: tp +5→5 (+0), fp +0→0 (+0), pending 0→1 (+1)
- `JSS-BIBTEX-003`: tp +3→3 (+0), fp +1→1 (+0), pending 0→4 (+4)
- `JSS-BIBTEX-004`: tp +8→8 (+0), fp +1→1 (+0), pending 0→8 (+8)
- `JSS-CAP-002`: tp +22→22 (+0), fp +7→7 (+0), pending 0→10 (+10)
- `JSS-CAP-003`: tp +1→1 (+0), fp +8→8 (+0), pending 0→4 (+4)
- `JSS-CAP-004`: tp +6→6 (+0), fp +1→1 (+0), pending 0→2 (+2)
- **new** `JSS-CODE-001`: tp=0 fp=0 pending=12
- `JSS-CODE-003`: tp +35→31 (-4), fp +6→4 (-2), pending 0→11 (+11)
- `JSS-HOUSE-001`: tp +39→39 (+0), fp +0→0 (+0), pending 0→19 (+19)
- `JSS-HOUSE-003`: tp +5→5 (+0), fp +1→1 (+0), pending 0→5 (+5)
- `JSS-MARKUP-001`: tp +281→278 (-3), fp +26→24 (-2), pending 0→39 (+39)
- `JSS-MARKUP-002`: tp +115→115 (+0), fp +4→4 (+0), pending 0→1 (+1)
- `JSS-MARKUP-003`: tp +13→13 (+0), fp +1→0 (-1), pending 0→1 (+1)
- `JSS-MARKUP-004`: tp +28→28 (+0), fp +3→3 (+0), pending 0→5 (+5)
- `JSS-NAME-002`: tp +12→12 (+0), fp +6→6 (+0), pending 0→20 (+20)
- `JSS-OPER-002`: tp +27→27 (+0), fp +0→0 (+0), pending 0→6 (+6)
- **new** `JSS-OPER-003`: tp=0 fp=0 pending=4
- `JSS-OPER-004`: tp +3→3 (+0), fp +0→0 (+0), pending 0→8 (+8)
- `JSS-PRE-001`: tp +10→10 (+0), fp +0→0 (+0), pending 0→4 (+4)
- `JSS-PRE-003`: tp +7→7 (+0), fp +0→0 (+0), pending 0→2 (+2)
- `JSS-PRE-006`: tp +9→9 (+0), fp +0→0 (+0), pending 0→3 (+3)
- `JSS-PRE-007`: tp +8→8 (+0), fp +1→1 (+0), pending 0→2 (+2)
- `JSS-REFS-003`: tp +383→383 (+0), fp +46→46 (+0), pending 0→311 (+311)
- `JSS-REFS-004`: tp +72→72 (+0), fp +4→4 (+0), pending 0→44 (+44)
- `JSS-REFS-005`: tp +2→2 (+0), fp +0→0 (+0), pending 0→3 (+3)
- `JSS-REFS-006`: tp +42→42 (+0), fp +4→4 (+0), pending 0→55 (+55)
- `JSS-REFS-007`: tp +21→21 (+0), fp +0→0 (+0), pending 0→22 (+22)
- `JSS-STRUCT-001`: tp +6→6 (+0), fp +1→1 (+0), pending 0→5 (+5)
- `JSS-STRUCT-002`: tp +2→2 (+0), fp +0→0 (+0), pending 0→2 (+2)
- `JSS-TYPO-001`: tp +15→15 (+0), fp +1→1 (+0), pending 0→9 (+9)
- **new** `JSS-TYPO-004`: tp=0 fp=0 pending=16
- **new** `JSS-WIDTH-001`: tp=0 fp=0 pending=5
- `JSS-XREF-001`: tp +10→10 (+0), fp +0→0 (+0), pending 0→7 (+7)
- `JSS-XREF-002`: tp +41→41 (+0), fp +5→5 (+0), pending 0→23 (+23)
- `JSS-XREF-004`: tp +49→49 (+0), fp +0→0 (+0), pending 0→28 (+28)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

Closed by iteration 14, but iteration 14 was a corpus expansion
(82 → 98 papers, +16 JSS-counterpart vignettes), not a continuation
of the fix loop. The post-cleanup state was preserved on the existing
82 papers; the iter-14 numbers reflect both that state and the new
papers. New FP pressure surfaced by the larger corpus:

- **JSS-MARKUP-001**: fp 58 → 89 (+31) — single-letter `R`/`C` ambiguity
  resurfaces on the new manuscripts (math symbol, name initial in
  `\bibitem`, `.r` filenames).
- **JSS-CITE-002**: fp 7 → 29 (+22) — drove the iter-15 fix cycle.
  Cluster split: heading/Keywords (3), `\citep[...]` optarg (~12),
  bibliography (3), base-R packages (3), wrapper macros (5).
- **JSS-CAP-003**: fp 18 → 29 (+11) — caption-style misfires multiplied;
  many at column 1 of the `\caption{}` line with an "off by 2"
  verdict-reason cluster.
- **JSS-OPER-002**: 0 → 7 — `T` as upper bound of sums/products/
  integrals mistaken for transpose; new pattern from the new corpus.
- **JSS-TYPO-004**: 0 → 7 — caption-position policy fires in both
  directions (3 "before content", 2 "after"); needs table-vs-figure
  branching.
- **JSS-CAP-002**: fp 14 → 21 (+7) — hyphenated proper names
  (Hardy-Weinberg, Newey-West, etc.) tripping the second-word check.

These clusters drove iter-14's Findings + Plan.

## Iteration 14 — 2026-04-28T19:13:19Z — iter-14-baseline

- **Corpus size:** 98 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=23, pinned=19

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 163 | 29 | 0 | 84.90% | FAIL |
| citation | JSS-CITE-003 | 8 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-BIBTEX-004 | 25 | 3 | 0 | 89.29% | FAIL |
| unknown | JSS-CAP-001 | 2 | 3 | 0 | 40.00% | FAIL |
| unknown | JSS-CAP-002 | 157 | 21 | 0 | 88.20% | FAIL |
| unknown | JSS-CAP-003 | 18 | 29 | 0 | 38.30% | FAIL |
| unknown | JSS-CAP-004 | 10 | 4 | 0 | 71.43% | FAIL |
| unknown | JSS-CODE-001 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 98 | 9 | 0 | 91.59% | PASS |
| unknown | JSS-HOUSE-001 | 263 | 4 | 0 | 98.50% | PASS |
| unknown | JSS-HOUSE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 45 | 2 | 0 | 95.74% | PASS |
| unknown | JSS-MARKUP-001 | 853 | 89 | 0 | 90.55% | PASS |
| unknown | JSS-MARKUP-002 | 250 | 19 | 0 | 92.94% | PASS |
| unknown | JSS-MARKUP-003 | 171 | 9 | 0 | 95.00% | PASS |
| unknown | JSS-MARKUP-004 | 121 | 10 | 0 | 92.37% | PASS |
| unknown | JSS-NAME-001 | 2 | 1 | 0 | 66.67% | FAIL |
| unknown | JSS-NAME-002 | 33 | 10 | 0 | 76.74% | FAIL |
| unknown | JSS-OPER-001 | 57 | 1 | 0 | 98.28% | PASS |
| unknown | JSS-OPER-002 | 37 | 7 | 0 | 84.09% | FAIL |
| unknown | JSS-OPER-003 | 12 | 2 | 0 | 85.71% | FAIL |
| unknown | JSS-OPER-004 | 21 | 1 | 0 | 95.45% | PASS |
| unknown | JSS-PRE-001 | 56 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 7 | 3 | 0 | 70.00% | FAIL |
| unknown | JSS-PRE-003 | 25 | 1 | 0 | 96.15% | PASS |
| unknown | JSS-PRE-006 | 24 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 28 | 5 | 0 | 84.85% | FAIL |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 814 | 53 | 0 | 93.89% | PASS |
| unknown | JSS-REFS-004 | 129 | 4 | 0 | 96.99% | PASS |
| unknown | JSS-REFS-005 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 124 | 5 | 0 | 96.12% | PASS |
| unknown | JSS-REFS-007 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 33 | 4 | 0 | 89.19% | FAIL |
| unknown | JSS-STRUCT-002 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 41 | 1 | 0 | 97.62% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 7 | 0 | 77.42% | FAIL |
| unknown | JSS-WIDTH-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 33 | 3 | 0 | 91.67% | PASS |
| unknown | JSS-XREF-002 | 152 | 9 | 0 | 94.41% | PASS |
| unknown | JSS-XREF-004 | 123 | 3 | 0 | 97.62% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 53 | 26 | 0 | 67.09% | FAIL |
| citation | JSS-CITE-003 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-BIBTEX-004 | 18 | 1 | 0 | 94.74% | PASS |
| unknown | JSS-CAP-001 | 0 | 1 | 0 | 0.00% | FAIL |
| unknown | JSS-CAP-002 | 52 | 10 | 0 | 83.87% | FAIL |
| unknown | JSS-CAP-003 | 13 | 15 | 0 | 46.43% | FAIL |
| unknown | JSS-CAP-004 | 9 | 3 | 0 | 75.00% | FAIL |
| unknown | JSS-CODE-001 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 51 | 5 | 0 | 91.07% | PASS |
| unknown | JSS-HOUSE-001 | 59 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 15 | 1 | 0 | 93.75% | PASS |
| unknown | JSS-MARKUP-001 | 314 | 47 | 0 | 86.98% | FAIL |
| unknown | JSS-MARKUP-002 | 116 | 4 | 0 | 96.67% | PASS |
| unknown | JSS-MARKUP-003 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-004 | 33 | 3 | 0 | 91.67% | PASS |
| unknown | JSS-NAME-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 33 | 10 | 0 | 76.74% | FAIL |
| unknown | JSS-OPER-001 | 12 | 1 | 0 | 92.31% | PASS |
| unknown | JSS-OPER-002 | 27 | 6 | 0 | 81.82% | FAIL |
| unknown | JSS-OPER-003 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 11 | 1 | 0 | 91.67% | PASS |
| unknown | JSS-PRE-001 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 2 | 0 | 66.67% | FAIL |
| unknown | JSS-PRE-003 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 10 | 2 | 0 | 83.33% | FAIL |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 814 | 53 | 0 | 93.89% | PASS |
| unknown | JSS-REFS-004 | 129 | 4 | 0 | 96.99% | PASS |
| unknown | JSS-REFS-005 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 124 | 5 | 0 | 96.12% | PASS |
| unknown | JSS-REFS-007 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 11 | 2 | 0 | 84.62% | FAIL |
| unknown | JSS-STRUCT-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 27 | 1 | 0 | 96.43% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 19 | 4 | 0 | 82.61% | FAIL |
| unknown | JSS-WIDTH-001 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 25 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 76 | 5 | 0 | 93.83% | PASS |
| unknown | JSS-XREF-004 | 86 | 3 | 0 | 96.63% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-CITE-002`: tp +54→163 (+109), fp +7→29 (+22), pending 107→0 (-107)
- `JSS-CITE-003`: tp +5→8 (+3), fp +0→0 (+0), pending 3→0 (-3)
- `JSS-ABBR-001`: tp +8→10 (+2), fp +0→0 (+0), pending 1→0 (-1)
- `JSS-BIBTEX-002`: tp +1→2 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-BIBTEX-003`: tp +3→8 (+5), fp +1→1 (+0), pending 4→0 (-4)
- `JSS-BIBTEX-004`: tp +13→25 (+12), fp +3→3 (+0), pending 10→0 (-10)
- `JSS-CAP-001`: tp +1→2 (+1), fp +1→3 (+2), pending 2→0 (-2)
- `JSS-CAP-002`: tp +124→157 (+33), fp +14→21 (+7), pending 17→0 (-17)
- `JSS-CAP-003`: tp +4→18 (+14), fp +18→29 (+11), pending 9→0 (-9)
- `JSS-CAP-004`: tp +6→10 (+4), fp +2→4 (+2), pending 3→0 (-3)
- `JSS-CODE-001`: tp +1→15 (+14), fp +0→0 (+0), pending 14→0 (-14)
- `JSS-CODE-003`: tp +71→98 (+27), fp +8→9 (+1), pending 18→0 (-18)
- `JSS-HOUSE-001`: tp +216→263 (+47), fp +4→4 (+0), pending 45→0 (-45)
- `JSS-HOUSE-002`: tp +3→4 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-HOUSE-003`: tp +27→45 (+18), fp +2→2 (+0), pending 13→0 (-13)
- `JSS-MARKUP-001`: tp +788→853 (+65), fp +58→89 (+31), pending 64→0 (-64)
- `JSS-MARKUP-002`: tp +177→250 (+73), fp +18→19 (+1), pending 74→0 (-74)
- `JSS-MARKUP-003`: tp +160→171 (+11), fp +9→9 (+0), pending 10→0 (-10)
- `JSS-MARKUP-004`: tp +109→121 (+12), fp +9→10 (+1), pending 13→0 (-13)
- `JSS-NAME-001`: tp +1→2 (+1), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-NAME-002`: tp +12→33 (+21), fp +6→10 (+4), pending 20→0 (-20)
- `JSS-OPER-001`: tp +56→57 (+1), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-OPER-002`: tp +37→37 (+0), fp +0→7 (+7), pending 7→0 (-7)
- `JSS-OPER-003`: tp +3→12 (+9), fp +2→2 (+0), pending 4→0 (-4)
- `JSS-OPER-004`: tp +13→21 (+8), fp +0→1 (+1), pending 8→0 (-8)
- `JSS-PRE-001`: tp +43→56 (+13), fp +0→0 (+0), pending 11→0 (-11)
- `JSS-PRE-002`: tp +4→7 (+3), fp +2→3 (+1), pending 3→0 (-3)
- `JSS-PRE-003`: tp +21→25 (+4), fp +1→1 (+0), pending 4→0 (-4)
- `JSS-PRE-006`: tp +15→24 (+9), fp +0→0 (+0), pending 8→0 (-8)
- `JSS-PRE-007`: tp +24→28 (+4), fp +4→5 (+1), pending 4→0 (-4)
- `JSS-REFS-003`: tp +383→814 (+431), fp +46→53 (+7), pending 311→0 (-311)
- `JSS-REFS-004`: tp +72→129 (+57), fp +4→4 (+0), pending 44→0 (-44)
- `JSS-REFS-005`: tp +2→5 (+3), fp +0→0 (+0), pending 3→0 (-3)
- `JSS-REFS-006`: tp +42→124 (+82), fp +4→5 (+1), pending 55→0 (-55)
- `JSS-REFS-007`: tp +21→53 (+32), fp +0→0 (+0), pending 22→0 (-22)
- `JSS-STRUCT-001`: tp +22→33 (+11), fp +2→4 (+2), pending 11→0 (-11)
- `JSS-STRUCT-002`: tp +3→8 (+5), fp +0→0 (+0), pending 4→0 (-4)
- **new** `JSS-STRUCT-003`: tp=1 fp=0 pending=0
- `JSS-STRUCT-004`: tp +2→3 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-STRUCT-005`: tp +3→4 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-TYPO-001`: tp +24→41 (+17), fp +1→1 (+0), pending 10→0 (-10)
- `JSS-TYPO-004`: tp +1→24 (+23), fp +0→7 (+7), pending 23→0 (-23)
- `JSS-WIDTH-001`: tp +4→10 (+6), fp +0→0 (+0), pending 6→0 (-6)
- `JSS-XREF-001`: tp +18→33 (+15), fp +2→3 (+1), pending 8→0 (-8)
- `JSS-XREF-002`: tp +111→152 (+41), fp +9→9 (+0), pending 29→0 (-29)
- `JSS-XREF-004`: tp +77→123 (+46), fp +0→3 (+3), pending 32→0 (-32)

**Pinned only**

- `JSS-CITE-002`: tp +30→53 (+23), fp +5→26 (+21), pending 20→0 (-20)
- `JSS-ABBR-001`: tp +5→7 (+2), fp +0→0 (+0), pending 1→0 (-1)
- `JSS-BIBTEX-002`: tp +1→2 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-BIBTEX-003`: tp +3→8 (+5), fp +1→1 (+0), pending 4→0 (-4)
- `JSS-BIBTEX-004`: tp +8→18 (+10), fp +1→1 (+0), pending 8→0 (-8)
- **new** `JSS-CAP-001`: tp=0 fp=1 pending=0
- `JSS-CAP-002`: tp +22→52 (+30), fp +7→10 (+3), pending 10→0 (-10)
- `JSS-CAP-003`: tp +1→13 (+12), fp +8→15 (+7), pending 4→0 (-4)
- `JSS-CAP-004`: tp +6→9 (+3), fp +1→3 (+2), pending 2→0 (-2)
- `JSS-CODE-001`: tp +0→12 (+12), fp +0→0 (+0), pending 12→0 (-12)
- `JSS-CODE-003`: tp +31→51 (+20), fp +4→5 (+1), pending 11→0 (-11)
- `JSS-HOUSE-001`: tp +39→59 (+20), fp +0→0 (+0), pending 19→0 (-19)
- `JSS-HOUSE-002`: tp +3→4 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-HOUSE-003`: tp +5→15 (+10), fp +1→1 (+0), pending 5→0 (-5)
- `JSS-MARKUP-001`: tp +278→314 (+36), fp +24→47 (+23), pending 39→0 (-39)
- `JSS-MARKUP-002`: tp +115→116 (+1), fp +4→4 (+0), pending 1→0 (-1)
- `JSS-MARKUP-003`: tp +13→15 (+2), fp +0→0 (+0), pending 1→0 (-1)
- `JSS-MARKUP-004`: tp +28→33 (+5), fp +3→3 (+0), pending 5→0 (-5)
- **new** `JSS-NAME-001`: tp=1 fp=0 pending=0
- `JSS-NAME-002`: tp +12→33 (+21), fp +6→10 (+4), pending 20→0 (-20)
- `JSS-OPER-002`: tp +27→27 (+0), fp +0→6 (+6), pending 6→0 (-6)
- `JSS-OPER-003`: tp +0→9 (+9), fp +0→0 (+0), pending 4→0 (-4)
- `JSS-OPER-004`: tp +3→11 (+8), fp +0→1 (+1), pending 8→0 (-8)
- `JSS-PRE-001`: tp +10→16 (+6), fp +0→0 (+0), pending 4→0 (-4)
- `JSS-PRE-002`: tp +4→4 (+0), fp +1→2 (+1), pending 0→0 (+0)
- `JSS-PRE-003`: tp +7→9 (+2), fp +0→0 (+0), pending 2→0 (-2)
- `JSS-PRE-006`: tp +9→13 (+4), fp +0→0 (+0), pending 3→0 (-3)
- `JSS-PRE-007`: tp +8→10 (+2), fp +1→2 (+1), pending 2→0 (-2)
- `JSS-REFS-003`: tp +383→814 (+431), fp +46→53 (+7), pending 311→0 (-311)
- `JSS-REFS-004`: tp +72→129 (+57), fp +4→4 (+0), pending 44→0 (-44)
- `JSS-REFS-005`: tp +2→5 (+3), fp +0→0 (+0), pending 3→0 (-3)
- `JSS-REFS-006`: tp +42→124 (+82), fp +4→5 (+1), pending 55→0 (-55)
- `JSS-REFS-007`: tp +21→53 (+32), fp +0→0 (+0), pending 22→0 (-22)
- `JSS-STRUCT-001`: tp +6→11 (+5), fp +1→2 (+1), pending 5→0 (-5)
- `JSS-STRUCT-002`: tp +2→5 (+3), fp +0→0 (+0), pending 2→0 (-2)
- **new** `JSS-STRUCT-003`: tp=1 fp=0 pending=0
- `JSS-STRUCT-004`: tp +1→2 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-STRUCT-005`: tp +2→3 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-TYPO-001`: tp +15→27 (+12), fp +1→1 (+0), pending 9→0 (-9)
- `JSS-TYPO-004`: tp +0→19 (+19), fp +0→4 (+4), pending 16→0 (-16)
- `JSS-WIDTH-001`: tp +0→5 (+5), fp +0→0 (+0), pending 5→0 (-5)
- `JSS-XREF-001`: tp +10→25 (+15), fp +0→0 (+0), pending 7→0 (-7)
- `JSS-XREF-002`: tp +41→76 (+35), fp +5→5 (+0), pending 23→0 (-23)
- `JSS-XREF-004`: tp +49→86 (+37), fp +0→3 (+3), pending 28→0 (-28)

### Findings / suggestions

The grown corpus (82 → 98) re-surfaced FP clusters that had
shrunk in iter-13. Top targets for the next iteration, ranked by
absolute FP count and ease of fix:

| rank | rule | fp | sketch |
|---|---|---:|---|
| 1 | JSS-MARKUP-001 | 89 | single-letter `R`/`C` in math, initials, filenames; also fires inside `\bibitem` |
| 2 | JSS-REFS-003 | 53 | DOI-presence check misses existing fields; also advisory-vs-mandatory policy |
| 3 | JSS-CITE-002 | 29 | sub-clusters: heading/Keywords (3), `\citep[...]` optarg (12), bibitem (3), base-R (3), wrappers (5), abstract-cite-coverage (1) |
| 4 | JSS-CAP-003 | 29 | caption-style "off by 2" + misfires at `\caption{}` col 1 |
| 5 | JSS-CAP-002 | 21 | hyphenated proper names (Hardy-Weinberg, Newey-West) |
| 6 | JSS-MARKUP-002 | 19 | already-wrapped `\pkg{}` re-flagged; code-block context not skipped |
| 7 | JSS-NAME-002 | 10 | publisher-canonicalization heuristic disagrees with corpus |
| 8 | JSS-MARKUP-004 | 10 | `\dots`, `\&`, accents treated as markup |
| 9 | JSS-CODE-003 | 9 | bare-identifier code samples (no operators) |
| 10 | JSS-XREF-002 | 9 | equation-ref check fires on section/model refs |
| 11 | JSS-MARKUP-003 | 9 | rule fires inside Schunk/Code blocks |
| 12 | JSS-TYPO-004 | 7 | caption position needs table-vs-figure branching |
| 13 | JSS-OPER-002 | 7 | `T` as upper bound mistaken for transpose |

Smaller clusters (1–5 FPs each) catalogued as todos
#23–#37 — accent/markup edge cases, single-FP investigations,
Discussion-as-summary detection, e.g./i.e. regex tightening.

### Plan

The lowest-effort, highest-payoff target is **JSS-CITE-002 sub-cluster
1** (heading/Keywords) — three confirmed FPs with a clean shape. Pick
that for the first fix this iteration.

Order for follow-up cycles:

1. **CITE-002 heading/Keywords** (this iter, ~3 FPs) — done.
2. **CITE-002 `\citep[...]` optarg** (~12 FPs) — extend ancestor walk.
3. **CITE-002 bibitem + base-R + wrappers** (~11 FPs) — add masks.
4. **CAP-002 hyphenated proper names** (~6 FPs) — allowlist + hyphen-aware.
5. **MARKUP-002 already-wrapped + code blocks** (~6 FPs) — mask logic.
6. **MARKUP-001 single-letter** (~89 FPs) — biggest payoff but also
   highest risk; defer until smaller fixes have shrunk noise.

The single-FP rules (NAME-001, BIBTEX-003, OPER-001/004, PRE-003,
TYPO-001) are tracked in todo #37 as a sweep-pass once the bigger
clusters are closed.

### Results (post-implementation)

Closed by iteration 15. Headings/Keywords fix landed:

- **JSS-CITE-002** (full): tp 163 → 161 (−2), fp 29 → 27 (−2),
  precision **84.90% → 85.64% (+0.74pp)** — still FAIL.
- **JSS-CITE-002** (pinned): tp 53 → 52 (−1), fp 26 → 24 (−2),
  precision **67.09% → 68.42% (+1.33pp)** — still FAIL.
- **5 orphans** dropped: 3 confirmed FPs in headings/Keywords
  (dtwclust:1808, plot3logit:88, spacetime:1263), 2 mislabeled TPs
  in `\Keywords{}` (ggmcmc:38, lifecontingencies/mortality_projection:40)
  that were really FPs.
- **1 new violation surfaced** at ggmcmc/v70i09.Rnw:76 — `\pkg{ggmcmc}`
  in §1 body without same-paragraph `\citep`. Previously masked because
  the `\Keywords{}` mention exhausted the `seen` set; the new fix lets
  the body mention through. Labeled FP after the fact (citation lives
  in `\Abstract{}`); recorded as a new sub-cluster (todo #39:
  abstract-cite-coverage).

Most of the iter-14 plan remains open — see iter-15 Findings/Plan
for the full catalogue.


## Iteration 15 — 2026-04-28T19:49:27Z — post-JSS-CITE-002-headings-keywords

- **Corpus size:** 98 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=23, pinned=19

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 161 | 27 | 0 | 85.64% | FAIL |
| citation | JSS-CITE-003 | 8 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-BIBTEX-004 | 25 | 3 | 0 | 89.29% | FAIL |
| unknown | JSS-CAP-001 | 2 | 3 | 0 | 40.00% | FAIL |
| unknown | JSS-CAP-002 | 157 | 21 | 0 | 88.20% | FAIL |
| unknown | JSS-CAP-003 | 18 | 29 | 0 | 38.30% | FAIL |
| unknown | JSS-CAP-004 | 10 | 4 | 0 | 71.43% | FAIL |
| unknown | JSS-CODE-001 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 98 | 9 | 0 | 91.59% | PASS |
| unknown | JSS-HOUSE-001 | 263 | 4 | 0 | 98.50% | PASS |
| unknown | JSS-HOUSE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 45 | 2 | 0 | 95.74% | PASS |
| unknown | JSS-MARKUP-001 | 853 | 89 | 0 | 90.55% | PASS |
| unknown | JSS-MARKUP-002 | 250 | 19 | 0 | 92.94% | PASS |
| unknown | JSS-MARKUP-003 | 171 | 9 | 0 | 95.00% | PASS |
| unknown | JSS-MARKUP-004 | 121 | 10 | 0 | 92.37% | PASS |
| unknown | JSS-NAME-001 | 2 | 1 | 0 | 66.67% | FAIL |
| unknown | JSS-NAME-002 | 33 | 10 | 0 | 76.74% | FAIL |
| unknown | JSS-OPER-001 | 57 | 1 | 0 | 98.28% | PASS |
| unknown | JSS-OPER-002 | 37 | 7 | 0 | 84.09% | FAIL |
| unknown | JSS-OPER-003 | 12 | 2 | 0 | 85.71% | FAIL |
| unknown | JSS-OPER-004 | 21 | 1 | 0 | 95.45% | PASS |
| unknown | JSS-PRE-001 | 56 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 7 | 3 | 0 | 70.00% | FAIL |
| unknown | JSS-PRE-003 | 25 | 1 | 0 | 96.15% | PASS |
| unknown | JSS-PRE-006 | 24 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 28 | 5 | 0 | 84.85% | FAIL |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 814 | 53 | 0 | 93.89% | PASS |
| unknown | JSS-REFS-004 | 129 | 4 | 0 | 96.99% | PASS |
| unknown | JSS-REFS-005 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 124 | 5 | 0 | 96.12% | PASS |
| unknown | JSS-REFS-007 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 33 | 4 | 0 | 89.19% | FAIL |
| unknown | JSS-STRUCT-002 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 41 | 1 | 0 | 97.62% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 7 | 0 | 77.42% | FAIL |
| unknown | JSS-WIDTH-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 33 | 3 | 0 | 91.67% | PASS |
| unknown | JSS-XREF-002 | 152 | 9 | 0 | 94.41% | PASS |
| unknown | JSS-XREF-004 | 123 | 3 | 0 | 97.62% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 52 | 24 | 0 | 68.42% | FAIL |
| citation | JSS-CITE-003 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-BIBTEX-004 | 18 | 1 | 0 | 94.74% | PASS |
| unknown | JSS-CAP-001 | 0 | 1 | 0 | 0.00% | FAIL |
| unknown | JSS-CAP-002 | 52 | 10 | 0 | 83.87% | FAIL |
| unknown | JSS-CAP-003 | 13 | 15 | 0 | 46.43% | FAIL |
| unknown | JSS-CAP-004 | 9 | 3 | 0 | 75.00% | FAIL |
| unknown | JSS-CODE-001 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 51 | 5 | 0 | 91.07% | PASS |
| unknown | JSS-HOUSE-001 | 59 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 15 | 1 | 0 | 93.75% | PASS |
| unknown | JSS-MARKUP-001 | 314 | 47 | 0 | 86.98% | FAIL |
| unknown | JSS-MARKUP-002 | 116 | 4 | 0 | 96.67% | PASS |
| unknown | JSS-MARKUP-003 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-004 | 33 | 3 | 0 | 91.67% | PASS |
| unknown | JSS-NAME-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 33 | 10 | 0 | 76.74% | FAIL |
| unknown | JSS-OPER-001 | 12 | 1 | 0 | 92.31% | PASS |
| unknown | JSS-OPER-002 | 27 | 6 | 0 | 81.82% | FAIL |
| unknown | JSS-OPER-003 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 11 | 1 | 0 | 91.67% | PASS |
| unknown | JSS-PRE-001 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 2 | 0 | 66.67% | FAIL |
| unknown | JSS-PRE-003 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 10 | 2 | 0 | 83.33% | FAIL |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 814 | 53 | 0 | 93.89% | PASS |
| unknown | JSS-REFS-004 | 129 | 4 | 0 | 96.99% | PASS |
| unknown | JSS-REFS-005 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 124 | 5 | 0 | 96.12% | PASS |
| unknown | JSS-REFS-007 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 11 | 2 | 0 | 84.62% | FAIL |
| unknown | JSS-STRUCT-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 27 | 1 | 0 | 96.43% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 19 | 4 | 0 | 82.61% | FAIL |
| unknown | JSS-WIDTH-001 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 25 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 76 | 5 | 0 | 93.83% | PASS |
| unknown | JSS-XREF-004 | 86 | 3 | 0 | 96.63% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-CITE-002`: tp +163→161 (-2), fp +29→27 (-2), pending 0→0 (+0)

**Pinned only**

- `JSS-CITE-002`: tp +53→52 (-1), fp +26→24 (-2), pending 0→0 (+0)

### Findings / suggestions

A full sweep of the labelled FPs across every rule with at least
one FP. Clusters surfaced for each rule, ranked by potential
FP-elimination volume.

**JSS-CITE-002** — 27 FPs split into 6 sub-clusters (only one
addressed this iter):

| sub-cluster | fp | sketch |
|---|---:|---|
| `\citep[...]` / `\citealp[...]` optional arg | ~12 | cite is ancestor of `\pkg{}`, not sibling — extend ancestor walk |
| `\mbox{}` / `\caption{}` / list `\item{}` wrappers | ~5 | wrapper macro hides cite from sibling check |
| `\bibitem` / `thebibliography` | ~3 | bib entry IS the citation — add to no-cite zone |
| base-R packages (parallel, methods, stats) | ~3 | ship with R; allowlist |
| `\footnote{}` cite-in-footnote | ~2 | cite + pkg both in footnote arg group |
| abstract-cite-coverage (ggmcmc:76) | ~1 | abstract has both `\pkg{X}` and `\citep{}` but body mention still flagged |

**JSS-MARKUP-001** — 89 FPs, biggest single source:

- single-letter `R`/`C` ambiguity (~50): math symbol, name initial,
  `.r` filename, version-string segment
- inside `\bibitem` (subset of above; ~10 in GPareto bibliography)

**JSS-REFS-003** — 53 FPs, two policy questions:

- DOI present but rule fires anyway (~12) — bib-field detection bug
- "advisory rule, missing DOI not a violation" (~10) — severity question

**JSS-CAP-003** — 29 FPs, precision 38.3%:

- "off by 2" line-number cluster + `\caption{}` sentence-style misfires
  at column 1 (~21 empty-reason rows likely the same cluster)

**JSS-CAP-002** — 21 FPs:

- hyphenated proper names (Hardy-Weinberg, Newey-West, Klein-Spady,
  Robert Koch) — second-word capitalisation rule trips compound nouns

**JSS-MARKUP-002** — 19 FPs:

- false-fire when `\pkg{}` already wraps (~6)
- inside code blocks (~3)
- ambiguous identifiers (sandwich-as-method, ggplot2 in code) (~3)

**JSS-NAME-002** — 10 FPs:

- publisher-canonicalization heuristic disagrees with corpus
  (Springer vs Springer-Verlag remnants from reverted commit)

**JSS-MARKUP-004** — 10 FPs:

- `\dots`, `\&`, `\.`, accents treated as markup needing plain-text shim
- `\subsection`/`\subsubsection` not handled by the `\section[plain]{markup}` check

**JSS-CODE-003** — 9 FPs:

- code samples without operators or commas (bare identifiers)

**JSS-XREF-002** — 9 FPs:

- equation-ref check fires on section/model refs (`sec:summary`, `mod:cox`)

**JSS-MARKUP-003** — 9 FPs:

- rule fires inside Schunk / Code blocks / verbatim envs

**JSS-TYPO-004** — 7 FPs:

- caption-position rule enforces single direction; JSS style is
  table-captions-above + figure-captions-below

**JSS-OPER-002** — 7 FPs:

- `T` as upper bound of `\sum_{t=1}^T` etc. mistaken for transpose

**Smaller clusters** (1–5 FPs each), tracked individually:

- JSS-PARSE-000 (5, noisy parse errors), JSS-PRE-007 (5, accents in
  `\author{}`), JSS-REFS-006 (5, leading `\pkg{}:` titles), JSS-CAP-004
  (4, multi-line Keywords), JSS-STRUCT-001 (4, Discussion as summary),
  JSS-REFS-004 (4, title markup detection), JSS-HOUSE-001 (4, e.g./i.e.
  regex), JSS-CAP-001 (3, mislabeled-package), JSS-PRE-002 (3, missing
  preamble macros), JSS-BIBTEX-004 (3, fires at definition site),
  JSS-XREF-001 (3, cross-paper refs), JSS-XREF-004 (3, subequations),
  JSS-OPER-003 (2, code-chunk paragraph break), JSS-HOUSE-003 (2,
  package allowlist), and 6 single-FP rules swept together.

Catalogued in `TaskList` as todos #4-#37, #39 (#38 was the
post-fix human-review of the new ggmcmc:76 violation, completed).

### Plan

The 27 CITE-002 FPs split cleanly. After this iter's heading/Keywords
fix (3 FPs), the next CITE-002 cycle should tackle the
`\citep[...]` optarg cluster (~12 FPs, mechanical) — that alone takes
CITE-002 from 24 → ~12 FPs and likely flips it to PASS.

Recommended attack order across rules (bigger-first within similar
risk tiers):

1. **JSS-CITE-002 cite-optarg** (todo #4) — ~12 FPs, mechanical extension of the existing rule.
2. **JSS-CITE-002 bibitem + base-R + abstract-coverage** (todos #5, #6, #39) — ~7 FPs, all add-to-mask-list shape.
3. **JSS-MARKUP-002 already-wrapped + code-block context** (todo #15) — ~9 FPs, simple skip-already-wrapped check.
4. **JSS-MARKUP-003 code-block context** (todo #16) — ~5 FPs, share env-list with #15.
5. **JSS-CAP-002 hyphenated proper names** (todo #10) — ~6 FPs, allowlist or hyphen-aware capitalisation.
6. **JSS-XREF-002 equation-only restriction** (todo #18) — ~7 FPs, label-prefix filter.
7. **JSS-OPER-002 T-as-bound disambiguation** (todo #19) — ~7 FPs, math-context inspection.
8. **JSS-TYPO-004 caption-position branching** (todo #20) — 7 FPs, simple env-name branch.
9. **JSS-REFS-003 DOI presence detection** (todo #13) — ~12 FPs, bib-field parsing audit.
10. **JSS-CAP-003 line-offset bug + caption-style** (todo #9) — ~29 FPs but needs investigation; do after smaller wins.
11. **JSS-MARKUP-001 single-letter ambiguity** (todos #11, #12) — ~89 FPs, biggest payoff but highest regression risk; tackle after the smaller, cleaner rules have stabilised.

Smaller-cluster sweeps (todos #17, #22-#37) bundled into a single
"single-FP investigations" pass once the volume rules above have closed.

### Results (post-implementation)

Closed across iterations 16-35 (corpus pinned at 98 papers; FAIL
count dropped from 15 → 3, PASS count from 35 → 47).

**Rules brought to PASS:**

| rule | iter | path |
|---|---|---|
| JSS-CITE-002 | 16 | extend cite check to ancestor walk for `\citep[...]` optarg |
| JSS-CITE-002 | 17 | bibitem soft-zone + base-R allowlist + abstract-cite-coverage |
| JSS-MARKUP-003 | 18 | rmd parser: recognise indented fenced code blocks in lists |
| JSS-XREF-002 | 19 | restrict equation-ref check to non-{sec,fig,tab,mod,...} prefixes |
| JSS-CAP-002 | 20 | collapse hyphenated proper-noun runs in section titles |
| JSS-OPER-002 | 21 | distinguish `^T` transpose from `\sum_{...}^T` upper bound |
| JSS-MARKUP-004 | 24 | accents / `\label` / `\dots` aren't visible markup |
| JSS-PRE-002 | 26 | skip `\Address{}` requirement for `[nojss]` documents |
| JSS-PRE-003/007/008 | 27 | gate markup→Plain* pair on strict-jss class |
| JSS-HOUSE-003 | 28 | gate redundant-`\usepackage` on `\documentclass{jss}` |
| JSS-OPER-003 | 30 | stripped Sweave chunks aren't paragraph breaks |
| JSS-STRUCT-001 | 31 | accept Examples / Illustrations / Applications as summary |
| JSS-NAME-002 | 33 | flip 10 AI mislabels (Springer mapping is JSS canon) + skip-list |
| JSS-CAP-001 | 34 | exempt own-package title prefix |
| JSS-NAME-001, JSS-BIBTEX-003/004 | 34-35 | flip 5 AI/migrated mislabels |

**Iter-14 → iter-35 deltas (full corpus):**

- Total TP: 4090 → 3935 (−155); total FP: 352 → 248 (−104).
- Most TPs lost are mislabels of two kinds: (a) labelers applying
  rules to non-jss / `[nojss]` documents where the rule's intent
  doesn't reach (PRE-003 −24, PRE-007 −23, HOUSE-003 −31, XREF-002
  −23), and (b) AI/migrated labels with stale or hallucinated
  reasoning (NAME-002 +10/−10 net flip, MARKUP-004 −14, BIBTEX-004
  −3 flips).
- Real new violations surfaced and labelled this round: 1
  (ggmcmc:76 CITE-002 in §1 body without same-paragraph cite,
  initially flagged by the iter-15 fix and labelled FP after the
  abstract-cite-coverage rule extension).

**Rules deliberately not closed (see iter-15 Plan #15, #20, plus #9
left FAILing):**

- JSS-MARKUP-002 (#15) — own-package noun usage cluster is too
  entangled with labeler convention; first attempt at a skip-list
  dropped 191 labelled TPs across xts/zoo/sandwich vignettes.
- JSS-TYPO-004 (#20) — table caption-above-content vs figure
  caption-below-content split: corpus labelers consistently flag
  the table case as TP, contradicting both my reading of JSS style
  and a clean rule fix.
- JSS-CAP-003 (#9) — got 2 incremental fixes (numbered-list
  boundary stub, geographic/microbe proper-noun extensions) for a
  combined 47% precision; remaining 19 FPs are diverse minor
  patterns ("X and Y" two-author runs, mixed-case continuations,
  paper-specific phrasings) without a clean cluster.
- JSS-CAP-004 (#25) — tried hyphenated-compound + abbreviation
  exemption; labelers flag Q-Q / Kaplan-Meier / ANOVA as TP while
  flagging Bayesian / MCMC / GARCH as FP on the same code path,
  reverted.

**Skip-list change:** added JSS-NAME-002 to
`eval/review-skip-list.toml` so the AI classifier no longer
auto-labels publisher canonicalisation cases — the model
hallucinates JSS conventions on them.

**Memory note:** dropped (and re-added) the Springer →
Springer-Verlag canonical mapping twice over the project's history.
Saved a `feedback_jss_publisher_canonical.md` memory entry to break
the cycle: bare publisher mappings are JSS canon, not labeler noise.

Next iteration starts by growing the corpus (the 16-paper expansion
in iter-14 is overdue for a follow-up).

## Iteration 16 — 2026-04-28T20:00:39Z — post-JSS-CITE-002-cite-optarg

- **Corpus size:** 98 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=23, pinned=19

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 161 | 15 | 0 | 91.48% | PASS |
| citation | JSS-CITE-003 | 8 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-BIBTEX-004 | 25 | 3 | 0 | 89.29% | FAIL |
| unknown | JSS-CAP-001 | 2 | 3 | 0 | 40.00% | FAIL |
| unknown | JSS-CAP-002 | 157 | 21 | 0 | 88.20% | FAIL |
| unknown | JSS-CAP-003 | 18 | 29 | 0 | 38.30% | FAIL |
| unknown | JSS-CAP-004 | 10 | 4 | 0 | 71.43% | FAIL |
| unknown | JSS-CODE-001 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 98 | 9 | 0 | 91.59% | PASS |
| unknown | JSS-HOUSE-001 | 263 | 4 | 0 | 98.50% | PASS |
| unknown | JSS-HOUSE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 45 | 2 | 0 | 95.74% | PASS |
| unknown | JSS-MARKUP-001 | 853 | 89 | 0 | 90.55% | PASS |
| unknown | JSS-MARKUP-002 | 250 | 19 | 0 | 92.94% | PASS |
| unknown | JSS-MARKUP-003 | 171 | 9 | 0 | 95.00% | PASS |
| unknown | JSS-MARKUP-004 | 121 | 10 | 0 | 92.37% | PASS |
| unknown | JSS-NAME-001 | 2 | 1 | 0 | 66.67% | FAIL |
| unknown | JSS-NAME-002 | 33 | 10 | 0 | 76.74% | FAIL |
| unknown | JSS-OPER-001 | 57 | 1 | 0 | 98.28% | PASS |
| unknown | JSS-OPER-002 | 37 | 7 | 0 | 84.09% | FAIL |
| unknown | JSS-OPER-003 | 12 | 2 | 0 | 85.71% | FAIL |
| unknown | JSS-OPER-004 | 21 | 1 | 0 | 95.45% | PASS |
| unknown | JSS-PRE-001 | 56 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 7 | 3 | 0 | 70.00% | FAIL |
| unknown | JSS-PRE-003 | 25 | 1 | 0 | 96.15% | PASS |
| unknown | JSS-PRE-006 | 24 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 28 | 5 | 0 | 84.85% | FAIL |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 814 | 53 | 0 | 93.89% | PASS |
| unknown | JSS-REFS-004 | 129 | 4 | 0 | 96.99% | PASS |
| unknown | JSS-REFS-005 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 124 | 5 | 0 | 96.12% | PASS |
| unknown | JSS-REFS-007 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 33 | 4 | 0 | 89.19% | FAIL |
| unknown | JSS-STRUCT-002 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 41 | 1 | 0 | 97.62% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 7 | 0 | 77.42% | FAIL |
| unknown | JSS-WIDTH-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 33 | 3 | 0 | 91.67% | PASS |
| unknown | JSS-XREF-002 | 152 | 9 | 0 | 94.41% | PASS |
| unknown | JSS-XREF-004 | 123 | 3 | 0 | 97.62% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 52 | 14 | 0 | 78.79% | FAIL |
| citation | JSS-CITE-003 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-BIBTEX-004 | 18 | 1 | 0 | 94.74% | PASS |
| unknown | JSS-CAP-001 | 0 | 1 | 0 | 0.00% | FAIL |
| unknown | JSS-CAP-002 | 52 | 10 | 0 | 83.87% | FAIL |
| unknown | JSS-CAP-003 | 13 | 15 | 0 | 46.43% | FAIL |
| unknown | JSS-CAP-004 | 9 | 3 | 0 | 75.00% | FAIL |
| unknown | JSS-CODE-001 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 51 | 5 | 0 | 91.07% | PASS |
| unknown | JSS-HOUSE-001 | 59 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 15 | 1 | 0 | 93.75% | PASS |
| unknown | JSS-MARKUP-001 | 314 | 47 | 0 | 86.98% | FAIL |
| unknown | JSS-MARKUP-002 | 116 | 4 | 0 | 96.67% | PASS |
| unknown | JSS-MARKUP-003 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-004 | 33 | 3 | 0 | 91.67% | PASS |
| unknown | JSS-NAME-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 33 | 10 | 0 | 76.74% | FAIL |
| unknown | JSS-OPER-001 | 12 | 1 | 0 | 92.31% | PASS |
| unknown | JSS-OPER-002 | 27 | 6 | 0 | 81.82% | FAIL |
| unknown | JSS-OPER-003 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 11 | 1 | 0 | 91.67% | PASS |
| unknown | JSS-PRE-001 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 2 | 0 | 66.67% | FAIL |
| unknown | JSS-PRE-003 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 10 | 2 | 0 | 83.33% | FAIL |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 814 | 53 | 0 | 93.89% | PASS |
| unknown | JSS-REFS-004 | 129 | 4 | 0 | 96.99% | PASS |
| unknown | JSS-REFS-005 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 124 | 5 | 0 | 96.12% | PASS |
| unknown | JSS-REFS-007 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 11 | 2 | 0 | 84.62% | FAIL |
| unknown | JSS-STRUCT-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 27 | 1 | 0 | 96.43% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 19 | 4 | 0 | 82.61% | FAIL |
| unknown | JSS-WIDTH-001 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 25 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 76 | 5 | 0 | 93.83% | PASS |
| unknown | JSS-XREF-004 | 86 | 3 | 0 | 96.63% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-CITE-002`: tp +161→161 (+0), fp +27→15 (-12), pending 0→0 (+0)

**Pinned only**

- `JSS-CITE-002`: tp +52→52 (+0), fp +24→14 (-10), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 17 — 2026-04-28T20:08:46Z — post-CITE-002-bibitem-baseR-abstract

- **Corpus size:** 98 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=23, pinned=19

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 139 | 7 | 0 | 95.21% | PASS |
| citation | JSS-CITE-003 | 8 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-BIBTEX-004 | 25 | 3 | 0 | 89.29% | FAIL |
| unknown | JSS-CAP-001 | 2 | 3 | 0 | 40.00% | FAIL |
| unknown | JSS-CAP-002 | 157 | 21 | 0 | 88.20% | FAIL |
| unknown | JSS-CAP-003 | 18 | 29 | 0 | 38.30% | FAIL |
| unknown | JSS-CAP-004 | 10 | 4 | 0 | 71.43% | FAIL |
| unknown | JSS-CODE-001 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 98 | 9 | 0 | 91.59% | PASS |
| unknown | JSS-HOUSE-001 | 263 | 4 | 0 | 98.50% | PASS |
| unknown | JSS-HOUSE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 45 | 2 | 0 | 95.74% | PASS |
| unknown | JSS-MARKUP-001 | 853 | 89 | 0 | 90.55% | PASS |
| unknown | JSS-MARKUP-002 | 250 | 19 | 0 | 92.94% | PASS |
| unknown | JSS-MARKUP-003 | 171 | 9 | 0 | 95.00% | PASS |
| unknown | JSS-MARKUP-004 | 121 | 10 | 0 | 92.37% | PASS |
| unknown | JSS-NAME-001 | 2 | 1 | 0 | 66.67% | FAIL |
| unknown | JSS-NAME-002 | 33 | 10 | 0 | 76.74% | FAIL |
| unknown | JSS-OPER-001 | 57 | 1 | 0 | 98.28% | PASS |
| unknown | JSS-OPER-002 | 37 | 7 | 0 | 84.09% | FAIL |
| unknown | JSS-OPER-003 | 12 | 2 | 0 | 85.71% | FAIL |
| unknown | JSS-OPER-004 | 21 | 1 | 0 | 95.45% | PASS |
| unknown | JSS-PRE-001 | 56 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 7 | 3 | 0 | 70.00% | FAIL |
| unknown | JSS-PRE-003 | 25 | 1 | 0 | 96.15% | PASS |
| unknown | JSS-PRE-006 | 24 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 28 | 5 | 0 | 84.85% | FAIL |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 814 | 53 | 0 | 93.89% | PASS |
| unknown | JSS-REFS-004 | 129 | 4 | 0 | 96.99% | PASS |
| unknown | JSS-REFS-005 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 124 | 5 | 0 | 96.12% | PASS |
| unknown | JSS-REFS-007 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 33 | 4 | 0 | 89.19% | FAIL |
| unknown | JSS-STRUCT-002 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 41 | 1 | 0 | 97.62% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 7 | 0 | 77.42% | FAIL |
| unknown | JSS-WIDTH-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 33 | 3 | 0 | 91.67% | PASS |
| unknown | JSS-XREF-002 | 152 | 9 | 0 | 94.41% | PASS |
| unknown | JSS-XREF-004 | 123 | 3 | 0 | 97.62% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 39 | 6 | 0 | 86.67% | FAIL |
| citation | JSS-CITE-003 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-BIBTEX-004 | 18 | 1 | 0 | 94.74% | PASS |
| unknown | JSS-CAP-001 | 0 | 1 | 0 | 0.00% | FAIL |
| unknown | JSS-CAP-002 | 52 | 10 | 0 | 83.87% | FAIL |
| unknown | JSS-CAP-003 | 13 | 15 | 0 | 46.43% | FAIL |
| unknown | JSS-CAP-004 | 9 | 3 | 0 | 75.00% | FAIL |
| unknown | JSS-CODE-001 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 51 | 5 | 0 | 91.07% | PASS |
| unknown | JSS-HOUSE-001 | 59 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 15 | 1 | 0 | 93.75% | PASS |
| unknown | JSS-MARKUP-001 | 314 | 47 | 0 | 86.98% | FAIL |
| unknown | JSS-MARKUP-002 | 116 | 4 | 0 | 96.67% | PASS |
| unknown | JSS-MARKUP-003 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-004 | 33 | 3 | 0 | 91.67% | PASS |
| unknown | JSS-NAME-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 33 | 10 | 0 | 76.74% | FAIL |
| unknown | JSS-OPER-001 | 12 | 1 | 0 | 92.31% | PASS |
| unknown | JSS-OPER-002 | 27 | 6 | 0 | 81.82% | FAIL |
| unknown | JSS-OPER-003 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 11 | 1 | 0 | 91.67% | PASS |
| unknown | JSS-PRE-001 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 2 | 0 | 66.67% | FAIL |
| unknown | JSS-PRE-003 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 10 | 2 | 0 | 83.33% | FAIL |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 814 | 53 | 0 | 93.89% | PASS |
| unknown | JSS-REFS-004 | 129 | 4 | 0 | 96.99% | PASS |
| unknown | JSS-REFS-005 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 124 | 5 | 0 | 96.12% | PASS |
| unknown | JSS-REFS-007 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 11 | 2 | 0 | 84.62% | FAIL |
| unknown | JSS-STRUCT-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 27 | 1 | 0 | 96.43% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 19 | 4 | 0 | 82.61% | FAIL |
| unknown | JSS-WIDTH-001 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 25 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 76 | 5 | 0 | 93.83% | PASS |
| unknown | JSS-XREF-004 | 86 | 3 | 0 | 96.63% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-CITE-002`: tp +161→139 (-22), fp +15→7 (-8), pending 0→0 (+0)

**Pinned only**

- `JSS-CITE-002`: tp +52→39 (-13), fp +14→6 (-8), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 18 — 2026-04-28T20:14:53Z — post-rmd-indented-fence

- **Corpus size:** 98 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=23, pinned=19

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 139 | 7 | 0 | 95.21% | PASS |
| citation | JSS-CITE-003 | 8 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-BIBTEX-004 | 25 | 3 | 0 | 89.29% | FAIL |
| unknown | JSS-CAP-001 | 2 | 3 | 0 | 40.00% | FAIL |
| unknown | JSS-CAP-002 | 157 | 21 | 0 | 88.20% | FAIL |
| unknown | JSS-CAP-003 | 18 | 29 | 0 | 38.30% | FAIL |
| unknown | JSS-CAP-004 | 10 | 4 | 0 | 71.43% | FAIL |
| unknown | JSS-CODE-001 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 98 | 9 | 0 | 91.59% | PASS |
| unknown | JSS-HOUSE-001 | 263 | 4 | 0 | 98.50% | PASS |
| unknown | JSS-HOUSE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 45 | 2 | 0 | 95.74% | PASS |
| unknown | JSS-MARKUP-001 | 853 | 88 | 0 | 90.65% | PASS |
| unknown | JSS-MARKUP-002 | 249 | 19 | 0 | 92.91% | PASS |
| unknown | JSS-MARKUP-003 | 167 | 3 | 0 | 98.24% | PASS |
| unknown | JSS-MARKUP-004 | 121 | 10 | 0 | 92.37% | PASS |
| unknown | JSS-NAME-001 | 2 | 1 | 0 | 66.67% | FAIL |
| unknown | JSS-NAME-002 | 33 | 10 | 0 | 76.74% | FAIL |
| unknown | JSS-OPER-001 | 57 | 1 | 0 | 98.28% | PASS |
| unknown | JSS-OPER-002 | 37 | 7 | 0 | 84.09% | FAIL |
| unknown | JSS-OPER-003 | 12 | 2 | 0 | 85.71% | FAIL |
| unknown | JSS-OPER-004 | 21 | 1 | 0 | 95.45% | PASS |
| unknown | JSS-PRE-001 | 56 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 7 | 3 | 0 | 70.00% | FAIL |
| unknown | JSS-PRE-003 | 25 | 1 | 0 | 96.15% | PASS |
| unknown | JSS-PRE-006 | 24 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 28 | 5 | 0 | 84.85% | FAIL |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 814 | 53 | 0 | 93.89% | PASS |
| unknown | JSS-REFS-004 | 129 | 4 | 0 | 96.99% | PASS |
| unknown | JSS-REFS-005 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 124 | 5 | 0 | 96.12% | PASS |
| unknown | JSS-REFS-007 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 33 | 4 | 0 | 89.19% | FAIL |
| unknown | JSS-STRUCT-002 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 41 | 1 | 0 | 97.62% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 7 | 0 | 77.42% | FAIL |
| unknown | JSS-WIDTH-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 33 | 3 | 0 | 91.67% | PASS |
| unknown | JSS-XREF-002 | 152 | 9 | 0 | 94.41% | PASS |
| unknown | JSS-XREF-004 | 123 | 3 | 0 | 97.62% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 39 | 6 | 0 | 86.67% | FAIL |
| citation | JSS-CITE-003 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-BIBTEX-004 | 18 | 1 | 0 | 94.74% | PASS |
| unknown | JSS-CAP-001 | 0 | 1 | 0 | 0.00% | FAIL |
| unknown | JSS-CAP-002 | 52 | 10 | 0 | 83.87% | FAIL |
| unknown | JSS-CAP-003 | 13 | 15 | 0 | 46.43% | FAIL |
| unknown | JSS-CAP-004 | 9 | 3 | 0 | 75.00% | FAIL |
| unknown | JSS-CODE-001 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 51 | 5 | 0 | 91.07% | PASS |
| unknown | JSS-HOUSE-001 | 59 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 15 | 1 | 0 | 93.75% | PASS |
| unknown | JSS-MARKUP-001 | 314 | 47 | 0 | 86.98% | FAIL |
| unknown | JSS-MARKUP-002 | 115 | 4 | 0 | 96.64% | PASS |
| unknown | JSS-MARKUP-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-004 | 33 | 3 | 0 | 91.67% | PASS |
| unknown | JSS-NAME-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 33 | 10 | 0 | 76.74% | FAIL |
| unknown | JSS-OPER-001 | 12 | 1 | 0 | 92.31% | PASS |
| unknown | JSS-OPER-002 | 27 | 6 | 0 | 81.82% | FAIL |
| unknown | JSS-OPER-003 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 11 | 1 | 0 | 91.67% | PASS |
| unknown | JSS-PRE-001 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 2 | 0 | 66.67% | FAIL |
| unknown | JSS-PRE-003 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 10 | 2 | 0 | 83.33% | FAIL |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 814 | 53 | 0 | 93.89% | PASS |
| unknown | JSS-REFS-004 | 129 | 4 | 0 | 96.99% | PASS |
| unknown | JSS-REFS-005 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 124 | 5 | 0 | 96.12% | PASS |
| unknown | JSS-REFS-007 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 11 | 2 | 0 | 84.62% | FAIL |
| unknown | JSS-STRUCT-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 27 | 1 | 0 | 96.43% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 19 | 4 | 0 | 82.61% | FAIL |
| unknown | JSS-WIDTH-001 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 25 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 76 | 5 | 0 | 93.83% | PASS |
| unknown | JSS-XREF-004 | 86 | 3 | 0 | 96.63% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-MARKUP-001`: tp +853→853 (+0), fp +89→88 (-1), pending 0→0 (+0)
- `JSS-MARKUP-002`: tp +250→249 (-1), fp +19→19 (+0), pending 0→0 (+0)
- `JSS-MARKUP-003`: tp +171→167 (-4), fp +9→3 (-6), pending 0→0 (+0)

**Pinned only**

- `JSS-MARKUP-002`: tp +116→115 (-1), fp +4→4 (+0), pending 0→0 (+0)
- `JSS-MARKUP-003`: tp +15→13 (-2), fp +0→0 (+0), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 19 — 2026-04-28T20:33:00Z — post-XREF-002-eq-prefix-only

- **Corpus size:** 98 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=23, pinned=19

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 139 | 7 | 0 | 95.21% | PASS |
| citation | JSS-CITE-003 | 8 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-BIBTEX-004 | 25 | 3 | 0 | 89.29% | FAIL |
| unknown | JSS-CAP-001 | 2 | 3 | 0 | 40.00% | FAIL |
| unknown | JSS-CAP-002 | 157 | 21 | 0 | 88.20% | FAIL |
| unknown | JSS-CAP-003 | 18 | 29 | 0 | 38.30% | FAIL |
| unknown | JSS-CAP-004 | 10 | 4 | 0 | 71.43% | FAIL |
| unknown | JSS-CODE-001 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 98 | 9 | 0 | 91.59% | PASS |
| unknown | JSS-HOUSE-001 | 263 | 4 | 0 | 98.50% | PASS |
| unknown | JSS-HOUSE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 45 | 2 | 0 | 95.74% | PASS |
| unknown | JSS-MARKUP-001 | 853 | 88 | 0 | 90.65% | PASS |
| unknown | JSS-MARKUP-002 | 249 | 19 | 0 | 92.91% | PASS |
| unknown | JSS-MARKUP-003 | 167 | 3 | 0 | 98.24% | PASS |
| unknown | JSS-MARKUP-004 | 121 | 10 | 0 | 92.37% | PASS |
| unknown | JSS-NAME-001 | 2 | 1 | 0 | 66.67% | FAIL |
| unknown | JSS-NAME-002 | 33 | 10 | 0 | 76.74% | FAIL |
| unknown | JSS-OPER-001 | 57 | 1 | 0 | 98.28% | PASS |
| unknown | JSS-OPER-002 | 37 | 7 | 0 | 84.09% | FAIL |
| unknown | JSS-OPER-003 | 12 | 2 | 0 | 85.71% | FAIL |
| unknown | JSS-OPER-004 | 21 | 1 | 0 | 95.45% | PASS |
| unknown | JSS-PRE-001 | 56 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 7 | 3 | 0 | 70.00% | FAIL |
| unknown | JSS-PRE-003 | 25 | 1 | 0 | 96.15% | PASS |
| unknown | JSS-PRE-006 | 24 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 28 | 5 | 0 | 84.85% | FAIL |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 814 | 53 | 0 | 93.89% | PASS |
| unknown | JSS-REFS-004 | 129 | 4 | 0 | 96.99% | PASS |
| unknown | JSS-REFS-005 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 124 | 5 | 0 | 96.12% | PASS |
| unknown | JSS-REFS-007 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 33 | 4 | 0 | 89.19% | FAIL |
| unknown | JSS-STRUCT-002 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 41 | 1 | 0 | 97.62% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 7 | 0 | 77.42% | FAIL |
| unknown | JSS-WIDTH-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 33 | 3 | 0 | 91.67% | PASS |
| unknown | JSS-XREF-002 | 129 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 123 | 3 | 0 | 97.62% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 39 | 6 | 0 | 86.67% | FAIL |
| citation | JSS-CITE-003 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-BIBTEX-004 | 18 | 1 | 0 | 94.74% | PASS |
| unknown | JSS-CAP-001 | 0 | 1 | 0 | 0.00% | FAIL |
| unknown | JSS-CAP-002 | 52 | 10 | 0 | 83.87% | FAIL |
| unknown | JSS-CAP-003 | 13 | 15 | 0 | 46.43% | FAIL |
| unknown | JSS-CAP-004 | 9 | 3 | 0 | 75.00% | FAIL |
| unknown | JSS-CODE-001 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 51 | 5 | 0 | 91.07% | PASS |
| unknown | JSS-HOUSE-001 | 59 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 15 | 1 | 0 | 93.75% | PASS |
| unknown | JSS-MARKUP-001 | 314 | 47 | 0 | 86.98% | FAIL |
| unknown | JSS-MARKUP-002 | 115 | 4 | 0 | 96.64% | PASS |
| unknown | JSS-MARKUP-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-004 | 33 | 3 | 0 | 91.67% | PASS |
| unknown | JSS-NAME-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 33 | 10 | 0 | 76.74% | FAIL |
| unknown | JSS-OPER-001 | 12 | 1 | 0 | 92.31% | PASS |
| unknown | JSS-OPER-002 | 27 | 6 | 0 | 81.82% | FAIL |
| unknown | JSS-OPER-003 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 11 | 1 | 0 | 91.67% | PASS |
| unknown | JSS-PRE-001 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 2 | 0 | 66.67% | FAIL |
| unknown | JSS-PRE-003 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 10 | 2 | 0 | 83.33% | FAIL |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 814 | 53 | 0 | 93.89% | PASS |
| unknown | JSS-REFS-004 | 129 | 4 | 0 | 96.99% | PASS |
| unknown | JSS-REFS-005 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 124 | 5 | 0 | 96.12% | PASS |
| unknown | JSS-REFS-007 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 11 | 2 | 0 | 84.62% | FAIL |
| unknown | JSS-STRUCT-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 27 | 1 | 0 | 96.43% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 19 | 4 | 0 | 82.61% | FAIL |
| unknown | JSS-WIDTH-001 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 25 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 59 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 86 | 3 | 0 | 96.63% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-XREF-002`: tp +152→129 (-23), fp +9→0 (-9), pending 0→0 (+0)

**Pinned only**

- `JSS-XREF-002`: tp +76→59 (-17), fp +5→0 (-5), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 20 — 2026-04-28T20:35:58Z — post-CAP-002-hyphenated-proper-names

- **Corpus size:** 98 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=23, pinned=19

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 139 | 7 | 0 | 95.21% | PASS |
| citation | JSS-CITE-003 | 8 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-BIBTEX-004 | 25 | 3 | 0 | 89.29% | FAIL |
| unknown | JSS-CAP-001 | 2 | 3 | 0 | 40.00% | FAIL |
| unknown | JSS-CAP-002 | 157 | 15 | 0 | 91.28% | PASS |
| unknown | JSS-CAP-003 | 18 | 29 | 0 | 38.30% | FAIL |
| unknown | JSS-CAP-004 | 10 | 4 | 0 | 71.43% | FAIL |
| unknown | JSS-CODE-001 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 98 | 9 | 0 | 91.59% | PASS |
| unknown | JSS-HOUSE-001 | 263 | 4 | 0 | 98.50% | PASS |
| unknown | JSS-HOUSE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 45 | 2 | 0 | 95.74% | PASS |
| unknown | JSS-MARKUP-001 | 853 | 88 | 0 | 90.65% | PASS |
| unknown | JSS-MARKUP-002 | 249 | 19 | 0 | 92.91% | PASS |
| unknown | JSS-MARKUP-003 | 167 | 3 | 0 | 98.24% | PASS |
| unknown | JSS-MARKUP-004 | 121 | 10 | 0 | 92.37% | PASS |
| unknown | JSS-NAME-001 | 2 | 1 | 0 | 66.67% | FAIL |
| unknown | JSS-NAME-002 | 33 | 10 | 0 | 76.74% | FAIL |
| unknown | JSS-OPER-001 | 57 | 1 | 0 | 98.28% | PASS |
| unknown | JSS-OPER-002 | 37 | 7 | 0 | 84.09% | FAIL |
| unknown | JSS-OPER-003 | 12 | 2 | 0 | 85.71% | FAIL |
| unknown | JSS-OPER-004 | 21 | 1 | 0 | 95.45% | PASS |
| unknown | JSS-PRE-001 | 56 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 7 | 3 | 0 | 70.00% | FAIL |
| unknown | JSS-PRE-003 | 25 | 1 | 0 | 96.15% | PASS |
| unknown | JSS-PRE-006 | 24 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 28 | 5 | 0 | 84.85% | FAIL |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 814 | 53 | 0 | 93.89% | PASS |
| unknown | JSS-REFS-004 | 129 | 4 | 0 | 96.99% | PASS |
| unknown | JSS-REFS-005 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 124 | 5 | 0 | 96.12% | PASS |
| unknown | JSS-REFS-007 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 33 | 4 | 0 | 89.19% | FAIL |
| unknown | JSS-STRUCT-002 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 41 | 1 | 0 | 97.62% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 7 | 0 | 77.42% | FAIL |
| unknown | JSS-WIDTH-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 33 | 3 | 0 | 91.67% | PASS |
| unknown | JSS-XREF-002 | 129 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 123 | 3 | 0 | 97.62% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 39 | 6 | 0 | 86.67% | FAIL |
| citation | JSS-CITE-003 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-BIBTEX-004 | 18 | 1 | 0 | 94.74% | PASS |
| unknown | JSS-CAP-001 | 0 | 1 | 0 | 0.00% | FAIL |
| unknown | JSS-CAP-002 | 52 | 4 | 0 | 92.86% | PASS |
| unknown | JSS-CAP-003 | 13 | 15 | 0 | 46.43% | FAIL |
| unknown | JSS-CAP-004 | 9 | 3 | 0 | 75.00% | FAIL |
| unknown | JSS-CODE-001 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 51 | 5 | 0 | 91.07% | PASS |
| unknown | JSS-HOUSE-001 | 59 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 15 | 1 | 0 | 93.75% | PASS |
| unknown | JSS-MARKUP-001 | 314 | 47 | 0 | 86.98% | FAIL |
| unknown | JSS-MARKUP-002 | 115 | 4 | 0 | 96.64% | PASS |
| unknown | JSS-MARKUP-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-004 | 33 | 3 | 0 | 91.67% | PASS |
| unknown | JSS-NAME-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 33 | 10 | 0 | 76.74% | FAIL |
| unknown | JSS-OPER-001 | 12 | 1 | 0 | 92.31% | PASS |
| unknown | JSS-OPER-002 | 27 | 6 | 0 | 81.82% | FAIL |
| unknown | JSS-OPER-003 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 11 | 1 | 0 | 91.67% | PASS |
| unknown | JSS-PRE-001 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 2 | 0 | 66.67% | FAIL |
| unknown | JSS-PRE-003 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 10 | 2 | 0 | 83.33% | FAIL |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 814 | 53 | 0 | 93.89% | PASS |
| unknown | JSS-REFS-004 | 129 | 4 | 0 | 96.99% | PASS |
| unknown | JSS-REFS-005 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 124 | 5 | 0 | 96.12% | PASS |
| unknown | JSS-REFS-007 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 11 | 2 | 0 | 84.62% | FAIL |
| unknown | JSS-STRUCT-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 27 | 1 | 0 | 96.43% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 19 | 4 | 0 | 82.61% | FAIL |
| unknown | JSS-WIDTH-001 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 25 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 59 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 86 | 3 | 0 | 96.63% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-CAP-002`: tp +157→157 (+0), fp +21→15 (-6), pending 0→0 (+0)

**Pinned only**

- `JSS-CAP-002`: tp +52→52 (+0), fp +10→4 (-6), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 21 — 2026-04-28T20:45:39Z — post-OPER-002-bound-vs-transpose

- **Corpus size:** 98 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=23, pinned=19

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 139 | 7 | 0 | 95.21% | PASS |
| citation | JSS-CITE-003 | 8 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-BIBTEX-004 | 25 | 3 | 0 | 89.29% | FAIL |
| unknown | JSS-CAP-001 | 2 | 3 | 0 | 40.00% | FAIL |
| unknown | JSS-CAP-002 | 157 | 15 | 0 | 91.28% | PASS |
| unknown | JSS-CAP-003 | 18 | 29 | 0 | 38.30% | FAIL |
| unknown | JSS-CAP-004 | 10 | 4 | 0 | 71.43% | FAIL |
| unknown | JSS-CODE-001 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 98 | 9 | 0 | 91.59% | PASS |
| unknown | JSS-HOUSE-001 | 263 | 4 | 0 | 98.50% | PASS |
| unknown | JSS-HOUSE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 45 | 2 | 0 | 95.74% | PASS |
| unknown | JSS-MARKUP-001 | 853 | 88 | 0 | 90.65% | PASS |
| unknown | JSS-MARKUP-002 | 249 | 19 | 0 | 92.91% | PASS |
| unknown | JSS-MARKUP-003 | 167 | 3 | 0 | 98.24% | PASS |
| unknown | JSS-MARKUP-004 | 121 | 10 | 0 | 92.37% | PASS |
| unknown | JSS-NAME-001 | 2 | 1 | 0 | 66.67% | FAIL |
| unknown | JSS-NAME-002 | 33 | 10 | 0 | 76.74% | FAIL |
| unknown | JSS-OPER-001 | 57 | 1 | 0 | 98.28% | PASS |
| unknown | JSS-OPER-002 | 28 | 0 | 7 | 100.00% | PASS |
| unknown | JSS-OPER-003 | 12 | 2 | 0 | 85.71% | FAIL |
| unknown | JSS-OPER-004 | 21 | 1 | 0 | 95.45% | PASS |
| unknown | JSS-PRE-001 | 56 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 7 | 3 | 0 | 70.00% | FAIL |
| unknown | JSS-PRE-003 | 25 | 1 | 0 | 96.15% | PASS |
| unknown | JSS-PRE-006 | 24 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 28 | 5 | 0 | 84.85% | FAIL |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 814 | 53 | 0 | 93.89% | PASS |
| unknown | JSS-REFS-004 | 129 | 4 | 0 | 96.99% | PASS |
| unknown | JSS-REFS-005 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 124 | 5 | 0 | 96.12% | PASS |
| unknown | JSS-REFS-007 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 33 | 4 | 0 | 89.19% | FAIL |
| unknown | JSS-STRUCT-002 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 41 | 1 | 0 | 97.62% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 7 | 0 | 77.42% | FAIL |
| unknown | JSS-WIDTH-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 33 | 3 | 0 | 91.67% | PASS |
| unknown | JSS-XREF-002 | 129 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 123 | 3 | 0 | 97.62% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 39 | 6 | 0 | 86.67% | FAIL |
| citation | JSS-CITE-003 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-BIBTEX-004 | 18 | 1 | 0 | 94.74% | PASS |
| unknown | JSS-CAP-001 | 0 | 1 | 0 | 0.00% | FAIL |
| unknown | JSS-CAP-002 | 52 | 4 | 0 | 92.86% | PASS |
| unknown | JSS-CAP-003 | 13 | 15 | 0 | 46.43% | FAIL |
| unknown | JSS-CAP-004 | 9 | 3 | 0 | 75.00% | FAIL |
| unknown | JSS-CODE-001 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 51 | 5 | 0 | 91.07% | PASS |
| unknown | JSS-HOUSE-001 | 59 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 15 | 1 | 0 | 93.75% | PASS |
| unknown | JSS-MARKUP-001 | 314 | 47 | 0 | 86.98% | FAIL |
| unknown | JSS-MARKUP-002 | 115 | 4 | 0 | 96.64% | PASS |
| unknown | JSS-MARKUP-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-004 | 33 | 3 | 0 | 91.67% | PASS |
| unknown | JSS-NAME-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 33 | 10 | 0 | 76.74% | FAIL |
| unknown | JSS-OPER-001 | 12 | 1 | 0 | 92.31% | PASS |
| unknown | JSS-OPER-002 | 19 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-OPER-003 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 11 | 1 | 0 | 91.67% | PASS |
| unknown | JSS-PRE-001 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 2 | 0 | 66.67% | FAIL |
| unknown | JSS-PRE-003 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 10 | 2 | 0 | 83.33% | FAIL |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 814 | 53 | 0 | 93.89% | PASS |
| unknown | JSS-REFS-004 | 129 | 4 | 0 | 96.99% | PASS |
| unknown | JSS-REFS-005 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 124 | 5 | 0 | 96.12% | PASS |
| unknown | JSS-REFS-007 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 11 | 2 | 0 | 84.62% | FAIL |
| unknown | JSS-STRUCT-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 27 | 1 | 0 | 96.43% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 19 | 4 | 0 | 82.61% | FAIL |
| unknown | JSS-WIDTH-001 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 25 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 59 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 86 | 3 | 0 | 96.63% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-OPER-002`: tp +37→28 (-9), fp +7→0 (-7), pending 0→7 (+7)

**Pinned only**

- `JSS-OPER-002`: tp +27→19 (-8), fp +6→0 (-6), pending 0→1 (+1)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 22 — 2026-04-28T20:50:32Z — post-CAP-003-numbered-list-boundary

- **Corpus size:** 98 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=23, pinned=19

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 139 | 7 | 0 | 95.21% | PASS |
| citation | JSS-CITE-003 | 8 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-BIBTEX-004 | 25 | 3 | 0 | 89.29% | FAIL |
| unknown | JSS-CAP-001 | 2 | 3 | 0 | 40.00% | FAIL |
| unknown | JSS-CAP-002 | 157 | 15 | 0 | 91.28% | PASS |
| unknown | JSS-CAP-003 | 18 | 25 | 0 | 41.86% | FAIL |
| unknown | JSS-CAP-004 | 10 | 4 | 0 | 71.43% | FAIL |
| unknown | JSS-CODE-001 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 98 | 9 | 0 | 91.59% | PASS |
| unknown | JSS-HOUSE-001 | 263 | 4 | 0 | 98.50% | PASS |
| unknown | JSS-HOUSE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 45 | 2 | 0 | 95.74% | PASS |
| unknown | JSS-MARKUP-001 | 853 | 88 | 0 | 90.65% | PASS |
| unknown | JSS-MARKUP-002 | 249 | 19 | 0 | 92.91% | PASS |
| unknown | JSS-MARKUP-003 | 167 | 3 | 0 | 98.24% | PASS |
| unknown | JSS-MARKUP-004 | 121 | 10 | 0 | 92.37% | PASS |
| unknown | JSS-NAME-001 | 2 | 1 | 0 | 66.67% | FAIL |
| unknown | JSS-NAME-002 | 33 | 10 | 0 | 76.74% | FAIL |
| unknown | JSS-OPER-001 | 57 | 1 | 0 | 98.28% | PASS |
| unknown | JSS-OPER-002 | 28 | 0 | 7 | 100.00% | PASS |
| unknown | JSS-OPER-003 | 12 | 2 | 0 | 85.71% | FAIL |
| unknown | JSS-OPER-004 | 21 | 1 | 0 | 95.45% | PASS |
| unknown | JSS-PRE-001 | 56 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 7 | 3 | 0 | 70.00% | FAIL |
| unknown | JSS-PRE-003 | 25 | 1 | 0 | 96.15% | PASS |
| unknown | JSS-PRE-006 | 24 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 28 | 5 | 0 | 84.85% | FAIL |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 814 | 53 | 0 | 93.89% | PASS |
| unknown | JSS-REFS-004 | 129 | 4 | 0 | 96.99% | PASS |
| unknown | JSS-REFS-005 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 124 | 5 | 0 | 96.12% | PASS |
| unknown | JSS-REFS-007 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 33 | 4 | 0 | 89.19% | FAIL |
| unknown | JSS-STRUCT-002 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 41 | 1 | 0 | 97.62% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 7 | 0 | 77.42% | FAIL |
| unknown | JSS-WIDTH-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 33 | 3 | 0 | 91.67% | PASS |
| unknown | JSS-XREF-002 | 129 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 123 | 3 | 0 | 97.62% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 39 | 6 | 0 | 86.67% | FAIL |
| citation | JSS-CITE-003 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-BIBTEX-004 | 18 | 1 | 0 | 94.74% | PASS |
| unknown | JSS-CAP-001 | 0 | 1 | 0 | 0.00% | FAIL |
| unknown | JSS-CAP-002 | 52 | 4 | 0 | 92.86% | PASS |
| unknown | JSS-CAP-003 | 13 | 15 | 0 | 46.43% | FAIL |
| unknown | JSS-CAP-004 | 9 | 3 | 0 | 75.00% | FAIL |
| unknown | JSS-CODE-001 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 51 | 5 | 0 | 91.07% | PASS |
| unknown | JSS-HOUSE-001 | 59 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 15 | 1 | 0 | 93.75% | PASS |
| unknown | JSS-MARKUP-001 | 314 | 47 | 0 | 86.98% | FAIL |
| unknown | JSS-MARKUP-002 | 115 | 4 | 0 | 96.64% | PASS |
| unknown | JSS-MARKUP-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-004 | 33 | 3 | 0 | 91.67% | PASS |
| unknown | JSS-NAME-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 33 | 10 | 0 | 76.74% | FAIL |
| unknown | JSS-OPER-001 | 12 | 1 | 0 | 92.31% | PASS |
| unknown | JSS-OPER-002 | 19 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-OPER-003 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 11 | 1 | 0 | 91.67% | PASS |
| unknown | JSS-PRE-001 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 2 | 0 | 66.67% | FAIL |
| unknown | JSS-PRE-003 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 10 | 2 | 0 | 83.33% | FAIL |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 814 | 53 | 0 | 93.89% | PASS |
| unknown | JSS-REFS-004 | 129 | 4 | 0 | 96.99% | PASS |
| unknown | JSS-REFS-005 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 124 | 5 | 0 | 96.12% | PASS |
| unknown | JSS-REFS-007 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 11 | 2 | 0 | 84.62% | FAIL |
| unknown | JSS-STRUCT-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 27 | 1 | 0 | 96.43% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 19 | 4 | 0 | 82.61% | FAIL |
| unknown | JSS-WIDTH-001 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 25 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 59 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 86 | 3 | 0 | 96.63% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-CAP-003`: tp +18→18 (+0), fp +29→25 (-4), pending 0→0 (+0)

**Pinned only**

_(no rule-level changes)_

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 23 — 2026-04-28T20:53:40Z — post-CAP-002-3-extra-proper-nouns

- **Corpus size:** 98 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=23, pinned=19

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 139 | 7 | 0 | 95.21% | PASS |
| citation | JSS-CITE-003 | 8 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-BIBTEX-004 | 25 | 3 | 0 | 89.29% | FAIL |
| unknown | JSS-CAP-001 | 2 | 3 | 0 | 40.00% | FAIL |
| unknown | JSS-CAP-002 | 156 | 11 | 0 | 93.41% | PASS |
| unknown | JSS-CAP-003 | 17 | 19 | 0 | 47.22% | FAIL |
| unknown | JSS-CAP-004 | 10 | 4 | 0 | 71.43% | FAIL |
| unknown | JSS-CODE-001 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 98 | 9 | 0 | 91.59% | PASS |
| unknown | JSS-HOUSE-001 | 263 | 4 | 0 | 98.50% | PASS |
| unknown | JSS-HOUSE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 45 | 2 | 0 | 95.74% | PASS |
| unknown | JSS-MARKUP-001 | 853 | 88 | 0 | 90.65% | PASS |
| unknown | JSS-MARKUP-002 | 249 | 19 | 0 | 92.91% | PASS |
| unknown | JSS-MARKUP-003 | 167 | 3 | 0 | 98.24% | PASS |
| unknown | JSS-MARKUP-004 | 121 | 10 | 0 | 92.37% | PASS |
| unknown | JSS-NAME-001 | 2 | 1 | 0 | 66.67% | FAIL |
| unknown | JSS-NAME-002 | 33 | 10 | 0 | 76.74% | FAIL |
| unknown | JSS-OPER-001 | 57 | 1 | 0 | 98.28% | PASS |
| unknown | JSS-OPER-002 | 28 | 0 | 7 | 100.00% | PASS |
| unknown | JSS-OPER-003 | 12 | 2 | 0 | 85.71% | FAIL |
| unknown | JSS-OPER-004 | 21 | 1 | 0 | 95.45% | PASS |
| unknown | JSS-PRE-001 | 56 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 7 | 3 | 0 | 70.00% | FAIL |
| unknown | JSS-PRE-003 | 25 | 1 | 0 | 96.15% | PASS |
| unknown | JSS-PRE-006 | 24 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 28 | 5 | 0 | 84.85% | FAIL |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 814 | 53 | 0 | 93.89% | PASS |
| unknown | JSS-REFS-004 | 129 | 4 | 0 | 96.99% | PASS |
| unknown | JSS-REFS-005 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 124 | 5 | 0 | 96.12% | PASS |
| unknown | JSS-REFS-007 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 33 | 4 | 0 | 89.19% | FAIL |
| unknown | JSS-STRUCT-002 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 41 | 1 | 0 | 97.62% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 7 | 0 | 77.42% | FAIL |
| unknown | JSS-WIDTH-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 33 | 3 | 0 | 91.67% | PASS |
| unknown | JSS-XREF-002 | 129 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 123 | 3 | 0 | 97.62% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 39 | 6 | 0 | 86.67% | FAIL |
| citation | JSS-CITE-003 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-BIBTEX-004 | 18 | 1 | 0 | 94.74% | PASS |
| unknown | JSS-CAP-001 | 0 | 1 | 0 | 0.00% | FAIL |
| unknown | JSS-CAP-002 | 51 | 4 | 0 | 92.73% | PASS |
| unknown | JSS-CAP-003 | 12 | 13 | 0 | 48.00% | FAIL |
| unknown | JSS-CAP-004 | 9 | 3 | 0 | 75.00% | FAIL |
| unknown | JSS-CODE-001 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 51 | 5 | 0 | 91.07% | PASS |
| unknown | JSS-HOUSE-001 | 59 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 15 | 1 | 0 | 93.75% | PASS |
| unknown | JSS-MARKUP-001 | 314 | 47 | 0 | 86.98% | FAIL |
| unknown | JSS-MARKUP-002 | 115 | 4 | 0 | 96.64% | PASS |
| unknown | JSS-MARKUP-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-004 | 33 | 3 | 0 | 91.67% | PASS |
| unknown | JSS-NAME-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 33 | 10 | 0 | 76.74% | FAIL |
| unknown | JSS-OPER-001 | 12 | 1 | 0 | 92.31% | PASS |
| unknown | JSS-OPER-002 | 19 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-OPER-003 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 11 | 1 | 0 | 91.67% | PASS |
| unknown | JSS-PRE-001 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 2 | 0 | 66.67% | FAIL |
| unknown | JSS-PRE-003 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 10 | 2 | 0 | 83.33% | FAIL |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 814 | 53 | 0 | 93.89% | PASS |
| unknown | JSS-REFS-004 | 129 | 4 | 0 | 96.99% | PASS |
| unknown | JSS-REFS-005 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 124 | 5 | 0 | 96.12% | PASS |
| unknown | JSS-REFS-007 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 11 | 2 | 0 | 84.62% | FAIL |
| unknown | JSS-STRUCT-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 27 | 1 | 0 | 96.43% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 19 | 4 | 0 | 82.61% | FAIL |
| unknown | JSS-WIDTH-001 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 25 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 59 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 86 | 3 | 0 | 96.63% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-CAP-002`: tp +157→156 (-1), fp +15→11 (-4), pending 0→0 (+0)
- `JSS-CAP-003`: tp +18→17 (-1), fp +25→19 (-6), pending 0→0 (+0)

**Pinned only**

- `JSS-CAP-002`: tp +52→51 (-1), fp +4→4 (+0), pending 0→0 (+0)
- `JSS-CAP-003`: tp +13→12 (-1), fp +15→13 (-2), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 24 — 2026-04-29T04:37:13Z — post-MARKUP-004-non-visible-macros

- **Corpus size:** 98 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=23, pinned=19

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 139 | 7 | 0 | 95.21% | PASS |
| citation | JSS-CITE-003 | 8 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-BIBTEX-004 | 25 | 3 | 0 | 89.29% | FAIL |
| unknown | JSS-CAP-001 | 2 | 3 | 0 | 40.00% | FAIL |
| unknown | JSS-CAP-002 | 156 | 11 | 0 | 93.41% | PASS |
| unknown | JSS-CAP-003 | 17 | 19 | 0 | 47.22% | FAIL |
| unknown | JSS-CAP-004 | 10 | 4 | 0 | 71.43% | FAIL |
| unknown | JSS-CODE-001 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 98 | 9 | 0 | 91.59% | PASS |
| unknown | JSS-HOUSE-001 | 263 | 4 | 0 | 98.50% | PASS |
| unknown | JSS-HOUSE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 45 | 2 | 0 | 95.74% | PASS |
| unknown | JSS-MARKUP-001 | 853 | 88 | 0 | 90.65% | PASS |
| unknown | JSS-MARKUP-002 | 249 | 19 | 0 | 92.91% | PASS |
| unknown | JSS-MARKUP-003 | 167 | 3 | 0 | 98.24% | PASS |
| unknown | JSS-MARKUP-004 | 107 | 4 | 0 | 96.40% | PASS |
| unknown | JSS-NAME-001 | 2 | 1 | 0 | 66.67% | FAIL |
| unknown | JSS-NAME-002 | 33 | 10 | 0 | 76.74% | FAIL |
| unknown | JSS-OPER-001 | 57 | 1 | 0 | 98.28% | PASS |
| unknown | JSS-OPER-002 | 28 | 0 | 7 | 100.00% | PASS |
| unknown | JSS-OPER-003 | 12 | 2 | 0 | 85.71% | FAIL |
| unknown | JSS-OPER-004 | 21 | 1 | 0 | 95.45% | PASS |
| unknown | JSS-PRE-001 | 56 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 7 | 3 | 0 | 70.00% | FAIL |
| unknown | JSS-PRE-003 | 25 | 1 | 0 | 96.15% | PASS |
| unknown | JSS-PRE-006 | 24 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 28 | 5 | 0 | 84.85% | FAIL |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 814 | 53 | 0 | 93.89% | PASS |
| unknown | JSS-REFS-004 | 129 | 4 | 0 | 96.99% | PASS |
| unknown | JSS-REFS-005 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 124 | 5 | 0 | 96.12% | PASS |
| unknown | JSS-REFS-007 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 33 | 4 | 0 | 89.19% | FAIL |
| unknown | JSS-STRUCT-002 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 41 | 1 | 0 | 97.62% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 7 | 0 | 77.42% | FAIL |
| unknown | JSS-WIDTH-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 33 | 3 | 0 | 91.67% | PASS |
| unknown | JSS-XREF-002 | 129 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 123 | 3 | 0 | 97.62% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 39 | 6 | 0 | 86.67% | FAIL |
| citation | JSS-CITE-003 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-BIBTEX-004 | 18 | 1 | 0 | 94.74% | PASS |
| unknown | JSS-CAP-001 | 0 | 1 | 0 | 0.00% | FAIL |
| unknown | JSS-CAP-002 | 51 | 4 | 0 | 92.73% | PASS |
| unknown | JSS-CAP-003 | 12 | 13 | 0 | 48.00% | FAIL |
| unknown | JSS-CAP-004 | 9 | 3 | 0 | 75.00% | FAIL |
| unknown | JSS-CODE-001 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 51 | 5 | 0 | 91.07% | PASS |
| unknown | JSS-HOUSE-001 | 59 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 15 | 1 | 0 | 93.75% | PASS |
| unknown | JSS-MARKUP-001 | 314 | 47 | 0 | 86.98% | FAIL |
| unknown | JSS-MARKUP-002 | 115 | 4 | 0 | 96.64% | PASS |
| unknown | JSS-MARKUP-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-004 | 26 | 1 | 0 | 96.30% | PASS |
| unknown | JSS-NAME-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 33 | 10 | 0 | 76.74% | FAIL |
| unknown | JSS-OPER-001 | 12 | 1 | 0 | 92.31% | PASS |
| unknown | JSS-OPER-002 | 19 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-OPER-003 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 11 | 1 | 0 | 91.67% | PASS |
| unknown | JSS-PRE-001 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 2 | 0 | 66.67% | FAIL |
| unknown | JSS-PRE-003 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 10 | 2 | 0 | 83.33% | FAIL |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 814 | 53 | 0 | 93.89% | PASS |
| unknown | JSS-REFS-004 | 129 | 4 | 0 | 96.99% | PASS |
| unknown | JSS-REFS-005 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 124 | 5 | 0 | 96.12% | PASS |
| unknown | JSS-REFS-007 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 11 | 2 | 0 | 84.62% | FAIL |
| unknown | JSS-STRUCT-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 27 | 1 | 0 | 96.43% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 19 | 4 | 0 | 82.61% | FAIL |
| unknown | JSS-WIDTH-001 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 25 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 59 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 86 | 3 | 0 | 96.63% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-MARKUP-004`: tp +121→107 (-14), fp +10→4 (-6), pending 0→0 (+0)

**Pinned only**

- `JSS-MARKUP-004`: tp +33→26 (-7), fp +3→1 (-2), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 25 — 2026-04-29T04:42:23Z — post-CODE-003-paths-versions

- **Corpus size:** 98 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=23, pinned=19

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 139 | 7 | 0 | 95.21% | PASS |
| citation | JSS-CITE-003 | 8 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-BIBTEX-004 | 25 | 3 | 0 | 89.29% | FAIL |
| unknown | JSS-CAP-001 | 2 | 3 | 0 | 40.00% | FAIL |
| unknown | JSS-CAP-002 | 156 | 11 | 0 | 93.41% | PASS |
| unknown | JSS-CAP-003 | 17 | 19 | 0 | 47.22% | FAIL |
| unknown | JSS-CAP-004 | 10 | 4 | 0 | 71.43% | FAIL |
| unknown | JSS-CODE-001 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 93 | 7 | 0 | 93.00% | PASS |
| unknown | JSS-HOUSE-001 | 263 | 4 | 0 | 98.50% | PASS |
| unknown | JSS-HOUSE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 45 | 2 | 0 | 95.74% | PASS |
| unknown | JSS-MARKUP-001 | 853 | 88 | 0 | 90.65% | PASS |
| unknown | JSS-MARKUP-002 | 249 | 19 | 0 | 92.91% | PASS |
| unknown | JSS-MARKUP-003 | 167 | 3 | 0 | 98.24% | PASS |
| unknown | JSS-MARKUP-004 | 107 | 4 | 0 | 96.40% | PASS |
| unknown | JSS-NAME-001 | 2 | 1 | 0 | 66.67% | FAIL |
| unknown | JSS-NAME-002 | 33 | 10 | 0 | 76.74% | FAIL |
| unknown | JSS-OPER-001 | 57 | 1 | 0 | 98.28% | PASS |
| unknown | JSS-OPER-002 | 28 | 0 | 7 | 100.00% | PASS |
| unknown | JSS-OPER-003 | 12 | 2 | 0 | 85.71% | FAIL |
| unknown | JSS-OPER-004 | 21 | 1 | 0 | 95.45% | PASS |
| unknown | JSS-PRE-001 | 56 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 7 | 3 | 0 | 70.00% | FAIL |
| unknown | JSS-PRE-003 | 25 | 1 | 0 | 96.15% | PASS |
| unknown | JSS-PRE-006 | 24 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 28 | 5 | 0 | 84.85% | FAIL |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 814 | 53 | 0 | 93.89% | PASS |
| unknown | JSS-REFS-004 | 129 | 4 | 0 | 96.99% | PASS |
| unknown | JSS-REFS-005 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 124 | 5 | 0 | 96.12% | PASS |
| unknown | JSS-REFS-007 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 33 | 4 | 0 | 89.19% | FAIL |
| unknown | JSS-STRUCT-002 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 41 | 1 | 0 | 97.62% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 7 | 0 | 77.42% | FAIL |
| unknown | JSS-WIDTH-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 33 | 3 | 0 | 91.67% | PASS |
| unknown | JSS-XREF-002 | 129 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 123 | 3 | 0 | 97.62% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 39 | 6 | 0 | 86.67% | FAIL |
| citation | JSS-CITE-003 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-BIBTEX-004 | 18 | 1 | 0 | 94.74% | PASS |
| unknown | JSS-CAP-001 | 0 | 1 | 0 | 0.00% | FAIL |
| unknown | JSS-CAP-002 | 51 | 4 | 0 | 92.73% | PASS |
| unknown | JSS-CAP-003 | 12 | 13 | 0 | 48.00% | FAIL |
| unknown | JSS-CAP-004 | 9 | 3 | 0 | 75.00% | FAIL |
| unknown | JSS-CODE-001 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 49 | 3 | 0 | 94.23% | PASS |
| unknown | JSS-HOUSE-001 | 59 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 15 | 1 | 0 | 93.75% | PASS |
| unknown | JSS-MARKUP-001 | 314 | 47 | 0 | 86.98% | FAIL |
| unknown | JSS-MARKUP-002 | 115 | 4 | 0 | 96.64% | PASS |
| unknown | JSS-MARKUP-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-004 | 26 | 1 | 0 | 96.30% | PASS |
| unknown | JSS-NAME-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 33 | 10 | 0 | 76.74% | FAIL |
| unknown | JSS-OPER-001 | 12 | 1 | 0 | 92.31% | PASS |
| unknown | JSS-OPER-002 | 19 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-OPER-003 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 11 | 1 | 0 | 91.67% | PASS |
| unknown | JSS-PRE-001 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 2 | 0 | 66.67% | FAIL |
| unknown | JSS-PRE-003 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 10 | 2 | 0 | 83.33% | FAIL |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 814 | 53 | 0 | 93.89% | PASS |
| unknown | JSS-REFS-004 | 129 | 4 | 0 | 96.99% | PASS |
| unknown | JSS-REFS-005 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 124 | 5 | 0 | 96.12% | PASS |
| unknown | JSS-REFS-007 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 11 | 2 | 0 | 84.62% | FAIL |
| unknown | JSS-STRUCT-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 27 | 1 | 0 | 96.43% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 19 | 4 | 0 | 82.61% | FAIL |
| unknown | JSS-WIDTH-001 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 25 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 59 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 86 | 3 | 0 | 96.63% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-CODE-003`: tp +98→93 (-5), fp +9→7 (-2), pending 0→0 (+0)

**Pinned only**

- `JSS-CODE-003`: tp +51→49 (-2), fp +5→3 (-2), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 26 — 2026-04-29T04:44:47Z — post-PRE-002-nojss-skip

- **Corpus size:** 98 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=23, pinned=19

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 139 | 7 | 0 | 95.21% | PASS |
| citation | JSS-CITE-003 | 8 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-BIBTEX-004 | 25 | 3 | 0 | 89.29% | FAIL |
| unknown | JSS-CAP-001 | 2 | 3 | 0 | 40.00% | FAIL |
| unknown | JSS-CAP-002 | 156 | 11 | 0 | 93.41% | PASS |
| unknown | JSS-CAP-003 | 17 | 19 | 0 | 47.22% | FAIL |
| unknown | JSS-CAP-004 | 10 | 4 | 0 | 71.43% | FAIL |
| unknown | JSS-CODE-001 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 93 | 7 | 0 | 93.00% | PASS |
| unknown | JSS-HOUSE-001 | 263 | 4 | 0 | 98.50% | PASS |
| unknown | JSS-HOUSE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 45 | 2 | 0 | 95.74% | PASS |
| unknown | JSS-MARKUP-001 | 853 | 88 | 0 | 90.65% | PASS |
| unknown | JSS-MARKUP-002 | 249 | 19 | 0 | 92.91% | PASS |
| unknown | JSS-MARKUP-003 | 167 | 3 | 0 | 98.24% | PASS |
| unknown | JSS-MARKUP-004 | 107 | 4 | 0 | 96.40% | PASS |
| unknown | JSS-NAME-001 | 2 | 1 | 0 | 66.67% | FAIL |
| unknown | JSS-NAME-002 | 33 | 10 | 0 | 76.74% | FAIL |
| unknown | JSS-OPER-001 | 57 | 1 | 0 | 98.28% | PASS |
| unknown | JSS-OPER-002 | 28 | 0 | 7 | 100.00% | PASS |
| unknown | JSS-OPER-003 | 12 | 2 | 0 | 85.71% | FAIL |
| unknown | JSS-OPER-004 | 21 | 1 | 0 | 95.45% | PASS |
| unknown | JSS-PRE-001 | 56 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 25 | 1 | 0 | 96.15% | PASS |
| unknown | JSS-PRE-006 | 24 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 28 | 5 | 0 | 84.85% | FAIL |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 814 | 53 | 0 | 93.89% | PASS |
| unknown | JSS-REFS-004 | 129 | 4 | 0 | 96.99% | PASS |
| unknown | JSS-REFS-005 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 124 | 5 | 0 | 96.12% | PASS |
| unknown | JSS-REFS-007 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 33 | 4 | 0 | 89.19% | FAIL |
| unknown | JSS-STRUCT-002 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 41 | 1 | 0 | 97.62% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 7 | 0 | 77.42% | FAIL |
| unknown | JSS-WIDTH-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 33 | 3 | 0 | 91.67% | PASS |
| unknown | JSS-XREF-002 | 129 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 123 | 3 | 0 | 97.62% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 39 | 6 | 0 | 86.67% | FAIL |
| citation | JSS-CITE-003 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-BIBTEX-004 | 18 | 1 | 0 | 94.74% | PASS |
| unknown | JSS-CAP-001 | 0 | 1 | 0 | 0.00% | FAIL |
| unknown | JSS-CAP-002 | 51 | 4 | 0 | 92.73% | PASS |
| unknown | JSS-CAP-003 | 12 | 13 | 0 | 48.00% | FAIL |
| unknown | JSS-CAP-004 | 9 | 3 | 0 | 75.00% | FAIL |
| unknown | JSS-CODE-001 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 49 | 3 | 0 | 94.23% | PASS |
| unknown | JSS-HOUSE-001 | 59 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 15 | 1 | 0 | 93.75% | PASS |
| unknown | JSS-MARKUP-001 | 314 | 47 | 0 | 86.98% | FAIL |
| unknown | JSS-MARKUP-002 | 115 | 4 | 0 | 96.64% | PASS |
| unknown | JSS-MARKUP-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-004 | 26 | 1 | 0 | 96.30% | PASS |
| unknown | JSS-NAME-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 33 | 10 | 0 | 76.74% | FAIL |
| unknown | JSS-OPER-001 | 12 | 1 | 0 | 92.31% | PASS |
| unknown | JSS-OPER-002 | 19 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-OPER-003 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 11 | 1 | 0 | 91.67% | PASS |
| unknown | JSS-PRE-001 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 10 | 2 | 0 | 83.33% | FAIL |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 814 | 53 | 0 | 93.89% | PASS |
| unknown | JSS-REFS-004 | 129 | 4 | 0 | 96.99% | PASS |
| unknown | JSS-REFS-005 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 124 | 5 | 0 | 96.12% | PASS |
| unknown | JSS-REFS-007 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 11 | 2 | 0 | 84.62% | FAIL |
| unknown | JSS-STRUCT-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 27 | 1 | 0 | 96.43% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 19 | 4 | 0 | 82.61% | FAIL |
| unknown | JSS-WIDTH-001 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 25 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 59 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 86 | 3 | 0 | 96.63% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-PRE-002`: tp +7→4 (-3), fp +3→0 (-3), pending 0→0 (+0)

**Pinned only**

- `JSS-PRE-002`: tp +4→4 (+0), fp +2→0 (-2), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 27 — 2026-04-29T04:50:18Z — post-PRE-007-jss-class-and-non-markup

- **Corpus size:** 98 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=23, pinned=19

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 139 | 7 | 0 | 95.21% | PASS |
| citation | JSS-CITE-003 | 8 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-BIBTEX-004 | 25 | 3 | 0 | 89.29% | FAIL |
| unknown | JSS-CAP-001 | 2 | 3 | 0 | 40.00% | FAIL |
| unknown | JSS-CAP-002 | 156 | 11 | 0 | 93.41% | PASS |
| unknown | JSS-CAP-003 | 17 | 19 | 0 | 47.22% | FAIL |
| unknown | JSS-CAP-004 | 10 | 4 | 0 | 71.43% | FAIL |
| unknown | JSS-CODE-001 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 93 | 7 | 0 | 93.00% | PASS |
| unknown | JSS-HOUSE-001 | 263 | 4 | 0 | 98.50% | PASS |
| unknown | JSS-HOUSE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 45 | 2 | 0 | 95.74% | PASS |
| unknown | JSS-MARKUP-001 | 853 | 88 | 0 | 90.65% | PASS |
| unknown | JSS-MARKUP-002 | 249 | 19 | 0 | 92.91% | PASS |
| unknown | JSS-MARKUP-003 | 167 | 3 | 0 | 98.24% | PASS |
| unknown | JSS-MARKUP-004 | 107 | 4 | 0 | 96.40% | PASS |
| unknown | JSS-NAME-001 | 2 | 1 | 0 | 66.67% | FAIL |
| unknown | JSS-NAME-002 | 33 | 10 | 0 | 76.74% | FAIL |
| unknown | JSS-OPER-001 | 57 | 1 | 0 | 98.28% | PASS |
| unknown | JSS-OPER-002 | 28 | 0 | 7 | 100.00% | PASS |
| unknown | JSS-OPER-003 | 12 | 2 | 0 | 85.71% | FAIL |
| unknown | JSS-OPER-004 | 21 | 1 | 0 | 95.45% | PASS |
| unknown | JSS-PRE-001 | 56 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 24 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 814 | 53 | 0 | 93.89% | PASS |
| unknown | JSS-REFS-004 | 129 | 4 | 0 | 96.99% | PASS |
| unknown | JSS-REFS-005 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 124 | 5 | 0 | 96.12% | PASS |
| unknown | JSS-REFS-007 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 33 | 4 | 0 | 89.19% | FAIL |
| unknown | JSS-STRUCT-002 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 41 | 1 | 0 | 97.62% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 7 | 0 | 77.42% | FAIL |
| unknown | JSS-WIDTH-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 33 | 3 | 0 | 91.67% | PASS |
| unknown | JSS-XREF-002 | 129 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 123 | 3 | 0 | 97.62% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 39 | 6 | 0 | 86.67% | FAIL |
| citation | JSS-CITE-003 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-BIBTEX-004 | 18 | 1 | 0 | 94.74% | PASS |
| unknown | JSS-CAP-001 | 0 | 1 | 0 | 0.00% | FAIL |
| unknown | JSS-CAP-002 | 51 | 4 | 0 | 92.73% | PASS |
| unknown | JSS-CAP-003 | 12 | 13 | 0 | 48.00% | FAIL |
| unknown | JSS-CAP-004 | 9 | 3 | 0 | 75.00% | FAIL |
| unknown | JSS-CODE-001 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 49 | 3 | 0 | 94.23% | PASS |
| unknown | JSS-HOUSE-001 | 59 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 15 | 1 | 0 | 93.75% | PASS |
| unknown | JSS-MARKUP-001 | 314 | 47 | 0 | 86.98% | FAIL |
| unknown | JSS-MARKUP-002 | 115 | 4 | 0 | 96.64% | PASS |
| unknown | JSS-MARKUP-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-004 | 26 | 1 | 0 | 96.30% | PASS |
| unknown | JSS-NAME-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 33 | 10 | 0 | 76.74% | FAIL |
| unknown | JSS-OPER-001 | 12 | 1 | 0 | 92.31% | PASS |
| unknown | JSS-OPER-002 | 19 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-OPER-003 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 11 | 1 | 0 | 91.67% | PASS |
| unknown | JSS-PRE-001 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 814 | 53 | 0 | 93.89% | PASS |
| unknown | JSS-REFS-004 | 129 | 4 | 0 | 96.99% | PASS |
| unknown | JSS-REFS-005 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 124 | 5 | 0 | 96.12% | PASS |
| unknown | JSS-REFS-007 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 11 | 2 | 0 | 84.62% | FAIL |
| unknown | JSS-STRUCT-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 27 | 1 | 0 | 96.43% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 19 | 4 | 0 | 82.61% | FAIL |
| unknown | JSS-WIDTH-001 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 25 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 59 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 86 | 3 | 0 | 96.63% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-PRE-003`: tp +25→1 (-24), fp +1→0 (-1), pending 0→0 (+0)
- `JSS-PRE-007`: tp +28→5 (-23), fp +5→0 (-5), pending 0→0 (+0)

**Pinned only**

- `JSS-PRE-003`: tp +9→1 (-8), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-PRE-007`: tp +10→5 (-5), fp +2→0 (-2), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 28 — 2026-04-29T04:54:57Z — post-HOUSE-003-jss-class-gate

- **Corpus size:** 98 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=23, pinned=19

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 139 | 7 | 0 | 95.21% | PASS |
| citation | JSS-CITE-003 | 8 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-BIBTEX-004 | 25 | 3 | 0 | 89.29% | FAIL |
| unknown | JSS-CAP-001 | 2 | 3 | 0 | 40.00% | FAIL |
| unknown | JSS-CAP-002 | 156 | 11 | 0 | 93.41% | PASS |
| unknown | JSS-CAP-003 | 17 | 19 | 0 | 47.22% | FAIL |
| unknown | JSS-CAP-004 | 10 | 4 | 0 | 71.43% | FAIL |
| unknown | JSS-CODE-001 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 93 | 7 | 0 | 93.00% | PASS |
| unknown | JSS-HOUSE-001 | 263 | 4 | 0 | 98.50% | PASS |
| unknown | JSS-HOUSE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 853 | 88 | 0 | 90.65% | PASS |
| unknown | JSS-MARKUP-002 | 249 | 19 | 0 | 92.91% | PASS |
| unknown | JSS-MARKUP-003 | 167 | 3 | 0 | 98.24% | PASS |
| unknown | JSS-MARKUP-004 | 107 | 4 | 0 | 96.40% | PASS |
| unknown | JSS-NAME-001 | 2 | 1 | 0 | 66.67% | FAIL |
| unknown | JSS-NAME-002 | 33 | 10 | 0 | 76.74% | FAIL |
| unknown | JSS-OPER-001 | 57 | 1 | 0 | 98.28% | PASS |
| unknown | JSS-OPER-002 | 28 | 0 | 7 | 100.00% | PASS |
| unknown | JSS-OPER-003 | 12 | 2 | 0 | 85.71% | FAIL |
| unknown | JSS-OPER-004 | 21 | 1 | 0 | 95.45% | PASS |
| unknown | JSS-PRE-001 | 56 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 24 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 814 | 53 | 0 | 93.89% | PASS |
| unknown | JSS-REFS-004 | 129 | 4 | 0 | 96.99% | PASS |
| unknown | JSS-REFS-005 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 124 | 5 | 0 | 96.12% | PASS |
| unknown | JSS-REFS-007 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 33 | 4 | 0 | 89.19% | FAIL |
| unknown | JSS-STRUCT-002 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 41 | 1 | 0 | 97.62% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 7 | 0 | 77.42% | FAIL |
| unknown | JSS-WIDTH-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 33 | 3 | 0 | 91.67% | PASS |
| unknown | JSS-XREF-002 | 129 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 123 | 3 | 0 | 97.62% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 39 | 6 | 0 | 86.67% | FAIL |
| citation | JSS-CITE-003 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-BIBTEX-004 | 18 | 1 | 0 | 94.74% | PASS |
| unknown | JSS-CAP-001 | 0 | 1 | 0 | 0.00% | FAIL |
| unknown | JSS-CAP-002 | 51 | 4 | 0 | 92.73% | PASS |
| unknown | JSS-CAP-003 | 12 | 13 | 0 | 48.00% | FAIL |
| unknown | JSS-CAP-004 | 9 | 3 | 0 | 75.00% | FAIL |
| unknown | JSS-CODE-001 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 49 | 3 | 0 | 94.23% | PASS |
| unknown | JSS-HOUSE-001 | 59 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 314 | 47 | 0 | 86.98% | FAIL |
| unknown | JSS-MARKUP-002 | 115 | 4 | 0 | 96.64% | PASS |
| unknown | JSS-MARKUP-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-004 | 26 | 1 | 0 | 96.30% | PASS |
| unknown | JSS-NAME-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 33 | 10 | 0 | 76.74% | FAIL |
| unknown | JSS-OPER-001 | 12 | 1 | 0 | 92.31% | PASS |
| unknown | JSS-OPER-002 | 19 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-OPER-003 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 11 | 1 | 0 | 91.67% | PASS |
| unknown | JSS-PRE-001 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 814 | 53 | 0 | 93.89% | PASS |
| unknown | JSS-REFS-004 | 129 | 4 | 0 | 96.99% | PASS |
| unknown | JSS-REFS-005 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 124 | 5 | 0 | 96.12% | PASS |
| unknown | JSS-REFS-007 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 11 | 2 | 0 | 84.62% | FAIL |
| unknown | JSS-STRUCT-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 27 | 1 | 0 | 96.43% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 19 | 4 | 0 | 82.61% | FAIL |
| unknown | JSS-WIDTH-001 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 25 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 59 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 86 | 3 | 0 | 96.63% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-HOUSE-003`: tp +45→14 (-31), fp +2→0 (-2), pending 0→0 (+0)

**Pinned only**

- `JSS-HOUSE-003`: tp +15→11 (-4), fp +1→0 (-1), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 29 — 2026-04-29T05:00:16Z — post-NAME-002-drop-springer

- **Corpus size:** 98 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=23, pinned=19

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 139 | 7 | 0 | 95.21% | PASS |
| citation | JSS-CITE-003 | 8 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-BIBTEX-004 | 25 | 3 | 0 | 89.29% | FAIL |
| unknown | JSS-CAP-001 | 2 | 3 | 0 | 40.00% | FAIL |
| unknown | JSS-CAP-002 | 156 | 11 | 0 | 93.41% | PASS |
| unknown | JSS-CAP-003 | 17 | 19 | 0 | 47.22% | FAIL |
| unknown | JSS-CAP-004 | 10 | 4 | 0 | 71.43% | FAIL |
| unknown | JSS-CODE-001 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 93 | 7 | 0 | 93.00% | PASS |
| unknown | JSS-HOUSE-001 | 263 | 4 | 0 | 98.50% | PASS |
| unknown | JSS-HOUSE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 853 | 88 | 0 | 90.65% | PASS |
| unknown | JSS-MARKUP-002 | 249 | 19 | 0 | 92.91% | PASS |
| unknown | JSS-MARKUP-003 | 167 | 3 | 0 | 98.24% | PASS |
| unknown | JSS-MARKUP-004 | 107 | 4 | 0 | 96.40% | PASS |
| unknown | JSS-NAME-001 | 2 | 1 | 0 | 66.67% | FAIL |
| unknown | JSS-NAME-002 | 10 | 2 | 0 | 83.33% | FAIL |
| unknown | JSS-OPER-001 | 57 | 1 | 0 | 98.28% | PASS |
| unknown | JSS-OPER-002 | 28 | 0 | 7 | 100.00% | PASS |
| unknown | JSS-OPER-003 | 12 | 2 | 0 | 85.71% | FAIL |
| unknown | JSS-OPER-004 | 21 | 1 | 0 | 95.45% | PASS |
| unknown | JSS-PRE-001 | 56 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 24 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 814 | 53 | 0 | 93.89% | PASS |
| unknown | JSS-REFS-004 | 129 | 4 | 0 | 96.99% | PASS |
| unknown | JSS-REFS-005 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 124 | 5 | 0 | 96.12% | PASS |
| unknown | JSS-REFS-007 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 33 | 4 | 0 | 89.19% | FAIL |
| unknown | JSS-STRUCT-002 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 41 | 1 | 0 | 97.62% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 7 | 0 | 77.42% | FAIL |
| unknown | JSS-WIDTH-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 33 | 3 | 0 | 91.67% | PASS |
| unknown | JSS-XREF-002 | 129 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 123 | 3 | 0 | 97.62% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 39 | 6 | 0 | 86.67% | FAIL |
| citation | JSS-CITE-003 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-BIBTEX-004 | 18 | 1 | 0 | 94.74% | PASS |
| unknown | JSS-CAP-001 | 0 | 1 | 0 | 0.00% | FAIL |
| unknown | JSS-CAP-002 | 51 | 4 | 0 | 92.73% | PASS |
| unknown | JSS-CAP-003 | 12 | 13 | 0 | 48.00% | FAIL |
| unknown | JSS-CAP-004 | 9 | 3 | 0 | 75.00% | FAIL |
| unknown | JSS-CODE-001 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 49 | 3 | 0 | 94.23% | PASS |
| unknown | JSS-HOUSE-001 | 59 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 314 | 47 | 0 | 86.98% | FAIL |
| unknown | JSS-MARKUP-002 | 115 | 4 | 0 | 96.64% | PASS |
| unknown | JSS-MARKUP-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-004 | 26 | 1 | 0 | 96.30% | PASS |
| unknown | JSS-NAME-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 10 | 2 | 0 | 83.33% | FAIL |
| unknown | JSS-OPER-001 | 12 | 1 | 0 | 92.31% | PASS |
| unknown | JSS-OPER-002 | 19 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-OPER-003 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 11 | 1 | 0 | 91.67% | PASS |
| unknown | JSS-PRE-001 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 814 | 53 | 0 | 93.89% | PASS |
| unknown | JSS-REFS-004 | 129 | 4 | 0 | 96.99% | PASS |
| unknown | JSS-REFS-005 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 124 | 5 | 0 | 96.12% | PASS |
| unknown | JSS-REFS-007 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 11 | 2 | 0 | 84.62% | FAIL |
| unknown | JSS-STRUCT-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 27 | 1 | 0 | 96.43% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 19 | 4 | 0 | 82.61% | FAIL |
| unknown | JSS-WIDTH-001 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 25 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 59 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 86 | 3 | 0 | 96.63% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-NAME-002`: tp +33→10 (-23), fp +10→2 (-8), pending 0→0 (+0)

**Pinned only**

- `JSS-NAME-002`: tp +33→10 (-23), fp +10→2 (-8), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 30 — 2026-04-29T05:02:51Z — post-OPER-003-chunk-newlines

- **Corpus size:** 98 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=23, pinned=19

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 139 | 7 | 0 | 95.21% | PASS |
| citation | JSS-CITE-003 | 8 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-BIBTEX-004 | 25 | 3 | 0 | 89.29% | FAIL |
| unknown | JSS-CAP-001 | 2 | 3 | 0 | 40.00% | FAIL |
| unknown | JSS-CAP-002 | 156 | 11 | 0 | 93.41% | PASS |
| unknown | JSS-CAP-003 | 17 | 19 | 0 | 47.22% | FAIL |
| unknown | JSS-CAP-004 | 10 | 4 | 0 | 71.43% | FAIL |
| unknown | JSS-CODE-001 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 93 | 7 | 0 | 93.00% | PASS |
| unknown | JSS-HOUSE-001 | 263 | 4 | 0 | 98.50% | PASS |
| unknown | JSS-HOUSE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 853 | 88 | 0 | 90.65% | PASS |
| unknown | JSS-MARKUP-002 | 249 | 19 | 0 | 92.91% | PASS |
| unknown | JSS-MARKUP-003 | 167 | 3 | 0 | 98.24% | PASS |
| unknown | JSS-MARKUP-004 | 107 | 4 | 0 | 96.40% | PASS |
| unknown | JSS-NAME-001 | 2 | 1 | 0 | 66.67% | FAIL |
| unknown | JSS-NAME-002 | 10 | 2 | 0 | 83.33% | FAIL |
| unknown | JSS-OPER-001 | 57 | 1 | 0 | 98.28% | PASS |
| unknown | JSS-OPER-002 | 28 | 0 | 7 | 100.00% | PASS |
| unknown | JSS-OPER-003 | 9 | 1 | 0 | 90.00% | PASS |
| unknown | JSS-OPER-004 | 21 | 1 | 0 | 95.45% | PASS |
| unknown | JSS-PRE-001 | 56 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 24 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 814 | 53 | 0 | 93.89% | PASS |
| unknown | JSS-REFS-004 | 129 | 4 | 0 | 96.99% | PASS |
| unknown | JSS-REFS-005 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 124 | 5 | 0 | 96.12% | PASS |
| unknown | JSS-REFS-007 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 33 | 4 | 0 | 89.19% | FAIL |
| unknown | JSS-STRUCT-002 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 41 | 1 | 0 | 97.62% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 7 | 0 | 77.42% | FAIL |
| unknown | JSS-WIDTH-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 33 | 3 | 0 | 91.67% | PASS |
| unknown | JSS-XREF-002 | 129 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 123 | 3 | 0 | 97.62% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 39 | 6 | 0 | 86.67% | FAIL |
| citation | JSS-CITE-003 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-BIBTEX-004 | 18 | 1 | 0 | 94.74% | PASS |
| unknown | JSS-CAP-001 | 0 | 1 | 0 | 0.00% | FAIL |
| unknown | JSS-CAP-002 | 51 | 4 | 0 | 92.73% | PASS |
| unknown | JSS-CAP-003 | 12 | 13 | 0 | 48.00% | FAIL |
| unknown | JSS-CAP-004 | 9 | 3 | 0 | 75.00% | FAIL |
| unknown | JSS-CODE-001 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 49 | 3 | 0 | 94.23% | PASS |
| unknown | JSS-HOUSE-001 | 59 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 314 | 47 | 0 | 86.98% | FAIL |
| unknown | JSS-MARKUP-002 | 115 | 4 | 0 | 96.64% | PASS |
| unknown | JSS-MARKUP-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-004 | 26 | 1 | 0 | 96.30% | PASS |
| unknown | JSS-NAME-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 10 | 2 | 0 | 83.33% | FAIL |
| unknown | JSS-OPER-001 | 12 | 1 | 0 | 92.31% | PASS |
| unknown | JSS-OPER-002 | 19 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-OPER-003 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 11 | 1 | 0 | 91.67% | PASS |
| unknown | JSS-PRE-001 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 814 | 53 | 0 | 93.89% | PASS |
| unknown | JSS-REFS-004 | 129 | 4 | 0 | 96.99% | PASS |
| unknown | JSS-REFS-005 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 124 | 5 | 0 | 96.12% | PASS |
| unknown | JSS-REFS-007 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 11 | 2 | 0 | 84.62% | FAIL |
| unknown | JSS-STRUCT-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 27 | 1 | 0 | 96.43% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 19 | 4 | 0 | 82.61% | FAIL |
| unknown | JSS-WIDTH-001 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 25 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 59 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 86 | 3 | 0 | 96.63% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-OPER-003`: tp +12→9 (-3), fp +2→1 (-1), pending 0→0 (+0)

**Pinned only**

- `JSS-OPER-003`: tp +9→6 (-3), fp +0→0 (+0), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 31 — 2026-04-29T05:06:02Z — post-STRUCT-001-illustrations-examples

- **Corpus size:** 98 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=23, pinned=19

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 139 | 7 | 0 | 95.21% | PASS |
| citation | JSS-CITE-003 | 8 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-BIBTEX-004 | 25 | 3 | 0 | 89.29% | FAIL |
| unknown | JSS-CAP-001 | 2 | 3 | 0 | 40.00% | FAIL |
| unknown | JSS-CAP-002 | 156 | 11 | 0 | 93.41% | PASS |
| unknown | JSS-CAP-003 | 17 | 19 | 0 | 47.22% | FAIL |
| unknown | JSS-CAP-004 | 10 | 4 | 0 | 71.43% | FAIL |
| unknown | JSS-CODE-001 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 93 | 7 | 0 | 93.00% | PASS |
| unknown | JSS-HOUSE-001 | 263 | 4 | 0 | 98.50% | PASS |
| unknown | JSS-HOUSE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 853 | 88 | 0 | 90.65% | PASS |
| unknown | JSS-MARKUP-002 | 249 | 19 | 0 | 92.91% | PASS |
| unknown | JSS-MARKUP-003 | 167 | 3 | 0 | 98.24% | PASS |
| unknown | JSS-MARKUP-004 | 107 | 4 | 0 | 96.40% | PASS |
| unknown | JSS-NAME-001 | 2 | 1 | 0 | 66.67% | FAIL |
| unknown | JSS-NAME-002 | 10 | 2 | 0 | 83.33% | FAIL |
| unknown | JSS-OPER-001 | 57 | 1 | 0 | 98.28% | PASS |
| unknown | JSS-OPER-002 | 28 | 0 | 7 | 100.00% | PASS |
| unknown | JSS-OPER-003 | 9 | 1 | 0 | 90.00% | PASS |
| unknown | JSS-OPER-004 | 21 | 1 | 0 | 95.45% | PASS |
| unknown | JSS-PRE-001 | 56 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 24 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 814 | 53 | 0 | 93.89% | PASS |
| unknown | JSS-REFS-004 | 129 | 4 | 0 | 96.99% | PASS |
| unknown | JSS-REFS-005 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 124 | 5 | 0 | 96.12% | PASS |
| unknown | JSS-REFS-007 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 30 | 3 | 0 | 90.91% | PASS |
| unknown | JSS-STRUCT-002 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 41 | 1 | 0 | 97.62% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 7 | 0 | 77.42% | FAIL |
| unknown | JSS-WIDTH-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 33 | 3 | 0 | 91.67% | PASS |
| unknown | JSS-XREF-002 | 129 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 123 | 3 | 0 | 97.62% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 39 | 6 | 0 | 86.67% | FAIL |
| citation | JSS-CITE-003 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-BIBTEX-004 | 18 | 1 | 0 | 94.74% | PASS |
| unknown | JSS-CAP-001 | 0 | 1 | 0 | 0.00% | FAIL |
| unknown | JSS-CAP-002 | 51 | 4 | 0 | 92.73% | PASS |
| unknown | JSS-CAP-003 | 12 | 13 | 0 | 48.00% | FAIL |
| unknown | JSS-CAP-004 | 9 | 3 | 0 | 75.00% | FAIL |
| unknown | JSS-CODE-001 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 49 | 3 | 0 | 94.23% | PASS |
| unknown | JSS-HOUSE-001 | 59 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 314 | 47 | 0 | 86.98% | FAIL |
| unknown | JSS-MARKUP-002 | 115 | 4 | 0 | 96.64% | PASS |
| unknown | JSS-MARKUP-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-004 | 26 | 1 | 0 | 96.30% | PASS |
| unknown | JSS-NAME-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 10 | 2 | 0 | 83.33% | FAIL |
| unknown | JSS-OPER-001 | 12 | 1 | 0 | 92.31% | PASS |
| unknown | JSS-OPER-002 | 19 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-OPER-003 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 11 | 1 | 0 | 91.67% | PASS |
| unknown | JSS-PRE-001 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 814 | 53 | 0 | 93.89% | PASS |
| unknown | JSS-REFS-004 | 129 | 4 | 0 | 96.99% | PASS |
| unknown | JSS-REFS-005 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 124 | 5 | 0 | 96.12% | PASS |
| unknown | JSS-REFS-007 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 10 | 1 | 0 | 90.91% | PASS |
| unknown | JSS-STRUCT-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 27 | 1 | 0 | 96.43% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 19 | 4 | 0 | 82.61% | FAIL |
| unknown | JSS-WIDTH-001 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 25 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 59 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 86 | 3 | 0 | 96.63% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-STRUCT-001`: tp +33→30 (-3), fp +4→3 (-1), pending 0→0 (+0)

**Pinned only**

- `JSS-STRUCT-001`: tp +11→10 (-1), fp +2→1 (-1), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 32 — 2026-04-29T10:59:16Z — post-NAME-002-revert-drop-springer

- **Corpus size:** 98 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=23, pinned=19

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 139 | 7 | 0 | 95.21% | PASS |
| citation | JSS-CITE-003 | 8 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-BIBTEX-004 | 25 | 3 | 0 | 89.29% | FAIL |
| unknown | JSS-CAP-001 | 2 | 3 | 0 | 40.00% | FAIL |
| unknown | JSS-CAP-002 | 156 | 11 | 0 | 93.41% | PASS |
| unknown | JSS-CAP-003 | 17 | 19 | 0 | 47.22% | FAIL |
| unknown | JSS-CAP-004 | 10 | 4 | 0 | 71.43% | FAIL |
| unknown | JSS-CODE-001 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 93 | 7 | 0 | 93.00% | PASS |
| unknown | JSS-HOUSE-001 | 263 | 4 | 0 | 98.50% | PASS |
| unknown | JSS-HOUSE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 853 | 88 | 0 | 90.65% | PASS |
| unknown | JSS-MARKUP-002 | 249 | 19 | 0 | 92.91% | PASS |
| unknown | JSS-MARKUP-003 | 167 | 3 | 0 | 98.24% | PASS |
| unknown | JSS-MARKUP-004 | 107 | 4 | 0 | 96.40% | PASS |
| unknown | JSS-NAME-001 | 2 | 1 | 0 | 66.67% | FAIL |
| unknown | JSS-NAME-002 | 33 | 10 | 0 | 76.74% | FAIL |
| unknown | JSS-OPER-001 | 57 | 1 | 0 | 98.28% | PASS |
| unknown | JSS-OPER-002 | 28 | 0 | 7 | 100.00% | PASS |
| unknown | JSS-OPER-003 | 9 | 1 | 0 | 90.00% | PASS |
| unknown | JSS-OPER-004 | 21 | 1 | 0 | 95.45% | PASS |
| unknown | JSS-PRE-001 | 56 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 24 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 814 | 53 | 0 | 93.89% | PASS |
| unknown | JSS-REFS-004 | 129 | 4 | 0 | 96.99% | PASS |
| unknown | JSS-REFS-005 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 124 | 5 | 0 | 96.12% | PASS |
| unknown | JSS-REFS-007 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 30 | 3 | 0 | 90.91% | PASS |
| unknown | JSS-STRUCT-002 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 41 | 1 | 0 | 97.62% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 7 | 0 | 77.42% | FAIL |
| unknown | JSS-WIDTH-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 33 | 3 | 0 | 91.67% | PASS |
| unknown | JSS-XREF-002 | 129 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 123 | 3 | 0 | 97.62% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 39 | 6 | 0 | 86.67% | FAIL |
| citation | JSS-CITE-003 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-BIBTEX-004 | 18 | 1 | 0 | 94.74% | PASS |
| unknown | JSS-CAP-001 | 0 | 1 | 0 | 0.00% | FAIL |
| unknown | JSS-CAP-002 | 51 | 4 | 0 | 92.73% | PASS |
| unknown | JSS-CAP-003 | 12 | 13 | 0 | 48.00% | FAIL |
| unknown | JSS-CAP-004 | 9 | 3 | 0 | 75.00% | FAIL |
| unknown | JSS-CODE-001 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 49 | 3 | 0 | 94.23% | PASS |
| unknown | JSS-HOUSE-001 | 59 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 314 | 47 | 0 | 86.98% | FAIL |
| unknown | JSS-MARKUP-002 | 115 | 4 | 0 | 96.64% | PASS |
| unknown | JSS-MARKUP-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-004 | 26 | 1 | 0 | 96.30% | PASS |
| unknown | JSS-NAME-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 33 | 10 | 0 | 76.74% | FAIL |
| unknown | JSS-OPER-001 | 12 | 1 | 0 | 92.31% | PASS |
| unknown | JSS-OPER-002 | 19 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-OPER-003 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 11 | 1 | 0 | 91.67% | PASS |
| unknown | JSS-PRE-001 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 814 | 53 | 0 | 93.89% | PASS |
| unknown | JSS-REFS-004 | 129 | 4 | 0 | 96.99% | PASS |
| unknown | JSS-REFS-005 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 124 | 5 | 0 | 96.12% | PASS |
| unknown | JSS-REFS-007 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 10 | 1 | 0 | 90.91% | PASS |
| unknown | JSS-STRUCT-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 27 | 1 | 0 | 96.43% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 19 | 4 | 0 | 82.61% | FAIL |
| unknown | JSS-WIDTH-001 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 25 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 59 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 86 | 3 | 0 | 96.63% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-NAME-002`: tp +10→33 (+23), fp +2→10 (+8), pending 0→0 (+0)

**Pinned only**

- `JSS-NAME-002`: tp +10→33 (+23), fp +2→10 (+8), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 33 — 2026-04-29T11:10:02Z — post-NAME-002-flip-fps-and-skiplist

- **Corpus size:** 98 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=23, pinned=19

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 139 | 7 | 0 | 95.21% | PASS |
| citation | JSS-CITE-003 | 8 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-BIBTEX-004 | 25 | 3 | 0 | 89.29% | FAIL |
| unknown | JSS-CAP-001 | 2 | 3 | 0 | 40.00% | FAIL |
| unknown | JSS-CAP-002 | 156 | 11 | 0 | 93.41% | PASS |
| unknown | JSS-CAP-003 | 17 | 19 | 0 | 47.22% | FAIL |
| unknown | JSS-CAP-004 | 10 | 4 | 0 | 71.43% | FAIL |
| unknown | JSS-CODE-001 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 93 | 7 | 0 | 93.00% | PASS |
| unknown | JSS-HOUSE-001 | 263 | 4 | 0 | 98.50% | PASS |
| unknown | JSS-HOUSE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 853 | 88 | 0 | 90.65% | PASS |
| unknown | JSS-MARKUP-002 | 249 | 19 | 0 | 92.91% | PASS |
| unknown | JSS-MARKUP-003 | 167 | 3 | 0 | 98.24% | PASS |
| unknown | JSS-MARKUP-004 | 107 | 4 | 0 | 96.40% | PASS |
| unknown | JSS-NAME-001 | 2 | 1 | 0 | 66.67% | FAIL |
| unknown | JSS-NAME-002 | 43 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-001 | 57 | 1 | 0 | 98.28% | PASS |
| unknown | JSS-OPER-002 | 28 | 0 | 7 | 100.00% | PASS |
| unknown | JSS-OPER-003 | 9 | 1 | 0 | 90.00% | PASS |
| unknown | JSS-OPER-004 | 21 | 1 | 0 | 95.45% | PASS |
| unknown | JSS-PRE-001 | 56 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 24 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 814 | 53 | 0 | 93.89% | PASS |
| unknown | JSS-REFS-004 | 129 | 4 | 0 | 96.99% | PASS |
| unknown | JSS-REFS-005 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 124 | 5 | 0 | 96.12% | PASS |
| unknown | JSS-REFS-007 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 30 | 3 | 0 | 90.91% | PASS |
| unknown | JSS-STRUCT-002 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 41 | 1 | 0 | 97.62% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 7 | 0 | 77.42% | FAIL |
| unknown | JSS-WIDTH-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 33 | 3 | 0 | 91.67% | PASS |
| unknown | JSS-XREF-002 | 129 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 123 | 3 | 0 | 97.62% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 39 | 6 | 0 | 86.67% | FAIL |
| citation | JSS-CITE-003 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-BIBTEX-004 | 18 | 1 | 0 | 94.74% | PASS |
| unknown | JSS-CAP-001 | 0 | 1 | 0 | 0.00% | FAIL |
| unknown | JSS-CAP-002 | 51 | 4 | 0 | 92.73% | PASS |
| unknown | JSS-CAP-003 | 12 | 13 | 0 | 48.00% | FAIL |
| unknown | JSS-CAP-004 | 9 | 3 | 0 | 75.00% | FAIL |
| unknown | JSS-CODE-001 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 49 | 3 | 0 | 94.23% | PASS |
| unknown | JSS-HOUSE-001 | 59 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 314 | 47 | 0 | 86.98% | FAIL |
| unknown | JSS-MARKUP-002 | 115 | 4 | 0 | 96.64% | PASS |
| unknown | JSS-MARKUP-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-004 | 26 | 1 | 0 | 96.30% | PASS |
| unknown | JSS-NAME-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 43 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-001 | 12 | 1 | 0 | 92.31% | PASS |
| unknown | JSS-OPER-002 | 19 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-OPER-003 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 11 | 1 | 0 | 91.67% | PASS |
| unknown | JSS-PRE-001 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 814 | 53 | 0 | 93.89% | PASS |
| unknown | JSS-REFS-004 | 129 | 4 | 0 | 96.99% | PASS |
| unknown | JSS-REFS-005 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 124 | 5 | 0 | 96.12% | PASS |
| unknown | JSS-REFS-007 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 10 | 1 | 0 | 90.91% | PASS |
| unknown | JSS-STRUCT-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 27 | 1 | 0 | 96.43% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 19 | 4 | 0 | 82.61% | FAIL |
| unknown | JSS-WIDTH-001 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 25 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 59 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 86 | 3 | 0 | 96.63% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-NAME-002`: tp +33→43 (+10), fp +10→0 (-10), pending 0→0 (+0)

**Pinned only**

- `JSS-NAME-002`: tp +33→43 (+10), fp +10→0 (-10), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 34 — 2026-04-29T15:48:55Z — post-CAP-001-own-package-skip-and-flips

- **Corpus size:** 98 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=23, pinned=19

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 139 | 7 | 0 | 95.21% | PASS |
| citation | JSS-CITE-003 | 8 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 25 | 3 | 0 | 89.29% | FAIL |
| unknown | JSS-CAP-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 156 | 11 | 0 | 93.41% | PASS |
| unknown | JSS-CAP-003 | 17 | 19 | 0 | 47.22% | FAIL |
| unknown | JSS-CAP-004 | 10 | 4 | 0 | 71.43% | FAIL |
| unknown | JSS-CODE-001 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 93 | 7 | 0 | 93.00% | PASS |
| unknown | JSS-HOUSE-001 | 263 | 4 | 0 | 98.50% | PASS |
| unknown | JSS-HOUSE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 853 | 88 | 0 | 90.65% | PASS |
| unknown | JSS-MARKUP-002 | 249 | 19 | 0 | 92.91% | PASS |
| unknown | JSS-MARKUP-003 | 167 | 3 | 0 | 98.24% | PASS |
| unknown | JSS-MARKUP-004 | 107 | 4 | 0 | 96.40% | PASS |
| unknown | JSS-NAME-001 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 43 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-001 | 57 | 1 | 0 | 98.28% | PASS |
| unknown | JSS-OPER-002 | 28 | 0 | 7 | 100.00% | PASS |
| unknown | JSS-OPER-003 | 9 | 1 | 0 | 90.00% | PASS |
| unknown | JSS-OPER-004 | 21 | 1 | 0 | 95.45% | PASS |
| unknown | JSS-PRE-001 | 56 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 24 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 814 | 53 | 0 | 93.89% | PASS |
| unknown | JSS-REFS-004 | 129 | 4 | 0 | 96.99% | PASS |
| unknown | JSS-REFS-005 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 124 | 5 | 0 | 96.12% | PASS |
| unknown | JSS-REFS-007 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 30 | 3 | 0 | 90.91% | PASS |
| unknown | JSS-STRUCT-002 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 41 | 1 | 0 | 97.62% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 7 | 0 | 77.42% | FAIL |
| unknown | JSS-WIDTH-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 33 | 3 | 0 | 91.67% | PASS |
| unknown | JSS-XREF-002 | 129 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 123 | 3 | 0 | 97.62% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 39 | 6 | 0 | 86.67% | FAIL |
| citation | JSS-CITE-003 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 18 | 1 | 0 | 94.74% | PASS |
| unknown | JSS-CAP-002 | 51 | 4 | 0 | 92.73% | PASS |
| unknown | JSS-CAP-003 | 12 | 13 | 0 | 48.00% | FAIL |
| unknown | JSS-CAP-004 | 9 | 3 | 0 | 75.00% | FAIL |
| unknown | JSS-CODE-001 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 49 | 3 | 0 | 94.23% | PASS |
| unknown | JSS-HOUSE-001 | 59 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 314 | 47 | 0 | 86.98% | FAIL |
| unknown | JSS-MARKUP-002 | 115 | 4 | 0 | 96.64% | PASS |
| unknown | JSS-MARKUP-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-004 | 26 | 1 | 0 | 96.30% | PASS |
| unknown | JSS-NAME-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 43 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-001 | 12 | 1 | 0 | 92.31% | PASS |
| unknown | JSS-OPER-002 | 19 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-OPER-003 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 11 | 1 | 0 | 91.67% | PASS |
| unknown | JSS-PRE-001 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 814 | 53 | 0 | 93.89% | PASS |
| unknown | JSS-REFS-004 | 129 | 4 | 0 | 96.99% | PASS |
| unknown | JSS-REFS-005 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 124 | 5 | 0 | 96.12% | PASS |
| unknown | JSS-REFS-007 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 10 | 1 | 0 | 90.91% | PASS |
| unknown | JSS-STRUCT-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 27 | 1 | 0 | 96.43% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 19 | 4 | 0 | 82.61% | FAIL |
| unknown | JSS-WIDTH-001 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 25 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 59 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 86 | 3 | 0 | 96.63% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-BIBTEX-003`: tp +8→9 (+1), fp +1→0 (-1), pending 0→0 (+0)
- `JSS-CAP-001`: tp +2→1 (-1), fp +3→0 (-3), pending 0→0 (+0)
- `JSS-NAME-001`: tp +2→3 (+1), fp +1→0 (-1), pending 0→0 (+0)

**Pinned only**

- `JSS-BIBTEX-003`: tp +8→9 (+1), fp +1→0 (-1), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 35 — 2026-04-29T15:50:02Z — post-BIBTEX-004-flip-migrated-mislabels

- **Corpus size:** 98 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=23, pinned=19

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 139 | 7 | 0 | 95.21% | PASS |
| citation | JSS-CITE-003 | 8 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 28 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 156 | 11 | 0 | 93.41% | PASS |
| unknown | JSS-CAP-003 | 17 | 19 | 0 | 47.22% | FAIL |
| unknown | JSS-CAP-004 | 10 | 4 | 0 | 71.43% | FAIL |
| unknown | JSS-CODE-001 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 93 | 7 | 0 | 93.00% | PASS |
| unknown | JSS-HOUSE-001 | 263 | 4 | 0 | 98.50% | PASS |
| unknown | JSS-HOUSE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 853 | 88 | 0 | 90.65% | PASS |
| unknown | JSS-MARKUP-002 | 249 | 19 | 0 | 92.91% | PASS |
| unknown | JSS-MARKUP-003 | 167 | 3 | 0 | 98.24% | PASS |
| unknown | JSS-MARKUP-004 | 107 | 4 | 0 | 96.40% | PASS |
| unknown | JSS-NAME-001 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 43 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-001 | 57 | 1 | 0 | 98.28% | PASS |
| unknown | JSS-OPER-002 | 28 | 0 | 7 | 100.00% | PASS |
| unknown | JSS-OPER-003 | 9 | 1 | 0 | 90.00% | PASS |
| unknown | JSS-OPER-004 | 21 | 1 | 0 | 95.45% | PASS |
| unknown | JSS-PRE-001 | 56 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 24 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 814 | 53 | 0 | 93.89% | PASS |
| unknown | JSS-REFS-004 | 129 | 4 | 0 | 96.99% | PASS |
| unknown | JSS-REFS-005 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 124 | 5 | 0 | 96.12% | PASS |
| unknown | JSS-REFS-007 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 30 | 3 | 0 | 90.91% | PASS |
| unknown | JSS-STRUCT-002 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 41 | 1 | 0 | 97.62% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 7 | 0 | 77.42% | FAIL |
| unknown | JSS-WIDTH-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 33 | 3 | 0 | 91.67% | PASS |
| unknown | JSS-XREF-002 | 129 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 123 | 3 | 0 | 97.62% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 39 | 6 | 0 | 86.67% | FAIL |
| citation | JSS-CITE-003 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 19 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 51 | 4 | 0 | 92.73% | PASS |
| unknown | JSS-CAP-003 | 12 | 13 | 0 | 48.00% | FAIL |
| unknown | JSS-CAP-004 | 9 | 3 | 0 | 75.00% | FAIL |
| unknown | JSS-CODE-001 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 49 | 3 | 0 | 94.23% | PASS |
| unknown | JSS-HOUSE-001 | 59 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 314 | 47 | 0 | 86.98% | FAIL |
| unknown | JSS-MARKUP-002 | 115 | 4 | 0 | 96.64% | PASS |
| unknown | JSS-MARKUP-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-004 | 26 | 1 | 0 | 96.30% | PASS |
| unknown | JSS-NAME-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 43 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-001 | 12 | 1 | 0 | 92.31% | PASS |
| unknown | JSS-OPER-002 | 19 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-OPER-003 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 11 | 1 | 0 | 91.67% | PASS |
| unknown | JSS-PRE-001 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 814 | 53 | 0 | 93.89% | PASS |
| unknown | JSS-REFS-004 | 129 | 4 | 0 | 96.99% | PASS |
| unknown | JSS-REFS-005 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 124 | 5 | 0 | 96.12% | PASS |
| unknown | JSS-REFS-007 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 10 | 1 | 0 | 90.91% | PASS |
| unknown | JSS-STRUCT-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 27 | 1 | 0 | 96.43% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 19 | 4 | 0 | 82.61% | FAIL |
| unknown | JSS-WIDTH-001 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 25 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 59 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 86 | 3 | 0 | 96.63% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-BIBTEX-004`: tp +25→28 (+3), fp +3→0 (-3), pending 0→0 (+0)

**Pinned only**

- `JSS-BIBTEX-004`: tp +18→19 (+1), fp +1→0 (-1), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 36 — 2026-04-29T17:34:38Z — iter-36-baseline

- **Corpus size:** 112 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=28, pinned=24

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 147 | 9 | 0 | 94.23% | PASS |
| citation | JSS-CITE-003 | 9 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 36 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 157 | 12 | 0 | 92.90% | PASS |
| unknown | JSS-CAP-003 | 17 | 22 | 0 | 43.59% | FAIL |
| unknown | JSS-CAP-004 | 11 | 4 | 0 | 73.33% | FAIL |
| unknown | JSS-CODE-001 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 113 | 7 | 0 | 94.17% | PASS |
| unknown | JSS-HOUSE-001 | 273 | 4 | 0 | 98.56% | PASS |
| unknown | JSS-HOUSE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 902 | 96 | 0 | 90.38% | PASS |
| unknown | JSS-MARKUP-002 | 250 | 19 | 0 | 92.94% | PASS |
| unknown | JSS-MARKUP-003 | 171 | 3 | 0 | 98.28% | PASS |
| unknown | JSS-MARKUP-004 | 107 | 4 | 0 | 96.40% | PASS |
| unknown | JSS-NAME-001 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 51 | 1 | 0 | 98.08% | PASS |
| unknown | JSS-OPER-001 | 60 | 1 | 0 | 98.36% | PASS |
| unknown | JSS-OPER-002 | 47 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-003 | 9 | 1 | 0 | 90.00% | PASS |
| unknown | JSS-OPER-004 | 47 | 1 | 0 | 97.92% | PASS |
| unknown | JSS-PRE-001 | 63 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 24 | 1 | 0 | 96.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 2 | 0 | 33.33% | FAIL |
| unknown | JSS-REFS-003 | 948 | 58 | 0 | 94.23% | PASS |
| unknown | JSS-REFS-004 | 156 | 4 | 0 | 97.50% | PASS |
| unknown | JSS-REFS-005 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 152 | 5 | 0 | 96.82% | PASS |
| unknown | JSS-REFS-007 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 39 | 3 | 0 | 92.86% | PASS |
| unknown | JSS-STRUCT-002 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 53 | 1 | 0 | 98.15% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 7 | 0 | 77.42% | FAIL |
| unknown | JSS-WIDTH-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 33 | 4 | 0 | 89.19% | FAIL |
| unknown | JSS-XREF-002 | 154 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 143 | 3 | 0 | 97.95% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 46 | 8 | 0 | 85.19% | FAIL |
| citation | JSS-CITE-003 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 27 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 52 | 5 | 0 | 91.23% | PASS |
| unknown | JSS-CAP-003 | 12 | 15 | 0 | 44.44% | FAIL |
| unknown | JSS-CAP-004 | 10 | 3 | 0 | 76.92% | FAIL |
| unknown | JSS-CODE-001 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 63 | 3 | 0 | 95.45% | PASS |
| unknown | JSS-HOUSE-001 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 335 | 49 | 0 | 87.24% | FAIL |
| unknown | JSS-MARKUP-002 | 115 | 4 | 0 | 96.64% | PASS |
| unknown | JSS-MARKUP-003 | 17 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-004 | 26 | 1 | 0 | 96.30% | PASS |
| unknown | JSS-NAME-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 51 | 1 | 0 | 98.08% | PASS |
| unknown | JSS-OPER-001 | 14 | 1 | 0 | 93.33% | PASS |
| unknown | JSS-OPER-002 | 32 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-003 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 37 | 1 | 0 | 97.37% | PASS |
| unknown | JSS-PRE-001 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 13 | 1 | 0 | 92.86% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 2 | 0 | 33.33% | FAIL |
| unknown | JSS-REFS-003 | 948 | 58 | 0 | 94.23% | PASS |
| unknown | JSS-REFS-004 | 156 | 4 | 0 | 97.50% | PASS |
| unknown | JSS-REFS-005 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 152 | 5 | 0 | 96.82% | PASS |
| unknown | JSS-REFS-007 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 15 | 1 | 0 | 93.75% | PASS |
| unknown | JSS-STRUCT-002 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 36 | 1 | 0 | 97.30% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 19 | 4 | 0 | 82.61% | FAIL |
| unknown | JSS-WIDTH-001 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 25 | 1 | 0 | 96.15% | PASS |
| unknown | JSS-XREF-002 | 74 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 104 | 3 | 0 | 97.20% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-CITE-002`: tp +139→147 (+8), fp +7→9 (+2), pending 0→0 (+0)
- `JSS-CITE-003`: tp +8→9 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-CITE-004`: tp +4→18 (+14), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-ABBR-001`: tp +10→16 (+6), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-BIBTEX-002`: tp +2→4 (+2), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-BIBTEX-003`: tp +9→13 (+4), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-BIBTEX-004`: tp +28→36 (+8), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-CAP-002`: tp +156→157 (+1), fp +11→12 (+1), pending 0→0 (+0)
- `JSS-CAP-003`: tp +17→17 (+0), fp +19→22 (+3), pending 0→0 (+0)
- `JSS-CAP-004`: tp +10→11 (+1), fp +4→4 (+0), pending 0→0 (+0)
- `JSS-CODE-003`: tp +93→113 (+20), fp +7→7 (+0), pending 0→0 (+0)
- `JSS-HOUSE-001`: tp +263→273 (+10), fp +4→4 (+0), pending 0→0 (+0)
- `JSS-HOUSE-002`: tp +4→5 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-HOUSE-003`: tp +14→16 (+2), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-MARKUP-001`: tp +853→902 (+49), fp +88→96 (+8), pending 0→0 (+0)
- `JSS-MARKUP-002`: tp +249→250 (+1), fp +19→19 (+0), pending 0→0 (+0)
- `JSS-MARKUP-003`: tp +167→171 (+4), fp +3→3 (+0), pending 0→0 (+0)
- `JSS-NAME-002`: tp +43→51 (+8), fp +0→1 (+1), pending 0→0 (+0)
- `JSS-OPER-001`: tp +57→60 (+3), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-OPER-002`: tp +28→47 (+19), fp +0→0 (+0), pending 7→0 (-7)
- `JSS-OPER-004`: tp +21→47 (+26), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-PRE-001`: tp +56→63 (+7), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-PRE-006`: tp +24→24 (+0), fp +0→1 (+1), pending 0→0 (+0)
- `JSS-REFS-001`: tp +1→1 (+0), fp +0→2 (+2), pending 0→0 (+0)
- `JSS-REFS-003`: tp +814→948 (+134), fp +53→58 (+5), pending 0→0 (+0)
- `JSS-REFS-004`: tp +129→156 (+27), fp +4→4 (+0), pending 0→0 (+0)
- `JSS-REFS-005`: tp +5→6 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-REFS-006`: tp +124→152 (+28), fp +5→5 (+0), pending 0→0 (+0)
- `JSS-REFS-007`: tp +53→64 (+11), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-STRUCT-001`: tp +30→39 (+9), fp +3→3 (+0), pending 0→0 (+0)
- `JSS-STRUCT-002`: tp +8→11 (+3), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-TYPO-001`: tp +41→53 (+12), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-WIDTH-001`: tp +10→13 (+3), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-XREF-001`: tp +33→33 (+0), fp +3→4 (+1), pending 0→0 (+0)
- `JSS-XREF-002`: tp +129→154 (+25), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-XREF-004`: tp +123→143 (+20), fp +3→3 (+0), pending 0→0 (+0)

**Pinned only**

- `JSS-CITE-002`: tp +39→46 (+7), fp +6→8 (+2), pending 0→0 (+0)
- `JSS-CITE-003`: tp +3→4 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-ABBR-001`: tp +7→9 (+2), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-BIBTEX-002`: tp +2→4 (+2), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-BIBTEX-003`: tp +9→13 (+4), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-BIBTEX-004`: tp +19→27 (+8), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-CAP-002`: tp +51→52 (+1), fp +4→5 (+1), pending 0→0 (+0)
- `JSS-CAP-003`: tp +12→12 (+0), fp +13→15 (+2), pending 0→0 (+0)
- `JSS-CAP-004`: tp +9→10 (+1), fp +3→3 (+0), pending 0→0 (+0)
- `JSS-CODE-003`: tp +49→63 (+14), fp +3→3 (+0), pending 0→0 (+0)
- `JSS-HOUSE-001`: tp +59→64 (+5), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-HOUSE-002`: tp +4→5 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-HOUSE-003`: tp +11→13 (+2), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-MARKUP-001`: tp +314→335 (+21), fp +47→49 (+2), pending 0→0 (+0)
- `JSS-MARKUP-003`: tp +13→17 (+4), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-NAME-002`: tp +43→51 (+8), fp +0→1 (+1), pending 0→0 (+0)
- `JSS-OPER-001`: tp +12→14 (+2), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-OPER-002`: tp +19→32 (+13), fp +0→0 (+0), pending 1→0 (-1)
- `JSS-OPER-004`: tp +11→37 (+26), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-PRE-001`: tp +16→18 (+2), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-PRE-006`: tp +13→13 (+0), fp +0→1 (+1), pending 0→0 (+0)
- `JSS-REFS-001`: tp +1→1 (+0), fp +0→2 (+2), pending 0→0 (+0)
- `JSS-REFS-003`: tp +814→948 (+134), fp +53→58 (+5), pending 0→0 (+0)
- `JSS-REFS-004`: tp +129→156 (+27), fp +4→4 (+0), pending 0→0 (+0)
- `JSS-REFS-005`: tp +5→6 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-REFS-006`: tp +124→152 (+28), fp +5→5 (+0), pending 0→0 (+0)
- `JSS-REFS-007`: tp +53→64 (+11), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-STRUCT-001`: tp +10→15 (+5), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-STRUCT-002`: tp +5→8 (+3), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-TYPO-001`: tp +27→36 (+9), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-WIDTH-001`: tp +5→8 (+3), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-XREF-001`: tp +25→25 (+0), fp +0→1 (+1), pending 0→0 (+0)
- `JSS-XREF-002`: tp +59→74 (+15), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-XREF-004`: tp +86→104 (+18), fp +3→3 (+0), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 37 — 2026-04-29T18:29:21Z — post-OPER-003-period-and-directional

- **Corpus size:** 112 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=28, pinned=24

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 147 | 9 | 0 | 94.23% | PASS |
| citation | JSS-CITE-003 | 9 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 11 | 5 | 0 | 68.75% | FAIL |
| unknown | JSS-BIBTEX-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 36 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 157 | 12 | 0 | 92.90% | PASS |
| unknown | JSS-CAP-003 | 17 | 22 | 0 | 43.59% | FAIL |
| unknown | JSS-CAP-004 | 11 | 4 | 0 | 73.33% | FAIL |
| unknown | JSS-CODE-001 | 14 | 1 | 0 | 93.33% | PASS |
| unknown | JSS-CODE-003 | 113 | 7 | 0 | 94.17% | PASS |
| unknown | JSS-HOUSE-001 | 273 | 4 | 0 | 98.56% | PASS |
| unknown | JSS-HOUSE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 899 | 99 | 0 | 90.08% | PASS |
| unknown | JSS-MARKUP-002 | 249 | 20 | 0 | 92.57% | PASS |
| unknown | JSS-MARKUP-003 | 171 | 3 | 0 | 98.28% | PASS |
| unknown | JSS-MARKUP-004 | 107 | 4 | 0 | 96.40% | PASS |
| unknown | JSS-NAME-001 | 2 | 1 | 0 | 66.67% | FAIL |
| unknown | JSS-NAME-002 | 51 | 1 | 0 | 98.08% | PASS |
| unknown | JSS-OPER-001 | 60 | 1 | 0 | 98.36% | PASS |
| unknown | JSS-OPER-002 | 47 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 47 | 1 | 0 | 97.92% | PASS |
| unknown | JSS-PRE-001 | 62 | 1 | 0 | 98.41% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 21 | 4 | 0 | 84.00% | FAIL |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 2 | 1 | 0 | 66.67% | FAIL |
| unknown | JSS-REFS-003 | 948 | 58 | 0 | 94.23% | PASS |
| unknown | JSS-REFS-004 | 155 | 5 | 0 | 96.88% | PASS |
| unknown | JSS-REFS-005 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 152 | 5 | 0 | 96.82% | PASS |
| unknown | JSS-REFS-007 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 38 | 4 | 0 | 90.48% | PASS |
| unknown | JSS-STRUCT-002 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 47 | 7 | 0 | 87.04% | FAIL |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 7 | 0 | 77.42% | FAIL |
| unknown | JSS-WIDTH-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 27 | 10 | 0 | 72.97% | FAIL |
| unknown | JSS-XREF-002 | 154 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 143 | 3 | 0 | 97.95% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 46 | 8 | 0 | 85.19% | FAIL |
| citation | JSS-CITE-003 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 7 | 2 | 0 | 77.78% | FAIL |
| unknown | JSS-BIBTEX-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 27 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 52 | 5 | 0 | 91.23% | PASS |
| unknown | JSS-CAP-003 | 12 | 15 | 0 | 44.44% | FAIL |
| unknown | JSS-CAP-004 | 10 | 3 | 0 | 76.92% | FAIL |
| unknown | JSS-CODE-001 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 63 | 3 | 0 | 95.45% | PASS |
| unknown | JSS-HOUSE-001 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 332 | 52 | 0 | 86.46% | FAIL |
| unknown | JSS-MARKUP-002 | 115 | 4 | 0 | 96.64% | PASS |
| unknown | JSS-MARKUP-003 | 17 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-004 | 26 | 1 | 0 | 96.30% | PASS |
| unknown | JSS-NAME-001 | 0 | 1 | 0 | 0.00% | FAIL |
| unknown | JSS-NAME-002 | 51 | 1 | 0 | 98.08% | PASS |
| unknown | JSS-OPER-001 | 14 | 1 | 0 | 93.33% | PASS |
| unknown | JSS-OPER-002 | 32 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 37 | 1 | 0 | 97.37% | PASS |
| unknown | JSS-PRE-001 | 17 | 1 | 0 | 94.44% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 10 | 4 | 0 | 71.43% | FAIL |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 2 | 1 | 0 | 66.67% | FAIL |
| unknown | JSS-REFS-003 | 948 | 58 | 0 | 94.23% | PASS |
| unknown | JSS-REFS-004 | 155 | 5 | 0 | 96.88% | PASS |
| unknown | JSS-REFS-005 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 152 | 5 | 0 | 96.82% | PASS |
| unknown | JSS-REFS-007 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 14 | 2 | 0 | 87.50% | FAIL |
| unknown | JSS-STRUCT-002 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 30 | 7 | 0 | 81.08% | FAIL |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 19 | 4 | 0 | 82.61% | FAIL |
| unknown | JSS-WIDTH-001 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 20 | 6 | 0 | 76.92% | FAIL |
| unknown | JSS-XREF-002 | 74 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 104 | 3 | 0 | 97.20% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-ABBR-001`: tp +16→11 (-5), fp +0→5 (+5), pending 0→0 (+0)
- `JSS-CODE-001`: tp +15→14 (-1), fp +0→1 (+1), pending 0→0 (+0)
- `JSS-MARKUP-001`: tp +902→899 (-3), fp +96→99 (+3), pending 0→0 (+0)
- `JSS-MARKUP-002`: tp +250→249 (-1), fp +19→20 (+1), pending 0→0 (+0)
- `JSS-NAME-001`: tp +3→2 (-1), fp +0→1 (+1), pending 0→0 (+0)
- `JSS-PRE-001`: tp +63→62 (-1), fp +0→1 (+1), pending 0→0 (+0)
- `JSS-PRE-006`: tp +24→21 (-3), fp +1→4 (+3), pending 0→0 (+0)
- `JSS-REFS-001`: tp +1→2 (+1), fp +2→1 (-1), pending 0→0 (+0)
- `JSS-REFS-004`: tp +156→155 (-1), fp +4→5 (+1), pending 0→0 (+0)
- `JSS-STRUCT-001`: tp +39→38 (-1), fp +3→4 (+1), pending 0→0 (+0)
- `JSS-TYPO-001`: tp +53→47 (-6), fp +1→7 (+6), pending 0→0 (+0)
- `JSS-XREF-001`: tp +33→27 (-6), fp +4→10 (+6), pending 0→0 (+0)

**Pinned only**

- `JSS-ABBR-001`: tp +9→7 (-2), fp +0→2 (+2), pending 0→0 (+0)
- `JSS-MARKUP-001`: tp +335→332 (-3), fp +49→52 (+3), pending 0→0 (+0)
- `JSS-NAME-001`: tp +1→0 (-1), fp +0→1 (+1), pending 0→0 (+0)
- `JSS-PRE-001`: tp +18→17 (-1), fp +0→1 (+1), pending 0→0 (+0)
- `JSS-PRE-006`: tp +13→10 (-3), fp +1→4 (+3), pending 0→0 (+0)
- `JSS-REFS-001`: tp +1→2 (+1), fp +2→1 (-1), pending 0→0 (+0)
- `JSS-REFS-004`: tp +156→155 (-1), fp +4→5 (+1), pending 0→0 (+0)
- `JSS-STRUCT-001`: tp +15→14 (-1), fp +1→2 (+1), pending 0→0 (+0)
- `JSS-TYPO-001`: tp +36→30 (-6), fp +1→7 (+6), pending 0→0 (+0)
- `JSS-XREF-001`: tp +25→20 (-5), fp +1→6 (+5), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 38 — 2026-04-29T18:34:53Z — post-XREF-001-cross-paper-refs

- **Corpus size:** 112 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=28, pinned=24

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 147 | 9 | 0 | 94.23% | PASS |
| citation | JSS-CITE-003 | 9 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 11 | 5 | 0 | 68.75% | FAIL |
| unknown | JSS-BIBTEX-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 36 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 157 | 12 | 0 | 92.90% | PASS |
| unknown | JSS-CAP-003 | 17 | 22 | 0 | 43.59% | FAIL |
| unknown | JSS-CAP-004 | 11 | 4 | 0 | 73.33% | FAIL |
| unknown | JSS-CODE-001 | 14 | 1 | 0 | 93.33% | PASS |
| unknown | JSS-CODE-003 | 113 | 7 | 0 | 94.17% | PASS |
| unknown | JSS-HOUSE-001 | 273 | 4 | 0 | 98.56% | PASS |
| unknown | JSS-HOUSE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 899 | 99 | 0 | 90.08% | PASS |
| unknown | JSS-MARKUP-002 | 249 | 20 | 0 | 92.57% | PASS |
| unknown | JSS-MARKUP-003 | 171 | 3 | 0 | 98.28% | PASS |
| unknown | JSS-MARKUP-004 | 107 | 4 | 0 | 96.40% | PASS |
| unknown | JSS-NAME-001 | 2 | 1 | 0 | 66.67% | FAIL |
| unknown | JSS-NAME-002 | 51 | 1 | 0 | 98.08% | PASS |
| unknown | JSS-OPER-001 | 60 | 1 | 0 | 98.36% | PASS |
| unknown | JSS-OPER-002 | 47 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 47 | 1 | 0 | 97.92% | PASS |
| unknown | JSS-PRE-001 | 62 | 1 | 0 | 98.41% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 21 | 4 | 0 | 84.00% | FAIL |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 2 | 1 | 0 | 66.67% | FAIL |
| unknown | JSS-REFS-003 | 948 | 58 | 0 | 94.23% | PASS |
| unknown | JSS-REFS-004 | 155 | 5 | 0 | 96.88% | PASS |
| unknown | JSS-REFS-005 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 152 | 5 | 0 | 96.82% | PASS |
| unknown | JSS-REFS-007 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 38 | 4 | 0 | 90.48% | PASS |
| unknown | JSS-STRUCT-002 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 47 | 7 | 0 | 87.04% | FAIL |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 7 | 0 | 77.42% | FAIL |
| unknown | JSS-WIDTH-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 20 | 3 | 0 | 86.96% | FAIL |
| unknown | JSS-XREF-002 | 154 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 143 | 3 | 0 | 97.95% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 46 | 8 | 0 | 85.19% | FAIL |
| citation | JSS-CITE-003 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 7 | 2 | 0 | 77.78% | FAIL |
| unknown | JSS-BIBTEX-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 27 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 52 | 5 | 0 | 91.23% | PASS |
| unknown | JSS-CAP-003 | 12 | 15 | 0 | 44.44% | FAIL |
| unknown | JSS-CAP-004 | 10 | 3 | 0 | 76.92% | FAIL |
| unknown | JSS-CODE-001 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 63 | 3 | 0 | 95.45% | PASS |
| unknown | JSS-HOUSE-001 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 332 | 52 | 0 | 86.46% | FAIL |
| unknown | JSS-MARKUP-002 | 115 | 4 | 0 | 96.64% | PASS |
| unknown | JSS-MARKUP-003 | 17 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-004 | 26 | 1 | 0 | 96.30% | PASS |
| unknown | JSS-NAME-001 | 0 | 1 | 0 | 0.00% | FAIL |
| unknown | JSS-NAME-002 | 51 | 1 | 0 | 98.08% | PASS |
| unknown | JSS-OPER-001 | 14 | 1 | 0 | 93.33% | PASS |
| unknown | JSS-OPER-002 | 32 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 37 | 1 | 0 | 97.37% | PASS |
| unknown | JSS-PRE-001 | 17 | 1 | 0 | 94.44% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 10 | 4 | 0 | 71.43% | FAIL |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 2 | 1 | 0 | 66.67% | FAIL |
| unknown | JSS-REFS-003 | 948 | 58 | 0 | 94.23% | PASS |
| unknown | JSS-REFS-004 | 155 | 5 | 0 | 96.88% | PASS |
| unknown | JSS-REFS-005 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 152 | 5 | 0 | 96.82% | PASS |
| unknown | JSS-REFS-007 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 14 | 2 | 0 | 87.50% | FAIL |
| unknown | JSS-STRUCT-002 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 30 | 7 | 0 | 81.08% | FAIL |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 19 | 4 | 0 | 82.61% | FAIL |
| unknown | JSS-WIDTH-001 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 13 | 2 | 0 | 86.67% | FAIL |
| unknown | JSS-XREF-002 | 74 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 104 | 3 | 0 | 97.20% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-XREF-001`: tp +27→20 (-7), fp +10→3 (-7), pending 0→0 (+0)

**Pinned only**

- `JSS-XREF-001`: tp +20→13 (-7), fp +6→2 (-4), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 39 — 2026-04-29T18:40:33Z — post-ABBR-001-author-initials

- **Corpus size:** 112 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=28, pinned=24

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 147 | 9 | 0 | 94.23% | PASS |
| citation | JSS-CITE-003 | 9 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 8 | 3 | 0 | 72.73% | FAIL |
| unknown | JSS-BIBTEX-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 36 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 157 | 12 | 0 | 92.90% | PASS |
| unknown | JSS-CAP-003 | 17 | 22 | 0 | 43.59% | FAIL |
| unknown | JSS-CAP-004 | 11 | 4 | 0 | 73.33% | FAIL |
| unknown | JSS-CODE-001 | 14 | 1 | 0 | 93.33% | PASS |
| unknown | JSS-CODE-003 | 113 | 7 | 0 | 94.17% | PASS |
| unknown | JSS-HOUSE-001 | 273 | 4 | 0 | 98.56% | PASS |
| unknown | JSS-HOUSE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 899 | 99 | 0 | 90.08% | PASS |
| unknown | JSS-MARKUP-002 | 249 | 20 | 0 | 92.57% | PASS |
| unknown | JSS-MARKUP-003 | 171 | 3 | 0 | 98.28% | PASS |
| unknown | JSS-MARKUP-004 | 107 | 4 | 0 | 96.40% | PASS |
| unknown | JSS-NAME-001 | 2 | 1 | 0 | 66.67% | FAIL |
| unknown | JSS-NAME-002 | 51 | 1 | 0 | 98.08% | PASS |
| unknown | JSS-OPER-001 | 60 | 1 | 0 | 98.36% | PASS |
| unknown | JSS-OPER-002 | 47 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 47 | 1 | 0 | 97.92% | PASS |
| unknown | JSS-PRE-001 | 62 | 1 | 0 | 98.41% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 21 | 4 | 0 | 84.00% | FAIL |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 2 | 1 | 0 | 66.67% | FAIL |
| unknown | JSS-REFS-003 | 948 | 58 | 0 | 94.23% | PASS |
| unknown | JSS-REFS-004 | 155 | 5 | 0 | 96.88% | PASS |
| unknown | JSS-REFS-005 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 152 | 5 | 0 | 96.82% | PASS |
| unknown | JSS-REFS-007 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 38 | 4 | 0 | 90.48% | PASS |
| unknown | JSS-STRUCT-002 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 47 | 7 | 0 | 87.04% | FAIL |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 7 | 0 | 77.42% | FAIL |
| unknown | JSS-WIDTH-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 20 | 3 | 0 | 86.96% | FAIL |
| unknown | JSS-XREF-002 | 154 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 143 | 3 | 0 | 97.95% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 46 | 8 | 0 | 85.19% | FAIL |
| citation | JSS-CITE-003 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 27 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 52 | 5 | 0 | 91.23% | PASS |
| unknown | JSS-CAP-003 | 12 | 15 | 0 | 44.44% | FAIL |
| unknown | JSS-CAP-004 | 10 | 3 | 0 | 76.92% | FAIL |
| unknown | JSS-CODE-001 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 63 | 3 | 0 | 95.45% | PASS |
| unknown | JSS-HOUSE-001 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 332 | 52 | 0 | 86.46% | FAIL |
| unknown | JSS-MARKUP-002 | 115 | 4 | 0 | 96.64% | PASS |
| unknown | JSS-MARKUP-003 | 17 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-004 | 26 | 1 | 0 | 96.30% | PASS |
| unknown | JSS-NAME-001 | 0 | 1 | 0 | 0.00% | FAIL |
| unknown | JSS-NAME-002 | 51 | 1 | 0 | 98.08% | PASS |
| unknown | JSS-OPER-001 | 14 | 1 | 0 | 93.33% | PASS |
| unknown | JSS-OPER-002 | 32 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 37 | 1 | 0 | 97.37% | PASS |
| unknown | JSS-PRE-001 | 17 | 1 | 0 | 94.44% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 10 | 4 | 0 | 71.43% | FAIL |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 2 | 1 | 0 | 66.67% | FAIL |
| unknown | JSS-REFS-003 | 948 | 58 | 0 | 94.23% | PASS |
| unknown | JSS-REFS-004 | 155 | 5 | 0 | 96.88% | PASS |
| unknown | JSS-REFS-005 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 152 | 5 | 0 | 96.82% | PASS |
| unknown | JSS-REFS-007 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 14 | 2 | 0 | 87.50% | FAIL |
| unknown | JSS-STRUCT-002 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 30 | 7 | 0 | 81.08% | FAIL |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 19 | 4 | 0 | 82.61% | FAIL |
| unknown | JSS-WIDTH-001 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 13 | 2 | 0 | 86.67% | FAIL |
| unknown | JSS-XREF-002 | 74 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 104 | 3 | 0 | 97.20% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-ABBR-001`: tp +11→8 (-3), fp +5→3 (-2), pending 0→0 (+0)

**Pinned only**

- `JSS-ABBR-001`: tp +7→4 (-3), fp +2→0 (-2), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 40 — 2026-04-29T18:44:24Z — post-NAME-001-url-skip-and-REFS-001-crossref

- **Corpus size:** 112 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=28, pinned=24

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 147 | 9 | 0 | 94.23% | PASS |
| citation | JSS-CITE-003 | 9 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 8 | 3 | 0 | 72.73% | FAIL |
| unknown | JSS-BIBTEX-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 36 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 157 | 12 | 0 | 92.90% | PASS |
| unknown | JSS-CAP-003 | 17 | 22 | 0 | 43.59% | FAIL |
| unknown | JSS-CAP-004 | 11 | 4 | 0 | 73.33% | FAIL |
| unknown | JSS-CODE-001 | 14 | 1 | 0 | 93.33% | PASS |
| unknown | JSS-CODE-003 | 113 | 7 | 0 | 94.17% | PASS |
| unknown | JSS-HOUSE-001 | 273 | 4 | 0 | 98.56% | PASS |
| unknown | JSS-HOUSE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 899 | 99 | 0 | 90.08% | PASS |
| unknown | JSS-MARKUP-002 | 249 | 20 | 0 | 92.57% | PASS |
| unknown | JSS-MARKUP-003 | 171 | 3 | 0 | 98.28% | PASS |
| unknown | JSS-MARKUP-004 | 107 | 4 | 0 | 96.40% | PASS |
| unknown | JSS-NAME-001 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 51 | 1 | 0 | 98.08% | PASS |
| unknown | JSS-OPER-001 | 60 | 1 | 0 | 98.36% | PASS |
| unknown | JSS-OPER-002 | 47 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 47 | 1 | 0 | 97.92% | PASS |
| unknown | JSS-PRE-001 | 62 | 1 | 0 | 98.41% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 21 | 4 | 0 | 84.00% | FAIL |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 948 | 58 | 0 | 94.23% | PASS |
| unknown | JSS-REFS-004 | 155 | 5 | 0 | 96.88% | PASS |
| unknown | JSS-REFS-005 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 152 | 5 | 0 | 96.82% | PASS |
| unknown | JSS-REFS-007 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 38 | 4 | 0 | 90.48% | PASS |
| unknown | JSS-STRUCT-002 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 47 | 7 | 0 | 87.04% | FAIL |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 7 | 0 | 77.42% | FAIL |
| unknown | JSS-WIDTH-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 20 | 3 | 0 | 86.96% | FAIL |
| unknown | JSS-XREF-002 | 154 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 143 | 3 | 0 | 97.95% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 46 | 8 | 0 | 85.19% | FAIL |
| citation | JSS-CITE-003 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 27 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 52 | 5 | 0 | 91.23% | PASS |
| unknown | JSS-CAP-003 | 12 | 15 | 0 | 44.44% | FAIL |
| unknown | JSS-CAP-004 | 10 | 3 | 0 | 76.92% | FAIL |
| unknown | JSS-CODE-001 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 63 | 3 | 0 | 95.45% | PASS |
| unknown | JSS-HOUSE-001 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 332 | 52 | 0 | 86.46% | FAIL |
| unknown | JSS-MARKUP-002 | 115 | 4 | 0 | 96.64% | PASS |
| unknown | JSS-MARKUP-003 | 17 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-004 | 26 | 1 | 0 | 96.30% | PASS |
| unknown | JSS-NAME-002 | 51 | 1 | 0 | 98.08% | PASS |
| unknown | JSS-OPER-001 | 14 | 1 | 0 | 93.33% | PASS |
| unknown | JSS-OPER-002 | 32 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 37 | 1 | 0 | 97.37% | PASS |
| unknown | JSS-PRE-001 | 17 | 1 | 0 | 94.44% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 10 | 4 | 0 | 71.43% | FAIL |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 948 | 58 | 0 | 94.23% | PASS |
| unknown | JSS-REFS-004 | 155 | 5 | 0 | 96.88% | PASS |
| unknown | JSS-REFS-005 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 152 | 5 | 0 | 96.82% | PASS |
| unknown | JSS-REFS-007 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 14 | 2 | 0 | 87.50% | FAIL |
| unknown | JSS-STRUCT-002 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 30 | 7 | 0 | 81.08% | FAIL |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 19 | 4 | 0 | 82.61% | FAIL |
| unknown | JSS-WIDTH-001 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 13 | 2 | 0 | 86.67% | FAIL |
| unknown | JSS-XREF-002 | 74 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 104 | 3 | 0 | 97.20% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-NAME-001`: tp +2→2 (+0), fp +1→0 (-1), pending 0→0 (+0)
- `JSS-REFS-001`: tp +2→1 (-1), fp +1→0 (-1), pending 0→0 (+0)

**Pinned only**

- `JSS-REFS-001`: tp +2→1 (-1), fp +1→0 (-1), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 41 — 2026-04-29T18:46:56Z — post-TYPO-001-skip-subfloat

- **Corpus size:** 112 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=28, pinned=24

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 147 | 9 | 0 | 94.23% | PASS |
| citation | JSS-CITE-003 | 9 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 8 | 3 | 0 | 72.73% | FAIL |
| unknown | JSS-BIBTEX-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 36 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 157 | 12 | 0 | 92.90% | PASS |
| unknown | JSS-CAP-003 | 17 | 22 | 0 | 43.59% | FAIL |
| unknown | JSS-CAP-004 | 11 | 4 | 0 | 73.33% | FAIL |
| unknown | JSS-CODE-001 | 14 | 1 | 0 | 93.33% | PASS |
| unknown | JSS-CODE-003 | 113 | 7 | 0 | 94.17% | PASS |
| unknown | JSS-HOUSE-001 | 273 | 4 | 0 | 98.56% | PASS |
| unknown | JSS-HOUSE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 899 | 99 | 0 | 90.08% | PASS |
| unknown | JSS-MARKUP-002 | 249 | 20 | 0 | 92.57% | PASS |
| unknown | JSS-MARKUP-003 | 171 | 3 | 0 | 98.28% | PASS |
| unknown | JSS-MARKUP-004 | 107 | 4 | 0 | 96.40% | PASS |
| unknown | JSS-NAME-001 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 51 | 1 | 0 | 98.08% | PASS |
| unknown | JSS-OPER-001 | 60 | 1 | 0 | 98.36% | PASS |
| unknown | JSS-OPER-002 | 47 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 47 | 1 | 0 | 97.92% | PASS |
| unknown | JSS-PRE-001 | 62 | 1 | 0 | 98.41% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 21 | 4 | 0 | 84.00% | FAIL |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 948 | 58 | 0 | 94.23% | PASS |
| unknown | JSS-REFS-004 | 155 | 5 | 0 | 96.88% | PASS |
| unknown | JSS-REFS-005 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 152 | 5 | 0 | 96.82% | PASS |
| unknown | JSS-REFS-007 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 38 | 4 | 0 | 90.48% | PASS |
| unknown | JSS-STRUCT-002 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 47 | 1 | 0 | 97.92% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 7 | 0 | 77.42% | FAIL |
| unknown | JSS-WIDTH-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 20 | 3 | 0 | 86.96% | FAIL |
| unknown | JSS-XREF-002 | 154 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 143 | 3 | 0 | 97.95% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 46 | 8 | 0 | 85.19% | FAIL |
| citation | JSS-CITE-003 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 27 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 52 | 5 | 0 | 91.23% | PASS |
| unknown | JSS-CAP-003 | 12 | 15 | 0 | 44.44% | FAIL |
| unknown | JSS-CAP-004 | 10 | 3 | 0 | 76.92% | FAIL |
| unknown | JSS-CODE-001 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 63 | 3 | 0 | 95.45% | PASS |
| unknown | JSS-HOUSE-001 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 332 | 52 | 0 | 86.46% | FAIL |
| unknown | JSS-MARKUP-002 | 115 | 4 | 0 | 96.64% | PASS |
| unknown | JSS-MARKUP-003 | 17 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-004 | 26 | 1 | 0 | 96.30% | PASS |
| unknown | JSS-NAME-002 | 51 | 1 | 0 | 98.08% | PASS |
| unknown | JSS-OPER-001 | 14 | 1 | 0 | 93.33% | PASS |
| unknown | JSS-OPER-002 | 32 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 37 | 1 | 0 | 97.37% | PASS |
| unknown | JSS-PRE-001 | 17 | 1 | 0 | 94.44% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 10 | 4 | 0 | 71.43% | FAIL |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 948 | 58 | 0 | 94.23% | PASS |
| unknown | JSS-REFS-004 | 155 | 5 | 0 | 96.88% | PASS |
| unknown | JSS-REFS-005 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 152 | 5 | 0 | 96.82% | PASS |
| unknown | JSS-REFS-007 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 14 | 2 | 0 | 87.50% | FAIL |
| unknown | JSS-STRUCT-002 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 30 | 1 | 0 | 96.77% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 19 | 4 | 0 | 82.61% | FAIL |
| unknown | JSS-WIDTH-001 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 13 | 2 | 0 | 86.67% | FAIL |
| unknown | JSS-XREF-002 | 74 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 104 | 3 | 0 | 97.20% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-TYPO-001`: tp +47→47 (+0), fp +7→1 (-6), pending 0→0 (+0)

**Pinned only**

- `JSS-TYPO-001`: tp +30→30 (+0), fp +7→1 (-6), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 42 — 2026-04-29T18:50:56Z — post-ABBR-001-surname-trailing-initials

- **Corpus size:** 112 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=28, pinned=24

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 147 | 9 | 0 | 94.23% | PASS |
| citation | JSS-CITE-003 | 9 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 36 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 157 | 12 | 0 | 92.90% | PASS |
| unknown | JSS-CAP-003 | 17 | 22 | 0 | 43.59% | FAIL |
| unknown | JSS-CAP-004 | 11 | 4 | 0 | 73.33% | FAIL |
| unknown | JSS-CODE-001 | 14 | 1 | 0 | 93.33% | PASS |
| unknown | JSS-CODE-003 | 113 | 7 | 0 | 94.17% | PASS |
| unknown | JSS-HOUSE-001 | 273 | 4 | 0 | 98.56% | PASS |
| unknown | JSS-HOUSE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 899 | 99 | 0 | 90.08% | PASS |
| unknown | JSS-MARKUP-002 | 249 | 20 | 0 | 92.57% | PASS |
| unknown | JSS-MARKUP-003 | 171 | 3 | 0 | 98.28% | PASS |
| unknown | JSS-MARKUP-004 | 107 | 4 | 0 | 96.40% | PASS |
| unknown | JSS-NAME-001 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 51 | 1 | 0 | 98.08% | PASS |
| unknown | JSS-OPER-001 | 60 | 1 | 0 | 98.36% | PASS |
| unknown | JSS-OPER-002 | 47 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 47 | 1 | 0 | 97.92% | PASS |
| unknown | JSS-PRE-001 | 62 | 1 | 0 | 98.41% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 21 | 4 | 0 | 84.00% | FAIL |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 948 | 58 | 0 | 94.23% | PASS |
| unknown | JSS-REFS-004 | 155 | 5 | 0 | 96.88% | PASS |
| unknown | JSS-REFS-005 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 152 | 5 | 0 | 96.82% | PASS |
| unknown | JSS-REFS-007 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 38 | 4 | 0 | 90.48% | PASS |
| unknown | JSS-STRUCT-002 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 47 | 1 | 0 | 97.92% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 7 | 0 | 77.42% | FAIL |
| unknown | JSS-WIDTH-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 20 | 3 | 0 | 86.96% | FAIL |
| unknown | JSS-XREF-002 | 154 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 143 | 3 | 0 | 97.95% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 46 | 8 | 0 | 85.19% | FAIL |
| citation | JSS-CITE-003 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 27 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 52 | 5 | 0 | 91.23% | PASS |
| unknown | JSS-CAP-003 | 12 | 15 | 0 | 44.44% | FAIL |
| unknown | JSS-CAP-004 | 10 | 3 | 0 | 76.92% | FAIL |
| unknown | JSS-CODE-001 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 63 | 3 | 0 | 95.45% | PASS |
| unknown | JSS-HOUSE-001 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 332 | 52 | 0 | 86.46% | FAIL |
| unknown | JSS-MARKUP-002 | 115 | 4 | 0 | 96.64% | PASS |
| unknown | JSS-MARKUP-003 | 17 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-004 | 26 | 1 | 0 | 96.30% | PASS |
| unknown | JSS-NAME-002 | 51 | 1 | 0 | 98.08% | PASS |
| unknown | JSS-OPER-001 | 14 | 1 | 0 | 93.33% | PASS |
| unknown | JSS-OPER-002 | 32 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 37 | 1 | 0 | 97.37% | PASS |
| unknown | JSS-PRE-001 | 17 | 1 | 0 | 94.44% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 10 | 4 | 0 | 71.43% | FAIL |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 948 | 58 | 0 | 94.23% | PASS |
| unknown | JSS-REFS-004 | 155 | 5 | 0 | 96.88% | PASS |
| unknown | JSS-REFS-005 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 152 | 5 | 0 | 96.82% | PASS |
| unknown | JSS-REFS-007 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 14 | 2 | 0 | 87.50% | FAIL |
| unknown | JSS-STRUCT-002 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 30 | 1 | 0 | 96.77% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 19 | 4 | 0 | 82.61% | FAIL |
| unknown | JSS-WIDTH-001 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 13 | 2 | 0 | 86.67% | FAIL |
| unknown | JSS-XREF-002 | 74 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 104 | 3 | 0 | 97.20% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-ABBR-001`: tp +8→6 (-2), fp +3→0 (-3), pending 0→0 (+0)

**Pinned only**

_(no rule-level changes)_

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 43 — 2026-04-29T18:55:15Z — post-MARKUP-001-skip-single-letter-in-bib

- **Corpus size:** 112 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=28, pinned=24

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 147 | 9 | 0 | 94.23% | PASS |
| citation | JSS-CITE-003 | 9 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 36 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 157 | 12 | 0 | 92.90% | PASS |
| unknown | JSS-CAP-003 | 17 | 22 | 0 | 43.59% | FAIL |
| unknown | JSS-CAP-004 | 11 | 4 | 0 | 73.33% | FAIL |
| unknown | JSS-CODE-001 | 14 | 1 | 0 | 93.33% | PASS |
| unknown | JSS-CODE-003 | 113 | 7 | 0 | 94.17% | PASS |
| unknown | JSS-HOUSE-001 | 273 | 4 | 0 | 98.56% | PASS |
| unknown | JSS-HOUSE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 893 | 85 | 0 | 91.31% | PASS |
| unknown | JSS-MARKUP-002 | 249 | 20 | 0 | 92.57% | PASS |
| unknown | JSS-MARKUP-003 | 171 | 3 | 0 | 98.28% | PASS |
| unknown | JSS-MARKUP-004 | 107 | 4 | 0 | 96.40% | PASS |
| unknown | JSS-NAME-001 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 51 | 1 | 0 | 98.08% | PASS |
| unknown | JSS-OPER-001 | 60 | 1 | 0 | 98.36% | PASS |
| unknown | JSS-OPER-002 | 47 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 47 | 1 | 0 | 97.92% | PASS |
| unknown | JSS-PRE-001 | 62 | 1 | 0 | 98.41% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 21 | 4 | 0 | 84.00% | FAIL |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 948 | 58 | 0 | 94.23% | PASS |
| unknown | JSS-REFS-004 | 155 | 5 | 0 | 96.88% | PASS |
| unknown | JSS-REFS-005 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 152 | 5 | 0 | 96.82% | PASS |
| unknown | JSS-REFS-007 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 38 | 4 | 0 | 90.48% | PASS |
| unknown | JSS-STRUCT-002 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 47 | 1 | 0 | 97.92% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 7 | 0 | 77.42% | FAIL |
| unknown | JSS-WIDTH-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 20 | 3 | 0 | 86.96% | FAIL |
| unknown | JSS-XREF-002 | 154 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 143 | 3 | 0 | 97.95% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 46 | 8 | 0 | 85.19% | FAIL |
| citation | JSS-CITE-003 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 27 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 52 | 5 | 0 | 91.23% | PASS |
| unknown | JSS-CAP-003 | 12 | 15 | 0 | 44.44% | FAIL |
| unknown | JSS-CAP-004 | 10 | 3 | 0 | 76.92% | FAIL |
| unknown | JSS-CODE-001 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 63 | 3 | 0 | 95.45% | PASS |
| unknown | JSS-HOUSE-001 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 326 | 38 | 0 | 89.56% | FAIL |
| unknown | JSS-MARKUP-002 | 115 | 4 | 0 | 96.64% | PASS |
| unknown | JSS-MARKUP-003 | 17 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-004 | 26 | 1 | 0 | 96.30% | PASS |
| unknown | JSS-NAME-002 | 51 | 1 | 0 | 98.08% | PASS |
| unknown | JSS-OPER-001 | 14 | 1 | 0 | 93.33% | PASS |
| unknown | JSS-OPER-002 | 32 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 37 | 1 | 0 | 97.37% | PASS |
| unknown | JSS-PRE-001 | 17 | 1 | 0 | 94.44% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 10 | 4 | 0 | 71.43% | FAIL |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 948 | 58 | 0 | 94.23% | PASS |
| unknown | JSS-REFS-004 | 155 | 5 | 0 | 96.88% | PASS |
| unknown | JSS-REFS-005 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 152 | 5 | 0 | 96.82% | PASS |
| unknown | JSS-REFS-007 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 14 | 2 | 0 | 87.50% | FAIL |
| unknown | JSS-STRUCT-002 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 30 | 1 | 0 | 96.77% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 19 | 4 | 0 | 82.61% | FAIL |
| unknown | JSS-WIDTH-001 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 13 | 2 | 0 | 86.67% | FAIL |
| unknown | JSS-XREF-002 | 74 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 104 | 3 | 0 | 97.20% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-MARKUP-001`: tp +899→893 (-6), fp +99→85 (-14), pending 0→0 (+0)

**Pinned only**

- `JSS-MARKUP-001`: tp +332→326 (-6), fp +52→38 (-14), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 44 — 2026-04-29T19:06:48Z — post-STRUCT-001-extended-backmatter

- **Corpus size:** 112 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=28, pinned=24

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 147 | 9 | 0 | 94.23% | PASS |
| citation | JSS-CITE-003 | 9 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 36 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 157 | 12 | 0 | 92.90% | PASS |
| unknown | JSS-CAP-003 | 17 | 22 | 0 | 43.59% | FAIL |
| unknown | JSS-CAP-004 | 11 | 4 | 0 | 73.33% | FAIL |
| unknown | JSS-CODE-001 | 14 | 1 | 0 | 93.33% | PASS |
| unknown | JSS-CODE-003 | 113 | 7 | 0 | 94.17% | PASS |
| unknown | JSS-HOUSE-001 | 273 | 4 | 0 | 98.56% | PASS |
| unknown | JSS-HOUSE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 893 | 85 | 0 | 91.31% | PASS |
| unknown | JSS-MARKUP-002 | 249 | 20 | 0 | 92.57% | PASS |
| unknown | JSS-MARKUP-003 | 171 | 3 | 0 | 98.28% | PASS |
| unknown | JSS-MARKUP-004 | 107 | 4 | 0 | 96.40% | PASS |
| unknown | JSS-NAME-001 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 51 | 1 | 0 | 98.08% | PASS |
| unknown | JSS-OPER-001 | 60 | 1 | 0 | 98.36% | PASS |
| unknown | JSS-OPER-002 | 47 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 47 | 1 | 0 | 97.92% | PASS |
| unknown | JSS-PRE-001 | 62 | 1 | 0 | 98.41% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 21 | 4 | 0 | 84.00% | FAIL |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 948 | 58 | 0 | 94.23% | PASS |
| unknown | JSS-REFS-004 | 155 | 5 | 0 | 96.88% | PASS |
| unknown | JSS-REFS-005 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 152 | 5 | 0 | 96.82% | PASS |
| unknown | JSS-REFS-007 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 38 | 2 | 0 | 95.00% | PASS |
| unknown | JSS-STRUCT-002 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 47 | 1 | 0 | 97.92% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 7 | 0 | 77.42% | FAIL |
| unknown | JSS-WIDTH-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 20 | 3 | 0 | 86.96% | FAIL |
| unknown | JSS-XREF-002 | 154 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 143 | 3 | 0 | 97.95% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 46 | 8 | 0 | 85.19% | FAIL |
| citation | JSS-CITE-003 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 27 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 52 | 5 | 0 | 91.23% | PASS |
| unknown | JSS-CAP-003 | 12 | 15 | 0 | 44.44% | FAIL |
| unknown | JSS-CAP-004 | 10 | 3 | 0 | 76.92% | FAIL |
| unknown | JSS-CODE-001 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 63 | 3 | 0 | 95.45% | PASS |
| unknown | JSS-HOUSE-001 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 326 | 38 | 0 | 89.56% | FAIL |
| unknown | JSS-MARKUP-002 | 115 | 4 | 0 | 96.64% | PASS |
| unknown | JSS-MARKUP-003 | 17 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-004 | 26 | 1 | 0 | 96.30% | PASS |
| unknown | JSS-NAME-002 | 51 | 1 | 0 | 98.08% | PASS |
| unknown | JSS-OPER-001 | 14 | 1 | 0 | 93.33% | PASS |
| unknown | JSS-OPER-002 | 32 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 37 | 1 | 0 | 97.37% | PASS |
| unknown | JSS-PRE-001 | 17 | 1 | 0 | 94.44% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 10 | 4 | 0 | 71.43% | FAIL |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 948 | 58 | 0 | 94.23% | PASS |
| unknown | JSS-REFS-004 | 155 | 5 | 0 | 96.88% | PASS |
| unknown | JSS-REFS-005 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 152 | 5 | 0 | 96.82% | PASS |
| unknown | JSS-REFS-007 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-002 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 30 | 1 | 0 | 96.77% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 19 | 4 | 0 | 82.61% | FAIL |
| unknown | JSS-WIDTH-001 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 13 | 2 | 0 | 86.67% | FAIL |
| unknown | JSS-XREF-002 | 74 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 104 | 3 | 0 | 97.20% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-STRUCT-001`: tp +38→38 (+0), fp +4→2 (-2), pending 0→0 (+0)

**Pinned only**

- `JSS-STRUCT-001`: tp +14→14 (+0), fp +2→0 (-2), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 45 — 2026-04-29T19:10:06Z — post-HOUSE-001-flip-ai-mislabels

- **Corpus size:** 112 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=28, pinned=24

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 147 | 9 | 0 | 94.23% | PASS |
| citation | JSS-CITE-003 | 9 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 36 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 157 | 12 | 0 | 92.90% | PASS |
| unknown | JSS-CAP-003 | 17 | 22 | 0 | 43.59% | FAIL |
| unknown | JSS-CAP-004 | 11 | 4 | 0 | 73.33% | FAIL |
| unknown | JSS-CODE-001 | 14 | 1 | 0 | 93.33% | PASS |
| unknown | JSS-CODE-003 | 113 | 7 | 0 | 94.17% | PASS |
| unknown | JSS-HOUSE-001 | 277 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 893 | 85 | 0 | 91.31% | PASS |
| unknown | JSS-MARKUP-002 | 249 | 20 | 0 | 92.57% | PASS |
| unknown | JSS-MARKUP-003 | 171 | 3 | 0 | 98.28% | PASS |
| unknown | JSS-MARKUP-004 | 107 | 4 | 0 | 96.40% | PASS |
| unknown | JSS-NAME-001 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 51 | 1 | 0 | 98.08% | PASS |
| unknown | JSS-OPER-001 | 60 | 1 | 0 | 98.36% | PASS |
| unknown | JSS-OPER-002 | 47 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 47 | 1 | 0 | 97.92% | PASS |
| unknown | JSS-PRE-001 | 62 | 1 | 0 | 98.41% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 21 | 4 | 0 | 84.00% | FAIL |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 948 | 58 | 0 | 94.23% | PASS |
| unknown | JSS-REFS-004 | 155 | 5 | 0 | 96.88% | PASS |
| unknown | JSS-REFS-005 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 152 | 5 | 0 | 96.82% | PASS |
| unknown | JSS-REFS-007 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 38 | 2 | 0 | 95.00% | PASS |
| unknown | JSS-STRUCT-002 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 47 | 1 | 0 | 97.92% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 7 | 0 | 77.42% | FAIL |
| unknown | JSS-WIDTH-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 20 | 3 | 0 | 86.96% | FAIL |
| unknown | JSS-XREF-002 | 154 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 143 | 3 | 0 | 97.95% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 46 | 8 | 0 | 85.19% | FAIL |
| citation | JSS-CITE-003 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 27 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 52 | 5 | 0 | 91.23% | PASS |
| unknown | JSS-CAP-003 | 12 | 15 | 0 | 44.44% | FAIL |
| unknown | JSS-CAP-004 | 10 | 3 | 0 | 76.92% | FAIL |
| unknown | JSS-CODE-001 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 63 | 3 | 0 | 95.45% | PASS |
| unknown | JSS-HOUSE-001 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 326 | 38 | 0 | 89.56% | FAIL |
| unknown | JSS-MARKUP-002 | 115 | 4 | 0 | 96.64% | PASS |
| unknown | JSS-MARKUP-003 | 17 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-004 | 26 | 1 | 0 | 96.30% | PASS |
| unknown | JSS-NAME-002 | 51 | 1 | 0 | 98.08% | PASS |
| unknown | JSS-OPER-001 | 14 | 1 | 0 | 93.33% | PASS |
| unknown | JSS-OPER-002 | 32 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 37 | 1 | 0 | 97.37% | PASS |
| unknown | JSS-PRE-001 | 17 | 1 | 0 | 94.44% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 10 | 4 | 0 | 71.43% | FAIL |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 948 | 58 | 0 | 94.23% | PASS |
| unknown | JSS-REFS-004 | 155 | 5 | 0 | 96.88% | PASS |
| unknown | JSS-REFS-005 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 152 | 5 | 0 | 96.82% | PASS |
| unknown | JSS-REFS-007 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-002 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 30 | 1 | 0 | 96.77% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 19 | 4 | 0 | 82.61% | FAIL |
| unknown | JSS-WIDTH-001 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 13 | 2 | 0 | 86.67% | FAIL |
| unknown | JSS-XREF-002 | 74 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 104 | 3 | 0 | 97.20% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-HOUSE-001`: tp +273→277 (+4), fp +4→0 (-4), pending 0→0 (+0)

**Pinned only**

_(no rule-level changes)_

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 46 — 2026-04-29T19:16:54Z — post-REFS-004-bibtex-case-protection

- **Corpus size:** 112 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=28, pinned=24

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 147 | 9 | 0 | 94.23% | PASS |
| citation | JSS-CITE-003 | 9 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 36 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 157 | 12 | 0 | 92.90% | PASS |
| unknown | JSS-CAP-003 | 17 | 22 | 0 | 43.59% | FAIL |
| unknown | JSS-CAP-004 | 11 | 4 | 0 | 73.33% | FAIL |
| unknown | JSS-CODE-001 | 14 | 1 | 0 | 93.33% | PASS |
| unknown | JSS-CODE-003 | 113 | 7 | 0 | 94.17% | PASS |
| unknown | JSS-HOUSE-001 | 277 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 893 | 85 | 0 | 91.31% | PASS |
| unknown | JSS-MARKUP-002 | 249 | 20 | 0 | 92.57% | PASS |
| unknown | JSS-MARKUP-003 | 171 | 3 | 0 | 98.28% | PASS |
| unknown | JSS-MARKUP-004 | 107 | 4 | 0 | 96.40% | PASS |
| unknown | JSS-NAME-001 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 51 | 1 | 0 | 98.08% | PASS |
| unknown | JSS-OPER-001 | 60 | 1 | 0 | 98.36% | PASS |
| unknown | JSS-OPER-002 | 47 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 47 | 1 | 0 | 97.92% | PASS |
| unknown | JSS-PRE-001 | 62 | 1 | 0 | 98.41% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 21 | 4 | 0 | 84.00% | FAIL |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 948 | 58 | 0 | 94.23% | PASS |
| unknown | JSS-REFS-004 | 143 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 152 | 5 | 0 | 96.82% | PASS |
| unknown | JSS-REFS-007 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 38 | 2 | 0 | 95.00% | PASS |
| unknown | JSS-STRUCT-002 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 47 | 1 | 0 | 97.92% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 7 | 0 | 77.42% | FAIL |
| unknown | JSS-WIDTH-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 20 | 3 | 0 | 86.96% | FAIL |
| unknown | JSS-XREF-002 | 154 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 143 | 3 | 0 | 97.95% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 46 | 8 | 0 | 85.19% | FAIL |
| citation | JSS-CITE-003 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 27 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 52 | 5 | 0 | 91.23% | PASS |
| unknown | JSS-CAP-003 | 12 | 15 | 0 | 44.44% | FAIL |
| unknown | JSS-CAP-004 | 10 | 3 | 0 | 76.92% | FAIL |
| unknown | JSS-CODE-001 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 63 | 3 | 0 | 95.45% | PASS |
| unknown | JSS-HOUSE-001 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 326 | 38 | 0 | 89.56% | FAIL |
| unknown | JSS-MARKUP-002 | 115 | 4 | 0 | 96.64% | PASS |
| unknown | JSS-MARKUP-003 | 17 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-004 | 26 | 1 | 0 | 96.30% | PASS |
| unknown | JSS-NAME-002 | 51 | 1 | 0 | 98.08% | PASS |
| unknown | JSS-OPER-001 | 14 | 1 | 0 | 93.33% | PASS |
| unknown | JSS-OPER-002 | 32 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 37 | 1 | 0 | 97.37% | PASS |
| unknown | JSS-PRE-001 | 17 | 1 | 0 | 94.44% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 10 | 4 | 0 | 71.43% | FAIL |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 948 | 58 | 0 | 94.23% | PASS |
| unknown | JSS-REFS-004 | 143 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 152 | 5 | 0 | 96.82% | PASS |
| unknown | JSS-REFS-007 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-002 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 30 | 1 | 0 | 96.77% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 19 | 4 | 0 | 82.61% | FAIL |
| unknown | JSS-WIDTH-001 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 13 | 2 | 0 | 86.67% | FAIL |
| unknown | JSS-XREF-002 | 74 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 104 | 3 | 0 | 97.20% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-REFS-004`: tp +155→143 (-12), fp +5→0 (-5), pending 0→0 (+0)

**Pinned only**

- `JSS-REFS-004`: tp +155→143 (-12), fp +5→0 (-5), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 47 — 2026-04-29T19:25:32Z — post-XREF-001-cross-paper-extras

- **Corpus size:** 112 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=28, pinned=24

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 147 | 9 | 0 | 94.23% | PASS |
| citation | JSS-CITE-003 | 9 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 36 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 157 | 12 | 0 | 92.90% | PASS |
| unknown | JSS-CAP-003 | 17 | 22 | 0 | 43.59% | FAIL |
| unknown | JSS-CAP-004 | 11 | 4 | 0 | 73.33% | FAIL |
| unknown | JSS-CODE-001 | 14 | 1 | 0 | 93.33% | PASS |
| unknown | JSS-CODE-003 | 113 | 7 | 0 | 94.17% | PASS |
| unknown | JSS-HOUSE-001 | 277 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 893 | 85 | 0 | 91.31% | PASS |
| unknown | JSS-MARKUP-002 | 249 | 20 | 0 | 92.57% | PASS |
| unknown | JSS-MARKUP-003 | 171 | 3 | 0 | 98.28% | PASS |
| unknown | JSS-MARKUP-004 | 107 | 4 | 0 | 96.40% | PASS |
| unknown | JSS-NAME-001 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 51 | 1 | 0 | 98.08% | PASS |
| unknown | JSS-OPER-001 | 60 | 1 | 0 | 98.36% | PASS |
| unknown | JSS-OPER-002 | 47 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 47 | 1 | 0 | 97.92% | PASS |
| unknown | JSS-PRE-001 | 62 | 1 | 0 | 98.41% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 21 | 4 | 0 | 84.00% | FAIL |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 948 | 58 | 0 | 94.23% | PASS |
| unknown | JSS-REFS-004 | 143 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 152 | 5 | 0 | 96.82% | PASS |
| unknown | JSS-REFS-007 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 38 | 2 | 0 | 95.00% | PASS |
| unknown | JSS-STRUCT-002 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 47 | 1 | 0 | 97.92% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 7 | 0 | 77.42% | FAIL |
| unknown | JSS-WIDTH-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 154 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 143 | 3 | 0 | 97.95% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 46 | 8 | 0 | 85.19% | FAIL |
| citation | JSS-CITE-003 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 27 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 52 | 5 | 0 | 91.23% | PASS |
| unknown | JSS-CAP-003 | 12 | 15 | 0 | 44.44% | FAIL |
| unknown | JSS-CAP-004 | 10 | 3 | 0 | 76.92% | FAIL |
| unknown | JSS-CODE-001 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 63 | 3 | 0 | 95.45% | PASS |
| unknown | JSS-HOUSE-001 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 326 | 38 | 0 | 89.56% | FAIL |
| unknown | JSS-MARKUP-002 | 115 | 4 | 0 | 96.64% | PASS |
| unknown | JSS-MARKUP-003 | 17 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-004 | 26 | 1 | 0 | 96.30% | PASS |
| unknown | JSS-NAME-002 | 51 | 1 | 0 | 98.08% | PASS |
| unknown | JSS-OPER-001 | 14 | 1 | 0 | 93.33% | PASS |
| unknown | JSS-OPER-002 | 32 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 37 | 1 | 0 | 97.37% | PASS |
| unknown | JSS-PRE-001 | 17 | 1 | 0 | 94.44% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 10 | 4 | 0 | 71.43% | FAIL |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 948 | 58 | 0 | 94.23% | PASS |
| unknown | JSS-REFS-004 | 143 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 152 | 5 | 0 | 96.82% | PASS |
| unknown | JSS-REFS-007 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-002 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 30 | 1 | 0 | 96.77% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 19 | 4 | 0 | 82.61% | FAIL |
| unknown | JSS-WIDTH-001 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 74 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 104 | 3 | 0 | 97.20% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-XREF-001`: tp +20→20 (+0), fp +3→0 (-3), pending 0→0 (+0)

**Pinned only**

- `JSS-XREF-001`: tp +13→13 (+0), fp +2→0 (-2), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 48 — 2026-04-29T19:29:07Z — post-CODE-001-comment-marker

- **Corpus size:** 112 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=28, pinned=24

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 147 | 9 | 0 | 94.23% | PASS |
| citation | JSS-CITE-003 | 9 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 36 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 157 | 12 | 0 | 92.90% | PASS |
| unknown | JSS-CAP-003 | 17 | 22 | 0 | 43.59% | FAIL |
| unknown | JSS-CAP-004 | 11 | 4 | 0 | 73.33% | FAIL |
| unknown | JSS-CODE-001 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 113 | 7 | 0 | 94.17% | PASS |
| unknown | JSS-HOUSE-001 | 277 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 893 | 85 | 0 | 91.31% | PASS |
| unknown | JSS-MARKUP-002 | 249 | 20 | 0 | 92.57% | PASS |
| unknown | JSS-MARKUP-003 | 171 | 3 | 0 | 98.28% | PASS |
| unknown | JSS-MARKUP-004 | 107 | 4 | 0 | 96.40% | PASS |
| unknown | JSS-NAME-001 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 51 | 1 | 0 | 98.08% | PASS |
| unknown | JSS-OPER-001 | 60 | 1 | 0 | 98.36% | PASS |
| unknown | JSS-OPER-002 | 47 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 47 | 1 | 0 | 97.92% | PASS |
| unknown | JSS-PRE-001 | 62 | 1 | 0 | 98.41% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 21 | 4 | 0 | 84.00% | FAIL |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 948 | 58 | 0 | 94.23% | PASS |
| unknown | JSS-REFS-004 | 143 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 152 | 5 | 0 | 96.82% | PASS |
| unknown | JSS-REFS-007 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 38 | 2 | 0 | 95.00% | PASS |
| unknown | JSS-STRUCT-002 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 47 | 1 | 0 | 97.92% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 7 | 0 | 77.42% | FAIL |
| unknown | JSS-WIDTH-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 154 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 143 | 3 | 0 | 97.95% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 46 | 8 | 0 | 85.19% | FAIL |
| citation | JSS-CITE-003 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 27 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 52 | 5 | 0 | 91.23% | PASS |
| unknown | JSS-CAP-003 | 12 | 15 | 0 | 44.44% | FAIL |
| unknown | JSS-CAP-004 | 10 | 3 | 0 | 76.92% | FAIL |
| unknown | JSS-CODE-001 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 63 | 3 | 0 | 95.45% | PASS |
| unknown | JSS-HOUSE-001 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 326 | 38 | 0 | 89.56% | FAIL |
| unknown | JSS-MARKUP-002 | 115 | 4 | 0 | 96.64% | PASS |
| unknown | JSS-MARKUP-003 | 17 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-004 | 26 | 1 | 0 | 96.30% | PASS |
| unknown | JSS-NAME-002 | 51 | 1 | 0 | 98.08% | PASS |
| unknown | JSS-OPER-001 | 14 | 1 | 0 | 93.33% | PASS |
| unknown | JSS-OPER-002 | 32 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 37 | 1 | 0 | 97.37% | PASS |
| unknown | JSS-PRE-001 | 17 | 1 | 0 | 94.44% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 10 | 4 | 0 | 71.43% | FAIL |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 948 | 58 | 0 | 94.23% | PASS |
| unknown | JSS-REFS-004 | 143 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 152 | 5 | 0 | 96.82% | PASS |
| unknown | JSS-REFS-007 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-002 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 30 | 1 | 0 | 96.77% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 19 | 4 | 0 | 82.61% | FAIL |
| unknown | JSS-WIDTH-001 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 74 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 104 | 3 | 0 | 97.20% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-CODE-001`: tp +14→14 (+0), fp +1→0 (-1), pending 0→0 (+0)

**Pinned only**

_(no rule-level changes)_

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 49 — 2026-04-29T19:32:48Z — post-OPER-001-md-link

- **Corpus size:** 112 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=28, pinned=24

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 147 | 9 | 0 | 94.23% | PASS |
| citation | JSS-CITE-003 | 9 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 36 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 157 | 12 | 0 | 92.90% | PASS |
| unknown | JSS-CAP-003 | 17 | 22 | 0 | 43.59% | FAIL |
| unknown | JSS-CAP-004 | 11 | 4 | 0 | 73.33% | FAIL |
| unknown | JSS-CODE-001 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 113 | 7 | 0 | 94.17% | PASS |
| unknown | JSS-HOUSE-001 | 277 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 893 | 85 | 0 | 91.31% | PASS |
| unknown | JSS-MARKUP-002 | 249 | 20 | 0 | 92.57% | PASS |
| unknown | JSS-MARKUP-003 | 171 | 3 | 0 | 98.28% | PASS |
| unknown | JSS-MARKUP-004 | 107 | 4 | 0 | 96.40% | PASS |
| unknown | JSS-NAME-001 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 51 | 1 | 0 | 98.08% | PASS |
| unknown | JSS-OPER-001 | 60 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-002 | 47 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 47 | 1 | 0 | 97.92% | PASS |
| unknown | JSS-PRE-001 | 62 | 1 | 0 | 98.41% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 21 | 4 | 0 | 84.00% | FAIL |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 948 | 58 | 0 | 94.23% | PASS |
| unknown | JSS-REFS-004 | 143 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 152 | 5 | 0 | 96.82% | PASS |
| unknown | JSS-REFS-007 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 38 | 2 | 0 | 95.00% | PASS |
| unknown | JSS-STRUCT-002 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 47 | 1 | 0 | 97.92% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 7 | 0 | 77.42% | FAIL |
| unknown | JSS-WIDTH-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 154 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 143 | 3 | 0 | 97.95% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 46 | 8 | 0 | 85.19% | FAIL |
| citation | JSS-CITE-003 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 27 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 52 | 5 | 0 | 91.23% | PASS |
| unknown | JSS-CAP-003 | 12 | 15 | 0 | 44.44% | FAIL |
| unknown | JSS-CAP-004 | 10 | 3 | 0 | 76.92% | FAIL |
| unknown | JSS-CODE-001 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 63 | 3 | 0 | 95.45% | PASS |
| unknown | JSS-HOUSE-001 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 326 | 38 | 0 | 89.56% | FAIL |
| unknown | JSS-MARKUP-002 | 115 | 4 | 0 | 96.64% | PASS |
| unknown | JSS-MARKUP-003 | 17 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-004 | 26 | 1 | 0 | 96.30% | PASS |
| unknown | JSS-NAME-002 | 51 | 1 | 0 | 98.08% | PASS |
| unknown | JSS-OPER-001 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-002 | 32 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 37 | 1 | 0 | 97.37% | PASS |
| unknown | JSS-PRE-001 | 17 | 1 | 0 | 94.44% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 10 | 4 | 0 | 71.43% | FAIL |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 948 | 58 | 0 | 94.23% | PASS |
| unknown | JSS-REFS-004 | 143 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 152 | 5 | 0 | 96.82% | PASS |
| unknown | JSS-REFS-007 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-002 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 30 | 1 | 0 | 96.77% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 19 | 4 | 0 | 82.61% | FAIL |
| unknown | JSS-WIDTH-001 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 74 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 104 | 3 | 0 | 97.20% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-OPER-001`: tp +60→60 (+0), fp +1→0 (-1), pending 0→0 (+0)

**Pinned only**

- `JSS-OPER-001`: tp +14→14 (+0), fp +1→0 (-1), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 50 — 2026-04-29T19:36:16Z — post-PRE-001-options-and-flips

- **Corpus size:** 112 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=28, pinned=24

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 147 | 9 | 0 | 94.23% | PASS |
| citation | JSS-CITE-003 | 9 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 36 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 157 | 12 | 0 | 92.90% | PASS |
| unknown | JSS-CAP-003 | 17 | 22 | 0 | 43.59% | FAIL |
| unknown | JSS-CAP-004 | 11 | 4 | 0 | 73.33% | FAIL |
| unknown | JSS-CODE-001 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 113 | 7 | 0 | 94.17% | PASS |
| unknown | JSS-HOUSE-001 | 277 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 893 | 85 | 0 | 91.31% | PASS |
| unknown | JSS-MARKUP-002 | 249 | 20 | 0 | 92.57% | PASS |
| unknown | JSS-MARKUP-003 | 171 | 3 | 0 | 98.28% | PASS |
| unknown | JSS-MARKUP-004 | 107 | 4 | 0 | 96.40% | PASS |
| unknown | JSS-NAME-001 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 51 | 1 | 0 | 98.08% | PASS |
| unknown | JSS-OPER-001 | 60 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-002 | 47 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 47 | 1 | 0 | 97.92% | PASS |
| unknown | JSS-PRE-001 | 47 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 21 | 4 | 0 | 84.00% | FAIL |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 948 | 58 | 0 | 94.23% | PASS |
| unknown | JSS-REFS-004 | 143 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 152 | 5 | 0 | 96.82% | PASS |
| unknown | JSS-REFS-007 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 39 | 1 | 0 | 97.50% | PASS |
| unknown | JSS-STRUCT-002 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 48 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 7 | 0 | 77.42% | FAIL |
| unknown | JSS-WIDTH-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 154 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 143 | 3 | 0 | 97.95% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 46 | 8 | 0 | 85.19% | FAIL |
| citation | JSS-CITE-003 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 27 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 52 | 5 | 0 | 91.23% | PASS |
| unknown | JSS-CAP-003 | 12 | 15 | 0 | 44.44% | FAIL |
| unknown | JSS-CAP-004 | 10 | 3 | 0 | 76.92% | FAIL |
| unknown | JSS-CODE-001 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 63 | 3 | 0 | 95.45% | PASS |
| unknown | JSS-HOUSE-001 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 326 | 38 | 0 | 89.56% | FAIL |
| unknown | JSS-MARKUP-002 | 115 | 4 | 0 | 96.64% | PASS |
| unknown | JSS-MARKUP-003 | 17 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-004 | 26 | 1 | 0 | 96.30% | PASS |
| unknown | JSS-NAME-002 | 51 | 1 | 0 | 98.08% | PASS |
| unknown | JSS-OPER-001 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-002 | 32 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 37 | 1 | 0 | 97.37% | PASS |
| unknown | JSS-PRE-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 10 | 4 | 0 | 71.43% | FAIL |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 948 | 58 | 0 | 94.23% | PASS |
| unknown | JSS-REFS-004 | 143 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 152 | 5 | 0 | 96.82% | PASS |
| unknown | JSS-REFS-007 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-002 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 31 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 19 | 4 | 0 | 82.61% | FAIL |
| unknown | JSS-WIDTH-001 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 74 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 104 | 3 | 0 | 97.20% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-PRE-001`: tp +62→47 (-15), fp +1→0 (-1), pending 0→0 (+0)
- `JSS-STRUCT-001`: tp +38→39 (+1), fp +2→1 (-1), pending 0→0 (+0)
- `JSS-TYPO-001`: tp +47→48 (+1), fp +1→0 (-1), pending 0→0 (+0)

**Pinned only**

- `JSS-PRE-001`: tp +17→13 (-4), fp +1→0 (-1), pending 0→0 (+0)
- `JSS-TYPO-001`: tp +30→31 (+1), fp +1→0 (-1), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 51 — 2026-04-29T19:42:08Z — post-MARKUP-XREF004-customs

- **Corpus size:** 112 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=28, pinned=24

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 147 | 9 | 0 | 94.23% | PASS |
| citation | JSS-CITE-003 | 9 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 36 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 157 | 12 | 0 | 92.90% | PASS |
| unknown | JSS-CAP-003 | 17 | 22 | 0 | 43.59% | FAIL |
| unknown | JSS-CAP-004 | 11 | 4 | 0 | 73.33% | FAIL |
| unknown | JSS-CODE-001 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 113 | 7 | 0 | 94.17% | PASS |
| unknown | JSS-HOUSE-001 | 277 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 893 | 85 | 0 | 91.31% | PASS |
| unknown | JSS-MARKUP-002 | 248 | 20 | 0 | 92.54% | PASS |
| unknown | JSS-MARKUP-003 | 152 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-004 | 111 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-001 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 51 | 1 | 0 | 98.08% | PASS |
| unknown | JSS-OPER-001 | 60 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-002 | 47 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 47 | 1 | 0 | 97.92% | PASS |
| unknown | JSS-PRE-001 | 47 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 21 | 4 | 0 | 84.00% | FAIL |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 948 | 58 | 0 | 94.23% | PASS |
| unknown | JSS-REFS-004 | 143 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 152 | 5 | 0 | 96.82% | PASS |
| unknown | JSS-REFS-007 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 39 | 1 | 0 | 97.50% | PASS |
| unknown | JSS-STRUCT-002 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 48 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 7 | 0 | 77.42% | FAIL |
| unknown | JSS-WIDTH-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 154 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 141 | 0 | 0 | 100.00% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 46 | 8 | 0 | 85.19% | FAIL |
| citation | JSS-CITE-003 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 27 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 52 | 5 | 0 | 91.23% | PASS |
| unknown | JSS-CAP-003 | 12 | 15 | 0 | 44.44% | FAIL |
| unknown | JSS-CAP-004 | 10 | 3 | 0 | 76.92% | FAIL |
| unknown | JSS-CODE-001 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 63 | 3 | 0 | 95.45% | PASS |
| unknown | JSS-HOUSE-001 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 326 | 38 | 0 | 89.56% | FAIL |
| unknown | JSS-MARKUP-002 | 115 | 4 | 0 | 96.64% | PASS |
| unknown | JSS-MARKUP-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-004 | 27 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 51 | 1 | 0 | 98.08% | PASS |
| unknown | JSS-OPER-001 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-002 | 32 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 37 | 1 | 0 | 97.37% | PASS |
| unknown | JSS-PRE-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 10 | 4 | 0 | 71.43% | FAIL |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 948 | 58 | 0 | 94.23% | PASS |
| unknown | JSS-REFS-004 | 143 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 152 | 5 | 0 | 96.82% | PASS |
| unknown | JSS-REFS-007 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-002 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 31 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 19 | 4 | 0 | 82.61% | FAIL |
| unknown | JSS-WIDTH-001 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 74 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 102 | 0 | 0 | 100.00% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-MARKUP-002`: tp +249→248 (-1), fp +20→20 (+0), pending 0→0 (+0)
- `JSS-MARKUP-003`: tp +171→152 (-19), fp +3→0 (-3), pending 0→0 (+0)
- `JSS-MARKUP-004`: tp +107→111 (+4), fp +4→0 (-4), pending 0→0 (+0)
- `JSS-XREF-004`: tp +143→141 (-2), fp +3→0 (-3), pending 0→0 (+0)

**Pinned only**

- `JSS-MARKUP-003`: tp +17→13 (-4), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-MARKUP-004`: tp +26→27 (+1), fp +1→0 (-1), pending 0→0 (+0)
- `JSS-XREF-004`: tp +104→102 (-2), fp +3→0 (-3), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 52 — 2026-04-29T19:55:33Z — post-CAP-002-hyphen-pieces

- **Corpus size:** 112 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=28, pinned=24

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 147 | 9 | 0 | 94.23% | PASS |
| citation | JSS-CITE-003 | 9 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 36 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 157 | 8 | 0 | 95.15% | PASS |
| unknown | JSS-CAP-003 | 17 | 22 | 0 | 43.59% | FAIL |
| unknown | JSS-CAP-004 | 11 | 4 | 0 | 73.33% | FAIL |
| unknown | JSS-CODE-001 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 113 | 7 | 0 | 94.17% | PASS |
| unknown | JSS-HOUSE-001 | 277 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 893 | 85 | 0 | 91.31% | PASS |
| unknown | JSS-MARKUP-002 | 248 | 20 | 0 | 92.54% | PASS |
| unknown | JSS-MARKUP-003 | 152 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-004 | 111 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-001 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 51 | 1 | 0 | 98.08% | PASS |
| unknown | JSS-OPER-001 | 60 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-002 | 47 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 47 | 1 | 0 | 97.92% | PASS |
| unknown | JSS-PRE-001 | 47 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 21 | 4 | 0 | 84.00% | FAIL |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 948 | 58 | 0 | 94.23% | PASS |
| unknown | JSS-REFS-004 | 143 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 152 | 5 | 0 | 96.82% | PASS |
| unknown | JSS-REFS-007 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 39 | 1 | 0 | 97.50% | PASS |
| unknown | JSS-STRUCT-002 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 48 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 7 | 0 | 77.42% | FAIL |
| unknown | JSS-WIDTH-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 154 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 141 | 0 | 0 | 100.00% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 46 | 8 | 0 | 85.19% | FAIL |
| citation | JSS-CITE-003 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 27 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 52 | 3 | 0 | 94.55% | PASS |
| unknown | JSS-CAP-003 | 12 | 15 | 0 | 44.44% | FAIL |
| unknown | JSS-CAP-004 | 10 | 3 | 0 | 76.92% | FAIL |
| unknown | JSS-CODE-001 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 63 | 3 | 0 | 95.45% | PASS |
| unknown | JSS-HOUSE-001 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 326 | 38 | 0 | 89.56% | FAIL |
| unknown | JSS-MARKUP-002 | 115 | 4 | 0 | 96.64% | PASS |
| unknown | JSS-MARKUP-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-004 | 27 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 51 | 1 | 0 | 98.08% | PASS |
| unknown | JSS-OPER-001 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-002 | 32 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 37 | 1 | 0 | 97.37% | PASS |
| unknown | JSS-PRE-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 10 | 4 | 0 | 71.43% | FAIL |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 948 | 58 | 0 | 94.23% | PASS |
| unknown | JSS-REFS-004 | 143 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 152 | 5 | 0 | 96.82% | PASS |
| unknown | JSS-REFS-007 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-002 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 31 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 19 | 4 | 0 | 82.61% | FAIL |
| unknown | JSS-WIDTH-001 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 74 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 102 | 0 | 0 | 100.00% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-CAP-002`: tp +157→157 (+0), fp +12→8 (-4), pending 0→0 (+0)

**Pinned only**

- `JSS-CAP-002`: tp +52→52 (+0), fp +5→3 (-2), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 53 — 2026-04-29T20:14:42Z — post-CODE-003-pct-escapes

- **Corpus size:** 112 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=28, pinned=24

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 147 | 9 | 0 | 94.23% | PASS |
| citation | JSS-CITE-003 | 9 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 36 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 157 | 8 | 0 | 95.15% | PASS |
| unknown | JSS-CAP-003 | 17 | 22 | 0 | 43.59% | FAIL |
| unknown | JSS-CAP-004 | 11 | 4 | 0 | 73.33% | FAIL |
| unknown | JSS-CODE-001 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 117 | 1 | 0 | 99.15% | PASS |
| unknown | JSS-HOUSE-001 | 277 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 893 | 85 | 0 | 91.31% | PASS |
| unknown | JSS-MARKUP-002 | 248 | 20 | 0 | 92.54% | PASS |
| unknown | JSS-MARKUP-003 | 152 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-004 | 111 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-001 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 51 | 1 | 0 | 98.08% | PASS |
| unknown | JSS-OPER-001 | 60 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-002 | 47 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 47 | 1 | 0 | 97.92% | PASS |
| unknown | JSS-PRE-001 | 47 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 21 | 4 | 0 | 84.00% | FAIL |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 948 | 58 | 0 | 94.23% | PASS |
| unknown | JSS-REFS-004 | 143 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 152 | 5 | 0 | 96.82% | PASS |
| unknown | JSS-REFS-007 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 39 | 1 | 0 | 97.50% | PASS |
| unknown | JSS-STRUCT-002 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 48 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 7 | 0 | 77.42% | FAIL |
| unknown | JSS-WIDTH-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 154 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 141 | 0 | 0 | 100.00% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 46 | 8 | 0 | 85.19% | FAIL |
| citation | JSS-CITE-003 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 27 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 52 | 3 | 0 | 94.55% | PASS |
| unknown | JSS-CAP-003 | 12 | 15 | 0 | 44.44% | FAIL |
| unknown | JSS-CAP-004 | 10 | 3 | 0 | 76.92% | FAIL |
| unknown | JSS-CODE-001 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 64 | 1 | 0 | 98.46% | PASS |
| unknown | JSS-HOUSE-001 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 326 | 38 | 0 | 89.56% | FAIL |
| unknown | JSS-MARKUP-002 | 115 | 4 | 0 | 96.64% | PASS |
| unknown | JSS-MARKUP-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-004 | 27 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 51 | 1 | 0 | 98.08% | PASS |
| unknown | JSS-OPER-001 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-002 | 32 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 37 | 1 | 0 | 97.37% | PASS |
| unknown | JSS-PRE-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 10 | 4 | 0 | 71.43% | FAIL |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 948 | 58 | 0 | 94.23% | PASS |
| unknown | JSS-REFS-004 | 143 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-006 | 152 | 5 | 0 | 96.82% | PASS |
| unknown | JSS-REFS-007 | 64 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-002 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 31 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 19 | 4 | 0 | 82.61% | FAIL |
| unknown | JSS-WIDTH-001 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 74 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 102 | 0 | 0 | 100.00% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-CODE-003`: tp +113→117 (+4), fp +7→1 (-6), pending 0→0 (+0)

**Pinned only**

- `JSS-CODE-003`: tp +63→64 (+1), fp +3→1 (-2), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 54 — 2026-04-30T18:57:50Z — iter-54-baseline

- **Corpus size:** 142 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=38, pinned=30

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 159 | 14 | 0 | 91.91% | PASS |
| citation | JSS-CITE-003 | 9 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 55 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 176 | 10 | 0 | 94.62% | PASS |
| unknown | JSS-CAP-003 | 19 | 35 | 0 | 35.19% | FAIL |
| unknown | JSS-CAP-004 | 15 | 5 | 0 | 75.00% | FAIL |
| unknown | JSS-CODE-001 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 144 | 2 | 0 | 98.63% | PASS |
| unknown | JSS-HOUSE-001 | 362 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 21 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 934 | 101 | 0 | 90.24% | PASS |
| unknown | JSS-MARKUP-002 | 249 | 20 | 0 | 92.57% | PASS |
| unknown | JSS-MARKUP-003 | 243 | 1 | 0 | 99.59% | PASS |
| unknown | JSS-MARKUP-004 | 121 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-001 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 62 | 1 | 0 | 98.41% | PASS |
| unknown | JSS-OPER-001 | 62 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-002 | 48 | 1 | 0 | 97.96% | PASS |
| unknown | JSS-OPER-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 94 | 7 | 0 | 93.07% | PASS |
| unknown | JSS-PRE-001 | 52 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 24 | 4 | 0 | 85.71% | FAIL |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 1411 | 62 | 0 | 95.79% | PASS |
| unknown | JSS-REFS-004 | 166 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 30 | 1 | 0 | 96.77% | PASS |
| unknown | JSS-REFS-006 | 199 | 6 | 0 | 97.07% | PASS |
| unknown | JSS-REFS-007 | 78 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 50 | 1 | 0 | 98.04% | PASS |
| unknown | JSS-STRUCT-002 | 19 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 61 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 48 | 7 | 0 | 87.27% | FAIL |
| unknown | JSS-WIDTH-001 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 27 | 1 | 0 | 96.43% | PASS |
| unknown | JSS-XREF-002 | 229 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 206 | 1 | 0 | 99.52% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 55 | 11 | 0 | 83.33% | FAIL |
| citation | JSS-CITE-003 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 41 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 69 | 5 | 0 | 93.24% | PASS |
| unknown | JSS-CAP-003 | 13 | 26 | 0 | 33.33% | FAIL |
| unknown | JSS-CAP-004 | 12 | 4 | 0 | 75.00% | FAIL |
| unknown | JSS-CODE-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 88 | 2 | 0 | 97.78% | PASS |
| unknown | JSS-HOUSE-001 | 109 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 360 | 54 | 0 | 86.96% | FAIL |
| unknown | JSS-MARKUP-002 | 116 | 4 | 0 | 96.67% | PASS |
| unknown | JSS-MARKUP-003 | 93 | 1 | 0 | 98.94% | PASS |
| unknown | JSS-MARKUP-004 | 28 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 62 | 1 | 0 | 98.41% | PASS |
| unknown | JSS-OPER-001 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-002 | 33 | 1 | 0 | 97.06% | PASS |
| unknown | JSS-OPER-004 | 73 | 7 | 0 | 91.25% | PASS |
| unknown | JSS-PRE-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 13 | 4 | 0 | 76.47% | FAIL |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 1411 | 62 | 0 | 95.79% | PASS |
| unknown | JSS-REFS-004 | 166 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 30 | 1 | 0 | 96.77% | PASS |
| unknown | JSS-REFS-006 | 199 | 6 | 0 | 97.07% | PASS |
| unknown | JSS-REFS-007 | 78 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 21 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-002 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 40 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 37 | 4 | 0 | 90.24% | PASS |
| unknown | JSS-WIDTH-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 148 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 152 | 0 | 0 | 100.00% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-CITE-002`: tp +147→159 (+12), fp +9→14 (+5), pending 0→0 (+0)
- `JSS-BIBTEX-002`: tp +4→5 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-BIBTEX-003`: tp +13→20 (+7), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-BIBTEX-004`: tp +36→55 (+19), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-CAP-002`: tp +157→176 (+19), fp +8→10 (+2), pending 0→0 (+0)
- `JSS-CAP-003`: tp +17→19 (+2), fp +22→35 (+13), pending 0→0 (+0)
- `JSS-CAP-004`: tp +11→15 (+4), fp +4→5 (+1), pending 0→0 (+0)
- `JSS-CODE-001`: tp +14→18 (+4), fp +0→0 (+0), pending 0→0 (+0)
- **new** `JSS-CODE-002`: tp=1 fp=0 pending=0
- `JSS-CODE-003`: tp +117→144 (+27), fp +1→2 (+1), pending 0→0 (+0)
- `JSS-HOUSE-001`: tp +277→362 (+85), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-HOUSE-002`: tp +5→11 (+6), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-HOUSE-003`: tp +16→21 (+5), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-MARKUP-001`: tp +893→934 (+41), fp +85→101 (+16), pending 0→0 (+0)
- `JSS-MARKUP-002`: tp +248→249 (+1), fp +20→20 (+0), pending 0→0 (+0)
- `JSS-MARKUP-003`: tp +152→243 (+91), fp +0→1 (+1), pending 0→0 (+0)
- `JSS-MARKUP-004`: tp +111→121 (+10), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-NAME-002`: tp +51→62 (+11), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-OPER-001`: tp +60→62 (+2), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-OPER-002`: tp +47→48 (+1), fp +0→1 (+1), pending 0→0 (+0)
- **new** `JSS-OPER-003`: tp=13 fp=0 pending=0
- `JSS-OPER-004`: tp +47→94 (+47), fp +1→7 (+6), pending 0→0 (+0)
- `JSS-PRE-001`: tp +47→52 (+5), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-PRE-006`: tp +21→24 (+3), fp +4→4 (+0), pending 0→0 (+0)
- `JSS-REFS-003`: tp +948→1411 (+463), fp +58→62 (+4), pending 0→0 (+0)
- `JSS-REFS-004`: tp +143→166 (+23), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-REFS-005`: tp +6→30 (+24), fp +0→1 (+1), pending 0→0 (+0)
- `JSS-REFS-006`: tp +152→199 (+47), fp +5→6 (+1), pending 0→0 (+0)
- `JSS-REFS-007`: tp +64→78 (+14), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-STRUCT-001`: tp +39→50 (+11), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-STRUCT-002`: tp +11→19 (+8), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-STRUCT-003`: tp +1→2 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-TYPO-001`: tp +48→61 (+13), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-TYPO-003`: tp +1→2 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-TYPO-004`: tp +24→48 (+24), fp +7→7 (+0), pending 0→0 (+0)
- `JSS-WIDTH-001`: tp +13→15 (+2), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-XREF-001`: tp +20→27 (+7), fp +0→1 (+1), pending 0→0 (+0)
- `JSS-XREF-002`: tp +154→229 (+75), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-XREF-004`: tp +141→206 (+65), fp +0→1 (+1), pending 0→0 (+0)

**Pinned only**

- `JSS-CITE-002`: tp +46→55 (+9), fp +8→11 (+3), pending 0→0 (+0)
- `JSS-BIBTEX-002`: tp +4→5 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-BIBTEX-003`: tp +13→20 (+7), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-BIBTEX-004`: tp +27→41 (+14), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-CAP-002`: tp +52→69 (+17), fp +3→5 (+2), pending 0→0 (+0)
- `JSS-CAP-003`: tp +12→13 (+1), fp +15→26 (+11), pending 0→0 (+0)
- `JSS-CAP-004`: tp +10→12 (+2), fp +3→4 (+1), pending 0→0 (+0)
- `JSS-CODE-001`: tp +12→13 (+1), fp +0→0 (+0), pending 0→0 (+0)
- **new** `JSS-CODE-002`: tp=1 fp=0 pending=0
- `JSS-CODE-003`: tp +64→88 (+24), fp +1→2 (+1), pending 0→0 (+0)
- `JSS-HOUSE-001`: tp +64→109 (+45), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-HOUSE-002`: tp +5→11 (+6), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-HOUSE-003`: tp +13→18 (+5), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-MARKUP-001`: tp +326→360 (+34), fp +38→54 (+16), pending 0→0 (+0)
- `JSS-MARKUP-002`: tp +115→116 (+1), fp +4→4 (+0), pending 0→0 (+0)
- `JSS-MARKUP-003`: tp +13→93 (+80), fp +0→1 (+1), pending 0→0 (+0)
- `JSS-MARKUP-004`: tp +27→28 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-NAME-002`: tp +51→62 (+11), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-OPER-002`: tp +32→33 (+1), fp +0→1 (+1), pending 0→0 (+0)
- `JSS-OPER-004`: tp +37→73 (+36), fp +1→7 (+6), pending 0→0 (+0)
- `JSS-PRE-006`: tp +10→13 (+3), fp +4→4 (+0), pending 0→0 (+0)
- `JSS-REFS-003`: tp +948→1411 (+463), fp +58→62 (+4), pending 0→0 (+0)
- `JSS-REFS-004`: tp +143→166 (+23), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-REFS-005`: tp +6→30 (+24), fp +0→1 (+1), pending 0→0 (+0)
- `JSS-REFS-006`: tp +152→199 (+47), fp +5→6 (+1), pending 0→0 (+0)
- `JSS-REFS-007`: tp +64→78 (+14), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-STRUCT-001`: tp +14→21 (+7), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-STRUCT-002`: tp +8→13 (+5), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-STRUCT-003`: tp +1→2 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-TYPO-001`: tp +31→40 (+9), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-TYPO-003`: tp +1→2 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-TYPO-004`: tp +19→37 (+18), fp +4→4 (+0), pending 0→0 (+0)
- `JSS-WIDTH-001`: tp +8→10 (+2), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-XREF-001`: tp +13→15 (+2), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-XREF-002`: tp +74→148 (+74), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-XREF-004`: tp +102→152 (+50), fp +0→0 (+0), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 55 — 2026-04-30T19:14:11Z — post-JSS-PRE-006

- **Corpus size:** 142 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=38, pinned=30

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 159 | 14 | 0 | 91.91% | PASS |
| citation | JSS-CITE-003 | 9 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 55 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 176 | 10 | 0 | 94.62% | PASS |
| unknown | JSS-CAP-003 | 19 | 35 | 0 | 35.19% | FAIL |
| unknown | JSS-CAP-004 | 15 | 5 | 0 | 75.00% | FAIL |
| unknown | JSS-CODE-001 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 144 | 2 | 0 | 98.63% | PASS |
| unknown | JSS-HOUSE-001 | 362 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 21 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 934 | 101 | 0 | 90.24% | PASS |
| unknown | JSS-MARKUP-002 | 249 | 20 | 0 | 92.57% | PASS |
| unknown | JSS-MARKUP-003 | 243 | 1 | 0 | 99.59% | PASS |
| unknown | JSS-MARKUP-004 | 121 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-001 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 62 | 1 | 0 | 98.41% | PASS |
| unknown | JSS-OPER-001 | 62 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-002 | 48 | 1 | 0 | 97.96% | PASS |
| unknown | JSS-OPER-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 94 | 7 | 0 | 93.07% | PASS |
| unknown | JSS-PRE-001 | 52 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 1411 | 62 | 0 | 95.79% | PASS |
| unknown | JSS-REFS-004 | 166 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 30 | 1 | 0 | 96.77% | PASS |
| unknown | JSS-REFS-006 | 199 | 6 | 0 | 97.07% | PASS |
| unknown | JSS-REFS-007 | 78 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 50 | 1 | 0 | 98.04% | PASS |
| unknown | JSS-STRUCT-002 | 19 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 61 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 48 | 7 | 0 | 87.27% | FAIL |
| unknown | JSS-WIDTH-001 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 27 | 1 | 0 | 96.43% | PASS |
| unknown | JSS-XREF-002 | 229 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 206 | 1 | 0 | 99.52% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 55 | 11 | 0 | 83.33% | FAIL |
| citation | JSS-CITE-003 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 41 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 69 | 5 | 0 | 93.24% | PASS |
| unknown | JSS-CAP-003 | 13 | 26 | 0 | 33.33% | FAIL |
| unknown | JSS-CAP-004 | 12 | 4 | 0 | 75.00% | FAIL |
| unknown | JSS-CODE-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 88 | 2 | 0 | 97.78% | PASS |
| unknown | JSS-HOUSE-001 | 109 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 360 | 54 | 0 | 86.96% | FAIL |
| unknown | JSS-MARKUP-002 | 116 | 4 | 0 | 96.67% | PASS |
| unknown | JSS-MARKUP-003 | 93 | 1 | 0 | 98.94% | PASS |
| unknown | JSS-MARKUP-004 | 28 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 62 | 1 | 0 | 98.41% | PASS |
| unknown | JSS-OPER-001 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-002 | 33 | 1 | 0 | 97.06% | PASS |
| unknown | JSS-OPER-004 | 73 | 7 | 0 | 91.25% | PASS |
| unknown | JSS-PRE-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 1411 | 62 | 0 | 95.79% | PASS |
| unknown | JSS-REFS-004 | 166 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 30 | 1 | 0 | 96.77% | PASS |
| unknown | JSS-REFS-006 | 199 | 6 | 0 | 97.07% | PASS |
| unknown | JSS-REFS-007 | 78 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 21 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-002 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 40 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 37 | 4 | 0 | 90.24% | PASS |
| unknown | JSS-WIDTH-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 148 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 152 | 0 | 0 | 100.00% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-PRE-006`: tp +24→6 (-18), fp +4→0 (-4), pending 0→0 (+0)

**Pinned only**

- `JSS-PRE-006`: tp +13→5 (-8), fp +4→0 (-4), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 56 — 2026-04-30T19:20:05Z — post-JSS-CAP-003

- **Corpus size:** 142 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=38, pinned=30

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 159 | 14 | 0 | 91.91% | PASS |
| citation | JSS-CITE-003 | 9 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 55 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 125 | 10 | 0 | 92.59% | PASS |
| unknown | JSS-CAP-003 | 19 | 27 | 0 | 41.30% | FAIL |
| unknown | JSS-CAP-004 | 15 | 5 | 0 | 75.00% | FAIL |
| unknown | JSS-CODE-001 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 144 | 2 | 0 | 98.63% | PASS |
| unknown | JSS-HOUSE-001 | 362 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 21 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 934 | 101 | 0 | 90.24% | PASS |
| unknown | JSS-MARKUP-002 | 249 | 20 | 0 | 92.57% | PASS |
| unknown | JSS-MARKUP-003 | 243 | 1 | 0 | 99.59% | PASS |
| unknown | JSS-MARKUP-004 | 121 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-001 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 62 | 1 | 0 | 98.41% | PASS |
| unknown | JSS-OPER-001 | 62 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-002 | 48 | 1 | 0 | 97.96% | PASS |
| unknown | JSS-OPER-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 94 | 7 | 0 | 93.07% | PASS |
| unknown | JSS-PRE-001 | 52 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 1411 | 62 | 0 | 95.79% | PASS |
| unknown | JSS-REFS-004 | 166 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 30 | 1 | 0 | 96.77% | PASS |
| unknown | JSS-REFS-006 | 199 | 6 | 0 | 97.07% | PASS |
| unknown | JSS-REFS-007 | 78 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 50 | 1 | 0 | 98.04% | PASS |
| unknown | JSS-STRUCT-002 | 19 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 61 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 48 | 7 | 0 | 87.27% | FAIL |
| unknown | JSS-WIDTH-001 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 27 | 1 | 0 | 96.43% | PASS |
| unknown | JSS-XREF-002 | 229 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 206 | 1 | 0 | 99.52% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 55 | 11 | 0 | 83.33% | FAIL |
| citation | JSS-CITE-003 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 41 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 69 | 5 | 0 | 93.24% | PASS |
| unknown | JSS-CAP-003 | 13 | 18 | 0 | 41.94% | FAIL |
| unknown | JSS-CAP-004 | 12 | 4 | 0 | 75.00% | FAIL |
| unknown | JSS-CODE-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 88 | 2 | 0 | 97.78% | PASS |
| unknown | JSS-HOUSE-001 | 109 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 360 | 54 | 0 | 86.96% | FAIL |
| unknown | JSS-MARKUP-002 | 116 | 4 | 0 | 96.67% | PASS |
| unknown | JSS-MARKUP-003 | 93 | 1 | 0 | 98.94% | PASS |
| unknown | JSS-MARKUP-004 | 28 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 62 | 1 | 0 | 98.41% | PASS |
| unknown | JSS-OPER-001 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-002 | 33 | 1 | 0 | 97.06% | PASS |
| unknown | JSS-OPER-004 | 73 | 7 | 0 | 91.25% | PASS |
| unknown | JSS-PRE-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 1411 | 62 | 0 | 95.79% | PASS |
| unknown | JSS-REFS-004 | 166 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 30 | 1 | 0 | 96.77% | PASS |
| unknown | JSS-REFS-006 | 199 | 6 | 0 | 97.07% | PASS |
| unknown | JSS-REFS-007 | 78 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 21 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-002 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 40 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 37 | 4 | 0 | 90.24% | PASS |
| unknown | JSS-WIDTH-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 148 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 152 | 0 | 0 | 100.00% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-CAP-002`: tp +176→125 (-51), fp +10→10 (+0), pending 0→0 (+0)
- `JSS-CAP-003`: tp +19→19 (+0), fp +35→27 (-8), pending 0→0 (+0)

**Pinned only**

- `JSS-CAP-003`: tp +13→13 (+0), fp +26→18 (-8), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 57 — 2026-04-30T19:43:08Z — post-JSS-CAP-004

- **Corpus size:** 142 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=38, pinned=30

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 159 | 14 | 0 | 91.91% | PASS |
| citation | JSS-CITE-003 | 9 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 55 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 125 | 10 | 0 | 92.59% | PASS |
| unknown | JSS-CAP-003 | 19 | 27 | 0 | 41.30% | FAIL |
| unknown | JSS-CAP-004 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 144 | 2 | 0 | 98.63% | PASS |
| unknown | JSS-HOUSE-001 | 362 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 21 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 934 | 101 | 0 | 90.24% | PASS |
| unknown | JSS-MARKUP-002 | 249 | 20 | 0 | 92.57% | PASS |
| unknown | JSS-MARKUP-003 | 243 | 1 | 0 | 99.59% | PASS |
| unknown | JSS-MARKUP-004 | 121 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-001 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 62 | 1 | 0 | 98.41% | PASS |
| unknown | JSS-OPER-001 | 62 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-002 | 48 | 1 | 0 | 97.96% | PASS |
| unknown | JSS-OPER-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 94 | 7 | 0 | 93.07% | PASS |
| unknown | JSS-PRE-001 | 52 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 1411 | 62 | 0 | 95.79% | PASS |
| unknown | JSS-REFS-004 | 166 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 30 | 1 | 0 | 96.77% | PASS |
| unknown | JSS-REFS-006 | 199 | 6 | 0 | 97.07% | PASS |
| unknown | JSS-REFS-007 | 78 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 50 | 1 | 0 | 98.04% | PASS |
| unknown | JSS-STRUCT-002 | 19 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 61 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 48 | 7 | 0 | 87.27% | FAIL |
| unknown | JSS-WIDTH-001 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 27 | 1 | 0 | 96.43% | PASS |
| unknown | JSS-XREF-002 | 229 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 206 | 1 | 0 | 99.52% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 55 | 11 | 0 | 83.33% | FAIL |
| citation | JSS-CITE-003 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 41 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 69 | 5 | 0 | 93.24% | PASS |
| unknown | JSS-CAP-003 | 13 | 18 | 0 | 41.94% | FAIL |
| unknown | JSS-CAP-004 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 88 | 2 | 0 | 97.78% | PASS |
| unknown | JSS-HOUSE-001 | 109 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 360 | 54 | 0 | 86.96% | FAIL |
| unknown | JSS-MARKUP-002 | 116 | 4 | 0 | 96.67% | PASS |
| unknown | JSS-MARKUP-003 | 93 | 1 | 0 | 98.94% | PASS |
| unknown | JSS-MARKUP-004 | 28 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 62 | 1 | 0 | 98.41% | PASS |
| unknown | JSS-OPER-001 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-002 | 33 | 1 | 0 | 97.06% | PASS |
| unknown | JSS-OPER-004 | 73 | 7 | 0 | 91.25% | PASS |
| unknown | JSS-PRE-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 1411 | 62 | 0 | 95.79% | PASS |
| unknown | JSS-REFS-004 | 166 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 30 | 1 | 0 | 96.77% | PASS |
| unknown | JSS-REFS-006 | 199 | 6 | 0 | 97.07% | PASS |
| unknown | JSS-REFS-007 | 78 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 21 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-002 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 40 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 37 | 4 | 0 | 90.24% | PASS |
| unknown | JSS-WIDTH-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 148 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 152 | 0 | 0 | 100.00% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-CAP-004`: tp +15→7 (-8), fp +5→0 (-5), pending 0→0 (+0)

**Pinned only**

- `JSS-CAP-004`: tp +12→6 (-6), fp +4→0 (-4), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 58 — 2026-04-30T19:48:12Z — post-JSS-TYPO-004

- **Corpus size:** 142 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=38, pinned=30

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 159 | 14 | 0 | 91.91% | PASS |
| citation | JSS-CITE-003 | 9 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 55 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 125 | 10 | 0 | 92.59% | PASS |
| unknown | JSS-CAP-003 | 19 | 27 | 0 | 41.30% | FAIL |
| unknown | JSS-CAP-004 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 144 | 2 | 0 | 98.63% | PASS |
| unknown | JSS-HOUSE-001 | 362 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 21 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 934 | 101 | 0 | 90.24% | PASS |
| unknown | JSS-MARKUP-002 | 249 | 20 | 0 | 92.57% | PASS |
| unknown | JSS-MARKUP-003 | 243 | 1 | 0 | 99.59% | PASS |
| unknown | JSS-MARKUP-004 | 121 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-001 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 62 | 1 | 0 | 98.41% | PASS |
| unknown | JSS-OPER-001 | 62 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-002 | 48 | 1 | 0 | 97.96% | PASS |
| unknown | JSS-OPER-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 94 | 7 | 0 | 93.07% | PASS |
| unknown | JSS-PRE-001 | 52 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 1411 | 62 | 0 | 95.79% | PASS |
| unknown | JSS-REFS-004 | 166 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 30 | 1 | 0 | 96.77% | PASS |
| unknown | JSS-REFS-006 | 199 | 6 | 0 | 97.07% | PASS |
| unknown | JSS-REFS-007 | 78 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 50 | 1 | 0 | 98.04% | PASS |
| unknown | JSS-STRUCT-002 | 19 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 61 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 3 | 0 | 88.89% | FAIL |
| unknown | JSS-WIDTH-001 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 27 | 1 | 0 | 96.43% | PASS |
| unknown | JSS-XREF-002 | 229 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 206 | 1 | 0 | 99.52% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 55 | 11 | 0 | 83.33% | FAIL |
| citation | JSS-CITE-003 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 41 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 69 | 5 | 0 | 93.24% | PASS |
| unknown | JSS-CAP-003 | 13 | 18 | 0 | 41.94% | FAIL |
| unknown | JSS-CAP-004 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 88 | 2 | 0 | 97.78% | PASS |
| unknown | JSS-HOUSE-001 | 109 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 360 | 54 | 0 | 86.96% | FAIL |
| unknown | JSS-MARKUP-002 | 116 | 4 | 0 | 96.67% | PASS |
| unknown | JSS-MARKUP-003 | 93 | 1 | 0 | 98.94% | PASS |
| unknown | JSS-MARKUP-004 | 28 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 62 | 1 | 0 | 98.41% | PASS |
| unknown | JSS-OPER-001 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-002 | 33 | 1 | 0 | 97.06% | PASS |
| unknown | JSS-OPER-004 | 73 | 7 | 0 | 91.25% | PASS |
| unknown | JSS-PRE-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 1411 | 62 | 0 | 95.79% | PASS |
| unknown | JSS-REFS-004 | 166 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 30 | 1 | 0 | 96.77% | PASS |
| unknown | JSS-REFS-006 | 199 | 6 | 0 | 97.07% | PASS |
| unknown | JSS-REFS-007 | 78 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 21 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-002 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 40 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 1 | 0 | 96.00% | PASS |
| unknown | JSS-WIDTH-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 148 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 152 | 0 | 0 | 100.00% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-TYPO-004`: tp +48→24 (-24), fp +7→3 (-4), pending 0→0 (+0)

**Pinned only**

- `JSS-TYPO-004`: tp +37→24 (-13), fp +4→1 (-3), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 59 — 2026-04-30T19:58:14Z — post-JSS-REFS-006

- **Corpus size:** 142 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=38, pinned=30

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 159 | 14 | 0 | 91.91% | PASS |
| citation | JSS-CITE-003 | 9 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 55 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 125 | 10 | 0 | 92.59% | PASS |
| unknown | JSS-CAP-003 | 19 | 27 | 0 | 41.30% | FAIL |
| unknown | JSS-CAP-004 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 144 | 2 | 0 | 98.63% | PASS |
| unknown | JSS-HOUSE-001 | 362 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 21 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 934 | 101 | 0 | 90.24% | PASS |
| unknown | JSS-MARKUP-002 | 249 | 20 | 0 | 92.57% | PASS |
| unknown | JSS-MARKUP-003 | 243 | 1 | 0 | 99.59% | PASS |
| unknown | JSS-MARKUP-004 | 121 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-001 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 62 | 1 | 0 | 98.41% | PASS |
| unknown | JSS-OPER-001 | 62 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-002 | 48 | 1 | 0 | 97.96% | PASS |
| unknown | JSS-OPER-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 94 | 7 | 0 | 93.07% | PASS |
| unknown | JSS-PRE-001 | 52 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 1411 | 62 | 0 | 95.79% | PASS |
| unknown | JSS-REFS-004 | 166 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 30 | 1 | 0 | 96.77% | PASS |
| unknown | JSS-REFS-006 | 118 | 2 | 0 | 98.33% | PASS |
| unknown | JSS-REFS-007 | 78 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 50 | 1 | 0 | 98.04% | PASS |
| unknown | JSS-STRUCT-002 | 19 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 61 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 3 | 0 | 88.89% | FAIL |
| unknown | JSS-WIDTH-001 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 27 | 1 | 0 | 96.43% | PASS |
| unknown | JSS-XREF-002 | 229 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 206 | 1 | 0 | 99.52% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 55 | 11 | 0 | 83.33% | FAIL |
| citation | JSS-CITE-003 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 41 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 69 | 5 | 0 | 93.24% | PASS |
| unknown | JSS-CAP-003 | 13 | 18 | 0 | 41.94% | FAIL |
| unknown | JSS-CAP-004 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 88 | 2 | 0 | 97.78% | PASS |
| unknown | JSS-HOUSE-001 | 109 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 360 | 54 | 0 | 86.96% | FAIL |
| unknown | JSS-MARKUP-002 | 116 | 4 | 0 | 96.67% | PASS |
| unknown | JSS-MARKUP-003 | 93 | 1 | 0 | 98.94% | PASS |
| unknown | JSS-MARKUP-004 | 28 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 62 | 1 | 0 | 98.41% | PASS |
| unknown | JSS-OPER-001 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-002 | 33 | 1 | 0 | 97.06% | PASS |
| unknown | JSS-OPER-004 | 73 | 7 | 0 | 91.25% | PASS |
| unknown | JSS-PRE-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 1411 | 62 | 0 | 95.79% | PASS |
| unknown | JSS-REFS-004 | 166 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 30 | 1 | 0 | 96.77% | PASS |
| unknown | JSS-REFS-006 | 118 | 2 | 0 | 98.33% | PASS |
| unknown | JSS-REFS-007 | 78 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 21 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-002 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 40 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 1 | 0 | 96.00% | PASS |
| unknown | JSS-WIDTH-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 148 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 152 | 0 | 0 | 100.00% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-REFS-006`: tp +199→118 (-81), fp +6→2 (-4), pending 0→0 (+0)

**Pinned only**

- `JSS-REFS-006`: tp +199→118 (-81), fp +6→2 (-4), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 60 — 2026-04-30T20:00:33Z — post-JSS-REFS-003

- **Corpus size:** 142 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=38, pinned=30

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 159 | 14 | 0 | 91.91% | PASS |
| citation | JSS-CITE-003 | 9 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 55 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 125 | 10 | 0 | 92.59% | PASS |
| unknown | JSS-CAP-003 | 19 | 27 | 0 | 41.30% | FAIL |
| unknown | JSS-CAP-004 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 144 | 2 | 0 | 98.63% | PASS |
| unknown | JSS-HOUSE-001 | 362 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 21 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 934 | 101 | 0 | 90.24% | PASS |
| unknown | JSS-MARKUP-002 | 249 | 20 | 0 | 92.57% | PASS |
| unknown | JSS-MARKUP-003 | 243 | 1 | 0 | 99.59% | PASS |
| unknown | JSS-MARKUP-004 | 121 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-001 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 62 | 1 | 0 | 98.41% | PASS |
| unknown | JSS-OPER-001 | 62 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-002 | 48 | 1 | 0 | 97.96% | PASS |
| unknown | JSS-OPER-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 94 | 7 | 0 | 93.07% | PASS |
| unknown | JSS-PRE-001 | 52 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 947 | 35 | 0 | 96.44% | PASS |
| unknown | JSS-REFS-004 | 166 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 30 | 1 | 0 | 96.77% | PASS |
| unknown | JSS-REFS-006 | 118 | 2 | 0 | 98.33% | PASS |
| unknown | JSS-REFS-007 | 78 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 50 | 1 | 0 | 98.04% | PASS |
| unknown | JSS-STRUCT-002 | 19 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 61 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 3 | 0 | 88.89% | FAIL |
| unknown | JSS-WIDTH-001 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 27 | 1 | 0 | 96.43% | PASS |
| unknown | JSS-XREF-002 | 229 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 206 | 1 | 0 | 99.52% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 55 | 11 | 0 | 83.33% | FAIL |
| citation | JSS-CITE-003 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 41 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 69 | 5 | 0 | 93.24% | PASS |
| unknown | JSS-CAP-003 | 13 | 18 | 0 | 41.94% | FAIL |
| unknown | JSS-CAP-004 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 88 | 2 | 0 | 97.78% | PASS |
| unknown | JSS-HOUSE-001 | 109 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 360 | 54 | 0 | 86.96% | FAIL |
| unknown | JSS-MARKUP-002 | 116 | 4 | 0 | 96.67% | PASS |
| unknown | JSS-MARKUP-003 | 93 | 1 | 0 | 98.94% | PASS |
| unknown | JSS-MARKUP-004 | 28 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 62 | 1 | 0 | 98.41% | PASS |
| unknown | JSS-OPER-001 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-002 | 33 | 1 | 0 | 97.06% | PASS |
| unknown | JSS-OPER-004 | 73 | 7 | 0 | 91.25% | PASS |
| unknown | JSS-PRE-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 947 | 35 | 0 | 96.44% | PASS |
| unknown | JSS-REFS-004 | 166 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 30 | 1 | 0 | 96.77% | PASS |
| unknown | JSS-REFS-006 | 118 | 2 | 0 | 98.33% | PASS |
| unknown | JSS-REFS-007 | 78 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 21 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-002 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 40 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 1 | 0 | 96.00% | PASS |
| unknown | JSS-WIDTH-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 148 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 152 | 0 | 0 | 100.00% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-REFS-003`: tp +1411→947 (-464), fp +62→35 (-27), pending 0→0 (+0)

**Pinned only**

- `JSS-REFS-003`: tp +1411→947 (-464), fp +62→35 (-27), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 61 — 2026-04-30T20:07:16Z — post-JSS-MARKUP-001

- **Corpus size:** 142 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=38, pinned=30

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 159 | 14 | 0 | 91.91% | PASS |
| citation | JSS-CITE-003 | 9 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 55 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 125 | 10 | 0 | 92.59% | PASS |
| unknown | JSS-CAP-003 | 19 | 27 | 0 | 41.30% | FAIL |
| unknown | JSS-CAP-004 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 144 | 2 | 0 | 98.63% | PASS |
| unknown | JSS-HOUSE-001 | 362 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 21 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 924 | 88 | 0 | 91.30% | PASS |
| unknown | JSS-MARKUP-002 | 233 | 20 | 0 | 92.09% | PASS |
| unknown | JSS-MARKUP-003 | 243 | 1 | 0 | 99.59% | PASS |
| unknown | JSS-MARKUP-004 | 121 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-001 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 62 | 1 | 0 | 98.41% | PASS |
| unknown | JSS-OPER-001 | 62 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-002 | 48 | 1 | 0 | 97.96% | PASS |
| unknown | JSS-OPER-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 94 | 7 | 0 | 93.07% | PASS |
| unknown | JSS-PRE-001 | 52 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 947 | 35 | 0 | 96.44% | PASS |
| unknown | JSS-REFS-004 | 166 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 30 | 1 | 0 | 96.77% | PASS |
| unknown | JSS-REFS-006 | 118 | 2 | 0 | 98.33% | PASS |
| unknown | JSS-REFS-007 | 78 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 50 | 1 | 0 | 98.04% | PASS |
| unknown | JSS-STRUCT-002 | 19 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 61 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 3 | 0 | 88.89% | FAIL |
| unknown | JSS-WIDTH-001 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 27 | 1 | 0 | 96.43% | PASS |
| unknown | JSS-XREF-002 | 229 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 206 | 1 | 0 | 99.52% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 55 | 11 | 0 | 83.33% | FAIL |
| citation | JSS-CITE-003 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 41 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 69 | 5 | 0 | 93.24% | PASS |
| unknown | JSS-CAP-003 | 13 | 18 | 0 | 41.94% | FAIL |
| unknown | JSS-CAP-004 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 88 | 2 | 0 | 97.78% | PASS |
| unknown | JSS-HOUSE-001 | 109 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 353 | 42 | 0 | 89.37% | FAIL |
| unknown | JSS-MARKUP-002 | 104 | 4 | 0 | 96.30% | PASS |
| unknown | JSS-MARKUP-003 | 93 | 1 | 0 | 98.94% | PASS |
| unknown | JSS-MARKUP-004 | 28 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 62 | 1 | 0 | 98.41% | PASS |
| unknown | JSS-OPER-001 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-002 | 33 | 1 | 0 | 97.06% | PASS |
| unknown | JSS-OPER-004 | 73 | 7 | 0 | 91.25% | PASS |
| unknown | JSS-PRE-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 947 | 35 | 0 | 96.44% | PASS |
| unknown | JSS-REFS-004 | 166 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 30 | 1 | 0 | 96.77% | PASS |
| unknown | JSS-REFS-006 | 118 | 2 | 0 | 98.33% | PASS |
| unknown | JSS-REFS-007 | 78 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 21 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-002 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 40 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 1 | 0 | 96.00% | PASS |
| unknown | JSS-WIDTH-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 148 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 152 | 0 | 0 | 100.00% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-MARKUP-001`: tp +934→924 (-10), fp +101→88 (-13), pending 0→0 (+0)
- `JSS-MARKUP-002`: tp +249→233 (-16), fp +20→20 (+0), pending 0→0 (+0)

**Pinned only**

- `JSS-MARKUP-001`: tp +360→353 (-7), fp +54→42 (-12), pending 0→0 (+0)
- `JSS-MARKUP-002`: tp +116→104 (-12), fp +4→4 (+0), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 62 — 2026-04-30T20:14:48Z — post-JSS-MARKUP-002

- **Corpus size:** 142 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=38, pinned=30

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 159 | 14 | 0 | 91.91% | PASS |
| citation | JSS-CITE-003 | 9 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 55 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 125 | 10 | 0 | 92.59% | PASS |
| unknown | JSS-CAP-003 | 19 | 27 | 0 | 41.30% | FAIL |
| unknown | JSS-CAP-004 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 144 | 2 | 0 | 98.63% | PASS |
| unknown | JSS-HOUSE-001 | 362 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 21 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 924 | 88 | 0 | 91.30% | PASS |
| unknown | JSS-MARKUP-002 | 217 | 15 | 0 | 93.53% | PASS |
| unknown | JSS-MARKUP-003 | 243 | 1 | 0 | 99.59% | PASS |
| unknown | JSS-MARKUP-004 | 121 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-001 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 62 | 1 | 0 | 98.41% | PASS |
| unknown | JSS-OPER-001 | 62 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-002 | 48 | 1 | 0 | 97.96% | PASS |
| unknown | JSS-OPER-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 94 | 7 | 0 | 93.07% | PASS |
| unknown | JSS-PRE-001 | 52 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 947 | 35 | 0 | 96.44% | PASS |
| unknown | JSS-REFS-004 | 166 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 30 | 1 | 0 | 96.77% | PASS |
| unknown | JSS-REFS-006 | 118 | 2 | 0 | 98.33% | PASS |
| unknown | JSS-REFS-007 | 78 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 50 | 1 | 0 | 98.04% | PASS |
| unknown | JSS-STRUCT-002 | 19 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 61 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 3 | 0 | 88.89% | FAIL |
| unknown | JSS-WIDTH-001 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 27 | 1 | 0 | 96.43% | PASS |
| unknown | JSS-XREF-002 | 229 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 206 | 1 | 0 | 99.52% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 55 | 11 | 0 | 83.33% | FAIL |
| citation | JSS-CITE-003 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 41 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 69 | 5 | 0 | 93.24% | PASS |
| unknown | JSS-CAP-003 | 13 | 18 | 0 | 41.94% | FAIL |
| unknown | JSS-CAP-004 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 88 | 2 | 0 | 97.78% | PASS |
| unknown | JSS-HOUSE-001 | 109 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 353 | 42 | 0 | 89.37% | FAIL |
| unknown | JSS-MARKUP-002 | 103 | 3 | 0 | 97.17% | PASS |
| unknown | JSS-MARKUP-003 | 93 | 1 | 0 | 98.94% | PASS |
| unknown | JSS-MARKUP-004 | 28 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 62 | 1 | 0 | 98.41% | PASS |
| unknown | JSS-OPER-001 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-002 | 33 | 1 | 0 | 97.06% | PASS |
| unknown | JSS-OPER-004 | 73 | 7 | 0 | 91.25% | PASS |
| unknown | JSS-PRE-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 947 | 35 | 0 | 96.44% | PASS |
| unknown | JSS-REFS-004 | 166 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 30 | 1 | 0 | 96.77% | PASS |
| unknown | JSS-REFS-006 | 118 | 2 | 0 | 98.33% | PASS |
| unknown | JSS-REFS-007 | 78 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 21 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-002 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 40 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 1 | 0 | 96.00% | PASS |
| unknown | JSS-WIDTH-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 148 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 152 | 0 | 0 | 100.00% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-MARKUP-002`: tp +233→217 (-16), fp +20→15 (-5), pending 0→0 (+0)

**Pinned only**

- `JSS-MARKUP-002`: tp +104→103 (-1), fp +4→3 (-1), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 63 — 2026-05-01T06:07:20Z — iter-63-baseline

- **Corpus size:** 172 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=48, pinned=40

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 169 | 15 | 0 | 91.85% | PASS |
| citation | JSS-CITE-003 | 11 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-BIBTEX-002 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 23 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 61 | 2 | 0 | 96.83% | PASS |
| unknown | JSS-CAP-001 | 3 | 1 | 0 | 75.00% | FAIL |
| unknown | JSS-CAP-002 | 130 | 12 | 0 | 91.55% | PASS |
| unknown | JSS-CAP-003 | 19 | 31 | 0 | 38.00% | FAIL |
| unknown | JSS-CAP-004 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 21 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 169 | 5 | 0 | 97.13% | PASS |
| unknown | JSS-HOUSE-001 | 395 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 26 | 2 | 0 | 92.86% | PASS |
| unknown | JSS-MARKUP-001 | 953 | 95 | 0 | 90.94% | PASS |
| unknown | JSS-MARKUP-002 | 217 | 15 | 0 | 93.53% | PASS |
| unknown | JSS-MARKUP-003 | 250 | 1 | 0 | 99.60% | PASS |
| unknown | JSS-MARKUP-004 | 124 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-001 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 66 | 1 | 0 | 98.51% | PASS |
| unknown | JSS-OPER-001 | 68 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-002 | 50 | 1 | 0 | 98.04% | PASS |
| unknown | JSS-OPER-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 95 | 7 | 0 | 93.14% | PASS |
| unknown | JSS-PRE-001 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-004 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-005 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 1143 | 38 | 0 | 96.78% | PASS |
| unknown | JSS-REFS-004 | 190 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 33 | 1 | 0 | 97.06% | PASS |
| unknown | JSS-REFS-006 | 130 | 2 | 0 | 98.48% | PASS |
| unknown | JSS-REFS-007 | 87 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 56 | 2 | 0 | 96.55% | PASS |
| unknown | JSS-STRUCT-002 | 22 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 86 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 3 | 0 | 88.89% | FAIL |
| unknown | JSS-WIDTH-001 | 21 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 32 | 1 | 0 | 96.97% | PASS |
| unknown | JSS-XREF-002 | 290 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 259 | 3 | 0 | 98.85% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 63 | 12 | 0 | 84.00% | FAIL |
| citation | JSS-CITE-003 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 6 | 1 | 0 | 85.71% | FAIL |
| unknown | JSS-BIBTEX-002 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 23 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 47 | 2 | 0 | 95.92% | PASS |
| unknown | JSS-CAP-001 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 74 | 7 | 0 | 91.36% | PASS |
| unknown | JSS-CAP-003 | 13 | 21 | 0 | 38.24% | FAIL |
| unknown | JSS-CAP-004 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 107 | 5 | 0 | 95.54% | PASS |
| unknown | JSS-HOUSE-001 | 130 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 22 | 2 | 0 | 91.67% | PASS |
| unknown | JSS-MARKUP-001 | 381 | 49 | 0 | 88.60% | FAIL |
| unknown | JSS-MARKUP-002 | 103 | 3 | 0 | 97.17% | PASS |
| unknown | JSS-MARKUP-003 | 100 | 1 | 0 | 99.01% | PASS |
| unknown | JSS-MARKUP-004 | 31 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 66 | 1 | 0 | 98.51% | PASS |
| unknown | JSS-OPER-001 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-002 | 33 | 1 | 0 | 97.06% | PASS |
| unknown | JSS-OPER-004 | 74 | 7 | 0 | 91.36% | PASS |
| unknown | JSS-PRE-001 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-004 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-005 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 1143 | 38 | 0 | 96.78% | PASS |
| unknown | JSS-REFS-004 | 190 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 33 | 1 | 0 | 97.06% | PASS |
| unknown | JSS-REFS-006 | 130 | 2 | 0 | 98.48% | PASS |
| unknown | JSS-REFS-007 | 87 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 26 | 1 | 0 | 96.30% | PASS |
| unknown | JSS-STRUCT-002 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 45 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 1 | 0 | 96.00% | PASS |
| unknown | JSS-WIDTH-001 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 209 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 197 | 2 | 0 | 98.99% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-CITE-002`: tp +159→169 (+10), fp +14→15 (+1), pending 0→0 (+0)
- `JSS-CITE-003`: tp +9→11 (+2), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-ABBR-001`: tp +6→8 (+2), fp +0→1 (+1), pending 0→0 (+0)
- `JSS-BIBTEX-002`: tp +5→6 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-BIBTEX-003`: tp +20→23 (+3), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-BIBTEX-004`: tp +55→61 (+6), fp +0→2 (+2), pending 0→0 (+0)
- `JSS-CAP-001`: tp +1→3 (+2), fp +0→1 (+1), pending 0→0 (+0)
- `JSS-CAP-002`: tp +125→130 (+5), fp +10→12 (+2), pending 0→0 (+0)
- `JSS-CAP-003`: tp +19→19 (+0), fp +27→31 (+4), pending 0→0 (+0)
- `JSS-CODE-001`: tp +18→21 (+3), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-CODE-002`: tp +1→5 (+4), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-CODE-003`: tp +144→169 (+25), fp +2→5 (+3), pending 0→0 (+0)
- `JSS-HOUSE-001`: tp +362→395 (+33), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-HOUSE-002`: tp +11→16 (+5), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-HOUSE-003`: tp +21→26 (+5), fp +0→2 (+2), pending 0→0 (+0)
- `JSS-MARKUP-001`: tp +924→953 (+29), fp +88→95 (+7), pending 0→0 (+0)
- `JSS-MARKUP-003`: tp +243→250 (+7), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-MARKUP-004`: tp +121→124 (+3), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-NAME-002`: tp +62→66 (+4), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-OPER-001`: tp +62→68 (+6), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-OPER-002`: tp +48→50 (+2), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-OPER-004`: tp +94→95 (+1), fp +7→7 (+0), pending 0→0 (+0)
- `JSS-PRE-001`: tp +52→53 (+1), fp +0→0 (+0), pending 0→0 (+0)
- **new** `JSS-PRE-004`: tp=1 fp=0 pending=0
- **new** `JSS-PRE-005`: tp=1 fp=0 pending=0
- `JSS-REFS-003`: tp +947→1143 (+196), fp +35→38 (+3), pending 0→0 (+0)
- `JSS-REFS-004`: tp +166→190 (+24), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-REFS-005`: tp +30→33 (+3), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-REFS-006`: tp +118→130 (+12), fp +2→2 (+0), pending 0→0 (+0)
- `JSS-REFS-007`: tp +78→87 (+9), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-STRUCT-001`: tp +50→56 (+6), fp +1→2 (+1), pending 0→0 (+0)
- `JSS-STRUCT-002`: tp +19→22 (+3), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-STRUCT-006`: tp +2→3 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-TYPO-001`: tp +61→86 (+25), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-WIDTH-001`: tp +15→21 (+6), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-XREF-001`: tp +27→32 (+5), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-XREF-002`: tp +229→290 (+61), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-XREF-004`: tp +206→259 (+53), fp +1→3 (+2), pending 0→0 (+0)

**Pinned only**

- `JSS-CITE-002`: tp +55→63 (+8), fp +11→12 (+1), pending 0→0 (+0)
- `JSS-CITE-003`: tp +4→6 (+2), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-ABBR-001`: tp +4→6 (+2), fp +0→1 (+1), pending 0→0 (+0)
- `JSS-BIBTEX-002`: tp +5→6 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-BIBTEX-003`: tp +20→23 (+3), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-BIBTEX-004`: tp +41→47 (+6), fp +0→2 (+2), pending 0→0 (+0)
- **new** `JSS-CAP-001`: tp=2 fp=0 pending=0
- `JSS-CAP-002`: tp +69→74 (+5), fp +5→7 (+2), pending 0→0 (+0)
- `JSS-CAP-003`: tp +13→13 (+0), fp +18→21 (+3), pending 0→0 (+0)
- `JSS-CODE-001`: tp +13→16 (+3), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-CODE-002`: tp +1→5 (+4), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-CODE-003`: tp +88→107 (+19), fp +2→5 (+3), pending 0→0 (+0)
- `JSS-HOUSE-001`: tp +109→130 (+21), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-HOUSE-002`: tp +11→16 (+5), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-HOUSE-003`: tp +18→22 (+4), fp +0→2 (+2), pending 0→0 (+0)
- `JSS-MARKUP-001`: tp +353→381 (+28), fp +42→49 (+7), pending 0→0 (+0)
- `JSS-MARKUP-003`: tp +93→100 (+7), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-MARKUP-004`: tp +28→31 (+3), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-NAME-002`: tp +62→66 (+4), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-OPER-001`: tp +14→20 (+6), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-OPER-004`: tp +73→74 (+1), fp +7→7 (+0), pending 0→0 (+0)
- `JSS-PRE-001`: tp +13→14 (+1), fp +0→0 (+0), pending 0→0 (+0)
- **new** `JSS-PRE-004`: tp=1 fp=0 pending=0
- **new** `JSS-PRE-005`: tp=1 fp=0 pending=0
- `JSS-REFS-003`: tp +947→1143 (+196), fp +35→38 (+3), pending 0→0 (+0)
- `JSS-REFS-004`: tp +166→190 (+24), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-REFS-005`: tp +30→33 (+3), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-REFS-006`: tp +118→130 (+12), fp +2→2 (+0), pending 0→0 (+0)
- `JSS-REFS-007`: tp +78→87 (+9), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-STRUCT-001`: tp +21→26 (+5), fp +0→1 (+1), pending 0→0 (+0)
- `JSS-STRUCT-002`: tp +13→15 (+2), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-STRUCT-006`: tp +1→2 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-TYPO-001`: tp +40→45 (+5), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-WIDTH-001`: tp +10→16 (+6), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-XREF-001`: tp +15→20 (+5), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-XREF-002`: tp +148→209 (+61), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-XREF-004`: tp +152→197 (+45), fp +0→2 (+2), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 64 — 2026-05-01T06:42:45Z — post-JSS-CAP-001

- **Corpus size:** 172 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=48, pinned=40

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 169 | 15 | 0 | 91.85% | PASS |
| citation | JSS-CITE-003 | 11 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-BIBTEX-002 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 23 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 61 | 2 | 0 | 96.83% | PASS |
| unknown | JSS-CAP-001 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 130 | 12 | 0 | 91.55% | PASS |
| unknown | JSS-CAP-003 | 19 | 31 | 0 | 38.00% | FAIL |
| unknown | JSS-CAP-004 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 21 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 169 | 5 | 0 | 97.13% | PASS |
| unknown | JSS-HOUSE-001 | 395 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 26 | 2 | 0 | 92.86% | PASS |
| unknown | JSS-MARKUP-001 | 953 | 95 | 0 | 90.94% | PASS |
| unknown | JSS-MARKUP-002 | 217 | 15 | 0 | 93.53% | PASS |
| unknown | JSS-MARKUP-003 | 250 | 1 | 0 | 99.60% | PASS |
| unknown | JSS-MARKUP-004 | 124 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-001 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 66 | 1 | 0 | 98.51% | PASS |
| unknown | JSS-OPER-001 | 68 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-002 | 50 | 1 | 0 | 98.04% | PASS |
| unknown | JSS-OPER-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 95 | 7 | 0 | 93.14% | PASS |
| unknown | JSS-PRE-001 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-004 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-005 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 1143 | 38 | 0 | 96.78% | PASS |
| unknown | JSS-REFS-004 | 190 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 33 | 1 | 0 | 97.06% | PASS |
| unknown | JSS-REFS-006 | 130 | 2 | 0 | 98.48% | PASS |
| unknown | JSS-REFS-007 | 87 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 56 | 2 | 0 | 96.55% | PASS |
| unknown | JSS-STRUCT-002 | 22 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 86 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 3 | 0 | 88.89% | FAIL |
| unknown | JSS-WIDTH-001 | 21 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 32 | 1 | 0 | 96.97% | PASS |
| unknown | JSS-XREF-002 | 290 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 259 | 3 | 0 | 98.85% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 63 | 12 | 0 | 84.00% | FAIL |
| citation | JSS-CITE-003 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 6 | 1 | 0 | 85.71% | FAIL |
| unknown | JSS-BIBTEX-002 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 23 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 47 | 2 | 0 | 95.92% | PASS |
| unknown | JSS-CAP-001 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 74 | 7 | 0 | 91.36% | PASS |
| unknown | JSS-CAP-003 | 13 | 21 | 0 | 38.24% | FAIL |
| unknown | JSS-CAP-004 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 107 | 5 | 0 | 95.54% | PASS |
| unknown | JSS-HOUSE-001 | 130 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 22 | 2 | 0 | 91.67% | PASS |
| unknown | JSS-MARKUP-001 | 381 | 49 | 0 | 88.60% | FAIL |
| unknown | JSS-MARKUP-002 | 103 | 3 | 0 | 97.17% | PASS |
| unknown | JSS-MARKUP-003 | 100 | 1 | 0 | 99.01% | PASS |
| unknown | JSS-MARKUP-004 | 31 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 66 | 1 | 0 | 98.51% | PASS |
| unknown | JSS-OPER-001 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-002 | 33 | 1 | 0 | 97.06% | PASS |
| unknown | JSS-OPER-004 | 74 | 7 | 0 | 91.36% | PASS |
| unknown | JSS-PRE-001 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-004 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-005 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 1143 | 38 | 0 | 96.78% | PASS |
| unknown | JSS-REFS-004 | 190 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 33 | 1 | 0 | 97.06% | PASS |
| unknown | JSS-REFS-006 | 130 | 2 | 0 | 98.48% | PASS |
| unknown | JSS-REFS-007 | 87 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 26 | 1 | 0 | 96.30% | PASS |
| unknown | JSS-STRUCT-002 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 45 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 1 | 0 | 96.00% | PASS |
| unknown | JSS-WIDTH-001 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 209 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 197 | 2 | 0 | 98.99% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-CAP-001`: tp +3→3 (+0), fp +1→0 (-1), pending 0→0 (+0)

**Pinned only**

_(no rule-level changes)_

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 65 — 2026-05-01T06:49:34Z — post-JSS-XREF-004

- **Corpus size:** 172 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=48, pinned=40

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 169 | 15 | 0 | 91.85% | PASS |
| citation | JSS-CITE-003 | 11 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-BIBTEX-002 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 23 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 61 | 2 | 0 | 96.83% | PASS |
| unknown | JSS-CAP-001 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 130 | 12 | 0 | 91.55% | PASS |
| unknown | JSS-CAP-003 | 19 | 31 | 0 | 38.00% | FAIL |
| unknown | JSS-CAP-004 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 21 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 169 | 5 | 0 | 97.13% | PASS |
| unknown | JSS-HOUSE-001 | 395 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 26 | 2 | 0 | 92.86% | PASS |
| unknown | JSS-MARKUP-001 | 953 | 95 | 0 | 90.94% | PASS |
| unknown | JSS-MARKUP-002 | 217 | 15 | 0 | 93.53% | PASS |
| unknown | JSS-MARKUP-003 | 250 | 1 | 0 | 99.60% | PASS |
| unknown | JSS-MARKUP-004 | 124 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-001 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 66 | 1 | 0 | 98.51% | PASS |
| unknown | JSS-OPER-001 | 68 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-002 | 50 | 1 | 0 | 98.04% | PASS |
| unknown | JSS-OPER-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 95 | 7 | 0 | 93.14% | PASS |
| unknown | JSS-PRE-001 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-004 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-005 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 1143 | 38 | 0 | 96.78% | PASS |
| unknown | JSS-REFS-004 | 190 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 33 | 1 | 0 | 97.06% | PASS |
| unknown | JSS-REFS-006 | 130 | 2 | 0 | 98.48% | PASS |
| unknown | JSS-REFS-007 | 87 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 56 | 2 | 0 | 96.55% | PASS |
| unknown | JSS-STRUCT-002 | 22 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 86 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 3 | 0 | 88.89% | FAIL |
| unknown | JSS-WIDTH-001 | 21 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 32 | 1 | 0 | 96.97% | PASS |
| unknown | JSS-XREF-002 | 290 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 254 | 1 | 0 | 99.61% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 63 | 12 | 0 | 84.00% | FAIL |
| citation | JSS-CITE-003 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 6 | 1 | 0 | 85.71% | FAIL |
| unknown | JSS-BIBTEX-002 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 23 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 47 | 2 | 0 | 95.92% | PASS |
| unknown | JSS-CAP-001 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 74 | 7 | 0 | 91.36% | PASS |
| unknown | JSS-CAP-003 | 13 | 21 | 0 | 38.24% | FAIL |
| unknown | JSS-CAP-004 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 107 | 5 | 0 | 95.54% | PASS |
| unknown | JSS-HOUSE-001 | 130 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 22 | 2 | 0 | 91.67% | PASS |
| unknown | JSS-MARKUP-001 | 381 | 49 | 0 | 88.60% | FAIL |
| unknown | JSS-MARKUP-002 | 103 | 3 | 0 | 97.17% | PASS |
| unknown | JSS-MARKUP-003 | 100 | 1 | 0 | 99.01% | PASS |
| unknown | JSS-MARKUP-004 | 31 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 66 | 1 | 0 | 98.51% | PASS |
| unknown | JSS-OPER-001 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-002 | 33 | 1 | 0 | 97.06% | PASS |
| unknown | JSS-OPER-004 | 74 | 7 | 0 | 91.36% | PASS |
| unknown | JSS-PRE-001 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-004 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-005 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 1143 | 38 | 0 | 96.78% | PASS |
| unknown | JSS-REFS-004 | 190 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 33 | 1 | 0 | 97.06% | PASS |
| unknown | JSS-REFS-006 | 130 | 2 | 0 | 98.48% | PASS |
| unknown | JSS-REFS-007 | 87 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 26 | 1 | 0 | 96.30% | PASS |
| unknown | JSS-STRUCT-002 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 45 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 1 | 0 | 96.00% | PASS |
| unknown | JSS-WIDTH-001 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 209 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 195 | 1 | 0 | 99.49% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-XREF-004`: tp +259→254 (-5), fp +3→1 (-2), pending 0→0 (+0)

**Pinned only**

- `JSS-XREF-004`: tp +197→195 (-2), fp +2→1 (-1), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 66 — 2026-05-01T06:53:36Z — post-JSS-CODE-003

- **Corpus size:** 172 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=48, pinned=40

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 169 | 15 | 0 | 91.85% | PASS |
| citation | JSS-CITE-003 | 11 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-BIBTEX-002 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 23 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 61 | 2 | 0 | 96.83% | PASS |
| unknown | JSS-CAP-001 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 130 | 12 | 0 | 91.55% | PASS |
| unknown | JSS-CAP-003 | 19 | 31 | 0 | 38.00% | FAIL |
| unknown | JSS-CAP-004 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 21 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 108 | 2 | 0 | 98.18% | PASS |
| unknown | JSS-HOUSE-001 | 395 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 26 | 2 | 0 | 92.86% | PASS |
| unknown | JSS-MARKUP-001 | 953 | 95 | 0 | 90.94% | PASS |
| unknown | JSS-MARKUP-002 | 217 | 15 | 0 | 93.53% | PASS |
| unknown | JSS-MARKUP-003 | 250 | 1 | 0 | 99.60% | PASS |
| unknown | JSS-MARKUP-004 | 124 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-001 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 66 | 1 | 0 | 98.51% | PASS |
| unknown | JSS-OPER-001 | 68 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-002 | 50 | 1 | 0 | 98.04% | PASS |
| unknown | JSS-OPER-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 95 | 7 | 0 | 93.14% | PASS |
| unknown | JSS-PRE-001 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-004 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-005 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 1143 | 38 | 0 | 96.78% | PASS |
| unknown | JSS-REFS-004 | 190 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 33 | 1 | 0 | 97.06% | PASS |
| unknown | JSS-REFS-006 | 130 | 2 | 0 | 98.48% | PASS |
| unknown | JSS-REFS-007 | 87 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 56 | 2 | 0 | 96.55% | PASS |
| unknown | JSS-STRUCT-002 | 22 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 86 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 3 | 0 | 88.89% | FAIL |
| unknown | JSS-WIDTH-001 | 21 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 32 | 1 | 0 | 96.97% | PASS |
| unknown | JSS-XREF-002 | 290 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 254 | 1 | 0 | 99.61% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 63 | 12 | 0 | 84.00% | FAIL |
| citation | JSS-CITE-003 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 6 | 1 | 0 | 85.71% | FAIL |
| unknown | JSS-BIBTEX-002 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 23 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 47 | 2 | 0 | 95.92% | PASS |
| unknown | JSS-CAP-001 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 74 | 7 | 0 | 91.36% | PASS |
| unknown | JSS-CAP-003 | 13 | 21 | 0 | 38.24% | FAIL |
| unknown | JSS-CAP-004 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 64 | 2 | 0 | 96.97% | PASS |
| unknown | JSS-HOUSE-001 | 130 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 22 | 2 | 0 | 91.67% | PASS |
| unknown | JSS-MARKUP-001 | 381 | 49 | 0 | 88.60% | FAIL |
| unknown | JSS-MARKUP-002 | 103 | 3 | 0 | 97.17% | PASS |
| unknown | JSS-MARKUP-003 | 100 | 1 | 0 | 99.01% | PASS |
| unknown | JSS-MARKUP-004 | 31 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 66 | 1 | 0 | 98.51% | PASS |
| unknown | JSS-OPER-001 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-002 | 33 | 1 | 0 | 97.06% | PASS |
| unknown | JSS-OPER-004 | 74 | 7 | 0 | 91.36% | PASS |
| unknown | JSS-PRE-001 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-004 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-005 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 1143 | 38 | 0 | 96.78% | PASS |
| unknown | JSS-REFS-004 | 190 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 33 | 1 | 0 | 97.06% | PASS |
| unknown | JSS-REFS-006 | 130 | 2 | 0 | 98.48% | PASS |
| unknown | JSS-REFS-007 | 87 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 26 | 1 | 0 | 96.30% | PASS |
| unknown | JSS-STRUCT-002 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 45 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 1 | 0 | 96.00% | PASS |
| unknown | JSS-WIDTH-001 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 209 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 195 | 1 | 0 | 99.49% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-CODE-003`: tp +169→108 (-61), fp +5→2 (-3), pending 0→0 (+0)

**Pinned only**

- `JSS-CODE-003`: tp +107→64 (-43), fp +5→2 (-3), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 67 — 2026-05-01T07:00:38Z — post-JSS-MARKUP-001

- **Corpus size:** 172 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=48, pinned=40

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 169 | 15 | 0 | 91.85% | PASS |
| citation | JSS-CITE-003 | 11 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-BIBTEX-002 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 23 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 61 | 2 | 0 | 96.83% | PASS |
| unknown | JSS-CAP-001 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 130 | 12 | 0 | 91.55% | PASS |
| unknown | JSS-CAP-003 | 19 | 31 | 0 | 38.00% | FAIL |
| unknown | JSS-CAP-004 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 21 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 108 | 2 | 0 | 98.18% | PASS |
| unknown | JSS-HOUSE-001 | 395 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 26 | 2 | 0 | 92.86% | PASS |
| unknown | JSS-MARKUP-001 | 943 | 90 | 0 | 91.29% | PASS |
| unknown | JSS-MARKUP-002 | 217 | 15 | 0 | 93.53% | PASS |
| unknown | JSS-MARKUP-003 | 250 | 1 | 0 | 99.60% | PASS |
| unknown | JSS-MARKUP-004 | 124 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-001 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 66 | 1 | 0 | 98.51% | PASS |
| unknown | JSS-OPER-001 | 68 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-002 | 50 | 1 | 0 | 98.04% | PASS |
| unknown | JSS-OPER-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 95 | 7 | 0 | 93.14% | PASS |
| unknown | JSS-PRE-001 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-004 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-005 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 1143 | 38 | 0 | 96.78% | PASS |
| unknown | JSS-REFS-004 | 190 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 33 | 1 | 0 | 97.06% | PASS |
| unknown | JSS-REFS-006 | 130 | 2 | 0 | 98.48% | PASS |
| unknown | JSS-REFS-007 | 87 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 56 | 2 | 0 | 96.55% | PASS |
| unknown | JSS-STRUCT-002 | 22 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 86 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 3 | 0 | 88.89% | FAIL |
| unknown | JSS-WIDTH-001 | 21 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 32 | 1 | 0 | 96.97% | PASS |
| unknown | JSS-XREF-002 | 290 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 254 | 1 | 0 | 99.61% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 63 | 12 | 0 | 84.00% | FAIL |
| citation | JSS-CITE-003 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 6 | 1 | 0 | 85.71% | FAIL |
| unknown | JSS-BIBTEX-002 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 23 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 47 | 2 | 0 | 95.92% | PASS |
| unknown | JSS-CAP-001 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 74 | 7 | 0 | 91.36% | PASS |
| unknown | JSS-CAP-003 | 13 | 21 | 0 | 38.24% | FAIL |
| unknown | JSS-CAP-004 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 64 | 2 | 0 | 96.97% | PASS |
| unknown | JSS-HOUSE-001 | 130 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 22 | 2 | 0 | 91.67% | PASS |
| unknown | JSS-MARKUP-001 | 371 | 44 | 0 | 89.40% | FAIL |
| unknown | JSS-MARKUP-002 | 103 | 3 | 0 | 97.17% | PASS |
| unknown | JSS-MARKUP-003 | 100 | 1 | 0 | 99.01% | PASS |
| unknown | JSS-MARKUP-004 | 31 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 66 | 1 | 0 | 98.51% | PASS |
| unknown | JSS-OPER-001 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-002 | 33 | 1 | 0 | 97.06% | PASS |
| unknown | JSS-OPER-004 | 74 | 7 | 0 | 91.36% | PASS |
| unknown | JSS-PRE-001 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-004 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-005 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 1143 | 38 | 0 | 96.78% | PASS |
| unknown | JSS-REFS-004 | 190 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 33 | 1 | 0 | 97.06% | PASS |
| unknown | JSS-REFS-006 | 130 | 2 | 0 | 98.48% | PASS |
| unknown | JSS-REFS-007 | 87 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 26 | 1 | 0 | 96.30% | PASS |
| unknown | JSS-STRUCT-002 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 45 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 1 | 0 | 96.00% | PASS |
| unknown | JSS-WIDTH-001 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 209 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 195 | 1 | 0 | 99.49% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-MARKUP-001`: tp +953→943 (-10), fp +95→90 (-5), pending 0→0 (+0)

**Pinned only**

- `JSS-MARKUP-001`: tp +381→371 (-10), fp +49→44 (-5), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 68 — 2026-05-01T11:38:21Z — post-JSS-OPER-004

- **Corpus size:** 172 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=48, pinned=40

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 169 | 15 | 0 | 91.85% | PASS |
| citation | JSS-CITE-003 | 11 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-BIBTEX-002 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 23 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 61 | 2 | 0 | 96.83% | PASS |
| unknown | JSS-CAP-001 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 130 | 12 | 0 | 91.55% | PASS |
| unknown | JSS-CAP-003 | 19 | 31 | 0 | 38.00% | FAIL |
| unknown | JSS-CAP-004 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 21 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 108 | 2 | 0 | 98.18% | PASS |
| unknown | JSS-HOUSE-001 | 395 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 26 | 2 | 0 | 92.86% | PASS |
| unknown | JSS-MARKUP-001 | 943 | 90 | 0 | 91.29% | PASS |
| unknown | JSS-MARKUP-002 | 217 | 15 | 0 | 93.53% | PASS |
| unknown | JSS-MARKUP-003 | 250 | 1 | 0 | 99.60% | PASS |
| unknown | JSS-MARKUP-004 | 124 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-001 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 66 | 1 | 0 | 98.51% | PASS |
| unknown | JSS-OPER-001 | 68 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-002 | 50 | 1 | 0 | 98.04% | PASS |
| unknown | JSS-OPER-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 50 | 1 | 0 | 98.04% | PASS |
| unknown | JSS-PRE-001 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-004 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-005 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 1143 | 38 | 0 | 96.78% | PASS |
| unknown | JSS-REFS-004 | 190 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 33 | 1 | 0 | 97.06% | PASS |
| unknown | JSS-REFS-006 | 130 | 2 | 0 | 98.48% | PASS |
| unknown | JSS-REFS-007 | 87 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 56 | 2 | 0 | 96.55% | PASS |
| unknown | JSS-STRUCT-002 | 22 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 86 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 3 | 0 | 88.89% | FAIL |
| unknown | JSS-WIDTH-001 | 21 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 32 | 1 | 0 | 96.97% | PASS |
| unknown | JSS-XREF-002 | 290 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 254 | 1 | 0 | 99.61% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 63 | 12 | 0 | 84.00% | FAIL |
| citation | JSS-CITE-003 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 6 | 1 | 0 | 85.71% | FAIL |
| unknown | JSS-BIBTEX-002 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 23 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 47 | 2 | 0 | 95.92% | PASS |
| unknown | JSS-CAP-001 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 74 | 7 | 0 | 91.36% | PASS |
| unknown | JSS-CAP-003 | 13 | 21 | 0 | 38.24% | FAIL |
| unknown | JSS-CAP-004 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 64 | 2 | 0 | 96.97% | PASS |
| unknown | JSS-HOUSE-001 | 130 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 22 | 2 | 0 | 91.67% | PASS |
| unknown | JSS-MARKUP-001 | 371 | 44 | 0 | 89.40% | FAIL |
| unknown | JSS-MARKUP-002 | 103 | 3 | 0 | 97.17% | PASS |
| unknown | JSS-MARKUP-003 | 100 | 1 | 0 | 99.01% | PASS |
| unknown | JSS-MARKUP-004 | 31 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 66 | 1 | 0 | 98.51% | PASS |
| unknown | JSS-OPER-001 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-002 | 33 | 1 | 0 | 97.06% | PASS |
| unknown | JSS-OPER-004 | 42 | 1 | 0 | 97.67% | PASS |
| unknown | JSS-PRE-001 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-004 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-005 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 1143 | 38 | 0 | 96.78% | PASS |
| unknown | JSS-REFS-004 | 190 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 33 | 1 | 0 | 97.06% | PASS |
| unknown | JSS-REFS-006 | 130 | 2 | 0 | 98.48% | PASS |
| unknown | JSS-REFS-007 | 87 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 26 | 1 | 0 | 96.30% | PASS |
| unknown | JSS-STRUCT-002 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 45 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 1 | 0 | 96.00% | PASS |
| unknown | JSS-WIDTH-001 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 209 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 195 | 1 | 0 | 99.49% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-OPER-004`: tp +95→50 (-45), fp +7→1 (-6), pending 0→0 (+0)

**Pinned only**

- `JSS-OPER-004`: tp +74→42 (-32), fp +7→1 (-6), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 69 — 2026-05-01T11:41:26Z — post-CAP-002-months-refactor

- **Corpus size:** 172 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=48, pinned=40

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 169 | 15 | 0 | 91.85% | PASS |
| citation | JSS-CITE-003 | 11 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-BIBTEX-002 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 23 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 61 | 2 | 0 | 96.83% | PASS |
| unknown | JSS-CAP-001 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 181 | 12 | 0 | 93.78% | PASS |
| unknown | JSS-CAP-003 | 19 | 31 | 0 | 38.00% | FAIL |
| unknown | JSS-CAP-004 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 21 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 108 | 2 | 0 | 98.18% | PASS |
| unknown | JSS-HOUSE-001 | 395 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 26 | 2 | 0 | 92.86% | PASS |
| unknown | JSS-MARKUP-001 | 943 | 90 | 0 | 91.29% | PASS |
| unknown | JSS-MARKUP-002 | 217 | 15 | 0 | 93.53% | PASS |
| unknown | JSS-MARKUP-003 | 250 | 1 | 0 | 99.60% | PASS |
| unknown | JSS-MARKUP-004 | 124 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-001 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 66 | 1 | 0 | 98.51% | PASS |
| unknown | JSS-OPER-001 | 68 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-002 | 50 | 1 | 0 | 98.04% | PASS |
| unknown | JSS-OPER-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 50 | 1 | 0 | 98.04% | PASS |
| unknown | JSS-PRE-001 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-004 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-005 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 1143 | 38 | 0 | 96.78% | PASS |
| unknown | JSS-REFS-004 | 190 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 33 | 1 | 0 | 97.06% | PASS |
| unknown | JSS-REFS-006 | 130 | 2 | 0 | 98.48% | PASS |
| unknown | JSS-REFS-007 | 87 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 56 | 2 | 0 | 96.55% | PASS |
| unknown | JSS-STRUCT-002 | 22 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 86 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 3 | 0 | 88.89% | FAIL |
| unknown | JSS-WIDTH-001 | 21 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 32 | 1 | 0 | 96.97% | PASS |
| unknown | JSS-XREF-002 | 290 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 254 | 1 | 0 | 99.61% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 63 | 12 | 0 | 84.00% | FAIL |
| citation | JSS-CITE-003 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 6 | 1 | 0 | 85.71% | FAIL |
| unknown | JSS-BIBTEX-002 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 23 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 47 | 2 | 0 | 95.92% | PASS |
| unknown | JSS-CAP-001 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 74 | 7 | 0 | 91.36% | PASS |
| unknown | JSS-CAP-003 | 13 | 21 | 0 | 38.24% | FAIL |
| unknown | JSS-CAP-004 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 64 | 2 | 0 | 96.97% | PASS |
| unknown | JSS-HOUSE-001 | 130 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 22 | 2 | 0 | 91.67% | PASS |
| unknown | JSS-MARKUP-001 | 371 | 44 | 0 | 89.40% | FAIL |
| unknown | JSS-MARKUP-002 | 103 | 3 | 0 | 97.17% | PASS |
| unknown | JSS-MARKUP-003 | 100 | 1 | 0 | 99.01% | PASS |
| unknown | JSS-MARKUP-004 | 31 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 66 | 1 | 0 | 98.51% | PASS |
| unknown | JSS-OPER-001 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-002 | 33 | 1 | 0 | 97.06% | PASS |
| unknown | JSS-OPER-004 | 42 | 1 | 0 | 97.67% | PASS |
| unknown | JSS-PRE-001 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-004 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-005 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 1143 | 38 | 0 | 96.78% | PASS |
| unknown | JSS-REFS-004 | 190 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 33 | 1 | 0 | 97.06% | PASS |
| unknown | JSS-REFS-006 | 130 | 2 | 0 | 98.48% | PASS |
| unknown | JSS-REFS-007 | 87 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 26 | 1 | 0 | 96.30% | PASS |
| unknown | JSS-STRUCT-002 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 45 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 1 | 0 | 96.00% | PASS |
| unknown | JSS-WIDTH-001 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 209 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 195 | 1 | 0 | 99.49% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-CAP-002`: tp +130→181 (+51), fp +12→12 (+0), pending 0→0 (+0)

**Pinned only**

_(no rule-level changes)_

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 70 — 2026-05-01T11:45:01Z — post-JSS-CITE-002

- **Corpus size:** 172 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=48, pinned=40

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 169 | 13 | 0 | 92.86% | PASS |
| citation | JSS-CITE-003 | 11 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-BIBTEX-002 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 23 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 61 | 2 | 0 | 96.83% | PASS |
| unknown | JSS-CAP-001 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 181 | 12 | 0 | 93.78% | PASS |
| unknown | JSS-CAP-003 | 19 | 31 | 0 | 38.00% | FAIL |
| unknown | JSS-CAP-004 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 21 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 108 | 2 | 0 | 98.18% | PASS |
| unknown | JSS-HOUSE-001 | 395 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 26 | 2 | 0 | 92.86% | PASS |
| unknown | JSS-MARKUP-001 | 943 | 90 | 0 | 91.29% | PASS |
| unknown | JSS-MARKUP-002 | 217 | 15 | 0 | 93.53% | PASS |
| unknown | JSS-MARKUP-003 | 250 | 1 | 0 | 99.60% | PASS |
| unknown | JSS-MARKUP-004 | 124 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-001 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 66 | 1 | 0 | 98.51% | PASS |
| unknown | JSS-OPER-001 | 68 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-002 | 50 | 1 | 0 | 98.04% | PASS |
| unknown | JSS-OPER-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 50 | 1 | 0 | 98.04% | PASS |
| unknown | JSS-PRE-001 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-004 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-005 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 1143 | 38 | 0 | 96.78% | PASS |
| unknown | JSS-REFS-004 | 190 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 33 | 1 | 0 | 97.06% | PASS |
| unknown | JSS-REFS-006 | 130 | 2 | 0 | 98.48% | PASS |
| unknown | JSS-REFS-007 | 87 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 56 | 2 | 0 | 96.55% | PASS |
| unknown | JSS-STRUCT-002 | 22 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 86 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 3 | 0 | 88.89% | FAIL |
| unknown | JSS-WIDTH-001 | 21 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 32 | 1 | 0 | 96.97% | PASS |
| unknown | JSS-XREF-002 | 290 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 254 | 1 | 0 | 99.61% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 63 | 11 | 0 | 85.14% | FAIL |
| citation | JSS-CITE-003 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 6 | 1 | 0 | 85.71% | FAIL |
| unknown | JSS-BIBTEX-002 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 23 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 47 | 2 | 0 | 95.92% | PASS |
| unknown | JSS-CAP-001 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 74 | 7 | 0 | 91.36% | PASS |
| unknown | JSS-CAP-003 | 13 | 21 | 0 | 38.24% | FAIL |
| unknown | JSS-CAP-004 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 64 | 2 | 0 | 96.97% | PASS |
| unknown | JSS-HOUSE-001 | 130 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-002 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 22 | 2 | 0 | 91.67% | PASS |
| unknown | JSS-MARKUP-001 | 371 | 44 | 0 | 89.40% | FAIL |
| unknown | JSS-MARKUP-002 | 103 | 3 | 0 | 97.17% | PASS |
| unknown | JSS-MARKUP-003 | 100 | 1 | 0 | 99.01% | PASS |
| unknown | JSS-MARKUP-004 | 31 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 66 | 1 | 0 | 98.51% | PASS |
| unknown | JSS-OPER-001 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-002 | 33 | 1 | 0 | 97.06% | PASS |
| unknown | JSS-OPER-004 | 42 | 1 | 0 | 97.67% | PASS |
| unknown | JSS-PRE-001 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-004 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-005 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 1143 | 38 | 0 | 96.78% | PASS |
| unknown | JSS-REFS-004 | 190 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 33 | 1 | 0 | 97.06% | PASS |
| unknown | JSS-REFS-006 | 130 | 2 | 0 | 98.48% | PASS |
| unknown | JSS-REFS-007 | 87 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 26 | 1 | 0 | 96.30% | PASS |
| unknown | JSS-STRUCT-002 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 45 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 1 | 0 | 96.00% | PASS |
| unknown | JSS-WIDTH-001 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 209 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 195 | 1 | 0 | 99.49% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-CITE-002`: tp +169→169 (+0), fp +15→13 (-2), pending 0→0 (+0)

**Pinned only**

- `JSS-CITE-002`: tp +63→63 (+0), fp +12→11 (-1), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 71 — 2026-05-01T17:45:16Z — iter-71-baseline

- **Corpus size:** 222 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=67, pinned=56

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 191 | 19 | 0 | 90.95% | PASS |
| citation | JSS-CITE-003 | 11 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 11 | 1 | 0 | 91.67% | PASS |
| unknown | JSS-BIBTEX-002 | 9 | 2 | 0 | 81.82% | FAIL |
| unknown | JSS-BIBTEX-003 | 46 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 84 | 3 | 0 | 96.55% | PASS |
| unknown | JSS-CAP-001 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 215 | 21 | 0 | 91.10% | PASS |
| unknown | JSS-CAP-003 | 29 | 46 | 0 | 38.67% | FAIL |
| unknown | JSS-CAP-004 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 22 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 139 | 3 | 0 | 97.89% | PASS |
| unknown | JSS-HOUSE-001 | 511 | 1 | 0 | 99.80% | PASS |
| unknown | JSS-HOUSE-002 | 25 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 35 | 3 | 0 | 92.11% | PASS |
| unknown | JSS-MARKUP-001 | 1023 | 98 | 0 | 91.26% | PASS |
| unknown | JSS-MARKUP-002 | 225 | 15 | 0 | 93.75% | PASS |
| unknown | JSS-MARKUP-003 | 299 | 1 | 0 | 99.67% | PASS |
| unknown | JSS-MARKUP-004 | 136 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-001 | 8 | 2 | 0 | 80.00% | FAIL |
| unknown | JSS-NAME-002 | 105 | 1 | 0 | 99.06% | PASS |
| unknown | JSS-OPER-001 | 77 | 1 | 0 | 98.72% | PASS |
| unknown | JSS-OPER-002 | 70 | 1 | 0 | 98.59% | PASS |
| unknown | JSS-OPER-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 64 | 1 | 0 | 98.46% | PASS |
| unknown | JSS-PRE-001 | 63 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 1646 | 45 | 0 | 97.34% | PASS |
| unknown | JSS-REFS-004 | 230 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 36 | 1 | 0 | 97.30% | PASS |
| unknown | JSS-REFS-006 | 147 | 2 | 0 | 98.66% | PASS |
| unknown | JSS-REFS-007 | 123 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 73 | 2 | 0 | 97.33% | PASS |
| unknown | JSS-STRUCT-002 | 27 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 173 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 3 | 0 | 88.89% | FAIL |
| unknown | JSS-WIDTH-001 | 49 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 35 | 1 | 0 | 97.22% | PASS |
| unknown | JSS-XREF-002 | 453 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 338 | 1 | 0 | 99.71% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 81 | 17 | 0 | 82.65% | FAIL |
| citation | JSS-CITE-003 | 6 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-BIBTEX-002 | 9 | 2 | 0 | 81.82% | FAIL |
| unknown | JSS-BIBTEX-003 | 46 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 68 | 3 | 0 | 95.77% | PASS |
| unknown | JSS-CAP-001 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 98 | 16 | 0 | 85.96% | FAIL |
| unknown | JSS-CAP-003 | 20 | 29 | 0 | 40.82% | FAIL |
| unknown | JSS-CAP-004 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 17 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 88 | 3 | 0 | 96.70% | PASS |
| unknown | JSS-HOUSE-001 | 220 | 1 | 0 | 99.55% | PASS |
| unknown | JSS-HOUSE-002 | 25 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 28 | 3 | 0 | 90.32% | PASS |
| unknown | JSS-MARKUP-001 | 426 | 50 | 0 | 89.50% | FAIL |
| unknown | JSS-MARKUP-002 | 106 | 3 | 0 | 97.25% | PASS |
| unknown | JSS-MARKUP-003 | 124 | 1 | 0 | 99.20% | PASS |
| unknown | JSS-MARKUP-004 | 34 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 105 | 1 | 0 | 99.06% | PASS |
| unknown | JSS-OPER-001 | 26 | 1 | 0 | 96.30% | PASS |
| unknown | JSS-OPER-002 | 53 | 1 | 0 | 98.15% | PASS |
| unknown | JSS-OPER-004 | 53 | 1 | 0 | 98.15% | PASS |
| unknown | JSS-PRE-001 | 17 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 1646 | 45 | 0 | 97.34% | PASS |
| unknown | JSS-REFS-004 | 230 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 36 | 1 | 0 | 97.30% | PASS |
| unknown | JSS-REFS-006 | 147 | 2 | 0 | 98.66% | PASS |
| unknown | JSS-REFS-007 | 123 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 37 | 1 | 0 | 97.37% | PASS |
| unknown | JSS-STRUCT-002 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 86 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 1 | 0 | 96.00% | PASS |
| unknown | JSS-WIDTH-001 | 44 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 23 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 345 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 253 | 1 | 0 | 99.61% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-CITE-002`: tp +169→191 (+22), fp +13→19 (+6), pending 0→0 (+0)
- `JSS-CITE-004`: tp +18→20 (+2), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-ABBR-001`: tp +8→11 (+3), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-BIBTEX-002`: tp +6→9 (+3), fp +0→2 (+2), pending 0→0 (+0)
- `JSS-BIBTEX-003`: tp +23→46 (+23), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-BIBTEX-004`: tp +61→84 (+23), fp +2→3 (+1), pending 0→0 (+0)
- `JSS-CAP-002`: tp +181→215 (+34), fp +12→21 (+9), pending 0→0 (+0)
- `JSS-CAP-003`: tp +19→29 (+10), fp +31→46 (+15), pending 0→0 (+0)
- `JSS-CAP-004`: tp +7→15 (+8), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-CODE-001`: tp +21→22 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-CODE-002`: tp +5→7 (+2), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-CODE-003`: tp +108→139 (+31), fp +2→3 (+1), pending 0→0 (+0)
- `JSS-HOUSE-001`: tp +395→511 (+116), fp +0→1 (+1), pending 0→0 (+0)
- `JSS-HOUSE-002`: tp +16→25 (+9), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-HOUSE-003`: tp +26→35 (+9), fp +2→3 (+1), pending 0→0 (+0)
- `JSS-MARKUP-001`: tp +943→1023 (+80), fp +90→98 (+8), pending 0→0 (+0)
- `JSS-MARKUP-002`: tp +217→225 (+8), fp +15→15 (+0), pending 0→0 (+0)
- `JSS-MARKUP-003`: tp +250→299 (+49), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-MARKUP-004`: tp +124→136 (+12), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-NAME-001`: tp +2→8 (+6), fp +0→2 (+2), pending 0→0 (+0)
- `JSS-NAME-002`: tp +66→105 (+39), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-OPER-001`: tp +68→77 (+9), fp +0→1 (+1), pending 0→0 (+0)
- `JSS-OPER-002`: tp +50→70 (+20), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-OPER-004`: tp +50→64 (+14), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-PRE-001`: tp +53→63 (+10), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-PRE-004`: tp +1→4 (+3), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-PRE-005`: tp +1→4 (+3), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-PRE-006`: tp +6→15 (+9), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-REFS-003`: tp +1143→1646 (+503), fp +38→45 (+7), pending 0→0 (+0)
- `JSS-REFS-004`: tp +190→230 (+40), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-REFS-005`: tp +33→36 (+3), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-REFS-006`: tp +130→147 (+17), fp +2→2 (+0), pending 0→0 (+0)
- `JSS-REFS-007`: tp +87→123 (+36), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-STRUCT-001`: tp +56→73 (+17), fp +2→2 (+0), pending 0→0 (+0)
- `JSS-STRUCT-002`: tp +22→27 (+5), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-STRUCT-004`: tp +3→5 (+2), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-STRUCT-006`: tp +3→4 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-TYPO-001`: tp +86→173 (+87), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-WIDTH-001`: tp +21→49 (+28), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-XREF-001`: tp +32→35 (+3), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-XREF-002`: tp +290→453 (+163), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-XREF-004`: tp +254→338 (+84), fp +1→1 (+0), pending 0→0 (+0)

**Pinned only**

- `JSS-CITE-002`: tp +63→81 (+18), fp +11→17 (+6), pending 0→0 (+0)
- **new** `JSS-CITE-004`: tp=1 fp=0 pending=0
- `JSS-ABBR-001`: tp +6→8 (+2), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-BIBTEX-002`: tp +6→9 (+3), fp +0→2 (+2), pending 0→0 (+0)
- `JSS-BIBTEX-003`: tp +23→46 (+23), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-BIBTEX-004`: tp +47→68 (+21), fp +2→3 (+1), pending 0→0 (+0)
- `JSS-CAP-002`: tp +74→98 (+24), fp +7→16 (+9), pending 0→0 (+0)
- `JSS-CAP-003`: tp +13→20 (+7), fp +21→29 (+8), pending 0→0 (+0)
- `JSS-CAP-004`: tp +6→12 (+6), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-CODE-001`: tp +16→17 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-CODE-002`: tp +5→7 (+2), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-CODE-003`: tp +64→88 (+24), fp +2→3 (+1), pending 0→0 (+0)
- `JSS-HOUSE-001`: tp +130→220 (+90), fp +0→1 (+1), pending 0→0 (+0)
- `JSS-HOUSE-002`: tp +16→25 (+9), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-HOUSE-003`: tp +22→28 (+6), fp +2→3 (+1), pending 0→0 (+0)
- `JSS-MARKUP-001`: tp +371→426 (+55), fp +44→50 (+6), pending 0→0 (+0)
- `JSS-MARKUP-002`: tp +103→106 (+3), fp +3→3 (+0), pending 0→0 (+0)
- `JSS-MARKUP-003`: tp +100→124 (+24), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-MARKUP-004`: tp +31→34 (+3), fp +0→0 (+0), pending 0→0 (+0)
- **new** `JSS-NAME-001`: tp=1 fp=0 pending=0
- `JSS-NAME-002`: tp +66→105 (+39), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-OPER-001`: tp +20→26 (+6), fp +0→1 (+1), pending 0→0 (+0)
- `JSS-OPER-002`: tp +33→53 (+20), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-OPER-004`: tp +42→53 (+11), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-PRE-001`: tp +14→17 (+3), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-PRE-004`: tp +1→4 (+3), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-PRE-005`: tp +1→4 (+3), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-PRE-006`: tp +5→11 (+6), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-REFS-003`: tp +1143→1646 (+503), fp +38→45 (+7), pending 0→0 (+0)
- `JSS-REFS-004`: tp +190→230 (+40), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-REFS-005`: tp +33→36 (+3), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-REFS-006`: tp +130→147 (+17), fp +2→2 (+0), pending 0→0 (+0)
- `JSS-REFS-007`: tp +87→123 (+36), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-STRUCT-001`: tp +26→37 (+11), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-STRUCT-002`: tp +15→18 (+3), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-STRUCT-004`: tp +2→4 (+2), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-STRUCT-006`: tp +2→3 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-TYPO-001`: tp +45→86 (+41), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-WIDTH-001`: tp +16→44 (+28), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-XREF-001`: tp +20→23 (+3), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-XREF-002`: tp +209→345 (+136), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-XREF-004`: tp +195→253 (+58), fp +1→1 (+0), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 72 — 2026-05-03T16:55:39Z — post-JSS-CAP-003-eponyms

- **Corpus size:** 222 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=67, pinned=56

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 191 | 19 | 0 | 90.95% | PASS |
| citation | JSS-CITE-003 | 11 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 11 | 1 | 0 | 91.67% | PASS |
| unknown | JSS-BIBTEX-002 | 9 | 2 | 0 | 81.82% | FAIL |
| unknown | JSS-BIBTEX-003 | 46 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 84 | 3 | 0 | 96.55% | PASS |
| unknown | JSS-CAP-001 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 215 | 20 | 0 | 91.49% | PASS |
| unknown | JSS-CAP-003 | 29 | 34 | 0 | 46.03% | FAIL |
| unknown | JSS-CAP-004 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 22 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 139 | 3 | 0 | 97.89% | PASS |
| unknown | JSS-HOUSE-001 | 511 | 1 | 0 | 99.80% | PASS |
| unknown | JSS-HOUSE-002 | 25 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 35 | 3 | 0 | 92.11% | PASS |
| unknown | JSS-MARKUP-001 | 1023 | 98 | 0 | 91.26% | PASS |
| unknown | JSS-MARKUP-002 | 225 | 15 | 0 | 93.75% | PASS |
| unknown | JSS-MARKUP-003 | 299 | 1 | 0 | 99.67% | PASS |
| unknown | JSS-MARKUP-004 | 136 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-001 | 8 | 2 | 0 | 80.00% | FAIL |
| unknown | JSS-NAME-002 | 105 | 1 | 0 | 99.06% | PASS |
| unknown | JSS-OPER-001 | 77 | 1 | 0 | 98.72% | PASS |
| unknown | JSS-OPER-002 | 70 | 1 | 0 | 98.59% | PASS |
| unknown | JSS-OPER-003 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 64 | 1 | 0 | 98.46% | PASS |
| unknown | JSS-PRE-001 | 63 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 1646 | 45 | 0 | 97.34% | PASS |
| unknown | JSS-REFS-004 | 230 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 36 | 1 | 0 | 97.30% | PASS |
| unknown | JSS-REFS-006 | 147 | 2 | 0 | 98.66% | PASS |
| unknown | JSS-REFS-007 | 123 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 73 | 2 | 0 | 97.33% | PASS |
| unknown | JSS-STRUCT-002 | 27 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 173 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 3 | 0 | 88.89% | FAIL |
| unknown | JSS-WIDTH-001 | 49 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 35 | 1 | 0 | 97.22% | PASS |
| unknown | JSS-XREF-002 | 453 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 338 | 1 | 0 | 99.71% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 81 | 17 | 0 | 82.65% | FAIL |
| citation | JSS-CITE-003 | 6 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 8 | 1 | 0 | 88.89% | FAIL |
| unknown | JSS-BIBTEX-002 | 9 | 2 | 0 | 81.82% | FAIL |
| unknown | JSS-BIBTEX-003 | 46 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 68 | 3 | 0 | 95.77% | PASS |
| unknown | JSS-CAP-001 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 98 | 15 | 0 | 86.73% | FAIL |
| unknown | JSS-CAP-003 | 20 | 18 | 0 | 52.63% | FAIL |
| unknown | JSS-CAP-004 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 17 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 88 | 3 | 0 | 96.70% | PASS |
| unknown | JSS-HOUSE-001 | 220 | 1 | 0 | 99.55% | PASS |
| unknown | JSS-HOUSE-002 | 25 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 28 | 3 | 0 | 90.32% | PASS |
| unknown | JSS-MARKUP-001 | 426 | 50 | 0 | 89.50% | FAIL |
| unknown | JSS-MARKUP-002 | 106 | 3 | 0 | 97.25% | PASS |
| unknown | JSS-MARKUP-003 | 124 | 1 | 0 | 99.20% | PASS |
| unknown | JSS-MARKUP-004 | 34 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 105 | 1 | 0 | 99.06% | PASS |
| unknown | JSS-OPER-001 | 26 | 1 | 0 | 96.30% | PASS |
| unknown | JSS-OPER-002 | 53 | 1 | 0 | 98.15% | PASS |
| unknown | JSS-OPER-004 | 53 | 1 | 0 | 98.15% | PASS |
| unknown | JSS-PRE-001 | 17 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 1646 | 45 | 0 | 97.34% | PASS |
| unknown | JSS-REFS-004 | 230 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 36 | 1 | 0 | 97.30% | PASS |
| unknown | JSS-REFS-006 | 147 | 2 | 0 | 98.66% | PASS |
| unknown | JSS-REFS-007 | 123 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 37 | 1 | 0 | 97.37% | PASS |
| unknown | JSS-STRUCT-002 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 86 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 1 | 0 | 96.00% | PASS |
| unknown | JSS-WIDTH-001 | 44 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 23 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 345 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 253 | 1 | 0 | 99.61% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-CAP-002`: tp +215→215 (+0), fp +21→20 (-1), pending 0→0 (+0)
- `JSS-CAP-003`: tp +29→29 (+0), fp +46→34 (-12), pending 0→0 (+0)

**Pinned only**

- `JSS-CAP-002`: tp +98→98 (+0), fp +16→15 (-1), pending 0→0 (+0)
- `JSS-CAP-003`: tp +20→20 (+0), fp +29→18 (-11), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 73 — 2026-05-03T17:39:53Z — post-corpus-238

- **Corpus size:** 237 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=69, pinned=58

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 195 | 20 | 1 | 90.70% | PASS |
| citation | JSS-CITE-003 | 21 | 0 | 2 | 100.00% | PASS |
| citation | JSS-CITE-004 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 13 | 1 | 0 | 92.86% | PASS |
| unknown | JSS-BIBTEX-002 | 9 | 2 | 0 | 81.82% | FAIL |
| unknown | JSS-BIBTEX-003 | 46 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 88 | 3 | 5 | 96.70% | PASS |
| unknown | JSS-CAP-001 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 223 | 20 | 0 | 91.77% | PASS |
| unknown | JSS-CAP-003 | 29 | 34 | 13 | 46.03% | FAIL |
| unknown | JSS-CAP-004 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 30 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 149 | 3 | 0 | 98.03% | PASS |
| unknown | JSS-HOUSE-001 | 541 | 2 | 0 | 99.63% | PASS |
| unknown | JSS-HOUSE-002 | 27 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 40 | 3 | 0 | 93.02% | PASS |
| unknown | JSS-MARKUP-001 | 1034 | 105 | 4 | 90.78% | PASS |
| unknown | JSS-MARKUP-002 | 225 | 15 | 0 | 93.75% | PASS |
| unknown | JSS-MARKUP-003 | 366 | 2 | 7 | 99.46% | PASS |
| unknown | JSS-MARKUP-004 | 136 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-001 | 8 | 2 | 0 | 80.00% | FAIL |
| unknown | JSS-NAME-002 | 105 | 1 | 5 | 99.06% | PASS |
| unknown | JSS-OPER-001 | 81 | 1 | 0 | 98.78% | PASS |
| unknown | JSS-OPER-002 | 70 | 1 | 4 | 98.59% | PASS |
| unknown | JSS-OPER-003 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 68 | 1 | 2 | 98.55% | PASS |
| unknown | JSS-PRE-001 | 65 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 1755 | 46 | 0 | 97.45% | PASS |
| unknown | JSS-REFS-004 | 241 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 40 | 1 | 0 | 97.56% | PASS |
| unknown | JSS-REFS-006 | 150 | 2 | 0 | 98.68% | PASS |
| unknown | JSS-REFS-007 | 131 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 76 | 2 | 0 | 97.44% | PASS |
| unknown | JSS-STRUCT-002 | 28 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 198 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 3 | 0 | 88.89% | FAIL |
| unknown | JSS-WIDTH-001 | 52 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 35 | 1 | 1 | 97.22% | PASS |
| unknown | JSS-XREF-002 | 462 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 351 | 1 | 3 | 99.72% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 85 | 18 | 1 | 82.52% | FAIL |
| citation | JSS-CITE-003 | 16 | 0 | 2 | 100.00% | PASS |
| citation | JSS-CITE-004 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 10 | 1 | 0 | 90.91% | PASS |
| unknown | JSS-BIBTEX-002 | 9 | 2 | 0 | 81.82% | FAIL |
| unknown | JSS-BIBTEX-003 | 46 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 72 | 3 | 3 | 96.00% | PASS |
| unknown | JSS-CAP-001 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 103 | 15 | 0 | 87.29% | FAIL |
| unknown | JSS-CAP-003 | 20 | 18 | 13 | 52.63% | FAIL |
| unknown | JSS-CAP-004 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 25 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 98 | 3 | 0 | 97.03% | PASS |
| unknown | JSS-HOUSE-001 | 250 | 2 | 0 | 99.21% | PASS |
| unknown | JSS-HOUSE-002 | 27 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 33 | 3 | 0 | 91.67% | PASS |
| unknown | JSS-MARKUP-001 | 437 | 57 | 4 | 88.46% | FAIL |
| unknown | JSS-MARKUP-002 | 106 | 3 | 0 | 97.25% | PASS |
| unknown | JSS-MARKUP-003 | 191 | 2 | 7 | 98.96% | PASS |
| unknown | JSS-MARKUP-004 | 34 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 105 | 1 | 5 | 99.06% | PASS |
| unknown | JSS-OPER-001 | 27 | 1 | 0 | 96.43% | PASS |
| unknown | JSS-OPER-002 | 53 | 1 | 3 | 98.15% | PASS |
| unknown | JSS-OPER-003 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 55 | 1 | 0 | 98.21% | PASS |
| unknown | JSS-PRE-001 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 1755 | 46 | 0 | 97.45% | PASS |
| unknown | JSS-REFS-004 | 241 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 40 | 1 | 0 | 97.56% | PASS |
| unknown | JSS-REFS-006 | 150 | 2 | 0 | 98.68% | PASS |
| unknown | JSS-REFS-007 | 131 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 40 | 1 | 0 | 97.56% | PASS |
| unknown | JSS-STRUCT-002 | 19 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 110 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 1 | 0 | 96.00% | PASS |
| unknown | JSS-WIDTH-001 | 44 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 23 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 351 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 266 | 1 | 1 | 99.63% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-CITE-002`: tp +191→195 (+4), fp +19→20 (+1), pending 0→1 (+1)
- `JSS-CITE-003`: tp +11→21 (+10), fp +0→0 (+0), pending 0→2 (+2)
- `JSS-ABBR-001`: tp +11→13 (+2), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-BIBTEX-004`: tp +84→88 (+4), fp +3→3 (+0), pending 0→5 (+5)
- `JSS-CAP-002`: tp +215→223 (+8), fp +20→20 (+0), pending 0→0 (+0)
- `JSS-CAP-003`: tp +29→29 (+0), fp +34→34 (+0), pending 0→13 (+13)
- `JSS-CODE-001`: tp +22→30 (+8), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-CODE-002`: tp +7→14 (+7), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-CODE-003`: tp +139→149 (+10), fp +3→3 (+0), pending 0→0 (+0)
- `JSS-HOUSE-001`: tp +511→541 (+30), fp +1→2 (+1), pending 0→0 (+0)
- `JSS-HOUSE-002`: tp +25→27 (+2), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-HOUSE-003`: tp +35→40 (+5), fp +3→3 (+0), pending 0→0 (+0)
- `JSS-MARKUP-001`: tp +1023→1034 (+11), fp +98→105 (+7), pending 0→4 (+4)
- `JSS-MARKUP-003`: tp +299→366 (+67), fp +1→2 (+1), pending 0→7 (+7)
- `JSS-NAME-002`: tp +105→105 (+0), fp +1→1 (+0), pending 0→5 (+5)
- `JSS-OPER-001`: tp +77→81 (+4), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-OPER-002`: tp +70→70 (+0), fp +1→1 (+0), pending 0→4 (+4)
- `JSS-OPER-003`: tp +13→18 (+5), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-OPER-004`: tp +64→68 (+4), fp +1→1 (+0), pending 0→2 (+2)
- `JSS-PRE-001`: tp +63→65 (+2), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-PRE-006`: tp +15→16 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-REFS-003`: tp +1646→1755 (+109), fp +45→46 (+1), pending 0→0 (+0)
- `JSS-REFS-004`: tp +230→241 (+11), fp +0→0 (+0), pending 0→1 (+1)
- `JSS-REFS-005`: tp +36→40 (+4), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-REFS-006`: tp +147→150 (+3), fp +2→2 (+0), pending 0→0 (+0)
- `JSS-REFS-007`: tp +123→131 (+8), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-STRUCT-001`: tp +73→76 (+3), fp +2→2 (+0), pending 0→0 (+0)
- `JSS-STRUCT-002`: tp +27→28 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-STRUCT-004`: tp +5→6 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-STRUCT-006`: tp +4→5 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-TYPO-001`: tp +173→198 (+25), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-WIDTH-001`: tp +49→52 (+3), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-XREF-001`: tp +35→35 (+0), fp +1→1 (+0), pending 0→1 (+1)
- `JSS-XREF-002`: tp +453→462 (+9), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-XREF-004`: tp +338→351 (+13), fp +1→1 (+0), pending 0→3 (+3)

**Pinned only**

- `JSS-CITE-002`: tp +81→85 (+4), fp +17→18 (+1), pending 0→1 (+1)
- `JSS-CITE-003`: tp +6→16 (+10), fp +0→0 (+0), pending 0→2 (+2)
- `JSS-ABBR-001`: tp +8→10 (+2), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-BIBTEX-004`: tp +68→72 (+4), fp +3→3 (+0), pending 0→3 (+3)
- `JSS-CAP-002`: tp +98→103 (+5), fp +15→15 (+0), pending 0→0 (+0)
- `JSS-CAP-003`: tp +20→20 (+0), fp +18→18 (+0), pending 0→13 (+13)
- `JSS-CODE-001`: tp +17→25 (+8), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-CODE-002`: tp +7→14 (+7), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-CODE-003`: tp +88→98 (+10), fp +3→3 (+0), pending 0→0 (+0)
- `JSS-HOUSE-001`: tp +220→250 (+30), fp +1→2 (+1), pending 0→0 (+0)
- `JSS-HOUSE-002`: tp +25→27 (+2), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-HOUSE-003`: tp +28→33 (+5), fp +3→3 (+0), pending 0→0 (+0)
- `JSS-MARKUP-001`: tp +426→437 (+11), fp +50→57 (+7), pending 0→4 (+4)
- `JSS-MARKUP-003`: tp +124→191 (+67), fp +1→2 (+1), pending 0→7 (+7)
- `JSS-NAME-002`: tp +105→105 (+0), fp +1→1 (+0), pending 0→5 (+5)
- `JSS-OPER-001`: tp +26→27 (+1), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-OPER-002`: tp +53→53 (+0), fp +1→1 (+0), pending 0→3 (+3)
- **new** `JSS-OPER-003`: tp=5 fp=0 pending=0
- `JSS-OPER-004`: tp +53→55 (+2), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-PRE-001`: tp +17→18 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-PRE-006`: tp +11→12 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-REFS-003`: tp +1646→1755 (+109), fp +45→46 (+1), pending 0→0 (+0)
- `JSS-REFS-004`: tp +230→241 (+11), fp +0→0 (+0), pending 0→1 (+1)
- `JSS-REFS-005`: tp +36→40 (+4), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-REFS-006`: tp +147→150 (+3), fp +2→2 (+0), pending 0→0 (+0)
- `JSS-REFS-007`: tp +123→131 (+8), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-STRUCT-001`: tp +37→40 (+3), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-STRUCT-002`: tp +18→19 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-STRUCT-004`: tp +4→5 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-STRUCT-006`: tp +3→4 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-TYPO-001`: tp +86→110 (+24), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-XREF-001`: tp +23→23 (+0), fp +0→0 (+0), pending 0→1 (+1)
- `JSS-XREF-002`: tp +345→351 (+6), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-XREF-004`: tp +253→266 (+13), fp +1→1 (+0), pending 0→1 (+1)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 74 — 2026-05-03T17:51:16Z — post-JSS-CAP-003-xrefs

- **Corpus size:** 237 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=69, pinned=58

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 195 | 20 | 1 | 90.70% | PASS |
| citation | JSS-CITE-003 | 21 | 0 | 2 | 100.00% | PASS |
| citation | JSS-CITE-004 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 13 | 1 | 0 | 92.86% | PASS |
| unknown | JSS-BIBTEX-002 | 9 | 2 | 0 | 81.82% | FAIL |
| unknown | JSS-BIBTEX-003 | 46 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 88 | 3 | 5 | 96.70% | PASS |
| unknown | JSS-CAP-001 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 223 | 20 | 0 | 91.77% | PASS |
| unknown | JSS-CAP-003 | 21 | 24 | 11 | 46.67% | FAIL |
| unknown | JSS-CAP-004 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 30 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 149 | 3 | 0 | 98.03% | PASS |
| unknown | JSS-HOUSE-001 | 541 | 2 | 0 | 99.63% | PASS |
| unknown | JSS-HOUSE-002 | 27 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 40 | 3 | 0 | 93.02% | PASS |
| unknown | JSS-MARKUP-001 | 1034 | 105 | 4 | 90.78% | PASS |
| unknown | JSS-MARKUP-002 | 225 | 15 | 0 | 93.75% | PASS |
| unknown | JSS-MARKUP-003 | 366 | 2 | 7 | 99.46% | PASS |
| unknown | JSS-MARKUP-004 | 136 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 105 | 1 | 5 | 99.06% | PASS |
| unknown | JSS-OPER-001 | 81 | 1 | 0 | 98.78% | PASS |
| unknown | JSS-OPER-002 | 70 | 1 | 4 | 98.59% | PASS |
| unknown | JSS-OPER-003 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 68 | 1 | 2 | 98.55% | PASS |
| unknown | JSS-PRE-001 | 65 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 1755 | 46 | 0 | 97.45% | PASS |
| unknown | JSS-REFS-004 | 241 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 40 | 1 | 0 | 97.56% | PASS |
| unknown | JSS-REFS-006 | 150 | 2 | 0 | 98.68% | PASS |
| unknown | JSS-REFS-007 | 131 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 76 | 2 | 0 | 97.44% | PASS |
| unknown | JSS-STRUCT-002 | 28 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 198 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 3 | 0 | 88.89% | FAIL |
| unknown | JSS-WIDTH-001 | 52 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 35 | 1 | 1 | 97.22% | PASS |
| unknown | JSS-XREF-002 | 462 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 351 | 1 | 3 | 99.72% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 85 | 18 | 1 | 82.52% | FAIL |
| citation | JSS-CITE-003 | 16 | 0 | 2 | 100.00% | PASS |
| citation | JSS-CITE-004 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 10 | 1 | 0 | 90.91% | PASS |
| unknown | JSS-BIBTEX-002 | 9 | 2 | 0 | 81.82% | FAIL |
| unknown | JSS-BIBTEX-003 | 46 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 72 | 3 | 3 | 96.00% | PASS |
| unknown | JSS-CAP-001 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 103 | 15 | 0 | 87.29% | FAIL |
| unknown | JSS-CAP-003 | 14 | 12 | 11 | 53.85% | FAIL |
| unknown | JSS-CAP-004 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 25 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 98 | 3 | 0 | 97.03% | PASS |
| unknown | JSS-HOUSE-001 | 250 | 2 | 0 | 99.21% | PASS |
| unknown | JSS-HOUSE-002 | 27 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 33 | 3 | 0 | 91.67% | PASS |
| unknown | JSS-MARKUP-001 | 437 | 57 | 4 | 88.46% | FAIL |
| unknown | JSS-MARKUP-002 | 106 | 3 | 0 | 97.25% | PASS |
| unknown | JSS-MARKUP-003 | 191 | 2 | 7 | 98.96% | PASS |
| unknown | JSS-MARKUP-004 | 34 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 105 | 1 | 5 | 99.06% | PASS |
| unknown | JSS-OPER-001 | 27 | 1 | 0 | 96.43% | PASS |
| unknown | JSS-OPER-002 | 53 | 1 | 3 | 98.15% | PASS |
| unknown | JSS-OPER-003 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 55 | 1 | 0 | 98.21% | PASS |
| unknown | JSS-PRE-001 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 1755 | 46 | 0 | 97.45% | PASS |
| unknown | JSS-REFS-004 | 241 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 40 | 1 | 0 | 97.56% | PASS |
| unknown | JSS-REFS-006 | 150 | 2 | 0 | 98.68% | PASS |
| unknown | JSS-REFS-007 | 131 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 40 | 1 | 0 | 97.56% | PASS |
| unknown | JSS-STRUCT-002 | 19 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 110 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 1 | 0 | 96.00% | PASS |
| unknown | JSS-WIDTH-001 | 44 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 23 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 351 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 266 | 1 | 1 | 99.63% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-CAP-003`: tp +29→21 (-8), fp +34→24 (-10), pending 13→11 (-2)
- `JSS-NAME-001`: tp +8→10 (+2), fp +2→0 (-2), pending 0→0 (+0)

**Pinned only**

- `JSS-CAP-003`: tp +20→14 (-6), fp +18→12 (-6), pending 13→11 (-2)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 75 — 2026-05-03T17:54:20Z — post-JSS-BIBTEX-002-skip-strings

- **Corpus size:** 237 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=69, pinned=58

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 195 | 20 | 1 | 90.70% | PASS |
| citation | JSS-CITE-003 | 21 | 0 | 2 | 100.00% | PASS |
| citation | JSS-CITE-004 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 13 | 1 | 0 | 92.86% | PASS |
| unknown | JSS-BIBTEX-002 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 46 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 88 | 3 | 5 | 96.70% | PASS |
| unknown | JSS-CAP-001 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 223 | 20 | 0 | 91.77% | PASS |
| unknown | JSS-CAP-003 | 21 | 24 | 11 | 46.67% | FAIL |
| unknown | JSS-CAP-004 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 30 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 149 | 3 | 0 | 98.03% | PASS |
| unknown | JSS-HOUSE-001 | 541 | 2 | 0 | 99.63% | PASS |
| unknown | JSS-HOUSE-002 | 27 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 40 | 3 | 0 | 93.02% | PASS |
| unknown | JSS-MARKUP-001 | 1034 | 105 | 4 | 90.78% | PASS |
| unknown | JSS-MARKUP-002 | 225 | 15 | 0 | 93.75% | PASS |
| unknown | JSS-MARKUP-003 | 366 | 2 | 7 | 99.46% | PASS |
| unknown | JSS-MARKUP-004 | 136 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 105 | 1 | 5 | 99.06% | PASS |
| unknown | JSS-OPER-001 | 81 | 1 | 0 | 98.78% | PASS |
| unknown | JSS-OPER-002 | 70 | 1 | 4 | 98.59% | PASS |
| unknown | JSS-OPER-003 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 68 | 1 | 2 | 98.55% | PASS |
| unknown | JSS-PRE-001 | 65 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 1755 | 46 | 0 | 97.45% | PASS |
| unknown | JSS-REFS-004 | 241 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 40 | 1 | 0 | 97.56% | PASS |
| unknown | JSS-REFS-006 | 150 | 2 | 0 | 98.68% | PASS |
| unknown | JSS-REFS-007 | 131 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 76 | 2 | 0 | 97.44% | PASS |
| unknown | JSS-STRUCT-002 | 28 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 198 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 3 | 0 | 88.89% | FAIL |
| unknown | JSS-WIDTH-001 | 52 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 35 | 1 | 1 | 97.22% | PASS |
| unknown | JSS-XREF-002 | 462 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 351 | 1 | 3 | 99.72% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 85 | 18 | 1 | 82.52% | FAIL |
| citation | JSS-CITE-003 | 16 | 0 | 2 | 100.00% | PASS |
| citation | JSS-CITE-004 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 10 | 1 | 0 | 90.91% | PASS |
| unknown | JSS-BIBTEX-002 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 46 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 72 | 3 | 3 | 96.00% | PASS |
| unknown | JSS-CAP-001 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 103 | 15 | 0 | 87.29% | FAIL |
| unknown | JSS-CAP-003 | 14 | 12 | 11 | 53.85% | FAIL |
| unknown | JSS-CAP-004 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 25 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 98 | 3 | 0 | 97.03% | PASS |
| unknown | JSS-HOUSE-001 | 250 | 2 | 0 | 99.21% | PASS |
| unknown | JSS-HOUSE-002 | 27 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 33 | 3 | 0 | 91.67% | PASS |
| unknown | JSS-MARKUP-001 | 437 | 57 | 4 | 88.46% | FAIL |
| unknown | JSS-MARKUP-002 | 106 | 3 | 0 | 97.25% | PASS |
| unknown | JSS-MARKUP-003 | 191 | 2 | 7 | 98.96% | PASS |
| unknown | JSS-MARKUP-004 | 34 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 105 | 1 | 5 | 99.06% | PASS |
| unknown | JSS-OPER-001 | 27 | 1 | 0 | 96.43% | PASS |
| unknown | JSS-OPER-002 | 53 | 1 | 3 | 98.15% | PASS |
| unknown | JSS-OPER-003 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 55 | 1 | 0 | 98.21% | PASS |
| unknown | JSS-PRE-001 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 1755 | 46 | 0 | 97.45% | PASS |
| unknown | JSS-REFS-004 | 241 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 40 | 1 | 0 | 97.56% | PASS |
| unknown | JSS-REFS-006 | 150 | 2 | 0 | 98.68% | PASS |
| unknown | JSS-REFS-007 | 131 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 40 | 1 | 0 | 97.56% | PASS |
| unknown | JSS-STRUCT-002 | 19 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 110 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 24 | 1 | 0 | 96.00% | PASS |
| unknown | JSS-WIDTH-001 | 44 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 23 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 351 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 266 | 1 | 1 | 99.63% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-BIBTEX-002`: tp +9→6 (-3), fp +2→0 (-2), pending 0→0 (+0)

**Pinned only**

- `JSS-BIBTEX-002`: tp +9→6 (-3), fp +2→0 (-2), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 76 — 2026-05-03T18:01:37Z — post-JSS-CAP-003-textual-citations

- **Corpus size:** 237 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=69, pinned=58

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 195 | 20 | 1 | 90.70% | PASS |
| citation | JSS-CITE-003 | 21 | 0 | 2 | 100.00% | PASS |
| citation | JSS-CITE-004 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 46 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 88 | 3 | 5 | 96.70% | PASS |
| unknown | JSS-CAP-001 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 223 | 20 | 0 | 91.77% | PASS |
| unknown | JSS-CAP-003 | 20 | 17 | 7 | 54.05% | FAIL |
| unknown | JSS-CAP-004 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 30 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 149 | 3 | 0 | 98.03% | PASS |
| unknown | JSS-HOUSE-001 | 541 | 2 | 0 | 99.63% | PASS |
| unknown | JSS-HOUSE-002 | 27 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 43 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 1034 | 105 | 4 | 90.78% | PASS |
| unknown | JSS-MARKUP-002 | 225 | 15 | 0 | 93.75% | PASS |
| unknown | JSS-MARKUP-003 | 366 | 2 | 7 | 99.46% | PASS |
| unknown | JSS-MARKUP-004 | 136 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 105 | 1 | 5 | 99.06% | PASS |
| unknown | JSS-OPER-001 | 81 | 1 | 0 | 98.78% | PASS |
| unknown | JSS-OPER-002 | 70 | 1 | 4 | 98.59% | PASS |
| unknown | JSS-OPER-003 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 68 | 1 | 2 | 98.55% | PASS |
| unknown | JSS-PRE-001 | 65 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 1755 | 46 | 0 | 97.45% | PASS |
| unknown | JSS-REFS-004 | 241 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 40 | 1 | 0 | 97.56% | PASS |
| unknown | JSS-REFS-006 | 150 | 2 | 0 | 98.68% | PASS |
| unknown | JSS-REFS-007 | 131 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 76 | 2 | 0 | 97.44% | PASS |
| unknown | JSS-STRUCT-002 | 28 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 198 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 27 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-WIDTH-001 | 52 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 35 | 1 | 1 | 97.22% | PASS |
| unknown | JSS-XREF-002 | 462 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 351 | 1 | 3 | 99.72% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 85 | 18 | 1 | 82.52% | FAIL |
| citation | JSS-CITE-003 | 16 | 0 | 2 | 100.00% | PASS |
| citation | JSS-CITE-004 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 46 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 72 | 3 | 3 | 96.00% | PASS |
| unknown | JSS-CAP-001 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 103 | 15 | 0 | 87.29% | FAIL |
| unknown | JSS-CAP-003 | 13 | 11 | 7 | 54.17% | FAIL |
| unknown | JSS-CAP-004 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 25 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 98 | 3 | 0 | 97.03% | PASS |
| unknown | JSS-HOUSE-001 | 250 | 2 | 0 | 99.21% | PASS |
| unknown | JSS-HOUSE-002 | 27 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 36 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 437 | 57 | 4 | 88.46% | FAIL |
| unknown | JSS-MARKUP-002 | 106 | 3 | 0 | 97.25% | PASS |
| unknown | JSS-MARKUP-003 | 191 | 2 | 7 | 98.96% | PASS |
| unknown | JSS-MARKUP-004 | 34 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 105 | 1 | 5 | 99.06% | PASS |
| unknown | JSS-OPER-001 | 27 | 1 | 0 | 96.43% | PASS |
| unknown | JSS-OPER-002 | 53 | 1 | 3 | 98.15% | PASS |
| unknown | JSS-OPER-003 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 55 | 1 | 0 | 98.21% | PASS |
| unknown | JSS-PRE-001 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 1755 | 46 | 0 | 97.45% | PASS |
| unknown | JSS-REFS-004 | 241 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 40 | 1 | 0 | 97.56% | PASS |
| unknown | JSS-REFS-006 | 150 | 2 | 0 | 98.68% | PASS |
| unknown | JSS-REFS-007 | 131 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 40 | 1 | 0 | 97.56% | PASS |
| unknown | JSS-STRUCT-002 | 19 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 110 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 25 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-WIDTH-001 | 44 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 23 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 351 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 266 | 1 | 1 | 99.63% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-ABBR-001`: tp +13→14 (+1), fp +1→0 (-1), pending 0→0 (+0)
- `JSS-CAP-003`: tp +21→20 (-1), fp +24→17 (-7), pending 11→7 (-4)
- `JSS-HOUSE-003`: tp +40→43 (+3), fp +3→0 (-3), pending 0→0 (+0)
- `JSS-TYPO-004`: tp +24→27 (+3), fp +3→0 (-3), pending 0→0 (+0)

**Pinned only**

- `JSS-ABBR-001`: tp +10→11 (+1), fp +1→0 (-1), pending 0→0 (+0)
- `JSS-CAP-003`: tp +14→13 (-1), fp +12→11 (-1), pending 11→7 (-4)
- `JSS-HOUSE-003`: tp +33→36 (+3), fp +3→0 (-3), pending 0→0 (+0)
- `JSS-TYPO-004`: tp +24→25 (+1), fp +1→0 (-1), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 77 — 2026-05-03T18:08:06Z — post-JSS-CAP-003-label-prefix

- **Corpus size:** 237 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=69, pinned=58

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 195 | 20 | 1 | 90.70% | PASS |
| citation | JSS-CITE-003 | 21 | 0 | 2 | 100.00% | PASS |
| citation | JSS-CITE-004 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 46 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 88 | 3 | 5 | 96.70% | PASS |
| unknown | JSS-CAP-001 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 223 | 20 | 0 | 91.77% | PASS |
| unknown | JSS-CAP-003 | 20 | 13 | 7 | 60.61% | FAIL |
| unknown | JSS-CAP-004 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 30 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 149 | 3 | 0 | 98.03% | PASS |
| unknown | JSS-HOUSE-001 | 541 | 2 | 0 | 99.63% | PASS |
| unknown | JSS-HOUSE-002 | 27 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 43 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 1034 | 105 | 4 | 90.78% | PASS |
| unknown | JSS-MARKUP-002 | 225 | 15 | 0 | 93.75% | PASS |
| unknown | JSS-MARKUP-003 | 366 | 2 | 7 | 99.46% | PASS |
| unknown | JSS-MARKUP-004 | 136 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 105 | 1 | 5 | 99.06% | PASS |
| unknown | JSS-OPER-001 | 81 | 1 | 0 | 98.78% | PASS |
| unknown | JSS-OPER-002 | 70 | 1 | 4 | 98.59% | PASS |
| unknown | JSS-OPER-003 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 68 | 1 | 2 | 98.55% | PASS |
| unknown | JSS-PRE-001 | 65 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 16 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 1755 | 46 | 0 | 97.45% | PASS |
| unknown | JSS-REFS-004 | 241 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 40 | 1 | 0 | 97.56% | PASS |
| unknown | JSS-REFS-006 | 150 | 2 | 0 | 98.68% | PASS |
| unknown | JSS-REFS-007 | 131 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 76 | 2 | 0 | 97.44% | PASS |
| unknown | JSS-STRUCT-002 | 28 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 198 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 27 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-WIDTH-001 | 52 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 35 | 1 | 1 | 97.22% | PASS |
| unknown | JSS-XREF-002 | 462 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 351 | 1 | 3 | 99.72% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 85 | 18 | 1 | 82.52% | FAIL |
| citation | JSS-CITE-003 | 16 | 0 | 2 | 100.00% | PASS |
| citation | JSS-CITE-004 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 46 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 72 | 3 | 3 | 96.00% | PASS |
| unknown | JSS-CAP-001 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 103 | 15 | 0 | 87.29% | FAIL |
| unknown | JSS-CAP-003 | 13 | 10 | 7 | 56.52% | FAIL |
| unknown | JSS-CAP-004 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 25 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 98 | 3 | 0 | 97.03% | PASS |
| unknown | JSS-HOUSE-001 | 250 | 2 | 0 | 99.21% | PASS |
| unknown | JSS-HOUSE-002 | 27 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 36 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 437 | 57 | 4 | 88.46% | FAIL |
| unknown | JSS-MARKUP-002 | 106 | 3 | 0 | 97.25% | PASS |
| unknown | JSS-MARKUP-003 | 191 | 2 | 7 | 98.96% | PASS |
| unknown | JSS-MARKUP-004 | 34 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 105 | 1 | 5 | 99.06% | PASS |
| unknown | JSS-OPER-001 | 27 | 1 | 0 | 96.43% | PASS |
| unknown | JSS-OPER-002 | 53 | 1 | 3 | 98.15% | PASS |
| unknown | JSS-OPER-003 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 55 | 1 | 0 | 98.21% | PASS |
| unknown | JSS-PRE-001 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 1755 | 46 | 0 | 97.45% | PASS |
| unknown | JSS-REFS-004 | 241 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 40 | 1 | 0 | 97.56% | PASS |
| unknown | JSS-REFS-006 | 150 | 2 | 0 | 98.68% | PASS |
| unknown | JSS-REFS-007 | 131 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 40 | 1 | 0 | 97.56% | PASS |
| unknown | JSS-STRUCT-002 | 19 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 110 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 25 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-WIDTH-001 | 44 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 23 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 351 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 266 | 1 | 1 | 99.63% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-CAP-003`: tp +20→20 (+0), fp +17→13 (-4), pending 7→7 (+0)

**Pinned only**

- `JSS-CAP-003`: tp +13→13 (+0), fp +11→10 (-1), pending 7→7 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 78 — 2026-05-03T19:52:34Z — iter-78-convergence

- **Corpus size:** 238 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=69, pinned=58

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 198 | 20 | 1 | 90.83% | PASS |
| citation | JSS-CITE-003 | 21 | 0 | 2 | 100.00% | PASS |
| citation | JSS-CITE-004 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 46 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 92 | 0 | 6 | 100.00% | PASS |
| unknown | JSS-CAP-001 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 223 | 20 | 0 | 91.77% | PASS |
| unknown | JSS-CAP-003 | 20 | 13 | 7 | 60.61% | FAIL |
| unknown | JSS-CAP-004 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 30 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 150 | 3 | 0 | 98.04% | PASS |
| unknown | JSS-HOUSE-001 | 548 | 2 | 0 | 99.64% | PASS |
| unknown | JSS-HOUSE-002 | 27 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 44 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 1040 | 106 | 6 | 90.75% | PASS |
| unknown | JSS-MARKUP-002 | 226 | 15 | 0 | 93.78% | PASS |
| unknown | JSS-MARKUP-003 | 366 | 2 | 7 | 99.46% | PASS |
| unknown | JSS-MARKUP-004 | 136 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-001 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 105 | 1 | 6 | 99.06% | PASS |
| unknown | JSS-OPER-001 | 81 | 1 | 0 | 98.78% | PASS |
| unknown | JSS-OPER-002 | 70 | 1 | 18 | 98.59% | PASS |
| unknown | JSS-OPER-003 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 68 | 1 | 2 | 98.55% | PASS |
| unknown | JSS-PRE-001 | 66 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 1758 | 46 | 0 | 97.45% | PASS |
| unknown | JSS-REFS-004 | 244 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 40 | 1 | 0 | 97.56% | PASS |
| unknown | JSS-REFS-006 | 152 | 2 | 0 | 98.70% | PASS |
| unknown | JSS-REFS-007 | 131 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 76 | 2 | 0 | 97.44% | PASS |
| unknown | JSS-STRUCT-002 | 28 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 205 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 27 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-WIDTH-001 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 35 | 1 | 1 | 97.22% | PASS |
| unknown | JSS-XREF-002 | 465 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 351 | 1 | 3 | 99.72% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 86 | 18 | 1 | 82.69% | FAIL |
| citation | JSS-CITE-003 | 16 | 0 | 2 | 100.00% | PASS |
| citation | JSS-CITE-004 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 46 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 76 | 0 | 4 | 100.00% | PASS |
| unknown | JSS-CAP-001 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 103 | 15 | 0 | 87.29% | FAIL |
| unknown | JSS-CAP-003 | 13 | 10 | 7 | 56.52% | FAIL |
| unknown | JSS-CAP-004 | 12 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 25 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 14 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 98 | 3 | 0 | 97.03% | PASS |
| unknown | JSS-HOUSE-001 | 255 | 2 | 0 | 99.22% | PASS |
| unknown | JSS-HOUSE-002 | 27 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 37 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 439 | 58 | 5 | 88.33% | FAIL |
| unknown | JSS-MARKUP-002 | 107 | 3 | 0 | 97.27% | PASS |
| unknown | JSS-MARKUP-003 | 191 | 2 | 7 | 98.96% | PASS |
| unknown | JSS-MARKUP-004 | 34 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 105 | 1 | 6 | 99.06% | PASS |
| unknown | JSS-OPER-001 | 27 | 1 | 0 | 96.43% | PASS |
| unknown | JSS-OPER-002 | 53 | 1 | 14 | 98.15% | PASS |
| unknown | JSS-OPER-003 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 55 | 1 | 0 | 98.21% | PASS |
| unknown | JSS-PRE-001 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 1758 | 46 | 0 | 97.45% | PASS |
| unknown | JSS-REFS-004 | 244 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-REFS-005 | 40 | 1 | 0 | 97.56% | PASS |
| unknown | JSS-REFS-006 | 152 | 2 | 0 | 98.70% | PASS |
| unknown | JSS-REFS-007 | 131 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 40 | 1 | 0 | 97.56% | PASS |
| unknown | JSS-STRUCT-002 | 19 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-006 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 113 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 25 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-WIDTH-001 | 44 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-001 | 23 | 0 | 1 | 100.00% | PASS |
| unknown | JSS-XREF-002 | 354 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 266 | 1 | 1 | 99.63% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-CITE-002`: tp +195→198 (+3), fp +20→20 (+0), pending 1→1 (+0)
- `JSS-BIBTEX-004`: tp +88→92 (+4), fp +3→0 (-3), pending 5→6 (+1)
- `JSS-CAP-001`: tp +3→4 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-CODE-003`: tp +149→150 (+1), fp +3→3 (+0), pending 0→0 (+0)
- `JSS-HOUSE-001`: tp +541→548 (+7), fp +2→2 (+0), pending 0→0 (+0)
- `JSS-HOUSE-003`: tp +43→44 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-MARKUP-001`: tp +1034→1040 (+6), fp +105→106 (+1), pending 4→6 (+2)
- `JSS-MARKUP-002`: tp +225→226 (+1), fp +15→15 (+0), pending 0→0 (+0)
- `JSS-NAME-002`: tp +105→105 (+0), fp +1→1 (+0), pending 5→6 (+1)
- `JSS-OPER-002`: tp +70→70 (+0), fp +1→1 (+0), pending 4→18 (+14)
- `JSS-PRE-001`: tp +65→66 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-PRE-006`: tp +16→20 (+4), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-REFS-003`: tp +1755→1758 (+3), fp +46→46 (+0), pending 0→0 (+0)
- `JSS-REFS-004`: tp +241→244 (+3), fp +0→0 (+0), pending 1→1 (+0)
- `JSS-REFS-006`: tp +150→152 (+2), fp +2→2 (+0), pending 0→0 (+0)
- `JSS-TYPO-001`: tp +198→205 (+7), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-TYPO-003`: tp +2→10 (+8), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-WIDTH-001`: tp +52→53 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-XREF-002`: tp +462→465 (+3), fp +0→0 (+0), pending 0→0 (+0)

**Pinned only**

- `JSS-CITE-002`: tp +85→86 (+1), fp +18→18 (+0), pending 1→1 (+0)
- `JSS-BIBTEX-004`: tp +72→76 (+4), fp +3→0 (-3), pending 3→4 (+1)
- `JSS-HOUSE-001`: tp +250→255 (+5), fp +2→2 (+0), pending 0→0 (+0)
- `JSS-HOUSE-003`: tp +36→37 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-MARKUP-001`: tp +437→439 (+2), fp +57→58 (+1), pending 4→5 (+1)
- `JSS-MARKUP-002`: tp +106→107 (+1), fp +3→3 (+0), pending 0→0 (+0)
- `JSS-NAME-002`: tp +105→105 (+0), fp +1→1 (+0), pending 5→6 (+1)
- `JSS-OPER-002`: tp +53→53 (+0), fp +1→1 (+0), pending 3→14 (+11)
- `JSS-PRE-006`: tp +12→13 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-REFS-003`: tp +1755→1758 (+3), fp +46→46 (+0), pending 0→0 (+0)
- `JSS-REFS-004`: tp +241→244 (+3), fp +0→0 (+0), pending 1→1 (+0)
- `JSS-REFS-006`: tp +150→152 (+2), fp +2→2 (+0), pending 0→0 (+0)
- `JSS-TYPO-001`: tp +110→113 (+3), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-TYPO-003`: tp +2→3 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-XREF-002`: tp +351→354 (+3), fp +0→0 (+0), pending 0→0 (+0)

### Findings / suggestions

**Convergence reached.** This snapshot closes the autonomous-loop
phase. 53 of 54 catalogued JSS rules pass the precision threshold
on the 232-paper corpus; only `JSS-CAP-003` remains FAIL after
five consecutive fix attempts (38.0 % → 60.6 %). The five rounds
exhausted the tractable FP clusters (eponym whitelist, cross-ref
nouns, textual citations, label-prefix captions); the remaining
13 FPs are domain-ontology gaps — statistical method names like
*Huber's Proposal 2*, R class names like *DSClassify*, place
names, political proper nouns — that whack-a-mole patching would
only silence at the cost of recall.

The CRAN-vignette corpus is also effectively exhausted: of the
1 177 JSS-paper-counterpart candidate packages (JSS archive ∪
CRAN-GitHub), 232 are pinned, 496 are off-CRAN (archived), and the
476 currently on CRAN no longer ship JSS-counterpart vignettes
(53 % ship no vignette at all; the rest ship vignettes that don't
cite JSS). Non-R JSS papers (~115 across Python/MATLAB/Stata/Julia/
C++) have no JSS-hosted .tex source — only PDFs and code/data
archives.

### Plan

Hand off `JSS-CAP-003` to a human reviewer. Two options:

1. **Tighten the whitelist by category** — extend `_PROPER_NOUNS`
   with a curated statistics-vocabulary list and add an
   R-class-name detector (`[A-Z][a-z]+[A-Z]\w*` with ≥1 internal
   upper).
2. **Lower the rule's confidence** — accept that captions with
   embedded proper-noun runs are inherently ambiguous, downgrade
   to `severity=warning`, and surface the call to the author.

Both require human judgement; the autonomous loop has done all it
can without overfitting.

### Results (post-implementation)

Loop converged at iter 78 (overall precision 96.79 %, +0.91pp over
iters 67–78). 226/226 recall plants still fire after the rule
changes. The cron-driven 5-hour iteration trigger has been
cancelled and the iteration lock cleared.

---

## Conclusion (closing the autonomous loop, 2026-05-03)

This log is closed. 78 iterations across the precision-loop
methodology — six weeks of corpus growth, AI-classifier review,
human verification, and rule-by-rule fix attempts — have brought
the JSS lint catalogue from a 50-paper baseline (Iter 1) to a
**232-paper, 53/54 PASS, 96.79 % overall-precision** state. What
follows is a stable artefact: a linter whose remaining error budget
is concentrated in one rule and one corpus boundary, both of
which are out of reach of further mechanical iteration.

### Where the wins came from

The bulk of the precision gains came from three categories of
intervention:

1. **Mass FP elimination via targeted exemptions.** MARKUP-001 lost
   ~100 FPs to language-name + filename detection (iters 14, 26).
   REFS-003 lost 60+ FPs to abbreviation-aware matching. CITE-002
   lost the textual-citation cluster. Each was a domain pattern
   the rule's original author hadn't anticipated and that fresh
   corpus exposure surfaced.
2. **Per-rule labeller routing.** The full 934-row gold benchmark
   (iter 71) showed Bonsai-8B and Qwen3-30B are *complementary*,
   not redundant — Bonsai dominates short-prose rules (CAP-002,
   OPER-002), Qwen3 dominates long-prose rules (MARKUP-001,
   CITE-002). Pinning each rule to its best-performing model
   (`eval/review-routing.toml`) cut the human-review queue by ~40 %
   and made the AI-labelled rows trustworthy enough to drive the
   loop unattended.
3. **AI-mislabel correction.** A surprising fraction of "FPs"
   surfaced by the loop were AI-labeller mistakes, not rule
   defects. NAME-001 (FORTRAN→Fortran), TYPO-004 (caption-before-
   chunk-content), HOUSE-003 (`\usepackage{hyperref}` over
   jss.cls), BIBTEX-004 (6+-author entries), and PARSE-000 (real
   Latin-1 byte) were all correctly fired; the labellers
   misidentified them. Proxy-flipping these as `human:claude-proxy`
   added ~14 TPs without rule changes.

### What's deferred

Two open items survive convergence:

1. **JSS-CAP-003 at 60.6 %** (20 TP / 13 FP, 5/5 attempts used).
   The remaining 13 FPs split across statistical method names
   (*Huber's Proposal 2*), R class identifiers (*DSClassify*,
   *DSOutlier*), place names (*Long Bridge*, *Wind Field Park*,
   *Québec*), and political proper nouns. Each is a domain-
   ontology gap, not a parse / heuristic gap. Two paths forward
   are documented in the iter-78 Plan section.

2. **Non-R JSS-paper corpus.** ~115 JSS papers in Python, MATLAB,
   Stata, Julia, C++, etc., all written in jss.cls, are
   inaccessible via the current CRAN-vignette path. JSS itself
   doesn't host the manuscript .tex source — only the PDF and
   replication code/data. Hand-curating the .tex from author
   GitHubs / arXiv would extend the corpus into multi-language
   territory but isn't loop-tractable.

### What this log doesn't capture

The git history under `src/texlint/journals/jss/rules/`
documents *what* the rule changes were. This log documents
*why* — the corpus signals that motivated each change and the
TP/FP deltas that confirmed (or reverted) them. Read the two
together: the diff says what shipped, this log says what evidence
shipped it.

The infrastructure built along the way (the
`eval-jss iterate plan` decider, the policy-codified
`eval/iteration-policy.toml`, the per-rule labeller routing, the
recall-plants test suite, the pre-commit guard chained into
`.githooks/pre-commit`) outlives this log. Future
human-driven iterations can replay any step of the loop without
the historical context that produced these knobs.

### Resuming

The loop can be resumed at any time:

```bash
source .venv/bin/activate
eval-jss iterate plan        # what should we do next?
eval-jss iterate refresh     # re-scan + restore labels
eval-jss iterate record <label>
```

The planner correctly emits `deferred_rules` for the CAP-003
state; once that rule is hand-fixed (or downgraded to `warning`
severity), the planner will report `stop` with "all rules pass".
Until then, the answer is structurally `grow_corpus`, and the
corpus is structurally exhausted by the means available.

— end of log —

## Iteration 79 — 2026-06-18T19:14:08Z — post-xref005

- **Corpus size:** 244 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=39, pinned=29

**Note:** Add JSS-XREF-005 (orphan figures/tables); deterministic adjudication (179/179 TP); fix _collect_referenced_labels to capture \vref/\cref-family refs. Also added JSS-BIBTEX-005 earlier this cycle.

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 201 | 20 | 0 | 90.95% | PASS |
| citation | JSS-CITE-003 | 236 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 30 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 110 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-005 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-001 | 101 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 502 | 17 | 0 | 96.72% | PASS |
| unknown | JSS-CAP-003 | 15 | 32 | 0 | 31.91% | FAIL |
| unknown | JSS-CAP-004 | 19 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 421 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 248 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 2072 | 14 | 0 | 99.33% | PASS |
| unknown | JSS-HOUSE-001 | 590 | 2 | 0 | 99.66% | PASS |
| unknown | JSS-HOUSE-002 | 31 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 50 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 1089 | 168 | 0 | 86.63% | FAIL |
| unknown | JSS-MARKUP-002 | 236 | 14 | 0 | 94.40% | PASS |
| unknown | JSS-MARKUP-003 | 1666 | 149 | 0 | 91.79% | PASS |
| unknown | JSS-MARKUP-004 | 135 | 1 | 0 | 99.26% | PASS |
| unknown | JSS-NAME-001 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 155 | 1 | 0 | 99.36% | PASS |
| unknown | JSS-OPER-001 | 79 | 1 | 0 | 98.75% | PASS |
| unknown | JSS-OPER-002 | 146 | 159 | 0 | 47.87% | FAIL |
| unknown | JSS-OPER-003 | 369 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 89 | 7 | 0 | 92.71% | PASS |
| unknown | JSS-PRE-001 | 66 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 21 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 2023 | 56 | 0 | 97.31% | PASS |
| unknown | JSS-REFS-004 | 537 | 1 | 0 | 99.81% | PASS |
| unknown | JSS-REFS-005 | 44 | 2 | 0 | 95.65% | PASS |
| unknown | JSS-REFS-006 | 900 | 31 | 0 | 96.67% | PASS |
| unknown | JSS-REFS-007 | 141 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 81 | 2 | 0 | 97.59% | PASS |
| unknown | JSS-STRUCT-002 | 31 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 34 | 10 | 0 | 77.27% | FAIL |
| unknown | JSS-STRUCT-006 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 212 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 62 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-WIDTH-001 | 361 | 12 | 0 | 96.78% | PASS |
| unknown | JSS-XREF-001 | 37 | 11 | 0 | 77.08% | FAIL |
| unknown | JSS-XREF-002 | 817 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 815 | 32 | 0 | 96.22% | PASS |
| unknown | JSS-XREF-005 | 179 | 0 | 0 | 100.00% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 95 | 16 | 0 | 85.59% | FAIL |
| citation | JSS-CITE-003 | 171 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 25 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 91 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-005 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-001 | 47 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 293 | 12 | 0 | 96.07% | PASS |
| unknown | JSS-CAP-003 | 7 | 28 | 0 | 20.00% | FAIL |
| unknown | JSS-CAP-004 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 258 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 171 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 1303 | 11 | 0 | 99.16% | PASS |
| unknown | JSS-HOUSE-001 | 293 | 2 | 0 | 99.32% | PASS |
| unknown | JSS-HOUSE-002 | 31 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 43 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 463 | 104 | 0 | 81.66% | FAIL |
| unknown | JSS-MARKUP-002 | 116 | 2 | 0 | 98.31% | PASS |
| unknown | JSS-MARKUP-003 | 616 | 78 | 0 | 88.76% | FAIL |
| unknown | JSS-MARKUP-004 | 33 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 155 | 1 | 0 | 99.36% | PASS |
| unknown | JSS-OPER-001 | 27 | 1 | 0 | 96.43% | PASS |
| unknown | JSS-OPER-002 | 98 | 113 | 0 | 46.45% | FAIL |
| unknown | JSS-OPER-003 | 283 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 67 | 6 | 0 | 91.78% | PASS |
| unknown | JSS-PRE-001 | 17 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 2023 | 56 | 0 | 97.31% | PASS |
| unknown | JSS-REFS-004 | 537 | 1 | 0 | 99.81% | PASS |
| unknown | JSS-REFS-005 | 44 | 2 | 0 | 95.65% | PASS |
| unknown | JSS-REFS-006 | 900 | 31 | 0 | 96.67% | PASS |
| unknown | JSS-REFS-007 | 141 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 45 | 1 | 0 | 97.83% | PASS |
| unknown | JSS-STRUCT-002 | 22 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 19 | 9 | 0 | 67.86% | FAIL |
| unknown | JSS-STRUCT-006 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 119 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 45 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-WIDTH-001 | 188 | 6 | 0 | 96.91% | PASS |
| unknown | JSS-XREF-001 | 24 | 8 | 0 | 75.00% | FAIL |
| unknown | JSS-XREF-002 | 627 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 609 | 27 | 0 | 95.75% | PASS |
| unknown | JSS-XREF-005 | 125 | 0 | 0 | 100.00% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-CITE-002`: tp +198→201 (+3), fp +20→20 (+0), pending 1→0 (-1)
- `JSS-CITE-003`: tp +21→236 (+215), fp +0→0 (+0), pending 2→0 (-2)
- `JSS-ABBR-001`: tp +14→30 (+16), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-BIBTEX-002`: tp +6→7 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-BIBTEX-003`: tp +46→53 (+7), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-BIBTEX-004`: tp +92→110 (+18), fp +0→0 (+0), pending 6→0 (-6)
- **new** `JSS-BIBTEX-005`: tp=9 fp=0 pending=0
- `JSS-CAP-001`: tp +4→101 (+97), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-CAP-002`: tp +223→502 (+279), fp +20→17 (-3), pending 0→0 (+0)
- `JSS-CAP-003`: tp +20→15 (-5), fp +13→32 (+19), pending 7→0 (-7)
- `JSS-CAP-004`: tp +15→19 (+4), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-CODE-001`: tp +30→421 (+391), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-CODE-002`: tp +14→248 (+234), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-CODE-003`: tp +150→2072 (+1922), fp +3→14 (+11), pending 0→0 (+0)
- `JSS-HOUSE-001`: tp +548→590 (+42), fp +2→2 (+0), pending 0→0 (+0)
- `JSS-HOUSE-002`: tp +27→31 (+4), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-HOUSE-003`: tp +44→50 (+6), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-MARKUP-001`: tp +1040→1089 (+49), fp +106→168 (+62), pending 6→0 (-6)
- `JSS-MARKUP-002`: tp +226→236 (+10), fp +15→14 (-1), pending 0→0 (+0)
- `JSS-MARKUP-003`: tp +366→1666 (+1300), fp +2→149 (+147), pending 7→0 (-7)
- `JSS-MARKUP-004`: tp +136→135 (-1), fp +0→1 (+1), pending 0→0 (+0)
- `JSS-NAME-001`: tp +10→11 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-NAME-002`: tp +105→155 (+50), fp +1→1 (+0), pending 6→0 (-6)
- `JSS-OPER-001`: tp +81→79 (-2), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-OPER-002`: tp +70→146 (+76), fp +1→159 (+158), pending 18→0 (-18)
- `JSS-OPER-003`: tp +18→369 (+351), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-OPER-004`: tp +68→89 (+21), fp +1→7 (+6), pending 2→0 (-2)
- `JSS-PRE-006`: tp +20→21 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-REFS-003`: tp +1758→2023 (+265), fp +46→56 (+10), pending 0→0 (+0)
- `JSS-REFS-004`: tp +244→537 (+293), fp +0→1 (+1), pending 1→0 (-1)
- `JSS-REFS-005`: tp +40→44 (+4), fp +1→2 (+1), pending 0→0 (+0)
- `JSS-REFS-006`: tp +152→900 (+748), fp +2→31 (+29), pending 0→0 (+0)
- `JSS-REFS-007`: tp +131→141 (+10), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-STRUCT-001`: tp +76→81 (+5), fp +2→2 (+0), pending 0→0 (+0)
- `JSS-STRUCT-002`: tp +28→31 (+3), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-STRUCT-004`: tp +6→7 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-STRUCT-005`: tp +4→34 (+30), fp +0→10 (+10), pending 0→0 (+0)
- `JSS-STRUCT-006`: tp +5→8 (+3), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-TYPO-001`: tp +205→212 (+7), fp +0→0 (+0), pending 0→0 (+0)
- **new** `JSS-TYPO-002`: tp=1 fp=0 pending=0
- `JSS-TYPO-004`: tp +27→62 (+35), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-WIDTH-001`: tp +53→361 (+308), fp +0→12 (+12), pending 0→0 (+0)
- `JSS-XREF-001`: tp +35→37 (+2), fp +1→11 (+10), pending 1→0 (-1)
- `JSS-XREF-002`: tp +465→817 (+352), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-XREF-004`: tp +351→815 (+464), fp +1→32 (+31), pending 3→0 (-3)
- **new** `JSS-XREF-005`: tp=179 fp=0 pending=0

**Pinned only**

- `JSS-CITE-002`: tp +86→95 (+9), fp +18→16 (-2), pending 1→0 (-1)
- `JSS-CITE-003`: tp +16→171 (+155), fp +0→0 (+0), pending 2→0 (-2)
- `JSS-ABBR-001`: tp +11→25 (+14), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-BIBTEX-002`: tp +6→7 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-BIBTEX-003`: tp +46→53 (+7), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-BIBTEX-004`: tp +76→91 (+15), fp +0→0 (+0), pending 4→0 (-4)
- **new** `JSS-BIBTEX-005`: tp=9 fp=0 pending=0
- `JSS-CAP-001`: tp +2→47 (+45), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-CAP-002`: tp +103→293 (+190), fp +15→12 (-3), pending 0→0 (+0)
- `JSS-CAP-003`: tp +13→7 (-6), fp +10→28 (+18), pending 7→0 (-7)
- `JSS-CAP-004`: tp +12→15 (+3), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-CODE-001`: tp +25→258 (+233), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-CODE-002`: tp +14→171 (+157), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-CODE-003`: tp +98→1303 (+1205), fp +3→11 (+8), pending 0→0 (+0)
- `JSS-HOUSE-001`: tp +255→293 (+38), fp +2→2 (+0), pending 0→0 (+0)
- `JSS-HOUSE-002`: tp +27→31 (+4), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-HOUSE-003`: tp +37→43 (+6), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-MARKUP-001`: tp +439→463 (+24), fp +58→104 (+46), pending 5→0 (-5)
- `JSS-MARKUP-002`: tp +107→116 (+9), fp +3→2 (-1), pending 0→0 (+0)
- `JSS-MARKUP-003`: tp +191→616 (+425), fp +2→78 (+76), pending 7→0 (-7)
- `JSS-MARKUP-004`: tp +34→33 (-1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-NAME-002`: tp +105→155 (+50), fp +1→1 (+0), pending 6→0 (-6)
- `JSS-OPER-002`: tp +53→98 (+45), fp +1→113 (+112), pending 14→0 (-14)
- `JSS-OPER-003`: tp +5→283 (+278), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-OPER-004`: tp +55→67 (+12), fp +1→6 (+5), pending 0→0 (+0)
- `JSS-PRE-001`: tp +18→17 (-1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-PRE-006`: tp +13→15 (+2), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-REFS-003`: tp +1758→2023 (+265), fp +46→56 (+10), pending 0→0 (+0)
- `JSS-REFS-004`: tp +244→537 (+293), fp +0→1 (+1), pending 1→0 (-1)
- `JSS-REFS-005`: tp +40→44 (+4), fp +1→2 (+1), pending 0→0 (+0)
- `JSS-REFS-006`: tp +152→900 (+748), fp +2→31 (+29), pending 0→0 (+0)
- `JSS-REFS-007`: tp +131→141 (+10), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-STRUCT-001`: tp +40→45 (+5), fp +1→1 (+0), pending 0→0 (+0)
- `JSS-STRUCT-002`: tp +19→22 (+3), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-STRUCT-004`: tp +5→6 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-STRUCT-005`: tp +3→19 (+16), fp +0→9 (+9), pending 0→0 (+0)
- `JSS-STRUCT-006`: tp +4→5 (+1), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-TYPO-001`: tp +113→119 (+6), fp +0→0 (+0), pending 0→0 (+0)
- **new** `JSS-TYPO-002`: tp=1 fp=0 pending=0
- `JSS-TYPO-004`: tp +25→45 (+20), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-WIDTH-001`: tp +44→188 (+144), fp +0→6 (+6), pending 0→0 (+0)
- `JSS-XREF-001`: tp +23→24 (+1), fp +0→8 (+8), pending 1→0 (-1)
- `JSS-XREF-002`: tp +354→627 (+273), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-XREF-004`: tp +266→609 (+343), fp +1→27 (+26), pending 1→0 (-1)
- **new** `JSS-XREF-005`: tp=125 fp=0 pending=0

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 80 — 2026-06-22T09:14:49Z — post-fn-fixes

- **Corpus size:** 244 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=38, pinned=29

**Note:** Deterministic FN/FP fixes: CODE-003 <- ->  <<- and == != <= >=; XREF-004 per-label in multi-line eq envs; OPER-003 covers \[ \] / $$ display math; MARKUP-001 skips emphasised acronym initials. AI-reviewed: OPER-003 +507 TP/0 FP, CODE-003 0.993, XREF-004 0.960. 26 uncertain (XREF-006 x16, XREF-004 x10) pending human review.

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 201 | 20 | 0 | 90.95% | PASS |
| citation | JSS-CITE-003 | 236 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 110 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-005 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-001 | 101 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 502 | 17 | 0 | 96.72% | PASS |
| unknown | JSS-CAP-003 | 15 | 32 | 0 | 31.91% | FAIL |
| unknown | JSS-CAP-004 | 19 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 421 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 248 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 2109 | 14 | 0 | 99.34% | PASS |
| unknown | JSS-HOUSE-001 | 590 | 2 | 0 | 99.66% | PASS |
| unknown | JSS-HOUSE-002 | 31 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 50 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 1088 | 167 | 0 | 86.69% | FAIL |
| unknown | JSS-MARKUP-002 | 236 | 14 | 0 | 94.40% | PASS |
| unknown | JSS-MARKUP-003 | 1667 | 149 | 0 | 91.80% | PASS |
| unknown | JSS-MARKUP-004 | 135 | 1 | 0 | 99.26% | PASS |
| unknown | JSS-NAME-001 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 155 | 1 | 0 | 99.36% | PASS |
| unknown | JSS-OPER-001 | 79 | 1 | 0 | 98.75% | PASS |
| unknown | JSS-OPER-002 | 146 | 159 | 0 | 47.87% | FAIL |
| unknown | JSS-OPER-003 | 507 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 89 | 7 | 0 | 92.71% | PASS |
| unknown | JSS-PRE-001 | 66 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 21 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 2023 | 56 | 0 | 97.31% | PASS |
| unknown | JSS-REFS-004 | 537 | 1 | 0 | 99.81% | PASS |
| unknown | JSS-REFS-005 | 44 | 2 | 0 | 95.65% | PASS |
| unknown | JSS-REFS-006 | 900 | 31 | 0 | 96.67% | PASS |
| unknown | JSS-REFS-007 | 141 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 81 | 2 | 0 | 97.59% | PASS |
| unknown | JSS-STRUCT-002 | 31 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 34 | 10 | 0 | 77.27% | FAIL |
| unknown | JSS-STRUCT-006 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 212 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 62 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-WIDTH-001 | 361 | 12 | 0 | 96.78% | PASS |
| unknown | JSS-XREF-001 | 37 | 11 | 0 | 77.08% | FAIL |
| unknown | JSS-XREF-002 | 817 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 824 | 34 | 10 | 96.04% | PASS |
| unknown | JSS-XREF-005 | 179 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-006 | 0 | 0 | 16 | — | NOT MEASURED |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 95 | 16 | 0 | 85.59% | FAIL |
| citation | JSS-CITE-003 | 171 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 91 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-005 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-001 | 47 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 293 | 12 | 0 | 96.07% | PASS |
| unknown | JSS-CAP-003 | 7 | 28 | 0 | 20.00% | FAIL |
| unknown | JSS-CAP-004 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 258 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 171 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 1332 | 11 | 0 | 99.18% | PASS |
| unknown | JSS-HOUSE-001 | 293 | 2 | 0 | 99.32% | PASS |
| unknown | JSS-HOUSE-002 | 31 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 43 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 462 | 103 | 0 | 81.77% | FAIL |
| unknown | JSS-MARKUP-002 | 116 | 2 | 0 | 98.31% | PASS |
| unknown | JSS-MARKUP-003 | 617 | 78 | 0 | 88.78% | FAIL |
| unknown | JSS-MARKUP-004 | 33 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 155 | 1 | 0 | 99.36% | PASS |
| unknown | JSS-OPER-001 | 27 | 1 | 0 | 96.43% | PASS |
| unknown | JSS-OPER-002 | 98 | 113 | 0 | 46.45% | FAIL |
| unknown | JSS-OPER-003 | 349 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 67 | 6 | 0 | 91.78% | PASS |
| unknown | JSS-PRE-001 | 17 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 2023 | 56 | 0 | 97.31% | PASS |
| unknown | JSS-REFS-004 | 537 | 1 | 0 | 99.81% | PASS |
| unknown | JSS-REFS-005 | 44 | 2 | 0 | 95.65% | PASS |
| unknown | JSS-REFS-006 | 900 | 31 | 0 | 96.67% | PASS |
| unknown | JSS-REFS-007 | 141 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 45 | 1 | 0 | 97.83% | PASS |
| unknown | JSS-STRUCT-002 | 22 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 19 | 9 | 0 | 67.86% | FAIL |
| unknown | JSS-STRUCT-006 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 119 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 45 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-WIDTH-001 | 188 | 6 | 0 | 96.91% | PASS |
| unknown | JSS-XREF-001 | 24 | 8 | 0 | 75.00% | FAIL |
| unknown | JSS-XREF-002 | 627 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 617 | 29 | 8 | 95.51% | PASS |
| unknown | JSS-XREF-005 | 125 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-006 | 0 | 0 | 6 | — | NOT MEASURED |

### Delta vs. previous iteration

**Full corpus**

- `JSS-ABBR-001`: tp +30→18 (-12), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-CODE-003`: tp +2072→2109 (+37), fp +14→14 (+0), pending 0→0 (+0)
- `JSS-MARKUP-001`: tp +1089→1088 (-1), fp +168→167 (-1), pending 0→0 (+0)
- `JSS-MARKUP-003`: tp +1666→1667 (+1), fp +149→149 (+0), pending 0→0 (+0)
- `JSS-OPER-003`: tp +369→507 (+138), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-XREF-004`: tp +815→824 (+9), fp +32→34 (+2), pending 0→10 (+10)
- **new** `JSS-XREF-006`: tp=0 fp=0 pending=16

**Pinned only**

- `JSS-ABBR-001`: tp +25→13 (-12), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-CODE-003`: tp +1303→1332 (+29), fp +11→11 (+0), pending 0→0 (+0)
- `JSS-MARKUP-001`: tp +463→462 (-1), fp +104→103 (-1), pending 0→0 (+0)
- `JSS-MARKUP-003`: tp +616→617 (+1), fp +78→78 (+0), pending 0→0 (+0)
- `JSS-OPER-003`: tp +283→349 (+66), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-XREF-004`: tp +609→617 (+8), fp +27→29 (+2), pending 0→8 (+8)
- **new** `JSS-XREF-006`: tp=0 fp=0 pending=6

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 81 — 2026-06-22T17:36:21Z — post-fn-fixes-hr

- **Corpus size:** 244 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=38, pinned=29

**Note:** Post-human-review of iteration 80's 26 uncertain. XREF-006 (new no-caption-float rule) 15 TP/1 FP=0.938; XREF-004 832/36=0.959 (2 implicit-range FPs). 0 pending. Both FPs are semantic edge cases (adjacent-table caption; range references), not rule defects.

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 201 | 20 | 0 | 90.95% | PASS |
| citation | JSS-CITE-003 | 236 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 110 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-005 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-001 | 101 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 502 | 17 | 0 | 96.72% | PASS |
| unknown | JSS-CAP-003 | 15 | 32 | 0 | 31.91% | FAIL |
| unknown | JSS-CAP-004 | 19 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 421 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 248 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 2109 | 14 | 0 | 99.34% | PASS |
| unknown | JSS-HOUSE-001 | 590 | 2 | 0 | 99.66% | PASS |
| unknown | JSS-HOUSE-002 | 31 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 50 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 1088 | 167 | 0 | 86.69% | FAIL |
| unknown | JSS-MARKUP-002 | 236 | 14 | 0 | 94.40% | PASS |
| unknown | JSS-MARKUP-003 | 1667 | 149 | 0 | 91.80% | PASS |
| unknown | JSS-MARKUP-004 | 135 | 1 | 0 | 99.26% | PASS |
| unknown | JSS-NAME-001 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 155 | 1 | 0 | 99.36% | PASS |
| unknown | JSS-OPER-001 | 79 | 1 | 0 | 98.75% | PASS |
| unknown | JSS-OPER-002 | 146 | 159 | 0 | 47.87% | FAIL |
| unknown | JSS-OPER-003 | 507 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 89 | 7 | 0 | 92.71% | PASS |
| unknown | JSS-PRE-001 | 66 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 21 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 2023 | 56 | 0 | 97.31% | PASS |
| unknown | JSS-REFS-004 | 537 | 1 | 0 | 99.81% | PASS |
| unknown | JSS-REFS-005 | 44 | 2 | 0 | 95.65% | PASS |
| unknown | JSS-REFS-006 | 900 | 31 | 0 | 96.67% | PASS |
| unknown | JSS-REFS-007 | 141 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 81 | 2 | 0 | 97.59% | PASS |
| unknown | JSS-STRUCT-002 | 31 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 34 | 10 | 0 | 77.27% | FAIL |
| unknown | JSS-STRUCT-006 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 212 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 62 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-WIDTH-001 | 361 | 12 | 0 | 96.78% | PASS |
| unknown | JSS-XREF-001 | 37 | 11 | 0 | 77.08% | FAIL |
| unknown | JSS-XREF-002 | 817 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 832 | 36 | 0 | 95.85% | PASS |
| unknown | JSS-XREF-005 | 179 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-006 | 15 | 1 | 0 | 93.75% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 95 | 16 | 0 | 85.59% | FAIL |
| citation | JSS-CITE-003 | 171 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 91 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-005 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-001 | 47 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 293 | 12 | 0 | 96.07% | PASS |
| unknown | JSS-CAP-003 | 7 | 28 | 0 | 20.00% | FAIL |
| unknown | JSS-CAP-004 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 258 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 171 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 1332 | 11 | 0 | 99.18% | PASS |
| unknown | JSS-HOUSE-001 | 293 | 2 | 0 | 99.32% | PASS |
| unknown | JSS-HOUSE-002 | 31 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 43 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 462 | 103 | 0 | 81.77% | FAIL |
| unknown | JSS-MARKUP-002 | 116 | 2 | 0 | 98.31% | PASS |
| unknown | JSS-MARKUP-003 | 617 | 78 | 0 | 88.78% | FAIL |
| unknown | JSS-MARKUP-004 | 33 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 155 | 1 | 0 | 99.36% | PASS |
| unknown | JSS-OPER-001 | 27 | 1 | 0 | 96.43% | PASS |
| unknown | JSS-OPER-002 | 98 | 113 | 0 | 46.45% | FAIL |
| unknown | JSS-OPER-003 | 349 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 67 | 6 | 0 | 91.78% | PASS |
| unknown | JSS-PRE-001 | 17 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 2023 | 56 | 0 | 97.31% | PASS |
| unknown | JSS-REFS-004 | 537 | 1 | 0 | 99.81% | PASS |
| unknown | JSS-REFS-005 | 44 | 2 | 0 | 95.65% | PASS |
| unknown | JSS-REFS-006 | 900 | 31 | 0 | 96.67% | PASS |
| unknown | JSS-REFS-007 | 141 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 45 | 1 | 0 | 97.83% | PASS |
| unknown | JSS-STRUCT-002 | 22 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 19 | 9 | 0 | 67.86% | FAIL |
| unknown | JSS-STRUCT-006 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 119 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 45 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-WIDTH-001 | 188 | 6 | 0 | 96.91% | PASS |
| unknown | JSS-XREF-001 | 24 | 8 | 0 | 75.00% | FAIL |
| unknown | JSS-XREF-002 | 627 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 623 | 31 | 0 | 95.26% | PASS |
| unknown | JSS-XREF-005 | 125 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-006 | 6 | 0 | 0 | 100.00% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-XREF-004`: tp +824→832 (+8), fp +34→36 (+2), pending 10→0 (-10)
- `JSS-XREF-006`: tp +0→15 (+15), fp +0→1 (+1), pending 16→0 (-16)

**Pinned only**

- `JSS-XREF-004`: tp +617→623 (+6), fp +29→31 (+2), pending 8→0 (-8)
- `JSS-XREF-006`: tp +0→6 (+6), fp +0→0 (+0), pending 6→0 (-6)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 82 — 2026-06-24T20:06:25Z — post-tag-section-exempt

- **Corpus size:** 244 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=38, pinned=29

**Note:** Folded in XREF-004 \tag exemption and OPER-003 blank-before-sectioning carve-out (from trueskill FP review). Refresh: 16056/16077 restored, 21 orphaned (all previously-TP \tag/sectioning firings now exempt; incl. 1 human-labeled surveillance align of \tag'd predictors — same idiom, consistent with the exemption). 0 unlabelled; no AI review needed (fixes only remove firings).

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 201 | 20 | 0 | 90.95% | PASS |
| citation | JSS-CITE-003 | 236 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 110 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-005 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-001 | 101 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 502 | 17 | 0 | 96.72% | PASS |
| unknown | JSS-CAP-003 | 15 | 32 | 0 | 31.91% | FAIL |
| unknown | JSS-CAP-004 | 19 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 421 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 248 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 2109 | 14 | 0 | 99.34% | PASS |
| unknown | JSS-HOUSE-001 | 590 | 2 | 0 | 99.66% | PASS |
| unknown | JSS-HOUSE-002 | 31 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 50 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 1088 | 167 | 0 | 86.69% | FAIL |
| unknown | JSS-MARKUP-002 | 236 | 14 | 0 | 94.40% | PASS |
| unknown | JSS-MARKUP-003 | 1667 | 149 | 0 | 91.80% | PASS |
| unknown | JSS-MARKUP-004 | 135 | 1 | 0 | 99.26% | PASS |
| unknown | JSS-NAME-001 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 155 | 1 | 0 | 99.36% | PASS |
| unknown | JSS-OPER-001 | 79 | 1 | 0 | 98.75% | PASS |
| unknown | JSS-OPER-002 | 146 | 159 | 0 | 47.87% | FAIL |
| unknown | JSS-OPER-003 | 491 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 89 | 7 | 0 | 92.71% | PASS |
| unknown | JSS-PRE-001 | 66 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 21 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 2023 | 56 | 0 | 97.31% | PASS |
| unknown | JSS-REFS-004 | 537 | 1 | 0 | 99.81% | PASS |
| unknown | JSS-REFS-005 | 44 | 2 | 0 | 95.65% | PASS |
| unknown | JSS-REFS-006 | 900 | 31 | 0 | 96.67% | PASS |
| unknown | JSS-REFS-007 | 141 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 81 | 2 | 0 | 97.59% | PASS |
| unknown | JSS-STRUCT-002 | 31 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 34 | 10 | 0 | 77.27% | FAIL |
| unknown | JSS-STRUCT-006 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 212 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 62 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-WIDTH-001 | 361 | 12 | 0 | 96.78% | PASS |
| unknown | JSS-XREF-001 | 37 | 11 | 0 | 77.08% | FAIL |
| unknown | JSS-XREF-002 | 817 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 827 | 36 | 0 | 95.83% | PASS |
| unknown | JSS-XREF-005 | 179 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-006 | 15 | 1 | 0 | 93.75% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 95 | 16 | 0 | 85.59% | FAIL |
| citation | JSS-CITE-003 | 171 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 91 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-005 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-001 | 47 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 293 | 12 | 0 | 96.07% | PASS |
| unknown | JSS-CAP-003 | 7 | 28 | 0 | 20.00% | FAIL |
| unknown | JSS-CAP-004 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 258 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 171 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 1332 | 11 | 0 | 99.18% | PASS |
| unknown | JSS-HOUSE-001 | 293 | 2 | 0 | 99.32% | PASS |
| unknown | JSS-HOUSE-002 | 31 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 43 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 462 | 103 | 0 | 81.77% | FAIL |
| unknown | JSS-MARKUP-002 | 116 | 2 | 0 | 98.31% | PASS |
| unknown | JSS-MARKUP-003 | 617 | 78 | 0 | 88.78% | FAIL |
| unknown | JSS-MARKUP-004 | 33 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 155 | 1 | 0 | 99.36% | PASS |
| unknown | JSS-OPER-001 | 27 | 1 | 0 | 96.43% | PASS |
| unknown | JSS-OPER-002 | 98 | 113 | 0 | 46.45% | FAIL |
| unknown | JSS-OPER-003 | 337 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 67 | 6 | 0 | 91.78% | PASS |
| unknown | JSS-PRE-001 | 17 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 2023 | 56 | 0 | 97.31% | PASS |
| unknown | JSS-REFS-004 | 537 | 1 | 0 | 99.81% | PASS |
| unknown | JSS-REFS-005 | 44 | 2 | 0 | 95.65% | PASS |
| unknown | JSS-REFS-006 | 900 | 31 | 0 | 96.67% | PASS |
| unknown | JSS-REFS-007 | 141 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 45 | 1 | 0 | 97.83% | PASS |
| unknown | JSS-STRUCT-002 | 22 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 19 | 9 | 0 | 67.86% | FAIL |
| unknown | JSS-STRUCT-006 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 119 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 45 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-WIDTH-001 | 188 | 6 | 0 | 96.91% | PASS |
| unknown | JSS-XREF-001 | 24 | 8 | 0 | 75.00% | FAIL |
| unknown | JSS-XREF-002 | 627 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 619 | 31 | 0 | 95.23% | PASS |
| unknown | JSS-XREF-005 | 125 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-006 | 6 | 0 | 0 | 100.00% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-OPER-003`: tp +507→491 (-16), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-XREF-004`: tp +832→827 (-5), fp +36→36 (+0), pending 0→0 (+0)

**Pinned only**

- `JSS-OPER-003`: tp +349→337 (-12), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-XREF-004`: tp +623→619 (-4), fp +31→31 (+0), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 83 — 2026-06-25T19:24:03Z — post-cap004-leading-cap

- **Corpus size:** 244 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=38, pinned=29

**Note:** CAP-004 gained a leading-capital check (first \Keywords entry must be sentence case). Refresh: 16056/16056 restored, 0 orphaned (only adds firings). AI review (bonsai): 154 new firings all TP, 0 uncertain, 0 FP. CAP-004 now 173 TP / 0 FP = 1.000 — a pure recall gain (+154 TP), as it was already at 100% precision but low-recall (19/19, title-case only) at iter 82. \Plainkeywords deliberately not checked.

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 201 | 20 | 0 | 90.95% | PASS |
| citation | JSS-CITE-003 | 236 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 110 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-005 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-001 | 101 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 502 | 17 | 0 | 96.72% | PASS |
| unknown | JSS-CAP-003 | 15 | 32 | 0 | 31.91% | FAIL |
| unknown | JSS-CAP-004 | 173 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 421 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 248 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 2109 | 14 | 0 | 99.34% | PASS |
| unknown | JSS-HOUSE-001 | 590 | 2 | 0 | 99.66% | PASS |
| unknown | JSS-HOUSE-002 | 31 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 50 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 1088 | 167 | 0 | 86.69% | FAIL |
| unknown | JSS-MARKUP-002 | 236 | 14 | 0 | 94.40% | PASS |
| unknown | JSS-MARKUP-003 | 1667 | 149 | 0 | 91.80% | PASS |
| unknown | JSS-MARKUP-004 | 135 | 1 | 0 | 99.26% | PASS |
| unknown | JSS-NAME-001 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 155 | 1 | 0 | 99.36% | PASS |
| unknown | JSS-OPER-001 | 79 | 1 | 0 | 98.75% | PASS |
| unknown | JSS-OPER-002 | 146 | 159 | 0 | 47.87% | FAIL |
| unknown | JSS-OPER-003 | 491 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 89 | 7 | 0 | 92.71% | PASS |
| unknown | JSS-PRE-001 | 66 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 21 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 2023 | 56 | 0 | 97.31% | PASS |
| unknown | JSS-REFS-004 | 537 | 1 | 0 | 99.81% | PASS |
| unknown | JSS-REFS-005 | 44 | 2 | 0 | 95.65% | PASS |
| unknown | JSS-REFS-006 | 900 | 31 | 0 | 96.67% | PASS |
| unknown | JSS-REFS-007 | 141 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 81 | 2 | 0 | 97.59% | PASS |
| unknown | JSS-STRUCT-002 | 31 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 34 | 10 | 0 | 77.27% | FAIL |
| unknown | JSS-STRUCT-006 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 212 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 62 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-WIDTH-001 | 361 | 12 | 0 | 96.78% | PASS |
| unknown | JSS-XREF-001 | 37 | 11 | 0 | 77.08% | FAIL |
| unknown | JSS-XREF-002 | 817 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 827 | 36 | 0 | 95.83% | PASS |
| unknown | JSS-XREF-005 | 179 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-006 | 15 | 1 | 0 | 93.75% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 95 | 16 | 0 | 85.59% | FAIL |
| citation | JSS-CITE-003 | 171 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 91 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-005 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-001 | 47 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 293 | 12 | 0 | 96.07% | PASS |
| unknown | JSS-CAP-003 | 7 | 28 | 0 | 20.00% | FAIL |
| unknown | JSS-CAP-004 | 129 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 258 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 171 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 1332 | 11 | 0 | 99.18% | PASS |
| unknown | JSS-HOUSE-001 | 293 | 2 | 0 | 99.32% | PASS |
| unknown | JSS-HOUSE-002 | 31 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 43 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 462 | 103 | 0 | 81.77% | FAIL |
| unknown | JSS-MARKUP-002 | 116 | 2 | 0 | 98.31% | PASS |
| unknown | JSS-MARKUP-003 | 617 | 78 | 0 | 88.78% | FAIL |
| unknown | JSS-MARKUP-004 | 33 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 155 | 1 | 0 | 99.36% | PASS |
| unknown | JSS-OPER-001 | 27 | 1 | 0 | 96.43% | PASS |
| unknown | JSS-OPER-002 | 98 | 113 | 0 | 46.45% | FAIL |
| unknown | JSS-OPER-003 | 337 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 67 | 6 | 0 | 91.78% | PASS |
| unknown | JSS-PRE-001 | 17 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 2023 | 56 | 0 | 97.31% | PASS |
| unknown | JSS-REFS-004 | 537 | 1 | 0 | 99.81% | PASS |
| unknown | JSS-REFS-005 | 44 | 2 | 0 | 95.65% | PASS |
| unknown | JSS-REFS-006 | 900 | 31 | 0 | 96.67% | PASS |
| unknown | JSS-REFS-007 | 141 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 45 | 1 | 0 | 97.83% | PASS |
| unknown | JSS-STRUCT-002 | 22 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 19 | 9 | 0 | 67.86% | FAIL |
| unknown | JSS-STRUCT-006 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 119 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 45 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-WIDTH-001 | 188 | 6 | 0 | 96.91% | PASS |
| unknown | JSS-XREF-001 | 24 | 8 | 0 | 75.00% | FAIL |
| unknown | JSS-XREF-002 | 627 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 619 | 31 | 0 | 95.23% | PASS |
| unknown | JSS-XREF-005 | 125 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-006 | 6 | 0 | 0 | 100.00% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-CAP-004`: tp +19→173 (+154), fp +0→0 (+0), pending 0→0 (+0)

**Pinned only**

- `JSS-CAP-004`: tp +15→129 (+114), fp +0→0 (+0), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 84 — 2026-06-28T11:23:01Z — post-xref001-cite003-fp

- **Corpus size:** 244 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=38, pinned=29

**Note:** Folded in XREF-001 citation-locator exemption and CITE-003 lone-(\citeyear{}) narrative exemption (from HardyWeinberg FP review). Refresh: 16182/16210 restored, 28 orphaned (11 XREF-001 + 17 CITE-003): 8 were human-labeled FP (agreement), 19 AI-mislabeled TP (corrected), 1 human TP at cran_HardyWeinberg:373 — the same narrative \citeyear Manuel documented as a non-violation in the recall corpus. 0 unlabelled; no AI review (fixes only remove firings).

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 201 | 20 | 0 | 90.95% | PASS |
| citation | JSS-CITE-003 | 219 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 110 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-005 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-001 | 101 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 502 | 17 | 0 | 96.72% | PASS |
| unknown | JSS-CAP-003 | 15 | 32 | 0 | 31.91% | FAIL |
| unknown | JSS-CAP-004 | 173 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 421 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 248 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 2109 | 14 | 0 | 99.34% | PASS |
| unknown | JSS-HOUSE-001 | 590 | 2 | 0 | 99.66% | PASS |
| unknown | JSS-HOUSE-002 | 31 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 50 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 1088 | 167 | 0 | 86.69% | FAIL |
| unknown | JSS-MARKUP-002 | 236 | 14 | 0 | 94.40% | PASS |
| unknown | JSS-MARKUP-003 | 1667 | 149 | 0 | 91.80% | PASS |
| unknown | JSS-MARKUP-004 | 135 | 1 | 0 | 99.26% | PASS |
| unknown | JSS-NAME-001 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 155 | 1 | 0 | 99.36% | PASS |
| unknown | JSS-OPER-001 | 79 | 1 | 0 | 98.75% | PASS |
| unknown | JSS-OPER-002 | 146 | 159 | 0 | 47.87% | FAIL |
| unknown | JSS-OPER-003 | 491 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 89 | 7 | 0 | 92.71% | PASS |
| unknown | JSS-PRE-001 | 66 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 21 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 2023 | 56 | 0 | 97.31% | PASS |
| unknown | JSS-REFS-004 | 537 | 1 | 0 | 99.81% | PASS |
| unknown | JSS-REFS-005 | 44 | 2 | 0 | 95.65% | PASS |
| unknown | JSS-REFS-006 | 900 | 31 | 0 | 96.67% | PASS |
| unknown | JSS-REFS-007 | 141 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 81 | 2 | 0 | 97.59% | PASS |
| unknown | JSS-STRUCT-002 | 31 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 34 | 10 | 0 | 77.27% | FAIL |
| unknown | JSS-STRUCT-006 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 212 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 62 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-WIDTH-001 | 361 | 12 | 0 | 96.78% | PASS |
| unknown | JSS-XREF-001 | 34 | 3 | 0 | 91.89% | PASS |
| unknown | JSS-XREF-002 | 817 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 827 | 36 | 0 | 95.83% | PASS |
| unknown | JSS-XREF-005 | 179 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-006 | 15 | 1 | 0 | 93.75% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 95 | 16 | 0 | 85.59% | FAIL |
| citation | JSS-CITE-003 | 154 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 91 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-005 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-001 | 47 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 293 | 12 | 0 | 96.07% | PASS |
| unknown | JSS-CAP-003 | 7 | 28 | 0 | 20.00% | FAIL |
| unknown | JSS-CAP-004 | 129 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 258 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 171 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 1332 | 11 | 0 | 99.18% | PASS |
| unknown | JSS-HOUSE-001 | 293 | 2 | 0 | 99.32% | PASS |
| unknown | JSS-HOUSE-002 | 31 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 43 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 462 | 103 | 0 | 81.77% | FAIL |
| unknown | JSS-MARKUP-002 | 116 | 2 | 0 | 98.31% | PASS |
| unknown | JSS-MARKUP-003 | 617 | 78 | 0 | 88.78% | FAIL |
| unknown | JSS-MARKUP-004 | 33 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 155 | 1 | 0 | 99.36% | PASS |
| unknown | JSS-OPER-001 | 27 | 1 | 0 | 96.43% | PASS |
| unknown | JSS-OPER-002 | 98 | 113 | 0 | 46.45% | FAIL |
| unknown | JSS-OPER-003 | 337 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 67 | 6 | 0 | 91.78% | PASS |
| unknown | JSS-PRE-001 | 17 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 2023 | 56 | 0 | 97.31% | PASS |
| unknown | JSS-REFS-004 | 537 | 1 | 0 | 99.81% | PASS |
| unknown | JSS-REFS-005 | 44 | 2 | 0 | 95.65% | PASS |
| unknown | JSS-REFS-006 | 900 | 31 | 0 | 96.67% | PASS |
| unknown | JSS-REFS-007 | 141 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 45 | 1 | 0 | 97.83% | PASS |
| unknown | JSS-STRUCT-002 | 22 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 19 | 9 | 0 | 67.86% | FAIL |
| unknown | JSS-STRUCT-006 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 119 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 45 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-WIDTH-001 | 188 | 6 | 0 | 96.91% | PASS |
| unknown | JSS-XREF-001 | 22 | 2 | 0 | 91.67% | PASS |
| unknown | JSS-XREF-002 | 627 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 619 | 31 | 0 | 95.23% | PASS |
| unknown | JSS-XREF-005 | 125 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-006 | 6 | 0 | 0 | 100.00% | PASS |

### Delta vs. previous iteration

**Full corpus**

- `JSS-CITE-003`: tp +236→219 (-17), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-XREF-001`: tp +37→34 (-3), fp +11→3 (-8), pending 0→0 (+0)

**Pinned only**

- `JSS-CITE-003`: tp +171→154 (-17), fp +0→0 (+0), pending 0→0 (+0)
- `JSS-XREF-001`: tp +24→22 (-2), fp +8→2 (-6), pending 0→0 (+0)

### Findings / suggestions

_(fill in)_

### Plan

_(fill in)_

### Results (post-implementation)

_(fill in after the next `eval-jss iterate record` run)_

## Iteration 85 — 2026-06-28T12:14:20Z — post-house003-options

- **Corpus size:** 244 papers
- **Tool version:** `0.1.0`
- **Parse failures:** full=38, pinned=29

**Note:** HOUSE-003 options-handling change (advise \PassOptionsToPackage + withhold delete-fix when a jss-loaded package is loaded with options). The firing SET is unchanged — eval.db keys on the catalogue message, not the per-firing suggestion/fix — so refresh was clean (16182/16182 restored, 0 orphaned, 0 unlabelled) and metrics are unmoved (HOUSE-003 50 TP / 0 FP). Change is advisory text + autofix safety only.

### Stats — full corpus

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 201 | 20 | 0 | 90.95% | PASS |
| citation | JSS-CITE-003 | 219 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 20 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 18 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 110 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-005 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-001 | 101 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 502 | 17 | 0 | 96.72% | PASS |
| unknown | JSS-CAP-003 | 15 | 32 | 0 | 31.91% | FAIL |
| unknown | JSS-CAP-004 | 173 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 421 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 248 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 2109 | 14 | 0 | 99.34% | PASS |
| unknown | JSS-HOUSE-001 | 590 | 2 | 0 | 99.66% | PASS |
| unknown | JSS-HOUSE-002 | 31 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 50 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 1088 | 167 | 0 | 86.69% | FAIL |
| unknown | JSS-MARKUP-002 | 236 | 14 | 0 | 94.40% | PASS |
| unknown | JSS-MARKUP-003 | 1667 | 149 | 0 | 91.80% | PASS |
| unknown | JSS-MARKUP-004 | 135 | 1 | 0 | 99.26% | PASS |
| unknown | JSS-NAME-001 | 11 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 155 | 1 | 0 | 99.36% | PASS |
| unknown | JSS-OPER-001 | 79 | 1 | 0 | 98.75% | PASS |
| unknown | JSS-OPER-002 | 146 | 159 | 0 | 47.87% | FAIL |
| unknown | JSS-OPER-003 | 491 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 89 | 7 | 0 | 92.71% | PASS |
| unknown | JSS-PRE-001 | 66 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 21 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 2023 | 56 | 0 | 97.31% | PASS |
| unknown | JSS-REFS-004 | 537 | 1 | 0 | 99.81% | PASS |
| unknown | JSS-REFS-005 | 44 | 2 | 0 | 95.65% | PASS |
| unknown | JSS-REFS-006 | 900 | 31 | 0 | 96.67% | PASS |
| unknown | JSS-REFS-007 | 141 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 81 | 2 | 0 | 97.59% | PASS |
| unknown | JSS-STRUCT-002 | 31 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 34 | 10 | 0 | 77.27% | FAIL |
| unknown | JSS-STRUCT-006 | 8 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 212 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 10 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 62 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-WIDTH-001 | 361 | 12 | 0 | 96.78% | PASS |
| unknown | JSS-XREF-001 | 34 | 3 | 0 | 91.89% | PASS |
| unknown | JSS-XREF-002 | 817 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 827 | 36 | 0 | 95.83% | PASS |
| unknown | JSS-XREF-005 | 179 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-006 | 15 | 1 | 0 | 93.75% | PASS |

### Stats — pinned only

| category | rule | tp | fp | pending | precision | status |
|---|---|---:|---:|---:|---:|---|
| citation | JSS-CITE-002 | 95 | 16 | 0 | 85.59% | FAIL |
| citation | JSS-CITE-003 | 154 | 0 | 0 | 100.00% | PASS |
| citation | JSS-CITE-004 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-ABBR-001 | 13 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-002 | 7 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-003 | 53 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-004 | 91 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-BIBTEX-005 | 9 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-001 | 47 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CAP-002 | 293 | 12 | 0 | 96.07% | PASS |
| unknown | JSS-CAP-003 | 7 | 28 | 0 | 20.00% | FAIL |
| unknown | JSS-CAP-004 | 129 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-001 | 258 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-002 | 171 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-CODE-003 | 1332 | 11 | 0 | 99.18% | PASS |
| unknown | JSS-HOUSE-001 | 293 | 2 | 0 | 99.32% | PASS |
| unknown | JSS-HOUSE-002 | 31 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-HOUSE-003 | 43 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-MARKUP-001 | 462 | 103 | 0 | 81.77% | FAIL |
| unknown | JSS-MARKUP-002 | 116 | 2 | 0 | 98.31% | PASS |
| unknown | JSS-MARKUP-003 | 617 | 78 | 0 | 88.78% | FAIL |
| unknown | JSS-MARKUP-004 | 33 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-NAME-002 | 155 | 1 | 0 | 99.36% | PASS |
| unknown | JSS-OPER-001 | 27 | 1 | 0 | 96.43% | PASS |
| unknown | JSS-OPER-002 | 98 | 113 | 0 | 46.45% | FAIL |
| unknown | JSS-OPER-003 | 337 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-OPER-004 | 67 | 6 | 0 | 91.78% | PASS |
| unknown | JSS-PRE-001 | 17 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-002 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-003 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-004 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-005 | 4 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-006 | 15 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-PRE-007 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-001 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-REFS-003 | 2023 | 56 | 0 | 97.31% | PASS |
| unknown | JSS-REFS-004 | 537 | 1 | 0 | 99.81% | PASS |
| unknown | JSS-REFS-005 | 44 | 2 | 0 | 95.65% | PASS |
| unknown | JSS-REFS-006 | 900 | 31 | 0 | 96.67% | PASS |
| unknown | JSS-REFS-007 | 141 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-001 | 45 | 1 | 0 | 97.83% | PASS |
| unknown | JSS-STRUCT-002 | 22 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-003 | 2 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-004 | 6 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-STRUCT-005 | 19 | 9 | 0 | 67.86% | FAIL |
| unknown | JSS-STRUCT-006 | 5 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-001 | 119 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-002 | 1 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-003 | 3 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-TYPO-004 | 45 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-WIDTH-001 | 188 | 6 | 0 | 96.91% | PASS |
| unknown | JSS-XREF-001 | 22 | 2 | 0 | 91.67% | PASS |
| unknown | JSS-XREF-002 | 627 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-004 | 619 | 31 | 0 | 95.23% | PASS |
| unknown | JSS-XREF-005 | 125 | 0 | 0 | 100.00% | PASS |
| unknown | JSS-XREF-006 | 6 | 0 | 0 | 100.00% | PASS |

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
