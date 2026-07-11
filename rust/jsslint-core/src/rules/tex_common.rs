//! Shared tex-rule infrastructure — spec 018 Phase 3. Ports
//! `_helpers.py`'s `make_violation` / `tex_violation` / `_lineno_col`
//! factories (the tex-side counterparts of `entry_violation` in
//! `rules::mod`).

use crate::catalogue;
use crate::report::{Fix, Violation};
use crate::tex::position::LineIndex;

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
