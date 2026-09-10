//! Shared tex-rule infrastructure — spec 018 Phase 3. Ports
//! `_helpers.py`'s `make_violation` / `tex_violation` / `_lineno_col`
//! factories (the tex-side counterparts of `entry_violation` in
//! `rules::mod`).

use crate::catalogue;
use crate::report::{Fix, Violation};
use crate::tex::extract::group_text;
use crate::tex::node::{EnvironmentNode, Node};
use crate::tex::position::LineIndex;
use crate::tex::prose::walk;

/// Generic catalogue-backed violation: severity/message come from the
/// rule's catalogue entry; the caller supplies position. Mirrors
/// `_helpers.py::make_violation`.
pub fn make_violation(
    file: &str,
    line: u32,
    column: Option<u32>,
    rule_id: &str,
    suggestion: Option<String>,
    fix: Option<Fix>,
) -> Violation {
    let meta = catalogue::lookup(rule_id).unwrap_or_else(|| panic!("unknown rule_id {rule_id}"));
    Violation {
        file: file.to_string(),
        line,
        column,
        rule_id: rule_id.to_string(),
        severity: meta.severity,
        message: meta.message_template.to_string(),
        suggestion,
        fix,
    }
}

/// `(1-based line, 1-based column)` at a codepoint position — mirrors
/// `_helpers.py::_lineno_col` (`walker.pos_to_lineno_colno` + 1 on the
/// 0-based column it returns).
pub fn lineno_col(line_index: &LineIndex, pos: usize) -> (u32, u32) {
    let (line, col0) = line_index.lineno_colno(pos);
    (line, col0 + 1)
}

/// A violation anchored to a source position inside a parsed tex-like
/// file. Mirrors `_helpers.py::tex_violation`.
pub fn tex_violation(
    file: &str,
    line_index: &LineIndex,
    pos: usize,
    rule_id: &str,
    suggestion: Option<String>,
) -> Violation {
    tex_violation_with_fix(file, line_index, pos, rule_id, suggestion, None)
}

pub fn tex_violation_with_fix(
    file: &str,
    line_index: &LineIndex,
    pos: usize,
    rule_id: &str,
    suggestion: Option<String>,
    fix: Option<Fix>,
) -> Violation {
    let (line, column) = lineno_col(line_index, pos);
    make_violation(file, line, Some(column), rule_id, suggestion, fix)
}

// ---------------------------------------------------------------------------
// Token-specific suggestions (spec 027 item S)
// ---------------------------------------------------------------------------

/// Identifier length for an equation body head — mirrors
/// `_helpers._EQUATION_BODY_LIMIT`.
const EQUATION_BODY_LIMIT: usize = 40;

/// Python `str.split()`'s whitespace set. `char::is_whitespace` covers
/// Unicode White_Space, which is *almost* the same — Python also splits
/// on the four ASCII information separators, so they are added here.
/// Without them a `\x1c` inside a caption would collapse in one engine
/// and not the other, and the two suggestions would diverge.
fn is_py_whitespace(c: char) -> bool {
    c.is_whitespace() || ('\u{1c}'..='\u{1f}').contains(&c)
}

/// Normalise *text* into a stable identifier for a suggestion.
///
/// Mirrors `_helpers.identifier` exactly (contract:
/// `specs/027-first-time-user-gaps/contracts/suggestions.md` C-3):
/// collapse whitespace runs to one space, trim, then truncate to
/// *limit* **characters** (not bytes) with no ellipsis, escaping and
/// case left alone. A baseline entry is keyed on the suggestion, so any
/// divergence here would re-key findings between engines.
pub fn identifier(text: &str, limit: usize) -> String {
    let collapsed = text
        .split(is_py_whitespace)
        .filter(|part| !part.is_empty())
        .collect::<Vec<_>>()
        .join(" ");
    collapsed.chars().take(limit).collect()
}

/// Name a display equation: its `\label` key, else its first body line.
///
/// Mirrors `_helpers.equation_identifier`. `source` is the parsed file's
/// character vector; the body head is sliced out of it (not rebuilt from
/// the node list) so both engines quote the same source text.
pub fn equation_identifier(env: &EnvironmentNode, source: &[char]) -> String {
    let mut label: Option<String> = None;
    walk(&env.nodelist, &mut |node, _ancestors| {
        if label.is_some() {
            return;
        }
        let Node::Macro(m) = node else { return };
        if m.macroname != "label" {
            return;
        }
        for arg in m.args.iter().flatten() {
            let Node::Group(g) = arg else { continue };
            let key = identifier(&group_text(g), usize::MAX);
            if !key.is_empty() {
                label = Some(key);
                return;
            }
        }
    });
    if let Some(key) = label {
        return key;
    }

    let (Some(first), Some(last)) = (env.nodelist.first(), env.nodelist.last()) else {
        return String::new();
    };
    let start = first.span().pos;
    let end = (last.span().pos + last.span().len).min(source.len());
    if start >= end {
        return String::new();
    }
    let body: String = source[start..end].iter().collect();
    let first_row = body.split("\\\\").next().unwrap_or("");
    identifier(first_row, EQUATION_BODY_LIMIT)
}
