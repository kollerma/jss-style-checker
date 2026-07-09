//! Phase 5 stub. `wasm-bindgen` glue lands once `jsslint-core` has a
//! real engine. **Hard constraint (see the plan's network-dependency
//! callout): this crate must never link anything equivalent to
//! `texlint.crossref`'s live DOI verification.** The privacy promise
//! ("manuscripts never leave the machine") depends on that being true
//! by construction, not by a runtime flag default.

pub fn placeholder() -> &'static str {
    "jsslint-wasm: not yet implemented (spec 018, Phase 5 pending)"
}
