//! Tolerant LaTeX parsing substrate — spec 018 Phase 1. Ports
//! `pylatexenc.latexwalker`'s node model (`node.rs`, `parser.rs`),
//! `core/parser.py`'s pre-tokenization neutralization
//! (`neutralize.rs`), `pos_to_lineno_colno` (`position.rs`), and
//! `_helpers.py`'s prose-context classifier (`prose.rs`).
//!
//! No rules live here yet (Phase 3) — this module's job is only to
//! prove the substrate matches, validated by `tests/parser_parity.rs`
//! against a Python oracle dump (`tools/dump_tex_nodes.py`).

pub mod debug;
pub mod extract;
pub mod neutralize;
pub mod node;
pub mod parser;
pub mod position;
pub mod prose;
mod specs;

pub use node::*;
pub use position::LineIndex;

/// Full `.tex` parse pipeline, mirroring
/// `core/parser.py::parse_tex_source`'s preprocessing + tokenize order
/// (tolerant-parsing path only — see `parser::parse`'s doc comment).
pub struct ParsedTex {
    pub source: String,
    pub chars: Vec<char>,
    pub nodes: Vec<Node>,
    /// Zero for a normal `.tex`/`.rnw` file. Non-zero for a `.Rmd`
    /// raw-LaTeX prose fragment (see `crate::rmd`): `chars`/`node.pos`
    /// stay 0-based within the fragment's own (unpadded) text — same
    /// as Python's `node.pos`, which `_OffsetWalker` never touches —
    /// while every rule module's `LineIndex::with_offset(&parsed.chars,
    /// parsed.line_offset)` call adds this back in so reported lines
    /// stay source-accurate on the original `.Rmd`.
    pub line_offset: u32,
}

pub fn parse_tex_source(source: &str) -> ParsedTex {
    let preprocessed = neutralize::preprocess(source);
    let (nodes, chars) = parser::parse(&preprocessed);
    ParsedTex {
        source: preprocessed,
        chars,
        nodes,
        line_offset: 0,
    }
}
