//! Deterministic JSON renderer — mirrors
//! `/workspace/src/texlint/output/json_output.py` byte-for-byte,
//! including two of its quirks (both intentional to preserve parity,
//! not oversights):
//!
//! 1. `fix` is hardcoded to `null`. The Python renderer's docstring
//!    still says "reserved for Step 4" even though spec 008 (auto-fix)
//!    shipped — the JSON contract was never updated to emit real `Fix`
//!    payloads. If that Python gap is ever closed, this must change in
//!    lockstep (the parity harness in `tests/parity.rs` will catch a
//!    drift either way).
//! 2. Python's `json.dumps(..., indent=2, sort_keys=True)` uses the
//!    default `ensure_ascii=True`, which escapes every non-ASCII
//!    codepoint to `\uXXXX` — e.g. every `guide_section` value contains
//!    "§", so this fires on essentially every real violation, not just
//!    edge-case input. `serde_json`'s built-in pretty-printer does NOT
//!    do this, so we can't use it directly; `write_value` below is a
//!    small hand-rolled formatter that replicates CPython's C-accelerated
//!    JSON encoder output exactly.

use crate::catalogue;
use crate::report::{CategorySummary, ComplianceReport, Violation};
use serde_json::{json, Map, Value};

/// Builds the same payload shape as `json_output.py::to_payload`.
pub fn to_payload(report: &ComplianceReport) -> Value {
    let mut sorted = report.violations.clone();
    crate::report::sort_violations(&mut sorted);

    let violations: Vec<Value> = sorted.iter().map(violation_value).collect();
    let categories: Vec<Value> = report.categories.iter().map(category_value).collect();
    let skipped_rules: Vec<Value> = report
        .skipped_rules
        .iter()
        .map(|s| json!({"rule_id": s.rule_id, "reason": s.reason}))
        .collect();

    json!({
        "tool_version": report.tool_version,
        "journal_id": report.journal_id,
        "compliance_percentage": report.compliance_percentage,
        "categories": categories,
        "violations": violations,
        "skipped_rules": skipped_rules,
    })
}

fn violation_value(v: &Violation) -> Value {
    let meta = catalogue::lookup(&v.rule_id);
    let guide_section = meta.map(|m| m.guide_section).unwrap_or("");
    let guide_url = meta.and_then(|m| m.guide_url);
    let confidence = meta.map(|m| m.confidence).unwrap_or("high");

    json!({
        "file": v.file,
        "line": v.line,
        "column": v.column,
        "rule_id": v.rule_id,
        "severity": v.severity.as_str(),
        "message": v.message,
        "suggestion": v.suggestion,
        "fix": Value::Null,
        "guide_section": guide_section,
        "guide_url": guide_url,
        "confidence": confidence,
    })
}

fn category_value(c: &CategorySummary) -> Value {
    json!({
        "category_id": c.category_id,
        "title": c.title,
        "status": c.status.as_str(),
        "rules_applied": c.rules_applied,
        "rules_passed": c.rules_passed,
    })
}

/// Render a `ComplianceReport` exactly as `jss-lint --output json` does.
pub fn render(report: &ComplianceReport) -> String {
    let payload = to_payload(report);
    let mut out = String::new();
    write_value(&payload, 0, &mut out);
    out.push('\n');
    out
}

fn write_value(value: &Value, indent: usize, out: &mut String) {
    match value {
        Value::Null => out.push_str("null"),
        Value::Bool(b) => out.push_str(if *b { "true" } else { "false" }),
        Value::Number(n) => out.push_str(&n.to_string()),
        Value::String(s) => write_py_string(s, out),
        Value::Array(items) => write_array(items, indent, out),
        Value::Object(map) => write_object(map, indent, out),
    }
}

fn write_array(items: &[Value], indent: usize, out: &mut String) {
    if items.is_empty() {
        out.push_str("[]");
        return;
    }
    out.push('[');
    let inner_indent = indent + 2;
    for (i, item) in items.iter().enumerate() {
        out.push('\n');
        out.push_str(&" ".repeat(inner_indent));
        write_value(item, inner_indent, out);
        if i + 1 < items.len() {
            out.push(',');
        }
    }
    out.push('\n');
    out.push_str(&" ".repeat(indent));
    out.push(']');
}

fn write_object(map: &Map<String, Value>, indent: usize, out: &mut String) {
    if map.is_empty() {
        out.push_str("{}");
        return;
    }
    // Unicode-codepoint order (Python's `sort_keys=True` default) equals
    // UTF-8 byte order equals Rust's `str`/`String` `Ord` — plain `.sort()`
    // on the keys is sufficient, no custom collation needed.
    let mut keys: Vec<&String> = map.keys().collect();
    keys.sort();

    out.push('{');
    let inner_indent = indent + 2;
    for (i, key) in keys.iter().enumerate() {
        out.push('\n');
        out.push_str(&" ".repeat(inner_indent));
        write_py_string(key, out);
        out.push_str(": ");
        write_value(&map[*key], inner_indent, out);
        if i + 1 < keys.len() {
            out.push(',');
        }
    }
    out.push('\n');
    out.push_str(&" ".repeat(indent));
    out.push('}');
}

/// Matches CPython's JSON string encoding with `ensure_ascii=True` (the
/// default `json.dumps` uses, and what `json_output.py` relies on
/// without overriding): standard shorthand escapes for `"`, `\`, and
/// `\n\r\t\b\f`; printable ASCII (0x20-0x7E) passed through as-is;
/// every other codepoint — including other C0 controls, DEL (0x7F, NOT
/// ASCII-printable despite being in the ASCII range), and all non-ASCII
/// — emitted as `\uXXXX`, with UTF-16 surrogate pairs above U+FFFF.
fn write_py_string(s: &str, out: &mut String) {
    out.push('"');
    for c in s.chars() {
        match c {
            '"' => out.push_str("\\\""),
            '\\' => out.push_str("\\\\"),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            '\t' => out.push_str("\\t"),
            '\x08' => out.push_str("\\b"),
            '\x0c' => out.push_str("\\f"),
            c if (' '..='~').contains(&c) => out.push(c),
            c => {
                let cp = c as u32;
                if cp <= 0xFFFF {
                    out.push_str(&format!("\\u{cp:04x}"));
                } else {
                    let cp = cp - 0x10000;
                    let high = 0xD800 + (cp >> 10);
                    let low = 0xDC00 + (cp & 0x3FF);
                    out.push_str(&format!("\\u{high:04x}\\u{low:04x}"));
                }
            }
        }
    }
    out.push('"');
}
