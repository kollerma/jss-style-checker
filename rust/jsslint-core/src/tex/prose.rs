//! Prose-context classification — ports `_helpers.py`'s
//! `_walk_with_context` / `_is_in_prose_context` and the curated
//! environment/macro sets from `api.py` + `_helpers.py` verbatim. This
//! is the layer ~75% of the rule catalogue (the `tex_files` rules) sits
//! on, so fidelity here matters more than almost anywhere else in the
//! port — see the plan's "hard part" callout.

use super::node::{GroupDelims, Node};

// --- api.py: VERBATIM_ENVS family -----------------------------------

/// Sweave/knitr/jss.cls code-display environments. CODE-* and WIDTH-*
/// rules lint the *content* of these. Mirrors `api.py::CODE_DISPLAY_ENVS`.
pub const CODE_DISPLAY_ENVS: &[&str] = &[
    "verbatim",
    "Verbatim",
    "Code",
    "CodeInput",
    "CodeOutput",
    "Sinput",
    "Soutput",
    "Scode",
    "Schunk",
    "CodeChunk",
];

/// Authored-code (input) subset of `CODE_DISPLAY_ENVS` — excludes the
/// two *output*-only envs. Mirrors `api.py::CODE_INPUT_ENVS`.
pub const CODE_INPUT_ENVS: &[&str] = &[
    "verbatim",
    "Verbatim",
    "Code",
    "CodeInput",
    "Sinput",
    "Scode",
    "Schunk",
    "CodeChunk",
];

/// Other literal-body environments: not prose, but not JSS
/// code-display either. Mirrors `api.py::LISTING_ENVS`.
pub const LISTING_ENVS: &[&str] = &["lstlisting", "alltt", "tabbing", "verbatim*"];

/// Every environment whose body is non-prose. Mirrors
/// `api.py::VERBATIM_ENVS` (= `CODE_DISPLAY_ENVS | LISTING_ENVS`).
pub const VERBATIM_ENVS: &[&str] = &[
    "verbatim",
    "Verbatim",
    "Code",
    "CodeInput",
    "CodeOutput",
    "Sinput",
    "Soutput",
    "Scode",
    "Schunk",
    "CodeChunk",
    "lstlisting",
    "alltt",
    "tabbing",
    "verbatim*",
];

// --- _helpers.py curated sets ----------------------------------------

/// Mirrors `_helpers.py::_VERBATIM_MACROS`.
pub const VERBATIM_MACROS: &[&str] = &["verb", "code"];

/// Mirrors `_helpers.py::_MATH_ENVS`.
pub const MATH_ENVS: &[&str] = &[
    "equation",
    "equation*",
    "align",
    "align*",
    "eqnarray",
    "eqnarray*",
    "gather",
    "gather*",
    "multline",
    "multline*",
];

/// Section macros whose argument is a displayed title, not prose.
/// Mirrors `_helpers.py::_SECTION_MACROS`.
pub const SECTION_MACROS: &[&str] = &[
    "section",
    "section*",
    "subsection",
    "subsection*",
    "subsubsection",
    "subsubsection*",
    "chapter",
    "chapter*",
    "paragraph",
    "subparagraph",
];

/// Macros whose text arg is already JSS-wrapped markup. Mirrors
/// `_helpers.py::_MARKUP_MACROS`.
pub const MARKUP_MACROS: &[&str] = &[
    "pkg",
    "proglang",
    "code",
    "verb",
    "url",
    "email",
    "fct",
    "Rcmd",
    "Rpackage",
    "Rclass",
    "Rfun",
    "Rfunction",
    "Rargument",
    "Rstring",
    "Robject",
    "script",
    "Com",
    "Comt",
    "hlstd",
    "hlkwa",
    "hlopt",
    "hlkwd",
    "hlstr",
    "hlcom",
    "hlnum",
    "hlsng",
    "hlslc",
    "hlppc",
    "hlpps",
];

/// Preamble/meta-data/citation macros whose arg is not prose to scan.
/// Mirrors `_helpers.py::_META_MACROS`. Note `Abstract` is deliberately
/// absent — same rationale as the Python source.
pub const META_MACROS: &[&str] = &[
    "title",
    "Plaintitle",
    "Shorttitle",
    "author",
    "Plainauthor",
    "Keywords",
    "Plainkeywords",
    "Address",
    "documentclass",
    "usepackage",
    "include",
    "input",
    "label",
    "ref",
    "pageref",
    "bibliographystyle",
    "bibliography",
    "SweaveOpts",
    "SweaveInput",
    "SweaveSyntax",
    "VignetteIndexEntry",
    "VignettePackage",
    "VignetteDepends",
    "VignetteEngine",
    "VignetteKeywords",
    "VignetteEncoding",
    "newcommand",
    "renewcommand",
    "providecommand",
    "def",
    "lstinputlisting",
    "lstset",
    "inputminted",
    "VerbatimInput",
    "includegraphics",
    "includepdf",
    "graphicspath",
];

/// True if any ancestor is a verbatim-class environment or macro.
/// Mirrors `_helpers.py::_is_inside_verbatim`.
pub fn is_inside_verbatim(ancestors: &[&Node]) -> bool {
    ancestors.iter().any(|anc| match anc {
        Node::Environment(e) => VERBATIM_ENVS.contains(&e.environmentname.as_str()),
        Node::Macro(m) => VERBATIM_MACROS.contains(&m.macroname.as_str()),
        _ => false,
    })
}

/// True if any ancestor is a math environment or inline/display math
/// node. Mirrors `_helpers.py::_is_inside_math`.
pub fn is_inside_math(ancestors: &[&Node]) -> bool {
    ancestors.iter().any(|anc| match anc {
        Node::Math(_) => true,
        Node::Environment(e) => MATH_ENVS.contains(&e.environmentname.as_str()),
        _ => false,
    })
}

/// Cite-family macros whose MANDATORY `{key}` argument is a BibTeX key,
/// not prose — but whose OPTIONAL `[prefix]`/`[postfix]` arguments
/// (e.g. `\citep[R package by][]{key}`) ARE prose and stay linted.
/// Deliberately not in `META_MACROS` for that reason. Mirrors
/// `_helpers.py::_CITE_MACROS_FOR_SCOPE`.
pub const CITE_MACROS_FOR_SCOPE: &[&str] = &[
    "cite",
    "Cite",
    "citet",
    "Citet",
    "citep",
    "Citep",
    "citealp",
    "Citealp",
    "citealt",
    "Citealt",
    "citeauthor",
    "Citeauthor",
    "citeyear",
    "citeyearpar",
    "nocite",
];

/// True when a char node at this position is prose — not inside JSS
/// markup wrappers, math mode, verbatim envs, section titles, preamble
/// meta-data macros, or a cite-family macro's mandatory bib-key
/// argument. Mirrors `_helpers.py::_is_in_prose_context`.
pub fn is_in_prose_context(ancestors: &[&Node]) -> bool {
    if is_inside_verbatim(ancestors) {
        return false;
    }
    if is_inside_math(ancestors) {
        return false;
    }
    // Delimiters of the nearest enclosing group (ancestors are
    // outermost-first, so the LAST group found is innermost) — used to
    // tell a citation's mandatory `{key}` arg from its optional
    // `[prefix]`/`[postfix]` arg.
    let mut nearest_group_delims: Option<GroupDelims> = None;
    for anc in ancestors {
        if let Node::Group(g) = anc {
            nearest_group_delims = Some(g.delims);
        }
    }
    for anc in ancestors {
        if let Node::Macro(m) = anc {
            let name = m.macroname.as_str();
            if MARKUP_MACROS.contains(&name)
                || SECTION_MACROS.contains(&name)
                || META_MACROS.contains(&name)
            {
                return false;
            }
            if CITE_MACROS_FOR_SCOPE.contains(&name)
                && nearest_group_delims == Some(GroupDelims::Brace)
            {
                return false;
            }
        }
    }
    true
}

/// A walk position: `Some` for a real node, `None` for an absent
/// optional-argument slot — mirrors pylatexenc's `argnlist` entries,
/// which can be `None`. Definite child lists (group/environment/math
/// `nodelist`s) never contain a `None` slot.
pub type Slot<'a> = Option<&'a Node>;

pub(crate) fn children_slots<'a>(node: &'a Node) -> Vec<Slot<'a>> {
    match node {
        Node::Macro(m) => m.args.iter().map(|a| a.as_ref()).collect(),
        Node::Group(g) => g.nodelist.iter().map(Some).collect(),
        Node::Environment(e) => e.nodelist.iter().map(Some).collect(),
        Node::Math(m) => m.nodelist.iter().map(Some).collect(),
        Node::Chars(_) | Node::Comment(_) | Node::Specials(_) => Vec::new(),
    }
}

/// Pre-order walk yielding `(node, ancestors)` to `visit`, outermost
/// ancestor first. Mirrors `_helpers.py::_walk_with_context`, including
/// its unknown-macro sibling-argument rule: when a `Group` node
/// immediately follows a `Macro` node as a SIBLING in the same
/// sequence (not as that macro's own parsed argument — e.g. `\pkg`
/// followed by `{ggplot2}`, since `\pkg` is unknown to the tokenizer
/// and so takes no arguments of its own), that macro is pushed onto
/// the ancestor stack before recursing into the group.
pub fn walk_with_context<'a>(
    seq: &[Slot<'a>],
    ancestors: &mut Vec<&'a Node>,
    visit: &mut dyn FnMut(&'a Node, &[&'a Node]),
) {
    for (i, &slot) in seq.iter().enumerate() {
        let Some(node) = slot else { continue };
        visit(node, ancestors);

        let children = children_slots(node);
        let extra: Slot<'a> = if matches!(node, Node::Group(_)) && i > 0 {
            match seq[i - 1] {
                Some(prev @ Node::Macro(_)) => Some(prev),
                _ => None,
            }
        } else {
            None
        };

        if children.is_empty() {
            continue;
        }
        if let Some(e) = extra {
            ancestors.push(e);
        }
        ancestors.push(node);
        walk_with_context(&children, ancestors, visit);
        ancestors.pop();
        if extra.is_some() {
            ancestors.pop();
        }
    }
}

/// Convenience entry point over a top-level node list (no absent
/// slots — every entry is `Some`).
pub fn walk<'a>(nodes: &'a [Node], visit: &mut dyn FnMut(&'a Node, &[&'a Node])) {
    let top: Vec<Slot<'a>> = nodes.iter().map(Some).collect();
    let mut ancestors: Vec<&'a Node> = Vec::new();
    walk_with_context(&top, &mut ancestors, visit);
}
