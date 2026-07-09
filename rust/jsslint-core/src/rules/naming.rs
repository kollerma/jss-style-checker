//! Naming rules — mirrors `journals/jss/rules/naming.py`'s bib-facing
//! rule (JSS-NAME-002 only; JSS-NAME-001, a prose/tex_files rule, is
//! Phase 3 scope).

use super::{entry_violation_with_fix, field_value_span, py_repr, referenced_entries};
use crate::bib::{Entry, Library};
use crate::report::{Fix, FixConfidence, Violation};
use crate::terms::TERMS;
use crate::tex::node::Node as TexNode;

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
