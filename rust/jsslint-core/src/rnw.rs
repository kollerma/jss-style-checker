//! `.Rnw` (Sweave/knitr) chunk preprocessing — ports
//! `core/parser.py`'s `wrap_rnw_chunks_as_sinput` and its helpers
//! (`_global_chunk_defaults`, `_chunk_is_hidden`) exactly. Rewrites R
//! code chunks (`<<...>>=` ... `@`) into `\begin{Sinput}` /
//! `\end{Sinput}` envelopes in place (newline-count preserving) so the
//! rewritten source can be fed, unchanged, through the existing
//! `tex::parse_tex_source` pipeline — no changes needed there.
//!
//! See `src/texlint/core/parser.py` lines ~52-336 for the detailed
//! edge-case rationale (CRLF tolerance, indented/trailing-whitespace
//! chunk headers, `>` inside chunk option strings, `echo=FALSE` /
//! `include=FALSE` hidden chunks, global `\SweaveOpts` /
//! `opts_chunk$set` defaults, bare-`@` terminators with trailing text)
//! — replicated verbatim here, not reinvented. `_HIDDEN_CHUNK_OPT` from
//! the Python source is deliberately not ported: it's declared there
//! but never referenced (dead code), confirmed by grep.

use regex::{Captures, Regex};
use std::sync::LazyLock;

static RNW_CHUNK: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"(?ms)^[ \t]*<<[^\n]*?>>=[ \t]*\r?\n.*?^[ \t]*@(?:[ \t][^\n]*)?\r?$").unwrap()
});

static RNW_SEXPR: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"\\Sexpr\{[^{}]*\}").unwrap());

static GLOBAL_OPTS_BLOCK: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"(?:\\SweaveOpts\s*\{|opts_chunk\$set\s*\()([^)}]*)").unwrap());

static OPT_ECHO: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"\becho\s*=\s*(\w+)").unwrap());
static OPT_INCLUDE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"\binclude\s*=\s*(\w+)").unwrap());

fn is_falsey(s: &str) -> bool {
    s == "FALSE" || s == "F"
}

fn is_truthy(s: &str) -> bool {
    s == "TRUE" || s == "T"
}

/// Mirrors `parser.py::_global_chunk_defaults`: textually-last value
/// wins per option across every `\SweaveOpts{...}` /
/// `opts_chunk$set(...)` block in the document.
fn global_chunk_defaults(src: &str) -> (bool, bool) {
    let mut echo_hidden = false;
    let mut include_hidden = false;
    for caps in GLOBAL_OPTS_BLOCK.captures_iter(src) {
        let block = caps.get(1).unwrap().as_str();
        if let Some(e) = OPT_ECHO.captures(block) {
            let val = e.get(1).unwrap().as_str();
            if is_falsey(val) {
                echo_hidden = true;
            } else if is_truthy(val) {
                echo_hidden = false;
            }
        }
        if let Some(i) = OPT_INCLUDE.captures(block) {
            let val = i.get(1).unwrap().as_str();
            if is_falsey(val) {
                include_hidden = true;
            } else if is_truthy(val) {
                include_hidden = false;
            }
        }
    }
    (echo_hidden, include_hidden)
}

fn effective(opt_re: &Regex, header: &str, default_hidden: bool) -> bool {
    match opt_re.captures(header) {
        Some(caps) => is_falsey(caps.get(1).unwrap().as_str()),
        None => default_hidden,
    }
}

/// Mirrors `parser.py::_chunk_is_hidden`.
fn chunk_is_hidden(header: &str, echo_default_hidden: bool, include_default_hidden: bool) -> bool {
    effective(&OPT_ECHO, header, echo_default_hidden)
        || effective(&OPT_INCLUDE, header, include_default_hidden)
}

/// `{`, `}`, `\` -> space; length-preserving (newlines untouched).
/// Mirrors `parser.py::_CHUNK_BODY_NEUTRALIZE`.
fn neutralize_chunk_body(body: &str) -> String {
    body.chars()
        .map(|c| match c {
            '{' | '}' | '\\' => ' ',
            other => other,
        })
        .collect()
}

/// Every non-newline char -> space, newlines preserved. Mirrors the
/// `_blank_inline` closures in `parser.py` (shared shape between
/// `wrap_rnw_chunks_as_sinput` and `strip_rnw_chunks`).
fn blank_preserving_newlines(s: &str) -> String {
    s.chars()
        .map(|c| if c == '\n' { '\n' } else { ' ' })
        .collect()
}

fn rewrite_chunk(whole: &str, echo_default_hidden: bool, include_default_hidden: bool) -> String {
    let Some(nl) = whole.find('\n') else {
        return whole.to_string();
    };
    let header = &whole[..nl];
    if chunk_is_hidden(header, echo_default_hidden, include_default_hidden) {
        // Blank to whitespace, preserving line count exactly as
        // `strip_rnw_chunks` would — no other content survives.
        return "\n".repeat(whole.matches('\n').count());
    }
    // Strip a trailing CR from the header (if CRLF) so we re-emit a
    // clean line ending on the synthesized `\begin{Sinput}` line.
    let header_nl = if header.ends_with('\r') { "\r\n" } else { "\n" };
    let rest = &whole[nl + 1..];
    let Some(last_nl) = rest.rfind('\n') else {
        // Shouldn't happen given the regex shape, but bail safely.
        return whole.to_string();
    };
    let body = &rest[..last_nl + 1]; // keeps the trailing newline
    let body_safe = neutralize_chunk_body(body);
    format!("\\begin{{Sinput}}{header_nl}{body_safe}\\end{{Sinput}}")
}

/// Mirrors `parser.py::wrap_rnw_chunks_as_sinput`. Rewrite Sweave /
/// knitr R code chunks to `\begin{Sinput}` / `\end{Sinput}` envelopes
/// (so CODE-* / WIDTH-001 rules, which already target Sinput-class
/// envs, lint chunk content while prose rules continue to skip it) and
/// blank inline `\Sexpr{...}` calls. Line numbers stay
/// source-authoritative in the rewritten string.
pub fn wrap_rnw_chunks_as_sinput(src: &str) -> String {
    let (echo_default_hidden, include_default_hidden) = global_chunk_defaults(src);

    let rewritten = RNW_CHUNK.replace_all(src, |caps: &Captures| -> String {
        rewrite_chunk(
            caps.get(0).unwrap().as_str(),
            echo_default_hidden,
            include_default_hidden,
        )
    });

    RNW_SEXPR
        .replace_all(&rewritten, |caps: &Captures| -> String {
            blank_preserving_newlines(caps.get(0).unwrap().as_str())
        })
        .into_owned()
}
