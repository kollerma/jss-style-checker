//! `jsslint` — standalone JSS LaTeX/BibTeX style-checker binary
//! (spec 018 Phase 4). Mirrors the bare-`PATHS` invocation of
//! `texlint.cli`'s `jss-lint` (`--journal/--mode/--output/
//! --source-root/--ignore-rules/--min-confidence/--fail-on/
//! --verbose`, directory expansion, exit-code policy).
//!
//! `.jss-lint.toml` is loaded (`jsslint_core::config::load`);
//! `--fix`/`--dry-run`/`--apply`/`--fix-rule` are wired to
//! `jsslint_core::fixer::apply_fixes`. All four `--output` formats are
//! fully wired: `json`/`sarif` (`jsslint_core::json_output`/
//! `jsslint_core::sarif`), `terminal` (the default, via
//! `jsslint_core::terminal`, which targets the non-tty
//! piped/redirected rendering path only — see that module's doc
//! comment), and `html` (`jsslint_core::html_output`, author/reviewer
//! mode).
//!
//! The `explain`, `diff`, `init`, `report`, and `lsp` subcommands are
//! all wired (`jsslint_core::explain`/`jsslint_core::diff`/
//! `jsslint_core::conformance`; `init`'s logic lives in this crate's
//! own `init` module and `lsp`'s in `lsp_server`, not `jsslint-core`
//! — see each module's doc comment), via a hand-rolled dispatch in
//! `main()` mirroring `cli.py`'s Click-group hack
//! (`invoke_without_command=True` plus manually forwarding when
//! `paths[0]` matches a registered subcommand name) — clap's derive
//! subcommand DSL doesn't cleanly coexist with a catch-all `paths:
//! Vec<String>` positional on the same struct. `report --format html`
//! is byte-for-byte identical to Python's (`conformance.html.j2`,
//! rendered via `jsslint_core::conformance::render_html` — a separate
//! template from `--output html`'s `author.html.j2`/
//! `reviewer.html.j2`). `report --format pdf` renders a self-contained
//! but *not* byte/visually-identical PDF via this crate's own
//! `report_pdf` module (`genpdf`, pure Rust — see that module's doc
//! comment and `rust/README.md` for why parity with WeasyPrint's
//! output isn't the goal there). `--crossref`/`--crossref-mailto` (online,
//! opt-in `JSS-REFS-003` DOI verification) are wired via
//! `jsslint_crossref::make_resolver` — see that crate's module doc for
//! why the network client lives there and not in `jsslint-core`.
//! `.rnw`/`.rmd` inputs ARE supported (`SUPPORTED_SUFFIXES`, below)
//! — see `jsslint_core::engine`'s doc comment for the parsers.

mod init;
mod localdate;
mod lsp_server;
mod report_pdf;

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

/// Mirrors `cli.py::_SUPPORTED_SUFFIXES`. Kept in the same sorted order
/// Python's `', '.join(sorted(_SUPPORTED_SUFFIXES))` produces, since
/// this array is also joined verbatim into user-facing messages below.
const SUPPORTED_SUFFIXES: &[&str] = &[".bib", ".ltx", ".rmd", ".rnw", ".tex"];
const PARSE_RULE_ID: &str = "JSS-PARSE-000";

#[derive(Parser)]
#[command(name = "jss-lint", version, about = "JSS LaTeX/BibTeX style checker")]
struct Cli {
    /// Files or directories to lint.
    paths: Vec<String>,

    #[arg(long)]
    journal: Option<String>,

    #[arg(long, value_parser = ["author", "reviewer"], ignore_case = true)]
    mode: Option<String>,

    #[arg(long, value_parser = ["terminal", "json", "html", "sarif"], ignore_case = true)]
    output: Option<String>,

    #[arg(long)]
    source_root: Option<PathBuf>,

    #[arg(long)]
    ignore_rules: Option<String>,

    #[arg(long, value_parser = ["low", "medium", "high"], ignore_case = true)]
    min_confidence: Option<String>,

    #[arg(long, value_parser = ["error", "warning", "info"], ignore_case = true)]
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

    /// Online mode: verify missing DOIs against Crossref (articles,
    /// books, proceedings) and CRAN (package @Manual entries).
    /// JSS-REFS-003 then reports the exact DOI to add and suppresses
    /// the advisory when no DOI exists. Combine with --fix to write
    /// the DOIs into the .bib. Needs network access; off by default.
    #[arg(long)]
    crossref: bool,

    /// Contact e-mail for the Crossref polite pool (recommended when
    /// using --crossref).
    #[arg(long = "crossref-mailto")]
    crossref_mailto: Option<String>,
}

/// Subcommand names this port currently registers. Mirrors `cli.py`'s
/// `if paths and paths[0] in main.commands:` forwarding check, scoped
/// to only the subcommands actually wired so far.
const REGISTERED_SUBCOMMANDS: &[&str] = &["explain", "diff", "init", "report", "lsp"];

#[derive(Parser)]
#[command(
    name = "jss-lint explain",
    about = "Explain a rule, or list the catalogue"
)]
struct ExplainArgs {
    /// Rule id to explain; omit to list every rule by category.
    rule_id: Option<String>,

    #[arg(long = "format", value_parser = ["terminal", "markdown"], default_value = "terminal", ignore_case = true)]
    format: String,

    /// Reserved for fixture pull-through; currently a no-op.
    #[arg(long)]
    #[allow(dead_code)]
    example: bool,
}

fn run_explain(args: &[String]) -> ExitCode {
    let mut parsed = ExplainArgs::try_parse_from(
        std::iter::once("jss-lint-explain".to_string()).chain(args.iter().cloned()),
    )
    .unwrap_or_else(|e| e.exit());
    // `ignore_case = true` on `--format` accepts mixed case (mirrors
    // Python's `click.Choice(..., case_sensitive=False)`) but — unlike
    // Click, which normalizes to the declared-choice casing — preserves
    // whatever casing the user typed. Lowercase explicitly so the
    // `parsed.format` string comparisons below keep working unmodified.
    parsed.format = parsed.format.to_lowercase();

    match jsslint_core::explain::render(parsed.rule_id.as_deref(), &parsed.format) {
        Ok(out) => {
            print!("{out}");
            ExitCode::from(0)
        }
        Err(unknown) => {
            eprint_line(&format!("error: unknown rule id {unknown}"));
            let suggestions = jsslint_core::explain::did_you_mean(&unknown);
            if !suggestions.is_empty() {
                eprint_line(&format!("did you mean: {}", suggestions.join(", ")));
            }
            ExitCode::from(2)
        }
    }
}

#[derive(Parser)]
#[command(name = "jss-lint diff", about = "Diff two --output json reports")]
struct DiffArgs {
    old: PathBuf,
    new: PathBuf,

    #[arg(long = "ignore-line-drift")]
    ignore_line_drift: bool,

    #[arg(long = "format", value_parser = ["terminal", "markdown", "json"], default_value = "terminal", ignore_case = true)]
    format: String,
}

/// Reads and schema-validates one `diff` input file. On failure,
/// prints an error and returns the exit code to propagate.
///
/// Two of Python's error paths aren't byte-matched here: real
/// `jss-lint diff` uses `click.Path(exists=True, ...)` on the `OLD`/
/// `NEW` arguments, so a missing file is actually rejected by Click's
/// own multi-line usage-error formatter *before* `diff_cmd` ever runs
/// (the custom `_eprint(f"jss-lint: failed to read {p}: {exc}")` path
/// in `cli.py::_load` is effectively dead for "file not found", only
/// reachable for rarer `OSError`s like a permission failure). And a
/// malformed-JSON-content message comes from the two languages'
/// completely different JSON parsers, so `str(json.JSONDecodeError)`
/// and `serde_json::Error`'s `Display` were never going to match
/// character-for-character. Both are edge cases with no real-corpus
/// fixture; only the exit code (2) is guaranteed to match, and the
/// `SchemaMismatch` path (this crate's own message text, mirrored
/// exactly) still gets byte parity.
fn load_diff_input(path: &Path) -> Result<Vec<serde_json::Value>, ExitCode> {
    let contents = match std::fs::read_to_string(path) {
        Ok(c) => c,
        Err(exc) => {
            eprint_line(&format!(
                "jss-lint: failed to read {}: {exc}",
                path.display()
            ));
            return Err(ExitCode::from(2));
        }
    };
    let payload: serde_json::Value = match serde_json::from_str(&contents) {
        Ok(v) => v,
        Err(exc) => {
            eprint_line(&format!(
                "jss-lint: failed to read {}: {exc}",
                path.display()
            ));
            return Err(ExitCode::from(2));
        }
    };
    match jsslint_core::diff::validate_payload(&payload, &path.display().to_string()) {
        Ok(v) => Ok(v),
        Err(mismatch) => {
            eprint_line(&format!("jss-lint: {mismatch}"));
            Err(ExitCode::from(2))
        }
    }
}

fn run_diff(args: &[String]) -> ExitCode {
    let mut parsed = DiffArgs::try_parse_from(
        std::iter::once("jss-lint-diff".to_string()).chain(args.iter().cloned()),
    )
    .unwrap_or_else(|e| e.exit());
    // See `run_explain`'s comment on `ignore_case = true`: clap preserves
    // the user's casing, Click normalizes it, so we normalize by hand.
    parsed.format = parsed.format.to_lowercase();

    let old = match load_diff_input(&parsed.old) {
        Ok(v) => v,
        Err(code) => return code,
    };
    let new = match load_diff_input(&parsed.new) {
        Ok(v) => v,
        Err(code) => return code,
    };

    let diff = jsslint_core::diff::compare(&old, &new, parsed.ignore_line_drift, None);
    let rendered = match parsed.format.as_str() {
        "markdown" => jsslint_core::diff::render_markdown(&diff),
        "json" => jsslint_core::diff::render_json(&diff),
        _ => jsslint_core::diff::render_terminal(&diff),
    };
    print!("{rendered}");
    if diff.introduced.is_empty() {
        ExitCode::from(0)
    } else {
        ExitCode::from(1)
    }
}

#[derive(Parser)]
#[command(
    name = "jss-lint init",
    about = "Initialise .jss-lint.toml for a manuscript directory"
)]
struct InitArgs {
    /// File or directory to lint before writing the config.
    path: Option<String>,

    #[arg(long)]
    force: bool,

    #[arg(long = "dry-run")]
    dry_run: bool,

    #[arg(long, default_value_t = 0.90)]
    threshold: f64,
}

/// `Path.__truediv__`/construction in Python's `pathlib` drops bare
/// `.` components (`Path(".") / "x"` == `PosixPath("x")`, not
/// `"./x"`) — `std::path::PathBuf::join` doesn't do this, so a literal
/// `"./x"` or a `.`-joined path would otherwise print with a `./`
/// prefix real `jss-lint init` never shows (its `config_path`/error
/// messages come from `Path` objects throughout). Doesn't collapse a
/// bare `"."` to empty, matching `str(Path("."))` == `"."`.
pub(crate) fn pathlib_normalize(p: &Path) -> PathBuf {
    let filtered: PathBuf = p
        .components()
        .filter(|c| !matches!(c, std::path::Component::CurDir))
        .collect();
    if filtered.as_os_str().is_empty() {
        PathBuf::from(".")
    } else {
        filtered
    }
}

/// `path`'s existence isn't pre-validated the way Click's
/// `click.Path(exists=True, ...)` gates real `jss-lint init` — same
/// documented scope decision as `diff`'s `OLD`/`NEW` arguments (see
/// `load_diff_input`'s doc comment): only the exit code, not Click's
/// own usage-error text, is guaranteed to match for a missing path.
fn run_init(args: &[String]) -> ExitCode {
    let parsed = InitArgs::try_parse_from(
        std::iter::once("jss-lint-init".to_string()).chain(args.iter().cloned()),
    )
    .unwrap_or_else(|e| e.exit());
    let path_str = parsed.path.clone().unwrap_or_else(|| ".".to_string());
    let target = pathlib_normalize(&PathBuf::from(&path_str));
    if !target.exists() {
        eprint_line(&format!("jss-lint: path does not exist: {path_str}"));
        return ExitCode::from(2);
    }

    let (target_dir, candidates): (PathBuf, Vec<PathBuf>) = if target.is_dir() {
        let mut found: Vec<PathBuf> = std::fs::read_dir(&target)
            .map(|entries| {
                entries
                    .flatten()
                    .map(|e| e.path())
                    .filter(|p| p.is_file() && is_supported_suffix(p))
                    .map(|p| pathlib_normalize(&p))
                    .collect()
            })
            .unwrap_or_default();
        found.sort();
        (target.clone(), found)
    } else {
        (
            target
                .parent()
                .map(|p| p.to_path_buf())
                .unwrap_or_else(|| PathBuf::from(".")),
            vec![target.clone()],
        )
    };

    if candidates.is_empty() {
        eprint_line(&format!(
            "jss-lint: no lintable files under {}",
            target.display()
        ));
        return ExitCode::from(2);
    }

    let sources: Result<Vec<(String, String)>, std::io::Error> = candidates
        .iter()
        .map(|p| std::fs::read_to_string(p).map(|c| (p.to_string_lossy().into_owned(), c)))
        .collect();
    let sources = match sources {
        Ok(s) => s,
        Err(exc) => {
            eprint_line(&format!("jss-lint: {exc}"));
            return ExitCode::from(2);
        }
    };
    let document = match ParsedDocument::from_sources(&sources) {
        Ok(d) => d,
        Err(EngineError::UnsupportedSuffix(msg)) => {
            eprint_line(&format!("jss-lint: {msg}"));
            return ExitCode::from(2);
        }
    };

    let cwd = std::env::current_dir().unwrap_or_else(|_| PathBuf::from("."));
    let cfg = config::load(&cwd, &RawOverrides::default());
    if cfg.journal != "jss" {
        eprint_line(&format!(
            "jss-lint: No journal registered under '{}'. Known: ['jss']",
            cfg.journal
        ));
        return ExitCode::from(2);
    }
    let report = engine::run(&cfg, &document);

    match init::run(
        &target_dir,
        &report,
        parsed.force,
        parsed.dry_run,
        parsed.threshold,
        &cfg.journal,
        None,
    ) {
        Ok(result) => {
            if parsed.dry_run {
                println!("Proposed .jss-lint.toml (dry-run; nothing written):");
                println!("{}", result.contents);
            } else {
                println!("Wrote {}", result.config_path.display());
                let plural = if result.suppressed_count == 1 {
                    ""
                } else {
                    "s"
                };
                println!(
                    "({} distinct rules in {} violations; {} rule{plural} auto-suppressed by precision DB)",
                    result.must_fix_count, result.total_violations, result.suppressed_count
                );
            }
            ExitCode::from(0)
        }
        Err(init::InitError::Refused(msg)) | Err(init::InitError::InvalidThreshold(msg)) => {
            eprint_line(&format!("jss-lint: {msg}"));
            ExitCode::from(2)
        }
    }
}

#[derive(Parser)]
#[command(
    name = "jss-lint report",
    about = "Render a one-page conformance report"
)]
struct ReportArgs {
    /// File or directory to lint.
    path: String,

    #[arg(long = "format", value_parser = ["md", "html", "pdf"], default_value = "md", ignore_case = true)]
    format: String,

    /// Write the report to FILE instead of stdout.
    #[arg(long)]
    out: Option<PathBuf>,

    /// Override the manuscript title (default: extracted from \title{}).
    #[arg(long)]
    title: Option<String>,

    /// Override the manuscript author (default: extracted from \author{}).
    #[arg(long)]
    author: Option<String>,
}

/// `path`'s existence isn't pre-validated the way Click's
/// `click.Path(exists=True)` gates real `jss-lint report` — same
/// documented scope decision as `diff`/`init` (see
/// `load_diff_input`'s doc comment).
fn run_report(args: &[String]) -> ExitCode {
    let mut parsed = ReportArgs::try_parse_from(
        std::iter::once("jss-lint-report".to_string()).chain(args.iter().cloned()),
    )
    .unwrap_or_else(|e| e.exit());
    // See `run_explain`'s comment on `ignore_case = true`: clap preserves
    // the user's casing, Click normalizes it, so we normalize by hand.
    parsed.format = parsed.format.to_lowercase();

    let target = pathlib_normalize(&PathBuf::from(&parsed.path));
    if !target.exists() {
        eprint_line(&format!("jss-lint: path does not exist: {}", parsed.path));
        return ExitCode::from(2);
    }

    let candidates: Vec<PathBuf> = if target.is_dir() {
        let mut found: Vec<PathBuf> = std::fs::read_dir(&target)
            .map(|entries| {
                entries
                    .flatten()
                    .map(|e| e.path())
                    .filter(|p| p.is_file() && is_supported_suffix(p))
                    .map(|p| pathlib_normalize(&p))
                    .collect()
            })
            .unwrap_or_default();
        found.sort();
        found
    } else {
        vec![target.clone()]
    };

    if candidates.is_empty() {
        eprint_line(&format!(
            "jss-lint: no lintable files under {}",
            target.display()
        ));
        return ExitCode::from(2);
    }

    let sources: Result<Vec<(String, String)>, std::io::Error> = candidates
        .iter()
        .map(|p| std::fs::read_to_string(p).map(|c| (p.to_string_lossy().into_owned(), c)))
        .collect();
    let sources = match sources {
        Ok(s) => s,
        Err(exc) => {
            eprint_line(&format!("jss-lint: {exc}"));
            return ExitCode::from(2);
        }
    };
    let document = match ParsedDocument::from_sources(&sources) {
        Ok(d) => d,
        Err(EngineError::UnsupportedSuffix(msg)) => {
            eprint_line(&format!("jss-lint: {msg}"));
            return ExitCode::from(2);
        }
    };

    let cwd = std::env::current_dir().unwrap_or_else(|_| PathBuf::from("."));
    let cfg = config::load(&cwd, &RawOverrides::default());
    if cfg.journal != "jss" {
        eprint_line(&format!(
            "jss-lint: No journal registered under '{}'. Known: ['jss']",
            cfg.journal
        ));
        return ExitCode::from(2);
    }
    let report = engine::run(&cfg, &document);

    let (extracted_title, extracted_author) = if parsed.title.is_none() || parsed.author.is_none() {
        jsslint_core::conformance::extract_metadata(&document)
    } else {
        (None, None)
    };
    let title = parsed
        .title
        .unwrap_or_else(|| extracted_title.unwrap_or_else(|| "Manuscript".to_string()));
    let author = parsed
        .author
        .unwrap_or_else(|| extracted_author.unwrap_or_else(|| "(unknown)".to_string()));

    let run_date = localdate::today_iso();
    let summary = jsslint_core::conformance::compute_summary(
        &report,
        &title,
        &author,
        candidates.len(),
        &run_date,
        &HashSet::new(),
    );

    if parsed.format == "pdf" {
        // Mirrors the Python CLI's own `--format pdf requires --out
        // FILE` guard (`cli.py::report_cmd`) — PDF is bytes, not text,
        // so there's no sensible stdout behavior.
        let Some(out_path) = &parsed.out else {
            eprint_line("jss-lint: --format pdf requires --out FILE");
            return ExitCode::from(2);
        };
        let pdf_bytes = match report_pdf::render_pdf(&summary) {
            Ok(bytes) => bytes,
            Err(msg) => {
                eprint_line(&format!("jss-lint: {msg}"));
                return ExitCode::from(2);
            }
        };
        if let Err(exc) = std::fs::write(out_path, &pdf_bytes) {
            eprint_line(&format!("jss-lint: {exc}"));
            return ExitCode::from(2);
        }
        return ExitCode::from(0);
    }

    let rendered = if parsed.format == "html" {
        jsslint_core::conformance::render_html(&summary)
    } else {
        jsslint_core::conformance::render_md(&summary)
    };

    match &parsed.out {
        None => print!("{rendered}"),
        Some(out_path) => {
            if let Err(exc) = std::fs::write(out_path, rendered.as_bytes()) {
                eprint_line(&format!("jss-lint: {exc}"));
                return ExitCode::from(2);
            }
        }
    }
    ExitCode::from(0)
}

fn eprint_line(msg: &str) {
    eprintln!("{msg}");
}

fn main() -> ExitCode {
    let args: Vec<String> = std::env::args().collect();
    if let Some(first) = args.get(1) {
        if REGISTERED_SUBCOMMANDS.contains(&first.as_str()) {
            return match first.as_str() {
                "explain" => run_explain(&args[2..]),
                "diff" => run_diff(&args[2..]),
                "init" => run_init(&args[2..]),
                "report" => run_report(&args[2..]),
                "lsp" => lsp_server::main(),
                _ => unreachable!("REGISTERED_SUBCOMMANDS out of sync"),
            };
        }
    }
    run_lint()
}

fn run_lint() -> ExitCode {
    let mut cli = Cli::parse();
    // See `run_explain`'s comment on `ignore_case = true`: clap preserves
    // the user's casing, Click normalizes it, so we normalize by hand —
    // `config::load`/`RawOverrides` match against lowercase literals.
    cli.mode = cli.mode.map(|s| s.to_lowercase());
    cli.output = cli.output.map(|s| s.to_lowercase());
    cli.min_confidence = cli.min_confidence.map(|s| s.to_lowercase());
    cli.fail_on = cli.fail_on.map(|s| s.to_lowercase());

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
    let mut config = config::load(&cwd, &cli_overrides);
    if cli.crossref {
        // Online DOI verification is opt-in and injected here (never
        // via `.jss-lint.toml`), so the linter stays offline by
        // default — mirrors `cli.py`'s `cfg = replace(cfg,
        // doi_resolver=...)`.
        config.doi_resolver = Some(jsslint_crossref::make_resolver(
            jsslint_crossref::CrossrefOptions {
                mailto: cli.crossref_mailto.clone(),
                ..Default::default()
            },
        ));
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
        OutputFormat::Html => print!(
            "{}",
            jsslint_core::html_output::render(&report, config.mode)
        ),
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
