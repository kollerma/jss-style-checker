"""Integration test for User Story 5 — .jss-lint.toml precedence."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from texlint.cli import main

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


def _copy_fixture_bytes(name: str) -> bytes:
    return (FIXTURES / name).read_bytes()


class TestConfigPrecedence:
    def test_toml_ignore_rules_applies(self, runner: CliRunner, tmp_path: Path):
        # Stage the violation fixture into an isolated cwd with a .jss-lint.toml
        # that ignores JSS-CITE-002.
        workdir = tmp_path / "work"
        workdir.mkdir()
        (workdir / "paper.tex").write_bytes(
            _copy_fixture_bytes("violations/citations/JSS-CITE-002-bad.tex")
        )
        (workdir / ".jss-lint.toml").write_text(
            'ignore_rules = ["JSS-CITE-002"]\n', encoding="utf-8"
        )
        with runner.isolated_filesystem(temp_dir=workdir):
            # isolated_filesystem chdir's into a fresh dir; we need cwd to be
            # the workdir we just staged. Override by invoking from there.
            # CliRunner.isolated_filesystem creates its own subdir, so we
            # instead manipulate cwd directly.
            pass

        # Use os.chdir for deterministic cwd.
        import os

        original = os.getcwd()
        try:
            os.chdir(workdir)
            result = runner.invoke(main, ["paper.tex"])
            assert result.exit_code == 0, result.output
            assert "JSS-CITE-002" not in result.output
        finally:
            os.chdir(original)

    def test_cli_overrides_toml(self, runner: CliRunner, tmp_path: Path):
        workdir = tmp_path / "work"
        workdir.mkdir()
        (workdir / "paper.tex").write_bytes(
            _copy_fixture_bytes("violations/citations/JSS-CITE-002-bad.tex")
        )
        (workdir / ".jss-lint.toml").write_text(
            'ignore_rules = ["JSS-CITE-002"]\n', encoding="utf-8"
        )

        import os

        original = os.getcwd()
        try:
            os.chdir(workdir)
            # Override the TOML's ignore set with an empty CLI value.
            result = runner.invoke(main, ["--ignore-rules", "", "paper.tex"])
            assert result.exit_code == 1
            assert "JSS-CITE-002" in result.output
        finally:
            os.chdir(original)

    def test_toml_mode_reviewer(self, runner: CliRunner, tmp_path: Path):
        workdir = tmp_path / "work"
        workdir.mkdir()
        (workdir / "paper.tex").write_bytes(
            _copy_fixture_bytes("compliant/minimal.tex")
        )
        (workdir / "paper.bib").write_bytes(
            _copy_fixture_bytes("compliant/minimal.bib")
        )
        (workdir / ".jss-lint.toml").write_text(
            'mode = "reviewer"\n', encoding="utf-8"
        )

        import os

        original = os.getcwd()
        try:
            os.chdir(workdir)
            result = runner.invoke(main, ["paper.tex", "paper.bib"])
            assert result.exit_code == 0
            assert "Journal compliance" in result.output  # reviewer-mode heading
        finally:
            os.chdir(original)
