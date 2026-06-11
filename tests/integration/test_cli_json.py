"""Integration test for User Story 3 — deterministic JSON output."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from texlint import __version__
from texlint.cli import main

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


class TestJsonShape:
    def test_top_level_keys(self, runner: CliRunner):
        result = runner.invoke(
            main,
            [
                "--output",
                "json",
                str(FIXTURES / "compliant" / "minimal.tex"),
                str(FIXTURES / "compliant" / "minimal.bib"),
            ],
        )
        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)
        assert set(payload.keys()) == {
            "tool_version",
            "journal_id",
            "compliance_percentage",
            "categories",
            "violations",
            "skipped_rules",
        }
        assert payload["tool_version"] == __version__
        assert payload["journal_id"] == "jss"
        assert payload["compliance_percentage"] == 100.0
        assert payload["violations"] == []

    def test_violation_fields(self, runner: CliRunner):
        result = runner.invoke(
            main,
            [
                "--output",
                "json",
                str(FIXTURES / "violations" / "citations" / "JSS-CITE-002-bad.tex"),
            ],
        )
        assert result.exit_code == 1
        payload = json.loads(result.output)
        assert len(payload["violations"]) == 1
        v = payload["violations"][0]
        assert set(v.keys()) == {
            "file",
            "line",
            "column",
            "rule_id",
            "severity",
            "message",
            "suggestion",
            "fix",
            # Spec 007 follow-up — citation fields surface per violation.
            "guide_section",
            "guide_url",
            # Measured-precision confidence tier per violation.
            "confidence",
        }
        assert v["rule_id"] == "JSS-CITE-002"
        assert v["fix"] is None
        # JSS-CITE-002 was backfilled in spec 007; expect the citation
        # surface to flow through.
        assert v["guide_section"] == "§3.2 Citations"
        assert v["guide_url"].startswith("https://")
        # JSS-CITE-002 carries a narrowed tier in the catalogue
        # (82.7% pinned-corpus precision at iter-78).
        assert v["confidence"] == "medium"


class TestDeterminism:
    def test_two_runs_byte_identical(self, runner: CliRunner):
        args = [
            "--output",
            "json",
            str(FIXTURES / "compliant" / "minimal.tex"),
            str(FIXTURES / "compliant" / "minimal.bib"),
        ]
        r1 = runner.invoke(main, args)
        r2 = runner.invoke(main, args)
        assert r1.output == r2.output

    def test_object_keys_sorted(self, runner: CliRunner):
        result = runner.invoke(
            main,
            [
                "--output",
                "json",
                str(FIXTURES / "violations" / "citations" / "JSS-CITE-002-bad.tex"),
            ],
        )
        payload = result.output
        # Top-level keys appear in alphabetical order because of sort_keys=True.
        keys = sorted(
            [
                "categories",
                "compliance_percentage",
                "journal_id",
                "tool_version",
                "violations",
            ]
        )
        positions = [payload.index(f'"{k}"') for k in keys]
        assert positions == sorted(positions)


class TestParseErrorInJson:
    def test_parse_error_produces_valid_json_exit_two(self, runner: CliRunner):
        result = runner.invoke(
            main,
            ["--output", "json", str(FIXTURES / "violations" / "JSS-PARSE-000.tex")],
        )
        assert result.exit_code == 2
        payload = json.loads(result.output)
        assert any(v["rule_id"] == "JSS-PARSE-000" for v in payload["violations"])
        # Synthetic parse category present, excluded from the percentage.
        assert any(c["category_id"] == "parse" for c in payload["categories"])
        # compliance_percentage is over the non-parse categories only.
        assert payload["compliance_percentage"] == 100.0
