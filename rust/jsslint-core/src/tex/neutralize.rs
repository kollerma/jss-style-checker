//! Length-preserving pre-tokenization neutralization — ports
//! `core/parser.py`'s three passes (`_neutralize_macro_definition_bodies`,
//! `_neutralize_verbatim_envs`, `_neutralize_verbatim_args`), applied in
//! that same order before tokenizing. All three only ever replace an
//! ASCII special character with another ASCII character of equal
//! codepoint count, so codepoint alignment (what every downstream
//! position depends on) is preserved automatically — no byte/codepoint
//! bookkeeping needed here beyond what `&str` already guarantees.
//!
//! `_neutralize_verbatim_envs`'s Python original uses a regex
//! backreference (`(?P=name)`) to find the *matching* `\end{name}` for
//! a given `\begin{name}` — `regex` (Rust) has no backreference support
//! (by design, for its linear-time guarantee), so this port does the
//! equivalent with a manual name-extract-then-literal-search instead of
//! one large alternation regex. Same behavior, different mechanism.

use super::prose::VERBATIM_ENVS;
use regex::Regex;
use std::sync::LazyLock;

/// `$` and `%` → `?`. Mirrors `parser.py::_TEX_SPECIAL_CHARS`.
fn neutralize_tex_special_chars(s: &str) -> String {
    s.chars()
        .map(|c| match c {
            '$' | '%' => '?',
            other => other,
        })
        .collect()
}

/// A `%` not immediately preceded by `\`. Mirrors the Python regex
/// `(?<!\\)%` exactly, INCLUDING its known simplification: a
/// doubly-escaped backslash (`\\%`, where the `%` is actually
/// unescaped in real TeX) is still treated as "escaped" here, because
/// the lookbehind only inspects one preceding character. Replicating a
/// known Python quirk on purpose — not a bug to fix independently.
fn has_unescaped_percent(s: &str) -> bool {
    let chars: Vec<char> = s.chars().collect();
    for i in 0..chars.len() {
        if chars[i] == '%' && (i == 0 || chars[i - 1] != '\\') {
            return true;
        }
    }
    false
}

/// Mirrors `core/parser.py::_neutralize_verbatim_envs`.
pub fn neutralize_verbatim_envs(src: &str) -> String {
    let mut out = String::with_capacity(src.len());
    let mut pos = 0usize;
    loop {
        let Some(rel) = src[pos..].find(r"\begin{") else {
            out.push_str(&src[pos..]);
            break;
        };
        let begin_start = pos + rel;
        let name_start = begin_start + r"\begin{".len();
        let Some(name_rel_end) = src[name_start..].find('}') else {
            out.push_str(&src[pos..]);
            break;
        };
        let name_end = name_start + name_rel_end;
        let name = &src[name_start..name_end];

        if !VERBATIM_ENVS.contains(&name) {
            out.push_str(&src[pos..=name_end]);
            pos = name_end + 1;
            continue;
        }

        let head_end = name_end + 1; // just past `\begin{name}`
        let end_marker = format!("\\end{{{name}}}");
        let Some(end_rel) = src[head_end..].find(end_marker.as_str()) else {
            out.push_str(&src[pos..]);
            break;
        };
        let tail_start = head_end + end_rel;
        let whole_end = tail_start + end_marker.len();

        let line_start = src[..begin_start].rfind('\n').map(|i| i + 1).unwrap_or(0);
        let commented = has_unescaped_percent(&src[line_start..begin_start]);

        out.push_str(&src[pos..begin_start]);
        if commented {
            out.push_str(&src[begin_start..whole_end]);
        } else {
            out.push_str(&src[begin_start..head_end]);
            out.push_str(&neutralize_tex_special_chars(&src[head_end..tail_start]));
            out.push_str(&src[tail_start..whole_end]);
        }
        pos = whole_end;
    }
    out
}

static VERBATIM_ARG_MACROS: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"\\(?:code|verb|url|email|fct|pkg|proglang)\{([^{}]*)\}").unwrap()
});

/// Mirrors `core/parser.py::_neutralize_verbatim_args`.
pub fn neutralize_verbatim_args(src: &str) -> String {
    let mut out = String::with_capacity(src.len());
    let mut last = 0usize;
    for caps in VERBATIM_ARG_MACROS.captures_iter(src) {
        let whole = caps.get(0).unwrap();
        let body = caps.get(1).unwrap();
        out.push_str(&src[last..whole.start()]);
        out.push_str(&src[whole.start()..body.start()]);
        out.push_str(&neutralize_tex_special_chars(body.as_str()));
        out.push_str(&src[body.end()..whole.end()]);
        last = whole.end();
    }
    out.push_str(&src[last..]);
    out
}

// --- macro-definition-body neutralization ----------------------------
//
// Ports `_neutralize_macro_definition_bodies`: inside the body
// group(s) of `\newcommand`/`\renewcommand`/`\providecommand`/`\def`/
// `\newenvironment`/`\renewenvironment`, any `\begin`/`\end` TOKEN
// (not the whole word — just the control sequence) is blanked to
// ` begin`/` end` so a definition like
// `\newenvironment{ex}{\begin{alltt}}{\end{alltt}}` (whose begin/end
// are legitimately unbalanced *per body*, both balancing only across
// the two separate body groups) doesn't break environment tracking.

static MACRO_DEF_HEAD: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"\\(?:(?P<env>(?:re)?newenvironment)|(?P<cmd>(?:re)?newcommand|providecommand)|(?P<def>def))\*?")
        .unwrap()
});

/// ASCII-whitespace only (space/tab/CR/LF) — a narrower check than
/// Python's `str.isspace()` (which the original `_skip_ws` uses and is
/// Unicode-aware). Deliberate simplification: this function indexes
/// raw UTF-8 bytes, and `byte as char` would misinterpret a non-ASCII
/// continuation byte as a Latin-1 codepoint (some of which — e.g.
/// 0xA0 NBSP — are themselves "whitespace", corrupting the scan).
/// Restricting to ASCII whitespace sidesteps that entirely; the
/// practical divergence is limited to a Unicode space character
/// appearing inside a macro's arg-count/default-value brackets, which
/// does not occur in the corpus.
fn skip_ws(chars: &[u8], mut i: usize) -> usize {
    while i < chars.len() && matches!(chars[i], b' ' | b'\t' | b'\r' | b'\n') {
        i += 1;
    }
    i
}

/// `chars[i]` must be `{`; returns the index one past the matching
/// `}` (honoring `\{`/`\}` escapes), or `None` if it never closes.
fn match_brace_group(s: &str, i: usize) -> Option<usize> {
    let bytes = s.as_bytes();
    let mut depth = 0i32;
    let mut j = i;
    let n = bytes.len();
    while j < n {
        match bytes[j] {
            b'\\' => j += 2,
            b'{' => {
                depth += 1;
                j += 1;
            }
            b'}' => {
                depth -= 1;
                j += 1;
                if depth == 0 {
                    return Some(j);
                }
            }
            _ => j += 1,
        }
    }
    None
}

/// `chars[i]` must be `[`; returns the index one past the matching
/// `]`, tolerating nested brace groups, or `None` if unclosed.
fn skip_bracket_group(s: &str, i: usize) -> Option<usize> {
    let bytes = s.as_bytes();
    let n = bytes.len();
    let mut j = i + 1;
    while j < n {
        match bytes[j] {
            b'\\' => j += 2,
            b'{' => j = match_brace_group(s, j)?,
            b']' => return Some(j + 1),
            _ => j += 1,
        }
    }
    None
}

/// One control sequence: `\` + (letters/@)+ or `\` + one other char.
/// Returns the index one past it, or `None` if `s[i]` isn't `\`.
fn match_control_seq(s: &str, i: usize) -> Option<usize> {
    let bytes = s.as_bytes();
    if i >= bytes.len() || bytes[i] != b'\\' {
        return None;
    }
    let mut j = i + 1;
    if j < bytes.len() && ((bytes[j] as char).is_ascii_alphabetic() || bytes[j] == b'@') {
        while j < bytes.len() && ((bytes[j] as char).is_ascii_alphabetic() || bytes[j] == b'@') {
            j += 1;
        }
        Some(j)
    } else if j < bytes.len() {
        Some(j + 1)
    } else {
        Some(j)
    }
}

/// Mirrors `core/parser.py::_neutralize_macro_definition_bodies`.
pub fn neutralize_macro_definition_bodies(src: &str) -> String {
    let mut out: Vec<u8> = src.as_bytes().to_vec();
    let n = out.len();
    let mut search_from = 0usize;

    while let Some(m) = MACRO_DEF_HEAD.find_at(src, search_from) {
        search_from = m.end();
        let mut i = skip_ws(src.as_bytes(), m.end());
        if i >= n {
            break;
        }

        let is_def = MACRO_DEF_HEAD
            .captures(&src[m.start()..m.end()])
            .and_then(|c| c.name("def"))
            .is_some();
        let is_env = MACRO_DEF_HEAD
            .captures(&src[m.start()..m.end()])
            .and_then(|c| c.name("env"))
            .is_some();

        // --- the defined name -------------------------------------
        if is_def {
            let Some(after_cs) = match_control_seq(src, i) else {
                continue;
            };
            i = after_cs;
            let Some(brace) = src[i..].find('{').map(|off| i + off) else {
                continue;
            };
            i = brace;
        } else if src.as_bytes()[i] == b'{' {
            let Some(after) = match_brace_group(src, i) else {
                continue;
            };
            i = after;
            i = skip_ws(src.as_bytes(), i);
            while i < n && src.as_bytes()[i] == b'[' {
                match skip_bracket_group(src, i) {
                    Some(after_bracket) => {
                        i = after_bracket;
                        i = skip_ws(src.as_bytes(), i);
                    }
                    None => break,
                }
            }
        } else {
            let Some(after_cs) = match_control_seq(src, i) else {
                continue;
            };
            i = after_cs;
            i = skip_ws(src.as_bytes(), i);
            while i < n && src.as_bytes()[i] == b'[' {
                match skip_bracket_group(src, i) {
                    Some(after_bracket) => {
                        i = after_bracket;
                        i = skip_ws(src.as_bytes(), i);
                    }
                    None => break,
                }
            }
        }

        // --- the body group(s) --------------------------------------
        let n_bodies = if is_env { 2 } else { 1 };
        for _ in 0..n_bodies {
            i = skip_ws(src.as_bytes(), i);
            if i >= n || src.as_bytes()[i] != b'{' {
                break;
            }
            let Some(end) = match_brace_group(src, i) else {
                break;
            };
            blank_begin_end_tokens(src, &mut out, i + 1, end - 1);
            i = end;
            search_from = i;
        }
    }

    String::from_utf8(out)
        .expect("neutralization only ever overwrites ASCII bytes with ASCII bytes")
}

/// Overwrites every `\begin`/`\end` control-word TOKEN (only the token
/// itself — `\begin` → ` begin`, i.e. the backslash becomes a space) in
/// `src[start..end]` with a space in `out`, in place. Mirrors
/// `_BEGIN_END_TOKEN = re.compile(r"\\(begin|end)(?=\s*\{)")` — ported
/// as a manual scan since the `regex` crate has no lookahead support.
fn blank_begin_end_tokens(src: &str, out: &mut [u8], start: usize, end: usize) {
    let bytes = src.as_bytes();
    let mut i = start;
    while i < end {
        if bytes[i] == b'\\' {
            for word in [&b"begin"[..], &b"end"[..]] {
                let word_end = i + 1 + word.len();
                if word_end <= end && &bytes[i + 1..word_end] == word {
                    let after_ws = skip_ws(bytes, word_end);
                    if after_ws < end && bytes[after_ws] == b'{' {
                        out[i] = b' ';
                        break;
                    }
                }
            }
        }
        i += 1;
    }
}

/// Full pre-tokenization pipeline, applied in the same order as
/// `core/parser.py::parse_tex_source`.
pub fn preprocess(src: &str) -> String {
    let src = neutralize_macro_definition_bodies(src);
    let src = neutralize_verbatim_envs(&src);
    neutralize_verbatim_args(&src)
}
