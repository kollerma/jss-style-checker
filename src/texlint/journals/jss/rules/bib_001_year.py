"""JSS-BIB-001 — every bibliography entry must declare a ``year`` field.

Authority: JSS author instructions — every bibliography entry carries the
publication year, so automated citation processing and reader lookup both work.
"""

from __future__ import annotations

from collections.abc import Iterator

from texlint.api import ParsedDocument, Rule, Severity, ToolConfig, Violation


def _check(doc: ParsedDocument, _cfg: ToolConfig) -> Iterator[Violation]:
    for bib in doc.bib_files:
        if bib.library is None:
            continue
        for entry in getattr(bib.library, "entries", ()) or ():
            fields = getattr(entry, "fields_dict", None)
            if fields is None:
                continue
            if "year" in fields:
                continue
            start = getattr(entry, "start_line", 0) or 0
            key = getattr(entry, "key", None) or "<unknown>"
            yield Violation(
                file=bib.path,
                line=start + 1,
                column=None,
                rule_id="JSS-BIB-001",
                severity=Severity.ERROR,
                message=f"Bibliography entry '{key}' is missing a year field.",
                suggestion=f"Add 'year = {{YYYY}},' to the '{key}' entry.",
                fix=None,
            )


rule = Rule(
    id="JSS-BIB-001",
    category="bibliography",
    severity=Severity.ERROR,
    message_template="Bibliography entry must declare a year field.",
    authority="JSS author instructions",
    check=_check,
    formats=frozenset({".bib"}),
)
