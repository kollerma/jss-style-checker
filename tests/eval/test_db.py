"""Tests for `eval.db` — connection PRAGMAs, idempotent `init`, `now_utc`.

Spec: FR-005 (idempotent init), contracts/schema.md (PRAGMA contract,
FK CASCADE), data-model.md (timestamp format).
"""

from __future__ import annotations

import re
from pathlib import Path

from eval import db


def test_connect_applies_required_pragmas(tmp_db: Path) -> None:
    cx = db.connect(tmp_db)
    try:
        assert cx.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        assert cx.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
        # PRAGMA synchronous returns an integer: 1 == NORMAL.
        assert cx.execute("PRAGMA synchronous").fetchone()[0] == 1
    finally:
        cx.close()


def test_connect_uses_row_factory(tmp_db: Path) -> None:
    cx = db.connect(tmp_db)
    try:
        row = cx.execute("SELECT 1 AS x").fetchone()
        assert row["x"] == 1
    finally:
        cx.close()


def test_init_is_idempotent(tmp_path: Path) -> None:
    path = tmp_path / "idempotent.db"
    db.init(path)
    db.init(path)  # must not raise
    cx = db.connect(path)
    try:
        tables = {
            r["name"]
            for r in cx.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        assert {"papers", "runs", "violations"}.issubset(tables)
    finally:
        cx.close()


def test_init_creates_parent_dir(tmp_path: Path) -> None:
    path = tmp_path / "nested" / "dir" / "eval.db"
    db.init(path)
    assert path.exists()


def test_foreign_key_cascade_papers_to_violations(tmp_db: Path) -> None:
    cx = db.connect(tmp_db)
    try:
        cx.execute(
            "INSERT INTO runs (ts, tool_version, papers_scanned, violations_found)"
            " VALUES ('2026-04-23T00:00:00Z', '0.1.0', 0, 0)"
        )
        run_id = cx.execute("SELECT last_insert_rowid()").fetchone()[0]
        cx.execute(
            "INSERT INTO papers (path, source, status) VALUES ('p1', 'manual', 'scanned')"
        )
        paper_id = cx.execute("SELECT last_insert_rowid()").fetchone()[0]
        cx.execute(
            "INSERT INTO violations"
            " (paper_id, rule_id, category, message, severity, first_seen_run_id)"
            " VALUES (?, 'JSS-CITE-001', 'citation', 'm', 'warning', ?)",
            (paper_id, run_id),
        )
        assert cx.execute("SELECT COUNT(*) FROM violations").fetchone()[0] == 1
        cx.execute("DELETE FROM papers WHERE id = ?", (paper_id,))
        assert cx.execute("SELECT COUNT(*) FROM violations").fetchone()[0] == 0
    finally:
        cx.close()


def test_now_utc_format(tmp_path: Path) -> None:
    ts = db.now_utc()
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", ts), ts


def test_executemany_ignore_applies_or_ignore(tmp_db: Path) -> None:
    cx = db.connect(tmp_db)
    try:
        cx.execute(
            "INSERT INTO runs (ts, tool_version, papers_scanned, violations_found)"
            " VALUES ('2026-04-23T00:00:00Z', '0.1.0', 0, 0)"
        )
        run_id = cx.execute("SELECT last_insert_rowid()").fetchone()[0]
        cx.execute(
            "INSERT INTO papers (path, source, status) VALUES ('p1', 'manual', 'scanned')"
        )
        paper_id = cx.execute("SELECT last_insert_rowid()").fetchone()[0]
        rows = [
            (paper_id, "JSS-CITE-001", "citation", 3, 5, "m", "warning", run_id, "a.tex"),
            (paper_id, "JSS-CITE-001", "citation", 3, 5, "m", "warning", run_id, "a.tex"),
        ]
        db.executemany_ignore(
            cx,
            "INSERT OR IGNORE INTO violations (paper_id, rule_id, category, line, column,"
            " message, severity, first_seen_run_id, file) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            rows,
        )
        assert cx.execute("SELECT COUNT(*) FROM violations").fetchone()[0] == 1
    finally:
        cx.close()


def test_migration_adds_and_backfills_last_seen(tmp_path: Path) -> None:
    """A pre-migration DB (no last_seen_run_id) gains the column on init,
    backfilled from first_seen_run_id."""
    import sqlite3

    path = tmp_path / "legacy.db"
    # Build a minimal legacy schema WITHOUT last_seen_run_id.
    cx = sqlite3.connect(path)
    cx.executescript(
        """
        CREATE TABLE runs (id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT, tool_version TEXT, papers_scanned INT, violations_found INT);
        CREATE TABLE papers (id INTEGER PRIMARY KEY AUTOINCREMENT,
            doi TEXT, title TEXT, year INT, path TEXT, source TEXT, status TEXT);
        CREATE TABLE violations (
            id INTEGER PRIMARY KEY AUTOINCREMENT, paper_id INT, rule_id TEXT,
            category TEXT, line INT, column INT, message TEXT, severity TEXT,
            verdict TEXT, verdict_reason TEXT, reviewer TEXT,
            first_seen_run_id INT, file_suffix TEXT, file TEXT);
        INSERT INTO runs (id, ts, tool_version, papers_scanned, violations_found)
            VALUES (7, '2026-01-01T00:00:00Z', '0.1.0', 1, 1);
        INSERT INTO papers (id, path, source, status)
            VALUES (1, 'p', 'manual', 'scanned');
        INSERT INTO violations (paper_id, rule_id, category, line, message,
            severity, first_seen_run_id) VALUES (1, 'JSS-X-001', 'x', 1, 'm',
            'warning', 7);
        """
    )
    cx.commit()
    cx.close()

    db.init(path)  # runs the migration

    cx = db.connect(path)
    try:
        cols = {r["name"] for r in cx.execute("PRAGMA table_info(violations)")}
        assert "last_seen_run_id" in cols
        row = cx.execute(
            "SELECT first_seen_run_id, last_seen_run_id FROM violations"
        ).fetchone()
        assert row["last_seen_run_id"] == row["first_seen_run_id"] == 7
    finally:
        cx.close()
