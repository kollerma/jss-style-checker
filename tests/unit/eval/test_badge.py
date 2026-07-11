"""Spec 017 — shields.io badge JSON tests."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
from eval.badge import (
    f1_badge_json,
    pinned_precision_aggregate,
    pinned_recall_aggregate,
    precision_badge_json,
    recall_badge_json,
)
from eval.report import PrecisionTable, RuleRow

from eval import badge, history


class TestColorBuckets:
    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            (1.00, "brightgreen"),
            (0.85, "brightgreen"),
            (0.84, "green"),
            (0.70, "green"),
            (0.69, "yellow"),
            (0.55, "yellow"),
            (0.54, "red"),
            (0.00, "red"),
        ],
    )
    def test_thresholds(self, value: float, expected: str) -> None:
        assert precision_badge_json(value)["color"] == expected
        assert recall_badge_json(value)["color"] == expected


class TestShape:
    def test_precision(self) -> None:
        b = precision_badge_json(0.94)
        assert b == {
            "schemaVersion": 1,
            "label": "precision",
            "message": "0.94",
            "color": "brightgreen",
        }

    def test_recall(self) -> None:
        b = recall_badge_json(0.81)
        assert b == {
            "schemaVersion": 1,
            "label": "recall",
            "message": "0.81",
            "color": "green",
        }

    def test_f1(self) -> None:
        b = f1_badge_json(0.50)
        assert b == {
            "schemaVersion": 1,
            "label": "F1",
            "message": "0.50",
            "color": "red",
        }


class TestCli:
    def test_cli_emits_valid_json(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "eval.badge", "precision", "0.94"],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(result.stdout)
        assert payload["label"] == "precision"
        assert payload["message"] == "0.94"

    def test_cli_rejects_out_of_range(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "eval.badge", "precision", "1.5"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 2
        assert "must be in" in result.stderr


def _record_iteration(path: Path, *, label: str, tp: int, fp: int) -> None:
    """Insert one iteration + its full-scope stats row, via the real
    `history.record` path rather than hand-rolled SQL."""
    table = PrecisionTable(
        rows=[
            RuleRow(
                category="unknown", rule_id="JSS-CITE-001", source="overall",
                tp=tp, fp=fp, pending=0, precision=None, status="PASS",
            ),
        ],
        parse_failures=0,
    )
    history.record(
        path, ts="2026-01-01T00:00:00Z", label=label, note=None,
        corpus_size=1, tool_version="1.0.0", full=table, pinned=table,
    )


class TestPinnedAggregates:
    """Spec 018 (1.0.0 release) — badges pinned to a fixed iteration/
    snapshot rather than always reading 'latest'. Reference the module
    constants rather than hardcoding their values, so these tests stay
    correct across future re-pins."""

    def test_precision_reads_the_pinned_label_not_latest(self, tmp_path: Path) -> None:
        db = tmp_path / "precision-history.db"
        _record_iteration(db, label="some-earlier-iteration", tp=1, fp=99)
        _record_iteration(db, label=badge.PINNED_ITERATION_LABEL, tp=9, fp=1)
        # A later, non-pinned iteration must NOT affect the result —
        # this is the whole point of pinning by label instead of MAX(id).
        _record_iteration(db, label="some-later-iteration", tp=1, fp=99)

        assert pinned_precision_aggregate(db) == pytest.approx(0.9)

    def test_precision_is_zero_when_pinned_label_absent(self, tmp_path: Path) -> None:
        db = tmp_path / "precision-history.db"
        _record_iteration(db, label="unrelated-label", tp=9, fp=1)

        assert pinned_precision_aggregate(db) == 0.0

    def test_recall_reads_the_pinned_timestamp_not_latest(self, tmp_path: Path) -> None:
        db = tmp_path / "precision-history.db"
        history.record_recall(
            db, run_timestamp="2020-01-01T00:00:00Z", corpus_hash="h1",
            per_rule=[("JSS-CITE-001", 1, 99, None)],
        )
        history.record_recall(
            db, run_timestamp=badge.PINNED_RECALL_TIMESTAMP, corpus_hash="h2",
            per_rule=[("JSS-CITE-001", 9, 1, None)],
        )
        history.record_recall(
            db, run_timestamp="2030-01-01T00:00:00Z", corpus_hash="h3",
            per_rule=[("JSS-CITE-001", 1, 99, None)],
        )

        assert pinned_recall_aggregate(db) == pytest.approx(0.9)

    def test_recall_is_zero_when_pinned_timestamp_absent(self, tmp_path: Path) -> None:
        db = tmp_path / "precision-history.db"
        history.record_recall(
            db, run_timestamp="2020-01-01T00:00:00Z", corpus_hash="h1",
            per_rule=[("JSS-CITE-001", 9, 1, None)],
        )

        assert pinned_recall_aggregate(db) == 0.0
