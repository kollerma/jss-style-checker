# `examples/` — MVP evaluation corpus

This directory holds the hand-curated corpus that `eval-jss scan` walks.
Per the Phase A scope of `specs/002-eval-jss-harness/`, the production
target is **10 real CRAN JSS vignettes** (vignettes whose `.tex` source
uses `\documentclass{jss}` or `\usepackage{jss}`).

## Current state

This directory currently contains **three placeholder vignettes** that
prove the scan / review / report plumbing end-to-end against `jss-lint`.
They deliberately exercise:

- `placeholder_clean/` — no violations, exit-0 scan.
- `placeholder_cite_violation/` — triggers `JSS-CITE-001` (citation-looks-like-`\emph`).
- `placeholder_src_violation/` — triggers `JSS-SRC-001` (line > 80 cols).

## Handoff: populating with real CRAN vignettes

To grow the corpus to its 10-paper Phase A target:

1. Pick a CRAN package whose vignette uses `\documentclass{jss}`. Good
   candidates: `lme4`, `MASS`, `limma`, `zoo`, `xts`, `party`, etc.
2. Download the current source tarball from CRAN `Archive/`:
   `https://cran.r-project.org/src/contrib/Archive/{pkg}/{pkg}_{ver}.tar.gz`.
3. Extract, locate the JSS-style vignette under `vignettes/`. Copy the
   `.tex` and its companion `.bib` into a new directory named
   `cran_<pkg>_<version>/` here.
4. Drop a per-paper `README.md` recording the CRAN URL, pinned version,
   and JSS DOI (if one exists — check the `inst/CITATION`).
5. Run `eval-jss scan` to confirm the linter accepts the new paper.
6. (Phase B follow-up) Add a row to `eval/corpus-manifest.csv` with the
   tarball's `sha256`.

## Curation policy

- One vignette per directory.
- Paper directories are named `<source>_<source_id>_<version>/` for
  consistency with the Phase B manifest.
- Real corpus papers replace placeholders one-by-one; do not delete the
  placeholders until the replacement directory is known-good under `scan`.
- Remove placeholders once the 10-paper target is reached — they remain
  here only because Phase A needed a deterministic plumbing fixture.
