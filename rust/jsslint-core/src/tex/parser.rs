//! Tolerant LaTeX tokenizer — a from-scratch parser producing the same
//! six node kinds as `pylatexenc.latexwalker`, tuned to match its
//! observed behavior rather than general TeX semantics. Ground truth
//! was established empirically against the installed `pylatexenc`
//! (see git history / plan notes for the probe sessions), not by
//! reading its source line-by-line — where the two might diverge, the
//! `tests/parser_parity.rs` fixture-diff harness is the actual
//! arbiter, per the plan's Phase 1 scope ("no rules yet — just prove
//! the substrate matches").
//!
//! Key empirically-verified rules this parser encodes:
//!
//! 1. **Control-word whitespace eating.** A control WORD (`\` + one or
//!    more `[A-Za-z@]`) swallows trailing spaces/tabs and *at most one*
//!    newline (plus further spaces/tabs after it) into its own span —
//!    UNLESS eating that newline would immediately cross a blank line
//!    (two adjacent `\n`s), which is left untouched as a paragraph
//!    boundary. A control SYMBOL (`\` + exactly one other character)
//!    does not eat anything.
//! 2. **Unknown macros take zero arguments.** A macro/environment name
//!    absent from `specs::macro_argspec` (compiled from pylatexenc's
//!    own default database — see `tex/specs.rs`) ends immediately after
//!    its (whitespace-eaten) name. Whatever follows — commonly a
//!    `{...}` group — is simply the next sibling node in the parent's
//!    list, not an argument. This is *why* JSS's own macros (`\pkg`,
//!    `\proglang`, `\code`, ...) need the sibling-group fallback that
//!    `tex::prose` ports from `_helpers.py::_macro_args_text`.
//! 3. **Known macros/environments** parse arguments per an argspec
//!    string (`{` mandatory group, `[` optional bracket group, `*`
//!    optional literal star), each preceded by a TeX-whitespace skip
//!    (rule 1's skipping logic, reused) — except a `[` slot that finds
//!    no `[` does NOT consume the whitespace it peeked past.
//! 4. **`\[`/`\]` and `\(`/`\)`** are recognized as literal display/
//!    inline math delimiters at the tokenizer level, not as generic
//!    control symbols.
//!
//! Known, deliberate simplifications:
//!
//! - An *unbraced* mandatory argument (`\section\relax text`,
//!   vanishingly rare in real manuscripts) reads only a single bare
//!   token (one char, or one control-sequence *name* with no further
//!   recursive argument parsing), rather than pylatexenc's fully
//!   general recursive expression read.
//! - Inside a *deliberately unclosed* `{` group (malformed input),
//!   this tokenizer keeps tokenizing normally, while real pylatexenc's
//!   tolerant-mode recovery silently drops a stray `\end{...}` token
//!   encountered there — see `tests/parser_parity.rs`'s
//!   `KNOWN_DIVERGENCES` for the one fixture this affects.
//!
//! Revisit either only if the fixture-diff harness surfaces a real
//! corpus file that needs it.

use super::node::*;
use super::specs;

/// What ends the current `parse_nodelist` call. The matched stop text
/// itself is consumed (its end position is returned) but never appears
/// in the returned node list.
#[derive(Debug, Clone)]
enum Stop {
    /// Top-level document parse — nothing but end-of-input stops it.
    EndOfInput,
    CloseBrace,
    CloseBracket,
    /// A single, undoubled `$`.
    DollarMath,
    /// `$$`.
    DisplayDollarMath,
    /// Literal `\]`.
    MathBracket,
    /// Literal `\)`.
    MathParen,
    /// Literal `\end{<name>}`, exact name match.
    EndEnvironment(String),
}

pub struct Parser<'a> {
    chars: &'a [char],
}

/// Parse `source` into a top-level node list. Never fails — unclosed
/// groups/environments/math simply extend to end-of-input, matching
/// this crate's tolerant-only philosophy (the Python side has a
/// separate strict-then-tolerant retry; this port only implements the
/// tolerant behavior, which is what most real documents already
/// resolve to after `core/parser.py`'s pre-neutralization).
pub fn parse(source: &str) -> (Vec<Node>, Vec<char>) {
    let chars: Vec<char> = source.chars().collect();
    let (nodes, _end) = {
        let parser = Parser { chars: &chars };
        parser.parse_nodelist(0, &Stop::EndOfInput)
    };
    (nodes, chars)
}

impl<'a> Parser<'a> {
    fn len(&self) -> usize {
        self.chars.len()
    }

    fn parse_nodelist(&self, mut pos: usize, stop: &Stop) -> (Vec<Node>, usize) {
        let mut nodes: Vec<Node> = Vec::new();
        let mut chars_start: Option<usize> = None;
        let n = self.len();

        while pos < n {
            if let Some(stop_end) = self.matches_stop(pos, stop) {
                self.flush_chars(&mut nodes, &mut chars_start, pos);
                return (nodes, stop_end);
            }
            if let Some(matched) = self.match_specials(pos) {
                self.flush_chars(&mut nodes, &mut chars_start, pos);
                let len = matched.chars().count();
                nodes.push(Node::Specials(SpecialsNode {
                    span: Span { pos, len },
                    chars: matched.to_string(),
                }));
                pos += len;
                continue;
            }
            match self.chars[pos] {
                '%' => {
                    self.flush_chars(&mut nodes, &mut chars_start, pos);
                    let (node, next) = self.parse_comment(pos);
                    nodes.push(Node::Comment(node));
                    pos = next;
                }
                '\\' => {
                    self.flush_chars(&mut nodes, &mut chars_start, pos);
                    let (node, next) = self.parse_backslash(pos);
                    nodes.push(node);
                    pos = next;
                }
                '{' => {
                    self.flush_chars(&mut nodes, &mut chars_start, pos);
                    let (node, next) = self.parse_group(pos, GroupDelims::Brace);
                    nodes.push(Node::Group(node));
                    pos = next;
                }
                '$' => {
                    self.flush_chars(&mut nodes, &mut chars_start, pos);
                    let (node, next) = self.parse_dollar_math(pos);
                    nodes.push(Node::Math(node));
                    pos = next;
                }
                _ => {
                    if chars_start.is_none() {
                        chars_start = Some(pos);
                    }
                    pos += 1;
                }
            }
        }
        self.flush_chars(&mut nodes, &mut chars_start, pos);
        (nodes, pos)
    }

    fn flush_chars(&self, nodes: &mut Vec<Node>, chars_start: &mut Option<usize>, end: usize) {
        if let Some(start) = chars_start.take() {
            if end > start {
                nodes.push(Node::Chars(CharsNode {
                    span: Span {
                        pos: start,
                        len: end - start,
                    },
                    chars: self.chars[start..end].iter().collect(),
                }));
            }
        }
    }

    /// `None` if `stop` doesn't match at `pos`; otherwise the position
    /// right after the consumed stop text.
    fn matches_stop(&self, pos: usize, stop: &Stop) -> Option<usize> {
        match stop {
            Stop::EndOfInput => None,
            Stop::CloseBrace => (self.chars[pos] == '}').then_some(pos + 1),
            Stop::CloseBracket => (self.chars[pos] == ']').then_some(pos + 1),
            Stop::DollarMath => {
                (self.chars[pos] == '$' && !self.starts_with(pos, "$$")).then_some(pos + 1)
            }
            Stop::DisplayDollarMath => self.starts_with(pos, "$$").then_some(pos + 2),
            Stop::MathBracket => self.starts_with(pos, r"\]").then_some(pos + 2),
            Stop::MathParen => self.starts_with(pos, r"\)").then_some(pos + 2),
            Stop::EndEnvironment(name) => {
                let marker = format!(r"\end{{{name}}}");
                self.starts_with(pos, &marker)
                    .then_some(pos + marker.chars().count())
            }
        }
    }

    fn starts_with(&self, pos: usize, needle: &str) -> bool {
        let needle_chars: Vec<char> = needle.chars().collect();
        if pos + needle_chars.len() > self.len() {
            return false;
        }
        self.chars[pos..pos + needle_chars.len()] == needle_chars[..]
    }

    /// The longest `specs::specials()` entry matching literally at
    /// `pos`, if any (the table is already longest-first).
    fn match_specials(&self, pos: usize) -> Option<&'static str> {
        specs::specials()
            .iter()
            .find(|&&s| self.starts_with(pos, s))
            .copied()
    }

    /// TeX whitespace skip (control-word / macro post-space eating).
    /// Mirrors pylatexenc's tokenizer loop exactly: consume ANY
    /// Unicode-whitespace char (not just space/tab/`\n` — `\r`, form
    /// feed, etc. all count, like Python's `str.isspace()`), UNLESS
    /// doing so would make the just-consumed run end with a LITERAL
    /// `"\n\n"` (two LF in a row — a paragraph boundary), in which case
    /// back off those 2 chars and stop. This is a literal `"\n\n"`
    /// check, not "any two newline-class chars in a row": a `\r\n\r\n`
    /// blank line (CRLF) does NOT trigger it and is consumed in full —
    /// see module docs rule 1.
    fn skip_tex_whitespace(&self, pos: usize) -> usize {
        let n = self.len();
        let mut i = pos;
        while i < n && self.chars[i].is_whitespace() {
            i += 1;
            if i - pos >= 2 && self.chars[i - 2] == '\n' && self.chars[i - 1] == '\n' {
                i -= 2;
                break;
            }
        }
        i
    }

    fn parse_comment(&self, pos: usize) -> (CommentNode, usize) {
        debug_assert_eq!(self.chars[pos], '%');
        let n = self.len();
        let mut i = pos + 1;
        // `\r` terminates a comment exactly like `\n` — mirrors
        // pylatexenc's tokenizer regex `(\n|\r|\n\r)(?P<extraspace>\s*)`,
        // which matches whichever of `\n`/`\r` occurs first (a bare `\r`
        // stops the comment scan on its own, `\r\n` is NOT treated as
        // one atomic terminator).
        while i < n && self.chars[i] != '\n' && self.chars[i] != '\r' {
            i += 1;
        }
        let text_end = i;
        // Include the terminating newline in the span (not the text)
        // UNLESS doing so would cross into a blank line — same rule as
        // control-word whitespace-eating (`skip_tex_whitespace`); empirically
        // verified against pylatexenc (module docs rule 1 applies here too).
        // `\r` counts as a newline for THIS check too: since a bare `\r`
        // is itself "the terminator" the regex matches, a `\r\n` pair
        // means the very next char after that terminator is ALSO
        // newline-class, so pylatexenc's paragraph-break branch fires —
        // net effect: a `\r\n` line ending is never consumed into a
        // comment's span at all (differs from a plain `\n`, which IS
        // consumed when not followed by a second newline).
        let is_newline_class = |c: char| c == '\n' || c == '\r';
        let span_end = if i < n && !(i + 1 < n && is_newline_class(self.chars[i + 1])) {
            i + 1
        } else {
            i
        };
        (
            CommentNode {
                span: Span {
                    pos,
                    len: span_end - pos,
                },
                comment: self.chars[pos + 1..text_end].iter().collect(),
            },
            span_end,
        )
    }

    fn parse_group(&self, pos: usize, delims: GroupDelims) -> (GroupNode, usize) {
        debug_assert!(self.chars[pos] == '{' || self.chars[pos] == '[');
        let stop = match delims {
            GroupDelims::Brace => Stop::CloseBrace,
            GroupDelims::Bracket => Stop::CloseBracket,
        };
        let (nodelist, end) = self.parse_nodelist(pos + 1, &stop);
        (
            GroupNode {
                span: Span {
                    pos,
                    len: end - pos,
                },
                delims,
                nodelist,
            },
            end,
        )
    }

    fn parse_dollar_math(&self, pos: usize) -> (MathNode, usize) {
        debug_assert_eq!(self.chars[pos], '$');
        if self.starts_with(pos, "$$") {
            let (nodelist, end) = self.parse_nodelist(pos + 2, &Stop::DisplayDollarMath);
            (
                MathNode {
                    span: Span {
                        pos,
                        len: end - pos,
                    },
                    kind: MathKind::Display,
                    nodelist,
                },
                end,
            )
        } else {
            let (nodelist, end) = self.parse_nodelist(pos + 1, &Stop::DollarMath);
            (
                MathNode {
                    span: Span {
                        pos,
                        len: end - pos,
                    },
                    kind: MathKind::Inline,
                    nodelist,
                },
                end,
            )
        }
    }

    /// Dispatch on what follows a `\`: `\[`/`\(` math openers,
    /// `\begin`/`\end`, a verbatim macro, a known macro (argspec
    /// lookup), or an unknown zero-arg macro.
    fn parse_backslash(&self, pos: usize) -> (Node, usize) {
        debug_assert_eq!(self.chars[pos], '\\');
        let n = self.len();
        if pos + 1 >= n {
            // Trailing lone backslash at EOF — degrade to an empty-name macro.
            return (
                Node::Macro(MacroNode {
                    span: Span { pos, len: 1 },
                    macroname: String::new(),
                    args: Vec::new(),
                }),
                pos + 1,
            );
        }

        if self.starts_with(pos, r"\[") {
            let (nodelist, end) = self.parse_nodelist(pos + 2, &Stop::MathBracket);
            return (
                Node::Math(MathNode {
                    span: Span {
                        pos,
                        len: end - pos,
                    },
                    kind: MathKind::Display,
                    nodelist,
                }),
                end,
            );
        }
        if self.starts_with(pos, r"\(") {
            let (nodelist, end) = self.parse_nodelist(pos + 2, &Stop::MathParen);
            return (
                Node::Math(MathNode {
                    span: Span {
                        pos,
                        len: end - pos,
                    },
                    kind: MathKind::Inline,
                    nodelist,
                }),
                end,
            );
        }

        let next = self.chars[pos + 1];
        let (name, name_end, is_word) = if next.is_ascii_alphabetic() || next == '@' {
            let mut i = pos + 1;
            while i < n && (self.chars[i].is_ascii_alphabetic() || self.chars[i] == '@') {
                i += 1;
            }
            (self.chars[pos + 1..i].iter().collect::<String>(), i, true)
        } else {
            (next.to_string(), pos + 2, false)
        };

        let after_ws = if is_word {
            self.skip_tex_whitespace(name_end)
        } else {
            name_end
        };

        if is_word && name == "begin" {
            return self.parse_environment(pos, after_ws);
        }
        // A stray `\end` not consumed as a body's Stop::EndEnvironment
        // (e.g. mismatched/unbalanced input) — tolerant fallback: treat
        // as an ordinary (unknown) zero-arg macro.
        if is_word && specs::is_verbatim_macro(&name) {
            return self.parse_verbatim_macro(pos, name, after_ws);
        }
        if let Some(argspec) = specs::macro_argspec(&name) {
            let (args, end) = self.parse_args(argspec, after_ws);
            return (
                Node::Macro(MacroNode {
                    span: Span {
                        pos,
                        len: end - pos,
                    },
                    macroname: name,
                    args,
                }),
                end,
            );
        }
        // Unknown macro: zero args. Trailing whitespace already eaten
        // into `after_ws` for a control word; a control symbol eats
        // nothing (rule 1).
        (
            Node::Macro(MacroNode {
                span: Span {
                    pos,
                    len: after_ws - pos,
                },
                macroname: name,
                args: Vec::new(),
            }),
            after_ws,
        )
    }

    /// `\verb<delim>...<delim>` (and similarly-shaped verbatim macros):
    /// the character immediately after (whitespace-eaten) name-end is
    /// the delimiter; content runs verbatim until it repeats.
    fn parse_verbatim_macro(&self, pos: usize, name: String, after_ws: usize) -> (Node, usize) {
        let n = self.len();
        if after_ws >= n {
            return (
                Node::Macro(MacroNode {
                    span: Span {
                        pos,
                        len: after_ws - pos,
                    },
                    macroname: name,
                    args: Vec::new(),
                }),
                after_ws,
            );
        }
        let delim = self.chars[after_ws];
        let content_start = after_ws + 1;
        let mut i = content_start;
        while i < n && self.chars[i] != delim {
            i += 1;
        }
        let content_end = i;
        let span_end = if i < n { i + 1 } else { i }; // include closing delimiter if found
        let content: String = self.chars[content_start..content_end].iter().collect();
        let arg = Node::Chars(CharsNode {
            span: Span {
                pos: content_start,
                len: content_end - content_start,
            },
            chars: content,
        });
        (
            Node::Macro(MacroNode {
                span: Span {
                    pos,
                    len: span_end - pos,
                },
                macroname: name,
                args: vec![Some(arg)],
            }),
            span_end,
        )
    }

    fn parse_environment(&self, macro_start: usize, mut pos: usize) -> (Node, usize) {
        let n = self.len();
        // Expect `{name}` immediately (after whitespace, already skipped
        // by the caller via `after_ws`).
        if pos >= n || self.chars[pos] != '{' {
            // Malformed `\begin` with no name — tolerant fallback: an
            // unknown zero-arg macro named "begin".
            return (
                Node::Macro(MacroNode {
                    span: Span {
                        pos: macro_start,
                        len: pos - macro_start,
                    },
                    macroname: "begin".to_string(),
                    args: Vec::new(),
                }),
                pos,
            );
        }
        let (name, name_group_end) = self.read_brace_delimited_name(pos);
        pos = name_group_end;

        let args = if let Some(argspec) = specs::environment_argspec(&name) {
            let (a, next) = self.parse_args(argspec, pos);
            pos = next;
            a
        } else {
            Vec::new()
        };

        if specs::is_verbatim_environment(&name) {
            return self.parse_verbatim_environment(macro_start, name, pos);
        }

        let (nodelist, end) = self.parse_nodelist(pos, &Stop::EndEnvironment(name.clone()));
        (
            Node::Environment(EnvironmentNode {
                span: Span {
                    pos: macro_start,
                    len: end - macro_start,
                },
                environmentname: name,
                args,
                nodelist,
            }),
            end,
        )
    }

    /// The `verbatim`/`verbatim*` environment: body is read as raw
    /// text up to (not including further parsing of) the literal
    /// `\end{name}` marker.
    fn parse_verbatim_environment(
        &self,
        macro_start: usize,
        name: String,
        pos: usize,
    ) -> (Node, usize) {
        let marker: Vec<char> = format!(r"\end{{{name}}}").chars().collect();
        let n = self.len();
        let mut i = pos;
        while i < n {
            if i + marker.len() <= n && self.chars[i..i + marker.len()] == marker[..] {
                break;
            }
            i += 1;
        }
        let body_end = i;
        let span_end = if i < n { i + marker.len() } else { i };
        let body_text: String = self.chars[pos..body_end].iter().collect();
        // Mirrors pylatexenc's `VerbatimArgsParser`: the raw body lives
        // in the environment's ARGUMENT list (`nodeargd.argnlist`), not
        // its `nodelist` — `nodelist` is empty. This matters beyond
        // cosmetics: `prose::walk`/`_walk_with_context` only recurse
        // into `nodelist` for an `Environment` node, so a body stored
        // there would be visible to prose-context walking, while one
        // stored in `args` (matching pylatexenc) is invisible to it —
        // and WIDTH-001/CODE-* read `env.nodelist` too, so this also
        // reproduces Python's (accidental, but real) gap where content
        // inside a literal `verbatim` env is never width/style-checked.
        let verbatim_arg = vec![Some(Node::Chars(CharsNode {
            span: Span {
                pos,
                len: body_end - pos,
            },
            chars: body_text,
        }))];
        (
            Node::Environment(EnvironmentNode {
                span: Span {
                    pos: macro_start,
                    len: span_end - macro_start,
                },
                environmentname: name,
                args: verbatim_arg,
                nodelist: Vec::new(),
            }),
            span_end,
        )
    }

    /// Reads `{name}` starting at `pos` (which must be `{`), where
    /// `name` is a raw identifier (no nested macro parsing — matches
    /// environment names never legitimately containing them).
    fn read_brace_delimited_name(&self, pos: usize) -> (String, usize) {
        debug_assert_eq!(self.chars[pos], '{');
        let n = self.len();
        let mut i = pos + 1;
        while i < n && self.chars[i] != '}' {
            i += 1;
        }
        let name: String = self.chars[pos + 1..i].iter().collect();
        let end = if i < n { i + 1 } else { i };
        (name, end)
    }

    /// Parses `argspec` (chars `{`/`[`/`*`) starting at `pos`. See
    /// module docs rule 3 for the whitespace-consumption asymmetry
    /// between mandatory and optional slots.
    fn parse_args(&self, argspec: &str, mut pos: usize) -> (Args, usize) {
        let mut args: Args = Vec::with_capacity(argspec.chars().count());
        for slot in argspec.chars() {
            match slot {
                '{' => {
                    pos = self.skip_tex_whitespace(pos);
                    if pos < self.len() && self.chars[pos] == '{' {
                        let (g, next) = self.parse_group(pos, GroupDelims::Brace);
                        pos = next;
                        args.push(Some(Node::Group(g)));
                    } else if pos < self.len() {
                        let (node, next) = self.parse_single_token(pos);
                        pos = next;
                        args.push(Some(node));
                    } else {
                        args.push(None);
                    }
                }
                '[' => {
                    let peek = self.skip_tex_whitespace(pos);
                    if peek < self.len() && self.chars[peek] == '[' {
                        let (g, next) = self.parse_group(peek, GroupDelims::Bracket);
                        pos = next;
                        args.push(Some(Node::Group(g)));
                    } else {
                        args.push(None); // pos NOT advanced — matches pylatexenc
                    }
                }
                '*' => {
                    if pos < self.len() && self.chars[pos] == '*' {
                        args.push(Some(Node::Chars(CharsNode {
                            span: Span { pos, len: 1 },
                            chars: "*".to_string(),
                        })));
                        pos += 1;
                    } else {
                        args.push(None);
                    }
                }
                _ => {}
            }
        }
        (args, pos)
    }

    /// Simplified single-token read for an unbraced mandatory argument
    /// — see module docs' "known simplification" note.
    fn parse_single_token(&self, pos: usize) -> (Node, usize) {
        if self.chars[pos] == '}' {
            // A lone closing brace can never BE an argument — it's
            // whatever group we're already inside trying to close.
            // Mirrors pylatexenc's `get_latex_expression`'s
            // `tok.tok == 'brace_close'` branch: return an empty node
            // at this position WITHOUT consuming the brace, so the
            // enclosing group's own close-brace scan sees it next.
            // Without this, a macro used bare (no explicit `{...}`) as
            // the last thing before a group closes — e.g.
            // `\newcommand{\mbf}{ \mathbf }` — swallows the `}` as
            // `\mathbf`'s "argument", and the enclosing group never
            // finds its own terminator, running away to end of input.
            return (
                Node::Chars(CharsNode {
                    span: Span { pos, len: 0 },
                    chars: String::new(),
                }),
                pos,
            );
        }
        if self.chars[pos] == '\\' {
            let n = self.len();
            if pos + 1 >= n {
                return (
                    Node::Macro(MacroNode {
                        span: Span { pos, len: 1 },
                        macroname: String::new(),
                        args: Vec::new(),
                    }),
                    pos + 1,
                );
            }
            let next = self.chars[pos + 1];
            if next.is_ascii_alphabetic() || next == '@' {
                let mut i = pos + 1;
                while i < n && (self.chars[i].is_ascii_alphabetic() || self.chars[i] == '@') {
                    i += 1;
                }
                let end = self.skip_tex_whitespace(i);
                return (
                    Node::Macro(MacroNode {
                        span: Span {
                            pos,
                            len: end - pos,
                        },
                        macroname: self.chars[pos + 1..i].iter().collect(),
                        args: Vec::new(),
                    }),
                    end,
                );
            }
            return (
                Node::Macro(MacroNode {
                    span: Span { pos, len: 2 },
                    macroname: next.to_string(),
                    args: Vec::new(),
                }),
                pos + 2,
            );
        }
        (
            Node::Chars(CharsNode {
                span: Span { pos, len: 1 },
                chars: self.chars[pos].to_string(),
            }),
            pos + 1,
        )
    }
}
