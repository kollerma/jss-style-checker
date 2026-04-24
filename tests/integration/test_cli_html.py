"""Integration test for User Story 4 — HTML output in author and reviewer modes."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path

import pytest
from click.testing import CliRunner

from texlint.cli import main

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


class _WellFormednessChecker(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.errors: list[str] = []

    def error(self, message: str) -> None:  # pragma: no cover - deprecated API
        self.errors.append(message)


def _assert_parseable(html: str) -> None:
    p = _WellFormednessChecker()
    p.feed(html)
    p.close()
    assert not p.errors, p.errors


class TestAuthorHtml:
    def test_violations_rendered(self, runner: CliRunner):
        result = runner.invoke(
            main,
            [
                "--output",
                "html",
                str(FIXTURES / "violations" / "citations" / "JSS-CITE-002-bad.tex"),
            ],
        )
        assert result.exit_code == 1
        _assert_parseable(result.output)
        assert "JSS-CITE-002" in result.output
        assert "JSS-CITE-002-bad.tex" in result.output
        assert "<table" in result.output

    def test_compliant_shows_no_violations_message(self, runner: CliRunner):
        result = runner.invoke(
            main,
            [
                "--output",
                "html",
                str(FIXTURES / "compliant" / "minimal.tex"),
                str(FIXTURES / "compliant" / "minimal.bib"),
            ],
        )
        assert result.exit_code == 0
        _assert_parseable(result.output)
        assert "No violations" in result.output


class TestReviewerHtml:
    def test_category_table_present(self, runner: CliRunner):
        result = runner.invoke(
            main,
            [
                "--output",
                "html",
                "--mode",
                "reviewer",
                str(FIXTURES / "compliant" / "minimal.tex"),
                str(FIXTURES / "compliant" / "minimal.bib"),
            ],
        )
        assert result.exit_code == 0
        _assert_parseable(result.output)
        assert "Journal compliance" in result.output
        assert "Citations" in result.output
        assert "References" in result.output
        assert "Typography" in result.output
        assert "PASS" in result.output
        assert "100" in result.output


class TestDeterminism:
    def test_html_byte_identical_across_runs(self, runner: CliRunner):
        args = [
            "--output",
            "html",
            str(FIXTURES / "compliant" / "minimal.tex"),
            str(FIXTURES / "compliant" / "minimal.bib"),
        ]
        a = runner.invoke(main, args)
        b = runner.invoke(main, args)
        assert a.output == b.output
