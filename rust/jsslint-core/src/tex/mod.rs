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
}

pub fn parse_tex_source(source: &str) -> ParsedTex {
    let preprocessed = neutralize::preprocess(source);
    let (nodes, chars) = parser::parse(&preprocessed);
    ParsedTex {
        source: preprocessed,
        chars,
        nodes,
    }
}
