# Gold-set re-adjudication — 2026-07-04 (MARKUP-001 label consistency)

Targeted reconciliation of MARKUP-001 hyphen-compound constructs that were
labelled **inconsistently across papers** (same token → both TP and FP),
per the label-noise finding in the pre-merge MARKUP-001 investigation.
Labels live in `eval/eval.db` (gitignored); this file is the auditable
record. Reviewer tag on the flipped rows: `human:readjudicate`.

## Reconciled tokens (9 label flips → one consistent verdict per token)

**Policy (per the annotator, 2026-07-04):** `R` in `R-project` / `R-Forge`
IS wrapped in `\proglang{R}` when the token appears in **plain text**; it is
a false positive only inside a **URL** (`www.R-project.org`,
`R-project.org/...`). `C` in `cna`/causal-inference compounds is never the
C language.

| token | correct verdict | reasoning |
|---|---|---|
| `R-code` | **TP** | "R code" — R is the language, should be `\proglang{R}` |
| `R-Forge` | **TP** (all) | plain-text platform references ("hosted on R-Forge", "the R-Forge server") — R is the language, wrap it; none appear inside a URL |
| `R-project` | **TP** in prose, **FP** in a URL | plain-text mention (TraMineR "R-project, CRAN") → TP; the URLs (GPareto `R-project.org/view`, xts `www.R-project.org`) → FP |
| `C-component` | **FP** | causal-inference term (c-component factorization), not the C language |
| `C-coverage` | **FP** | a `cna` package measure (contrapositive coverage), not the C language |

**Effect:** after reconciling to this policy, MARKUP-001 precision is
**90.19% (PASS)** (1076 TP / 117 FP), vs 90.11% before. The re-adjudication
mainly removes label *noise* (making each token internally consistent)
rather than moving the headline; the C-* mislabels were the only genuine
TP→FP corrections. 306 MARKUP-001 rows remain pending after the main-merge
re-scan and may still shift this.

## Documented, NOT reconciled — inherent context dependency

Bare single-token language names fire on genuinely different uses, so a
single verdict is wrong — these are **not** labelling inconsistencies:

- `R` (734 TP / 39 FP), `C` (70 / 29), `C++` (44 / 1), `Stan` (136 / 4),
  `Stata` (12 / 3), `Python` (8 / 1): each FP is a real non-language use
  (a math symbol, a panel/group label, `R&D`, a URL, etc.), correctly
  distinguished from the language TPs. Left as-is.

This is a concrete example of the label-noise / context-ambiguity that
caps MARKUP-001's achievable precision near the 90% line — a point for the
paper's labelling-methodology section.

## MARKUP-001 mislabel corrections (FP → TP, 22 rows)

During human review of MARKUP-001, 22 firings labelled FP were found to be
genuine TPs — the single-letter name IS the language in context, so the
firing was correct. Corrected (reviewer `human:readjudicate`):

- **"R package / function / code" (12):** DBR, boxcoxmix, clValid, clifford,
  copula, datatable ×2, knitr, lbfgs, mdsOpt, rpart, interp — `R` modifies a
  noun and should be `\proglang{R}`.
- **R version / Base R / "in R" / C-or-Fortran (10):** fic, glmnet, knitr
  (`R 3.0.x`), np (`C or Fortran`), purrr (`R 4.1`), stream (`R 3.1.2`),
  stringr / tibble (`Base R`), datatable / stemmatology (`in R`).

Left as genuine FPs: single-letter names that are NOT the language —
`Penta_C` (marker), `factors S, C and F` (labels), tensor `mode C` /
`A and C` (rrcov3way).

**Effect:** MARKUP-001 precision 84.67% → **86.33%** (1143 TP / 181 FP).
Still below the 90% gate: the residual 181 FPs are the inherent
single-letter / domain-compound ambiguity (panel/factor/disease `C`,
`C-component`/`C-consistency`/`R-J`/… hyphen compounds) that no clean guard
resolves without corpus-overfitting.
