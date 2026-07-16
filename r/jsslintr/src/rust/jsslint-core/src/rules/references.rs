//! References rules — mirrors `journals/jss/rules/references.py`'s
//! bib-facing rules (JSS-REFS-001/003/004/005/006/007). All operate on
//! plain field-value strings (title/journal/note/year) — none need the
//! tex surface or a byte-offset `Fix`.
//!
//! **JSS-REFS-003's online path is deliberately not ported.** Python's
//! `check_jss_refs_003` accepts a `cfg.doi_resolver` (wired only when
//! `jss-lint --crossref` is passed) that calls the live CrossRef API to
//! verify/populate a DOI — see `src/texlint/crossref.py` and the
//! plan's network-dependency callout: that path must never be silently
//! reachable, least of all from a bib-rule port with no visible
//! indication it makes a network call. This module implements only the
//! offline advisory (`resolver is None`) branch.

use super::{entry_violation, py_repr, referenced_entries};
use crate::bib::{Entry, Library};
use crate::report::Violation;
use crate::terms::TERMS;
use crate::tex::node::Node as TexNode;
use regex::{Regex, RegexBuilder};
use std::sync::LazyLock;

fn field_value(entry: &Entry, name: &str) -> String {
    entry
        .field(name)
        .map(|f| f.value.clone())
        .unwrap_or_default()
}

// --- shared regex / word helpers (mirrors references.py module scope) --

static ABBREV_RE: LazyLock<Regex> = LazyLock::new(|| {
    RegexBuilder::new(
        r"\b(?:J|Jnl|Proc|Trans|Conf|Rev|Stat|Sci|Appl|Math|Comp|Comput|Softw|Bull|Ann|Lett|Res|Assoc|Theor|Commun|Med)\.",
    )
    .case_insensitive(true)
    .build()
    .unwrap()
});

static ABBREV_BAREWORD_RE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(
        r"\b(?:Stat|Sci|Appl|Math|Comp|Comput|Softw|Bull|Ann|Lett|Res|Assoc|Theor|Commun|Med|Proc|Trans|Conf|Rev|Mol|Cell|Biol)\b",
    )
    .unwrap()
});

static TITLE_STOPWORDS: &[&str] = &[
    "a", "an", "the", "and", "but", "or", "nor", "for", "so", "yet", "at", "by", "in", "of", "on",
    "to", "up", "via", "with", "as", "is", "vs", "per",
];

static MACRO_STRIP_RE: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"\\[A-Za-z]+\s*").unwrap());
static MARKUP_CONTENT_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"\\[A-Za-z]+\*?\s*\{[^{}]*\}").unwrap());
static WORD_SPLIT_RE: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"[\s\-/]+").unwrap());
static HAS_LETTER_RE: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"[A-Za-z]").unwrap());
static NON_LETTER_RE: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"[^A-Za-z]").unwrap());

/// Mirrors `references.py::_visible_words`.
fn visible_words(title: &str) -> Vec<String> {
    WORD_SPLIT_RE
        .split(title)
        .filter(|w| HAS_LETTER_RE.is_match(w))
        .map(str::to_string)
        .collect()
}

/// Mirrors `references.py::_strip_latex`.
fn strip_latex(text: &str) -> String {
    let no_macros = MACRO_STRIP_RE.replace_all(text, "");
    no_macros.replace(['{', '}'], "")
}

/// Mirrors `references.py::_strip_markup_content`.
fn strip_markup_content(text: &str) -> String {
    let mut cur = text.to_string();
    loop {
        let next = MARKUP_CONTENT_RE.replace_all(&cur, " ").to_string();
        if next == cur {
            break;
        }
        cur = next;
    }
    cur.replace(['{', '}'], "")
}

/// Mirrors `references.py::_word_is_uppercase_start`.
fn word_is_uppercase_start(word: &str) -> bool {
    let letters: String = word.chars().filter(|c| c.is_ascii_alphabetic()).collect();
    match letters.chars().next() {
        None => true,
        Some(c) => c.is_uppercase(),
    }
}

// --- JSS-REFS-001 -------------------------------------------------------

/// JSS-REFS-001 — every entry declares a `year` field (or inherits one
/// via `crossref`).
pub fn check_refs_001(file: &str, library: &Library, tex_like: &[&[TexNode]]) -> Vec<Violation> {
    referenced_entries(library, tex_like)
        .into_iter()
        .filter(|e| e.field("year").is_none() && e.field("crossref").is_none())
        .map(|e| {
            let key = if e.key.is_empty() {
                "<unknown>"
            } else {
                &e.key
            };
            entry_violation(
                file,
                e,
                "JSS-REFS-001",
                Some(format!("Add a year field to entry {}.", py_repr(key))),
            )
        })
        .collect()
}

// --- JSS-REFS-003 (offline advisory only) -------------------------------

static YEAR_RE: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"\d{4}").unwrap());
const DOI_ENTRY_TYPES: &[&str] = &["article", "inproceedings", "incollection", "book", "manual"];
const DOI_ERA_CUTOFF_YEAR: i32 = 2000;

/// JSS-REFS-003 — advisory: article/inproceedings/incollection/book/
/// manual entries should carry a `doi`. Offline path only (see module
/// docs) — no `Fix`, matching Python's non-resolver branch.
pub fn check_refs_003(file: &str, library: &Library, tex_like: &[&[TexNode]]) -> Vec<Violation> {
    let mut out = Vec::new();
    for entry in referenced_entries(library, tex_like) {
        if !DOI_ENTRY_TYPES.contains(&entry.entry_type.to_lowercase().as_str()) {
            continue;
        }
        if entry.field("doi").is_some() {
            continue;
        }
        if let Some(year_field) = entry.field("year") {
            if let Some(m) = YEAR_RE.find(&year_field.value) {
                if m.as_str().parse::<i32>().unwrap_or(9999) < DOI_ERA_CUTOFF_YEAR {
                    continue;
                }
            }
        }
        let key = if entry.key.is_empty() {
            "<unknown>"
        } else {
            &entry.key
        };
        out.push(entry_violation(
            file,
            entry,
            "JSS-REFS-003",
            Some(format!(
                "Add a doi field to entry {} if one is available.",
                py_repr(key)
            )),
        ));
    }
    out
}

// --- JSS-REFS-004 --------------------------------------------------------

static UNWRAP_MACRO_ARG_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"\\[A-Za-z]+\s*\{[^{}]*\}").unwrap());
static UNWRAP_BRACE_RE: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"\{([^{}\\]*)\}").unwrap());
static UNWRAP_BARE_MACRO_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"\\[A-Za-z]+").unwrap());
static TITLE_PACKAGE_PREFIX_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"^\{*\s*\{?([A-Za-z][A-Za-z0-9.]*)\}?\s*:").unwrap());
// Anchored at `^`: every call site mirrors Python's `re.match(...)`
// (anchored-at-start), not `re.search(...)`.
static MARKUP_TITLE_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"^\\(pkg|proglang|code|fct|verb)\{").unwrap());
static TITLE_STOP_WORDS: &[&str] = &[
    "a", "an", "the", "and", "or", "but", "nor", "for", "yet", "so", "if", "as", "at", "by", "in",
    "of", "on", "to", "up", "via", "vs", "with", "from", "into", "onto", "than", "per", "off",
    "about", "around", "et", "al", "is", "be", "do",
];

/// Mirrors `references.py::_title_mentions_unwrapped`. Picks the
/// leftmost match in `text` rather than "the first name `names`
/// happens to yield" — `names` is typically a `HashSet::iter()`,
/// whose order is randomized per process (default `RandomState`
/// hasher), same nondeterminism as Python's `frozenset` iteration
/// under hash randomization. Leftmost-in-text is deterministic and
/// the more intuitive choice for a suggestion message.
fn title_mentions_unwrapped<'a>(
    text: &str,
    names: impl Iterator<Item = &'a str>,
) -> Option<String> {
    let unwrapped = UNWRAP_MACRO_ARG_RE.replace_all(text, "");
    let unwrapped = UNWRAP_BRACE_RE.replace_all(&unwrapped, "$1");
    let unwrapped = UNWRAP_BARE_MACRO_RE.replace_all(&unwrapped, " ");
    let mut best: Option<(usize, &str)> = None;
    for name in names {
        let pattern = format!(r"\b{}\b", regex::escape(name));
        if let Some(m) = Regex::new(&pattern).unwrap().find(&unwrapped) {
            let candidate = (m.start(), name);
            best = Some(match best {
                Some(b) if b <= candidate => b,
                _ => candidate,
            });
        }
    }
    best.map(|(_, name)| name.to_string())
}

fn starts_with_markup(title: &str) -> bool {
    let s = title.trim_start();
    let s = s
        .strip_prefix('{')
        .map(|rest| rest.trim_start())
        .unwrap_or(s);
    MARKUP_TITLE_RE.is_match(s)
}

fn check_refs_004_field(
    out: &mut Vec<Violation>,
    file: &str,
    entry: &Entry,
    field_name: &str,
    is_title: bool,
) {
    let value = field_value(entry, field_name);
    if value.is_empty() {
        return;
    }
    if let Some(lang) = title_mentions_unwrapped(&value, TERMS.languages.iter().map(String::as_str))
    {
        out.push(entry_violation(
            file,
            entry,
            "JSS-REFS-004",
            Some(format!(
                "Wrap {} in \\proglang{{{lang}}} in the {}.",
                py_repr(&lang),
                if is_title { "title" } else { "note field" }
            )),
        ));
        return;
    }
    if !is_title {
        return; // note-field scan only checks LANGUAGES, matching Python.
    }
    if let Some(pkg) = title_mentions_unwrapped(&value, TERMS.r_packages.iter().map(String::as_str))
    {
        out.push(entry_violation(
            file,
            entry,
            "JSS-REFS-004",
            Some(format!(
                "Wrap {} in \\pkg{{{pkg}}} in the title.",
                py_repr(&pkg)
            )),
        ));
        return;
    }
    if starts_with_markup(&value) {
        return;
    }
    let Some(caps) = TITLE_PACKAGE_PREFIX_RE.captures(&value) else {
        return;
    };
    let name = caps.get(1).unwrap().as_str();
    if TITLE_STOP_WORDS.contains(&name.to_lowercase().as_str()) {
        return;
    }
    if TERMS.languages.contains(name) {
        return;
    }
    out.push(entry_violation(
        file,
        entry,
        "JSS-REFS-004",
        Some(format!(
            "The leading identifier {} looks like a package name; wrap it in \\pkg{{{name}}} in the title.",
            py_repr(name)
        )),
    ));
}

/// JSS-REFS-004 — BibTeX titles/notes use JSS markup (`\proglang`,
/// `\pkg`) for language/package names.
pub fn check_refs_004(file: &str, library: &Library, tex_like: &[&[TexNode]]) -> Vec<Violation> {
    let mut out = Vec::new();
    for entry in referenced_entries(library, tex_like) {
        check_refs_004_field(&mut out, file, entry, "title", true);
    }
    for entry in referenced_entries(library, tex_like) {
        check_refs_004_field(&mut out, file, entry, "note", false);
    }
    out
}

// --- JSS-REFS-005 --------------------------------------------------------

/// JSS-REFS-005 — journal titles are not abbreviated.
pub fn check_refs_005(file: &str, library: &Library, tex_like: &[&[TexNode]]) -> Vec<Violation> {
    let mut out = Vec::new();
    for entry in referenced_entries(library, tex_like) {
        let journal = field_value(entry, "journal");
        if journal.is_empty() {
            continue;
        }
        let plain = strip_latex(&journal);
        let bareword_count = ABBREV_BAREWORD_RE.find_iter(&plain).count();
        if ABBREV_RE.is_match(&plain) || bareword_count >= 2 {
            out.push(entry_violation(
                file,
                entry,
                "JSS-REFS-005",
                Some("Expand the journal name (e.g., 'J. Stat. Softw.' \u{2192} 'Journal of Statistical Software').".to_string()),
            ));
        }
    }
    out
}

// --- JSS-REFS-006 --------------------------------------------------------

static PACKAGE_LIKE_TITLE_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"^\{*\s*\{?[a-z][a-zA-Z0-9._]*\}?\s*:").unwrap());
static AFTER_COLON_RE: LazyLock<Regex> = LazyLock::new(|| {
    RegexBuilder::new(r":\s*(.+)")
        .dot_matches_new_line(true)
        .build()
        .unwrap()
});
static AFTER_COLON_WORD_RE: LazyLock<Regex> = LazyLock::new(|| Regex::new(r":\s*(\S+)").unwrap());
static WS_SPLIT_RE: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"\s+").unwrap());
static PUNCT_TRIM_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"^[^A-Za-z]+|[^A-Za-z0-9]+$").unwrap());

static REFS006_STOP_WORDS: &[&str] = &[
    "a", "an", "the", "and", "or", "but", "nor", "for", "yet", "so", "if", "as", "at", "by", "in",
    "of", "on", "to", "up", "via", "vs", "with", "from", "into", "onto", "than", "per", "off",
    "about", "around", "et", "al", "is", "be", "do",
];

fn starts_with_package_idiom(title: &str) -> bool {
    PACKAGE_LIKE_TITLE_RE.is_match(title)
}

fn after_colon_starts_with_markup(title: &str) -> bool {
    let Some(caps) = AFTER_COLON_RE.captures(title) else {
        return false;
    };
    let rest = caps.get(1).unwrap().as_str().trim_start();
    let rest = rest
        .strip_prefix('{')
        .map(|r| r.trim_start())
        .unwrap_or(rest);
    MARKUP_TITLE_RE.is_match(rest)
}

fn visible_words_for_titlecase(title: &str) -> Vec<String> {
    WS_SPLIT_RE
        .split(title)
        .filter(|w| HAS_LETTER_RE.is_match(w))
        .map(str::to_string)
        .collect()
}

fn is_lowercase_principal(word: &str) -> bool {
    let stripped = PUNCT_TRIM_RE.replace_all(word, "");
    if stripped.is_empty() {
        return false;
    }
    if stripped != stripped.to_lowercase() {
        return false;
    }
    if stripped.chars().count() < 4 {
        return false;
    }
    if REFS006_STOP_WORDS.contains(&stripped.as_ref()) {
        return false;
    }
    if TERMS.r_packages.contains(stripped.as_ref()) {
        return false;
    }
    true
}

/// JSS-REFS-006 — loose title-case heuristic (first word, word after
/// `:`, and principal words all capitalised, modulo markup/stop-word/
/// package-idiom exemptions).
pub fn check_refs_006(file: &str, library: &Library, tex_like: &[&[TexNode]]) -> Vec<Violation> {
    let mut out = Vec::new();
    'entries: for entry in referenced_entries(library, tex_like) {
        let title = field_value(entry, "title");
        if title.is_empty() {
            continue;
        }
        let plain = strip_latex(&title);
        let words = visible_words(&plain);
        if words.is_empty() {
            continue;
        }
        if words.len() == 1 && words[0] == words[0].to_lowercase() {
            continue;
        }
        if !starts_with_markup(&title)
            && !starts_with_package_idiom(&title)
            && !word_is_uppercase_start(&words[0])
        {
            out.push(entry_violation(
                file,
                entry,
                "JSS-REFS-006",
                Some("Capitalize the first word of the title.".to_string()),
            ));
            continue;
        }
        if let Some(caps) = AFTER_COLON_WORD_RE.captures(&plain) {
            if !after_colon_starts_with_markup(&title) {
                let after = caps.get(1).unwrap().as_str();
                if !word_is_uppercase_start(after) {
                    out.push(entry_violation(
                        file,
                        entry,
                        "JSS-REFS-006",
                        Some("Capitalize the first word after ':' in the title.".to_string()),
                    ));
                    continue 'entries;
                }
            }
        }
        let prose_only = visible_words_for_titlecase(&strip_markup_content(&title));
        let offenders: Vec<&String> = prose_only
            .iter()
            .skip(1)
            .filter(|w| is_lowercase_principal(w))
            .collect();
        if !offenders.is_empty() {
            let sample = offenders
                .iter()
                .take(3)
                .map(|w| py_repr(w))
                .collect::<Vec<_>>()
                .join(", ");
            out.push(entry_violation(
                file,
                entry,
                "JSS-REFS-006",
                Some(format!(
                    "Capitalize the principal words in the title (found lowercase: {sample})."
                )),
            ));
        }
    }
    out
}

// --- JSS-REFS-007 --------------------------------------------------------

/// JSS-REFS-007 — journal titles are in title case.
pub fn check_refs_007(file: &str, library: &Library, tex_like: &[&[TexNode]]) -> Vec<Violation> {
    let mut out = Vec::new();
    for entry in referenced_entries(library, tex_like) {
        let journal = field_value(entry, "journal");
        if journal.is_empty() {
            continue;
        }
        let plain = strip_latex(&journal);
        if ABBREV_RE.is_match(&plain) {
            continue;
        }
        let words = visible_words(&plain);
        if words.is_empty() {
            continue;
        }
        for (idx, word) in words.iter().enumerate() {
            let low = NON_LETTER_RE.replace_all(word, "").to_lowercase();
            if idx > 0 && TITLE_STOPWORDS.contains(&low.as_str()) {
                continue;
            }
            if !word_is_uppercase_start(word) {
                out.push(entry_violation(
                    file,
                    entry,
                    "JSS-REFS-007",
                    Some("Capitalize the principal words of the journal title.".to_string()),
                ));
                break;
            }
        }
    }
    out
}
