//! Inline-suppression parity (spec 027 item B, FR-B-007).
//!
//! Until 1.2.0 this engine ignored `% jss-lint: ignore` entirely, so
//! every surface built on it — `jsslint`, the web app, VS Code, the
//! PyO3 wheel, the R package — reported findings their author had
//! explicitly signed off on, while `jss-lint` hid them. This harness
//! runs both engines over one fixture per behaviour of the directive
//! grammar and compares the rendered JSON byte for byte.
//!
//! The fixtures are checked in (no corpus dependency); the suite skips
//! only when the Python venv is missing.

use jsslint_core::config::ToolConfig;
use jsslint_core::engine::{self, ParsedDocument};
use jsslint_core::json_output;
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

/// One fixture per directive behaviour:
///
/// - `inline.tex` — a directive on a content line silences that line
///   only, both with and without an explicit rule id.
/// - `scoped.tex` — a comment-only directive also targets the *next*
///   line, is rule-scoped (a second rule on the same line survives),
///   tolerates a `%%` banner, lowercase ids, and free-text rationale.
/// - `verbatim.tex` — a `%` inside a code environment is not a TeX
///   comment, so the directive is inert.
/// - `escaped.tex` — `\%` does not introduce a comment either.
/// - `entries.bib` — a directive above a BibTeX entry silences findings
///   reported on the entry's first line.
/// - `chunks.Rnw` — directives around a Sweave chunk keep
///   file-authoritative line numbers.
/// - `prose.Rmd` — the case that was broken in *both* engines: a prose
///   block that does not start at line 1, whose fragment-relative
///   source has to be mapped back through `line_offset`.
const FIXTURES: &[&str] = &[
    "tests/fixtures/suppress/inline.tex",
    "tests/fixtures/suppress/scoped.tex",
    "tests/fixtures/suppress/verbatim.tex",
    "tests/fixtures/suppress/escaped.tex",
    "tests/fixtures/suppress/entries.bib",
    "tests/fixtures/suppress/chunks.Rnw",
    "tests/fixtures/suppress/prose.Rmd",
];

fn python_oracle_json(jss_lint: &Path, root: &Path, fixture: &str) -> String {
    let output = Command::new(jss_lint)
        .arg("--no-resolve")
        .arg("--output")
        .arg("json")
        .arg(fixture)
        .current_dir(root)
        .output()
        .expect("failed to run jss-lint");
    assert!(
        !output.stdout.is_empty(),
        "jss-lint produced no stdout (exit {:?}): {}",
        output.status.code(),
        String::from_utf8_lossy(&output.stderr)
    );
    String::from_utf8(output.stdout).expect("oracle output must be valid UTF-8")
}

#[test]
fn inline_suppression_matches_python_cli_json() {
    let root = repo_root();
    let jss_lint = root.join(".venv/bin/jss-lint");
    if !jss_lint.exists() {
        eprintln!(
            "SKIP: {} not found (Python venv not set up)",
            jss_lint.display()
        );
        return;
    }

    let mut mismatches = Vec::new();
    for fixture in FIXTURES {
        let contents =
            std::fs::read_to_string(root.join(fixture)).expect("fixture must be readable");
        let document = ParsedDocument::from_sources(&[(fixture.to_string(), contents)])
            .expect("fixture suffix must be supported");
        let actual = json_output::render(&engine::run(&ToolConfig::default(), &document));
        let expected = python_oracle_json(&jss_lint, &root, fixture);
        if actual != expected {
            mismatches.push(format!(
                "{fixture} differs\n  expected:\n{expected}\n  actual:\n{actual}"
            ));
        }
    }
    assert!(
        mismatches.is_empty(),
        "{} fixture(s) diverge:\n{}",
        mismatches.len(),
        mismatches.join("\n---\n")
    );
}

/// The directives must actually *do* something: a suite that silently
/// stopped suppressing would otherwise still pass the byte comparison
/// above the day both engines regress together.
#[test]
fn directives_actually_suppress_something() {
    let root = repo_root();
    let fixture = "tests/fixtures/suppress/inline.tex";
    let contents = std::fs::read_to_string(root.join(fixture)).expect("fixture readable");

    let document = ParsedDocument::from_sources(&[(fixture.to_string(), contents.clone())])
        .expect("supported suffix");
    let with_directives = engine::run(&ToolConfig::default(), &document)
        .violations
        .len();

    let stripped: String = contents
        .lines()
        .map(|line| match line.find("% jss-lint:") {
            Some(idx) => line[..idx].to_string(),
            None => line.to_string(),
        })
        .collect::<Vec<_>>()
        .join("\n");
    let document =
        ParsedDocument::from_sources(&[(fixture.to_string(), stripped)]).expect("supported suffix");
    let without_directives = engine::run(&ToolConfig::default(), &document)
        .violations
        .len();

    assert!(
        without_directives > with_directives,
        "removing the directives changed nothing ({without_directives} vs \
         {with_directives} findings) — inline suppression is not being applied"
    );
}
