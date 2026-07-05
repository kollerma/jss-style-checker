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

from texlint.api import (
    CODE_INPUT_ENVS,
    Fix,
    ParsedDocument,
    Rule,
    ToolConfig,
    Violation,
)
from texlint.journals.jss.rules import _helpers

# Envs where *authored* code lives — the input subset of the code-display
# contract. Program-output envs (CodeOutput / Soutput) are excluded: their
# body is verbatim tool output, not author-written code, so restyling it
# (CODE-003) or flagging its comments (CODE-001) would be wrong. LISTING_ENVS
# like lstlisting are non-prose but not JSS code-display, so CODE-* skips
# them too.
_CODE_ENVS: frozenset[str] = CODE_INPUT_ENVS

# Match ``#`` (or ``##``, ``###``) followed by at least one space then
# non-whitespace content — the shape of an explanatory R / shell /
# Python comment. This excludes template/placeholder markers like
# ``##ID##`` inside example HTML and CSS hex colours like ``#fff``.
_COMMENT_LINE_RE = re.compile(r"(?m)#+[^\S\n]+\S[^\n]*")
_LIBRARY_UNQUOTED_RE = re.compile(
    # Match bareword first arg whether the call ends there (``require(sf)``)
    # or continues with additional args (``require(sf, quietly = TRUE)``).
    # The trailing context is ``\s*[,)]`` instead of ``\s*\)``.
    r"\b(?:library|data|require|requireNamespace)\(\s*"
    r"([A-Za-z][A-Za-z0-9_.]*)\s*[,)]"
)
_MISSING_SPACES_RE = re.compile(
    # R multi-char operators that also need surrounding spaces: assignment
    # (``<-``, ``->``, ``<<-``) and comparison (``==``, ``!=``, ``<=``,
    # ``>=``). Match them as a unit *before* the single-char class —
    # otherwise the embedded ``-`` / ``=`` sits next to ``<`` / ``=`` (not
    # identifier chars), the ident-op-ident pattern never matches, and
    # ``x<-y`` / ``a==b`` slip through entirely.
    r"(?:[A-Za-z0-9_\.\)\]](?:<<-|<-|->|==|!=|<=|>=)[A-Za-z0-9_\.\(\[])"
    r"|(?:[A-Za-z0-9_\.\)\]][=+\-*/][A-Za-z0-9_\.\(\[])"
    r"|(?:,[A-Za-z0-9_\.\(\[])"
)

# Comma-without-following-space inside a code env (Sinput / CodeInput /
# verbatim). The code-env scan applies this *alongside*
# ``_MISSING_SPACES_RE`` (operator spacing, including ``=``): JSS requires
# spaces around ``=`` even in function-argument keyword position —
# ``f(x = 1)``, not ``f(x=1)`` — overriding the usual R/Python
# convention (recall-corpus annotation CARBayesST.Rnw:52 et al.,
# 2026-06-11). So ``group=mvad`` in a chunk is a genuine violation, not a
# tolerated keyword arg.
_CODE_ENV_MISSING_COMMA_SPACE_RE = re.compile(r",[A-Za-z0-9_\.\(\[\"']")
# An R / shell comment from ``#`` to end-of-line — used to mask comments
# before scanning operator spacing so prose-style commas inside comments
# (``# foo, bar``) don't trip the rule.
_CODE_ENV_COMMENT_RE = re.compile(r"#[^\n]*")
# Bare string literals ``"..."`` / ``'...'``. Mask before scanning so
# commas inside file paths (``"plot3logit-overview"``) or quoted text
# (``"foo,bar"``) don't trip the rule.
_CODE_ENV_STRING_RE = re.compile(r"\"[^\"\n]*\"|'[^'\n]*'")

# Clean R identifier — letter, then letters/digits/underscore/dot. The
# detection regex (_LIBRARY_UNQUOTED_RE) already enforces this shape on
# the bareword first arg, so every flagged match has a deterministic
# canonical form (wrap in double quotes). Confidence is therefore
# "safe" across the entire current detection set.
_CLEAN_R_IDENT_RE = re.compile(r"^[A-Za-z][A-Za-z0-9._]*$")


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


# Catalogue-backed factories live in _helpers (one definition for all
# rule modules); the module-local names are kept for call-site brevity.
_violation = _helpers.tex_violation


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
                    bareword = match.group(1)
                    # The detection regex (_LIBRARY_UNQUOTED_RE) already
                    # constrains the bareword to a clean R identifier
                    # (``[A-Za-z][A-Za-z0-9_.]*``). Wrapping it in
                    # double quotes is the deterministic canonical
                    # form, so confidence is "safe" for every match.
                    # Quoted first args (``library("MASS")``) and
                    # expression first args (``library(get("MASS"))``)
                    # never match the regex in the first place, so
                    # they don't reach this point.
                    if _CLEAN_R_IDENT_RE.match(bareword):
                        bareword_start = child.pos + match.start(1)
                        bareword_end = child.pos + match.end(1)
                        fix: Fix | None = Fix(
                            start=bareword_start,
                            end=bareword_end,
                            replacement=f'"{bareword}"',
                            description=(
                                "quote first argument to library() / data()"
                            ),
                            confidence="safe",
                        )
                    else:
                        fix = None
                    yield _violation(
                        tex=tex,
                        pos=abs_pos,
                        rule_id="JSS-CODE-002",
                        suggestion=_code_002_suggestion(match),
                        fix=fix,
                    )


# ---------------------------------------------------------------------------
# JSS-CODE-003 — missing spaces around operators in \code{}
# ---------------------------------------------------------------------------


def check_jss_code_003(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.all_tex_like():
        # First pass: scan code envs (Sinput / verbatim / CodeInput / ...)
        # for missing-space-after-comma. Narrower than the \code{} check
        # because R style permits ``f(x=1)`` so ``=`` inside chunks isn't
        # a reliable signal; comma-without-space is unambiguous.
        for env in _helpers._walk(tex.nodes):
            if not isinstance(env, LatexEnvironmentNode):
                continue
            if env.environmentname not in _CODE_ENVS:
                continue
            yield from _scan_code_env_for_spacing(tex, env)
        # Second pass: original \code{...} macro check.
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
            # Mask scientific notation and bare string literals before
            # the operator check so the exponent sign in 2.22e-16
            # doesn't look like subtraction and the dash in
            # "plot3logit-overview" doesn't look like an operator.
            # Replace strings with an identifier-shaped placeholder so
            # patterns like ``method="exact"`` still expose the missing
            # space around ``=`` (else the empty-string replacement
            # would collapse the right-of-= context to EOL and miss it).
            cleaned = _SCIENTIFIC_NOTATION_RE.sub("", text)
            cleaned = _STRING_LITERAL_RE.sub("S", cleaned)
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


def _scan_code_env_for_spacing(tex: Any, env: Any) -> Iterator[Violation]:
    """Yield a single CODE-003 violation per code env that contains a
    missing-space-after-comma or missing-space-around-operator pattern.
    One violation per env keeps the output proportional to the defect —
    authors fix one chunk at a time and per-line repetition is noisy.
    """
    nodelist = env.nodelist or ()
    for child in nodelist:
        if not isinstance(child, LatexCharsNode):
            continue
        text = child.chars
        # Mask comments first, then scientific notation, then strings.
        # Strings are replaced with an identifier-shaped placeholder so
        # ``col="red"`` still exposes the missing space around ``=``.
        cleaned = _CODE_ENV_COMMENT_RE.sub("", text)
        cleaned = _SCIENTIFIC_NOTATION_RE.sub("", cleaned)
        cleaned = _CODE_ENV_STRING_RE.sub("S", cleaned)
        if not (
            _CODE_ENV_MISSING_COMMA_SPACE_RE.search(cleaned)
            or _MISSING_SPACES_RE.search(cleaned)
        ):
            continue
        # Anchor the violation at the environment opening (the
        # ``\begin{Sinput}`` / chunk header), not the content start.
        # This is one violation per env, and reporting at ``env.pos``
        # keeps it consistent with the ``\code{...}`` pass (which
        # reports at the macro's ``\``) and lands on column 1 of the
        # chunk rather than mid-line after the ``\begin`` tag. The
        # cleaned-string match offset doesn't map back to the original
        # source anyway once comments / strings are stripped.
        yield _violation(
            tex=tex,
            pos=env.pos,
            rule_id="JSS-CODE-003",
            suggestion=(
                "Add spaces around operators and after commas in the "
                "code sample (e.g., 'f(x = 1, y = 2)' rather than "
                "'f(x=1,y=2)')."
            ),
        )
        return  # one violation per env


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


_rule = _helpers.make_rule


jss_code_001 = _rule("JSS-CODE-001", check_jss_code_001)
jss_code_002 = _rule("JSS-CODE-002", check_jss_code_002)
jss_code_003 = _rule("JSS-CODE-003", check_jss_code_003)


rules: tuple[Rule, ...] = (jss_code_001, jss_code_002, jss_code_003)
