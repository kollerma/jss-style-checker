//! `.Rmd` (R Markdown) parsing — ports `core/rmd_parser.py`'s hand-rolled
//! line-based tokenizer exactly: `START -> FRONTMATTER -> BODY -> FENCE`
//! state machine splitting the file into YAML frontmatter, headings,
//! prose blocks, and fenced code blocks. Each prose block is scrubbed
//! (HTML comments, URLs, inline R/code spans, bold/italic emphasis ->
//! blanked to equivalent-length whitespace) and then parsed as a
//! raw-LaTeX fragment via the *unmodified* `tex::parse_tex_source`.
//!
//! Line-offset: mirrors Python's `_OffsetWalker`, which adds
//! `prose.line - 1` to every line `pos_to_lineno_colno` reports while
//! leaving `node.pos` itself fragment-local (untouched). Each fragment
//! is parsed from its OWN unpadded text — `chars`/`node.pos` positions
//! stay 0-based within that fragment, exactly like Python — and
//! `LineIndex::with_offset` bakes the `prose.line - 1` shift into line
//! lookups only. This matters beyond line/column display: SARIF's
//! `byteOffset` renders `Fix::start` directly (unlike JSON, which
//! hardcodes `fix: null`), so a fragment-local raw offset has to match
//! Python's fragment-local `node.pos` for that field to byte-match too
//! — an earlier version of this module prepended blank lines instead
//! (shifting `node.pos` along with the reported line), which broke
//! exactly this.

use crate::engine::{ParsedRmdFileDoc, ParsedTexFileDoc};
use crate::report::{Severity, Violation};
use crate::tex::{self, position::LineIndex};
use regex::{Captures, Regex};
use std::sync::LazyLock;

const PARSE_RULE_ID: &str = "JSS-PARSE-000";

static FENCE_OPEN: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"^\s*```\s*(?:\{[^}]*\}|[A-Za-z0-9_.+-]+)?\s*$").unwrap());
static FENCE_CLOSE: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"^\s*```\s*$").unwrap());
static HEADING: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"^#{1,6}\s+.+$").unwrap());

static INLINE_R: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"`r\s[^`]*`").unwrap());
static BOLD_SPAN: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"\*\*([^*\n]+)\*\*").unwrap());
static HTML_COMMENT: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"(?s)<!--.*?-->").unwrap());
static AUTOLINK_URL: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"<https?://[^>\s]+>").unwrap());
static LINK_URL: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"\]\([^)\s]+\)").unwrap());
static BARE_URL: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"https?://[^\s]+").unwrap());

// knitr's `!r expr()` YAML tag, only after a mapping colon (the only
// realistic position it appears in real vignette frontmatter) — dropped
// before validation so a stock YAML parser doesn't choke on the unknown
// tag, matching `_KnitrYamlLoader`'s tolerance. Mirrors
// `rmd_parser.py::_KnitrYamlLoader`/`_knitr_r_tag_constructor`.
static KNITR_R_TAG: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"(:\s*)!r(\s+)").unwrap());

fn is_word_char(c: char) -> bool {
    c.is_alphanumeric() || c == '_'
}

/// Every char in `s` -> space, except `\n` which is preserved. Mirrors
/// the `_blank_match`/`_blank_inline` closures in `rmd_parser.py`.
fn blank_preserving_newlines(s: &str) -> String {
    s.chars()
        .map(|c| if c == '\n' { '\n' } else { ' ' })
        .collect()
}

/// Mirrors `_INLINE_CODE = re.compile(r"(?<!`)`([^`\n]+)`(?!`)")` — the
/// `regex` crate has no lookaround, so this is a manual scan for a
/// single backtick span not adjacent to another backtick (i.e., not
/// part of a double-backtick span).
fn strip_inline_code(text: &str) -> String {
    let chars: Vec<char> = text.chars().collect();
    let n = chars.len();
    let mut mask = vec![false; n];
    let mut i = 0;
    while i < n {
        if chars[i] == '`' && !(i > 0 && chars[i - 1] == '`') {
            let mut j = i + 1;
            while j < n && chars[j] != '`' && chars[j] != '\n' {
                j += 1;
            }
            if j < n && chars[j] == '`' && j > i + 1 && !(j + 1 < n && chars[j + 1] == '`') {
                for slot in mask.iter_mut().take(j + 1).skip(i) {
                    *slot = true;
                }
                i = j + 1;
                continue;
            }
        }
        i += 1;
    }
    chars
        .iter()
        .zip(mask.iter())
        .map(|(&c, &m)| if m && c != '\n' { ' ' } else { c })
        .collect()
}

/// Mirrors `_ITALIC_SPAN = re.compile(r"(?<![*\w])\*([^*\n]+)\*(?!\w)")`
/// — manual scan for the same lookaround reason as `strip_inline_code`.
/// Must run after `BOLD_SPAN` blanking so `**bold**` asterisks are
/// already gone (matches Python's `_scrub_prose` ordering).
fn strip_italic_spans(text: &str) -> String {
    let chars: Vec<char> = text.chars().collect();
    let n = chars.len();
    let mut mask = vec![false; n];
    let mut i = 0;
    while i < n {
        if chars[i] == '*' {
            let prev_ok = i == 0 || !(chars[i - 1] == '*' || is_word_char(chars[i - 1]));
            if prev_ok {
                let mut j = i + 1;
                while j < n && chars[j] != '*' && chars[j] != '\n' {
                    j += 1;
                }
                if j < n && chars[j] == '*' && j > i + 1 {
                    let next_ok = j + 1 >= n || !is_word_char(chars[j + 1]);
                    if next_ok {
                        for slot in mask.iter_mut().take(j + 1).skip(i) {
                            *slot = true;
                        }
                        i = j + 1;
                        continue;
                    }
                }
            }
        }
        i += 1;
    }
    chars
        .iter()
        .zip(mask.iter())
        .map(|(&c, &m)| if m && c != '\n' { ' ' } else { c })
        .collect()
}

fn regex_blank(re: &Regex, text: &str) -> String {
    re.replace_all(text, |caps: &Captures| -> String {
        blank_preserving_newlines(caps.get(0).unwrap().as_str())
    })
    .into_owned()
}

/// Mirrors `rmd_parser.py::_scrub_prose` — same regex chain, same order.
fn scrub_prose(text: &str) -> String {
    let text = regex_blank(&HTML_COMMENT, text);
    let text = regex_blank(&AUTOLINK_URL, &text);
    let text = regex_blank(&LINK_URL, &text);
    let text = regex_blank(&BARE_URL, &text);
    let text = regex_blank(&INLINE_R, &text);
    let text = strip_inline_code(&text);
    let text = regex_blank(&BOLD_SPAN, &text);
    strip_italic_spans(&text)
}

fn parse_violation(path: &str, line: usize, severity: Severity, message: String) -> Violation {
    Violation {
        file: path.to_string(),
        line: line as u32,
        column: None,
        rule_id: PARSE_RULE_ID.to_string(),
        severity,
        message,
        suggestion: None,
        fix: None,
    }
}

/// `Ok(())` when `text` is empty/whitespace (Python: `{}` without
/// invoking the YAML loader) or parses as valid YAML — a
/// valid-but-non-mapping document is NOT an error either (mirrors
/// `frontmatter = loaded if isinstance(loaded, dict) else {}`, which
/// silently discards a non-dict result with no warning). `Err(message)`
/// only on an actual parse failure. The message text is this crate's
/// own YAML parser's, NOT PyYAML's — a deliberately scoped parity
/// exception (see the plan): PyYAML's exception text includes internal
/// scanner state that no other YAML implementation reproduces.
fn validate_yaml_frontmatter(text: &str) -> Result<(), String> {
    if text.trim().is_empty() {
        return Ok(());
    }
    let sanitized = KNITR_R_TAG.replace_all(text, "$1$2");
    match serde_yaml::from_str::<serde_yaml::Value>(&sanitized) {
        Ok(_) => Ok(()),
        Err(e) => Err(e.to_string()),
    }
}

struct ProseBlock<'a> {
    text: &'a str,
    line: usize,
}

fn is_line_boundary(c: char) -> bool {
    matches!(
        c,
        '\n' | '\r'
            | '\u{0b}'
            | '\u{0c}'
            | '\u{1c}'
            | '\u{1d}'
            | '\u{1e}'
            | '\u{85}'
            | '\u{2028}'
            | '\u{2029}'
    )
}

/// Mirrors Python's `str.splitlines()`, which the real tokenizer uses
/// (`lines = src.splitlines()`) — a broader boundary set than Rust's
/// `str::lines()` (`\n`/`\r\n` only): `\v`, `\f`, `\x1c`-`\x1e`, NEL
/// (`\x85`), LINE/PARAGRAPH SEPARATOR (`\u{2028}`/`\u{2029}`) all count
/// too. Confirmed load-bearing against a real CRAN vignette
/// (`extremefit`) that ships a stray `\v` inside a YAML frontmatter
/// value — Python's tokenizer treats it as a line break, shifting
/// every subsequent line number by one; matching `str::lines()` here
/// would desync every violation after it. `\r\n` is one boundary, not
/// two.
fn python_splitlines(src: &str) -> Vec<&str> {
    let mut out = Vec::new();
    let mut start = 0usize;
    let mut iter = src.char_indices().peekable();
    while let Some((pos, c)) = iter.next() {
        if is_line_boundary(c) {
            out.push(&src[start..pos]);
            let mut end = pos + c.len_utf8();
            if c == '\r' {
                if let Some(&(npos, '\n')) = iter.peek() {
                    end = npos + 1;
                    iter.next();
                }
            }
            start = end;
        }
    }
    if start < src.len() {
        out.push(&src[start..]);
    }
    out
}

/// Mirrors `rmd_parser.py::parse_rmd_source`'s tokenizer + fragment
/// construction. `path` is used verbatim as `Violation::file` and every
/// fragment's path (no filesystem I/O here).
pub fn parse_rmd_source(path: &str, src: &str) -> ParsedRmdFileDoc {
    let lines: Vec<&str> = python_splitlines(src);
    let n_lines = lines.len();

    let mut violations: Vec<Violation> = Vec::new();
    let mut prose_owned: Vec<(String, usize)> = Vec::new(); // (joined text, start_line)

    #[derive(PartialEq, Eq)]
    enum State {
        Start,
        Frontmatter,
        Body,
        Fence,
    }
    let mut state = State::Start;

    let mut fm_start_line = 0usize;
    let mut fm_lines: Vec<&str> = Vec::new();
    let mut fence_open_line = 0usize;
    let mut prose_buffer: Vec<&str> = Vec::new();
    let mut prose_start_line = 0usize;

    fn flush_prose(buffer: &mut Vec<&str>, start_line: usize, out: &mut Vec<(String, usize)>) {
        if !buffer.is_empty() {
            out.push((buffer.join("\n"), start_line));
            buffer.clear();
        }
    }

    let mut i = 0usize;
    while i < n_lines {
        let line = lines[i];
        let line_no = i + 1;

        match state {
            State::Start => {
                if line.trim() == "---" {
                    state = State::Frontmatter;
                    fm_lines.clear();
                    fm_start_line = line_no;
                } else {
                    state = State::Body;
                    continue; // reprocess this line in BODY
                }
            }
            State::Frontmatter => {
                if line.trim() == "---" {
                    let text = fm_lines.join("\n");
                    if let Err(msg) = validate_yaml_frontmatter(&text) {
                        violations.push(parse_violation(
                            path,
                            fm_start_line,
                            Severity::Warning,
                            format!("Malformed YAML frontmatter (ignored): {msg}"),
                        ));
                    }
                    state = State::Body;
                } else {
                    fm_lines.push(line);
                }
            }
            State::Body => {
                if FENCE_OPEN.is_match(line) {
                    flush_prose(&mut prose_buffer, prose_start_line, &mut prose_owned);
                    fence_open_line = line_no;
                    state = State::Fence;
                } else if HEADING.is_match(line) || line.trim().is_empty() {
                    flush_prose(&mut prose_buffer, prose_start_line, &mut prose_owned);
                } else {
                    if prose_buffer.is_empty() {
                        prose_start_line = line_no;
                    }
                    prose_buffer.push(line);
                }
            }
            State::Fence => {
                if FENCE_CLOSE.is_match(line) {
                    state = State::Body;
                }
            }
        }
        i += 1;
    }

    match state {
        State::Frontmatter => {
            violations.push(parse_violation(
                path,
                fm_start_line,
                Severity::Error,
                "Unterminated YAML frontmatter.".to_string(),
            ));
        }
        State::Fence => {
            violations.push(parse_violation(
                path,
                fence_open_line,
                Severity::Error,
                "Unterminated fenced code block.".to_string(),
            ));
        }
        _ => {
            flush_prose(&mut prose_buffer, prose_start_line, &mut prose_owned);
        }
    }

    let scrubbed: Vec<ProseBlock> = prose_owned
        .iter()
        .map(|(text, line)| ProseBlock {
            text: text.as_str(),
            line: *line,
        })
        .collect();

    let mut latex_fragments: Vec<ParsedTexFileDoc> = Vec::new();
    for block in &scrubbed {
        let scrubbed_text = scrub_prose(block.text);
        if scrubbed_text.trim().is_empty() {
            continue;
        }
        let mut parsed = tex::parse_tex_source(&scrubbed_text);
        parsed.line_offset = (block.line - 1) as u32;
        let line_index = LineIndex::with_offset(&parsed.chars, parsed.line_offset);
        latex_fragments.push(ParsedTexFileDoc {
            path: path.to_string(),
            parsed,
            line_index,
        });
    }

    ParsedRmdFileDoc {
        path: path.to_string(),
        latex_fragments,
        violations,
    }
}
