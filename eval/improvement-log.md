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
