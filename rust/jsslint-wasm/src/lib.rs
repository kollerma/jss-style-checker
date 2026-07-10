//! Browser/npm binding (spec 018 Phase 5), built with `wasm-bindgen`.
//! **Hard constraint (see the plan's network-dependency callout): this
//! crate must never link anything equivalent to `texlint.crossref`'s
//! live DOI verification.** The privacy promise ("manuscripts never
//! leave the machine") depends on that being true by construction, not
//! a runtime flag default — satisfied here simply by not depending on
//! anything network-capable at all: `jsslint-core` has none, and this
//! binding adds none.
//!
//! `.jss-lint.toml` loading degrades gracefully rather than being
//! specially disabled for this target: `wasm32-unknown-unknown` has no
//! real filesystem, so `jsslint_core::config::load`'s `std::fs::
//! read_to_string` call simply always errors, which its own "file
//! missing → defaults" tolerance already handles — no special-casing
//! needed, and no path on this target ever touches anything outside
//! the in-memory `files` the caller passes in.

use jsslint_core::config::{self, RawOverrides};
use jsslint_core::engine::ParsedDocument;
use jsslint_core::{engine, html_output, json_output, sarif, terminal};
use serde::Deserialize;
use wasm_bindgen::prelude::*;

/// Mirrors `jsslint_py::render`'s parameter shape, as a single
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
}

/// Lints `request.files` and renders the report in `request.output`
/// format. Mirrors `jsslint_py::render` / `jsslint-cli`'s bare-lint
/// invocation. `request` is a JS object shaped like `LintRequest`
/// (camelCase keys: `files`, `journal`, `mode`, `output`,
/// `ignoreRules`, `minConfidence`, `failOn`, `sourceRoot`, `verbose`).
#[wasm_bindgen]
pub fn render(request: JsValue) -> Result<String, JsValue> {
    let req: LintRequest = serde_wasm_bindgen::from_value(request)
        .map_err(|e| JsValue::from_str(&format!("invalid lint request: {e}")))?;

    let document =
        ParsedDocument::from_sources(&req.files).map_err(|e| JsValue::from_str(&e.to_string()))?;

    let overrides = RawOverrides {
        journal: req.journal,
        mode: req.mode,
        output: req.output,
        ignore_rules: req.ignore_rules.map(|s| {
            s.split(',')
                .map(|p| p.trim().to_string())
                .filter(|p| !p.is_empty())
                .collect()
        }),
        verbose: req.verbose,
        code_width: None,
        source_root: req.source_root.map(std::path::PathBuf::from),
        min_confidence: req.min_confidence,
        fail_on: req.fail_on,
        severity_overrides: None,
    };
    // No meaningful "current working directory" in a browser; `.` is
    // never resolvable to a real `.jss-lint.toml` on this target
    // anyway (see module doc comment), so this is just a stable,
    // harmless base path.
    let cfg = config::load(std::path::Path::new("."), &overrides);
    let report = engine::run(&cfg, &document);

    let rendered = match cfg.output {
        config::OutputFormat::Json => json_output::render(&report),
        config::OutputFormat::Sarif => sarif::render(&report, &cfg),
        config::OutputFormat::Terminal => terminal::render(&report, &cfg),
        config::OutputFormat::Html => html_output::render(&report, cfg.mode),
    };
    Ok(rendered)
}
