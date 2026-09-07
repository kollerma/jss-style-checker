//! Baseline files: accept today's findings, fail only on new ones.
//!
//! Port of `src/texlint/core/baseline.py` (spec 027 item B); contract:
//! `specs/027-first-time-user-gaps/contracts/baseline-file.md`. See the
//! Python module for the why.
//!
//! Pure, like its counterpart: reading and writing the file, and
//! computing the `path_map`, belong to `jsslint-cli` (§XIV). The
//! serialiser goes through `json_output::write_value` so that a file
//! written by this engine is byte-identical to one written by CPython's
//! `json.dumps(indent=2, sort_keys=True)` — the whole point of a
//! baseline being committed once and read by whichever engine CI runs.

use crate::engine::Suppressor;
use crate::json_output;
use crate::report::{BaselineSummary, Violation};
use serde_json::{json, Value};
use std::collections::{BTreeMap, HashMap, HashSet};

/// The only schema version this release reads or writes.
pub const SCHEMA_VERSION: u64 = 1;

const PARSE_RULE_ID: &str = "JSS-PARSE-000";

/// `(rule_id, path, message, suggestion)` — `baseline-file.md` C-2.
pub type Key = (String, String, String, String);

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct BaselineEntry {
    pub rule_id: String,
    pub path: String,
    pub message: String,
    pub suggestion: String,
    pub count: u32,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct BaselineDocument {
    pub schema_version: u64,
    pub tool_version: String,
    pub ruleset_version: Option<String>,
    pub journal: String,
    pub entries: Vec<BaselineEntry>,
}

/// Sort order for both reading and writing: `(path, rule_id, message,
/// suggestion)`, so a human reviewing an updated baseline's diff reads
/// it file by file.
fn sort_entries(entries: &mut [BaselineEntry]) {
    entries.sort_by(|a, b| {
        (&a.path, &a.rule_id, &a.message, &a.suggestion).cmp(&(
            &b.path,
            &b.rule_id,
            &b.message,
            &b.suggestion,
        ))
    });
}

fn string_field(obj: &serde_json::Map<String, Value>, key: &str) -> Result<String, String> {
    match obj.get(key) {
        Some(Value::String(s)) => Ok(s.clone()),
        Some(_) => Err(format!("entries: {key} must be a string")),
        None => Err(format!("entries: missing key '{key}'")),
    }
}

fn entry_from(raw: &Value) -> Result<BaselineEntry, String> {
    let Some(obj) = raw.as_object() else {
        return Err("entries must be a list of objects".to_string());
    };
    let rule_id = string_field(obj, "rule_id")?;
    let path = string_field(obj, "path")?;
    let message = string_field(obj, "message")?;
    let suggestion = string_field(obj, "suggestion")?;
    let count = match obj.get("count") {
        Some(Value::Number(n)) => n.as_u64().unwrap_or(0),
        Some(_) => return Err("entries: count must be an integer >= 1".to_string()),
        None => return Err("entries: missing key 'count'".to_string()),
    };
    if count < 1 {
        return Err("entries: count must be an integer >= 1".to_string());
    }
    Ok(BaselineEntry {
        rule_id,
        path,
        message,
        suggestion,
        count: count as u32,
    })
}

/// Read a baseline file. The error text is a documented per-engine
/// divergence (`baseline-file.md` C-10) — only exit code 2 is
/// guaranteed to match, as for `jss-lint diff`.
pub fn parse(text: &str) -> Result<BaselineDocument, String> {
    let payload: Value = serde_json::from_str(text).map_err(|e| format!("not valid JSON: {e}"))?;
    let Some(obj) = payload.as_object() else {
        return Err("document must be a JSON object".to_string());
    };
    if obj.get("schema_version").and_then(Value::as_u64) != Some(SCHEMA_VERSION) {
        return Err(format!(
            "unsupported schema_version {} (this release reads {SCHEMA_VERSION})",
            obj.get("schema_version").unwrap_or(&Value::Null)
        ));
    }
    let journal = match obj.get("journal") {
        Some(Value::String(s)) => s.clone(),
        _ => return Err("journal must be a string".to_string()),
    };
    let tool_version = match obj.get("tool_version") {
        Some(Value::String(s)) => s.clone(),
        _ => return Err("tool_version must be a string".to_string()),
    };
    let ruleset_version = match obj.get("ruleset_version") {
        Some(Value::String(s)) => Some(s.clone()),
        Some(Value::Null) | None => None,
        Some(_) => return Err("ruleset_version must be a string or null".to_string()),
    };
    let Some(raw_entries) = obj.get("entries").and_then(Value::as_array) else {
        return Err("entries must be a list".to_string());
    };
    let mut entries = raw_entries
        .iter()
        .map(entry_from)
        .collect::<Result<Vec<_>, _>>()?;
    sort_entries(&mut entries);
    Ok(BaselineDocument {
        schema_version: SCHEMA_VERSION,
        tool_version,
        ruleset_version,
        journal,
        entries,
    })
}

/// Accept every reported finding. A finding whose file is absent from
/// `path_map` is dropped: it could never be matched again, so an entry
/// for it would be stale forever.
pub fn build(
    violations: &[Violation],
    path_map: &HashMap<String, String>,
    tool_version: &str,
    ruleset_version: Option<&str>,
    journal: &str,
) -> BaselineDocument {
    let mut counts: BTreeMap<Key, u32> = BTreeMap::new();
    for v in violations {
        if v.rule_id == PARSE_RULE_ID {
            continue;
        }
        let Some(path) = path_map.get(&v.file) else {
            continue;
        };
        let key = (
            v.rule_id.clone(),
            path.clone(),
            v.message.clone(),
            v.suggestion.clone().unwrap_or_default(),
        );
        *counts.entry(key).or_insert(0) += 1;
    }
    let mut entries: Vec<BaselineEntry> = counts
        .into_iter()
        .map(|((rule_id, path, message, suggestion), count)| BaselineEntry {
            rule_id,
            path,
            message,
            suggestion,
            count,
        })
        .collect();
    sort_entries(&mut entries);
    BaselineDocument {
        schema_version: SCHEMA_VERSION,
        tool_version: tool_version.to_string(),
        ruleset_version: ruleset_version.map(str::to_string),
        journal: journal.to_string(),
        entries,
    }
}

/// Serialise. No timestamp, no host-specific field, sorted keys — so
/// two engines and two runs produce byte-identical files.
pub fn to_json(doc: &BaselineDocument) -> String {
    let entries: Vec<Value> = doc
        .entries
        .iter()
        .map(|e| {
            json!({
                "rule_id": e.rule_id,
                "path": e.path,
                "message": e.message,
                "suggestion": e.suggestion,
                "count": e.count,
            })
        })
        .collect();
    let payload = json!({
        "schema_version": doc.schema_version,
        "tool_version": doc.tool_version,
        "ruleset_version": doc.ruleset_version,
        "journal": doc.journal,
        "entries": entries,
    });
    let mut out = String::new();
    json_output::write_value(&payload, 0, &mut out);
    out.push('\n');
    out
}

/// The [`Suppressor`] that hides accepted findings.
///
/// Entries form a multiset: each match decrements the remaining count,
/// so the *n*-th occurrence of an accepted finding is reported once the
/// accepted count is exhausted. The engine offers findings in
/// `Violation::sort_key` order, which makes *which* occurrences are
/// hidden deterministic and identical in both engines.
pub struct BaselineMatcher {
    remaining: HashMap<Key, u32>,
    path_map: HashMap<String, String>,
    ruleset_version: Option<String>,
    matched: u32,
}

impl BaselineMatcher {
    pub fn new(doc: &BaselineDocument, path_map: HashMap<String, String>) -> Self {
        let mut remaining: HashMap<Key, u32> = HashMap::new();
        for entry in &doc.entries {
            *remaining
                .entry((
                    entry.rule_id.clone(),
                    entry.path.clone(),
                    entry.message.clone(),
                    entry.suggestion.clone(),
                ))
                .or_insert(0) += entry.count;
        }
        Self {
            remaining,
            path_map,
            ruleset_version: doc.ruleset_version.clone(),
            matched: 0,
        }
    }

    pub fn summary(&self, path: &str, applied_rule_ids: &HashSet<String>) -> BaselineSummary {
        let mut stale = 0;
        let mut unevaluated = 0;
        for ((rule_id, _path, _message, _suggestion), remaining) in &self.remaining {
            if *remaining == 0 {
                continue;
            }
            if applied_rule_ids.contains(rule_id) {
                stale += remaining;
            } else {
                unevaluated += remaining;
            }
        }
        BaselineSummary {
            path: path.to_string(),
            matched: self.matched,
            stale,
            unevaluated,
            ruleset_version: self.ruleset_version.clone(),
        }
    }
}

impl Suppressor for BaselineMatcher {
    fn suppress(&mut self, violation: &Violation) -> bool {
        let Some(path) = self.path_map.get(&violation.file) else {
            return false;
        };
        let key = (
            violation.rule_id.clone(),
            path.clone(),
            violation.message.clone(),
            violation.suggestion.clone().unwrap_or_default(),
        );
        match self.remaining.get_mut(&key) {
            Some(count) if *count > 0 => {
                *count -= 1;
                self.matched += 1;
                true
            }
            _ => false,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::report::Severity;

    fn violation(line: u32, rule_id: &str, suggestion: Option<&str>) -> Violation {
        Violation {
            file: "paper.tex".to_string(),
            line,
            column: Some(1),
            rule_id: rule_id.to_string(),
            severity: Severity::Warning,
            message: "msg".to_string(),
            suggestion: suggestion.map(str::to_string),
            fix: None,
        }
    }

    fn path_map() -> HashMap<String, String> {
        HashMap::from([("paper.tex".to_string(), "paper.tex".to_string())])
    }

    fn doc(violations: &[Violation]) -> BaselineDocument {
        build(violations, &path_map(), "1.2.0", Some("2026-09-07"), "jss")
    }

    #[test]
    fn counts_identical_findings() {
        let d = doc(&[
            violation(3, "JSS-MARKUP-001", Some("sug")),
            violation(9, "JSS-MARKUP-001", Some("sug")),
        ]);
        assert_eq!(d.entries.len(), 1);
        assert_eq!(d.entries[0].count, 2);
    }

    #[test]
    fn parse_errors_are_never_written() {
        assert!(doc(&[violation(1, PARSE_RULE_ID, None)]).entries.is_empty());
    }

    #[test]
    fn round_trips_through_json() {
        let d = doc(&[
            violation(1, "JSS-XREF-002", Some("a")),
            violation(2, "JSS-CAP-002", Some("b")),
        ]);
        assert_eq!(parse(&to_json(&d)).unwrap(), d);
    }

    #[test]
    fn rejects_an_unknown_schema_version() {
        let text = to_json(&doc(&[])).replace("\"schema_version\": 1", "\"schema_version\": 2");
        assert!(parse(&text).unwrap_err().contains("schema_version"));
    }

    #[test]
    fn rejects_a_malformed_entry() {
        let text = r#"{"schema_version": 1, "tool_version": "1.2.0",
            "ruleset_version": null, "journal": "jss",
            "entries": [{"rule_id": "JSS-CAP-002"}]}"#;
        assert!(parse(text).unwrap_err().contains("entries"));
    }

    #[test]
    fn matches_and_consumes_in_offered_order() {
        let d = doc(&[
            violation(1, "JSS-MARKUP-001", Some("sug")),
            violation(2, "JSS-MARKUP-001", Some("sug")),
        ]);
        let mut matcher = BaselineMatcher::new(&d, path_map());
        let seen: Vec<bool> = (1..=3)
            .map(|line| matcher.suppress(&violation(line, "JSS-MARKUP-001", Some("sug"))))
            .collect();
        assert_eq!(seen, vec![true, true, false]);
    }

    #[test]
    fn a_different_suggestion_is_a_different_finding() {
        let d = doc(&[violation(1, "JSS-MARKUP-001", Some("sug"))]);
        let mut matcher = BaselineMatcher::new(&d, path_map());
        assert!(!matcher.suppress(&violation(1, "JSS-MARKUP-001", Some("other"))));
    }

    #[test]
    fn summary_splits_stale_from_unevaluated() {
        let d = doc(&[
            violation(1, "JSS-CAP-002", Some("s")),
            violation(2, "JSS-XREF-002", Some("s")),
            violation(3, "JSS-REFS-003", Some("s")),
        ]);
        let mut matcher = BaselineMatcher::new(&d, path_map());
        matcher.suppress(&violation(1, "JSS-CAP-002", Some("s")));
        let applied: HashSet<String> = ["JSS-CAP-002", "JSS-XREF-002"]
            .iter()
            .map(|s| s.to_string())
            .collect();
        let summary = matcher.summary("b.json", &applied);
        assert_eq!((summary.matched, summary.stale, summary.unevaluated), (1, 1, 1));
        assert_eq!(summary.ruleset_version.as_deref(), Some("2026-09-07"));
    }
}
