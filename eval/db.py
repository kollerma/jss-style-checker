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
    (all DDL is `CREATE ... IF NOT EXISTS`).
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    cx = connect(path)
    try:
        cx.executescript(_SCHEMA_PATH.read_text(encoding="utf-8"))
    finally:
        cx.close()


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
