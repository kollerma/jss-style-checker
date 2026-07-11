//! Differential parity harness (plan Phase 0 / Phase 5 scope): asserts
//! the Rust JSON renderer produces byte-identical output to
//! `jss-lint --output json` for the same input.
//!
//! Phase 0 scope only covers the "compliant" no-violations case (see
//! the plan's Phase 0 description) — there is no tokenizer or rule
//! engine yet, so the Rust side of this test hand-builds the
//! `ComplianceReport` that the real engine is known (from the Python
//! reference run below) to produce for
//! `tests/fixtures/compliant/minimal.tex`. Once the engine exists
//! (Phase 1-3), this hardcoded report should be replaced by an actual
//! `jsslint_core::run(...)` call over the same fixture path.
//!
//! Skips (rather than fails) if the Python `jss-lint` CLI isn't on the
//! expected venv path, so `cargo test` still works in environments
//! without the Python toolchain set up.

use jsslint_core::report::{
    CategoryStatus, CategorySummary, ComplianceReport, Severity, Violation,
};
use std::path::PathBuf;
use std::process::Command;

fn repo_root() -> PathBuf {
    // rust/jsslint-core -> repo root is two levels up.
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .parent()
        .unwrap()
        .to_path_buf()
}

fn python_jss_lint_reference(fixture: &str) -> Option<String> {
    let bin = repo_root().join(".venv/bin/jss-lint");
    if !bin.exists() {
        eprintln!("SKIP: {} not found (Python venv not set up)", bin.display());
        return None;
    }
    let output = Command::new(bin)
        .arg("--output")
        .arg("json")
        .arg(fixture)
        .current_dir(repo_root())
        .output()
        .expect("failed to run jss-lint");
    // Exit codes per texlint.cli: 0 clean, 1 violations found, 2
    // parse-or-usage error. Only 2+ is a real failure here.
    let code = output.status.code().unwrap_or(-1);
    assert!(
        code == 0 || code == 1,
        "jss-lint exited with {code:?}: {}",
        String::from_utf8_lossy(&output.stderr)
    );
    Some(String::from_utf8(output.stdout).expect("jss-lint output must be valid UTF-8"))
}

/// The 15-category, journal-declared (ROLLOUT_ORDER) list every fixture
/// in this file produces, each `(rules_applied, rules_passed)` pair
/// overridable per test. Hardcoded from real reference runs — see
/// module docs.
fn base_categories(overrides: &[(&str, u32)]) -> Vec<CategorySummary> {
    let cats: &[(&str, &str, u32)] = &[
        ("preamble", "Preamble", 8),
        ("structure", "Structure", 6),
        ("markup", "Markup", 4),
        ("citations", "Citations", 3),
        ("references", "References", 6),
        ("bibtex", "BibTeX", 5),
        ("naming", "Naming", 2),
        ("capitalization", "Capitalization", 3),
        ("typography", "Typography", 4),
        ("abbreviations", "Abbreviations", 1),
        ("code_style", "Code style", 3),
        ("code_width", "Code width", 1),
        ("operators", "Operators", 4),
        ("crossrefs", "Cross-references", 7),
        ("house_style", "House style", 3),
    ];
    cats.iter()
        .map(|(id, title, applied)| {
            let passed = overrides
                .iter()
                .find(|(oid, _)| oid == id)
                .map(|(_, p)| *p)
                .unwrap_or(*applied);
            let status = if passed < *applied {
                CategoryStatus::Fail
            } else {
                CategoryStatus::Pass
            };
            CategorySummary {
                category_id: id.to_string(),
                title: title.to_string(),
                status,
                rules_applied: *applied,
                rules_passed: passed,
                violations: Vec::new(),
            }
        })
        .collect()
}

#[test]
fn compliant_minimal_tex_matches_python_byte_for_byte() {
    let Some(expected) = python_jss_lint_reference("tests/fixtures/compliant/minimal.tex") else {
        return; // Python venv unavailable — see skip message above.
    };
    let report = ComplianceReport {
        tool_version: "0.1.0".to_string(),
        journal_id: "jss".to_string(),
        violations: Vec::new(),
        categories: base_categories(&[]),
        compliance_percentage: Some(100.0),
        skipped_rules: Vec::new(),
    };
    let actual = jsslint_core::json_output::render(&report);
    assert_eq!(
        actual, expected,
        "Rust JSON output must be byte-identical to `jss-lint --output json`"
    );
}

/// Exercises the code path `compliant_minimal_tex...` above cannot: a
/// real violation, whose `guide_section` metadata (pulled from the
/// build.rs-generated catalogue) contains "§" (U+00A7) — non-ASCII text
/// that fires on nearly every real violation, not an edge case. Proves
/// `write_py_string`'s `\uXXXX` escaping (matching Python's
/// `ensure_ascii=True` default) actually engages, and that catalogue
/// lookup + non-100% `compliance_percentage` formatting match too.
#[test]
fn single_violation_matches_python_byte_for_byte_incl_unicode_escaping() {
    let fixture = "tests/fixtures/violations/preamble/JSS-PRE-001-bad.tex";
    let Some(expected) = python_jss_lint_reference(fixture) else {
        return;
    };
    let report = ComplianceReport {
        tool_version: "0.1.0".to_string(),
        journal_id: "jss".to_string(),
        violations: vec![Violation {
            file: fixture.to_string(),
            line: 1,
            column: Some(1),
            rule_id: "JSS-PRE-001".to_string(),
            severity: Severity::Error,
            message: "Document class must be jss with a valid class option (article, codesnippet, bookreview, softwarereview)".to_string(),
            suggestion: Some(
                "Use \\documentclass[article]{jss} (or codesnippet / bookreview / softwarereview).".to_string(),
            ),
            fix: None,
        }],
        categories: base_categories(&[("preamble", 7)]),
        compliance_percentage: Some(93.3),
        skipped_rules: Vec::new(),
    };
    let actual = jsslint_core::json_output::render(&report);
    assert_eq!(
        actual, expected,
        "Rust JSON output must be byte-identical to `jss-lint --output json`, including \\uXXXX-escaped guide_section"
    );
}
