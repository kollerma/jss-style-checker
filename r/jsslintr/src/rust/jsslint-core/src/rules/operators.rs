//! Operator/math-notation rules — mirrors
//! `journals/jss/rules/operators.py` (JSS-OPER-001/002/003/004).
//!
//! `check_oper_004` spans every tex-like fragment in the document (not
//! just one `ParsedTex`) so its `flag_pr`/alias pre-scan matches
//! Python's `doc.all_tex_like()` — see its doc comment.

use super::tex_common::tex_violation_with_fix;
use crate::report::{Fix, FixConfidence, Violation};
use crate::tex::extract;
use crate::tex::node::{GroupNode, MacroNode, Node};
use crate::tex::prose::{is_inside_math, walk, walk_with_context, Slot};
use crate::tex::{position::LineIndex, ParsedTex};
use regex::Regex;
use std::collections::HashMap;
use std::sync::LazyLock;

const DISPLAY_EQ_ENVS: &[&str] = &[
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

// --- JSS-OPER-001 ---------------------------------------------------------

static SYMBOL_NOUN_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"\b([a-z])-(value|statistic|values|statistics)\b").unwrap());

/// JSS-OPER-001 — `p-value`-style constructs use `$p$~value`.
pub fn check_oper_001(file: &str, parsed: &ParsedTex) -> Vec<Violation> {
    let line_index = LineIndex::with_offset(&parsed.chars, parsed.line_offset);
    let mut out = Vec::new();
    walk(&parsed.nodes, &mut |node, ancestors| {
        let Node::Chars(c) = node else { return };
        if !crate::tex::prose::is_in_prose_context(ancestors) {
            return;
        }
        for m in SYMBOL_NOUN_RE.captures_iter(&c.chars) {
            let whole = m.get(0).unwrap();
            if whole.start() > 0 && c.chars[..whole.start()].ends_with('[') {
                continue;
            }
            let sym = m.get(1).unwrap().as_str();
            let noun = m.get(2).unwrap().as_str();
            let abs_pos = c.span.pos + c.chars[..whole.start()].chars().count();
            let abs_end = c.span.pos + c.chars[..whole.end()].chars().count();
            let replacement = format!("${sym}$~{noun}");
            out.push(tex_violation_with_fix(
                file,
                &line_index,
                abs_pos,
                "JSS-OPER-001",
                Some(format!(
                    "Replace {} with '{replacement}' (italicized symbol, tie).",
                    super::py_repr(whole.as_str())
                )),
                Some(Fix {
                    start: abs_pos,
                    end: abs_end,
                    replacement: replacement.clone(),
                    description: format!("rewrite {} as {replacement}", whole.as_str()),
                    confidence: FixConfidence::Safe,
                }),
            ));
        }
    });
    out
}

// --- JSS-OPER-002 ---------------------------------------------------------

const BIG_OPERATORS: &[&str] = &[
    "sum",
    "prod",
    "int",
    "iint",
    "iiint",
    "oint",
    "coprod",
    "bigcup",
    "bigcap",
    "bigvee",
    "bigwedge",
    "bigoplus",
    "bigotimes",
    "bigodot",
    "biguplus",
    "bigsqcup",
];
static CARET_T_RE: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"\^\s*T").unwrap());
static SUBSCRIPT_TAIL_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"_(?:\{[^{}]*\}|[A-Za-z0-9])\s*$").unwrap());
static SUBSCRIPT_TOKEN_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"^_[A-Za-z0-9]$").unwrap());

/// Mirrors `operators.py::_t_caret_follows_big_operator`.
fn t_caret_follows_big_operator(parent: &[Slot], idx: usize, match_start: usize) -> bool {
    let Some(Node::Chars(c)) = parent[idx] else {
        return false;
    };
    let mut prefix = c.chars[..match_start].trim_end();
    if let Some(m) = SUBSCRIPT_TAIL_RE.find(prefix) {
        prefix = prefix[..m.start()].trim_end();
    } else if let Some(stripped) = prefix.strip_suffix('_') {
        prefix = stripped.trim_end();
    }
    if !prefix.is_empty() {
        return false;
    }
    let mut j = idx as isize - 1;
    let mut saw_subscript_token = false;
    let mut saw_subscript_group = false;
    while j >= 0 {
        let sib = parent[j as usize];
        match sib {
            Some(Node::Macro(m)) if BIG_OPERATORS.contains(&m.macroname.as_str()) => return true,
            Some(Node::Group(_)) if !saw_subscript_group => {
                saw_subscript_group = true;
                j -= 1;
                continue;
            }
            Some(Node::Chars(sc)) => {
                let text = sc.chars.trim();
                if text.is_empty() {
                    j -= 1;
                    continue;
                }
                if text == "_" {
                    j -= 1;
                    continue;
                }
                if let Some(stripped) = text.strip_suffix('_') {
                    if !saw_subscript_token {
                        let _ = stripped;
                        saw_subscript_token = true;
                        j -= 1;
                        continue;
                    }
                }
                if SUBSCRIPT_TOKEN_RE.is_match(text) && !saw_subscript_token {
                    saw_subscript_token = true;
                    j -= 1;
                    continue;
                }
                return false;
            }
            _ => return false,
        }
    }
    false
}

/// JSS-OPER-002 — literal `^T` transpose should be `\top`.
pub fn check_oper_002(file: &str, parsed: &ParsedTex) -> Vec<Violation> {
    let line_index = LineIndex::with_offset(&parsed.chars, parsed.line_offset);
    let mut out = Vec::new();
    let top: Vec<Slot> = parsed.nodes.iter().map(Some).collect();
    let mut ancestors: Vec<&Node> = Vec::new();
    // `\^\s*T(?![A-Za-z])` — `regex` has no lookahead, so match the
    // simpler `\^\s*T` and reject a following letter manually.
    walk_with_context(&top, &mut ancestors, &mut |node, ancestors, parent, idx| {
        let Node::Chars(c) = node else { return };
        if !is_inside_math(ancestors) {
            return;
        }
        for m in CARET_T_RE.find_iter(&c.chars) {
            let after = c.chars[m.end()..].chars().next();
            if after.is_some_and(|ch| ch.is_ascii_alphabetic()) {
                continue;
            }
            if t_caret_follows_big_operator(parent, idx, m.start()) {
                continue;
            }
            let abs_pos = c.span.pos + c.chars[..m.start()].chars().count();
            out.push(tex_violation_with_fix(
                file,
                &line_index,
                abs_pos,
                "JSS-OPER-002",
                Some("Use '\\top' for transpose: e.g., 'X^\\top X'.".to_string()),
                None,
            ));
        }
    });
    out
}

// --- JSS-OPER-003 ---------------------------------------------------------

static BLANK_LINE_RE: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"\n\s*\n").unwrap());
static CHUNK_COLLAPSE_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"\n[ \t]*(?:\n[ \t]*){2,}").unwrap());
const INVISIBLE_TRAILING_MACROS: &[&str] = &[
    "label",
    "nonumber",
    "notag",
    "tag",
    "tag*",
    "ignorespaces",
    "ignorespacesafterend",
    "leavevmode",
];

fn equation_body_ends_with_period(env: &crate::tex::node::EnvironmentNode) -> bool {
    for child in env.nodelist.iter().rev() {
        match child {
            Node::Chars(c) => {
                let text = c.chars.trim_end();
                if text.is_empty() {
                    continue;
                }
                return text.ends_with('.');
            }
            Node::Macro(m) if INVISIBLE_TRAILING_MACROS.contains(&m.macroname.as_str()) => continue,
            Node::Environment(inner) => return equation_body_ends_with_period(inner),
            _ => return false,
        }
    }
    false
}

fn chars_ends_with_blank_line(node: Option<&Node>) -> bool {
    let Some(Node::Chars(c)) = node else {
        return false;
    };
    if c.chars.is_empty() {
        return false;
    }
    let tail = match c.chars.rfind(|ch: char| !ch.is_whitespace()) {
        Some(byte_idx) => {
            let after = byte_idx + c.chars[byte_idx..].chars().next().unwrap().len_utf8();
            &c.chars[after..]
        }
        None => &c.chars,
    };
    let stripped = CHUNK_COLLAPSE_RE.replace_all(tail, "\n");
    BLANK_LINE_RE.is_match(&stripped)
}

fn chars_starts_with_blank_line(node: Option<&Node>) -> bool {
    let Some(Node::Chars(c)) = node else {
        return false;
    };
    if c.chars.is_empty() {
        return false;
    }
    let head = match c.chars.find(|ch: char| !ch.is_whitespace()) {
        Some(byte_idx) => &c.chars[..byte_idx],
        None => &c.chars,
    };
    let stripped = CHUNK_COLLAPSE_RE.replace_all(head, "\n");
    BLANK_LINE_RE.is_match(&stripped)
}

/// JSS-OPER-003 — no blank lines immediately around display equations.
pub fn check_oper_003(file: &str, parsed: &ParsedTex) -> Vec<Violation> {
    let line_index = LineIndex::with_offset(&parsed.chars, parsed.line_offset);
    let mut out = Vec::new();
    extract::iter_with_parent_visit(&parsed.nodes, &mut |parent: &[Slot], idx, node| {
        let Node::Environment(env) = node else { return };
        if !DISPLAY_EQ_ENVS.contains(&env.environmentname.as_str()) {
            return;
        }
        let before = if idx > 0 { parent[idx - 1] } else { None };
        let after = parent.get(idx + 1).copied().flatten();
        let ends_period = equation_body_ends_with_period(env);
        let blank_before = chars_ends_with_blank_line(before);
        let blank_after = chars_starts_with_blank_line(after) && !ends_period;
        if blank_before || blank_after {
            out.push(tex_violation_with_fix(
                file,
                &line_index,
                env.span.pos,
                "JSS-OPER-003",
                Some(
                    "Remove the blank line(s) around the display equation (add '%' after/before to suppress the paragraph break)."
                        .to_string(),
                ),
                None,
            ));
        }
    });
    out
}

// --- JSS-OPER-004 ---------------------------------------------------------

const NONCANON_PROB_MACROS: &[&str] = &[
    "mathbb",
    "mathsf",
    "mathrm",
    "mathbf",
    "text",
    "operatorname",
    "Pr",
];
const NONCANON_PROB_ARGS: &[&str] = &["E", "Var", "VAR", "var", "Cov", "COV", "cov", "P", "Prob"];
const PROB_GLYPH_MACROS: &[&str] = &["mathbb", "mathsf"];
const DEF_MACROS: &[&str] = &["newcommand", "renewcommand", "providecommand", "def"];
const CANONICAL_PROB_MACROS: &[&str] = &["E", "VAR", "COV", "Prob"];

fn shortcut_macro(shortcut: &str) -> &'static str {
    match shortcut {
        "Prob" => "\\Prob",
        "E" => "\\E",
        _ => "",
    }
}

static LITERAL_VARCOV_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"(var|cov|Var|Cov)(?:[(\[])").unwrap());
static LITERAL_PROB_RE: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"P(?:[(\[])").unwrap());
static PROB_ARG_RELATION_RE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"[=<>|]|\\(?:le|leq|ge|geq|in|mid|vert|neq|ne|leqslant|geqslant)").unwrap()
});

/// `chars[open_idx]` is `(`/`[` right after a bare `P`. True when the
/// balanced argument carries a relational/event token. Mirrors
/// `operators.py::_p_literal_arg_has_relation` — including its
/// no-lookahead-support workaround: Python's regex excludes a
/// following-letter match on `\le`-family tokens via `(?![A-Za-z])`;
/// this port checks that manually since `regex` has no lookahead.
fn p_literal_arg_has_relation(chars: &str, open_idx: usize) -> bool {
    let bytes: Vec<char> = chars.chars().collect();
    let open_ch = bytes[open_idx];
    let close_ch = if open_ch == '(' { ')' } else { ']' };
    let mut depth = 0i32;
    for i in open_idx..bytes.len() {
        let c = bytes[i];
        if c == open_ch {
            depth += 1;
        } else if c == close_ch {
            depth -= 1;
            if depth == 0 {
                let inner: String = bytes[open_idx + 1..i].iter().collect();
                return relation_matches(&inner);
            }
        }
    }
    true
}

fn relation_matches(inner: &str) -> bool {
    for m in PROB_ARG_RELATION_RE.find_iter(inner) {
        let matched = m.as_str();
        if matched.starts_with('\\') {
            let after = inner[m.end()..].chars().next();
            if after.is_some_and(|c| c.is_ascii_alphabetic()) {
                continue; // e.g. \left, \leftarrow — not a bare \le token
            }
        }
        return true;
    }
    false
}

fn macro_first_group_text(macro_node: &MacroNode) -> String {
    for arg in &macro_node.args {
        if let Some(Node::Group(g)) = arg {
            return extract::group_text(g);
        }
    }
    String::new()
}

fn first_macro_name(nodes: &[Node]) -> Option<&str> {
    nodes.iter().find_map(|n| {
        if let Node::Macro(m) = n {
            Some(m.macroname.as_str())
        } else {
            None
        }
    })
}

/// Mirrors `operators.py::_resolve_prob_body`.
fn resolve_prob_body(body_nodes: &[Node]) -> Option<&'static str> {
    let mut result = None;
    walk(body_nodes, &mut |node, _ancestors| {
        if result.is_some() {
            return;
        }
        match node {
            Node::Macro(m) if PROB_GLYPH_MACROS.contains(&m.macroname.as_str()) => {
                let arg = macro_first_group_text(m);
                if arg == "P" {
                    result = Some("Prob");
                } else if arg == "E" {
                    result = Some("E");
                }
            }
            Node::Chars(c) if c.chars.contains("Pr(") => result = Some("Prob"),
            _ => {}
        }
    });
    result
}

fn def_groups(macro_node: &MacroNode) -> Vec<&GroupNode> {
    macro_node
        .args
        .iter()
        .filter_map(|a| {
            if let Some(Node::Group(g)) = a {
                Some(g)
            } else {
                None
            }
        })
        .collect()
}

/// `(alias, shortcut)`. Mirrors `operators.py::_parse_prob_def`.
fn parse_prob_def<'a>(
    node: &'a MacroNode,
    parent: &[Slot<'a>],
    idx: usize,
) -> (Option<&'a str>, Option<&'static str>) {
    let groups = def_groups(node);
    if groups.len() >= 2 {
        let alias = first_macro_name(&groups[0].nodelist);
        return (alias, resolve_prob_body(&groups.last().unwrap().nodelist));
    }
    // `\def` form: alias macro and body group are siblings. Python's
    // `list(parent)[idx+1:idx+4]` auto-clamps an out-of-range slice to
    // `[]`; Rust panics on `start > end`, so clamp both bounds (not
    // just the end) before slicing.
    let mut alias: Option<&str> = None;
    let window_start = (idx + 1).min(parent.len());
    let window_end = (idx + 4).min(parent.len());
    for sib in &parent[window_start..window_end] {
        match sib {
            Some(Node::Macro(m)) if alias.is_none() => {
                alias = Some(&m.macroname);
            }
            Some(Node::Group(g)) => {
                return (alias, resolve_prob_body(&g.nodelist));
            }
            _ => {}
        }
    }
    (None, None)
}

/// True when any tex-like surface invokes `\Prob` (or redefines `\Pr`).
/// Mirrors `operators.py::_doc_uses_prob_macro`.
fn doc_uses_prob_macro(nodes: &[Node]) -> bool {
    let mut found = false;
    walk(nodes, &mut |node, _ancestors| {
        if found {
            return;
        }
        let Node::Macro(m) = node else { return };
        if m.macroname == "Prob" {
            found = true;
            return;
        }
        if matches!(
            m.macroname.as_str(),
            "newcommand" | "renewcommand" | "providecommand"
        ) {
            walk(std::slice::from_ref(node), &mut |child, _a| {
                if let Node::Macro(cm) = child {
                    if cm.macroname == "Pr" && !std::ptr::eq(child, node) {
                        found = true;
                    }
                }
            });
        }
    });
    found
}

struct ProbAlias<'a> {
    /// Index into the `fragments` slice this def site came from —
    /// `check_oper_004` needs it to resolve the right `file`/`LineIndex`
    /// when reporting the violation (mirrors `operators.py::_collect_prob_aliases`
    /// returning `(tex, pos, alias, shortcut)` tuples that carry their
    /// owning fragment directly).
    fragment_idx: usize,
    pos: usize,
    alias: &'a str,
    shortcut: &'static str,
}

/// Mirrors `operators.py::_collect_prob_aliases`, generalized to scan
/// every tex-like fragment (not just one) — see `check_oper_004`'s doc
/// comment for why `aliases`/`def_sites` need whole-document scope.
fn collect_prob_aliases<'a>(
    fragments: &'a [(&str, &ParsedTex)],
) -> (HashMap<&'a str, &'static str>, Vec<ProbAlias<'a>>) {
    let mut aliases = HashMap::new();
    let mut def_sites = Vec::new();
    for (fragment_idx, (_file, parsed)) in fragments.iter().enumerate() {
        let top: Vec<Slot> = parsed.nodes.iter().map(Some).collect();
        let mut ancestors: Vec<&Node> = Vec::new();
        walk_with_context(
            &top,
            &mut ancestors,
            &mut |node, _ancestors, parent, idx| {
                let Node::Macro(m) = node else { return };
                if !DEF_MACROS.contains(&m.macroname.as_str()) {
                    return;
                }
                let (alias, shortcut) = parse_prob_def(m, parent, idx);
                let (Some(alias), Some(shortcut)) = (alias, shortcut) else {
                    return;
                };
                if alias == "Pr" {
                    return;
                }
                aliases.insert(alias, shortcut);
                def_sites.push(ProbAlias {
                    fragment_idx,
                    pos: m.span.pos,
                    alias,
                    shortcut,
                });
            },
        );
    }
    (aliases, def_sites)
}

/// JSS-OPER-004 — probability/expectation notation uses jss.cls
/// shortcuts (`\E`/`\VAR`/`\COV`/`\Prob`). `flag_pr` and
/// `aliases`/`def_sites` need whole-document scope: `flag_pr` must know
/// whether `\Prob` appears ANYWHERE before deciding to flag a bare
/// `\Pr` elsewhere, and an alias defined via `\newcommand` in one
/// `.Rmd` prose block must still be recognized when used in a later
/// one. Mirrors `operators.py::check_jss_oper_004` computing both
/// before its per-fragment walk.
pub fn check_oper_004(fragments: &[(&str, &ParsedTex)]) -> Vec<Violation> {
    let mut out = Vec::new();
    let flag_pr = fragments
        .iter()
        .any(|(_, parsed)| doc_uses_prob_macro(&parsed.nodes));
    let (aliases, def_sites) = collect_prob_aliases(fragments);

    for site in &def_sites {
        let (file, parsed) = fragments[site.fragment_idx];
        let line_index = LineIndex::with_offset(&parsed.chars, parsed.line_offset);
        out.push(tex_violation_with_fix(
            file,
            &line_index,
            site.pos,
            "JSS-OPER-004",
            Some(format!(
                "'\\{}' redefines a probability/expectation operator as a raw glyph; use jss.cls {}.",
                site.alias,
                shortcut_macro(site.shortcut)
            )),
            None,
        ));
    }

    for (file, parsed) in fragments {
        let file = *file;
        let line_index = LineIndex::with_offset(&parsed.chars, parsed.line_offset);
        check_oper_004_fragment(file, parsed, &line_index, flag_pr, &aliases, &mut out);
    }
    out
}

fn check_oper_004_fragment(
    file: &str,
    parsed: &ParsedTex,
    line_index: &LineIndex,
    flag_pr: bool,
    aliases: &HashMap<&str, &'static str>,
    out: &mut Vec<Violation>,
) {
    let top: Vec<Slot> = parsed.nodes.iter().map(Some).collect();
    let mut ancestors: Vec<&Node> = Vec::new();
    walk_with_context(&top, &mut ancestors, &mut |node, ancestors, parent, idx| {
        if let Node::Chars(c) = node {
            if !is_inside_math(ancestors) {
                return;
            }
            for m in LITERAL_VARCOV_RE.captures_iter(&c.chars) {
                let whole = m.get(0).unwrap();
                let token = m.get(1).unwrap().as_str();
                if literal_preceded_by_ident(&c.chars, whole.start()) {
                    continue;
                }
                let shortcut = if matches!(token.chars().next(), Some('v') | Some('V')) {
                    "\\VAR"
                } else {
                    "\\COV"
                };
                let abs_pos = c.span.pos + c.chars[..whole.start()].chars().count();
                out.push(tex_violation_with_fix(
                    file,
                    line_index,
                    abs_pos,
                    "JSS-OPER-004",
                    Some(format!("Use the jss.cls shortcut {shortcut} instead of a bare '{token}(' operator.")),
                    None,
                ));
            }
            for m in LITERAL_PROB_RE.captures_iter(&c.chars) {
                let whole = m.get(0).unwrap();
                if literal_preceded_by_ident_p(&c.chars, whole.start()) {
                    continue;
                }
                let open_idx_char = c.chars[..whole.end() - 1].chars().count();
                if flag_pr && !p_literal_arg_has_relation(&c.chars, open_idx_char) {
                    continue;
                }
                let abs_pos = c.span.pos + c.chars[..whole.start()].chars().count();
                out.push(tex_violation_with_fix(
                    file,
                    line_index,
                    abs_pos,
                    "JSS-OPER-004",
                    Some("Use the jss.cls shortcut \\Prob instead of a bare 'P(' probability operator.".to_string()),
                    None,
                ));
            }
            return;
        }
        let Node::Macro(m) = node else { return };
        if !is_inside_math(ancestors) {
            return;
        }
        if let Some(&shortcut) = aliases.get(m.macroname.as_str()) {
            if !CANONICAL_PROB_MACROS.contains(&m.macroname.as_str()) {
                out.push(tex_violation_with_fix(
                    file,
                    line_index,
                    m.span.pos,
                    "JSS-OPER-004",
                    Some(format!(
                        "'\\{}' aliases a probability/expectation operator; use jss.cls {}.",
                        m.macroname,
                        shortcut_macro(shortcut)
                    )),
                    None,
                ));
                return;
            }
        }
        if m.macroname == "Pr" {
            if flag_pr {
                out.push(tex_violation_with_fix(
                    file,
                    line_index,
                    m.span.pos,
                    "JSS-OPER-004",
                    Some("Use \\Prob from jss.cls instead of \\Pr.".to_string()),
                    None,
                ));
            }
            return;
        }
        if !NONCANON_PROB_MACROS.contains(&m.macroname.as_str()) {
            return;
        }
        let arg_text = extract::macro_args_text(m, parent, idx);
        if NONCANON_PROB_ARGS.contains(&arg_text.as_str()) {
            out.push(tex_violation_with_fix(
                file,
                line_index,
                m.span.pos,
                "JSS-OPER-004",
                Some(format!(
                    "Use the jss.cls shortcut (\\E / \\VAR / \\COV / \\Prob) instead of \\{}{{{arg_text}}}.",
                    m.macroname
                )),
                None,
            ));
        }
    });
}

/// Mirrors the Python regex's `(?<![A-Za-z\\])` negative lookbehind for
/// `_LITERAL_VARCOV_RE` (no lookbehind support in `regex`).
fn literal_preceded_by_ident(chars: &str, byte_start: usize) -> bool {
    match chars[..byte_start].chars().next_back() {
        Some(c) => c.is_ascii_alphabetic() || c == '\\',
        None => false,
    }
}

/// Mirrors `_LITERAL_PROB_RE`'s `(?<![A-Za-z\\_])`.
fn literal_preceded_by_ident_p(chars: &str, byte_start: usize) -> bool {
    match chars[..byte_start].chars().next_back() {
        Some(c) => c.is_ascii_alphabetic() || c == '\\' || c == '_',
        None => false,
    }
}
