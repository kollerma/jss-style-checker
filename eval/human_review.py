"""Interactive TUI for labelling violations.

Iterates violations where `verdict IS NULL OR verdict = 'uncertain'`,
shows each with a ±3-line source snippet, and prompts the reviewer for
a verdict via `rich.prompt.Prompt.ask`.

Every verdict commits immediately so a `Ctrl-C` mid-session loses at
most the violation currently on screen (spec FR-015). A `b` (back)
action re-opens the previously-decided violation; its prior state is
restored in the DB so the history stack is consistent with on-disk
state.
"""

from __future__ import annotations

import os
from pathlib import Path

from rich.console import Console
from rich.prompt import Prompt
from rich.syntax import Syntax
from rich.table import Table

from eval import db

_CHOICES = ["t", "f", "u", "s", "b", "q"]
_VERDICT = {
    "t": "true_positive",
    "f": "false_positive",
    "u": "uncertain",
}

_LEGEND = (
    "Verdicts: [bold green]t[/] true positive  ·  "
    "[bold red]f[/] false positive  ·  "
    "[yellow]u[/] uncertain (re-surfaces later)  ·  "
    "[dim]s[/] skip (no change)  ·  "
    "[cyan]b[/] back (undo previous)  ·  "
    "[bold]q[/] quit"
)


def _resolve_reviewer(reviewer: str | None) -> str:
    if reviewer:
        return reviewer
    user = os.environ.get("USER", "unknown")
    return f"human:{user}"


def _first_tex_file(paper_path: Path) -> Path | None:
    """Legacy fallback — used only when `violations.file` is NULL
    (pre-P8 rows) and no better source pointer is available.
    """
    if not paper_path.exists() or not paper_path.is_dir():
        return None
    tex_files = sorted(paper_path.glob("*.tex"))
    return tex_files[0] if tex_files else None


def _resolve_source(paper_path: str, file: str | None) -> Path | None:
    """Return the absolute path of the violation's source file.

    Prefers `violations.file` (paper-relative POSIX path captured at scan
    time). Falls back to the legacy "first .tex at the paper root"
    behaviour when `file` is NULL.
    """
    paper_dir = Path(paper_path)
    if file:
        return paper_dir / file
    return _first_tex_file(paper_dir)


_LEXER_BY_SUFFIX = {
    ".tex": "latex",
    ".Rnw": "latex",
    ".Rmd": "markdown",
    ".bib": "bibtex",
}


def source_snippet(
    paper_path: str, file: str | None, line: int | None, window: int = 3
) -> str | None:
    """Return a ±window line slice of the violation's source file."""
    src = _resolve_source(paper_path, file)
    if src is None or line is None:
        return None
    try:
        text = src.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    lines = text.splitlines()
    if not lines:
        return None
    start = max(1, line - window)
    end = min(len(lines), line + window)
    return "\n".join(lines[start - 1 : end])


def _locator(
    paper_path: str, file: str | None, line: int | None, column: int | None
) -> str:
    """Return a VS-Code-clickable ``path:line:col`` string, relative to CWD
    when possible.
    """
    src = _resolve_source(paper_path, file)
    target = src if src is not None else Path(paper_path)
    try:
        display = str(target.resolve().relative_to(Path.cwd()))
    except ValueError:
        display = str(target)
    if line is None:
        return display
    if column is None:
        return f"{display}:{line}"
    return f"{display}:{line}:{column}"


def _lexer_for(file: str | None, paper_path: str) -> str:
    """Pick a Pygments lexer by file suffix. Default: latex."""
    if file:
        suffix = Path(file).suffix
    else:
        src = _resolve_source(paper_path, None)
        suffix = src.suffix if src else ".tex"
    return _LEXER_BY_SUFFIX.get(suffix, "latex")


def _render_violation(
    console: Console,
    *,
    index: int,
    total: int,
    paper_path: str,
    file: str | None,
    rule_id: str,
    category: str,
    severity: str,
    line: int | None,
    column: int | None,
    message: str,
) -> None:
    console.rule(f"[bold]{index}/{total}[/bold]")
    locator = _locator(paper_path, file, line, column)
    table = Table(show_header=False, box=None)
    table.add_row("Location", locator)
    table.add_row("Rule", f"{rule_id}  ({category}, {severity})")
    table.add_row("Message", message)
    console.print(table)

    snippet = source_snippet(paper_path, file, line)
    if snippet:
        start = max(1, (line or 1) - 3)
        console.print(
            Syntax(
                snippet,
                _lexer_for(file, paper_path),
                line_numbers=True,
                start_line=start,
            )
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
        " v.message, v.severity, v.file, p.path AS paper_path"
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


def _read_verdict_state(cx, violation_id: int) -> tuple[str | None, str | None, str | None]:
    row = cx.execute(
        "SELECT verdict, verdict_reason, reviewer FROM violations WHERE id=?",
        (violation_id,),
    ).fetchone()
    if row is None:
        return (None, None, None)
    return (row["verdict"], row["verdict_reason"], row["reviewer"])


def _write_verdict(
    cx,
    *,
    violation_id: int,
    verdict: str | None,
    reason: str | None,
    reviewer: str | None,
) -> None:
    cx.execute(
        "UPDATE violations SET verdict=?, verdict_reason=?, reviewer=? WHERE id=?",
        (verdict, reason, reviewer, violation_id),
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

        total = len(rows)
        console.print(f"[bold]{total}[/bold] violation(s) to review.")
        console.print(_LEGEND)

        # Stack of (idx, prev_verdict, prev_reason, prev_reviewer) snapshots
        # so `b` can restore the previous violation's pre-verdict state.
        history: list[tuple[int, str | None, str | None, str | None]] = []

        idx = 0
        while idx < total:
            row = rows[idx]
            _render_violation(
                console,
                index=idx + 1,
                total=total,
                paper_path=row["paper_path"],
                file=row["file"],
                rule_id=row["rule_id"],
                category=row["category"],
                severity=row["severity"],
                line=row["line"],
                column=row["column"],
                message=row["message"],
            )
            answer = Prompt.ask("Verdict [t/f/u/s/b/q]", choices=_CHOICES, default="u")
            if answer == "q":
                break
            if answer == "s":
                idx += 1
                continue
            if answer == "b":
                if not history:
                    console.print("[dim]Nothing to undo.[/dim]")
                    continue
                prev_idx, prev_verdict, prev_reason, prev_reviewer = history.pop()
                prev_row = rows[prev_idx]
                _write_verdict(
                    cx,
                    violation_id=prev_row["id"],
                    verdict=prev_verdict,
                    reason=prev_reason,
                    reviewer=prev_reviewer,
                )
                idx = prev_idx
                continue

            # Snapshot current verdict state so `b` later can restore it.
            prev_state = _read_verdict_state(cx, row["id"])
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
            history.append((idx, *prev_state))
            idx += 1
    finally:
        cx.close()

    return 0
