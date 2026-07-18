//! Markup rules — mirrors `journals/jss/rules/markup.py`
//! (JSS-MARKUP-001..004). The noisiest, most heuristic-laden rule
//! module in the Python codebase (per the porting plan).
//!
//! Offset convention (see individual helper doc comments for the ones
//! that matter): helpers taking `chars: &str` operate on a single
//! `CharsNode`'s own text using regex BYTE offsets directly as an
//! approximation of Python's codepoint offsets — the same accepted
//! approximation `abbreviations.rs::looks_like_author_initial` already
//! uses (only wrong in the presence of non-ASCII text within the
//! lookback/lookahead window, validated clean by the fixture sweep).
//! Helpers taking `source: &[char]` (the whole document) and an
//! `abs_pos`/`abs_end` always use exact codepoint offsets, matching
//! `Fix`/`Violation` position units — those `abs_pos` values are
//! computed via the established `c.span.pos + c.chars[..byte_off]
//! .chars().count()` conversion before being passed in.

use super::py_repr;
use super::tex_common::{tex_violation, tex_violation_with_fix};
use crate::report::{Fix, FixConfidence, Violation};
use crate::terms::TERMS;
use crate::tex::extract;
use crate::tex::node::{GroupDelims, GroupNode, MacroNode, Node};
use crate::tex::position::LineIndex;
use crate::tex::prose::{
    is_in_prose_context, is_inside_verbatim, walk, walk_with_context, Slot, MARKUP_MACROS,
    SECTION_MACROS,
};
use crate::tex::ParsedTex;
use regex::Regex;
use std::collections::HashSet;
use std::sync::LazyLock;

// --- shared low-level helpers -----------------------------------------

fn byte_at(s: &str, i: usize) -> Option<u8> {
    s.as_bytes().get(i).copied()
}

fn floor_char_boundary(s: &str, mut i: usize) -> usize {
    i = i.min(s.len());
    while i > 0 && !s.is_char_boundary(i) {
        i -= 1;
    }
    i
}

fn ceil_char_boundary(s: &str, mut i: usize) -> usize {
    let n = s.len();
    if i >= n {
        return n;
    }
    while i < n && !s.is_char_boundary(i) {
        i += 1;
    }
    i
}

fn line_start(chars: &[char], pos: usize) -> usize {
    match chars[..pos.min(chars.len())]
        .iter()
        .rposition(|&c| c == '\n')
    {
        Some(i) => i + 1,
        None => 0,
    }
}

fn line_end(chars: &[char], pos: usize) -> usize {
    let pos = pos.min(chars.len());
    match chars[pos..].iter().position(|&c| c == '\n') {
        Some(i) => pos + i,
        None => chars.len(),
    }
}

static TOKEN_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"[A-Za-z][A-Za-z0-9+\-]*").unwrap());

const LANG_HYPHEN_STATS_TAILS: &[&str] = &["squared", "package", "packages"];

fn is_lang_hyphen_term(_prefix: &str, tail: &str) -> bool {
    let lower = tail.to_lowercase();
    LANG_HYPHEN_STATS_TAILS.contains(&lower.as_str())
}

fn is_initial(chars: &str, offset: usize) -> bool {
    byte_at(chars, offset + 1) == Some(b'.')
}

fn is_superscripted(chars: &str, offset: usize, token_len: usize) -> bool {
    byte_at(chars, offset + token_len) == Some(b'^')
}

static PATH_SEGMENT_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"^[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*\.[A-Za-z0-9]+").unwrap());

fn is_filename_context(chars: &str, offset: usize, token_len: usize) -> bool {
    if offset > 0 && matches!(byte_at(chars, offset - 1), Some(b'.') | Some(b'/')) {
        return true;
    }
    let tail = offset + token_len;
    if byte_at(chars, tail) == Some(b'/') {
        if let Some(rest) = chars.get(tail + 1..) {
            return PATH_SEGMENT_RE.is_match(rest);
        }
    }
    false
}

static MACRO_DEF_LINE_RE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(
        r"^[ \t]*\\(?:(?:re)?new(?:command|environment)|providecommand|def|DeclareMathOperator|DeclareRobustCommand|newcolumntype|newtheorem)\b",
    )
    .unwrap()
});

fn is_macro_definition_line(source: &[char], abs_pos: usize) -> bool {
    let ls = line_start(source, abs_pos);
    let le = line_end(source, ls);
    let line: String = source[ls..le].iter().collect();
    MACRO_DEF_LINE_RE.is_match(&line)
}

static CODE_MACRO_REDEF_RE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(
        r"\\(?:(?:re)?newcommand|providecommand|def|DeclareRobustCommand)\b\*?\s*\{?\s*\\(?:code|pkg|proglang)\b",
    )
    .unwrap()
});

fn is_code_macro_redefinition(source: &[char], abs_pos: usize) -> bool {
    let ls = line_start(source, abs_pos);
    let le = line_end(source, abs_pos);
    let line: String = source[ls..le].iter().collect();
    CODE_MACRO_REDEF_RE.is_match(&line)
}

fn is_escaped(source: &[char], idx: usize) -> bool {
    let mut n = 0u32;
    let mut j = idx as isize - 1;
    while j >= 0 && source[j as usize] == '\\' {
        n += 1;
        j -= 1;
    }
    n % 2 == 1
}

static MACRO_DEF_HEAD_BEFORE_BRACE_RE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(
        r"\\(?:(?:re)?new(?:command|environment)|providecommand|def|DeclareMathOperator|DeclareRobustCommand|newcolumntype|newtheorem)\*?(?:(?:\s|%[^\n]*\n)*(?:\{[^{}]*\}|\[[^\]]*\]|\\[A-Za-z@]+))*(?:\s|%[^\n]*\n)*\z",
    )
    .unwrap()
});

const DEF_BODY_SCAN_LIMIT: usize = 4000;

fn is_in_macro_definition_body(source: &[char], abs_pos: usize) -> bool {
    let mut depth: i32 = 0;
    let lower = abs_pos.saturating_sub(DEF_BODY_SCAN_LIMIT) as isize;
    let mut i = abs_pos as isize - 1;
    while i >= lower {
        let ii = i as usize;
        let c = source[ii];
        if (c == '{' || c == '}') && !is_escaped(source, ii) {
            if c == '}' {
                depth += 1;
            } else if depth == 0 {
                let head_start = ii.saturating_sub(120);
                let head: String = source[head_start..ii].iter().collect();
                return MACRO_DEF_HEAD_BEFORE_BRACE_RE.is_match(&head);
            } else {
                depth -= 1;
            }
        }
        i -= 1;
    }
    false
}

static EPONYM_FOLLOWERS_RE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"(?i)^[\s~]+(?:index|indices|statistic|statistics|criterion|criteria|step|steps)\b")
        .unwrap()
});
static POSSESSIVE_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"[A-Za-z](?:'|\u{2019})s\z").unwrap());

fn is_eponym_letter(chars: &str, offset: usize, token: &str) -> bool {
    if token.len() != 1 {
        return false;
    }
    let head_end = offset.min(chars.len());
    let head = chars[..head_end].trim_end();
    if POSSESSIVE_RE.is_match(head) {
        return true;
    }
    let tail = chars.get(offset + 1..).unwrap_or("");
    EPONYM_FOLLOWERS_RE.is_match(tail)
}

const LABEL_WORDS: &[&str] = &[
    "panel",
    "panels",
    "group",
    "groups",
    "class",
    "classes",
    "model",
    "models",
    "compartment",
    "compartments",
    "column",
    "columns",
    "plate",
    "arm",
    "arms",
    "factor",
    "factors",
    "level",
    "levels",
    "label",
    "labels",
    "letter",
    "letters",
];

static LABEL_WORDS_RE: LazyLock<Regex> = LazyLock::new(|| {
    let mut sorted: Vec<&str> = LABEL_WORDS.to_vec();
    sorted.sort_unstable();
    Regex::new(&format!(r"(?i)\b(?:{})\b", sorted.join("|"))).unwrap()
});

static ENUM_CHAIN_RE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"\b[A-Z]\b(?:\s*,\s*[A-Z]\b)+\s*(?:,\s*)?(?:or|and)\s+[A-Z]\b").unwrap()
});

static PREV_WORD_RE: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"([A-Za-z]+)\s+\z").unwrap());

fn near_label_word(chars: &str, start: usize, end: usize) -> bool {
    let head_lo = floor_char_boundary(chars, start.saturating_sub(24));
    let head_hi = start.min(chars.len());
    let head = if head_lo <= head_hi {
        &chars[head_lo..head_hi]
    } else {
        ""
    };
    let tail_lo = end.min(chars.len());
    let tail_hi = ceil_char_boundary(chars, (end + 24).min(chars.len()));
    let tail = if tail_lo <= tail_hi {
        &chars[tail_lo..tail_hi]
    } else {
        ""
    };
    LABEL_WORDS_RE.is_match(head) || LABEL_WORDS_RE.is_match(tail)
}

/// Mirrors `markup.py::_is_label_letter`. The `ENUM_CHAIN_RE` scan is
/// a full-string search filtered to matches starting within
/// `[offset-40, offset+41)`, rather than a sliced substring, since
/// `ENUM_CHAIN_RE` starts with `\b` — slicing first would corrupt that
/// boundary assertion at the window edge (Python's
/// `finditer(chars, pos, endpos)` sees the real surrounding text, a
/// sliced Rust substring would not).
fn is_label_letter(chars: &str, offset: usize, token: &str) -> bool {
    if token.len() != 1 {
        return false;
    }
    let head = &chars[..offset.min(chars.len())];
    if let Some(caps) = PREV_WORD_RE.captures(head) {
        let w = caps.get(1).unwrap().as_str().to_lowercase();
        if LABEL_WORDS.contains(&w.as_str()) {
            return true;
        }
    }
    let win_lo = offset.saturating_sub(40);
    let win_hi = offset + 41;
    for m in ENUM_CHAIN_RE.find_iter(chars) {
        if m.start() < win_lo || m.start() >= win_hi {
            continue;
        }
        if m.start() <= offset && offset < m.end() {
            return near_label_word(chars, m.start(), m.end());
        }
    }
    false
}

fn is_tex_amp_adjacent(source: &[char], abs_pos: usize, abs_end: usize) -> bool {
    let after_ok = source.get(abs_end..abs_end + 2) == Some(&['\\', '&'][..]);
    let before_ok = abs_pos >= 2 && source.get(abs_pos - 2..abs_pos) == Some(&['\\', '&'][..]);
    after_ok || before_ok
}

fn is_table_cell_letter(source: &[char], abs_pos: usize, abs_end: usize) -> bool {
    let ls = line_start(source, abs_pos);
    let le = line_end(source, abs_end);
    let before: String = source[ls..abs_pos].iter().collect();
    let before = before.trim_end().trim_end_matches('{');
    let after: String = source[abs_end..le].iter().collect();
    let after = after.trim_start().trim_start_matches('}');
    before.ends_with('&') && (after.starts_with('&') || after.starts_with("\\\\"))
}

static OPTION_KEY_RE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(
        r"\b(?:language|style|backgroundcolor|basicstyle|keywordstyle|commentstyle|stringstyle|columns|frame|caption|label|numbers|numberstyle|firstline|lastline|tabsize|breaklines|formatcom)\s*=\s*\z",
    )
    .unwrap()
});

fn is_option_list_value(chars: &str, offset: usize) -> bool {
    let lo = floor_char_boundary(chars, offset.saturating_sub(50));
    let hi = offset.min(chars.len());
    if lo > hi {
        return false;
    }
    OPTION_KEY_RE.is_match(&chars[lo..hi])
}

// ---------------------------------------------------------------------
// JSS-MARKUP-001 / MARKUP-002 — language / package names in prose
// ---------------------------------------------------------------------

const SANDWICH_FOLLOWERS: &[&str] = &[
    "estimator",
    "estimators",
    "matrix",
    "matrices",
    "type",
    "types",
    "expression",
    "expressions",
    "method",
    "methods",
    "form",
    "forms",
    "covariance",
    "covariances",
    "construction",
    "coefficient",
    "coefficients",
    "variance",
    "variances",
    "formula",
    "formulae",
    "formulas",
    "product",
    "products",
    "meat",
    "bread",
    "any",
];

static OF_THE_RE: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"(?i)of the\s*\z").unwrap());
static NEXT_WORD_RE: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"^[A-Za-z]+").unwrap());

/// Mirrors `markup.py::_disambiguates_to_method` — currently only
/// `_PACKAGE_TERM_DISAMBIGUATORS` has a `"sandwich"` entry, so the
/// dict lookup is inlined as a direct equality check.
fn disambiguates_to_method(chars: &str, offset: usize, token: &str) -> bool {
    if token != "sandwich" {
        return false;
    }
    let head = &chars[..offset.min(chars.len())];
    if OF_THE_RE.is_match(head) {
        return true;
    }
    let after_token = offset + token.len();
    let tail = chars.get(after_token..).unwrap_or("");
    let tail = tail.trim_start_matches([' ', '\t', '\r', '\n', '\u{0c}', '\u{0b}', '_', '*']);
    if tail.is_empty() {
        return false;
    }
    let Some(m) = NEXT_WORD_RE.find(tail) else {
        return false;
    };
    SANDWICH_FOLLOWERS.contains(&m.as_str().to_lowercase().as_str())
}

const BIB_ENV_NAMES: &[&str] = &["thebibliography"];

fn is_inside_bibliography(ancestors: &[&Node]) -> bool {
    ancestors
        .iter()
        .any(|anc| matches!(anc, Node::Environment(e) if BIB_ENV_NAMES.contains(&e.environmentname.as_str())))
}

#[allow(clippy::too_many_arguments)]
fn check_bare_terms(
    file: &str,
    parsed: &ParsedTex,
    terms: &HashSet<String>,
    rule_id: &str,
    wrap_macro: &str,
    skip_initials: bool,
    emit_fix: bool,
) -> Vec<Violation> {
    let line_index = LineIndex::with_offset(&parsed.chars, parsed.line_offset);
    let mut out = Vec::new();
    walk(&parsed.nodes, &mut |node, ancestors| {
        let Node::Chars(c) = node else { return };
        if !is_in_prose_context(ancestors) {
            return;
        }
        let in_bib = is_inside_bibliography(ancestors);
        for m in TOKEN_RE.find_iter(&c.chars) {
            let offset = m.start();
            let token = m.as_str();
            if !terms.contains(token) {
                if let Some(dash) = token.find('-') {
                    let prefix = &token[..dash];
                    let tail = &token[dash + 1..];
                    if terms.contains(prefix) && !is_lang_hyphen_term(prefix, tail) {
                        let abs_pos = c.span.pos + c.chars[..offset].chars().count();
                        let abs_end = abs_pos + prefix.chars().count();
                        let fix = emit_fix.then(|| Fix {
                            start: abs_pos,
                            end: abs_end,
                            replacement: format!("\\{wrap_macro}{{{prefix}}}"),
                            description: format!("wrap {prefix} in \\{wrap_macro}{{}}"),
                            confidence: FixConfidence::Safe,
                        });
                        out.push(tex_violation_with_fix(
                            file,
                            &line_index,
                            abs_pos,
                            rule_id,
                            Some(format!(
                                "Wrap {} in \\{wrap_macro}{{{prefix}}} (found bare in {}).",
                                py_repr(prefix),
                                py_repr(token)
                            )),
                            fix,
                        ));
                    }
                }
                continue;
            }
            if in_bib && token.len() == 1 {
                continue;
            }
            if skip_initials && token.len() == 1 && is_initial(&c.chars, offset) {
                continue;
            }
            if is_superscripted(&c.chars, offset, token.len()) {
                continue;
            }
            if is_filename_context(&c.chars, offset, token.len()) {
                continue;
            }
            if is_option_list_value(&c.chars, offset) {
                continue;
            }
            if disambiguates_to_method(&c.chars, offset, token) {
                continue;
            }
            if is_eponym_letter(&c.chars, offset, token) {
                continue;
            }
            if is_label_letter(&c.chars, offset, token) {
                continue;
            }
            let abs_pos = c.span.pos + c.chars[..offset].chars().count();
            let abs_end = abs_pos + token.len();
            if is_macro_definition_line(&parsed.chars, abs_pos) {
                continue;
            }
            if is_in_macro_definition_body(&parsed.chars, abs_pos) {
                continue;
            }
            if is_tex_amp_adjacent(&parsed.chars, abs_pos, abs_end) {
                continue;
            }
            if token.len() == 1 && is_table_cell_letter(&parsed.chars, abs_pos, abs_end) {
                continue;
            }
            let fix = emit_fix.then(|| Fix {
                start: abs_pos,
                end: abs_end,
                replacement: format!("\\{wrap_macro}{{{token}}}"),
                description: format!("wrap {token} in \\{wrap_macro}{{}}"),
                confidence: FixConfidence::Safe,
            });
            out.push(tex_violation_with_fix(
                file,
                &line_index,
                abs_pos,
                rule_id,
                Some(format!(
                    "Wrap {} in \\{wrap_macro}{{{token}}}.",
                    py_repr(token)
                )),
                fix,
            ));
        }
    });
    out
}

/// JSS-MARKUP-001 — programming-language names wrapped in `\proglang{}`.
pub fn check_markup_001(file: &str, parsed: &ParsedTex) -> Vec<Violation> {
    check_bare_terms(
        file,
        parsed,
        &TERMS.languages,
        "JSS-MARKUP-001",
        "proglang",
        true,
        true,
    )
}

static TITLE_PKG_IDIOM_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"^\s*([a-z][A-Za-z0-9.]*)\s*(?::|--|\u{2014}|\z)").unwrap());
static TITLE_PKG_SOURCE_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"\\title\s*\{\s*\\pkg\s*\{").unwrap());

/// Char-only projection of a title group up to the first macro child.
/// Mirrors `markup.py::_project_title_plain_text`.
fn project_title_plain_text(group: &GroupNode) -> String {
    let mut parts = String::new();
    for child in &group.nodelist {
        match child {
            Node::Chars(c) => parts.push_str(&c.chars),
            Node::Macro(_) => break,
            Node::Specials(s) => parts.push_str(&s.chars),
            _ => {}
        }
    }
    parts.trim_start().to_string()
}

/// Flags `\title{pkgname ...}` openings as MARKUP-002. Mirrors
/// `markup.py::_check_title_package_idiom`.
fn check_title_package_idiom(file: &str, parsed: &ParsedTex) -> Vec<Violation> {
    let line_index = LineIndex::with_offset(&parsed.chars, parsed.line_offset);
    let mut out = Vec::new();
    extract::iter_with_parent_visit(&parsed.nodes, &mut |_parent, _idx, node| {
        let Node::Macro(m) = node else { return };
        if m.macroname != "title" {
            return;
        }
        let group = m.args.iter().find_map(|a| match a {
            Some(Node::Group(g)) => Some(g),
            _ => None,
        });
        let Some(group) = group else { return };
        let text = project_title_plain_text(group);
        let Some(caps) = TITLE_PKG_IDIOM_RE.captures(&text) else {
            return;
        };
        let pkg_name = caps.get(1).unwrap().as_str();
        let macro_end = m.span.pos + m.span.len;
        let source: String = parsed.chars[m.span.pos..macro_end].iter().collect();
        if TITLE_PKG_SOURCE_RE.is_match(&source) {
            return;
        }
        out.push(tex_violation(
            file,
            &line_index,
            m.span.pos,
            "JSS-MARKUP-002",
            Some(format!(
                "Wrap the leading package name {} in \\pkg{{{pkg_name}}} in the \\title{{}} body.",
                py_repr(pkg_name)
            )),
        ));
    });
    out
}

/// JSS-MARKUP-002 — software-package names wrapped in `\pkg{}`.
pub fn check_markup_002(file: &str, parsed: &ParsedTex) -> Vec<Violation> {
    let mut out = check_bare_terms(
        file,
        parsed,
        &TERMS.r_packages,
        "JSS-MARKUP-002",
        "pkg",
        false,
        true,
    );
    out.extend(check_title_package_idiom(file, parsed));
    out
}

// ---------------------------------------------------------------------
// JSS-MARKUP-003 — inline function/argument names + R sentinel values
// ---------------------------------------------------------------------

static FUNCTION_CALL_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"\b[a-zA-Z][a-zA-Z0-9_.]*\(\s*\)").unwrap());

static OPEN_CODE_MACRO_RE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"\\(?:code|texttt|pkg|proglang|verb|fct|command|samp|file)\*?\{[^{}]*\z").unwrap()
});

fn already_code_wrapped(source: &[char], abs_pos: usize) -> bool {
    let ls = line_start(source, abs_pos);
    let region: String = source[ls..abs_pos].iter().collect();
    OPEN_CODE_MACRO_RE.is_match(&region)
}

static WRAPPER_DEF_RE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(
        r"\\(?:def\s*\\([A-Za-z@]+)|(?:re)?newcommand\*?\s*\{\s*\\([A-Za-z@]+)\s*\})[^\n]*?(?:\\lstinline\b|\\(?:e|E)?[vV]erb\b|\\mintinline\b|\\texttt\s*\{\s*#|\\code\s*\{\s*#)",
    )
    .unwrap()
});

fn custom_code_wrapper_macros(source: &str) -> HashSet<String> {
    let mut names = HashSet::new();
    for caps in WRAPPER_DEF_RE.captures_iter(source) {
        let name = caps
            .get(1)
            .or_else(|| caps.get(2))
            .expect("one alternative always captures")
            .as_str()
            .to_string();
        names.insert(name);
    }
    names
}

fn inside_custom_wrapper(ancestors: &[&Node], wrappers: &HashSet<String>) -> bool {
    if wrappers.is_empty() {
        return false;
    }
    ancestors
        .iter()
        .any(|anc| matches!(anc, Node::Macro(m) if wrappers.contains(&m.macroname)))
}

const R_SENTINEL_VALUES: &[&str] = &[
    "NULL",
    "NA",
    "NA_integer_",
    "NA_real_",
    "NA_character_",
    "NA_complex_",
    "TRUE",
    "FALSE",
];
static SENTINEL_TOKEN_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"[A-Za-z][A-Za-z0-9_]*").unwrap());

const INVISIBLE_TEXT_MACROS: &[&str] = &["index", "nomenclature", "glossary", "glsadd"];

fn is_inside_invisible_macro(ancestors: &[&Node]) -> bool {
    ancestors
        .iter()
        .any(|anc| matches!(anc, Node::Macro(m) if INVISIBLE_TEXT_MACROS.contains(&m.macroname.as_str())))
}

const ALGORITHM_ENVS: &[&str] = &[
    "algorithmic",
    "algorithm",
    "algorithm2e",
    "algorithmicx",
    "algorithmial",
    "pseudocode",
    "ALC@g",
];

fn is_inside_algorithm(ancestors: &[&Node]) -> bool {
    ancestors
        .iter()
        .any(|anc| matches!(anc, Node::Environment(e) if ALGORITHM_ENVS.contains(&e.environmentname.as_str())))
}

static OPEN_SHORT_OPTARG_RE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"\\(?:caption|(?:sub)*section|paragraph|subparagraph|chapter|part)\*?\[[^\]]*\z")
        .unwrap()
});

fn in_short_optarg(source: &[char], abs_pos: usize) -> bool {
    let ls = line_start(source, abs_pos);
    let region: String = source[ls..abs_pos].iter().collect();
    OPEN_SHORT_OPTARG_RE.is_match(&region)
}

static EMAIL_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"^[\w.+-]+@[\w-]+\.[\w.-]+\z").unwrap());
static URL_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"^(?:https?://|www\.|ftp://)").unwrap());
static DOI_RE: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"^10\.\d{4,}/").unwrap());
static NUM_LABEL_RE: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"^\d+:?\z").unwrap());

fn texttt_is_noncode(inner: &str) -> bool {
    let inner = inner.trim();
    EMAIL_RE.is_match(inner)
        || URL_RE.is_match(inner)
        || inner.contains("//")
        || DOI_RE.is_match(inner)
        || NUM_LABEL_RE.is_match(inner)
}

fn is_inside_jss_markup(ancestors: &[&Node]) -> bool {
    ancestors
        .iter()
        .any(|anc| matches!(anc, Node::Macro(m) if MARKUP_MACROS.contains(&m.macroname.as_str())))
}

/// JSS-MARKUP-003 — inline function/argument names and bare R
/// sentinel values wrapped in `\code{}`; `\texttt{}` retargeted to the
/// appropriate JSS markup macro.
pub fn check_markup_003(file: &str, parsed: &ParsedTex) -> Vec<Violation> {
    let line_index = LineIndex::with_offset(&parsed.chars, parsed.line_offset);
    let mut out = Vec::new();
    let wrappers = custom_code_wrapper_macros(&parsed.source);
    let top: Vec<Slot> = parsed.nodes.iter().map(Some).collect();
    let mut ancestors: Vec<&Node> = Vec::new();
    walk_with_context(&top, &mut ancestors, &mut |node, ancestors, parent, idx| {
        if let Node::Macro(m) = node {
            if m.macroname == "texttt" {
                if is_inside_verbatim(ancestors) {
                    return;
                }
                if is_inside_bibliography(ancestors) {
                    return;
                }
                if is_inside_jss_markup(ancestors) {
                    return;
                }
                if is_inside_invisible_macro(ancestors) {
                    return;
                }
                if is_inside_algorithm(ancestors) {
                    return;
                }
                if in_short_optarg(&parsed.chars, m.span.pos) {
                    return;
                }
                if is_code_macro_redefinition(&parsed.chars, m.span.pos) {
                    return;
                }
                let inner = extract::macro_args_text(m, parent, idx);
                let inner = inner.trim();
                if texttt_is_noncode(inner) {
                    return;
                }
                let (target_macro, suggestion) = if TERMS.languages.contains(inner) {
                    (
                        "proglang",
                        format!(
                            "\\texttt{{{inner}}} names a programming language; wrap as \\proglang{{{inner}}}."
                        ),
                    )
                } else if TERMS.r_packages.contains(inner) {
                    (
                        "pkg",
                        format!(
                            "\\texttt{{{inner}}} names an R package; wrap as \\pkg{{{inner}}}."
                        ),
                    )
                } else {
                    (
                        "code",
                        "Replace \\texttt{...} with the appropriate JSS markup: \\code{...} for inline code, \\pkg{...} for package names, \\proglang{...} for language names."
                            .to_string(),
                    )
                };
                out.push(tex_violation_with_fix(
                    file,
                    &line_index,
                    m.span.pos,
                    "JSS-MARKUP-003",
                    Some(suggestion),
                    Some(Fix {
                        start: m.span.pos,
                        end: m.span.pos + "\\texttt".len(),
                        replacement: format!("\\{target_macro}"),
                        description: format!("replace \\texttt with \\{target_macro}"),
                        confidence: FixConfidence::Safe,
                    }),
                ));
                return;
            }
        }
        let Node::Chars(c) = node else { return };
        if !is_in_prose_context(ancestors) {
            return;
        }
        if inside_custom_wrapper(ancestors, &wrappers) {
            return;
        }
        if is_inside_invisible_macro(ancestors) {
            return;
        }
        if is_inside_algorithm(ancestors) {
            return;
        }
        if is_inside_bibliography(ancestors) {
            return;
        }
        for m in FUNCTION_CALL_RE.find_iter(&c.chars) {
            let abs_pos = c.span.pos + c.chars[..m.start()].chars().count();
            if already_code_wrapped(&parsed.chars, abs_pos) {
                continue;
            }
            if in_short_optarg(&parsed.chars, abs_pos) {
                continue;
            }
            out.push(tex_violation(
                file,
                &line_index,
                abs_pos,
                "JSS-MARKUP-003",
                Some(format!(
                    "Wrap {} in \\code{{{}}}.",
                    py_repr(m.as_str()),
                    m.as_str()
                )),
            ));
        }
        for m in SENTINEL_TOKEN_RE.find_iter(&c.chars) {
            let token = m.as_str();
            if !R_SENTINEL_VALUES.contains(&token) {
                continue;
            }
            let start = m.start();
            let end = m.end();
            if c.chars[..start].trim_end().ends_with('=') {
                continue;
            }
            let next_char = c.chars[end..].chars().next();
            if matches!(next_char, Some('\'') | Some('\u{2019}')) {
                continue;
            }
            let abs_pos = c.span.pos + c.chars[..start].chars().count();
            let abs_end = c.span.pos + c.chars[..end].chars().count();
            if in_short_optarg(&parsed.chars, abs_pos) {
                continue;
            }
            out.push(tex_violation_with_fix(
                file,
                &line_index,
                abs_pos,
                "JSS-MARKUP-003",
                Some(format!(
                    "Wrap bare R sentinel {} in \\code{{{token}}}.",
                    py_repr(token)
                )),
                Some(Fix {
                    start: abs_pos,
                    end: abs_end,
                    replacement: format!("\\code{{{token}}}"),
                    description: format!("wrap {token} in \\code{{}}"),
                    confidence: FixConfidence::Safe,
                }),
            ));
        }
    });
    out
}

// ---------------------------------------------------------------------
// JSS-MARKUP-004 — section titles with markup need a plain-text shim
// ---------------------------------------------------------------------

const NON_MARKUP_TITLE_MACROS: &[&str] = &[
    "label",
    "index",
    "nocite",
    "ignorespaces",
    "dots",
    "ldots",
    "cdots",
    "vdots",
    "textbackslash",
    "textunderscore",
    "'",
    "`",
    "\"",
    "^",
    "~",
    "=",
    ".",
    "u",
    "v",
    "H",
    "t",
    "c",
    "d",
    "b",
    "r",
    "k",
    " ",
    ",",
    ";",
    ":",
    "!",
    "&",
    "_",
    "$",
    "#",
    "%",
    "{",
    "}",
    "ss",
    "aa",
    "AA",
    "ae",
    "AE",
    "oe",
    "OE",
    "o",
    "O",
    "l",
    "L",
    "i",
    "j",
    "S",
    "P",
];

fn has_optional_shim(macro_node: &MacroNode) -> bool {
    macro_node
        .args
        .iter()
        .any(|a| matches!(a, Some(Node::Group(g)) if g.delims == GroupDelims::Bracket))
}

fn mandatory_arg_contains_markup(macro_node: &MacroNode) -> bool {
    for arg in &macro_node.args {
        let Some(Node::Group(g)) = arg else { continue };
        let mut found = false;
        walk(&g.nodelist, &mut |node, _ancestors| match node {
            Node::Math(_) => found = true,
            Node::Macro(m) if !NON_MARKUP_TITLE_MACROS.contains(&m.macroname.as_str()) => {
                found = true;
            }
            _ => {}
        });
        return found;
    }
    false
}

fn collect_plain_text(nodes: &[Node], out: &mut String) {
    for node in nodes {
        match node {
            Node::Math(_) => continue,
            Node::Chars(c) => out.push_str(&c.chars),
            Node::Group(g) => collect_plain_text(&g.nodelist, out),
            Node::Environment(e) => collect_plain_text(&e.nodelist, out),
            Node::Macro(m) => {
                if NON_MARKUP_TITLE_MACROS.contains(&m.macroname.as_str()) {
                    continue;
                }
                for arg in &m.args {
                    if let Some(Node::Group(g)) = arg {
                        if g.delims == GroupDelims::Brace {
                            collect_plain_text(&g.nodelist, out);
                        }
                    }
                }
            }
            Node::Specials(_) | Node::Comment(_) => {}
        }
    }
}

static WHITESPACE_RUN_RE: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"\s+").unwrap());

fn project_section_title_to_plain(group: &GroupNode) -> String {
    let mut text = String::new();
    collect_plain_text(&group.nodelist, &mut text);
    WHITESPACE_RUN_RE.replace_all(&text, " ").trim().to_string()
}

fn build_markup_004_fix(macro_node: &MacroNode) -> Option<Fix> {
    let mandatory_group = macro_node.args.iter().find_map(|a| match a {
        Some(Node::Group(g)) if g.delims == GroupDelims::Brace => Some(g),
        _ => None,
    })?;
    let plain = project_section_title_to_plain(mandatory_group);
    if plain.is_empty() {
        return None;
    }
    let insert_at = mandatory_group.span.pos;
    Some(Fix {
        start: insert_at,
        end: insert_at,
        replacement: format!("[{plain}]"),
        description: format!("Insert plain-text optional arg [{plain}] before the section title."),
        confidence: FixConfidence::Safe,
    })
}

/// JSS-MARKUP-004 — section titles with markup supply a plain-text
/// optional arg: `\section[plain]{markup}`.
pub fn check_markup_004(file: &str, parsed: &ParsedTex) -> Vec<Violation> {
    let line_index = LineIndex::with_offset(&parsed.chars, parsed.line_offset);
    let mut out = Vec::new();
    extract::iter_with_parent_visit(&parsed.nodes, &mut |_parent, _idx, node| {
        let Node::Macro(m) = node else { return };
        if !SECTION_MACROS.contains(&m.macroname.as_str()) {
            return;
        }
        if has_optional_shim(m) {
            return;
        }
        if !mandatory_arg_contains_markup(m) {
            return;
        }
        out.push(tex_violation_with_fix(
            file,
            &line_index,
            m.span.pos,
            "JSS-MARKUP-004",
            Some(
                "Provide a plain-text section title as the optional argument: \\section[plain]{...}."
                    .to_string(),
            ),
            build_markup_004_fix(m),
        ));
    });
    out
}
