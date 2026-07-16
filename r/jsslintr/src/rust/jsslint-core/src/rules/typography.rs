//! Typography rules — mirrors `journals/jss/rules/typography.py`
//! (JSS-TYPO-001/002/003/004).

use super::tex_common::tex_violation_with_fix;
use crate::report::{Fix, FixConfidence, Violation};
use crate::tex::node::{EnvironmentNode, GroupNode, MacroNode, Node};
use crate::tex::prose::{walk, walk_with_context, Slot};
use crate::tex::{position::LineIndex, ParsedTex};

const FIGURE_TABLE_ENVS: &[&str] = &["figure", "figure*", "table", "table*"];
const SUBFLOAT_ENVS: &[&str] = &[
    "subfigure",
    "subtable",
    "subfloat",
    "minipage",
    "wrapfigure",
    "wraptable",
    "sidewaysfigure",
    "sidewaystable",
];
const EMPHASIS_MACROS: &[&str] = &["emph", "textbf", "textit", "textsl", "textsc"];

fn nearest_env<'a>(ancestors: &[&'a Node], names: &[&str]) -> Option<&'a EnvironmentNode> {
    ancestors.iter().rev().find_map(|anc| match anc {
        Node::Environment(e) if names.contains(&e.environmentname.as_str()) => Some(e),
        _ => None,
    })
}

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
    crate::tex::extract::next_group_arg(parent, idx)
}

fn group_visible_children(group: &GroupNode) -> Vec<&Node> {
    group
        .nodelist
        .iter()
        .filter(|child| match child {
            Node::Macro(m) if m.macroname == "label" => false,
            Node::Chars(c) if c.chars.trim().is_empty() => false,
            _ => true,
        })
        .collect()
}

fn group_plain_text(group: &GroupNode) -> String {
    group
        .nodelist
        .iter()
        .filter_map(|child| match child {
            Node::Chars(c) => Some(c.chars.as_str()),
            _ => None,
        })
        .collect()
}

/// Every `\caption` macro: `(macro, parent_seq, idx, enclosing figure/
/// table env)`. Mirrors `typography.py::_iter_captions`.
fn iter_captions<'a>(
    nodes: &'a [Node],
    skip_subfloats: bool,
) -> Vec<(
    &'a MacroNode,
    Vec<Slot<'a>>,
    usize,
    Option<&'a EnvironmentNode>,
)> {
    let mut out = Vec::new();
    let top: Vec<Slot<'a>> = nodes.iter().map(Some).collect();
    let mut ancestors: Vec<&'a Node> = Vec::new();
    walk_with_context(&top, &mut ancestors, &mut |node, ancestors, parent, idx| {
        let Node::Macro(m) = node else { return };
        if m.macroname != "caption" {
            return;
        }
        if skip_subfloats && nearest_env(ancestors, SUBFLOAT_ENVS).is_some() {
            return;
        }
        let env = nearest_env(ancestors, FIGURE_TABLE_ENVS);
        out.push((m, parent.to_vec(), idx, env));
    });
    out
}

/// Byte offset to insert `.` at so the caption text ends with a
/// period. Mirrors `typography.py::_caption_period_insert_pos`.
fn caption_period_insert_pos(group: &GroupNode) -> Option<usize> {
    for child in group.nodelist.iter().rev() {
        match child {
            Node::Chars(c) => {
                let stripped = c.chars.trim_end();
                if stripped.is_empty() {
                    continue;
                }
                return Some(c.span.pos + stripped.chars().count());
            }
            Node::Macro(m) if m.macroname == "label" => continue,
            _ => return None,
        }
    }
    None
}

/// JSS-TYPO-001 — figure/table captions end with a period.
pub fn check_typo_001(file: &str, parsed: &ParsedTex) -> Vec<Violation> {
    let line_index = LineIndex::new(&parsed.chars);
    let mut out = Vec::new();
    for (node, parent, idx, env) in iter_captions(&parsed.nodes, true) {
        if env.is_none() {
            continue;
        }
        let Some(group) = first_group_arg(node, &parent, idx) else {
            continue;
        };
        let text = group_plain_text(group);
        let text = text.trim_end();
        if text.is_empty() || text.ends_with('.') {
            continue;
        }
        let insert_pos = if text.ends_with('?') || text.ends_with('!') {
            None
        } else {
            caption_period_insert_pos(group)
        };
        let fix = insert_pos.map(|pos| Fix {
            start: pos,
            end: pos,
            replacement: ".".to_string(),
            description: "end caption with a period".to_string(),
            confidence: FixConfidence::Safe,
        });
        out.push(tex_violation_with_fix(
            file,
            &line_index,
            node.span.pos,
            "JSS-TYPO-001",
            Some("End the caption with a period.".to_string()),
            fix,
        ));
    }
    out
}

/// Trailing chars-only nodes containing only punctuation/space.
/// Mirrors `typography.py::_strip_trailing_punct`.
fn strip_trailing_punct(mut visible: Vec<&Node>) -> Vec<&Node> {
    while let Some(Node::Chars(c)) = visible.last() {
        if c.chars.chars().all(|ch| " \t\n.,;:!?-".contains(ch)) {
            visible.pop();
        } else {
            break;
        }
    }
    visible
}

/// JSS-TYPO-002 — caption not wholly wrapped in an emphasis macro.
pub fn check_typo_002(file: &str, parsed: &ParsedTex) -> Vec<Violation> {
    let line_index = LineIndex::new(&parsed.chars);
    let mut out = Vec::new();
    for (node, parent, idx, env) in iter_captions(&parsed.nodes, false) {
        if env.is_none() {
            continue;
        }
        let Some(group) = first_group_arg(node, &parent, idx) else {
            continue;
        };
        let visible = strip_trailing_punct(group_visible_children(group));
        if visible.len() != 1 {
            continue;
        }
        if let Node::Macro(sole) = visible[0] {
            if EMPHASIS_MACROS.contains(&sole.macroname.as_str()) {
                out.push(tex_violation_with_fix(
                    file,
                    &line_index,
                    sole.span.pos,
                    "JSS-TYPO-002",
                    Some(format!(
                        "Remove the wrapping \\{}{{...}} from the caption (intra-caption markup is fine).",
                        sole.macroname
                    )),
                    None,
                ));
            }
        }
    }
    out
}

/// JSS-TYPO-003 — no `\footnote` inside table environments.
pub fn check_typo_003(file: &str, parsed: &ParsedTex) -> Vec<Violation> {
    let line_index = LineIndex::new(&parsed.chars);
    let mut out = Vec::new();
    walk(&parsed.nodes, &mut |node, ancestors| {
        let Node::Macro(m) = node else { return };
        if m.macroname != "footnote" {
            return;
        }
        if nearest_env(ancestors, &["table", "table*"]).is_none() {
            return;
        }
        out.push(tex_violation_with_fix(
            file,
            &line_index,
            m.span.pos,
            "JSS-TYPO-003",
            Some("Move footnote annotations into the caption text.".to_string()),
            None,
        ));
    });
    out
}

const TYPO004_SKIPPABLE_MACROS: &[&str] =
    &["centering", "label", "small", "footnotesize", "scriptsize"];

fn first_caption_index(children: &[Node]) -> Option<usize> {
    children
        .iter()
        .position(|c| matches!(c, Node::Macro(m) if m.macroname == "caption"))
}

/// Mirrors `typography.py::_has_content_before`.
fn has_content_before(children: &[Node], cap_idx: usize) -> bool {
    for child in &children[..cap_idx] {
        match child {
            Node::Chars(c) => {
                if c.chars.trim().is_empty() {
                    if c.chars.matches('\n').count() >= 3 {
                        return true;
                    }
                    continue;
                }
                return true;
            }
            Node::Macro(m) if TYPO004_SKIPPABLE_MACROS.contains(&m.macroname.as_str()) => continue,
            _ => return true,
        }
    }
    false
}

/// JSS-TYPO-004 — `\caption{}` follows the figure/table content.
pub fn check_typo_004(file: &str, parsed: &ParsedTex) -> Vec<Violation> {
    let line_index = LineIndex::new(&parsed.chars);
    let mut out = Vec::new();
    walk(&parsed.nodes, &mut |node, _ancestors| {
        let Node::Environment(env) = node else { return };
        if !FIGURE_TABLE_ENVS.contains(&env.environmentname.as_str()) {
            return;
        }
        let Some(cap_idx) = first_caption_index(&env.nodelist) else {
            return;
        };
        if has_content_before(&env.nodelist, cap_idx) {
            return;
        }
        out.push(tex_violation_with_fix(
            file,
            &line_index,
            env.nodelist[cap_idx].span().pos,
            "JSS-TYPO-004",
            Some("Place \\caption{} after the figure / table content.".to_string()),
            None,
        ));
    });
    out
}
