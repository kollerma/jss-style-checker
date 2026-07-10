//! Phase 4 end-to-end acceptance harness for the `explain` subcommand
//! (`jsslint_core::explain`, wired via `main.rs`'s hand-rolled
//! subcommand dispatch): runs the real `jss-lint explain` and the
//! compiled `jsslint explain` and diffs stdout/stderr/exit code.
//! Covers the full per-category listing (exercises every catalogue
//! rule's category grouping/sorting in one shot), a high-confidence
//! rule (no "Confidence:" line) and a below-high-confidence rule (has
//! one), case-insensitive/whitespace-tolerant lookup, both output
//! formats, and the unknown-rule-id "did you mean?" path (which
//! exercises `difflib`-parity tie-breaking in `close_matches`).
//!
//! Skips entirely (doesn't fail) if the Python venv isn't set up.

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

struct Outcome {
    stdout: String,
    stderr: String,
    exit_code: Option<i32>,
}

fn run(bin: &str, args: &[&str]) -> Outcome {
    let output = Command::new(bin)
        .args(args)
        .current_dir(repo_root())
        .output()
        .unwrap_or_else(|e| panic!("failed to run {bin}: {e}"));
    Outcome {
        stdout: String::from_utf8_lossy(&output.stdout).into_owned(),
        stderr: String::from_utf8_lossy(&output.stderr).into_owned(),
        exit_code: output.status.code(),
    }
}

#[test]
fn explain_matches_python_cli() {
    let root = repo_root();
    let jss_lint = root.join(".venv/bin/jss-lint");
    if !jss_lint.exists() {
        eprintln!(
            "SKIP: {} not found (Python venv not set up)",
            jss_lint.display()
        );
        return;
    }
    let jss_lint = jss_lint.to_string_lossy().to_string();
    let jsslint_bin = env!("CARGO_BIN_EXE_jsslint");

    let cases: &[&[&str]] = &[
        &["explain"],
        &["explain", "--format", "markdown"],
        &["explain", "JSS-STRUCT-001"],
        &["explain", "JSS-STRUCT-001", "--format", "markdown"],
        &["explain", "JSS-CITE-002"],
        &["explain", "JSS-CITE-002", "--format", "markdown"],
        &["explain", "  jss-cite-002  "],
        &["explain", "JSS-CITE-999"],
        &["explain", "JSS-CITE-999", "--format", "markdown"],
        &["explain", "totally-bogus-id"],
    ];

    let mut mismatches = Vec::new();
    for &args in cases {
        let expected = run(&jss_lint, args);
        let actual = run(jsslint_bin, args);

        if actual.stdout != expected.stdout {
            mismatches.push(format!(
                "{args:?} STDOUT differs\n  expected:\n{}\n  actual:\n{}",
                expected.stdout, actual.stdout
            ));
        }
        if actual.stderr != expected.stderr {
            mismatches.push(format!(
                "{args:?} STDERR differs\n  expected: {:?}\n  actual: {:?}",
                expected.stderr, actual.stderr
            ));
        }
        if actual.exit_code != expected.exit_code {
            mismatches.push(format!(
                "{args:?} EXIT CODE differs: expected {:?}, actual {:?}",
                expected.exit_code, actual.exit_code
            ));
        }
    }

    assert!(
        mismatches.is_empty(),
        "{} mismatches:\n{}",
        mismatches.len(),
        mismatches.join("\n---\n")
    );
}
