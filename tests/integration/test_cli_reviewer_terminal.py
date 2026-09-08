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
        # Citations category fails; others (references, preamble, etc.) pass
        # because the fixture has a valid preamble and bib.
        assert "PASS" in result.output

    def test_ignored_category_shows_skipped(self, runner: CliRunner):
        # Ignore every rule in the Citations category → category is SKIPPED,
        # excluded from compliance_percentage.
        result = runner.invoke(
            main,
            [
                "--mode",
                "reviewer",
                "--ignore-rules",
                "JSS-CITE-002,JSS-CITE-003,JSS-CITE-004",
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


class TestNotCheckedBlock:
    """Spec 027 FR-G-003: reviewer mode ends with what is *not* checked.

    A compliance percentage over a rule set that covers 80 of 83
    checkable provisions means something different from one over a rule
    set that covers all of them; the block is what lets a reviewer tell.
    """

    def _output(self, runner: CliRunner) -> str:
        result = runner.invoke(
            main,
            ["--mode", "reviewer", str(FIXTURES / "compliant" / "minimal.tex")],
        )
        assert result.exit_code == 0, result.output
        return result.output

    def test_block_follows_the_compliance_line(self, runner: CliRunner) -> None:
        output = self._output(runner)
        assert output.index("Overall:") < output.index("Not checked by jss-lint")

    def test_lists_partial_before_not_checked(self, runner: CliRunner) -> None:
        output = self._output(runner)
        assert output.index("partial") < output.index("not checked")

    def test_out_of_scope_rows_are_not_listed(self, runner: CliRunner) -> None:
        # 66 provisions are out of scope; listing them here would bury
        # the handful a reviewer can act on.
        assert "out of scope" not in self._output(runner).split(
            "Run jss-lint coverage"
        )[0]

    def test_ends_with_the_counts_and_a_pointer(self, runner: CliRunner) -> None:
        output = self._output(runner)
        assert "Run jss-lint coverage for the full matrix (" in output
        assert "out of scope)." in output
