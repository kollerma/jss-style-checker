"""File parsers for ``.tex``, ``.bib``, ``.Rnw`` and ``.Rmd`` inputs.

All parsers are non-raising: any failure to read or parse produces a
``JSS-PARSE-000`` violation on the returned object instead of propagating
an exception. See spec FR-005, spec 005 FR-014.

``.Rnw`` handling (spec 005 §US1): :func:`strip_rnw_chunks` replaces R
code chunks with equivalent-length whitespace, then
:func:`parse_rnw_file` delegates to :func:`parse_tex_source`. Line
numbers remain source-authoritative.

``.Rmd`` handling (spec 005 §US2): :func:`parse_rmd_file` delegates to
:mod:`texlint.core.rmd_parser`.
"""

from __future__ import annotations

import re
from pathlib import Path

import bibtexparser
from pylatexenc.latexwalker import LatexWalker, LatexWalkerError

from texlint.api import (
    ParsedBibFile,
    ParsedRmdFile,
    ParsedTexFile,
    Severity,
    Violation,
)

_PARSE_RULE_ID = "JSS-PARSE-000"
_UTF8_BOM = "﻿"

# Spec 005 FR-001: line-preserving regex substitution over Sweave / knitr
# R code chunks. Handles `<<>>=` (no label) and `<<lbl, opts>>=` forms.
_RNW_CHUNK = re.compile(
    r"<<[^>]*>>=\n.*?^@\s*$",
    re.DOTALL | re.MULTILINE,
)

# Inline `\Sexpr{...}` (single-line only; nested braces unsupported).
_RNW_SEXPR = re.compile(r"\\Sexpr\{[^{}]*\}")


def strip_rnw_chunks(src: str) -> str:
    """Replace R code chunks and inline ``\\Sexpr`` calls with
    equivalent-length whitespace so the residue parses as normal LaTeX
    and line numbers remain source-authoritative.

    Invariant: ``strip_rnw_chunks(src).count("\\n") == src.count("\\n")``.

    Note: an ``\\Sexpr{...}`` argument can contain a literal newline
    (knitr accepts the line-broken form). We preserve those newlines —
    replacing only non-``\\n`` characters with spaces — otherwise the
    stripped output's line count would shrink and downstream rules
    would report off-by-N positions in the original ``.Rnw``.
    """
    def _blank_chunk(m: re.Match[str]) -> str:
        return "\n" * m.group(0).count("\n")

    def _blank_inline(m: re.Match[str]) -> str:
        return "".join(c if c == "\n" else " " for c in m.group(0))

    stripped = _RNW_CHUNK.sub(_blank_chunk, src)
    stripped = _RNW_SEXPR.sub(_blank_inline, stripped)
    return stripped


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
    return parse_tex_source(source, path)


def parse_tex_source(source: str, path: Path) -> ParsedTexFile:
    """Parse already-read TeX source into a :class:`ParsedTexFile`.

    Used by :func:`parse_rnw_file` (which pre-processes Sweave chunks)
    and by :mod:`texlint.core.rmd_parser` (which parses raw-LaTeX
    islands extracted from Rmd prose blocks).
    """
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


def parse_rnw_file(path: Path) -> ParsedTexFile:
    """Parse a Sweave / knitr ``.Rnw`` file by stripping R code chunks
    and then delegating to :func:`parse_tex_source`. Line numbers stay
    source-authoritative (spec 005 FR-003).
    """
    source, read_err = _read_utf8(path)
    if read_err is not None:
        return ParsedTexFile(
            path=path, source="", nodes=(), walker=None, violations=(read_err,)
        )
    stripped = strip_rnw_chunks(source)
    return parse_tex_source(stripped, path)


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


def parse_rmd_file(path: Path) -> ParsedRmdFile:
    """Parse an R Markdown ``.Rmd`` file into a structured
    :class:`ParsedRmdFile`. Delegates to :mod:`texlint.core.rmd_parser`.
    """
    from texlint.core.rmd_parser import parse_rmd_source

    source, read_err = _read_utf8(path)
    if read_err is not None:
        return ParsedRmdFile(
            path=path,
            source="",
            yaml_frontmatter={},
            violations=(read_err,),
        )
    return parse_rmd_source(source, path)
