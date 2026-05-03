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
# CRLF tolerant: real CRAN vignettes (e.g., zoo-quickref.Rnw) ship with
# `\r\n` line endings; without `\r?\n` the chunk-header line break never
# matches and the entire chunk is left in the stripped source, exposing
# code identifiers to MARKUP-001 / -003 etc.
_RNW_CHUNK = re.compile(
    r"<<[^>]*>>=\r?\n.*?^@\s*$",
    re.DOTALL | re.MULTILINE,
)

# Inline `\Sexpr{...}` (single-line only; nested braces unsupported).
_RNW_SEXPR = re.compile(r"\\Sexpr\{[^{}]*\}")

# Macros whose argument is conceptually verbatim: ``\code{$}``,
# ``\verb{%}``, ``\url{...}`` etc. pylatexenc parses these as ordinary
# LaTeX, so a literal ``$`` inside enters math mode and the trailing
# ``}`` then mismatches. Pre-substitute the well-known TeX special
# characters to ``?`` (length-preserving) so the parser stops choking.
# Downstream rules don't rely on the literal special chars in these
# macros' content — they're identifiers, file paths, or example tokens
# whose case/spacing is what matters, not whether a ``$`` is literal.
_VERBATIM_ARG_MACROS = re.compile(
    r"\\(?:code|verb|url|email|fct|pkg|proglang)\{([^{}]*)\}"
)
# Only `$` (math-mode entry) and `%` (comment-to-end-of-line) actually
# trip pylatexenc's strict parser. `_`, `^`, `&`, `#` are tolerated as
# regular chars in text mode, so don't substitute them — leaving
# CODE-001's # comment-detection inside CodeInput envs intact.
_TEX_SPECIAL_CHARS = str.maketrans({"$": "?", "%": "?"})


def _neutralize_verbatim_args(src: str) -> str:
    """Replace TeX special characters inside ``\\code{...}`` and similar
    macro arguments with ``?``, preserving length so line / column
    positions stay source-authoritative. Without this pylatexenc enters
    math mode on a stray ``$`` inside ``\\code{...}`` and emits
    JSS-PARSE-000 on otherwise valid documents.
    """
    def _sub(m: re.Match[str]) -> str:
        whole = m.group(0)
        body = m.group(1)
        safe = body.translate(_TEX_SPECIAL_CHARS)
        # whole = "\\macro{body}" → splice the safe body back in at the
        # same offset relative to the match start.
        body_offset = m.start(1) - m.start(0)
        return whole[:body_offset] + safe + whole[body_offset + len(body):]

    return _VERBATIM_ARG_MACROS.sub(_sub, src)


# Sweave / knitr / JSS-style code-listing environments. pylatexenc
# doesn't know they're verbatim, so any TeX special chars (`$`, `%`,
# unbalanced `{` `}`, …) inside their bodies trips strict-parse with
# either math-mode-entry or environment-mismatch errors. Pre-substitute
# special chars to ``?`` so the body parses as innocuous chars while
# line / column offsets stay source-authoritative.
_VERBATIM_ENVS_RE = re.compile(
    r"(\\begin\{(?P<name>Sinput|Soutput|Scode|Code|CodeInput|CodeOutput"
    r"|CodeChunk|alltt|tabbing|verbatim\*|lstlisting)\}.*?\\end\{(?P=name)\})",
    re.DOTALL,
)


def _neutralize_verbatim_envs(src: str) -> str:
    """Replace TeX special chars inside Sweave/knitr/jss verbatim envs
    with ``?``. Length-preserving (newlines preserved by the translation
    table since ``\\n`` isn't in the map)."""
    def _sub(m: re.Match[str]) -> str:
        whole = m.group(0)
        # Locate the env body (everything between \begin{...} and \end{...}).
        head_re = re.match(r"\\begin\{[^}]+\}", whole)
        if head_re is None:
            return whole
        head_end = head_re.end()
        tail_start = whole.rfind(r"\end{")
        body = whole[head_end:tail_start]
        safe = body.translate(_TEX_SPECIAL_CHARS)
        return whole[:head_end] + safe + whole[tail_start:]

    return _VERBATIM_ENVS_RE.sub(_sub, src)


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
    source = _neutralize_verbatim_envs(source)
    source = _neutralize_verbatim_args(source)
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
        # DuplicateBlockKeyBlock is a recoverable warning, not a parse
        # failure — bibtexparser kept the first occurrence and routed
        # the rest here. JSS-BIBTEX-002 reports duplicate citation
        # keys directly; we must not double-flag them as parse errors.
        if type(failed).__name__ == "DuplicateBlockKeyBlock":
            continue
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
