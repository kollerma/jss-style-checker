//! R binding (spec 018 Phase 5), built with `extendr`. Exposes
//! `jss_lint(files, ...)` — the same rule engine `jsslint-cli`,
//! `jsslint-wasm`, and `jsslint` (the PyO3 binding) all wrap, adapted to R's data
//! model: `files` is a named character vector (names = paths, values
//! = file contents) rather than a list of pairs, since that's the
//! idiomatic R shape (`c(path1 = contents1, path2 = contents2)`).
//!
//! `R/extendr-wrappers.R` is regenerated from this crate's own
//! extendr metadata by `document.rs` on every build (see
//! `src/Makevars`) — never hand-edited.

use extendr_api::prelude::*;
use jsslint_core::config::{self, RawOverrides, ToolConfig};
use jsslint_core::engine::{self, ParsedDocument};
use jsslint_core::fixer::{self, ApplyMode};
use jsslint_core::report::ComplianceReport;
use jsslint_core::{catalogue, html_output, json_output, sarif, terminal};
use std::collections::HashSet;

/// Unpacks the named-character-vector `files` argument every entry
/// point takes into the `(path, contents)` pairs
/// `ParsedDocument::from_sources` wants.
fn file_pairs_from_robj(files: &Robj) -> extendr_api::Result<Vec<(String, String)>> {
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
    Ok(names.into_iter().zip(values).collect())
}

fn split_rule_list(s: Option<String>) -> Option<Vec<String>> {
    s.map(|s| {
        s.split(',')
            .map(|p| p.trim().to_string())
            .filter(|p| !p.is_empty())
            .collect()
    })
}

/// Config + report for the given sources, layering the shared subset
/// of CLI-flag-equivalent overrides over `.jss-lint.toml` and the
/// defaults, exactly as `render` does.
#[allow(clippy::too_many_arguments)]
fn lint_report(
    files: &Robj,
    journal: Option<String>,
    mode: Option<String>,
    output: Option<String>,
    ignore_rules: Option<String>,
    min_confidence: Option<String>,
    fail_on: Option<String>,
    source_root: Option<String>,
    verbose: Option<bool>,
) -> extendr_api::Result<(ToolConfig, ComplianceReport)> {
    let file_pairs = file_pairs_from_robj(files)?;
    let document =
        ParsedDocument::from_sources(&file_pairs).map_err(|e| Error::from(e.to_string()))?;
    let overrides = RawOverrides {
        journal,
        mode,
        output,
        ignore_rules: split_rule_list(ignore_rules),
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
    Ok((cfg, report))
}

/// Lint files against the JSS style guide
///
/// Mirrors `jsslint::render` (the PyO3 binding) / the WASM binding's
/// `render()`.
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
    let (cfg, report) = lint_report(
        &files,
        journal,
        mode,
        output,
        ignore_rules,
        min_confidence,
        fail_on,
        source_root,
        verbose,
    )?;

    let rendered = match cfg.output {
        config::OutputFormat::Json => json_output::render(&report),
        config::OutputFormat::Sarif => sarif::render(&report, &cfg),
        config::OutputFormat::Terminal => terminal::render(&report, &cfg),
        config::OutputFormat::Html => html_output::render(&report, cfg.mode),
    };
    Ok(rendered)
}

/// Structured lint results backing `jsslint()` — internal; the
/// user-facing wrapper turns the parallel vectors into data frames.
/// @noRd
#[extendr]
fn lint_data(
    files: Robj,
    #[extendr(default = "NULL")] journal: Option<String>,
    #[extendr(default = "NULL")] mode: Option<String>,
    #[extendr(default = "NULL")] ignore_rules: Option<String>,
    #[extendr(default = "NULL")] min_confidence: Option<String>,
    #[extendr(default = "NULL")] verbose: Option<bool>,
) -> extendr_api::Result<List> {
    let (_cfg, report) = lint_report(
        &files,
        journal,
        mode,
        None,
        ignore_rules,
        min_confidence,
        None,
        None,
        verbose,
    )?;

    let mut sorted = report.violations.clone();
    jsslint_core::report::sort_violations(&mut sorted);

    let opt_str = |values: Vec<Option<&str>>| -> Strings {
        Strings::from_values(
            values
                .into_iter()
                .map(|v| v.map(Rstr::from).unwrap_or_else(Rstr::na))
                .collect::<Vec<Rstr>>(),
        )
    };

    let violations = List::from_pairs([
        ("file", Robj::from(sorted.iter().map(|v| v.file.as_str()).collect::<Vec<_>>())),
        ("line", Robj::from(sorted.iter().map(|v| v.line as i32).collect::<Vec<_>>())),
        (
            "column",
            Robj::from(Integers::from_values(
                sorted
                    .iter()
                    .map(|v| v.column.map(|c| Rint::from(c as i32)).unwrap_or_else(Rint::na))
                    .collect::<Vec<Rint>>(),
            )),
        ),
        ("rule_id", Robj::from(sorted.iter().map(|v| v.rule_id.as_str()).collect::<Vec<_>>())),
        (
            "severity",
            Robj::from(sorted.iter().map(|v| v.severity.as_str()).collect::<Vec<_>>()),
        ),
        ("message", Robj::from(sorted.iter().map(|v| v.message.as_str()).collect::<Vec<_>>())),
        (
            "suggestion",
            Robj::from(opt_str(sorted.iter().map(|v| v.suggestion.as_deref()).collect())),
        ),
        (
            "fixable",
            Robj::from(sorted.iter().map(|v| v.fix.is_some()).collect::<Vec<_>>()),
        ),
        (
            "fix_description",
            Robj::from(opt_str(
                sorted
                    .iter()
                    .map(|v| v.fix.as_ref().map(|f| f.description.as_str()))
                    .collect(),
            )),
        ),
        (
            "fix_confidence",
            Robj::from(opt_str(
                sorted
                    .iter()
                    .map(|v| v.fix.as_ref().map(|f| f.confidence.as_str()))
                    .collect(),
            )),
        ),
        (
            "guide_section",
            Robj::from(
                sorted
                    .iter()
                    .map(|v| catalogue::lookup(&v.rule_id).map(|m| m.guide_section).unwrap_or(""))
                    .collect::<Vec<_>>(),
            ),
        ),
        (
            "confidence",
            Robj::from(
                sorted
                    .iter()
                    .map(|v| catalogue::lookup(&v.rule_id).map(|m| m.confidence).unwrap_or("high"))
                    .collect::<Vec<_>>(),
            ),
        ),
    ]);

    let categories = List::from_pairs([
        (
            "category_id",
            Robj::from(report.categories.iter().map(|c| c.category_id.as_str()).collect::<Vec<_>>()),
        ),
        (
            "title",
            Robj::from(report.categories.iter().map(|c| c.title.as_str()).collect::<Vec<_>>()),
        ),
        (
            "status",
            Robj::from(report.categories.iter().map(|c| c.status.as_str()).collect::<Vec<_>>()),
        ),
        (
            "rules_applied",
            Robj::from(report.categories.iter().map(|c| c.rules_applied as i32).collect::<Vec<_>>()),
        ),
        (
            "rules_passed",
            Robj::from(report.categories.iter().map(|c| c.rules_passed as i32).collect::<Vec<_>>()),
        ),
        (
            "issues",
            Robj::from(
                report
                    .categories
                    .iter()
                    .map(|c| c.violations.len() as i32)
                    .collect::<Vec<_>>(),
            ),
        ),
    ]);

    let skipped_rules = List::from_pairs([
        (
            "rule_id",
            Robj::from(report.skipped_rules.iter().map(|s| s.rule_id.as_str()).collect::<Vec<_>>()),
        ),
        (
            "reason",
            Robj::from(report.skipped_rules.iter().map(|s| s.reason.as_str()).collect::<Vec<_>>()),
        ),
    ]);

    let compliance = match report.compliance_percentage {
        Some(p) => Robj::from(p),
        None => Robj::from(()),
    };

    Ok(List::from_pairs([
        ("tool_version", Robj::from(report.tool_version.as_str())),
        ("journal_id", Robj::from(report.journal_id.as_str())),
        ("compliance_percentage", compliance),
        ("violations", Robj::from(violations)),
        ("categories", Robj::from(categories)),
        ("skipped_rules", Robj::from(skipped_rules)),
    ]))
}

/// Auto-fix backing `jssfix()` — internal. Lints `files` (named
/// character vector, same shape as `render`), then hands the report to
/// `fixer::apply_fixes`, which reads/writes the files at the paths
/// given by `names(files)` on disk (atomic write + re-validation with
/// rollback on regression). In dry-run mode nothing is written and the
/// captured `output` holds the unified diffs that would be applied.
/// @noRd
#[extendr]
fn fix_data(
    files: Robj,
    #[extendr(default = "FALSE")] dry_run: bool,
    #[extendr(default = "NULL")] rules: Option<String>,
    #[extendr(default = "NULL")] journal: Option<String>,
    #[extendr(default = "NULL")] mode: Option<String>,
    #[extendr(default = "NULL")] ignore_rules: Option<String>,
    #[extendr(default = "NULL")] min_confidence: Option<String>,
    #[extendr(default = "NULL")] verbose: Option<bool>,
) -> extendr_api::Result<List> {
    let (_cfg, report) = lint_report(
        &files,
        journal,
        mode,
        None,
        ignore_rules,
        min_confidence,
        None,
        None,
        verbose,
    )?;

    let rule_set: Option<HashSet<String>> =
        split_rule_list(rules).map(|v| v.into_iter().collect());
    let apply_mode = if dry_run {
        ApplyMode::DryRun
    } else {
        ApplyMode::Write
    };

    let mut stdin = std::io::empty();
    let mut stdout: Vec<u8> = Vec::new();
    let mut stderr: Vec<u8> = Vec::new();
    let fix_report = fixer::apply_fixes(
        &report,
        apply_mode,
        rule_set.as_ref(),
        &mut stdin,
        &mut stdout,
        &mut stderr,
    );

    let applied = List::from_pairs([
        (
            "file",
            Robj::from(fix_report.applied.iter().map(|a| a.file.as_str()).collect::<Vec<_>>()),
        ),
        (
            "rule_id",
            Robj::from(fix_report.applied.iter().map(|a| a.rule_id.as_str()).collect::<Vec<_>>()),
        ),
        (
            "description",
            Robj::from(
                fix_report
                    .applied
                    .iter()
                    .map(|a| a.fix.description.as_str())
                    .collect::<Vec<_>>(),
            ),
        ),
        (
            "confidence",
            Robj::from(
                fix_report
                    .applied
                    .iter()
                    .map(|a| a.fix.confidence.as_str())
                    .collect::<Vec<_>>(),
            ),
        ),
    ]);

    let skipped = List::from_pairs([
        (
            "file",
            Robj::from(fix_report.skipped.iter().map(|s| s.file.as_str()).collect::<Vec<_>>()),
        ),
        (
            "rule_id",
            Robj::from(fix_report.skipped.iter().map(|s| s.rule_id.as_str()).collect::<Vec<_>>()),
        ),
        (
            "reason",
            Robj::from(
                fix_report
                    .skipped
                    .iter()
                    .map(|s| match s.reason {
                        fixer::SkipReason::Conflict => "conflict",
                        fixer::SkipReason::RuleNotSelected => "rule-not-selected",
                        fixer::SkipReason::UserSkipped => "user-skipped",
                    })
                    .collect::<Vec<_>>(),
            ),
        ),
    ]);

    let rejected = List::from_pairs([
        (
            "file",
            Robj::from(fix_report.rejected.iter().map(|r| r.file.as_str()).collect::<Vec<_>>()),
        ),
        (
            "rule_id",
            Robj::from(fix_report.rejected.iter().map(|r| r.rule_id.as_str()).collect::<Vec<_>>()),
        ),
        (
            "reason",
            Robj::from(
                fix_report
                    .rejected
                    .iter()
                    .map(|r| match r.reason {
                        fixer::RejectReason::Regression => "regression",
                        fixer::RejectReason::PermissionDenied => "io-error",
                    })
                    .collect::<Vec<_>>(),
            ),
        ),
    ]);

    Ok(List::from_pairs([
        ("applied", Robj::from(applied)),
        ("skipped", Robj::from(skipped)),
        ("rejected", Robj::from(rejected)),
        ("output", Robj::from(String::from_utf8_lossy(&stdout).into_owned())),
        ("log", Robj::from(String::from_utf8_lossy(&stderr).into_owned())),
    ]))
}

extendr_module! {
    mod jsslintr;
    fn render;
    fn lint_data;
    fn fix_data;
}
