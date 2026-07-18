//! Browser/npm binding, built with `wasm-bindgen`.
//! **Hard constraint: this crate must never link anything network-capable
//! at all** — in particular never `jsslint-crossref`, the crate that ports
//! `texlint.crossref`'s live DOI verification for `jss-lint --crossref`
//! (see that crate's module doc). The privacy promise ("manuscripts never
//! leave the machine") depends on that being true by construction, not a
//! runtime flag default: `jsslint-core` depends on nothing network-capable
//! and only exposes an inert injection hook (`config::DoiResolver`) that
//! this binding never fills in, and this binding itself adds no network
//! dependency either. Checkable, not just asserted: `cargo tree -p
//! jsslint-wasm` never mentions `jsslint-crossref` or `ureq`.
//!
//! `.jss-lint.toml` loading degrades gracefully rather than being
//! specially disabled for this target: `wasm32-unknown-unknown` has no
//! real filesystem, so `jsslint_core::config::load`'s `std::fs::
//! read_to_string` call simply always errors, which its own "file
//! missing → defaults" tolerance already handles — no special-casing
//! needed, and no path on this target ever touches anything outside
//! the in-memory `files` the caller passes in.

use std::collections::HashMap;

use jsslint_core::config::{self, RawOverrides};
use jsslint_core::engine::ParsedDocument;
use jsslint_core::report::Severity;
use jsslint_core::{engine, fixer, html_output, json_output, sarif, terminal};
use serde::{Deserialize, Serialize};
use wasm_bindgen::prelude::*;

/// Mirrors `jsslint::render`'s parameter shape (the PyO3 binding), as a single
/// structured object (idiomatic for a JS caller) rather than many
/// positional optional arguments.
#[derive(Deserialize)]
#[serde(rename_all = "camelCase")]
struct LintRequest {
    files: Vec<(String, String)>,
    journal: Option<String>,
    mode: Option<String>,
    output: Option<String>,
    ignore_rules: Option<String>,
    min_confidence: Option<String>,
    fail_on: Option<String>,
    source_root: Option<String>,
    verbose: Option<bool>,
    code_width: Option<u32>,
    severity_overrides: Option<HashMap<String, String>>,
}

fn overrides_from(req: &LintRequest) -> RawOverrides {
    RawOverrides {
        journal: req.journal.clone(),
        mode: req.mode.clone(),
        output: req.output.clone(),
        ignore_rules: req.ignore_rules.as_ref().map(|s| {
            s.split(',')
                .map(|p| p.trim().to_string())
                .filter(|p| !p.is_empty())
                .collect()
        }),
        verbose: req.verbose,
        code_width: req.code_width,
        // No meaningful cwd in a browser; `.` never resolves to a real
        // `.jss-lint.toml` on this target (see module docs), so it's just a
        // stable, harmless base path.
        source_root: req.source_root.as_ref().map(std::path::PathBuf::from),
        min_confidence: req.min_confidence.clone(),
        fail_on: req.fail_on.clone(),
        severity_overrides: req.severity_overrides.clone(),
    }
}

fn lint(
    req: &LintRequest,
) -> Result<(config::ToolConfig, jsslint_core::report::ComplianceReport), JsValue> {
    let document =
        ParsedDocument::from_sources(&req.files).map_err(|e| JsValue::from_str(&e.to_string()))?;
    let cfg = config::load(std::path::Path::new("."), &overrides_from(req));
    let report = engine::run(&cfg, &document);
    Ok((cfg, report))
}

/// Lints `request.files` and renders the report in `request.output`
/// format. Mirrors `jsslint::render` / `jsslint-cli`'s bare-lint
/// invocation. `request` is a JS object shaped like `LintRequest`
/// (camelCase keys: `files`, `journal`, `mode`, `output`, `ignoreRules`,
/// `minConfidence`, `failOn`, `sourceRoot`, `verbose`, `codeWidth`,
/// `severityOverrides`).
#[wasm_bindgen]
pub fn render(request: JsValue) -> Result<String, JsValue> {
    let req: LintRequest = serde_wasm_bindgen::from_value(request)
        .map_err(|e| JsValue::from_str(&format!("invalid lint request: {e}")))?;
    let (cfg, report) = lint(&req)?;

    let rendered = match cfg.output {
        config::OutputFormat::Json => json_output::render(&report),
        config::OutputFormat::Sarif => sarif::render(&report, &cfg),
        config::OutputFormat::Terminal => terminal::render(&report, &cfg),
        config::OutputFormat::Html => html_output::render(&report, cfg.mode),
    };
    Ok(rendered)
}

/// Applies every available auto-fix in memory and returns the files whose
/// contents changed, as `[path, fixedContents]` pairs (same shape as the
/// `files` input). Files with no applicable fix are omitted. Takes the same
/// request shape as `render`; the `output` field is ignored. No filesystem
/// access — the caller writes the results back however it likes.
#[wasm_bindgen]
pub fn fix(request: JsValue) -> Result<JsValue, JsValue> {
    let req: LintRequest = serde_wasm_bindgen::from_value(request)
        .map_err(|e| JsValue::from_str(&format!("invalid fix request: {e}")))?;
    let (_cfg, report) = lint(&req)?;

    let mut by_file: std::collections::BTreeMap<String, Vec<fixer::Candidate>> =
        std::collections::BTreeMap::new();
    for c in fixer::candidates_from_violations(&report.violations) {
        by_file.entry(c.file.clone()).or_default().push(c);
    }

    let originals: HashMap<&str, &str> = req
        .files
        .iter()
        .map(|(p, c)| (p.as_str(), c.as_str()))
        .collect();

    let mut changed: Vec<(String, String)> = Vec::new();
    for (file, candidates) in by_file {
        let (applied, _skipped) = fixer::resolve_conflicts(candidates);
        if applied.is_empty() {
            continue;
        }
        let Some(source) = originals.get(file.as_str()) else {
            continue;
        };
        let chars: Vec<char> = source.chars().collect();
        let fixed = fixer::apply_to_text(&chars, &applied);
        if &fixed != source {
            changed.push((file, fixed));
        }
    }

    serde_wasm_bindgen::to_value(&changed)
        .map_err(|e| JsValue::from_str(&format!("failed to serialize fix result: {e}")))
}

#[derive(Serialize)]
struct WasmFix {
    /// Character offsets into the file (same convention the whole engine uses).
    start: usize,
    end: usize,
    replacement: String,
    description: String,
}

#[derive(Serialize)]
struct WasmViolation {
    rule_id: String,
    severity: &'static str,
    message: String,
    /// 1-based.
    line: u32,
    /// 1-based; null when the rule operates at line granularity.
    column: Option<u32>,
    /// Present only when the violation carries a safe auto-fix.
    fix: Option<WasmFix>,
}

/// Lints `request.files` and returns the violations as structured data
/// (camelCase), each carrying its auto-fix (`fix`) when one exists. Unlike
/// `render(output:"json")` — whose `fix` field is hardcoded null for
/// byte-parity with the Python contract — this exposes the real fixes so a
/// UI (e.g. the VS Code extension) can offer per-diagnostic quick fixes.
#[wasm_bindgen]
pub fn analyze(request: JsValue) -> Result<JsValue, JsValue> {
    let req: LintRequest = serde_wasm_bindgen::from_value(request)
        .map_err(|e| JsValue::from_str(&format!("invalid analyze request: {e}")))?;
    let (_cfg, report) = lint(&req)?;

    let out: Vec<WasmViolation> = report
        .violations
        .iter()
        .map(|v| WasmViolation {
            rule_id: v.rule_id.clone(),
            severity: match v.severity {
                Severity::Error => "error",
                Severity::Warning => "warning",
                Severity::Info => "info",
            },
            message: v.message.clone(),
            line: v.line,
            column: v.column,
            fix: v.fix.as_ref().map(|f| WasmFix {
                start: f.start,
                end: f.end,
                replacement: f.replacement.clone(),
                description: f.description.clone(),
            }),
        })
        .collect();

    serde_wasm_bindgen::to_value(&out)
        .map_err(|e| JsValue::from_str(&format!("failed to serialize analyze result: {e}")))
}
