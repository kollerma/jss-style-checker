//! Capitalization rules — mirrors `journals/jss/rules/capitalization.py`
//! (JSS-CAP-001/002/004; JSS-CAP-003 is retired — see
//! `specs/003-jss-rule-catalogue/catalogue.yaml`'s `retired_rule_ids`).
//!
//! Scope simplification: `_doc_pkg_names_lower` (CAP-001) scans
//! `doc.all_tex_like()` in Python (every tex-like file in the whole
//! document). This port, like every other Phase 3 rule so far, only
//! ever receives a single `ParsedTex` — consistent with the rest of
//! this phase's per-file scope; multi-file documents are Phase 4
//! engine territory.

use super::tex_common::tex_violation_with_fix;
use crate::report::Violation;
use crate::terms::TERMS;
use crate::tex::extract;
use crate::tex::node::{GroupNode, MacroNode, Node};
use crate::tex::prose::{Slot, MARKUP_MACROS};
use crate::tex::{position::LineIndex, ParsedTex};
use regex::Regex;
use std::collections::HashSet;
use std::sync::LazyLock;

const TITLE_STOPWORDS: &[&str] = &[
    "a", "an", "the", "and", "or", "but", "nor", "for", "so", "yet", "at", "by", "in", "of", "on",
    "to", "up", "via", "with", "as", "is", "vs",
];

const CAP_SECTION_MACROS: &[&str] = &[
    "section",
    "section*",
    "subsection",
    "subsection*",
    "subsubsection",
    "subsubsection*",
];

const EXTRA_PROPER_NOUNS: &[&str] = &[
    "American",
    "Asian",
    "Australian",
    "Austrian",
    "Belgian",
    "British",
    "Canadian",
    "Chinese",
    "Czech",
    "Dutch",
    "English",
    "European",
    "Finnish",
    "French",
    "German",
    "Greek",
    "Indian",
    "Iranian",
    "Irish",
    "Italian",
    "Japanese",
    "Korean",
    "Latin",
    "Mexican",
    "Norwegian",
    "Polish",
    "Portuguese",
    "Russian",
    "Scottish",
    "Spanish",
    "Swedish",
    "Swiss",
    "Turkish",
    "Welsh",
    "Bayes",
    "Bayesian",
    "Bernoulli",
    "Boole",
    "Boolean",
    "Cauchy",
    "Cholesky",
    "Clayton",
    "Cox",
    "Dirichlet",
    "Euclidean",
    "Fisher",
    "Frank",
    "Gauss",
    "Gaussian",
    "Gumbel",
    "Lagrange",
    "Laplace",
    "Markov",
    "Maxwell",
    "Monte",
    "Carlo",
    "Newton",
    "Pareto",
    "Pearson",
    "Poisson",
    "Riemann",
    "Shannon",
    "Wald",
    "Weibull",
    "Wishart",
    "Apple",
    "Google",
    "Linux",
    "Microsoft",
    "Oracle",
    "Unix",
    "Windows",
    "Beijing",
    "Berlin",
    "Bavaria",
    "Boston",
    "China",
    "Germany",
    "Ireland",
    "Spain",
    "Innsbruck",
    "Vienna",
    "Wien",
    "Alzheimer",
    "Campylobacter",
    "Faithful",
    "Indians",
    "Listeria",
    "Moby",
    "Newport",
    "Pima",
    "Salmonella",
];

static PROPER_NOUNS: LazyLock<HashSet<String>> = LazyLock::new(|| {
    let mut set: HashSet<String> = TERMS
        .languages
        .iter()
        .cloned()
        .chain(TERMS.r_packages.iter().cloned())
        .collect();
    set.extend(EXTRA_PROPER_NOUNS.iter().map(|s| s.to_string()));
    set
});

static PROPER_NOUNS_LOWER: LazyLock<HashSet<String>> =
    LazyLock::new(|| PROPER_NOUNS.iter().map(|s| s.to_lowercase()).collect());

/// Mirrors `capitalization.py::_first_group_arg` — unlike the
/// `typography`/`code_style` variants, this one SKIPS a leading
/// optional `[...]` arg (needed for `\section[short]{long}`, where the
/// mandatory `{long}` group is what capitalization rules must check).
fn first_group_arg_brace_only<'a>(
    macro_node: &'a MacroNode,
    parent: &[Slot<'a>],
    idx: usize,
) -> Option<&'a GroupNode> {
    for arg in &macro_node.args {
        if let Some(Node::Group(g)) = arg {
            if g.delims == crate::tex::node::GroupDelims::Bracket {
                continue;
            }
            return Some(g);
        }
    }
    extract::next_group_arg(parent, idx)
}

/// Mirrors `capitalization.py::_group_plain_text`: recurses into
/// nested groups, but skips a group immediately following a markup
/// macro (`\pkg`/`\proglang`/`\code`/...) — that group is the macro's
/// unknown-macro sibling argument, whose author-chosen casing must not
/// leak into the plain-text projection.
fn group_plain_text(group: &GroupNode) -> String {
    let mut parts = String::new();
    let mut skip_next_group = false;
    for child in &group.nodelist {
        match child {
            Node::Chars(c) => {
                skip_next_group = false;
                parts.push_str(&c.chars);
            }
            Node::Group(g) => {
                if skip_next_group {
                    skip_next_group = false;
                    continue;
                }
                parts.push_str(&group_plain_text(g));
            }
            Node::Macro(m) => {
                if m.macroname == "label" {
                    continue;
                }
                skip_next_group = MARKUP_MACROS.contains(&m.macroname.as_str());
            }
            _ => {}
        }
    }
    parts
}

fn words(text: &str) -> Vec<&str> {
    static SPLIT_RE: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"[\s\-]+").unwrap());
    SPLIT_RE
        .split(text.trim())
        .filter(|w| !w.is_empty())
        .collect()
}

fn word_letters_lower(word: &str) -> String {
    word.chars()
        .filter(|c| c.is_ascii_alphabetic())
        .collect::<String>()
        .to_lowercase()
}

fn is_capitalised_word(word: &str) -> bool {
    match word.chars().find(|c| c.is_ascii_alphabetic()) {
        None => true,
        Some(c) => c.is_uppercase(),
    }
}

// --- JSS-CAP-001 --------------------------------------------------------

static FUNCTION_CALL_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"^[A-Za-z][A-Za-z0-9_.]*\(\)?$").unwrap());
static TITLE_LEADING_MARKUP_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"^\{?\s*\\(pkg|proglang|code|fct|verb)\b").unwrap());

/// Raw-source-shaped probe of a title's leading token. Mirrors
/// `capitalization.py::_title_source`.
fn title_source(group: &GroupNode) -> String {
    let mut parts = String::new();
    for child in &group.nodelist {
        match child {
            Node::Chars(c) => {
                parts.push_str(&c.chars);
                if !c.chars.trim().is_empty() {
                    break;
                }
            }
            Node::Macro(m) => {
                parts.push('\\');
                parts.push_str(&m.macroname);
                break;
            }
            Node::Group(g) => {
                parts.push('{');
                parts.push_str(&title_source(g));
                break;
            }
            _ => {}
        }
    }
    parts
}

fn pkg_token(word: &str) -> String {
    let kept: String = word
        .chars()
        .filter(|c| c.is_ascii_alphanumeric() || *c == '.')
        .collect();
    kept.trim_matches('.').to_lowercase()
}

/// Mirrors `capitalization.py::_doc_pkg_names_lower` — see module docs
/// for the single-file scope simplification.
fn doc_pkg_names_lower(nodes: &[Node]) -> HashSet<String> {
    let mut out = HashSet::new();
    extract::iter_with_parent_visit(nodes, &mut |parent: &[Slot], idx, node| {
        let Node::Macro(m) = node else { return };
        if m.macroname != "pkg" {
            return;
        }
        let text = extract::macro_args_text(m, parent, idx);
        if !text.is_empty() {
            let tok = pkg_token(&text);
            if !tok.is_empty() {
                out.insert(tok);
            }
        }
    });
    out
}

// --- shared "capitalise the first word after a colon" check --------------
//
// Both JSS styles agree on the colon: sentence style capitalises "the
// first word after a colon or a hyphen", title style says "Do capitalize
// the first word after a colon". We enforce the COLON only (capital-
// after-hyphen deliberately not enforced — see catalogue notes for
// CAP-002). Mirrors `capitalization.py::_lowercase_after_colon_offender`.

/// Package / language names whose canonical form is lowercase (`zoo`,
/// `ggplot2`, `mgcv`). A colon-leading token matching one is a known
/// code identifier, not a forgotten capital — exempt it.
static LOWERCASE_CANONICAL_TERMS: LazyLock<HashSet<String>> = LazyLock::new(|| {
    TERMS
        .languages
        .iter()
        .chain(TERMS.r_packages.iter())
        .filter(|t| t.chars().next().map(|c| c.is_lowercase()).unwrap_or(false))
        .map(|t| pkg_token(t))
        .filter(|t| !t.is_empty())
        .collect()
});

// Beyond the standard JSS semantic-markup set, also recognise `\class`
// (S4 class names) and typewriter-font wrappers (`\texttt`/`{\tt ...}`/
// `\ttfamily`) authors use for code tokens after a colon.
static COLON_MARKUP_RE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"^\\(?:pkg|proglang|code|fct|verb|class|texttt|ttfamily|tt)\b").unwrap()
});
static AFTER_COLON_REST_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"(?s):\s*(.+)").unwrap());
static AFTER_COLON_TOKEN_RE: LazyLock<Regex> = LazyLock::new(|| Regex::new(r":\s*(\S+)").unwrap());

/// Reconstruct a light LaTeX source of `group` preserving markup macros
/// and math delimiters (which `group_plain_text` strips). Mirrors
/// `capitalization.py::_markup_source`.
fn markup_source(group: &GroupNode) -> String {
    let mut parts = String::new();
    for child in &group.nodelist {
        match child {
            Node::Chars(c) => parts.push_str(&c.chars),
            Node::Math(_) => parts.push('$'),
            Node::Macro(m) => {
                if m.macroname == "label" {
                    continue;
                }
                // Trailing space guarantees a word boundary even when the
                // parser consumed the macro's post-space (`{\tt as.xts}`).
                parts.push('\\');
                parts.push_str(&m.macroname);
                parts.push(' ');
            }
            Node::Group(g) => {
                parts.push('{');
                parts.push_str(&markup_source(g));
                parts.push('}');
            }
            _ => {}
        }
    }
    parts
}

/// True if the first non-space token after a colon is a markup macro or
/// inline math. Mirrors `capitalization.py::_after_colon_is_markup`.
fn after_colon_is_markup(raw: &str) -> bool {
    let Some(caps) = AFTER_COLON_REST_RE.captures(raw) else {
        return false;
    };
    let mut rest = caps.get(1).unwrap().as_str().trim_start();
    while let Some(stripped) = rest.strip_prefix('{') {
        rest = stripped.trim_start();
    }
    if rest.starts_with('$') {
        return true;
    }
    COLON_MARKUP_RE.is_match(rest)
}

/// True if the first token after the first colon starts with a lowercase
/// letter and no exemption applies. Mirrors
/// `capitalization.py::_lowercase_after_colon_offender`.
fn lowercase_after_colon_offender(group: &GroupNode) -> bool {
    let plain = group_plain_text(group);
    let Some(caps) = AFTER_COLON_TOKEN_RE.captures(&plain) else {
        return false;
    };
    let after = caps.get(1).unwrap().as_str();
    match after.chars().next() {
        Some(c) if c.is_alphabetic() => {}
        _ => return false, // (b) non-letter first char
    }
    if LOWERCASE_CANONICAL_TERMS.contains(&pkg_token(after)) {
        return false; // (c) known lowercase-canonical term
    }
    if after_colon_is_markup(&markup_source(group)) {
        return false; // (a) markup/math immediately after colon
    }
    !is_capitalised_word(after)
}

/// JSS-CAP-001 — `\title{}` is in title style.
pub fn check_cap_001(file: &str, parsed: &ParsedTex) -> Vec<Violation> {
    let line_index = LineIndex::new(&parsed.chars);
    let mut out = Vec::new();
    let doc_pkgs_lower = doc_pkg_names_lower(&parsed.nodes);

    extract::iter_with_parent_visit(&parsed.nodes, &mut |parent: &[Slot], idx, node| {
        let Node::Macro(m) = node else { return };
        if m.macroname != "title" {
            return;
        }
        let Some(group) = first_group_arg_brace_only(m, parent, idx) else {
            return;
        };
        let text = group_plain_text(group);
        let ws = words(&text);
        if ws.is_empty() {
            return;
        }
        if text.trim_start().starts_with('-')
            && TITLE_LEADING_MARKUP_RE.is_match(&title_source(group))
        {
            return;
        }
        let has_principal = ws.iter().any(|w| {
            let low = word_letters_lower(w);
            !low.is_empty() && !TITLE_STOPWORDS.contains(&low.as_str())
        });
        if !has_principal {
            return;
        }
        let first = ws[0];
        let first_lower = word_letters_lower(first);
        let first_word_exempt = PROPER_NOUNS_LOWER.contains(&first_lower)
            || doc_pkgs_lower.contains(&pkg_token(first))
            || FUNCTION_CALL_RE.is_match(first);
        if !first_word_exempt
            && (!is_capitalised_word(first) || ws.iter().all(|w| *w == w.to_lowercase()))
        {
            out.push(tex_violation_with_fix(
                file,
                &line_index,
                m.span.pos,
                "JSS-CAP-001",
                Some("Use title style: capitalise principal words in the title.".to_string()),
                None,
            ));
            return;
        }
        // Title style: "Do capitalize the first word after a colon."
        if lowercase_after_colon_offender(group) {
            out.push(tex_violation_with_fix(
                file,
                &line_index,
                m.span.pos,
                "JSS-CAP-001",
                Some("Use title style: capitalise the first word after ':' (or wrap it in \\code{}/\\pkg{} if it is a code identifier or package name).".to_string()),
                None,
            ));
            return;
        }
        for word in &ws[1..] {
            let bare = word_letters_lower(word);
            if bare.is_empty() || bare.chars().count() < 4 {
                continue;
            }
            if *word == word.to_lowercase() && !TITLE_STOPWORDS.contains(&bare.as_str()) {
                if PROPER_NOUNS_LOWER.contains(&bare) || doc_pkgs_lower.contains(&bare) {
                    continue;
                }
                out.push(tex_violation_with_fix(
                    file,
                    &line_index,
                    m.span.pos,
                    "JSS-CAP-001",
                    Some(format!(
                        "Use title style: capitalise principal words in the title (found lowercase {}).",
                        super::py_repr(word)
                    )),
                    None,
                ));
                break;
            }
        }
    });
    out
}

// --- shared sentence-style engine (CAP-002) ------------------------------

static LIST_NUMBERING: &str = r"(?:[(\[]\d+[)\]]|\d+[).]|[(\[][a-z][)\]]|[(\[][ivx]{1,4}[)\]])";

static SENTENCE_BOUNDARY_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(&format!(r"[.:?!]\s+(?:{LIST_NUMBERING}\s+)?(\S)")).unwrap());
static CAPTION_LEADING_LABEL_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(&format!(r"^\s*{LIST_NUMBERING}\s+(\S)")).unwrap());
static HYPHEN_SPLIT_RE: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"-+").unwrap());
static WORD_TRIM_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"^[^A-Za-z0-9]+|[^A-Za-z0-9]+$").unwrap());
static NON_SPACE_RE: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"\S+").unwrap());

/// `(word, is_boundary, is_hyphen_piece)`. Mirrors
/// `capitalization.py::_words_with_boundary`.
fn words_with_boundary(text: &str) -> Vec<(String, bool, bool)> {
    let mut boundary_offsets: HashSet<usize> = HashSet::new();
    for caps in SENTENCE_BOUNDARY_RE.captures_iter(text) {
        boundary_offsets.insert(caps.get(1).unwrap().start());
    }
    if let Some(caps) = CAPTION_LEADING_LABEL_RE.captures(text) {
        boundary_offsets.insert(caps.get(1).unwrap().start());
    }
    let mut out = Vec::new();
    for source_match in NON_SPACE_RE.find_iter(text) {
        let source_word = source_match.as_str();
        let is_boundary = boundary_offsets.contains(&source_match.start());
        for (piece_idx, piece) in HYPHEN_SPLIT_RE.split(source_word).enumerate() {
            let clean = WORD_TRIM_RE.replace_all(piece, "").to_string();
            if clean.is_empty() {
                continue;
            }
            out.push((clean, is_boundary && piece_idx == 0, piece_idx > 0));
        }
    }
    out
}

/// Mirrors `capitalization.py::_looks_like_abbrev`.
fn looks_like_abbrev(token: &str) -> bool {
    let letters: Vec<char> = token.chars().filter(|c| c.is_ascii_alphabetic()).collect();
    if letters.is_empty() {
        return false;
    }
    let n = letters.len();
    if (2..=6).contains(&n) && letters.iter().all(|c| c.is_uppercase()) {
        return true;
    }
    if (3..=7).contains(&n)
        && letters[n - 1].is_lowercase()
        && n > 2
        && letters[..n - 1].iter().all(|c| c.is_uppercase())
    {
        return true;
    }
    for i in 1..n {
        if letters[i].is_uppercase() && letters[i - 1].is_lowercase() {
            return true;
        }
    }
    false
}

fn is_code_identifier(word: &str) -> bool {
    if word.chars().any(|c| c.is_ascii_digit()) {
        return true;
    }
    let letters: Vec<char> = word.chars().filter(|c| c.is_ascii_alphabetic()).collect();
    letters.iter().skip(1).any(|c| c.is_uppercase())
}

fn is_capitalised_offender(word: &str, proper_nouns: &HashSet<String>) -> bool {
    let bare: String = word.chars().filter(|c| c.is_ascii_alphabetic()).collect();
    if bare.is_empty() {
        return false;
    }
    if bare.chars().count() == 1 {
        return false;
    }
    if !bare.chars().next().unwrap().is_uppercase() {
        return false;
    }
    if is_code_identifier(word) {
        return false;
    }
    if proper_nouns.contains(&bare) {
        return false;
    }
    if TITLE_STOPWORDS.contains(&bare.to_lowercase().as_str()) {
        return false;
    }
    if looks_like_abbrev(&bare) {
        return false;
    }
    true
}

fn is_run_eligible(word: &str) -> bool {
    let bare: String = word.chars().filter(|c| c.is_ascii_alphabetic()).collect();
    if bare.chars().count() < 2 {
        return false;
    }
    if is_code_identifier(word) {
        return false;
    }
    bare.chars().next().unwrap().is_uppercase()
}

const PROPER_NOUN_RUN_MAX: usize = 3;

/// Fires when >= `min_offenders` distinct offending capitalisations
/// appear in `group`. Mirrors `capitalization.py::_check_sentence_style`.
#[allow(clippy::too_many_arguments)]
fn check_sentence_style(
    file: &str,
    line_index: &LineIndex,
    pos: usize,
    group: &GroupNode,
    rule_id: &str,
    suggestion: &str,
    collapse_runs: bool,
    proper_nouns: &HashSet<String>,
    min_offenders: usize,
    out: &mut Vec<Violation>,
) {
    let text = group_plain_text(group);
    let words = words_with_boundary(&text);
    if words.is_empty() {
        return;
    }

    let mut seen: HashSet<String> = HashSet::new();
    let mut offenders = 0usize;
    let n = words.len();
    let mut i = 0usize;
    while i < n {
        let (word, is_boundary, _) = &words[i];
        let is_start = i == 0 || *is_boundary;
        if !is_run_eligible(word) {
            i += 1;
            continue;
        }

        let run_start = i;
        let mut j = i + 1;
        let mut all_hyphen_joined = true;
        while j < n {
            let (nw, nb, nh) = &words[j];
            if *nb || !is_run_eligible(nw) {
                break;
            }
            if !nh {
                all_hyphen_joined = false;
            }
            j += 1;
        }
        let run: Vec<&str> = words[run_start..j]
            .iter()
            .map(|(w, _, _)| w.as_str())
            .collect();
        let run_text = run
            .iter()
            .map(|w| w.to_lowercase())
            .collect::<Vec<_>>()
            .join("-");
        let any_known = run
            .iter()
            .any(|p| proper_nouns.contains(*p) || looks_like_abbrev(p));
        let any_stopword = run
            .iter()
            .any(|p| TITLE_STOPWORDS.contains(&p.to_lowercase().as_str()));

        let is_compound = (collapse_runs || all_hyphen_joined)
            && run.len() >= 2
            && run.len() <= PROPER_NOUN_RUN_MAX
            && !any_stopword;

        if is_compound {
            if !any_known && !is_start && !seen.contains(&run_text) {
                seen.insert(run_text);
                offenders += 1;
            }
            i = j;
            continue;
        }

        let run_meta = &words[run_start..j];
        for (k, (w, _, w_is_hyphen)) in run_meta.iter().enumerate() {
            if k == 0 && is_start {
                continue;
            }
            if *w_is_hyphen && k > 0 {
                continue;
            }
            if is_capitalised_offender(w, proper_nouns) {
                let key = w.to_lowercase();
                if seen.contains(&key) {
                    continue;
                }
                seen.insert(key);
                offenders += 1;
            }
        }
        i = j;
    }

    if offenders >= min_offenders {
        out.push(tex_violation_with_fix(
            file,
            line_index,
            pos,
            rule_id,
            Some(suggestion.to_string()),
            None,
        ));
    }
}

/// JSS-CAP-002 — section titles are in sentence style.
pub fn check_cap_002(file: &str, parsed: &ParsedTex) -> Vec<Violation> {
    let line_index = LineIndex::new(&parsed.chars);
    let mut out = Vec::new();
    extract::iter_with_parent_visit(&parsed.nodes, &mut |parent: &[Slot], idx, node| {
        let Node::Macro(m) = node else { return };
        if !CAP_SECTION_MACROS.contains(&m.macroname.as_str()) {
            return;
        }
        let Some(group) = first_group_arg_brace_only(m, parent, idx) else {
            return;
        };
        check_sentence_style(
            file,
            &line_index,
            m.span.pos,
            group,
            "JSS-CAP-002",
            "Use sentence style: capitalise only the first word (proper names remain capitalised).",
            false,
            &PROPER_NOUNS,
            1,
            &mut out,
        );
        // Sentence style also capitalises "the first word after a
        // colon"; independent of the over-capitalisation check above.
        if lowercase_after_colon_offender(group) {
            out.push(tex_violation_with_fix(
                file,
                &line_index,
                m.span.pos,
                "JSS-CAP-002",
                Some("Use sentence style: capitalise the first word after ':' (or wrap it in \\code{}/\\pkg{} if it is a code identifier or package name).".to_string()),
                None,
            ));
        }
    });
    out
}

// --- JSS-CAP-004 ----------------------------------------------------------

fn keyword_case_violation(entries: &[String]) -> bool {
    for entry in entries {
        let ws: Vec<&str> = entry.split_whitespace().collect();
        if ws.len() < 2 {
            continue;
        }
        let mut offenders = 0;
        for word in &ws[1..] {
            let bare: String = word.chars().filter(|c| c.is_ascii_alphabetic()).collect();
            if bare.is_empty() {
                continue;
            }
            if !bare.chars().next().unwrap().is_uppercase() {
                continue;
            }
            if PROPER_NOUNS.contains(&bare) {
                continue;
            }
            if TITLE_STOPWORDS.contains(&bare.to_lowercase().as_str()) {
                continue;
            }
            if looks_like_abbrev(&bare) {
                continue;
            }
            offenders += 1;
        }
        if offenders >= 1 {
            return true;
        }
    }
    false
}

/// JSS-CAP-004 — `\Keywords{}` entries are in sentence case,
/// comma-separated.
pub fn check_cap_004(file: &str, parsed: &ParsedTex) -> Vec<Violation> {
    let line_index = LineIndex::new(&parsed.chars);
    let mut out = Vec::new();
    extract::iter_with_parent_visit(&parsed.nodes, &mut |parent: &[Slot], idx, node| {
        let Node::Macro(m) = node else { return };
        if m.macroname != "Keywords" {
            return;
        }
        let Some(group) = first_group_arg_brace_only(m, parent, idx) else {
            return;
        };
        let text = group_plain_text(group);
        let entries: Vec<String> = text
            .split(',')
            .map(|e| e.trim().to_string())
            .filter(|e| !e.is_empty())
            .collect();
        // Only Title Case across entries is a defect; a fully-lowercase
        // list is the journal's published convention (F5 narrowing).
        if keyword_case_violation(&entries) {
            out.push(tex_violation_with_fix(
                file,
                &line_index,
                m.span.pos,
                "JSS-CAP-004",
                Some(
                    "Use sentence case for keywords: do not capitalise words after the first in an entry (proper names and abbreviations excepted)."
                        .to_string(),
                ),
                None,
            ));
        }
    });
    out
}
