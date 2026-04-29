"""Typography rules for the JSS journal plugin.

Rules:
  - JSS-TYPO-001 — figure / table captions end with a period.
  - JSS-TYPO-002 — captions are not wrapped in an emphasis macro
    (\\emph / \\textbf / \\textit covering the entire caption).
  - JSS-TYPO-003 — tables avoid \\footnote annotations; annotations
    go in the caption.
  - JSS-TYPO-004 — \\caption{} follows the figure / table content.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from pylatexenc.latexwalker import (
    LatexCharsNode,
    LatexEnvironmentNode,
    LatexGroupNode,
    LatexMacroNode,
)

from texlint.api import ParsedDocument, Rule, ToolConfig, Violation
from texlint.journals.jss import _catalogue_data
from texlint.journals.jss.rules import _helpers

_FIGURE_TABLE_ENVS: frozenset[str] = frozenset(
    {"figure", "figure*", "table", "table*"}
)

# Sub-float environments whose ``\\caption{}`` is conventionally a
# short non-sentence label (panel description, subplot title) — JSS
# accepts these without a trailing period. The TYPO-001 / TYPO-002
# rules should skip captions inside any of these.
_SUBFLOAT_ENVS: frozenset[str] = frozenset(
    {"subfigure", "subtable", "subfloat", "minipage", "wrapfigure",
     "wraptable", "sidewaysfigure", "sidewaystable"}
)

_EMPHASIS_MACROS: frozenset[str] = frozenset(
    {"emph", "textbf", "textit", "textsl", "textsc"}
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


def _iter_captions(
    tex: Any, *, skip_subfloats: bool = False
) -> Iterator[tuple[Any, Any, int, Any]]:
    """Yield ``(caption_macro, parent_nodelist, idx, enclosing_env_or_None)``
    for every ``\\caption`` in ``tex``.

    With ``skip_subfloats=True``, captions inside ``subfigure`` /
    ``subtable`` / ``minipage`` etc. are filtered out — those are
    panel labels (often short non-sentence strings) and JSS-TYPO-001
    / JSS-TYPO-002 don't apply.
    """
    for node, ancestors, parent, idx in _helpers._walk_with_context(tex.nodes):
        if not (
            isinstance(node, LatexMacroNode) and node.macroname == "caption"
        ):
            continue
        if skip_subfloats and _nearest_env(ancestors, _SUBFLOAT_ENVS) is not None:
            continue
        env = _nearest_env(ancestors, _FIGURE_TABLE_ENVS)
        yield node, parent, idx, env


def _nearest_env(ancestors: list[Any], env_names: frozenset[str]) -> Any:
    for anc in reversed(ancestors):
        if (
            isinstance(anc, LatexEnvironmentNode)
            and anc.environmentname in env_names
        ):
            return anc
    return None


def _first_group_arg(macro: Any, parent: Any, idx: int) -> Any:
    argd = getattr(macro, "nodeargd", None)
    if argd is not None:
        for arg in argd.argnlist or ():
            if isinstance(arg, LatexGroupNode):
                return arg
    return _helpers._next_group_arg(parent, idx)


def _group_visible_children(group: Any) -> list[Any]:
    """Children of ``group`` ignoring \\label (caption meta) and blank chars."""
    out: list[Any] = []
    for child in group.nodelist or ():
        if (
            isinstance(child, LatexMacroNode)
            and child.macroname == "label"
        ):
            continue
        if isinstance(child, LatexCharsNode) and not child.chars.strip():
            continue
        out.append(child)
    return out


def _group_plain_text(group: Any) -> str:
    parts: list[str] = []
    for child in group.nodelist or ():
        if isinstance(child, LatexCharsNode):
            parts.append(child.chars)
    return "".join(parts)


# ---------------------------------------------------------------------------
# JSS-TYPO-001 — caption ends with period
# ---------------------------------------------------------------------------


def check_jss_typo_001(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.all_tex_like():
        for node, parent, idx, env in _iter_captions(tex, skip_subfloats=True):
            if env is None:
                continue
            group = _first_group_arg(node, parent, idx)
            if group is None:
                continue
            text = _group_plain_text(group).rstrip()
            if not text:
                continue
            if text.endswith("."):
                continue
            yield _violation(
                tex=tex,
                pos=node.pos,
                rule_id="JSS-TYPO-001",
                suggestion="End the caption with a period.",
            )


# ---------------------------------------------------------------------------
# JSS-TYPO-002 — caption not wholly wrapped in emphasis
# ---------------------------------------------------------------------------


def check_jss_typo_002(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.all_tex_like():
        for node, parent, idx, env in _iter_captions(tex):
            if env is None:
                continue
            group = _first_group_arg(node, parent, idx)
            if group is None:
                continue
            visible = _strip_trailing_punct(_group_visible_children(group))
            if len(visible) != 1:
                continue
            sole = visible[0]
            if (
                isinstance(sole, LatexMacroNode)
                and sole.macroname in _EMPHASIS_MACROS
            ):
                yield _violation(
                    tex=tex,
                    pos=sole.pos,
                    rule_id="JSS-TYPO-002",
                    suggestion=(
                        f"Remove the wrapping \\{sole.macroname}{{...}} "
                        "from the caption (intra-caption markup is fine)."
                    ),
                )


def _strip_trailing_punct(visible: list[Any]) -> list[Any]:
    """Drop trailing chars-only nodes that contain only punctuation / spaces."""
    while visible:
        last = visible[-1]
        if isinstance(last, LatexCharsNode) and all(
            c in " \t\n.,;:!?-" for c in last.chars
        ):
            visible = visible[:-1]
            continue
        break
    return visible


# ---------------------------------------------------------------------------
# JSS-TYPO-003 — no \footnote inside table envs
# ---------------------------------------------------------------------------


def check_jss_typo_003(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.all_tex_like():
        for node, ancestors, _parent, _idx in _helpers._walk_with_context(
            tex.nodes
        ):
            if not (
                isinstance(node, LatexMacroNode)
                and node.macroname == "footnote"
            ):
                continue
            if _nearest_env(ancestors, frozenset({"table", "table*"})) is None:
                continue
            yield _violation(
                tex=tex,
                pos=node.pos,
                rule_id="JSS-TYPO-003",
                suggestion=(
                    "Move footnote annotations into the caption text."
                ),
            )


# ---------------------------------------------------------------------------
# JSS-TYPO-004 — \caption{} after content
# ---------------------------------------------------------------------------


def check_jss_typo_004(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.all_tex_like():
        for node in _helpers._walk(tex.nodes):
            if not (
                isinstance(node, LatexEnvironmentNode)
                and node.environmentname in _FIGURE_TABLE_ENVS
            ):
                continue
            children = list(node.nodelist or ())
            cap_idx = _first_caption_index(children)
            if cap_idx is None:
                continue
            if _has_content_before(children, cap_idx):
                continue
            yield _violation(
                tex=tex,
                pos=children[cap_idx].pos,
                rule_id="JSS-TYPO-004",
                suggestion=(
                    "Place \\caption{} after the figure / table content."
                ),
            )


def _first_caption_index(children: list[Any]) -> int | None:
    for i, child in enumerate(children):
        if (
            isinstance(child, LatexMacroNode)
            and child.macroname == "caption"
        ):
            return i
    return None


def _has_content_before(children: list[Any], cap_idx: int) -> bool:
    """True if the figure / table body has visible content before the
    first ``\\caption{}``.

    A whitespace-only chars node with many newlines in a row is a
    fingerprint of a stripped Sweave / knitr code chunk (the stripper
    blanks the chunk to ``\\n``-only filler). Treat that as content,
    since the chunk produces the figure (e.g., ``<<fig=TRUE>>=``). A
    single ``\\n`` between ``\\begin{figure}`` and the next macro is
    just normal source formatting and is NOT treated as content.
    """
    for child in children[:cap_idx]:
        if isinstance(child, LatexCharsNode):
            if not child.chars.strip():
                # Many consecutive newlines → stripped knitr chunk; count
                # as content. The threshold of 3 newlines is empirical:
                # 1-2 newlines are normal source formatting (a blank
                # line between \begin{figure} and \caption); 3+ implies
                # a multi-line chunk body.
                if child.chars.count("\n") >= 3:
                    return True
                continue
            return True
        if isinstance(child, LatexMacroNode) and child.macroname in {
            "centering", "label", "small", "footnotesize", "scriptsize",
        }:
            continue
        return True
    return False


# ---------------------------------------------------------------------------
# Rule objects
# ---------------------------------------------------------------------------


def _rule(rule_id: str, check_fn, formats: frozenset[str] | None = None) -> Rule:
    meta = _catalogue_data.RULES[rule_id]
    return Rule(
        id=rule_id,
        category=meta["category"],
        severity=meta["severity"],
        message_template=meta["message_template"],
        authority=meta["authority"],
        check=check_fn,
        formats=formats,
    )


jss_typo_001 = _rule("JSS-TYPO-001", check_jss_typo_001)
jss_typo_002 = _rule("JSS-TYPO-002", check_jss_typo_002)
jss_typo_003 = _rule("JSS-TYPO-003", check_jss_typo_003)
# TYPO-004 now fires on any tex-like input. _has_content_before
# recognises a chunk-shaped whitespace block (≥3 consecutive newlines)
# as content, so the Rnw stripper's blanked chunks are treated as
# figure source and the rule no longer false-positives on
# `<<fig=TRUE>>=` chunks placed before `\caption{}`.
jss_typo_004 = _rule("JSS-TYPO-004", check_jss_typo_004)


rules: tuple[Rule, ...] = (jss_typo_001, jss_typo_002, jss_typo_003, jss_typo_004)
