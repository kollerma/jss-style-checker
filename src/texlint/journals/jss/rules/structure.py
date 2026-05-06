"""Structure rules for the JSS journal plugin.

Rules in this module:
  - JSS-STRUCT-001 — document ends with a summary/discussion section
    before the bibliography.
  - JSS-STRUCT-002 — "Acknowledgments" uses American spelling.
  - JSS-STRUCT-003 — appendix sections have descriptive titles, not a
    bare ``Appendix``.
  - JSS-STRUCT-004 — references use ``\\bibliography{}``, not a
    hand-written ``thebibliography`` environment.
  - JSS-STRUCT-005 — ``\\author{}`` separates authors with ``\\And`` /
    ``\\AND`` (not lowercase ``\\and``).
  - JSS-STRUCT-006 — appendix follows the bibliography with a page
    separator (``\\newpage`` / ``\\clearpage`` / ``\\pagebreak``).
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from typing import Any

from pylatexenc.latexwalker import (
    LatexEnvironmentNode,
    LatexGroupNode,
    LatexMacroNode,
)

from texlint.api import Fix, ParsedDocument, Rule, ToolConfig, Violation
from texlint.journals.jss import _catalogue_data
from texlint.journals.jss.rules import _helpers

# Words that mark a section as a summary / discussion / conclusion.
# ``Illustrations`` / ``Examples`` / ``Applications`` are JSS-conventional
# names for the closing examples-heavy section that doubles as a
# discussion (papers from colorspace, mlogit, etc. follow this pattern).
_SUMMARY_WORDS_RE = re.compile(
    r"\b(summary|discussion|conclusion|conclusions|concluding|"
    r"illustrations?|examples?|applications?|outlook)\b",
    flags=re.IGNORECASE,
)

# Section titles that conventionally appear AFTER the conclusion but
# before the bibliography — they're back-matter, not the document's
# main-content endpoint, so STRUCT-001 ignores them when picking the
# "last content section". Includes typical technical-appendix
# patterns (``Code for Section ...``, ``Derivation of ...``,
# ``Proof of ...``, ``Notations``, ``Glossary``) common in JSS
# papers that put their summary mid-document.
_BACKMATTER_TITLE_RE = re.compile(
    # Anchored at title start (after optional leading whitespace).
    # Prefix matching only: ``Acknowledgments`` matches via the
    # "acknowledg" prefix; "General notation" mid-title doesn't.
    r"^\s*(acknowledg|funding?|session\s*info|computational\s*details|"
    r"appendix|appendices|references|"
    r"notation|glossar|nomenclature|list\s+of\s+(?:symbols|figures|tables)|"
    r"code\s+for\s+section|derivation\s+of|proof\s+of|proofs)",
    flags=re.IGNORECASE,
)

# Page-break macros accepted by STRUCT-006.
_PAGEBREAK_MACROS: frozenset[str] = frozenset(
    {"newpage", "clearpage", "cleardoublepage", "pagebreak"}
)

# Section macros whose titles we inspect.
_SECTION_MACROS: frozenset[str] = frozenset(
    {"section", "section*", "subsection", "subsection*",
     "chapter", "chapter*"}
)

# STRUCT-001 considers only top-level sectioning — a `\subsection*{New
# Features}` at the very end of a long section shouldn't masquerade as
# the document's last section.
_TOP_LEVEL_SECTION_MACROS: frozenset[str] = frozenset(
    {"section", "section*", "chapter", "chapter*"}
)


def _first_arg_text(macro: Any, parent: Any, idx: int) -> str:
    return _helpers._macro_args_text(macro, parent, idx)


def _violation(
    *,
    tex: Any,
    pos: int,
    rule_id: str,
    suggestion: str,
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
# JSS-STRUCT-001 — ends with summary / discussion
# ---------------------------------------------------------------------------


def check_jss_struct_001(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.tex_files:
        bib_pos = _find_bibliography_pos(tex)
        if bib_pos is None:
            continue  # no bibliography → out of scope
        # Collect every top-level section before the bibliography; the
        # "last content section" is the last one whose title isn't
        # back-matter (Acknowledgments, Funding, Session Info, etc.).
        sections: list[tuple[Any, Any, int, str]] = []
        for parent, idx, node in _helpers._iter_with_parent(tex.nodes):
            if node.pos >= bib_pos:
                continue
            if (
                isinstance(node, LatexMacroNode)
                and node.macroname in _TOP_LEVEL_SECTION_MACROS
            ):
                title = _first_arg_text(node, parent, idx)
                sections.append((node, parent, idx, title))
        # Walk from the end and skip back-matter sections.
        last_content = next(
            (s for s in reversed(sections)
             if not _BACKMATTER_TITLE_RE.search(s[3])),
            None,
        )
        if last_content is None:
            continue
        node, _parent, _idx, title = last_content
        if _SUMMARY_WORDS_RE.search(title):
            continue
        yield _violation(
            tex=tex,
            pos=node.pos,
            rule_id="JSS-STRUCT-001",
            suggestion=(
                "Add a 'Summary and discussion' (or similar) section "
                "before the bibliography."
            ),
        )


def _find_bibliography_pos(tex: Any) -> int | None:
    for _parent, _idx, node in _helpers._iter_with_parent(tex.nodes):
        if (
            isinstance(node, LatexMacroNode)
            and node.macroname == "bibliography"
        ):
            return node.pos
        if (
            isinstance(node, LatexEnvironmentNode)
            and node.environmentname == "thebibliography"
        ):
            return node.pos
    return None


# ---------------------------------------------------------------------------
# JSS-STRUCT-002 — "Acknowledgments" (AE spelling)
# ---------------------------------------------------------------------------


_ACKNOWLEDGEMENT_WORD_RE = re.compile(
    r"\backnowledgement(s?)\b", flags=re.IGNORECASE
)


def _struct_002_replacement(matched: str) -> str:
    """Map ``acknowledgement[s]`` to ``acknowledgment[s]`` preserving case.

    JSS submissions use American spelling (no ``e`` before ``ment``); we
    drop the same letter regardless of upper/lower casing, so
    ``Acknowledgements`` -> ``Acknowledgments``,
    ``acknowledgement`` -> ``acknowledgment``,
    ``ACKNOWLEDGEMENTS`` -> ``ACKNOWLEDGMENTS``.
    """
    # Drop the 'e' / 'E' between 'g' (index 9) and 'm' (index 11).
    return matched[:10] + matched[11:]


def check_jss_struct_002(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    meta = _catalogue_data.RULES["JSS-STRUCT-002"]
    for tex in doc.tex_files:
        for parent, idx, node in _helpers._iter_with_parent(tex.nodes):
            if not (
                isinstance(node, LatexMacroNode)
                and node.macroname in _SECTION_MACROS
            ):
                continue
            title = _first_arg_text(node, parent, idx)
            if not _ACKNOWLEDGEMENT_WORD_RE.search(title):
                continue
            # Locate the word within the macro's source span so we can
            # emit a Fix(...) with exact byte offsets. The macro span
            # covers ``\section{...Acknowledgements...}``; we search
            # inside it for the offending word.
            macro_src = tex.source[node.pos : node.pos + node.len]
            match = _ACKNOWLEDGEMENT_WORD_RE.search(macro_src)
            line, col = _helpers._lineno_col(tex, node.pos)
            fix: Fix | None = None
            if match is not None:
                matched = match.group(0)
                replacement = _struct_002_replacement(matched)
                start = node.pos + match.start()
                end = node.pos + match.end()
                fix = Fix(
                    start=start,
                    end=end,
                    replacement=replacement,
                    description=(
                        f"Replace {matched!r} with American spelling "
                        f"{replacement!r}."
                    ),
                    confidence="safe",
                )
            yield Violation(
                file=tex.path,
                line=line,
                column=col,
                rule_id="JSS-STRUCT-002",
                severity=meta["severity"],
                message=meta["message_template"],
                suggestion=(
                    "Use 'Acknowledgments' (American spelling) — "
                    "not 'Acknowledgements'."
                ),
                fix=fix,
            )


# ---------------------------------------------------------------------------
# JSS-STRUCT-003 — appendix sections have proper titles
# ---------------------------------------------------------------------------


def check_jss_struct_003(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.tex_files:
        for env in _walk_envs(tex.nodes, "appendix"):
            for sub_parent, sub_idx, sub in _helpers._iter_with_parent(
                env.nodelist or ()
            ):
                if not (
                    isinstance(sub, LatexMacroNode)
                    and sub.macroname in _SECTION_MACROS
                ):
                    continue
                title = _first_arg_text(sub, sub_parent, sub_idx).strip()
                if _is_bare_appendix(title):
                    yield _violation(
                        tex=tex,
                        pos=sub.pos,
                        rule_id="JSS-STRUCT-003",
                        suggestion=(
                            "Give the appendix section a descriptive title "
                            "(e.g., 'More technical details'), not a bare "
                            "'Appendix'."
                        ),
                    )


def _walk_envs(nodes: Any, name: str) -> Iterator[Any]:
    for node in _helpers._walk(nodes):
        if (
            isinstance(node, LatexEnvironmentNode)
            and node.environmentname == name
        ):
            yield node


def _is_bare_appendix(title: str) -> bool:
    stripped = title.strip().lower()
    return stripped in {"appendix", "appendices"}


# ---------------------------------------------------------------------------
# JSS-STRUCT-004 — no hand-written thebibliography
# ---------------------------------------------------------------------------


def check_jss_struct_004(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.tex_files:
        for env in _walk_envs(tex.nodes, "thebibliography"):
            yield _violation(
                tex=tex,
                pos=env.pos,
                rule_id="JSS-STRUCT-004",
                suggestion=(
                    "Replace \\begin{thebibliography}...\\end{thebibliography}"
                    " with \\bibliography{<bib-file>}."
                ),
            )


# ---------------------------------------------------------------------------
# JSS-STRUCT-005 — \and separator in \author{}
# ---------------------------------------------------------------------------


def check_jss_struct_005(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    meta = _catalogue_data.RULES["JSS-STRUCT-005"]
    for tex in doc.tex_files:
        for parent, idx, node in _helpers._iter_with_parent(tex.nodes):
            if not (
                isinstance(node, LatexMacroNode)
                and node.macroname == "author"
            ):
                continue
            group = _first_group_arg(node, parent, idx)
            if group is None:
                continue
            # Each lowercase ``\and`` inside the \author{} group becomes
            # its own Violation carrying a Fix that swaps the 4 bytes
            # ``\and`` for ``\And`` (post-macro whitespace untouched —
            # the engine applies fixes in reverse-position order so
            # multiple sites compose).
            for and_node in _iter_lowercase_and(group):
                line, col = _helpers._lineno_col(tex, and_node.pos)
                fix = Fix(
                    start=and_node.pos,
                    end=and_node.pos + len("\\and"),
                    replacement="\\And",
                    description=(
                        "Replace lowercase \\and with capitalised \\And — "
                        "the JSS-canonical author separator."
                    ),
                    confidence="safe",
                )
                yield Violation(
                    file=tex.path,
                    line=line,
                    column=col,
                    rule_id="JSS-STRUCT-005",
                    severity=meta["severity"],
                    message=meta["message_template"],
                    suggestion=(
                        "Separate authors with \\And (inline) or \\AND "
                        "(line break), not lowercase \\and."
                    ),
                    fix=fix,
                )


def _first_group_arg(macro: Any, parent: Any, idx: int) -> Any:
    argd = getattr(macro, "nodeargd", None)
    if argd is not None:
        for arg in argd.argnlist or ():
            if isinstance(arg, LatexGroupNode):
                return arg
    return _helpers._next_group_arg(parent, idx)


def _iter_lowercase_and(group: Any) -> Iterator[Any]:
    """Yield every ``\\and`` macro node inside ``group`` (ordered)."""
    for node in _helpers._walk(group.nodelist or ()):
        if isinstance(node, LatexMacroNode) and node.macroname == "and":
            yield node


# ---------------------------------------------------------------------------
# JSS-STRUCT-006 — appendix follows bibliography with a page separator
# ---------------------------------------------------------------------------


def check_jss_struct_006(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.tex_files:
        bib_pos = _find_bibliography_macro_pos(tex)
        if bib_pos is None:
            continue
        appendix_env = _find_first_appendix_env(tex)
        if appendix_env is None:
            continue
        if appendix_env.pos <= bib_pos:
            continue  # appendix precedes bibliography — different layout
        if _has_pagebreak_between(tex, bib_pos, appendix_env.pos):
            continue
        yield _violation(
            tex=tex,
            pos=appendix_env.pos,
            rule_id="JSS-STRUCT-006",
            suggestion=(
                "Insert \\newpage (or \\clearpage) between \\bibliography{}"
                " and \\begin{appendix}."
            ),
        )


def _find_bibliography_macro_pos(tex: Any) -> int | None:
    for node in _helpers._walk(tex.nodes):
        if (
            isinstance(node, LatexMacroNode)
            and node.macroname == "bibliography"
        ):
            return node.pos
    return None


def _find_first_appendix_env(tex: Any) -> Any:
    for env in _walk_envs(tex.nodes, "appendix"):
        return env
    return None


def _has_pagebreak_between(tex: Any, start: int, end: int) -> bool:
    for node in _helpers._walk(tex.nodes):
        if not isinstance(node, LatexMacroNode):
            continue
        if node.macroname not in _PAGEBREAK_MACROS:
            continue
        if start < node.pos < end:
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


jss_struct_001 = _rule("JSS-STRUCT-001", check_jss_struct_001)
jss_struct_002 = _rule("JSS-STRUCT-002", check_jss_struct_002)
jss_struct_003 = _rule("JSS-STRUCT-003", check_jss_struct_003)
jss_struct_004 = _rule("JSS-STRUCT-004", check_jss_struct_004)
jss_struct_005 = _rule("JSS-STRUCT-005", check_jss_struct_005)
jss_struct_006 = _rule("JSS-STRUCT-006", check_jss_struct_006)


rules: tuple[Rule, ...] = (
    jss_struct_001,
    jss_struct_002,
    jss_struct_003,
    jss_struct_004,
    jss_struct_005,
    jss_struct_006,
)
