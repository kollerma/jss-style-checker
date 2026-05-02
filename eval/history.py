"""Precision-history store for the eval-improve loop.

`eval/precision-history.db` is a small, append-only SQLite file that
records one `iterations` row per snapshot plus a per-(scope, rule) stats
row. Separate from `eval/eval.db` so the raw violations DB can be wiped
and rebuilt without losing the precision trend.

Shape:

    iterations(
        id, ts, label, note, corpus_size, tool_version,
        full_parse_failures, pinned_parse_failures
    )
    iteration_rule_stats(
        iteration_id, scope, rule_id, category,
        tp, fp, pending, precision, status
    )

Scope is `'full'` or `'pinned'`. Every `iterations` row has both scopes
present in `iteration_rule_stats` (one set per rule). Nothing here reads
or writes `eval/eval.db`; the snapshot caller passes in fully-computed
`PrecisionTable`s.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from eval.report import PrecisionTable

_SCHEMA = """
CREATE TABLE IF NOT EXISTS iterations (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    ts                      TEXT    NOT NULL,
    label                   TEXT    NOT NULL,
    note                    TEXT,
    corpus_size             INTEGER NOT NULL,
    tool_version            TEXT    NOT NULL,
    full_parse_failures     INTEGER NOT NULL,
    pinned_parse_failures   INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS iteration_rule_stats (
    iteration_id   INTEGER NOT NULL REFERENCES iterations(id) ON DELETE CASCADE,
    scope          TEXT    NOT NULL,  -- 'full' | 'pinned'
    rule_id        TEXT    NOT NULL,
    category       TEXT    NOT NULL,
    tp             INTEGER NOT NULL,
    fp             INTEGER NOT NULL,
    pending        INTEGER NOT NULL,
    precision      REAL,
    status         TEXT    NOT NULL,
    PRIMARY KEY (iteration_id, scope, rule_id)
);

CREATE INDEX IF NOT EXISTS idx_iter_rule_rule ON iteration_rule_stats(rule_id);
"""


def connect(path: Path) -> sqlite3.Connection:
    cx = sqlite3.connect(path, isolation_level=None)
    cx.execute("PRAGMA journal_mode=WAL")
    cx.execute("PRAGMA foreign_keys=ON")
    cx.execute("PRAGMA synchronous=NORMAL")
    cx.row_factory = sqlite3.Row
    return cx


def init(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cx = connect(path)
    try:
        cx.executescript(_SCHEMA)
    finally:
        cx.close()


def record(
    db_path: Path,
    *,
    ts: str,
    label: str,
    note: str | None,
    corpus_size: int,
    tool_version: str,
    full: PrecisionTable,
    pinned: PrecisionTable,
) -> int:
    """Persist one snapshot; return the new iteration id."""
    init(db_path)
    cx = connect(db_path)
    try:
        cx.execute(
            "INSERT INTO iterations "
            "(ts, label, note, corpus_size, tool_version, "
            " full_parse_failures, pinned_parse_failures) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                ts, label, note, corpus_size, tool_version,
                full.parse_failures, pinned.parse_failures,
            ),
        )
        iteration_id = int(cx.execute("SELECT last_insert_rowid()").fetchone()[0])

        rows: list[tuple] = []
        for table, scope in ((full, "full"), (pinned, "pinned")):
            for r in table.rows:
                if r.source != "overall":
                    continue  # by-source/by-format rows are derivative
                rows.append((
                    iteration_id, scope, r.rule_id, r.category,
                    r.tp, r.fp, r.pending, r.precision, r.status,
                ))
        cx.executemany(
            "INSERT INTO iteration_rule_stats "
            "(iteration_id, scope, rule_id, category, tp, fp, pending, "
            " precision, status) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            rows,
        )
    finally:
        cx.close()
    return iteration_id


def previous(
    db_path: Path, before_id: int
) -> dict[tuple[str, str], tuple[int, int, int]]:
    """Return `{(scope, rule_id): (tp, fp, pending)}` from the latest
    iteration before `before_id`. Empty when there's no prior iteration.
    """
    if not db_path.exists():
        return {}
    cx = connect(db_path)
    try:
        prev = cx.execute(
            "SELECT id FROM iterations WHERE id < ? ORDER BY id DESC LIMIT 1",
            (before_id,),
        ).fetchone()
        if prev is None:
            return {}
        prev_id = int(prev["id"])
        out: dict[tuple[str, str], tuple[int, int, int]] = {}
        for r in cx.execute(
            "SELECT scope, rule_id, tp, fp, pending FROM iteration_rule_stats "
            "WHERE iteration_id = ?",
            (prev_id,),
        ).fetchall():
            out[(r["scope"], r["rule_id"])] = (r["tp"], r["fp"], r["pending"])
        return out
    finally:
        cx.close()


def latest_stats(
    db_path: Path,
) -> tuple[int | None, dict[tuple[str, str], tuple[int, int, int, float | None, str]]]:
    """Return ``(iteration_id, {(scope, rule_id): (tp, fp, pending, precision, status)})``
    from the most recent iteration. ``(None, {})`` when there's no history.

    Used by ``iterate guard`` to check whether the current scan
    introduces a precision regression vs. the last recorded snapshot.
    """
    if not db_path.exists():
        return None, {}
    cx = connect(db_path)
    try:
        row = cx.execute(
            "SELECT id FROM iterations ORDER BY id DESC LIMIT 1"
        ).fetchone()
        if row is None:
            return None, {}
        iter_id = int(row["id"])
        out: dict[tuple[str, str], tuple[int, int, int, float | None, str]] = {}
        for r in cx.execute(
            "SELECT scope, rule_id, tp, fp, pending, precision, status "
            "FROM iteration_rule_stats WHERE iteration_id = ?",
            (iter_id,),
        ).fetchall():
            out[(r["scope"], r["rule_id"])] = (
                r["tp"], r["fp"], r["pending"], r["precision"], r["status"],
            )
        return iter_id, out
    finally:
        cx.close()


def attempt_count_per_rule(db_path: Path) -> dict[str, int]:
    """Return ``{rule_id: count}`` for how many ``post-JSS-<RULE>-...``
    iterations have been recorded. Used by ``iterate plan`` to honour
    ``max_attempts_per_rule`` from the iteration policy.
    """
    if not db_path.exists():
        return {}
    import re
    pat = re.compile(r"^post-(JSS-[A-Z]+-\d+)\b")
    out: dict[str, int] = {}
    cx = connect(db_path)
    try:
        for r in cx.execute("SELECT label FROM iterations").fetchall():
            label = r["label"] or ""
            m = pat.match(label)
            if m is None:
                continue
            rule_id = m.group(1)
            out[rule_id] = out.get(rule_id, 0) + 1
    finally:
        cx.close()
    return out


def recent_overall_precision(
    db_path: Path, n: int,
) -> list[tuple[int, str, float]]:
    """Return ``[(iteration_id, label, overall_precision_full)]`` for
    the most recent ``n`` iterations, oldest-first within the window.

    Used by ``iterate plan`` to detect "no-progress streaks" — N
    consecutive iterations whose overall precision changed by less
    than the policy's ``min_progress_pp`` floor.
    """
    if not db_path.exists():
        return []
    cx = connect(db_path)
    try:
        rows = cx.execute(
            "SELECT id, label FROM iterations ORDER BY id DESC LIMIT ?",
            (n,),
        ).fetchall()
        out: list[tuple[int, str, float]] = []
        for r in rows:
            it_id = int(r["id"])
            stats = cx.execute(
                "SELECT SUM(tp) AS tp, SUM(fp) AS fp"
                " FROM iteration_rule_stats"
                " WHERE iteration_id = ? AND scope = 'full'",
                (it_id,),
            ).fetchone()
            tp = int(stats["tp"] or 0)
            fp = int(stats["fp"] or 0)
            prec = (tp / (tp + fp)) if (tp + fp) > 0 else 0.0
            out.append((it_id, r["label"] or "", prec))
        out.reverse()
        return out
    finally:
        cx.close()
