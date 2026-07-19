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

Published on crates.io because cargo requires a published crate's
dependencies to be published too — but it is **not a supported standalone
API**. It exists solely as an internal dependency of the `jsslint` CLI
binary; its interface may change in any release without notice. There is
no reason to depend on it directly: use `jsslint-cli` for the tool, or
`jsslint-core` for the (fully offline) engine.
