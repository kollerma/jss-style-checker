//! BibTeX parser — a from-scratch tolerant parser tuned to match
//! `bibtexparser` v2's observed behavior (empirically verified, same
//! methodology as `tex::parser`), not a general BibTeX grammar
//! implementation.
//!
//! Empirically-verified rules this parser encodes:
//!
//! 1. Anything outside an `@...{...}` block is a comment (ignored),
//!    including partial-line text before the first `@`.
//! 2. `@string{name = value}` defines a macro; a later BARE-token field
//!    value (no `{}`/`""` delimiters) matching a defined name resolves
//!    to that string's value. `@comment{...}`/`@preamble{...}` blocks
//!    are skipped entirely (their balanced-brace body is consumed but
//!    not otherwise interpreted).
//! 3. Field values may be `{...}` (nested-brace-balanced), `"..."`
//!    (no nesting; a literal `\"` inside unescapes to `"`), or a bare
//!    token (word/number, or an `@string` name) — parts joined by `#`
//!    concatenate with no separator. The assembled value has
//!    leading/trailing whitespace stripped (verified: `bibtexparser`
//!    does this too — see `naming.py::_field_value_span`'s comment).
//! 4. **Key uniqueness policy mirrors `core/parser.py::parse_bib_source`,
//!    NOT raw `bibtexparser`**: the first entry for a given key goes to
//!    `Library::entries`; a later entry reusing that key goes ONLY to
//!    `Library::duplicate_block_keys` (never re-added to `entries`,
//!    matching the Python comment "bibtexparser kept the first
//!    occurrence... we must not double-flag them as parse errors").
//! 5. **Duplicate-field-within-an-entry policy also mirrors
//!    `parse_bib_source`, not raw `bibtexparser`**: last value wins per
//!    field, the entry is recorded in `duplicate_field_keys` for
//!    BIBTEX-005 to report, AND (unlike a duplicate key) the recovered
//!    entry IS added to `Library::entries` too, so every other rule
//!    still lints it — Python re-inserts it explicitly via
//!    `RemoveEnclosingMiddleware` + `library.add(entry)` specifically
//!    so a single internal-duplicate-field typo doesn't blind every
//!    other bib rule to that entry.
//!
//! Known, deliberate gaps: no `crossref` inheritance, no `@string`
//! forward-reference validation (an undefined bare token is kept
//! literally, same fallback `bibtexparser` uses), no attempt at
//! `bibtexparser`'s full failed-block taxonomy — only the two variants
//! (`DuplicateBlockKeyBlock`, `DuplicateFieldKeyBlock`) the 13 bib
//! rules actually consume are modeled.

use super::model::{DuplicateBlockKey, DuplicateFieldKey, Entry, Field, Library, StringTable};
use std::collections::HashSet;

pub fn parse(source: &str) -> Library {
    let chars: Vec<char> = source.chars().collect();
    let parser = Parser { chars: &chars };
    parser.run()
}

struct Parser<'a> {
    chars: &'a [char],
}

impl<'a> Parser<'a> {
    fn len(&self) -> usize {
        self.chars.len()
    }

    fn run(&self) -> Library {
        let mut library = Library::default();
        let mut strings: StringTable = StringTable::new();
        let mut seen_keys: HashSet<String> = HashSet::new();
        let n = self.len();
        let mut pos = 0usize;

        while pos < n {
            let Some(at) = self.find_from(pos, '@') else {
                break;
            };
            let (directive_type, after_type) = self.read_word(at + 1);
            let open = self.skip_ws(after_type);
            let Some((open_delim, close_delim)) = self.opener_at(open) else {
                pos = at + 1;
                continue;
            };
            let block_start = open + 1;
            let Some(block_end) = self.find_matching_brace(block_start, close_delim) else {
                // Unclosed block: nothing more to parse.
                break;
            };

            let type_lower = directive_type.to_ascii_lowercase();
            match type_lower.as_str() {
                "string" => self.parse_string_directive(block_start, block_end, &mut strings),
                "comment" | "preamble" => {} // body intentionally ignored
                _ => {
                    let entry =
                        self.parse_entry_body(directive_type, at, block_start, block_end, &strings);
                    self.commit_entry(entry, &mut library, &mut seen_keys);
                }
            }

            pos = block_end + 1;
            let _ = open_delim;
        }

        library
    }

    fn commit_entry(
        &self,
        entry: EntryParse,
        library: &mut Library,
        seen_keys: &mut HashSet<String>,
    ) {
        let key_taken = !entry.entry.key.is_empty() && !seen_keys.insert(entry.entry.key.clone());
        if key_taken {
            library.duplicate_block_keys.push(DuplicateBlockKey {
                key: entry.entry.key.clone(),
                start_line: entry.entry.start_line,
                entry: entry.entry,
            });
            return;
        }
        if !entry.duplicate_field_names.is_empty() {
            library.duplicate_field_keys.push(DuplicateFieldKey {
                start_line: entry.entry.start_line,
                duplicate_keys: entry.duplicate_field_names.clone(),
                entry: entry.entry.clone(),
            });
        }
        library.entries.push(entry.entry);
    }

    fn parse_string_directive(&self, start: usize, end: usize, strings: &mut StringTable) {
        let mut pos = self.skip_ws(start);
        let (name, after_name) = self.read_ident(pos);
        if name.is_empty() {
            return;
        }
        pos = self.skip_ws(after_name);
        if pos >= end || self.chars[pos] != '=' {
            return;
        }
        pos = self.skip_ws(pos + 1);
        let (value, _next) = self.parse_value(pos, end, strings);
        strings.insert(name.to_ascii_lowercase(), value);
    }

    fn parse_entry_body(
        &self,
        entry_type: String,
        at_pos: usize,
        start: usize,
        end: usize,
        strings: &StringTable,
    ) -> EntryParse {
        let line_index = self.line_index_of(at_pos);
        let mut pos = self.skip_ws(start);
        let (key, after_key) = self.read_key(pos, end);
        pos = self.skip_ws_or_comma(after_key, end);

        let mut fields: Vec<Field> = Vec::new();
        let mut seen_field_names: HashSet<String> = HashSet::new();
        let mut duplicate_field_names: Vec<String> = Vec::new();

        while pos < end {
            let (field_name, after_name) = self.read_ident(pos);
            if field_name.is_empty() {
                break;
            }
            pos = self.skip_ws(after_name);
            if pos >= end || self.chars[pos] != '=' {
                break;
            }
            pos = self.skip_ws(pos + 1);
            let (value, after_value) = self.parse_value(pos, end, strings);
            pos = self.skip_ws(after_value);

            let lower = field_name.to_ascii_lowercase();
            if !seen_field_names.insert(lower.clone()) {
                if !duplicate_field_names.contains(&lower) {
                    duplicate_field_names.push(lower);
                }
                // Last value wins: drop any earlier field of this name.
                fields.retain(|f| !f.key.eq_ignore_ascii_case(&field_name));
            }
            fields.push(Field {
                key: field_name,
                value,
            });

            pos = self.skip_ws(pos);
            if pos < end && self.chars[pos] == ',' {
                pos = self.skip_ws(pos + 1);
            } else {
                break;
            }
        }

        duplicate_field_names.sort();
        EntryParse {
            entry: Entry {
                key,
                entry_type,
                start_line: line_index,
                fields,
            },
            duplicate_field_names,
        }
    }

    /// Parses a `{...}`/`"..."`/bare-token value, possibly `#`-concatenated
    /// with further parts, stopping at `end` regardless. Returns the
    /// assembled (whitespace-trimmed) value and the position after it.
    fn parse_value(&self, mut pos: usize, end: usize, strings: &StringTable) -> (String, usize) {
        let mut out = String::new();
        loop {
            pos = self.skip_ws(pos);
            if pos >= end {
                break;
            }
            match self.chars[pos] {
                '{' => {
                    let Some(close) = self.find_matching_brace(pos + 1, '}') else {
                        break;
                    };
                    out.push_str(&self.unescape_quotes(pos + 1, close));
                    pos = close + 1;
                }
                '"' => {
                    let Some(close) = self.find_unescaped_quote(pos + 1, end) else {
                        break;
                    };
                    out.push_str(&self.unescape_quotes(pos + 1, close));
                    pos = close + 1;
                }
                _ => {
                    let (tok, after) = self.read_ident_or_number(pos);
                    if tok.is_empty() {
                        break;
                    }
                    if let Some(resolved) = strings.get(&tok.to_ascii_lowercase()) {
                        out.push_str(resolved);
                    } else {
                        out.push_str(&tok);
                    }
                    pos = after;
                }
            }
            let after_ws = self.skip_ws(pos);
            if after_ws < end && self.chars[after_ws] == '#' {
                pos = after_ws + 1;
                continue;
            }
            break;
        }
        (out.trim().to_string(), pos)
    }

    /// Literal `\"` -> `"` inside a value's raw content — see module
    /// docs point 3; observed in real bibtexparser output.
    fn unescape_quotes(&self, start: usize, end: usize) -> String {
        let mut out = String::with_capacity(end - start);
        let mut i = start;
        while i < end {
            if self.chars[i] == '\\' && i + 1 < end && self.chars[i + 1] == '"' {
                out.push('"');
                i += 2;
            } else {
                out.push(self.chars[i]);
                i += 1;
            }
        }
        out
    }

    /// Entry key: everything up to the first `,` (or the block's end,
    /// for a fieldless entry), trimmed.
    fn read_key(&self, start: usize, end: usize) -> (String, usize) {
        let mut i = start;
        while i < end && self.chars[i] != ',' {
            i += 1;
        }
        (
            self.chars[start..i]
                .iter()
                .collect::<String>()
                .trim()
                .to_string(),
            i,
        )
    }

    fn skip_ws_or_comma(&self, mut pos: usize, end: usize) -> usize {
        if pos < end && self.chars[pos] == ',' {
            pos += 1;
        }
        self.skip_ws(pos)
    }

    fn skip_ws(&self, mut pos: usize) -> usize {
        while pos < self.len() && self.chars[pos].is_whitespace() {
            pos += 1;
        }
        pos
    }

    fn find_from(&self, start: usize, needle: char) -> Option<usize> {
        (start..self.len()).find(|&i| self.chars[i] == needle)
    }

    /// Reads a bare word: letters only. Used for the `@type` directive
    /// name, where BibTeX types are always alphabetic.
    fn read_word(&self, start: usize) -> (String, usize) {
        let n = self.len();
        let mut i = start;
        while i < n && self.chars[i].is_ascii_alphabetic() {
            i += 1;
        }
        (self.chars[start..i].iter().collect(), i)
    }

    /// A field/string name or key: letters, digits, `-`, `_`, `:`, `.`.
    fn read_ident(&self, start: usize) -> (String, usize) {
        let n = self.len();
        let mut i = start;
        while i < n
            && (self.chars[i].is_ascii_alphanumeric()
                || matches!(self.chars[i], '-' | '_' | ':' | '.'))
        {
            i += 1;
        }
        (self.chars[start..i].iter().collect(), i)
    }

    fn read_ident_or_number(&self, start: usize) -> (String, usize) {
        self.read_ident(start)
    }

    /// `{` or `(` at `pos` (after skipping to it); returns the matching
    /// closer character. `None` if `pos` isn't an opener.
    fn opener_at(&self, pos: usize) -> Option<(char, char)> {
        if pos >= self.len() {
            return None;
        }
        match self.chars[pos] {
            '{' => Some(('{', '}')),
            '(' => Some(('(', ')')),
            _ => None,
        }
    }

    /// `self.chars[start - 1]` must be the opener; returns the index of
    /// the matching closer (brace-depth-balanced; quotes are NOT
    /// treated specially here since this is only used for the
    /// outermost entry/string/comment block, whose content is scanned
    /// field-by-field separately).
    fn find_matching_brace(&self, start: usize, closer: char) -> Option<usize> {
        let opener = if closer == '}' { '{' } else { '(' };
        let n = self.len();
        let mut depth = 1i32;
        let mut i = start;
        while i < n {
            if self.chars[i] == opener {
                depth += 1;
            } else if self.chars[i] == closer {
                depth -= 1;
                if depth == 0 {
                    return Some(i);
                }
            }
            i += 1;
        }
        None
    }

    fn find_unescaped_quote(&self, start: usize, end: usize) -> Option<usize> {
        let mut i = start;
        while i < end {
            if self.chars[i] == '"' && (i == start || self.chars[i - 1] != '\\') {
                return Some(i);
            }
            i += 1;
        }
        None
    }

    fn line_index_of(&self, pos: usize) -> u32 {
        self.chars[..pos].iter().filter(|&&c| c == '\n').count() as u32
    }
}

struct EntryParse {
    entry: Entry,
    duplicate_field_names: Vec<String>,
}
