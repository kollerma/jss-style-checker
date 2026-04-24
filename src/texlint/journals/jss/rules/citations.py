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

from texlint.api import ParsedDocument, Rule, ToolConfig, Violation
from texlint.journals.jss import _catalogue_data
from texlint.journals.jss.rules import _helpers

_CITE_MACROS: frozenset[str] = frozenset(
    {"cite", "citet", "citep", "citealp", "citealt", "citeauthor", "citeyear"}
)

# Bibliography-rendering envs that should not trigger CITE-004.
_BIB_ENVS: frozenset[str] = frozenset({"thebibliography"})


# ---------------------------------------------------------------------------
# JSS-CITE-002 — \pkg{X} needs a citation in the same paragraph.
# ---------------------------------------------------------------------------


def _paragraph_span_in_parent(
    parent: Any, idx: int
) -> tuple[int, int]:
    """Return ``(start_idx, end_idx)`` inclusive-exclusive for the paragraph
    within ``parent`` that contains ``parent[idx]``.

    A paragraph boundary is any :class:`LatexCharsNode` whose text contains
    a blank line; boundaries themselves are excluded from the span.
    """
    start = 0
    for i in range(idx - 1, -1, -1):
        if _helpers._char_has_blank_line(parent[i]):
            start = i + 1
            break
    end = len(parent)
    for i in range(idx + 1, len(parent)):
        if _helpers._char_has_blank_line(parent[i]):
            end = i
            break
    return start, end


def check_jss_cite_002(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    meta = _catalogue_data.RULES["JSS-CITE-002"]
    for tex in doc.all_tex_like():
        seen: set[str] = set()
        for parent, idx, node in _helpers._iter_with_parent(tex.nodes):
            if not (
                isinstance(node, LatexMacroNode) and node.macroname == "pkg"
            ):
                continue
            name = _helpers._macro_args_text(node, parent, idx)
            if not name:
                continue
            if name in seen:
                continue
            seen.add(name)
            start, end = _paragraph_span_in_parent(parent, idx)
            if any(
                isinstance(sibling, LatexMacroNode)
                and sibling.macroname in _CITE_MACROS
                for sibling in parent[start:end]
            ):
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
            yield Violation(
                file=tex.path,
                line=line,
                column=col,
                rule_id="JSS-CITE-003",
                severity=meta["severity"],
                message=meta["message_template"],
                suggestion=r"Replace (\cite{...}) with \citep{...}.",
                fix=None,
            )


# ---------------------------------------------------------------------------
# JSS-CITE-004 — hardcoded (Author, YYYY) references.
# ---------------------------------------------------------------------------

_HARDCODED_CITE_RE = re.compile(
    r"\(\s*"
    r"[A-Z][A-Za-z.'\-]+"               # Author surname
    r"(?:\s+(?:et\s+al\.?|and\s+[A-Z][A-Za-z.'\-]+))?"
    r",\s*"
    r"(?:19|20)\d{2}[a-z]?"
    r"\s*\)"
)


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
