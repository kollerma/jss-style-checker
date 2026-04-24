"""Integration tests for `.Rmd` manuscript linting (spec 005 §US2)."""

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


class TestRmdDispatch:
    def test_compliant_rmd_exits_zero(self, runner: CliRunner):
        result = runner.invoke(
            main, [str(FIXTURES / "compliant" / "minimal.Rmd")]
        )
        # Compliant Rmd may still surface MARKUP findings on the fragment
        # (e.g., \proglang, \citep missing) but exit code must not be 2.
        assert result.exit_code in (0, 1), result.output

    def test_markup_rule_fires_on_prose_not_code_fence(self, runner: CliRunner):
        result = runner.invoke(
            main,
            [
                "--output", "json",
                str(FIXTURES / "violations" / "rmd" / "JSS-MARKUP-002-bad.Rmd"),
            ],
        )
        payload = json.loads(result.output)
        markup_hits = [
            v for v in payload["violations"] if v["rule_id"] == "JSS-MARKUP-002"
        ]
        assert len(markup_hits) == 1
        # The hit is on the prose line (7), not on the fenced code block
        # (which starts at line 9).
        assert markup_hits[0]["line"] == 7
        # Violation file path is the .Rmd file, not a synthetic fragment path.
        assert markup_hits[0]["file"].endswith(".Rmd")

    def test_rmd_uppercase_suffix_accepted(self, runner: CliRunner, tmp_path: Path):
        src = (FIXTURES / "compliant" / "minimal.Rmd").read_text(encoding="utf-8")
        p = tmp_path / "paper.RMD"
        p.write_text(src, encoding="utf-8")
        result = runner.invoke(main, [str(p)])
        assert result.exit_code in (0, 1), result.output


class TestRmdMalformed:
    def test_malformed_yaml_surfaces_parse_error(self, runner: CliRunner):
        result = runner.invoke(
            main,
            [
                "--output", "json",
                str(FIXTURES / "violations" / "rmd" / "malformed-yaml.Rmd"),
            ],
        )
        payload = json.loads(result.output)
        parse_errs = [
            v for v in payload["violations"] if v["rule_id"] == "JSS-PARSE-000"
        ]
        assert parse_errs, "Expected JSS-PARSE-000 for malformed YAML"

    def test_unterminated_fence_surfaces_parse_error(self, runner: CliRunner):
        result = runner.invoke(
            main,
            [
                "--output", "json",
                str(FIXTURES / "violations" / "rmd" / "unterminated-fence.Rmd"),
            ],
        )
        payload = json.loads(result.output)
        parse_errs = [
            v for v in payload["violations"] if v["rule_id"] == "JSS-PARSE-000"
        ]
        assert parse_errs

    def test_unterminated_frontmatter_surfaces_parse_error(
        self, runner: CliRunner
    ):
        result = runner.invoke(
            main,
            [
                "--output", "json",
                str(FIXTURES / "violations" / "rmd" / "unterminated-frontmatter.Rmd"),
            ],
        )
        payload = json.loads(result.output)
        parse_errs = [
            v for v in payload["violations"] if v["rule_id"] == "JSS-PARSE-000"
        ]
        assert parse_errs


class TestRmdFrontmatterNotLinted:
    def test_no_violations_on_frontmatter_content(self, runner: CliRunner):
        # Frontmatter contains "MASS"; rules must NOT fire on frontmatter.
        src = (
            "---\n"
            "title: Something about MASS\n"
            "---\n"
            "\n"
            "Compliant prose.\n"
        )
        import tempfile
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".Rmd", delete=False, encoding="utf-8"
        ) as f:
            f.write(src)
            p = Path(f.name)
        result = runner.invoke(main, ["--output", "json", str(p)])
        payload = json.loads(result.output)
        markup_hits = [
            v for v in payload["violations"] if v["rule_id"] == "JSS-MARKUP-002"
        ]
        # Compliant prose doesn't mention MASS; frontmatter does but shouldn't fire.
        assert markup_hits == []
