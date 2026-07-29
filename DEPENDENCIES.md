# Direct dependencies and their licenses

The project itself is MIT-licensed (see [LICENSE](LICENSE)). This file
lists the *direct* runtime dependencies of each distributed component
with their licenses, and states the compatibility conclusion. Transitive
dependencies are resolved by the respective package managers; the R
package additionally vendors its Rust crate dependencies and lists every
vendored crate's authors and licenses in `r/jsslintr/inst/AUTHORS`.

## Python reference implementation (`jss-style-checker`, PyPI)

| Package | License |
|---|---|
| pylatexenc | MIT |
| bibtexparser | MIT |
| click | BSD-3-Clause |
| rich | MIT |
| jinja2 | BSD-3-Clause |
| PyYAML | MIT |
| tomli (Python < 3.11 only) | MIT |

Optional extras: `pygls` (Apache-2.0, `[lsp]`), `weasyprint`
(BSD-3-Clause, `[pdf]`).

## Rust core and channels (crates.io, npm, PyPI wheel)

| Crate | Used by | License |
|---|---|---|
| serde / serde_json / serde_yaml | core | MIT OR Apache-2.0 |
| regex | core, cli, crossref | MIT OR Apache-2.0 |
| difflib | core, crossref | MIT |
| toml | core | MIT OR Apache-2.0 |
| clap | cli | MIT OR Apache-2.0 |
| ureq (rustls, no default features) | crossref (CLI-only network) | MIT OR Apache-2.0 |
| wasm-bindgen / serde-wasm-bindgen | wasm | MIT OR Apache-2.0 |
| pyo3 | Python wheel | MIT OR Apache-2.0 |
| extendr | R package | MIT |

`jsslint-cli`'s optional PDF report vendors a patched `printpdf` 0.3.4
(MIT); see `rust/vendor/printpdf-0.3.4/NOTICE.md`.

## R package (`jsslintr`, CRAN)

Depends only on R (>= 4.2); no `Imports`. Build requires Rust
(`SystemRequirements: Cargo, rustc >= 1.85`); the CRAN source tarball
vendors all Rust crates offline, with authorship and licenses documented
in `inst/AUTHORS`. Suggests (vignettes/tests only): knitr, rmarkdown,
testthat.

## Compatibility

Every direct dependency is under a permissive OSI-approved license
(MIT, BSD-3-Clause, or Apache-2.0, the latter always dual-licensed
MIT OR Apache-2.0 on the Rust side). All are compatible with the
project's MIT license and with GPL-2/GPL-3 as required by JSS, and
impose no restriction on distribution via PyPI, crates.io, npm, CRAN,
or the VS Code Marketplace.
