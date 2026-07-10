//! Cross-reference rules — mirrors `journals/jss/rules/crossrefs.py`
//! (JSS-XREF-001..007). Position convention: same as `markup.rs` —
//! helpers scoped to one `CharsNode`'s own text use byte offsets as an
//! approximation, but any offset that becomes a `Violation`/`Fix`
//! position is converted to an exact codepoint offset via the usual
//! `c.span.pos + c.chars[..byte_off].chars().count()` idiom before use.

use super::py_repr;
use super::tex_common::{tex_violation, tex_violation_with_fix};
use crate::report::{Fix, FixConfidence, Violation};
use crate::tex::extract;
use crate::tex::node::{EnvironmentNode, MacroNode, Node};
use crate::tex::position::LineIndex;
use crate::tex::prose::{
    is_in_prose_context, walk, walk_with_context, Slot, CITE_MACROS_FOR_SCOPE,
};
use crate::tex::ParsedTex;
use regex::Regex;
use std::collections::HashSet;
use std::sync::LazyLock;

fn floor_char_boundary(s: &str, mut i: usize) -> usize {
    i = i.min(s.len());
    while i > 0 && !s.is_char_boundary(i) {
        i -= 1;
    }
    i
}

/// `parent[idx]` for a possibly-negative/out-of-range `idx`, flattening
/// the `Option` slot. Mirrors the `parent[idx] if 0 <= idx < len(parent)
/// else None` guard pattern used throughout `crossrefs.py`.
fn sibling<'a>(parent: &[Slot<'a>], idx: isize) -> Option<&'a Node> {
    if idx < 0 {
        return None;
    }
    parent.get(idx as usize).copied().flatten()
}

static WS_RUN_RE: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"\s+").unwrap());

fn norm_label_key(raw: &str) -> String {
    WS_RUN_RE.replace_all(raw, " ").trim().to_string()
}

// ---------------------------------------------------------------------
// JSS-XREF-001 — Figure/Table N by number
// ---------------------------------------------------------------------

static FIG_TAB_NUMBER_RE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"\b(?:Figure|Fig\.|Figures|Table|Tab\.|Tables)\s+\d+[a-z]*").unwrap()
});

static CITE_FOLLOWERS_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"^\s*(?:in|of|from|on)\s*[`'(\[]?\s*\z").unwrap());

static INSIDE_AUTHOR_YEAR_PAREN_RE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(
        r"\(\s*(?:[A-Z][A-Za-z\-']+(?:,\s*[A-Z][A-Za-z\-']+|\s+(?:and|&)\s+[A-Z][A-Za-z\-']+)*\s+)?(?:19|20)\d{2}[a-z]?(?:,\s*p\.?\s*\d+)?,\s*\z",
    )
    .unwrap()
});

static ANAPHORIC_PAPER_REF_RE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(
        r"(?i)^\s*(?:in|of|from|on)\s+(?:that|their|the\s+(?:cited|referenced))\s+(?:paper|article|study|work)\b",
    )
    .unwrap()
});

fn is_inside_cite_macro(ancestors: &[&Node]) -> bool {
    ancestors
        .iter()
        .any(|anc| matches!(anc, Node::Macro(m) if CITE_MACROS_FOR_SCOPE.contains(&m.macroname.as_str())))
}

fn macro_body_has_cite(macro_node: &MacroNode) -> bool {
    for arg in &macro_node.args {
        let Some(Node::Group(g)) = arg else { continue };
        let mut found = false;
        walk(&g.nodelist, &mut |node, _ancestors| {
            if let Node::Macro(m) = node {
                if CITE_MACROS_FOR_SCOPE.contains(&m.macroname.as_str()) {
                    found = true;
                }
            }
        });
        if found {
            return true;
        }
    }
    false
}

fn is_in_cited_footnote(ancestors: &[&Node]) -> bool {
    for anc in ancestors.iter().rev() {
        if let Node::Macro(m) = anc {
            if m.macroname == "footnote" {
                return macro_body_has_cite(m);
            }
        }
    }
    false
}

/// Mirrors `crossrefs.py::_is_cross_paper_reference`.
fn is_cross_paper_reference(
    chars: &str,
    match_start: usize,
    match_end: usize,
    parent: &[Slot],
    idx: usize,
    ancestors: &[&Node],
) -> bool {
    let tail = &chars[match_end.min(chars.len())..];
    if CITE_FOLLOWERS_RE.is_match(tail) {
        if let Some(Node::Macro(m)) = sibling(parent, idx as isize + 1) {
            if CITE_MACROS_FOR_SCOPE.contains(&m.macroname.as_str()) {
                return true;
            }
        }
    }
    let head_lo = floor_char_boundary(chars, match_start.saturating_sub(60));
    let head = &chars[head_lo..match_start.min(chars.len())];
    if INSIDE_AUTHOR_YEAR_PAREN_RE.is_match(head) {
        return true;
    }
    if ANAPHORIC_PAPER_REF_RE.is_match(tail) {
        return true;
    }
    if is_in_cited_footnote(ancestors) {
        return true;
    }
    if is_inside_cite_macro(ancestors) {
        return true;
    }
    false
}

/// JSS-XREF-001 — figures/tables referenced by `\ref{}`, not by number.
pub fn check_xref_001(file: &str, parsed: &ParsedTex) -> Vec<Violation> {
    let line_index = LineIndex::new(&parsed.chars);
    let mut out = Vec::new();
    let top: Vec<Slot> = parsed.nodes.iter().map(Some).collect();
    let mut ancestors: Vec<&Node> = Vec::new();
    walk_with_context(&top, &mut ancestors, &mut |node, ancestors, parent, idx| {
        let Node::Chars(c) = node else { return };
        if !is_in_prose_context(ancestors) {
            return;
        }
        for m in FIG_TAB_NUMBER_RE.find_iter(&c.chars) {
            if is_cross_paper_reference(&c.chars, m.start(), m.end(), parent, idx, ancestors) {
                continue;
            }
            let abs_pos = c.span.pos + c.chars[..m.start()].chars().count();
            let matched = m.as_str();
            let first_word = matched.split_whitespace().next().unwrap_or(matched);
            out.push(tex_violation(
                file,
                &line_index,
                abs_pos,
                "JSS-XREF-001",
                Some(format!(
                    "Replace {} with '{first_word}~\\ref{{<label>}}'.",
                    py_repr(matched)
                )),
            ));
        }
    });
    out
}

// ---------------------------------------------------------------------
// JSS-XREF-002 — (\ref{...}) paren-wrapped
// ---------------------------------------------------------------------

fn chars_ends_with_open_paren(node: Slot) -> bool {
    let Some(Node::Chars(c)) = node else {
        return false;
    };
    c.chars.trim_end_matches([' ', '\t', '\n']).ends_with('(')
}

fn chars_starts_with_close_paren(node: Slot) -> bool {
    let Some(Node::Chars(c)) = node else {
        return false;
    };
    c.chars
        .trim_start_matches([' ', '\t', '\n'])
        .starts_with(')')
}

const NON_EQUATION_LABEL_PREFIXES: &[&str] = &[
    "sec",
    "subsec",
    "subsubsec",
    "ssec",
    "section",
    "fig",
    "figure",
    "tab",
    "table",
    "alg",
    "algorithm",
    "app",
    "appendix",
    "chap",
    "chapter",
    "ch",
    "mod",
    "model",
    "lst",
    "listing",
    "code",
];

/// Concatenated `Chars` content of the macro's first `Group` arg.
/// Mirrors the shared body of `crossrefs.py::_label_has_non_equation_prefix`
/// / `_eqref_label_text`.
fn label_arg_text(macro_node: &MacroNode) -> String {
    for arg in &macro_node.args {
        if let Some(Node::Group(g)) = arg {
            let mut text = String::new();
            for child in &g.nodelist {
                if let Node::Chars(c) = child {
                    text.push_str(&c.chars);
                }
            }
            return text;
        }
    }
    String::new()
}

fn label_has_non_equation_prefix(macro_node: &MacroNode) -> bool {
    let label_text = label_arg_text(macro_node);
    let label_text = label_text.trim();
    let Some(colon) = label_text.find(':') else {
        return false;
    };
    let prefix = label_text[..colon].trim().to_lowercase();
    NON_EQUATION_LABEL_PREFIXES.contains(&prefix.as_str())
}

fn eqref_label_text(macro_node: &MacroNode) -> String {
    label_arg_text(macro_node)
}

static EQ_ABBREV_TAIL_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"\b(Eqs?|Eqns?)\.?\s*~?\s*\z").unwrap());

/// JSS-XREF-002 — equation references use `Equation~\ref{...}` rather
/// than bare `(\ref{...})` or `\eqref{...}`; also normalizes the
/// `Eq.~\ref{...}` abbreviation.
pub fn check_xref_002(file: &str, parsed: &ParsedTex) -> Vec<Violation> {
    let line_index = LineIndex::new(&parsed.chars);
    let mut out = Vec::new();
    extract::iter_with_parent_visit(&parsed.nodes, &mut |parent, idx, node| {
        let Node::Macro(m) = node else { return };
        if m.macroname == "ref" {
            let mut before = sibling(parent, idx as isize - 1);
            let after = sibling(parent, idx as isize + 1);
            if let Some(Node::Specials(s)) = before {
                if s.chars == "~" {
                    before = sibling(parent, idx as isize - 2);
                }
            }
            let eq_abbrev = if let Some(Node::Chars(c)) = before {
                EQ_ABBREV_TAIL_RE
                    .find(&c.chars)
                    .map(|mm| (c, mm.start(), mm.as_str().to_string()))
            } else {
                None
            };
            if let Some((bc, abbrev_offset, abbrev_text)) = eq_abbrev {
                if !label_has_non_equation_prefix(m) {
                    let lower = abbrev_text.to_lowercase();
                    let is_plural = lower.starts_with("eqs") || lower.starts_with("eqns");
                    let canonical = if is_plural { "Equations" } else { "Equation" };
                    let abbrev_start = bc.span.pos + bc.chars[..abbrev_offset].chars().count();
                    let macro_end = m.span.pos + m.span.len;
                    let macro_body: String = parsed.chars[m.span.pos..macro_end].iter().collect();
                    let trimmed = abbrev_text.trim();
                    out.push(tex_violation_with_fix(
                        file,
                        &line_index,
                        m.span.pos,
                        "JSS-XREF-002",
                        Some(format!(
                            "Replace {} before \\ref with '{canonical}~' (capitalised, non-breaking space).",
                            py_repr(trimmed)
                        )),
                        Some(Fix {
                            start: abbrev_start,
                            end: macro_end,
                            replacement: format!("{canonical}~{macro_body}"),
                            description: format!("replace '{trimmed}' with '{canonical}~'"),
                            confidence: FixConfidence::Safe,
                        }),
                    ));
                    return;
                }
            }
            if !chars_ends_with_open_paren(before) {
                return;
            }
            if !chars_starts_with_close_paren(after) {
                return;
            }
            if label_has_non_equation_prefix(m) {
                return;
            }
            let (Some(Node::Chars(bc)), Some(Node::Chars(ac))) = (before, after) else {
                return;
            };
            let stripped = bc.chars.trim_end_matches([' ', '\t', '\n']);
            let paren_open = bc.span.pos + stripped.chars().count() - 1;
            let total_len = ac.chars.chars().count();
            let lstripped_len = ac
                .chars
                .trim_start_matches([' ', '\t', '\n'])
                .chars()
                .count();
            let paren_close = ac.span.pos + (total_len - lstripped_len);
            let macro_end = m.span.pos + m.span.len;
            let macro_body: String = parsed.chars[m.span.pos..macro_end].iter().collect();
            out.push(tex_violation_with_fix(
                file,
                &line_index,
                m.span.pos,
                "JSS-XREF-002",
                Some(
                    "Replace '(\\ref{...})' or '\\eqref{...}' with 'Equation~\\ref{...}' (capitalised, non-breaking space)."
                        .to_string(),
                ),
                Some(Fix {
                    start: paren_open,
                    end: paren_close + 1,
                    replacement: format!("Equation~{macro_body}"),
                    description: "replace (\\ref{}) with Equation~\\ref{}".to_string(),
                    confidence: FixConfidence::Safe,
                }),
            ));
        } else if m.macroname == "eqref" {
            if label_has_non_equation_prefix(m) {
                return;
            }
            let label_text = eqref_label_text(m);
            if label_text.is_empty() {
                return;
            }
            let macro_end = m.span.pos + m.span.len;
            out.push(tex_violation_with_fix(
                file,
                &line_index,
                m.span.pos,
                "JSS-XREF-002",
                Some(
                    "Replace '\\eqref{...}' with 'Equation~\\ref{...}' (capitalised, non-breaking space; \\eqref renders as parenthesised which reviewers discourage)."
                        .to_string(),
                ),
                Some(Fix {
                    start: m.span.pos,
                    end: macro_end,
                    replacement: format!("Equation~\\ref{{{label_text}}}"),
                    description: "replace \\eqref{} with Equation~\\ref{}".to_string(),
                    confidence: FixConfidence::Safe,
                }),
            ));
        }
    });
    out
}

// ---------------------------------------------------------------------
// JSS-XREF-003 — "Subsection N.N" -> "Section N.N"
// ---------------------------------------------------------------------

static SUBSECTION_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"(?-u)\bSubsection[s]?\s*~?\s*\d").unwrap());

/// JSS-XREF-003 — subsection references say "Section x.y", not
/// "Subsection x.y".
pub fn check_xref_003(file: &str, parsed: &ParsedTex) -> Vec<Violation> {
    let line_index = LineIndex::new(&parsed.chars);
    let mut out = Vec::new();
    walk(&parsed.nodes, &mut |node, ancestors| {
        let Node::Chars(c) = node else { return };
        if !is_in_prose_context(ancestors) {
            return;
        }
        for m in SUBSECTION_RE.find_iter(&c.chars) {
            let abs_pos = c.span.pos + c.chars[..m.start()].chars().count();
            out.push(tex_violation(
                file,
                &line_index,
                abs_pos,
                "JSS-XREF-003",
                Some(
                    "Use 'Section N.N' (or 'Section~\\ref{<label>}'), not 'Subsection N.N'."
                        .to_string(),
                ),
            ));
        }
    });
    out
}

// ---------------------------------------------------------------------
// JSS-XREF-004 — numbered equation missing \label{}
// ---------------------------------------------------------------------

const NUMBERED_EQ_ENVS: &[&str] = &["equation", "align", "eqnarray", "gather", "multline"];
const MULTILINE_EQ_ENVS: &[&str] = &["align", "eqnarray", "gather"];
const NONUMBER_MACROS: &[&str] = &["nonumber", "notag"];
const TAG_MACROS: &[&str] = &["tag", "tag*"];
const REF_MACROS: &[&str] = &[
    "ref", "eqref", "pageref", "nameref", "autoref", "vref", "cref", "Cref", "Ref", "subref",
];

fn collect_referenced_labels(parsed: &ParsedTex) -> HashSet<String> {
    let mut refs = HashSet::new();
    extract::iter_with_parent_visit(&parsed.nodes, &mut |parent, idx, node| {
        let Node::Macro(m) = node else { return };
        if !REF_MACROS.contains(&m.macroname.as_str()) {
            return;
        }
        let text = extract::macro_args_text(m, parent, idx);
        for key in text.split(',') {
            let k = norm_label_key(key);
            if !k.is_empty() {
                refs.insert(k);
            }
        }
    });
    refs
}

/// Every `\label{X}` key inside `env`, one entry per direct `Chars`
/// child of the label's group (not concatenated — mirrors
/// `crossrefs.py::_env_label_keys` exactly, including the possibility
/// of multiple keys from one `\label{}` if its body is fragmented
/// into several `Chars` nodes).
fn env_label_keys(env: &EnvironmentNode) -> Vec<String> {
    let mut keys = Vec::new();
    walk(&env.nodelist, &mut |node, _ancestors| {
        let Node::Macro(m) = node else { return };
        if m.macroname != "label" {
            return;
        }
        for arg in &m.args {
            let Some(Node::Group(g)) = arg else { continue };
            for ch in &g.nodelist {
                if let Node::Chars(c) = ch {
                    let k = norm_label_key(&c.chars);
                    if !k.is_empty() {
                        keys.push(k);
                    }
                }
            }
        }
    });
    keys
}

fn env_has_nonumber(env: &EnvironmentNode) -> bool {
    let mut found = false;
    walk(&env.nodelist, &mut |node, _ancestors| {
        if let Node::Macro(m) = node {
            if NONUMBER_MACROS.contains(&m.macroname.as_str()) {
                found = true;
            }
        }
    });
    found
}

fn env_has_tag(env: &EnvironmentNode) -> bool {
    let mut found = false;
    walk(&env.nodelist, &mut |node, _ancestors| {
        if let Node::Macro(m) = node {
            if TAG_MACROS.contains(&m.macroname.as_str()) {
                found = true;
            }
        }
    });
    found
}

fn inside_subequations(ancestors: &[&Node]) -> bool {
    ancestors
        .iter()
        .any(|anc| matches!(anc, Node::Environment(e) if e.environmentname == "subequations"))
}

const MISSING_ROW_LABEL_SUGGESTION: &str = "A numbered equation row carries no \\label{} and can never be referenced. Add \\label{eq:<name>} to the row or suppress its number with \\nonumber.";

fn orphan_label_suggestion(key: &str) -> String {
    format!(
        "Equation label '{key}' is never referenced from the text. Either cite the equation via \\ref{{}} / \\eqref{{}} or suppress the number with \\nonumber."
    )
}

/// Split a multi-line equation env body into contiguous row slices on
/// top-level `\\`. Mirrors `crossrefs.py::_split_env_rows` — the `\\`
/// delimiter node itself is dropped from both adjacent rows.
fn split_env_rows<'a>(source_chars: &[char], env: &'a EnvironmentNode) -> Vec<&'a [Node]> {
    let mut rows = Vec::new();
    let mut start = 0;
    for (i, child) in env.nodelist.iter().enumerate() {
        if let Node::Macro(m) = child {
            let end = (m.span.pos + 2).min(source_chars.len());
            if m.span.pos <= end && source_chars.get(m.span.pos..end) == Some(&['\\', '\\'][..]) {
                rows.push(&env.nodelist[start..i]);
                start = i + 1;
            }
        }
    }
    rows.push(&env.nodelist[start..]);
    rows
}

fn row_has_nonumber(row: &[Node]) -> bool {
    let mut found = false;
    walk(row, &mut |node, _ancestors| {
        if let Node::Macro(m) = node {
            if NONUMBER_MACROS.contains(&m.macroname.as_str()) {
                found = true;
            }
        }
    });
    found
}

fn row_label_positions(row: &[Node]) -> Vec<(String, usize)> {
    let mut out = Vec::new();
    walk(row, &mut |node, _ancestors| {
        let Node::Macro(m) = node else { return };
        if m.macroname != "label" {
            return;
        }
        for arg in &m.args {
            let Some(Node::Group(g)) = arg else { continue };
            for ch in &g.nodelist {
                if let Node::Chars(c) = ch {
                    let k = norm_label_key(&c.chars);
                    if !k.is_empty() {
                        out.push((k, m.span.pos));
                    }
                }
            }
        }
    });
    out
}

/// Per-row orphan check for a multi-line equation env. Mirrors
/// `crossrefs.py::_check_multiline_eq_rows`.
fn check_multiline_eq_rows(
    file: &str,
    line_index: &LineIndex,
    source_chars: &[char],
    env: &EnvironmentNode,
    ancestors: &[&Node],
    referenced: &HashSet<String>,
    out: &mut Vec<Violation>,
) {
    let in_subeq = inside_subequations(ancestors);
    let rows = split_env_rows(source_chars, env);
    let mut numbered: Vec<Vec<(String, usize)>> = Vec::new();
    let mut pending: Vec<(String, usize)> = Vec::new();
    for row in &rows {
        let labels = row_label_positions(row);
        if row_has_nonumber(row) {
            pending.extend(labels);
            continue;
        }
        let mut combined = std::mem::take(&mut pending);
        combined.extend(labels);
        numbered.push(combined);
    }
    if numbered.is_empty() {
        return;
    }
    let all_keys: Vec<&String> = numbered.iter().flatten().map(|(k, _)| k).collect();
    let has_referenced = all_keys.iter().any(|k| referenced.contains(k.as_str()));
    let mut seen_lines: HashSet<u32> = HashSet::new();

    if in_subeq {
        for labels in &numbered {
            for (key, pos) in labels {
                if referenced.contains(key) {
                    continue;
                }
                let line = line_index.lineno_colno(*pos).0;
                if !seen_lines.insert(line) {
                    continue;
                }
                out.push(tex_violation(
                    file,
                    line_index,
                    *pos,
                    "JSS-XREF-004",
                    Some(orphan_label_suggestion(key)),
                ));
            }
        }
        return;
    }

    if !has_referenced {
        let orphan_keys: Vec<&str> = all_keys
            .iter()
            .filter(|k| !referenced.contains(k.as_str()))
            .map(|k| k.as_str())
            .collect();
        let suggestion = if !orphan_keys.is_empty() {
            format!(
                "Equation label(s) {} are never referenced from the text. Either cite the equation via \\ref{{}} / \\eqref{{}} or suppress the number with \\nonumber.",
                py_repr(&orphan_keys.join(", "))
            )
        } else {
            "Add \\label{eq:<name>} inside the equation so it can be referenced from the text."
                .to_string()
        };
        out.push(tex_violation(
            file,
            line_index,
            env.span.pos,
            "JSS-XREF-004",
            Some(suggestion),
        ));
        return;
    }

    let mut missing_label_reported = false;
    for labels in &numbered {
        if labels.is_empty() {
            if missing_label_reported {
                continue;
            }
            let line = line_index.lineno_colno(env.span.pos).0;
            if !seen_lines.insert(line) {
                continue;
            }
            missing_label_reported = true;
            out.push(tex_violation(
                file,
                line_index,
                env.span.pos,
                "JSS-XREF-004",
                Some(MISSING_ROW_LABEL_SUGGESTION.to_string()),
            ));
            continue;
        }
        for (key, pos) in labels {
            if referenced.contains(key) {
                continue;
            }
            let line = line_index.lineno_colno(*pos).0;
            if !seen_lines.insert(line) {
                continue;
            }
            out.push(tex_violation(
                file,
                line_index,
                *pos,
                "JSS-XREF-004",
                Some(orphan_label_suggestion(key)),
            ));
        }
    }
}

/// JSS-XREF-004 — numbered equations carry `\label{}` and are
/// referenced.
pub fn check_xref_004(file: &str, parsed: &ParsedTex) -> Vec<Violation> {
    let line_index = LineIndex::new(&parsed.chars);
    let mut out = Vec::new();
    let referenced = collect_referenced_labels(parsed);
    let top: Vec<Slot> = parsed.nodes.iter().map(Some).collect();
    let mut ancestors: Vec<&Node> = Vec::new();
    walk_with_context(
        &top,
        &mut ancestors,
        &mut |node, ancestors, _parent, _idx| {
            let Node::Environment(env) = node else { return };
            if !NUMBERED_EQ_ENVS.contains(&env.environmentname.as_str()) {
                return;
            }
            if env_has_tag(env) {
                return;
            }
            if MULTILINE_EQ_ENVS.contains(&env.environmentname.as_str()) {
                check_multiline_eq_rows(
                    file,
                    &line_index,
                    &parsed.chars,
                    env,
                    ancestors,
                    &referenced,
                    &mut out,
                );
                return;
            }
            if inside_subequations(ancestors) {
                return;
            }
            let label_keys = env_label_keys(env);
            if label_keys.is_empty() {
                if env_has_nonumber(env) {
                    return;
                }
                out.push(tex_violation(
                file,
                &line_index,
                env.span.pos,
                "JSS-XREF-004",
                Some("Add \\label{eq:<name>} inside the equation so it can be referenced from the text.".to_string()),
            ));
                return;
            }
            if !label_keys.iter().any(|k| referenced.contains(k)) {
                let joined = label_keys.join(", ");
                out.push(tex_violation(
                file,
                &line_index,
                env.span.pos,
                "JSS-XREF-004",
                Some(format!(
                    "Equation label(s) {} are never referenced from the text. Either cite the equation via \\ref{{}} / \\eqref{{}} or suppress the number with \\nonumber.",
                    py_repr(&joined)
                )),
            ));
            }
        },
    );
    out
}

// ---------------------------------------------------------------------
// JSS-XREF-005 — figures/tables carry \label{} and are referenced
// ---------------------------------------------------------------------

const FLOAT_ENVS: &[&str] = &["figure", "figure*", "table", "table*"];
const LISTING_FLOAT_ENVS: &[&str] = &["lstlisting"];
const CAPTION_MACROS: &[&str] = &["caption", "captionof"];
const SUBFLOAT_ENVS: &[&str] = &[
    "subfigure",
    "subtable",
    "subfloat",
    "minipage",
    "wrapfigure",
    "wraptable",
    "sidewaysfigure",
    "sidewaystable",
];

fn env_has_caption(env: &EnvironmentNode) -> bool {
    let mut found = false;
    walk(&env.nodelist, &mut |node, _ancestors| {
        if let Node::Macro(m) = node {
            if CAPTION_MACROS.contains(&m.macroname.as_str()) {
                found = true;
            }
        }
    });
    found
}

fn env_contains_subfloat(env: &EnvironmentNode) -> bool {
    let mut found = false;
    walk(&env.nodelist, &mut |node, _ancestors| {
        if let Node::Environment(e) = node {
            if SUBFLOAT_ENVS.contains(&e.environmentname.as_str()) {
                found = true;
            }
        }
    });
    found
}

/// The raw `[...]` option-list text of a `\begin{lstlisting}[...]`
/// environment, or `None` when it carries no option block.
/// Brace-aware (a `]` inside `caption={... ]}` doesn't close the
/// list). Mirrors `crossrefs.py::_lstlisting_option_block` — manual
/// scanning rather than `env.latex_verbatim()` + regex since Rust has
/// no per-node verbatim reconstruction method; equivalent to matching
/// `\\begin\{lstlisting\}[ \t]*\[` at the environment's own start.
fn lstlisting_option_block(source_chars: &[char], env: &EnvironmentNode) -> Option<String> {
    let raw: Vec<char> =
        source_chars[env.span.pos..(env.span.pos + env.span.len).min(source_chars.len())].to_vec();
    let prefix: Vec<char> = "\\begin{lstlisting}".chars().collect();
    if raw.len() < prefix.len() || raw[..prefix.len()] != prefix[..] {
        return None;
    }
    let mut i = prefix.len();
    while i < raw.len() && matches!(raw[i], ' ' | '\t') {
        i += 1;
    }
    if i >= raw.len() || raw[i] != '[' {
        return None;
    }
    let opts_start = i + 1;
    let mut depth: i32 = 0;
    let mut j = opts_start;
    while j < raw.len() {
        match raw[j] {
            '{' => depth += 1,
            '}' => depth = (depth - 1).max(0),
            ']' if depth == 0 => return Some(raw[opts_start..j].iter().collect()),
            _ => {}
        }
        j += 1;
    }
    None
}

fn lstlisting_caption_and_labels(
    source_chars: &[char],
    env: &EnvironmentNode,
) -> (bool, Vec<String>) {
    let Some(opts) = lstlisting_option_block(source_chars, env) else {
        return (false, Vec::new());
    };
    let mut parts = Vec::new();
    let mut depth: i32 = 0;
    let mut cur = String::new();
    for ch in opts.chars() {
        match ch {
            '{' => {
                depth += 1;
                cur.push(ch);
            }
            '}' => {
                depth = (depth - 1).max(0);
                cur.push(ch);
            }
            ',' if depth == 0 => parts.push(std::mem::take(&mut cur)),
            _ => cur.push(ch),
        }
    }
    if !cur.trim().is_empty() {
        parts.push(cur);
    }
    let mut has_caption = false;
    let mut labels = Vec::new();
    for part in &parts {
        let Some(eq_idx) = part.find('=') else {
            continue;
        };
        let key = part[..eq_idx].trim().to_lowercase();
        let val = &part[eq_idx + 1..];
        if key == "caption" {
            has_caption = true;
        } else if key == "label" {
            let trimmed = val.trim().trim_matches(|c| c == '{' || c == '}');
            let norm = norm_label_key(trimmed);
            if !norm.is_empty() {
                labels.push(norm);
            }
        }
    }
    (has_caption, labels)
}

/// JSS-XREF-005 — captioned figures/tables/listings carry `\label{}`
/// and are referenced from the text (the float analogue of
/// JSS-XREF-004).
pub fn check_xref_005(file: &str, parsed: &ParsedTex) -> Vec<Violation> {
    let line_index = LineIndex::new(&parsed.chars);
    let mut out = Vec::new();
    let referenced = collect_referenced_labels(parsed);
    walk(&parsed.nodes, &mut |node, _ancestors| {
        let Node::Environment(env) = node else { return };
        let envname = env.environmentname.as_str();
        let (label_keys, add_hint, ref_hint): (Vec<String>, &str, &str) = if FLOAT_ENVS
            .contains(&envname)
        {
            if !env_has_caption(env) {
                return;
            }
            (
                env_label_keys(env),
                "Add \\label{fig:<name>} / \\label{tab:<name>} to the float so it can be referenced from the text.",
                "are never referenced from the text. Add a Figure~\\ref{} / Table~\\ref{} callout in the prose.",
            )
        } else if LISTING_FLOAT_ENVS.contains(&envname) {
            let (has_caption, labels) = lstlisting_caption_and_labels(&parsed.chars, env);
            if !has_caption {
                return;
            }
            (
                labels,
                "Add label=lst:<name> to the lstlisting options so it can be referenced from the text.",
                "are never referenced from the text. Add a Listing~\\ref{} callout in the prose.",
            )
        } else {
            return;
        };
        if label_keys.is_empty() {
            out.push(tex_violation(
                file,
                &line_index,
                env.span.pos,
                "JSS-XREF-005",
                Some(add_hint.to_string()),
            ));
            return;
        }
        if !label_keys.iter().any(|k| referenced.contains(k)) {
            let joined = label_keys.join(", ");
            out.push(tex_violation(
                file,
                &line_index,
                env.span.pos,
                "JSS-XREF-005",
                Some(format!("Float label(s) {} {ref_hint}", py_repr(&joined))),
            ));
        }
    });
    out
}

// ---------------------------------------------------------------------
// JSS-XREF-006 — figure/table floats carry a \caption{}
// ---------------------------------------------------------------------

/// JSS-XREF-006 — figure/table floats carry a `\caption{}`.
pub fn check_xref_006(file: &str, parsed: &ParsedTex) -> Vec<Violation> {
    let line_index = LineIndex::new(&parsed.chars);
    let mut out = Vec::new();
    walk(&parsed.nodes, &mut |node, _ancestors| {
        let Node::Environment(env) = node else { return };
        if !FLOAT_ENVS.contains(&env.environmentname.as_str()) {
            return;
        }
        if env_has_caption(env) {
            return;
        }
        if env_contains_subfloat(env) {
            return;
        }
        let kind = if env.environmentname.starts_with("table") {
            "table"
        } else {
            "figure"
        };
        out.push(tex_violation(
            file,
            &line_index,
            env.span.pos,
            "JSS-XREF-006",
            Some(format!(
                "Add a \\caption{{...}} to the {kind} so it is numbered and can be referenced from the text."
            )),
        ));
    });
    out
}

// ---------------------------------------------------------------------
// JSS-XREF-007 — abbreviated cross-reference nouns (Fig./Sec./Tab.)
// ---------------------------------------------------------------------

static FIGSECTAB_ABBREV_TAIL_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"(?i)\b(Figs?|Secs?|Tabs?)\.\s*~?\s*\z").unwrap());

fn figsectab_canonical(abbrev_lower: &str) -> &'static str {
    match abbrev_lower {
        "fig" => "Figure",
        "figs" => "Figures",
        "sec" => "Section",
        "secs" => "Sections",
        "tab" => "Table",
        "tabs" => "Tables",
        other => unreachable!(
            "FIGSECTAB_ABBREV_TAIL_RE only matches fig/figs/sec/secs/tab/tabs, got {other:?}"
        ),
    }
}

fn chars_ends_with_figsectab_abbrev(node: Slot) -> Option<(usize, String)> {
    let Some(Node::Chars(c)) = node else {
        return None;
    };
    let caps = FIGSECTAB_ABBREV_TAIL_RE.captures(&c.chars)?;
    let start = caps.get(0).unwrap().start();
    let abbrev = caps.get(1).unwrap().as_str().to_string();
    Some((start, abbrev))
}

/// JSS-XREF-007 — abbreviated cross-reference nouns (Fig./Sec./Tab.)
/// before `\ref{}` are spelled out.
pub fn check_xref_007(file: &str, parsed: &ParsedTex) -> Vec<Violation> {
    let line_index = LineIndex::new(&parsed.chars);
    let mut out = Vec::new();
    extract::iter_with_parent_visit(&parsed.nodes, &mut |parent, idx, node| {
        let Node::Macro(m) = node else { return };
        if m.macroname != "ref" {
            return;
        }
        let mut before = sibling(parent, idx as isize - 1);
        if let Some(Node::Specials(s)) = before {
            if s.chars == "~" {
                before = sibling(parent, idx as isize - 2);
            }
        }
        let Some((abbrev_offset, abbrev)) = chars_ends_with_figsectab_abbrev(before) else {
            return;
        };
        let Some(Node::Chars(bc)) = before else {
            return;
        };
        let canonical = figsectab_canonical(&abbrev.to_lowercase());
        let abbrev_start = bc.span.pos + bc.chars[..abbrev_offset].chars().count();
        let macro_end = m.span.pos + m.span.len;
        let macro_body: String = parsed.chars[m.span.pos..macro_end].iter().collect();
        out.push(tex_violation_with_fix(
            file,
            &line_index,
            m.span.pos,
            "JSS-XREF-007",
            Some(format!(
                "Spell out the cross-reference noun: '{canonical}~\\ref{{...}}', not '{abbrev}.~\\ref{{...}}'."
            )),
            Some(Fix {
                start: abbrev_start,
                end: macro_end,
                replacement: format!("{canonical}~{macro_body}"),
                description: format!("replace '{abbrev}.' with '{canonical}~'"),
                confidence: FixConfidence::Safe,
            }),
        ));
    });
    out
}
