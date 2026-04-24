"""Integration tests for `.Rnw` manuscript linting (spec 005 §US1)."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from texlint.cli import main

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


class TestRnwDispatch:
    def test_compliant_rnw_exits_zero(self, runner: CliRunner):
        result = runner.invoke(
            main, [str(FIXTURES / "compliant" / "minimal.Rnw")]
        )
        assert result.exit_code == 0, result.output

    def test_markup_rule_fires_on_prose_not_chunk(self, runner: CliRunner):
        # The prose "The MASS package is used throughout" triggers
        # JSS-MARKUP-002 on line 8; the chunk below contains
        # library("MASS") on line 11 but that must NOT trigger the rule.
        result = runner.invoke(
            main,
            [
                "--output", "json",
                str(FIXTURES / "violations" / "rnw" / "JSS-MARKUP-002-bad.Rnw"),
            ],
        )
        import json
        payload = json.loads(result.output)
        markup_hits = [
            v for v in payload["violations"] if v["rule_id"] == "JSS-MARKUP-002"
        ]
        assert len(markup_hits) == 1
        # The hit is on the prose line, not inside the chunk.
        assert markup_hits[0]["line"] == 8

    def test_rnw_uppercase_suffix_accepted(self, runner: CliRunner, tmp_path: Path):
        # Dispatch is case-insensitive (.RNW should work).
        src = (
            FIXTURES / "compliant" / "minimal.Rnw"
        ).read_text(encoding="utf-8")
        p = tmp_path / "paper.RNW"
        p.write_text(src, encoding="utf-8")
        result = runner.invoke(main, [str(p)])
        assert result.exit_code == 0, result.output


def test_rnw_line_count_preserved_on_real_fixture():
    from texlint.core.parser import strip_rnw_chunks
    src = (FIXTURES / "compliant" / "minimal.Rnw").read_text(encoding="utf-8")
    stripped = strip_rnw_chunks(src)
    assert stripped.count("\n") == src.count("\n")
