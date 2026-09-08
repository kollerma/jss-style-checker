//! `--version` parity (spec 027 item D,
//! `specs/027-first-time-user-gaps/contracts/version-output.md` C-5).
//!
//! Lines 1, 3, and 4 are byte-identical across engines; line 2 names the
//! engine and is the one documented §XIII divergence, so it is masked
//! here rather than compared. Cases: the default invocation, an explicit
//! `--journal jss`, and a scratch directory whose `.jss-lint.toml` names
//! an unregistered journal — the last one proves the flag is *not*
//! eager, i.e. that configuration is resolved before the block prints.
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

/// Everything but line 2 — the engine line, which legitimately differs.
fn masked(stdout: &str) -> Vec<&str> {
    stdout
        .lines()
        .enumerate()
        .filter(|(i, _)| *i != 1)
        .map(|(_, line)| line)
        .collect()
}

#[test]
fn version_block_matches_python_cli() {
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

    // A directory with no `.jss-lint.toml` above it would be ideal, but
    // the repo root has none either, so it doubles as the default case.
    let scratch = std::env::temp_dir().join("jsslint-version-parity");
    std::fs::create_dir_all(&scratch).expect("create scratch dir");
    std::fs::write(scratch.join(".jss-lint.toml"), "journal = \"nope\"\n")
        .expect("write scratch .jss-lint.toml");

    let cases: &[(&[&str], &Path)] = &[
        (&["--version"], root.as_path()),
        (&["--version", "--journal", "jss"], root.as_path()),
        (&["--version"], scratch.as_path()),
    ];

    let mut mismatches = Vec::new();
    for &(args, cwd) in cases {
        let expected = run(&jss_lint, args, cwd);
        let actual = run(jsslint_bin, args, cwd);

        assert_eq!(
            expected.stdout.lines().count(),
            4,
            "{args:?} in {}: the block must be four lines, got {:?}",
            cwd.display(),
            expected.stdout
        );
        if masked(&actual.stdout) != masked(&expected.stdout) {
            mismatches.push(format!(
                "{args:?} in {} STDOUT differs (line 2 masked)\n  expected:\n{}\n  actual:\n{}",
                cwd.display(),
                expected.stdout,
                actual.stdout
            ));
        }
        if actual.exit_code != expected.exit_code || actual.exit_code != Some(0) {
            mismatches.push(format!(
                "{args:?} EXIT CODE differs: expected {:?}, actual {:?}",
                expected.exit_code, actual.exit_code
            ));
        }
    }

    // The engine line differs by design: assert the divergence is exactly
    // that, so a future refactor cannot quietly make them equal-but-wrong.
    let py = run(&jss_lint, &["--version"], root.as_path());
    let rs = run(jsslint_bin, &["--version"], root.as_path());
    assert!(py
        .stdout
        .lines()
        .nth(1)
        .unwrap()
        .starts_with("engine: texlint/python "));
    assert!(rs
        .stdout
        .lines()
        .nth(1)
        .unwrap()
        .starts_with("engine: jsslint-core/rust "));

    assert!(
        mismatches.is_empty(),
        "{} mismatches:\n{}",
        mismatches.len(),
        mismatches.join("\n---\n")
    );
}
