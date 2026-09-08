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

    def test_report_pdf_format(self, runner: CliRunner, tmp_path: Path) -> None:
        """Spec 015 follow-up — `--format pdf` writes a PDF via
        WeasyPrint when the [pdf] extra is installed."""
        pytest.importorskip("weasyprint")
        out = tmp_path / "report.pdf"
        result = runner.invoke(
            main,
            ["report", "--format", "pdf", "--out", str(out), str(COMPLIANT_TEX)],
        )
        assert result.exit_code == 0, result.stderr
        assert out.exists()
        assert out.read_bytes().startswith(b"%PDF-")

    def test_report_pdf_requires_out_flag(
        self, runner: CliRunner
    ) -> None:
        """`--format pdf` writes binary; refusing to dump to stdout
        prevents terminal corruption."""
        pytest.importorskip("weasyprint")
        result = runner.invoke(
            main,
            ["report", "--format", "pdf", str(COMPLIANT_TEX)],
        )
        assert result.exit_code == 2
        assert "--format pdf requires --out" in result.stderr


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

    def test_diff_format_markdown(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        old = tmp_path / "old.json"
        new = tmp_path / "new.json"
        _write_json(old, [_v()])
        _write_json(new, [_v(rule_id="JSS-NEW-001")])
        result = runner.invoke(
            main, ["diff", "--format", "markdown", str(old), str(new)]
        )
        assert result.exit_code == 1
        assert "**fixed:**" in result.stdout
        assert "## Fixed" in result.stdout
        assert "## Introduced" in result.stdout
        assert "## Unchanged" in result.stdout

    def test_diff_format_json(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        old = tmp_path / "old.json"
        new = tmp_path / "new.json"
        _write_json(old, [_v()])
        _write_json(new, [_v()])
        result = runner.invoke(
            main, ["diff", "--format", "json", str(old), str(new)]
        )
        assert result.exit_code == 0, result.stderr
        payload = json.loads(result.stdout)
        assert payload["summary"] == {
            "fixed": 0,
            "introduced": 0,
            "unchanged": 1,
        }

    def test_diff_per_violation_missing_key_exits_2(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        """Per-violation schema validation now catches malformed
        entries in addition to missing top-level keys."""
        old = tmp_path / "old.json"
        new = tmp_path / "new.json"
        old.write_text(
            json.dumps(
                {
                    "tool_version": "0",
                    "journal_id": "jss",
                    # Each violation is missing line + message.
                    "violations": [{"rule_id": "X", "file": "m.tex"}],
                }
            ),
            encoding="utf-8",
        )
        _write_json(new, [])
        result = runner.invoke(main, ["diff", str(old), str(new)])
        assert result.exit_code == 2
        assert "missing key" in result.stderr.lower()


# ---------------------------------------------------------------- version ----


class TestVersion:
    """Contract: specs/027-first-time-user-gaps/contracts/version-output.md."""

    def test_four_line_block(self, runner: CliRunner) -> None:
        from texlint import __version__
        from texlint.journals.jss import _catalogue_data

        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0, result.stderr
        assert result.stdout == (
            f"jss-lint {__version__}\n"
            f"engine: texlint/python {__version__}\n"
            f"rule set: {_catalogue_data.RULESET_VERSION} "
            f"({_catalogue_data.GUIDE_EDITION}, vendored "
            f"{_catalogue_data.SOURCE_VENDORED_AT})\n"
            "journal: jss\n"
        )

    def test_explicit_jss_journal_matches_the_default(
        self, runner: CliRunner
    ) -> None:
        default = runner.invoke(main, ["--version"])
        explicit = runner.invoke(main, ["--version", "--journal", "jss"])
        assert explicit.exit_code == 0
        assert explicit.stdout == default.stdout

    def test_registered_journal_without_metadata_reports_n_a(
        self, runner: CliRunner
    ) -> None:
        result = runner.invoke(main, ["--version", "--journal", "stub"])
        assert result.exit_code == 0, result.stderr
        lines = result.stdout.splitlines()
        assert lines[2] == "rule set: n/a"
        assert lines[3] == "journal: stub"

    def test_unregistered_journal_still_exits_zero(
        self, runner: CliRunner
    ) -> None:
        result = runner.invoke(main, ["--version", "--journal", "nope"])
        assert result.exit_code == 0, result.stderr
        lines = result.stdout.splitlines()
        assert lines[2] == "rule set: n/a"
        assert lines[3] == "journal: nope (not registered)"

    def test_toml_journal_is_honoured(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        """`--version` is not eager: config is loaded before it prints."""
        (tmp_path / ".jss-lint.toml").write_text(
            'journal = "nope"\n', encoding="utf-8"
        )
        with runner.isolated_filesystem(temp_dir=tmp_path) as cwd:
            (Path(cwd) / ".jss-lint.toml").write_text(
                'journal = "nope"\n', encoding="utf-8"
            )
            result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0, result.stderr
        assert result.stdout.splitlines()[3] == "journal: nope (not registered)"


# --------------------------------------------------------------- coverage ----


class TestCoverage:
    """Spec 027 FR-G-004: `jss-lint coverage` in three formats."""

    def test_terminal_lists_every_status_group(self, runner: CliRunner) -> None:
        result = runner.invoke(main, ["coverage"])
        assert result.exit_code == 0, result.stderr
        assert result.stdout.startswith("Guide coverage — jss (rule set ")
        for group in ("checked (", "partial (", "not checked (", "out of scope ("):
            assert group in result.stdout
        # A gap explains itself; a checked row has nothing to explain.
        assert "        reason: " in result.stdout

    def test_markdown_has_one_table_per_authority(self, runner: CliRunner) -> None:
        result = runner.invoke(main, ["coverage", "--format", "markdown"])
        assert result.exit_code == 0, result.stderr
        for heading in (
            "## jss.cls",
            "## article.tex",
            "## Style guide",
            "## Author instructions",
        ):
            assert heading in result.stdout
        assert "| Directive | Status | Provision | Rules | Reason |" in result.stdout

    def test_json_carries_the_full_matrix(self, runner: CliRunner) -> None:
        result = runner.invoke(main, ["coverage", "--format", "json"])
        assert result.exit_code == 0, result.stderr
        payload = json.loads(result.stdout)
        assert set(payload) == {"counts", "directives", "journal_id", "sources"}
        assert payload["journal_id"] == "jss"
        # Unlike the report's `coverage` block, this one carries the
        # provision text and every status (`coverage-file.md` C-6).
        assert all(d["provision"] for d in payload["directives"])
        assert {d["status"] for d in payload["directives"]} == {
            "checked",
            "partial",
            "not_checked",
            "out_of_scope",
        }
        assert set(payload["sources"]) == {
            "jss_cls",
            "article_tex",
            "style_guide",
            "author_instructions",
        }

    def test_counts_agree_across_formats(self, runner: CliRunner) -> None:
        payload = json.loads(
            runner.invoke(main, ["coverage", "--format", "json"]).stdout
        )
        counts = payload["counts"]
        line = (
            f"{counts['checked']} checked, {counts['partial']} partial, "
            f"{counts['not_checked']} not checked, "
            f"{counts['out_of_scope']} out of scope"
        )
        assert line in runner.invoke(main, ["coverage"]).stdout
        assert sum(counts.values()) == len(payload["directives"])

    def test_a_journal_without_coverage_data_says_so(
        self, runner: CliRunner
    ) -> None:
        result = runner.invoke(main, ["coverage", "--journal", "stub"])
        assert result.exit_code == 0, result.stderr
        assert result.stdout == (
            "jss-lint has no guide-coverage data for journal stub.\n"
        )

    def test_an_unknown_journal_exits_two(self, runner: CliRunner) -> None:
        result = runner.invoke(main, ["coverage", "--journal", "nope"])
        assert result.exit_code == 2
