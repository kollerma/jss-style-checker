# Spec 023 — `.Rnw`/`.Rmd` support in the Rust engine (retroactive record)

> **RETROACTIVE**: shipped from a handoff prompt without a committed spec.
> Key commits: `7b918225` (feature), `17751044` (UTF-8 BOM fix).

## What shipped

The Rust engine (`jsslint-core`) accepts Sweave (`.Rnw`) and R Markdown
(`.Rmd`) manuscripts, matching the Python engine. Because every non-Python
distribution shares the core, this lit up `.Rnw`/`.Rmd` at once in the CLI,
the WASM/npm build, the web app, the VS Code extension, the PyO3 wheel, and
the R package.

## Design

A port of the Python preprocessing, not a redesign
(`src/texlint/core/parser.py` / `rmd_parser.py` are the reference):

- R code chunks (`<<…>>=` … `@`; ```` ```{r} ```` fences for `.Rmd`) are
  rewritten **in place** into `\begin{Sinput}…\end{Sinput}` envelopes so the
  chunk body becomes a verbatim environment prose rules already skip, while
  **line/column positions stay source-authoritative** — diagnostics map back
  to the original `.Rnw`/`.Rmd` lines.
- The Python side encodes years of CRAN-vignette edge cases (CRLF chunk
  headers, indented headers, `%`-commented pseudo-headers, `echo=FALSE` /
  `include=FALSE` hidden chunks, `\SweaveOpts` / `opts_chunk$set` global
  defaults, bare-`@` terminator variants). The port replicates these
  behaviors exactly; the parity suites are the spec.

## Verification

- Byte-for-byte parity against `jss-lint` across all four output formats on
  the recall corpus's 13 `.Rnw` vignettes; parity cases added to the Rust
  and Python parity suites (with the corpus-missing skip guard).
- Suffix allow-lists updated across the CLI (directory expansion), engine
  error messages, and docs (`web/index.html` footer, `rust/README.md`).
