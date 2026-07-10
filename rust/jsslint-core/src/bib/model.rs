//! BibTeX data model — mirrors the subset of `bibtexparser` v2's model
//! this codebase's rules consume (`Library.entries`, `Library.failed_blocks`,
//! `Entry.key`/`.entry_type`/`.start_line`/`.fields_dict`,
//! `Field.value`, `DuplicateBlockKeyBlock`, `DuplicateFieldKeyBlock`).
//!
//! Positions are Unicode codepoint offsets (see `tex::node`'s doc
//! comment on the same point) and `start_line` is 0-based, matching
//! `bibtexparser` exactly — `_helpers.py::entry_line` adds 1 at the
//! call site, not here.

use std::collections::HashMap;

#[derive(Debug, Clone)]
pub struct Field {
    /// Original-case field name as written in the source (`fields_dict`
    /// keys preserve source casing — `_lc_fields` in `_helpers.py`
    /// lowercases them itself, not `bibtexparser`).
    pub key: String,
    /// Cleaned value: surrounding `{}`/`""` stripped, `@string` macro
    /// references resolved, `#`-concatenated parts joined.
    pub value: String,
}

#[derive(Debug, Clone)]
pub struct Entry {
    pub key: String,
    /// Already lowercased at parse time — mirrors `bibtexparser`,
    /// which normalizes `entry.entry_type` regardless of source
    /// casing (`@TECHREPORT{...}` still reports `entry_type ==
    /// "techreport"`; verified empirically, not documented anywhere
    /// obvious). A few call sites still call `.to_lowercase()` on
    /// this defensively — harmless no-ops now, kept rather than
    /// touched, not evidence this field is ever non-lowercase.
    pub entry_type: String,
    /// 0-based line index of the entry's `@type{` opening.
    pub start_line: u32,
    pub fields: Vec<Field>,
}

impl Entry {
    /// Case-insensitive field lookup. Mirrors
    /// `_helpers.py::_lc_fields(entry).get(name.lower())`.
    pub fn field(&self, name: &str) -> Option<&Field> {
        self.fields
            .iter()
            .find(|f| f.key.eq_ignore_ascii_case(name))
    }
}

/// A duplicate-citation-key block: a second (or later) `@entry{key,...}`
/// using a key already claimed by an earlier entry in the same file.
/// Mirrors `bibtexparser`'s `DuplicateBlockKeyBlock`.
#[derive(Debug, Clone)]
pub struct DuplicateBlockKey {
    pub key: String,
    pub start_line: u32,
    /// The duplicate's own (recovered) entry — used by BIBTEX-002 to
    /// report a location.
    pub entry: Entry,
}

/// An entry that had a field key repeated within itself (last value
/// wins in the recovered `entry`, matching `bibtexparser`). Mirrors
/// `DuplicateFieldKeyBlock`.
#[derive(Debug, Clone)]
pub struct DuplicateFieldKey {
    pub start_line: u32,
    pub duplicate_keys: Vec<String>,
    pub entry: Entry,
}

#[derive(Debug, Clone, Default)]
pub struct Library {
    pub entries: Vec<Entry>,
    pub duplicate_block_keys: Vec<DuplicateBlockKey>,
    pub duplicate_field_keys: Vec<DuplicateFieldKey>,
}

/// `@string{name = value}` macro table, used only during parsing to
/// resolve bare-token field values (e.g. `journal = jsstat`).
pub(crate) type StringTable = HashMap<String, String>;
