---
title: "jss-lint: Automated style checking for Journal of Statistical Software manuscripts"
tags:
  - LaTeX
  - BibTeX
  - linter
  - scholarly publishing
  - reproducible research
  - R
  - Python
  - Rust
  - WebAssembly
authors:
  - name: Manuel Koller
    orcid: 0000-0002-4159-922X
    affiliation: 1
affiliations:
  - name: Independent researcher, Zürich, Switzerland
    index: 1
date: 23 August 2026
bibliography: paper.bib
---

<!-- AUTO-GENERATED from paper/joss/paper.md.in by
     `python -m tools.generate_paper_stats`. Do not edit by hand:
     numbers are pinned to precision iteration `new-additions-through-resolve-input`
     and recall run 2026-07-19T10:30:02Z (corpus 70951d5371df0734). -->

# Summary

Manuscripts submitted to the *Journal of Statistical Software* (JSS) must
satisfy a comprehensive style guide covering preamble macros, semantic
markup, citation conventions, capitalization, code formatting, bibliography
completeness, and typography [@jss_styleguide]. Style problems that reach
peer review cost editors, reviewers, and authors additional revision rounds
for defects a machine can find. `jss-lint` is an open-source, deterministic
style checker for JSS-format manuscripts [@jss-style-checker]. A single
Rust core implements 62 rules in 16
categories for `.tex`, `.Rnw` (Sweave) [@leisch2002], and `.Rmd`
[@xie2015knitr] sources, and ships through four channels: a command-line
tool, a Python package, an R package (`jsslintr`, on CRAN), and a
WebAssembly build that powers a Visual Studio Code extension and a browser
application which processes manuscripts entirely locally. Every violation
is reported with its source position and a fix suggestion, a large subset
can be applied automatically, and a reviewer mode aggregates the findings
into a per-category compliance summary.

# Statement of need

JSS publishes its style guide and LaTeX class, but conformance checking
has been manual: authors typically learn of violations only when editors
or reviewers return the manuscript, one revision round at a time.
`jss-lint` serves three audiences. *Authors* check a submission before it
leaves their machine — from the command line, from R or Python, or in the
browser without uploading the manuscript anywhere. *Reviewers and editors*
use the aggregated compliance report to separate questions of form from
questions of content. *Maintainers* of packages whose vignettes follow the
JSS format gate continuous integration on the checker via a GitHub Action.
All of these uses rest on one design commitment: the same input always
yields the same violations, byte for byte, which is what makes the tool
usable as a CI gate and — unlike heuristic or AI-based checking — makes
its accuracy a measurable quantity.

`jss-lint` is an independent, third-party project. It is not affiliated
with, endorsed by, or connected to the Journal of Statistical Software,
its editors, or its publisher; it merely checks manuscripts against the
journal's publicly documented style requirements.

# State of the field

General-purpose LaTeX linters — ChkTeX [@chktex], lacheck [@lacheck], and
the textlint ecosystem [@texlint_js] — check language-level hygiene:
mismatched delimiters, spacing, deprecated constructs. They know nothing
of any journal's requirements; ChkTeX run on a corrected JSS demonstration
manuscript reports LaTeX-idiom advice and not one JSS style item. At the
other end, commercial AI writing assistants such as Writefull [@writefull]
give probabilistic language feedback: valuable for prose, but
non-deterministic, unspecific to journal rules, and requiring manuscript
upload to a third party. Within statistical computing, lintr [@lintr] and
styler [@styler] lint and format R source code — establishing the
community's expectation that linting is an ordinary part of the workflow,
but acting on code rather than on manuscripts. Several publishers run
internal submission checkers; none we know of publishes its accuracy.

None of these tools could have been extended to fill the gap: journal
style rules need an abstract syntax tree spanning LaTeX, BibTeX, and
knitr/Sweave sources, plus journal-specific ground truth to measure
against — machinery that line-oriented or code-oriented linters do not
have. To our knowledge, `jss-lint` is the first tool to encode a
statistical journal's style guide as an executable rule set and to report
measured precision and recall against a corpus of real manuscripts.

# Software design

Four principles, fixed early, embody the design trade-offs. *Parse, do not
pattern-match*: rules operate on an abstract syntax tree of the
manuscript, not on raw lines — the cost of full parsing buys the ability
to distinguish a bare language name in prose from one inside a comment,
verbatim block, citation key, or macro definition, which is what separates
a useful checker from a noisy one. *Deterministic rules only*: AI played a
large role in the development of the rules but plays none in their
execution; the trade-off is that genuinely judgment-bound checks are
excluded or publicly retired (4 retirements to date)
rather than shipped as noise. *Fail soft*: a parse error degrades one
file's analysis and is itself reported, but never aborts the run — real
manuscripts contain unbalanced braces in verbatim blocks and other legacy
constructs. *Two report modes*: author mode reports positions and fixes,
reviewer mode aggregates the same findings into a compliance summary,
and the maintainers' CI gate reads either as machine-readable JSON —
one engine serving the three audiences above.

The implementation is one engine shipped through four channels. The
original Python implementation is retained as the reference; the Rust core
compiles to a CLI, a Python wheel, an R package, and WebAssembly, and
parity suites in both ecosystems enforce byte-identical output across all
of them. Maintaining two engines is a real cost that purchases continuous
differential testing — a strong correctness check given how the code was
written (see the AI disclosure below). The portable core performs no
network or filesystem access, enforced by isolation tests, which is what
makes the fully-local browser deployment trustworthy. Finally, rules are
data: the engine itself is journal-agnostic, and a rule catalogue for
another journal's style guide is the intended extension path.

# Research impact statement

The software is released and externally gatekept across the ecosystems its
audiences work in: CRAN (`jsslintr`, accepted after the usual editorial
review), PyPI, crates.io, npm, the Visual Studio Code Marketplace and Open
VSX, a GitHub Action, and a hosted browser application, with releases
archived on Zenodo [@jss-style-checker].

The significance claim rests on measured accuracy, not on adoption counts.
After 116 recorded evaluation iterations against a pinned
corpus of 254 real JSS-format manuscripts, precision
estimated over 20,060 adjudicated violation instances is
97.2% — a label-set estimate bracketed by the human-only
subset (93.8%) and a labeler-error-propagated band
(85.4%–91.2%) — and recall against a
hand-annotated ground-truth corpus is 80.7% per instance. A
replication script re-runs the released tool and reproduces every
published number, and the per-rule precision and recall badges on the
repository regenerate from the same evaluation database. The full-length
companion preprint [@koller2026companion] documents the corpus
construction, labeling provenance, and case studies, and was itself
checked by the tool before deposit. The project is young — public since
July 2026 — so external adoption evidence is necessarily early; the
reproducible evaluation harness and the transferable methodology it
implements are offered as the substantive contribution in the meantime.

# AI usage disclosure

Large language models of the Claude family [@claude] wrote every line of
the software, the tests, the evaluation tooling, and the text of this
paper and its companion; approximately 800 of the
repository's more than 950 commits carry an AI co-author
trailer. The human author's contribution was directional and evaluative:
setting requirements, issuing corrective instructions when the tool or
process drifted, hand-annotating the recall ground truth, and working the
interactive label-review queue with final authority over every disputed
label. Notably, the human author never reviewed the code — only its
measured behavior.

Correctness of the AI-generated content is verified by substituting
measurement for line review: 2,117 automated tests with full
branch coverage on rule logic; byte-parity between the two independently
implemented engines; a per-rule precision gate (at least 90%) with
1 documented exemption and 4 public
rule retirements; and AI-issued evaluation labels audited against a human
gold set, with observed labeler disagreement propagated into the reported
precision band. The process artifacts — feature specifications, the
evaluation log of every iteration, gate exceptions, and the project
constitution — are versioned in the public repository. Development began
in a private repository in April 2026; the full commit history has been
public since July 2026.

# Acknowledgements

No financial support was received for this work. `jss-lint` is not
affiliated with or endorsed by the Journal of Statistical Software.

# References
