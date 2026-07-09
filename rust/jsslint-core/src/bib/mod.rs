//! BibTeX parsing substrate — spec 018 Phase 2. See `parser.rs`'s
//! module docs for the exact `bibtexparser`-compatibility policy this
//! implements (including the `core/parser.py`-specific duplicate-key /
//! duplicate-field re-insertion behavior, which differs from raw
//! `bibtexparser`).

pub mod debug;
pub mod model;
pub mod parser;

pub use model::{DuplicateBlockKey, DuplicateFieldKey, Entry, Field, Library};
pub use parser::parse;
