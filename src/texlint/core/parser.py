"""File parsers for ``.tex``, ``.bib``, ``.Rnw`` and ``.Rmd`` inputs.

All parsers are non-raising: any failure to read or parse produces a
``JSS-PARSE-000`` violation on the returned object instead of propagating
an exception. See spec FR-005, spec 005 FR-014.

``.Rnw`` handling (spec 005 §US1): :func:`parse_rnw_file` rewrites R
code chunks to ``\\begin{Sinput} ... \\end{Sinput}`` envelopes (so the
chunk body becomes a verbatim env that prose rules already skip but
CODE-* / WIDTH-001 already target) and then delegates to
:func:`parse_tex_source`. Line numbers remain source-authoritative.

The legacy :func:`strip_rnw_chunks` (which blanks chunk content to
whitespace) is preserved for callers and tests that depend on the
older behaviour, but it is no longer used by :func:`parse_rnw_file`.

``.Rmd`` handling (spec 005 §US2): :func:`parse_rmd_file` delegates to
:mod:`texlint.core.rmd_parser`.
"""

from __future__ import annotations

import dataclasses
import logging
import re
from pathlib import Path

import bibtexparser
from pylatexenc.latexwalker import LatexWalker, LatexWalkerError

# bibtexparser's middleware chain logs a noisy "Unknown block type
# <class '...DuplicateFieldKeyBlock'>" warning to stderr for every
# failed block it routes past (bibtexparser/middlewares/middleware.py).
# Those blocks are exactly what parse_bib_source handles below, so the
# log line is pure noise to the CLI user — same suppression pattern as
# the pygls json-rpc logger in lsp/server.py.
logging.getLogger("bibtexparser").setLevel(logging.ERROR)

from texlint.api import (
    VERBATIM_ENVS,
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
#
# The line-start anchor is load-bearing: a chunk header must be the
# first non-whitespace on its line. Without it, a *commented-out*
# header (`% # <<data type, eval=F>>=` in cna.Rnw) is matched as a real
# opener; since its commented `% # @` is not a real terminator, the
# phantom chunk swallows everything down to the next `@` — blanking the
# `\`/`{`/`}` of intervening LaTeX prose and producing both spurious
# MARKUP findings and a broken parse.
#
# Leading horizontal whitespace IS allowed (`^[ \t]*`): knitr (unlike
# classic Sweave's strict column 0) accepts indented chunk headers, and
# real CRAN vignettes indent them inside `minipage` / `figure` envs
# (e.g. CUBvignette-knitr.Rnw). A comment prefix (`%`) is non-whitespace
# so it still won't match — keeping the cna.Rnw fix intact.
#
# TRAILING horizontal whitespace after `>>=` is also tolerated
# (`>>=[ \t]*`): both Sweave and knitr accept a chunk header with
# trailing spaces, and real vignettes ship them (multcomp's
# `<<alzheimer-K, echo = FALSE>>=  `). Without it the header isn't
# recognised, so an `echo=FALSE` chunk isn't blanked and its R code
# (e.g. `... <- NULL`) leaks into the linted prose, tripping MARKUP-*.
# Header option list is matched non-greedily up to the FIRST line-final
# `>>=` (`[^\n]*?` rather than `[^>]*`): knitr/Sweave options can contain
# `>` — comparison operators (`eval=a>b`) or `>` inside a quoted
# `fig.cap`/`out.width` string — which `[^>]*` truncated, leaving the
# chunk unrecognised (sets.Rnw, hhh4_spacetime.Rnw, hetGP).
#
# Terminator accepts trailing text after `@` (`@(?:[ \t][^\n]*)?`): the
# Sweave/noweb chunk end is a line whose first non-space char is `@`
# followed by whitespace or end-of-line — `@ %def` and `@ <comment>`
# are valid terminators. Requiring a *bare* `@` made those chunks
# over-run to the next `@`, swallowing (and blanking) intervening prose
# (arules.Rnw and 30+ other vignettes). `@foo` (no space) is NOT a
# terminator — and `@` never starts a line of R code (it's the S4 slot
# operator, always infix), so this can't truncate a chunk early.
_RNW_CHUNK = re.compile(
    r"^[ \t]*<<[^\n]*?>>=[ \t]*\r?\n.*?^[ \t]*@(?:[ \t][^\n]*)?\r?$",
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
#
# The environment list is the shared ``texlint.api.VERBATIM_ENVS``
# contract — the same set rule modules use to skip non-prose content —
# so the two can never drift apart again. Longest-first alternation so
# ``verbatim*`` is preferred over its ``verbatim`` prefix.
_VERBATIM_ENVS_RE = re.compile(
    r"(\\begin\{(?P<name>"
    + "|".join(
        re.escape(name)
        for name in sorted(VERBATIM_ENVS, key=lambda n: (-len(n), n))
    )
    + r")\}.*?\\end\{(?P=name)\})",
    re.DOTALL,
)


def _neutralize_verbatim_envs(src: str) -> str:
    """Replace TeX special chars inside Sweave/knitr/jss verbatim envs
    with ``?``. Length-preserving (newlines preserved by the translation
    table since ``\\n`` isn't in the map)."""
    def _sub(m: re.Match[str]) -> str:
        whole = m.group(0)
        # A commented-out verbatim env (``%\begin{Code} ... \end{Code}``)
        # is not a real env — leave it untouched so pylatexenc keeps
        # treating its lines as LaTeX comments. Otherwise the `%`
        # markers INSIDE the span get neutralised to `?`, un-commenting
        # the block and exposing its (commented-out) code to the markup
        # rules (networkVignette.Rnw:232, multivator.Rnw:62).
        line_start = m.string.rfind("\n", 0, m.start()) + 1
        if re.search(r"(?<!\\)%", m.string[line_start:m.start()]):
            return whole
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


# Characters inside an R chunk body that pylatexenc (strict mode) would
# otherwise misinterpret as TeX syntax: ``{`` / ``}`` form groups,
# ``\`` starts a macro. Length-preserving replacement to spaces keeps
# WIDTH-001's per-line measurements faithful to the original .Rnw and
# CODE-002 / CODE-003 token detection unaffected (they don't look at
# braces or backslashes anyway). ``$`` and ``%`` are handled later by
# :func:`_neutralize_verbatim_envs` once the Sinput envelope is in
# place. NB: deliberately not in :data:`_TEX_SPECIAL_CHARS` because
# those substitutions also apply inside ``\\code{...}`` macro args
# where ``{`` / ``}`` don't appear unbalanced.
_CHUNK_BODY_NEUTRALIZE = str.maketrans({"{": " ", "}": " ", "\\": " "})

# Sweave / knitr chunk options that suppress code echo in the rendered
# manuscript: ``echo=FALSE`` (Sweave + knitr) and ``include=FALSE``
# (knitr — suppresses both code and output). Both forms accept the
# single-letter ``F`` shorthand R uses for FALSE. Spaces around ``=``
# are optional. A hidden chunk's body never appears in the .tex / PDF
# the reviewer sees, so manuscript-style rules (CODE-*, WIDTH-001)
# must not fire on its content — the chunk only feeds the auto-purled
# .R script, where comments and looser style are encouraged. Match is
# case-sensitive: R / knitr treat ``False`` / ``false`` as undefined.
_HIDDEN_CHUNK_OPT = re.compile(r"\b(?:echo|include)\s*=\s*(?:FALSE|F)\b")

# Document-global chunk defaults: ``\SweaveOpts{echo=FALSE}`` (Sweave)
# and ``opts_chunk$set(echo=FALSE)`` (knitr) set the DEFAULT echo /
# include for every chunk, which a per-chunk option can override. ~20
# corpus vignettes hide all code this way; without honouring the
# global default we'd wrap that hidden code as visible Sinput and lint
# it (false positives on code the reader never sees). ``[^)}]*`` keeps
# each scan to one options block (nested parens, e.g. an
# ``out.width=paste0(...)`` before the echo setting, can truncate the
# scan — a documented limitation).
_GLOBAL_OPTS_BLOCK = re.compile(
    r"(?:\\SweaveOpts\s*\{|opts_chunk\$set\s*\()([^)}]*)"
)
_OPT_ECHO = re.compile(r"\becho\s*=\s*(\w+)")
_OPT_INCLUDE = re.compile(r"\binclude\s*=\s*(\w+)")
_FALSEY = frozenset({"FALSE", "F"})
_TRUTHY = frozenset({"TRUE", "T"})


def _global_chunk_defaults(src: str) -> tuple[bool, bool]:
    """Return ``(echo_default_hidden, include_default_hidden)`` from the
    document's global ``\\SweaveOpts`` / ``opts_chunk$set`` statements.

    Textually-last value wins per option (the common case sets each
    once near the top). Absent any setting, the default is *not* hidden
    — Sweave/knitr default to ``echo=TRUE`` / ``include=TRUE``."""
    echo_hidden = include_hidden = False
    for m in _GLOBAL_OPTS_BLOCK.finditer(src):
        block = m.group(1)
        e = _OPT_ECHO.search(block)
        if e and e.group(1) in _FALSEY:
            echo_hidden = True
        elif e and e.group(1) in _TRUTHY:
            echo_hidden = False
        i = _OPT_INCLUDE.search(block)
        if i and i.group(1) in _FALSEY:
            include_hidden = True
        elif i and i.group(1) in _TRUTHY:
            include_hidden = False
    return echo_hidden, include_hidden


def _chunk_is_hidden(
    header: str, echo_default_hidden: bool, include_default_hidden: bool
) -> bool:
    """True when a chunk's rendered output is suppressed (so its code
    must be blanked, not linted as visible). A per-chunk ``echo=`` /
    ``include=`` overrides the document global; otherwise the global
    default applies."""
    def _effective(opt: re.Pattern[str], default_hidden: bool) -> bool:
        m = opt.search(header)
        if m is None:
            return default_hidden
        return m.group(1) in _FALSEY

    return _effective(_OPT_ECHO, echo_default_hidden) or _effective(
        _OPT_INCLUDE, include_default_hidden
    )


def wrap_rnw_chunks_as_sinput(src: str) -> str:
    """Rewrite Sweave / knitr R code chunks to ``\\begin{Sinput}`` /
    ``\\end{Sinput}`` envelopes so CODE-* and WIDTH-001 rules (which
    already target Sinput-class envs) can lint chunk content while
    prose rules (which check ``_is_inside_verbatim``) continue to skip
    it.

    Newline count is preserved per-chunk so line numbers in downstream
    violations remain source-authoritative on the original ``.Rnw``.
    Chunk body lines are kept verbatim (modulo length-preserving
    neutralisation of ``{`` / ``}`` / ``\\`` to spaces) so WIDTH-001's
    per-line widths match the source. Inline ``\\Sexpr{...}`` calls are
    blanked exactly as in :func:`strip_rnw_chunks` because they live in
    prose and prose rules must continue to ignore them.

    Design note: chosen over the alternative of carrying a separate
    ``code_chunks`` field on :class:`ParsedTexFile` and editing every
    CODE-* / WIDTH-001 rule. CODE-* / WIDTH-001 already iterate Sinput,
    so re-emitting chunks as Sinput needs zero rule-level changes.
    """
    # Document-global echo/include defaults (\SweaveOpts /
    # opts_chunk$set) — a chunk with no per-chunk override inherits these.
    echo_default_hidden, include_default_hidden = _global_chunk_defaults(src)

    def _rewrite(m: re.Match[str]) -> str:
        whole = m.group(0)
        # Locate header line (`<<...>>=`) and trailing `@` line.
        nl = whole.find("\n")
        if nl == -1:
            return whole
        header = whole[:nl]
        # Hidden chunks (echo=FALSE / include=FALSE, per-chunk OR via a
        # document-global default) do not appear in the rendered
        # manuscript, so manuscript rules must not lint them. Blank to
        # whitespace, preserving line count exactly as
        # ``strip_rnw_chunks`` would, so downstream line numbers stay
        # source-authoritative for any rule that does fire on the
        # surrounding prose.
        if _chunk_is_hidden(
            header, echo_default_hidden, include_default_hidden
        ):
            return "\n" * whole.count("\n")
        # Strip CR if present so we re-emit a clean LF.
        header_nl = "\r\n" if header.endswith("\r") else "\n"
        rest = whole[nl + 1:]
        # rest ends with the `@` (possibly trailing whitespace) on its
        # own line. Find the start of that final line.
        last_nl = rest.rfind("\n")
        if last_nl == -1:
            # Shouldn't happen given the regex shape, but bail safely.
            return whole
        body = rest[:last_nl + 1]  # keeps the trailing newline
        # Trailer is the bare `@` (regex anchors ^@\s*$ on its own line).
        # Length-preserving neutralisation of body-only TeX-special chars.
        body_safe = body.translate(_CHUNK_BODY_NEUTRALIZE)
        return (
            f"\\begin{{Sinput}}{header_nl}"
            f"{body_safe}"
            f"\\end{{Sinput}}"
        )

    def _blank_inline(m: re.Match[str]) -> str:
        return "".join(c if c == "\n" else " " for c in m.group(0))

    rewritten = _RNW_CHUNK.sub(_rewrite, src)
    rewritten = _RNW_SEXPR.sub(_blank_inline, rewritten)
    return rewritten


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


# Macro-definition heads whose brace-group bodies routinely contain
# *unbalanced* \begin / \end pairs split across the begin-code and
# end-code arguments — the canonical LaTeX idiom
#
#     \newenvironment{smallexample}{\begin{alltt}\small}{\end{alltt}}
#
# trips pylatexenc's strict environment tracking ("mismatching closing
# brace/environment") even though the document is perfectly valid.
# 21% of the eval corpus failed to parse on this class alone.
_MACRO_DEF_HEAD = re.compile(
    r"\\(?:(?P<env>(?:re)?newenvironment)|(?P<cmd>(?:re)?newcommand|providecommand)|(?P<def>def))\*?"
)

# A TeX control sequence: multi-letter control word or single-char
# control symbol (`\x`, `\@foo`, `\%`).
_CONTROL_SEQ = re.compile(r"\\(?:[A-Za-z@]+|.)")

# \begin / \end tokens (only when introducing an environment group).
_BEGIN_END_TOKEN = re.compile(r"\\(begin|end)(?=\s*\{)")


def _match_brace_group(src: str, i: int) -> int:
    """``src[i]`` must be ``{``; return the index one past the matching
    ``}``, honouring backslash escapes (``\\{`` / ``\\}``). Returns -1
    when the group never closes (then the caller leaves the definition
    untouched — never guess on imbalance)."""
    depth = 0
    n = len(src)
    j = i
    while j < n:
        c = src[j]
        if c == "\\":
            j += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return j + 1
        j += 1
    return -1


def _skip_ws(src: str, i: int) -> int:
    n = len(src)
    while i < n and src[i].isspace():
        i += 1
    return i


def _skip_bracket_group(src: str, i: int) -> int:
    """``src[i]`` must be ``[``; return the index one past the matching
    ``]``, tolerating nested brace groups inside (e.g. a ``[{dflt}]``
    default argument). Returns -1 when unclosed."""
    n = len(src)
    j = i + 1
    while j < n:
        c = src[j]
        if c == "\\":
            j += 2
            continue
        if c == "{":
            j = _match_brace_group(src, j)
            if j == -1:
                return -1
            continue
        if c == "]":
            return j + 1
        j += 1
    return -1


def _neutralize_macro_definition_bodies(src: str) -> str:
    """Neutralize ``\\begin`` / ``\\end`` tokens inside the body groups
    of ``\\newcommand`` / ``\\newenvironment`` / ``\\providecommand`` /
    ``\\def`` (and the ``re``-variants): ``\\begin`` → `` begin`` —
    length-preserving, so line / column positions stay
    source-authoritative. Only the begin/end *tokens* are touched; the
    rest of the body stays intact for preamble-inspecting rules.

    Brace balance inside a body is guaranteed by the scanner (a body is
    exactly one balanced brace group), so removing the environment
    tokens is sufficient to stop pylatexenc's strict parser from
    chasing an ``\\end`` that lives in a different brace group.
    """
    out = list(src)
    pos = 0
    n = len(src)
    while True:
        m = _MACRO_DEF_HEAD.search(src, pos)
        if m is None:
            break
        pos = m.end()
        i = _skip_ws(src, m.end())
        if i >= n:
            break

        # --- the defined name -------------------------------------- #
        if m.group("def") is not None:
            # \def\name<param text>{body}
            cs = _CONTROL_SEQ.match(src, i)
            if cs is None:
                continue
            i = cs.end()
            # Parameter text: everything up to the body's opening brace.
            brace = src.find("{", i)
            if brace == -1:
                continue
            i = brace
        else:
            # \newcommand{\name} | \newcommand\name | \newenvironment{name}
            if src[i] == "{":
                i = _match_brace_group(src, i)
                if i == -1:
                    continue
            else:
                cs = _CONTROL_SEQ.match(src, i)
                if cs is None:
                    continue
                i = cs.end()
            # Optional arg-count / default-value groups.
            i = _skip_ws(src, i)
            while i < n and src[i] == "[":
                i = _skip_bracket_group(src, i)
                if i == -1:
                    break
                i = _skip_ws(src, i)
            if i == -1:
                continue

        # --- the body group(s) ------------------------------------- #
        n_bodies = 2 if m.group("env") is not None else 1
        for _ in range(n_bodies):
            i = _skip_ws(src, i)
            if i >= n or src[i] != "{":
                break
            end = _match_brace_group(src, i)
            if end == -1:
                break
            for tok in _BEGIN_END_TOKEN.finditer(src, i + 1, end - 1):
                out[tok.start()] = " "
            i = end
            pos = i

    return "".join(out)


def _parse_error(
    path: Path,
    *,
    line: int = 1,
    column: int | None = None,
    message: str,
    severity: Severity = Severity.ERROR,
) -> Violation:
    """A ``JSS-PARSE-000`` violation. ``severity=ERROR`` (default) marks
    a failed parse and forces exit 2; ``severity=WARNING`` marks a
    *degraded* parse — the file was recovered and fully linted — and
    obeys the normal ``--fail-on`` threshold (contracts/cli.md §Exit
    codes)."""
    return Violation(
        file=path,
        line=line,
        column=column,
        rule_id=_PARSE_RULE_ID,
        severity=severity,
        message=message,
        suggestion=None,
        fix=None,
    )


def _read_utf8(path: Path) -> tuple[str | None, Violation | None]:
    """Read ``path`` as UTF-8 text with BOM stripping.

    Returns ``(source, None)`` on success and ``(None, violation)``
    when the file cannot be read at all. A file that is readable but
    not valid UTF-8 is decoded as Latin-1 instead (which cannot fail —
    every byte maps to a code point) and returned as
    ``(source, advisory)`` with a warning-severity degraded-parse
    finding: pre-2015 CRAN vignettes commonly ship Latin-1 ``.tex`` /
    ``.Rnw`` sources, and refusing the file entirely left those
    manuscripts with zero diagnostics.
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
        source = raw.decode("latin-1")
        return source, _parse_error(
            path,
            severity=Severity.WARNING,
            message=(
                f"File is not valid UTF-8 ({exc.reason} at byte "
                f"{exc.start}); decoded as Latin-1 — check the result "
                "for mojibake and consider converting the file to UTF-8."
            ),
        )

    if source.startswith(_UTF8_BOM):
        source = source[len(_UTF8_BOM) :]
    return source, None


def parse_tex_file(path: Path) -> ParsedTexFile:
    source, read_err = _read_utf8(path)
    if source is None:
        return ParsedTexFile(
            path=path, source="", nodes=(), walker=None, violations=(read_err,)
        )
    parsed = parse_tex_source(source, path)
    if read_err is not None:  # degraded read (e.g. Latin-1 fallback)
        parsed = dataclasses.replace(
            parsed, violations=(read_err, *parsed.violations)
        )
    return parsed


def parse_tex_source(source: str, path: Path) -> ParsedTexFile:
    """Parse already-read TeX source into a :class:`ParsedTexFile`.

    Used by :func:`parse_rnw_file` (which pre-processes Sweave chunks)
    and by :mod:`texlint.core.rmd_parser` (which parses raw-LaTeX
    islands extracted from Rmd prose blocks).
    """
    source = _neutralize_macro_definition_bodies(source)
    source = _neutralize_verbatim_envs(source)
    source = _neutralize_verbatim_args(source)
    walker = LatexWalker(source, tolerant_parsing=False)
    try:
        nodes, _pos, _length = walker.get_latex_nodes()
    except LatexWalkerError as exc:
        line = _extract_line(exc) or 1
        # Strict parse failed; retry tolerantly so the author still
        # gets a full lint. The degraded parse is surfaced as a
        # warning-severity JSS-PARSE-000 (obeys --fail-on; exit != 2).
        tolerant_walker = LatexWalker(source, tolerant_parsing=True)
        try:
            nodes, _pos, _length = tolerant_walker.get_latex_nodes()
        except LatexWalkerError:
            return ParsedTexFile(
                path=path,
                source=source,
                nodes=(),
                walker=walker,
                violations=(
                    _parse_error(
                        path, line=line, message=f"LaTeX parse error: {exc}"
                    ),
                ),
            )
        return ParsedTexFile(
            path=path,
            source=source,
            nodes=tuple(nodes),
            walker=tolerant_walker,
            violations=(
                _parse_error(
                    path,
                    line=line,
                    severity=Severity.WARNING,
                    message=(
                        f"LaTeX strict parse failed ({exc}); linted with the "
                        "tolerant parser — results may be incomplete near the "
                        "reported location."
                    ),
                ),
            ),
        )

    return ParsedTexFile(
        path=path, source=source, nodes=tuple(nodes), walker=walker, violations=()
    )


def parse_rnw_file(path: Path) -> ParsedTexFile:
    """Parse a Sweave / knitr ``.Rnw`` file by rewriting R code chunks
    to ``\\begin{Sinput}...\\end{Sinput}`` envelopes (so CODE-* /
    WIDTH-001 rules see chunk content while prose rules continue to
    skip it via ``_is_inside_verbatim``) and then delegating to
    :func:`parse_tex_source`. Line numbers stay source-authoritative
    (spec 005 FR-003).
    """
    source, read_err = _read_utf8(path)
    if source is None:
        return ParsedTexFile(
            path=path, source="", nodes=(), walker=None, violations=(read_err,)
        )
    parsed = parse_rnw_source(source, path)
    if read_err is not None:  # degraded read (e.g. Latin-1 fallback)
        parsed = dataclasses.replace(
            parsed, violations=(read_err, *parsed.violations)
        )
    return parsed


def parse_rnw_source(source: str, path: Path) -> ParsedTexFile:
    """Parse already-read ``.Rnw`` source into a :class:`ParsedTexFile`.

    Source-based seam mirroring :func:`parse_tex_source`; used by the
    LSP server to lint in-memory editor buffers without touching disk.
    """
    rewritten = wrap_rnw_chunks_as_sinput(source)
    return parse_tex_source(rewritten, path)


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
    if source is None:
        return ParsedBibFile(path=path, source="", library=None, violations=(read_err,))
    parsed = parse_bib_source(source, path)
    if read_err is not None:  # degraded read (e.g. Latin-1 fallback)
        parsed = dataclasses.replace(
            parsed, violations=(read_err, *parsed.violations)
        )
    return parsed


def parse_bib_source(source: str, path: Path) -> ParsedBibFile:
    """Parse already-read BibTeX source into a :class:`ParsedBibFile`.

    Source-based seam mirroring :func:`parse_tex_source`; used by the
    LSP server to lint in-memory editor buffers without touching disk.
    """
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
        if type(failed).__name__ == "DuplicateFieldKeyBlock":
            # Also recoverable: BibTeX itself tolerates a duplicated
            # field (last occurrence wins). bibtexparser hands us the
            # deduplicated entry on `.ignore_error_block` — put it back
            # into the library so bib rules lint it, and surface the
            # defect as a warning-severity degraded-parse finding
            # instead of failing the whole file.
            entry = getattr(failed, "ignore_error_block", None)
            if entry is not None:
                # The recovered entry skipped the parse middlewares, so
                # its field values still carry the enclosing braces /
                # quotes that regular entries have stripped — normalise
                # it to the same shape before it rejoins the library.
                from bibtexparser.middlewares import RemoveEnclosingMiddleware

                entry = RemoveEnclosingMiddleware().transform_entry(entry, None)
                library.add(entry)
                # Recovered silently: the dedicated JSS-BIBTEX-005 rule
                # reports the duplicated field key during rule checking, so
                # this is not surfaced as a degraded-parse finding here.
                continue
        raw_error = getattr(failed, "error", None)
        message = str(raw_error).strip() if raw_error is not None else ""
        if not message:
            message = "block could not be parsed"
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
    if source is None:
        return ParsedRmdFile(
            path=path,
            source="",
            yaml_frontmatter={},
            violations=(read_err,),
        )
    parsed = parse_rmd_source(source, path)
    if read_err is not None:  # degraded read (e.g. Latin-1 fallback)
        parsed = dataclasses.replace(
            parsed, violations=(read_err, *parsed.violations)
        )
    return parsed
