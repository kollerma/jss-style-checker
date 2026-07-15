//! Phase 3 rule acceptance harness: for every `.tex` fixture and each
//! implemented tex rule, the Rust rule function's violations must
//! match the Python oracle's (`tools/dump_tex_violations.py`, calling
//! the real rule function directly — same rationale as
//! `tests/bib_rules_parity.rs`).
//!
//! Skips entirely (doesn't fail) if the Python venv isn't set up.

use jsslint_core::report::Violation;
use jsslint_core::rules::{
    abbreviations, capitalization, citations, code_style, code_width, crossrefs, house_style,
    markup, naming, operators, preamble, structure, typography,
};
use jsslint_core::tex;
use std::collections::HashMap;
use std::path::{Path, PathBuf};
use std::process::Command;

const RULE_IDS: &[&str] = &[
    "JSS-WIDTH-001",
    "JSS-CODE-001",
    "JSS-CODE-002",
    "JSS-CODE-003",
    "JSS-ABBR-001",
    "JSS-TYPO-001",
    "JSS-TYPO-002",
    "JSS-TYPO-003",
    "JSS-TYPO-004",
    "JSS-CAP-001",
    "JSS-CAP-002",
    "JSS-CAP-004",
    "JSS-STRUCT-001",
    "JSS-STRUCT-002",
    "JSS-STRUCT-003",
    "JSS-STRUCT-004",
    "JSS-STRUCT-005",
    "JSS-STRUCT-006",
    "JSS-OPER-001",
    "JSS-OPER-002",
    "JSS-OPER-003",
    "JSS-OPER-004",
    "JSS-HOUSE-001",
    "JSS-HOUSE-003",
    "JSS-NAME-001",
    "JSS-PRE-001",
    "JSS-PRE-002",
    "JSS-PRE-003",
    "JSS-PRE-004",
    "JSS-PRE-005",
    "JSS-PRE-006",
    "JSS-PRE-007",
    "JSS-PRE-008",
    "JSS-CITE-002",
    "JSS-CITE-003",
    "JSS-CITE-004",
    "JSS-MARKUP-001",
    "JSS-MARKUP-002",
    "JSS-MARKUP-003",
    "JSS-MARKUP-004",
    "JSS-XREF-001",
    "JSS-XREF-002",
    "JSS-XREF-003",
    "JSS-XREF-004",
    "JSS-XREF-005",
    "JSS-XREF-006",
    "JSS-XREF-007",
];

fn repo_root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .parent()
        .unwrap()
        .to_path_buf()
}

fn find_tex_fixtures(dir: &Path, out: &mut Vec<PathBuf>) {
    let Ok(entries) = std::fs::read_dir(dir) else {
        return;
    };
    for entry in entries.flatten() {
        let path = entry.path();
        if path.is_dir() {
            find_tex_fixtures(&path, out);
        } else if path
            .extension()
            .is_some_and(|e| e.eq_ignore_ascii_case("tex"))
        {
            out.push(path);
        }
    }
}

/// Dumps every rule's violations for `fixture` via a single subprocess call
/// (`--all`), parsing the file only once on the Python side, at ~1/46th the
/// subprocess+reparse cost of dumping one rule at a time.
///
/// Frames are delimited by `\x00<rule_id>\x00<blob>` rather than split by
/// newline: a violation's `fix.replacement` can itself contain embedded
/// newlines (e.g. an inserted line of LaTeX), which line-based re-grouping
/// would silently misfile onto the wrong rule. NUL can't appear in real
/// LaTeX source, so it's safe as a frame delimiter. Must match
/// `tools/dump_tex_violations.py`'s `_RULE_SENTINEL`.
fn python_oracle_dump_all(python: &Path, fixture: &Path) -> HashMap<String, String> {
    let output = Command::new(python)
        .arg("-m")
        .arg("tools.dump_tex_violations")
        .arg("--all")
        .arg(fixture)
        .current_dir(repo_root())
        .output()
        .expect("failed to run tools.dump_tex_violations --all");
    assert!(
        output.status.success(),
        "dump_tex_violations --all failed on {}: {}",
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
    loop {
        let Some(rule_id) = parts.next() else { break };
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
    let parsed = tex::parse_tex_source(source);
    match rule_id {
        "JSS-WIDTH-001" => code_width::check_width_001(&file, &parsed, 80),
        "JSS-CODE-001" => code_style::check_code_001(&file, &parsed),
        "JSS-CODE-002" => code_style::check_code_002(&file, &parsed),
        "JSS-CODE-003" => code_style::check_code_003(&file, &parsed),
        "JSS-ABBR-001" => abbreviations::check_abbr_001(&file, &parsed),
        "JSS-TYPO-001" => typography::check_typo_001(&file, &parsed),
        "JSS-TYPO-002" => typography::check_typo_002(&file, &parsed),
        "JSS-TYPO-003" => typography::check_typo_003(&file, &parsed),
        "JSS-TYPO-004" => typography::check_typo_004(&file, &parsed),
        "JSS-CAP-001" => capitalization::check_cap_001(&file, &parsed),
        "JSS-CAP-002" => capitalization::check_cap_002(&file, &parsed),
        "JSS-CAP-004" => capitalization::check_cap_004(&file, &parsed),
        "JSS-STRUCT-001" => structure::check_struct_001(&file, &parsed),
        "JSS-STRUCT-002" => structure::check_struct_002(&file, &parsed),
        "JSS-STRUCT-003" => structure::check_struct_003(&file, &parsed),
        "JSS-STRUCT-004" => structure::check_struct_004(&file, &parsed),
        "JSS-STRUCT-005" => structure::check_struct_005(&file, &parsed),
        "JSS-STRUCT-006" => structure::check_struct_006(&file, &parsed),
        "JSS-OPER-001" => operators::check_oper_001(&file, &parsed),
        "JSS-OPER-002" => operators::check_oper_002(&file, &parsed),
        "JSS-OPER-003" => operators::check_oper_003(&file, &parsed),
        "JSS-OPER-004" => operators::check_oper_004(&file, &parsed),
        "JSS-HOUSE-001" => house_style::check_house_001(&file, &parsed),
        "JSS-HOUSE-003" => house_style::check_house_003(&file, &parsed),
        "JSS-NAME-001" => naming::check_name_001(&file, &parsed),
        "JSS-PRE-001" => preamble::check_pre_001(&file, &parsed),
        "JSS-PRE-002" => preamble::check_pre_002(&file, &parsed),
        "JSS-PRE-003" => preamble::check_pre_003(&file, &parsed),
        "JSS-PRE-004" => preamble::check_pre_004(&file, &parsed),
        "JSS-PRE-005" => preamble::check_pre_005(&file, &parsed),
        "JSS-PRE-006" => preamble::check_pre_006(&file, &parsed),
        "JSS-PRE-007" => preamble::check_pre_007(&file, &parsed),
        "JSS-PRE-008" => preamble::check_pre_008(&file, &parsed),
        "JSS-CITE-002" => citations::check_cite_002(&file, &parsed),
        "JSS-CITE-003" => citations::check_cite_003(&file, &parsed),
        "JSS-CITE-004" => citations::check_cite_004(&file, &parsed),
        "JSS-MARKUP-001" => markup::check_markup_001(&file, &parsed),
        "JSS-MARKUP-002" => markup::check_markup_002(&file, &parsed),
        "JSS-MARKUP-003" => markup::check_markup_003(&file, &parsed),
        "JSS-MARKUP-004" => markup::check_markup_004(&file, &parsed),
        "JSS-XREF-001" => crossrefs::check_xref_001(&file, &parsed),
        "JSS-XREF-002" => crossrefs::check_xref_002(&file, &parsed),
        "JSS-XREF-003" => crossrefs::check_xref_003(&file, &parsed),
        "JSS-XREF-004" => crossrefs::check_xref_004(&file, &parsed),
        "JSS-XREF-005" => crossrefs::check_xref_005(&file, &parsed),
        "JSS-XREF-006" => crossrefs::check_xref_006(&file, &parsed),
        "JSS-XREF-007" => crossrefs::check_xref_007(&file, &parsed),
        other => panic!("no Rust rule wired up for {other}"),
    }
}

#[test]
fn all_tex_rules_match_python_oracle() {
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
    find_tex_fixtures(&root.join("tests/fixtures"), &mut fixtures);
    fixtures.sort();
    assert!(
        !fixtures.is_empty(),
        "expected to find .tex fixtures under tests/fixtures/"
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
