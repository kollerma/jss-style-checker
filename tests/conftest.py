"""Shared pytest fixtures for the texlint test suite."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

import pytest

from texlint.api import ParsedBibFile, ParsedDocument, ParsedTexFile, Rule, ToolConfig, Violation
from texlint.core.parser import parse_bib_file, parse_tex_file


@pytest.fixture
def parse_tex_source(tmp_path: Path) -> Callable[[str], ParsedTexFile]:
    """Write ``src`` to a tempfile and parse it as a ``.tex`` file.

    Removes tempfile boilerplate from rule tests; rules are self-contained
    and don't need per-test fixture files on disk.
    """
    counter = {"n": 0}

    def _parse(src: str) -> ParsedTexFile:
        counter["n"] += 1
        path = tmp_path / f"frag_{counter['n']}.tex"
        path.write_text(src, encoding="utf-8")
        return parse_tex_file(path)

    return _parse


@pytest.fixture
def parse_bib_source(tmp_path: Path) -> Callable[[str], ParsedBibFile]:
    """Write ``src`` to a tempfile and parse it as a ``.bib`` file."""
    counter = {"n": 0}

    def _parse(src: str) -> ParsedBibFile:
        counter["n"] += 1
        path = tmp_path / f"frag_{counter['n']}.bib"
        path.write_text(src, encoding="utf-8")
        return parse_bib_file(path)

    return _parse


@pytest.fixture
def run_rule(
    parse_tex_source: Callable[[str], ParsedTexFile],
    parse_bib_source: Callable[[str], ParsedBibFile],
) -> Callable[..., list[Violation]]:
    """Apply ``rule.check`` to a one-file document built from ``src``.

    Dispatches by the ``kind`` kwarg: ``"tex"`` (default) or ``"bib"``.
    """

    def _run(
        rule: Rule,
        src: str,
        config: ToolConfig | None = None,
        *,
        kind: str = "tex",
    ) -> list[Violation]:
        cfg = config if config is not None else ToolConfig()
        if kind == "bib":
            doc = ParsedDocument(bib_files=(parse_bib_source(src),))
        else:
            doc = ParsedDocument(tex_files=(parse_tex_source(src),))
        return list(rule.check(doc, cfg))

    return _run
