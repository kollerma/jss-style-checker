//! BibTeX mechanical rules — mirrors
//! `journals/jss/rules/bibtex.py` (JSS-BIBTEX-001..005).

use super::{entry_violation, py_repr, referenced_entries};
use crate::bib::{Entry, Library};
use crate::catalogue;
use crate::report::Violation;
use crate::tex::extract;
use crate::tex::node::Node as TexNode;
use crate::tex::prose::{Slot, CITE_MACROS_FOR_SCOPE};
use regex::Regex;
use std::collections::{HashMap, HashSet};
use std::sync::LazyLock;

static AND_SPLIT_RE: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"\s+and\s+").unwrap());

const AUTHOR_THRESHOLD: usize = 6;

/// Required-field matrix per the catalogue's BIBTEX-003 notes. Each
/// entry is a tuple of alternative-field groups (any one field in the
/// group satisfies that requirement) — mirrors
/// `bibtex.py::_REQUIRED_FIELDS`.
fn required_fields(entry_type_lower: &str) -> Option<&'static [&'static [&'static str]]> {
    match entry_type_lower {
        "article" => Some(&[&["author"], &["title"], &["journal"], &["year"]]),
        "book" => Some(&[&["author", "editor"], &["title"], &["publisher"], &["year"]]),
        "inproceedings" => Some(&[&["author"], &["title"], &["booktitle"], &["year"]]),
        "incollection" => Some(&[
            &["author"],
            &["title"],
            &["booktitle"],
            &["publisher"],
            &["year"],
        ]),
        "inbook" => Some(&[
            &["author", "editor"],
            &["title"],
            &["chapter", "pages"],
            &["publisher"],
            &["year"],
        ]),
        "manual" => Some(&[&["title"]]),
        "mastersthesis" => Some(&[&["author"], &["title"], &["school"], &["year"]]),
        "phdthesis" => Some(&[&["author"], &["title"], &["school"], &["year"]]),
        "techreport" => Some(&[&["author"], &["title"], &["institution"], &["year"]]),
        "unpublished" => Some(&[&["author"], &["title"], &["note"]]),
        _ => None, // misc / unknown — no requirements
    }
}

/// JSS-BIBTEX-001 — every entry has a non-empty citation key.
pub fn check_bibtex_001(file: &str, library: &Library, tex_like: &[&[TexNode]]) -> Vec<Violation> {
    referenced_entries(library, tex_like)
        .into_iter()
        .filter(|e| e.key.is_empty())
        .map(|e| {
            entry_violation(
                file,
                e,
                "JSS-BIBTEX-001",
                Some("Give this entry a non-empty citation key.".to_string()),
            )
        })
        .collect()
}

/// JSS-BIBTEX-002 — citation keys are unique. Fires from
/// `Library::duplicate_block_keys`, not `entries` (see
/// `bib::parser`'s module docs on why a duplicate-keyed entry never
/// reaches `entries`).
pub fn check_bibtex_002(file: &str, library: &Library) -> Vec<Violation> {
    library
        .duplicate_block_keys
        .iter()
        .filter(|b| !b.key.is_empty())
        .map(|b| {
            entry_violation(
                file,
                &b.entry,
                "JSS-BIBTEX-002",
                Some(format!(
                    "Citation key {} is used more than once; rename one (e.g., add a suffix 'a' / 'b').",
                    py_repr(&b.key)
                )),
            )
        })
        .collect()
}

/// JSS-BIBTEX-003 — required fields present per entry type.
pub fn check_bibtex_003(file: &str, library: &Library, tex_like: &[&[TexNode]]) -> Vec<Violation> {
    let mut out = Vec::new();
    for entry in referenced_entries(library, tex_like) {
        let Some(requirements) = required_fields(&entry.entry_type.to_lowercase()) else {
            continue;
        };
        let have: HashSet<String> = entry.fields.iter().map(|f| f.key.to_lowercase()).collect();
        let missing_groups: Vec<&[&str]> = requirements
            .iter()
            .filter(|group| group.iter().all(|f| !have.contains(*f)))
            .copied()
            .collect();
        if missing_groups.is_empty() {
            continue;
        }
        let missing_str = missing_groups
            .iter()
            .map(|g| {
                let mut sorted: Vec<&str> = g.to_vec();
                sorted.sort();
                sorted.join("|")
            })
            .collect::<Vec<_>>()
            .join(" / ");
        out.push(entry_violation(
            file,
            entry,
            "JSS-BIBTEX-003",
            Some(format!(
                "Entry type {} is missing required field(s): {missing_str}.",
                py_repr(&entry.entry_type)
            )),
        ));
    }
    out
}

/// Mirrors `bibtex.py::_author_count`: `len(re.split(r"\s+and\s+",
/// value.strip()))` — note `re.split` on an empty string still returns
/// one (empty) element, so a present-but-empty `author` field counts
/// as 1, not 0. Matched faithfully via `Regex::split` (same behavior).
fn author_count(entry: &Entry) -> usize {
    match entry.field("author") {
        Some(f) => AND_SPLIT_RE.split(f.value.trim()).count(),
        None => 0,
    }
}

fn has_shortnames_option(tex_like: &[&[TexNode]]) -> bool {
    for &nodes in tex_like {
        for node in nodes {
            let TexNode::Macro(m) = node else { continue };
            if m.macroname != "documentclass" {
                continue;
            }
            for arg in &m.args {
                if let Some(TexNode::Group(g)) = arg {
                    let text = extract::group_text(g);
                    if text.contains("shortnames") {
                        return true;
                    }
                }
            }
            return false; // one \documentclass per preamble
        }
    }
    false
}

fn shortcites_keys(tex_like: &[&[TexNode]]) -> HashSet<String> {
    let mut out = HashSet::new();
    for &nodes in tex_like {
        extract::iter_with_parent_visit(nodes, &mut |parent: &[Slot], idx, node| {
            let TexNode::Macro(m) = node else { return };
            if m.macroname != "shortcites" {
                return;
            }
            let text = extract::macro_args_text(m, parent, idx);
            for key in text.split(',') {
                let key = key.trim();
                if !key.is_empty() {
                    out.insert(key.to_string());
                }
            }
        });
    }
    out
}

fn entries_by_key(library: &Library) -> HashMap<String, &Entry> {
    let mut out = HashMap::new();
    for entry in &library.entries {
        if !entry.key.is_empty() {
            out.entry(entry.key.clone()).or_insert(entry);
        }
    }
    out
}

/// One `(macro_pos, key)` per key referenced from a cite-family macro
/// site. Mirrors `bibtex.py::_iter_cite_sites` (position only — the
/// Python version also threads `tex`/`node`/`parent`/`idx` through for
/// line/column lookup, which the caller does here via `macro_pos`).
/// Returns `(tex_like_index, pos, key)` — the index into `tex_like`
/// identifies which tex file a cite site came from, so a caller with
/// more than one tex file can resolve `pos` against the right file's
/// own `LineIndex`.
fn cite_sites(tex_like: &[&[TexNode]]) -> Vec<(usize, usize, String)> {
    let mut out = Vec::new();
    for (i, &nodes) in tex_like.iter().enumerate() {
        extract::iter_with_parent_visit(nodes, &mut |parent: &[Slot], idx, node| {
            let TexNode::Macro(m) = node else { return };
            if !CITE_MACROS_FOR_SCOPE.contains(&m.macroname.as_str()) {
                return;
            }
            let text = extract::macro_args_text(m, parent, idx);
            for raw in text.split(',') {
                let key = raw.trim();
                if !key.is_empty() && key != "*" {
                    out.push((i, m.span.pos, key.to_string()));
                }
            }
        });
    }
    out
}

/// JSS-BIBTEX-004 — 6+ authors need `\shortcites{}` or the
/// `shortnames` class option.
///
/// `tex_files`: one `(file_name, LineIndex)` pair per slice in
/// `tex_like`, same order — resolves a cite site's char position to
/// its OWN file's 1-based line/col (mirrors `_helpers._lineno_col`
/// called with that cite's own `tex` file object in
/// `bibtex.py::check_jss_bibtex_004`; a single global resolver would
/// misattribute positions when a document has more than one tex file).
pub fn check_bibtex_004(
    bib_file: &str,
    tex_files: &[(&str, &crate::tex::position::LineIndex)],
    library: &Library,
    tex_like: &[&[TexNode]],
) -> Vec<Violation> {
    if has_shortnames_option(tex_like) {
        return Vec::new();
    }
    let shortcited = shortcites_keys(tex_like);
    let entries = entries_by_key(library);
    let meta = catalogue::lookup("JSS-BIBTEX-004").expect("JSS-BIBTEX-004 must be in catalogue");

    if tex_like.is_empty() {
        return referenced_entries(library, tex_like)
            .into_iter()
            .filter(|e| author_count(e) >= AUTHOR_THRESHOLD)
            .filter(|e| !(!e.key.is_empty() && shortcited.contains(&e.key)))
            .map(|e| {
                entry_violation(
                    bib_file,
                    e,
                    "JSS-BIBTEX-004",
                    Some(format!(
                        "Add the 'shortnames' option to \\documentclass{{jss}}, or list this key in \\shortcites{{{}}}.",
                        e.key
                    )),
                )
            })
            .collect();
    }

    let mut seen = HashSet::new();
    let mut out = Vec::new();
    for (tex_idx, pos, key) in cite_sites(tex_like) {
        if seen.contains(&key) || shortcited.contains(&key) {
            continue;
        }
        let Some(&entry) = entries.get(&key) else {
            continue;
        };
        if author_count(entry) < AUTHOR_THRESHOLD {
            continue;
        }
        seen.insert(key.clone());
        let (tex_file, line_index) = tex_files[tex_idx];
        let (line, column) = super::tex_common::lineno_col(line_index, pos);
        out.push(Violation {
            file: tex_file.to_string(),
            line,
            column: Some(column),
            rule_id: "JSS-BIBTEX-004".to_string(),
            severity: meta.severity,
            message: meta.message_template.to_string(),
            suggestion: Some(format!(
                "Add the 'shortnames' option to \\documentclass{{jss}}, or list this key in \\shortcites{{{key}}}."
            )),
            fix: None,
        });
    }
    out
}

/// JSS-BIBTEX-005 — no duplicate field keys within a single entry.
/// Fires from `Library::duplicate_field_keys`.
pub fn check_bibtex_005(file: &str, library: &Library) -> Vec<Violation> {
    library
        .duplicate_field_keys
        .iter()
        .map(|b| {
            let dup_fields = b.duplicate_keys.join(", ");
            let where_ = if b.entry.key.is_empty() {
                "this entry".to_string()
            } else {
                format!("entry {}", py_repr(&b.entry.key))
            };
            let fields_msg = if dup_fields.is_empty() {
                " a field".to_string()
            } else {
                format!(" field(s) {dup_fields}")
            };
            entry_violation(
                file,
                &b.entry,
                "JSS-BIBTEX-005",
                Some(format!(
                    "Remove the duplicate{fields_msg} in {where_}; BibTeX keeps only the first occurrence and silently drops the rest."
                )),
            )
        })
        .collect()
}
