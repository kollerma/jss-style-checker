# `jss_template_article` — canonical JSS Demo article

Verbatim copy of [`docs/jss-template/article.tex`](../../docs/jss-template/article.tex)
and its companion [`refs.bib`](../../docs/jss-template/refs.bib), the
authoritative CTAN `jss` package demo article by Achim Zeileis.

**Source**: CTAN `jss` package, vendored into this repository during
Step 0.5. License / redistribution terms are the CTAN package's.

## Why this is in the corpus

The JSS Demo article *is* the JSS style's reference implementation —
by construction, every violation it triggers under `jss-lint` is a
**false positive**. This makes it the highest-value calibration paper
in the corpus: a rule that fires here is by definition too strict.

As of Step 1's smoke rules, scanning this article produces **8
`JSS-SRC-001`** violations (lines >80 columns in the JSS-authored
template). The `JSS-SRC-001` default width of 80 is therefore already
known to overfit Step 1's working assumption. Step 3 is expected to
re-tune the threshold — the corpus-precision feedback here is the
signal that drives that tuning.
