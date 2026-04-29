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

# Author-initial pattern: a 2-letter dotted abbrev (``W.G.``, ``A.B.``,
# ``S.D.``) immediately followed by a tie or space and a surname-like
# token. Three-letter+ abbrevs (``U.S.A.``, ``MIT``) won't match
# group(3) being None — they get a separate longer regex. This skip
# applies only to the 2-letter case where the pattern is dominated by
# author initials in JSS bibliographies / acknowledgements.
_AUTHOR_INITIAL_FOLLOWER_RE = re.compile(
    r"[~ ][A-Z][a-z]+"
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


def _looks_like_author_initial(
    chars: str, match_end: int, parent: Any, idx: int
) -> bool:
    """Heuristic: a 2-letter dotted abbrev followed by a tie or space
    plus a surname-shaped token is an author initial, not a generic
    abbreviation. ``A.B.~Simas`` / ``W.G. Cochran`` / ``S.D. Dubois``.

    Pylatexenc parses ``~`` as a :class:`LatexSpecialsNode`, splitting
    the chars there — so we may need to look at the next sibling.
    """
    tail = chars[match_end : match_end + 30]
    if _AUTHOR_INITIAL_FOLLOWER_RE.match(tail):
        return True
    # Same-line chars stops at ``~`` (a specials node). Look at the
    # next sibling: if it's a tilde-or-space specials/chars followed
    # by a chars node starting with a surname-shaped token, treat as
    # initial.
    if not chars[match_end:].rstrip(" \t"):
        # The chars node ends right at (or just after) the abbrev.
        # ``~`` is a specials node that splits chars; the surname
        # token starts in the chars two siblings later.
        sib_two = parent[idx + 2] if idx + 2 < len(parent) else None
        if isinstance(sib_two, LatexCharsNode):
            head = sib_two.chars[:30]
            if re.match(r"[A-Z][a-z]+", head):
                return True
    return False


def check_jss_abbr_001(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.all_tex_like():
        for node, ancestors, parent, idx in _helpers._walk_with_context(
            tex.nodes
        ):
            if not isinstance(node, LatexCharsNode):
                continue
            if not _helpers._is_in_prose_context(ancestors):
                continue
            for match in _DOTTED_ABBREV_RE.finditer(node.chars):
                raw = match.group(0)
                # Author-initial heuristic only applies to the
                # 2-letter form (``X.Y.``); 3+-letter abbrevs
                # (``U.S.A.``, ``Ph.D.``) are real abbreviations.
                if match.group(3) is None and _looks_like_author_initial(
                    node.chars, match.end(), parent, idx
                ):
                    continue
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
