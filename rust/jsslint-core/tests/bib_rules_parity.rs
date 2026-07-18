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
use jsslint_core::rules::{bibtex, house_style, naming, references};
use std::collections::HashMap;
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
    "JSS-REFS-001",
    "JSS-REFS-003",
    "JSS-REFS-004",
    "JSS-REFS-005",
    "JSS-REFS-006",
    "JSS-REFS-007",
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

/// Dumps every rule's violations for `fixture` via a single subprocess call
/// (`--all`), parsing the file only once on the Python side, at ~1/26th the
/// subprocess+reparse cost of dumping one rule at a time.
///
/// Frames are delimited by `\x00<rule_id>\x00<blob>` rather than split by
/// newline: a violation's `fix.replacement` can itself contain embedded
/// newlines, which line-based re-grouping would silently misfile onto the
/// wrong rule. NUL can't appear in real BibTeX source, so it's safe as a
/// frame delimiter. Must match `tools/dump_bib_violations.py`'s
/// `_RULE_SENTINEL`.
fn python_oracle_dump_all(python: &Path, fixture: &Path) -> HashMap<String, String> {
    let output = Command::new(python)
        .arg("-m")
        .arg("tools.dump_bib_violations")
        .arg("--all")
        .arg(fixture)
        .current_dir(repo_root())
        .output()
        .expect("failed to run tools.dump_bib_violations --all");
    assert!(
        output.status.success(),
        "dump_bib_violations --all failed on {}: {}",
        fixture.display(),
        String::from_utf8_lossy(&output.stderr)
    );
    let text = String::from_utf8(output.stdout).expect("oracle output must be valid UTF-8");

    let mut parts = text.split('\x00');
    assert_eq!(
        parts.next(),
        Some(""),
        "expected output to start with the \\x00 sentinel"
    );
    let mut by_rule: HashMap<String, String> = HashMap::new();
    while let Some(rule_id) = parts.next() {
        let blob = parts
            .next()
            .unwrap_or_else(|| panic!("sentinel for {rule_id} missing its blob"));
        by_rule.insert(rule_id.to_string(), blob.to_string());
    }
    by_rule
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
        "JSS-BIBTEX-004" => bibtex::check_bibtex_004(&file, &[], &library, empty),
        "JSS-BIBTEX-005" => bibtex::check_bibtex_005(&file, &library),
        "JSS-NAME-002" => naming::check_name_002(&file, &chars, &library, empty),
        "JSS-HOUSE-002" => house_style::check_house_002(&file, &chars, &library, empty),
        "JSS-REFS-001" => references::check_refs_001(&file, &library, empty),
        "JSS-REFS-003" => references::check_refs_003(&file, &chars, &library, empty, None),
        "JSS-REFS-004" => references::check_refs_004(&file, &library, empty),
        "JSS-REFS-005" => references::check_refs_005(&file, &library, empty),
        "JSS-REFS-006" => references::check_refs_006(&file, &library, empty),
        "JSS-REFS-007" => references::check_refs_007(&file, &library, empty),
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
        let oracle = python_oracle_dump_all(&python, fixture);
        for &rule_id in RULE_IDS {
            let expected = oracle.get(rule_id).cloned().unwrap_or_default();
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
