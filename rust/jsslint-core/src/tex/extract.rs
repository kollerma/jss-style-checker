//! Macro-argument text extraction — ports `_helpers.py`'s
//! `_iter_with_parent` / `_next_group_arg` / `_macro_args_text` /
//! `_group_text` verbatim, including a latent imprecision worth
//! flagging rather than "fixing": `_macro_args_text`'s known-macro
//! path takes the FIRST non-absent `Group` in `args` regardless of
//! whether it's a `{` or `[` slot. For `\citep[e.g.][]{key}` (argspec
//! `*[[{`), that's the OPTIONAL prenote group, not the mandatory
//! `{key}` — so citation-key extraction can pick up prenote text
//! instead of the key when a prenote is present. This is the existing
//! Python behavior (not a Rust-port bug); replicated faithfully for
//! parity, not independently corrected.

use super::node::Node;
use super::prose::{children_slots, Slot};

/// Recursively visits every `(parent_seq, idx, node)` triple in
/// pre-order — mirrors `_helpers.py::_iter_with_parent`. A callback
/// rather than a returned `Vec` because a macro's `args`-derived
/// parent sequence is only ever a temporary (Rust can't hand back a
/// reference into it once the recursive call returns).
pub fn iter_with_parent_visit<'a>(
    nodes: &'a [Node],
    visit: &mut dyn FnMut(&[Slot<'a>], usize, &'a Node),
) {
    let top: Vec<Slot<'a>> = nodes.iter().map(Some).collect();
    visit_seq(&top, visit);
}

fn visit_seq<'a>(seq: &[Slot<'a>], visit: &mut dyn FnMut(&[Slot<'a>], usize, &'a Node)) {
    for (i, &slot) in seq.iter().enumerate() {
        let Some(node) = slot else { continue };
        visit(seq, i, node);
        let children = children_slots(node);
        if !children.is_empty() {
            visit_seq(&children, visit);
        }
    }
}

/// The sibling `Group` right after `parent[idx]`, if any. Mirrors
/// `_helpers.py::_next_group_arg`.
pub fn next_group_arg<'a>(parent: &[Slot<'a>], idx: usize) -> Option<&'a super::node::GroupNode> {
    let next = parent.get(idx + 1).copied().flatten()?;
    match next {
        Node::Group(g) => Some(g),
        _ => None,
    }
}

/// Concatenated text of every direct `Chars` child, trimmed. Mirrors
/// `_helpers.py::_group_text`.
pub fn group_text(group: &super::node::GroupNode) -> String {
    let mut out = String::new();
    for child in &group.nodelist {
        if let Node::Chars(c) = child {
            out.push_str(&c.chars);
        }
    }
    out.trim().to_string()
}

/// Extract a macro's first braced-group argument as plain text — tries
/// `args` first (known macros; see module docs for the first-Group
/// imprecision), falls back to the next sibling `Group` (unknown
/// macros like `\pkg`, `\nocite`, `\shortcites`). `""` if neither
/// yields a group. Mirrors `_helpers.py::_macro_args_text`.
pub fn macro_args_text<'a>(
    macro_node: &super::node::MacroNode,
    parent: &[Slot<'a>],
    idx: usize,
) -> String {
    for arg in &macro_node.args {
        if let Some(Node::Group(g)) = arg {
            return group_text(g);
        }
    }
    if let Some(sibling) = next_group_arg(parent, idx) {
        return group_text(sibling);
    }
    String::new()
}
