"""Private shared walkers and safety helpers for JSS rule modules.

All functions are pure: same inputs → same outputs, no mutable module
state, no randomness. The module is underscore-prefixed to mark it
private to the ``rules/`` package (not part of any third-party surface).
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

_VERBATIM_ENVS: frozenset[str] = frozenset(
    {
        "verbatim",
        "Verbatim",
        "Code",
        "CodeInput",
        "CodeOutput",
        "Sinput",
        "Soutput",
        "Scode",
        "Schunk",
        "CodeChunk",
    }
)

_VERBATIM_MACROS: frozenset[str] = frozenset({"verb", "code"})


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


_BLANK_LINE_RE: "re.Pattern[str]" = re.compile(r"\n\s*\n")


def _char_has_blank_line(node: Any) -> bool:
    """True when a :class:`LatexCharsNode` contains a blank line."""
    return isinstance(node, LatexCharsNode) and bool(_BLANK_LINE_RE.search(node.chars))
