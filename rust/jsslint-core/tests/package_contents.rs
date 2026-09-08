//! The published crate carries the catalogue data it compiles against.
//!
//! `build.rs` reads five files from `specs/003-jss-rule-catalogue/`. A
//! crates.io tarball cannot reach outside its own directory, so the
//! crate ships a vendored copy — and `cargo package` only includes what
//! it is told to. If one of these files were left out, the crate would
//! simply fail to build for everyone installing it from crates.io while
//! building fine in this repository, which is the worst possible place
//! to discover it (spec 027 §10).
//!
//! Skips when `cargo` is unavailable or the packaging step cannot run
//! (a dirty workspace is fine — `--allow-dirty` covers it — but an
//! offline registry, say, is not something to fail a test run over).

use std::path::PathBuf;
use std::process::Command;

const REQUIRED: &[&str] = &[
    "specs/003-jss-rule-catalogue/catalogue.yaml",
    "specs/003-jss-rule-catalogue/terms.json",
    "specs/003-jss-rule-catalogue/latex-macro-specs.json",
    "specs/003-jss-rule-catalogue/recall.json",
    "specs/003-jss-rule-catalogue/guide-coverage.yaml",
];

#[test]
fn published_crate_includes_every_catalogue_file() {
    let manifest = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("Cargo.toml");
    let output = Command::new(std::env::var("CARGO").unwrap_or_else(|_| "cargo".into()))
        .args(["package", "--list", "--allow-dirty", "--manifest-path"])
        .arg(&manifest)
        .output();
    let Ok(output) = output else {
        eprintln!("SKIP: cargo not runnable");
        return;
    };
    if !output.status.success() {
        eprintln!(
            "SKIP: `cargo package --list` failed: {}",
            String::from_utf8_lossy(&output.stderr)
        );
        return;
    }
    let listed = String::from_utf8_lossy(&output.stdout);
    let missing: Vec<&str> = REQUIRED
        .iter()
        .copied()
        .filter(|path| !listed.lines().any(|line| line.trim() == *path))
        .collect();
    assert!(
        missing.is_empty(),
        "these files are read by build.rs but would not ship in the crate: \
         {missing:?}\nlisted:\n{listed}"
    );
}
