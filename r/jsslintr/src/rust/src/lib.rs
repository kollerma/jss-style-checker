//! R binding (spec 018 Phase 5), built with `extendr`. Exposes
//! `jss_lint(files, ...)` — the same rule engine `jsslint-cli`,
//! `jsslint-wasm`, and `jsslint_py` all wrap, adapted to R's data
//! model: `files` is a named character vector (names = paths, values
//! = file contents) rather than a list of pairs, since that's the
//! idiomatic R shape (`c(path1 = contents1, path2 = contents2)`).
//!
//! `R/extendr-wrappers.R` is regenerated from this crate's own
//! extendr metadata by `document.rs` on every build (see
//! `src/Makevars`) — never hand-edited.

use extendr_api::prelude::*;
use jsslint_core::config::{self, RawOverrides};
use jsslint_core::engine::{self, ParsedDocument};
use jsslint_core::{html_output, json_output, sarif, terminal};

/// Lints `files` and renders the report in `output` format. Mirrors
/// `jsslint_py::render` / the WASM binding's `render()`.
/// @param files A named character vector: names are file paths
///   (`.tex`/`.ltx`/`.bib`), values are the file contents.
/// @param journal Journal identifier (default: `"jss"`).
/// @param mode `"author"` or `"reviewer"` (default: `"author"`).
/// @param output `"terminal"`, `"json"`, `"sarif"`, or `"html"`
///   (default: `"terminal"`).
/// @param ignore_rules Comma-separated rule ids to suppress.
/// @param min_confidence `"low"`, `"medium"`, or `"high"`.
/// @param fail_on `"error"`, `"warning"`, or `"info"`.
/// @param source_root Base directory for SARIF artifact URIs.
/// @param verbose Enable diagnostic output on stderr.
/// @return The rendered report, as a single string.
/// @export
#[extendr]
#[allow(clippy::too_many_arguments)]
fn render(
    files: Robj,
    #[extendr(default = "NULL")] journal: Option<String>,
    #[extendr(default = "NULL")] mode: Option<String>,
    #[extendr(default = "NULL")] output: Option<String>,
    #[extendr(default = "NULL")] ignore_rules: Option<String>,
    #[extendr(default = "NULL")] min_confidence: Option<String>,
    #[extendr(default = "NULL")] fail_on: Option<String>,
    #[extendr(default = "NULL")] source_root: Option<String>,
    #[extendr(default = "NULL")] verbose: Option<bool>,
) -> extendr_api::Result<String> {
    let names: Vec<String> = files
        .names()
        .ok_or_else(|| Error::from("files must be a named character vector".to_string()))?
        .map(|s| s.to_string())
        .collect();
    let values: Vec<String> = files
        .as_str_vector()
        .ok_or_else(|| Error::from("files must be a character vector".to_string()))?
        .into_iter()
        .map(|s| s.to_string())
        .collect();
    if names.len() != values.len() {
        return Err(Error::from(
            "files: names and values must be the same length".to_string(),
        ));
    }
    let file_pairs: Vec<(String, String)> = names.into_iter().zip(values).collect();

    let document =
        ParsedDocument::from_sources(&file_pairs).map_err(|e| Error::from(e.to_string()))?;

    let overrides = RawOverrides {
        journal,
        mode,
        output,
        ignore_rules: ignore_rules.map(|s| {
            s.split(',')
                .map(|p| p.trim().to_string())
                .filter(|p| !p.is_empty())
                .collect()
        }),
        verbose,
        code_width: None,
        source_root: source_root.map(std::path::PathBuf::from),
        min_confidence,
        fail_on,
        severity_overrides: None,
    };
    let cwd = std::env::current_dir().unwrap_or_else(|_| std::path::PathBuf::from("."));
    let cfg = config::load(&cwd, &overrides);
    let report = engine::run(&cfg, &document);

    let rendered = match cfg.output {
        config::OutputFormat::Json => json_output::render(&report),
        config::OutputFormat::Sarif => sarif::render(&report, &cfg),
        config::OutputFormat::Terminal => terminal::render(&report, &cfg),
        config::OutputFormat::Html => html_output::render(&report, cfg.mode),
    };
    Ok(rendered)
}

extendr_module! {
    mod jsslintr;
    fn render;
}
