//! `jss-lint diff` engine + renderers — mirrors `texlint/diff.py`
//! (spec 016). Pure comparison over the spec-001 `--output json` shape;
//! violations are kept as generic `serde_json::Value` objects (not
//! this crate's typed `Violation`) since a diff input can be any
//! spec-001-shaped JSON file, including ones this binary didn't
//! produce, and every original field must round-trip into
//! `render_json`'s output untouched.

use crate::engine::python_list_repr;
use serde_json::{Map, Value};
use std::collections::{HashMap, HashSet};

const SPEC_001_REQUIRED_KEYS: &[&str] = &["tool_version", "journal_id", "violations"];
const PER_VIOLATION_REQUIRED: &[&str] = &["rule_id", "file", "line", "message"];

/// Mirrors `diff.py::SchemaMismatch`.
#[derive(Debug, Clone)]
pub struct SchemaMismatch(pub String);

impl std::fmt::Display for SchemaMismatch {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.0)
    }
}

fn json_type_name(v: &Value) -> &'static str {
    match v {
        Value::Null => "NoneType",
        Value::Bool(_) => "bool",
        Value::Number(n) => {
            if n.is_f64() {
                "float"
            } else {
                "int"
            }
        }
        Value::String(_) => "str",
        Value::Array(_) => "list",
        Value::Object(_) => "dict",
    }
}

/// Validates a parsed JSON payload against the spec-001 shape and
/// returns its `violations` array. `source` is a short human-readable
/// identifier (typically a file path) included in the error message.
/// Mirrors `diff.py::validate_payload`.
pub fn validate_payload(payload: &Value, source: &str) -> Result<Vec<Value>, SchemaMismatch> {
    let Value::Object(obj) = payload else {
        return Err(SchemaMismatch(format!(
            "{source}: top-level value is not a JSON object"
        )));
    };

    let mut missing: Vec<&str> = SPEC_001_REQUIRED_KEYS
        .iter()
        .filter(|k| !obj.contains_key(**k))
        .copied()
        .collect();
    if !missing.is_empty() {
        missing.sort_unstable();
        return Err(SchemaMismatch(format!(
            "{source}: missing required key(s) {} — not a spec-001 jss-lint JSON report",
            python_list_repr(&missing)
        )));
    }

    let violations_value = obj.get("violations").expect("checked above");
    let Value::Array(items) = violations_value else {
        return Err(SchemaMismatch(format!(
            "{source}: 'violations' must be a list (got {})",
            json_type_name(violations_value)
        )));
    };

    for (i, v) in items.iter().enumerate() {
        let Value::Object(vobj) = v else {
            return Err(SchemaMismatch(format!(
                "{source}: violations[{i}] is not an object"
            )));
        };
        let mut v_missing: Vec<&str> = PER_VIOLATION_REQUIRED
            .iter()
            .filter(|k| !vobj.contains_key(**k))
            .copied()
            .collect();
        if !v_missing.is_empty() {
            v_missing.sort_unstable();
            return Err(SchemaMismatch(format!(
                "{source}: violations[{i}] missing key(s) {}",
                python_list_repr(&v_missing)
            )));
        }
    }

    Ok(items.clone())
}

/// Mirrors `diff.py::DiffReport`.
#[derive(Debug, Clone)]
pub struct DiffReport {
    pub fixed: Vec<Value>,
    pub introduced: Vec<Value>,
    pub unchanged: Vec<Value>,
}

#[derive(Debug, Clone, PartialEq, Eq, Hash)]
struct IdentityKey {
    rule_id: String,
    file: String,
    line: Option<i64>,
    message: String,
}

fn str_field(obj: &Map<String, Value>, key: &str) -> String {
    obj.get(key)
        .and_then(Value::as_str)
        .unwrap_or_default()
        .to_string()
}

fn identity(obj: &Map<String, Value>, drop_line: bool) -> IdentityKey {
    IdentityKey {
        rule_id: str_field(obj, "rule_id"),
        file: str_field(obj, "file"),
        line: if drop_line {
            None
        } else {
            obj.get("line").and_then(Value::as_i64)
        },
        message: str_field(obj, "message"),
    }
}

fn apply_renames(violations: &[Value], renames: &HashMap<String, String>) -> Vec<Value> {
    violations
        .iter()
        .map(|v| {
            let Some(obj) = v.as_object() else {
                return v.clone();
            };
            let rule_id = obj.get("rule_id").and_then(Value::as_str).unwrap_or("");
            match renames.get(rule_id) {
                Some(new_id) if new_id != rule_id => {
                    let mut new_obj = obj.clone();
                    new_obj.insert("rule_id".to_string(), Value::String(new_id.clone()));
                    Value::Object(new_obj)
                }
                _ => v.clone(),
            }
        })
        .collect()
}

fn sort_key(v: &Value) -> (String, i64, String) {
    let Some(obj) = v.as_object() else {
        return (String::new(), 0, String::new());
    };
    (
        str_field(obj, "file"),
        obj.get("line").and_then(Value::as_i64).unwrap_or(0),
        str_field(obj, "rule_id"),
    )
}

/// Compares two spec-001 violation lists. Mirrors `diff.py::compare`
/// (spec 016 contract C-2). `rule_renames` isn't exposed by the
/// `jss-lint diff` CLI surface today (Python's `diff_cmd` doesn't wire
/// a `--rule-renames` flag either) — kept as a parameter for API
/// parity with the Python function.
pub fn compare(
    old: &[Value],
    new: &[Value],
    ignore_line_drift: bool,
    rule_renames: Option<&HashMap<String, String>>,
) -> DiffReport {
    let empty = HashMap::new();
    let renames = rule_renames.unwrap_or(&empty);
    let old_norm = apply_renames(old, renames);

    let mut old_index: HashMap<IdentityKey, Value> = HashMap::new();
    for v in &old_norm {
        if let Some(obj) = v.as_object() {
            old_index.insert(identity(obj, ignore_line_drift), v.clone());
        }
    }
    let mut new_index: HashMap<IdentityKey, Value> = HashMap::new();
    for v in new {
        if let Some(obj) = v.as_object() {
            new_index.insert(identity(obj, ignore_line_drift), v.clone());
        }
    }

    let old_keys: HashSet<&IdentityKey> = old_index.keys().collect();
    let new_keys: HashSet<&IdentityKey> = new_index.keys().collect();

    let mut fixed: Vec<Value> = old_keys
        .difference(&new_keys)
        .map(|k| old_index[*k].clone())
        .collect();
    fixed.sort_by_key(sort_key);

    let mut introduced: Vec<Value> = new_keys
        .difference(&old_keys)
        .map(|k| new_index[*k].clone())
        .collect();
    introduced.sort_by_key(sort_key);

    // `unchanged` uses NEW's values (diff.py's `research §7` note).
    let mut unchanged: Vec<Value> = old_keys
        .intersection(&new_keys)
        .map(|k| new_index[*k].clone())
        .collect();
    unchanged.sort_by_key(sort_key);

    DiffReport {
        fixed,
        introduced,
        unchanged,
    }
}

fn v_summary(v: &Value) -> String {
    let Some(obj) = v.as_object() else {
        return String::new();
    };
    let rule_id = str_field(obj, "rule_id");
    let file = str_field(obj, "file");
    let line = obj.get("line").and_then(Value::as_i64).unwrap_or(0);
    let message = str_field(obj, "message");
    format!("{rule_id} {file}:{line}: {message}")
}

/// ANSI-free plain-text rendering. Mirrors `diff.py::render_terminal`.
pub fn render_terminal(diff: &DiffReport) -> String {
    let mut lines = vec![format!(
        "fixed: {} introduced: {} unchanged: {}",
        diff.fixed.len(),
        diff.introduced.len(),
        diff.unchanged.len()
    )];
    for (label, group) in [
        ("Fixed", &diff.fixed),
        ("Introduced", &diff.introduced),
        ("Unchanged", &diff.unchanged),
    ] {
        if group.is_empty() {
            continue;
        }
        lines.push(String::new());
        lines.push(format!("== {label} =="));
        for v in group {
            lines.push(format!("  {}", v_summary(v)));
        }
    }
    lines.join("\n") + "\n"
}

/// GitHub-flavoured CommonMark. Mirrors `diff.py::render_markdown`.
pub fn render_markdown(diff: &DiffReport) -> String {
    let mut parts = vec![
        format!(
            "**fixed:** {} | **introduced:** {} | **unchanged:** {}",
            diff.fixed.len(),
            diff.introduced.len(),
            diff.unchanged.len()
        ),
        String::new(),
    ];
    for (label, group) in [
        ("Fixed", &diff.fixed),
        ("Introduced", &diff.introduced),
        ("Unchanged", &diff.unchanged),
    ] {
        parts.push(format!("## {label}"));
        if group.is_empty() {
            parts.push(String::new());
            parts.push("(none)".to_string());
            parts.push(String::new());
            continue;
        }
        parts.push(String::new());
        for v in group {
            let Some(obj) = v.as_object() else { continue };
            let rule_id = str_field(obj, "rule_id");
            let file = str_field(obj, "file");
            let line = obj.get("line").and_then(Value::as_i64).unwrap_or(0);
            let message = str_field(obj, "message");
            parts.push(format!("- `{rule_id}` {file}:{line}: {message}"));
        }
        parts.push(String::new());
    }
    parts.join("\n").trim_end().to_string() + "\n"
}

/// Deterministic JSON output. Mirrors `diff.py::render_json`, reusing
/// `json_output::write_value` for the same `json.dumps`-compatible
/// serialization.
pub fn render_json(diff: &DiffReport) -> String {
    let payload = serde_json::json!({
        "summary": {
            "fixed": diff.fixed.len(),
            "introduced": diff.introduced.len(),
            "unchanged": diff.unchanged.len(),
        },
        "fixed": diff.fixed,
        "introduced": diff.introduced,
        "unchanged": diff.unchanged,
    });
    let mut out = String::new();
    crate::json_output::write_value(&payload, 0, &mut out);
    out.push('\n');
    out
}
