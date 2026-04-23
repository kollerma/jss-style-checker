"""JSS-SRC-001 — source lines must not exceed ``config.code_width`` code points.

Authority: JSS / ``article.tex`` style convention — long source lines degrade
reviewer / diff readability. This rule is the canonical raw-source scan
example that the framework supports (Constitution §II).
"""

from __future__ import annotations

from collections.abc import Iterator

from texlint.api import ParsedDocument, Rule, Severity, ToolConfig, Violation


def _check(doc: ParsedDocument, cfg: ToolConfig) -> Iterator[Violation]:
    limit = cfg.code_width
    for source_file in doc.all_files():
        source = source_file.source
        if not source:
            continue
        for idx, line in enumerate(source.splitlines(), start=1):
            length = len(line)
            if length <= limit:
                continue
            yield Violation(
                file=source_file.path,
                line=idx,
                column=length,
                rule_id="JSS-SRC-001",
                severity=Severity.WARNING,
                message=f"Line length {length} exceeds the {limit}-column limit.",
                suggestion=f"Wrap or reflow the line to fit in {limit} columns.",
                fix=None,
            )


rule = Rule(
    id="JSS-SRC-001",
    category="typography",
    severity=Severity.WARNING,
    message_template="Source line exceeds the configured column limit.",
    authority="article.tex / JSS style convention",
    check=_check,
    formats=None,
)
