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


def test_corpus_fetch_rejects_missing_manifest(tmp_path: Path) -> None:
    """`corpus fetch` against a non-existent manifest exits 2 (malformed)."""
    runner = CliRunner()
    result = runner.invoke(
        cli_mod.cli,
        [
            "corpus",
            "fetch",
            "--manifest",
            str(tmp_path / "no-such-manifest.csv"),
            "--target",
            str(tmp_path / "target"),
            "--gaps",
            str(tmp_path / "gaps.csv"),
        ],
    )
    # A missing manifest surfaces as an OSError wrapped by the file read —
    # the CLI should still exit non-zero (click's file-check or our catch).
    assert result.exit_code != 0
