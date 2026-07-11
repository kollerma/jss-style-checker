//! Abbreviations rule — mirrors `journals/jss/rules/abbreviations.py`
//! (JSS-ABBR-001).

use super::tex_common::tex_violation_with_fix;
use crate::report::{Fix, FixConfidence, Violation};
use crate::tex::node::Node;
use crate::tex::prose::{is_in_prose_context, walk_with_context, Slot};
use crate::tex::{position::LineIndex, ParsedTex};
use regex::Regex;
use std::sync::LazyLock;

static DOTTED_ABBREV_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"\b([A-Z])\.([A-Z])(\.[A-Z])*\.?").unwrap());
// Anchored at `^` (Python's `.match()` semantics).
static AUTHOR_INITIAL_FOLLOWER_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"^[~ ][A-Z][a-z]+").unwrap());
static KNOWN_DOTTED_ABBREVS: &[&str] = &["U.S.", "U.K.", "U.N.", "E.U.", "No."];
// `\Z` in Python -> `\z` in Rust (absolute end, not "before trailing \n").
static AUTHOR_SURNAME_COMMA_PREFIX_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"[A-Z][a-z]+(?:-[A-Z][a-z]+)*,\s+\z").unwrap());
static AUTHOR_SURNAME_SPACE_PREFIX_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"[A-Z][a-z]+(?:-[A-Z][a-z]+)*\s+\z").unwrap());
// Anchored at `^` (Python's `.match()` semantics).
static BIB_INITIAL_FOLLOWER_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"^\s*(?:,|\(\s*\d{4}|;|$)").unwrap());
static SURNAME_HEAD_RE: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"^[A-Z][a-z]+").unwrap());

/// Mirrors `abbreviations.py::_looks_like_author_initial`.
fn looks_like_author_initial(
    chars: &str,
    match_start: usize,
    match_end: usize,
    parent: &[Slot],
    idx: usize,
) -> bool {
    let n = chars.len();
    let tail_end = (match_end + 30).min(n);
    let tail = &chars[match_end..tail_end];
    if AUTHOR_INITIAL_FOLLOWER_RE.is_match(tail) {
        return true;
    }
    if tail.chars().next().is_some_and(|c| c.is_lowercase()) {
        return true;
    }
    if chars[match_end..].trim_end_matches([' ', '\t']).is_empty() {
        if let Some(Some(Node::Chars(c))) = parent.get(idx + 2) {
            let head_end = c
                .chars
                .char_indices()
                .nth(30)
                .map(|(i, _)| i)
                .unwrap_or(c.chars.len());
            let head = &c.chars[..head_end];
            if SURNAME_HEAD_RE.is_match(head) {
                return true;
            }
        }
    }
    // Python's `chars[match_start-60:match_start]` counts 60
    // CODEPOINTS back; `match_start` here is a Rust regex BYTE offset,
    // so this is 60 bytes back — a fuzzy lookback-window boundary that
    // only shifts (never breaks) in the presence of non-ASCII text
    // near the window edge. Accepted as a documented approximation for
    // this already-heuristic author-initial detector; the fixture
    // sweep would surface it if it ever mattered on a real file.
    let head_start = floor_char_boundary(chars, match_start.saturating_sub(60));
    let head = &chars[head_start..match_start];
    if AUTHOR_SURNAME_COMMA_PREFIX_RE.is_match(head) {
        return true;
    }
    if AUTHOR_SURNAME_SPACE_PREFIX_RE.is_match(head) && BIB_INITIAL_FOLLOWER_RE.is_match(tail) {
        return true;
    }
    false
}

fn floor_char_boundary(s: &str, mut i: usize) -> usize {
    while i > 0 && !s.is_char_boundary(i) {
        i -= 1;
    }
    i
}

/// JSS-ABBR-001 — abbreviations are uppercase without periods
/// (`U.S.A.` -> `USA`), excluding author-initial patterns.
pub fn check_abbr_001(file: &str, parsed: &ParsedTex) -> Vec<Violation> {
    let line_index = LineIndex::new(&parsed.chars);
    let mut out = Vec::new();
    let top: Vec<Slot> = parsed.nodes.iter().map(Some).collect();
    let mut ancestors: Vec<&Node> = Vec::new();
    walk_with_context(&top, &mut ancestors, &mut |node, ancestors, parent, idx| {
        let Node::Chars(c) = node else { return };
        if !is_in_prose_context(ancestors) {
            return;
        }
        for m in DOTTED_ABBREV_RE.find_iter(&c.chars) {
            let raw = m.as_str();
            if !KNOWN_DOTTED_ABBREVS.contains(&raw)
                && looks_like_author_initial(&c.chars, m.start(), m.end(), parent, idx)
            {
                continue;
            }
            let collapsed = raw.replace('.', "");
            let abs_pos = c.span.pos + c.chars[..m.start()].chars().count();
            let abs_end = c.span.pos + c.chars[..m.end()].chars().count();
            let fix = Fix {
                start: abs_pos,
                end: abs_end,
                replacement: collapsed.clone(),
                description: format!(
                    "Normalize abbreviation {} to canonical {}.",
                    super::py_repr(raw),
                    super::py_repr(&collapsed)
                ),
                confidence: FixConfidence::Safe,
            };
            out.push(tex_violation_with_fix(
                file,
                &line_index,
                abs_pos,
                "JSS-ABBR-001",
                Some(format!(
                    "Replace {} with {} (uppercase, no periods).",
                    super::py_repr(raw),
                    super::py_repr(&collapsed)
                )),
                Some(fix),
            ));
        }
    });
    out
}
