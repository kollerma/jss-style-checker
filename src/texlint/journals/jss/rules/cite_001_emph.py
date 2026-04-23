"""JSS-CITE-001 — flag ``\\emph{bibkey}`` (citation markup masquerading as emphasis).

Authority: JSS author instructions — bibliographic citations use ``\\cite``
and its variants; ``\\emph`` is reserved for textual emphasis.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from typing import Any

from pylatexenc.latexwalker import (
    LatexCharsNode,
    LatexEnvironmentNode,
    LatexGroupNode,
    LatexMacroNode,
    LatexMathNode,
)

from texlint.api import ParsedDocument, Rule, Severity, ToolConfig, Violation

_BIBKEY = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*\d{4}$")


def _walk(nodes: Any) -> Iterator[Any]:
    # Under strict-parse, pylatexenc guarantees nodeargd is non-None on every
    # LatexMacroNode; missing-arg cases raise LatexWalkerError at parse time.
    for node in nodes or ():
        if node is None:
            continue
        yield node
        children: Any = ()
        if isinstance(node, (LatexEnvironmentNode, LatexGroupNode, LatexMathNode)):
            children = node.nodelist
        elif isinstance(node, LatexMacroNode):
            children = node.nodeargd.argnlist
        yield from _walk(children)


def _emph_arg_text(macro: LatexMacroNode) -> str:
    argnlist = macro.nodeargd.argnlist
    first = argnlist[0] if argnlist else None
    if not isinstance(first, LatexGroupNode):
        # e.g. `\emph X` — pylatexenc binds a single LatexCharsNode as the arg.
        return ""
    return "".join(
        child.chars
        for child in (first.nodelist or ())
        if isinstance(child, LatexCharsNode)
    ).strip()


def _check(doc: ParsedDocument, _cfg: ToolConfig) -> Iterator[Violation]:
    for tex in doc.tex_files:
        for node in _walk(tex.nodes):
            if not isinstance(node, LatexMacroNode):
                continue
            if node.macroname != "emph":
                continue
            arg_text = _emph_arg_text(node)
            if not _BIBKEY.match(arg_text):
                continue
            line, col0 = tex.walker.pos_to_lineno_colno(node.pos)
            yield Violation(
                file=tex.path,
                line=line,
                column=col0 + 1,
                rule_id="JSS-CITE-001",
                severity=Severity.WARNING,
                message=(
                    rf"\emph{{{arg_text}}} looks like a citation key; "
                    r"use \cite{...} instead of \emph for bibliographic references."
                ),
                suggestion=rf"Replace \emph{{{arg_text}}} with \cite{{{arg_text}}}.",
                fix=None,
            )


rule = Rule(
    id="JSS-CITE-001",
    category="citation",
    severity=Severity.WARNING,
    message_template="\\emph used for citation markup; use \\cite instead.",
    authority="JSS author instructions",
    check=_check,
    formats=frozenset({".tex"}),
)
