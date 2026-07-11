//! Python binding (spec 018 Phase 5), built with PyO3 + maturin.
//! Published to PyPI as `jsslint`, importable as `import jsslint`.
//! Exposes the same rule engine `jsslint-cli` wraps, callable
//! in-process on in-memory `(path, contents)` pairs rather than only
//! against files on disk — which also makes this binding the
//! in-process parity oracle the porting plan calls for: a single
//! Python test can call both `texlint.core.engine.run` and
//! `jsslint.render` on the same input and diff the results,
//! without shelling out to the compiled CLI binary the way every
//! `tests/*_parity.rs` differential test in this workspace does.

use jsslint_core::config::{self, RawOverrides};
use jsslint_core::engine::ParsedDocument;
use jsslint_core::{engine, html_output, json_output, sarif, terminal};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

/// Lints `files` (a list of `(path, contents)` pairs — `path`'s
/// extension dispatches `.tex`/`.ltx` to the LaTeX parser and `.bib`
/// to the BibTeX parser, matching `ParsedDocument::from_sources`) and
/// renders the report in the requested `output` format. Mirrors
/// `jsslint-cli`'s bare-lint invocation: `journal`/`mode`/`output`/
/// `ignore_rules`/`min_confidence`/`fail_on`/`source_root`/`verbose`
/// are the same CLI-flag-equivalent overrides, layered over
/// `.jss-lint.toml` (read from the current working directory, same as
/// the CLI) and `ToolConfig::default()`.
#[pyfunction]
#[pyo3(signature = (
    files,
    journal=None,
    mode=None,
    output=None,
    ignore_rules=None,
    min_confidence=None,
    fail_on=None,
    source_root=None,
    verbose=None,
))]
#[allow(clippy::too_many_arguments)]
fn render(
    files: Vec<(String, String)>,
    journal: Option<String>,
    mode: Option<String>,
    output: Option<String>,
    ignore_rules: Option<String>,
    min_confidence: Option<String>,
    fail_on: Option<String>,
    source_root: Option<String>,
    verbose: Option<bool>,
) -> PyResult<String> {
    let document =
        ParsedDocument::from_sources(&files).map_err(|e| PyValueError::new_err(e.to_string()))?;

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

#[pymodule]
fn jsslint(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(render, m)?)?;
    Ok(())
}
