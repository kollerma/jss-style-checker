"""Smoke tests for the Click sub-group migration of ``jss-lint``.

The cross-cutting follow-up converted the top-level command from a
``@click.command`` to a ``@click.group(invoke_without_command=True)``
so that subcommands such as ``explain`` / ``init`` / ``report`` /
``diff`` / ``lsp`` (specs 009, 010, 011, 015, 016) can attach without
breaking the historic bare-PATHS invocation.

These tests pin the seam: bare-PATHS still runs the read-only lint
pass, and ``main`` is a Click group that subcommands can register
against.
"""

from __future__ import annotations

from pathlib import Path

import click
import pytest
from click.testing import CliRunner

from texlint.cli import main

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


def test_bare_invocation_still_works(runner: CliRunner) -> None:
    """The historic ``jss-lint <PATHS>`` invocation must keep working.

    Mirrors the first author-terminal test: a compliant fixture pair
    exits 0 with empty stdout.
    """
    result = runner.invoke(
        main,
        [
            str(FIXTURES / "compliant" / "minimal.tex"),
            str(FIXTURES / "compliant" / "minimal.bib"),
        ],
    )
    assert result.exit_code == 0, result.output
    assert result.output.strip() == ""


def test_main_is_a_click_group() -> None:
    """The seam: ``main`` is a ``click.Group`` so subcommands can attach."""
    assert isinstance(main, click.Group)
