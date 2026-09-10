//! Renderers for the guide-coverage matrix — mirrors
//! `src/texlint/coverage.py` (spec 027 item A).
//!
//! Contract: `specs/027-first-time-user-gaps/contracts/coverage-file.md`
//! C-5/C-6. Byte-identical to the Python renderers in all three
//! subcommand formats (`coverage_parity.rs`).

use crate::catalogue::CoverageDirectiveData;
use crate::json_output;
use serde_json::{json, Value};

/// Display order: `checked` first, then the two kinds of gap, then what
/// was never checkable.
const STATUS_ORDER: [&str; 4] = ["checked", "partial", "not_checked", "out_of_scope"];

/// Sources in the order the file declares them.
const SOURCE_ORDER: [(&str, &str); 4] = [
    ("jss_cls", "jss.cls"),
    ("article_tex", "article.tex"),
    ("style_guide", "Style guide"),
    ("author_instructions", "Author instructions"),
];

fn status_label(status: &str) -> &'static str {
    match status {
        "checked" => "checked",
        "partial" => "partial",
        "not_checked" => "not checked",
        _ => "out of scope",
    }
}

#[derive(Debug, Clone, Copy, Default)]
pub struct Counts {
    pub checked: u32,
    pub partial: u32,
    pub not_checked: u32,
    pub out_of_scope: u32,
}

impl Counts {
    pub fn of(directives: &[CoverageDirectiveData]) -> Self {
        let mut counts = Self::default();
        for directive in directives {
            match directive.status {
                "checked" => counts.checked += 1,
                "partial" => counts.partial += 1,
                "not_checked" => counts.not_checked += 1,
                _ => counts.out_of_scope += 1,
            }
        }
        counts
    }

    /// Provisions a source-level linter could check at all.
    pub fn checkable(&self) -> u32 {
        self.checked + self.partial + self.not_checked
    }

    pub fn covered(&self) -> u32 {
        self.checked + self.partial
    }
}

pub fn counts_line(directives: &[CoverageDirectiveData]) -> String {
    let c = Counts::of(directives);
    format!(
        "{} checked, {} partial, {} not checked, {} out of scope",
        c.checked, c.partial, c.not_checked, c.out_of_scope
    )
}

/// The line closing the reviewer block — counts plus where to see more.
pub fn counts_sentence(directives: &[CoverageDirectiveData]) -> String {
    format!(
        "Run jss-lint coverage for the full matrix ({}).",
        counts_line(directives)
    )
}

/// The author footer's second line. Quotes the *checkable* ratio:
/// out-of-scope provisions were never checkable from source.
pub fn footer_sentence(directives: &[CoverageDirectiveData]) -> String {
    let c = Counts::of(directives);
    format!(
        "jss-lint checks {} of {} guide directives ({} not checked, {} partial). \
         Run jss-lint coverage for the list.",
        c.covered(),
        c.checkable(),
        c.not_checked,
        c.partial
    )
}

/// The rows the reviewer block lists: partial first, then not checked,
/// each group sorted by id. Out-of-scope rows are not gaps.
pub fn gaps(directives: &[CoverageDirectiveData]) -> Vec<&CoverageDirectiveData> {
    let mut rows: Vec<&CoverageDirectiveData> = directives
        .iter()
        .filter(|d| d.status == "partial" || d.status == "not_checked")
        .collect();
    rows.sort_by_key(|d| (if d.status == "partial" { 0 } else { 1 }, d.id));
    rows
}

fn header(journal_id: &str, ruleset_version: Option<&str>, prefix: &str) -> String {
    let mut line = format!("{prefix}Guide coverage \u{2014} {journal_id}");
    if let Some(version) = ruleset_version {
        line.push_str(&format!(" (rule set {version})"));
    }
    line
}

pub fn render_terminal(
    directives: &[CoverageDirectiveData],
    journal_id: &str,
    ruleset_version: Option<&str>,
) -> String {
    if directives.is_empty() {
        return format!("jss-lint has no guide-coverage data for journal {journal_id}.\n");
    }
    let mut out = vec![
        header(journal_id, ruleset_version, ""),
        counts_line(directives),
        String::new(),
    ];
    for status in STATUS_ORDER {
        let mut group: Vec<&CoverageDirectiveData> =
            directives.iter().filter(|d| d.status == status).collect();
        if group.is_empty() {
            continue;
        }
        group.sort_by_key(|d| d.id);
        out.push(format!("{} ({})", status_label(status), group.len()));
        for d in group {
            out.push(format!("  {}  {}  {}", d.id, d.section, d.provision));
            if !d.rules.is_empty() {
                out.push(format!("        rules: {}", d.rules.join(", ")));
            }
            if !d.reason.is_empty() {
                out.push(format!("        reason: {}", d.reason));
            }
        }
        out.push(String::new());
    }
    format!("{}\n", out.join("\n").trim_end_matches('\n'))
}

pub fn render_markdown(
    directives: &[CoverageDirectiveData],
    journal_id: &str,
    ruleset_version: Option<&str>,
) -> String {
    if directives.is_empty() {
        return format!("jss-lint has no guide-coverage data for journal {journal_id}.\n");
    }
    let mut out = vec![
        header(journal_id, ruleset_version, "# "),
        String::new(),
        counts_line(directives),
        String::new(),
    ];
    for (source, label) in SOURCE_ORDER {
        let mut group: Vec<&CoverageDirectiveData> =
            directives.iter().filter(|d| d.source == source).collect();
        if group.is_empty() {
            continue;
        }
        group.sort_by_key(|d| d.id);
        out.push(format!("## {label}"));
        out.push(String::new());
        out.push("| Directive | Status | Provision | Rules | Reason |".to_string());
        out.push("|---|---|---|---|---|".to_string());
        for d in group {
            let rules = if d.rules.is_empty() {
                "\u{2014}".to_string()
            } else {
                d.rules.join(", ")
            };
            let reason = if d.reason.is_empty() {
                "\u{2014}".to_string()
            } else {
                escape_pipe(d.reason)
            };
            out.push(format!(
                "| {} | {} | {} | {rules} | {reason} |",
                d.id,
                status_label(d.status),
                escape_pipe(d.provision)
            ));
        }
        out.push(String::new());
    }
    format!("{}\n", out.join("\n").trim_end_matches('\n'))
}

pub fn render_json(
    directives: &[CoverageDirectiveData],
    journal_id: &str,
    sources: Value,
) -> String {
    let payload = if directives.is_empty() {
        json!({"journal_id": journal_id, "counts": null, "directives": []})
    } else {
        let c = Counts::of(directives);
        json!({
            "counts": {
                "checked": c.checked,
                "not_checked": c.not_checked,
                "out_of_scope": c.out_of_scope,
                "partial": c.partial,
            },
            "directives": directives
                .iter()
                .map(|d| json!({
                    "id": d.id,
                    "provision": d.provision,
                    "reason": d.reason,
                    "rules": d.rules,
                    "section": d.section,
                    "source": d.source,
                    "status": d.status,
                }))
                .collect::<Vec<_>>(),
            "journal_id": journal_id,
            "sources": sources,
        })
    };
    let mut out = String::new();
    json_output::write_value(&payload, 0, &mut out);
    out.push('\n');
    out
}

fn escape_pipe(text: &str) -> String {
    text.replace('|', "\\|")
}
