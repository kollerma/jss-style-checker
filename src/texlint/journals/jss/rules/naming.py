"""Naming rules for the JSS journal plugin.

Rules in this module:
  - JSS-NAME-001 — programming-language names use canonical capitalisation
    (e.g., "JAVA" → "Java"); driven by terms.CANONICAL.
  - JSS-NAME-002 — BibTeX publisher / journal fields use canonical forms
    per style-guide SG-048..SG-052; driven by terms.PUBLISHER_CANONICAL
    and terms.JOURNAL_CANONICAL.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from typing import Any

from pylatexenc.latexwalker import LatexCharsNode

from texlint.api import ParsedDocument, Rule, ToolConfig, Violation
from texlint.journals.jss import _catalogue_data
from texlint.journals.jss.rules import _helpers
from texlint.journals.jss.terms import (
    CANONICAL,
    JOURNAL_CANONICAL,
    PUBLISHER_CANONICAL,
)

_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9+\-]*")


def _violation(
    *, file: Any, line: int, column: int | None, rule_id: str, suggestion: str
) -> Violation:
    meta = _catalogue_data.RULES[rule_id]
    return Violation(
        file=file,
        line=line,
        column=column,
        rule_id=rule_id,
        severity=meta["severity"],
        message=meta["message_template"],
        suggestion=suggestion,
        fix=None,
    )


# ---------------------------------------------------------------------------
# JSS-NAME-001 — language canonical capitalisation in prose
# ---------------------------------------------------------------------------


def check_jss_name_001(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.all_tex_like():
        for node, ancestors in _helpers._walk_with_ancestors(tex.nodes):
            if not isinstance(node, LatexCharsNode):
                continue
            if not _helpers._is_in_prose_context(ancestors):
                continue
            for match in _TOKEN_RE.finditer(node.chars):
                token = match.group(0)
                if token not in CANONICAL:
                    continue
                canonical = CANONICAL[token]
                abs_pos = node.pos + match.start()
                line, col = _helpers._lineno_col(tex, abs_pos)
                yield _violation(
                    file=tex.path,
                    line=line,
                    column=col,
                    rule_id="JSS-NAME-001",
                    suggestion=(
                        f"Use canonical form {canonical!r} instead of "
                        f"{token!r}."
                    ),
                )


# ---------------------------------------------------------------------------
# JSS-NAME-002 — BibTeX publisher / journal canonical forms
# ---------------------------------------------------------------------------


def _field_value(entry: Any, name: str) -> str:
    f = entry.fields_dict.get(name)
    if f is None:
        return ""
    return str(f.value).strip()


def _entry_line(entry: Any) -> int:
    start = getattr(entry, "start_line", 0) or 0
    return start + 1


def check_jss_name_002(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for bib in doc.bib_files:
        if bib.library is None:
            continue
        for entry in getattr(bib.library, "entries", ()) or ():
            publisher = _field_value(entry, "publisher")
            if publisher and publisher in PUBLISHER_CANONICAL:
                yield _violation(
                    file=bib.path,
                    line=_entry_line(entry),
                    column=None,
                    rule_id="JSS-NAME-002",
                    suggestion=(
                        f"Replace publisher {publisher!r} with "
                        f"{PUBLISHER_CANONICAL[publisher]!r}."
                    ),
                )
            journal = _field_value(entry, "journal")
            if journal and journal in JOURNAL_CANONICAL:
                yield _violation(
                    file=bib.path,
                    line=_entry_line(entry),
                    column=None,
                    rule_id="JSS-NAME-002",
                    suggestion=(
                        f"Replace journal {journal!r} with "
                        f"{JOURNAL_CANONICAL[journal]!r}."
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


jss_name_001 = _rule("JSS-NAME-001", check_jss_name_001)
jss_name_002 = _rule("JSS-NAME-002", check_jss_name_002)


rules: tuple[Rule, ...] = (jss_name_001, jss_name_002)
