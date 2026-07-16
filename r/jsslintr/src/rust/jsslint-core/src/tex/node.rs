//! LaTeX AST node types — mirrors the subset of `pylatexenc.latexwalker`
//! node kinds this codebase's rules actually consume (see
//! `_helpers.py`'s imports: `LatexCharsNode`, `LatexCommentNode`,
//! `LatexEnvironmentNode`, `LatexGroupNode`, `LatexMacroNode`,
//! `LatexMathNode`).
//!
//! **Positions are Unicode codepoint offsets, not byte offsets** —
//! matching Python `str` indexing (which is what `pylatexenc.pos`/`.len`
//! and `Fix.start`/`.end` actually are; see the correction in
//! `report.rs`'s `Fix` doc comment). A `Vec<char>` is the parser's
//! working representation of the source for exactly this reason.

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Span {
    pub pos: usize,
    pub len: usize,
}

impl Span {
    pub fn end(&self) -> usize {
        self.pos + self.len
    }
}

#[derive(Debug, Clone)]
pub enum Node {
    Chars(CharsNode),
    Comment(CommentNode),
    Macro(MacroNode),
    Group(GroupNode),
    Environment(EnvironmentNode),
    Math(MathNode),
    Specials(SpecialsNode),
}

impl Node {
    pub fn span(&self) -> Span {
        match self {
            Node::Chars(n) => n.span,
            Node::Comment(n) => n.span,
            Node::Macro(n) => n.span,
            Node::Group(n) => n.span,
            Node::Environment(n) => n.span,
            Node::Math(n) => n.span,
            Node::Specials(n) => n.span,
        }
    }
}

#[derive(Debug, Clone)]
pub struct CharsNode {
    pub span: Span,
    pub chars: String,
}

/// A literal token pylatexenc tokenizes as its own node rather than
/// plain characters or a macro: `~`, `&`, `--`, `---`, `` `` ``, `''`,
/// `` !` ``, `` ?` ``. Takes no arguments in the default database.
#[derive(Debug, Clone)]
pub struct SpecialsNode {
    pub span: Span,
    pub chars: String,
}

#[derive(Debug, Clone)]
pub struct CommentNode {
    pub span: Span,
    pub comment: String,
}

/// One argument slot's parse result, aligned 1:1 with the macro/env's
/// argspec string. `None` means an optional (`[` or `*`) slot that
/// wasn't present at the call site — mirrors `argnlist`'s `None`
/// entries in pylatexenc.
pub type Args = Vec<Option<Node>>;

#[derive(Debug, Clone)]
pub struct MacroNode {
    pub span: Span,
    pub macroname: String,
    pub args: Args,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum GroupDelims {
    /// `{...}` — an ordinary brace group.
    Brace,
    /// `[...]` — an optional-argument bracket group.
    Bracket,
}

#[derive(Debug, Clone)]
pub struct GroupNode {
    pub span: Span,
    pub delims: GroupDelims,
    pub nodelist: Vec<Node>,
}

#[derive(Debug, Clone)]
pub struct EnvironmentNode {
    pub span: Span,
    pub environmentname: String,
    pub args: Args,
    pub nodelist: Vec<Node>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum MathKind {
    /// `$...$` or `\(...\)`.
    Inline,
    /// `$$...$$` or `\[...\]`.
    Display,
}

#[derive(Debug, Clone)]
pub struct MathNode {
    pub span: Span,
    pub kind: MathKind,
    pub nodelist: Vec<Node>,
}
