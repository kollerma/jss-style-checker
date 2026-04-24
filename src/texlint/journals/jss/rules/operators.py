"""Operator / math-notation rules for the JSS journal plugin.

Rules:
  - JSS-OPER-001 — symbol-plus-noun constructs like ``p-value`` use a
    typeset form ``$p$~value`` (no hyphen).
  - JSS-OPER-002 — transpose is typeset with ``\\top``, not ``^T`` or ``^\\prime``.
  - JSS-OPER-003 — display equations have no blank lines immediately
    before or after; carve-out: equation body ending with a period
    closes a sentence and doesn't need the ``%`` wrapper.
  - JSS-OPER-004 — expectation / variance / covariance / probability use
    jss.cls shortcuts ``\\E / \\VAR / \\COV / \\Prob``.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from typing import Any

from pylatexenc.latexwalker import (
    LatexCharsNode,
    LatexEnvironmentNode,
    LatexMacroNode,
    LatexMathNode,
)

from texlint.api import ParsedDocument, Rule, ToolConfig, Violation
from texlint.journals.jss import _catalogue_data
from texlint.journals.jss.rules import _helpers


# Display-math envs subject to OPER-003.
_DISPLAY_EQ_ENVS: frozenset[str] = frozenset(
    {"equation", "equation*", "align", "align*", "eqnarray", "eqnarray*",
     "gather", "gather*", "multline", "multline*"}
)

# Statistical-symbol-plus-noun constructs for OPER-001.
_SYMBOL_NOUN_RE = re.compile(
    r"\b([a-z])-(value|statistic|values|statistics)\b"
)

# Non-canonical probabilistic-function macros flagged by OPER-004.
_NONCANON_PROB_MACROS: frozenset[str] = frozenset(
    {"mathbb", "mathsf", "mathrm", "operatorname", "Pr"}
)
_NONCANON_PROB_ARGS: frozenset[str] = frozenset(
    {"E", "Var", "Cov", "P", "Prob"}
)


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


# ---------------------------------------------------------------------------
# JSS-OPER-001 — p-value / t-statistic hyphenation
# ---------------------------------------------------------------------------


def check_jss_oper_001(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.tex_files:
        for node, ancestors in _helpers._walk_with_ancestors(tex.nodes):
            if not isinstance(node, LatexCharsNode):
                continue
            if not _helpers._is_in_prose_context(ancestors):
                continue
            for match in _SYMBOL_NOUN_RE.finditer(node.chars):
                abs_pos = node.pos + match.start()
                sym, noun = match.group(1), match.group(2)
                yield _violation(
                    tex=tex,
                    pos=abs_pos,
                    rule_id="JSS-OPER-001",
                    suggestion=(
                        f"Replace {match.group(0)!r} with "
                        f"'${sym}$~{noun}' (italicized symbol, tie)."
                    ),
                )


# ---------------------------------------------------------------------------
# JSS-OPER-002 — transpose with \top
# ---------------------------------------------------------------------------


def check_jss_oper_002(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.tex_files:
        for node, ancestors in _helpers._walk_with_ancestors(tex.nodes):
            if not isinstance(node, LatexCharsNode):
                continue
            if not _helpers._is_inside_math(ancestors):
                continue
            for match in re.finditer(r"\^\s*T\b", node.chars):
                abs_pos = node.pos + match.start()
                yield _violation(
                    tex=tex,
                    pos=abs_pos,
                    rule_id="JSS-OPER-002",
                    suggestion="Use '\\top' for transpose: e.g., 'X^\\top X'.",
                )


# ---------------------------------------------------------------------------
# JSS-OPER-003 — blank lines around display equations
# ---------------------------------------------------------------------------


def check_jss_oper_003(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.tex_files:
        for parent, idx, node in _helpers._iter_with_parent(tex.nodes):
            if not (
                isinstance(node, LatexEnvironmentNode)
                and node.environmentname in _DISPLAY_EQ_ENVS
            ):
                continue
            if _equation_body_ends_with_period(node):
                continue
            before = parent[idx - 1] if idx > 0 else None
            after = parent[idx + 1] if idx + 1 < len(parent) else None
            if _chars_has_blank_lines(before) or _chars_has_blank_lines(after):
                yield _violation(
                    tex=tex,
                    pos=node.pos,
                    rule_id="JSS-OPER-003",
                    suggestion=(
                        "Remove the blank line(s) around the display "
                        "equation (add '%' after/before to suppress the "
                        "paragraph break)."
                    ),
                )


def _equation_body_ends_with_period(env: Any) -> bool:
    for child in reversed(env.nodelist or ()):
        if isinstance(child, LatexCharsNode):
            text = child.chars.rstrip()
            if not text:
                continue
            return text.endswith(".")
        # Non-chars node at the tail — we can't see a period ending.
        return False
    return False


def _chars_has_blank_lines(node: Any) -> bool:
    return isinstance(node, LatexCharsNode) and _helpers._char_has_blank_line(node)


# ---------------------------------------------------------------------------
# JSS-OPER-004 — jss.cls probabilistic shortcuts
# ---------------------------------------------------------------------------


def check_jss_oper_004(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.tex_files:
        for node, ancestors, parent, idx in _helpers._walk_with_context(
            tex.nodes
        ):
            if not isinstance(node, LatexMacroNode):
                continue
            if not _helpers._is_inside_math(ancestors):
                continue
            if node.macroname == "Pr":
                yield _violation(
                    tex=tex,
                    pos=node.pos,
                    rule_id="JSS-OPER-004",
                    suggestion="Use \\Prob from jss.cls instead of \\Pr.",
                )
                continue
            if node.macroname not in _NONCANON_PROB_MACROS:
                continue
            arg_text = _helpers._macro_args_text(node, parent, idx)
            if arg_text in _NONCANON_PROB_ARGS:
                yield _violation(
                    tex=tex,
                    pos=node.pos,
                    rule_id="JSS-OPER-004",
                    suggestion=(
                        "Use the jss.cls shortcut "
                        f"(\\E / \\VAR / \\COV / \\Prob) instead of "
                        f"\\{node.macroname}{{{arg_text}}}."
                    ),
                )


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


jss_oper_001 = _rule("JSS-OPER-001", check_jss_oper_001)
jss_oper_002 = _rule("JSS-OPER-002", check_jss_oper_002)
jss_oper_003 = _rule("JSS-OPER-003", check_jss_oper_003)
jss_oper_004 = _rule("JSS-OPER-004", check_jss_oper_004)


rules: tuple[Rule, ...] = (jss_oper_001, jss_oper_002, jss_oper_003, jss_oper_004)
