//! One-page conformance report — mirrors `texlint/report.py` (spec
//! 015). Markdown only; HTML/PDF stay Python-only per the porting
//! plan (jinja2 templates + optional WeasyPrint aren't a good target
//! for this port's early phases).

use crate::catalogue;
use crate::engine::ParsedDocument;
use crate::report::{ComplianceReport, Severity, Violation};
use crate::tex::node::{Args, Node};
use std::collections::{HashMap, HashSet};

const TOOL_SIDE_CATEGORIES: &[&str] = &["parse", "internal"];
const TITLE_MACROS: &[&str] = &["title", "Plaintitle"];
const AUTHOR_MACROS: &[&str] = &["Plainauthor", "author"];

#[derive(Debug, Clone)]
pub struct TopFiveEntry {
    pub rule_id: String,
    pub count: usize,
    pub example_file: String,
    pub example_line: u32,
    pub example_excerpt: String,
}

#[derive(Debug, Clone)]
pub struct FixMeItem {
    pub rule_id: String,
    pub severity: Severity,
    pub count: usize,
}

#[derive(Debug, Clone)]
pub struct ConformanceSummary {
    pub title: String,
    pub author: String,
    pub file_count: usize,
    pub run_date: String,
    pub score_percent: Option<i64>,
    pub rules_passing: usize,
    pub rules_total_active: usize,
    pub error_count: usize,
    pub warning_count: usize,
    pub info_count: usize,
    pub top_five: Vec<TopFiveEntry>,
    pub fix_me_first: Vec<FixMeItem>,
}

fn active_rule_ids(ignore_rules: &HashSet<String>) -> HashSet<&'static str> {
    catalogue::all_rules()
        .iter()
        .filter(|m| {
            !ignore_rules.contains(m.rule_id) && !TOOL_SIDE_CATEGORIES.contains(&m.category)
        })
        .map(|m| m.rule_id)
        .collect()
}

fn severity_rank(s: Severity) -> u8 {
    match s {
        Severity::Error => 0,
        Severity::Warning => 1,
        Severity::Info => 2,
    }
}

/// Mirrors Python's `round()` on a non-negative float: round-half-
/// to-even, not Rust `f64::round()`'s round-half-away-from-zero.
/// Matters here: `total_active` is a small denominator (currently
/// ~50 active rules), so an exact `.5` tie in the integer percentage
/// is a realistic occurrence, not a hypothetical edge case.
fn python_round_to_i64(x: f64) -> i64 {
    let floor = x.floor();
    let diff = x - floor;
    let floor_i = floor as i64;
    if diff < 0.5 {
        floor_i
    } else if diff > 0.5 {
        floor_i + 1
    } else if floor_i % 2 == 0 {
        floor_i
    } else {
        floor_i + 1
    }
}

/// Builds a `ConformanceSummary` from a lint report. Mirrors
/// `report.py::_compute_summary`. `run_date` is supplied by the
/// caller (`date.today().isoformat()`-equivalent) rather than computed
/// here — a wall-clock read belongs at the binding/CLI layer, not in
/// this crate's otherwise-pure logic.
pub fn compute_summary(
    report: &ComplianceReport,
    title: &str,
    author: &str,
    file_count: usize,
    run_date: &str,
    ignore_rules: &HashSet<String>,
) -> ConformanceSummary {
    let active = active_rule_ids(ignore_rules);

    let mut violating_active: HashSet<&str> = HashSet::new();
    for v in &report.violations {
        if active.contains(v.rule_id.as_str()) {
            violating_active.insert(v.rule_id.as_str());
        }
    }
    let total_active = active.len();
    let passing = total_active - violating_active.len();
    let score = if total_active > 0 {
        Some(python_round_to_i64(
            100.0 * passing as f64 / total_active as f64,
        ))
    } else {
        None
    };

    let mut severity_counts: HashMap<Severity, usize> = HashMap::new();
    for v in &report.violations {
        *severity_counts.entry(v.severity).or_insert(0) += 1;
    }

    // Group by rule_id, preserving first-encounter order in
    // report.violations (already canonically sorted).
    let mut files: Vec<(&str, Vec<&Violation>)> = Vec::new();
    let mut index_of: HashMap<&str, usize> = HashMap::new();
    for v in &report.violations {
        if let Some(&idx) = index_of.get(v.rule_id.as_str()) {
            files[idx].1.push(v);
        } else {
            index_of.insert(v.rule_id.as_str(), files.len());
            files.push((v.rule_id.as_str(), vec![v]));
        }
    }
    files.sort_by(|a, b| b.1.len().cmp(&a.1.len()).then_with(|| a.0.cmp(b.0)));

    let mut top_five: Vec<TopFiveEntry> = Vec::new();
    for (rid, viols) in &files {
        if !active.contains(rid) {
            continue;
        }
        let first = viols[0];
        let excerpt: String = first.message.chars().take(80).collect();
        top_five.push(TopFiveEntry {
            rule_id: rid.to_string(),
            count: viols.len(),
            example_file: first.file.clone(),
            example_line: first.line,
            example_excerpt: excerpt,
        });
        if top_five.len() == 5 {
            break;
        }
    }

    let mut by_rule_severity: HashMap<&str, Severity> = HashMap::new();
    let mut by_rule_count: HashMap<&str, usize> = HashMap::new();
    for v in &report.violations {
        if !active.contains(v.rule_id.as_str()) {
            continue;
        }
        by_rule_severity.insert(v.rule_id.as_str(), v.severity);
        *by_rule_count.entry(v.rule_id.as_str()).or_insert(0) += 1;
    }
    let mut rule_ids: Vec<&str> = by_rule_count.keys().copied().collect();
    rule_ids.sort_by(|a, b| {
        severity_rank(by_rule_severity[a])
            .cmp(&severity_rank(by_rule_severity[b]))
            .then_with(|| a.cmp(b))
    });
    let fix_me_first: Vec<FixMeItem> = rule_ids
        .iter()
        .map(|rid| FixMeItem {
            rule_id: rid.to_string(),
            severity: by_rule_severity[rid],
            count: by_rule_count[rid],
        })
        .collect();

    ConformanceSummary {
        title: title.to_string(),
        author: author.to_string(),
        file_count,
        run_date: run_date.to_string(),
        score_percent: score,
        rules_passing: passing,
        rules_total_active: total_active,
        error_count: *severity_counts.get(&Severity::Error).unwrap_or(&0),
        warning_count: *severity_counts.get(&Severity::Warning).unwrap_or(&0),
        info_count: *severity_counts.get(&Severity::Info).unwrap_or(&0),
        top_five,
        fix_me_first,
    }
}

/// Mirrors `report.py::_render_md`.
pub fn render_md(summary: &ConformanceSummary) -> String {
    let score = match summary.score_percent {
        Some(p) => format!("{p} %"),
        None => "n/a".to_string(),
    };
    let mut parts = vec![
        format!("# JSS conformance report — {}", summary.title),
        String::new(),
        format!("- **Author:** {}", summary.author),
        format!("- **Files:** {}", summary.file_count),
        format!("- **Run date:** {}", summary.run_date),
        String::new(),
        format!("## Conformance score: {score}"),
        format!(
            "({} of {} rules pass)",
            summary.rules_passing, summary.rules_total_active
        ),
        String::new(),
        "## Severity counts".to_string(),
        format!("- Errors: {}", summary.error_count),
        format!("- Warnings: {}", summary.warning_count),
        format!("- Info: {}", summary.info_count),
        String::new(),
        "## Top 5 most-violated rules".to_string(),
    ];
    if summary.top_five.is_empty() {
        parts.push("- (none)".to_string());
    } else {
        for e in &summary.top_five {
            parts.push(format!(
                "- `{}` — {} violation(s); {}:{}: {}",
                e.rule_id, e.count, e.example_file, e.example_line, e.example_excerpt
            ));
        }
    }
    parts.push(String::new());
    parts.push("## Fix me first".to_string());
    if summary.fix_me_first.is_empty() {
        parts.push("1. (no violations)".to_string());
    } else {
        for (i, item) in summary.fix_me_first.iter().enumerate() {
            parts.push(format!(
                "{}. `{}` ({}) — {}",
                i + 1,
                item.rule_id,
                item.severity.as_str(),
                item.count
            ));
        }
    }
    parts.push(String::new());
    parts.push("---".to_string());
    parts.push("Generated by jss-lint.".to_string());
    parts.join("\n") + "\n"
}

// ---------------------------------------------------------------------
// Manuscript metadata extraction (spec 015 follow-up)
// ---------------------------------------------------------------------

/// Recursively collects literal text from a node tree. Mirrors
/// `report.py::_node_plain_text`, which walks pylatexenc's generic
/// `chars`/`nodelist`/`nodeargd` attributes; this port's typed `Node`
/// enum has the same shape split across variants (`Chars.chars`,
/// `Group`/`Environment`/`Math.nodelist`, `Macro`/`Environment.args`).
fn node_plain_text(node: &Node) -> String {
    match node {
        Node::Chars(n) => n.chars.clone(),
        Node::Macro(n) => n.args.iter().flatten().map(node_plain_text).collect(),
        Node::Group(n) => n.nodelist.iter().map(node_plain_text).collect(),
        Node::Environment(n) => {
            let mut s: String = n.nodelist.iter().map(node_plain_text).collect();
            s.extend(n.args.iter().flatten().map(node_plain_text));
            s
        }
        Node::Math(n) => n.nodelist.iter().map(node_plain_text).collect(),
        Node::Comment(_) | Node::Specials(_) => String::new(),
    }
}

fn args_nodelist(args: &Args) -> impl Iterator<Item = &Node> {
    args.iter().flatten()
}

/// Walks `items` depth-first, recording the first non-empty
/// brace-arg text for each macro name in `macronames` encountered.
/// Mirrors `report.py::_first_macro_arg_text`'s inner `walk`.
fn walk_for_macro_text<'a>(
    items: &'a [Node],
    macronames: &[&str],
    found: &mut HashMap<&'a str, String>,
) {
    for n in items {
        if let Node::Macro(m) = n {
            let name: &'a str = m.macroname.as_str();
            if macronames.contains(&name) && !found.contains_key(name) {
                for arg in args_nodelist(&m.args) {
                    let text = node_plain_text(arg).trim().to_string();
                    if !text.is_empty() {
                        found.insert(name, text);
                        break;
                    }
                }
            }
        }
        match n {
            Node::Group(g) => walk_for_macro_text(&g.nodelist, macronames, found),
            Node::Environment(e) => walk_for_macro_text(&e.nodelist, macronames, found),
            Node::Math(m) => walk_for_macro_text(&m.nodelist, macronames, found),
            _ => {}
        }
        let args: Option<&Args> = match n {
            Node::Macro(m) => Some(&m.args),
            Node::Environment(e) => Some(&e.args),
            _ => None,
        };
        if let Some(args) = args {
            for arg in args_nodelist(args) {
                match arg {
                    Node::Group(g) => walk_for_macro_text(&g.nodelist, macronames, found),
                    Node::Environment(e) => walk_for_macro_text(&e.nodelist, macronames, found),
                    Node::Math(m) => walk_for_macro_text(&m.nodelist, macronames, found),
                    _ => {}
                }
            }
        }
    }
}

fn first_macro_arg_text(nodes: &[Node], macronames: &[&str]) -> Option<String> {
    let mut found: HashMap<&str, String> = HashMap::new();
    walk_for_macro_text(nodes, macronames, &mut found);
    macronames.iter().find_map(|name| found.get(name).cloned())
}

/// Returns `(title, author)` extracted from the parsed document's
/// preamble. Mirrors `report.py::extract_metadata`, which iterates
/// `document.all_tex_like()` — every `.tex`/`.rnw` file plus every
/// `.Rmd` file's raw-LaTeX prose fragments.
pub fn extract_metadata(document: &ParsedDocument) -> (Option<String>, Option<String>) {
    let mut title: Option<String> = None;
    let mut author: Option<String> = None;
    for tex_file in document.all_tex_like_docs() {
        let nodes = &tex_file.parsed.nodes;
        if title.is_none() {
            title = first_macro_arg_text(nodes, TITLE_MACROS);
        }
        if author.is_none() {
            author = first_macro_arg_text(nodes, AUTHOR_MACROS);
        }
        if title.is_some() && author.is_some() {
            break;
        }
    }
    (title, author)
}
