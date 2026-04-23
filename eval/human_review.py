"""Interactive TUI for labelling violations.

Iterates violations where `verdict IS NULL OR verdict = 'uncertain'`,
shows each with a ±3-line source snippet, and prompts the reviewer for
a verdict via `rich.prompt.Prompt.ask`.

Every verdict commits immediately so a `Ctrl-C` mid-session loses at
most the violation currently on screen (spec FR-015).
"""

from __future__ import annotations

import os
from pathlib import Path

from rich.console import Console
from rich.prompt import Prompt
from rich.syntax import Syntax
from rich.table import Table

from eval import db


_CHOICES = ["t", "f", "u", "s", "q"]
_VERDICT = {
    "t": "true_positive",
    "f": "false_positive",
    "u": "uncertain",
}


def _resolve_reviewer(reviewer: str | None) -> str:
    if reviewer:
        return reviewer
    user = os.environ.get("USER", "unknown")
    return f"human:{user}"


def _source_snippet(paper_path: Path, line: int | None, window: int = 3) -> str | None:
    """Return a ±window line slice of `paper_path`'s first `.tex` file, or None."""
    if not paper_path.exists() or not paper_path.is_dir():
        return None
    tex_files = sorted(paper_path.glob("*.tex"))
    if not tex_files:
        return None
    try:
        text = tex_files[0].read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    if line is None:
        return None
    lines = text.splitlines()
    if not lines:
        return None
    start = max(1, line - window)
    end = min(len(lines), line + window)
    return "\n".join(lines[start - 1 : end])


def _render_violation(
    console: Console,
    *,
    paper_path: str,
    rule_id: str,
    category: str,
    severity: str,
    line: int | None,
    column: int | None,
    message: str,
) -> None:
    table = Table(show_header=False, box=None)
    table.add_row("Paper", paper_path)
    table.add_row("Rule", f"{rule_id}  ({category}, {severity})")
    table.add_row("Line:col", f"{line}:{column if column is not None else '-'}")
    table.add_row("Message", message)
    console.print(table)

    snippet = _source_snippet(Path(paper_path), line)
    if snippet:
        start = max(1, (line or 1) - 3)
        console.print(
            Syntax(snippet, "latex", line_numbers=True, start_line=start)
        )


def _select_violations(
    cx,
    *,
    rule_id: str | None,
    limit: int | None,
) -> list:
    """Return a list of `sqlite3.Row` violations to review."""
    sql = (
        "SELECT v.id, v.paper_id, v.rule_id, v.category, v.line, v.column,"
        " v.message, v.severity, p.path AS paper_path"
        " FROM violations v JOIN papers p ON p.id = v.paper_id"
        " WHERE (v.verdict IS NULL OR v.verdict = 'uncertain')"
    )
    params: list = []
    if rule_id:
        sql += " AND v.rule_id = ?"
        params.append(rule_id)
    sql += " ORDER BY p.path, v.line, v.id"
    if limit is not None:
        sql += " LIMIT ?"
        params.append(limit)
    return cx.execute(sql, params).fetchall()


def _write_verdict(
    cx,
    *,
    violation_id: int,
    verdict: str,
    reason: str | None,
    reviewer: str,
) -> None:
    cx.execute(
        "UPDATE violations SET verdict=?, verdict_reason=?, reviewer=? WHERE id=?",
        (verdict, reason or None, reviewer, violation_id),
    )


def run(
    *,
    db_path: Path,
    limit: int | None,
    rule_id: str | None,
    reviewer: str | None,
) -> int:
    """Interactive review loop. Returns the CLI exit code."""
    reviewer_str = _resolve_reviewer(reviewer)
    console = Console()

    cx = db.connect(db_path)
    try:
        rows = _select_violations(cx, rule_id=rule_id, limit=limit)
        if not rows:
            console.print("eval-jss: no pending violations to review.")
            return 0

        for row in rows:
            _render_violation(
                console,
                paper_path=row["paper_path"],
                rule_id=row["rule_id"],
                category=row["category"],
                severity=row["severity"],
                line=row["line"],
                column=row["column"],
                message=row["message"],
            )
            answer = Prompt.ask("Verdict [t/f/u/s/q]", choices=_CHOICES, default="u")
            if answer == "q":
                break
            if answer == "s":
                continue
            verdict_str = _VERDICT[answer]
            reason = None
            if answer in ("t", "f"):
                reason_input = Prompt.ask("Reason (optional)", default="")
                reason = reason_input.strip() or None
            _write_verdict(
                cx,
                violation_id=row["id"],
                verdict=verdict_str,
                reason=reason,
                reviewer=reviewer_str,
            )
    finally:
        cx.close()

    return 0
