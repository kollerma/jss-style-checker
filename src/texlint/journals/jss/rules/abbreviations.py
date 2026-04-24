"""Abbreviations rule for the JSS journal plugin.

Rule:
  - JSS-ABBR-001 — abbreviations are in uppercase without periods
    (e.g., "U.S.A." → "USA").
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from typing import Any

from pylatexenc.latexwalker import LatexCharsNode

from texlint.api import ParsedDocument, Rule, ToolConfig, Violation
from texlint.journals.jss import _catalogue_data
from texlint.journals.jss.rules import _helpers

# "U.S.A.", "e.g.", "i.e." and similar two-or-more-letter abbreviations
# with internal periods. We require at least two letters separated by
# periods to avoid matching things like "vs." or one-letter initials.
_DOTTED_ABBREV_RE = re.compile(
    r"\b([A-Z])\.([A-Z])(\.[A-Z])*\.?"
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


def check_jss_abbr_001(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.all_tex_like():
        for node, ancestors in _helpers._walk_with_ancestors(tex.nodes):
            if not isinstance(node, LatexCharsNode):
                continue
            if not _helpers._is_in_prose_context(ancestors):
                continue
            for match in _DOTTED_ABBREV_RE.finditer(node.chars):
                raw = match.group(0)
                collapsed = raw.replace(".", "")
                abs_pos = node.pos + match.start()
                yield _violation(
                    tex=tex,
                    pos=abs_pos,
                    rule_id="JSS-ABBR-001",
                    suggestion=(
                        f"Replace {raw!r} with {collapsed!r} (uppercase, "
                        "no periods)."
                    ),
                )


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


jss_abbr_001 = _rule("JSS-ABBR-001", check_jss_abbr_001)


rules: tuple[Rule, ...] = (jss_abbr_001,)
