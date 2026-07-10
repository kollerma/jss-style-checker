//! Shared rule infrastructure — spec 018 Phase 2. Ports the parts of
//! `_helpers.py` and per-rule-module helper functions that more than
//! one bib rule needs: citation-scope resolution
//! (`_iter_referenced_entries` / `_collect_cited_keys`), the
//! `entry_line`/`entry_violation` factories, and the source-rescan
//! technique `naming.py`/`house_style.py` use to locate a field value's
//! byte span for a `Fix` (bibtexparser exposes no field-level offsets,
//! only `entry.start_line`).

pub mod abbreviations;
pub mod bibtex;
pub mod capitalization;
pub mod citations;
pub mod code_style;
pub mod code_width;
pub mod crossrefs;
pub mod house_style;
pub mod markup;
pub mod naming;
pub mod operators;
pub mod preamble;
pub mod references;
pub mod structure;
pub mod tex_common;
pub mod typography;

use crate::bib::{Entry, Library};
use crate::catalogue;
use crate::report::{Fix, Violation};
use crate::tex::extract;
use crate::tex::node::Node as TexNode;
use crate::tex::prose::{Slot, CITE_MACROS_FOR_SCOPE};
use std::collections::HashSet;

/// Mimics Python's `repr()` for a plain string — used everywhere a
/// rule message embeds a value via Python's `!r` (e.g.
/// `f"key {entry.key!r} ..."`). Rust's `{:?}` always double-quotes;
/// Python's `repr()` prefers single quotes and only switches to double
/// when the string contains a `'` but no `"` (CPython's
/// `unicode_repr`). Covers the common cases (quotes, backslash, `\n`/
/// `\r`/`\t`); does not attempt full `\xXX`-escaping of arbitrary
/// control characters, which none of these rules' inputs produce.
pub fn py_repr(s: &str) -> String {
    let has_single = s.contains('\'');
    let has_double = s.contains('"');
    let (quote, escape_quote) = if has_single && !has_double {
        ('"', '"')
    } else {
        ('\'', '\'')
    };
    let mut out = String::with_capacity(s.len() + 2);
    out.push(quote);
    for c in s.chars() {
        match c {
            '\\' => out.push_str("\\\\"),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            '\t' => out.push_str("\\t"),
            c if c == escape_quote => {
                out.push('\\');
                out.push(c);
            }
            c => out.push(c),
        }
    }
    out.push(quote);
    out
}

/// 1-based line of an entry's `@type{` opening. Mirrors
/// `_helpers.py::entry_line` (`entry.start_line` is 0-based).
pub fn entry_line(entry: &Entry) -> u32 {
    entry.start_line + 1
}

/// A catalogue-backed violation anchored to a bib entry's first line.
/// Mirrors `_helpers.py::entry_violation`.
pub fn entry_violation(
    file: &str,
    entry: &Entry,
    rule_id: &str,
    suggestion: Option<String>,
) -> Violation {
    let meta = catalogue::lookup(rule_id).unwrap_or_else(|| panic!("unknown rule_id {rule_id}"));
    Violation {
        file: file.to_string(),
        line: entry_line(entry),
        column: None,
        rule_id: rule_id.to_string(),
        severity: meta.severity,
        message: meta.message_template.to_string(),
        suggestion,
        fix: None,
    }
}

/// Same as `entry_violation` but with an attached `Fix`.
pub fn entry_violation_with_fix(
    file: &str,
    entry: &Entry,
    rule_id: &str,
    suggestion: Option<String>,
    fix: Option<Fix>,
) -> Violation {
    Violation {
        fix,
        ..entry_violation(file, entry, rule_id, suggestion)
    }
}

// --- citation-scope resolution (mirrors _helpers.py) ------------------

/// `(cited_keys, include_all)` from every `\cite*`/`\nocite` macro
/// across the given tex-like node lists. Mirrors
/// `_helpers.py::_collect_cited_keys`.
pub fn collect_cited_keys(tex_like: &[&[TexNode]]) -> (HashSet<String>, bool) {
    let mut keys = HashSet::new();
    let mut include_all = false;
    for &nodes in tex_like {
        extract::iter_with_parent_visit(nodes, &mut |parent: &[Slot], idx, node| {
            let TexNode::Macro(m) = node else { return };
            if !CITE_MACROS_FOR_SCOPE.contains(&m.macroname.as_str()) {
                return;
            }
            let text = extract::macro_args_text(m, parent, idx);
            for raw in text.split(',') {
                let key = raw.trim();
                if key == "*" {
                    include_all = true;
                } else if !key.is_empty() {
                    keys.insert(key.to_string());
                }
            }
        });
    }
    (keys, include_all)
}

/// Entries referenced from the paper's tex-like surface (or every
/// entry, per the bib-only / `\nocite{*}` scope-widening rules).
/// Mirrors `_helpers.py::_iter_referenced_entries`. `tex_like` empty
/// means "no tex/rnw/rmd input present" — the bib-only widening case.
pub fn referenced_entries<'a>(library: &'a Library, tex_like: &[&[TexNode]]) -> Vec<&'a Entry> {
    if tex_like.is_empty() {
        return library.entries.iter().collect();
    }
    let (cited, include_all) = collect_cited_keys(tex_like);
    let cited_lower: HashSet<String> = cited.iter().map(|k| k.to_lowercase()).collect();
    library
        .entries
        .iter()
        .filter(|e| include_all || cited_lower.contains(&e.key.to_lowercase()))
        .collect()
}

// --- field-value Fix span location (mirrors naming.py) -----------------

/// The `[start, end)` char-offset slice of `source` covering `entry`:
/// from the start of its `@type{` line through just before the next
/// line-starting `@` (or EOF). Mirrors `naming.py::_entry_source_span`.
pub fn entry_source_span(source_chars: &[char], entry: &Entry) -> (usize, usize) {
    let start = line_start_offset(source_chars, entry.start_line);
    let mut end = source_chars.len();
    let mut i = start + 1;
    while i < source_chars.len() {
        let at_line_start = i == start + 1 || source_chars[i - 1] == '\n';
        if at_line_start && source_chars[i] == '@' {
            end = i;
            break;
        }
        i += 1;
    }
    (start, end)
}

fn line_start_offset(chars: &[char], line: u32) -> usize {
    let mut offset = 0usize;
    let mut cur = 0u32;
    while cur < line {
        match chars[offset..].iter().position(|&c| c == '\n') {
            Some(rel) => {
                offset += rel + 1;
                cur += 1;
            }
            None => return chars.len(),
        }
    }
    offset
}

/// Locates `field_name = <delim><expected_value><delim>` within
/// `entry`'s source span and returns the `[start, end)` char-offset
/// span of JUST the value (delimiters excluded, whitespace trimmed) —
/// the same span a `Fix` should cover so the rewrite preserves the
/// surrounding `{}`/`""` style. Mirrors `naming.py::_field_value_span`,
/// **including its non-nested-brace limitation**: the value scanner
/// stops at the first `}`/`"`, it does not balance nested braces (this
/// is a deliberate parity choice, not an oversight — replicating
/// Python's regex `[^{}]*` exactly).
pub fn field_value_span(
    source_chars: &[char],
    entry: &Entry,
    field_name: &str,
    expected_value: &str,
) -> Option<(usize, usize)> {
    let (es, ee) = entry_source_span(source_chars, entry);
    let name_chars: Vec<char> = field_name.chars().collect();
    let mut i = es;
    while i < ee {
        let boundary_ok =
            i == es || !(source_chars[i - 1].is_ascii_alphanumeric() || source_chars[i - 1] == '_');
        let name_matches = boundary_ok
            && i + name_chars.len() <= ee
            && source_chars[i..i + name_chars.len()]
                .iter()
                .zip(&name_chars)
                .all(|(a, b)| a.eq_ignore_ascii_case(b));
        if !name_matches {
            i += 1;
            continue;
        }
        let mut j = skip_ws(source_chars, i + name_chars.len(), ee);
        if j >= ee || source_chars[j] != '=' {
            i += 1;
            continue;
        }
        j = skip_ws(source_chars, j + 1, ee);
        if j >= ee {
            break;
        }
        let (mut v_start, mut v_end) = match source_chars[j] {
            '{' => match find_char(source_chars, j + 1, ee, '}') {
                Some(close) => (j + 1, close),
                None => {
                    i += 1;
                    continue;
                }
            },
            '"' => match find_char(source_chars, j + 1, ee, '"') {
                Some(close) => (j + 1, close),
                None => {
                    i += 1;
                    continue;
                }
            },
            _ => {
                i += 1;
                continue;
            }
        };
        let literal: String = source_chars[v_start..v_end].iter().collect();
        if literal.trim() != expected_value {
            i += 1;
            continue;
        }
        // Trim in CHAR units (not `String::len()` bytes) since v_start/
        // v_end index `source_chars`, a `&[char]` — a byte-length delta
        // would corrupt these offsets for any non-ASCII whitespace-
        // adjacent content.
        let inner = &source_chars[v_start..v_end];
        let lead_ws = inner.iter().take_while(|c| c.is_whitespace()).count();
        let trail_ws = inner.iter().rev().take_while(|c| c.is_whitespace()).count();
        v_start += lead_ws;
        v_end -= trail_ws.min(inner.len() - lead_ws);
        return Some((v_start, v_end));
    }
    None
}

fn skip_ws(chars: &[char], mut i: usize, end: usize) -> usize {
    while i < end && chars[i].is_whitespace() {
        i += 1;
    }
    i
}

fn find_char(chars: &[char], start: usize, end: usize, needle: char) -> Option<usize> {
    (start..end).find(|&i| chars[i] == needle)
}
