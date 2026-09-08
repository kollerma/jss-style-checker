//! Soft gate on the browser bundle (spec 027 plan §10).
//!
//! The web app is the front door for an author who has installed
//! nothing, and the whole engine has to arrive before the page is
//! usable. Bundle growth is invisible in a diff — every rule, every
//! catalogue string, every embedded table adds a few kilobytes that
//! nobody notices until the page is slow on a conference wifi.
//!
//! So: a ceiling, checked in CI, well above today's size. It is
//! deliberately *soft* — crossing it means "look at what you added and
//! decide", not "this is forbidden". Raise it with a reason in the
//! commit message.
//!
//! Skips (doesn't fail) when no bundle has been built: `cargo test`
//! alone does not run `wasm-pack`, and a developer who has never built
//! the web app should not see a red suite.

use std::path::PathBuf;

/// 2.2 MB. Spec 027 measured 1.96 MB before the feature and 2.07 MB
/// after; the headroom is roughly one more feature's worth.
const CEILING_BYTES: u64 = 2_200_000;

fn repo_root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .parent()
        .unwrap()
        .to_path_buf()
}

#[test]
fn browser_bundle_stays_under_the_ceiling() {
    let bundle = repo_root().join("web/pkg/jsslint_wasm_bg.wasm");
    let Ok(meta) = std::fs::metadata(&bundle) else {
        eprintln!(
            "SKIP: {} not built (run `wasm-pack build --release --target web \
             --out-dir ../../web/pkg` in rust/jsslint-wasm)",
            bundle.display()
        );
        return;
    };

    let size = meta.len();
    eprintln!(
        "web/pkg/jsslint_wasm_bg.wasm: {size} bytes ({:.2} MB)",
        size as f64 / 1_048_576.0
    );
    assert!(
        size <= CEILING_BYTES,
        "browser bundle is {size} bytes, over the {CEILING_BYTES}-byte soft ceiling.\n\
         Check what grew (embedded catalogue data? a new dependency?). If the growth \
         is justified, raise CEILING_BYTES here and say why in the commit message."
    );
}
