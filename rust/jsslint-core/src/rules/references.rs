//! References rules — mirrors `journals/jss/rules/references.py`'s
//! bib-facing rules (JSS-REFS-001/003/004/005/006/007).
//!
//! Not yet ported — tracked as the remaining Phase 2 slice. The 7
//! rules landed so far (BIBTEX-001..005, NAME-002, HOUSE-002) are
//! purely structural/lookup-table checks; these six lean on text
//! heuristics (title-case detection, journal-abbreviation signals,
//! markup-wrapping checks) that need more careful porting.
