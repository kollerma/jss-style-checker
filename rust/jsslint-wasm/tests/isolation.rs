//! Constitution §XIV — portable-core isolation guard.
//!
//! The WASM build's privacy guarantee ("manuscripts never leave the
//! machine") holds **by construction**: no network-capable crate may appear
//! in the dependency graph of `jsslint-core` or any portable binding built
//! on it. Network code lives exclusively in `jsslint-crossref`, consumed
//! only by `jsslint-cli`. This test turns that from a convention into a
//! CI-enforced fact: it fails if a forbidden crate ever enters the graph of
//! `jsslint-core`, `jsslint-wasm`, `jsslint-py`, or the R package's
//! vendored workspace.
//!
//! (`jsslint-cli` intentionally DOES depend on `jsslint-crossref`/`ureq` —
//! it is the fs/network-having front-end — so it is not checked here.)

use std::path::Path;
use std::process::Command;

/// Crate names that indicate network capability. `jsslint-crossref` is the
/// project's own network client; the rest are the HTTP stacks it (or a
/// future edit) could plausibly pull in.
const FORBIDDEN: &[&str] = &[
    "jsslint-crossref",
    "ureq",
    "reqwest",
    "hyper",
    "curl",
    "native-tls",
];

/// `cargo tree --prefix none` prints one `name vX.Y.Z ...` line per crate;
/// match on the `name v` prefix so an unrelated crate that merely contains
/// a forbidden name as a substring can't false-positive.
fn assert_tree_clean(label: &str, tree_output: &str) {
    for forbidden in FORBIDDEN {
        let prefix = format!("{forbidden} v");
        assert!(
            !tree_output.lines().any(|l| l.trim().starts_with(&prefix)),
            "Constitution §XIV violation: network-capable crate `{forbidden}` \
             appears in the dependency graph of {label}. Network code must \
             live in jsslint-crossref and be consumed only by jsslint-cli."
        );
    }
}

#[test]
fn portable_crates_link_no_network_code() {
    let cargo = std::env::var("CARGO").unwrap_or_else(|_| "cargo".to_string());
    // CARGO_MANIFEST_DIR = rust/jsslint-wasm; the workspace root is rust/.
    let workspace = Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .expect("jsslint-wasm has a parent dir")
        .to_path_buf();

    for pkg in ["jsslint-core", "jsslint-wasm", "jsslint-py"] {
        let out = Command::new(&cargo)
            // normal+build edges = what ships; dev-dependencies (test
            // harnesses) are excluded deliberately.
            .args(["tree", "-p", pkg, "--edges", "normal,build", "--prefix", "none"])
            .current_dir(&workspace)
            .output()
            .expect("failed to spawn cargo tree");
        assert!(
            out.status.success(),
            "cargo tree -p {pkg} failed: {}",
            String::from_utf8_lossy(&out.stderr)
        );
        assert_tree_clean(pkg, &String::from_utf8_lossy(&out.stdout));
    }
}

#[test]
fn vendored_r_crate_links_no_network_code() {
    // The R package's vendored workspace is separate and carries its own
    // committed Cargo.lock, which enumerates every crate in its graph — so a
    // hermetic lockfile scan suffices (no cargo invocation that might need
    // the network to resolve a second workspace in CI).
    let lock = Path::new(env!("CARGO_MANIFEST_DIR"))
        .join("../../r/jsslintr/src/rust/Cargo.lock");
    let text = std::fs::read_to_string(&lock)
        .unwrap_or_else(|e| panic!("cannot read {}: {e}", lock.display()));
    for forbidden in FORBIDDEN {
        let entry = format!("name = \"{forbidden}\"");
        assert!(
            !text.contains(&entry),
            "Constitution §XIV violation: network-capable crate `{forbidden}` \
             appears in the vendored R workspace lockfile {}.",
            lock.display()
        );
    }
}
