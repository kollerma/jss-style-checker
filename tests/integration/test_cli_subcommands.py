"""Integration tests for the four follow-up CLI subcommands.

Wires the existing Python APIs (``texlint.explain``, ``texlint.init``,
``texlint.report``, ``texlint.diff``) to the post-Click-migration
``jss-lint`` group. The shims are byte-thin: each test below exercises
both happy and unhappy paths to pin contract behaviour.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from texlint.cli import main

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
COMPLIANT_TEX = FIXTURES / "compliant" / "minimal.tex"


@pytest.fixture
def runner() -> CliRunner:
    # Click 8.3+ keeps stderr split by default; no constructor argument needed.
    return CliRunner()


# ---------------------------------------------------------------- explain ----


class TestExplain:
    def test_explain_terminal(self, runner: CliRunner) -> None:
        result = runner.invoke(main, ["explain", "JSS-CITE-002"])
        assert result.exit_code == 0, result.stderr
        assert "JSS-CITE-002" in result.stdout

    def test_explain_unknown_exits_2(self, runner: CliRunner) -> None:
        result = runner.invoke(main, ["explain", "JSS-CITE-022"])
        assert result.exit_code == 2
        assert "unknown rule id" in result.stderr
        assert "did you mean" in result.stderr

    def test_explain_listing(self, runner: CliRunner) -> None:
        result = runner.invoke(main, ["explain"])
        assert result.exit_code == 0, result.stderr
        # Listing renders a per-category section header (terminal form).
        assert "citations" in result.stdout

    def test_explain_markdown_format(self, runner: CliRunner) -> None:
        result = runner.invoke(main, ["explain", "--format", "markdown", "JSS-CITE-002"])
        assert result.exit_code == 0, result.stderr
        assert result.stdout.startswith("# JSS-CITE-002")


# ------------------------------------------------------------------- init ----


class TestInit:
    def test_init_writes_config(self, runner: CliRunner, tmp_path: Path) -> None:
        # Stage a compliant fixture so the lint pipeline has something to chew on.
        (tmp_path / "manuscript.tex").write_bytes(COMPLIANT_TEX.read_bytes())
        result = runner.invoke(main, ["init", str(tmp_path)])
        assert result.exit_code == 0, result.stderr
        assert (tmp_path / ".jss-lint.toml").exists()
        assert "Wrote" in result.stdout

    def test_init_dry_run(self, runner: CliRunner, tmp_path: Path) -> None:
        (tmp_path / "manuscript.tex").write_bytes(COMPLIANT_TEX.read_bytes())
        result = runner.invoke(main, ["init", "--dry-run", str(tmp_path)])
        assert result.exit_code == 0, result.stderr
        assert not (tmp_path / ".jss-lint.toml").exists()
        # The proposed config body is echoed on stdout.
        assert 'journal = "jss"' in result.stdout

    def test_init_refusal_without_force(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        (tmp_path / "manuscript.tex").write_bytes(COMPLIANT_TEX.read_bytes())
        existing = tmp_path / ".jss-lint.toml"
        existing.write_text("# pre-existing\n")
        result = runner.invoke(main, ["init", str(tmp_path)])
        assert result.exit_code == 2
        assert existing.read_text() == "# pre-existing\n"

    def test_init_threshold_out_of_range(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        (tmp_path / "manuscript.tex").write_bytes(COMPLIANT_TEX.read_bytes())
        result = runner.invoke(
            main, ["init", "--threshold", "1.5", str(tmp_path)]
        )
        assert result.exit_code == 2


# ----------------------------------------------------------------- report ----


class TestReport:
    def test_report_md_to_stdout(self, runner: CliRunner) -> None:
        result = runner.invoke(main, ["report", str(COMPLIANT_TEX)])
        assert result.exit_code == 0, result.stderr
        assert result.stdout.startswith("# JSS conformance report")

    def test_report_md_to_file(self, runner: CliRunner, tmp_path: Path) -> None:
        out = tmp_path / "report.md"
        result = runner.invoke(
            main, ["report", "--out", str(out), str(COMPLIANT_TEX)]
        )
        assert result.exit_code == 0, result.stderr
        assert out.exists()
        assert out.read_text().startswith("# JSS conformance report")

    def test_report_extracts_title_from_preamble(self, runner: CliRunner) -> None:
        """Spec 015 follow-up: when --title is omitted, the report uses
        the manuscript's \\title{} from the preamble."""
        result = runner.invoke(main, ["report", str(COMPLIANT_TEX)])
        assert result.exit_code == 0, result.stderr
        # Compliant fixture's title starts with "A Short Demo Article".
        assert "A Short Demo Article" in result.stdout

    def test_report_extracts_author_from_preamble(self, runner: CliRunner) -> None:
        """Spec 015 follow-up: when --author is omitted, the report uses
        \\Plainauthor{} (preferred) from the preamble."""
        result = runner.invoke(main, ["report", str(COMPLIANT_TEX)])
        assert result.exit_code == 0, result.stderr
        assert "Achim Zeileis" in result.stdout

    def test_report_explicit_title_overrides_preamble(
        self, runner: CliRunner
    ) -> None:
        result = runner.invoke(
            main, ["report", "--title", "Override Title", str(COMPLIANT_TEX)]
        )
        assert result.exit_code == 0, result.stderr
        assert "Override Title" in result.stdout
        assert "A Short Demo Article" not in result.stdout

    def test_report_html_format(self, runner: CliRunner, tmp_path: Path) -> None:
        out = tmp_path / "report.html"
        result = runner.invoke(
            main,
            ["report", "--format", "html", "--out", str(out), str(COMPLIANT_TEX)],
        )
        assert result.exit_code == 0, result.stderr
        text = out.read_text()
        assert "<h1>" in text or "<H1>" in text
        # Title still flows through to HTML.
        assert "A Short Demo Article" in text


# ------------------------------------------------------------------- diff ----


def _write_json(p: Path, violations: list[dict]) -> None:
    payload = {
        "tool_version": "0.0.0-test",
        "journal_id": "jss",
        "compliance_percentage": 100.0,
        "categories": [],
        "violations": violations,
        "skipped_rules": [],
    }
    p.write_text(json.dumps(payload), encoding="utf-8")


def _v(rule_id: str = "JSS-CITE-002", line: int = 1, message: str = "x") -> dict:
    return {
        "file": "m.tex",
        "line": line,
        "column": 1,
        "rule_id": rule_id,
        "severity": "warning",
        "message": message,
        "suggestion": None,
        "fix": None,
    }


class TestDiff:
    def test_diff_no_changes_exit_zero(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        old = tmp_path / "old.json"
        new = tmp_path / "new.json"
        _write_json(old, [_v()])
        _write_json(new, [_v()])
        result = runner.invoke(main, ["diff", str(old), str(new)])
        assert result.exit_code == 0, result.stderr
        assert "fixed: 0" in result.stdout
        assert "introduced: 0" in result.stdout
        assert "unchanged: 1" in result.stdout

    def test_diff_introduced_exit_one(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        old = tmp_path / "old.json"
        new = tmp_path / "new.json"
        _write_json(old, [])
        _write_json(new, [_v()])
        result = runner.invoke(main, ["diff", str(old), str(new)])
        assert result.exit_code == 1
        assert "introduced: 1" in result.stdout

    def test_diff_schema_mismatch_exits_2(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        old = tmp_path / "old.json"
        new = tmp_path / "new.json"
        old.write_text('{"not": "a report"}', encoding="utf-8")
        _write_json(new, [])
        result = runner.invoke(main, ["diff", str(old), str(new)])
        assert result.exit_code == 2
        assert "violations" in result.stderr

    def test_diff_ignore_line_drift(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        old = tmp_path / "old.json"
        new = tmp_path / "new.json"
        _write_json(old, [_v(line=10)])
        _write_json(new, [_v(line=30)])
        result = runner.invoke(
            main, ["diff", "--ignore-line-drift", str(old), str(new)]
        )
        assert result.exit_code == 0, result.stderr
        assert "unchanged: 1" in result.stdout
