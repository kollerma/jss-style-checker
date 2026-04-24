"""Markup rules for the JSS journal plugin.

Rules in this module:
  - JSS-MARKUP-001 — programming-language names wrapped in \\proglang{}.
  - JSS-MARKUP-002 — software-package names wrapped in \\pkg{}.
  - JSS-MARKUP-003 — inline function / argument names wrapped in \\code{}.
  - JSS-MARKUP-004 — section titles with markup supply a plain-text
    optional arg: ``\\section[plain]{markup}``.

MARKUP-001/002/003 skip math mode, verbatim envs, and content already
inside JSS markup macros (\\pkg / \\proglang / \\code / \\verb); they also
skip section titles (those are handled by MARKUP-004).
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from typing import Any

from pylatexenc.latexwalker import (
    LatexCharsNode,
    LatexGroupNode,
    LatexMacroNode,
    LatexMathNode,
)

from texlint.api import ParsedDocument, Rule, ToolConfig, Violation
from texlint.journals.jss import _catalogue_data
from texlint.journals.jss.rules import _helpers
from texlint.journals.jss.terms import LANGUAGES, R_PACKAGES


def _violation(
    *, tex: Any, pos: int, rule_id: str, suggestion: str
) -> Violation:
    meta = _catalogue_data.RULES[rule_id]
    line, col = _helpers._lineno_col(tex, pos)
    return Violation(
        file=tex.path,
        line=line,
        column=col,
        rule_id=rule_id,
        severity=meta["severity"],
        message=meta["message_template"],
        suggestion=suggestion,
        fix=None,
    )


_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9+\-]*")


def _iter_tokens_in_chars(chars: str) -> Iterator[tuple[int, str]]:
    """Yield ``(start_offset, token)`` for every word-like token."""
    for match in _TOKEN_RE.finditer(chars):
        yield match.start(), match.group(0)


def _is_initial(chars: str, offset: int) -> bool:
    """True when the token at ``offset`` is a single letter followed by '.'.

    Captures "J. R. Statistical" (initials) so single-letter languages
    like R / C don't false-positive.
    """
    tail_start = offset + 1
    # Single-letter token whose next char is a period.
    return tail_start < len(chars) and chars[tail_start] == "."


# ---------------------------------------------------------------------------
# JSS-MARKUP-001 / MARKUP-002 — language / package names in prose
# ---------------------------------------------------------------------------


def _check_bare_terms(
    doc: ParsedDocument,
    *,
    terms: frozenset[str],
    rule_id: str,
    wrap_macro: str,
    skip_initials: bool,
) -> Iterator[Violation]:
    for tex in doc.all_tex_like():
        for node, ancestors in _helpers._walk_with_ancestors(tex.nodes):
            if not isinstance(node, LatexCharsNode):
                continue
            if not _helpers._is_in_prose_context(ancestors):
                continue
            for offset, token in _iter_tokens_in_chars(node.chars):
                if token not in terms:
                    continue
                if skip_initials and len(token) == 1 and _is_initial(
                    node.chars, offset
                ):
                    continue
                abs_pos = node.pos + offset
                yield _violation(
                    tex=tex,
                    pos=abs_pos,
                    rule_id=rule_id,
                    suggestion=(
                        f"Wrap {token!r} in \\{wrap_macro}{{{token}}}."
                    ),
                )


def check_jss_markup_001(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    yield from _check_bare_terms(
        doc, terms=LANGUAGES, rule_id="JSS-MARKUP-001",
        wrap_macro="proglang", skip_initials=True,
    )


def check_jss_markup_002(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    yield from _check_bare_terms(
        doc, terms=R_PACKAGES, rule_id="JSS-MARKUP-002",
        wrap_macro="pkg", skip_initials=False,
    )


# ---------------------------------------------------------------------------
# JSS-MARKUP-003 — inline function / argument names
# ---------------------------------------------------------------------------


_FUNCTION_CALL_RE = re.compile(r"\b[a-zA-Z][a-zA-Z0-9_.]*\(\s*\)")


def check_jss_markup_003(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.all_tex_like():
        for node, ancestors in _helpers._walk_with_ancestors(tex.nodes):
            if not isinstance(node, LatexCharsNode):
                continue
            if not _helpers._is_in_prose_context(ancestors):
                continue
            for match in _FUNCTION_CALL_RE.finditer(node.chars):
                abs_pos = node.pos + match.start()
                yield _violation(
                    tex=tex,
                    pos=abs_pos,
                    rule_id="JSS-MARKUP-003",
                    suggestion=(
                        f"Wrap {match.group(0)!r} in "
                        f"\\code{{{match.group(0)}}}."
                    ),
                )


# ---------------------------------------------------------------------------
# JSS-MARKUP-004 — section titles with markup need a plain-text shim
# ---------------------------------------------------------------------------


def check_jss_markup_004(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.all_tex_like():
        for _parent, _idx, node in _helpers._iter_with_parent(tex.nodes):
            if not (
                isinstance(node, LatexMacroNode)
                and node.macroname in _helpers._SECTION_MACROS
            ):
                continue
            if _has_optional_shim(node):
                continue
            if not _mandatory_arg_contains_markup(node):
                continue
            yield _violation(
                tex=tex,
                pos=node.pos,
                rule_id="JSS-MARKUP-004",
                suggestion=(
                    "Provide a plain-text section title as the optional "
                    "argument: \\section[plain]{...}."
                ),
            )


def _has_optional_shim(macro: Any) -> bool:
    argd = getattr(macro, "nodeargd", None)
    if argd is None:
        return False
    for arg in argd.argnlist or ():
        if isinstance(arg, LatexGroupNode):
            delim = getattr(arg, "delimiters", None)
            if delim and delim[0] == "[":
                return True
    return False


def _mandatory_arg_contains_markup(macro: Any) -> bool:
    argd = getattr(macro, "nodeargd", None)
    if argd is None:
        return False
    # The mandatory arg is the first non-optional group in argnlist. Since
    # _has_optional_shim already filtered away section-with-shim cases, the
    # first group here is the mandatory one.
    for arg in argd.argnlist or ():
        if not isinstance(arg, LatexGroupNode):
            continue
        for node in _helpers._walk(arg.nodelist or ()):
            if isinstance(node, (LatexMacroNode, LatexMathNode)):
                return True
        return False
    return False


# ---------------------------------------------------------------------------
# Rule objects
# ---------------------------------------------------------------------------


def _rule(rule_id: str, check_fn) -> Rule:
    meta = _catalogue_data.RULES[rule_id]
    return Rule(
        id=rule_id,
        category=meta["category"],
        severity=meta["severity"],
        message_template=meta["message_template"],
        authority=meta["authority"],
        check=check_fn,
        formats=None,
    )


jss_markup_001 = _rule("JSS-MARKUP-001", check_jss_markup_001)
jss_markup_002 = _rule("JSS-MARKUP-002", check_jss_markup_002)
jss_markup_003 = _rule("JSS-MARKUP-003", check_jss_markup_003)
jss_markup_004 = _rule("JSS-MARKUP-004", check_jss_markup_004)


rules: tuple[Rule, ...] = (
    jss_markup_001,
    jss_markup_002,
    jss_markup_003,
    jss_markup_004,
)
