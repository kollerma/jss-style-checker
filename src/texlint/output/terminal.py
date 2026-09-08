"""Rich-based terminal renderer for :class:`texlint.api.ComplianceReport`.

Author mode (default): one `console.rule` banner per file that carries
violations, followed by a table of line:col / severity / rule_id / message /
suggestion. Reviewer mode (added for User Story 2): a single per-category
table with PASS / FAIL / SKIPPED status plus the overall compliance percentage.
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

from rich.console import Console
from rich.table import Table

from texlint import coverage as coverage_module
from texlint.api import CategoryStatus, ComplianceReport, Severity, ToolConfig, Violation


def _guide_sections() -> dict[str, str]:
    """Return a mapping ``rule_id -> guide_section`` for every catalogue rule.

    Cached on first call. Sentinel rules (e.g. ``JSS-PARSE-000``) are not
    in the catalogue and absent from this dict, so a missing key signals
    "no suffix to render" without an extra check.
    """
    cached = getattr(_guide_sections, "_cache", None)
    if cached is None:
        from texlint.journals.jss._catalogue_data import RULES

        cached = {
            rid: str(meta.get("guide_section") or "") for rid, meta in RULES.items()
        }
        _guide_sections._cache = cached  # type: ignore[attr-defined]
    return cached


def _guide_suffix(rule_id: str) -> str:
    """Return ``" (see <section>)"`` for citable rules, else an empty string.

    The leading single space lets callers append the suffix unconditionally
    to an existing message without an additional separator check.
    """
    section = _guide_sections().get(rule_id, "")
    if not section or section == "internal":
        return ""
    return f" (see {section})"


def _confidences() -> dict[str, str]:
    """``rule_id -> confidence`` for rules with a narrowed tier.

    Only non-"high" tiers are kept, so a missing key means "high" and
    no marker is rendered. Cached on first call, like
    :func:`_guide_sections`.
    """
    cached = getattr(_confidences, "_cache", None)
    if cached is None:
        from texlint.journals.jss._catalogue_data import RULES

        cached = {
            rid: str(meta["confidence"])
            for rid, meta in RULES.items()
            if meta.get("confidence", "high") != "high"
        }
        _confidences._cache = cached  # type: ignore[attr-defined]
    return cached


def _confidence_suffix(rule_id: str) -> str:
    """Return a dim ``(<tier> conf.)`` marker on its own line for
    medium/low-precision rules, else an empty string.

    Surfaces the measured-precision tier under the rule id so a reader
    can weigh the finding — a low-confidence rule is right only a bit
    more often than not on the eval corpus. Rendered as a second line
    inside the (no-wrap) rule cell: ``(medium conf.)`` is no wider than
    a rule id, so the table's column geometry is unchanged.
    """
    tier = _confidences().get(rule_id)
    return f"\n[dim]({tier} conf.)[/dim]" if tier else ""


def _display_path(raw: str) -> str:
    """Return `raw` relative to CWD when possible.

    `console.rule(title)` fits the title within the terminal width and
    truncates with `…` when the title is too long, which drops the file
    extension on long absolute paths (a real problem on CI where the
    checkout lives under `/home/runner/work/<repo>/<repo>/…`). Relative
    paths are both shorter and friendlier to eyes.
    """
    try:
        return str(Path(raw).resolve().relative_to(Path.cwd()))
    except (OSError, ValueError):
        return raw

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
    if config.mode != "reviewer":
        _render_author_footer(report)
    if report.baseline is not None:
        _render_baseline(report)
    if config.verbose and report.skipped_rules:
        _render_skipped_rules(report)


def _render_not_checked(report: ComplianceReport, console: Console) -> None:
    """What the tool does *not* check, under the reviewer table.

    Only `partial` and `not_checked` rows: an out-of-scope provision was
    never checkable from source (compilability, graphics legibility,
    submission metadata), and listing all sixty-odd of them here would
    bury the handful a reviewer can act on. The closing line gives the
    full counts and points at the subcommand.
    """
    assert report.coverage is not None  # guarded by the caller
    console.rule("[bold]Not checked by jss-lint[/bold]")
    rows = coverage_module.gaps(report.coverage)
    if rows:
        table = Table(show_header=True, header_style="bold")
        table.add_column("Directive", no_wrap=True)
        table.add_column("Status", no_wrap=True)
        table.add_column("Provision")
        for directive in rows:
            table.add_row(
                directive.id,
                "partial" if directive.status == "partial" else "not checked",
                directive.provision,
            )
        console.print(table)
    console.print(
        coverage_module.counts_sentence(report.coverage), highlight=False
    )


def _min_plants(report: ComplianceReport) -> int:
    run = report.rule_set.recall
    return run.min_plants if run is not None else 0


def measured_recall_line(report: ComplianceReport) -> str | None:
    """`Measured recall: 81% (1967 annotated instances, 17 papers, run …)`.

    ``None`` for a journal that publishes no measurement — the author
    footer says so in words instead.
    """
    run = report.rule_set.recall
    if run is None:
        return None
    stat = run.stat
    day = run.run_timestamp.split("T", 1)[0]
    return (
        f"Measured recall: {stat.label(run.min_plants)} "
        f"({stat.plants} annotated instances, {run.papers} papers, run {day})"
    )


def _render_author_footer(report: ComplianceReport) -> None:
    """The statement a clean run has to carry (spec 027 FR-A-004).

    Printed on **stdout**, always — including when there are no findings
    at all. An empty report reads as an all-clear the tool has not
    earned: recall is 81 %, so roughly one in five planted defects goes
    unreported. Rationale for stdout over stderr, and for printing it
    unconditionally, is in plan §7.3 and the Complexity Tracking table:
    the terminal report *is* the report, and a saved text file of a
    clean run must not be empty.
    """
    _console().print(author_footer_text(report), highlight=False)


def author_footer_text(report: ComplianceReport) -> str:
    """The footer sentence, shared with the HTML renderer."""
    run = report.rule_set.recall
    if run is None:
        return (
            "jss-lint has no recall or coverage data for journal "
            f"{report.journal_id}."
        )
    stat = run.stat
    lines = [
        "No findings does not mean compliant. Measured recall: "
        f"{stat.label(run.min_plants)} ({stat.plants} annotated instances, "
        f"{run.papers} papers)."
    ]
    if report.coverage:
        lines.append(coverage_module.footer_sentence(report.coverage))
    return "\n".join(lines)


def _render_baseline(report: ComplianceReport) -> None:
    """One line saying what the baseline hid (`baseline-file.md` C-6).

    Printed in both modes, and in particular on an otherwise clean run:
    "no findings" and "no findings you have not already accepted" are
    different claims, and the user must be able to tell them apart.
    """
    summary = report.baseline
    assert summary is not None  # guarded by the caller
    line = (
        f"Baseline: {summary.matched} findings hidden by {summary.path} "
        f"({summary.stale} stale, {summary.unevaluated} unevaluated)"
    )
    current = report.rule_set.version
    if (
        summary.ruleset_version is not None
        and current is not None
        and summary.ruleset_version != current
    ):
        # The wording users' baselines key on may change in a minor
        # release (docs/versions.md), which strands entries silently
        # unless the two dates are named.
        line += (
            f" — written for rule set {summary.ruleset_version}, current "
            f"{current}; run --update-baseline"
        )
    _console().print(line, highlight=False)



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
        console.rule(f"[bold]{_display_path(file_path)}[/bold]")
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
                f"{v.rule_id}{_confidence_suffix(v.rule_id)}",
                f"{v.message}{_guide_suffix(v.rule_id)}",
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
    # Left-justified and no-wrap: the widest cell is `limited (n=NN)`,
    # which keeps the table inside the 120-column console so rich never
    # collapses the other columns.
    table.add_column("Recall", no_wrap=True)

    min_plants = _min_plants(report)
    for cat in report.categories:
        style = _STATUS_STYLE.get(cat.status, "")
        status_cell = (
            f"[{style}]{cat.status.value}[/{style}]" if style else cat.status.value
        )
        table.add_row(
            cat.title,
            status_cell,
            str(cat.rules_applied),
            str(cat.rules_passed),
            cat.recall.label(min_plants) if cat.recall is not None else "n/a",
        )

    console.print(table)
    pct = report.compliance_percentage
    if pct is None:
        console.print("Overall: [dim]n/a[/dim]")
    else:
        console.print(f"Overall: [bold]{pct}%[/bold]")
    line = measured_recall_line(report)
    if line is not None:
        console.print(line, highlight=False)
    if report.coverage:
        _render_not_checked(report, console)
