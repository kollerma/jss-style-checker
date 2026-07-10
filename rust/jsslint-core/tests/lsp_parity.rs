//! Phase 4 differential harness for `jsslint_core::lsp`
//! (Violation/Fix -> LSP Diagnostic/CodeAction projections): calls the
//! real `texlint.lsp.conversions` functions via
//! `tools/dump_lsp_conversions.py` on synthetic violations and
//! compares against this port's output, serialized to the same JSON
//! shape.
//!
//! Skips entirely (doesn't fail) if the Python venv isn't set up.

use jsslint_core::lsp::{violation_to_code_action, violation_to_diagnostic};
use jsslint_core::report::{Fix, FixConfidence, Severity, Violation};
use serde_json::{json, Value};
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

fn violation(
    line: u32,
    column: Option<u32>,
    rule_id: &str,
    message: &str,
    fix: Option<Fix>,
) -> Violation {
    Violation {
        file: "m.tex".to_string(),
        line,
        column,
        rule_id: rule_id.to_string(),
        severity: Severity::Warning,
        message: message.to_string(),
        suggestion: None,
        fix,
    }
}

fn fix(start: usize, end: usize, replacement: &str, description: &str) -> Fix {
    Fix {
        start,
        end,
        replacement: replacement.to_string(),
        description: description.to_string(),
        confidence: FixConfidence::Safe,
    }
}

fn rust_output(v: &Violation, guide_url: Option<&str>, source: Option<&str>, uri: &str) -> Value {
    let d = violation_to_diagnostic(v, guide_url, source);
    let mut diagnostic = serde_json::Map::new();
    diagnostic.insert(
        "range".to_string(),
        json!({
            "start": {"line": d.range.start.line, "character": d.range.start.character},
            "end": {"line": d.range.end.line, "character": d.range.end.character},
        }),
    );
    diagnostic.insert("severity".to_string(), json!(d.severity));
    diagnostic.insert("code".to_string(), json!(d.code));
    diagnostic.insert("source".to_string(), json!(d.source));
    diagnostic.insert("message".to_string(), json!(d.message));
    if let Some(href) = &d.code_description_href {
        diagnostic.insert("codeDescription".to_string(), json!({"href": href}));
    }
    let diagnostic = Value::Object(diagnostic);
    let code_action = source.and_then(|src| violation_to_code_action(v, src, uri)).map(|ca| {
        json!({
            "title": ca.title,
            "kind": ca.kind,
            "edit": {"changes": {ca.uri: [{
                "range": {
                    "start": {"line": ca.edit.range.start.line, "character": ca.edit.range.start.character},
                    "end": {"line": ca.edit.range.end.line, "character": ca.edit.range.end.character},
                },
                "newText": ca.edit.new_text,
            }]}},
        })
    });
    json!({"diagnostic": diagnostic, "code_action": code_action})
}

fn python_oracle(python: &Path, input: &Value) -> Value {
    let mut child = Command::new(python)
        .arg("-m")
        .arg("tools.dump_lsp_conversions")
        .current_dir(repo_root())
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .expect("failed to spawn tools.dump_lsp_conversions");
    child
        .stdin
        .take()
        .unwrap()
        .write_all(input.to_string().as_bytes())
        .expect("failed to write input JSON to stdin");
    let output = child
        .wait_with_output()
        .expect("failed to wait on dump_lsp_conversions");
    assert!(
        output.status.success(),
        "dump_lsp_conversions failed: {}",
        String::from_utf8_lossy(&output.stderr)
    );
    serde_json::from_slice(&output.stdout).expect("oracle output must be valid JSON")
}

#[test]
fn lsp_conversions_match_python_oracle() {
    let root = repo_root();
    let python = root.join(".venv/bin/python");
    if !python.exists() {
        eprintln!(
            "SKIP: {} not found (Python venv not set up)",
            python.display()
        );
        return;
    }

    let source = "line one\nline two here\nfoo bar baz qux\n";
    let long_line_source = "\\proglang{Python} is great and \\pkg{numpy} too\nsecond line\n";

    let scenarios: Vec<(&str, Violation, Option<&str>, Option<&str>)> = vec![
        (
            "no-column-no-source",
            violation(3, None, "JSS-X-001", "no column, no source", None),
            None,
            None,
        ),
        (
            "with-column-no-source",
            violation(3, Some(5), "JSS-X-001", "with column, no source", None),
            None,
            None,
        ),
        (
            "with-column-and-source-mid-token",
            violation(3, Some(5), "JSS-X-001", "token span", None),
            Some(source),
            None,
        ),
        (
            "no-column-with-source",
            violation(2, None, "JSS-X-002", "whole line span", None),
            Some(source),
            None,
        ),
        (
            "column-past-eol",
            violation(1, Some(500), "JSS-X-003", "clamped column", None),
            Some(source),
            None,
        ),
        (
            "column-out-of-range-line",
            violation(50, Some(1), "JSS-X-004", "line beyond source", None),
            Some(source),
            None,
        ),
        (
            "column-on-whitespace",
            violation(2, Some(9), "JSS-X-005", "lands on a space", None),
            Some(source),
            None,
        ),
        (
            "with-guide-url",
            violation(1, Some(1), "JSS-X-006", "has guide url", None),
            Some(source),
            Some("https://example.com/guide#x"),
        ),
        (
            "with-fix-and-source",
            violation(
                1,
                Some(12),
                "JSS-MARKUP-001",
                "wrap in proglang",
                Some(fix(
                    0,
                    6,
                    "\\proglang{Python}",
                    "Wrap 'Python' in \\proglang{}",
                )),
            ),
            Some(long_line_source),
            None,
        ),
        (
            "with-fix-spanning-newline",
            violation(
                1,
                Some(1),
                "JSS-Y-001",
                "multi-line fix",
                Some(fix(5, 15, "REPLACED", "cross-line replace")),
            ),
            Some(long_line_source),
            None,
        ),
        (
            "fix-but-no-source",
            violation(
                1,
                Some(1),
                "JSS-Z-001",
                "fix present but no source given",
                Some(fix(0, 3, "X", "desc")),
            ),
            None,
            None,
        ),
    ];

    let mut mismatches = Vec::new();
    for (name, v, source, guide_url) in scenarios {
        let uri = "file:///m.tex";
        let input = json!({
            "violation": {
                "file": v.file,
                "line": v.line,
                "column": v.column,
                "rule_id": v.rule_id,
                "severity": "warning",
                "message": v.message,
                "suggestion": null,
                "fix": v.fix.as_ref().map(|f| json!({
                    "start": f.start, "end": f.end, "replacement": f.replacement,
                    "description": f.description, "confidence": "safe",
                })),
            },
            "source": source,
            "guide_url": guide_url,
            "uri": uri,
        });
        let expected = python_oracle(&python, &input);
        let actual = rust_output(&v, guide_url, source, uri);
        if actual != expected {
            mismatches.push(format!(
                "{name}\n  expected: {expected}\n  actual:   {actual}"
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
