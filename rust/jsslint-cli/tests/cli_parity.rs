//! Phase 4 end-to-end acceptance harness: the compiled `jsslint`
//! binary's stdout AND exit code must match the real `jss-lint`
//! binary on real multi-file papers — the plan's "binary smoke test"
//! criterion (`jsslint paper.tex` exits with the right code and
//! output), run as an actual differential test rather than a manual
//! check.
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

/// See `jsslint-core/tests/engine_parity.rs` for why trueskill needs
/// JSS-REFS-004 ignored on both sides (a genuine, confirmed
/// nondeterminism in the Python original's frozenset-iteration-order
/// "first match" logic, not a Rust-port bug).
const PAPERS: &[(&str, &[&str], &[&str])] = &[
    (
        "eval/recall-corpus/opentsne",
        &["main.tex", "references.bib"],
        &[],
    ),
    (
        "eval/recall-corpus/trueskill",
        &["article.tex", "gaming.bib", "journalsAbbr.bib"],
        &["JSS-REFS-004"],
    ),
];

struct Outcome {
    stdout: String,
    exit_code: Option<i32>,
}

fn run(bin: &str, dir: &PathBuf, files: &[&str], ignore_rules: &[&str]) -> Outcome {
    let mut cmd = Command::new(bin);
    cmd.arg("--output").arg("json");
    if !ignore_rules.is_empty() {
        cmd.arg("--ignore-rules").arg(ignore_rules.join(","));
    }
    let output = cmd
        .args(files)
        .current_dir(dir)
        .output()
        .unwrap_or_else(|e| panic!("failed to run {bin}: {e}"));
    Outcome {
        stdout: String::from_utf8(output.stdout).expect("stdout must be valid UTF-8"),
        exit_code: output.status.code(),
    }
}

#[test]
fn cli_matches_python_cli_end_to_end() {
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

    let mut mismatches = Vec::new();
    for &(paper_dir, files, ignore_rules) in PAPERS {
        let dir = root.join(paper_dir);
        let expected = run(&jss_lint, &dir, files, ignore_rules);
        let actual = run(jsslint_bin, &dir, files, ignore_rules);

        if actual.stdout != expected.stdout {
            mismatches.push(format!(
                "{paper_dir} STDOUT differs\n  expected:\n{}\n  actual:\n{}",
                expected.stdout, actual.stdout
            ));
        }
        if actual.exit_code != expected.exit_code {
            mismatches.push(format!(
                "{paper_dir} EXIT CODE differs: expected {:?}, actual {:?}",
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
