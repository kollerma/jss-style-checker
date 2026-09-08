"""Renderers for the guide-coverage matrix (spec 027 item A).

Contract: ``specs/027-first-time-user-gaps/contracts/coverage-file.md``
C-5/C-6.

"No findings" only means something next to "here is what was looked
for". This module renders the second half: the `jss-lint coverage`
subcommand's three formats, and the "Not checked by jss-lint" block the
reviewer report ends with.

Pure string building — no I/O, no journal imports. The directives arrive
on the :class:`~texlint.api.ComplianceReport`, or from the journal's
metadata for the standalone subcommand.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Sequence

from texlint.api import CoverageCounts, CoverageDirective

#: Display order and labels. `checked` first, then the two kinds of gap,
#: then what was never checkable — the order a reader wants to walk.
_STATUS_ORDER: tuple[str, ...] = ("checked", "partial", "not_checked", "out_of_scope")

_STATUS_LABEL: dict[str, str] = {
    "checked": "checked",
    "partial": "partial",
    "not_checked": "not checked",
    "out_of_scope": "out of scope",
}

_SOURCE_LABEL: dict[str, str] = {
    "jss_cls": "jss.cls",
    "article_tex": "article.tex",
    "style_guide": "Style guide",
    "author_instructions": "Author instructions",
}


def counts_line(directives: Sequence[CoverageDirective]) -> str:
    """`76 checked, 4 partial, 3 not checked, 66 out of scope`."""
    counts = CoverageCounts.of(directives)
    return (
        f"{counts.checked} checked, {counts.partial} partial, "
        f"{counts.not_checked} not checked, {counts.out_of_scope} out of scope"
    )


def counts_sentence(directives: Sequence[CoverageDirective]) -> str:
    """The line closing the reviewer block — counts plus where to see more."""
    return f"Run jss-lint coverage for the full matrix ({counts_line(directives)})."


def footer_sentence(directives: Sequence[CoverageDirective]) -> str:
    """The author footer's second line.

    Quotes the *checkable* ratio: out-of-scope provisions were never
    checkable from source, so counting them would understate coverage as
    surely as ignoring the gaps would overstate it.
    """
    counts = CoverageCounts.of(directives)
    return (
        f"jss-lint checks {counts.covered} of {counts.checkable} guide "
        f"directives ({counts.not_checked} not checked, {counts.partial} "
        "partial). Run jss-lint coverage for the list."
    )


def gaps(directives: Iterable[CoverageDirective]) -> list[CoverageDirective]:
    """The rows the reviewer block lists: partial first, then not checked,
    each group sorted by id. Out-of-scope rows are deliberately absent —
    they are not gaps, and listing 66 of them would bury the three that
    matter."""
    ranked = {"partial": 0, "not_checked": 1}
    return sorted(
        (d for d in directives if d.status in ranked),
        key=lambda d: (ranked[d.status], d.id),
    )


def render_terminal(
    directives: Sequence[CoverageDirective], journal_id: str, ruleset_version: str | None
) -> str:
    """The `coverage` subcommand's default format."""
    if not directives:
        return f"jss-lint has no guide-coverage data for journal {journal_id}.\n"

    header = f"Guide coverage — {journal_id}"
    if ruleset_version:
        header += f" (rule set {ruleset_version})"
    # Inside `coverage` itself, pointing at `coverage` would be circular.
    out = [header, counts_line(directives), ""]

    for status in _STATUS_ORDER:
        group = sorted(
            (d for d in directives if d.status == status), key=lambda d: d.id
        )
        if not group:
            continue
        out.append(f"{_STATUS_LABEL[status]} ({len(group)})")
        for directive in group:
            out.append(f"  {directive.id}  {directive.section}  {directive.provision}")
            if directive.rules:
                out.append(f"        rules: {', '.join(directive.rules)}")
            if directive.reason:
                out.append(f"        reason: {directive.reason}")
        out.append("")
    return "\n".join(out).rstrip("\n") + "\n"


def render_markdown(
    directives: Sequence[CoverageDirective], journal_id: str, ruleset_version: str | None
) -> str:
    """One table per authority — for pasting into a README or an issue."""
    if not directives:
        return f"jss-lint has no guide-coverage data for journal {journal_id}.\n"

    header = f"# Guide coverage — {journal_id}"
    if ruleset_version:
        header += f" (rule set {ruleset_version})"
    out = [header, "", counts_line(directives), ""]

    for source in _SOURCE_LABEL:
        group = sorted(
            (d for d in directives if d.source == source), key=lambda d: d.id
        )
        if not group:
            continue
        out.append(f"## {_SOURCE_LABEL[source]}")
        out.append("")
        out.append("| Directive | Status | Provision | Rules | Reason |")
        out.append("|---|---|---|---|---|")
        for directive in group:
            out.append(
                f"| {directive.id} | {_STATUS_LABEL[directive.status]} "
                f"| {_escape_pipe(directive.provision)} "
                f"| {', '.join(directive.rules) or '—'} "
                f"| {_escape_pipe(directive.reason) or '—'} |"
            )
        out.append("")
    return "\n".join(out).rstrip("\n") + "\n"


def render_json(
    directives: Sequence[CoverageDirective], journal_id: str, sources: dict
) -> str:
    """Every directive, provision text included, for tooling."""
    if not directives:
        return (
            json.dumps(
                {"journal_id": journal_id, "counts": None, "directives": []},
                indent=2,
                sort_keys=True,
            )
            + "\n"
        )
    counts = CoverageCounts.of(directives)
    payload = {
        "counts": {
            "checked": counts.checked,
            "not_checked": counts.not_checked,
            "out_of_scope": counts.out_of_scope,
            "partial": counts.partial,
        },
        "directives": [
            {
                "id": d.id,
                "provision": d.provision,
                "reason": d.reason,
                "rules": list(d.rules),
                "section": d.section,
                "source": d.source,
                "status": d.status,
            }
            for d in directives
        ],
        "journal_id": journal_id,
        "sources": sources,
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def _escape_pipe(text: str) -> str:
    return text.replace("|", "\\|")
