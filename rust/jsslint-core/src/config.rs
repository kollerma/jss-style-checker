//! Tool configuration — mirrors `texlint.api.ToolConfig` (the fields
//! Phase 4 needs, plus `doi_resolver`) and `texlint.config`'s
//! defaults-then-`.jss-lint.toml`-then-CLI merge (`load`).
//!
//! `doi_resolver` is a plain injection hook — the type alias below
//! requires no networking dependency to *define*, only to *implement*.
//! Mirrors `texlint.crossref.Resolver`: `jss-lint --crossref` builds
//! the real (network-backed) resolver and hands it to `cfg.doi_resolver`;
//! with no resolver, `JSS-REFS-003` keeps its offline-advisory behavior.
//! The live implementation lives in the separate `jsslint-crossref`
//! crate (depends on `jsslint-core`, not the reverse) precisely so that
//! `jsslint-wasm` — which depends on `jsslint-core` but never on
//! `jsslint-crossref` — can't reach the network even by accident: this
//! field being `Option<Arc<DoiResolver>>` rather than a concrete
//! network client is what makes that guarantee structural. See
//! `jsslint-wasm/src/lib.rs`'s module doc and `jsslint-crossref/src/lib.rs`'s.

use crate::report::Severity;
use std::collections::{HashMap, HashSet};
use std::path::{Path, PathBuf};
use std::sync::Arc;

/// `(fields, entry_type) -> Option<doi>`. `fields` is a lowercase-keyed
/// field map (title/author/year/url…); `entry_type` is the lowercase
/// BibTeX entry type. Mirrors `texlint.crossref.Resolver`.
pub type DoiResolver = dyn Fn(&HashMap<String, String>, &str) -> Option<String> + Send + Sync;

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

/// `#[derive(Debug)]` doesn't reach here — `dyn Fn` isn't `Debug` — so
/// `Debug` is hand-written just below, printing `doi_resolver` as
/// present/absent rather than skipping the derive on the whole struct.
#[derive(Clone)]
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
    /// Online DOI verification hook (`jss-lint --crossref`). `None`
    /// (the default, always true on the wasm target) keeps
    /// `JSS-REFS-003` offline. Not part of `.jss-lint.toml`/CLI-flag
    /// merging below — injected directly by the caller, same as Python's
    /// `cfg = replace(cfg, doi_resolver=...)` in `cli.py`.
    pub doi_resolver: Option<Arc<DoiResolver>>,
}

impl std::fmt::Debug for ToolConfig {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("ToolConfig")
            .field("journal", &self.journal)
            .field("mode", &self.mode)
            .field("output", &self.output)
            .field("ignore_rules", &self.ignore_rules)
            .field("verbose", &self.verbose)
            .field("code_width", &self.code_width)
            .field("source_root", &self.source_root)
            .field("min_confidence", &self.min_confidence)
            .field("fail_on", &self.fail_on)
            .field("severity_overrides", &self.severity_overrides)
            .field("doi_resolver", &self.doi_resolver.is_some())
            .finish()
    }
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
            doi_resolver: None,
        }
    }
}

/// `.jss-lint.toml`'s filename, relative to the current working
/// directory. Mirrors `config.py::_CONFIG_FILENAME`.
pub const CONFIG_FILENAME: &str = ".jss-lint.toml";

const KNOWN_FIELDS: &[&str] = &[
    "journal",
    "mode",
    "output",
    "ignore_rules",
    "verbose",
    "code_width",
    "source_root",
    "min_confidence",
    "fail_on",
    "severity_overrides",
];

/// Values a caller (CLI flags today; any other binding tomorrow) wants
/// to layer on top of `.jss-lint.toml`. `None` means "the caller
/// didn't set this" and leaves a file-provided value (or the default)
/// untouched — mirrors `config.py::load`'s `if value is None: continue`
/// rule for `cli_overrides`.
#[derive(Debug, Clone, Default)]
pub struct RawOverrides {
    pub journal: Option<String>,
    pub mode: Option<String>,
    pub output: Option<String>,
    pub ignore_rules: Option<Vec<String>>,
    pub verbose: Option<bool>,
    pub code_width: Option<u32>,
    pub source_root: Option<PathBuf>,
    pub min_confidence: Option<String>,
    pub fail_on: Option<String>,
    pub severity_overrides: Option<HashMap<String, String>>,
}

fn toml_value_to_string_list(value: &toml::Value) -> Vec<String> {
    match value {
        toml::Value::String(s) => s
            .split(',')
            .map(|p| p.trim().to_string())
            .filter(|p| !p.is_empty())
            .collect(),
        toml::Value::Array(items) => items
            .iter()
            .filter_map(|v| v.as_str())
            .map(|s| s.trim().to_string())
            .filter(|s| !s.is_empty())
            .collect(),
        _ => Vec::new(),
    }
}

/// Reads and parses `<cwd>/.jss-lint.toml` (absent or unparsable ⇒
/// empty, silently — mirrors `config.py::_read_toml`'s "file doesn't
/// exist ⇒ `{}`"; a malformed file has no real-corpus fixture to match
/// against, so it's treated the same way rather than surfacing a
/// separate error path). Returns the known-field overrides plus any
/// top-level keys the loader doesn't recognise (sorted, for the
/// unrecognised-keys warning).
fn read_toml_overrides(cwd: &Path) -> (RawOverrides, Vec<String>) {
    let path = cwd.join(CONFIG_FILENAME);
    let Ok(contents) = std::fs::read_to_string(&path) else {
        return (RawOverrides::default(), Vec::new());
    };
    let Ok(table) = contents.parse::<toml::Table>() else {
        return (RawOverrides::default(), Vec::new());
    };

    let mut unknown_keys: Vec<String> = table
        .keys()
        .filter(|k| !KNOWN_FIELDS.contains(&k.as_str()))
        .cloned()
        .collect();
    unknown_keys.sort();

    let mut out = RawOverrides::default();
    if let Some(v) = table.get("journal").and_then(|v| v.as_str()) {
        out.journal = Some(v.to_string());
    }
    if let Some(v) = table.get("mode").and_then(|v| v.as_str()) {
        out.mode = Some(v.to_string());
    }
    if let Some(v) = table.get("output").and_then(|v| v.as_str()) {
        out.output = Some(v.to_string());
    }
    if let Some(v) = table.get("ignore_rules") {
        out.ignore_rules = Some(toml_value_to_string_list(v));
    }
    if let Some(v) = table.get("verbose").and_then(|v| v.as_bool()) {
        out.verbose = Some(v);
    }
    if let Some(v) = table.get("code_width").and_then(|v| v.as_integer()) {
        out.code_width = Some(v.max(0) as u32);
    }
    if let Some(v) = table.get("source_root").and_then(|v| v.as_str()) {
        out.source_root = Some(PathBuf::from(v));
    }
    if let Some(v) = table.get("min_confidence").and_then(|v| v.as_str()) {
        out.min_confidence = Some(v.to_string());
    }
    if let Some(v) = table.get("fail_on").and_then(|v| v.as_str()) {
        out.fail_on = Some(v.to_string());
    }
    if let Some(toml::Value::Table(t)) = table.get("severity_overrides") {
        let map = t
            .iter()
            .filter_map(|(k, v)| v.as_str().map(|s| (k.clone(), s.to_string())))
            .collect();
        out.severity_overrides = Some(map);
    }

    (out, unknown_keys)
}

/// Mirrors `config.py::_normalise_severity_overrides` + `load`'s
/// merge: unknown/invalid severity strings drop the entry (the rule
/// keeps its catalogue severity) rather than failing the whole config.
/// `mode`/`output`/`min_confidence`/`fail_on` fall back to their
/// current value on an unrecognised string — Python's dataclass fields
/// are untyped `Literal`s at runtime and would just store the bad
/// string (later comparisons silently treat it as "not that variant");
/// falling back to the current value is this port's typed-enum
/// equivalent of that same "malformed config degrades gracefully,
/// doesn't crash" intent, not a byte-parity target (no fixture
/// exercises an invalid `.jss-lint.toml`).
fn apply_overrides(cfg: &mut ToolConfig, overrides: &RawOverrides) {
    if let Some(v) = &overrides.journal {
        cfg.journal = v.clone();
    }
    if let Some(v) = &overrides.mode {
        cfg.mode = if v == "reviewer" {
            Mode::Reviewer
        } else {
            Mode::Author
        };
    }
    if let Some(v) = &overrides.output {
        cfg.output = match v.as_str() {
            "json" => OutputFormat::Json,
            "html" => OutputFormat::Html,
            "sarif" => OutputFormat::Sarif,
            _ => OutputFormat::Terminal,
        };
    }
    if let Some(v) = &overrides.ignore_rules {
        cfg.ignore_rules = v.iter().cloned().collect();
    }
    if let Some(v) = overrides.verbose {
        cfg.verbose = v;
    }
    if let Some(v) = overrides.code_width {
        cfg.code_width = v;
    }
    if let Some(v) = &overrides.source_root {
        cfg.source_root = v.clone();
    }
    if let Some(v) = &overrides.min_confidence {
        if let Some(tier) = ConfidenceTier::parse(v) {
            cfg.min_confidence = tier;
        }
    }
    if let Some(v) = &overrides.fail_on {
        if let Some(sev) = Severity::parse(v) {
            cfg.fail_on = sev;
        }
    }
    if let Some(v) = &overrides.severity_overrides {
        cfg.severity_overrides = v
            .iter()
            .filter_map(|(rule_id, sev)| {
                Severity::parse(&sev.trim().to_lowercase())
                    .map(|sev| (rule_id.trim().to_uppercase(), sev))
            })
            .collect();
    }
}

/// Builds a `ToolConfig` by merging, lowest to highest precedence:
/// `ToolConfig::default()`, then `<cwd>/.jss-lint.toml`, then
/// `cli_overrides`. Mirrors `config.py::load`, including the
/// unrecognised-TOML-keys warning (printed only when the *final*
/// merged config is verbose, matching Python's post-merge check).
pub fn load(cwd: &Path, cli_overrides: &RawOverrides) -> ToolConfig {
    let mut cfg = ToolConfig::default();
    let (file_overrides, unknown_keys) = read_toml_overrides(cwd);
    apply_overrides(&mut cfg, &file_overrides);
    apply_overrides(&mut cfg, cli_overrides);

    if !unknown_keys.is_empty() && cfg.verbose {
        eprintln!(
            "warning: {CONFIG_FILENAME} has unrecognised keys: {}",
            unknown_keys.join(", ")
        );
    }
    cfg
}
