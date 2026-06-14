"""Markup rules for the JSS journal plugin.

Rules in this module:
  - JSS-MARKUP-001 — programming-language names wrapped in \\proglang{}.
  - JSS-MARKUP-002 — software-package names wrapped in \\pkg{}.
  - JSS-MARKUP-003 — inline function / argument names AND bare R
    sentinel values (``NULL``, ``NA`` family, ``TRUE`` / ``FALSE``)
    wrapped in \\code{}.
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
from texlint.journals.jss.rules import _helpers
from texlint.journals.jss.terms import LANGUAGES, R_PACKAGES

# Catalogue-backed factories live in _helpers (one definition for all
# rule modules); the module-local names are kept for call-site brevity.
_violation = _helpers.tex_violation


_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9+\-]*")


# Tails that turn a ``LANG-tail`` token into a stats / domain term
# rather than a language reference. ``R-squared`` is the coefficient
# of determination, ``R-package`` is a generic phrase (the bare ``R``
# inside is intended as a literal label, not a code reference).
_LANG_HYPHEN_STATS_TAILS: frozenset[str] = frozenset(
    {"squared", "package", "packages"}
)


def _is_lang_hyphen_term(prefix: str, tail: str) -> bool:
    """True when ``<prefix>-<tail>`` is a domain term, not a bare
    language reference (e.g., ``R-squared``)."""
    del prefix
    return tail.lower() in _LANG_HYPHEN_STATS_TAILS


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


def _is_filename_context(chars: str, offset: int, token_len: int = 1) -> bool:
    """True when the token at ``offset`` is a file-extension or
    path-segment, not a bare language / package mention.

    A leading ``.`` means the token is the extension of a filename
    (``foo.R``, ``algo.tex``, ``data.table.R``). A leading ``/``
    means it's a path-segment suffix (``include/R``); a trailing
    ``/`` means it's a path-segment prefix (``R/models.R``).
    """
    if offset > 0 and chars[offset - 1] in {".", "/"}:
        return True
    tail = offset + token_len
    # Trailing slash counts as a path only when an extension-bearing
    # segment follows (``R/models.R``). Slash-joined language pairs —
    # ``R/S``, ``C/C++`` — are bare language mentions and must fire.
    return (
        tail < len(chars)
        and chars[tail] == "/"
        and bool(_PATH_SEGMENT_RE.match(chars, tail + 1))
    )


_PATH_SEGMENT_RE = re.compile(
    r"[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*\.[A-Za-z0-9]+"
)


# Lines that *define* macros mention math-alphabet letters that are
# not prose: ``\def \calC {\mathcal C}``, ``\DeclareMathOperator
# {\Real}{\mathbb{R}}``, ``\newcolumntype{C}[1]{...}``. Eight labelled
# corpus FPs came from shared ``defs.tex`` preambles of this shape.
# NB: no leading ``^`` — the pattern is applied with ``match(src, pos)``
# at a computed line start, where ``^`` would not assert.
_MACRO_DEF_LINE_RE = re.compile(
    r"[ \t]*\\(?:(?:re)?new(?:command|environment)|providecommand|def"
    r"|DeclareMathOperator|DeclareRobustCommand|newcolumntype|newtheorem)\b"
)


def _is_macro_definition_line(source: str, abs_pos: int) -> bool:
    """True when the token at ``abs_pos`` (offset into ``source``) sits
    on a line whose first content is a macro-definition head."""
    line_start = source.rfind("\n", 0, abs_pos) + 1
    return bool(_MACRO_DEF_LINE_RE.match(source, line_start))


# NB: no guard for the ``R`` in "Comprehensive R Archive Network" —
# the AI precision labels disagree with each other on that phrase
# (5 FP vs 6 TP labels on identical text), and the hand-annotated
# recall corpus (CARBayesST line 441) plants it as a genuine
# violation. Ground truth wins: it fires.


# Followers that turn a lone capital letter into an eponym / labelled
# statistic ("Hubert's C index", "C-steps", "C statistic") rather than
# a language mention.
_EPONYM_FOLLOWERS_RE = re.compile(
    r"[\s~]+(?:index|indices|statistic|statistics|criterion|criteria"
    r"|step|steps)\b",
    re.IGNORECASE,
)


def _is_eponym_letter(chars: str, offset: int, token: str) -> bool:
    """True when a single-letter token is possessively attributed
    (``Hubert's C``) or names a statistic (``Harell C index``)."""
    if len(token) != 1:
        return False
    head = chars[:offset].rstrip()
    # Possessive: the previous word ends with 's (also typographic ').
    if re.search(r"[A-Za-z](?:'|’)s$", head):
        return True
    return bool(_EPONYM_FOLLOWERS_RE.match(chars, offset + 1))


# Single capital letters used as enumeration labels: "panel C",
# "Group C", "Class A'', ``Class B''", "(S, I or R)", "A, B, C and D".
_LABEL_WORDS: frozenset[str] = frozenset({
    "panel", "panels", "group", "groups", "class", "classes",
    "model", "models", "compartment", "compartments", "column",
    "columns", "plate", "arm", "arms", "factor", "factors",
    "level", "levels", "label", "labels", "letter", "letters",
})

# A chain of THREE or more comma/and/or-joined single capitals is an
# enumeration ("S, I or R", "A, B, C and D") — but only when a label
# word sits next to the chain ("compartment (S, I or R)", "factors
# S, C and F", "groups of A, B, C and D"). Without that cue, identical
# surface forms are language lists ("tools (R, S, and C API's)") and
# must fire. Pairs — "R and S", "R and Python" — never qualify.
_ENUM_CHAIN_RE = re.compile(
    r"\b[A-Z]\b(?:\s*,\s*[A-Z]\b)+\s*(?:,\s*)?(?:or|and)\s+[A-Z]\b"
)

_LABEL_WORDS_RE = None  # built lazily from _LABEL_WORDS below


def _near_label_word(chars: str, start: int, end: int) -> bool:
    global _LABEL_WORDS_RE
    if _LABEL_WORDS_RE is None:
        _LABEL_WORDS_RE = re.compile(
            r"\b(?:" + "|".join(sorted(_LABEL_WORDS)) + r")\b",
            re.IGNORECASE,
        )
    head = chars[max(0, start - 24) : start]
    tail = chars[end : end + 24]
    return bool(_LABEL_WORDS_RE.search(head) or _LABEL_WORDS_RE.search(tail))


def _is_label_letter(chars: str, offset: int, token: str) -> bool:
    """True when a single-letter token is an enumeration label, judged
    by a label word immediately before it (``panel C`` — whitespace
    adjacency only, so ``Models: R package`` still fires) or by being
    part of a label-word-adjacent chain of three or more single-letter
    labels (``S, I or R compartments``)."""
    if len(token) != 1:
        return False
    prev_word = re.search(r"([A-Za-z]+)\s+$", chars[:offset])
    if prev_word and prev_word.group(1).lower() in _LABEL_WORDS:
        return True
    for m in _ENUM_CHAIN_RE.finditer(
        chars, max(0, offset - 40), offset + 41
    ):
        if m.start() <= offset < m.end():
            return _near_label_word(chars, m.start(), m.end())
    return False


def _is_tex_amp_adjacent(source: str, abs_pos: int, abs_end: int) -> bool:
    """True when the token is glued to a literal ``\\&`` on either side
    (``R\\&D``): an abbreviation, not a language mention. The ``\\&``
    parses as a sibling macro node, so only the source shows it."""
    return source[abs_end : abs_end + 2] == "\\&" or (
        abs_pos >= 2 and source[abs_pos - 2 : abs_pos] == "\\&"
    )


def _is_table_cell_letter(source: str, abs_pos: int, abs_end: int) -> bool:
    """True when a single-letter token is a lone tabular cell —
    ``Model & R & S \\\\`` — judged by alignment chars on both sides on
    the same line. A lone letter column label is not a language
    mention."""
    line_start = source.rfind("\n", 0, abs_pos) + 1
    line_end = source.find("\n", abs_end)
    if line_end == -1:
        line_end = len(source)
    before = source[line_start:abs_pos].rstrip().rstrip("{")
    after = source[abs_end:line_end].lstrip().lstrip("}")
    return (
        before.endswith("&")
        and (after.startswith("&") or after.startswith("\\\\"))
    )


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
                    # Hyphenated prefix: ``R-code`` / ``R-centric`` /
                    # ``Sage-related``. The leading element is a bare
                    # language (or package) reference that JSS wants
                    # wrapped — emit a violation on just the prefix.
                    # ``R-squared`` is a stats term (coefficient of
                    # determination), not an R-code reference; skip.
                    if "-" in token:
                        prefix, tail = token.split("-", 1)
                        if (
                            prefix in terms
                            and not _is_lang_hyphen_term(prefix, tail)
                        ):
                            abs_pos = node.pos + offset
                            abs_end = abs_pos + len(prefix)
                            fix: Fix | None = None
                            if emit_fix:
                                fix = Fix(
                                    start=abs_pos,
                                    end=abs_end,
                                    replacement=(
                                        f"\\{wrap_macro}{{{prefix}}}"
                                    ),
                                    description=(
                                        f"wrap {prefix} in "
                                        f"\\{wrap_macro}{{}}"
                                    ),
                                    confidence="safe",
                                )
                            yield _violation(
                                tex=tex,
                                pos=abs_pos,
                                rule_id=rule_id,
                                suggestion=(
                                    f"Wrap {prefix!r} in "
                                    f"\\{wrap_macro}{{{prefix}}} "
                                    f"(found bare in {token!r})."
                                ),
                                fix=fix,
                            )
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
                if _is_filename_context(node.chars, offset, len(token)):
                    continue
                if _is_option_list_value(node.chars, offset):
                    continue
                if _disambiguates_to_method(node.chars, offset, token):
                    continue
                if _is_eponym_letter(node.chars, offset, token):
                    continue
                if _is_label_letter(node.chars, offset, token):
                    continue
                abs_pos = node.pos + offset
                abs_end = abs_pos + len(token)
                if _is_macro_definition_line(tex.source, abs_pos):
                    continue
                if _is_tex_amp_adjacent(tex.source, abs_pos, abs_end):
                    continue
                if len(token) == 1 and _is_table_cell_letter(
                    tex.source, abs_pos, abs_end
                ):
                    continue
                # Spec 008 follow-up: MARKUP-001 / MARKUP-002 each emit
                # a ``safe`` Fix that wraps the bare token in
                # ``\proglang{...}`` / ``\pkg{...}`` respectively. The
                # already-applied carve-outs (``_is_in_prose_context``
                # filters tokens inside ``\code{}`` / ``\verb`` /
                # ``\pkg{}`` / ``\proglang{}`` / math / verbatim envs;
                # ``_is_filename_context`` / ``_is_option_list_value`` /
                # ``_disambiguates_to_method`` cover ambiguous prose
                # contexts) leave only true bare prose mentions, where
                # the wrap is mechanical and the rewritten bytes do not
                # re-trigger the same rule.
                fix: Fix | None = None
                if emit_fix:
                    fix = Fix(
                        start=abs_pos,
                        end=abs_end,
                        replacement=f"\\{wrap_macro}{{{token}}}",
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
        wrap_macro="pkg", skip_initials=False, emit_fix=True,
    )
    yield from _check_title_package_idiom(doc)


# A lowercase-or-mixedCase identifier in the package-idiom shape
# (``mdsOpt``, ``ggplot2``, ``rstanarm``, ``robustlmm``) followed by
# a description separator (``:``, ``--``, ``—``). Matches the title
# convention ``\title{pkgname: description}`` and ``\title{pkgname --
# description}`` that authors of vignette papers use. Excludes
# fully-capitalised first words (``"MASS: ..."`` — also a package
# idiom but caught separately) so we only flag the cases where
# CAP-001's title-case check would otherwise spuriously fire.
_TITLE_PKG_IDIOM_RE = re.compile(
    r"^\s*([a-z][A-Za-z0-9.]*)\s*(?::|--|—|\\-\\-|\Z)"
)


def _check_title_package_idiom(
    doc: ParsedDocument,
) -> Iterator[Violation]:
    """Flag ``\\title{pkgname ...}`` openings as MARKUP-002.

    Carrier: mdsOpt.ltx:27 — ``\\title{mdsOpt -- Searching for ...}``
    where ``mdsOpt`` is a bare package-name first word that should be
    ``\\pkg{mdsOpt}``. This is the JSS-MARKUP-002-scope half of the
    JSS-CAP-001 / MARKUP-002 split documented in
    roadmap/follow-ups.md L439: CAP-001 already defers on titles
    whose first word is in the document's existing ``\\pkg{}`` set,
    but the underlying defect (missing markup) needs to surface
    somewhere — that's here.
    """
    for tex in doc.all_tex_like():
        for parent, idx, node in _helpers._iter_with_parent(tex.nodes):
            if not (
                isinstance(node, LatexMacroNode)
                and node.macroname == "title"
            ):
                continue
            argd = getattr(node, "nodeargd", None)
            if argd is None:
                continue
            group = None
            for arg in argd.argnlist or ():
                if isinstance(arg, LatexGroupNode):
                    group = arg
                    break
            if group is None:
                continue
            # Plain-text projection of the title group; if the FIRST
            # word looks like a package-idiom identifier and is NOT
            # already inside \pkg{...} in the source, fire.
            text = _project_title_plain_text(group)
            match = _TITLE_PKG_IDIOM_RE.match(text)
            if match is None:
                continue
            pkg_name = match.group(1)
            # Skip when the title source itself opens with \pkg{...}
            # (author already wrapped it).
            source = tex.source[node.pos : node.pos + node.len]
            if re.search(r"\\title\s*\{\s*\\pkg\s*\{", source):
                continue
            yield _violation(
                tex=tex,
                pos=node.pos,
                rule_id="JSS-MARKUP-002",
                suggestion=(
                    f"Wrap the leading package name {pkg_name!r} in "
                    f"\\pkg{{{pkg_name}}} in the \\title{{}} body."
                ),
            )


def _project_title_plain_text(group: Any) -> str:
    """Char-only projection of a title group (drops macros, math,
    nested groups). Used for the package-idiom prefix check.

    ``LatexSpecialsNode`` (typesetting punctuation such as ``--``,
    ``---``, ``~``, ``\\&``) contributes its ``specials_chars``
    verbatim — without it, ``\\title{pkg -- Description}`` would
    project to ``"pkg  Description"`` and the package-idiom regex
    would miss the ``--`` separator.
    """
    parts: list[str] = []
    for child in group.nodelist or ():
        if isinstance(child, LatexCharsNode):
            parts.append(child.chars)
        elif isinstance(child, LatexMacroNode):
            # Drop macro contents — we only care about the leading
            # bare-word prefix.
            break
        else:
            specials = getattr(child, "specials_chars", None)
            if specials:
                parts.append(specials)
    return "".join(parts).lstrip()


# ---------------------------------------------------------------------------
# JSS-MARKUP-003 — inline function / argument names + R sentinel values
# ---------------------------------------------------------------------------


_FUNCTION_CALL_RE = re.compile(r"\b[a-zA-Z][a-zA-Z0-9_.]*\(\s*\)")

# A code-like markup macro left open (no closing brace yet) on the
# stretch of source preceding a match — i.e. the match sits *inside*
# ``\code{...}`` / ``\texttt{...}`` / ``\pkg{...}`` etc. This is a
# source-level guard that does NOT rely on the parsed node tree: when
# a document falls back to the tolerant parser (mismatched
# environment, etc.), the tree degrades and a ``\code{f()}`` argument
# may lose its macro parent, so the ancestor-based
# ``_is_in_prose_context`` check stops recognising the wrapper and the
# function-call detector fires on already-wrapped code. Checking the
# raw source is robust to that degradation.
_OPEN_CODE_MACRO_RE = re.compile(
    r"\\(?:code|texttt|pkg|proglang|verb|fct|command|samp|file)\*?\{[^{}]*\Z"
)


def _already_code_wrapped(source: str, abs_pos: int) -> bool:
    """True when ``abs_pos`` sits inside an unclosed code-like markup
    macro on its source line (``\\code{ … <abs_pos> … }``)."""
    line_start = source.rfind("\n", 0, abs_pos) + 1
    return bool(_OPEN_CODE_MACRO_RE.search(source, line_start, abs_pos))


# A paper-defined *inline-code wrapper* macro: a ``\def`` / ``\newcommand``
# whose body renders its argument as inline code/verbatim — e.g.
# ``\def\cmd{\lstinline[...]}`` or ``\newcommand{\cmdtxt}[1]{\texttt{#1}}``
# (interp's tri/partDeriv/interp vignettes). A USE such as
# ``\cmd{interp::triangles()}`` is already code-marked, so MARKUP-003's
# function-call / sentinel detectors must not flag the tokens inside it
# (premise "bare name in prose" is false; the fix would nest \code in
# the wrapper). The wrapper's *definition* is unaffected and still
# flagged where it uses \texttt (handled by the \texttt branch).
_WRAPPER_DEF_RE = re.compile(
    r"\\(?:def\s*\\([A-Za-z@]+)"
    r"|(?:re)?newcommand\*?\s*\{\s*\\([A-Za-z@]+)\s*\})"
    r"[^\n]*?"
    r"(?:\\lstinline\b|\\(?:e|E)?[vV]erb\b|\\mintinline\b"
    r"|\\texttt\s*\{\s*#|\\code\s*\{\s*#)"
)


def _custom_code_wrapper_macros(source: str) -> frozenset[str]:
    """Names (without backslash) of paper-defined inline-code wrapper
    macros found in ``source`` — see :data:`_WRAPPER_DEF_RE`."""
    names: set[str] = set()
    for m in _WRAPPER_DEF_RE.finditer(source):
        names.add(m.group(1) or m.group(2))
    return frozenset(names)


def _inside_custom_wrapper(
    ancestors: Any, wrappers: frozenset[str]
) -> bool:
    """True when any ancestor macro is one of the paper's custom
    inline-code wrappers (so its content is already code-marked)."""
    if not wrappers:
        return False
    return any(
        isinstance(a, LatexMacroNode) and a.macroname in wrappers
        for a in ancestors
    )

# R sentinel values that should be wrapped in ``\code{}`` when they
# appear as standalone words in prose. Reviewer R5-r3 on jss5342
# explicitly called out ``NULL -> \code{NULL}`` in Table 3; the same
# JSS markup expectation applies to the closely-related missing-value
# and logical sentinels (``NA`` family, ``TRUE`` / ``FALSE``). The
# scope is intentionally conservative: it omits ``Inf`` / ``-Inf`` /
# ``NaN`` because those frequently appear as displayed math symbols
# rather than R values.
_R_SENTINEL_VALUES: frozenset[str] = frozenset({
    "NULL",
    "NA", "NA_integer_", "NA_real_", "NA_character_", "NA_complex_",
    "TRUE", "FALSE",
})

# Word-boundary token finder: an uppercase-leading identifier whose
# tail may include letters, digits, and underscores (so ``NA_integer_``
# matches in full and ``ANNULLED`` does not match ``NULL`` because the
# leading ``A`` extends the token).
_SENTINEL_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9_]*")


def check_jss_markup_003(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.all_tex_like():
        # Paper-defined inline-code wrapper macros (\cmd, \cmdtxt, ...);
        # content inside their USES is already code-marked.
        wrappers = _custom_code_wrapper_macros(tex.source)
        for node, ancestors, parent, idx in _helpers._walk_with_context(
            tex.nodes
        ):
            if isinstance(node, LatexMacroNode) and node.macroname == "texttt":
                # \texttt{...} in JSS papers should be \code{...} for code,
                # \pkg{...} for packages, \proglang{...} for languages.
                # Skip verbatim envs (where \texttt is literal), bibliography
                # envs, and content already inside JSS markup wrappers.
                if _helpers._is_inside_verbatim(ancestors):
                    continue
                if _is_inside_bibliography(ancestors):
                    continue
                if _is_inside_jss_markup(ancestors):
                    continue
                # \texttt inside \index{} (or other non-rendered macro)
                # only formats the index entry, not body text — not a
                # visible-markup issue.
                if _is_inside_invisible_macro(ancestors):
                    continue
                # NB: \texttt inside a macro-definition body
                # (``\newcommand{\Rcmd}[1]{\texttt{#1}}``) is deliberately
                # NOT skipped. Those helpers (\Rcmd, \Rarg, \fct, \File,
                # \Rlevel ...) are code-styling wrappers that JSS wants
                # defined with \code, and fixing the definition fixes
                # every use — reviewers (humans included) consistently
                # label these TP. A guard here regressed ~97 such TPs.
                # Content-aware suggestion and fix. When the argument is a
                # known language token (R, C, Stan, ...) → \proglang{X};
                # when it's a known R package → \pkg{X}; otherwise → \code.
                inner = _helpers._macro_args_text(node, parent, idx).strip()
                if inner in LANGUAGES:
                    target_macro = "proglang"
                    suggestion = (
                        f"\\texttt{{{inner}}} names a programming language; "
                        f"wrap as \\proglang{{{inner}}}."
                    )
                elif inner in R_PACKAGES:
                    target_macro = "pkg"
                    suggestion = (
                        f"\\texttt{{{inner}}} names an R package; "
                        f"wrap as \\pkg{{{inner}}}."
                    )
                else:
                    target_macro = "code"
                    suggestion = (
                        "Replace \\texttt{...} with the appropriate JSS "
                        "markup: \\code{...} for inline code, \\pkg{...} "
                        "for package names, \\proglang{...} for language "
                        "names."
                    )
                yield _violation(
                    tex=tex,
                    pos=node.pos,
                    rule_id="JSS-MARKUP-003",
                    suggestion=suggestion,
                    fix=Fix(
                        start=node.pos,
                        end=node.pos + len("\\texttt"),
                        replacement=f"\\{target_macro}",
                        description=(
                            f"replace \\texttt with \\{target_macro}"
                        ),
                        confidence="safe",
                    ),
                )
                continue
            if not isinstance(node, LatexCharsNode):
                continue
            if not _helpers._is_in_prose_context(ancestors):
                continue
            # Already inside a paper-defined inline-code wrapper
            # (\cmd{...}, \cmdtxt{...}): the content is code-marked, so
            # neither the function-call nor the sentinel detector should
            # flag tokens within it.
            if _inside_custom_wrapper(ancestors, wrappers):
                continue
            # Inside \index{}/\nomenclature{} etc.: content is registered,
            # not rendered as body text — not a visible-markup issue.
            if _is_inside_invisible_macro(ancestors):
                continue
            # Skip bibliography environments — those go through the
            # references.py rules, not the JSS markup rules. Avoids
            # false-positives on ``NA`` / ``NULL`` appearing inside
            # ``\bibitem`` titles.
            if _is_inside_bibliography(ancestors):
                continue
            for match in _FUNCTION_CALL_RE.finditer(node.chars):
                abs_pos = node.pos + match.start()
                # Source-level belt-and-suspenders: skip matches already
                # inside \code{}/\texttt{} etc. The ancestor-based prose
                # check above misses these on tolerant-parsed documents
                # whose degraded node tree drops the macro parent.
                if _already_code_wrapped(tex.source, abs_pos):
                    continue
                yield _violation(
                    tex=tex,
                    pos=abs_pos,
                    rule_id="JSS-MARKUP-003",
                    suggestion=(
                        f"Wrap {match.group(0)!r} in "
                        f"\\code{{{match.group(0)}}}."
                    ),
                )
            for match in _SENTINEL_TOKEN_RE.finditer(node.chars):
                token = match.group(0)
                if token not in _R_SENTINEL_VALUES:
                    continue
                start = match.start()
                end = match.end()
                # Option-value guard: a sentinel that is the RHS of a
                # ``key=`` assignment is an option value, not bare R
                # prose — e.g. ``\includegraphics[clip=TRUE]{...}`` or
                # ``\includegraphics[..., trim = 5 5, clip = TRUE]``,
                # and knitr chunk options (``comment=NA``). Look back
                # over whitespace for an ``=``.
                if node.chars[:start].rstrip().endswith("="):
                    continue
                abs_pos = node.pos + start
                abs_end = node.pos + end
                # Wrap is mechanical and self-stabilising: the rewritten
                # bytes ``\code{NULL}`` no longer match the sentinel
                # token (the token is now inside ``\code{}`` and skipped
                # by ``_is_in_prose_context``).
                fix = Fix(
                    start=abs_pos,
                    end=abs_end,
                    replacement=f"\\code{{{token}}}",
                    description=f"wrap {token} in \\code{{}}",
                    confidence="safe",
                )
                yield _violation(
                    tex=tex,
                    pos=abs_pos,
                    rule_id="JSS-MARKUP-003",
                    suggestion=(
                        f"Wrap bare R sentinel {token!r} in "
                        f"\\code{{{token}}}."
                    ),
                    fix=fix,
                )


# Macros whose argument is NOT rendered as body text — its content is
# registered elsewhere (the back-of-book index) or is invisible. A
# ``\texttt`` / function call / R sentinel inside one of these is not a
# visible-markup issue, so MARKUP-003 must not flag it: e.g.
# ``\newcommand{\codefunind}[1]{\codefun{#1}\index{\texttt{#1}}}`` —
# the visible styling is \codefun; the \texttt only formats the index
# entry (where \texttt is conventional and \code would be wrong). NB:
# deliberately NOT the broader _META_MACROS (which includes
# \newcommand) — a def-body \texttt that styles VISIBLE code is still a
# TP (\Rcmd / \cmdtxt), so only genuinely non-rendered commands belong
# here.
_INVISIBLE_TEXT_MACROS: frozenset[str] = frozenset(
    {"index", "nomenclature", "glossary", "glsadd"}
)


def _is_inside_invisible_macro(ancestors: Any) -> bool:
    return any(
        isinstance(a, LatexMacroNode) and a.macroname in _INVISIBLE_TEXT_MACROS
        for a in ancestors
    )


def _is_inside_jss_markup(ancestors: Any) -> bool:
    """True when any ancestor is a JSS markup wrapper (\\code, \\pkg, etc.).

    Used to avoid firing on ``\\texttt{...}`` that is already nested inside
    a JSS markup macro — the outer wrapper conveys the intent and the
    inner ``\\texttt`` is unusual but not the rule's target.
    """
    for anc in ancestors:
        if (
            isinstance(anc, LatexMacroNode)
            and anc.macroname in _helpers._MARKUP_MACROS
        ):
            return True
    return False


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
                fix=_build_markup_004_fix(node),
            )


def _build_markup_004_fix(macro: Any) -> Fix | None:
    """Build a 0-length-insert ``Fix`` that supplies the missing
    ``[<plain text>]`` optional argument immediately before the
    mandatory ``{...}`` group.

    Returns ``None`` when the mandatory group cannot be located or its
    plain-text projection is empty (rare edge case, e.g. a title that
    consists solely of math / comments).
    """
    argd = getattr(macro, "nodeargd", None)
    if argd is None:
        return None
    mandatory_group: Any = None
    for arg in argd.argnlist or ():
        if isinstance(arg, LatexGroupNode):
            delim = getattr(arg, "delimiters", None)
            if delim and delim[0] == "{":
                mandatory_group = arg
                break
    if mandatory_group is None:
        return None
    plain = _project_section_title_to_plain(mandatory_group)
    if not plain:
        return None
    insert_at = mandatory_group.pos
    replacement = f"[{plain}]"
    return Fix(
        start=insert_at,
        end=insert_at,
        replacement=replacement,
        description=(
            f"Insert plain-text optional arg [{plain}] before the "
            "section title."
        ),
        confidence="safe",
    )


def _project_section_title_to_plain(group: Any) -> str:
    """Project a section-title brace group to plain text.

    Char-data nodes contribute verbatim; macro brace-args recurse in
    (so ``\\pkg{foo}`` projects to ``foo``); math nodes and comments are
    dropped. Whitespace is collapsed to single spaces and the result is
    stripped.
    """
    if group is None:
        return ""
    parts: list[str] = []
    _collect_plain_text(group.nodelist or (), parts)
    text = "".join(parts)
    return re.sub(r"\s+", " ", text).strip()


def _collect_plain_text(nodes: Any, out: list[str]) -> None:
    for node in nodes or ():
        if node is None:
            continue
        if isinstance(node, LatexMathNode):
            continue
        if isinstance(node, LatexCharsNode):
            out.append(node.chars)
            continue
        if isinstance(node, LatexGroupNode):
            _collect_plain_text(node.nodelist or (), out)
            continue
        if isinstance(node, LatexEnvironmentNode):
            _collect_plain_text(node.nodelist or (), out)
            continue
        if isinstance(node, LatexMacroNode):
            if node.macroname in _NON_MARKUP_TITLE_MACROS:
                # Renders as no glyph or a single accented character;
                # contribute nothing to the plain-text projection.
                continue
            argd = getattr(node, "nodeargd", None)
            if argd is None:
                continue
            for arg in argd.argnlist or ():
                if isinstance(arg, LatexGroupNode):
                    delim = getattr(arg, "delimiters", None)
                    if delim and delim[0] == "{":
                        _collect_plain_text(arg.nodelist or (), out)
            continue


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


_rule = _helpers.make_rule


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
