//! Author/reviewer HTML renderer — hand-translated from
//! `output/html_output.py`'s `author.html.j2`/`reviewer.html.j2`
//! (no templating-engine dependency, matching this crate's existing
//! `terminal.rs`/`sarif.rs`/`conformance.rs` approach of building
//! output strings directly). Byte-exact output was derived by reading
//! the templates' Jinja2 whitespace-control semantics (`{%- -%}` trim
//! markers around the guide-link `<td>`; every other `{% %}` tag is
//! *not* trimmed, since the templates' `Environment` doesn't set
//! `trim_blocks`/`lstrip_blocks`, so untrimmed tags leave their
//! adjacent source newlines/indentation in the output) and cross-
//! checked against real `jss-lint --output html` renders.
//!
//! `report --format html`/`pdf` (spec 015's `conformance.html.j2`,
//! rendered via `jsslint_core::conformance`) is a separate template
//! and stays Python-only per the porting plan's report-subcommand
//! scope note — this module only covers the bare-lint `--output html`
//! path (`author.html.j2`/`reviewer.html.j2`).

use crate::catalogue;
use crate::report::ComplianceReport;
use std::collections::BTreeMap;

/// Mirrors `markupsafe.escape()`, which Jinja2's `select_autoescape`
/// uses for every `{{ }}` interpolation in these `.html.j2` templates.
fn escape_html(s: &str) -> String {
    let mut out = String::with_capacity(s.len());
    for c in s.chars() {
        match c {
            '&' => out.push_str("&amp;"),
            '<' => out.push_str("&lt;"),
            '>' => out.push_str("&gt;"),
            '"' => out.push_str("&#34;"),
            '\'' => out.push_str("&#39;"),
            other => out.push(other),
        }
    }
    out
}

const AUTHOR_STYLE: &str = "  body { font-family: -apple-system, Segoe UI, Roboto, sans-serif; margin: 2rem; color: #222; }\n  h1 { margin-top: 0; }\n  h2 { border-bottom: 1px solid #ccc; padding-bottom: 0.25rem; margin-top: 2rem; }\n  table { border-collapse: collapse; width: 100%; margin-top: 0.5rem; }\n  th, td { border: 1px solid #ddd; padding: 0.4rem 0.6rem; text-align: left; vertical-align: top; font-size: 0.9rem; }\n  th { background: #f5f5f5; }\n  .sev-error { color: #b00020; font-weight: 600; }\n  .sev-warning { color: #b8860b; font-weight: 600; }\n  .loc { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; white-space: nowrap; }\n  .rid { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }\n  .none { color: #888; font-style: italic; }\n  .ok { color: #2a7a2a; font-weight: 600; }\n";

/// Mirrors `author.html.j2` (individual violations grouped by file).
pub fn render_author(report: &ComplianceReport) -> String {
    let journal = escape_html(&report.journal_id);
    let mut out = String::new();
    out.push_str("<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n<title>jss-lint report \u{2014} ");
    out.push_str(&journal);
    out.push_str("</title>\n<style>\n");
    out.push_str(AUTHOR_STYLE);
    out.push_str("</style>\n</head>\n<body>\n<h1>jss-lint report</h1>\n<p>Journal: <strong>");
    out.push_str(&journal);
    out.push_str("</strong> \u{b7} Tool version: <code>");
    out.push_str(&escape_html(&report.tool_version));
    out.push_str("</code></p>\n");

    if report.violations.is_empty() {
        out.push_str("\n<p class=\"ok\">No violations found.</p>\n");
        out.push('\n');
    } else {
        out.push('\n');
        let mut by_file: BTreeMap<&str, Vec<&crate::report::Violation>> = BTreeMap::new();
        for v in &report.violations {
            by_file.entry(v.file.as_str()).or_default().push(v);
        }
        for (file, violations) in &by_file {
            out.push('\n');
            out.push_str("<h2>");
            out.push_str(&escape_html(file));
            out.push_str("</h2>\n<table>\n  <thead>\n    <tr><th>Line:Col</th><th>Severity</th><th>Rule</th><th>Message</th><th>Section</th><th>Suggestion</th></tr>\n  </thead>\n  <tbody>\n  ");
            for v in violations {
                out.push_str("\n    \n    <tr>\n      <td class=\"loc\">");
                out.push_str(&v.line.to_string());
                if let Some(col) = v.column {
                    out.push(':');
                    out.push_str(&col.to_string());
                }
                out.push_str("</td>\n      <td class=\"sev-");
                out.push_str(v.severity.as_str());
                out.push_str("\">");
                out.push_str(v.severity.as_str());
                out.push_str("</td>\n      <td class=\"rid\">");
                out.push_str(&escape_html(&v.rule_id));
                out.push_str("</td>\n      <td>");
                out.push_str(&escape_html(&v.message));
                out.push_str("</td>\n      <td>");

                let meta = catalogue::lookup(&v.rule_id);
                let section = meta.map(|m| m.guide_section).unwrap_or("");
                let url = meta.and_then(|m| m.guide_url);
                match url {
                    Some(url) if !section.is_empty() && section != "internal" => {
                        out.push_str("<a href=\"");
                        out.push_str(&escape_html(url));
                        out.push_str("\">");
                        out.push_str(&escape_html(section));
                        out.push_str("</a>");
                    }
                    _ => out.push_str("<span class=\"none\">internal</span>"),
                }
                out.push_str("</td>\n      <td>");
                match v.suggestion.as_deref() {
                    Some(s) if !s.is_empty() => out.push_str(&escape_html(s)),
                    _ => out.push_str("<span class=\"none\">\u{2014}</span>"),
                }
                out.push_str("</td>\n    </tr>\n  ");
            }
            out.push_str("\n  </tbody>\n</table>\n");
        }
        out.push('\n');
        out.push('\n');
    }
    out.push_str("</body>\n</html>\n");
    out
}

const REVIEWER_STYLE: &str = "  body { font-family: -apple-system, Segoe UI, Roboto, sans-serif; margin: 2rem; color: #222; }\n  h1 { margin-top: 0; }\n  table { border-collapse: collapse; width: 100%; margin-top: 0.5rem; }\n  th, td { border: 1px solid #ddd; padding: 0.5rem 0.75rem; font-size: 0.95rem; }\n  th { background: #f5f5f5; text-align: left; }\n  .num { text-align: right; font-variant-numeric: tabular-nums; }\n  .status-PASS { color: #2a7a2a; font-weight: 600; }\n  .status-FAIL { color: #b00020; font-weight: 600; }\n  .status-SKIPPED { color: #777; font-weight: 600; }\n  .overall { font-size: 1.6rem; margin-top: 1rem; }\n  .overall.none { color: #777; }\n";

/// Mirrors `reviewer.html.j2` (per-category compliance table).
pub fn render_reviewer(report: &ComplianceReport) -> String {
    let journal = escape_html(&report.journal_id);
    let mut out = String::new();
    out.push_str("<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n<title>jss-lint compliance \u{2014} ");
    out.push_str(&journal);
    out.push_str("</title>\n<style>\n");
    out.push_str(REVIEWER_STYLE);
    out.push_str("</style>\n</head>\n<body>\n<h1>Journal compliance \u{2014} ");
    out.push_str(&journal);
    out.push_str("</h1>\n<p>Tool version: <code>");
    out.push_str(&escape_html(&report.tool_version));
    out.push_str("</code></p>\n<table>\n  <thead>\n    <tr><th>Category</th><th>Status</th><th class=\"num\">Applied</th><th class=\"num\">Passed</th></tr>\n  </thead>\n  <tbody>\n  ");

    for c in &report.categories {
        out.push_str("\n    <tr>\n      <td>");
        out.push_str(&escape_html(&c.title));
        out.push_str("</td>\n      <td class=\"status-");
        out.push_str(c.status.as_str());
        out.push_str("\">");
        out.push_str(c.status.as_str());
        out.push_str("</td>\n      <td class=\"num\">");
        out.push_str(&c.rules_applied.to_string());
        out.push_str("</td>\n      <td class=\"num\">");
        out.push_str(&c.rules_passed.to_string());
        out.push_str("</td>\n    </tr>\n  ");
    }
    out.push_str("\n  </tbody>\n</table>\n");

    out.push('\n');
    match report.compliance_percentage {
        None => out.push_str("<p class=\"overall none\">Overall: n/a</p>\n"),
        Some(pct) => out.push_str(&format!(
            "<p class=\"overall\">Overall: <strong>{pct:.1}%</strong></p>\n"
        )),
    }
    out.push('\n');

    out.push_str("</body>\n</html>\n");
    out
}

/// Renders exactly as `jss-lint --output html` does: `author.html.j2`
/// in author mode, `reviewer.html.j2` in reviewer mode. Mirrors
/// `html_output.py::render`.
pub fn render(report: &ComplianceReport, mode: crate::config::Mode) -> String {
    match mode {
        crate::config::Mode::Reviewer => render_reviewer(report),
        crate::config::Mode::Author => render_author(report),
    }
}
