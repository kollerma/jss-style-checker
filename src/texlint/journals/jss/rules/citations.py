"""``citations`` rules for the JSS journal plugin.

Implements the citation-related rules in
``specs/003-jss-rule-catalogue/catalogue.yaml``:

* ``JSS-CITE-001`` — ``\\emph{bibkey}`` flagged as misused citation markup
  (retrofit of the Step 1 smoke rule ``cite_001_emph.py``).
* ``JSS-CITE-002`` — ``\\pkg{X}`` mentioned without a citation command in
  the same paragraph; fires once per distinct package name.
* ``JSS-CITE-003`` — ``(\\cite{...})`` bracket-in-bracket construct;
  author should use ``\\citep{...}``.
* ``JSS-CITE-004`` — hardcoded parenthetical ``(Author, YYYY)`` text that
  should go through natbib.

Every check is a pure function of ``ParsedDocument``; rule objects are
exported via the module-level ``rules`` tuple (spec 003
contracts/rules-module.md).
"""

from __future__ import annotations

import re
from collections.abc import Iterator, Sequence
from typing import Any

from pylatexenc.latexwalker import (
    LatexCharsNode,
    LatexEnvironmentNode,
    LatexGroupNode,
    LatexMacroNode,
    LatexMathNode,
)

from texlint.api import ParsedDocument, Rule, Severity, ToolConfig, Violation

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

_BIBKEY_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_:+.-]*\d{4}[a-z]?$")

_CITATION_MACROS: frozenset[str] = frozenset(
    {
        "cite",
        "citet",
        "citep",
        "citealp",
        "citealt",
        "citeauthor",
        "citeyear",
        "citet*",
        "citep*",
        "citealp*",
        "citealt*",
    }
)

_CITE_TEXT_MACROS: frozenset[str] = frozenset({"cite", "citet"})

# "Same paragraph" window for CITE-002. Pragmatic heuristic; the precision
# gate (T024) may tune this.
_CITE_PROXIMITY_CHARS = 400


def _iter_with_parent(
    nodelist: Sequence[Any] | None,
) -> Iterator[tuple[Sequence[Any], int, Any]]:
    """Yield ``(parent_nodelist, index, node)`` triples recursively.

    Recurses into environment bodies, group contents, math-node contents,
    and macro-argument group contents so sibling-adjacency checks work
    inside, e.g., ``\\emph{...}``.
    """
    if not nodelist:
        return
    for idx, node in enumerate(nodelist):
        yield (nodelist, idx, node)
        if isinstance(node, (LatexEnvironmentNode, LatexGroupNode, LatexMathNode)):
            yield from _iter_with_parent(node.nodelist)
        elif isinstance(node, LatexMacroNode) and node.nodeargd:
            for arg in node.nodeargd.argnlist:
                if isinstance(arg, LatexGroupNode):
                    yield from _iter_with_parent(arg.nodelist)


def _group_plain_text(group: LatexGroupNode) -> str:
    """Return the concatenated chars of a group's immediate children."""
    return "".join(
        child.chars for child in (group.nodelist or ())
        if isinstance(child, LatexCharsNode)
    ).strip()


def _macro_first_group_arg(
    macro: LatexMacroNode,
    parent_nodelist: Sequence[Any],
    idx: int,
) -> LatexGroupNode | None:
    """Locate the first braced-group arg of ``macro``.

    For pylatexenc-recognised macros (``\\cite``, ``\\emph``, ...), the
    arg lives in ``macro.nodeargd.argnlist``. For macros unknown to
    pylatexenc's default context (``\\pkg``, ``\\proglang``, ``\\code``,
    ...), the braced group appears as the next sibling in
    ``parent_nodelist``.
    """
    if macro.nodeargd and macro.nodeargd.argnlist:
        for arg in macro.nodeargd.argnlist:
            if isinstance(arg, LatexGroupNode):
                return arg
    if idx + 1 < len(parent_nodelist):
        nxt = parent_nodelist[idx + 1]
        if isinstance(nxt, LatexGroupNode):
            return nxt
    return None


def _lineno_col(tex: Any, pos: int) -> tuple[int, int]:
    """Resolve (line, 1-based column) from a source position."""
    line, col0 = tex.walker.pos_to_lineno_colno(pos)
    return line, col0 + 1


# ---------------------------------------------------------------------------
# JSS-CITE-001 — \emph{bibkey}
# ---------------------------------------------------------------------------


def _check_jss_citations_001(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.tex_files:
        for parent, idx, node in _iter_with_parent(tex.nodes):
            if not isinstance(node, LatexMacroNode):
                continue
            if node.macroname != "emph":
                continue
            group = _macro_first_group_arg(node, parent, idx)
            if group is None:
                continue
            arg_text = _group_plain_text(group)
            if not _BIBKEY_RE.match(arg_text):
                continue
            line, col = _lineno_col(tex, node.pos)
            yield Violation(
                file=tex.path,
                line=line,
                column=col,
                rule_id="JSS-CITE-001",
                severity=Severity.WARNING,
                message=(
                    rf"\emph{{{arg_text}}} looks like a citation key; "
                    r"use \cite{...} instead of \emph for bibliographic references."
                ),
                suggestion=rf"Replace \emph{{{arg_text}}} with \cite{{{arg_text}}}.",
                fix=None,
            )


# ---------------------------------------------------------------------------
# JSS-CITE-002 — \pkg without nearby citation
# ---------------------------------------------------------------------------


def _check_jss_citations_002(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.tex_files:
        pkg_by_name: dict[str, tuple[int, int]] = {}  # name -> (pos, node_idx)
        cite_positions: list[int] = []
        for parent, idx, node in _iter_with_parent(tex.nodes):
            if not isinstance(node, LatexMacroNode):
                continue
            if node.macroname == "pkg":
                group = _macro_first_group_arg(node, parent, idx)
                if group is None:
                    continue
                name = _group_plain_text(group)
                if not name:
                    continue
                # First occurrence wins — later mentions of the same
                # package are silent even if also uncited.
                pkg_by_name.setdefault(name, (node.pos, idx))
            elif node.macroname in _CITATION_MACROS:
                cite_positions.append(node.pos)

        cite_positions.sort()
        for name, (pos, _) in pkg_by_name.items():
            if _has_citation_within(pos, cite_positions, _CITE_PROXIMITY_CHARS):
                continue
            line, col = _lineno_col(tex, pos)
            yield Violation(
                file=tex.path,
                line=line,
                column=col,
                rule_id="JSS-CITE-002",
                severity=Severity.WARNING,
                message=(
                    rf"\pkg{{{name}}} is mentioned without a citation within the "
                    r"same paragraph; every software package's first mention "
                    r"should be accompanied by \cite / \citep / \citet."
                ),
                suggestion=(
                    rf"Add a citation near \pkg{{{name}}}, e.g., "
                    rf"\pkg{{{name}}} \citep{{<key>}}."
                ),
                fix=None,
            )


def _has_citation_within(pos: int, cites: Sequence[int], window: int) -> bool:
    return any(abs(cp - pos) <= window for cp in cites)


# ---------------------------------------------------------------------------
# JSS-CITE-003 — (\cite{...}) bracket-in-bracket
# ---------------------------------------------------------------------------


def _check_jss_citations_003(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.tex_files:
        for parent, idx, node in _iter_with_parent(tex.nodes):
            if not isinstance(node, LatexMacroNode):
                continue
            if node.macroname not in _CITE_TEXT_MACROS:
                continue
            if not _prev_char_ends_with_open_paren(parent, idx):
                continue
            if not _next_char_starts_with_close_paren(parent, idx):
                continue
            line, col = _lineno_col(tex, node.pos)
            yield Violation(
                file=tex.path,
                line=line,
                column=col,
                rule_id="JSS-CITE-003",
                severity=Severity.WARNING,
                message=(
                    r"(\\" + node.macroname + "{...}) produces double parentheses; "
                    r"use \citep{...} for a parenthetical citation."
                ),
                suggestion=r"Replace (\cite{...}) with \citep{...}.",
                fix=None,
            )


def _prev_char_ends_with_open_paren(parent: Sequence[Any], idx: int) -> bool:
    if idx <= 0:
        return False
    prev = parent[idx - 1]
    if not isinstance(prev, LatexCharsNode):
        return False
    return prev.chars.rstrip(" \t").endswith("(")


def _next_char_starts_with_close_paren(parent: Sequence[Any], idx: int) -> bool:
    if idx + 1 >= len(parent):
        return False
    nxt = parent[idx + 1]
    if not isinstance(nxt, LatexCharsNode):
        return False
    return nxt.chars.lstrip(" \t").startswith(")")


# ---------------------------------------------------------------------------
# JSS-CITE-004 — hardcoded (Author, YYYY) text
# ---------------------------------------------------------------------------

_HARDCODED_CITATION_RE = re.compile(
    r"""
    \(                                  # opening paren
    ([A-Z][A-Za-z-]+)                   # first author surname
    (?:                                 # optional extension:
        \s+                             #   whitespace
        (?:                             #   then either
            et\s+al\.?                  #     "et al" / "et al."
          | and\s+[A-Z][A-Za-z-]+       #     "and Secondauthor"
          | &\s+[A-Z][A-Za-z-]+         #     "& Secondauthor"
        )
    )?
    ,\s+                                # comma + whitespace
    (\d{4}[a-z]?)                       # year (optional disambiguator)
    \)                                  # closing paren
    """,
    re.VERBOSE,
)


def _check_jss_citations_004(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.tex_files:
        for _parent, _idx, node in _iter_with_parent(tex.nodes):
            if not isinstance(node, LatexCharsNode):
                continue
            for match in _HARDCODED_CITATION_RE.finditer(node.chars):
                match_pos = node.pos + match.start()
                line, col = _lineno_col(tex, match_pos)
                yield Violation(
                    file=tex.path,
                    line=line,
                    column=col,
                    rule_id="JSS-CITE-004",
                    severity=Severity.WARNING,
                    message=(
                        f"Hardcoded parenthetical citation {match.group(0)!r}; "
                        r"use natbib commands (\citet, \citep, \citealp) "
                        "so the reference back-links to refs.bib."
                    ),
                    suggestion=(
                        f"Replace {match.group(0)!r} with "
                        rf"\citep{{{match.group(1)}<Year>}} or similar."
                    ),
                    fix=None,
                )


# ---------------------------------------------------------------------------
# Rule registry
# ---------------------------------------------------------------------------


_rule_jss_cite_001 = Rule(
    id="JSS-CITE-001",
    category="citations",
    severity=Severity.WARNING,
    message_template=r"\emph used for citation markup; use \cite instead.",
    authority="style_guide",
    check=_check_jss_citations_001,
    formats=None,
)

_rule_jss_cite_002 = Rule(
    id="JSS-CITE-002",
    category="citations",
    severity=Severity.WARNING,
    message_template=r"\pkg{X} mentioned without a nearby citation.",
    authority="style_guide",
    check=_check_jss_citations_002,
    formats=None,
)

_rule_jss_cite_003 = Rule(
    id="JSS-CITE-003",
    category="citations",
    severity=Severity.WARNING,
    message_template=r"(\cite{...}) bracket-in-bracket; use \citep{...}.",
    authority="style_guide",
    check=_check_jss_citations_003,
    formats=None,
)

_rule_jss_cite_004 = Rule(
    id="JSS-CITE-004",
    category="citations",
    severity=Severity.WARNING,
    message_template=r"Hardcoded (Author, YYYY) citation; use natbib.",
    authority="jss_cls",
    check=_check_jss_citations_004,
    formats=None,
)


rules: tuple[Rule, ...] = (
    _rule_jss_cite_001,
    _rule_jss_cite_002,
    _rule_jss_cite_003,
    _rule_jss_cite_004,
)
