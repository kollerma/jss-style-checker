"""Cross-reference rules for the JSS journal plugin.

Rules:
  - JSS-XREF-001 — figures / tables referenced by \\ref{}, not by number.
  - JSS-XREF-002 — equation references use ``Equation~\\ref{...}``
    rather than bare ``(\\ref{...})``.
  - JSS-XREF-003 — subsection references say "Section x.y", not
    "Subsection x.y".
  - JSS-XREF-004 — numbered equation environments carry \\label{}.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from typing import Any

from pylatexenc.latexwalker import (
    LatexCharsNode,
    LatexEnvironmentNode,
    LatexMacroNode,
)

from texlint.api import ParsedDocument, Rule, ToolConfig, Violation
from texlint.journals.jss import _catalogue_data
from texlint.journals.jss.rules import _helpers

# "Figure 2", "Table 3", "Fig. 2", "Tab. 3" followed by a number (not
# followed by a ref macro).
_FIG_TAB_NUMBER_RE = re.compile(
    r"\b(?:Figure|Fig\.|Figures|Table|Tab\.|Tables)\s+\d+",
)

# "Subsection 3.2" / "Subsection~3.2" — needs replacement with "Section".
_SUBSECTION_RE = re.compile(r"\bSubsection[s]?\s*~?\s*\d", flags=re.ASCII)

# Numbered equation environments (unlabelled ones trigger XREF-004).
_NUMBERED_EQ_ENVS: frozenset[str] = frozenset(
    {"equation", "align", "eqnarray", "gather", "multline"}
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
# JSS-XREF-001 — Figure/Table N by number
# ---------------------------------------------------------------------------


def check_jss_xref_001(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.all_tex_like():
        for node, ancestors in _helpers._walk_with_ancestors(tex.nodes):
            if not isinstance(node, LatexCharsNode):
                continue
            if not _helpers._is_in_prose_context(ancestors):
                continue
            for match in _FIG_TAB_NUMBER_RE.finditer(node.chars):
                abs_pos = node.pos + match.start()
                yield _violation(
                    tex=tex,
                    pos=abs_pos,
                    rule_id="JSS-XREF-001",
                    suggestion=(
                        f"Replace {match.group(0)!r} with "
                        f"'{match.group(0).split()[0]}~\\ref{{<label>}}'."
                    ),
                )


# ---------------------------------------------------------------------------
# JSS-XREF-002 — (\ref{...}) paren-wrapped
# ---------------------------------------------------------------------------


def _chars_ends_with_open_paren(node: Any) -> bool:
    if not isinstance(node, LatexCharsNode):
        return False
    text = node.chars.rstrip(" \t\n")
    return text.endswith("(")


def _chars_starts_with_close_paren(node: Any) -> bool:
    if not isinstance(node, LatexCharsNode):
        return False
    text = node.chars.lstrip(" \t\n")
    return text.startswith(")")


def check_jss_xref_002(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.all_tex_like():
        for parent, idx, node in _helpers._iter_with_parent(tex.nodes):
            if not (
                isinstance(node, LatexMacroNode) and node.macroname == "ref"
            ):
                continue
            before = parent[idx - 1] if idx > 0 else None
            after = parent[idx + 1] if idx + 1 < len(parent) else None
            if not _chars_ends_with_open_paren(before):
                continue
            if not _chars_starts_with_close_paren(after):
                continue
            yield _violation(
                tex=tex,
                pos=node.pos,
                rule_id="JSS-XREF-002",
                suggestion=(
                    "Replace '(\\ref{...})' with 'Equation~\\ref{...}' "
                    "(capitalised, non-breaking space)."
                ),
            )


# ---------------------------------------------------------------------------
# JSS-XREF-003 — "Subsection N.N" → "Section N.N"
# ---------------------------------------------------------------------------


def check_jss_xref_003(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.all_tex_like():
        for node, ancestors in _helpers._walk_with_ancestors(tex.nodes):
            if not isinstance(node, LatexCharsNode):
                continue
            if not _helpers._is_in_prose_context(ancestors):
                continue
            for match in _SUBSECTION_RE.finditer(node.chars):
                abs_pos = node.pos + match.start()
                yield _violation(
                    tex=tex,
                    pos=abs_pos,
                    rule_id="JSS-XREF-003",
                    suggestion=(
                        "Use 'Section N.N' (or 'Section~\\ref{<label>}'), "
                        "not 'Subsection N.N'."
                    ),
                )


# ---------------------------------------------------------------------------
# JSS-XREF-004 — numbered equation missing \label{}
# ---------------------------------------------------------------------------


def check_jss_xref_004(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.all_tex_like():
        for node in _helpers._walk(tex.nodes):
            if not isinstance(node, LatexEnvironmentNode):
                continue
            if node.environmentname not in _NUMBERED_EQ_ENVS:
                continue
            if _env_has_label(node):
                continue
            yield _violation(
                tex=tex,
                pos=node.pos,
                rule_id="JSS-XREF-004",
                suggestion=(
                    "Add \\label{eq:<name>} inside the equation so it can "
                    "be referenced from the text."
                ),
            )


def _env_has_label(env: Any) -> bool:
    for child in _helpers._walk(env.nodelist or ()):
        if (
            isinstance(child, LatexMacroNode)
            and child.macroname == "label"
        ):
            return True
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


jss_xref_001 = _rule("JSS-XREF-001", check_jss_xref_001)
jss_xref_002 = _rule("JSS-XREF-002", check_jss_xref_002)
jss_xref_003 = _rule("JSS-XREF-003", check_jss_xref_003)
jss_xref_004 = _rule("JSS-XREF-004", check_jss_xref_004)


rules: tuple[Rule, ...] = (jss_xref_001, jss_xref_002, jss_xref_003, jss_xref_004)
