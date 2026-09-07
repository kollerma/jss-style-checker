//! Code-style rules — mirrors `journals/jss/rules/code_style.py`
//! (JSS-CODE-001/002/003).

use super::tex_common::{identifier, tex_violation_with_fix};
use crate::report::{Fix, FixConfidence, Violation};
use crate::tex::extract;
use crate::tex::node::{GroupNode, MacroNode, Node};
use crate::tex::prose::{walk, Slot, CODE_INPUT_ENVS};
use crate::tex::{position::LineIndex, ParsedTex};
use regex::Regex;
use std::sync::LazyLock;

static COMMENT_LINE_RE: LazyLock<Regex> = LazyLock::new(|| {
    // Python's `(?m)#+[^\S\n]+\S[^\n]*` — Rust: match per-line via
    // `(?m)` multi-line mode (`regex` crate supports it); `[^\S\n]`
    // (whitespace-but-not-newline) has no single-char Rust class, so
    // spell it as `[ \t\r\x0c\x0b]` (ASCII horizontal/vertical
    // whitespace minus `\n`, matching Python's `\s` minus `\n` for the
    // ASCII case this corpus uses).
    Regex::new(r"(?m)#+[ \t\r\x0c\x0b]+\S[^\n]*").unwrap()
});

static LIBRARY_UNQUOTED_RE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"\b(?:library|data|require|requireNamespace)\(\s*([A-Za-z][A-Za-z0-9_.]*)\s*[,)]")
        .unwrap()
});

static MISSING_SPACES_RE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(
        r"(?:[A-Za-z0-9_.)\]](?:<<-|<-|->|==|!=|<=|>=)[A-Za-z0-9_.(\[])|(?:[A-Za-z0-9_.)\]][=+\-*/][A-Za-z0-9_.(\[])|(?:,[A-Za-z0-9_.(\[])",
    )
    .unwrap()
});

static CODE_ENV_MISSING_COMMA_SPACE_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r#",[A-Za-z0-9_.(\["']"#).unwrap());
static CODE_ENV_COMMENT_RE: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"#[^\n]*").unwrap());
static CODE_ENV_STRING_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r#""[^"\n]*"|'[^'\n]*'"#).unwrap());
static CLEAN_R_IDENT_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"^[A-Za-z][A-Za-z0-9._]*$").unwrap());
static IDENTIFIER_ONLY_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"^[A-Za-z][A-Za-z0-9_.\-]*$").unwrap());
static VERSION_OR_LABEL_RE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"^(?:[0-9][\w.\-]*|[A-Za-z][\w.\-]*\s*\\?%[\w.\-\s\\]*)$").unwrap()
});
// Note: Python's `code_style.py` also defines `_KEYWORD_ARG_RE` at this
// point in the module but never references it anywhere else — dead
// code in the source being ported, not an oversight here. Omitted.
static PATH_LIKE_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"^[A-Za-z0-9_.\-]+(?:/[A-Za-z0-9_.\-]*)+/?$").unwrap());
// `\code{--fix}`, `\code{--fix --dry-run}`, `\code{.jss-lint.toml}`,
// `\code{cargo install jsslint-cli}` — command-line flags, dotfile
// names, and space-separated command words. A leading dash is option
// syntax and internal hyphens are part of the name, not subtraction;
// applied per whitespace-separated token so a real expression anywhere
// in the sample still trips the operator check.
static NAME_LIKE_TOKEN_RE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"^(?:--?|\.)?[A-Za-z][A-Za-z0-9_.\-]*$|^[A-Za-z0-9_.\-]+(?:/[A-Za-z0-9_.\-]*)+/?$")
        .unwrap()
});
static SCIENTIFIC_NOTATION_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"\b\d+(?:\.\d+)?[eE][-+]?\d+\b").unwrap());
static STRING_LITERAL_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r#""[^"\n]*"|'[^'\n]*'"#).unwrap());

const SINGLE_CHAR_ESCAPE_MACROS: &[&str] = &["%", "&", "_", "#", "$", "{", "}", "\\"];

const CODE_001_BASE: &str = "Move the comment into the surrounding LaTeX text";
static CODE_001_MARKER_RE: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"^#+\s*").unwrap());

const CODE_003_MACRO_BASE: &str =
    "Add spaces around operators and after commas in the code sample (e.g., 'y = a + b * x')";
const CODE_003_ENV_BASE: &str = "Add spaces around operators and after commas in the code sample \
                                 (e.g., 'f(x = 1, y = 2)' rather than 'f(x=1,y=2)')";
/// Characters of context quoted either side of the matched operator or
/// comma — mirrors `code_style._CODE_003_WINDOW`.
const CODE_003_WINDOW: usize = 8;

/// Quote the comment so two comments in one file are distinguishable
/// (spec 027 item S). `COMMENT_LINE_RE` requires a non-space character
/// after the marker, so the identifier is never empty.
fn code_001_suggestion(comment: &str) -> String {
    let text = identifier(&CODE_001_MARKER_RE.replace(comment, ""), 40);
    format!("{CODE_001_BASE}: '{text}'.")
}

/// Blank out `pattern` matches, preserving every *character* offset.
///
/// Mirrors `code_style._mask`. The scans run on masked text but the
/// quoted fragment must come from the source the author wrote, so the
/// two strings stay index-aligned by character. (Character, not byte:
/// the fragment is sliced by character index, exactly as Python slices
/// a `str`.)
fn mask(pattern: &Regex, text: &str, fill: char) -> String {
    pattern
        .replace_all(text, |caps: &regex::Captures| {
            fill.to_string().repeat(caps[0].chars().count())
        })
        .into_owned()
}

/// The offending fragment: the match plus `CODE_003_WINDOW` characters
/// either side, taken from the unmasked `text`. `start`/`end` are byte
/// offsets into `cleaned`, which `mask` keeps character-aligned with
/// `text`.
fn fragment(text: &str, cleaned: &str, start: usize, end: usize) -> String {
    let start_chars = cleaned[..start].chars().count();
    let end_chars = start_chars + cleaned[start..end].chars().count();
    let window: String = text
        .chars()
        .skip(start_chars.saturating_sub(CODE_003_WINDOW))
        .take(end_chars + CODE_003_WINDOW - start_chars.saturating_sub(CODE_003_WINDOW))
        .collect();
    identifier(&window, 40)
}

/// JSS-CODE-001 — code-display envs contain no `#`-style comments.
pub fn check_code_001(file: &str, parsed: &ParsedTex) -> Vec<Violation> {
    let line_index = LineIndex::with_offset(&parsed.chars, parsed.line_offset);
    let mut out = Vec::new();
    walk(&parsed.nodes, &mut |node, _ancestors| {
        let Node::Environment(env) = node else { return };
        if !CODE_INPUT_ENVS.contains(&env.environmentname.as_str()) {
            return;
        }
        for child in &env.nodelist {
            let Node::Chars(c) = child else { continue };
            let Some(m) = COMMENT_LINE_RE.find(&c.chars) else {
                continue;
            };
            let abs_pos = c.span.pos + c.chars[..m.start()].chars().count();
            out.push(tex_violation_with_fix(
                file,
                &line_index,
                abs_pos,
                "JSS-CODE-001",
                Some(code_001_suggestion(m.as_str())),
                None,
            ));
            break; // one violation per code block is enough
        }
    });
    out
}

/// JSS-CODE-002 — `library()`/`data()`/`require()`/`requireNamespace()`
/// quote their first argument.
pub fn check_code_002(file: &str, parsed: &ParsedTex) -> Vec<Violation> {
    let line_index = LineIndex::with_offset(&parsed.chars, parsed.line_offset);
    let mut out = Vec::new();
    walk(&parsed.nodes, &mut |node, _ancestors| {
        let Node::Environment(env) = node else { return };
        if !CODE_INPUT_ENVS.contains(&env.environmentname.as_str()) {
            return;
        }
        for child in &env.nodelist {
            let Node::Chars(c) = child else { continue };
            for m in LIBRARY_UNQUOTED_RE.captures_iter(&c.chars) {
                let whole = m.get(0).unwrap();
                let arg = m.get(1).unwrap();
                let abs_pos = c.span.pos + c.chars[..whole.start()].chars().count();
                let bareword = arg.as_str();
                // Python's `.replace()` (no count) replaces every
                // occurrence, not just the first — match that exactly
                // rather than assume `bareword` appears once.
                let quoted = whole.as_str().replace(bareword, &format!("\"{bareword}\""));
                let suggestion = format!("Quote the argument: e.g., {}.", super::py_repr(&quoted));
                let fix = if CLEAN_R_IDENT_RE.is_match(bareword) {
                    let bareword_start = c.span.pos + c.chars[..arg.start()].chars().count();
                    let bareword_end = c.span.pos + c.chars[..arg.end()].chars().count();
                    Some(Fix {
                        start: bareword_start,
                        end: bareword_end,
                        replacement: format!("\"{bareword}\""),
                        description: "quote first argument to library() / data()".to_string(),
                        confidence: FixConfidence::Safe,
                    })
                } else {
                    None
                };
                out.push(tex_violation_with_fix(
                    file,
                    &line_index,
                    abs_pos,
                    "JSS-CODE-002",
                    Some(suggestion),
                    fix,
                ));
            }
        }
    });
    out
}

/// JSS-CODE-003 — code samples use spaces around operators and after
/// commas, checked both inside code-display envs and `\code{...}`.
pub fn check_code_003(file: &str, parsed: &ParsedTex) -> Vec<Violation> {
    let line_index = LineIndex::with_offset(&parsed.chars, parsed.line_offset);
    let mut out = Vec::new();

    walk(&parsed.nodes, &mut |node, _ancestors| {
        let Node::Environment(env) = node else { return };
        if !CODE_INPUT_ENVS.contains(&env.environmentname.as_str()) {
            return;
        }
        if let Some(v) = scan_code_env_for_spacing(file, &line_index, env) {
            out.push(v);
        }
    });

    extract::iter_with_parent_visit(&parsed.nodes, &mut |parent: &[Slot], idx, node| {
        let Node::Macro(m) = node else { return };
        if m.macroname != "code" {
            return;
        }
        let Some(group) = first_group_arg(m, parent, idx) else {
            return;
        };
        let text = group_plain_text(group);
        if text.is_empty() {
            return;
        }
        let stripped = text.trim();
        if IDENTIFIER_ONLY_RE.is_match(stripped)
            || VERSION_OR_LABEL_RE.is_match(stripped)
            || PATH_LIKE_RE.is_match(stripped)
        {
            return;
        }
        // Command line made of flag / name / path tokens only.
        if !stripped.is_empty()
            && stripped
                .split_whitespace()
                .all(|t| NAME_LIKE_TOKEN_RE.is_match(t))
        {
            return;
        }
        let cleaned = mask(&SCIENTIFIC_NOTATION_RE, &text, ' ');
        let cleaned = mask(&STRING_LITERAL_RE, &cleaned, 'S');
        if let Some(hit) = MISSING_SPACES_RE.find(&cleaned) {
            out.push(tex_violation_with_fix(
                file,
                &line_index,
                m.span.pos,
                "JSS-CODE-003",
                Some(format!(
                    "{CODE_003_MACRO_BASE}: '{}'.",
                    fragment(&text, &cleaned, hit.start(), hit.end())
                )),
                None,
            ));
        }
    });

    out
}

fn scan_code_env_for_spacing(
    file: &str,
    line_index: &LineIndex,
    env: &crate::tex::node::EnvironmentNode,
) -> Option<Violation> {
    for child in &env.nodelist {
        let Node::Chars(c) = child else { continue };
        let cleaned = mask(&CODE_ENV_COMMENT_RE, &c.chars, ' ');
        let cleaned = mask(&SCIENTIFIC_NOTATION_RE, &cleaned, ' ');
        let cleaned = mask(&CODE_ENV_STRING_RE, &cleaned, 'S');
        let hit = CODE_ENV_MISSING_COMMA_SPACE_RE
            .find(&cleaned)
            .or_else(|| MISSING_SPACES_RE.find(&cleaned));
        if let Some(hit) = hit {
            return Some(tex_violation_with_fix(
                file,
                line_index,
                env.span.pos,
                "JSS-CODE-003",
                Some(format!(
                    "{CODE_003_ENV_BASE}: '{}'.",
                    fragment(&c.chars, &cleaned, hit.start(), hit.end())
                )),
                None,
            ));
        }
    }
    None
}

fn first_group_arg<'a>(
    macro_node: &'a MacroNode,
    parent: &[Slot<'a>],
    idx: usize,
) -> Option<&'a GroupNode> {
    for arg in &macro_node.args {
        if let Some(Node::Group(g)) = arg {
            return Some(g);
        }
    }
    extract::next_group_arg(parent, idx)
}

/// Mirrors `code_style.py::_group_plain_text` — reconstructs
/// `\code{...}` content preserving LaTeX special escapes, including
/// the `\?`-is-really-`\%` remap left by `neutralize::verbatim_args`
/// (see that function's doc comment).
fn group_plain_text(group: &GroupNode) -> String {
    let mut out = String::new();
    for child in &group.nodelist {
        match child {
            Node::Chars(c) => out.push_str(&c.chars),
            Node::Specials(s) => out.push_str(&s.chars),
            Node::Macro(m) if SINGLE_CHAR_ESCAPE_MACROS.contains(&m.macroname.as_str()) => {
                out.push_str(&m.macroname);
            }
            Node::Macro(m) if m.macroname == "?" => out.push('%'),
            _ => {}
        }
    }
    out.trim().to_string()
}
