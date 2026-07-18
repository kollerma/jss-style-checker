//! Citations rules — mirrors `journals/jss/rules/citations.py`
//! (JSS-CITE-002/003/004).

use super::py_repr;
use super::tex_common::{tex_violation, tex_violation_with_fix};
use crate::report::{Fix, FixConfidence, Violation};
use crate::terms::TERMS;
use crate::tex::extract;
use crate::tex::node::Node;
use crate::tex::position::LineIndex;
use crate::tex::prose::{children_slots, is_inside_verbatim, walk, walk_with_context, Slot};
use crate::tex::ParsedTex;
use regex::Regex;
use std::collections::{HashMap, HashSet};
use std::sync::LazyLock;

const CITE_MACROS: &[&str] = &[
    "cite",
    "citet",
    "citep",
    "citealp",
    "citealt",
    "citeauthor",
    "citeyear",
];

const BIB_ENVS: &[&str] = &["thebibliography"];

const NO_CITE_MACROS: &[&str] = &[
    "title",
    "Title",
    "Plaintitle",
    "Shorttitle",
    "Keywords",
    "Plainkeywords",
    "section",
    "subsection",
    "subsubsection",
    "paragraph",
    "subparagraph",
];
const NO_CITE_ENVS: &[&str] = &[];

const SOFT_NO_CITE_MACROS_FULL: &[&str] = &["Abstract", "Plainabstract", "bibitem"];
const SOFT_NO_CITE_ENVS: &[&str] = &["abstract", "thebibliography"];

const BASE_R_PACKAGES: &[&str] = &[
    "base",
    "compiler",
    "datasets",
    "graphics",
    "grDevices",
    "grid",
    "methods",
    "parallel",
    "splines",
    "stats",
    "stats4",
    "tcltk",
    "tools",
    "utils",
];

const DEFINITION_MACROS: &[&str] = &[
    "newcommand",
    "renewcommand",
    "providecommand",
    "def",
    "edef",
    "newcommand*",
    "renewcommand*",
    "providecommand*",
];

static RMD_BRACKET_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"\[\s*@[A-Za-z][\w:.\-]*").unwrap());
static RMD_BARE_AT_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"@[A-Za-z][\w:.\-]*").unwrap());

/// Mirrors `citations.py::_RMD_AT_CITATION`'s
/// `r"\[\s*@[A-Za-z][\w:.\-]*|(?<![A-Za-z])@[A-Za-z][\w:.\-]*"` — the
/// negative lookbehind on the second alternative has no `regex`-crate
/// equivalent, so it's a manual preceding-char check instead.
fn rmd_citation_present(text: &str) -> bool {
    if RMD_BRACKET_RE.is_match(text) {
        return true;
    }
    RMD_BARE_AT_RE.find_iter(text).any(|m| {
        !text[..m.start()]
            .chars()
            .next_back()
            .is_some_and(|c| c.is_ascii_alphabetic())
    })
}

const TABULAR_ENVS: &[&str] = &[
    "tabular",
    "tabular*",
    "tabularx",
    "tabbing",
    "longtable",
    "supertabular",
];
const ROW_SEP_MACROS: &[&str] = &[
    "\\",
    "tabularnewline",
    "hline",
    "midrule",
    "toprule",
    "bottomrule",
    "cmidrule",
];

static BLANK_LINE_RE: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"\n\s*\n").unwrap());

static TEXTUAL_AUTHOR_YEAR_RE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(
        r"\b[A-Z][A-Za-z'À-ſ]{2,}(?:\s+(?:and|&)\s+[A-Z][A-Za-z'À-ſ]{2,}|\s+et\s+al\.?)?\s*\((?:18|19|20)\d{2}\b",
    )
    .unwrap()
});

const URL_MACROS: &[&str] = &["url", "href"];
static BARE_URL_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"(?i)(?:https?://|www\.)\S").unwrap());
const URL_SENTINEL: &str = "\u{0}url\u{0}";
static SENTENCE_BREAK_RE: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"\.\s").unwrap());
const URL_ADJACENCY_CHARS: usize = 60;

const INLINE_WRAPPERS: &[&str] = &[
    "href",
    "url",
    "mbox",
    "fbox",
    "emph",
    "textbf",
    "textit",
    "texttt",
    "textsf",
    "textsc",
    "textnormal",
    "textrm",
    "text",
    "uline",
    "underline",
];

fn is_inside_no_cite_zone(ancestors: &[&Node]) -> bool {
    ancestors.iter().any(|anc| match anc {
        Node::Macro(m) => NO_CITE_MACROS.contains(&m.macroname.as_str()),
        Node::Environment(e) => NO_CITE_ENVS.contains(&e.environmentname.as_str()),
        _ => false,
    })
}

fn is_inside_soft_no_cite_zone(ancestors: &[&Node]) -> bool {
    ancestors.iter().any(|anc| match anc {
        Node::Macro(m) => SOFT_NO_CITE_MACROS_FULL.contains(&m.macroname.as_str()),
        Node::Environment(e) => SOFT_NO_CITE_ENVS.contains(&e.environmentname.as_str()),
        _ => false,
    })
}

fn is_inside_definition(ancestors: &[&Node]) -> bool {
    ancestors.iter().any(
        |anc| matches!(anc, Node::Macro(m) if DEFINITION_MACROS.contains(&m.macroname.as_str())),
    )
}

fn is_cite_ancestor(ancestors: &[&Node]) -> bool {
    ancestors
        .iter()
        .any(|anc| matches!(anc, Node::Macro(m) if CITE_MACROS.contains(&m.macroname.as_str())))
}

fn is_in_tabular(ancestors: &[&Node]) -> bool {
    ancestors.iter().any(
        |anc| matches!(anc, Node::Environment(e) if TABULAR_ENVS.contains(&e.environmentname.as_str())),
    )
}

fn char_has_blank_line(node: Slot) -> bool {
    matches!(node, Some(Node::Chars(c)) if BLANK_LINE_RE.is_match(&c.chars))
}

fn is_row_sep(node: Slot) -> bool {
    matches!(node, Some(Node::Macro(m)) if ROW_SEP_MACROS.contains(&m.macroname.as_str()))
}

/// `(start_idx, end_idx)` inclusive-exclusive for the paragraph within
/// `parent` that contains `parent[idx]`. Mirrors
/// `citations.py::_paragraph_span_in_parent`.
fn paragraph_span_in_parent(parent: &[Slot], idx: usize, in_tabular: bool) -> (usize, usize) {
    let mut start = 0;
    for i in (0..idx).rev() {
        let sib = parent[i];
        if char_has_blank_line(sib) {
            start = i + 1;
            break;
        }
        if in_tabular && is_row_sep(sib) {
            start = i + 1;
            break;
        }
    }
    let mut end = parent.len();
    for (i, &sib) in parent.iter().enumerate().skip(idx + 1) {
        if char_has_blank_line(sib) {
            end = i;
            break;
        }
        if in_tabular && is_row_sep(sib) {
            end = i;
            break;
        }
    }
    (start, end)
}

/// True if any cite macro lives in the paragraph span, recursively
/// (cites wrapped in `\emph{...}` etc. count). Mirrors
/// `citations.py::_has_cite_in_span`.
fn has_cite_in_span(parent: &[Slot], start: usize, end: usize) -> bool {
    let mut found = false;
    let mut ancestors = Vec::new();
    walk_with_context(
        &parent[start..end],
        &mut ancestors,
        &mut |node, _anc, _seq, _idx| {
            if let Node::Macro(m) = node {
                if CITE_MACROS.contains(&m.macroname.as_str()) {
                    found = true;
                }
            }
        },
    );
    found
}

fn has_rmd_citation_in_span(parent: &[Slot], start: usize, end: usize) -> bool {
    parent[start..end]
        .iter()
        .flatten()
        .any(|sib| matches!(sib, Node::Chars(c) if rmd_citation_present(&c.chars)))
}

fn has_textual_citation_in_span(parent: &[Slot], start: usize, end: usize) -> bool {
    parent[start..end]
        .iter()
        .flatten()
        .any(|sib| matches!(sib, Node::Chars(c) if TEXTUAL_AUTHOR_YEAR_RE.is_match(&c.chars)))
}

/// True if a `\url`/`\href` or bare URL sits directly after the `\pkg`
/// at `parent[idx]` — same sentence, within a few tens of characters.
/// Mirrors `citations.py::_url_references_pkg`.
fn url_references_pkg(parent: &[Slot], idx: usize, end: usize) -> bool {
    let mut following = String::new();
    for sib in parent[(idx + 1)..end].iter().flatten() {
        match sib {
            Node::Macro(m) if URL_MACROS.contains(&m.macroname.as_str()) => {
                following.push(' ');
                following.push_str(URL_SENTINEL);
                following.push(' ');
            }
            Node::Chars(c) => following.push_str(&c.chars),
            _ => following.push(' '),
        }
        if following.chars().count() > 2 * URL_ADJACENCY_CHARS {
            break;
        }
    }
    let scope_full = match SENTENCE_BREAK_RE.find(&following) {
        Some(m) => &following[..m.start()],
        None => following.as_str(),
    };
    let scope: String = scope_full.chars().take(URL_ADJACENCY_CHARS).collect();
    scope.contains(URL_SENTINEL) || BARE_URL_RE.is_match(&scope)
}

/// True when a `\pkg{X}` nested inside an inline wrapper has a
/// citation in the paragraph that surrounds the wrapper. Mirrors
/// `citations.py::_cited_in_wrapper_paragraph`.
fn cited_in_wrapper_paragraph(
    ancestors: &[&Node],
    pos_map: &HashMap<*const Node, (Vec<Slot>, usize)>,
    in_tab: bool,
) -> bool {
    if in_tab {
        return false;
    }
    for anc in ancestors {
        let is_wrapper = match anc {
            Node::Group(_) => true,
            Node::Macro(m) => INLINE_WRAPPERS.contains(&m.macroname.as_str()),
            _ => false,
        };
        if !is_wrapper {
            continue;
        }
        let key = *anc as *const Node;
        let Some((wp, wi)) = pos_map.get(&key) else {
            continue;
        };
        let (ws, we) = paragraph_span_in_parent(wp, *wi, in_tab);
        if has_cite_in_span(wp, ws, we)
            || has_rmd_citation_in_span(wp, ws, we)
            || has_textual_citation_in_span(wp, ws, we)
        {
            return true;
        }
    }
    false
}

/// `seen` spans the entire document, NOT each tex-like fragment — in
/// `.Rmd` input, each prose block becomes its own fragment, and a
/// per-fragment `seen` would re-ask for a citation on every prose
/// block that mentions `\pkg{X}`, even when `X` was already cited
/// earlier in the document. Mirrors `citations.py::check_jss_cite_002`'s
/// own `seen` comment verbatim. `check_cite_002` (the public entry
/// point) threads one `seen` across every fragment in document order.
fn check_cite_002_fragment(
    file: &str,
    parsed: &ParsedTex,
    seen: &mut HashSet<String>,
) -> Vec<Violation> {
    let line_index = LineIndex::with_offset(&parsed.chars, parsed.line_offset);
    let mut out = Vec::new();
    let top: Vec<Slot> = parsed.nodes.iter().map(Some).collect();

    // Position map (node ptr -> its parent seq + index) so a \pkg
    // nested inside an inline wrapper can locate that wrapper's own
    // paragraph span. Mirrors citations.py's `pos_map` built from a
    // separate full walk before the main pass.
    let mut pos_map: HashMap<*const Node, (Vec<Slot>, usize)> = HashMap::new();
    {
        let mut ancestors: Vec<&Node> = Vec::new();
        walk_with_context(&top, &mut ancestors, &mut |node, _anc, parent, idx| {
            pos_map.insert(node as *const Node, (parent.to_vec(), idx));
        });
    }

    let mut ancestors: Vec<&Node> = Vec::new();
    walk_with_context(&top, &mut ancestors, &mut |node, ancestors, parent, idx| {
        let Node::Macro(m) = node else { return };
        if m.macroname != "pkg" {
            return;
        }
        let name = extract::macro_args_text(m, parent, idx);
        if name.is_empty() {
            return;
        }
        if TERMS.languages.contains(name.as_str()) {
            return;
        }
        if BASE_R_PACKAGES.contains(&name.as_str()) {
            seen.insert(name);
            return;
        }
        if is_inside_no_cite_zone(ancestors) {
            return;
        }
        if is_inside_definition(ancestors) {
            return;
        }
        let in_tab = is_in_tabular(ancestors);
        if is_inside_soft_no_cite_zone(ancestors) {
            let (start, end) = paragraph_span_in_parent(parent, idx, in_tab);
            if has_cite_in_span(parent, start, end) || is_cite_ancestor(ancestors) {
                seen.insert(name);
            }
            return;
        }
        if seen.contains(&name) {
            return;
        }
        seen.insert(name.clone());
        if is_cite_ancestor(ancestors) {
            return;
        }
        let (start, end) = paragraph_span_in_parent(parent, idx, in_tab);
        if has_cite_in_span(parent, start, end) {
            return;
        }
        if url_references_pkg(parent, idx, end) {
            return;
        }
        if has_rmd_citation_in_span(parent, start, end) {
            return;
        }
        if has_textual_citation_in_span(parent, start, end) {
            return;
        }
        if cited_in_wrapper_paragraph(ancestors, &pos_map, in_tab) {
            return;
        }
        out.push(tex_violation(
            file,
            &line_index,
            m.span.pos,
            "JSS-CITE-002",
            Some(format!(
                "Add a citation for \\pkg{{{name}}} (e.g., \\citep{{…}}) within this paragraph."
            )),
        ));
    });
    out
}

/// JSS-CITE-002 — first `\pkg{X}` mention per distinct X needs a
/// citation in the same paragraph. Mirrors `citations.py::check_jss_cite_002`
/// threading one `seen` set across every tex-like fragment in the
/// document — see `check_cite_002_fragment`'s doc comment.
pub fn check_cite_002(fragments: &[(&str, &ParsedTex)]) -> Vec<Violation> {
    let mut seen: HashSet<String> = HashSet::new();
    let mut out = Vec::new();
    for (file, parsed) in fragments {
        out.extend(check_cite_002_fragment(file, parsed, &mut seen));
    }
    out
}

// ---------------------------------------------------------------------
// JSS-CITE-003 — (\cite{...}) bracket-in-bracket.
// ---------------------------------------------------------------------

const TRIGGERING_CITE_MACROS: &[&str] = &["cite", "citep", "citet", "citeauthor"];

static KEY_MATCH_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"^\\[a-zA-Z]+\s*(?:\[[^\]]*\])?\s*\{([^}]*)\}").unwrap());

/// Scan `source[:pos]` backwards for an unmatched `(` in the same
/// paragraph. Mirrors `citations.py::_find_enclosing_open_paren`.
fn find_enclosing_open_paren(source: &[char], pos: usize) -> Option<usize> {
    let mut depth: i32 = 0;
    for i in (0..pos).rev() {
        match source[i] {
            ')' => depth += 1,
            '(' => {
                if depth == 0 {
                    return Some(i);
                }
                depth -= 1;
            }
            '\n' => {
                let mut j = i;
                while j > 0 && matches!(source[j - 1], ' ' | '\t' | '\r') {
                    j -= 1;
                }
                if j > 0 && source[j - 1] == '\n' {
                    return None;
                }
            }
            _ => {}
        }
    }
    None
}

/// Scan `source[pos:]` forwards for the matching `)` in the same
/// paragraph. Mirrors `citations.py::_find_matching_close_paren`.
fn find_matching_close_paren(source: &[char], pos: usize) -> Option<usize> {
    let mut depth: i32 = 0;
    let mut i = pos;
    while i < source.len() {
        match source[i] {
            '(' => depth += 1,
            ')' => {
                if depth == 0 {
                    return Some(i);
                }
                depth -= 1;
            }
            '\n' => {
                let mut j = i + 1;
                while j < source.len() && matches!(source[j], ' ' | '\t' | '\r') {
                    j += 1;
                }
                if j < source.len() && source[j] == '\n' {
                    return None;
                }
            }
            _ => {}
        }
        i += 1;
    }
    None
}

/// JSS-CITE-003 — no bracket-in-bracket citation forms like
/// `(\cite{...})` — use `\citep{...}` instead.
pub fn check_cite_003(file: &str, parsed: &ParsedTex) -> Vec<Violation> {
    let line_index = LineIndex::with_offset(&parsed.chars, parsed.line_offset);
    let mut out = Vec::new();
    let mut emitted: HashSet<usize> = HashSet::new();
    extract::iter_with_parent_visit(&parsed.nodes, &mut |_parent, _idx, node| {
        let Node::Macro(m) = node else { return };
        if !TRIGGERING_CITE_MACROS.contains(&m.macroname.as_str()) {
            return;
        }
        if emitted.contains(&m.span.pos) {
            return;
        }
        let Some(open_paren) = find_enclosing_open_paren(&parsed.chars, m.span.pos) else {
            return;
        };
        let macro_end = m.span.pos + m.span.len;
        let Some(close_paren) = find_matching_close_paren(&parsed.chars, macro_end) else {
            return;
        };
        let tail: String = parsed.chars[m.span.pos..].iter().collect();
        if let Some(caps) = KEY_MATCH_RE.captures(&tail) {
            if caps.get(1).unwrap().as_str().contains('#') {
                return;
            }
        }
        if m.macroname == "citeauthor" {
            let paren_text: String = parsed.chars[open_paren..=close_paren].iter().collect();
            if !paren_text.contains("\\citeyear") {
                return;
            }
        }
        emitted.insert(m.span.pos);
        let mut fix = None;
        if m.macroname == "cite" {
            let before: String = parsed.chars[(open_paren + 1)..m.span.pos].iter().collect();
            let after: String = parsed.chars[macro_end..close_paren].iter().collect();
            if before.trim().is_empty() && after.trim().is_empty() {
                let macro_body: String = parsed.chars[m.span.pos..macro_end].iter().collect();
                let replacement = format!("\\citep{}", &macro_body["\\cite".len()..]);
                fix = Some(Fix {
                    start: open_paren,
                    end: close_paren + 1,
                    replacement,
                    description: "Replace (\\cite{...}) with \\citep{...}.".to_string(),
                    confidence: FixConfidence::Safe,
                });
            }
        }
        out.push(tex_violation_with_fix(
            file,
            &line_index,
            m.span.pos,
            "JSS-CITE-003",
            Some(
                "Citation inside parens: replace (\\cite{...}) with \\citep{...}, or use \\citealp{...} when additional text shares the parens."
                    .to_string(),
            ),
            fix,
        ));
    });
    out
}

// ---------------------------------------------------------------------
// JSS-CITE-004 — hardcoded (Author, YYYY) references.
// ---------------------------------------------------------------------

static HARDCODED_CITE_RE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(
        r"\(\s*(?P<surname>[A-Z][A-Za-z.'\-]+)(?:\s+(?:et\s+al\.?|and\s+[A-Z][A-Za-z.'\-]+))?,\s*(?:19|20)\d{2}[a-z]?\s*\)",
    )
    .unwrap()
});

const NON_AUTHOR_TOKENS: &[&str] = &[
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Sept",
    "Oct",
    "Nov",
    "Dec",
];

const MASK_MACROS: &[&str] = &["code", "url", "verb"];

/// Ancestors (outermost first) whose descendant is `target` (identity
/// comparison). Handles the `\code`/`\url`/`\verb`-sibling-Group
/// unknown-macro rule specifically (narrower than the generic
/// `walk_with_context` sibling rule, which applies to any preceding
/// macro — irrelevant here since `_is_masked` only inspects
/// `MASK_MACROS` membership either way, but ported as its own
/// function rather than relying on that equivalence). Mirrors
/// `citations.py::_collect_ancestors`.
fn collect_ancestors<'a>(nodes: &'a [Node], target: &'a Node) -> Vec<&'a Node> {
    let top: Vec<Slot<'a>> = nodes.iter().map(Some).collect();
    let target_ptr = target as *const Node;
    let mut path = Vec::new();
    collect_ancestors_inner(&top, target_ptr, &mut path);
    path
}

fn collect_ancestors_inner<'a>(
    seq: &[Slot<'a>],
    target: *const Node,
    path: &mut Vec<&'a Node>,
) -> bool {
    for (i, slot) in seq.iter().enumerate() {
        let Some(node) = slot else { continue };
        let node = *node;
        if std::ptr::eq(node, target) {
            return true;
        }
        let children = children_slots(node);
        let mut extra: Option<&'a Node> = None;
        if matches!(node, Node::Group(_)) && i > 0 {
            if let Some(Node::Macro(pm)) = seq[i - 1] {
                if MASK_MACROS.contains(&pm.macroname.as_str()) {
                    extra = seq[i - 1];
                }
            }
        }
        if children.is_empty() {
            continue;
        }
        if let Some(e) = extra {
            path.push(e);
        }
        path.push(node);
        if collect_ancestors_inner(&children, target, path) {
            return true;
        }
        path.pop();
        if extra.is_some() {
            path.pop();
        }
    }
    false
}

fn is_masked(ancestors: &[&Node]) -> bool {
    if is_inside_verbatim(ancestors) {
        return true;
    }
    ancestors.iter().any(|anc| match anc {
        Node::Macro(m) => MASK_MACROS.contains(&m.macroname.as_str()),
        Node::Environment(e) => BIB_ENVS.contains(&e.environmentname.as_str()),
        _ => false,
    })
}

/// JSS-CITE-004 — hardcoded author-year `(Name, YYYY)` references
/// bypass the bibliography; use natbib commands.
pub fn check_cite_004(file: &str, parsed: &ParsedTex) -> Vec<Violation> {
    let line_index = LineIndex::with_offset(&parsed.chars, parsed.line_offset);
    let mut out = Vec::new();
    walk(&parsed.nodes, &mut |node, _walk_ancestors| {
        let Node::Chars(c) = node else { return };
        let matches: Vec<_> = HARDCODED_CITE_RE.captures_iter(&c.chars).collect();
        if matches.is_empty() {
            return;
        }
        let mut ancestors_cache: Option<Vec<&Node>> = None;
        for caps in matches {
            let whole = caps.get(0).unwrap();
            let surname = caps.name("surname").unwrap().as_str();
            if NON_AUTHOR_TOKENS.contains(&surname) {
                continue;
            }
            let ancestors =
                ancestors_cache.get_or_insert_with(|| collect_ancestors(&parsed.nodes, node));
            if is_masked(ancestors) {
                continue;
            }
            let abs_pos = c.span.pos + c.chars[..whole.start()].chars().count();
            out.push(tex_violation(
                file,
                &line_index,
                abs_pos,
                "JSS-CITE-004",
                Some(format!(
                    "Replace the hardcoded reference {} with a natbib command (e.g., \\citet{{Key}}).",
                    py_repr(whole.as_str())
                )),
            ));
        }
    });
    out
}
