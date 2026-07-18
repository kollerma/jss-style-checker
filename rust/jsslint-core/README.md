# jsslint-core

The rule engine behind the [JSS style checker](https://github.com/kollerma/jss-style-checker) —
a linter for LaTeX/BibTeX manuscripts submitted to the
[Journal of Statistical Software](https://www.jstatsoft.org/) (JSS).

This crate is the shared engine, not an application. It parses `.tex`/`.bib`
sources, applies the JSS rule catalogue, and renders reports (`terminal`,
`json`, `sarif`, `html`). It is compiled into every JSS-checker distribution:

- **`jsslint`** — command-line binary ([`jsslint-cli`](https://crates.io/crates/jsslint-cli))
- **`jsslint-wasm`** — browser / Node.js ([npm](https://www.npmjs.com/package/jsslint-wasm))
- **`jsslint`** — Python extension ([PyPI](https://pypi.org/project/jsslint/))
- **`jsslintr`** — R package

Most users want one of those rather than this crate directly. If you are
embedding the engine in Rust, the entry point is `jsslint_core::engine::run`,
which takes a `ToolConfig` plus a parsed document and returns a
`ComplianceReport`; `jsslint_core::{sarif, html, json, terminal}` render it.

See the [project README](https://github.com/kollerma/jss-style-checker) for
the full rule catalogue and design.

## License

MIT.
