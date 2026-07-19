//! Phase 4 end-to-end acceptance harness for `.jss-lint.toml` loading
//! (`jsslint_core::config::load`): writes a config file plus a fixture
//! `.tex` into an isolated scratch directory, runs the real `jss-lint`
//! and the compiled `jsslint` with that directory as cwd, and diffs
//! stdout/stderr/exit code. Every scenario's TOML sets `output =
//! "json"` itself (rather than passing `--output json` on the CLI) so
//! each case also exercises the TOML-sourced `output` field, not just
//! whichever field it's nominally testing — mirrors the scenario
//! breadth of `tests/unit/test_config.py` (defaults, file-overlay,
//! ignore_rules list/CSV, severity_overrides valid+dropped-invalid,
//! unknown-key warning gated on verbose, CLI-wins-over-file
//! precedence, empty-CLI-value clears a file value).
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

struct Outcome {
    stdout: String,
    stderr: String,
    exit_code: Option<i32>,
}

fn run(bin: &str, dir: &Path, args: &[&str]) -> Outcome {
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

/// Sets up `<scratch>/<name>-{py,rs}/` each with `before.tex` (the
/// `JSS-MARKUP-001` auto-fix fixture — reliably produces exactly one
/// violation, useful for ignore/severity-override scenarios) and the
/// given `.jss-lint.toml` body.
fn setup_scenario(name: &str, toml_body: &str) -> (PathBuf, PathBuf) {
    let fixture = repo_root().join("tests/fixtures/auto-fix/JSS-MARKUP-001/before.tex");
    let mut dirs = Vec::new();
    for side in ["py", "rs"] {
        let dir = scratch_base().join(format!("config-{name}-{side}"));
        let _ = fs::remove_dir_all(&dir);
        fs::create_dir_all(&dir).expect("failed to create scratch dir");
        fs::copy(&fixture, dir.join("before.tex")).expect("failed to copy fixture");
        fs::write(dir.join(".jss-lint.toml"), toml_body).expect("failed to write .jss-lint.toml");
        dirs.push(dir);
    }
    (dirs.remove(0), dirs.remove(0))
}

struct Scenario {
    name: &'static str,
    toml_body: &'static str,
    args: &'static [&'static str],
}

#[test]
fn config_load_matches_python_cli() {
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

    let scenarios = [
        Scenario {
            name: "overlay",
            toml_body: "output = \"json\"\nmode = \"reviewer\"\ncode_width = 100\n",
            args: &["before.tex"],
        },
        Scenario {
            name: "ignore-rules-list",
            toml_body: "output = \"json\"\nignore_rules = [\"JSS-MARKUP-001\"]\n",
            args: &["before.tex"],
        },
        Scenario {
            name: "severity-overrides",
            toml_body: concat!(
                "output = \"json\"\n",
                "[severity_overrides]\n",
                "\"JSS-MARKUP-001\" = \"error\"\n",
                "\"JSS-BOGUS-999\" = \"loud\"\n",
            ),
            args: &["before.tex"],
        },
        Scenario {
            name: "unknown-key-quiet",
            toml_body: "output = \"json\"\nfuture_key = \"future_value\"\n",
            args: &["before.tex"],
        },
        Scenario {
            name: "unknown-key-verbose",
            toml_body: "output = \"json\"\nfuture_key = \"future_value\"\n",
            args: &["--verbose", "before.tex"],
        },
        Scenario {
            name: "cli-ignore-rules-clears-file",
            toml_body: "output = \"json\"\nignore_rules = [\"JSS-MARKUP-001\"]\n",
            args: &["--ignore-rules", "", "before.tex"],
        },
        Scenario {
            name: "cli-min-confidence-wins",
            toml_body: "output = \"json\"\nmin_confidence = \"high\"\n",
            args: &["--min-confidence", "low", "before.tex"],
        },
        Scenario {
            name: "toml-min-confidence-alone",
            toml_body: "output = \"json\"\nmin_confidence = \"high\"\n",
            args: &["before.tex"],
        },
        Scenario {
            name: "toml-fail-on-error-exit-zero",
            toml_body: "output = \"json\"\nfail_on = \"error\"\n",
            args: &["before.tex"],
        },
        Scenario {
            name: "cli-output-wins-over-file",
            toml_body: "output = \"terminal\"\n",
            args: &["--output", "json", "before.tex"],
        },
        Scenario {
            name: "invalid-journal-in-toml",
            toml_body: "output = \"json\"\njournal = \"nature\"\n",
            args: &["before.tex"],
        },
        // Mixed-case CLI flag values: Python's click.Choice(...,
        // case_sensitive=False) accepts any case for --output/--mode/
        // --min-confidence/--fail-on; clap's `ignore_case = true` must
        // too, and (unlike Click, which normalizes the parsed value)
        // clap preserves the caller's casing, so `main.rs` lowercases
        // by hand before these ever reach `RawOverrides` — these
        // scenarios are the regression coverage for that.
        Scenario {
            name: "cli-output-mixed-case",
            toml_body: "",
            args: &["--output", "JSON", "before.tex"],
        },
        Scenario {
            name: "cli-mode-mixed-case",
            toml_body: "",
            args: &["--output", "html", "--mode", "AUTHOR", "before.tex"],
        },
        Scenario {
            name: "cli-min-confidence-mixed-case",
            toml_body: "output = \"json\"\nmin_confidence = \"high\"\n",
            args: &["--min-confidence", "LOW", "before.tex"],
        },
        Scenario {
            name: "cli-fail-on-mixed-case",
            toml_body: "output = \"json\"\n",
            args: &["--fail-on", "ERROR", "before.tex"],
        },
    ];

    let mut mismatches = Vec::new();
    for scenario in scenarios {
        let (py_dir, rs_dir) = setup_scenario(scenario.name, scenario.toml_body);
        let expected = run(&jss_lint, &py_dir, scenario.args);
        let actual = run(jsslint_bin, &rs_dir, scenario.args);

        // Spec 013 auto-resolve canonicalizes a bare single-file root
        // argument to an absolute path (`resolver.py`/`resolver.rs`
        // both call `.resolve()`/`canonicalize()` — contract C-12:
        // deterministic across hosts). `py_dir`/`rs_dir` are two
        // distinct scratch directories with different names by
        // construction (`setup_scenario`), so their absolute-path
        // prefixes never match even when the linted content is
        // identical; normalize both to a shared placeholder before
        // comparing so this scenario harness keeps working for scans
        // that resolve.
        let expected_stdout = expected
            .stdout
            .replace(&py_dir.display().to_string(), "<SCRATCH>");
        let actual_stdout = actual
            .stdout
            .replace(&rs_dir.display().to_string(), "<SCRATCH>");

        if actual_stdout != expected_stdout {
            mismatches.push(format!(
                "{} STDOUT differs\n  expected:\n{}\n  actual:\n{}",
                scenario.name, expected_stdout, actual_stdout
            ));
        }
        // `invalid-journal-in-toml`'s exact message lists every
        // registered journal; the dev venv has a `stub` test-fixture
        // journal installed (tests/fixtures/stub_journal) that this
        // single-journal ("jss"-only) port intentionally doesn't
        // replicate — so only the shared prefix is checked for that
        // one scenario, not byte-equality.
        if scenario.name == "invalid-journal-in-toml" {
            let prefix = "jss-lint: No journal registered under 'nature'. Known: [";
            if !expected.stderr.starts_with(prefix) || !actual.stderr.starts_with(prefix) {
                mismatches.push(format!(
                    "{} STDERR prefix differs\n  expected: {:?}\n  actual: {:?}",
                    scenario.name, expected.stderr, actual.stderr
                ));
            }
        } else if actual.stderr != expected.stderr {
            mismatches.push(format!(
                "{} STDERR differs\n  expected: {:?}\n  actual: {:?}",
                scenario.name, expected.stderr, actual.stderr
            ));
        }
        if actual.exit_code != expected.exit_code {
            mismatches.push(format!(
                "{} EXIT CODE differs: expected {:?}, actual {:?}",
                scenario.name, expected.exit_code, actual.exit_code
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
