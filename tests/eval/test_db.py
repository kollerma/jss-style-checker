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
