"""Per-rule precision report.

Phase A scope (this module):
- `compute_precision(db_path)` runs the per-rule SQL and returns a
  `PrecisionTable` plus a parse-failure count.
- `render_terminal(table)` prints a `rich.table.Table` grouped by category
  with PASS / FAIL / NOT MEASURED / NOT EXERCISED statuses.
- `run(db_path, *, by_source, csv_path)` is the CLI entry point;
  returns exit 1 if any rule is below the 0.90 threshold.

Phase B additions (`by_source` and `csv_path`) are typed in the signature
but currently raise the "not implemented" stub — see `specs/002-eval-jss-harness/tasks.md`
phases 6–7 for the follow-up work.

Threshold constant `PRECISION_THRESHOLD` is the Constitution §VI gate.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from rich.console import Console
from rich.table import Table

from eval import db


PRECISION_THRESHOLD = 0.90


# -----------------------------------------------------------------------------
# Data model
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class RuleRow:
    rule_id: str
    category: str
    tp: int
    fp: int
    pending: int
    precision: float | None  # None = "not yet measured"
    status: str              # PASS | FAIL | NOT MEASURED | NOT EXERCISED


@dataclass
class PrecisionTable:
    rows: list[RuleRow] = field(default_factory=list)
    parse_failures: int = 0

    @property
    def any_below_threshold(self) -> bool:
        return any(r.status == "FAIL" for r in self.rows)


# -----------------------------------------------------------------------------
# Computation
# -----------------------------------------------------------------------------


_PER_RULE_SQL = """
    SELECT rule_id,
           -- Any rule should have one category; pick an arbitrary row's.
           MIN(category) AS category,
           SUM(CASE WHEN verdict = 'true_positive'  THEN 1 ELSE 0 END) AS tp,
           SUM(CASE WHEN verdict = 'false_positive' THEN 1 ELSE 0 END) AS fp,
           SUM(CASE WHEN verdict IS NULL OR verdict = 'uncertain' THEN 1 ELSE 0 END) AS pending
      FROM violations
     WHERE rule_id != 'JSS-PARSE-000'
     GROUP BY rule_id
     ORDER BY MIN(category), rule_id
"""

_PARSE_FAILURE_COUNT_SQL = (
    "SELECT COUNT(*) AS c FROM violations WHERE rule_id = 'JSS-PARSE-000'"
)


def _classify(tp: int, fp: int, pending: int) -> tuple[float | None, str]:
    denom = tp + fp
    if denom == 0 and pending == 0:
        # Rule is known (has a row in violations) but none of those rows
        # are labelled or even pending — shouldn't normally happen.
        return None, "NOT EXERCISED"
    if denom == 0:
        return None, "NOT MEASURED"
    precision = tp / denom
    if precision >= PRECISION_THRESHOLD:
        return precision, "PASS"
    return precision, "FAIL"


def compute_precision(db_path: Path) -> PrecisionTable:
    cx = db.connect(db_path)
    try:
        rows: list[RuleRow] = []
        for r in cx.execute(_PER_RULE_SQL).fetchall():
            precision, status = _classify(r["tp"], r["fp"], r["pending"])
            rows.append(
                RuleRow(
                    rule_id=r["rule_id"],
                    category=r["category"] or "unknown",
                    tp=r["tp"],
                    fp=r["fp"],
                    pending=r["pending"],
                    precision=precision,
                    status=status,
                )
            )
        parse_failures = int(
            cx.execute(_PARSE_FAILURE_COUNT_SQL).fetchone()["c"]
        )
        return PrecisionTable(rows=rows, parse_failures=parse_failures)
    finally:
        cx.close()


# -----------------------------------------------------------------------------
# Rendering
# -----------------------------------------------------------------------------


_STATUS_STYLE = {
    "PASS": "green",
    "FAIL": "red",
    "NOT MEASURED": "dim",
    "NOT EXERCISED": "dim",
}


def render_terminal(table: PrecisionTable, console: Console | None = None) -> None:
    console = console or Console()

    if not table.rows:
        console.print("eval-jss: no rules observed yet. Run `eval-jss scan`.")
    else:
        t = Table(title="Per-rule precision")
        t.add_column("Category")
        t.add_column("Rule")
        t.add_column("TP", justify="right")
        t.add_column("FP", justify="right")
        t.add_column("Pending", justify="right")
        t.add_column("Precision", justify="right")
        t.add_column("Status")
        for r in table.rows:
            precision_str = f"{r.precision:.2%}" if r.precision is not None else "—"
            style = _STATUS_STYLE.get(r.status, "white")
            t.add_row(
                r.category,
                r.rule_id,
                str(r.tp),
                str(r.fp),
                str(r.pending),
                precision_str,
                f"[{style}]{r.status}[/{style}]",
            )
        console.print(t)

    if table.parse_failures:
        console.print(
            f"\n[bold]Parse failures (JSS-PARSE-000):[/bold] "
            f"{table.parse_failures} row(s) — excluded from per-rule precision."
        )


# -----------------------------------------------------------------------------
# CLI entry
# -----------------------------------------------------------------------------


def run(
    *,
    db_path: Path,
    by_source: bool = False,
    csv_path: str | None = None,
) -> int:
    if by_source:
        # Phase B — T034. Keep the stub honest.
        print("eval-jss: --by-source is Phase B — not wired yet.")
        return 2
    if csv_path is not None and csv_path != "-":
        # Phase B — T031. Keep the stub honest.
        print("eval-jss: --csv append is Phase B — not wired yet.")
        return 2

    table = compute_precision(db_path)
    render_terminal(table)
    return 1 if table.any_below_threshold else 0
