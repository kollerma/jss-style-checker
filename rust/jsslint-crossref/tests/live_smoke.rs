//! Live-network smoke test. **Not** part of the default hermetic suite
//! (see `src/resolve.rs`'s `tests` module for that) — `#[ignore]`d, and
//! double-gated behind an env var so `cargo test --workspace --
//! --ignored` alone still can't accidentally hit the network:
//!
//! ```sh
//! JSSLINT_CROSSREF_LIVE_TEST=1 cargo test -p jsslint-crossref --test live_smoke -- --ignored
//! ```
//!
//! Needs real network access to `api.crossref.org` and `doi.org`.

use jsslint_crossref::{resolve_doi, UreqClient};
use std::collections::HashMap;
use std::time::Duration;

fn live_test_enabled() -> bool {
    if std::env::var("JSSLINT_CROSSREF_LIVE_TEST").as_deref() == Ok("1") {
        return true;
    }
    eprintln!("SKIP: set JSSLINT_CROSSREF_LIVE_TEST=1 to run this live-network test");
    false
}

/// CRAN's `10.32614/CRAN.package.NAME` DOI scheme is deterministic —
/// this only confirms it actually resolves via `doi.org`, no fuzzy
/// matching involved, so it's the more reliable of the two live checks.
#[test]
#[ignore]
fn live_cran_manual_doi_resolves() {
    if !live_test_enabled() {
        return;
    }
    let client = UreqClient::new(Duration::from_secs(10));
    let mut fields = HashMap::new();
    fields.insert(
        "url".to_string(),
        "https://CRAN.R-project.org/package=boot".to_string(),
    );
    let doi = resolve_doi(&client, &fields, "manual", None);
    assert_eq!(doi.as_deref(), Some("10.32614/CRAN.package.boot"));
}

/// A well-known, stably-titled article — real network round trip
/// through the Crossref ranking logic. Doesn't pin the exact DOI
/// (Crossref's own casing/response shape isn't this crate's contract
/// to pin), just that the live lookup finds *a* match.
#[test]
#[ignore]
fn live_crossref_article_lookup() {
    if !live_test_enabled() {
        return;
    }
    let client = UreqClient::new(Duration::from_secs(10));
    let mut fields = HashMap::new();
    fields.insert("title".to_string(), "Random Forests".to_string());
    fields.insert("author".to_string(), "Breiman".to_string());
    fields.insert("year".to_string(), "2001".to_string());
    let doi = resolve_doi(
        &client,
        &fields,
        "article",
        Some("crossref-live-test@example.com"),
    );
    assert!(
        doi.is_some(),
        "expected a live Crossref match for a well-known article"
    );
}
