//! Debug dump: one line per node, pre-order, in the exact walk order
//! `prose::walk` visits them — the Phase 1 acceptance artifact per the
//! plan ("a debug dump of (node-kind, span, prose?) for every fixture
//! must match a parallel dump from the Python walker"). Format:
//!
//! ```text
//! <depth>\t<pos>\t<end>\t<kind>\t<prose>
//! ```
//!
//! `kind` encodes the node's identifying detail (macro/environment
//! name, group delimiter, math kind) so a mismatch is diagnosable from
//! the dump alone, without needing the original source alongside it.
//! Compared against `tools/dump_tex_nodes.py`'s identical format.

use super::node::{GroupDelims, MathKind, Node};
use super::prose;

fn kind_label(node: &Node) -> String {
    match node {
        Node::Chars(_) => "Chars".to_string(),
        Node::Comment(_) => "Comment".to_string(),
        Node::Macro(m) => format!("Macro:{}", m.macroname),
        Node::Group(g) => match g.delims {
            GroupDelims::Brace => "Group:{".to_string(),
            GroupDelims::Bracket => "Group:[".to_string(),
        },
        Node::Environment(e) => format!("Environment:{}", e.environmentname),
        Node::Math(m) => match m.kind {
            MathKind::Inline => "Math:inline".to_string(),
            MathKind::Display => "Math:display".to_string(),
        },
        Node::Specials(s) => format!("Specials:{}", s.chars),
    }
}

/// Dumps `nodes` in the same pre-order `prose::walk` visits them.
pub fn dump(nodes: &[Node]) -> String {
    let mut out = String::new();
    prose::walk(nodes, &mut |node, ancestors| {
        let depth = ancestors.len();
        let span = node.span();
        let prose = prose::is_in_prose_context(ancestors);
        out.push_str(&format!(
            "{depth}\t{pos}\t{end}\t{kind}\t{prose}\n",
            pos = span.pos,
            end = span.end(),
            kind = kind_label(node),
            prose = prose,
        ));
    });
    out
}
