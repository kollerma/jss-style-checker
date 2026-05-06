"""Cross-reference rules for the JSS journal plugin.

Rules:
  - JSS-XREF-001 — figures / tables referenced by \\ref{}, not by number.
  - JSS-XREF-002 — equation references use ``Equation~\\ref{...}``
    rather than bare ``(\\ref{...})`` or ``\\eqref{...}`` (both render
    the same parenthesised form the reviewer discourages).
  - JSS-XREF-003 — subsection references say "Section x.y", not
    "Subsection x.y".
  - JSS-XREF-004 — numbered equation environments carry \\label{}.
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
from texlint.journals.jss import _catalogue_data
from texlint.journals.jss.rules import _helpers

# "Figure 2", "Table 3", "Fig. 2", "Tab. 3" followed by a number (not
# followed by a ref macro). The trailing ``[a-z]*`` captures
# sub-figure / sub-table letters (``Figure 1b``, ``Table 2a``) so the
# whole reference span is consumed before the cross-paper-cite check
# inspects the tail.
_FIG_TAB_NUMBER_RE = re.compile(
    r"\b(?:Figure|Fig\.|Figures|Table|Tab\.|Tables)\s+\d+[a-z]*",
)

# Cite macros that mean "this figure/table number is in another
# paper": ``Figure N in \cite{...}``, ``Table 2 of \citet{X}``,
# ``Figure 1b in `\cite{X}`` (backtick punctuation between connector
# and cite). Trailing punctuation (backticks, opening parens) before
# the cite macro is tolerated.
_CITE_FOLLOWERS_RE = re.compile(
    r"\A\s*(?:in|of|from|on)\s*[`'(\[]?\s*\Z"
)

# Author-year inline cite preceding the match: ``(2010, Figure 3)``,
# ``(McNeil 2009, Table 2)``. The number mention is the cited paper's
# numbering, not a label in this manuscript.
_INSIDE_AUTHOR_YEAR_PAREN_RE = re.compile(
    r"\(\s*(?:[A-Z][A-Za-z\-']+(?:,\s*[A-Z][A-Za-z\-']+|\s+(?:and|&)\s+[A-Z][A-Za-z\-']+)*"
    r"\s+)?(?:19|20)\d{2}[a-z]?(?:,\s*p\.?\s*\d+)?,\s*\Z"
)

# Anaphoric reference to a previously cited paper: ``Figure N from that
# paper``, ``Table 2 of their study``. Narrow phrasing — matches only
# when the trailing prose names the cited paper through ``that`` /
# ``their`` (or ``the cited|referenced``), so generic "Table 2 of the
# vignette" stays flagged.
_ANAPHORIC_PAPER_REF_RE = re.compile(
    r"\A\s*(?:in|of|from|on)\s+"
    r"(?:that|their|the\s+(?:cited|referenced))\s+"
    r"(?:paper|article|study|work)\b",
    flags=re.IGNORECASE,
)

# "Subsection 3.2" / "Subsection~3.2" — needs replacement with "Section".
_SUBSECTION_RE = re.compile(r"\bSubsection[s]?\s*~?\s*\d", flags=re.ASCII)

# Numbered equation environments (unlabelled ones trigger XREF-004).
_NUMBERED_EQ_ENVS: frozenset[str] = frozenset(
    {"equation", "align", "eqnarray", "gather", "multline"}
)


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
# JSS-XREF-001 — Figure/Table N by number
# ---------------------------------------------------------------------------


def _is_cross_paper_reference(
    chars: str, match_start: int, match_end: int,
    parent: Any, idx: int, ancestors: list[Any],
) -> bool:
    """True when the ``Figure N`` / ``Table N`` mention is a reference
    to a CITED external paper, not to a float in this manuscript.

    Three shapes:
    - ``Figure N {in|of|from|on} \\cite*{...}`` — the trailing prose
      after the match contains a connector word and the next sibling
      is a cite macro.
    - ``({Author, }YYYY, Figure N)`` — the match sits inside a
      hardcoded author-year parenthetical citation. (CITE-004 handles
      flagging the parenthetical itself separately.)
    - ``\\footnote{... \\cite{...} ... Figure N ...}`` — figure
      mention inside a footnote whose body cites another work; the
      footnote is discussing the cited paper, so the figure number
      refers to that paper's figure, not the current manuscript's.
    """
    # Trailing-cite shape: the immediate text after the match is
    # connector-only ("in", "of", "from", "on"), followed by a cite
    # macro sibling.
    tail = chars[match_end:]
    if _CITE_FOLLOWERS_RE.match(tail) and idx + 1 < len(parent):
        nxt = parent[idx + 1]
        if (
            isinstance(nxt, LatexMacroNode)
            and nxt.macroname in _helpers._CITE_MACROS_FOR_SCOPE
        ):
            return True
    # Author-year preceding-paren shape — last 60 chars before match.
    head = chars[max(0, match_start - 60) : match_start]
    if _INSIDE_AUTHOR_YEAR_PAREN_RE.search(head):
        return True
    # Anaphoric-paper shape: ``Figure N from that paper``, ``Table 2
    # of their study``.
    if _ANAPHORIC_PAPER_REF_RE.match(tail):
        return True
    # Footnote-with-cite shape: the figure mention sits inside a
    # \footnote whose body contains a \cite — likely discussing the
    # cited paper.
    if _is_in_cited_footnote(ancestors):
        return True
    return False


def _is_in_cited_footnote(ancestors: list[Any]) -> bool:
    for anc in reversed(ancestors):
        if (
            isinstance(anc, LatexMacroNode)
            and anc.macroname == "footnote"
        ):
            return _macro_body_has_cite(anc)
    return False


def _macro_body_has_cite(macro: Any) -> bool:
    argd = getattr(macro, "nodeargd", None)
    if argd is None:
        return False
    for arg in argd.argnlist or ():
        if not isinstance(arg, LatexGroupNode):
            continue
        for descendant in _helpers._walk(arg.nodelist or ()):
            if (
                isinstance(descendant, LatexMacroNode)
                and descendant.macroname in _helpers._CITE_MACROS_FOR_SCOPE
            ):
                return True
    return False


def check_jss_xref_001(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.all_tex_like():
        for node, ancestors, parent, idx in _helpers._walk_with_context(
            tex.nodes
        ):
            if not isinstance(node, LatexCharsNode):
                continue
            if not _helpers._is_in_prose_context(ancestors):
                continue
            for match in _FIG_TAB_NUMBER_RE.finditer(node.chars):
                if _is_cross_paper_reference(
                    node.chars, match.start(), match.end(),
                    parent, idx, ancestors,
                ):
                    continue
                abs_pos = node.pos + match.start()
                yield _violation(
                    tex=tex,
                    pos=abs_pos,
                    rule_id="JSS-XREF-001",
                    suggestion=(
                        f"Replace {match.group(0)!r} with "
                        f"'{match.group(0).split()[0]}~\\ref{{<label>}}'."
                    ),
                )


# ---------------------------------------------------------------------------
# JSS-XREF-002 — (\ref{...}) paren-wrapped
# ---------------------------------------------------------------------------


def _chars_ends_with_open_paren(node: Any) -> bool:
    if not isinstance(node, LatexCharsNode):
        return False
    text = node.chars.rstrip(" \t\n")
    return text.endswith("(")


def _chars_starts_with_close_paren(node: Any) -> bool:
    if not isinstance(node, LatexCharsNode):
        return False
    text = node.chars.lstrip(" \t\n")
    return text.startswith(")")


# Label-prefix conventions that are clearly NOT equations: sectioning,
# figure/table cross-refs, model/algorithm/appendix labels, etc. When a
# parenthesised \ref points at one of these, the rule should not fire
# (the "Equation~\\ref{...}" wording wouldn't make sense). Labels with
# no colon, or with a colon prefix not in this set (eq:, eqn:, formula:,
# def:, ...), still fire — those are predominantly equation refs in
# the corpus.
_NON_EQUATION_LABEL_PREFIXES: frozenset[str] = frozenset({
    "sec", "subsec", "subsubsec", "ssec", "section",
    "fig", "figure", "tab", "table",
    "alg", "algorithm", "app", "appendix",
    "chap", "chapter", "ch",
    "mod", "model",
    "lst", "listing", "code",
})


def _label_has_non_equation_prefix(node: Any) -> bool:
    """True if the macro's first arg looks like ``foo:bar`` with ``foo`` in
    the non-equation prefix set. Returns ``False`` when the label has no
    prefix or an unknown prefix — those are still treated as
    equation-like by the rule (matches corpus convention)."""
    argd = getattr(node, "nodeargd", None)
    if argd is None:
        return False
    label_text = ""
    for arg in argd.argnlist or ():
        if isinstance(arg, LatexGroupNode):
            for child in arg.nodelist or ():
                if isinstance(child, LatexCharsNode):
                    label_text += child.chars
            break
    label_text = label_text.strip()
    if ":" not in label_text:
        return False
    prefix = label_text.split(":", 1)[0].strip().lower()
    return prefix in _NON_EQUATION_LABEL_PREFIXES


def _eqref_label_text(node: Any) -> str:
    """Return the label text inside an ``\\eqref{...}`` macro, or ``""``."""
    argd = getattr(node, "nodeargd", None)
    if argd is None:
        return ""
    label_text = ""
    for arg in argd.argnlist or ():
        if isinstance(arg, LatexGroupNode):
            for child in arg.nodelist or ():
                if isinstance(child, LatexCharsNode):
                    label_text += child.chars
            break
    return label_text


def check_jss_xref_002(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    meta = _catalogue_data.RULES["JSS-XREF-002"]
    for tex in doc.all_tex_like():
        for parent, idx, node in _helpers._iter_with_parent(tex.nodes):
            if not isinstance(node, LatexMacroNode):
                continue
            if node.macroname == "ref":
                before = parent[idx - 1] if idx > 0 else None
                after = parent[idx + 1] if idx + 1 < len(parent) else None
                if not _chars_ends_with_open_paren(before):
                    continue
                if not _chars_starts_with_close_paren(after):
                    continue
                if _label_has_non_equation_prefix(node):
                    continue
                # Auto-fix: replace ``(\ref{label})`` with
                # ``Equation~\ref{label}``. The matching pre-conditions
                # already guarantee a single ``\ref`` macro tightly nested
                # between ``(`` and ``)`` (the chars node before ends with
                # ``(`` after stripping trailing whitespace, and the chars
                # node after starts with ``)`` after stripping leading
                # whitespace). Multi-ref / mixed-token cases like
                # ``(\ref{a}, \ref{b})`` never satisfy those conditions
                # because the comma-separated siblings break the
                # adjacency, so a fix here is unambiguous.
                paren_open = (
                    before.pos + len(before.chars.rstrip(" \t\n")) - 1
                )
                paren_close = after.pos + (
                    len(after.chars) - len(after.chars.lstrip(" \t\n"))
                )
                macro_body = tex.source[node.pos : node.pos + node.len]
                replacement = "Equation~" + macro_body
                line, col = _helpers._lineno_col(tex, node.pos)
                yield Violation(
                    file=tex.path,
                    line=line,
                    column=col,
                    rule_id="JSS-XREF-002",
                    severity=meta["severity"],
                    message=meta["message_template"],
                    suggestion=(
                        "Replace '(\\ref{...})' or '\\eqref{...}' with "
                        "'Equation~\\ref{...}' (capitalised, non-breaking "
                        "space)."
                    ),
                    fix=Fix(
                        start=paren_open,
                        end=paren_close + 1,
                        replacement=replacement,
                        description=(
                            r"replace (\ref{}) with Equation~\ref{}"
                        ),
                        confidence="safe",
                    ),
                )
            elif node.macroname == "eqref":
                # ``\eqref{label}`` renders as ``(N)``, the same
                # parenthesised form reviewer P10 discourages. Same
                # defect class as ``(\ref{label})`` so it shares the
                # rule id. Honour the non-equation-prefix filter to
                # avoid renaming references whose label clearly points
                # at a section / figure / table / algorithm.
                if _label_has_non_equation_prefix(node):
                    continue
                label_text = _eqref_label_text(node)
                if not label_text:
                    continue
                # Auto-fix: rewrite ``\eqref{label}`` to
                # ``Equation~\ref{label}`` (drop the ``eq`` prefix).
                replacement = "Equation~\\ref{" + label_text + "}"
                line, col = _helpers._lineno_col(tex, node.pos)
                yield Violation(
                    file=tex.path,
                    line=line,
                    column=col,
                    rule_id="JSS-XREF-002",
                    severity=meta["severity"],
                    message=meta["message_template"],
                    suggestion=(
                        "Replace '\\eqref{...}' with 'Equation~\\ref{...}' "
                        "(capitalised, non-breaking space; \\eqref renders "
                        "as parenthesised which reviewers discourage)."
                    ),
                    fix=Fix(
                        start=node.pos,
                        end=node.pos + node.len,
                        replacement=replacement,
                        description=(
                            r"replace \eqref{} with Equation~\ref{}"
                        ),
                        confidence="safe",
                    ),
                )


# ---------------------------------------------------------------------------
# JSS-XREF-003 — "Subsection N.N" → "Section N.N"
# ---------------------------------------------------------------------------


def check_jss_xref_003(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.all_tex_like():
        for node, ancestors in _helpers._walk_with_ancestors(tex.nodes):
            if not isinstance(node, LatexCharsNode):
                continue
            if not _helpers._is_in_prose_context(ancestors):
                continue
            for match in _SUBSECTION_RE.finditer(node.chars):
                abs_pos = node.pos + match.start()
                yield _violation(
                    tex=tex,
                    pos=abs_pos,
                    rule_id="JSS-XREF-003",
                    suggestion=(
                        "Use 'Section N.N' (or 'Section~\\ref{<label>}'), "
                        "not 'Subsection N.N'."
                    ),
                )


# ---------------------------------------------------------------------------
# JSS-XREF-004 — numbered equation missing \label{}
# ---------------------------------------------------------------------------


def check_jss_xref_004(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.all_tex_like():
        for node, ancestors in _helpers._walk_with_ancestors(tex.nodes):
            if not isinstance(node, LatexEnvironmentNode):
                continue
            if node.environmentname not in _NUMBERED_EQ_ENVS:
                continue
            if _env_has_label(node):
                continue
            # Inner numbered envs of a ``subequations`` block share the
            # outer block's ``\label{}`` and are referenced via
            # ``\eqref{...}`` / ``\subref{...}`` against that label —
            # they don't need their own.
            if _inside_subequations(ancestors):
                continue
            # ``\nonumber`` / ``\notag`` inside a single-line equation
            # env (``equation``, ``multline``) suppresses the equation
            # number, so the equation isn't a cross-ref target and a
            # missing ``\label{}`` is not a defect. Multi-line envs
            # (``align``, ``eqnarray``, ``gather``) carry per-line
            # numbering — a ``\nonumber`` on one line doesn't unnumber
            # the others, so they still need their own labels.
            if (
                node.environmentname in {"equation", "multline"}
                and _env_has_nonumber(node)
            ):
                continue
            yield _violation(
                tex=tex,
                pos=node.pos,
                rule_id="JSS-XREF-004",
                suggestion=(
                    "Add \\label{eq:<name>} inside the equation so it can "
                    "be referenced from the text."
                ),
            )


_NONUMBER_MACROS: frozenset[str] = frozenset({"nonumber", "notag"})


def _env_has_nonumber(env: Any) -> bool:
    for child in _helpers._walk(env.nodelist or ()):
        if (
            isinstance(child, LatexMacroNode)
            and child.macroname in _NONUMBER_MACROS
        ):
            return True
    return False


def _inside_subequations(ancestors: list[Any]) -> bool:
    for anc in ancestors:
        if (
            isinstance(anc, LatexEnvironmentNode)
            and anc.environmentname == "subequations"
        ):
            return True
    return False


def _env_has_label(env: Any) -> bool:
    for child in _helpers._walk(env.nodelist or ()):
        if (
            isinstance(child, LatexMacroNode)
            and child.macroname == "label"
        ):
            return True
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


jss_xref_001 = _rule("JSS-XREF-001", check_jss_xref_001)
jss_xref_002 = _rule("JSS-XREF-002", check_jss_xref_002)
jss_xref_003 = _rule("JSS-XREF-003", check_jss_xref_003)
jss_xref_004 = _rule("JSS-XREF-004", check_jss_xref_004)


rules: tuple[Rule, ...] = (jss_xref_001, jss_xref_002, jss_xref_003, jss_xref_004)
