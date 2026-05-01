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
    LatexGroupNode,
    LatexMacroNode,
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
    for tex in doc.all_tex_like():
        for node, ancestors in _helpers._walk_with_ancestors(tex.nodes):
            if not isinstance(node, LatexCharsNode):
                continue
            if not _helpers._is_in_prose_context(ancestors):
                continue
            for match in _SYMBOL_NOUN_RE.finditer(node.chars):
                # Skip Markdown link labels — ``[r-statistics](url)`` —
                # where the bracketed text is a site name, not a
                # statistical symbol-plus-noun construct. The Rmd
                # stripper preserves the ``[label]`` brackets but
                # blanks the URL, so the immediately-preceding ``[``
                # is a reliable signal.
                if match.start() > 0 and node.chars[match.start() - 1] == "[":
                    continue
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


# Big-operator macros whose ``^T`` is an upper bound, not a transpose:
# ``\\sum_{t=1}^T``, ``\\prod_{i=2}^T``, ``\\int_0^T``, etc. The
# transpose check should not fire on these.
# Big-operator macros whose ``^T`` is an upper bound (``\\sum_{t=1}^T``,
# ``\\prod_{i=2}^T``, ``\\int_0^T``) — not a transpose. The transpose
# check should not fire on these.
_BIG_OPERATORS: frozenset[str] = frozenset({
    "sum", "prod", "int", "iint", "iiint", "oint", "coprod",
    "bigcup", "bigcap", "bigvee", "bigwedge",
    "bigoplus", "bigotimes", "bigodot",
    "biguplus", "bigsqcup",
})


def _t_caret_follows_big_operator(
    parent: Any, idx: int, match_start: int
) -> bool:
    """True when the ``^T`` at ``parent[idx].chars[match_start]`` is the
    upper-bound caret of a preceding ``\\sum_{...}``, ``\\prod_{...}``,
    ``\\int_{...}`` (or similar) — i.e., not a transpose marker.

    pylatexenc fragments ``\\sum_{t=1}^T`` into a sibling chain like:
      [LatexMacroNode \\sum, LatexCharsNode '_', LatexGroupNode {t=1},
       LatexCharsNode '^T ...']
    or, when the caret follows directly in the same chars node, into
    a single LatexCharsNode following the ``\\sum``. Walk backwards
    through subscript-shaped siblings to find the big-operator macro.
    """
    chars = parent[idx].chars
    prefix = chars[:match_start].rstrip()
    # Strip an optional ``_{...}`` or ``_X`` subscript at the end of
    # the prefix (when caret and subscript share a chars node).
    sub_match = re.search(r"_(?:\{[^{}]*\}|[A-Za-z0-9])\s*$", prefix)
    if sub_match is not None:
        prefix = prefix[: sub_match.start()].rstrip()
    elif prefix.endswith("_"):
        prefix = prefix[:-1].rstrip()
    if prefix:
        # Other math content between the operator and the caret.
        return False
    # Walk backwards through siblings, skipping a single subscript
    # (``_`` chars + group, or ``_X`` chars) — at most one subscript
    # may sit between the big operator and ``^T``.
    j = idx - 1
    saw_subscript_token = False
    saw_subscript_group = False
    while j >= 0:
        sib = parent[j]
        if isinstance(sib, LatexMacroNode) and sib.macroname in _BIG_OPERATORS:
            return True
        if isinstance(sib, LatexGroupNode) and not saw_subscript_group:
            saw_subscript_group = True
            j -= 1
            continue
        if isinstance(sib, LatexCharsNode):
            text = sib.chars.strip()
            if not text:
                j -= 1
                continue
            if text == "_":
                j -= 1
                continue
            if text.endswith("_") and not saw_subscript_token:
                saw_subscript_token = True
                j -= 1
                continue
            if re.fullmatch(r"_[A-Za-z0-9]", text) and not saw_subscript_token:
                saw_subscript_token = True
                j -= 1
                continue
            return False
        return False
    return False


def check_jss_oper_002(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.all_tex_like():
        for node, ancestors, parent, idx in _helpers._walk_with_context(
            tex.nodes
        ):
            if not isinstance(node, LatexCharsNode):
                continue
            if not _helpers._is_inside_math(ancestors):
                continue
            for match in re.finditer(r"\^\s*T(?![A-Za-z])", node.chars):
                if _t_caret_follows_big_operator(
                    parent, idx, match.start()
                ):
                    continue
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
    for tex in doc.all_tex_like():
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
            if (
                _chars_ends_with_blank_line(before)
                or _chars_starts_with_blank_line(after)
            ):
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


# Macros that don't render a glyph in the equation body. Used by the
# trailing-period scan: ``\\begin{equation} ... a + b. \\label{eq:x}
# \\end{equation}`` should still count as period-terminated even
# though ``\\label`` sits between the period and ``\\end{}``.
_INVISIBLE_TRAILING_MACROS: frozenset[str] = frozenset({
    "label", "nonumber", "notag", "tag", "tag*",
    "ignorespaces", "ignorespacesafterend", "leavevmode",
})


def _equation_body_ends_with_period(env: Any) -> bool:
    """True if the last visible character in the equation body is ``.``.

    Walks ``env.nodelist`` in reverse, skipping whitespace and
    invisible macros (``\\label``, ``\\nonumber``, ``\\notag``, ...).
    Recurses into nested environments — the math body is often
    wrapped in ``aligned`` / ``cases`` / ``split`` etc., and the
    period sits inside the inner env.
    """
    for child in reversed(env.nodelist or ()):
        if isinstance(child, LatexCharsNode):
            text = child.chars.rstrip()
            if not text:
                continue
            return text.endswith(".")
        if (
            isinstance(child, LatexMacroNode)
            and child.macroname in _INVISIBLE_TRAILING_MACROS
        ):
            # ``\\label{...}`` and friends don't render — the
            # period-ending check should look past them.
            continue
        if isinstance(child, LatexEnvironmentNode):
            # Recurse into ``aligned`` / ``cases`` / ``split`` /
            # ``gathered`` / ``array`` etc. — the period typically
            # ends the inner env's body.
            return _equation_body_ends_with_period(child)
        # Visible non-chars node at the tail — we can't see a period
        # ending.
        return False
    return False


def _chars_ends_with_blank_line(node: Any) -> bool:
    """True when ``node``'s tail (the bit immediately before the next
    sibling) contains a blank-line separator that's NOT the
    fingerprint of a stripped Sweave / knitr chunk.

    The Rnw stripper blanks each chunk to ``\\n``-only filler; many
    consecutive newlines (≥3) signal a multi-line chunk, not normal
    paragraph spacing. We only care about a blank line in the LAST
    line or two of the preceding chars node — a blank line buried
    deep in the prose (e.g., between an earlier ``\\section{}`` and
    the next sentence) doesn't mean the equation has a blank line
    immediately before it.
    """
    if not isinstance(node, LatexCharsNode):
        return False
    chars = node.chars
    if not chars:
        return False
    # Tail = everything after the last non-whitespace character.
    tail_match = re.search(r"\S(\s*)\Z", chars)
    tail = tail_match.group(1) if tail_match else chars
    # Strip chunk-shaped runs before checking; a stripped chunk's
    # filler is structural, not paragraph spacing.
    stripped = re.sub(r"\n[ \t]*(?:\n[ \t]*){2,}", "\n", tail)
    return bool(_helpers._BLANK_LINE_RE.search(stripped))


def _chars_starts_with_blank_line(node: Any) -> bool:
    """Mirror of :func:`_chars_ends_with_blank_line` for the chars
    node immediately following the equation env."""
    if not isinstance(node, LatexCharsNode):
        return False
    chars = node.chars
    if not chars:
        return False
    head_match = re.match(r"(\s*)\S", chars)
    head = head_match.group(1) if head_match else chars
    stripped = re.sub(r"\n[ \t]*(?:\n[ \t]*){2,}", "\n", head)
    return bool(_helpers._BLANK_LINE_RE.search(stripped))


# ---------------------------------------------------------------------------
# JSS-OPER-004 — jss.cls probabilistic shortcuts
# ---------------------------------------------------------------------------


def _doc_uses_prob_macro(doc: ParsedDocument) -> bool:
    """True when any tex-like surface invokes ``\\Prob``.

    JSS reviewers accept ``\\Pr`` as canonical when the paper uses it
    consistently — papers with neither ``\\Prob`` nor a redefining
    ``\\newcommand{\\Pr}`` simply chose the LaTeX built-in. Only flag
    ``\\Pr`` when the paper also has ``\\Prob`` somewhere (inconsistent
    notation) or has a custom ``\\Pr`` redefinition that proves the
    author knows about the jss.cls variant.
    """
    for tex in doc.all_tex_like():
        for node in _helpers._walk(tex.nodes):
            if not isinstance(node, LatexMacroNode):
                continue
            if node.macroname == "Prob":
                return True
            if node.macroname in {"newcommand", "renewcommand", "providecommand"}:
                # Walk into the macro's first group arg to see if it
                # defines \Pr; pylatexenc represents the target macro
                # as a child of the def macro's argument.
                for child in _helpers._walk([node]):
                    if (
                        isinstance(child, LatexMacroNode)
                        and child.macroname == "Pr"
                        and child is not node
                    ):
                        return True
    return False


def check_jss_oper_004(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    flag_pr = _doc_uses_prob_macro(doc)
    for tex in doc.all_tex_like():
        for node, ancestors, parent, idx in _helpers._walk_with_context(
            tex.nodes
        ):
            if not isinstance(node, LatexMacroNode):
                continue
            if not _helpers._is_inside_math(ancestors):
                continue
            if node.macroname == "Pr":
                if flag_pr:
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


def _rule(rule_id: str, check_fn, formats: frozenset[str] | None = None) -> Rule:
    meta = _catalogue_data.RULES[rule_id]
    return Rule(
        id=rule_id,
        category=meta["category"],
        severity=meta["severity"],
        message_template=meta["message_template"],
        authority=meta["authority"],
        check=check_fn,
        formats=formats,
    )


jss_oper_001 = _rule("JSS-OPER-001", check_jss_oper_001)
jss_oper_002 = _rule("JSS-OPER-002", check_jss_oper_002)
# OPER-003 is structural: it walks tex_like sibling nodes around a
# display-equation env and checks for blank-line text between them. In
# .Rnw input the Rnw stripper replaces R chunks with whitespace, which
# manufactures spurious blank-line text immediately before/after the
# equation env even when the source had a chunk there. Narrow to the
# native LaTeX surface only until we have a "pre-stripped whitespace
# is figure content" signal.
jss_oper_003 = _rule(
    "JSS-OPER-003", check_jss_oper_003, formats=frozenset({"tex"})
)
jss_oper_004 = _rule("JSS-OPER-004", check_jss_oper_004)


rules: tuple[Rule, ...] = (jss_oper_001, jss_oper_002, jss_oper_003, jss_oper_004)
