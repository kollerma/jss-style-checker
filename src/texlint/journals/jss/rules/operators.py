"""Operator / math-notation rules for the JSS journal plugin.

Rules:
  - JSS-OPER-001 — symbol-plus-noun constructs like ``p-value`` use a
    typeset form ``$p$~value`` (no hyphen).
  - JSS-OPER-002 — transpose written as literal ``^T`` should be ``\\top``.
    (Prime notation ``X'`` / ``^\\prime`` is NOT flagged — 31% precision
    on the labelled corpus; it's usually a derivative or a distinct
    variable, not a transpose. See check_jss_oper_002.)
  - JSS-OPER-003 — display equations have no blank lines immediately
    before or after; carve-out: equation body ending with a period
    closes a sentence and doesn't need the ``%`` wrapper.
  - JSS-OPER-004 — expectation / variance / covariance / probability use
    jss.cls shortcuts ``\\E / \\VAR / \\COV / \\Prob``. Beyond the macro
    forms (``\\mathrm{var}``, ``\\Pr``, ...) this also flags, in math
    mode, bare literal tokens (``var(``, ``Cov(``, uppercase ``P(``) and
    paper-defined aliases whose ``\\newcommand`` body resolves to a
    probability / expectation glyph (CUB's ``\\p{}``, mlt.docreg's
    ``\\Ex`` / ``\\Prob``) — both the definition site and each use.
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
)

from texlint.api import Fix, ParsedDocument, Rule, ToolConfig, Violation
from texlint.journals.jss.rules import _helpers

# Display-math envs subject to OPER-003.
_DISPLAY_EQ_ENVS: frozenset[str] = frozenset(
    {"equation", "equation*", "align", "align*", "eqnarray", "eqnarray*",
     "gather", "gather*", "multline", "multline*"}
)

# Statistical-symbol-plus-noun constructs for OPER-001.
_SYMBOL_NOUN_RE = re.compile(
    r"\b([a-z])-(value|statistic|values|statistics)\b"
)

# Non-canonical probabilistic-function macros flagged by OPER-004.
# ``mathbf`` and ``text`` join the original mathbb/mathsf/mathrm/
# operatorname set: papers commonly write ``\mathbf{E}`` (bold E for
# expectation, CARBayesST/rstpm2 pattern) or ``\text{var}`` (text-style
# variance, multistate.Rnw pattern) — both should use the jss.cls
# shortcuts (\E, \VAR, \COV, \Prob).
_NONCANON_PROB_MACROS: frozenset[str] = frozenset(
    {"mathbb", "mathsf", "mathrm", "mathbf", "text", "operatorname", "Pr"}
)
# Probability/expectation/variance/covariance argument tokens. JSS
# uses \E / \VAR / \COV / \Prob; common variants appear in the corpus
# in mixed case (``\mathrm{VAR}``) and shorthand (``\text{var}``).
_NONCANON_PROB_ARGS: frozenset[str] = frozenset(
    {"E", "Var", "VAR", "var", "Cov", "COV", "cov", "P", "Prob"}
)

# --- OPER-004 literal-token detection (in math mode only) -----------------
#
# Beyond the macro forms above, the corpus writes variance / covariance /
# probability operators as bare literal tokens: ``var(x)``, ``Cov(a, b)``,
# ``P(X \le x)``. These are flagged only inside math mode.
#
# Phase 1a (low risk): a bare ``var`` / ``cov`` / ``Var`` / ``Cov`` token
# immediately followed by ``(`` or ``[``. The negative lookbehind keeps it
# a whole token (so ``covariate`` / ``microVar`` don't match).
_LITERAL_VARCOV_RE: re.Pattern[str] = re.compile(
    r"(?<![A-Za-z\\])(var|cov|Var|Cov)(?=[(\[])"
)
# Phase 1b (moderate risk): a bare uppercase ``P`` immediately followed by
# ``(`` or ``[``. Guards baked into the pattern: uppercase only (never the
# lowercase density ``p``); not a subscript label (``A_P(x, y)`` — the
# ``_`` lookbehind); not part of an identifier / macro (a preceding letter
# or backslash).
_LITERAL_PROB_RE: re.Pattern[str] = re.compile(r"(?<![A-Za-z\\_])P(?=[(\[])")

# Relational / event tokens that mark a bare ``P(...)`` as a genuine
# probability (``P(X > x)``, ``P(A \mid B)``) rather than a function or a
# transition-probability matrix (``P(t_0, t)``) or a CDF (``P(x)``).
_PROB_ARG_RELATION_RE: re.Pattern[str] = re.compile(
    r"[=<>|]|\\(?:le|leq|ge|geq|in|mid|vert|neq|ne|leqslant|geqslant)(?![A-Za-z])"
)


def _p_literal_arg_has_relation(chars: str, open_idx: int) -> bool:
    """``chars[open_idx]`` is the ``(`` / ``[`` right after a bare ``P``.

    Return ``True`` when the balanced argument carries a relational / event
    token, i.e. the ``P`` reads as a probability. An argument that runs past
    the end of this char node can't be confirmed as a plain function call, so
    we err toward flagging (return ``True``).
    """
    open_ch = chars[open_idx]
    close_ch = ")" if open_ch == "(" else "]"
    depth = 0
    for i in range(open_idx, len(chars)):
        c = chars[i]
        if c == open_ch:
            depth += 1
        elif c == close_ch:
            depth -= 1
            if depth == 0:
                return bool(_PROB_ARG_RELATION_RE.search(chars[open_idx + 1:i]))
    return True

# --- OPER-004 custom-macro resolution (Phase 2) ---------------------------
#
# Papers alias probability / expectation operators via ``\newcommand`` &
# friends: CUB defines ``\p{}`` and mlt.docreg defines ``\Ex`` / ``\Prob``.
# We pre-scan the definitions, and when a body resolves to a probability
# (``\mathbb{P}`` / ``\mathsf{P}`` / literal ``Pr(``) or expectation
# (``\mathbb{E}`` / ``\mathsf{E}``) glyph we record the alias, then flag
# both the definition site and every use.

# Glyph macros whose single-letter arg marks the operator: ``\mathbb{P}``.
_PROB_GLYPH_MACROS: frozenset[str] = frozenset({"mathbb", "mathsf"})
# Macros that introduce / redefine another macro.
_DEF_MACROS: frozenset[str] = frozenset(
    {"newcommand", "renewcommand", "providecommand", "def"}
)
# jss.cls's own shortcuts. When a paper redefines one of these to a raw
# glyph we flag the redefinition site but NOT every use (each use already
# reads as the canonical name; fixing the definition corrects them all).
# ``Pr`` is intentionally excluded here — it has a dedicated flag_pr path.
_CANONICAL_PROB_MACROS: frozenset[str] = frozenset({"E", "VAR", "COV", "Prob"})
# Resolved shortcut → the jss.cls macro named in the violation message.
_SHORTCUT_MACRO: dict[str, str] = {"Prob": "\\Prob", "E": "\\E"}


# Catalogue-backed factories live in _helpers (one definition for all
# rule modules); the module-local names are kept for call-site brevity.
_violation = _helpers.tex_violation


# ---------------------------------------------------------------------------
# JSS-OPER-001 — p-value / t-statistic hyphenation
# ---------------------------------------------------------------------------


def check_jss_oper_001(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.all_tex_like():
        for node, ancestors in _helpers._walk_with_ancestors(tex.nodes):
            if not isinstance(node, LatexCharsNode):
                continue
            if not _helpers._is_in_prose_context(ancestors):
                continue
            for match in _SYMBOL_NOUN_RE.finditer(node.chars):
                # Skip Markdown link labels — ``[r-statistics](url)`` —
                # where the bracketed text is a site name, not a
                # statistical symbol-plus-noun construct. The Rmd
                # stripper preserves the ``[label]`` brackets but
                # blanks the URL, so the immediately-preceding ``[``
                # is a reliable signal.
                if match.start() > 0 and node.chars[match.start() - 1] == "[":
                    continue
                abs_pos = node.pos + match.start()
                abs_end = node.pos + match.end()
                sym, noun = match.group(1), match.group(2)
                replacement = f"${sym}$~{noun}"
                # The detection regex constrains the match to a single
                # lowercase symbol letter + hyphen + noun; the canonical
                # form is unambiguous, so confidence is always "safe".
                yield _violation(
                    tex=tex,
                    pos=abs_pos,
                    rule_id="JSS-OPER-001",
                    suggestion=(
                        f"Replace {match.group(0)!r} with "
                        f"'{replacement}' (italicized symbol, tie)."
                    ),
                    fix=Fix(
                        start=abs_pos,
                        end=abs_end,
                        replacement=replacement,
                        description=(
                            f"rewrite {match.group(0)} as {replacement}"
                        ),
                        confidence="safe",
                    ),
                )


# ---------------------------------------------------------------------------
# JSS-OPER-002 — transpose with \top
# ---------------------------------------------------------------------------


# Big-operator macros whose ``^T`` is an upper bound, not a transpose:
# ``\\sum_{t=1}^T``, ``\\prod_{i=2}^T``, ``\\int_0^T``, etc. The
# transpose check should not fire on these.
# Big-operator macros whose ``^T`` is an upper bound (``\\sum_{t=1}^T``,
# ``\\prod_{i=2}^T``, ``\\int_0^T``) — not a transpose. The transpose
# check should not fire on these.
_BIG_OPERATORS: frozenset[str] = frozenset({
    "sum", "prod", "int", "iint", "iiint", "oint", "coprod",
    "bigcup", "bigcap", "bigvee", "bigwedge",
    "bigoplus", "bigotimes", "bigodot",
    "biguplus", "bigsqcup",
})


def _t_caret_follows_big_operator(
    parent: Any, idx: int, match_start: int
) -> bool:
    """True when the ``^T`` at ``parent[idx].chars[match_start]`` is the
    upper-bound caret of a preceding ``\\sum_{...}``, ``\\prod_{...}``,
    ``\\int_{...}`` (or similar) — i.e., not a transpose marker.

    pylatexenc fragments ``\\sum_{t=1}^T`` into a sibling chain like:
      [LatexMacroNode \\sum, LatexCharsNode '_', LatexGroupNode {t=1},
       LatexCharsNode '^T ...']
    or, when the caret follows directly in the same chars node, into
    a single LatexCharsNode following the ``\\sum``. Walk backwards
    through subscript-shaped siblings to find the big-operator macro.
    """
    chars = parent[idx].chars
    prefix = chars[:match_start].rstrip()
    # Strip an optional ``_{...}`` or ``_X`` subscript at the end of
    # the prefix (when caret and subscript share a chars node).
    sub_match = re.search(r"_(?:\{[^{}]*\}|[A-Za-z0-9])\s*$", prefix)
    if sub_match is not None:
        prefix = prefix[: sub_match.start()].rstrip()
    elif prefix.endswith("_"):
        prefix = prefix[:-1].rstrip()
    if prefix:
        # Other math content between the operator and the caret.
        return False
    # Walk backwards through siblings, skipping a single subscript
    # (``_`` chars + group, or ``_X`` chars) — at most one subscript
    # may sit between the big operator and ``^T``.
    j = idx - 1
    saw_subscript_token = False
    saw_subscript_group = False
    while j >= 0:
        sib = parent[j]
        if isinstance(sib, LatexMacroNode) and sib.macroname in _BIG_OPERATORS:
            return True
        if isinstance(sib, LatexGroupNode) and not saw_subscript_group:
            saw_subscript_group = True
            j -= 1
            continue
        if isinstance(sib, LatexCharsNode):
            text = sib.chars.strip()
            if not text:
                j -= 1
                continue
            if text == "_":
                j -= 1
                continue
            if text.endswith("_") and not saw_subscript_token:
                saw_subscript_token = True
                j -= 1
                continue
            if re.fullmatch(r"_[A-Za-z0-9]", text) and not saw_subscript_token:
                saw_subscript_token = True
                j -= 1
                continue
            return False
        return False
    return False


def check_jss_oper_002(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    # NB: prime notation (``X'`` / ``X^\prime``) is deliberately NOT
    # flagged. The full human-labelled corpus showed the prime branch
    # at 31% precision (73 TP / 163 FP): in statistics prose a prime is
    # overwhelmingly a *different variable* (``(x, x')``), a derivative
    # (``f'(t)``, ``\dZ^\prime``), or a paired sample (``\bX - \bX'``),
    # not a transpose. The literal ``^T`` form is 99% precise (91/1) and
    # is the only convention the recall corpus tests, so OPER-002 now
    # flags ``^T`` only. (Authors using ``'`` for transpose are missed —
    # an accepted scope bound; see eval/improvement-log.md.)
    for tex in doc.all_tex_like():
        for node, ancestors, parent, idx in _helpers._walk_with_context(
            tex.nodes
        ):
            if not isinstance(node, LatexCharsNode):
                continue
            if not _helpers._is_inside_math(ancestors):
                continue
            for match in re.finditer(r"\^\s*T(?![A-Za-z])", node.chars):
                if _t_caret_follows_big_operator(
                    parent, idx, match.start()
                ):
                    continue
                abs_pos = node.pos + match.start()
                yield _violation(
                    tex=tex,
                    pos=abs_pos,
                    rule_id="JSS-OPER-002",
                    suggestion="Use '\\top' for transpose: e.g., 'X^\\top X'.",
                )


# ---------------------------------------------------------------------------
# JSS-OPER-003 — blank lines around display equations
# ---------------------------------------------------------------------------


def check_jss_oper_003(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.all_tex_like():
        for parent, idx, node in _helpers._iter_with_parent(tex.nodes):
            if not (
                isinstance(node, LatexEnvironmentNode)
                and node.environmentname in _DISPLAY_EQ_ENVS
            ):
                continue
            before = parent[idx - 1] if idx > 0 else None
            after = parent[idx + 1] if idx + 1 < len(parent) else None
            # The period-exemption only applies to the blank-line-AFTER
            # check: a display equation that ends a sentence (period in
            # the body) legitimately gets a blank line after, but a
            # blank line BEFORE \begin{} is wrong regardless of whether
            # the equation is sentence-terminal.
            ends_period = _equation_body_ends_with_period(node)
            blank_before = _chars_ends_with_blank_line(before)
            blank_after = _chars_starts_with_blank_line(after) and not ends_period
            if blank_before or blank_after:
                yield _violation(
                    tex=tex,
                    pos=node.pos,
                    rule_id="JSS-OPER-003",
                    suggestion=(
                        "Remove the blank line(s) around the display "
                        "equation (add '%' after/before to suppress the "
                        "paragraph break)."
                    ),
                )


# Macros that don't render a glyph in the equation body. Used by the
# trailing-period scan: ``\\begin{equation} ... a + b. \\label{eq:x}
# \\end{equation}`` should still count as period-terminated even
# though ``\\label`` sits between the period and ``\\end{}``.
_INVISIBLE_TRAILING_MACROS: frozenset[str] = frozenset({
    "label", "nonumber", "notag", "tag", "tag*",
    "ignorespaces", "ignorespacesafterend", "leavevmode",
})


def _equation_body_ends_with_period(env: Any) -> bool:
    """True if the last visible character in the equation body is ``.``.

    Walks ``env.nodelist`` in reverse, skipping whitespace and
    invisible macros (``\\label``, ``\\nonumber``, ``\\notag``, ...).
    Recurses into nested environments — the math body is often
    wrapped in ``aligned`` / ``cases`` / ``split`` etc., and the
    period sits inside the inner env.
    """
    for child in reversed(env.nodelist or ()):
        if isinstance(child, LatexCharsNode):
            text = child.chars.rstrip()
            if not text:
                continue
            return text.endswith(".")
        if (
            isinstance(child, LatexMacroNode)
            and child.macroname in _INVISIBLE_TRAILING_MACROS
        ):
            # ``\\label{...}`` and friends don't render — the
            # period-ending check should look past them.
            continue
        if isinstance(child, LatexEnvironmentNode):
            # Recurse into ``aligned`` / ``cases`` / ``split`` /
            # ``gathered`` / ``array`` etc. — the period typically
            # ends the inner env's body.
            return _equation_body_ends_with_period(child)
        # Visible non-chars node at the tail — we can't see a period
        # ending.
        return False
    return False


def _chars_ends_with_blank_line(node: Any) -> bool:
    """True when ``node``'s tail (the bit immediately before the next
    sibling) contains a blank-line separator that's NOT the
    fingerprint of a stripped Sweave / knitr chunk.

    The Rnw stripper blanks each chunk to ``\\n``-only filler; many
    consecutive newlines (≥3) signal a multi-line chunk, not normal
    paragraph spacing. We only care about a blank line in the LAST
    line or two of the preceding chars node — a blank line buried
    deep in the prose (e.g., between an earlier ``\\section{}`` and
    the next sentence) doesn't mean the equation has a blank line
    immediately before it.
    """
    if not isinstance(node, LatexCharsNode):
        return False
    chars = node.chars
    if not chars:
        return False
    # Tail = everything after the last non-whitespace character.
    tail_match = re.search(r"\S(\s*)\Z", chars)
    tail = tail_match.group(1) if tail_match else chars
    # Strip chunk-shaped runs before checking; a stripped chunk's
    # filler is structural, not paragraph spacing.
    stripped = re.sub(r"\n[ \t]*(?:\n[ \t]*){2,}", "\n", tail)
    return bool(_helpers._BLANK_LINE_RE.search(stripped))


def _chars_starts_with_blank_line(node: Any) -> bool:
    """Mirror of :func:`_chars_ends_with_blank_line` for the chars
    node immediately following the equation env."""
    if not isinstance(node, LatexCharsNode):
        return False
    chars = node.chars
    if not chars:
        return False
    head_match = re.match(r"(\s*)\S", chars)
    head = head_match.group(1) if head_match else chars
    stripped = re.sub(r"\n[ \t]*(?:\n[ \t]*){2,}", "\n", head)
    return bool(_helpers._BLANK_LINE_RE.search(stripped))


# ---------------------------------------------------------------------------
# JSS-OPER-004 — jss.cls probabilistic shortcuts
# ---------------------------------------------------------------------------


def _doc_uses_prob_macro(doc: ParsedDocument) -> bool:
    """True when any tex-like surface invokes ``\\Prob``.

    JSS reviewers accept ``\\Pr`` as canonical when the paper uses it
    consistently — papers with neither ``\\Prob`` nor a redefining
    ``\\newcommand{\\Pr}`` simply chose the LaTeX built-in. Only flag
    ``\\Pr`` when the paper also has ``\\Prob`` somewhere (inconsistent
    notation) or has a custom ``\\Pr`` redefinition that proves the
    author knows about the jss.cls variant.
    """
    for tex in doc.all_tex_like():
        for node in _helpers._walk(tex.nodes):
            if not isinstance(node, LatexMacroNode):
                continue
            if node.macroname == "Prob":
                return True
            if node.macroname in {"newcommand", "renewcommand", "providecommand"}:
                # Walk into the macro's first group arg to see if it
                # defines \Pr; pylatexenc represents the target macro
                # as a child of the def macro's argument.
                for child in _helpers._walk([node]):
                    if (
                        isinstance(child, LatexMacroNode)
                        and child.macroname == "Pr"
                        and child is not node
                    ):
                        return True
    return False


def _macro_first_group_text(macro: Any) -> str:
    """Text of a macro's first braced-group argument (``\\mathbb{P}`` → 'P')."""
    argd = getattr(macro, "nodeargd", None)
    if argd is not None:
        for arg in argd.argnlist or ():
            if isinstance(arg, LatexGroupNode):
                return _helpers._group_text(arg)
    return ""


def _first_macro_name(nodes: Any) -> str | None:
    """Name of the first macro node in ``nodes`` (the aliased macro)."""
    for node in nodes or ():
        if isinstance(node, LatexMacroNode):
            return node.macroname
    return None


def _resolve_prob_body(body_nodes: Any) -> str | None:
    """Classify a macro-definition body as a probability / expectation
    operator glyph.

    Returns ``"Prob"`` for ``\\mathbb{P}`` / ``\\mathsf{P}`` / literal
    ``Pr(``, ``"E"`` for ``\\mathbb{E}`` / ``\\mathsf{E}``, else ``None``.
    """
    for child in _helpers._walk(body_nodes):
        if (
            isinstance(child, LatexMacroNode)
            and child.macroname in _PROB_GLYPH_MACROS
        ):
            arg = _macro_first_group_text(child)
            if arg == "P":
                return "Prob"
            if arg == "E":
                return "E"
        elif isinstance(child, LatexCharsNode) and "Pr(" in child.chars:
            return "Prob"
    return None


def _def_groups(node: Any) -> list[Any]:
    """Braced-group arguments of a ``\\newcommand``-family definition node."""
    argd = getattr(node, "nodeargd", None)
    if argd is None:
        return []
    return [a for a in (argd.argnlist or ()) if isinstance(a, LatexGroupNode)]


def _parse_prob_def(
    node: Any, parent: Any, idx: int
) -> tuple[str | None, str | None]:
    """Extract ``(alias_name, shortcut)`` from a definition node.

    Handles ``\\newcommand{\\Ex}{\\mathbb{E}}`` (alias / body live in the
    node's braced-group args) and ``\\def\\Ex{\\mathbb{E}}`` (alias / body
    are following siblings). Returns ``(None, None)`` when the body is not
    a probability / expectation glyph.
    """
    groups = _def_groups(node)
    if len(groups) >= 2:
        alias = _first_macro_name(groups[0].nodelist)
        return alias, _resolve_prob_body(groups[-1].nodelist)
    # ``\def`` form: the alias macro and its body group are siblings.
    alias = None
    for sib in list(parent)[idx + 1 : idx + 4]:
        if alias is None and isinstance(sib, LatexMacroNode):
            alias = sib.macroname
            continue
        if isinstance(sib, LatexGroupNode):
            return alias, _resolve_prob_body(sib.nodelist)
    return None, None


def _collect_prob_aliases(
    doc: ParsedDocument,
) -> tuple[dict[str, str], list[tuple[Any, int, str, str]]]:
    """Pre-scan definitions for probability / expectation aliases.

    Returns ``(aliases, def_sites)`` where ``aliases`` maps a macro name
    to its resolved shortcut (``"Prob"`` / ``"E"``) and ``def_sites`` lists
    ``(tex, pos, alias, shortcut)`` for each flaggable definition site.
    ``\\Pr`` redefinitions are skipped — the dedicated flag_pr path owns
    them.
    """
    aliases: dict[str, str] = {}
    def_sites: list[tuple[Any, int, str, str]] = []
    for tex in doc.all_tex_like():
        for node, _anc, parent, idx in _helpers._walk_with_context(tex.nodes):
            if not (
                isinstance(node, LatexMacroNode)
                and node.macroname in _DEF_MACROS
            ):
                continue
            alias, shortcut = _parse_prob_def(node, parent, idx)
            if alias is None or shortcut is None or alias == "Pr":
                continue
            aliases[alias] = shortcut
            def_sites.append((tex, node.pos, alias, shortcut))
    return aliases, def_sites


def check_jss_oper_004(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    flag_pr = _doc_uses_prob_macro(doc)
    aliases, def_sites = _collect_prob_aliases(doc)
    # Phase 2 (i): definition / redefinition sites. These live in the
    # preamble, so they are not math-gated.
    for tex, pos, alias, shortcut in def_sites:
        yield _violation(
            tex=tex,
            pos=pos,
            rule_id="JSS-OPER-004",
            suggestion=(
                f"'\\{alias}' redefines a probability/expectation operator "
                f"as a raw glyph; use jss.cls {_SHORTCUT_MACRO[shortcut]}."
            ),
        )
    for tex in doc.all_tex_like():
        for node, ancestors, parent, idx in _helpers._walk_with_context(
            tex.nodes
        ):
            # Phase 1: bare literal operator tokens in math mode.
            if isinstance(node, LatexCharsNode):
                if not _helpers._is_inside_math(ancestors):
                    continue
                for m in _LITERAL_VARCOV_RE.finditer(node.chars):
                    token = m.group(1)
                    shortcut = "\\VAR" if token[0] in "vV" else "\\COV"
                    yield _violation(
                        tex=tex,
                        pos=node.pos + m.start(),
                        rule_id="JSS-OPER-004",
                        suggestion=(
                            f"Use the jss.cls shortcut {shortcut} instead of "
                            f"a bare '{token}(' operator."
                        ),
                    )
                for m in _LITERAL_PROB_RE.finditer(node.chars):
                    # A bare ``P(...)`` in a document that reserves ``\Prob``
                    # for real probabilities, whose argument carries no
                    # relational / event token, is a function or a
                    # transition-probability matrix (``P(t_0, t)``) or a CDF
                    # (``P(x)``), not the probability operator — don't flag it.
                    if flag_pr and not _p_literal_arg_has_relation(
                        node.chars, m.end()
                    ):
                        continue
                    yield _violation(
                        tex=tex,
                        pos=node.pos + m.start(),
                        rule_id="JSS-OPER-004",
                        suggestion=(
                            "Use the jss.cls shortcut \\Prob instead of a "
                            "bare 'P(' probability operator."
                        ),
                    )
                continue
            if not isinstance(node, LatexMacroNode):
                continue
            if not _helpers._is_inside_math(ancestors):
                continue
            # Phase 2 (ii): uses of a custom probability / expectation
            # alias. Redefined jss.cls shortcuts (``\Prob`` → ``\mathbb{P}``)
            # are flagged at the definition site only, not per use.
            if (
                node.macroname in aliases
                and node.macroname not in _CANONICAL_PROB_MACROS
            ):
                shortcut = aliases[node.macroname]
                yield _violation(
                    tex=tex,
                    pos=node.pos,
                    rule_id="JSS-OPER-004",
                    suggestion=(
                        f"'\\{node.macroname}' aliases a probability/"
                        f"expectation operator; use jss.cls "
                        f"{_SHORTCUT_MACRO[shortcut]}."
                    ),
                )
                continue
            if node.macroname == "Pr":
                if flag_pr:
                    yield _violation(
                        tex=tex,
                        pos=node.pos,
                        rule_id="JSS-OPER-004",
                        suggestion="Use \\Prob from jss.cls instead of \\Pr.",
                    )
                continue
            if node.macroname not in _NONCANON_PROB_MACROS:
                continue
            arg_text = _helpers._macro_args_text(node, parent, idx)
            if arg_text in _NONCANON_PROB_ARGS:
                yield _violation(
                    tex=tex,
                    pos=node.pos,
                    rule_id="JSS-OPER-004",
                    suggestion=(
                        "Use the jss.cls shortcut "
                        f"(\\E / \\VAR / \\COV / \\Prob) instead of "
                        f"\\{node.macroname}{{{arg_text}}}."
                    ),
                )


# ---------------------------------------------------------------------------
# Rule objects
# ---------------------------------------------------------------------------


_rule = _helpers.make_rule


jss_oper_001 = _rule("JSS-OPER-001", check_jss_oper_001)
jss_oper_002 = _rule("JSS-OPER-002", check_jss_oper_002)
# OPER-003 walks tex_like sibling nodes around a display-equation env
# and checks for blank-line text between them. The Rnw stripper
# replaces R chunks with whitespace runs; ``_chars_ends_with_blank_line``
# / ``_chars_starts_with_blank_line`` handle this by collapsing runs of
# ≥ 3 newlines (the fingerprint of a stripped multi-line chunk) before
# checking for a single blank-line separator, so the rule applies to
# both tex and rnw inputs.
jss_oper_003 = _rule(
    "JSS-OPER-003", check_jss_oper_003, formats=frozenset({"tex", "rnw"})
)
jss_oper_004 = _rule("JSS-OPER-004", check_jss_oper_004)


rules: tuple[Rule, ...] = (jss_oper_001, jss_oper_002, jss_oper_003, jss_oper_004)
