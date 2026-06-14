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
    SELECT v.rule_id,
           -- Any rule should have one category; pick an arbitrary row's.
           MIN(v.category) AS category,
           SUM(CASE WHEN v.verdict = 'true_positive'  THEN 1 ELSE 0 END) AS tp,
           SUM(CASE WHEN v.verdict = 'false_positive' THEN 1 ELSE 0 END) AS fp,
           SUM(CASE WHEN v.verdict IS NULL OR v.verdict = 'uncertain' THEN 1 ELSE 0 END) AS pending
      FROM violations v JOIN papers p ON p.id = v.paper_id
     {pinned_join}
     WHERE v.rule_id != 'JSS-PARSE-000'
       -- Only count violations the tool STILL emits (latest run), so
       -- guard-silenced / fixed findings stop dragging precision down.
       -- NULL = staleness untracked (pre-migration / direct insert) →
       -- count it; the migration backfills live rows so NULL never
       -- leaks a stale row in practice.
       AND (v.last_seen_run_id = (SELECT MAX(id) FROM runs)
            OR v.last_seen_run_id IS NULL)
     GROUP BY v.rule_id
     ORDER BY MIN(v.category), v.rule_id
"""

_PER_RULE_BY_SOURCE_SQL = """
    SELECT v.rule_id,
           MIN(v.category) AS category,
           p.source AS source,
           SUM(CASE WHEN v.verdict = 'true_positive'  THEN 1 ELSE 0 END) AS tp,
           SUM(CASE WHEN v.verdict = 'false_positive' THEN 1 ELSE 0 END) AS fp,
           SUM(CASE WHEN v.verdict IS NULL OR v.verdict = 'uncertain' THEN 1 ELSE 0 END) AS pending
      FROM violations v JOIN papers p ON p.id = v.paper_id
     {pinned_join}
     WHERE v.rule_id != 'JSS-PARSE-000'
       -- Only count violations the tool STILL emits (latest run), so
       -- guard-silenced / fixed findings stop dragging precision down.
       -- NULL = staleness untracked (pre-migration / direct insert) →
       -- count it; the migration backfills live rows so NULL never
       -- leaks a stale row in practice.
       AND (v.last_seen_run_id = (SELECT MAX(id) FROM runs)
            OR v.last_seen_run_id IS NULL)
     GROUP BY v.rule_id, p.source
     ORDER BY MIN(v.category), v.rule_id, p.source
"""

_PER_RULE_BY_FORMAT_SQL = """
    SELECT v.rule_id,
           MIN(v.category) AS category,
           LOWER(LTRIM(COALESCE(v.file_suffix, ''), '.')) AS format,
           SUM(CASE WHEN v.verdict = 'true_positive'  THEN 1 ELSE 0 END) AS tp,
           SUM(CASE WHEN v.verdict = 'false_positive' THEN 1 ELSE 0 END) AS fp,
           SUM(CASE WHEN v.verdict IS NULL OR v.verdict = 'uncertain' THEN 1 ELSE 0 END) AS pending
      FROM violations v JOIN papers p ON p.id = v.paper_id
     {pinned_join}
     WHERE v.rule_id != 'JSS-PARSE-000'
       -- Only count violations the tool STILL emits (latest run), so
       -- guard-silenced / fixed findings stop dragging precision down.
       -- NULL = staleness untracked (pre-migration / direct insert) →
       -- count it; the migration backfills live rows so NULL never
       -- leaks a stale row in practice.
       AND (v.last_seen_run_id = (SELECT MAX(id) FROM runs)
            OR v.last_seen_run_id IS NULL)
     GROUP BY v.rule_id, format
     ORDER BY MIN(v.category), v.rule_id, format
"""

_PARSE_FAILURE_COUNT_SQL = (
    "SELECT COUNT(*) AS c FROM violations v JOIN papers p ON p.id = v.paper_id"
    " {pinned_join} WHERE v.rule_id = 'JSS-PARSE-000'"
    " AND (v.last_seen_run_id = (SELECT MAX(id) FROM runs)"
    "      OR v.last_seen_run_id IS NULL)"
)


def _pinned_pairs(
    manifest_path: Path, target_dir: Path
) -> list[tuple[str, str]]:
    """Return `(paper_path, source_file)` tuples matching DB columns.

    `papers.path` stores the paper directory as written by `scan.py` (e.g.
    `examples/cran_dplyr`); `violations.file` stores the paper-relative
    POSIX path (e.g. `dplyr/vignettes/rowwise.Rmd`). The manifest's
    `local_path` is the paper dir name (`cran_dplyr/`) under the corpus
    root, and `vignette_file` is already paper-relative — so we join
    `target_dir / local_path` to form the first column and pass
    `vignette_file` verbatim as the second.

    Pinning a vignette also pins every `.bib` file that sits in the
    vignette's directory on disk — the LaTeX `\\bibliography{...}` lookup
    resolves relative to the vignette, so any sibling bib is a candidate
    reference and its violations belong with the vignette's.
    """
    from eval.corpus import load_manifest

    rows = load_manifest(manifest_path)
    pairs: list[tuple[str, str]] = []
    for row in rows:
        paper_abs = (target_dir / row.local_path).resolve()
        paper_path = str(target_dir / row.local_path).rstrip("/")
        pairs.append((paper_path, row.vignette_file))

        vignette_rel = Path(row.vignette_file)
        vignette_dir_abs = paper_abs / vignette_rel.parent
        if not vignette_dir_abs.is_dir():
            continue
        for bib in sorted(vignette_dir_abs.glob("*.bib")):
            bib_rel = bib.resolve().relative_to(paper_abs).as_posix()
            pairs.append((paper_path, bib_rel))
    return pairs


def _pinned_join(pinned: list[tuple[str, str]] | None) -> tuple[str, list]:
    """Return `(SQL fragment, params)` that restricts `v`/`p` rows to the
    manifest-pinned `(papers.path, violations.file)` pairs. Empty strings
    when `pinned is None`.

    Uses SQLite's default `column1`/`column2` names for `VALUES` rows
    because SQLite does not accept the `AS alias(col1, col2)` form on
    derived tables (only on CTEs).
    """
    if pinned is None:
        return "", []
    if not pinned:
        # Empty manifest → intentionally match nothing; 1=0 keeps SQL valid.
        return (
            " JOIN (SELECT NULL AS column1, NULL AS column2 WHERE 1=0) AS pinned ON 1=1 ",
            [],
        )
    placeholders = ", ".join(["(?, ?)"] * len(pinned))
    clause = (
        f" JOIN (VALUES {placeholders}) AS pinned "
        " ON pinned.column1 = p.path AND pinned.column2 = v.file "
    )
    params = [item for pair in pinned for item in pair]
    return clause, params


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


def compute_precision(
    db_path: Path,
    *,
    pinned: list[tuple[str, str]] | None = None,
) -> PrecisionTable:
    join_sql, join_params = _pinned_join(pinned)
    per_rule = _PER_RULE_SQL.format(pinned_join=join_sql)
    parse_count_sql = _PARSE_FAILURE_COUNT_SQL.format(pinned_join=join_sql)
    cx = db.connect(db_path)
    try:
        rows: list[RuleRow] = []
        for r in cx.execute(per_rule, join_params).fetchall():
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
            cx.execute(parse_count_sql, join_params).fetchone()["c"]
        )
        return PrecisionTable(rows=rows, parse_failures=parse_failures)
    finally:
        cx.close()


def compute_precision_by_format(
    db_path: Path,
    *,
    pinned: list[tuple[str, str]] | None = None,
) -> PrecisionTable:
    """Overall + per-format breakdown using `violations.file_suffix` (spec 005).

    Per-format rows carry the suffix in `.source` (`tex`, `rnw`, `rmd`,
    `bib`, or `""` for pre-migration rows). Only `overall` rows gate
    the CLI exit code.
    """
    overall = compute_precision(db_path, pinned=pinned)
    join_sql, join_params = _pinned_join(pinned)
    per_format = _PER_RULE_BY_FORMAT_SQL.format(pinned_join=join_sql)
    cx = db.connect(db_path)
    try:
        per_format_rows: list[RuleRow] = []
        for r in cx.execute(per_format, join_params).fetchall():
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


def compute_precision_by_source(
    db_path: Path,
    *,
    pinned: list[tuple[str, str]] | None = None,
) -> PrecisionTable:
    """Overall + per-source breakdown, one `PrecisionTable` with both layers.

    Rows with `source="overall"` are gated by the 90% threshold; rows with
    a concrete source value (`cran`, `arxiv`, ...) are informational only
    (see research.md §"Per-source breakdown").
    """
    overall = compute_precision(db_path, pinned=pinned)
    join_sql, join_params = _pinned_join(pinned)
    per_source = _PER_RULE_BY_SOURCE_SQL.format(pinned_join=join_sql)
    cx = db.connect(db_path)
    try:
        per_source_rows: list[RuleRow] = []
        for r in cx.execute(per_source, join_params).fetchall():
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


def _f1(precision: float | None, recall: float | None) -> float | None:
    """Standard F1 = 2 * P * R / (P + R). Returns None when either
    component is missing or both are zero."""
    if precision is None or recall is None:
        return None
    if precision + recall == 0:
        return None
    return 2 * precision * recall / (precision + recall)


def render_terminal(
    table: PrecisionTable,
    console: Console | None = None,
    *,
    recall_per_rule: dict[str, float | None] | None = None,
) -> None:
    """Render the per-rule precision table.

    When *recall_per_rule* is provided (a ``{rule_id: recall}`` map,
    typically from ``eval.history.latest_recall_per_rule``), the
    overall table gains two columns: Recall and F1. F1 is computed
    pointwise from the precision/recall pair; cells where either is
    missing render as ``"—"``.
    """
    console = console or Console()
    recall_per_rule = recall_per_rule or {}
    show_recall = bool(recall_per_rule)

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
        if show_recall:
            t.add_column("Recall", justify="right")
            t.add_column("F1", justify="right")
        t.add_column("Status")
        for r in overall_rows:
            precision_str = f"{r.precision:.2%}" if r.precision is not None else "—"
            style = _STATUS_STYLE.get(r.status, "white")
            row = [
                r.category,
                r.rule_id,
                str(r.tp),
                str(r.fp),
                str(r.pending),
                precision_str,
            ]
            if show_recall:
                rec = recall_per_rule.get(r.rule_id)
                row.append(f"{rec:.2%}" if rec is not None else "—")
                f1 = _f1(r.precision, rec)
                row.append(f"{f1:.2%}" if f1 is not None else "—")
            row.append(f"[{style}]{r.status}[/{style}]")
            t.add_row(*row)
        if show_recall:
            # Aggregate row at the bottom: pooled precision (already
            # known) + pooled recall (sum of TP / sum of TP+FN over
            # the rules with measured recall) + F1 from the pair.
            pooled_tp = sum(r.tp for r in overall_rows)
            pooled_fp = sum(r.fp for r in overall_rows)
            agg_precision = (
                pooled_tp / (pooled_tp + pooled_fp)
                if (pooled_tp + pooled_fp) > 0
                else None
            )
            measured = [
                rec for rec in recall_per_rule.values() if rec is not None
            ]
            agg_recall = (
                sum(measured) / len(measured) if measured else None
            )
            agg_f1 = _f1(agg_precision, agg_recall)
            t.add_row(
                "[bold]aggregate[/bold]",
                "",
                str(pooled_tp),
                str(pooled_fp),
                "",
                f"{agg_precision:.2%}" if agg_precision is not None else "—",
                f"{agg_recall:.2%}" if agg_recall is not None else "—",
                f"{agg_f1:.2%}" if agg_f1 is not None else "—",
                "",
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


def render_diff(
    history_db: Path,
    against: int | None,
    console: Console | None = None,
) -> None:
    """Render a per-rule TP/FP/precision delta between two iterations.

    Compares the latest iteration in `precision-history.db` against the
    one specified by `against` (id), or the immediately-preceding one
    when `against is None`. The table only shows rules whose TP, FP,
    or status changed between the two iterations.
    """
    import sqlite3
    console = console or Console()
    if not history_db.exists():
        console.print(
            f"eval-jss: precision-history DB not found at {history_db}. "
            f"Run `eval-jss iterate record …` first."
        )
        return
    cx = sqlite3.connect(history_db)
    cx.row_factory = sqlite3.Row
    try:
        ids = [r["id"] for r in cx.execute("SELECT id FROM iterations ORDER BY id")]
        if len(ids) < 2:
            console.print(
                "eval-jss: need at least two iterations recorded "
                "to render a diff."
            )
            return
        cur_id = ids[-1]
        prev_id = against if against is not None else ids[-2]

        def _load(it_id: int) -> dict[str, sqlite3.Row]:
            rows = cx.execute(
                "SELECT rule_id, tp, fp, pending, precision, status "
                "FROM iteration_rule_stats "
                "WHERE iteration_id=? AND scope='full'",
                (it_id,),
            ).fetchall()
            return {r["rule_id"]: r for r in rows}

        prev_map = _load(prev_id)
        cur_map = _load(cur_id)

        prev_label = cx.execute(
            "SELECT label FROM iterations WHERE id=?", (prev_id,)
        ).fetchone()["label"]
        cur_label = cx.execute(
            "SELECT label FROM iterations WHERE id=?", (cur_id,)
        ).fetchone()["label"]
    finally:
        cx.close()

    table = Table(
        title=(
            f"Per-rule diff — iter {prev_id} ({prev_label}) "
            f"→ iter {cur_id} ({cur_label})"
        )
    )
    table.add_column("Rule")
    table.add_column("TP", justify="right")
    table.add_column("FP", justify="right")
    table.add_column("Precision", justify="right")
    table.add_column("Status")

    rule_ids = sorted(set(prev_map) | set(cur_map))
    rendered = 0
    for rid in rule_ids:
        a = prev_map.get(rid)
        b = cur_map.get(rid)
        a_tp = a["tp"] if a else 0
        a_fp = a["fp"] if a else 0
        b_tp = b["tp"] if b else 0
        b_fp = b["fp"] if b else 0
        a_p = a["precision"] if a else None
        b_p = b["precision"] if b else None
        a_s = a["status"] if a else "—"
        b_s = b["status"] if b else "—"
        if a_tp == b_tp and a_fp == b_fp and a_s == b_s:
            continue
        rendered += 1

        def _delta(prev: int, now: int) -> str:
            d = now - prev
            sign = f"{d:+d}" if d else "0"
            return f"{prev}→{now} ({sign})"

        def _delta_p(prev: float | None, now: float | None) -> str:
            if prev is None and now is None:
                return "—"
            ps = f"{prev:.1%}" if prev is not None else "—"
            ns = f"{now:.1%}" if now is not None else "—"
            if prev is not None and now is not None:
                pp = (now - prev) * 100
                return f"{ps}→{ns} ({pp:+.1f}pp)"
            return f"{ps}→{ns}"

        if a_s != b_s:
            status_cell = f"{a_s}→{b_s}"
        else:
            status_cell = a_s

        style = ""
        if b_s == "PASS" and a_s != "PASS":
            style = "green"
        elif b_s == "FAIL" and a_s == "PASS":
            style = "red"

        cells = [
            rid,
            _delta(a_tp, b_tp),
            _delta(a_fp, b_fp),
            _delta_p(a_p, b_p),
            f"[{style}]{status_cell}[/{style}]" if style else status_cell,
        ]
        table.add_row(*cells)

    if rendered == 0:
        console.print(
            f"No per-rule changes between iter {prev_id} and iter {cur_id}."
        )
    else:
        console.print(table)


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
    pinned_only: bool = False,
    manifest_path: Path | None = None,
    corpus_dir: Path | None = None,
    diff: bool = False,
    history_db: Path | None = None,
    against: int | None = None,
    with_recall: bool = False,
) -> int:
    if diff:
        render_diff(
            history_db or Path("eval/precision-history.db"),
            against=against,
        )
        return 0

    pinned: list[tuple[str, str]] | None = None
    if pinned_only:
        if manifest_path is None or corpus_dir is None:
            raise ValueError(
                "pinned_only=True requires both manifest_path and corpus_dir."
            )
        pinned = _pinned_pairs(manifest_path, corpus_dir)

    if by_format:
        table = compute_precision_by_format(db_path, pinned=pinned)
    elif by_source:
        table = compute_precision_by_source(db_path, pinned=pinned)
    else:
        table = compute_precision(db_path, pinned=pinned)

    recall_per_rule: dict[str, float | None] | None = None
    if with_recall:
        from eval import history as history_mod

        recall_per_rule = history_mod.latest_recall_per_rule(
            history_db or Path("eval/precision-history.db")
        )
    render_terminal(table, recall_per_rule=recall_per_rule)

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
