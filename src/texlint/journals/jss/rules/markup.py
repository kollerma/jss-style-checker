"""Markup rules for the JSS journal plugin.

Rules in this module:
  - JSS-MARKUP-001 — programming-language names wrapped in \\proglang{}.
  - JSS-MARKUP-002 — software-package names wrapped in \\pkg{}.
  - JSS-MARKUP-003 — inline function / argument names wrapped in \\code{}.
  - JSS-MARKUP-004 — section titles with markup supply a plain-text
    optional arg: ``\\section[plain]{markup}``.

MARKUP-001/002/003 skip math mode, verbatim envs, and content already
inside JSS markup macros (\\pkg / \\proglang / \\code / \\verb); they also
skip section titles (those are handled by MARKUP-004).
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
    LatexMathNode,
)

from texlint.api import Fix, ParsedDocument, Rule, ToolConfig, Violation
from texlint.journals.jss import _catalogue_data
from texlint.journals.jss.rules import _helpers
from texlint.journals.jss.terms import LANGUAGES, R_PACKAGES


def _violation(
    *,
    tex: Any,
    pos: int,
    rule_id: str,
    suggestion: str,
    fix: Fix | None = None,
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
        fix=fix,
    )


_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9+\-]*")


def _iter_tokens_in_chars(chars: str) -> Iterator[tuple[int, str]]:
    """Yield ``(start_offset, token)`` for every word-like token."""
    for match in _TOKEN_RE.finditer(chars):
        yield match.start(), match.group(0)


def _is_initial(chars: str, offset: int) -> bool:
    """True when the token at ``offset`` is a single letter followed by '.'.

    Captures "J. R. Statistical" (initials) so single-letter languages
    like R / C don't false-positive.
    """
    tail_start = offset + 1
    # Single-letter token whose next char is a period.
    return tail_start < len(chars) and chars[tail_start] == "."


def _is_superscripted(chars: str, offset: int, token_len: int) -> bool:
    """True when the token at ``offset`` is followed by a ``^`` exponent.

    Captures ``R^2`` (R-squared) and the like — a letter used as a
    mathematical symbol in prose, not a programming-language name.
    """
    tail_start = offset + token_len
    if tail_start >= len(chars):
        return False
    return chars[tail_start] == "^"


def _is_filename_context(chars: str, offset: int) -> bool:
    """True when the token at ``offset`` is a file-extension or
    path-segment suffix, not a bare language / package mention.

    A leading ``.`` means the token is the extension of a filename
    (``foo.R``, ``algo.tex``, ``data.table.R``). A leading ``/``
    means it's a path-segment suffix (``include/R``).
    """
    if offset == 0:
        return False
    return chars[offset - 1] in {".", "/"}


# Option-list keys that take a language / package identifier as
# their RHS — typically inside ``\lstinputlisting[language=R, ...]``,
# ``\lstset{language=Python}``, ``\inputminted{R}``. Pylatexenc
# parses ``[language=R]`` as plain chars, so the bare-token scan
# would otherwise flag the ``R``.
_OPTION_KEY_RE = re.compile(
    r"\b(?:language|style|backgroundcolor|basicstyle|keywordstyle|"
    r"commentstyle|stringstyle|columns|frame|caption|label|numbers|"
    r"numberstyle|firstline|lastline|tabsize|breaklines|formatcom)"
    r"\s*=\s*\Z"
)


def _is_option_list_value(chars: str, offset: int) -> bool:
    """True when the token at ``offset`` is the RHS of a listings /
    minted option-list key (``language=R``, ``style=python``).
    """
    head = chars[max(0, offset - 50) : offset]
    return bool(_OPTION_KEY_RE.search(head))


# ---------------------------------------------------------------------------
# JSS-MARKUP-001 / MARKUP-002 — language / package names in prose
# ---------------------------------------------------------------------------


# Tokens whose immediate right-context turns the token from a package
# reference into a domain-statistics term. ``sandwich estimator`` /
# ``sandwich matrix`` / ``sandwich type`` are statistical-method usages
# of "sandwich" — not references to the `sandwich` R package — and
# wrapping them in `\pkg{}` would be wrong. Same for ``Stan model``
# (the framework, not the model package), ``Stata syntax`` (other
# software). Extend conservatively: only on direct adjacency.
_PACKAGE_TERM_DISAMBIGUATORS: dict[str, frozenset[str]] = {
    "sandwich": frozenset({
        "estimator", "estimators", "matrix", "matrices", "type", "types",
        "expression", "expressions", "method", "methods", "form", "forms",
        "covariance", "covariances", "construction",
        # Statistical-method follower vocabulary surfaced by reviewer
        # feedback in cran_effects, cran_clifford, cran_sandwich (the
        # vignette IS about the `sandwich` package, but bare prose
        # mentions like "sandwich coefficient" / "sandwich product"
        # / "sandwich formula" describe the *method*, not the package).
        "coefficient", "coefficients", "variance", "variances",
        "formula", "formulae", "formulas", "product", "products",
        "meat", "bread",
    }),
}


def _disambiguates_to_method(chars: str, offset: int, token: str) -> bool:
    """True if the word(s) immediately AFTER ``token`` at ``offset`` in
    ``chars`` indicate a non-package, statistical-method usage of the
    token (e.g., ``sandwich estimator``).
    """
    followers = _PACKAGE_TERM_DISAMBIGUATORS.get(token)
    if not followers:
        return False
    tail = chars[offset + len(token) :].lstrip()
    if not tail:
        return False
    next_word_match = re.match(r"[A-Za-z]+", tail)
    if next_word_match is None:
        return False
    return next_word_match.group(0).lower() in followers


# Environments whose contents are bibliography entries: ``\\bibitem``
# bodies, BibTeX-style hand-written entries. The author-name field
# typically contains lone-letter initials (``Bendtsen C``, ``Gramacy
# R``) that the LANGUAGES set treats as ``C`` / ``R`` mentions —
# false-positive territory for MARKUP-001.
_BIB_ENV_NAMES: frozenset[str] = frozenset({"thebibliography"})


def _is_inside_bibliography(ancestors: list[Any]) -> bool:
    for anc in ancestors:
        if (
            isinstance(anc, LatexEnvironmentNode)
            and anc.environmentname in _BIB_ENV_NAMES
        ):
            return True
    return False


def _check_bare_terms(
    doc: ParsedDocument,
    *,
    terms: frozenset[str],
    rule_id: str,
    wrap_macro: str,
    skip_initials: bool,
    emit_fix: bool = False,
) -> Iterator[Violation]:
    for tex in doc.all_tex_like():
        for node, ancestors in _helpers._walk_with_ancestors(tex.nodes):
            if not isinstance(node, LatexCharsNode):
                continue
            if not _helpers._is_in_prose_context(ancestors):
                continue
            in_bib = _is_inside_bibliography(ancestors)
            for offset, token in _iter_tokens_in_chars(node.chars):
                if token not in terms:
                    continue
                if in_bib and len(token) == 1:
                    # Single-letter ``R`` / ``C`` / ``B`` inside the
                    # bibliography is overwhelmingly an author
                    # initial (``Bendtsen C``, ``Gramacy R``). Skip
                    # those; multi-letter language/package names
                    # (``Java``, ``Python``, ``zoo``) still fire so
                    # that bibliographic prose stays linted for real
                    # missing markup.
                    continue
                if skip_initials and len(token) == 1 and _is_initial(
                    node.chars, offset
                ):
                    continue
                if _is_superscripted(node.chars, offset, len(token)):
                    continue
                if _is_filename_context(node.chars, offset):
                    continue
                if _is_option_list_value(node.chars, offset):
                    continue
                if _disambiguates_to_method(node.chars, offset, token):
                    continue
                abs_pos = node.pos + offset
                abs_end = abs_pos + len(token)
                fix: Fix | None = None
                if emit_fix:
                    replacement = f"\\{wrap_macro}{{{token}}}"
                    fix = Fix(
                        start=abs_pos,
                        end=abs_end,
                        replacement=replacement,
                        description=f"wrap {token} in \\{wrap_macro}{{}}",
                        confidence="safe",
                    )
                yield _violation(
                    tex=tex,
                    pos=abs_pos,
                    rule_id=rule_id,
                    suggestion=(
                        f"Wrap {token!r} in \\{wrap_macro}{{{token}}}."
                    ),
                    fix=fix,
                )


def check_jss_markup_001(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    """Emit JSS-MARKUP-001 violations for bare programming-language names.

    Each violation carries a ``Fix`` payload that wraps the offending
    token in ``\\proglang{...}``. The fix is safe because all carve-outs
    that could make the rewrite ambiguous (math mode, verbatim, section
    titles, code/url/verb, file-extension and option-list-value contexts,
    bibliography author initials) are already filtered upstream by
    ``_check_bare_terms`` — anything reaching the violation site is a
    bare prose mention whose canonical fix is the ``\\proglang{}``
    wrapper.
    """
    yield from _check_bare_terms(
        doc, terms=LANGUAGES, rule_id="JSS-MARKUP-001",
        wrap_macro="proglang", skip_initials=True, emit_fix=True,
    )


def check_jss_markup_002(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    yield from _check_bare_terms(
        doc, terms=R_PACKAGES, rule_id="JSS-MARKUP-002",
        wrap_macro="pkg", skip_initials=False,
    )


# ---------------------------------------------------------------------------
# JSS-MARKUP-003 — inline function / argument names
# ---------------------------------------------------------------------------


_FUNCTION_CALL_RE = re.compile(r"\b[a-zA-Z][a-zA-Z0-9_.]*\(\s*\)")


def check_jss_markup_003(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.all_tex_like():
        for node, ancestors in _helpers._walk_with_ancestors(tex.nodes):
            if not isinstance(node, LatexCharsNode):
                continue
            if not _helpers._is_in_prose_context(ancestors):
                continue
            for match in _FUNCTION_CALL_RE.finditer(node.chars):
                abs_pos = node.pos + match.start()
                yield _violation(
                    tex=tex,
                    pos=abs_pos,
                    rule_id="JSS-MARKUP-003",
                    suggestion=(
                        f"Wrap {match.group(0)!r} in "
                        f"\\code{{{match.group(0)}}}."
                    ),
                )


# ---------------------------------------------------------------------------
# JSS-MARKUP-004 — section titles with markup need a plain-text shim
# ---------------------------------------------------------------------------


def check_jss_markup_004(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.all_tex_like():
        for _parent, _idx, node in _helpers._iter_with_parent(tex.nodes):
            if not (
                isinstance(node, LatexMacroNode)
                and node.macroname in _helpers._SECTION_MACROS
            ):
                continue
            if _has_optional_shim(node):
                continue
            if not _mandatory_arg_contains_markup(node):
                continue
            yield _violation(
                tex=tex,
                pos=node.pos,
                rule_id="JSS-MARKUP-004",
                suggestion=(
                    "Provide a plain-text section title as the optional "
                    "argument: \\section[plain]{...}."
                ),
            )


def _has_optional_shim(macro: Any) -> bool:
    argd = getattr(macro, "nodeargd", None)
    if argd is None:
        return False
    for arg in argd.argnlist or ():
        if isinstance(arg, LatexGroupNode):
            delim = getattr(arg, "delimiters", None)
            if delim and delim[0] == "[":
                return True
    return False


# Macros that may legally appear inside a section title without
# triggering MARKUP-004's "needs plain-text shim" check. They render
# as no visible glyph (``\label`` / ``\index``), as a single
# accented character (``\'``, ``\.``, ``\^``, ``\&``, ...), or as a
# typographic shortcut (``\dots``, ``\ldots``). None of them break a
# table-of-contents entry, so a parallel plain-text optional argument
# isn't needed solely on their account.
_NON_MARKUP_TITLE_MACROS: frozenset[str] = frozenset({
    # Invisible / structural commands
    "label", "index", "nocite", "ignorespaces",
    # Typographic shortcuts that render as plain glyphs
    "dots", "ldots", "cdots", "vdots",
    "textbackslash", "textunderscore",
    # Accent commands — single non-ASCII character output
    "'", "`", '"', "^", "~", "=", ".", "u", "v", "H", "t", "c",
    "d", "b", "r", "k",
    # Spacing / kerning controls (single backslash-space etc.)
    " ", ",", ";", ":", "!",
    # Quoted / national-character commands
    "&", "_", "$", "#", "%", "{", "}",
    # Common JSS-specific accent or symbol shortcuts
    "ss", "aa", "AA", "ae", "AE", "oe", "OE", "o", "O", "l", "L",
    "i", "j", "S", "P",
})


def _mandatory_arg_contains_markup(macro: Any) -> bool:
    argd = getattr(macro, "nodeargd", None)
    if argd is None:
        return False
    # The mandatory arg is the first non-optional group in argnlist. Since
    # _has_optional_shim already filtered away section-with-shim cases, the
    # first group here is the mandatory one.
    for arg in argd.argnlist or ():
        if not isinstance(arg, LatexGroupNode):
            continue
        for node in _helpers._walk(arg.nodelist or ()):
            if isinstance(node, LatexMathNode):
                return True
            if isinstance(node, LatexMacroNode):
                if node.macroname in _NON_MARKUP_TITLE_MACROS:
                    continue
                return True
        return False
    return False


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


jss_markup_001 = _rule("JSS-MARKUP-001", check_jss_markup_001)
jss_markup_002 = _rule("JSS-MARKUP-002", check_jss_markup_002)
jss_markup_003 = _rule("JSS-MARKUP-003", check_jss_markup_003)
jss_markup_004 = _rule("JSS-MARKUP-004", check_jss_markup_004)


rules: tuple[Rule, ...] = (
    jss_markup_001,
    jss_markup_002,
    jss_markup_003,
    jss_markup_004,
)
