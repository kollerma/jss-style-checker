"""Integration test for User Story 2 — reviewer-mode per-category table."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from texlint.cli import main

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


class TestReviewerMode:
    def test_compliant_all_pass_overall_100(self, runner: CliRunner):
        result = runner.invoke(
            main,
            [
                "--mode",
                "reviewer",
                str(FIXTURES / "compliant" / "minimal.tex"),
                str(FIXTURES / "compliant" / "minimal.bib"),
            ],
        )
        assert result.exit_code == 0, result.output
        # Reviewer mode emits one row per category from JSSJournal.categories().
        assert "Citations" in result.output
        assert "References" in result.output
        assert "Typography" in result.output
        assert "PASS" in result.output
        assert "100" in result.output  # overall percentage

    def test_one_category_fails(self, runner: CliRunner):
        result = runner.invoke(
            main,
            [
                "--mode",
                "reviewer",
                str(FIXTURES / "violations" / "citations" / "JSS-CITE-002-bad.tex"),
                str(FIXTURES / "compliant" / "minimal.bib"),
            ],
        )
        assert result.exit_code == 1
        assert "FAIL" in result.output
        # During spec-004 rollout, only implemented categories (currently:
        # citations) have rules — others report SKIPPED until they ship.
        assert "SKIPPED" in result.output

    def test_ignored_category_shows_skipped(self, runner: CliRunner):
        # Ignore the one rule in Citation → category is SKIPPED,
        # excluded from compliance_percentage.
        result = runner.invoke(
            main,
            [
                "--mode",
                "reviewer",
                "--ignore-rules",
                "JSS-CITE-002",
                str(FIXTURES / "violations" / "citations" / "JSS-CITE-002-bad.tex"),
                str(FIXTURES / "compliant" / "minimal.bib"),
            ],
        )
        assert result.exit_code == 0
        assert "SKIPPED" in result.output
        # Overall percentage still 100 (only the non-skipped categories count).
        assert "100" in result.output


class TestAuthorVsReviewer:
    def test_author_mode_does_not_emit_category_table(self, runner: CliRunner):
        result = runner.invoke(
            main,
            [
                str(FIXTURES / "violations" / "citations" / "JSS-CITE-002-bad.tex"),
            ],
        )
        # Author mode shows individual violations, not the summary table heading.
        assert "Journal compliance" not in result.output
        assert "JSS-CITE-002" in result.output

    def test_reviewer_mode_shows_table_heading(self, runner: CliRunner):
        result = runner.invoke(
            main,
            [
                "--mode",
                "reviewer",
                str(FIXTURES / "violations" / "citations" / "JSS-CITE-002-bad.tex"),
            ],
        )
        assert "Journal compliance" in result.output
