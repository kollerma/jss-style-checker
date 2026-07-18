# jsslint-crossref

Optional online DOI verification (Crossref + CRAN/DataCite) for the
[`jsslint`](https://crates.io/crates/jsslint-cli) CLI's `--crossref` flag.
Ports `texlint/crossref.py`.

This is a separate crate — not a `jsslint-core` feature — so that
`jsslint-wasm` (and anything else that only depends on `jsslint-core`) can
never reach the network, structurally: nothing outside `jsslint-cli`
depends on this crate. See this crate's `src/lib.rs` module doc for the
full rationale, and `jsslint-core::config::DoiResolver` for the injection
hook `JSS-REFS-003` consumes.

Not published independently — it's an internal dependency of the `jsslint`
CLI binary.
