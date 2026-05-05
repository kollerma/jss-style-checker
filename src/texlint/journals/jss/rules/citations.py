"""Citations rules for the JSS journal plugin.

Rule metadata comes from ``_catalogue_data.RULES``; this module never
duplicates catalogue text.

Rules:
  - JSS-CITE-002 — first \\pkg{X} mention per distinct X needs a citation
    in the same paragraph.
  - JSS-CITE-003 — no bracket-in-bracket citation forms like
    ``(\\cite{...})`` — use ``\\citep{...}`` instead.
  - JSS-CITE-004 — hardcoded author-year ``(Name, YYYY)`` references
    bypass the bibliography; use natbib commands.
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

_CITE_MACROS: frozenset[str] = frozenset(
    {"cite", "citet", "citep", "citealp", "citealt", "citeauthor", "citeyear"}
)

# Bibliography-rendering envs that should not trigger CITE-004.
_BIB_ENVS: frozenset[str] = frozenset({"thebibliography"})

# Containers where ``\pkg{X}`` mentions cannot satisfy CITE-002 because
# JSS convention forbids (titles, section headings, keywords) inline
# citations there. The first mention typically lands in §1 (Introduction)
# with the actual ``\citep{...}``. Suppressing here matches the published
# JSS-paper conventions our corpus shows.
_NO_CITE_MACROS: frozenset[str] = frozenset(
    {
        "title", "Title", "Plaintitle", "Shorttitle",
        "Keywords", "Plainkeywords",
        "section", "subsection", "subsubsection",
        "paragraph", "subparagraph",
    }
)
_NO_CITE_ENVS: frozenset[str] = frozenset()

# Soft no-cite zones: places where citations *are* allowed but where
# the JSS convention is to NOT require one (the §1 body mention is the
# canonical citation site). Unlike hard no-cite zones, if the soft
# zone happens to contain both ``\pkg{X}`` and a ``\citep{}`` for it,
# we add ``X`` to ``seen`` so the body mention isn't re-flagged.
_SOFT_NO_CITE_MACROS: frozenset[str] = frozenset(
    {"Abstract", "Plainabstract"}
)
_SOFT_NO_CITE_ENVS: frozenset[str] = frozenset(
    {"abstract", "thebibliography"}
)
# Bibliography entries are also soft — \pkg{X} inside a \bibitem IS
# the citation; a body mention satisfies once seen.
_SOFT_NO_CITE_MACROS_FULL = _SOFT_NO_CITE_MACROS | frozenset({"bibitem"})


def _is_inside_no_cite_zone(ancestors: list[Any]) -> bool:
    for node in ancestors:
        if isinstance(node, LatexMacroNode) and node.macroname in _NO_CITE_MACROS:
            return True
        if (
            isinstance(node, LatexEnvironmentNode)
            and node.environmentname in _NO_CITE_ENVS
        ):
            return True
    return False


def _is_inside_soft_no_cite_zone(ancestors: list[Any]) -> bool:
    for node in ancestors:
        if (
            isinstance(node, LatexMacroNode)
            and node.macroname in _SOFT_NO_CITE_MACROS_FULL
        ):
            return True
        if (
            isinstance(node, LatexEnvironmentNode)
            and node.environmentname in _SOFT_NO_CITE_ENVS
        ):
            return True
    return False


# Packages bundled with the R distribution — their citation is
# subsumed by the citation for R itself, so a bare ``\pkg{parallel}``
# mention without a separate ``\citep`` does not violate CITE-002.
# Source: ``rownames(installed.packages(priority = "base"))`` on a
# stock R install.
_BASE_R_PACKAGES: frozenset[str] = frozenset(
    {
        "base", "compiler", "datasets", "graphics", "grDevices",
        "grid", "methods", "parallel", "splines", "stats", "stats4",
        "tcltk", "tools", "utils",
    }
)


# Macros whose body is a *definition* of new markup, not user-visible
# prose. ``\pkg{X}`` inside ``\newcommand{\foo}{\pkg{X}}`` is a template
# fragment; the actual mention happens at every ``\foo`` expansion. The
# rule can't reliably flag the definition site (no surrounding
# paragraph context applies) — defer to point-of-usage like BIBTEX-004.
_DEFINITION_MACROS: frozenset[str] = frozenset(
    {"newcommand", "renewcommand", "providecommand", "def", "edef",
     "newcommand*", "renewcommand*", "providecommand*"}
)


def _is_inside_definition(ancestors: list[Any]) -> bool:
    return any(
        isinstance(node, LatexMacroNode) and node.macroname in _DEFINITION_MACROS
        for node in ancestors
    )


# Pandoc-flavoured Rmd citation marker: `[@key]`, `[@key, p. 5]`,
# `[@a; @b]`, or bare `@key`. The Rmd parser passes prose to LaTeX
# parsing, but the `[@...]` syntax stays as bare characters; the LaTeX
# walker doesn't recognise it as a citation. Detect it textually so
# CITE-002 doesn't fire on a `\pkg{X}` whose Rmd-style citation is
# adjacent.
_RMD_AT_CITATION = re.compile(r"\[\s*@[A-Za-z][\w:.\-]*|(?<![A-Za-z])@[A-Za-z][\w:.\-]*")


def _has_rmd_citation_in_span(parent: Any, start: int, end: int) -> bool:
    for sibling in parent[start:end]:
        if isinstance(sibling, LatexCharsNode) and _RMD_AT_CITATION.search(
            sibling.chars
        ):
            return True
    return False


def _has_cite_in_span(parent: Any, start: int, end: int) -> bool:
    """Return ``True`` if any cite macro lives in the paragraph span,
    recursively (so cites wrapped in ``\\emph{...}`` etc. count)."""
    for descendant in _helpers._walk(parent[start:end]):
        if (
            isinstance(descendant, LatexMacroNode)
            and descendant.macroname in _CITE_MACROS
        ):
            return True
    return False


# ---------------------------------------------------------------------------
# JSS-CITE-002 — \pkg{X} needs a citation in the same paragraph.
# ---------------------------------------------------------------------------


# Tabular environments where rows are independent units — a citation
# in one row's cell shouldn't satisfy CITE-002 for ``\pkg{X}`` in
# another row. The paragraph span is narrowed to the surrounding row
# (bounded by ``\\`` / ``\tabularnewline`` / ``\hline``).
_TABULAR_ENVS: frozenset[str] = frozenset(
    {"tabular", "tabular*", "tabularx", "tabbing", "longtable", "supertabular"}
)
_ROW_SEP_MACROS: frozenset[str] = frozenset(
    {"\\", "tabularnewline", "hline", "midrule", "toprule", "bottomrule",
     "cmidrule"}
)


def _is_in_tabular(ancestors: Any) -> bool:
    for anc in ancestors:
        if (
            isinstance(anc, LatexEnvironmentNode)
            and anc.environmentname in _TABULAR_ENVS
        ):
            return True
    return False


def _paragraph_span_in_parent(
    parent: Any, idx: int, *, in_tabular: bool = False,
) -> tuple[int, int]:
    """Return ``(start_idx, end_idx)`` inclusive-exclusive for the paragraph
    within ``parent`` that contains ``parent[idx]``.

    A paragraph boundary is any :class:`LatexCharsNode` whose text contains
    a blank line; boundaries themselves are excluded from the span. When
    ``in_tabular`` is True, row-separator macros (``\\\\``, ``\\hline``,
    etc.) also count as boundaries so a citation in one cell doesn't
    satisfy ``\\pkg{X}`` in another row.
    """
    start = 0
    for i in range(idx - 1, -1, -1):
        sib = parent[i]
        if _helpers._char_has_blank_line(sib):
            start = i + 1
            break
        if in_tabular and _is_row_sep(sib):
            start = i + 1
            break
    end = len(parent)
    for i in range(idx + 1, len(parent)):
        sib = parent[i]
        if _helpers._char_has_blank_line(sib):
            end = i
            break
        if in_tabular and _is_row_sep(sib):
            end = i
            break
    return start, end


def _is_row_sep(node: Any) -> bool:
    return (
        isinstance(node, LatexMacroNode)
        and node.macroname in _ROW_SEP_MACROS
    )


# Free-form text-style citation: ``Henningsen (2008)`` /
# ``Smith and Jones (2020)`` / ``Brown et al. (2019)``. Authors who
# write a self-contained "Author (year)" string in the same paragraph
# as ``\\pkg{X}`` have effectively cited the package without using
# ``\\citep{}``. Restricted to ≥3-letter capitalised author tokens to
# avoid matching short prose like ``In (2020)``; year is 18xx-20xx
# to avoid every parenthesised number.
_TEXTUAL_AUTHOR_YEAR = re.compile(
    r"\b[A-Z][A-Za-z'À-ſ]{2,}"
    r"(?:"
    r"\s+(?:and|&)\s+[A-Z][A-Za-z'À-ſ]{2,}"
    r"|\s+et\s+al\.?"
    r")?"
    r"\s*\((?:18|19|20)\d{2}\b"
)


def _has_textual_citation_in_span(
    parent: Any, start: int, end: int,
) -> bool:
    """Return True if a paragraph carries an ``Author (year)`` string —
    common in quote envs and footnote glosses where the citation is
    spelled out rather than wrapped in ``\\citep{}``.
    """
    for sibling in parent[start:end]:
        if isinstance(sibling, LatexCharsNode) and _TEXTUAL_AUTHOR_YEAR.search(
            sibling.chars
        ):
            return True
    return False


def check_jss_cite_002(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    meta = _catalogue_data.RULES["JSS-CITE-002"]
    # `seen` spans the entire document, NOT each tex-like fragment. In
    # .Rmd input, each prose block becomes its own ParsedTexFile island;
    # a per-fragment `seen` would re-ask for a citation on every prose
    # block that mentions \pkg{X}, even when X was already cited
    # earlier in the document.
    seen: set[str] = set()
    for tex in doc.all_tex_like():
        for node, ancestors, parent, idx in _helpers._walk_with_context(tex.nodes):
            if not (
                isinstance(node, LatexMacroNode) and node.macroname == "pkg"
            ):
                continue
            name = _helpers._macro_args_text(node, parent, idx)
            if not name:
                continue
            if name in _BASE_R_PACKAGES:
                # Packages shipped with R itself (parallel, methods,
                # stats, ...) don't need a separate citation — citing
                # R covers them. Mark seen so any later mention is also
                # exempt.
                seen.add(name)
                continue
            if _is_inside_no_cite_zone(ancestors):
                # JSS style forbids citations in titles, section headings,
                # and keywords; the rule cannot be satisfied here, so
                # treat as not-a-first-mention rather than flagging an
                # unfixable violation. The first mention in §1 will still
                # be required to carry a citation.
                continue
            if _is_inside_definition(ancestors):
                # `\pkg{X}` inside a `\newcommand{\foo}{\pkg{X}}` body is
                # a template fragment, not a first-mention. The actual
                # mention happens at every `\foo` use; CITE-002 can flag
                # those instead.
                continue
            in_tab = _is_in_tabular(ancestors)
            if _is_inside_soft_no_cite_zone(ancestors):
                # \Abstract{}, abstract env, thebibliography, and
                # \bibitem are places where citations are allowed but
                # the body mention is the canonical citation site. If
                # this soft zone happens to carry both \pkg{X} and a
                # \citep{} for it, mark X as "seen" so the body mention
                # isn't re-flagged.
                start, end = _paragraph_span_in_parent(
                    parent, idx, in_tabular=in_tab,
                )
                if _has_cite_in_span(parent, start, end) or any(
                    isinstance(anc, LatexMacroNode)
                    and anc.macroname in _CITE_MACROS
                    for anc in ancestors
                ):
                    seen.add(name)
                continue
            if name in seen:
                continue
            seen.add(name)
            if any(
                isinstance(anc, LatexMacroNode)
                and anc.macroname in _CITE_MACROS
                for anc in ancestors
            ):
                # `\pkg{X}` inside a cite macro's optional argument
                # (e.g., `\citep[package \pkg{X},][]{key}`). The cite IS
                # the package's citation — the sibling-paragraph check
                # would miss it because the cite is an ancestor, not a
                # sibling.
                continue
            start, end = _paragraph_span_in_parent(
                parent, idx, in_tabular=in_tab,
            )
            if _has_cite_in_span(parent, start, end):
                continue
            if _has_rmd_citation_in_span(parent, start, end):
                # Pandoc/Rmd `[@key]` or `@key` citation in the same
                # paragraph satisfies CITE-002. The Rmd parser doesn't
                # convert these to `\cite{}` macros, so we recognise
                # them textually here.
                continue
            if _has_textual_citation_in_span(parent, start, end):
                # Free-form ``Henningsen (2008)`` / ``Smith and Jones
                # (2020)`` citation in the same paragraph (or table
                # row, when ``in_tabular`` narrows the span). Common
                # in quote envs and footnote glosses where the
                # citation is spelled out rather than wrapped in
                # ``\citep{}``.
                continue
            line, col = _helpers._lineno_col(tex, node.pos)
            yield Violation(
                file=tex.path,
                line=line,
                column=col,
                rule_id="JSS-CITE-002",
                severity=meta["severity"],
                message=meta["message_template"],
                suggestion=(
                    f"Add a citation for \\pkg{{{name}}} (e.g., "
                    f"\\citep{{…}}) within this paragraph."
                ),
                fix=None,
            )


# ---------------------------------------------------------------------------
# JSS-CITE-003 — (\cite{...}) bracket-in-bracket.
# ---------------------------------------------------------------------------


def _chars_ends_with_open_paren(node: Any) -> bool:
    if not isinstance(node, LatexCharsNode):
        return False
    text = node.chars.rstrip(" \t")
    return text.endswith("(")


def _chars_starts_with_close_paren(node: Any) -> bool:
    if not isinstance(node, LatexCharsNode):
        return False
    text = node.chars.lstrip(" \t")
    return text.startswith(")")


def check_jss_cite_003(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    meta = _catalogue_data.RULES["JSS-CITE-003"]
    for tex in doc.all_tex_like():
        for parent, idx, node in _helpers._iter_with_parent(tex.nodes):
            if not isinstance(node, LatexMacroNode):
                continue
            if node.macroname != "cite":
                continue
            # Need a LatexCharsNode right before ending with "(" and one right
            # after starting with ")". Walk backwards skipping whitespace-only
            # chars nodes — stop on the first non-whitespace text.
            before = parent[idx - 1] if idx > 0 else None
            after = parent[idx + 1] if idx + 1 < len(parent) else None
            if not _chars_ends_with_open_paren(before):
                continue
            if not _chars_starts_with_close_paren(after):
                continue
            line, col = _helpers._lineno_col(tex, node.pos)
            # Auto-fix: replace the bracketed `(\cite{key})` form with
            # `\citep{key}`. The `(` lives at the end of the
            # whitespace-stripped `before` chars node and `)` at the
            # start of the whitespace-stripped `after` chars node; the
            # macro body itself is verbatim except for the `\cite` →
            # `\citep` swap, so we keep multi-key arguments as-is.
            paren_open = before.pos + len(before.chars.rstrip(" \t")) - 1
            paren_close = after.pos + (
                len(after.chars) - len(after.chars.lstrip(" \t"))
            )
            macro_body = tex.source[node.pos : node.pos + node.len]
            replacement = "\\citep" + macro_body[len("\\cite") :]
            yield Violation(
                file=tex.path,
                line=line,
                column=col,
                rule_id="JSS-CITE-003",
                severity=meta["severity"],
                message=meta["message_template"],
                suggestion=r"Replace (\cite{...}) with \citep{...}.",
                fix=Fix(
                    start=paren_open,
                    end=paren_close + 1,
                    replacement=replacement,
                    description=r"Replace (\cite{...}) with \citep{...}.",
                    confidence="safe",
                ),
            )


# ---------------------------------------------------------------------------
# JSS-CITE-004 — hardcoded (Author, YYYY) references.
# ---------------------------------------------------------------------------

_HARDCODED_CITE_RE = re.compile(
    r"\(\s*"
    r"(?P<surname>[A-Z][A-Za-z.'\-]+)"   # Author-like first token
    r"(?:\s+(?:et\s+al\.?|and\s+[A-Z][A-Za-z.'\-]+))?"
    r",\s*"
    r"(?:19|20)\d{2}[a-z]?"
    r"\s*\)"
)


# Tokens that match the "[A-Z][A-Za-z.'-]+" surname slot but are
# actually dates, not citations. ``(April, 1961)`` and friends are
# point-in-time references, not author-year references.
_NON_AUTHOR_TOKENS: frozenset[str] = frozenset({
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
    "Jan", "Feb", "Mar", "Apr", "Jun", "Jul", "Aug", "Sep", "Sept",
    "Oct", "Nov", "Dec",
})


_MASK_MACROS: frozenset[str] = frozenset({"code", "url", "verb"})


def _collect_ancestors(
    nodes: tuple[Any, ...],
    target: Any,
    path: list[Any] | None = None,
) -> list[Any] | None:
    """Return ancestors (outermost first) whose descendant is ``target``.

    Handles unknown-macro sibling semantics: when a macro from
    :data:`_MASK_MACROS` (e.g. ``\\code``) is followed by a sibling
    :class:`LatexGroupNode`, we consider the macro an ancestor of the
    group's content. Also recurses into env/group/math/known-macro args.
    """
    if path is None:
        path = []
    seq = tuple(nodes or ())
    for i, node in enumerate(seq):
        if node is target:
            return list(path)
        children: tuple[Any, ...] = ()
        if isinstance(node, (LatexEnvironmentNode, LatexGroupNode, LatexMathNode)):
            children = tuple(node.nodelist or ())
        elif isinstance(node, LatexMacroNode):
            argd = getattr(node, "nodeargd", None)
            if argd is not None:
                children = tuple(argd.argnlist or ())
        extra: Any = None
        # Unknown-macro sibling semantics: a group after \code/\url/\verb is
        # that macro's argument.
        if (
            isinstance(node, LatexGroupNode)
            and i > 0
            and isinstance(seq[i - 1], LatexMacroNode)
            and seq[i - 1].macroname in _MASK_MACROS
        ):
            extra = seq[i - 1]
        if not children:
            continue
        if extra is not None:
            path.append(extra)
        path.append(node)
        found = _collect_ancestors(children, target, path)
        if found is not None:
            return found
        path.pop()
        if extra is not None:
            path.pop()
    return None


def _is_masked(ancestors: list[Any]) -> bool:
    if _helpers._is_inside_verbatim(ancestors):
        return True
    for anc in ancestors:
        if isinstance(anc, LatexMacroNode) and anc.macroname in _MASK_MACROS:
            return True
        if (
            isinstance(anc, LatexEnvironmentNode)
            and anc.environmentname in _BIB_ENVS
        ):
            return True
    return False


def check_jss_cite_004(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    meta = _catalogue_data.RULES["JSS-CITE-004"]
    for tex in doc.all_tex_like():
        for node in _helpers._walk(tex.nodes):
            if not isinstance(node, LatexCharsNode):
                continue
            for match in _HARDCODED_CITE_RE.finditer(node.chars):
                if match.group("surname") in _NON_AUTHOR_TOKENS:
                    # `(April, 1961)` etc. — a date, not an author-year
                    # citation. Surname slot matches month names because
                    # they're "[A-Z][a-z]+" but this isn't what the rule
                    # is meant to flag.
                    continue
                ancestors = _collect_ancestors(tex.nodes, node) or []
                if _is_masked(ancestors):
                    continue
                abs_pos = node.pos + match.start()
                line, col = _helpers._lineno_col(tex, abs_pos)
                yield Violation(
                    file=tex.path,
                    line=line,
                    column=col,
                    rule_id="JSS-CITE-004",
                    severity=meta["severity"],
                    message=meta["message_template"],
                    suggestion=(
                        f"Replace the hardcoded reference {match.group(0)!r} "
                        r"with a natbib command (e.g., \citet{Key})."
                    ),
                    fix=None,
                )


# ---------------------------------------------------------------------------
# Rule objects + module-level rules tuple
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


jss_cite_002 = _rule("JSS-CITE-002", check_jss_cite_002)
jss_cite_003 = _rule("JSS-CITE-003", check_jss_cite_003)
jss_cite_004 = _rule("JSS-CITE-004", check_jss_cite_004)


rules: tuple[Rule, ...] = (jss_cite_002, jss_cite_003, jss_cite_004)
