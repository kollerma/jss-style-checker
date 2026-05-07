# JSS Recall Corpus — Annotation Protocol

> **Status (2026-05-07):** infrastructure ships in v1 plus 10
> scaffolded paper directories (manuscript + bib + stub
> `annotations.toml`). Hand-annotation of the 10 stubs is the
> remaining v1 work, tracked as the deferred item in
> `roadmap/follow-ups.md` § Feature 017.

## What this corpus is for

Recall measurement: when the linter fires, how often is it
right? Precision (the existing `eval/precision-history.db`
metric) answers that. Recall — when the linter does NOT fire,
how often is there really nothing to flag? — needs a hand-
annotated ground truth to compute.

## Per-paper directory layout

```
eval/recall-corpus/
├── README.md                       (this file)
├── <paper-id>/
│   ├── <manuscript>.{Rnw,Rmd,tex}  (any name; original from the source vignette)
│   ├── <refs>.bib                  (one or more sibling .bib files)
│   └── annotations.toml            (every ground-truth violation)
└── (more papers...)
```

`eval-jss recall` walks every `.tex / .ltx / .rnw / .rmd / .bib`
file in the paper directory and lints them together. Manuscript
filenames are kept as the package's vignette ships them, so
`annotations.toml`'s `file = "..."` entries reference those names
(e.g., `file = "rlmer.Rnw"`, not `file = "manuscript.tex"`).

## Annotation file shape

```toml
[meta]
paper_id = "<id>"               # equals the directory name
annotator = "<name>"
date = "2026-05-04"             # ISO-8601
notes = "<optional>"

[[violations]]
rule_id = "JSS-CITE-002"
file = "rlmer.Rnw"              # whatever the manuscript file is called on disk
line = 42
comment = "<optional rationale>"

# ... one entry per ground-truth violation
```

## Lint surface for fair recall measurement

The annotator reads the rendered `.tex` / PDF; the linter should
see the same surface. For Sweave-style vignettes (`.Rnw`), this
means the recall corpus should ideally ship the Sweave-rendered
`.tex` alongside the source. The `jss5342` recall study
(`examples/jss5342-versions/_analysis/recall-study.md`) shows that
linting only the `.Rnw` misses ~30 % of reviewer-relevant defects
(rendered Sinput / Soutput widths, paragraph-break artefacts
around `\Sexpr` evaluations, post-render `\section{}` / `\eqref{}`
forms).

V1 of the corpus ships only `.Rnw` because rendering requires R +
each package's deps, which is out of scope for the linter repo.
V2 will add sibling `.tex` files (built locally and committed) for
each paper. Until then, recall numbers are a lower bound — what
the linter would catch given source-only access.

## Annotation walk-through

1. Pick the paper directory you intend to annotate. The 10 v1
   directories were scaffolded on 2026-05-07; see the picks
   table at the bottom of this README.
2. Read the manuscript end-to-end (the rendered PDF is best;
   the `.Rnw` source is acceptable). For each violation you
   spot, identify the rule id (`jss-lint explain RULE-ID`).
3. Record `(rule_id, file, line, comment?)` in the directory's
   `annotations.toml`. Fill in the `[meta] annotator` and
   `notes` fields.
4. Run `python -m eval.cli recall --validate` to verify every
   annotation parses, every rule id exists, and every line is
   in range.
5. Run `python -m eval.cli recall --no-record` to see the
   per-rule TP / FN / recall. Iterate the annotation if the
   linter found cases you missed (genuine false negatives in
   your annotation) or you found cases the linter missed (real
   recall data).
6. Commit. CI runs `eval-jss recall` on every push to record
   the aggregate against `eval/precision-history.db`.

**Do not pre-populate the `[[violations]]` list from the
linter's output.** The recall measurement depends on
*independent* annotation: if you only confirm what the linter
found, you record TPs but no FNs, which means recall is
mathematically pinned at 1.0. The point is to surface defects
the linter missed.

### TOML escaping for backslashes

A double-quoted TOML string interprets `\X` as an escape, so a
`comment` like `"Used 'and' not '\And'"` fails to parse (`\A` is
not a valid escape). Use a literal single-quoted string for any
comment that mentions LaTeX macros:

```toml
# bad — TOMLDecodeError on '\A':
comment = "Used 'and' not '\And' in author list"

# good — literal string preserves backslashes verbatim:
comment = 'Used "and" not "\And" in author list'
```

### Papers split across `\input` files

If the manuscript pulls in additional `.tex` files via
`\input{...}` (only `pmclust` does this in the v1 slate), the
scaffolder copies them under the same relative subdirectory. The
recall CLI walks the paper directory recursively, so a violation
in `pmclust-include/02-example.tex` is annotated as

```toml
[[violations]]
rule_id = "JSS-CITE-002"
file = "02-example.tex"   # iterdir basename — not "pmclust-include/02-example.tex"
line = 47
```

The linter reports `file` as the bare basename, so annotations
should match.

## Identity tuple

`(rule_id, file, line)`. Column does NOT participate. A
violation the annotator marked at line 42 column 1 and the
linter caught at line 42 column 12 both count as a TP.

## Inter-annotator agreement

V1 ships single-annotator; v2 (a future spec) introduces a
second annotator and a Cohen-kappa-style agreement metric.

## License

Annotations are released under the same license as the
linter: MIT. See research §4 for the rationale on publishing
the corpus rather than keeping it private.

## V1 paper picks (scaffolded 2026-05-07)

Selected to maximise rule-coverage diversity (47 of 51 corpus-firing
rules) while keeping total annotation cost manageable
(~8.8k LOC across 10 papers, ~9 hours read-end-to-end).

| paper | LOC | unique rules in slate |
|---|---:|---|
| `robustlmm` | 799 | TYPO-004, CAP-003 |
| `CARBayesST` | 961 | ABBR-001, CAP-001, OPER-001 |
| `mdsOpt` | 1273 | CITE-003, OPER-003, REFS-005 |
| `DBR` | 528 | BIBTEX-003 |
| `pmclust` | 101 | PRE-004, PRE-005 |
| `cusp` | 627 | MARKUP-004, STRUCT-006 |
| `spacetime` | 1566 | PRE-003, PRE-007 |
| `deSolve` | 1942 | CITE-004, NAME-001 |
| `rstpm2` | 527 | TYPO-003 |
| `clifford` | 510 | BIBTEX-002 |

Rules not yet covered (deferred to v2):
`JSS-PRE-001`, `JSS-STRUCT-003`, `JSS-STRUCT-004`,
`JSS-STRUCT-005`. Each of these has a single high-LOC carrier in
the corpus (BNPmix, ICS, cotram); they'll be easier to add once
the v1 annotation cadence is established.

Suggested annotation order: `pmclust` (1 hour, calibrates the
process cheaply), then `robustlmm` (author-familiar territory),
then the diverse pair `CARBayesST` / `mdsOpt`, then the rest in
order of length.
