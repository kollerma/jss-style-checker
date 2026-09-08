//! `coverage` subcommand parity (spec 027 FR-G-004, `coverage-file.md` C-6).
//!
//! The matrix answers "what does this tool not check?", and an author
//! who asks a WASM/CRAN/crates.io build must get the same answer the
//! Python CLI gives. All three formats are compared byte for byte, plus
//! the journal-without-coverage case.
//!
//! Skips entirely (doesn't fail) if the Python venv isn't set up.

use std::path::{Path, PathBuf};
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
    exit_code: Option<i32>,
}

fn run(bin: &str, args: &[&str], cwd: &Path) -> Outcome {
    let output = Command::new(bin)
        .args(args)
        .current_dir(cwd)
        .output()
        .unwrap_or_else(|e| panic!("failed to run {bin}: {e}"));
    Outcome {
        stdout: String::from_utf8_lossy(&output.stdout).into_owned(),
        exit_code: output.status.code(),
    }
}

#[test]
fn coverage_matches_python_cli() {
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
        &["coverage"],
        &["coverage", "--format", "terminal"],
        &["coverage", "--format", "markdown"],
        &["coverage", "--format", "json"],
        // `ignore_case` on both sides.
        &["coverage", "--format", "MARKDOWN"],
        &["coverage", "--journal", "jss"],
    ];

    let mut mismatches = Vec::new();
    for &args in cases {
        let expected = run(&jss_lint, args, &root);
        let actual = run(jsslint_bin, args, &root);
        if expected.stdout != actual.stdout {
            mismatches.push(format!(
                "{args:?} STDOUT differs\n  expected:\n{}\n  actual:\n{}",
                expected.stdout, actual.stdout
            ));
        }
        if expected.exit_code != actual.exit_code || expected.exit_code != Some(0) {
            mismatches.push(format!(
                "{args:?} EXIT CODE differs: expected {:?}, actual {:?}",
                expected.exit_code, actual.exit_code
            ));
        }
    }

    // A journal with no coverage data says so, and still exits 0: asking
    // what a tool checks must never be an error.
    let scratch = std::env::temp_dir().join("jsslint-coverage-parity");
    std::fs::create_dir_all(&scratch).expect("create scratch dir");
    std::fs::write(scratch.join(".jss-lint.toml"), "journal = \"stub\"\n")
        .expect("write config");
    let expected = run(&jss_lint, &["coverage"], &scratch);
    let actual = run(jsslint_bin, &["coverage"], &scratch);
    assert_eq!(expected.exit_code, Some(0), "python must exit 0");
    assert!(
        expected.stdout.contains("no guide-coverage data"),
        "expected the no-data sentence, got: {}",
        expected.stdout
    );
    if expected.stdout != actual.stdout || expected.exit_code != actual.exit_code {
        mismatches.push(format!(
            "no-coverage journal differs\n  expected:\n{}\n  actual:\n{}",
            expected.stdout, actual.stdout
        ));
    }

    assert!(
        mismatches.is_empty(),
        "{} case(s) diverge:\n{}",
        mismatches.len(),
        mismatches.join("\n---\n")
    );
}
