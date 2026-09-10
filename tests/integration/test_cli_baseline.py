"""End-to-end `--baseline` / `--update-baseline` behaviour (spec 027 item B).

Contract: `specs/027-first-time-user-gaps/contracts/baseline-file.md`,
`contracts/cli.md` C-1/C-4/C-5.

The story these cover is Story 3: adopt the tool on a manuscript that
predates it, commit the accepted state, and from then on fail only on
what is new.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from texlint.cli import main

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
# Two findings of two different rules, in one file.
SOURCE = (
    "\\documentclass[article]{jss}\n"
    "\\title{A Short Demo}\n"
    "\\Abstract{Demo.}\n"
    "\\Keywords{Demo}\n"
    "\\Address{Demo}\n"
    "\\begin{document}\n"
    "\\section{Methods And Results}\n"
    "We use R for everything.\n"
    "\\end{document}\n"
)


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


def _write(directory: Path, source: str = SOURCE) -> Path:
    paper = directory / "paper.tex"
    paper.write_text(source, encoding="utf-8")
    return paper


class TestUpdateBaseline:
    def test_creates_the_file_and_exits_zero(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        paper = _write(tmp_path)
        target = tmp_path / "b.json"
        result = runner.invoke(
            main, ["--baseline", str(target), "--update-baseline", str(paper)]
        )
        assert result.exit_code == 0, result.stderr
        assert "wrote" in result.stderr
        payload = json.loads(target.read_text(encoding="utf-8"))
        assert payload["schema_version"] == 1
        assert payload["journal"] == "jss"
        assert {e["path"] for e in payload["entries"]} == {"paper.tex"}

    def test_renders_no_report(self, runner: CliRunner, tmp_path: Path) -> None:
        paper = _write(tmp_path)
        result = runner.invoke(
            main,
            ["--baseline", str(tmp_path / "b.json"), "--update-baseline", str(paper)],
        )
        assert result.stdout == ""

    def test_defaults_to_the_conventional_filename(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        with runner.isolated_filesystem(temp_dir=tmp_path) as cwd:
            paper = _write(Path(cwd))
            result = runner.invoke(main, ["--update-baseline", str(paper)])
            assert result.exit_code == 0, result.stderr
            assert (Path(cwd) / ".jss-lint-baseline.json").is_file()

    def test_rewriting_prunes_fixed_findings(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        paper = _write(tmp_path)
        target = tmp_path / "b.json"
        runner.invoke(
            main, ["--baseline", str(target), "--update-baseline", str(paper)]
        )
        before = len(json.loads(target.read_text())["entries"])
        paper.write_text(
            SOURCE.replace("We use R for everything.", "All fixed here."),
            encoding="utf-8",
        )
        runner.invoke(
            main, ["--baseline", str(target), "--update-baseline", str(paper)]
        )
        after = len(json.loads(target.read_text())["entries"])
        assert after < before


class TestApplyBaseline:
    def _accept(self, runner: CliRunner, paper: Path, target: Path) -> None:
        result = runner.invoke(
            main, ["--baseline", str(target), "--update-baseline", str(paper)]
        )
        assert result.exit_code == 0, result.stderr

    def test_accepted_findings_are_hidden_and_exit_zero(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        paper = _write(tmp_path)
        target = tmp_path / "b.json"
        assert runner.invoke(main, [str(paper)]).exit_code == 1
        self._accept(runner, paper, target)

        result = runner.invoke(main, ["--baseline", str(target), str(paper)])
        assert result.exit_code == 0, result.stdout
        assert "JSS-MARKUP-001" not in result.stdout
        assert "Baseline: " in result.stdout

    def test_edits_that_move_lines_do_not_resurrect_findings(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        paper = _write(tmp_path)
        target = tmp_path / "b.json"
        self._accept(runner, paper, target)
        paper.write_text(
            SOURCE.replace(
                "\\begin{document}\n",
                "\\begin{document}\n\nAn inserted paragraph, harmless.\n\n",
            ),
            encoding="utf-8",
        )
        result = runner.invoke(main, ["--baseline", str(target), str(paper)])
        assert result.exit_code == 0, result.stdout

    def test_a_new_finding_is_reported_and_exits_one(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        paper = _write(tmp_path)
        target = tmp_path / "b.json"
        self._accept(runner, paper, target)
        # A different rule, not in the baseline.
        paper.write_text(
            SOURCE.replace(
                "\\end{document}", "We call lm() in prose.\n\\end{document}"
            ),
            encoding="utf-8",
        )
        result = runner.invoke(main, ["--baseline", str(target), str(paper)])
        assert result.exit_code == 1
        assert "JSS-MARKUP-003" in result.stdout

    def test_summary_counts_stale_entries(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        paper = _write(tmp_path)
        target = tmp_path / "b.json"
        self._accept(runner, paper, target)
        paper.write_text(
            SOURCE.replace("We use R for everything.", "All fixed here."),
            encoding="utf-8",
        )
        result = runner.invoke(main, ["--baseline", str(target), str(paper)])
        assert "stale" in result.stdout
        assert "0 stale" not in result.stdout

    def test_min_confidence_makes_entries_unevaluated_not_stale(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        paper = _write(tmp_path)
        target = tmp_path / "b.json"
        self._accept(runner, paper, target)
        result = runner.invoke(
            main,
            [
                "--baseline",
                str(target),
                "--min-confidence",
                "high",
                str(paper),
            ],
        )
        assert result.exit_code == 0, result.stdout
        assert "unevaluated)" in result.stdout
        assert "(0 stale" in result.stdout


class TestPathHandling:
    def test_a_baseline_in_a_subdirectory_uses_parent_relative_paths(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        paper = _write(tmp_path)
        subdir = tmp_path / "ci"
        subdir.mkdir()
        target = subdir / "b.json"
        runner.invoke(
            main, ["--baseline", str(target), "--update-baseline", str(paper)]
        )
        payload = json.loads(target.read_text(encoding="utf-8"))
        assert {e["path"] for e in payload["entries"]} == {"../paper.tex"}
        # And it still matches on the next run.
        result = runner.invoke(main, ["--baseline", str(target), str(paper)])
        assert result.exit_code == 0, result.stdout

    def test_resolve_and_no_resolve_produce_the_same_file(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        paper = _write(tmp_path)
        auto = tmp_path / "auto.json"
        literal = tmp_path / "literal.json"
        runner.invoke(main, ["--baseline", str(auto), "--update-baseline", str(paper)])
        runner.invoke(
            main,
            [
                "--baseline",
                str(literal),
                "--update-baseline",
                "--no-resolve",
                str(paper),
            ],
        )
        assert auto.read_text(encoding="utf-8") == literal.read_text(encoding="utf-8")


class TestConfigAndErrors:
    def test_toml_key_is_honoured(self, runner: CliRunner, tmp_path: Path) -> None:
        with runner.isolated_filesystem(temp_dir=tmp_path) as cwd:
            paper = _write(Path(cwd))
            target = Path(cwd) / "b.json"
            runner.invoke(
                main, ["--baseline", str(target), "--update-baseline", str(paper)]
            )
            (Path(cwd) / ".jss-lint.toml").write_text(
                f'baseline = "{target.name}"\n', encoding="utf-8"
            )
            result = runner.invoke(main, [str(paper)])
        assert result.exit_code == 0, result.stdout
        assert "Baseline: " in result.stdout

    def test_journal_mismatch_exits_two(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        paper = _write(tmp_path)
        target = tmp_path / "b.json"
        runner.invoke(
            main, ["--baseline", str(target), "--update-baseline", str(paper)]
        )
        payload = json.loads(target.read_text(encoding="utf-8"))
        payload["journal"] = "other"
        target.write_text(json.dumps(payload), encoding="utf-8")
        result = runner.invoke(main, ["--baseline", str(target), str(paper)])
        assert result.exit_code == 2
        assert "journal" in result.stderr

    def test_unknown_schema_exits_two(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        target = tmp_path / "b.json"
        target.write_text('{"schema_version": 99}', encoding="utf-8")
        result = runner.invoke(
            main, ["--baseline", str(target), str(_write(tmp_path))]
        )
        assert result.exit_code == 2
        assert "schema_version" in result.stderr

    def test_missing_file_exits_two(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        result = runner.invoke(
            main, ["--baseline", str(tmp_path / "nope.json"), str(_write(tmp_path))]
        )
        assert result.exit_code == 2
        assert "failed to read" in result.stderr


class TestOtherFormats:
    def test_json_carries_the_summary(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        paper = _write(tmp_path)
        target = tmp_path / "b.json"
        runner.invoke(
            main, ["--baseline", str(target), "--update-baseline", str(paper)]
        )
        result = runner.invoke(
            main, ["--baseline", str(target), "--output", "json", str(paper)]
        )
        payload = json.loads(result.stdout)
        assert payload["baseline"]["matched"] == 2
        assert payload["baseline"]["path"] == str(target)
        assert payload["violations"] == []

    def test_html_carries_the_note(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        paper = _write(tmp_path)
        target = tmp_path / "b.json"
        runner.invoke(
            main, ["--baseline", str(target), "--update-baseline", str(paper)]
        )
        result = runner.invoke(
            main, ["--baseline", str(target), "--output", "html", str(paper)]
        )
        assert '<p class="note">Baseline: 2 findings hidden' in result.stdout

    def test_sarif_omits_baselined_results(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        paper = _write(tmp_path)
        target = tmp_path / "b.json"
        runner.invoke(
            main, ["--baseline", str(target), "--update-baseline", str(paper)]
        )
        result = runner.invoke(
            main, ["--baseline", str(target), "--output", "sarif", str(paper)]
        )
        payload = json.loads(result.stdout)
        assert payload["runs"][0]["results"] == []

    def test_fix_only_touches_visible_findings(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        # JSS-MARKUP-001 has a safe auto-fix; accepted, it must be left
        # alone (`baseline-file.md` C-7).
        paper = _write(tmp_path)
        target = tmp_path / "b.json"
        runner.invoke(
            main, ["--baseline", str(target), "--update-baseline", str(paper)]
        )
        before = paper.read_text(encoding="utf-8")
        runner.invoke(main, ["--baseline", str(target), "--fix", str(paper)])
        assert paper.read_text(encoding="utf-8") == before

        # Guard against a vacuous assertion: without the baseline the
        # same invocation *does* rewrite the file.
        runner.invoke(main, ["--fix", str(paper)])
        assert paper.read_text(encoding="utf-8") != before
