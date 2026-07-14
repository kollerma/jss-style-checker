//! Phase 5 end-to-end acceptance harness for the WASM binding:
//! cross-compiles `jsslint-wasm` to `wasm32-unknown-unknown`,
//! generates Node.js-target JS glue via `wasm-bindgen-cli`, then runs
//! a small Node script that calls the compiled module's `render()`
//! exactly as a real JS caller would, and diffs its output against
//! the real `jss-lint --output json` CLI on the same real
//! recall-corpus paper.
//!
//! Skips entirely (doesn't fail) if the `wasm32-unknown-unknown`
//! target, the `wasm-bindgen` CLI (`cargo install wasm-bindgen-cli`,
//! version-matched to the `wasm-bindgen` crate in Cargo.lock), `node`,
//! or the Python venv aren't available — none of these are assumed
//! present in every environment this workspace might be built in.

use std::path::PathBuf;
use std::process::Command;

fn repo_root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .parent()
        .unwrap()
        .to_path_buf()
}

fn tool_on_path(name: &str) -> bool {
    Command::new(name)
        .arg("--version")
        .output()
        .map(|o| o.status.success())
        .unwrap_or(false)
}

#[test]
fn wasm_render_matches_python_cli() {
    let root = repo_root();
    let jss_lint = root.join(".venv/bin/jss-lint");
    if !jss_lint.exists() {
        eprintln!(
            "SKIP: {} not found (Python venv not set up)",
            jss_lint.display()
        );
        return;
    }
    if !tool_on_path("wasm-bindgen") {
        eprintln!("SKIP: wasm-bindgen CLI not on PATH (cargo install wasm-bindgen-cli)");
        return;
    }
    if !tool_on_path("node") {
        eprintln!("SKIP: node not on PATH");
        return;
    }
    let corpus_sentinel = root.join("eval/recall-corpus/opentsne/main.tex");
    if !corpus_sentinel.exists() {
        eprintln!(
            "SKIP: {} not found (run `eval-jss corpus fetch` && `python -m eval.recall_corpus_scaffold` to materialize the recall corpus)",
            corpus_sentinel.display()
        );
        return;
    }

    let rust_dir = root.join("rust");
    let build = Command::new("cargo")
        .args([
            "build",
            "-p",
            "jsslint-wasm",
            "--target",
            "wasm32-unknown-unknown",
            "--release",
        ])
        .current_dir(&rust_dir)
        .status()
        .expect("failed to run cargo build for wasm32 target");
    if !build.success() {
        panic!("cargo build --target wasm32-unknown-unknown failed");
    }

    let wasm_artifact = rust_dir.join("target/wasm32-unknown-unknown/release/jsslint_wasm.wasm");
    let scratch = std::env::var("CARGO_TARGET_TMPDIR")
        .map(PathBuf::from)
        .unwrap_or_else(|_| std::env::temp_dir())
        .join("jsslint-wasm-pkg");
    let _ = std::fs::remove_dir_all(&scratch);

    let bindgen = Command::new("wasm-bindgen")
        .args(["--target", "nodejs", "--out-dir"])
        .arg(&scratch)
        .arg(&wasm_artifact)
        .status()
        .expect("failed to run wasm-bindgen");
    if !bindgen.success() {
        panic!("wasm-bindgen failed");
    }

    let paper_dir = root.join("eval/recall-corpus/opentsne");
    // File labels must match exactly what the Python oracle below uses
    // (invoked with cwd=paper_dir and bare "main.tex"/"references.bib"
    // args) — Violation.file is a verbatim echo of whatever label the
    // caller passes in, on both sides, so a mismatched label here
    // would fail every violation's "file" field despite both engines
    // agreeing on every substantive finding.
    let node_script = format!(
        r#"
const jsslint = require({glue_path:?});
const fs = require('fs');
const tex = fs.readFileSync({tex_path:?}, 'utf8');
const bib = fs.readFileSync({bib_path:?}, 'utf8');
const result = jsslint.render({{
  files: [
    ['main.tex', tex],
    ['references.bib', bib],
  ],
  output: 'json',
}});
process.stdout.write(result);
"#,
        glue_path = scratch.join("jsslint_wasm.js").to_string_lossy(),
        tex_path = paper_dir.join("main.tex").to_string_lossy(),
        bib_path = paper_dir.join("references.bib").to_string_lossy(),
    );
    let script_path = scratch.join("run.js");
    std::fs::write(&script_path, node_script).expect("failed to write node script");

    let node_output = Command::new("node")
        .arg(&script_path)
        .output()
        .expect("failed to run node");
    assert!(
        node_output.status.success(),
        "node script failed: {}",
        String::from_utf8_lossy(&node_output.stderr)
    );
    let actual = String::from_utf8(node_output.stdout).expect("node stdout must be valid UTF-8");

    let py_output = Command::new(&jss_lint)
        .arg("--output")
        .arg("json")
        .arg("main.tex")
        .arg("references.bib")
        .current_dir(&paper_dir)
        .output()
        .expect("failed to run jss-lint");
    let expected =
        String::from_utf8(py_output.stdout).expect("jss-lint stdout must be valid UTF-8");

    assert_eq!(
        actual, expected,
        "WASM render() output diverges from jss-lint --output json"
    );
}
