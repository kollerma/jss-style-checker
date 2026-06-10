"""Inline suppression directives: ``% jss-lint: ignore [RULE-IDS]``.

Authors silence a single false positive in place instead of disabling a
whole rule project-wide (``--ignore-rules`` loses every true positive
the rule would have caught elsewhere).

Directive grammar (one per comment, case-insensitive keyword)::

    ... offending construct ...  % jss-lint: ignore
    ... offending construct ...  % jss-lint: ignore JSS-MARKUP-001
    % jss-lint: ignore JSS-CAP-002, JSS-CAP-003   <- standalone: applies
    ... offending construct ...                       to the NEXT line

Semantics:

* A directive on a line with content before the ``%`` suppresses
  findings reported on that same line.
* A directive on a comment-only line suppresses findings on the next
  line (and the comment line itself).
* Rule ids after ``ignore`` restrict the suppression to those rules;
  tokens are matched by rule-id shape (``ABC-DEF-123``) so trailing
  free-text rationale is allowed. A directive with no rule-id-shaped
  token suppresses every rule on the target line.
* Parse errors (``JSS-PARSE-000``) are never suppressed — they signal
  an incomplete report, not a style finding.

Directives are read from parsed-file ``source`` text. Inside verbatim
environments the parser neutralises ``%`` before the source is stored,
so code comments can never act as directives — which is the correct
reading: they are not TeX comments.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Any

from texlint.api import ParsedDocument, Violation

#: Set member that stands for "every rule".
ALL_RULES = "*"

# A real TeX comment introducer (not an escaped ``\%``) followed by the
# directive keyword. ``%+`` tolerates ``%% jss-lint: ...`` banners.
_DIRECTIVE_RE = re.compile(
    r"(?<!\\)%+\s*jss-lint:\s*ignore\b(?P<args>[^\n]*)",
    re.IGNORECASE,
)

# Rule-id shape: dash-joined uppercase/digit segments (JSS-MARKUP-001).
# Matched against the upper-cased argument text so authors may type
# lowercase ids.
_RULE_ID_RE = re.compile(r"\b[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+\b")


def _parse_args(args: str) -> frozenset[str]:
    """Extract rule ids from the directive's trailing text.

    No rule-id-shaped token → suppress all rules (the trailing text is
    free-form rationale, e.g. ``% jss-lint: ignore -- proper noun``).
    """
    ids = frozenset(_RULE_ID_RE.findall(args.upper()))
    return ids if ids else frozenset({ALL_RULES})


def directive_lines(source: str) -> dict[int, frozenset[str]]:
    """Map 1-based line numbers to the rule ids suppressed on them.

    A value containing :data:`ALL_RULES` suppresses every rule.
    """
    out: dict[int, frozenset[str]] = {}

    def _add(line: int, ids: frozenset[str]) -> None:
        existing = out.get(line)
        out[line] = ids if existing is None else existing | ids

    for lineno, line in enumerate(source.splitlines(), start=1):
        m = _DIRECTIVE_RE.search(line)
        if m is None:
            continue
        ids = _parse_args(m.group("args"))
        _add(lineno, ids)
        if not line[: m.start()].strip():
            # Comment-only line: the directive targets the next line.
            _add(lineno + 1, ids)
    return out


def build_index(
    documents: Iterable[ParsedDocument],
) -> dict[str, dict[int, frozenset[str]]]:
    """Build a per-file suppression index across ``documents``.

    Scans tex-like sources (including raw-LaTeX islands extracted from
    ``.Rmd`` files, whose line numbers are source-authoritative) and
    ``.bib`` sources — a directive line directly above a BibTeX entry
    suppresses findings reported on the entry's first line.
    """
    index: dict[str, dict[int, frozenset[str]]] = {}

    def _merge(path: Any, source: str) -> None:
        lines = directive_lines(source)
        if not lines:
            return
        per_file = index.setdefault(str(path), {})
        for lineno, ids in lines.items():
            existing = per_file.get(lineno)
            per_file[lineno] = ids if existing is None else existing | ids

    for doc in documents:
        for tex in doc.all_tex_like():
            _merge(tex.path, tex.source)
        for bib in doc.bib_files:
            _merge(bib.path, bib.source)
    return index


def is_suppressed(
    index: dict[str, dict[int, frozenset[str]]], violation: Violation
) -> bool:
    """True when ``violation`` is silenced by an inline directive."""
    per_file = index.get(str(violation.file))
    if not per_file:
        return False
    ids = per_file.get(violation.line)
    if ids is None:
        return False
    return ALL_RULES in ids or violation.rule_id in ids
