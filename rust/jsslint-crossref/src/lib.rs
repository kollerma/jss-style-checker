//! Optional online DOI verification (Crossref + CRAN/DataCite) for the
//! `jsslint` CLI — the Rust port of `texlint/crossref.py`.
//!
//! **Why this is its own crate, not a `jsslint-core` feature flag:**
//! `jsslint-wasm` promises "manuscripts never leave the machine" *by
//! construction* (see `jsslint-wasm/src/lib.rs`'s module doc) — no
//! network-capable code linked in at all, not even behind a disabled
//! flag someone could later flip. A Cargo feature on `jsslint-core`
//! can't make that guarantee structural: any downstream crate could
//! enable it. Putting the network client (`ureq`) here instead, in a
//! crate `jsslint-core`/`jsslint-wasm` never depend on, makes "wasm
//! can't reach the network" a fact about the dependency graph —
//! checkable with `cargo tree -p jsslint-wasm | grep -i ureq` (must be
//! empty) rather than a convention someone has to remember to uphold.
//!
//! `jsslint-core` owns only the abstract hook
//! (`jsslint_core::config::DoiResolver` / `ToolConfig::doi_resolver`)
//! that `JSS-REFS-003` consumes — see that rule's module doc
//! (`jsslint-core/src/rules/references.rs`). This crate's one public
//! entry point, [`make_resolver`], builds the real implementation and
//! hands it to the CLI to inject.
//!
//! Every network or parse error resolves to `None`/no match, same as
//! Python — the feature never fails a lint run (see [`http::HttpClient`]'s
//! doc comment).

mod http;
mod resolve;

pub use http::{HttpClient, UreqClient};
pub use resolve::{make_resolver, resolve_doi, CrossrefOptions, DEFAULT_TIMEOUT};
