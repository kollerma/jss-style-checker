//! House-style rules — mirrors `journals/jss/rules/house_style.py`:
//! JSS-HOUSE-001/003 (tex_files) and JSS-HOUSE-002 (bib_files).

use super::tex_common::{tex_violation, tex_violation_with_fix};
use super::{entry_violation_with_fix, field_value_span, py_repr, referenced_entries};
use crate::bib::{Entry, Library};
use crate::report::{Fix, FixConfidence, Violation};
use crate::tex::extract;
use crate::tex::node::Node as TexNode;
use crate::tex::node::{GroupDelims, MacroNode, Node};
use crate::tex::position::LineIndex;
use crate::tex::prose::{is_in_prose_context, walk_with_context, Slot};
use crate::tex::ParsedTex;
use regex::Regex;
use std::sync::LazyLock;

const JSS_LOADED_PACKAGES: &[&str] = &["graphicx", "xcolor", "ae", "fancyvrb", "hyperref"];

static EG_IE_RE: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"\b(e\.g\.|i\.e\.)").unwrap());

static WORDY_EDITION_RE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(
        r"(?i)^(?:first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|1e|2e|3e|4e|5e|6e|7e|8e|9e|10e)$",
    )
    .unwrap()
});

static REDUNDANT_EDITION_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"(?i)^\s*(\d+(?:st|nd|rd|th))\s+edition\s*$").unwrap());

fn edition_canonical(lower: &str) -> Option<&'static str> {
    Some(match lower {
        "first" => "1st",
        "second" => "2nd",
        "third" => "3rd",
        "fourth" => "4th",
        "fifth" => "5th",
        "sixth" => "6th",
        "seventh" => "7th",
        "eighth" => "8th",
        "ninth" => "9th",
        "tenth" => "10th",
        "1e" => "1st",
        "2e" => "2nd",
        "3e" => "3rd",
        "4e" => "4th",
        "5e" => "5th",
        "6e" => "6th",
        "7e" => "7th",
        "8e" => "8th",
        "9e" => "9th",
        "10e" => "10th",
        _ => return None,
    })
}

fn build_fix(source_chars: &[char], entry: &Entry, value: &str, canonical: &str) -> Option<Fix> {
    let (start, end) = field_value_span(source_chars, entry, "edition", value)?;
    Some(Fix {
        start,
        end,
        replacement: canonical.to_string(),
        description: format!("use {} for edition shorthand", py_repr(canonical)),
        confidence: FixConfidence::Safe,
    })
}

/// JSS-HOUSE-002 — book editions are "2nd"/"3rd"/etc, not
/// "second"/"2e"/"2nd edition".
pub fn check_house_002(
    bib_file: &str,
    bib_source_chars: &[char],
    library: &Library,
    tex_like: &[&[TexNode]],
) -> Vec<Violation> {
    let mut out = Vec::new();
    for entry in referenced_entries(library, tex_like) {
        let Some(field) = entry.field("edition") else {
            continue;
        };
        let value = field.value.trim().to_string();
        let suggestion = Some(format!(
            "Replace edition {} with an ordinal form (e.g., '2nd', '3rd').",
            py_repr(&value)
        ));
        let canonical = if WORDY_EDITION_RE.is_match(&value) {
            match edition_canonical(&value.to_lowercase()) {
                Some(c) => c,
                None => continue,
            }
        } else if let Some(caps) = REDUNDANT_EDITION_RE.captures(&value) {
            // `.lower()` of the matched ordinal group, matching
            // house_style.py's `m.group(1).lower()`.
            let ordinal = caps.get(1).unwrap().as_str().to_lowercase();
            out.push(entry_violation_with_fix(
                bib_file,
                entry,
                "JSS-HOUSE-002",
                suggestion,
                build_fix(bib_source_chars, entry, &value, &ordinal),
            ));
            continue;
        } else {
            continue;
        };
        out.push(entry_violation_with_fix(
            bib_file,
            entry,
            "JSS-HOUSE-002",
            suggestion,
            build_fix(bib_source_chars, entry, &value, canonical),
        ));
    }
    out
}

/// JSS-HOUSE-001 — "e.g." / "i.e." are followed by a comma.
pub fn check_house_001(file: &str, parsed: &ParsedTex) -> Vec<Violation> {
    let line_index = LineIndex::with_offset(&parsed.chars, parsed.line_offset);
    let mut out = Vec::new();
    let top: Vec<Slot> = parsed.nodes.iter().map(Some).collect();
    let mut ancestors: Vec<&Node> = Vec::new();
    walk_with_context(
        &top,
        &mut ancestors,
        &mut |node, ancestors, _parent, _idx| {
            let Node::Chars(c) = node else { return };
            if !is_in_prose_context(ancestors) {
                return;
            }
            for m in EG_IE_RE.find_iter(&c.chars) {
                if c.chars[m.end()..].starts_with(',') {
                    continue;
                }
                let matched = m.as_str();
                let abs_pos = c.span.pos + c.chars[..m.start()].chars().count();
                let dot_pos = c.span.pos + c.chars[..m.end()].chars().count() - 1;
                out.push(tex_violation_with_fix(
                    file,
                    &line_index,
                    abs_pos,
                    "JSS-HOUSE-001",
                    Some(format!(
                        "Add a comma after {}: '{matched},'.",
                        py_repr(matched)
                    )),
                    Some(Fix {
                        start: dot_pos,
                        end: dot_pos + 1,
                        replacement: ".,".to_string(),
                        description: "insert comma after e.g. / i.e.".to_string(),
                        confidence: FixConfidence::Safe,
                    }),
                ));
            }
        },
    );
    out
}

/// The first mandatory-arg package name of `\usepackage`. Mirrors
/// `house_style.py::_usepackage_name`.
fn usepackage_name<'a>(macro_node: &'a MacroNode, parent: &[Slot<'a>], idx: usize) -> String {
    for arg in &macro_node.args {
        if let Some(Node::Group(g)) = arg {
            if g.delims == GroupDelims::Bracket {
                continue;
            }
            return extract::group_text(g);
        }
    }
    if let Some(sibling) = extract::next_group_arg(parent, idx) {
        return extract::group_text(sibling);
    }
    String::new()
}

/// The `[options]` text of `\usepackage[...]{pkg}`, or `""`. Mirrors
/// `house_style.py::_usepackage_options`.
fn usepackage_options(macro_node: &MacroNode) -> String {
    for arg in &macro_node.args {
        if let Some(Node::Group(g)) = arg {
            if g.delims == GroupDelims::Bracket {
                return extract::group_text(g);
            }
        }
    }
    String::new()
}

/// `(line_start, line_end_after_newline)` if the line containing
/// `\usepackage{...}` (spanning `[macro_start, macro_end)`) consists
/// only of that macro and optional surrounding whitespace; `None`
/// otherwise. Offsets are codepoint indices into `source_chars` (a
/// `Fix`-ready deletion range including the trailing newline). Mirrors
/// `house_style.py::_whole_line_range`.
fn whole_line_range(
    source_chars: &[char],
    macro_start: usize,
    macro_end: usize,
) -> Option<(usize, usize)> {
    let prev_nl = source_chars[..macro_start].iter().rposition(|&c| c == '\n');
    let line_start = prev_nl.map_or(0, |p| p + 1);
    let next_nl = source_chars[macro_end..]
        .iter()
        .position(|&c| c == '\n')
        .map(|p| p + macro_end);
    let line_end = next_nl.map_or(source_chars.len(), |p| p + 1);

    let before_empty = source_chars[line_start..macro_start]
        .iter()
        .all(|c| c.is_whitespace());
    let after_end = next_nl.unwrap_or(source_chars.len());
    let after_empty = source_chars[macro_end..after_end]
        .iter()
        .all(|c| c.is_whitespace());
    if !before_empty || !after_empty {
        return None;
    }
    Some((line_start, line_end))
}

/// JSS-HOUSE-003 (info) — preamble avoids `\usepackage` for packages
/// jss.cls already loads (graphicx, xcolor, ae, fancyvrb, hyperref).
pub fn check_house_003(file: &str, parsed: &ParsedTex) -> Vec<Violation> {
    let mut out = Vec::new();
    if !super::preamble::has_jss_class(parsed) {
        return out;
    }
    let line_index = LineIndex::with_offset(&parsed.chars, parsed.line_offset);
    extract::iter_with_parent_visit(&parsed.nodes, &mut |parent, idx, node| {
        let Node::Macro(m) = node else { return };
        if m.macroname != "usepackage" {
            return;
        }
        let name = usepackage_name(m, parent, idx);
        if name.is_empty() {
            return;
        }
        if !JSS_LOADED_PACKAGES.contains(&name.as_str()) {
            return;
        }
        let options = usepackage_options(m);
        if !options.is_empty() {
            out.push(tex_violation(
                file,
                &line_index,
                m.span.pos,
                "JSS-HOUSE-003",
                Some(format!(
                    "Move the options to \\PassOptionsToPackage{{{options}}}{{{name}}} before \\documentclass — jss.cls already loads {name} (re-loading it with options is an option clash)."
                )),
            ));
            return;
        }
        let macro_end = m.span.pos + m.span.len;
        let fix = whole_line_range(&parsed.chars, m.span.pos, macro_end).map(|(start, end)| Fix {
            start,
            end,
            replacement: String::new(),
            description: format!("delete redundant \\usepackage{{{name}}}"),
            confidence: FixConfidence::Safe,
        });
        out.push(tex_violation_with_fix(
            file,
            &line_index,
            m.span.pos,
            "JSS-HOUSE-003",
            Some(format!(
                "Remove \\usepackage{{{name}}} — jss.cls already loads it."
            )),
            fix,
        ));
    });
    out
}
