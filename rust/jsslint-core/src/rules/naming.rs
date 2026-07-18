//! Naming rules — mirrors `journals/jss/rules/naming.py` (JSS-NAME-001
//! tex_files, JSS-NAME-002 bib_files).

use super::tex_common::tex_violation_with_fix;
use super::{entry_violation_with_fix, field_value_span, py_repr, referenced_entries};
use crate::bib::{Entry, Library};
use crate::report::{Fix, FixConfidence, Violation};
use crate::terms::TERMS;
use crate::tex::node::Node;
use crate::tex::node::Node as TexNode;
use crate::tex::position::LineIndex;
use crate::tex::prose::{is_in_prose_context, walk_with_context, Slot};
use crate::tex::ParsedTex;
use regex::Regex;
use std::sync::LazyLock;

static TOKEN_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"[A-Za-z][A-Za-z0-9+\-]*").unwrap());

static BARE_URL_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"(?i)\b(?:https?|ftp|ftps|file)://\S+").unwrap());

/// JSS-NAME-001 — programming-language names use canonical
/// capitalisation in prose (e.g. "JAVA" -> "Java"). Note: this checks
/// `TERMS.canonical` (aliases) directly, NOT `Terms::canonical_form`
/// (which also matches already-canonical `languages`/`r_packages`
/// members and would wrongly fire on e.g. bare "R") — mirrors
/// `naming.py::check_jss_name_001`'s `token not in CANONICAL` guard.
pub fn check_name_001(file: &str, parsed: &ParsedTex) -> Vec<Violation> {
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
            let url_spans: Vec<(usize, usize)> = BARE_URL_RE
                .find_iter(&c.chars)
                .map(|m| (m.start(), m.end()))
                .collect();
            for m in TOKEN_RE.find_iter(&c.chars) {
                let token = m.as_str();
                let Some(canonical) = TERMS.canonical.get(token) else {
                    continue;
                };
                if url_spans
                    .iter()
                    .any(|&(s, e)| s <= m.start() && m.start() < e)
                {
                    continue;
                }
                let after: String = c.chars[m.end()..].chars().take(4).collect();
                if after.trim_start().starts_with('(') {
                    continue;
                }
                let abs_pos = c.span.pos + c.chars[..m.start()].chars().count();
                let abs_end = c.span.pos + c.chars[..m.end()].chars().count();
                out.push(tex_violation_with_fix(
                    file,
                    &line_index,
                    abs_pos,
                    "JSS-NAME-001",
                    Some(format!(
                        "Use canonical form {} instead of {}.",
                        py_repr(canonical),
                        py_repr(token)
                    )),
                    Some(Fix {
                        start: abs_pos,
                        end: abs_end,
                        replacement: canonical.clone(),
                        description: format!(
                            "Replace {} with canonical {}.",
                            py_repr(token),
                            py_repr(canonical)
                        ),
                        confidence: FixConfidence::Safe,
                    }),
                ));
            }
        },
    );
    out
}

fn field_value(entry: &Entry, name: &str) -> String {
    entry
        .field(name)
        .map(|f| f.value.trim().to_string())
        .unwrap_or_default()
}

/// Mirrors `naming.py::_publisher_canonical`: exact match first, then
/// prefix match (word-boundary: exact, or followed by a space/comma).
/// `TERMS` is a `'static` static, so borrows into it are naturally
/// `'static` too — no unsafe lifetime extension needed.
fn publisher_canonical(value: &str) -> Option<&'static str> {
    if let Some(canon) = TERMS.publisher_canonical.get(value) {
        return Some(canon.as_str());
    }
    for (prefix, canonical) in &TERMS.publisher_prefix_canonical {
        if value == prefix
            || value.starts_with(&format!("{prefix} "))
            || value.starts_with(&format!("{prefix},"))
        {
            return Some(canonical.as_str());
        }
    }
    None
}

fn build_fix(
    source_chars: &[char],
    entry: &Entry,
    field_name: &str,
    raw_value: &str,
    canonical: &str,
) -> Option<Fix> {
    let (start, end) = field_value_span(source_chars, entry, field_name, raw_value)?;
    Some(Fix {
        start,
        end,
        replacement: canonical.to_string(),
        description: format!("use canonical form {}", py_repr(canonical)),
        confidence: FixConfidence::Safe,
    })
}

/// JSS-NAME-002 — BibTeX `publisher`/`journal` fields use JSS-canonical
/// forms.
pub fn check_name_002(
    bib_file: &str,
    bib_source_chars: &[char],
    library: &Library,
    tex_like: &[&[TexNode]],
) -> Vec<Violation> {
    let mut out = Vec::new();
    for entry in referenced_entries(library, tex_like) {
        let publisher = field_value(entry, "publisher");
        if !publisher.is_empty() {
            if let Some(canonical) = publisher_canonical(&publisher) {
                if canonical != publisher {
                    out.push(entry_violation_with_fix(
                        bib_file,
                        entry,
                        "JSS-NAME-002",
                        Some(format!(
                            "Replace publisher {} with {}.",
                            py_repr(&publisher),
                            py_repr(canonical)
                        )),
                        build_fix(bib_source_chars, entry, "publisher", &publisher, canonical),
                    ));
                }
            }
        }
        let journal = field_value(entry, "journal");
        if !journal.is_empty() {
            if let Some(canonical) = TERMS.journal_canonical.get(&journal) {
                out.push(entry_violation_with_fix(
                    bib_file,
                    entry,
                    "JSS-NAME-002",
                    Some(format!(
                        "Replace journal {} with {}.",
                        py_repr(&journal),
                        py_repr(canonical)
                    )),
                    build_fix(bib_source_chars, entry, "journal", &journal, canonical),
                ));
            }
        }
    }
    out
}
