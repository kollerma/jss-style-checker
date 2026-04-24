"""Rich-based terminal renderer for :class:`texlint.api.ComplianceReport`.

Author mode (default): one `console.rule` banner per file that carries
violations, followed by a table of line:col / severity / rule_id / message /
suggestion. Reviewer mode (added for User Story 2): a single per-category
table with PASS / FAIL / SKIPPED status plus the overall compliance percentage.
"""

from __future__ import annotations

import sys
from collections import defaultdict

from rich.console import Console
from rich.table import Table

from texlint.api import CategoryStatus, ComplianceReport, Severity, ToolConfig, Violation

_STATUS_STYLE = {
    CategoryStatus.PASS: "green",
    CategoryStatus.FAIL: "red",
    CategoryStatus.SKIPPED: "dim",
}

_SEVERITY_STYLE = {
    Severity.ERROR: "red",
    Severity.WARNING: "yellow",
    Severity.INFO: "cyan",
}


def _console() -> Console:
    # Force a fixed width so CI / test captures are stable and the output
    # looks sensible in pipe-to-file scenarios.
    return Console(file=sys.stdout, force_terminal=False, no_color=False, width=120)


def render(report: ComplianceReport, config: ToolConfig) -> None:
    if config.mode == "reviewer":
        _render_reviewer(report)
    else:
        _render_author(report)
    if config.verbose and report.skipped_rules:
        _render_skipped_rules(report)


def _render_skipped_rules(report: ComplianceReport) -> None:
    console = _console()
    console.rule("[bold]Skipped rules[/bold]")
    table = Table(show_header=True, header_style="bold")
    table.add_column("Rule", no_wrap=True)
    table.add_column("Reason")
    for skip in report.skipped_rules:
        table.add_row(skip.rule_id, skip.reason)
    console.print(table)


def _render_author(report: ComplianceReport) -> None:
    console = _console()
    by_file: dict[str, list[Violation]] = defaultdict(list)
    for v in report.violations:
        by_file[str(v.file)].append(v)

    if not by_file:
        return

    for file_path in sorted(by_file):
        console.rule(f"[bold]{file_path}[/bold]")
        table = Table(show_header=True, header_style="bold")
        table.add_column("Line:Col", no_wrap=True)
        table.add_column("Severity", no_wrap=True)
        table.add_column("Rule", no_wrap=True)
        table.add_column("Message")
        table.add_column("Suggestion")
        for v in by_file[file_path]:
            col = "" if v.column is None else str(v.column)
            locator = f"{v.line}:{col}" if col else str(v.line)
            style = _SEVERITY_STYLE.get(v.severity, "")
            table.add_row(
                locator,
                f"[{style}]{v.severity.value}[/{style}]" if style else v.severity.value,
                v.rule_id,
                v.message,
                v.suggestion or "",
            )
        console.print(table)


def _render_reviewer(report: ComplianceReport) -> None:
    console = _console()
    table = Table(
        title=f"Journal compliance — {report.journal_id}",
        show_header=True,
        header_style="bold",
    )
    table.add_column("Category", no_wrap=True)
    table.add_column("Status", no_wrap=True)
    table.add_column("Applied", justify="right")
    table.add_column("Passed", justify="right")

    for cat in report.categories:
        style = _STATUS_STYLE.get(cat.status, "")
        status_cell = (
            f"[{style}]{cat.status.value}[/{style}]" if style else cat.status.value
        )
        table.add_row(cat.title, status_cell, str(cat.rules_applied), str(cat.rules_passed))

    console.print(table)
    pct = report.compliance_percentage
    if pct is None:
        console.print("Overall: [dim]n/a[/dim]")
    else:
        console.print(f"Overall: [bold]{pct}%[/bold]")
