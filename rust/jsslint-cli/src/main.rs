//! `jsslint` — standalone JSS LaTeX/BibTeX style-checker binary
//! (spec 018 Phase 4). Mirrors the bare-`PATHS` invocation of
//! `texlint.cli`'s `jss-lint` (`--journal/--mode/--output/
//! --source-root/--ignore-rules/--min-confidence/--fail-on/
//! --verbose`, directory expansion, exit-code policy).
//!
//! Not yet ported (see the plan's Phase 4 scope and this crate's
//! follow-up commits): the `explain`/`init`/`report`/`diff`/`lsp`
//! subcommands, `--crossref` (an online, opt-in feature out of scope
//! per the plan), `.jss-lint.toml` config-file loading (CLI flags +
//! defaults only for now), and `.rnw`/`.rmd` inputs (no parser ported
//! yet — see `jsslint_core::engine`'s doc comment). `--output html` is
//! unimplemented (the plan defers HTML/PDF rendering). `--output
//! json`/`sarif` are fully wired (`jsslint_core::json_output`/
//! `jsslint_core::sarif`); `--output terminal` (the default) is wired
//! to `jsslint_core::terminal`, which targets the non-tty
//! (piped/redirected) rendering path only — see that module's doc
//! comment. `--fix`/`--dry-run`/`--apply`/`--fix-rule` are wired to
//! `jsslint_core::fixer::apply_fixes`.

use clap::Parser;
use jsslint_core::catalogue;
use jsslint_core::config::{self, OutputFormat, RawOverrides};
use jsslint_core::engine::{self, EngineError, ParsedDocument};
use jsslint_core::fixer::{self, ApplyMode};
use jsslint_core::report::{ComplianceReport, Severity};
use jsslint_core::{json_output, sarif, terminal};
use std::collections::HashSet;
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

    /// Apply auto-fixes (spec 008). Atomic write per file.
    #[arg(long)]
    fix: bool,

    /// With --fix: print proposed fixes as a unified diff; do not write.
    #[arg(long = "dry-run")]
    dry_run: bool,

    /// With --fix: prompt [y/n/a/q] per fix.
    #[arg(long)]
    apply: bool,

    /// Repeatable; limits --fix to the named rule ids.
    #[arg(long = "fix-rule")]
    fix_rules: Vec<String>,
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

    let cli_overrides = RawOverrides {
        journal: cli.journal.clone(),
        mode: cli.mode.clone(),
        output: cli.output.clone(),
        ignore_rules: cli.ignore_rules.as_deref().map(|s| {
            s.split(',')
                .map(|p| p.trim().to_string())
                .filter(|p| !p.is_empty())
                .collect()
        }),
        verbose: if cli.verbose { Some(true) } else { None },
        code_width: None,
        source_root: cli.source_root.clone(),
        min_confidence: cli.min_confidence.clone(),
        fail_on: cli.fail_on.clone(),
        severity_overrides: None,
    };
    let cwd = std::env::current_dir().unwrap_or_else(|_| PathBuf::from("."));
    let config = config::load(&cwd, &cli_overrides);

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

    // Mirrors `cli.py`'s `load_journal(cfg.journal)` call (which runs
    // after `_parse_inputs`): only the "jss" journal is registered in
    // this port (no journal registry exists), so any other value —
    // from `.jss-lint.toml` or `--journal` — is a
    // `JournalNotFoundError` equivalent.
    if config.journal != "jss" {
        eprint_line(&format!(
            "jss-lint: No journal registered under '{}'. Known: ['jss']",
            config.journal
        ));
        return ExitCode::from(2);
    }

    let report = engine::run(&config, &document);

    if cli.dry_run && !cli.fix {
        eprint_line("jss-lint: --dry-run requires --fix");
        return ExitCode::from(2);
    }
    if cli.apply && !cli.fix {
        eprint_line("jss-lint: --apply requires --fix");
        return ExitCode::from(2);
    }
    if cli.dry_run && cli.apply {
        eprint_line("jss-lint: --dry-run and --apply are mutually exclusive");
        return ExitCode::from(2);
    }
    if cli.fix {
        let scope: Option<HashSet<String>> = if cli.fix_rules.is_empty() {
            None
        } else {
            let mut known_ids: HashSet<String> = report
                .violations
                .iter()
                .map(|v| v.rule_id.clone())
                .collect();
            for rule in catalogue::all_rules() {
                known_ids.insert(rule.rule_id.to_string());
            }
            for rid in &cli.fix_rules {
                if !known_ids.contains(rid) {
                    eprint_line(&format!("jss-lint: unknown --fix-rule '{rid}'"));
                    return ExitCode::from(2);
                }
            }
            Some(cli.fix_rules.iter().cloned().collect())
        };
        let mode = if cli.dry_run {
            ApplyMode::DryRun
        } else if cli.apply {
            ApplyMode::Interactive
        } else {
            ApplyMode::Write
        };
        let stdin = std::io::stdin();
        let mut stdin_lock = stdin.lock();
        let mut stdout = std::io::stdout();
        let mut stderr = std::io::stderr();
        let fix_report = fixer::apply_fixes(
            &report,
            mode,
            scope.as_ref(),
            &mut stdin_lock,
            &mut stdout,
            &mut stderr,
        );
        if !fix_report.rejected.is_empty() {
            return ExitCode::from(2);
        }
    }

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
