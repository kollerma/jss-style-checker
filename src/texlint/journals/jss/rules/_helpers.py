"""Private shared walkers, factories, and safety helpers for JSS rule modules.

All functions are pure: same inputs → same outputs, no mutable module
state, no randomness. The module is underscore-prefixed to mark it
private to the ``rules/`` package (not part of any third-party surface).

Besides the node walkers, this module is the single home of the
rule/violation factories (:func:`make_rule`, :func:`tex_violation`,
:func:`entry_violation`, :func:`make_violation`) that every category
module previously re-declared locally — fourteen copies of
``_violation`` and fifteen of ``_rule`` before the consolidation.
"""

from __future__ import annotations

import re
from collections.abc import Iterator, Sequence
from typing import Any

from pylatexenc.latexwalker import (
    LatexCharsNode,
    LatexCommentNode,
    LatexEnvironmentNode,
    LatexGroupNode,
    LatexMacroNode,
    LatexMathNode,
)

from texlint.api import (
    VERBATIM_ENVS,
    Fix,
    Rule,
    RuleCheck,
    RuleCheckProject,
    Violation,
)

# Shared with the parser's special-char neutraliser via texlint.api —
# any env the parser neutralises is also non-prose for rule purposes.
_VERBATIM_ENVS: frozenset[str] = VERBATIM_ENVS


# ---------------------------------------------------------------------------
# Rule / violation factories
# ---------------------------------------------------------------------------


def make_rule(
    rule_id: str,
    check: RuleCheck,
    *,
    formats: frozenset[str] | None = None,
    check_project: RuleCheckProject | None = None,
) -> Rule:
    """Build a :class:`Rule` whose metadata comes from the catalogue.

    Single replacement for the per-module ``_rule`` factories. The
    measured-precision ``confidence`` tier is stamped here as well (the
    journal-assembly stamp in ``texlint.journals.jss`` then no-ops).
    """
    from texlint.journals.jss import _catalogue_data

    meta = _catalogue_data.RULES[rule_id]
    return Rule(
        id=rule_id,
        category=meta["category"],
        severity=meta["severity"],
        message_template=meta["message_template"],
        authority=meta["authority"],
        check=check,
        formats=formats,
        check_project=check_project,
        confidence=meta.get("confidence", "high"),
    )


def make_violation(
    *,
    file: Any,
    line: int,
    column: int | None,
    rule_id: str,
    suggestion: str | None,
    fix: Fix | None = None,
) -> Violation:
    """Generic catalogue-backed violation: severity and message come
    from the rule's catalogue entry; the caller supplies position."""
    from texlint.journals.jss import _catalogue_data

    meta = _catalogue_data.RULES[rule_id]
    return Violation(
        file=file,
        line=line,
        column=column,
        rule_id=rule_id,
        severity=meta["severity"],
        message=meta["message_template"],
        suggestion=suggestion,
        fix=fix,
    )


def tex_violation(
    *,
    tex: Any,
    pos: int,
    rule_id: str,
    suggestion: str | None,
    fix: Fix | None = None,
) -> Violation:
    """Violation at a source position inside a parsed tex-like file."""
    line, col = _lineno_col(tex, pos)
    return make_violation(
        file=tex.path,
        line=line,
        column=col,
        rule_id=rule_id,
        suggestion=suggestion,
        fix=fix,
    )


def entry_line(entry: Any) -> int:
    """1-based line of a bibtexparser entry (``start_line`` is 0-based)."""
    start = getattr(entry, "start_line", 0) or 0
    return start + 1


def entry_violation(
    *,
    bib: Any,
    entry: Any,
    rule_id: str,
    suggestion: str | None,
) -> Violation:
    """Violation anchored to a BibTeX entry's first line."""
    return make_violation(
        file=bib.path,
        line=entry_line(entry),
        column=None,
        rule_id=rule_id,
        suggestion=suggestion,
    )

_VERBATIM_MACROS: frozenset[str] = frozenset({"verb", "code"})

# natbib + amsrefs + base LaTeX citation macros. `nocite` is included
# because `\nocite{*}` forces the bibliography to render every entry,
# so it widens the "referenced" scope to all-of-them.
_CITE_MACROS_FOR_SCOPE: frozenset[str] = frozenset({
    "cite", "Cite", "citet", "Citet", "citep", "Citep",
    "citealp", "Citealp", "citealt", "Citealt",
    "citeauthor", "Citeauthor", "citeyear", "citeyearpar",
    "nocite",
})


def _walk(nodes: Sequence[Any] | None) -> Iterator[Any]:
    """Pre-order traversal of a pylatexenc node list.

    Recurses into environment bodies, group contents, math-node
    contents, and macro argument groups. Yields every non-None node.
    An empty or ``None`` input yields nothing.
    """
    for node in nodes or ():
        if node is None:
            continue
        yield node
        children: Sequence[Any] = ()
        if isinstance(node, (LatexEnvironmentNode, LatexGroupNode, LatexMathNode)):
            children = node.nodelist or ()
        elif isinstance(node, LatexMacroNode):
            argd = getattr(node, "nodeargd", None)
            if argd is not None:
                children = argd.argnlist or ()
        yield from _walk(children)


def _iter_with_parent(
    nodes: Sequence[Any] | None,
) -> Iterator[tuple[Sequence[Any], int, Any]]:
    """Like ``_walk`` but yields ``(parent_nodelist, index, node)`` triples.

    Needed for sibling-context checks (e.g., macro followed by a group
    that is its unknown-macro argument, or a ``\\cite`` wrapped in
    literal parentheses).
    """
    parent = nodes or ()
    for idx, node in enumerate(parent):
        if node is None:
            continue
        yield parent, idx, node
        children: Sequence[Any] = ()
        if isinstance(node, (LatexEnvironmentNode, LatexGroupNode, LatexMathNode)):
            children = node.nodelist or ()
        elif isinstance(node, LatexMacroNode):
            argd = getattr(node, "nodeargd", None)
            if argd is not None:
                children = argd.argnlist or ()
        yield from _iter_with_parent(children)


def _next_group_arg(parent: Sequence[Any], idx: int) -> Any:
    """Return the sibling :class:`LatexGroupNode` right after ``parent[idx]``.

    Returns ``None`` when there is no such sibling.
    """
    nxt = idx + 1
    if nxt >= len(parent):
        return None
    sibling = parent[nxt]
    if isinstance(sibling, LatexGroupNode):
        return sibling
    return None


def _macro_args_text(macro: Any, parent: Sequence[Any], idx: int) -> str:
    """Extract the macro's first braced-group arg as plain text.

    Tries ``nodeargd.argnlist`` first (pylatexenc-known macros); falls
    back to the next sibling :class:`LatexGroupNode` for unknown macros
    like ``\\pkg``, ``\\proglang``, ``\\code``. Returns ``""`` when no
    braced arg is present.
    """
    argd = getattr(macro, "nodeargd", None)
    if argd is not None:
        for arg in argd.argnlist or ():
            if isinstance(arg, LatexGroupNode):
                return _group_text(arg)
    sibling = _next_group_arg(parent, idx)
    if sibling is not None:
        return _group_text(sibling)
    return ""


def _group_text(group: Any) -> str:
    chars: list[str] = []
    for child in group.nodelist or ():
        if isinstance(child, LatexCharsNode):
            chars.append(child.chars)
    return "".join(chars).strip()


def _lc_fields(entry: Any) -> dict[str, Any]:
    """Return ``entry.fields_dict`` with field-name keys lower-cased.

    BibTeX field names are case-insensitive (`AUTHOR`, `Author`, and
    `author` mean the same thing per the BibTeX spec). bibtexparser 2.x
    keeps the source casing in ``fields_dict``, which made every
    ``entry.fields_dict.get("year")`` miss entries that wrote ``YEAR``
    or ``Year``. Use this helper to normalise once at the call site.
    """
    return {k.lower(): v for k, v in (entry.fields_dict or {}).items()}


def _collect_cited_keys(doc: Any) -> tuple[set[str], bool]:
    """Return ``(keys, include_all)`` from all ``\\cite*`` / ``\\nocite``
    macros across every tex-like island in ``doc``.

    - ``keys`` is the set of bibkey strings collected from macro
      arguments; multi-key args like ``{foo,bar}`` are split on commas
      and stripped.
    - ``include_all`` flips to ``True`` if any ``\\nocite{*}`` is seen
      — that pattern forces BibTeX to render every entry in the
      bibliography, so the "referenced" scope widens to all of them.

    Uses :func:`_macro_args_text` so macros unknown to pylatexenc
    (``\\nocite``, ``\\shortcites``) resolve their arg via the
    next-sibling-group fallback rather than through ``nodeargd``.
    """
    keys: set[str] = set()
    include_all = False
    for tex in doc.all_tex_like():
        for parent, idx, node in _iter_with_parent(tex.nodes):
            if not isinstance(node, LatexMacroNode):
                continue
            if node.macroname not in _CITE_MACROS_FOR_SCOPE:
                continue
            text = _macro_args_text(node, parent, idx)
            for raw in text.split(","):
                key = raw.strip()
                if key == "*":
                    include_all = True
                elif key:
                    keys.add(key)
    return keys, include_all


def _collect_macro_arg_texts(doc: Any, macroname: str) -> set[str]:
    """Collect the first braced-arg text of every ``\\<macroname>{...}``
    across all tex-like islands in ``doc``.

    Used e.g. to learn the document's own package vocabulary from its
    ``\\pkg{...}`` usage: a paper that wraps ``\\pkg{flexsurv}`` anywhere
    has told us "flexsurv" is a package name, which beats any global
    curated list (and any filesystem-path heuristic).
    """
    texts: set[str] = set()
    for tex in doc.all_tex_like():
        for parent, idx, node in _iter_with_parent(tex.nodes):
            if not isinstance(node, LatexMacroNode):
                continue
            if node.macroname != macroname:
                continue
            text = _macro_args_text(node, parent, idx)
            if text:
                texts.add(text)
    return texts


def _iter_referenced_entries(doc: Any) -> Iterator[tuple[Any, Any]]:
    """Yield ``(bib_file, entry)`` pairs for entries that are cited from
    the paper's tex-like surface.

    Rationale: authors often drop a shared ``.bib`` collection into the
    paper dir even though only a subset of entries is cited; rule
    violations on unreferenced entries are noise for the author.

    Scope widening:
    - Bib-only lint (no tex/rnw/rmd input present) → include every
      entry (we have no way to know scope, and the user explicitly
      asked to lint the bib).
    - ``\\nocite{*}`` present anywhere in the tex surface → include
      every entry (that's the semantic of the macro).
    """
    bib_files = list(doc.bib_files)
    if not bib_files:
        return
    tex_like_present = any(True for _ in doc.all_tex_like())
    if not tex_like_present:
        for bib in bib_files:
            if bib.library is None:
                continue
            for entry in getattr(bib.library, "entries", ()) or ():
                yield bib, entry
        return
    cited, include_all = _collect_cited_keys(doc)
    for bib in bib_files:
        if bib.library is None:
            continue
        for entry in getattr(bib.library, "entries", ()) or ():
            if include_all or entry.key in cited:
                yield bib, entry


def _lineno_col(tex: Any, pos: int) -> tuple[int, int]:
    """Resolve ``(1-based line, 1-based column)`` from a source position."""
    line, col0 = tex.walker.pos_to_lineno_colno(pos)
    return line, col0 + 1


def _is_inside_verbatim(ancestors: Sequence[Any]) -> bool:
    """True if any ancestor is a verbatim-class environment or macro."""
    for node in ancestors:
        if (
            isinstance(node, LatexEnvironmentNode)
            and node.environmentname in _VERBATIM_ENVS
        ):
            return True
        if (
            isinstance(node, LatexMacroNode)
            and node.macroname in _VERBATIM_MACROS
        ):
            return True
    return False


def _is_inside_comment(node: Any) -> bool:
    """True when ``node`` is a :class:`LatexCommentNode`."""
    return isinstance(node, LatexCommentNode)


_MATH_ENVS: frozenset[str] = frozenset(
    {"equation", "equation*", "align", "align*", "eqnarray", "eqnarray*",
     "gather", "gather*", "multline", "multline*"}
)


def _is_inside_math(ancestors: Sequence[Any]) -> bool:
    """True if any ancestor is a math environment or inline-math node."""
    for node in ancestors:
        if isinstance(node, LatexMathNode):
            return True
        if (
            isinstance(node, LatexEnvironmentNode)
            and node.environmentname in _MATH_ENVS
        ):
            return True
    return False


_BLANK_LINE_RE: re.Pattern[str] = re.compile(r"\n\s*\n")


def _char_has_blank_line(node: Any) -> bool:
    """True when a :class:`LatexCharsNode` contains a blank line."""
    return isinstance(node, LatexCharsNode) and bool(_BLANK_LINE_RE.search(node.chars))


def _walk_with_ancestors(
    nodes: Sequence[Any] | None,
    ancestors: list[Any] | None = None,
) -> Iterator[tuple[Any, list[Any]]]:
    """Pre-order walk yielding ``(node, ancestor_stack)`` — outermost first.

    See :func:`_walk_with_context` for the sibling-aware variant that
    additionally yields ``(parent, idx)`` for each node.
    """
    for node, anc, _p, _i in _walk_with_context(nodes, ancestors):
        yield node, anc


def _walk_with_context(
    nodes: Sequence[Any] | None,
    ancestors: list[Any] | None = None,
) -> Iterator[tuple[Any, list[Any], Sequence[Any], int]]:
    """Pre-order walk yielding ``(node, ancestors, parent, idx)``.

    Handles unknown-macro sibling semantics: when a :class:`LatexGroupNode`
    follows an unknown macro (no registered arg spec), the macro is
    pushed onto the ancestor stack before recursing into the group.
    """
    if ancestors is None:
        ancestors = []
    seq = tuple(nodes or ())
    for i, node in enumerate(seq):
        if node is None:
            continue
        yield node, list(ancestors), seq, i
        children: Sequence[Any] = ()
        if isinstance(node, (LatexEnvironmentNode, LatexGroupNode, LatexMathNode)):
            children = node.nodelist or ()
        elif isinstance(node, LatexMacroNode):
            argd = getattr(node, "nodeargd", None)
            if argd is not None:
                children = argd.argnlist or ()
        extra: Any = None
        if (
            isinstance(node, LatexGroupNode)
            and i > 0
            and isinstance(seq[i - 1], LatexMacroNode)
        ):
            extra = seq[i - 1]
        if not children:
            continue
        if extra is not None:
            ancestors.append(extra)
        ancestors.append(node)
        yield from _walk_with_context(children, ancestors)
        ancestors.pop()
        if extra is not None:
            ancestors.pop()


# Section macros whose argument is a displayed title, not prose.
_SECTION_MACROS: frozenset[str] = frozenset(
    {"section", "section*", "subsection", "subsection*",
     "subsubsection", "subsubsection*", "chapter", "chapter*",
     "paragraph", "subparagraph"}
)

# Macros whose text arg is already JSS-wrapped markup. Beyond the
# canonical jss.cls macros (``\pkg``, ``\proglang``, ``\code``, ...),
# this also includes common paper-defined ``\Rcmd``-family wrappers —
# vignettes from multcomp, cotram, tram, mlt, tbm, etc. define
# ``\newcommand{\Rcmd}[1]{\texttt{#1}}`` and friends, which render
# code-style content. Treating them as markup avoids MARKUP-003 firing
# on already-wrapped function calls like ``\Rcmd{glht()}``.
_MARKUP_MACROS: frozenset[str] = frozenset(
    {"pkg", "proglang", "code", "verb", "url", "email", "fct",
     "Rcmd", "Rpackage", "Rclass", "Rfun", "Rfunction",
     "Rargument", "Rstring", "Robject",
     # Paper-defined filename wrapper — robustlmm defines
     # ``\script{...}`` (renders in \texttt) for filenames; treating
     # it as markup avoids MARKUP-001 firing on ``R`` extensions
     # inside ``\script{convergence.R}`` etc.
     "script",
     # Paper-defined ``\code`` aliases — TraMineR / WeightedCluster
     # define ``\newcommand{\Com}[1]{\code{#1}}`` (and ``\Comt``) for
     # inline code, so their content is code, not prose.
     "Com", "Comt",
     # ``highlight`` package code-highlighting macros — knitr / Rnw
     # output uses ``\hlstd{}``, ``\hlkwa{}``, ``\hlopt{}``,
     # ``\hlkwd{}``, ``\hlstr{}``, ``\hlcom{}`` to wrap tokens of
     # syntax-highlighted code. Content is code, not prose.
     "hlstd", "hlkwa", "hlopt", "hlkwd", "hlstr", "hlcom",
     "hlnum", "hlsng", "hlslc", "hlppc", "hlpps"}
)

# Preamble / meta-data / citation macros whose arg is not prose to scan.
# ``Abstract`` is NOT in this set even though it's a JSS meta-data macro
# — the abstract IS prose and the JSS markup rules (MARKUP-001/002/003)
# should fire on bare ``R`` / package mentions inside it (corpus FNs in
# mdsOpt/mdsOpt.ltx:43-45).
_META_MACROS: frozenset[str] = frozenset(
    {"title", "Plaintitle", "Shorttitle",
     "author", "Plainauthor",
     "Keywords", "Plainkeywords",
     "Address",
     "documentclass", "usepackage", "include", "input",
     "label", "ref", "pageref",
     "bibliographystyle", "bibliography",
     # Sweave/Rnw directives — option lists, not prose.
     "SweaveOpts", "SweaveInput", "SweaveSyntax",
     "VignetteIndexEntry", "VignettePackage", "VignetteDepends",
     "VignetteEngine", "VignetteKeywords", "VignetteEncoding",
     "newcommand", "renewcommand", "providecommand", "def",
     # Listings / minted / inputlisting directives — option lists like
     # ``language=R``, not prose. Without this, MARKUP-001 fires on
     # the ``R`` token inside ``\lstinputlisting[language=R, ...]``.
     "lstinputlisting", "lstset", "inputminted", "VerbatimInput",
     # Graphics inclusion — the optional arg is a key=value option list
     # (``clip = TRUE``, ``trim = 5 5 5 5``) and the mandatory arg is a
     # filename; neither is prose. Without this, MARKUP-003 fires on the
     # ``TRUE`` / ``FALSE`` graphics booleans inside
     # ``\includegraphics[clip = TRUE]{...}``.
     "includegraphics", "includepdf", "graphicspath"}
)
# Cite-family macros are NOT in _META_MACROS so that their optional-arg
# prose (``\citep[e.g.][]{key}`` — the prenote / postnote slots) gets
# scanned by HOUSE-001 etc. Cite-key contents don't typically contain
# language / package terms that would false-positive other rules.


def _is_in_prose_context(ancestors: Sequence[Any]) -> bool:
    """True when a char node at this position is prose — not inside JSS
    markup wrappers, math mode, verbatim envs, section titles, or preamble
    meta-data macros."""
    if _is_inside_verbatim(ancestors):
        return False
    if _is_inside_math(ancestors):
        return False
    for anc in ancestors:
        if isinstance(anc, LatexMacroNode):
            if anc.macroname in _MARKUP_MACROS:
                return False
            if anc.macroname in _SECTION_MACROS:
                return False
            if anc.macroname in _META_MACROS:
                return False
    return True
