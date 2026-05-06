"""Spec 017 — shields.io badge JSON tests."""

from __future__ import annotations

import json
import subprocess
import sys

import pytest
from eval.badge import (
    f1_badge_json,
    precision_badge_json,
    recall_badge_json,
)


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
