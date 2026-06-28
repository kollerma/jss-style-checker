"""Cross-reference rules for the JSS journal plugin.

Rules:
  - JSS-XREF-001 — figures / tables referenced by \\ref{}, not by number.
  - JSS-XREF-002 — equation references use ``Equation~\\ref{...}``
    rather than bare ``(\\ref{...})`` or ``\\eqref{...}`` (both render
    the same parenthesised form the reviewer discourages).
  - JSS-XREF-003 — subsection references say "Section x.y", not
    "Subsection x.y".
  - JSS-XREF-004 — numbered equations carry \\label{} and are referenced.
  - JSS-XREF-005 — captioned figures / tables carry \\label{} and are
    referenced from the text (the float analogue of JSS-XREF-004).
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

# Subset that numbers each line independently — every \label{} marks its
# own numbered equation, so each must be referenced (not just one per env).
_MULTILINE_EQ_ENVS: frozenset[str] = frozenset(
    {"align", "eqnarray", "gather"}
)


# Catalogue-backed factories live in _helpers (one definition for all
# rule modules); the module-local names are kept for call-site brevity.
_violation = _helpers.tex_violation


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
    # Citation-locator shape: ``\citet[Table 2.5]{X}`` / ``\cite[Figure 3]{X}``
    # — the optional argument is a locator into the *cited* work, parsed as
    # a chars node inside the cite macro. A cite-macro ancestor means the
    # "Table N" is the cited paper's float, not a manuscript cross-ref.
    if _is_inside_cite_macro(ancestors):
        return True
    return False


def _is_inside_cite_macro(ancestors: list[Any]) -> bool:
    for anc in ancestors:
        if (
            isinstance(anc, LatexMacroNode)
            and anc.macroname in _helpers._CITE_MACROS_FOR_SCOPE
        ):
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


_EQ_ABBREV_TAIL_RE = re.compile(r"\b(Eqs?|Eqns?)\.?\s*~?\s*$")


def _chars_ends_with_eq_abbrev(node: Any) -> tuple[int, str] | None:
    """If ``node`` is a chars node whose trailing text ends with ``Eq.``
    or ``Eqs.`` (the equation abbreviation reviewers want rewritten to
    ``Equation`` / ``Equations``), return the start offset of the
    abbreviation match and its raw match text. Otherwise ``None``.
    """
    if not isinstance(node, LatexCharsNode):
        return None
    m = _EQ_ABBREV_TAIL_RE.search(node.chars)
    if m is None:
        return None
    return m.start(), m.group(0)


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
                # ``Eq.~\ref{...}`` / ``Eqs.~\ref{...}`` — the
                # abbreviated form. The corpus convention (DBR.Rnw:183
                # et al.) wants ``Equation~\ref{...}`` /
                # ``Equations~\ref{...}`` instead. The ``~``
                # non-breaking space parses as a LatexSpecialsNode
                # sibling between the chars node carrying "Eq." and
                # the ``\ref`` macro — walk back past one such
                # specials sibling when present.
                tilde_idx: int | None = None
                if (
                    before is not None
                    and not isinstance(before, LatexCharsNode)
                    and getattr(before, "specials_chars", None) == "~"
                ):
                    tilde_idx = idx - 1
                    before = parent[idx - 2] if idx > 1 else None
                eq_abbrev = _chars_ends_with_eq_abbrev(before)
                if eq_abbrev is not None and not _label_has_non_equation_prefix(node):
                    abbrev_offset, abbrev_text = eq_abbrev
                    is_plural = abbrev_text.lower().startswith(("eqs", "eqns"))
                    canonical = "Equations" if is_plural else "Equation"
                    abbrev_start = before.pos + abbrev_offset
                    # Fix range: from the abbreviation through the
                    # macro itself, replacing everything in between
                    # (chars tail + optional ``~`` + macro body) with
                    # the canonical form. node.pos+node.len gives the
                    # end of the macro.
                    line, col = _helpers._lineno_col(tex, node.pos)
                    macro_body = tex.source[node.pos : node.pos + node.len]
                    yield Violation(
                        file=tex.path,
                        line=line,
                        column=col,
                        rule_id="JSS-XREF-002",
                        severity=meta["severity"],
                        message=meta["message_template"],
                        suggestion=(
                            f"Replace {abbrev_text.strip()!r} before "
                            f"\\ref with '{canonical}~' (capitalised, "
                            "non-breaking space)."
                        ),
                        fix=Fix(
                            start=abbrev_start,
                            end=node.pos + node.len,
                            replacement=f"{canonical}~{macro_body}",
                            description=(
                                f"replace '{abbrev_text.strip()}' with "
                                f"'{canonical}~'"
                            ),
                            confidence="safe",
                        ),
                    )
                    continue
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


_REF_MACROS: frozenset[str] = frozenset(
    {"ref", "eqref", "pageref", "nameref", "autoref", "vref", "cref",
     "Cref", "Ref", "subref"}
)


def _collect_referenced_labels(doc: ParsedDocument) -> set[str]:
    """Gather every label key referenced from ``\\ref{...}``-family macros
    across every tex_like file in the document.

    Labels can be referenced in multi-key form (``\\ref{a,b,c}``) and the
    comma-separated keys are split. Whitespace around keys is stripped.
    """
    refs: set[str] = set()
    for tex in doc.all_tex_like():
        for parent, idx, node in _helpers._iter_with_parent(tex.nodes):
            if not isinstance(node, LatexMacroNode):
                continue
            if node.macroname not in _REF_MACROS:
                continue
            # Use the shared arg extractor: it reads pylatexenc's parsed
            # argument for known macros (\ref, \pageref) and falls back to
            # the next sibling group for macros pylatexenc has no spec for
            # (\vref, \cref, \autoref, …) — otherwise their {label} parses
            # as a standalone group and the reference is missed.
            text = _helpers._macro_args_text(node, parent, idx)
            for key in text.split(","):
                key = key.strip()
                if key:
                    refs.add(key)
    return refs


def _env_label_keys(env: Any) -> list[str]:
    """Return every ``\\label{X}`` key found inside ``env``."""
    keys: list[str] = []
    for child in _helpers._walk(env.nodelist or ()):
        if not (
            isinstance(child, LatexMacroNode)
            and child.macroname == "label"
        ):
            continue
        argd = getattr(child, "nodeargd", None)
        if argd is None:
            continue
        for arg in argd.argnlist or ():
            if not isinstance(arg, LatexGroupNode):
                continue
            for ch in arg.nodelist or ():
                if isinstance(ch, LatexCharsNode):
                    k = ch.chars.strip()
                    if k:
                        keys.append(k)
    return keys


def check_jss_xref_004(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    referenced = _collect_referenced_labels(doc)
    for tex in doc.all_tex_like():
        for node, ancestors in _helpers._walk_with_ancestors(tex.nodes):
            if not isinstance(node, LatexEnvironmentNode):
                continue
            if node.environmentname not in _NUMBERED_EQ_ENVS:
                continue
            # Inner numbered envs of a ``subequations`` block share the
            # outer block's ``\label{}`` and are referenced via
            # ``\eqref{...}`` / ``\subref{...}`` against that label —
            # they don't need their own and the label-orphan check
            # below shouldn't fire on the outer either.
            if _inside_subequations(ancestors):
                continue
            # ``\tag{...}`` / ``\tag*{...}`` replaces the automatic equation
            # number with a custom label (e.g. ``\tag{\texttt{approx()}}``),
            # so the equation isn't a standard auto-numbered cross-ref
            # target — analogous to ``\nonumber``. Don't require it to be
            # \ref'd (recall-corpus trueskill \tag'd equations).
            if _env_has_tag(node):
                continue
            label_keys = _env_label_keys(node)
            if not label_keys:
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
                        "Add \\label{eq:<name>} inside the equation so it "
                        "can be referenced from the text."
                    ),
                )
                continue
            # Label(s) present. In a multi-line env (align / eqnarray /
            # gather) every line is independently numbered, so EACH label
            # marks a separately-numbered equation that should be
            # referenced — a sibling line being referenced doesn't excuse
            # an orphan one (recall-corpus romc eq:1D_example). We only
            # apply the strict per-label check when the env has no
            # \nonumber/\notag (which would unnumber a line and make its
            # label a non-target); otherwise fall back to the conservative
            # per-env check. Single-line envs (equation, multline) carry a
            # single number, so one referenced label suffices.
            if (
                node.environmentname in _MULTILINE_EQ_ENVS
                and not _env_has_nonumber(node)
            ):
                orphans = [k for k in label_keys if k not in referenced]
            elif not any(k in referenced for k in label_keys):
                orphans = label_keys
            else:
                orphans = []
            if orphans:
                yield _violation(
                    tex=tex,
                    pos=node.pos,
                    rule_id="JSS-XREF-004",
                    suggestion=(
                        f"Equation label(s) {', '.join(orphans)!r} "
                        "are never referenced from the text. Either "
                        "cite the equation via \\ref{} / \\eqref{} or "
                        "suppress the number with \\nonumber."
                    ),
                )


_NONUMBER_MACROS: frozenset[str] = frozenset({"nonumber", "notag"})
_TAG_MACROS: frozenset[str] = frozenset({"tag", "tag*"})


def _env_has_nonumber(env: Any) -> bool:
    for child in _helpers._walk(env.nodelist or ()):
        if (
            isinstance(child, LatexMacroNode)
            and child.macroname in _NONUMBER_MACROS
        ):
            return True
    return False


def _env_has_tag(env: Any) -> bool:
    for child in _helpers._walk(env.nodelist or ()):
        if (
            isinstance(child, LatexMacroNode)
            and child.macroname in _TAG_MACROS
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
# JSS-XREF-005 — figures / tables carry \label{} and are referenced
# ---------------------------------------------------------------------------

# Float environments that get a number (via \caption). Starred variants
# (figure*, table*) span both columns but are still numbered floats.
_FLOAT_ENVS: frozenset[str] = frozenset(
    {"figure", "figure*", "table", "table*"}
)

_CAPTION_MACROS: frozenset[str] = frozenset({"caption", "captionof"})

# Sub-float environments: a panel nested inside a parent float relies on
# the parent's caption (or carries its own panel caption). A float that
# contains one of these is a composite figure and is not flagged by
# JSS-XREF-006 for lacking its own top-level caption.
_SUBFLOAT_ENVS: frozenset[str] = frozenset(
    {"subfigure", "subtable", "subfloat", "minipage", "wrapfigure",
     "wraptable", "sidewaysfigure", "sidewaystable"}
)


def _env_has_caption(env: Any) -> bool:
    for child in _helpers._walk(env.nodelist or ()):
        if (
            isinstance(child, LatexMacroNode)
            and child.macroname in _CAPTION_MACROS
        ):
            return True
    return False


def _env_contains_subfloat(env: Any) -> bool:
    for child in _helpers._walk(env.nodelist or ()):
        if (
            isinstance(child, LatexEnvironmentNode)
            and child.environmentname in _SUBFLOAT_ENVS
        ):
            return True
    return False


def check_jss_xref_005(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    """Float analogue of JSS-XREF-004: a captioned (numbered) figure / table
    should carry a ``\\label{}`` and be referenced from the prose."""
    referenced = _collect_referenced_labels(doc)
    for tex in doc.all_tex_like():
        for node in _helpers._walk(tex.nodes):
            if not isinstance(node, LatexEnvironmentNode):
                continue
            if node.environmentname not in _FLOAT_ENVS:
                continue
            # Captionless floats aren't numbered, so they're not cross-ref
            # targets and a missing \label{} is not a defect (parallels the
            # \nonumber carve-out in JSS-XREF-004).
            if not _env_has_caption(node):
                continue
            label_keys = _env_label_keys(node)
            if not label_keys:
                yield _violation(
                    tex=tex,
                    pos=node.pos,
                    rule_id="JSS-XREF-005",
                    suggestion=(
                        "Add \\label{fig:<name>} / \\label{tab:<name>} to the "
                        "float so it can be referenced from the text."
                    ),
                )
                continue
            if not any(k in referenced for k in label_keys):
                yield _violation(
                    tex=tex,
                    pos=node.pos,
                    rule_id="JSS-XREF-005",
                    suggestion=(
                        f"Float label(s) {', '.join(label_keys)!r} are never "
                        "referenced from the text. Add a Figure~\\ref{} / "
                        "Table~\\ref{} callout in the prose."
                    ),
                )


# ---------------------------------------------------------------------------
# JSS-XREF-006 — figure / table floats carry a \caption{}
# ---------------------------------------------------------------------------


def check_jss_xref_006(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    """A ``figure`` / ``table`` float must carry a ``\\caption{}`` so it is
    numbered and can be cross-referenced. This is the precondition JSS-XREF-005
    assumes: a captionless float is unnumbered and silently skipped there."""
    for tex in doc.all_tex_like():
        for node in _helpers._walk(tex.nodes):
            if not isinstance(node, LatexEnvironmentNode):
                continue
            if node.environmentname not in _FLOAT_ENVS:
                continue
            if _env_has_caption(node):
                continue
            # Composite figure: a panel nested inside relies on the parent's
            # caption (or carries its own), so a missing top-level caption is
            # not a defect here.
            if _env_contains_subfloat(node):
                continue
            kind = "table" if node.environmentname.startswith("table") else "figure"
            yield _violation(
                tex=tex,
                pos=node.pos,
                rule_id="JSS-XREF-006",
                suggestion=(
                    f"Add a \\caption{{...}} to the {kind} so it is numbered "
                    "and can be referenced from the text."
                ),
            )


# ---------------------------------------------------------------------------
# Rule objects
# ---------------------------------------------------------------------------


_rule = _helpers.make_rule


jss_xref_001 = _rule("JSS-XREF-001", check_jss_xref_001)
jss_xref_002 = _rule("JSS-XREF-002", check_jss_xref_002)
jss_xref_003 = _rule("JSS-XREF-003", check_jss_xref_003)
jss_xref_004 = _rule("JSS-XREF-004", check_jss_xref_004)
jss_xref_005 = _rule("JSS-XREF-005", check_jss_xref_005)
jss_xref_006 = _rule("JSS-XREF-006", check_jss_xref_006)


rules: tuple[Rule, ...] = (
    jss_xref_001, jss_xref_002, jss_xref_003, jss_xref_004, jss_xref_005,
    jss_xref_006,
)
