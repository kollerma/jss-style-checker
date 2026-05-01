"""Code-style rules for the JSS journal plugin.

Rules:
  - JSS-CODE-001 — verbatim / CodeInput blocks do not contain comments.
  - JSS-CODE-002 — ``library()`` / ``data()`` calls quote their first arg.
  - JSS-CODE-003 — code samples use spaces around operators and after commas.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from typing import Any

from pylatexenc.latexwalker import (
    LatexCharsNode,
    LatexEnvironmentNode,
    LatexGroupNode,
    LatexMacroNode,
    LatexSpecialsNode,
)

from texlint.api import ParsedDocument, Rule, ToolConfig, Violation
from texlint.journals.jss import _catalogue_data
from texlint.journals.jss.rules import _helpers

# Envs where code lives.
_CODE_ENVS: frozenset[str] = frozenset(
    {"verbatim", "Verbatim", "Code", "CodeInput", "CodeOutput",
     "Sinput", "Soutput", "Scode", "Schunk", "CodeChunk"}
)

# Match ``#`` (or ``##``, ``###``) followed by at least one space then
# non-whitespace content — the shape of an explanatory R / shell /
# Python comment. This excludes template/placeholder markers like
# ``##ID##`` inside example HTML and CSS hex colours like ``#fff``.
_COMMENT_LINE_RE = re.compile(r"(?m)#+[^\S\n]+\S[^\n]*")
_LIBRARY_UNQUOTED_RE = re.compile(
    r"\b(?:library|data|require|requireNamespace)\(\s*([A-Za-z][A-Za-z0-9_.]*)\s*\)"
)
_MISSING_SPACES_RE = re.compile(
    r"(?:[A-Za-z0-9_\.\)\]][=+\-*/][A-Za-z0-9_\.\(\[])"
    r"|(?:,[A-Za-z0-9_\.\(\[])"
)

# `\code{foo.bar}` / `\code{Ch-Intro}` / `\code{with-dash_and.dot}` —
# content that's a single dotted/hyphenated identifier token. These are
# names (demo names, helpfile ids, S4 method signatures), not R code,
# and the operator-spacing check mis-fires on the internal hyphens.
_IDENTIFIER_ONLY_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_.\-]*$")

# `\code{0.8-0}`, `\code{l-95\% CI}` — version-number-shaped or
# label-shaped strings that begin with a digit or contain percent /
# whitespace. The hyphen here is part of the label, not a subtraction
# operator.
_VERSION_OR_LABEL_RE = re.compile(
    r"^(?:[0-9][\w.\-]*|[A-Za-z][\w.\-]*\s*\\?%[\w.\-\s\\]*)$"
)

# `\code{n.cores=1}`, `\code{W.binary=TRUE}`, `\code{interaction=TRUE}`
# — single function-argument keyword form. R/Python conventions don't
# put spaces around ``=`` inside function calls, so these aren't
# operator-spacing violations.
_KEYWORD_ARG_RE = re.compile(
    r"^[A-Za-z][\w.]*\s*=\s*"
    r"(?:[A-Za-z][\w.]*|TRUE|FALSE|NA|NULL|-?\d+(?:\.\d+)?|"
    r'"[^"]*"|\'[^\']*\')$'
)

# `\code{inst/tex/}`, `\code{src/main.cpp}` — filesystem-like paths with
# slashes between identifier-shaped pieces. The `/` is a path
# separator, not a division operator.
_PATH_LIKE_RE = re.compile(r"^[A-Za-z0-9_.\-]+(?:/[A-Za-z0-9_.\-]*)+/?$")


# Scientific number formats like 2.22e-16, 1.0E+9 — the exponent sign is
# notation, not a subtraction operator, so mask it before the missing-
# spaces check.
_SCIENTIFIC_NOTATION_RE = re.compile(
    r"\b\d+(?:\.\d+)?[eE][-+]?\d+\b"
)

# Bare string literals like "plot3logit-overview" or 'foo-bar' — the
# dash inside is part of a filename / vignette id, not an operator.
# Mask them before the missing-spaces check so `\code{vignette("a-b")}`
# doesn't trip CODE-003. Conservative: single-line, no escape handling.
_STRING_LITERAL_RE = re.compile(r"\"[^\"\n]*\"|'[^'\n]*'")


def _violation(
    *, tex: Any, pos: int, rule_id: str, suggestion: str
) -> Violation:
    meta = _catalogue_data.RULES[rule_id]
    line, col = _helpers._lineno_col(tex, pos)
    return Violation(
        file=tex.path,
        line=line,
        column=col,
        rule_id=rule_id,
        severity=meta["severity"],
        message=meta["message_template"],
        suggestion=suggestion,
        fix=None,
    )


# ---------------------------------------------------------------------------
# JSS-CODE-001 — comments inside code envs
# ---------------------------------------------------------------------------


def check_jss_code_001(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.all_tex_like():
        for node in _helpers._walk(tex.nodes):
            if not isinstance(node, LatexEnvironmentNode):
                continue
            if node.environmentname not in _CODE_ENVS:
                continue
            for child in node.nodelist or ():
                if not isinstance(child, LatexCharsNode):
                    continue
                match = _COMMENT_LINE_RE.search(child.chars)
                if match is None:
                    continue
                abs_pos = child.pos + match.start()
                yield _violation(
                    tex=tex,
                    pos=abs_pos,
                    rule_id="JSS-CODE-001",
                    suggestion=(
                        "Move the comment into the surrounding LaTeX text."
                    ),
                )
                break  # one violation per code block is enough


# ---------------------------------------------------------------------------
# JSS-CODE-002 — unquoted library() / data()
# ---------------------------------------------------------------------------


def _code_002_suggestion(match: Any) -> str:
    arg = match.group(1)
    quoted = match.group(0).replace(arg, f'"{arg}"')
    return f"Quote the argument: e.g., {quoted!r}."


def check_jss_code_002(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.all_tex_like():
        for node in _helpers._walk(tex.nodes):
            if not isinstance(node, LatexEnvironmentNode):
                continue
            if node.environmentname not in _CODE_ENVS:
                continue
            for child in node.nodelist or ():
                if not isinstance(child, LatexCharsNode):
                    continue
                for match in _LIBRARY_UNQUOTED_RE.finditer(child.chars):
                    abs_pos = child.pos + match.start()
                    yield _violation(
                        tex=tex,
                        pos=abs_pos,
                        rule_id="JSS-CODE-002",
                        suggestion=_code_002_suggestion(match),
                    )


# ---------------------------------------------------------------------------
# JSS-CODE-003 — missing spaces around operators in \code{}
# ---------------------------------------------------------------------------


def check_jss_code_003(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.all_tex_like():
        for parent, idx, node in _helpers._iter_with_parent(tex.nodes):
            if not (
                isinstance(node, LatexMacroNode)
                and node.macroname == "code"
            ):
                continue
            group = _first_group_arg(node, parent, idx)
            if group is None:
                continue
            text = _group_plain_text(group)
            if not text:
                continue
            stripped = text.strip()
            # Single dotted/hyphenated identifier — treat as a name.
            if _IDENTIFIER_ONLY_RE.match(stripped):
                continue
            # Version number / labelled string — hyphen is part of the
            # label, not an operator.
            if _VERSION_OR_LABEL_RE.match(stripped):
                continue
            # Filesystem path — slashes are separators, not division.
            if _PATH_LIKE_RE.match(stripped):
                continue
            # Single function-argument keyword (``n.cores=1`` /
            # ``interaction=TRUE``) — R/Python style omits spaces here.
            if _KEYWORD_ARG_RE.match(stripped):
                continue
            # Mask scientific notation and bare string literals before
            # the operator check so the exponent sign in 2.22e-16
            # doesn't look like subtraction and the dash in
            # "plot3logit-overview" doesn't look like an operator.
            cleaned = _SCIENTIFIC_NOTATION_RE.sub("", text)
            cleaned = _STRING_LITERAL_RE.sub("", cleaned)
            if _MISSING_SPACES_RE.search(cleaned):
                yield _violation(
                    tex=tex,
                    pos=node.pos,
                    rule_id="JSS-CODE-003",
                    suggestion=(
                        "Add spaces around operators and after commas in "
                        "the code sample (e.g., 'y = a + b * x')."
                    ),
                )


def _first_group_arg(macro: Any, parent: Any, idx: int) -> Any:
    argd = getattr(macro, "nodeargd", None)
    if argd is not None:
        for arg in argd.argnlist or ():
            if isinstance(arg, LatexGroupNode):
                return arg
    return _helpers._next_group_arg(parent, idx)


_SINGLE_CHAR_ESCAPE_MACROS: frozenset[str] = frozenset(
    {"%", "&", "_", "#", "$", "{", "}", "\\"}
)


def _group_plain_text(group: Any) -> str:
    """Reconstruct the plain text of ``\\code{...}`` content, preserving
    LaTeX special escapes (``\\%`` → ``%``, ``\\&`` → ``&``, ``\\_`` →
    ``_``) and macro arguments. Without this, ``\\code{l-95\\% CI}`` is
    seen as ``l-95 CI`` and the missing-spaces check trips on the
    label hyphen between ``l`` and ``95``.

    The ``parser._neutralize_verbatim_args`` pre-pass rewrites ``%`` /
    ``$`` inside ``\\code{...}`` to ``?`` (length-preserving) so
    pylatexenc strict mode doesn't enter math mode on a stray ``$``
    inside code. That turns the source ``\\%`` into ``\\?`` here,
    which pylatexenc parses as a macro with macroname=``?``. Map it
    back to a literal char (``%`` is by far the more common case in
    JSS prose) so the version/label regex can recognise the label.
    """
    parts: list[str] = []
    for child in group.nodelist or ():
        if isinstance(child, LatexCharsNode):
            parts.append(child.chars)
        elif isinstance(child, LatexSpecialsNode):
            parts.append(child.specials_chars)
        elif isinstance(child, LatexMacroNode):
            # Single-character escape macros (``\%`` / ``\&`` / ``\_`` /
            # ``\#`` / ``\$``) emit the literal char in code prose.
            if child.macroname in _SINGLE_CHAR_ESCAPE_MACROS:
                parts.append(child.macroname)
                continue
            # ``\?`` is the parser-substituted form of ``\%`` (and very
            # rarely ``\$``) inside ``\\code{...}``.
            if child.macroname == "?":
                parts.append("%")
    return "".join(parts).strip()


# ---------------------------------------------------------------------------
# Rule objects
# ---------------------------------------------------------------------------


def _rule(rule_id: str, check_fn) -> Rule:
    meta = _catalogue_data.RULES[rule_id]
    return Rule(
        id=rule_id,
        category=meta["category"],
        severity=meta["severity"],
        message_template=meta["message_template"],
        authority=meta["authority"],
        check=check_fn,
        formats=None,
    )


jss_code_001 = _rule("JSS-CODE-001", check_jss_code_001)
jss_code_002 = _rule("JSS-CODE-002", check_jss_code_002)
jss_code_003 = _rule("JSS-CODE-003", check_jss_code_003)


rules: tuple[Rule, ...] = (jss_code_001, jss_code_002, jss_code_003)
