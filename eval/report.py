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

import csv
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
    # `overall` = all rows. Per-source values from papers.source:
    # cran | bioc | arxiv | jss_archive | manual. Per-format values
    # from violations.file_suffix (spec 005): tex | bib | rnw | rmd.
    source: str = "overall"


@dataclass
class PrecisionTable:
    rows: list[RuleRow] = field(default_factory=list)
    parse_failures: int = 0
    # Dimension of the non-overall rows: "source" (papers.source) or
    # "format" (violations.file_suffix). Drives the breakdown column
    # header in `render_terminal`. Irrelevant when there are no
    # non-overall rows.
    breakdown: str = "source"

    @property
    def any_below_threshold(self) -> bool:
        # Only the overall rows gate the CLI exit code — per-source/format
        # rows are a tuning aid, not a gate (research.md §"Per-source breakdown").
        return any(
            r.status == "FAIL" and r.source == "overall" for r in self.rows
        )


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

_PER_RULE_BY_SOURCE_SQL = """
    SELECT v.rule_id,
           MIN(v.category) AS category,
           p.source AS source,
           SUM(CASE WHEN v.verdict = 'true_positive'  THEN 1 ELSE 0 END) AS tp,
           SUM(CASE WHEN v.verdict = 'false_positive' THEN 1 ELSE 0 END) AS fp,
           SUM(CASE WHEN v.verdict IS NULL OR v.verdict = 'uncertain' THEN 1 ELSE 0 END) AS pending
      FROM violations v JOIN papers p ON p.id = v.paper_id
     WHERE v.rule_id != 'JSS-PARSE-000'
     GROUP BY v.rule_id, p.source
     ORDER BY MIN(v.category), v.rule_id, p.source
"""

_PER_RULE_BY_FORMAT_SQL = """
    SELECT rule_id,
           MIN(category) AS category,
           LOWER(LTRIM(COALESCE(file_suffix, ''), '.')) AS format,
           SUM(CASE WHEN verdict = 'true_positive'  THEN 1 ELSE 0 END) AS tp,
           SUM(CASE WHEN verdict = 'false_positive' THEN 1 ELSE 0 END) AS fp,
           SUM(CASE WHEN verdict IS NULL OR verdict = 'uncertain' THEN 1 ELSE 0 END) AS pending
      FROM violations
     WHERE rule_id != 'JSS-PARSE-000'
     GROUP BY rule_id, format
     ORDER BY MIN(category), rule_id, format
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
                    source="overall",
                )
            )
        parse_failures = int(
            cx.execute(_PARSE_FAILURE_COUNT_SQL).fetchone()["c"]
        )
        return PrecisionTable(rows=rows, parse_failures=parse_failures)
    finally:
        cx.close()


def compute_precision_by_format(db_path: Path) -> PrecisionTable:
    """Overall + per-format breakdown using `violations.file_suffix` (spec 005).

    Per-format rows carry the suffix in `.source` (`tex`, `rnw`, `rmd`,
    `bib`, or `""` for pre-migration rows). Only `overall` rows gate
    the CLI exit code.
    """
    overall = compute_precision(db_path)
    cx = db.connect(db_path)
    try:
        per_format_rows: list[RuleRow] = []
        for r in cx.execute(_PER_RULE_BY_FORMAT_SQL).fetchall():
            precision, status = _classify(r["tp"], r["fp"], r["pending"])
            per_format_rows.append(
                RuleRow(
                    rule_id=r["rule_id"],
                    category=r["category"] or "unknown",
                    tp=r["tp"],
                    fp=r["fp"],
                    pending=r["pending"],
                    precision=precision,
                    status=status,
                    source=r["format"] or "unknown",
                )
            )
    finally:
        cx.close()
    return PrecisionTable(
        rows=overall.rows + per_format_rows,
        parse_failures=overall.parse_failures,
        breakdown="format",
    )


def compute_precision_by_source(db_path: Path) -> PrecisionTable:
    """Overall + per-source breakdown, one `PrecisionTable` with both layers.

    Rows with `source="overall"` are gated by the 90% threshold; rows with
    a concrete source value (`cran`, `arxiv`, ...) are informational only
    (see research.md §"Per-source breakdown").
    """
    overall = compute_precision(db_path)
    cx = db.connect(db_path)
    try:
        per_source_rows: list[RuleRow] = []
        for r in cx.execute(_PER_RULE_BY_SOURCE_SQL).fetchall():
            precision, status = _classify(r["tp"], r["fp"], r["pending"])
            per_source_rows.append(
                RuleRow(
                    rule_id=r["rule_id"],
                    category=r["category"] or "unknown",
                    tp=r["tp"],
                    fp=r["fp"],
                    pending=r["pending"],
                    precision=precision,
                    status=status,
                    source=r["source"],
                )
            )
    finally:
        cx.close()
    return PrecisionTable(
        rows=overall.rows + per_source_rows,
        parse_failures=overall.parse_failures,
        breakdown="source",
    )


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

    overall_rows = [r for r in table.rows if r.source == "overall"]
    per_source_rows = [r for r in table.rows if r.source != "overall"]

    if not overall_rows:
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
        for r in overall_rows:
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

    if per_source_rows:
        is_format = table.breakdown == "format"
        title = "Per-format breakdown" if is_format else "Per-source breakdown"
        col_label = "Format" if is_format else "Source"
        t = Table(title=title)
        t.add_column(col_label)
        t.add_column("Rule")
        t.add_column("TP", justify="right")
        t.add_column("FP", justify="right")
        t.add_column("Precision", justify="right")
        t.add_column("Status")
        for r in per_source_rows:
            precision_str = f"{r.precision:.2%}" if r.precision is not None else "—"
            style = _STATUS_STYLE.get(r.status, "white")
            t.add_row(
                r.source,
                r.rule_id,
                str(r.tp),
                str(r.fp),
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


CSV_FIELDNAMES = [
    "ts",
    "tool_version",
    "rule_id",
    "category",
    "tp",
    "fp",
    "pending",
    "precision",
    "source",
    "below_threshold",
]


def _latest_tool_version(db_path: Path) -> str:
    cx = db.connect(db_path)
    try:
        row = cx.execute(
            "SELECT tool_version FROM runs ORDER BY id DESC LIMIT 1"
        ).fetchone()
    finally:
        cx.close()
    return row["tool_version"] if row else ""


def _table_to_csv_rows(
    table: PrecisionTable,
    *,
    ts: str,
    tool_version: str,
) -> list[dict]:
    """Flatten a `PrecisionTable` into CSV row dicts (one per rule per source)."""
    rows: list[dict] = []
    for r in table.rows:
        precision_s = f"{r.precision:.4f}" if r.precision is not None else ""
        below = 1 if r.status == "FAIL" else 0
        rows.append(
            {
                "ts": ts,
                "tool_version": tool_version,
                "rule_id": r.rule_id,
                "category": r.category,
                "tp": r.tp,
                "fp": r.fp,
                "pending": r.pending,
                "precision": precision_s,
                "source": r.source,
                "below_threshold": below,
            }
        )
    return rows


def append_csv(path: Path, rows: list[dict]) -> None:
    """Append `rows` to `path`; write the header if the file didn't exist."""
    write_header = not path.exists()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
        if write_header:
            writer.writeheader()
        for row in rows:
            writer.writerow(row)
        f.flush()


def run(
    *,
    db_path: Path,
    by_source: bool = False,
    by_format: bool = False,
    csv_path: str | None = None,
) -> int:
    if by_format:
        table = compute_precision_by_format(db_path)
    elif by_source:
        table = compute_precision_by_source(db_path)
    else:
        table = compute_precision(db_path)
    render_terminal(table)

    if csv_path and csv_path != "-":
        append_csv(
            Path(csv_path),
            _table_to_csv_rows(
                table,
                ts=db.now_utc(),
                tool_version=_latest_tool_version(db_path),
            ),
        )

    return 1 if table.any_below_threshold else 0
