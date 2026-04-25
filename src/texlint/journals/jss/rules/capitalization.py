"""Capitalization rules for the JSS journal plugin.

Rules:
  - JSS-CAP-001 — ``\\title{}`` is in title style (principal words
    capitalised).
  - JSS-CAP-002 — section titles are in sentence style.
  - JSS-CAP-003 — figure / table captions are in sentence style.
  - JSS-CAP-004 — ``\\Keywords{}`` entries are in sentence case,
    comma-separated.

Heuristics tuned via the precision gate; flag rules live in the
AI-skip-list so AI labelling bypasses them entirely.
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

from texlint.api import ParsedDocument, Rule, ToolConfig, Violation
from texlint.journals.jss import _catalogue_data
from texlint.journals.jss.rules import _helpers
from texlint.journals.jss.terms import LANGUAGES, R_PACKAGES

_TITLE_STOPWORDS: frozenset[str] = frozenset(
    {"a", "an", "the", "and", "or", "but", "nor", "for", "so", "yet",
     "at", "by", "in", "of", "on", "to", "up", "via", "with", "as",
     "is", "vs"}
)

_SECTION_MACROS: frozenset[str] = frozenset(
    {"section", "section*", "subsection", "subsection*",
     "subsubsection", "subsubsection*"}
)

_FIGURE_TABLE_ENVS: frozenset[str] = frozenset(
    {"figure", "figure*", "table", "table*"}
)

_PROPER_NOUNS: frozenset[str] = LANGUAGES | R_PACKAGES


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


def _first_group_arg(macro: Any, parent: Any, idx: int) -> Any:
    argd = getattr(macro, "nodeargd", None)
    if argd is not None:
        for arg in argd.argnlist or ():
            if isinstance(arg, LatexGroupNode):
                delim = getattr(arg, "delimiters", None)
                if delim and delim[0] == "[":
                    continue
                return arg
    return _helpers._next_group_arg(parent, idx)


def _group_plain_text(group: Any) -> str:
    """Plain text of a group — strips wrapped macros like \\pkg{X} to X."""
    parts: list[str] = []
    for child in group.nodelist or ():
        if isinstance(child, LatexCharsNode):
            parts.append(child.chars)
        elif isinstance(child, LatexGroupNode):
            parts.append(_group_plain_text(child))
        elif isinstance(child, LatexMacroNode) and child.macroname == "label":
            continue
    return "".join(parts)


def _words(text: str) -> list[str]:
    return [w for w in re.split(r"[\s\-]+", text.strip()) if w]


_SENTENCE_BOUNDARY_RE = re.compile(r"[.:?!]\s+(\S+)")


def _words_with_boundary(text: str) -> list[tuple[str, bool]]:
    """Like ``_words`` but each entry carries a flag for whether the word
    starts a new sub-sentence — i.e., the previous token ended with
    ``.``, ``:``, ``?``, or ``!``. Sub-sentence-initial words are
    allowed to be capitalised under JSS sentence style.
    """
    boundary_offsets: set[int] = set()
    for m in _SENTENCE_BOUNDARY_RE.finditer(text):
        boundary_offsets.add(m.start(1))
    out: list[tuple[str, bool]] = []
    for m in re.finditer(r"\S+", text):
        word = m.group(0)
        # Strip trailing punctuation for the word view but keep the offset.
        clean = re.sub(r"^[^A-Za-z0-9]+|[^A-Za-z0-9]+$", "", word)
        if not clean:
            continue
        out.append((clean, m.start() in boundary_offsets))
    return out


def _looks_like_abbrev(token: str) -> bool:
    """True for abbreviations that are conventionally capitalised even
    in sentence style — all-caps 2–6 letter tokens (PDF, NIH, NACP),
    or mixed-case scientific shorthands like mRNA / iPad.
    """
    letters = re.sub(r"[^A-Za-z]", "", token)
    if not letters:
        return False
    if 2 <= len(letters) <= 6 and letters.isupper():
        return True
    # Mixed-case with an interior uppercase that follows a lowercase
    # (mRNA, iPad, gRPC). Single capital at the start is NOT a match.
    if any(letters[i].isupper() and letters[i - 1].islower() for i in range(1, len(letters))):
        return True
    return False


def _is_capitalised_word(word: str) -> bool:
    letters = re.sub(r"[^A-Za-z]", "", word)
    if not letters:
        return True
    return letters[0].isupper()


# ---------------------------------------------------------------------------
# JSS-CAP-001 — \title{} in title style
# ---------------------------------------------------------------------------


def check_jss_cap_001(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.all_tex_like():
        for parent, idx, node in _helpers._iter_with_parent(tex.nodes):
            if not (
                isinstance(node, LatexMacroNode) and node.macroname == "title"
            ):
                continue
            group = _first_group_arg(node, parent, idx)
            if group is None:
                continue
            text = _group_plain_text(group)
            words = _words(text)
            if not words:
                continue
            first = words[0]
            if not _is_capitalised_word(first) or all(
                w == w.lower() for w in words
            ):
                yield _violation(
                    tex=tex,
                    pos=node.pos,
                    rule_id="JSS-CAP-001",
                    suggestion=(
                        "Use title style: capitalise principal words in "
                        "the title."
                    ),
                )


# ---------------------------------------------------------------------------
# JSS-CAP-002 — section titles in sentence style
# ---------------------------------------------------------------------------


def check_jss_cap_002(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.all_tex_like():
        for parent, idx, node in _helpers._iter_with_parent(tex.nodes):
            if not (
                isinstance(node, LatexMacroNode)
                and node.macroname in _SECTION_MACROS
            ):
                continue
            group = _first_group_arg(node, parent, idx)
            if group is None:
                continue
            yield from _check_sentence_style(
                tex, node.pos, group, "JSS-CAP-002",
                "Use sentence style: capitalise only the first word "
                "(proper names remain capitalised).",
            )


# ---------------------------------------------------------------------------
# JSS-CAP-003 — captions in sentence style
# ---------------------------------------------------------------------------


def check_jss_cap_003(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.all_tex_like():
        for node, ancestors, parent, idx in _helpers._walk_with_context(
            tex.nodes
        ):
            if not (
                isinstance(node, LatexMacroNode)
                and node.macroname == "caption"
            ):
                continue
            if not any(
                isinstance(a, LatexEnvironmentNode)
                and a.environmentname in _FIGURE_TABLE_ENVS
                for a in ancestors
            ):
                continue
            group = _first_group_arg(node, parent, idx)
            if group is None:
                continue
            yield from _check_sentence_style(
                tex, node.pos, group, "JSS-CAP-003",
                "Use sentence style in the caption (capitalise only the "
                "first word; proper names remain capitalised).",
            )


def _check_sentence_style(
    tex: Any, pos: int, group: Any, rule_id: str, suggestion: str
) -> Iterator[Violation]:
    text = _group_plain_text(group)
    words = _words_with_boundary(text)
    # Flag when two or more capitalised words break sentence style.
    # Exemptions: the first word of the caption, words that follow a
    # `.`/`:`/`?`/`!` (sub-sentence start), known proper nouns, title
    # stopwords ("a", "the", ...), and abbreviations / scientific
    # shorthands like "PDF" or "mRNA".
    offenders = 0
    for idx, (word, follows_boundary) in enumerate(words):
        if idx == 0 or follows_boundary:
            continue
        bare = re.sub(r"[^A-Za-z]", "", word)
        if not bare:
            continue
        if not bare[0].isupper():
            continue
        if bare in _PROPER_NOUNS:
            continue
        if bare.lower() in _TITLE_STOPWORDS:
            continue
        if _looks_like_abbrev(bare):
            continue
        offenders += 1
    if offenders >= 2:
        yield _violation(
            tex=tex, pos=pos, rule_id=rule_id, suggestion=suggestion
        )


# ---------------------------------------------------------------------------
# JSS-CAP-004 — \Keywords sentence case
# ---------------------------------------------------------------------------


def check_jss_cap_004(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.all_tex_like():
        for parent, idx, node in _helpers._iter_with_parent(tex.nodes):
            if not (
                isinstance(node, LatexMacroNode)
                and node.macroname == "Keywords"
            ):
                continue
            group = _first_group_arg(node, parent, idx)
            if group is None:
                continue
            text = _group_plain_text(group)
            entries = [e.strip() for e in text.split(",") if e.strip()]
            if _keyword_case_violation(entries):
                yield _violation(
                    tex=tex,
                    pos=node.pos,
                    rule_id="JSS-CAP-004",
                    suggestion=(
                        "Use sentence case for keywords (capitalise only "
                        "the first word of each entry unless a proper name)."
                    ),
                )


def _keyword_case_violation(entries: list[str]) -> bool:
    for entry in entries:
        words = _words(entry)
        if len(words) < 2:
            continue
        offenders = 0
        for idx, word in enumerate(words):
            if idx == 0:
                continue
            bare = re.sub(r"[^A-Za-z]", "", word)
            if not bare:
                continue
            if not bare[0].isupper():
                continue
            if bare in _PROPER_NOUNS:
                continue
            if bare.lower() in _TITLE_STOPWORDS:
                continue
            offenders += 1
        if offenders >= 1:
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


jss_cap_001 = _rule("JSS-CAP-001", check_jss_cap_001)
jss_cap_002 = _rule("JSS-CAP-002", check_jss_cap_002)
jss_cap_003 = _rule("JSS-CAP-003", check_jss_cap_003)
jss_cap_004 = _rule("JSS-CAP-004", check_jss_cap_004)


rules: tuple[Rule, ...] = (jss_cap_001, jss_cap_002, jss_cap_003, jss_cap_004)
