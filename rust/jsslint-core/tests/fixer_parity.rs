//! Phase 3 follow-up acceptance harness for `jsslint_core::fixer`:
//!
//! 1. `resolve_conflicts` is differentially checked against the
//!    Python oracle (`tools/dump_fix_resolution.py`, calling the real
//!    `_resolve_conflicts` directly) on a handful of synthetic
//!    overlap scenarios covering same-position confidence tie-break,
//!    partial-overlap cluster merging, and no-overlap pass-through —
//!    the real `auto-fix/JSS-*/` fixtures are all single-violation, so
//!    they never exercise clustering.
//! 2. `apply_to_text` is checked against every real `auto-fix/JSS-*/`
//!    fixture: run the fixture's own rule on `before.{tex,bib}`,
//!    resolve conflicts, apply, and compare byte-for-byte against
//!    `after.{tex,bib}`.
//!
//! Skips entirely (doesn't fail) if the Python venv isn't set up.

use jsslint_core::bib;
use jsslint_core::fixer::{candidates_from_violations, resolve_conflicts, Candidate};
use jsslint_core::report::{Fix, FixConfidence, Violation};
use jsslint_core::rules::{
    abbreviations, citations, code_style, crossrefs, house_style, markup, naming, operators,
    preamble, structure, typography,
};
use jsslint_core::tex;
use std::io::Write;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};

fn repo_root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .parent()
        .unwrap()
        .to_path_buf()
}

fn candidate(
    rule_id: &str,
    line: u32,
    start: usize,
    end: usize,
    replacement: &str,
    confidence: FixConfidence,
) -> Candidate {
    Candidate {
        file: "dummy.tex".to_string(),
        fix: Fix {
            start,
            end,
            replacement: replacement.to_string(),
            description: "test".to_string(),
            confidence,
        },
        rule_id: rule_id.to_string(),
        line,
    }
}

fn format_candidates(candidates: &[Candidate]) -> String {
    candidates
        .iter()
        .map(|c| {
            format!(
                "{}\t{}\t{}\t{}",
                c.rule_id, c.fix.start, c.fix.end, c.fix.replacement
            )
        })
        .collect::<Vec<_>>()
        .join("\n")
}

fn python_resolve_oracle(python: &Path, json: &str) -> String {
    let mut child = Command::new(python)
        .arg("-m")
        .arg("tools.dump_fix_resolution")
        .current_dir(repo_root())
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .expect("failed to spawn tools.dump_fix_resolution");
    child
        .stdin
        .take()
        .unwrap()
        .write_all(json.as_bytes())
        .expect("failed to write candidates JSON to stdin");
    let output = child
        .wait_with_output()
        .expect("failed to wait on dump_fix_resolution");
    assert!(
        output.status.success(),
        "dump_fix_resolution failed: {}",
        String::from_utf8_lossy(&output.stderr)
    );
    String::from_utf8(output.stdout).expect("oracle output must be valid UTF-8")
}

#[test]
fn resolve_conflicts_matches_python_oracle() {
    let root = repo_root();
    let python = root.join(".venv/bin/python");
    if !python.exists() {
        eprintln!(
            "SKIP: {} not found (Python venv not set up)",
            python.display()
        );
        return;
    }

    let scenarios: Vec<(&str, Vec<Candidate>)> = vec![
        (
            // Same-span tie: safe confidence, break by rule_id (A < B).
            r#"[
                {"rule_id":"JSS-B","line":1,"start":10,"end":15,"replacement":"X"},
                {"rule_id":"JSS-A","line":1,"start":10,"end":15,"replacement":"Y"},
                {"rule_id":"JSS-C","line":2,"start":20,"end":25,"replacement":"Z","confidence":"review"},
                {"rule_id":"JSS-D","line":2,"start":22,"end":30,"replacement":"W"},
                {"rule_id":"JSS-E","line":3,"start":50,"end":55,"replacement":"V"}
            ]"#,
            vec![
                candidate("JSS-B", 1, 10, 15, "X", FixConfidence::Safe),
                candidate("JSS-A", 1, 10, 15, "Y", FixConfidence::Safe),
                candidate("JSS-C", 2, 20, 25, "Z", FixConfidence::Review),
                candidate("JSS-D", 2, 22, 30, "W", FixConfidence::Safe),
                candidate("JSS-E", 3, 50, 55, "V", FixConfidence::Safe),
            ],
        ),
        (
            // Chained cluster merging: [0,5) + [3,10) + [9,12) all merge
            // into one cluster via max(cluster_end) even though the
            // first and third don't directly overlap.
            r#"[
                {"rule_id":"JSS-X","line":1,"start":0,"end":5,"replacement":"a"},
                {"rule_id":"JSS-Y","line":1,"start":3,"end":10,"replacement":"b"},
                {"rule_id":"JSS-Z","line":1,"start":9,"end":12,"replacement":"c"},
                {"rule_id":"JSS-W","line":2,"start":20,"end":21,"replacement":"d"}
            ]"#,
            vec![
                candidate("JSS-X", 1, 0, 5, "a", FixConfidence::Safe),
                candidate("JSS-Y", 1, 3, 10, "b", FixConfidence::Safe),
                candidate("JSS-Z", 1, 9, 12, "c", FixConfidence::Safe),
                candidate("JSS-W", 2, 20, 21, "d", FixConfidence::Safe),
            ],
        ),
        (
            // Zero-length (insertion) fixes at the same point.
            r#"[
                {"rule_id":"JSS-P","line":1,"start":5,"end":5,"replacement":"[1]"},
                {"rule_id":"JSS-Q","line":1,"start":5,"end":5,"replacement":"[2]"}
            ]"#,
            vec![
                candidate("JSS-P", 1, 5, 5, "[1]", FixConfidence::Safe),
                candidate("JSS-Q", 1, 5, 5, "[2]", FixConfidence::Safe),
            ],
        ),
    ];

    let mut mismatches = Vec::new();
    for (json, candidates) in scenarios {
        let expected = python_resolve_oracle(&python, json);
        let (applied, skipped) = resolve_conflicts(candidates);
        let actual = format!(
            "{}\n---\n{}\n",
            format_candidates(&applied),
            format_candidates(
                &skipped
                    .iter()
                    .map(|s| Candidate {
                        file: s.file.clone(),
                        fix: s.fix.clone(),
                        rule_id: s.rule_id.clone(),
                        line: 0,
                    })
                    .collect::<Vec<_>>()
            )
        );
        // Oracle prints a trailing blank line's worth of formatting
        // differently than our manual join; normalize both to the
        // same shape before comparing.
        let expected_norm = expected.trim_end().to_string() + "\n";
        let actual_norm = actual.trim_end().to_string() + "\n";
        if actual_norm != expected_norm {
            mismatches.push(format!(
                "scenario:\n{json}\n  expected:\n{expected_norm}  actual:\n{actual_norm}"
            ));
        }
    }

    assert!(
        mismatches.is_empty(),
        "{} scenario mismatches:\n{}",
        mismatches.len(),
        mismatches.join("\n---\n")
    );
}

fn tex_violations(dirname: &str, file: &str, parsed: &tex::ParsedTex) -> Vec<Violation> {
    match dirname {
        "JSS-ABBR-001" => abbreviations::check_abbr_001(file, parsed),
        "JSS-CITE-003" => citations::check_cite_003(file, parsed),
        "JSS-CODE-002" => code_style::check_code_002(file, parsed),
        "JSS-HOUSE-001" => house_style::check_house_001(file, parsed),
        "JSS-HOUSE-003" => house_style::check_house_003(file, parsed),
        "JSS-MARKUP-001" => markup::check_markup_001(file, parsed),
        "JSS-MARKUP-002" => markup::check_markup_002(file, parsed),
        "JSS-MARKUP-004" => markup::check_markup_004(file, parsed),
        "JSS-NAME-001" => naming::check_name_001(file, parsed),
        "JSS-OPER-001" => operators::check_oper_001(file, parsed),
        "JSS-PRE-003" => preamble::check_pre_003(file, parsed),
        "JSS-PRE-006" => preamble::check_pre_006(file, parsed),
        "JSS-PRE-007" => preamble::check_pre_007(file, parsed),
        "JSS-PRE-008" => preamble::check_pre_008(file, parsed),
        "JSS-STRUCT-002" => structure::check_struct_002(file, parsed),
        "JSS-STRUCT-005" => structure::check_struct_005(file, parsed),
        "JSS-STRUCT-006" => structure::check_struct_006(file, parsed),
        "JSS-TYPO-001" => typography::check_typo_001(file, parsed),
        "JSS-XREF-002" => crossrefs::check_xref_002(file, parsed),
        other => panic!("fixer_parity: no tex rule wired up for {other}"),
    }
}

fn bib_violations(
    dirname: &str,
    file: &str,
    source_chars: &[char],
    library: &bib::Library,
) -> Vec<Violation> {
    let empty: &[&[jsslint_core::tex::node::Node]] = &[];
    match dirname {
        "JSS-HOUSE-002" => house_style::check_house_002(file, source_chars, library, empty),
        "JSS-NAME-002" => naming::check_name_002(file, source_chars, library, empty),
        other => panic!("fixer_parity: no bib rule wired up for {other}"),
    }
}

#[test]
fn apply_to_text_matches_after_fixture() {
    let root = repo_root();
    let autofix_dir = root.join("tests/fixtures/auto-fix");
    let Ok(entries) = std::fs::read_dir(&autofix_dir) else {
        panic!("expected {} to exist", autofix_dir.display());
    };

    let mut dirs: Vec<PathBuf> = entries
        .flatten()
        .map(|e| e.path())
        .filter(|p| p.is_dir())
        .collect();
    dirs.sort();
    assert!(
        !dirs.is_empty(),
        "expected fixture directories under tests/fixtures/auto-fix/"
    );

    let mut mismatches = Vec::new();
    let mut checked = 0;
    for dir in &dirs {
        let dirname = dir.file_name().unwrap().to_string_lossy().to_string();
        let before_tex = dir.join("before.tex");
        let before_bib = dir.join("before.bib");

        let (before, after, violations): (String, String, Vec<Violation>) = if before_tex.exists() {
            let before = std::fs::read_to_string(&before_tex).unwrap();
            let after = std::fs::read_to_string(dir.join("after.tex")).unwrap();
            let file = before_tex.to_string_lossy().to_string();
            let parsed = tex::parse_tex_source(&before);
            let violations = tex_violations(&dirname, &file, &parsed);
            (before, after, violations)
        } else if before_bib.exists() {
            let before = std::fs::read_to_string(&before_bib).unwrap();
            let after = std::fs::read_to_string(dir.join("after.bib")).unwrap();
            let file = before_bib.to_string_lossy().to_string();
            let source_chars: Vec<char> = before.chars().collect();
            let library = bib::parse(&before);
            let violations = bib_violations(&dirname, &file, &source_chars, &library);
            (before, after, violations)
        } else {
            continue;
        };

        checked += 1;
        let candidates = candidates_from_violations(&violations);
        let (applied, _skipped) = resolve_conflicts(candidates);
        let before_chars: Vec<char> = before.chars().collect();
        let actual = jsslint_core::fixer::apply_to_text(&before_chars, &applied);
        if actual != after {
            mismatches.push(format!(
                "{dirname}\n  expected:\n{after}\n  actual:\n{actual}"
            ));
        }
    }

    assert!(
        checked > 0,
        "expected to check at least one auto-fix fixture"
    );
    assert!(
        mismatches.is_empty(),
        "{} fixture mismatches:\n{}",
        mismatches.len(),
        mismatches.join("\n---\n")
    );
}
