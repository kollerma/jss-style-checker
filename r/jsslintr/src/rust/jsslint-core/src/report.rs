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

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
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

    pub fn parse(s: &str) -> Option<Self> {
        match s {
            "error" => Some(Severity::Error),
            "warning" => Some(Severity::Warning),
            "info" => Some(Severity::Info),
            _ => None,
        }
    }

    /// Mirrors `cli.py::_SEVERITY_RANK = {"info": 0, "warning": 1,
    /// "error": 2}` — used for the `--fail-on` exit-code threshold.
    /// Deliberately not `derive(Ord)`: this enum's declaration order
    /// (Error, Warning, Info) doesn't match severity rank order, so a
    /// derived `Ord` would silently invert every threshold comparison.
    pub fn rank(&self) -> u8 {
        match self {
            Severity::Info => 0,
            Severity::Warning => 1,
            Severity::Error => 2,
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

/// Provenance of a journal's rule set — mirrors `api.RuleSetInfo`.
///
/// Every field is optional so a journal without provenance renders
/// `n/a` / `null` exactly as the Python reference does for a
/// third-party journal that supplies no metadata.
#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct RuleSetInfo {
    pub version: Option<String>,
    pub fingerprint: Option<String>,
    pub guide_edition: Option<String>,
    pub source_vendored_at: Option<String>,
}

impl RuleSetInfo {
    /// `"jss.cls 3.3 (2021-05-23)"` — the report/JSON rendering.
    /// `--version` lays the same two parts out differently, which is why
    /// they are stored apart. Mirrors `RuleSetInfo.guide_source`.
    pub fn guide_source(&self) -> Option<String> {
        let edition = self.guide_edition.as_ref()?;
        Some(match &self.source_vendored_at {
            Some(date) => format!("{edition} ({date})"),
            None => edition.clone(),
        })
    }
}

/// What a `--baseline` run hid — mirrors `core.baseline.BaselineSummary`.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct BaselineSummary {
    /// The path as the user gave it (flag or TOML), not resolved.
    pub path: String,
    pub matched: u32,
    /// Unmatched occurrences whose rule *did* run — findings since fixed.
    pub stale: u32,
    /// Unmatched occurrences whose rule did not run at all (ignored,
    /// below `--min-confidence`, format-skipped, retired).
    pub unevaluated: u32,
    pub ruleset_version: Option<String>,
}

#[derive(Debug, Clone)]
pub struct ComplianceReport {
    pub tool_version: String,
    pub journal_id: String,
    pub violations: Vec<Violation>,
    pub categories: Vec<CategorySummary>,
    pub compliance_percentage: Option<f64>,
    pub skipped_rules: Vec<SkippedRule>,
    /// Filled in by the CLI after the run; the engine never sees the
    /// baseline file (§XIV), only the matcher as a `Suppressor`.
    pub baseline: Option<BaselineSummary>,
    /// Provenance of the rule set that produced these findings, so no
    /// renderer has to reach into the catalogue itself.
    pub rule_set: RuleSetInfo,
}
