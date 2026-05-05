"""Integration test for User Story 1 — CLI in author/terminal mode."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from texlint.cli import main

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


@pytest.fixture
def runner() -> CliRunner:
    # click ≥8.2 removed mix_stderr — use bare CliRunner and inspect result.output.
    return CliRunner()


class TestExitCodes:
    def test_compliant_exits_zero(self, runner: CliRunner):
        result = runner.invoke(
            main,
            [
                str(FIXTURES / "compliant" / "minimal.tex"),
                str(FIXTURES / "compliant" / "minimal.bib"),
            ],
        )
        assert result.exit_code == 0, result.output

    def test_single_rule_violation_exits_one(self, runner: CliRunner):
        result = runner.invoke(
            main, [str(FIXTURES / "violations" / "citations" / "JSS-CITE-002-bad.tex")]
        )
        assert result.exit_code == 1
        assert "JSS-CITE-002" in result.output

    def test_parse_error_exits_two(self, runner: CliRunner):
        result = runner.invoke(
            main, [str(FIXTURES / "violations" / "JSS-PARSE-000.tex")]
        )
        assert result.exit_code == 2
        assert "JSS-PARSE-000" in result.output


class TestAuthorOutputShape:
    def test_groups_by_file(self, runner: CliRunner):
        result = runner.invoke(
            main,
            [
                str(FIXTURES / "violations" / "citations" / "JSS-CITE-002-bad.tex"),
                str(FIXTURES / "violations" / "citations" / "JSS-CITE-003-bad.tex"),
            ],
        )
        assert result.exit_code == 1
        # Both file paths appear as rule banners.
        assert "JSS-CITE-002-bad.tex" in result.output
        assert "JSS-CITE-003-bad.tex" in result.output
        # Both rule ids appear.
        assert "JSS-CITE-002" in result.output
        assert "JSS-CITE-003" in result.output

    def test_includes_suggestion(self, runner: CliRunner):
        result = runner.invoke(
            main, [str(FIXTURES / "violations" / "citations" / "JSS-CITE-002-bad.tex")]
        )
        assert "Add a citation" in result.output  # suggestion text

    def test_compliant_output_is_empty(self, runner: CliRunner):
        result = runner.invoke(
            main,
            [
                str(FIXTURES / "compliant" / "minimal.tex"),
                str(FIXTURES / "compliant" / "minimal.bib"),
            ],
        )
        assert result.exit_code == 0
        assert result.output.strip() == ""


class TestGuideSectionSuffix:
    """Spec 007 follow-up: terminal lines append ``(see <section>)`` for
    citable rules; sentinel rules (``JSS-PARSE-000``) render unchanged."""

    def test_citable_rule_appends_see_suffix(self, runner: CliRunner):
        result = runner.invoke(
            main,
            [str(FIXTURES / "violations" / "citations" / "JSS-CITE-002-bad.tex")],
        )
        assert result.exit_code == 1
        assert "(see §3.2 Citations)" in result.output

    def test_parse_failure_has_no_see_suffix(self, runner: CliRunner):
        result = runner.invoke(
            main,
            [str(FIXTURES / "violations" / "JSS-PARSE-000.tex")],
        )
        assert result.exit_code == 2
        assert "(see " not in result.output


class TestIgnoreRules:
    def test_ignored_rule_not_reported(self, runner: CliRunner):
        result = runner.invoke(
            main,
            [
                "--ignore-rules",
                "JSS-CITE-002",
                str(FIXTURES / "violations" / "citations" / "JSS-CITE-002-bad.tex"),
            ],
        )
        assert result.exit_code == 0
        assert "JSS-CITE-002" not in result.output

    def test_unknown_rule_in_ignore_is_silently_tolerated(self, runner: CliRunner):
        result = runner.invoke(
            main,
            [
                "--ignore-rules",
                "JSS-DOES-NOT-EXIST",
                str(FIXTURES / "compliant" / "minimal.tex"),
            ],
        )
        assert result.exit_code == 0
