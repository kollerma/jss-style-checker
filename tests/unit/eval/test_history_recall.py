"""Spec 017 — recall_history persistence tests."""

from __future__ import annotations

from pathlib import Path

from eval.history import (
    init,
    latest_recall_per_rule,
    record_recall,
)


class TestRecordRecall:
    def test_round_trip_one_run(self, tmp_path: Path) -> None:
        db = tmp_path / "ph.db"
        n = record_recall(
            db,
            run_timestamp="2026-05-04T00:00:00Z",
            corpus_hash="abc123",
            per_rule=[
                ("JSS-CITE-002", 8, 2, 0.8),
                ("JSS-CAP-002", 0, 0, None),
            ],
        )
        assert n == 2
        assert latest_recall_per_rule(db) == {
            "JSS-CITE-002": 0.8,
            "JSS-CAP-002": None,
        }

    def test_only_latest_run_is_returned(self, tmp_path: Path) -> None:
        db = tmp_path / "ph.db"
        record_recall(
            db,
            run_timestamp="2026-05-01T00:00:00Z",
            corpus_hash="early",
            per_rule=[("JSS-X-001", 1, 1, 0.5)],
        )
        record_recall(
            db,
            run_timestamp="2026-05-04T00:00:00Z",
            corpus_hash="late",
            per_rule=[("JSS-X-001", 9, 1, 0.9)],
        )
        # Only the late snapshot should appear.
        assert latest_recall_per_rule(db) == {"JSS-X-001": 0.9}

    def test_empty_db_returns_empty_dict(self, tmp_path: Path) -> None:
        db = tmp_path / "no-such.db"
        assert latest_recall_per_rule(db) == {}

    def test_initialised_but_empty_db(self, tmp_path: Path) -> None:
        db = tmp_path / "ph.db"
        init(db)  # creates the schema; no rows
        assert latest_recall_per_rule(db) == {}
