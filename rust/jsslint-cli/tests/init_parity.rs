//! Phase 4 end-to-end acceptance harness for the `init` subcommand
//! (logic in `jsslint-cli`'s own `init` module — see its doc comment
//! for why the SQLite dependency isn't in `jsslint-core`): runs the
//! real `jss-lint init` and the compiled `jsslint init` in isolated
//! scratch directories seeded with real auto-fix fixtures, and diffs
//! stdout/stderr/exit code plus the written `.jss-lint.toml` bytes.
//! Both binaries run against *this repo's own*
//! `eval/precision-history.db` (found via the default repo-relative
//! candidate path, since the scratch dirs don't have their own DB),
//! which is what makes this a genuine test of the precision-DB
//! auto-suppression path, not just the DB-absent fallback.
//!
//! Covers: dry-run (single + multi-file directory, explicit file
//! target), write + refuse-without-force + `--force` overwrite, a
//! custom `--threshold`, an out-of-range `--threshold` (exit 2), and
//! an empty directory (no lintable files, exit 2). Skips entirely
//! (doesn't fail) if the Python venv isn't set up.

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

struct Outcome {
    stdout: String,
    stderr: String,
    exit_code: Option<i32>,
    toml_after: Option<String>,
}

fn run(bin: &str, dir: &PathBuf, args: &[&str]) -> Outcome {
    let output = Command::new(bin)
        .args(args)
        .current_dir(dir)
        .output()
        .unwrap_or_else(|e| panic!("failed to run {bin}: {e}"));
    let toml_after = fs::read_to_string(dir.join(".jss-lint.toml")).ok();
    Outcome {
        stdout: String::from_utf8_lossy(&output.stdout).into_owned(),
        stderr: String::from_utf8_lossy(&output.stderr).into_owned(),
        exit_code: output.status.code(),
        toml_after,
    }
}

struct Scenario {
    name: &'static str,
    files: &'static [(&'static str, &'static str)],
    args: &'static [&'static str],
}

fn setup(root: &Path, name: &str, side: &str, files: &[(&str, &str)]) -> PathBuf {
    let dir = scratch_base().join(format!("init-{name}-{side}"));
    let _ = fs::remove_dir_all(&dir);
    fs::create_dir_all(&dir).expect("failed to create scratch dir");
    for (dest_name, fixture_rel) in files {
        let src = root.join("tests/fixtures/auto-fix").join(fixture_rel);
        fs::copy(&src, dir.join(dest_name)).expect("failed to copy fixture");
    }
    dir
}

#[test]
fn init_matches_python_cli() {
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

    let scenarios: &[Scenario] = &[
        Scenario {
            name: "dry-run-single",
            files: &[("paper.tex", "JSS-MARKUP-001/before.tex")],
            args: &["init", "--dry-run"],
        },
        Scenario {
            name: "dry-run-multi",
            files: &[
                ("paper.tex", "JSS-MARKUP-001/before.tex"),
                ("refs.bib", "JSS-NAME-002/before.bib"),
            ],
            args: &["init", "--dry-run"],
        },
        Scenario {
            name: "dry-run-explicit-file",
            files: &[("paper.tex", "JSS-MARKUP-001/before.tex")],
            args: &["init", "paper.tex", "--dry-run"],
        },
        Scenario {
            name: "custom-threshold",
            files: &[("paper.tex", "JSS-MARKUP-001/before.tex")],
            args: &["init", "--dry-run", "--threshold", "0.5"],
        },
        Scenario {
            name: "invalid-threshold",
            files: &[("paper.tex", "JSS-MARKUP-001/before.tex")],
            args: &["init", "--dry-run", "--threshold", "1.5"],
        },
        Scenario {
            name: "empty-dir",
            files: &[],
            args: &["init", "--dry-run"],
        },
    ];

    let mut mismatches = Vec::new();
    for scenario in scenarios {
        let py_dir = setup(&root, scenario.name, "py", scenario.files);
        let rs_dir = setup(&root, scenario.name, "rs", scenario.files);
        let expected = run(&jss_lint, &py_dir, scenario.args);
        let actual = run(jsslint_bin, &rs_dir, scenario.args);
        compare(scenario.name, &expected, &actual, &mut mismatches);
    }

    // Write + refuse-without-force + --force, run sequentially against
    // the same pair of directories (state carries across sub-steps).
    {
        let py_dir = setup(
            &root,
            "write-sequence",
            "py",
            &[("paper.tex", "JSS-MARKUP-001/before.tex")],
        );
        let rs_dir = setup(
            &root,
            "write-sequence",
            "rs",
            &[("paper.tex", "JSS-MARKUP-001/before.tex")],
        );

        let expected = run(&jss_lint, &py_dir, &["init"]);
        let actual = run(jsslint_bin, &rs_dir, &["init"]);
        compare("write", &expected, &actual, &mut mismatches);

        let expected = run(&jss_lint, &py_dir, &["init"]);
        let actual = run(jsslint_bin, &rs_dir, &["init"]);
        compare("refuse-without-force", &expected, &actual, &mut mismatches);

        let expected = run(&jss_lint, &py_dir, &["init", "--force"]);
        let actual = run(jsslint_bin, &rs_dir, &["init", "--force"]);
        compare("force-overwrite", &expected, &actual, &mut mismatches);
    }

    assert!(
        mismatches.is_empty(),
        "{} mismatches:\n{}",
        mismatches.len(),
        mismatches.join("\n---\n")
    );
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
    if actual.toml_after != expected.toml_after {
        mismatches.push(format!(
            "{name} .jss-lint.toml differs\n  expected: {:?}\n  actual: {:?}",
            expected.toml_after, actual.toml_after
        ));
    }
}
