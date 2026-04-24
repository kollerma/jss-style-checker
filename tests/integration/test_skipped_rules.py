"""Integration tests for spec 005 US3 — format-filter skipped rules."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from texlint.cli import main

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


_PREAMBLE_RULE_IDS = {f"JSS-PRE-00{i}" for i in range(1, 9)}


class TestSkippedRulesOnRmd:
    def test_preamble_rules_skipped_on_rmd(self, runner: CliRunner):
        result = runner.invoke(
            main,
            [
                "--output", "json",
                str(FIXTURES / "compliant" / "minimal.Rmd"),
            ],
        )
        payload = json.loads(result.output)
        skipped_ids = {s["rule_id"] for s in payload["skipped_rules"]}
        assert _PREAMBLE_RULE_IDS.issubset(skipped_ids), (
            f"missing preamble rules: {_PREAMBLE_RULE_IDS - skipped_ids}"
        )

    def test_no_preamble_skips_on_tex(self, runner: CliRunner):
        result = runner.invoke(
            main,
            [
                "--output", "json",
                str(FIXTURES / "compliant" / "minimal.tex"),
                str(FIXTURES / "compliant" / "minimal.bib"),
            ],
        )
        payload = json.loads(result.output)
        skipped_ids = {s["rule_id"] for s in payload["skipped_rules"]}
        assert not (skipped_ids & _PREAMBLE_RULE_IDS), (
            f"unexpected preamble skips on .tex: {skipped_ids & _PREAMBLE_RULE_IDS}"
        )

    def test_skipped_rule_reason_mentions_format(self, runner: CliRunner):
        result = runner.invoke(
            main,
            [
                "--output", "json",
                str(FIXTURES / "compliant" / "minimal.Rmd"),
            ],
        )
        payload = json.loads(result.output)
        for s in payload["skipped_rules"]:
            if s["rule_id"] in _PREAMBLE_RULE_IDS:
                assert "format mismatch" in s["reason"]
                break
        else:
            pytest.fail("no preamble skip reasons found")


class TestVerboseRendering:
    def test_verbose_terminal_includes_skipped_rules(self, runner: CliRunner):
        result = runner.invoke(
            main,
            [
                "--verbose",
                str(FIXTURES / "compliant" / "minimal.Rmd"),
            ],
        )
        assert "Skipped rules" in result.output
        assert "JSS-PRE-001" in result.output

    def test_non_verbose_terminal_omits_skipped_rules(self, runner: CliRunner):
        result = runner.invoke(
            main,
            [
                str(FIXTURES / "compliant" / "minimal.Rmd"),
            ],
        )
        assert "Skipped rules" not in result.output
