//! Deterministic SARIF 2.1.0 renderer — mirrors `output/sarif.py`
//! (spec 006 contract + the spec 008 `fixes[]` addition). Reuses
//! `json_output::write_value` for the same Python-`json.dumps`-
//! compatible serialization (`ensure_ascii=True` escaping,
//! `sort_keys=True`, `indent=2`).

use crate::catalogue::{self, RuleMeta};
use crate::config::ToolConfig;
use crate::report::{ComplianceReport, Severity, Violation};
use serde_json::{json, Value};
use std::path::{Component, Path, PathBuf};

const PARSE_RULE_ID: &str = "JSS-PARSE-000";
const INFORMATION_URI: &str = "https://github.com/kollerma/jss-style-checker";
const SCHEMA_URI: &str = "https://json.schemastore.org/sarif-2.1.0.json";

fn sarif_level(severity: Severity) -> &'static str {
    match severity {
        Severity::Error => "error",
        Severity::Warning => "warning",
        Severity::Info => "note",
    }
}

/// Lexically normalizes `.`/`..` components. Last-resort fallback for
/// when even the longest-existing-ancestor walk in `resolve_path`
/// can't canonicalize anything (e.g. no component of the path exists
/// at all). Does not resolve symlinks.
fn normalize_lexically(p: &Path) -> PathBuf {
    let mut out = PathBuf::new();
    for comp in p.components() {
        match comp {
            Component::ParentDir => {
                out.pop();
            }
            Component::CurDir => {}
            other => out.push(other.as_os_str()),
        }
    }
    out
}

/// Mirrors `pathlib.Path.resolve()`: makes `p` absolute and resolves
/// symlinks, tolerating a path that doesn't exist. Python's
/// `resolve()` still resolves symlinks in whatever prefix of the path
/// *does* exist, even when the leaf component is missing — plain
/// `std::fs::canonicalize` requires the whole path to exist, so on
/// its failure we walk up to the longest existing ancestor,
/// canonicalize that, and re-append the non-existent tail.
fn resolve_path(p: &Path) -> PathBuf {
    if let Ok(c) = std::fs::canonicalize(p) {
        return c;
    }
    let abs = if p.is_absolute() {
        p.to_path_buf()
    } else {
        std::env::current_dir().unwrap_or_default().join(p)
    };
    let mut tail: Vec<std::ffi::OsString> = Vec::new();
    let mut cur = abs.as_path();
    loop {
        if let Ok(base) = std::fs::canonicalize(cur) {
            let mut out = base;
            for c in tail.iter().rev() {
                out.push(c);
            }
            return out;
        }
        match (cur.parent(), cur.file_name()) {
            (Some(parent), Some(name)) => {
                tail.push(name.to_os_string());
                cur = parent;
            }
            _ => return normalize_lexically(&abs),
        }
    }
}

/// Mirrors `os.path.relpath(target, base)`: the relative path from
/// `base` to `target`, inserting `..` segments as needed. Subsumes
/// Python's `Path.relative_to()` fast path too — when `base` is a
/// true prefix of `target`, this produces the identical result (zero
/// `..` segments).
fn relative_path(target: &Path, base: &Path) -> PathBuf {
    let target_comps: Vec<Component> = target.components().collect();
    let base_comps: Vec<Component> = base.components().collect();
    let mut common = 0;
    while common < target_comps.len()
        && common < base_comps.len()
        && target_comps[common] == base_comps[common]
    {
        common += 1;
    }
    let mut result = PathBuf::new();
    for _ in common..base_comps.len() {
        result.push("..");
    }
    for comp in &target_comps[common..] {
        result.push(comp.as_os_str());
    }
    if result.as_os_str().is_empty() {
        result.push(".");
    }
    result
}

fn as_posix(p: &Path) -> String {
    p.components()
        .map(|c| c.as_os_str().to_string_lossy().into_owned())
        .collect::<Vec<_>>()
        .join("/")
}

/// Mirrors `sarif.py::_relativise`: render `file` as a POSIX-style
/// path relative to `source_root`.
fn relativise(file: &str, source_root: &Path) -> String {
    let file_path = Path::new(file);
    let abs_file = if file_path.is_absolute() {
        resolve_path(file_path)
    } else {
        resolve_path(&source_root.join(file_path))
    };
    let abs_root = resolve_path(source_root);
    as_posix(&relative_path(&abs_file, &abs_root))
}

fn location_value(v: &Violation, source_root: &Path) -> Value {
    let mut region = serde_json::Map::new();
    region.insert("startLine".to_string(), json!(v.line));
    if let Some(col) = v.column {
        region.insert("startColumn".to_string(), json!(col));
    }
    json!({
        "physicalLocation": {
            "artifactLocation": {"uri": relativise(&v.file, source_root)},
            "region": region,
        }
    })
}

fn result_value(v: &Violation, source_root: &Path) -> Value {
    let mut obj = serde_json::Map::new();
    obj.insert("ruleId".to_string(), json!(v.rule_id));
    obj.insert("level".to_string(), json!(sarif_level(v.severity)));
    obj.insert("message".to_string(), json!({"text": v.message}));
    obj.insert(
        "locations".to_string(),
        json!([location_value(v, source_root)]),
    );
    if let Some(fix) = &v.fix {
        obj.insert(
            "fixes".to_string(),
            json!([{
                "description": {"text": fix.description},
                "artifactChanges": [{
                    "artifactLocation": {"uri": relativise(&v.file, source_root)},
                    "replacements": [{
                        "deletedRegion": {
                            "byteOffset": fix.start,
                            "byteLength": fix.end - fix.start,
                        },
                        "insertedContent": {"text": fix.replacement},
                    }],
                }],
            }]),
        );
    }
    Value::Object(obj)
}

fn notification_value(v: &Violation, source_root: &Path) -> Value {
    json!({
        "descriptor": {"id": PARSE_RULE_ID},
        "level": "error",
        "message": {"text": v.message},
        "locations": [location_value(v, source_root)],
    })
}

fn rule_descriptor(id: &str, meta: &RuleMeta) -> Value {
    let short_text = if !meta.guide_section.is_empty() && meta.guide_section != "internal" {
        format!("{} ({})", meta.message_template, meta.guide_section)
    } else {
        meta.message_template.to_string()
    };
    let mut obj = serde_json::Map::new();
    obj.insert("id".to_string(), json!(id));
    obj.insert("name".to_string(), json!(id));
    obj.insert("shortDescription".to_string(), json!({"text": short_text}));
    obj.insert(
        "fullDescription".to_string(),
        json!({"text": meta.message_template}),
    );
    obj.insert(
        "defaultConfiguration".to_string(),
        json!({"level": sarif_level(meta.severity)}),
    );
    obj.insert("properties".to_string(), json!({"tags": [meta.category]}));
    if let Some(url) = meta.guide_url {
        obj.insert("helpUri".to_string(), json!(url));
    }
    Value::Object(obj)
}

/// The synthetic `JSS-PARSE-000` rule descriptor — parse failures are
/// notifications, not results, but the rule still appears under
/// `tool.driver.rules`.
fn internal_parse_rule_descriptor() -> Value {
    json!({
        "id": PARSE_RULE_ID,
        "name": PARSE_RULE_ID,
        "shortDescription": {"text": "Parser failed to process the input file."},
        "fullDescription": {
            "text": "Emitted when the parser could not analyse a file. The file is reported under runs[0].invocations[0].toolExecutionNotifications rather than runs[0].results."
        },
        "defaultConfiguration": {"level": "error"},
        "properties": {"tags": ["parse"]},
    })
}

fn catalogue_rules() -> Vec<Value> {
    let mut rules: Vec<Value> = catalogue::all_rules()
        .iter()
        .map(|m| rule_descriptor(m.rule_id, m))
        .collect();
    rules.push(internal_parse_rule_descriptor());
    rules.sort_by(|a, b| a["id"].as_str().unwrap().cmp(b["id"].as_str().unwrap()));
    rules
}

fn violation_sort_key(v: &Violation) -> (String, u32, u32, String) {
    (
        v.file.clone(),
        v.line,
        v.column.unwrap_or(0),
        v.rule_id.clone(),
    )
}

/// Builds the full SARIF document as a `serde_json::Value`. Pure:
/// same `(report, config)` always produces the same value.
pub fn to_payload(report: &ComplianceReport, config: &ToolConfig) -> Value {
    let source_root = config.source_root.as_path();

    let mut parse_failures: Vec<&Violation> = Vec::new();
    let mut other_violations: Vec<&Violation> = Vec::new();
    for v in &report.violations {
        if v.rule_id == PARSE_RULE_ID {
            parse_failures.push(v);
        } else {
            other_violations.push(v);
        }
    }
    parse_failures.sort_by_key(|v| violation_sort_key(v));
    other_violations.sort_by_key(|v| violation_sort_key(v));

    let results: Vec<Value> = other_violations
        .iter()
        .map(|v| result_value(v, source_root))
        .collect();
    let notifications: Vec<Value> = parse_failures
        .iter()
        .map(|v| notification_value(v, source_root))
        .collect();

    json!({
        "$schema": SCHEMA_URI,
        "version": "2.1.0",
        "runs": [{
            "tool": {
                "driver": {
                    "name": "jss-lint",
                    "version": report.tool_version,
                    "informationUri": INFORMATION_URI,
                    "rules": catalogue_rules(),
                }
            },
            "invocations": [{
                "executionSuccessful": true,
                "toolExecutionNotifications": notifications,
            }],
            "results": results,
        }],
    })
}

/// Render a `ComplianceReport` exactly as `jss-lint --output sarif` does.
pub fn render(report: &ComplianceReport, config: &ToolConfig) -> String {
    let payload = to_payload(report, config);
    let mut out = String::new();
    crate::json_output::write_value(&payload, 0, &mut out);
    out.push('\n');
    out
}
