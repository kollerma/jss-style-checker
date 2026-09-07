//! Baseline parity (spec 027 item B, `baseline-file.md` C-10).
//!
//! A baseline is written once and read for months, quite possibly by
//! the other engine: a maintainer runs `jss-lint --update-baseline`
//! locally and CI runs `jsslint --baseline`, or the reverse. So the
//! file must be byte-identical whichever engine wrote it, and applying
//! it must produce identical stdout and exit codes.
//!
//! Only the error text for a malformed file may differ (the two JSON
//! parsers' messages), as for `jss-lint diff`; exit code 2 is compared.
//!
//! Skips entirely (doesn't fail) if the Python venv isn't set up.

use std::fs;
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

/// Two findings of two different rules, in one file — enough for the
/// summary line to distinguish matched from stale from unevaluated.
const SOURCE: &str = "\\documentclass[article]{jss}\n\
                      \\title{A Short Demo}\n\
                      \\Abstract{Demo.}\n\
                      \\Keywords{Demo}\n\
                      \\Address{Demo}\n\
                      \\begin{document}\n\
                      \\section{Methods And Results}\n\
                      We use R for everything.\n\
                      \\end{document}\n";

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

/// A scratch directory holding `paper.tex`, per engine, so neither run
/// can see the other's baseline file.
fn scratch(name: &str, source: &str) -> PathBuf {
    let dir = std::env::temp_dir().join(format!("jsslint-baseline-parity-{name}"));
    let _ = fs::remove_dir_all(&dir);
    fs::create_dir_all(&dir).expect("create scratch dir");
    fs::write(dir.join("paper.tex"), source).expect("write fixture");
    dir
}

#[test]
fn baseline_files_and_reports_match_python_cli() {
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

    let py_dir = scratch("py", SOURCE);
    let rs_dir = scratch("rs", SOURCE);

    // 1. `--update-baseline` writes byte-identical files.
    let write_args = ["--baseline", "b.json", "--update-baseline", "paper.tex"];
    let py_write = run(&jss_lint, &write_args, &py_dir);
    let rs_write = run(jsslint_bin, &write_args, &rs_dir);
    assert_eq!(py_write.exit_code, Some(0), "python --update-baseline failed");
    assert_eq!(rs_write.exit_code, Some(0), "rust --update-baseline failed");
    assert_eq!(
        py_write.stdout, rs_write.stdout,
        "--update-baseline renders no report in either engine"
    );
    let py_file = fs::read_to_string(py_dir.join("b.json")).expect("python wrote a baseline");
    let rs_file = fs::read_to_string(rs_dir.join("b.json")).expect("rust wrote a baseline");
    assert_eq!(
        py_file, rs_file,
        "baseline files differ; a file written by one engine must be readable \
         and identical to one written by the other"
    );
    assert!(
        py_file.contains("\"schema_version\": 1"),
        "unexpected baseline shape: {py_file}"
    );

    // 2. Applying it: identical stdout and exit code in every format.
    let mut mismatches = Vec::new();
    let apply_cases: &[&[&str]] = &[
        &["--baseline", "b.json", "paper.tex"],
        &["--baseline", "b.json", "--mode", "reviewer", "paper.tex"],
        &["--baseline", "b.json", "--output", "json", "paper.tex"],
        &["--baseline", "b.json", "--output", "sarif", "paper.tex"],
        &["--baseline", "b.json", "--output", "html", "paper.tex"],
        // `--min-confidence high` turns unmatched entries into
        // `unevaluated`, not `stale` — the split both engines must agree
        // on (`baseline-file.md` C-4 §4).
        &[
            "--baseline",
            "b.json",
            "--min-confidence",
            "high",
            "paper.tex",
        ],
    ];
    for &args in apply_cases {
        let expected = run(&jss_lint, args, &py_dir);
        let actual = run(jsslint_bin, args, &rs_dir);
        if expected.stdout != actual.stdout || expected.exit_code != actual.exit_code {
            mismatches.push(format!(
                "{args:?}\n  expected (exit {:?}):\n{}\n  actual (exit {:?}):\n{}",
                expected.exit_code, expected.stdout, actual.exit_code, actual.stdout
            ));
        }
    }

    // 3. Drift: an edit that adds a finding of a *different* rule must
    // be reported by both, with the same exit code.
    let drifted = SOURCE.replace(
        "\\end{document}",
        "We call lm() in prose.\n\\end{document}",
    );
    for dir in [&py_dir, &rs_dir] {
        fs::write(dir.join("paper.tex"), &drifted).expect("rewrite fixture");
    }
    let args = ["--baseline", "b.json", "paper.tex"];
    let expected = run(&jss_lint, &args, &py_dir);
    let actual = run(jsslint_bin, &args, &rs_dir);
    assert_eq!(expected.exit_code, Some(1), "the new finding must fail the run");
    if expected.stdout != actual.stdout || expected.exit_code != actual.exit_code {
        mismatches.push(format!(
            "drift case\n  expected:\n{}\n  actual:\n{}",
            expected.stdout, actual.stdout
        ));
    }

    // 4. The TOML key is honoured identically.
    for dir in [&py_dir, &rs_dir] {
        fs::write(dir.join("paper.tex"), SOURCE).expect("restore fixture");
        fs::write(dir.join(".jss-lint.toml"), "baseline = \"b.json\"\n")
            .expect("write config");
    }
    let expected = run(&jss_lint, &["paper.tex"], &py_dir);
    let actual = run(jsslint_bin, &["paper.tex"], &rs_dir);
    if expected.stdout != actual.stdout || expected.exit_code != actual.exit_code {
        mismatches.push(format!(
            "TOML key\n  expected:\n{}\n  actual:\n{}",
            expected.stdout, actual.stdout
        ));
    }
    assert!(
        expected.stdout.contains("Baseline: "),
        "the TOML key did not apply a baseline: {}",
        expected.stdout
    );

    assert!(
        mismatches.is_empty(),
        "{} case(s) diverge:\n{}",
        mismatches.len(),
        mismatches.join("\n---\n")
    );
}

#[test]
fn subdirectory_baseline_and_journal_mismatch_match_python_cli() {
    let root = repo_root();
    let jss_lint = root.join(".venv/bin/jss-lint");
    if !jss_lint.exists() {
        eprintln!("SKIP: {} not found", jss_lint.display());
        return;
    }
    let jss_lint = jss_lint.to_string_lossy().to_string();
    let jsslint_bin = env!("CARGO_BIN_EXE_jsslint");

    for (name, bin) in [("py-sub", jss_lint.as_str()), ("rs-sub", jsslint_bin)] {
        let dir = scratch(name, SOURCE);
        fs::create_dir_all(dir.join("ci")).expect("create subdir");

        // A baseline one directory down records `../paper.tex` and still
        // matches (`baseline-file.md` C-3).
        let write = run(
            bin,
            &["--baseline", "ci/b.json", "--update-baseline", "paper.tex"],
            &dir,
        );
        assert_eq!(write.exit_code, Some(0), "{name}: --update-baseline failed");
        let text = fs::read_to_string(dir.join("ci/b.json")).expect("baseline written");
        assert!(
            text.contains("\"path\": \"../paper.tex\""),
            "{name}: expected parent-relative paths, got:\n{text}"
        );
        let apply = run(bin, &["--baseline", "ci/b.json", "paper.tex"], &dir);
        assert_eq!(
            apply.exit_code,
            Some(0),
            "{name}: a subdirectory baseline did not match:\n{}",
            apply.stdout
        );

        // A baseline written for another journal is refused, exit 2.
        let swapped = text.replace("\"journal\": \"jss\"", "\"journal\": \"other\"");
        fs::write(dir.join("ci/b.json"), swapped).expect("rewrite baseline");
        let mismatch = run(bin, &["--baseline", "ci/b.json", "paper.tex"], &dir);
        assert_eq!(
            mismatch.exit_code,
            Some(2),
            "{name}: a journal mismatch must exit 2"
        );

        // A malformed file is exit 2 as well; only the message differs.
        fs::write(dir.join("ci/b.json"), "{not json").expect("rewrite baseline");
        let malformed = run(bin, &["--baseline", "ci/b.json", "paper.tex"], &dir);
        assert_eq!(
            malformed.exit_code,
            Some(2),
            "{name}: a malformed baseline must exit 2"
        );
    }
}
