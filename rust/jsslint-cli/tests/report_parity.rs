//! Phase 4 end-to-end acceptance harness for the `report` subcommand
//! (`jsslint_core::conformance`, wired via `main.rs`'s hand-rolled
//! subcommand dispatch): runs the real `jss-lint report` and the
//! compiled `jsslint report` over real recall-corpus papers and diffs
//! stdout/stderr/exit code/`--out` file bytes.
//!
//! Covers: a single-file target, a directory target (multi-file, with
//! title/author extracted from `\title{}`/`\author{}` — opentsne),
//! `--title`/`--author` overrides, `--out` on a paper whose metadata
//! comes from `\Plaintitle{}`/`\Plainauthor{}` instead (trueskill —
//! exercises the macro-precedence + nested-node-text-extraction path
//! differently), and the `--format html`/`pdf` not-yet-implemented
//! rejection (exit code only — the message is this port's own, not a
//! byte-parity target, since Python actually renders HTML there while
//! this port doesn't yet).
//!
//! Skips entirely (doesn't fail) if the Python venv isn't set up.

use std::fs;
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

fn scratch_base() -> PathBuf {
    std::env::var("CARGO_TARGET_TMPDIR")
        .map(PathBuf::from)
        .unwrap_or_else(|_| std::env::temp_dir())
}

struct Outcome {
    stdout: String,
    stderr: String,
    exit_code: Option<i32>,
}

fn run(bin: &str, root: &PathBuf, args: &[&str]) -> Outcome {
    let output = Command::new(bin)
        .args(args)
        .current_dir(root)
        .output()
        .unwrap_or_else(|e| panic!("failed to run {bin}: {e}"));
    Outcome {
        stdout: String::from_utf8_lossy(&output.stdout).into_owned(),
        stderr: String::from_utf8_lossy(&output.stderr).into_owned(),
        exit_code: output.status.code(),
    }
}

fn compare(name: &str, expected: &Outcome, actual: &Outcome, mismatches: &mut Vec<String>) {
    if actual.stdout != expected.stdout {
        mismatches.push(format!(
            "{name} STDOUT differs\n  expected:\n{}\n  actual:\n{}",
            expected.stdout, actual.stdout
        ));
    }
    if actual.stderr != expected.stderr {
        mismatches.push(format!(
            "{name} STDERR differs\n  expected: {:?}\n  actual: {:?}",
            expected.stderr, actual.stderr
        ));
    }
    if actual.exit_code != expected.exit_code {
        mismatches.push(format!(
            "{name} EXIT CODE differs: expected {:?}, actual {:?}",
            expected.exit_code, actual.exit_code
        ));
    }
}

#[test]
fn report_matches_python_cli() {
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

    let cases: &[(&str, &[&str])] = &[
        (
            "single-file",
            &["report", "eval/recall-corpus/opentsne/main.tex"],
        ),
        ("dir-opentsne", &["report", "eval/recall-corpus/opentsne"]),
        ("dir-trueskill", &["report", "eval/recall-corpus/trueskill"]),
        (
            "title-author-override",
            &[
                "report",
                "eval/recall-corpus/opentsne",
                "--title",
                "Custom Title",
                "--author",
                "Custom Author",
            ],
        ),
    ];

    let mut mismatches = Vec::new();
    for &(name, args) in cases {
        let expected = run(&jss_lint, &root, args);
        let actual = run(jsslint_bin, &root, args);
        compare(name, &expected, &actual, &mut mismatches);
    }

    // `--format html`: real jss-lint actually renders HTML here (exit
    // 0); this port hasn't implemented it (task scope: markdown only)
    // and exits 2 with its own "not yet implemented" message — not a
    // Python-comparison scenario, just asserting this port's own
    // documented behavior.
    {
        let actual = run(
            jsslint_bin,
            &root,
            &["report", "eval/recall-corpus/opentsne", "--format", "html"],
        );
        if actual.exit_code != Some(2) {
            mismatches.push(format!(
                "format-html-not-implemented: expected exit 2, got {:?}",
                actual.exit_code
            ));
        }
        if !actual.stderr.contains("not yet implemented") {
            mismatches.push(format!(
                "format-html-not-implemented: expected a 'not yet implemented' stderr message, got {:?}",
                actual.stderr
            ));
        }
    }

    // --out: write to a file and diff the bytes.
    {
        let dir = scratch_base().join("report-out");
        fs::create_dir_all(&dir).expect("failed to create scratch dir");
        let py_out = dir.join("py.md");
        let rs_out = dir.join("rs.md");
        let expected = run(
            &jss_lint,
            &root,
            &[
                "report",
                "eval/recall-corpus/trueskill",
                "--out",
                py_out.to_str().unwrap(),
            ],
        );
        let actual = run(
            jsslint_bin,
            &root,
            &[
                "report",
                "eval/recall-corpus/trueskill",
                "--out",
                rs_out.to_str().unwrap(),
            ],
        );
        compare("out-flag", &expected, &actual, &mut mismatches);
        let expected_bytes = fs::read(&py_out).ok();
        let actual_bytes = fs::read(&rs_out).ok();
        if actual_bytes != expected_bytes {
            mismatches.push("out-flag: written file bytes differ".to_string());
        }
    }

    assert!(
        mismatches.is_empty(),
        "{} mismatches:\n{}",
        mismatches.len(),
        mismatches.join("\n---\n")
    );
}
