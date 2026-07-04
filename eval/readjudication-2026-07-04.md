# Gold-set re-adjudication — 2026-07-04 (MARKUP-001 label consistency)

Targeted reconciliation of MARKUP-001 hyphen-compound constructs that were
labelled **inconsistently across papers** (same token → both TP and FP),
per the label-noise finding in the pre-merge MARKUP-001 investigation.
Labels live in `eval/eval.db` (gitignored); this file is the auditable
record. Reviewer tag on the flipped rows: `human:readjudicate`.

## Reconciled tokens (9 label flips → one consistent verdict per token)

| token | correct verdict | reasoning | flips |
|---|---|---|---|
| `R-code` | **TP** | "R code" — R is the language, should be `\proglang{R}` | 1 FP→TP (deSolve:1553, identical to its sibling TPs) |
| `R-project` | **FP** | the `r-project.org` URL / proper noun — not wrappable | 1 TP→FP (GPareto:1468) |
| `R-Forge` | **FP** | proper-noun development platform (cf. SourceForge); the `R-` is part of the name, consistent with `R-project` | 5 TP→FP (archetypes, colorspace, datatable, simecol, animation) |
| `C-component` | **FP** | causal-inference term (c-component factorization), not the C language | 1 TP→FP (causaleffect:733) |
| `C-coverage` | **FP** | a `cna` package measure (contrapositive coverage), not the C language | 1 TP→FP (cna:530) |

**Effect:** MARKUP-001 precision 90.11% → **89.52% (FAIL)**. The
inconsistent labels had been masking the rule just above the 90% gate; the
honest post-reconciliation figure is ~89.5%. (306 MARKUP-001 rows are also
pending review after the main-merge re-scan and may shift this further.)

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
