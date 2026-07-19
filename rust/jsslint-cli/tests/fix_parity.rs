//! Phase 4 end-to-end acceptance harness for `--fix`/`--dry-run`/
//! `--apply`/`--fix-rule`: copies each `auto-fix/JSS-*/before.{tex,bib}`
//! fixture into an isolated scratch directory, runs the real
//! `jss-lint --fix` and the compiled `jsslint --fix` against their own
//! copies (same relative filename, so any path text embedded in
//! stdout/diffs lines up), and diffs stdout/exit code/final file
//! bytes. This exercises the full engine + fixer pipeline together
//! (not just each fixture's own rule, unlike `fixer_parity.rs`'s
//! `apply_to_text_matches_after_fixture`), so it's a genuine
//! differential test of `resolve_conflicts` + `apply_to_text` +
//! atomic write + re-validation-by-rerun end to end.
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

fn scratch_base() -> PathBuf {
    std::env::var("CARGO_TARGET_TMPDIR")
        .map(PathBuf::from)
        .unwrap_or_else(|_| std::env::temp_dir())
}

fn fixture_source(fixture: &str) -> (PathBuf, &'static str) {
    let dir = repo_root().join("tests/fixtures/auto-fix").join(fixture);
    if dir.join("before.tex").exists() {
        (dir.join("before.tex"), "before.tex")
    } else {
        (dir.join("before.bib"), "before.bib")
    }
}

struct Outcome {
    stdout: String,
    stderr: String,
    exit_code: Option<i32>,
    file_after: String,
}

fn run_fix(bin: &str, scratch: &Path, file_name: &str, extra_args: &[&str]) -> Outcome {
    let mut cmd = Command::new(bin);
    cmd.arg("--fix").arg("--output").arg("json");
    cmd.args(extra_args);
    cmd.arg(file_name);
    cmd.current_dir(scratch);
    let output = cmd
        .output()
        .unwrap_or_else(|e| panic!("failed to run {bin}: {e}"));
    let file_after = fs::read_to_string(scratch.join(file_name)).unwrap_or_default();
    Outcome {
        stdout: String::from_utf8_lossy(&output.stdout).into_owned(),
        stderr: String::from_utf8_lossy(&output.stderr).into_owned(),
        exit_code: output.status.code(),
        file_after,
    }
}

fn setup_scratch(fixture: &str, side: &str, mode: &str, source: &Path, file_name: &str) -> PathBuf {
    let dir = scratch_base().join(format!("fix-{fixture}-{side}-{mode}"));
    let _ = fs::remove_dir_all(&dir);
    fs::create_dir_all(&dir).expect("failed to create scratch dir");
    fs::copy(source, dir.join(file_name)).expect("failed to copy fixture into scratch dir");
    dir
}

/// Spec 013 auto-resolve canonicalizes a bare single-file root
/// argument to an absolute path (contract C-12). `py_dir`/`rs_dir` are
/// distinct scratch directories by construction (`{fixture}-py-*` vs
/// `{fixture}-rs-*`), so their absolute-path prefixes never match even
/// when the linted content is identical; normalize both to a shared
/// placeholder before comparing stdout.
fn normalize(stdout: &str, dir: &Path) -> String {
    stdout.replace(&dir.display().to_string(), "<SCRATCH>")
}

fn all_fixtures() -> Vec<String> {
    let dir = repo_root().join("tests/fixtures/auto-fix");
    let mut names: Vec<String> = fs::read_dir(&dir)
        .unwrap_or_else(|e| panic!("expected {} to exist: {e}", dir.display()))
        .flatten()
        .filter(|e| e.path().is_dir())
        .map(|e| e.file_name().to_string_lossy().into_owned())
        .collect();
    names.sort();
    names
}

#[test]
fn fix_write_matches_python_cli() {
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
    for fixture in all_fixtures() {
        let (source, file_name) = fixture_source(&fixture);
        let py_dir = setup_scratch(&fixture, "py", "write", &source, file_name);
        let rs_dir = setup_scratch(&fixture, "rs", "write", &source, file_name);

        let expected = run_fix(&jss_lint, &py_dir, file_name, &[]);
        let actual = run_fix(jsslint_bin, &rs_dir, file_name, &[]);
        let expected_stdout = normalize(&expected.stdout, &py_dir);
        let actual_stdout = normalize(&actual.stdout, &rs_dir);

        if actual_stdout != expected_stdout {
            mismatches.push(format!(
                "{fixture} STDOUT differs\n  expected:\n{expected_stdout}\n  actual:\n{actual_stdout}"
            ));
        }
        if actual.exit_code != expected.exit_code {
            mismatches.push(format!(
                "{fixture} EXIT CODE differs: expected {:?}, actual {:?}\n  expected stderr:\n{}\n  actual stderr:\n{}",
                expected.exit_code, actual.exit_code, expected.stderr, actual.stderr
            ));
        }
        if actual.file_after != expected.file_after {
            mismatches.push(format!(
                "{fixture} FILE CONTENT differs\n  expected:\n{}\n  actual:\n{}",
                expected.file_after, actual.file_after
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

#[test]
fn fix_dry_run_matches_python_cli_and_does_not_write() {
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

    // A tex fixture and a bib fixture — enough to exercise the
    // difflib-parity unified-diff path on both file kinds without
    // re-running every fixture (fix_write_matches_python_cli already
    // covers exhaustive fixture breadth for the write path).
    let fixtures = ["JSS-MARKUP-001", "JSS-NAME-002"];

    let mut mismatches = Vec::new();
    for fixture in fixtures {
        let (source, file_name) = fixture_source(fixture);
        let original = fs::read_to_string(&source).unwrap();
        let py_dir = setup_scratch(fixture, "py", "dry-run", &source, file_name);
        let rs_dir = setup_scratch(fixture, "rs", "dry-run", &source, file_name);

        let expected = run_fix(&jss_lint, &py_dir, file_name, &["--dry-run"]);
        let actual = run_fix(jsslint_bin, &rs_dir, file_name, &["--dry-run"]);
        let expected_stdout = normalize(&expected.stdout, &py_dir);
        let actual_stdout = normalize(&actual.stdout, &rs_dir);

        if actual_stdout != expected_stdout {
            mismatches.push(format!(
                "{fixture} STDOUT differs\n  expected:\n{expected_stdout}\n  actual:\n{actual_stdout}"
            ));
        }
        if actual.exit_code != expected.exit_code {
            mismatches.push(format!(
                "{fixture} EXIT CODE differs: expected {:?}, actual {:?}",
                expected.exit_code, actual.exit_code
            ));
        }
        if expected.file_after != original {
            mismatches.push(format!(
                "{fixture} python --dry-run unexpectedly wrote the file"
            ));
        }
        if actual.file_after != original {
            mismatches.push(format!(
                "{fixture} rust --dry-run unexpectedly wrote the file"
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

#[test]
fn fix_rule_filter_and_unknown_rule_match_python_cli() {
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
    let fixture = "JSS-MARKUP-001";
    let (source, file_name) = fixture_source(fixture);
    let original = fs::read_to_string(&source).unwrap();

    let mut mismatches = Vec::new();

    // A --fix-rule that doesn't match this fixture's own rule: the
    // violation is skipped as "rule-not-selected", file unchanged.
    {
        let py_dir = setup_scratch(fixture, "py", "filter-other", &source, file_name);
        let rs_dir = setup_scratch(fixture, "rs", "filter-other", &source, file_name);
        let expected = run_fix(
            &jss_lint,
            &py_dir,
            file_name,
            &["--fix-rule", "JSS-TYPO-001"],
        );
        let actual = run_fix(
            jsslint_bin,
            &rs_dir,
            file_name,
            &["--fix-rule", "JSS-TYPO-001"],
        );
        let expected_stdout = normalize(&expected.stdout, &py_dir);
        let actual_stdout = normalize(&actual.stdout, &rs_dir);
        if actual_stdout != expected_stdout {
            mismatches.push(format!(
                "filter-other STDOUT differs\n  expected:\n{expected_stdout}\n  actual:\n{actual_stdout}"
            ));
        }
        if actual.exit_code != expected.exit_code {
            mismatches.push(format!(
                "filter-other EXIT CODE differs: expected {:?}, actual {:?}",
                expected.exit_code, actual.exit_code
            ));
        }
        if expected.file_after != original || actual.file_after != original {
            mismatches.push("filter-other: file was unexpectedly modified".to_string());
        }
    }

    // An unknown --fix-rule: exit 2, matching stderr, no write.
    {
        let py_dir = setup_scratch(fixture, "py", "unknown-rule", &source, file_name);
        let rs_dir = setup_scratch(fixture, "rs", "unknown-rule", &source, file_name);
        let expected = run_fix(
            &jss_lint,
            &py_dir,
            file_name,
            &["--fix-rule", "JSS-DOES-NOT-EXIST"],
        );
        let actual = run_fix(
            jsslint_bin,
            &rs_dir,
            file_name,
            &["--fix-rule", "JSS-DOES-NOT-EXIST"],
        );
        if actual.stderr != expected.stderr {
            mismatches.push(format!(
                "unknown-rule STDERR differs\n  expected: {:?}\n  actual: {:?}",
                expected.stderr, actual.stderr
            ));
        }
        if actual.exit_code != expected.exit_code {
            mismatches.push(format!(
                "unknown-rule EXIT CODE differs: expected {:?}, actual {:?}",
                expected.exit_code, actual.exit_code
            ));
        }
        if expected.file_after != original || actual.file_after != original {
            mismatches.push("unknown-rule: file was unexpectedly modified".to_string());
        }
    }

    assert!(
        mismatches.is_empty(),
        "{} mismatches:\n{}",
        mismatches.len(),
        mismatches.join("\n---\n")
    );
}
