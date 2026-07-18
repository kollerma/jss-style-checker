//! Integration tests for `JSS-REFS-003`'s online-mode resolver path
//! (`references::check_refs_003`'s `Option<&DoiResolver>` parameter,
//! added alongside the `--crossref` port, commit e6c2caa). The pure
//! DOI-matching algorithm lives in `jsslint-crossref` and is
//! unit-tested there (`resolve.rs`'s `tests` module) — this file only
//! exercises how the *rule* consumes an already-resolved DOI: the
//! lowercase-keyed fields map built for the resolver call, the
//! online-found/offline-advisory message formatting, `doi_insertion_fix`'s
//! byte-vs-char offset arithmetic, and the interaction with the
//! existing pre-2000-cutoff / already-has-a-doi skip logic. Mirrors
//! `tests/unit/rules/test_references.py`'s `test_online_*` cases.
//!
//! Unlike the `tests/*_parity.rs` fixture-diff tests elsewhere in this
//! crate, the online resolver needs an injected closure, not a
//! fixture file on disk — so this is a hand-built-source integration
//! test instead of a fixture sweep (this crate has no inline
//! `#[cfg(test)]` anywhere in `src/`; all testing here goes through
//! `tests/*.rs`).

use jsslint_core::bib;
use jsslint_core::config::DoiResolver;
use jsslint_core::report::{Fix, Violation};
use jsslint_core::rules::references::check_refs_003;
use jsslint_core::tex::node::Node as TexNode;
use std::collections::HashMap;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};

fn check(source: &str, resolver: Option<&DoiResolver>) -> Vec<Violation> {
    let chars: Vec<char> = source.chars().collect();
    let library = bib::parse(source);
    let empty: &[&[TexNode]] = &[];
    check_refs_003("refs.bib", &chars, &library, empty, resolver)
}

/// Applies a single, non-overlapping `Fix` to `source`. Char-indexed,
/// matching `Fix::start`/`end`'s own units (`entry_source_span` and
/// friends all index a `&[char]`, not raw UTF-8 bytes) — the same
/// units `jsslint_core::fixer` uses when it applies fixes for real.
fn apply_fix(source: &str, fix: &Fix) -> String {
    let chars: Vec<char> = source.chars().collect();
    let mut out: String = chars[..fix.start].iter().collect();
    out.push_str(&fix.replacement);
    out.extend(&chars[fix.end..]);
    out
}

/// What `online_resolver_receives_lowercase_keyed_fields_and_type`
/// captures from the resolver call: `(fields map, entry_type)`.
type SeenCall = Arc<Mutex<Option<(HashMap<String, String>, String)>>>;

// --- ported from tests/unit/rules/test_references.py -----------------

#[test]
fn online_doi_found_reports_and_fixes() {
    let src = "@article{smith, author={Smith}, title={A Study}, journal={J}, year={2020}}\n";
    let resolver: &DoiResolver = &|_fields, _entry_type| Some("10.1/xyz".to_string());

    let out = check(src, Some(resolver));
    assert_eq!(out.len(), 1);
    let v = &out[0];
    assert_eq!(
        v.suggestion.as_deref(),
        Some("DOI '10.1/xyz' is registered for entry 'smith'; add doi = {10.1/xyz} (use --fix to insert it).")
    );

    let fix = v.fix.as_ref().expect("expected a Fix");
    assert_eq!(fix.replacement, "\n  doi = {10.1/xyz},");
    assert_eq!(fix.description, "insert doi = {10.1/xyz}");

    let patched = apply_fix(src, fix);
    assert!(patched.contains("doi = {10.1/xyz}"));
    assert!(patched.find("doi").unwrap() < patched.find("title").unwrap());
}

#[test]
fn online_no_doi_suppressed() {
    let src = "@article{smith, author={Smith}, title={A Study}, journal={J}, year={2020}}\n";
    let resolver: &DoiResolver = &|_fields, _entry_type| None;
    assert!(check(src, Some(resolver)).is_empty());
}

#[test]
fn online_resolver_receives_lowercase_keyed_fields_and_type() {
    // Source field names are deliberately upper/mixed-cased
    // (`TITLE`, `Author`, `YEAR`) — the resolver must still see
    // lowercase keys, mirroring `_lc_fields` on the Python side.
    //
    // The closure below is coerced to `&DoiResolver`, which (like
    // `jsslint_crossref::make_resolver`'s own resolver) carries an
    // implicit `Send + Sync + 'static` bound — so captured state must
    // be owned (`Arc<Mutex<_>>`, `move`d in), not a borrow of a local.
    let seen: SeenCall = Arc::new(Mutex::new(None));
    let seen_for_resolver = Arc::clone(&seen);
    let resolver_fn = move |fields: &HashMap<String, String>, entry_type: &str| -> Option<String> {
        *seen_for_resolver.lock().unwrap() = Some((fields.clone(), entry_type.to_string()));
        None
    };
    let resolver: &DoiResolver = &resolver_fn;

    let src = "@article{smith, Author={Smith}, TITLE={A Study}, Journal={J}, YEAR={2020}}\n";
    let _ = check(src, Some(resolver));

    let seen = seen.lock().unwrap();
    let (fields, entry_type) = seen.as_ref().expect("resolver should have been called");
    assert_eq!(fields.get("title").map(String::as_str), Some("A Study"));
    assert_eq!(fields.get("author").map(String::as_str), Some("Smith"));
    assert_eq!(fields.get("year").map(String::as_str), Some("2020"));
    assert_eq!(entry_type, "article");
}

// --- offline-mode message formatting (the other half of the "message
// formatting" gap: online-found is pinned above) ----------------------

#[test]
fn offline_advisory_message_is_pinned() {
    let src = "@article{smith, author={Smith}, title={A Study}, journal={J}, year={2020}}\n";
    let out = check(src, None);
    assert_eq!(out.len(), 1);
    assert_eq!(
        out[0].suggestion.as_deref(),
        Some("Add a doi field to entry 'smith' if one is available.")
    );
    assert!(out[0].fix.is_none());
}

// --- edge cases not exercised by the Python port but worth pinning ---

#[test]
fn multi_entry_fix_offset_targets_correct_entry() {
    let src = concat!(
        "@article{first, author={A}, title={First}, journal={J}, year={2019}}\n",
        "\n",
        "@article{second, author={B}, title={Second}, journal={J}, year={2021}}\n",
    );
    // Only "second" gets a DOI — "first" must stay suppressed (matches
    // `online_no_doi_suppressed`'s per-entry behavior) so this also
    // confirms the fields map isn't accidentally shared/stale across
    // entries in the same `referenced_entries` loop.
    let resolver: &DoiResolver = &|fields, _et| {
        if fields.get("title").map(String::as_str) == Some("Second") {
            Some("10.2/second".to_string())
        } else {
            None
        }
    };

    let out = check(src, Some(resolver));
    assert_eq!(out.len(), 1);
    let fix = out[0].fix.as_ref().expect("expected a Fix");

    // Exact patched output, not just relative ordering: an off-by-one
    // in the offset arithmetic can shift the insertion point by a
    // character without disturbing substring *order*, so ordering-only
    // assertions don't actually pin the exact splice point (verified:
    // this is what let an earlier draft of this test pass against a
    // deliberately-reintroduced byte/char offset bug).
    assert_eq!(
        apply_fix(src, fix),
        concat!(
            "@article{first, author={A}, title={First}, journal={J}, year={2019}}\n",
            "\n",
            "@article{second,\n  doi = {10.2/second}, author={B}, title={Second}, journal={J}, year={2021}}\n",
        )
    );
}

#[test]
fn preceding_multibyte_entry_does_not_corrupt_the_fix_offset() {
    // A CJK/accented `note` field ahead of the target entry: pins
    // that `entry_source_span`'s `es` (the entry's own start offset)
    // stays correct in a document containing multi-byte content
    // elsewhere. This does NOT by itself exercise `doi_insertion_fix`'s
    // `m.end()` byte->char conversion (see the next test for that) —
    // `ENTRY_HEAD_RE`'s match against the *target* entry's own header
    // is pure ASCII here, so `m.end()` in bytes already equals chars.
    let src = concat!(
        "@article{first, note = {h\u{e9}llo w\u{f6}rld \u{4e2d}\u{6587}}, author={A}, title={First}, journal={J}, year={2019}}\n",
        "\n",
        "@article{second, author={B}, title={Second}, journal={J}, year={2021}}\n",
    );
    let resolver: &DoiResolver = &|fields, _et| {
        if fields.get("title").map(String::as_str) == Some("Second") {
            Some("10.2/second".to_string())
        } else {
            None
        }
    };

    let out = check(src, Some(resolver));
    assert_eq!(out.len(), 1);
    let fix = out[0].fix.as_ref().expect("expected a Fix");

    // Exact patched output — see the previous test's comment on why
    // ordering-only assertions are too weak to pin this.
    assert_eq!(
        apply_fix(src, fix),
        concat!(
            "@article{first, note = {h\u{e9}llo w\u{f6}rld \u{4e2d}\u{6587}}, author={A}, title={First}, journal={J}, year={2019}}\n",
            "\n",
            "@article{second,\n  doi = {10.2/second}, author={B}, title={Second}, journal={J}, year={2021}}\n",
        )
    );
}

#[test]
fn multibyte_entry_key_does_not_corrupt_the_fix_offset() {
    // Unlike the previous test, the multi-byte character sits *inside*
    // `ENTRY_HEAD_RE`'s own match (the entry key, "s\u{e9}cond") — this is
    // what actually exercises `doi_insertion_fix`'s `m.end()` byte->char
    // conversion: `span[..m.end()]` (bytes into the reconstructed
    // header string) is no longer numerically equal to its char count,
    // since 'é' is 2 UTF-8 bytes but 1 char. A byte-offset regression
    // here lands the `Fix` a byte short, inside the multi-byte
    // character's own encoding — which `apply_fix`'s char-indexed slice
    // would catch as a wrong (or panicking) insertion point.
    let src = "@article{s\u{e9}cond, author={B}, title={Second}, journal={J}, year={2021}}\n";
    let resolver: &DoiResolver = &|_fields, _et| Some("10.2/second".to_string());

    let out = check(src, Some(resolver));
    assert_eq!(out.len(), 1);
    let fix = out[0].fix.as_ref().expect("expected a Fix");

    // `at = es + m.end()` (bytes, not chars) would land one char short
    // — inside the pre-comma whitespace instead of right after the
    // comma — since 'é' encodes to 2 UTF-8 bytes but is 1 char. Exact
    // equality catches that off-by-one; substring-ordering checks
    // alone do not (see the multi-entry test's comment).
    assert_eq!(
        apply_fix(src, fix),
        "@article{s\u{e9}cond,\n  doi = {10.2/second}, author={B}, title={Second}, journal={J}, year={2021}}\n"
    );
}

#[test]
fn multiline_entry_header_is_matched_across_newlines() {
    // `ENTRY_HEAD_RE`'s `\s*` must still bridge the header across
    // `@article` / `{` / the key each landing on their own line.
    let src = "@article\n{\n  second,\n  author = {B},\n  title = {Second},\n  journal = {J},\n  year = {2021},\n}\n";
    let resolver: &DoiResolver = &|_fields, _et| Some("10.2/second".to_string());

    let out = check(src, Some(resolver));
    assert_eq!(out.len(), 1);
    let fix = out[0]
        .fix
        .as_ref()
        .expect("expected a Fix — the multi-line header must still be relocated");

    assert_eq!(
        apply_fix(src, fix),
        "@article\n{\n  second,\n  doi = {10.2/second},\n  author = {B},\n  title = {Second},\n  journal = {J},\n  year = {2021},\n}\n"
    );
}

#[test]
fn pre_2000_cutoff_suppresses_before_the_resolver_is_consulted() {
    // `Arc`-owned (not borrowed) for the same reason as the fields-map
    // test above: `&DoiResolver`'s implicit `'static` bound rules out
    // a closure that borrows a plain local `AtomicUsize`.
    let calls = Arc::new(AtomicUsize::new(0));
    let calls_for_resolver = Arc::clone(&calls);
    let resolver_fn = move |_fields: &HashMap<String, String>, _et: &str| -> Option<String> {
        calls_for_resolver.fetch_add(1, Ordering::SeqCst);
        Some("10.1/should-not-be-used".to_string())
    };
    let resolver: &DoiResolver = &resolver_fn;

    let src = "@article{old, author={x}, title={T}, journal={J}, year={1986}}\n";
    let out = check(src, Some(resolver));

    assert!(out.is_empty());
    assert_eq!(
        calls.load(Ordering::SeqCst),
        0,
        "the pre-2000 cutoff must short-circuit before the resolver is ever called"
    );
}

#[test]
fn entry_with_existing_doi_skips_the_resolver_entirely() {
    // `Arc`-owned (not borrowed) for the same reason as the fields-map
    // test above: `&DoiResolver`'s implicit `'static` bound rules out
    // a closure that borrows a plain local `AtomicUsize`.
    let calls = Arc::new(AtomicUsize::new(0));
    let calls_for_resolver = Arc::clone(&calls);
    let resolver_fn = move |_fields: &HashMap<String, String>, _et: &str| -> Option<String> {
        calls_for_resolver.fetch_add(1, Ordering::SeqCst);
        Some("10.1/should-not-be-used".to_string())
    };
    let resolver: &DoiResolver = &resolver_fn;

    let src =
        "@article{has, author={x}, title={T}, journal={J}, year={2020}, doi = {10.9999/already}}\n";
    let out = check(src, Some(resolver));

    assert!(out.is_empty());
    assert_eq!(
        calls.load(Ordering::SeqCst),
        0,
        "an entry that already has a doi field must never reach the resolver"
    );
}
