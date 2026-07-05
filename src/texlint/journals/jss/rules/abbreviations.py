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


# Country / region / organisation abbreviations that are unambiguously
# NOT author initials, even when followed by a capitalised word
# ("U.S. National Science Foundation", "U.K. Met Office"). Keeps
# ABBR-001 firing on these well-known forms despite the surname-like
# follower context. ``No.`` is a "Number" abbreviation that the same
# author-initial heuristic over-suppresses.
_KNOWN_DOTTED_ABBREVS: frozenset[str] = frozenset(
    {"U.S.", "U.K.", "U.N.", "E.U.", "No."}
)

# Author-initial pattern in the OPPOSITE direction: surname first,
# then the initials. Two bibliography spellings:
#   ``Cochran, W.G.``  — surname, COMMA, initials (BibTeX-rendered).
#                        Unambiguous, suppressed on the prefix alone.
#   ``Greene W.H.``    — surname, SPACE, initials, no comma (hand-rolled
#                        ``thebibliography`` lists routinely drop it:
#                        ``Greene W.H., Hensher D.A.``). This shape
#                        collides with a sentence-leading word before a
#                        real abbreviation (``The I.R.S. rules``), so it
#                        is only treated as initials when a bibliographic
#                        follower (next author's comma, a ``(year)``, or
#                        end-of-entry) confirms the author context.
_AUTHOR_SURNAME_COMMA_PREFIX_RE = re.compile(
    r"[A-Z][a-z]+(?:-[A-Z][a-z]+)*,\s+\Z"
)
_AUTHOR_SURNAME_SPACE_PREFIX_RE = re.compile(
    r"[A-Z][a-z]+(?:-[A-Z][a-z]+)*\s+\Z"
)
# Bibliographic follower confirming ``Surname W.H.`` is an author entry:
# the next author (``,``), the publication year (``(2010)``), or the end
# of the run. Prose like ``The I.R.S. rules`` fails this (lowercase word
# follows) and stays flagged.
_BIB_INITIAL_FOLLOWER_RE = re.compile(r"\s*(?:,|\(\s*\d{4}|;|$)")


# Catalogue-backed factories live in _helpers (one definition for all
# rule modules); the module-local names are kept for call-site brevity.
_violation = _helpers.tex_violation


def _looks_like_author_initial(
    chars: str, match_start: int, match_end: int, parent: Any, idx: int
) -> bool:
    """Heuristic: a dotted uppercase run that's part of an author-name
    pattern, not a generic abbreviation. Shapes:

    - ``A.B.~Simas`` / ``W.G. Cochran`` — initials BEFORE surname,
      detected by tie/space + ``[A-Z][a-z]+`` follower.
    - Pylatexenc parses ``~`` as a :class:`LatexSpecialsNode` that
      splits chars; check the second-next sibling for the surname.
    - ``J.Wiley`` — initial glued to a surname with the space dropped;
      the run is immediately followed by lower-case letters.
    - ``Cochran, W.G.`` — surname, comma, initials (suppressed on the
      prefix alone).
    - ``Greene W.H., Hensher D.A.`` — surname, space, initials, no
      comma; suppressed only when a bibliographic follower confirms it.
    """
    tail = chars[match_end : match_end + 30]
    if _AUTHOR_INITIAL_FOLLOWER_RE.match(tail):
        return True
    # ``J.Wiley`` — the run is the prefix of a longer mixed-case word
    # (an initial glued to a surname), so the next char is lower-case.
    if tail[:1].islower():
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
    head = chars[max(0, match_start - 60) : match_start]
    # ``Cochran, W.G.`` — surname + comma is unambiguously bibliographic.
    if _AUTHOR_SURNAME_COMMA_PREFIX_RE.search(head):
        return True
    # ``Greene W.H.`` — surname + space needs a bibliographic follower so
    # ``The I.R.S. rules`` (capitalised leading word + real abbrev) is
    # not mistaken for an author entry.
    if _AUTHOR_SURNAME_SPACE_PREFIX_RE.search(head) and (
        _BIB_INITIAL_FOLLOWER_RE.match(tail)
    ):
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
                # The author-initial heuristic now covers both the
                # 2-letter (``W.H.``) and 3+-letter (``R.H.B.``) forms:
                # both are author initials when they sit next to a
                # surname, and the heuristic only fires in that context.
                # Genuine abbreviations (``U.S.A.``, ``P.D.E.``) survive
                # because they appear after a lower-case word, not a
                # surname. Known country / org abbreviations (``U.S.``,
                # ``U.K.``) are never author initials even when followed
                # by a surname-shaped word, so they stay exempt.
                if (
                    raw not in _KNOWN_DOTTED_ABBREVS
                    and _looks_like_author_initial(
                        node.chars, match.start(), match.end(),
                        parent, idx,
                    )
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


_rule = _helpers.make_rule


jss_abbr_001 = _rule("JSS-ABBR-001", check_jss_abbr_001)


rules: tuple[Rule, ...] = (jss_abbr_001,)
