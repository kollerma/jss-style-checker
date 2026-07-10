//! Pure projections from `Violation`/`Fix` to LSP-shaped plain data —
//! mirrors `texlint/lsp/conversions.py`. Deliberately returns plain
//! structs, not `lsp_types` wire types: this module has no LSP
//! protocol library dependency, matching `conversions.py`'s own
//! design ("importable without `pygls`; the actual LSP server ...
//! lives in a sibling module"). `jsslint-cli`'s protocol-speaking
//! server converts these into `lsp_types` structs for transmission.

use crate::report::{Fix, Severity, Violation};

pub fn lsp_severity(sev: Severity) -> u8 {
    match sev {
        Severity::Error => 1,
        Severity::Warning => 2,
        Severity::Info => 3,
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Position {
    pub line: u32,
    pub character: u32,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Range {
    pub start: Position,
    pub end: Position,
}

#[derive(Debug, Clone)]
pub struct Diagnostic {
    pub range: Range,
    pub severity: u8,
    pub code: String,
    pub source: String,
    pub message: String,
    pub code_description_href: Option<String>,
}

#[derive(Debug, Clone)]
pub struct TextEdit {
    pub range: Range,
    pub new_text: String,
}

#[derive(Debug, Clone)]
pub struct CodeAction {
    pub title: String,
    pub kind: String,
    pub uri: String,
    pub edit: TextEdit,
}

/// Extent of the contiguous non-whitespace run starting exactly at
/// `col` (codepoint index into `text`), or `text`'s length when `col`
/// is out of bounds or lands on whitespace. Mirrors
/// `conversions.py`'s `_TOKEN_AT_RE = re.compile(r"\S+")` matched via
/// `.match(text, col)` (anchored at `col`, `None` on no match).
fn token_end(chars: &[char], col: usize) -> usize {
    if col >= chars.len() || chars[col].is_whitespace() {
        return chars.len();
    }
    let mut i = col;
    while i < chars.len() && !chars[i].is_whitespace() {
        i += 1;
    }
    i
}

/// Projects a `Violation` to an LSP `Diagnostic`. Mirrors
/// `conversions.py::violation_to_diagnostic`. With `source`, the range
/// spans the token at the violation's column (or the whole rstripped
/// line when the violation carries no column); without it, the range
/// is zero-width. `character`/`line` here are codepoint-indexed, not
/// UTF-16-code-unit-indexed as the LSP spec technically requires —
/// faithfully reproducing Python's own naive-but-consistent choice
/// (`str` indexing), not "fixing" it.
pub fn violation_to_diagnostic(
    v: &Violation,
    guide_url: Option<&str>,
    source: Option<&str>,
) -> Diagnostic {
    let line = v.line.saturating_sub(1);
    let mut col = v.column.unwrap_or(1).saturating_sub(1) as usize;
    let mut end_col = col;

    if let Some(source) = source {
        let lines: Vec<&str> = source.lines().collect();
        if (line as usize) < lines.len() {
            let text: Vec<char> = lines[line as usize].trim_end().chars().collect();
            if v.column.is_none() {
                col = 0;
                end_col = text.len();
            } else {
                col = col.min(text.len());
                end_col = token_end(&text, col);
            }
        }
    }

    Diagnostic {
        range: Range {
            start: Position {
                line,
                character: col as u32,
            },
            end: Position {
                line,
                character: end_col as u32,
            },
        },
        severity: lsp_severity(v.severity),
        code: v.rule_id.clone(),
        source: "jss-lint".to_string(),
        message: v.message.clone(),
        code_description_href: guide_url.map(|s| s.to_string()),
    }
}

/// Converts a 0-based codepoint offset into `text` to an LSP
/// `Position`. Mirrors `conversions.py::_byte_offset_to_lsp_position`
/// — misnamed on the Python side too (`Fix.start`/`.end` are codepoint
/// offsets, not byte offsets; see `report::Fix`'s doc comment for the
/// project-wide correction), faithfully replicated rather than
/// renamed away from its Python counterpart's quirk.
fn offset_to_lsp_position(text: &str, offset: usize) -> Position {
    let chunk: Vec<char> = text.chars().take(offset).collect();
    let line = chunk.iter().filter(|&&c| c == '\n').count() as u32;
    let character = match chunk.iter().rposition(|&c| c == '\n') {
        Some(idx) => (chunk.len() - idx - 1) as u32,
        None => chunk.len() as u32,
    };
    Position { line, character }
}

/// Mirrors `conversions.py::fix_to_text_edit`.
pub fn fix_to_text_edit(fix: &Fix, source: &str) -> TextEdit {
    TextEdit {
        range: Range {
            start: offset_to_lsp_position(source, fix.start),
            end: offset_to_lsp_position(source, fix.end),
        },
        new_text: fix.replacement.clone(),
    }
}

/// Projects a `Violation` carrying a `Fix` to an LSP `CodeAction`;
/// `None` when the violation has no fix. Mirrors
/// `conversions.py::violation_to_code_action`.
pub fn violation_to_code_action(v: &Violation, source: &str, uri: &str) -> Option<CodeAction> {
    let fix = v.fix.as_ref()?;
    Some(CodeAction {
        title: fix.description.clone(),
        kind: "quickfix".to_string(),
        uri: uri.to_string(),
        edit: fix_to_text_edit(fix, source),
    })
}
