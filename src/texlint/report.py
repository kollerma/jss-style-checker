"""Spec 015 — one-page conformance report.

Pure-Python markdown renderer for an editorial decision-letter
attachment. PDF / HTML rendering and CLI subcommand wiring are
deferred to follow-ups.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from typing import Literal

from texlint.api import ComplianceReport, Severity
from texlint.journals.jss._catalogue_data import RULES

Format = Literal["md"]

TOOL_SIDE_CATEGORIES = frozenset({"parse", "internal"})


@dataclass(frozen=True)
class TopFiveEntry:
    rule_id: str
    count: int
    example_file: str
    example_line: int
    example_excerpt: str


@dataclass(frozen=True)
class FixMeItem:
    rule_id: str
    severity: Severity
    count: int


@dataclass(frozen=True)
class ConformanceSummary:
    title: str
    author: str
    file_count: int
    run_date: str
    score_percent: int | None
    rules_passing: int
    rules_total_active: int
    error_count: int
    warning_count: int
    info_count: int
    top_five: tuple[TopFiveEntry, ...]
    fix_me_first: tuple[FixMeItem, ...]


def _active_rules(ignore_rules: Iterable[str]) -> tuple[str, ...]:
    ignored = frozenset(ignore_rules)
    return tuple(
        rid
        for rid, meta in RULES.items()
        if rid not in ignored and meta["category"] not in TOOL_SIDE_CATEGORIES
    )


def _compute_summary(
    report: ComplianceReport,
    *,
    title: str,
    author: str,
    file_count: int,
    ignore_rules: Iterable[str] = (),
) -> ConformanceSummary:
    active = _active_rules(ignore_rules)
    counts: Counter[str] = Counter(v.rule_id for v in report.violations)
    violating_active = {rid for rid in counts if rid in active}
    passing = len(active) - len(violating_active)
    total_active = len(active)
    score = round(100 * passing / total_active) if total_active else None

    severity_counts: Counter[Severity] = Counter(v.severity for v in report.violations)

    top = []
    files: dict[str, list] = defaultdict(list)
    for v in report.violations:
        files[v.rule_id].append(v)
    for rid, viols in sorted(files.items(), key=lambda x: (-len(x[1]), x[0])):
        if rid not in active:
            continue
        first = viols[0]
        top.append(
            TopFiveEntry(
                rule_id=rid,
                count=len(viols),
                example_file=str(first.file),
                example_line=first.line,
                example_excerpt=first.message[:80],
            )
        )
        if len(top) == 5:
            break

    fix_me: list[FixMeItem] = []
    by_rule_severity: dict[str, Severity] = {}
    by_rule_count: dict[str, int] = {}
    for v in report.violations:
        if v.rule_id not in active:
            continue
        by_rule_severity[v.rule_id] = v.severity
        by_rule_count[v.rule_id] = by_rule_count.get(v.rule_id, 0) + 1
    severity_order = {Severity.ERROR: 0, Severity.WARNING: 1, Severity.INFO: 2}
    for rid in sorted(
        by_rule_count.keys(),
        key=lambda r: (severity_order[by_rule_severity[r]], r),
    ):
        fix_me.append(
            FixMeItem(
                rule_id=rid,
                severity=by_rule_severity[rid],
                count=by_rule_count[rid],
            )
        )

    return ConformanceSummary(
        title=title,
        author=author,
        file_count=file_count,
        run_date=date.today().isoformat(),
        score_percent=score,
        rules_passing=passing,
        rules_total_active=total_active,
        error_count=severity_counts.get(Severity.ERROR, 0),
        warning_count=severity_counts.get(Severity.WARNING, 0),
        info_count=severity_counts.get(Severity.INFO, 0),
        top_five=tuple(top),
        fix_me_first=tuple(fix_me),
    )


def _render_md(summary: ConformanceSummary) -> str:
    score = (
        f"{summary.score_percent} %" if summary.score_percent is not None else "n/a"
    )
    parts: list[str] = [
        f"# JSS conformance report — {summary.title}",
        "",
        f"- **Author:** {summary.author}",
        f"- **Files:** {summary.file_count}",
        f"- **Run date:** {summary.run_date}",
        "",
        f"## Conformance score: {score}",
        f"({summary.rules_passing} of {summary.rules_total_active} rules pass)",
        "",
        "## Severity counts",
        f"- Errors: {summary.error_count}",
        f"- Warnings: {summary.warning_count}",
        f"- Info: {summary.info_count}",
        "",
        "## Top 5 most-violated rules",
    ]
    if summary.top_five:
        for e in summary.top_five:
            parts.append(
                f"- `{e.rule_id}` — {e.count} violation(s); "
                f"{e.example_file}:{e.example_line}: {e.example_excerpt}"
            )
    else:
        parts.append("- (none)")
    parts += ["", "## Fix me first"]
    if summary.fix_me_first:
        for i, item in enumerate(summary.fix_me_first, 1):
            parts.append(
                f"{i}. `{item.rule_id}` ({item.severity.value}) — {item.count}"
            )
    else:
        parts.append("1. (no violations)")
    parts += ["", "---", "Generated by jss-lint."]
    return "\n".join(parts) + "\n"


def render_report(
    report: ComplianceReport,
    *,
    fmt: Format = "md",
    title: str = "Manuscript",
    author: str = "(unknown)",
    file_count: int = 1,
    ignore_rules: Iterable[str] = (),
) -> str:
    summary = _compute_summary(
        report,
        title=title,
        author=author,
        file_count=file_count,
        ignore_rules=ignore_rules,
    )
    if fmt == "md":
        return _render_md(summary)
    raise ValueError(f"unsupported format: {fmt}")  # pragma: no cover
