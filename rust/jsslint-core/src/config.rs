//! Tool configuration — mirrors `texlint.api.ToolConfig` (the fields
//! Phase 4 needs; `doi_resolver`/`--crossref` is an online, opt-in
//! feature explicitly out of scope for this port, see the plan's
//! network-dependency callout).

use crate::report::Severity;
use std::collections::{HashMap, HashSet};
use std::path::PathBuf;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Mode {
    Author,
    Reviewer,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum OutputFormat {
    Terminal,
    Json,
    Html,
    Sarif,
}

/// Confidence floor: rules whose measured-precision tier sits below
/// this are skipped. Ordered `Low < Medium < High` so `>=` comparisons
/// mirror Python's `_CONFIDENCE_RANK = {"low": 0, "medium": 1, "high": 2}`.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub enum ConfidenceTier {
    Low,
    Medium,
    High,
}

impl ConfidenceTier {
    pub fn parse(s: &str) -> Option<Self> {
        match s {
            "low" => Some(Self::Low),
            "medium" => Some(Self::Medium),
            "high" => Some(Self::High),
            _ => None,
        }
    }

    pub fn as_str(&self) -> &'static str {
        match self {
            Self::Low => "low",
            Self::Medium => "medium",
            Self::High => "high",
        }
    }
}

#[derive(Debug, Clone)]
pub struct ToolConfig {
    pub journal: String,
    pub mode: Mode,
    pub output: OutputFormat,
    pub ignore_rules: HashSet<String>,
    pub verbose: bool,
    pub code_width: u32,
    pub source_root: PathBuf,
    pub min_confidence: ConfidenceTier,
    /// Exit-code policy: the minimum severity that makes the CLI exit 1.
    pub fail_on: Severity,
    pub severity_overrides: HashMap<String, Severity>,
}

impl Default for ToolConfig {
    fn default() -> Self {
        Self {
            journal: "jss".to_string(),
            mode: Mode::Author,
            output: OutputFormat::Terminal,
            ignore_rules: HashSet::new(),
            verbose: false,
            code_width: 80,
            source_root: PathBuf::from("."),
            min_confidence: ConfidenceTier::Low,
            fail_on: Severity::Warning,
            severity_overrides: HashMap::new(),
        }
    }
}
