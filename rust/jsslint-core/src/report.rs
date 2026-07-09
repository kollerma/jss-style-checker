//! Domain model — mirrors `texlint.api` (see `/workspace/src/texlint/api.py`).
//!
//! Deliberate deviation from the Python source: `Violation::file` is a
//! plain `String` (already POSIX-formatted at construction), not a path
//! type. The Python dataclass carries a `pathlib.Path` because it also
//! does filesystem I/O; this domain model doesn't (and one binding
//! target, WASM-in-browser, has no OS filesystem at all), so treating
//! the file as an opaque identifier string is the more portable choice.
//! `output::json` still renders it under the `"file"` key exactly as
//! `output/json_output.py` does via `Path.as_posix()`.

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Severity {
    Error,
    Warning,
    Info,
}

impl Severity {
    pub fn as_str(&self) -> &'static str {
        match self {
            Severity::Error => "error",
            Severity::Warning => "warning",
            Severity::Info => "info",
        }
    }
}

/// A single text-edit auto-fix payload (spec 008).
///
/// `start`/`end` are 0-based, half-open **Unicode codepoint offsets**,
/// NOT byte offsets, despite `Fix`'s docstring in api.py claiming
/// "byte offsets" — verified against actual behavior:
/// `core/fixer.py` applies a fix via plain Python string slicing
/// (`new[:fix.start] + fix.replacement + new[fix.end:]`), and Python
/// `str` slicing is codepoint-indexed. `pylatexenc`'s own `pos`/`len`
/// (which most `Fix` construction sites derive `start`/`end` from) are
/// likewise Python-string-index-based, i.e. codepoints. The two are
/// identical for ASCII-only spans (which is why this went unnoticed:
/// author names and prose text are the only realistic source of
/// non-ASCII content, and most auto-fixable rules don't touch them),
/// but diverge on any span containing non-ASCII text. This crate's
/// tokenizer positions codepoint-index throughout to match.
#[derive(Debug, Clone)]
pub struct Fix {
    pub start: usize,
    pub end: usize,
    pub replacement: String,
    pub description: String,
    pub confidence: FixConfidence,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum FixConfidence {
    Safe,
    Review,
}

impl FixConfidence {
    pub fn as_str(&self) -> &'static str {
        match self {
            FixConfidence::Safe => "safe",
            FixConfidence::Review => "review",
        }
    }
}

#[derive(Debug, Clone)]
pub struct Violation {
    pub file: String,
    /// 1-based.
    pub line: u32,
    /// 1-based; `None` when the rule operates at line granularity.
    pub column: Option<u32>,
    pub rule_id: String,
    pub severity: Severity,
    pub message: String,
    pub suggestion: Option<String>,
    pub fix: Option<Fix>,
}

impl Violation {
    /// Mirrors `Violation.sort_key` in api.py:
    /// `(file, line, column-bucket, column-value, rule_id)`, where
    /// `column = None` sorts before any integer (bucket 0 vs 1).
    pub fn sort_key(&self) -> (&str, u32, u8, u32, &str) {
        let (bucket, col) = match self.column {
            Some(c) => (1u8, c),
            None => (0u8, 0),
        };
        (
            self.file.as_str(),
            self.line,
            bucket,
            col,
            self.rule_id.as_str(),
        )
    }
}

/// Sorts violations by `Violation::sort_key`, matching the Python
/// engine's canonical ordering (spec 001 json-output.md "Determinism").
pub fn sort_violations(violations: &mut [Violation]) {
    violations.sort_by(|a, b| a.sort_key().cmp(&b.sort_key()));
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum CategoryStatus {
    Pass,
    Fail,
    Skipped,
}

impl CategoryStatus {
    pub fn as_str(&self) -> &'static str {
        match self {
            CategoryStatus::Pass => "PASS",
            CategoryStatus::Fail => "FAIL",
            CategoryStatus::Skipped => "SKIPPED",
        }
    }
}

#[derive(Debug, Clone)]
pub struct CategorySummary {
    pub category_id: String,
    pub title: String,
    pub status: CategoryStatus,
    pub rules_applied: u32,
    pub rules_passed: u32,
    /// Not serialized to JSON — mirrors api.py: violations live only in
    /// the top-level `violations` array (json-output.md, "Violations
    /// are not duplicated inside each category in JSON").
    pub violations: Vec<Violation>,
}

impl CategorySummary {
    /// Mirrors `CategorySummary.build` in api.py.
    pub fn build(
        category_id: impl Into<String>,
        title: impl Into<String>,
        rules_applied: u32,
        rules_passed: u32,
        violations: Vec<Violation>,
    ) -> Self {
        let status = if rules_applied == 0 {
            CategoryStatus::Skipped
        } else if !violations.is_empty() {
            CategoryStatus::Fail
        } else {
            CategoryStatus::Pass
        };
        Self {
            category_id: category_id.into(),
            title: title.into(),
            status,
            rules_applied,
            rules_passed,
            violations,
        }
    }
}

/// A rule that did NOT run because its `formats` filter excluded every
/// input format present. Mirrors `SkippedRule` in api.py.
#[derive(Debug, Clone)]
pub struct SkippedRule {
    pub rule_id: String,
    pub reason: String,
}

#[derive(Debug, Clone)]
pub struct ComplianceReport {
    pub tool_version: String,
    pub journal_id: String,
    pub violations: Vec<Violation>,
    pub categories: Vec<CategorySummary>,
    pub compliance_percentage: Option<f64>,
    pub skipped_rules: Vec<SkippedRule>,
}
