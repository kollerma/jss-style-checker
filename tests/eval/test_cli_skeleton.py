"""Smoke tests for the `eval-jss` CLI skeleton.

Verifies every subcommand is discoverable via `--help` and that `init`
actually creates the schema.
"""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from eval import cli as cli_mod


def test_help_lists_every_subcommand() -> None:
    runner = CliRunner()
    result = runner.invoke(cli_mod.cli, ["--help"])
    assert result.exit_code == 0, result.output
    for name in ("init", "scan", "human-review", "review", "report", "corpus"):
        assert name in result.output, f"subcommand {name!r} missing from --help"


def test_init_creates_schema(tmp_path: Path) -> None:
    runner = CliRunner()
    db_path = tmp_path / "eval.db"
    result = runner.invoke(cli_mod.cli, ["--db", str(db_path), "init"])
    assert result.exit_code == 0, result.output
    assert db_path.exists()

    # Re-running init must be idempotent.
    result2 = runner.invoke(cli_mod.cli, ["--db", str(db_path), "init"])
    assert result2.exit_code == 0, result2.output


def test_corpus_fetch_phase_a_stub_exits_2() -> None:
    runner = CliRunner()
    result = runner.invoke(cli_mod.cli, ["corpus", "fetch"])
    assert result.exit_code == 2
    assert "Phase B" in result.output or "Phase B" in (result.stderr if hasattr(result, "stderr") else "")
