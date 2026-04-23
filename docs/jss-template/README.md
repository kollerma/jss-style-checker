# JSS template (vendored reference)

Authoritative copy of the **Journal of Statistical Software** (JSS) author
template, vendored verbatim so that texlint rules can be developed and tested
against the real upstream sources without a network round-trip.

## Files

| File | Purpose |
|---|---|
| `article.tex`  | Canonical demo article (`\documentclass[article]{jss}`). |
| `article.Rnw`  | Sweave variant of the demo article — reference for Step 3 (.Rnw dispatch). |
| `refs.bib`     | Companion BibTeX database for `article.tex` / `article.Rnw`. |
| `article.R`    | R code that produces the figures used in `article.tex`. |
| `jss.cls`      | LaTeX2e class implementing JSS layout. |
| `jss.bst`      | BibTeX style implementing JSS bibliography format. |

## Provenance

- Upstream package: [`jss` on CTAN](https://ctan.org/pkg/jss) — distribution
  zips `jss-article-tex.zip` (provided `article.tex`, `refs.bib`, `article.R`,
  `jss.cls`, `jss.bst`) and `jss-article-rnw.zip` (provided `article.Rnw`;
  remaining files were byte-identical to the `-tex` variant).
- Distribution URLs:
  - `https://www.jstatsoft.org/public/journals/1/jss-article-tex.zip`
  - `https://www.jstatsoft.org/public/journals/1/jss-article-rnw.zip`
- Upstream version captured: `jss.cls` v3.3 (2021-05-23); demo article and
  bibliography dated 2018-04-30; demo article last touched 2021-12-10.
- Fetched into this repository: **2026-04-23** (commit
  [`cf4e5be`](https://github.com/kollerma/jss-style-checker/commit/cf4e5be)).
- SHA256 of the downloaded zips at that fetch:
  - `jss-article-tex.zip`: `9ce1f09286537600370be9fb64d80b1fa55d1de89fd9240db0dc065da7f03507`
  - `jss-article-rnw.zip`: `4c88f98b54f83e9b4e26926db6d26d7858d1de15e6d1b49f6e77077d1b12e1d9`
- Maintainer (upstream): Achim Zeileis (`Achim.Zeileis@R-project.org`).

## Licence

`jss.cls` and `jss.bst` are distributed by upstream under **GPL-2 | GPL-3**.
The demo `article.tex`, `refs.bib`, and `article.R` are distributed by
upstream as templates for JSS submissions and are reproduced here verbatim
for reference. These files are **not** bundled into the `jss-style-checker`
wheel or sdist (see `pyproject.toml` `[tool.hatch.build.targets.*]`); they
live in the source repository as documentation only.

## How to refresh

When upstream publishes a new revision:

```sh
mkdir -p /tmp/jss-ctan && cd /tmp/jss-ctan \
  && curl -fSL -o jss-article-tex.zip \
       https://www.jstatsoft.org/public/journals/1/jss-article-tex.zip \
  && curl -fSL -o jss-article-rnw.zip \
       https://www.jstatsoft.org/public/journals/1/jss-article-rnw.zip \
  && unzip -o jss-article-tex.zip -d jss-article-tex \
  && unzip -o jss-article-rnw.zip -d jss-article-rnw
cp jss-article-tex/{article.tex,refs.bib,article.R,jss.cls,jss.bst} \
   /workspace/docs/jss-template/
cp jss-article-rnw/article.Rnw /workspace/docs/jss-template/
```

Re-run the test suite (`scripts/vtest.sh`) afterwards. If the compliant
fixture `tests/fixtures/compliant/minimal.tex` (which mirrors this
template's preamble) starts to fail a smoke rule because of an upstream
change, prefer adapting the fixture over silently modifying this directory.
