"""Spec-007: SARIF carries guide_url as helpUri on rule descriptors."""

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


class TestSarifHelpUri:
    def test_backfilled_rule_has_helpuri(self, runner: CliRunner) -> None:
        """JSS-CITE-002 was backfilled in spec 007; its SARIF rule
        descriptor MUST carry helpUri equal to the guide URL."""
        result = runner.invoke(
            main,
            [
                "--output",
                "sarif",
                str(FIXTURES / "compliant" / "minimal.tex"),
            ],
        )
        payload = json.loads(result.output)
        rules = payload["runs"][0]["tool"]["driver"]["rules"]
        cite_rule = next(r for r in rules if r["id"] == "JSS-CITE-002")
        assert "helpUri" in cite_rule
        assert cite_rule["helpUri"].startswith("https://")
        # shortDescription includes the section number.
        assert "§3.2 Citations" in cite_rule["shortDescription"]["text"]

    def test_un_backfilled_rule_has_no_helpuri(self, runner: CliRunner) -> None:
        """A rule without a backfilled guide_url MUST NOT have a
        helpUri (sentinel pattern)."""
        result = runner.invoke(
            main,
            [
                "--output",
                "sarif",
                str(FIXTURES / "compliant" / "minimal.tex"),
            ],
        )
        payload = json.loads(result.output)
        rules = payload["runs"][0]["tool"]["driver"]["rules"]
        # JSS-PARSE-000 is the synthetic parse rule; it has no helpUri.
        parse_rule = next(r for r in rules if r["id"] == "JSS-PARSE-000")
        assert "helpUri" not in parse_rule
