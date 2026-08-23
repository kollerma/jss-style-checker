# Design rationale

Why `jss-lint` is built the way it is: the trade-offs behind the four
design principles and the one-engine/four-channel architecture. The
full treatment, with the empirical evidence, is in the companion paper
(see the [README's Paper section](../README.md#paper)); this page is
the user-facing summary.

## Four principles

### 1. Parse, do not pattern-match

Rules operate on an abstract syntax tree (AST) of the manuscript, not
on raw lines. The Python engine parses LaTeX with `pylatexenc` and
BibTeX with `bibtexparser`; the Rust engine re-implements the same
two-pass document model. `.Rnw` (Sweave/knitr) and `.Rmd` sources are
handled by extracting their LaTeX and code components with source
positions preserved, and multi-file manuscripts by recursively
resolving `\input`/`\include`.

**Trade-off**: full parsing costs far more implementation effort than
regexes. What it buys is the ability to distinguish a bare language
name in prose from the same string inside a comment, a verbatim block,
a citation key, or a macro definition — the distinctions that separate
a useful checker from a noisy one. Most of the measured precision
comes from this choice.

### 2. Deterministic rules only

The same input always produces the same violations, byte for byte. AI
played a large role in the *development* of the rules but plays no
role at all in their *execution* — an intentional contrast to AI-based
writing assistants.

**Trade-off**: checks that bottom out in judgment (is this capitalized
word a proper noun?) cannot be shipped as deterministic rules. They
are either narrowed until they are deterministic, or publicly retired
(4 retirements to date, recorded in the rule catalogue). What
determinism buys: the tool works as a CI gate, and its accuracy is a
measurable quantity — the precision/recall badges on the README are
regenerated from a real evaluation database, which is impossible for a
probabilistic checker.

### 3. Fail soft

A parse error in one file degrades that file's analysis and is itself
reported as a violation (`JSS-PARSE-000`); it never aborts the run.
Real manuscripts contain unbalanced braces in verbatim environments
and other legacy constructs, and a checker that dies on them never
gets to report anything useful.

### 4. Two audiences

Author mode reports each violation with its position and a fix
suggestion. Reviewer mode aggregates the same findings into a
per-category compliance summary, so editors and reviewers can see at a
glance whether a submission is ready for content review. Same engine,
same findings — two presentations.

## One engine, four channels

The project began as a pure Python package. The Rust port
(`rust/jsslint-core`) now ships the same behavior five ways: a native
CLI (`jsslint-cli` on crates.io), a Python wheel (`jsslint` on PyPI,
via PyO3), an R package (`jsslintr` on CRAN, via extendr), a
browser/npm WASM module (`jsslint-wasm`, powering the web app and the
VS Code extension), and a GitHub Action.

Two decisions make this trustworthy rather than merely convenient:

- **The Python implementation is retained as the reference.** Both
  engines must produce byte-identical `terminal`/`json`/`sarif`/`html`
  output, enforced by parity test suites in CI (Constitution §XIII).
  Maintaining two engines is a real, permanent cost; what it purchases
  is continuous differential testing — every corpus manuscript is an
  oracle check of one engine against the other. Given that the code
  was written by language models and verified by measurement rather
  than line review, this redundancy is load-bearing.
- **The portable core is isolated.** `jsslint-core`, the WASM build,
  the Python wheel, and the vendored R crate contain no network or
  filesystem code (Constitution §XIV, enforced by
  `rust/jsslint-wasm/tests/isolation.rs`). Network features (Crossref
  DOI lookup) live only in the CLI layer. This is what makes the
  browser deployment's privacy claim — your manuscript never leaves
  the machine — a checked property rather than a promise.

## Rules are data

The engine itself is journal-agnostic: journals are discovered through
the `texlint.journals` entry-point group, and the JSS rule catalogue is
generated from a YAML description
(`specs/003-jss-rule-catalogue/catalogue.yaml`). A rule set for another
journal's style guide is the intended extension path and requires no
changes to this repository.

## Non-affiliation

`jss-lint` is an independent, third-party project. It is not
affiliated with, endorsed by, or connected to the Journal of
Statistical Software, its editors, or its publisher.
