"""Abbreviations rule for the JSS journal plugin.

Rule:
  - JSS-ABBR-001 — abbreviations are in uppercase without periods
    (e.g., "U.S.A." → "USA").

Spec-013 cross-file migration deferred — current rule operates
per-document. The rule fires on text-pattern matches inside prose
nodes; it has no concept of "abbreviation definition" or "first
introduction" that would benefit from a project-wide pass. Author-
initial heuristics depend on the local pylatexenc node graph
(:func:`_looks_like_author_initial`), which is per-file by
construction. Until JSS-ABBR-001 grows a "definition tracking"
sub-rule (e.g., "every abbreviation must be defined on first use
across the project"), there is nothing for ``check_project`` to
do that ``check`` does not already do once per document. See
``roadmap/follow-ups.md`` Feature 013 for tracking.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from typing import Any

from pylatexenc.latexwalker import LatexCharsNode

from texlint.api import Fix, ParsedDocument, Rule, ToolConfig, Violation
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

# Author-initial pattern in the OPPOSITE direction: bibliography-style
# ``Cochran, W.G.`` — surname comes first, then a comma + space, then
# the initials. Detects the immediate ``Surname, `` prefix so the
# rule doesn't flag the trailing initials.
_AUTHOR_SURNAME_PREFIX_RE = re.compile(
    r"[A-Z][a-z]+(?:-[A-Z][a-z]+)*,\s+\Z"
)


def _violation(
    *,
    tex: Any,
    pos: int,
    rule_id: str,
    suggestion: str,
    fix: Fix | None = None,
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
        fix=fix,
    )


def _looks_like_author_initial(
    chars: str, match_start: int, match_end: int, parent: Any, idx: int
) -> bool:
    """Heuristic: a 2-letter dotted abbrev that's part of an
    author-name pattern, not a generic abbreviation. Three shapes:

    - ``A.B.~Simas`` / ``W.G. Cochran`` — initials BEFORE surname,
      detected by tie/space + ``[A-Z][a-z]+`` follower.
    - Pylatexenc parses ``~`` as a :class:`LatexSpecialsNode` that
      splits chars; check the second-next sibling for the surname.
    - ``Cochran, W.G.`` — surname BEFORE initials in a bibliography
      list, detected by ``Surname,\\s+`` prefix.
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
    # ``Cochran, W.G.`` — bibliography-style with surname first.
    head = chars[max(0, match_start - 60) : match_start]
    if _AUTHOR_SURNAME_PREFIX_RE.search(head):
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
                    node.chars, match.start(), match.end(), parent, idx
                ):
                    continue
                collapsed = raw.replace(".", "")
                abs_pos = node.pos + match.start()
                abs_end = node.pos + match.end()
                # The detection regex (_DOTTED_ABBREV_RE) only matches
                # runs of uppercase ASCII letters separated by periods
                # (``U.S.A.``, ``M.I.T.``, ``I.R.S.``). For every match
                # the canonical form is unambiguous: drop the periods.
                # Confidence is therefore "safe" across the entire
                # current detection set.
                fix = Fix(
                    start=abs_pos,
                    end=abs_end,
                    replacement=collapsed,
                    description=(
                        f"Normalize abbreviation {raw!r} to canonical "
                        f"{collapsed!r}."
                    ),
                    confidence="safe",
                )
                yield _violation(
                    tex=tex,
                    pos=abs_pos,
                    rule_id="JSS-ABBR-001",
                    suggestion=(
                        f"Replace {raw!r} with {collapsed!r} (uppercase, "
                        "no periods)."
                    ),
                    fix=fix,
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
