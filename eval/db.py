"""SQLite database layer for `eval-jss`.

All other modules go through `connect()` / `init()` rather than calling
`sqlite3` directly so the PRAGMA contract (WAL, foreign_keys=ON,
synchronous=NORMAL, autocommit) is enforced in one place.

Authoritative schema in `eval/schema.sql`; prose in
`specs/002-eval-jss-harness/contracts/schema.md`.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

_SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def connect(path: Path) -> sqlite3.Connection:
    """Open an `eval-jss` SQLite connection with the mandatory PRAGMAs.

    `isolation_level=None` puts the connection in autocommit mode; call
    sites use explicit `BEGIN` / `COMMIT` for multi-statement transactions.
    """
    cx = sqlite3.connect(path, isolation_level=None)
    cx.execute("PRAGMA journal_mode=WAL")
    cx.execute("PRAGMA foreign_keys=ON")
    cx.execute("PRAGMA synchronous=NORMAL")
    cx.row_factory = sqlite3.Row
    return cx


def init(path: Path) -> None:
    """Idempotently create the schema at `path`.

    Creates parent directories as needed. Safe to call on an existing DB
    (all DDL is `CREATE ... IF NOT EXISTS`). Also runs any in-place
    column / constraint migrations.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    cx = connect(path)
    try:
        cx.executescript(_SCHEMA_PATH.read_text(encoding="utf-8"))
        _migrate_violations_file_suffix(cx)
        _migrate_violations_file(cx)
        _migrate_violations_last_seen_run_id(cx)
    finally:
        cx.close()


def _migrate_violations_file_suffix(cx: sqlite3.Connection) -> None:
    """Add `violations.file_suffix` if the column is missing (spec 005)."""
    cols = {r["name"] for r in cx.execute("PRAGMA table_info(violations)").fetchall()}
    if "file_suffix" not in cols:
        cx.execute("ALTER TABLE violations ADD COLUMN file_suffix TEXT")


def _migrate_violations_last_seen_run_id(cx: sqlite3.Connection) -> None:
    """Add `violations.last_seen_run_id` if the column is missing.

    The column stays NULL on existing rows until the next `scan --force`
    re-emits each violation and stamps it with the current run id. Rows that
    never get re-stamped are stale (the tool stopped firing there) and are
    excluded from the default precision report — see
    `report._live_filter`.
    """
    cols = {r["name"] for r in cx.execute("PRAGMA table_info(violations)").fetchall()}
    if "last_seen_run_id" not in cols:
        cx.execute("ALTER TABLE violations ADD COLUMN last_seen_run_id INTEGER")


def _migrate_violations_file(cx: sqlite3.Connection) -> None:
    """Add `violations.file` and rebuild the UNIQUE constraint to include it.

    Pre-P8 databases have `UNIQUE(paper_id, rule_id, line, message)`, which
    silently collapses same-line/same-message violations across distinct
    source files within the same paper directory. The new constraint
    `UNIQUE(paper_id, rule_id, line, message, file)` preserves them.
    """
    cols = {r["name"] for r in cx.execute("PRAGMA table_info(violations)").fetchall()}
    if "file" not in cols:
        cx.execute("ALTER TABLE violations ADD COLUMN file TEXT")

    # Inspect the current UNIQUE index on violations. sqlite_master stores
    # the CREATE statement; easiest signal that migration is done is the
    # presence of `file` in the auto-index's column list.
    idx_cols: list[str] = []
    for r in cx.execute("PRAGMA index_list(violations)").fetchall():
        if not r["unique"]:
            continue
        info = cx.execute(f"PRAGMA index_info({r['name']!r})").fetchall()
        idx_cols = [c["name"] for c in info]
        # First user-defined UNIQUE wins; named auto-indexes appear in order.
        break
    if "file" in idx_cols:
        return

    # Rebuild the table with the new UNIQUE. `executescript` manages its
    # own transaction boundaries (it issues a COMMIT on entry), so no
    # explicit BEGIN/COMMIT wrapper here. Existing rows keep file=NULL.
    cx.executescript(
        """
        CREATE TABLE violations_new (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            paper_id          INTEGER NOT NULL REFERENCES papers(id) ON DELETE CASCADE,
            rule_id           TEXT    NOT NULL,
            category          TEXT    NOT NULL,
            line              INTEGER,
            column            INTEGER,
            message           TEXT    NOT NULL,
            severity          TEXT    NOT NULL,
            verdict           TEXT,
            verdict_reason    TEXT,
            reviewer          TEXT,
            first_seen_run_id INTEGER NOT NULL REFERENCES runs(id),
            file_suffix       TEXT,
            file              TEXT,
            UNIQUE(paper_id, rule_id, line, message, file)
        );
        INSERT INTO violations_new (
            id, paper_id, rule_id, category, line, column, message,
            severity, verdict, verdict_reason, reviewer,
            first_seen_run_id, file_suffix, file
        )
        SELECT
            id, paper_id, rule_id, category, line, column, message,
            severity, verdict, verdict_reason, reviewer,
            first_seen_run_id, file_suffix, file
        FROM violations;
        DROP TABLE violations;
        ALTER TABLE violations_new RENAME TO violations;
        CREATE INDEX IF NOT EXISTS idx_viol_rule    ON violations(rule_id);
        CREATE INDEX IF NOT EXISTS idx_viol_verdict ON violations(verdict);
        CREATE INDEX IF NOT EXISTS idx_viol_paper   ON violations(paper_id);
        """
    )


def now_utc() -> str:
    """ISO 8601 UTC timestamp with `Z` suffix — byte-identical across hosts."""
    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z")
    )


def executemany_ignore(
    cx: sqlite3.Connection, sql: str, rows: list[tuple]
) -> int:
    """Run `INSERT OR IGNORE ...` (or any `OR IGNORE` statement) over many rows.

    Returns the number of rows the driver reports as inserted
    (`cursor.rowcount` after `executemany`). With `INSERT OR IGNORE`, that
    is the count of rows that did not collide with an existing `UNIQUE`
    constraint.
    """
    cur = cx.executemany(sql, rows)
    return cur.rowcount
