//! Preamble rules — mirrors `journals/jss/rules/preamble.py`
//! (JSS-PRE-001..008). Single-file scope simplification per other
//! Phase 3 modules; the `.tex`/`.rnw`-only format restriction Python
//! encodes via `Rule(..., formats=_PREAMBLE_FORMATS)` is an engine
//! (Phase 4) concern, not modeled at the rule-function level here.

use super::py_repr;
use super::tex_common::{make_violation, tex_violation, tex_violation_with_fix};
use crate::report::{Fix, FixConfidence, Violation};
use crate::tex::extract;
use crate::tex::node::{GroupDelims, GroupNode, MacroNode, Node};
use crate::tex::position::LineIndex;
use crate::tex::prose::{walk, Slot};
use crate::tex::ParsedTex;

const VALID_CLASS_OPTIONS: &[&str] = &[
    "article",
    "codesnippet",
    "bookreview",
    "softwarereview",
    "shortnames",
    "nojss",
    "nofooter",
    "noheadings",
    "a4paper",
    "letterpaper",
];

const ABSTRACT_SENTINEL: &str = "an abstract is required";
const KEYWORDS_SENTINEL: &str = "at least one keyword is required";

// Macros that produce a single valid PDF-metadata-safe glyph (accents,
// spacing controls, special characters) and structural commands that
// get translated to plain text by JSS preprocessing (\and, \\,
// \newline). They don't justify a parallel \Plain* metadata twin.
// NOTE: the `"\\\\"` entry (two literal backslash characters) mirrors
// `preamble.py::_NON_MARKUP_PREAMBLE_MACROS`'s `"\\\\"` entry exactly
// — that Python string decodes to a 2-char value, but a `\\` control
// symbol's `macroname` is always 1 char (just `\`), so this entry can
// never actually match. Replicated as a latent no-op, not "fixed".
const NON_MARKUP_PREAMBLE_MACROS: &[&str] = &[
    "'",
    "`",
    "\"",
    "^",
    "~",
    "=",
    ".",
    "u",
    "v",
    "H",
    "t",
    "c",
    "d",
    "b",
    "r",
    "k",
    " ",
    ",",
    ";",
    ":",
    "!",
    "&",
    "_",
    "$",
    "#",
    "%",
    "{",
    "}",
    "ss",
    "aa",
    "AA",
    "ae",
    "AE",
    "oe",
    "OE",
    "o",
    "O",
    "l",
    "L",
    "i",
    "j",
    "S",
    "P",
    "and",
    "\\\\",
    "newline",
    "linebreak",
];

const AUTHOR_SEPARATOR_MACROS: &[&str] = &["and", "And", "AND"];

const PLAIN_MACROS: &[&str] = &["Plaintitle", "Plainauthor", "Plainkeywords"];

/// Every macro named `name`, pre-order, as `(macro, parent_seq, idx)`.
/// Mirrors `preamble.py::_iter_macros`.
fn iter_macros<'a>(nodes: &'a [Node], name: &str) -> Vec<(&'a MacroNode, Vec<Slot<'a>>, usize)> {
    let mut out = Vec::new();
    extract::iter_with_parent_visit(nodes, &mut |parent, idx, node| {
        if let Node::Macro(m) = node {
            if m.macroname == name {
                out.push((m, parent.to_vec(), idx));
            }
        }
    });
    out
}

/// First macro named `name`, pre-order. Mirrors
/// `preamble.py::_first_macro`.
fn first_macro<'a>(nodes: &'a [Node], name: &str) -> Option<(&'a MacroNode, Vec<Slot<'a>>, usize)> {
    iter_macros(nodes, name).into_iter().next()
}

/// The first `Group` argument of `macro` — checked in `args` first,
/// then the next sibling (unknown macros). Mirrors
/// `preamble.py::_first_group_arg`.
fn first_group_arg<'a>(
    macro_node: &'a MacroNode,
    parent: &[Slot<'a>],
    idx: usize,
) -> Option<&'a GroupNode> {
    for arg in &macro_node.args {
        if let Some(Node::Group(g)) = arg {
            return Some(g);
        }
    }
    extract::next_group_arg(parent, idx)
}

/// True when any descendant of `group` is a non-trivial macro, math,
/// or specials node. Mirrors `preamble.py::_group_contains_markup`.
pub(super) fn group_contains_markup(group: Option<&GroupNode>) -> bool {
    let Some(group) = group else { return false };
    let mut found = false;
    walk(&group.nodelist, &mut |node, _ancestors| match node {
        Node::Math(_) | Node::Specials(_) => found = true,
        Node::Macro(m) if !NON_MARKUP_PREAMBLE_MACROS.contains(&m.macroname.as_str()) => {
            found = true;
        }
        _ => {}
    });
    found
}

/// Concatenated plain char content of `group`, recursing into
/// descendants (no macro expansion), trimmed. Mirrors
/// `preamble.py::_group_plain_text` — distinct from the
/// direct-children-only variants of the same name in other rule
/// modules (see e.g. `typography.rs`).
pub(super) fn group_plain_text(group: &GroupNode) -> String {
    let mut out = String::new();
    walk(&group.nodelist, &mut |node, _ancestors| {
        if let Node::Chars(c) = node {
            out.push_str(&c.chars);
        }
    });
    out.trim().to_string()
}

/// `(macro, class_name, options)` for the first `\documentclass`, or
/// `None`. Mirrors `preamble.py::_class_and_options`.
fn class_and_options(parsed: &ParsedTex) -> Option<(&MacroNode, Option<String>, Vec<String>)> {
    let (macro_node, _parent, _idx) = first_macro(&parsed.nodes, "documentclass")?;
    let mut class_name = None;
    let mut options = Vec::new();
    for arg in &macro_node.args {
        if let Some(Node::Group(g)) = arg {
            let text = group_plain_text(g);
            match g.delims {
                GroupDelims::Bracket => {
                    options = text
                        .split(',')
                        .map(|s| s.trim().to_string())
                        .filter(|s| !s.is_empty())
                        .collect();
                }
                GroupDelims::Brace => {
                    class_name = Some(text);
                }
            }
        }
    }
    Some((macro_node, class_name, options))
}

/// True when the document uses `\documentclass{jss}` (any options).
/// Mirrors `preamble.py::_has_jss_class`.
pub(super) fn has_jss_class(parsed: &ParsedTex) -> bool {
    class_and_options(parsed).is_some_and(|(_, name, _)| name.as_deref() == Some("jss"))
}

/// True for `\documentclass{jss}` *without* the `nojss` option.
/// Mirrors `preamble.py::_has_strict_jss_class`.
fn has_strict_jss_class(parsed: &ParsedTex) -> bool {
    match class_and_options(parsed) {
        Some((_, Some(name), options)) if name == "jss" => !options.iter().any(|o| o == "nojss"),
        _ => false,
    }
}

fn violation_at_file_start(file: &str, rule_id: &str, suggestion: &str) -> Violation {
    make_violation(
        file,
        1,
        Some(1),
        rule_id,
        Some(suggestion.to_string()),
        None,
    )
}

fn py_repr_list(items: &[String]) -> String {
    let inner = items
        .iter()
        .map(|s| py_repr(s))
        .collect::<Vec<_>>()
        .join(", ");
    format!("[{inner}]")
}

/// JSS-PRE-001 — `\documentclass` must be jss with a valid class
/// option.
pub fn check_pre_001(file: &str, parsed: &ParsedTex) -> Vec<Violation> {
    let line_index = LineIndex::new(&parsed.chars);
    let mut out = Vec::new();
    let Some((macro_node, class_name, options)) = class_and_options(parsed) else {
        return out;
    };
    if class_name.as_deref() == Some("jss") {
        let unknown: Vec<String> = options
            .into_iter()
            .filter(|o| !VALID_CLASS_OPTIONS.contains(&o.as_str()))
            .collect();
        if !unknown.is_empty() {
            out.push(tex_violation(
                file,
                &line_index,
                macro_node.span.pos,
                "JSS-PRE-001",
                Some(format!(
                    "Unknown jss class option(s): {}. Allowed: article, codesnippet, bookreview, softwarereview (optionally with shortnames, nojss).",
                    py_repr_list(&unknown)
                )),
            ));
        }
        return out;
    }
    out.push(tex_violation(
        file,
        &line_index,
        macro_node.span.pos,
        "JSS-PRE-001",
        Some(
            "Use \\documentclass[article]{jss} (or codesnippet / bookreview / softwarereview)."
                .to_string(),
        ),
    ));
    out
}

/// JSS-PRE-002 — preamble defines `\Address{}`.
pub fn check_pre_002(file: &str, parsed: &ParsedTex) -> Vec<Violation> {
    let mut out = Vec::new();
    if first_macro(&parsed.nodes, "Address").is_none() && has_strict_jss_class(parsed) {
        out.push(violation_at_file_start(
            file,
            "JSS-PRE-002",
            "Add \\Address{...} in the preamble with author affiliation and e-mail.",
        ));
    }
    out
}

/// Project a nodelist to a PDF-metadata-safe plain-text string. Used
/// by PRE-003's auto-fix. Mirrors `preamble.py::_project_nodelist_to_plain`
/// — `source_chars` stands in for pylatexenc's `node.latex_verbatim()`
/// (Math nodes' raw source, `$`-stripped), which Rust has no per-node
/// method for.
fn project_nodelist_to_plain(source_chars: &[char], nodelist: &[Node]) -> String {
    let mut parts = Vec::new();
    for node in nodelist {
        match node {
            Node::Chars(c) => parts.push(c.chars.clone()),
            Node::Macro(m) => {
                for arg in &m.args {
                    if let Some(Node::Group(g)) = arg {
                        parts.push(project_nodelist_to_plain(source_chars, &g.nodelist));
                    }
                }
            }
            Node::Math(math) => {
                let raw: String = source_chars[math.span.pos..math.span.pos + math.span.len]
                    .iter()
                    .collect();
                parts.push(raw.trim_matches('$').to_string());
            }
            Node::Group(g) => {
                parts.push(project_nodelist_to_plain(source_chars, &g.nodelist));
            }
            _ => {}
        }
    }
    parts
        .concat()
        .split_whitespace()
        .collect::<Vec<_>>()
        .join(" ")
}

/// JSS-PRE-003 — if `\title{}` has markup, `\Plaintitle{}` is also
/// defined.
pub fn check_pre_003(file: &str, parsed: &ParsedTex) -> Vec<Violation> {
    let line_index = LineIndex::new(&parsed.chars);
    let mut out = Vec::new();
    if !has_strict_jss_class(parsed) {
        return out;
    }
    let Some((macro_node, parent, idx)) = first_macro(&parsed.nodes, "title") else {
        return out;
    };
    let group = first_group_arg(macro_node, &parent, idx);
    if !group_contains_markup(group) {
        return out;
    }
    if first_macro(&parsed.nodes, "Plaintitle").is_some() {
        return out;
    }
    let suggestion =
        "\\title{} contains LaTeX markup; add a \\Plaintitle{} with the markup-free form for PDF metadata."
            .to_string();
    let group = group.expect("group_contains_markup(None) is false");
    let plain_text = project_nodelist_to_plain(&parsed.chars, &group.nodelist);
    if plain_text.is_empty() {
        out.push(tex_violation(
            file,
            &line_index,
            macro_node.span.pos,
            "JSS-PRE-003",
            Some(suggestion),
        ));
        return out;
    }
    let insert_pos = macro_node.span.pos + macro_node.span.len;
    let replacement = format!("\n\\Plaintitle{{{plain_text}}}");
    out.push(tex_violation_with_fix(
        file,
        &line_index,
        macro_node.span.pos,
        "JSS-PRE-003",
        Some(suggestion),
        Some(Fix {
            start: insert_pos,
            end: insert_pos,
            replacement,
            description: format!("insert \\Plaintitle{{{plain_text}}}"),
            confidence: FixConfidence::Safe,
        }),
    ));
    out
}

/// Walk `\author{...}`'s nodelist and project it to plain text,
/// translating `\and`/`\And`/`\AND` to a literal `, `. Mirrors
/// `preamble.py::_project_author_plain_text` / `_project_nodes`.
fn project_author_plain_text(group: Option<&GroupNode>) -> String {
    let Some(group) = group else {
        return String::new();
    };
    let mut parts = Vec::new();
    project_nodes(&group.nodelist, &mut parts);
    let raw = parts.concat();
    let mut collapsed = raw.split_whitespace().collect::<Vec<_>>().join(" ");
    while collapsed.contains(" ,") {
        collapsed = collapsed.replace(" ,", ",");
    }
    while collapsed.contains(",,") {
        collapsed = collapsed.replace(",,", ",");
    }
    collapsed.trim().trim_matches(',').trim().to_string()
}

fn project_nodes(nodes: &[Node], out: &mut Vec<String>) {
    for node in nodes {
        match node {
            Node::Chars(c) => out.push(c.chars.clone()),
            Node::Macro(m) => {
                if AUTHOR_SEPARATOR_MACROS.contains(&m.macroname.as_str()) {
                    out.push(", ".to_string());
                    continue;
                }
                for arg in &m.args {
                    if let Some(Node::Group(g)) = arg {
                        project_nodes(&g.nodelist, out);
                    }
                }
            }
            Node::Group(g) => project_nodes(&g.nodelist, out),
            _ => {}
        }
    }
}

/// Shared PRE-003-family markup/Plain* pairing check. Mirrors
/// `preamble.py::_check_markup_plain_pair`.
#[allow(clippy::too_many_arguments)]
fn check_markup_plain_pair(
    file: &str,
    parsed: &ParsedTex,
    line_index: &LineIndex,
    markup_macro: &str,
    plain_macro: &str,
    rule_id: &str,
    emit_fix: bool,
) -> Vec<Violation> {
    let mut out = Vec::new();
    if !has_strict_jss_class(parsed) {
        return out;
    }
    let Some((macro_node, parent, idx)) = first_macro(&parsed.nodes, markup_macro) else {
        return out;
    };
    let group = first_group_arg(macro_node, &parent, idx);
    if !group_contains_markup(group) {
        return out;
    }
    if first_macro(&parsed.nodes, plain_macro).is_some() {
        return out;
    }
    let suggestion = format!(
        "\\{markup_macro}{{}} contains LaTeX markup; add a \\{plain_macro}{{}} with the markup-free form for PDF metadata."
    );
    let mut fix = None;
    if emit_fix {
        let group = group.expect("group_contains_markup(None) is false");
        let plain_text = if rule_id == "JSS-PRE-007" {
            project_author_plain_text(Some(group))
        } else {
            group_plain_text(group)
        };
        if !plain_text.is_empty() {
            let insertion_pos = group.span.pos + group.span.len;
            let replacement = format!("\n\\{plain_macro}{{{plain_text}}}");
            fix = Some(Fix {
                start: insertion_pos,
                end: insertion_pos,
                replacement,
                description: format!(
                    "Insert \\{plain_macro}{{{plain_text}}} after \\{markup_macro}{{}}."
                ),
                confidence: FixConfidence::Safe,
            });
        }
    }
    out.push(tex_violation_with_fix(
        file,
        line_index,
        macro_node.span.pos,
        rule_id,
        Some(suggestion),
        fix,
    ));
    out
}

/// JSS-PRE-007 — if `\author{}` has markup, `\Plainauthor{}` is also
/// defined.
pub fn check_pre_007(file: &str, parsed: &ParsedTex) -> Vec<Violation> {
    let line_index = LineIndex::new(&parsed.chars);
    check_markup_plain_pair(
        file,
        parsed,
        &line_index,
        "author",
        "Plainauthor",
        "JSS-PRE-007",
        true,
    )
}

/// JSS-PRE-008 — if `\Keywords{}` has markup, `\Plainkeywords{}` is
/// also defined.
pub fn check_pre_008(file: &str, parsed: &ParsedTex) -> Vec<Violation> {
    let line_index = LineIndex::new(&parsed.chars);
    check_markup_plain_pair(
        file,
        parsed,
        &line_index,
        "Keywords",
        "Plainkeywords",
        "JSS-PRE-008",
        true,
    )
}

/// Shared PRE-004/PRE-005 required-macro-present-and-not-sentinel
/// check. Mirrors `preamble.py::_check_required_macro`.
#[allow(clippy::too_many_arguments)]
fn check_required_macro(
    file: &str,
    parsed: &ParsedTex,
    line_index: &LineIndex,
    macro_name: &str,
    sentinel: &str,
    rule_id: &str,
    suggestion_missing: &str,
    suggestion_sentinel: &str,
) -> Vec<Violation> {
    let mut out = Vec::new();
    if !has_jss_class(parsed) {
        return out;
    }
    let Some((macro_node, parent, idx)) = first_macro(&parsed.nodes, macro_name) else {
        out.push(violation_at_file_start(file, rule_id, suggestion_missing));
        return out;
    };
    let group = first_group_arg(macro_node, &parent, idx);
    let text = group.map(group_plain_text).unwrap_or_default();
    if text.to_lowercase().contains(sentinel) {
        out.push(tex_violation(
            file,
            line_index,
            macro_node.span.pos,
            rule_id,
            Some(suggestion_sentinel.to_string()),
        ));
    }
    out
}

/// JSS-PRE-004 — `\Abstract{}` is present and not the sentinel
/// placeholder.
pub fn check_pre_004(file: &str, parsed: &ParsedTex) -> Vec<Violation> {
    let line_index = LineIndex::new(&parsed.chars);
    check_required_macro(
        file,
        parsed,
        &line_index,
        "Abstract",
        ABSTRACT_SENTINEL,
        "JSS-PRE-004",
        "Add \\Abstract{...} in the preamble with the paper's abstract.",
        "Replace the jss.cls placeholder text with the actual abstract.",
    )
}

/// JSS-PRE-005 — `\Keywords{}` is present and not the sentinel
/// placeholder.
pub fn check_pre_005(file: &str, parsed: &ParsedTex) -> Vec<Violation> {
    let line_index = LineIndex::new(&parsed.chars);
    check_required_macro(
        file,
        parsed,
        &line_index,
        "Keywords",
        KEYWORDS_SENTINEL,
        "JSS-PRE-005",
        "Add \\Keywords{...} in the preamble with comma-separated keywords.",
        "Replace the jss.cls placeholder text with the actual keywords.",
    )
}

/// JSS-PRE-006 — `\Plaintitle`/`\Plainauthor`/`\Plainkeywords`
/// contain no LaTeX markup.
pub fn check_pre_006(file: &str, parsed: &ParsedTex) -> Vec<Violation> {
    let line_index = LineIndex::new(&parsed.chars);
    let mut out = Vec::new();
    for &name in PLAIN_MACROS {
        for (macro_node, parent, idx) in iter_macros(&parsed.nodes, name) {
            let group = first_group_arg(macro_node, &parent, idx);
            if !group_contains_markup(group) {
                continue;
            }
            let plain_text = group.map(group_plain_text).unwrap_or_default();
            let fix = if !plain_text.is_empty() {
                group.map(|g| Fix {
                    start: g.span.pos + 1,
                    end: g.span.pos + g.span.len - 1,
                    replacement: plain_text.clone(),
                    description: "strip markup from \\Plain*{}".to_string(),
                    confidence: FixConfidence::Safe,
                })
            } else {
                None
            };
            out.push(tex_violation_with_fix(
                file,
                &line_index,
                macro_node.span.pos,
                "JSS-PRE-006",
                Some(format!(
                    "Strip LaTeX macros from \\{name}{{}}: PDF metadata must be plain text."
                )),
                fix,
            ));
        }
    }
    out
}
