//! Phase 2 rule acceptance harness: for every `.bib` fixture and each
//! implemented bib rule, the Rust rule function's violations must
//! match the Python oracle's (`tools/dump_bib_violations.py`, which
//! calls the real rule check function directly — bypassing the JSON
//! renderer's `fix: null` hardcoding — so `Fix` payloads are verified
//! too, not just message/line/column).
//!
//! Skips entirely (doesn't fail) if the Python venv isn't set up.

use jsslint_core::bib;
use jsslint_core::report::Violation;
use jsslint_core::rules::{bibtex, house_style, naming};
use std::path::{Path, PathBuf};
use std::process::Command;

const RULE_IDS: &[&str] = &[
    "JSS-BIBTEX-001",
    "JSS-BIBTEX-002",
    "JSS-BIBTEX-003",
    "JSS-BIBTEX-004",
    "JSS-BIBTEX-005",
    "JSS-NAME-002",
    "JSS-HOUSE-002",
];

fn repo_root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .parent()
        .unwrap()
        .to_path_buf()
}

fn find_bib_fixtures(dir: &Path, out: &mut Vec<PathBuf>) {
    let Ok(entries) = std::fs::read_dir(dir) else {
        return;
    };
    for entry in entries.flatten() {
        let path = entry.path();
        if path.is_dir() {
            find_bib_fixtures(&path, out);
        } else if path
            .extension()
            .is_some_and(|e| e.eq_ignore_ascii_case("bib"))
        {
            out.push(path);
        }
    }
}

fn python_oracle_dump(python: &Path, rule_id: &str, fixture: &Path) -> String {
    let output = Command::new(python)
        .arg("-m")
        .arg("tools.dump_bib_violations")
        .arg(rule_id)
        .arg(fixture)
        .current_dir(repo_root())
        .output()
        .expect("failed to run tools.dump_bib_violations");
    assert!(
        output.status.success(),
        "dump_bib_violations failed on {rule_id} {}: {}",
        fixture.display(),
        String::from_utf8_lossy(&output.stderr)
    );
    String::from_utf8(output.stdout).expect("oracle output must be valid UTF-8")
}

fn format_violation(v: &Violation) -> String {
    let column = v
        .column
        .map(|c| c.to_string())
        .unwrap_or_else(|| "None".to_string());
    let suggestion = v.suggestion.clone().unwrap_or_else(|| "None".to_string());
    let fix = match &v.fix {
        Some(f) => format!("{}:{}:{}", f.start, f.end, f.replacement),
        None => "-".to_string(),
    };
    format!(
        "{}\t{}\t{column}\t{}\t{suggestion}\t{fix}",
        v.rule_id, v.line, v.message
    )
}

fn rust_violations(rule_id: &str, fixture: &Path, source: &str) -> Vec<Violation> {
    let file = fixture.to_string_lossy().to_string();
    let chars: Vec<char> = source.chars().collect();
    let library = bib::parse(source);
    let empty: &[&[jsslint_core::tex::node::Node]] = &[];
    match rule_id {
        "JSS-BIBTEX-001" => bibtex::check_bibtex_001(&file, &library, empty),
        "JSS-BIBTEX-002" => bibtex::check_bibtex_002(&file, &library),
        "JSS-BIBTEX-003" => bibtex::check_bibtex_003(&file, &library, empty),
        "JSS-BIBTEX-004" => bibtex::check_bibtex_004(&file, &file, &library, empty, |_| (0, 0)),
        "JSS-BIBTEX-005" => bibtex::check_bibtex_005(&file, &library),
        "JSS-NAME-002" => naming::check_name_002(&file, &chars, &library, empty),
        "JSS-HOUSE-002" => house_style::check_house_002(&file, &chars, &library, empty),
        other => panic!("no Rust rule wired up for {other}"),
    }
}

#[test]
fn all_bib_rules_match_python_oracle() {
    let root = repo_root();
    let python = root.join(".venv/bin/python");
    if !python.exists() {
        eprintln!(
            "SKIP: {} not found (Python venv not set up)",
            python.display()
        );
        return;
    }

    let mut fixtures = Vec::new();
    find_bib_fixtures(&root.join("tests/fixtures"), &mut fixtures);
    fixtures.sort();
    assert!(
        !fixtures.is_empty(),
        "expected to find .bib fixtures under tests/fixtures/"
    );

    let mut mismatches = Vec::new();
    for fixture in &fixtures {
        let relative = fixture
            .strip_prefix(&root)
            .unwrap()
            .to_string_lossy()
            .replace('\\', "/");
        let source = std::fs::read_to_string(fixture)
            .unwrap_or_else(|e| panic!("failed to read {}: {e}", fixture.display()));
        for &rule_id in RULE_IDS {
            let expected = python_oracle_dump(&python, rule_id, fixture);
            let mut actual_violations = rust_violations(rule_id, fixture, &source);
            actual_violations.sort_by(|a, b| {
                (a.line, a.column.unwrap_or(0), a.rule_id.as_str()).cmp(&(
                    b.line,
                    b.column.unwrap_or(0),
                    b.rule_id.as_str(),
                ))
            });
            let actual = actual_violations
                .iter()
                .map(format_violation)
                .collect::<Vec<_>>()
                .join("\n")
                + if actual_violations.is_empty() {
                    ""
                } else {
                    "\n"
                };
            if actual != expected {
                mismatches.push(format!(
                    "{relative} [{rule_id}]\n  expected:\n{expected}\n  actual:\n{actual}"
                ));
            }
        }
    }

    assert!(
        mismatches.is_empty(),
        "{} (fixture, rule) mismatches:\n{}",
        mismatches.len(),
        mismatches.join("\n---\n")
    );
}
