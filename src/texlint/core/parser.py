"""File parsers for ``.tex`` and ``.bib`` inputs.

Both parsers are non-raising: any failure to read or parse produces a
``JSS-PARSE-000`` violation on the returned object instead of propagating
an exception. See spec FR-005 and research.md §pylatexenc / §bibtexparser.
"""

from __future__ import annotations

from pathlib import Path

import bibtexparser
from pylatexenc.latexwalker import LatexWalker, LatexWalkerError

from texlint.api import ParsedBibFile, ParsedTexFile, Severity, Violation

_PARSE_RULE_ID = "JSS-PARSE-000"
_UTF8_BOM = "﻿"


def _parse_error(
    path: Path, *, line: int = 1, column: int | None = None, message: str
) -> Violation:
    return Violation(
        file=path,
        line=line,
        column=column,
        rule_id=_PARSE_RULE_ID,
        severity=Severity.ERROR,
        message=message,
        suggestion=None,
        fix=None,
    )


def _read_utf8(path: Path) -> tuple[str | None, Violation | None]:
    """Read ``path`` as UTF-8 text with BOM stripping.

    Returns ``(source, None)`` on success; ``(None, violation)`` on any
    read or decode failure.
    """
    try:
        raw = path.read_bytes()
    except FileNotFoundError:
        return None, _parse_error(path, message=f"File not found: {path}")
    except OSError as exc:
        return None, _parse_error(path, message=f"Could not read {path}: {exc}")

    try:
        source = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        return None, _parse_error(
            path, message=f"File is not valid UTF-8: {exc.reason} at byte {exc.start}"
        )

    if source.startswith(_UTF8_BOM):
        source = source[len(_UTF8_BOM) :]
    return source, None


def parse_tex_file(path: Path) -> ParsedTexFile:
    source, read_err = _read_utf8(path)
    if read_err is not None:
        return ParsedTexFile(
            path=path, source="", nodes=(), walker=None, violations=(read_err,)
        )

    # tolerant_parsing=False so malformed input surfaces as LatexWalkerError
    # instead of silently producing a partial AST (which would let rules
    # fire against half-parsed documents and report false positives).
    walker = LatexWalker(source, tolerant_parsing=False)
    try:
        nodes, _pos, _length = walker.get_latex_nodes()
    except LatexWalkerError as exc:
        line = _extract_line(exc) or 1
        return ParsedTexFile(
            path=path,
            source=source,
            nodes=(),
            walker=walker,
            violations=(
                _parse_error(path, line=line, message=f"LaTeX parse error: {exc}"),
            ),
        )

    return ParsedTexFile(
        path=path, source=source, nodes=tuple(nodes), walker=walker, violations=()
    )


def _extract_line(exc: LatexWalkerError) -> int | None:
    # LatexWalkerError exposes ``pos`` occasionally; try a few attributes
    # defensively. Returning None means "fall back to line 1".
    for attr in ("lineno", "pos_line"):
        val = getattr(exc, attr, None)
        if isinstance(val, int) and val >= 1:
            return val
    return None


def parse_bib_file(path: Path) -> ParsedBibFile:
    source, read_err = _read_utf8(path)
    if read_err is not None:
        return ParsedBibFile(path=path, source="", library=None, violations=(read_err,))

    library = bibtexparser.parse_string(source)
    violations: list[Violation] = []
    for failed in getattr(library, "failed_blocks", ()):
        start = getattr(failed, "start_line", None)
        line = (start + 1) if isinstance(start, int) else 1
        message = getattr(failed, "error", None) or "BibTeX parse error"
        violations.append(
            _parse_error(path, line=line, message=f"BibTeX parse error: {message}")
        )

    return ParsedBibFile(
        path=path, source=source, library=library, violations=tuple(violations)
    )
