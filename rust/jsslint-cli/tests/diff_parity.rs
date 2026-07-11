//! Phase 4 end-to-end acceptance harness for the `diff` subcommand
//! (`jsslint_core::diff`, wired via `main.rs`'s hand-rolled subcommand
//! dispatch): runs the real `jss-lint diff` and the compiled `jsslint
//! diff` over a real recall-corpus report and diffs stdout/exit code.
//! Covers all three formats, `--ignore-line-drift`, an
//! identical-inputs no-op, a mixed fixed+introduced case, and every
//! `validate_payload` schema-mismatch branch (byte-matched exactly —
//! unlike the file-not-found/malformed-JSON-content paths, which
//! `main.rs::load_diff_input`'s doc comment explains are not
//! byte-parity targets).
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

fn run(bin: &str, dir: &PathBuf, args: &[&str]) -> Outcome {
    let output = Command::new(bin)
        .args(args)
        .current_dir(dir)
        .output()
        .unwrap_or_else(|e| panic!("failed to run {bin}: {e}"));
    Outcome {
        stdout: String::from_utf8_lossy(&output.stdout).into_owned(),
        stderr: String::from_utf8_lossy(&output.stderr).into_owned(),
        exit_code: output.status.code(),
    }
}

fn scratch_dir() -> PathBuf {
    let dir = scratch_base().join("diff-parity");
    fs::create_dir_all(&dir).expect("failed to create scratch dir");
    dir
}

/// Runs the real `jss-lint --output json` over a real corpus paper
/// once and writes `old.json`/`new.json` (new = old with one
/// violation removed and one synthetic one appended) plus a handful
/// of hand-built schema-mismatch fixtures into the scratch dir. Reused
/// by every scenario so the corpus lint itself only runs once.
fn setup_fixtures(jss_lint: &str) -> PathBuf {
    let dir = scratch_dir();
    let paper_dir = repo_root().join("eval/recall-corpus/opentsne");
    let old_json = Command::new(jss_lint)
        .arg("--output")
        .arg("json")
        .arg("main.tex")
        .arg("references.bib")
        .current_dir(&paper_dir)
        .output()
        .expect("failed to run jss-lint for fixture setup");
    let old_text = String::from_utf8(old_json.stdout).expect("stdout must be valid UTF-8");
    fs::write(dir.join("old.json"), &old_text).unwrap();

    let mut payload: serde_json::Value = serde_json::from_str(&old_text).unwrap();
    let violations = payload["violations"].as_array_mut().unwrap();
    if !violations.is_empty() {
        violations.remove(0);
    }
    if let Some(last) = violations.last().cloned() {
        let mut added = last;
        added["rule_id"] = serde_json::json!("JSS-ZZZ-999");
        added["message"] = serde_json::json!("synthetic new violation");
        violations.push(added);
    }
    fs::write(
        dir.join("new.json"),
        serde_json::to_string(&payload).unwrap(),
    )
    .unwrap();

    fs::write(dir.join("missing_keys.json"), r#"{"violations": []}"#).unwrap();
    fs::write(
        dir.join("bad_violations_type.json"),
        r#"{"tool_version":"x","journal_id":"y","violations":"not-a-list"}"#,
    )
    .unwrap();
    fs::write(dir.join("not_object.json"), "[]").unwrap();
    fs::write(
        dir.join("missing_v_keys.json"),
        r#"{"tool_version":"x","journal_id":"y","violations":[{"rule_id":"A","file":"m.tex"}]}"#,
    )
    .unwrap();
    fs::write(
        dir.join("v_not_object.json"),
        r#"{"tool_version":"x","journal_id":"y","violations":["notobj"]}"#,
    )
    .unwrap();

    dir
}

#[test]
fn diff_matches_python_cli() {
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
    let dir = setup_fixtures(&jss_lint);

    let cases: &[&[&str]] = &[
        &["diff", "old.json", "new.json"],
        &["diff", "old.json", "new.json", "--format", "markdown"],
        &["diff", "old.json", "new.json", "--format", "json"],
        &["diff", "old.json", "old.json"],
        &["diff", "old.json", "old.json", "--ignore-line-drift"],
        &["diff", "missing_keys.json", "old.json"],
        &["diff", "bad_violations_type.json", "old.json"],
        &["diff", "not_object.json", "old.json"],
        &["diff", "missing_v_keys.json", "old.json"],
        &["diff", "v_not_object.json", "old.json"],
    ];

    let mut mismatches = Vec::new();
    for &args in cases {
        let expected = run(&jss_lint, &dir, args);
        let actual = run(jsslint_bin, &dir, args);

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
