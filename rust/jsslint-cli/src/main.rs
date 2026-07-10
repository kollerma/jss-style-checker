//! `jsslint` — standalone JSS LaTeX/BibTeX style-checker binary
//! (spec 018 Phase 4). Mirrors the bare-`PATHS` invocation of
//! `texlint.cli`'s `jss-lint` (`--journal/--mode/--output/
//! --source-root/--ignore-rules/--min-confidence/--fail-on/
//! --verbose`, directory expansion, exit-code policy).
//!
//! Not yet ported (see the plan's Phase 4 scope and this crate's
//! follow-up commits): the `explain`/`init`/`report`/`diff`/`lsp`
//! subcommands, `--fix`/`--dry-run`/`--apply`/`--fix-rule`
//! (`jsslint_core::fixer` exists but isn't wired to disk I/O here
//! yet), `--crossref` (an online, opt-in feature out of scope per the
//! plan), `.jss-lint.toml` config-file loading (CLI flags + defaults
//! only for now), and `.rnw`/`.rmd` inputs (no parser ported yet —
//! see `jsslint_core::engine`'s doc comment). `--output html` is
//! unimplemented (the plan defers HTML/PDF rendering). `--output
//! json`/`sarif` are fully wired (`jsslint_core::json_output`/
//! `jsslint_core::sarif`); `--output terminal` (the default) is wired
//! to `jsslint_core::terminal`, which targets the non-tty
//! (piped/redirected) rendering path only — see that module's doc
//! comment.

use clap::Parser;
use jsslint_core::config::{ConfidenceTier, Mode, OutputFormat, ToolConfig};
use jsslint_core::engine::{self, EngineError, ParsedDocument};
use jsslint_core::report::{ComplianceReport, Severity};
use jsslint_core::{json_output, sarif, terminal};
use std::path::{Path, PathBuf};
use std::process::ExitCode;

const SUPPORTED_SUFFIXES: &[&str] = &[".tex", ".ltx", ".bib"];
const PARSE_RULE_ID: &str = "JSS-PARSE-000";

#[derive(Parser)]
#[command(name = "jss-lint", version, about = "JSS LaTeX/BibTeX style checker")]
struct Cli {
    /// Files or directories to lint.
    paths: Vec<String>,

    #[arg(long)]
    journal: Option<String>,

    #[arg(long, value_parser = ["author", "reviewer"])]
    mode: Option<String>,

    #[arg(long, value_parser = ["terminal", "json", "html", "sarif"])]
    output: Option<String>,

    #[arg(long)]
    source_root: Option<PathBuf>,

    #[arg(long)]
    ignore_rules: Option<String>,

    #[arg(long, value_parser = ["low", "medium", "high"])]
    min_confidence: Option<String>,

    #[arg(long, value_parser = ["error", "warning", "info"])]
    fail_on: Option<String>,

    #[arg(short = 'v', long)]
    verbose: bool,
}

fn eprint_line(msg: &str) {
    eprintln!("{msg}");
}

fn main() -> ExitCode {
    let cli = Cli::parse();

    if cli.paths.is_empty() {
        eprint_line("jss-lint: at least one FILE argument is required.");
        return ExitCode::from(2);
    }

    let journal = cli.journal.clone().unwrap_or_else(|| "jss".to_string());
    if journal != "jss" {
        eprint_line(&format!(
            "jss-lint: No journal registered under '{journal}'. Known: ['jss']"
        ));
        return ExitCode::from(2);
    }

    let (sources, exit_code) = match parse_inputs(&cli.paths) {
        Ok(s) => s,
        Err(code) => return ExitCode::from(code),
    };
    let _ = exit_code;

    let document = match ParsedDocument::from_sources(&sources) {
        Ok(d) => d,
        Err(EngineError::UnsupportedSuffix(msg)) => {
            eprint_line(&format!("jss-lint: {msg}"));
            return ExitCode::from(2);
        }
    };

    let mut config = ToolConfig {
        journal,
        ..ToolConfig::default()
    };
    if let Some(mode) = &cli.mode {
        config.mode = if mode == "reviewer" {
            Mode::Reviewer
        } else {
            Mode::Author
        };
    }
    if let Some(output) = &cli.output {
        config.output = match output.as_str() {
            "json" => OutputFormat::Json,
            "html" => OutputFormat::Html,
            "sarif" => OutputFormat::Sarif,
            _ => OutputFormat::Terminal,
        };
    }
    if let Some(root) = &cli.source_root {
        config.source_root = root.clone();
    }
    if let Some(ignore) = &cli.ignore_rules {
        config.ignore_rules = ignore
            .split(',')
            .map(|s| s.trim().to_string())
            .filter(|s| !s.is_empty())
            .collect();
    }
    if let Some(tier) = &cli.min_confidence {
        config.min_confidence = ConfidenceTier::parse(tier).unwrap_or(ConfidenceTier::Low);
    }
    if let Some(fail_on) = &cli.fail_on {
        config.fail_on = Severity::parse(fail_on).unwrap_or(Severity::Warning);
    }
    config.verbose = cli.verbose;

    let report = engine::run(&config, &document);

    match config.output {
        OutputFormat::Json => print!("{}", json_output::render(&report)),
        OutputFormat::Terminal => print!("{}", terminal::render(&report, &config)),
        OutputFormat::Sarif => print!("{}", sarif::render(&report, &config)),
        OutputFormat::Html => {
            eprint_line("jss-lint: --output html is not yet implemented in this binary");
            return ExitCode::from(2);
        }
    }

    ExitCode::from(determine_exit_code(&report, config.fail_on))
}

/// All lintable files under `path`, recursively, sorted for
/// deterministic output. Mirrors `cli.py::_expand_directory`.
fn expand_directory(path: &Path) -> Vec<PathBuf> {
    let mut out = Vec::new();
    collect_lintable(path, &mut out);
    out.sort();
    out
}

fn collect_lintable(dir: &Path, out: &mut Vec<PathBuf>) {
    let Ok(entries) = std::fs::read_dir(dir) else {
        return;
    };
    for entry in entries.flatten() {
        let path = entry.path();
        if path.is_dir() {
            collect_lintable(&path, out);
        } else if is_supported_suffix(&path) {
            out.push(path);
        }
    }
}

fn is_supported_suffix(path: &Path) -> bool {
    let Some(ext) = path.extension().and_then(|e| e.to_str()) else {
        return false;
    };
    let dotted = format!(".{}", ext.to_lowercase());
    SUPPORTED_SUFFIXES.contains(&dotted.as_str())
}

/// Reads every input path (expanding directories), returning
/// `(path_string, contents)` pairs in the order Python's
/// `_parse_inputs` would process them, or an exit code on the first
/// error. Mirrors `cli.py::_parse_inputs`.
fn parse_inputs(paths: &[String]) -> Result<(Vec<(String, String)>, u8), u8> {
    let mut resolved: Vec<PathBuf> = Vec::new();
    for raw in paths {
        let path = PathBuf::from(raw);
        if path.is_dir() {
            let found = expand_directory(&path);
            if found.is_empty() {
                eprint_line(&format!(
                    "jss-lint: no lintable files under {} (looked for: {})",
                    path.display(),
                    SUPPORTED_SUFFIXES.join(", ")
                ));
                return Err(2);
            }
            resolved.extend(found);
            continue;
        }
        if !is_supported_suffix(&path) {
            let ext = path.extension().and_then(|e| e.to_str()).unwrap_or("");
            eprint_line(&format!(
                "jss-lint: unsupported file extension '.{ext}' for {} (expected one of: {})",
                path.display(),
                SUPPORTED_SUFFIXES.join(", ")
            ));
            return Err(2);
        }
        if !path.exists() {
            eprint_line(&format!("jss-lint: file not found: {}", path.display()));
            return Err(2);
        }
        resolved.push(path);
    }

    let mut sources = Vec::with_capacity(resolved.len());
    for path in resolved {
        let contents = match std::fs::read_to_string(&path) {
            Ok(c) => c,
            Err(exc) => {
                eprint_line(&format!("jss-lint: {}: {exc}", path.display()));
                return Err(2);
            }
        };
        sources.push((path.to_string_lossy().to_string(), contents));
    }
    Ok((sources, 0))
}

/// Exit 2 if any error-severity `JSS-PARSE-000` finding is present;
/// else 1 if any violation is at/above `fail_on`'s severity rank;
/// else 0. Mirrors `cli.py::_determine_exit_code`.
fn determine_exit_code(report: &ComplianceReport, fail_on: Severity) -> u8 {
    let has_fatal_parse_error = report
        .violations
        .iter()
        .any(|v| v.rule_id == PARSE_RULE_ID && v.severity == Severity::Error);
    if has_fatal_parse_error {
        return 2;
    }
    let threshold = fail_on.rank();
    if report
        .violations
        .iter()
        .any(|v| v.severity.rank() >= threshold)
    {
        return 1;
    }
    0
}
