"""Preamble rules for the JSS journal plugin.

Rules in this module:
  - JSS-PRE-001 — \\documentclass must be jss with a valid class option.
  - JSS-PRE-002 — preamble defines \\Address{}.
  - JSS-PRE-003 — if \\title{} has markup, \\Plaintitle{} is also defined.
  - JSS-PRE-004 — \\Abstract{} is present and not the sentinel placeholder.
  - JSS-PRE-005 — \\Keywords{} is present and not the sentinel placeholder.
  - JSS-PRE-006 — \\Plaintitle / \\Plainauthor / \\Plainkeywords contain no
    LaTeX markup (PDF metadata must be plain text).
  - JSS-PRE-007 — if \\author{} has markup, \\Plainauthor{} is also defined.
  - JSS-PRE-008 — if \\Keywords{} has markup, \\Plainkeywords{} is also
    defined.

PRE-003/007/008 fire only when the target macro's argument contains LaTeX
markup (any macro call, math, or line-break). A plain-text argument does
not require a companion Plain* command (FR-019).
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from pylatexenc.latexwalker import (
    LatexCharsNode,
    LatexGroupNode,
    LatexMacroNode,
    LatexMathNode,
    LatexSpecialsNode,
)

from texlint.api import ParsedDocument, Rule, ToolConfig, Violation
from texlint.journals.jss import _catalogue_data
from texlint.journals.jss.rules import _helpers


_VALID_CLASS_OPTIONS: frozenset[str] = frozenset(
    {"article", "codesnippet", "bookreview", "softwarereview", "shortnames", "nojss"}
)

# JSS sentinels that jss.cls uses as placeholder defaults.
_ABSTRACT_SENTINEL = "an abstract is required"
_KEYWORDS_SENTINEL = "at least one keyword is required"


def _iter_macros(
    tex: Any, name: str
) -> Iterator[tuple[Any, tuple[Any, ...], int]]:
    """Yield every ``(node, parent, idx)`` for macros named ``name`` in ``tex``."""
    for parent, idx, node in _helpers._iter_with_parent(tex.nodes):
        if isinstance(node, LatexMacroNode) and node.macroname == name:
            yield node, parent, idx


def _first_macro(tex: Any, name: str) -> tuple[Any, tuple[Any, ...], int] | None:
    for triple in _iter_macros(tex, name):
        return triple
    return None


def _first_group_arg(macro: Any, parent: tuple[Any, ...], idx: int) -> Any:
    """Return the first ``LatexGroupNode`` argument of ``macro`` — checked
    in ``nodeargd.argnlist`` first, then the next sibling (unknown macros)."""
    argd = getattr(macro, "nodeargd", None)
    if argd is not None:
        for arg in argd.argnlist or ():
            if isinstance(arg, LatexGroupNode):
                return arg
    return _helpers._next_group_arg(parent, idx)


def _group_contains_markup(group: Any) -> bool:
    """True when any descendant of ``group`` is a macro, math, or specials."""
    if group is None:
        return False
    for node in _helpers._walk(group.nodelist or ()):
        if isinstance(node, (LatexMacroNode, LatexMathNode, LatexSpecialsNode)):
            return True
    return False


def _group_plain_text(group: Any) -> str:
    """Concatenate plain char content of ``group`` (no macro expansion)."""
    if group is None:
        return ""
    parts: list[str] = []
    for node in _helpers._walk(group.nodelist or ()):
        if isinstance(node, LatexCharsNode):
            parts.append(node.chars)
    return "".join(parts).strip()


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


def _violation_at_file_start(
    *, tex: Any, rule_id: str, suggestion: str
) -> Violation:
    """A preamble-level violation with no single macro to anchor on — point
    at the top of the file so the author sees it on the file banner."""
    meta = _catalogue_data.RULES[rule_id]
    return Violation(
        file=tex.path,
        line=1,
        column=1,
        rule_id=rule_id,
        severity=meta["severity"],
        message=meta["message_template"],
        suggestion=suggestion,
        fix=None,
    )


# ---------------------------------------------------------------------------
# JSS-PRE-001 — \documentclass[...]{jss}
# ---------------------------------------------------------------------------


def _class_and_options(
    tex: Any,
) -> tuple[Any, str | None, list[str]] | None:
    """Return ``(macro, class_name, options)`` for the first \\documentclass
    in ``tex``, or ``None`` if there isn't one."""
    triple = _first_macro(tex, "documentclass")
    if triple is None:
        return None
    macro, parent, idx = triple
    argd = getattr(macro, "nodeargd", None)
    class_name: str | None = None
    options: list[str] = []
    if argd is not None:
        for arg in argd.argnlist or ():
            if isinstance(arg, LatexGroupNode):
                text = _group_plain_text(arg)
                # First group is options (optional), second is class name.
                # pylatexenc packs optional args as separate args; the
                # mandatory arg is the one whose raw source starts with '{'.
                delimiters = getattr(arg, "delimiters", None)
                if delimiters and delimiters[0] == "[":
                    options = [x.strip() for x in text.split(",") if x.strip()]
                else:
                    class_name = text
    return macro, class_name, options


def check_jss_pre_001(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.tex_files:
        info = _class_and_options(tex)
        if info is None:
            continue
        macro, class_name, options = info
        if class_name == "jss":
            # Validate options: allow any known option; at most one of the
            # mutually-exclusive class-type options may be specified.
            unknown = [o for o in options if o not in _VALID_CLASS_OPTIONS]
            if unknown:
                yield _violation(
                    tex=tex,
                    pos=macro.pos,
                    rule_id="JSS-PRE-001",
                    suggestion=(
                        f"Unknown jss class option(s): {unknown!r}. "
                        "Allowed: article, codesnippet, bookreview, "
                        "softwarereview (optionally with shortnames, nojss)."
                    ),
                )
            continue
        yield _violation(
            tex=tex,
            pos=macro.pos,
            rule_id="JSS-PRE-001",
            suggestion=(
                "Use \\documentclass[article]{jss} (or codesnippet / "
                "bookreview / softwarereview)."
            ),
        )


# ---------------------------------------------------------------------------
# JSS-PRE-002 — \Address{...} present
# ---------------------------------------------------------------------------


def check_jss_pre_002(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.tex_files:
        if _first_macro(tex, "Address") is None and _has_jss_class(tex):
            yield _violation_at_file_start(
                tex=tex,
                rule_id="JSS-PRE-002",
                suggestion=(
                    "Add \\Address{...} in the preamble with author "
                    "affiliation and e-mail."
                ),
            )


def _has_jss_class(tex: Any) -> bool:
    info = _class_and_options(tex)
    return bool(info and info[1] == "jss")


# ---------------------------------------------------------------------------
# JSS-PRE-003 / PRE-007 / PRE-008 — markup ↔ Plain* pair
# ---------------------------------------------------------------------------


def _check_markup_plain_pair(
    tex: Any, *, markup_macro: str, plain_macro: str, rule_id: str
) -> Iterator[Violation]:
    triple = _first_macro(tex, markup_macro)
    if triple is None:
        return
    macro, parent, idx = triple
    group = _first_group_arg(macro, parent, idx)
    if not _group_contains_markup(group):
        return
    if _first_macro(tex, plain_macro) is not None:
        return
    yield _violation(
        tex=tex,
        pos=macro.pos,
        rule_id=rule_id,
        suggestion=(
            f"\\{markup_macro}{{}} contains LaTeX markup; add a \\{plain_macro}"
            f"{{}} with the markup-free form for PDF metadata."
        ),
    )


def check_jss_pre_003(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.tex_files:
        yield from _check_markup_plain_pair(
            tex, markup_macro="title", plain_macro="Plaintitle",
            rule_id="JSS-PRE-003",
        )


def check_jss_pre_007(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.tex_files:
        yield from _check_markup_plain_pair(
            tex, markup_macro="author", plain_macro="Plainauthor",
            rule_id="JSS-PRE-007",
        )


def check_jss_pre_008(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.tex_files:
        yield from _check_markup_plain_pair(
            tex, markup_macro="Keywords", plain_macro="Plainkeywords",
            rule_id="JSS-PRE-008",
        )


# ---------------------------------------------------------------------------
# JSS-PRE-004 / PRE-005 — Abstract / Keywords present + not sentinel
# ---------------------------------------------------------------------------


def _check_required_macro(
    tex: Any, *, macro_name: str, sentinel: str, rule_id: str,
    suggestion_missing: str, suggestion_sentinel: str,
) -> Iterator[Violation]:
    if not _has_jss_class(tex):
        return
    triple = _first_macro(tex, macro_name)
    if triple is None:
        yield _violation_at_file_start(
            tex=tex, rule_id=rule_id, suggestion=suggestion_missing
        )
        return
    macro, parent, idx = triple
    group = _first_group_arg(macro, parent, idx)
    text = _group_plain_text(group)
    if sentinel in text.lower():
        yield _violation(
            tex=tex, pos=macro.pos, rule_id=rule_id,
            suggestion=suggestion_sentinel,
        )


def check_jss_pre_004(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.tex_files:
        yield from _check_required_macro(
            tex,
            macro_name="Abstract",
            sentinel=_ABSTRACT_SENTINEL,
            rule_id="JSS-PRE-004",
            suggestion_missing=(
                "Add \\Abstract{...} in the preamble with the paper's abstract."
            ),
            suggestion_sentinel=(
                "Replace the jss.cls placeholder text with the actual abstract."
            ),
        )


def check_jss_pre_005(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.tex_files:
        yield from _check_required_macro(
            tex,
            macro_name="Keywords",
            sentinel=_KEYWORDS_SENTINEL,
            rule_id="JSS-PRE-005",
            suggestion_missing=(
                "Add \\Keywords{...} in the preamble with comma-separated keywords."
            ),
            suggestion_sentinel=(
                "Replace the jss.cls placeholder text with the actual keywords."
            ),
        )


# ---------------------------------------------------------------------------
# JSS-PRE-006 — Plain* commands must not contain LaTeX markup
# ---------------------------------------------------------------------------


_PLAIN_MACROS: tuple[str, ...] = ("Plaintitle", "Plainauthor", "Plainkeywords")


def check_jss_pre_006(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.tex_files:
        for name in _PLAIN_MACROS:
            for macro, parent, idx in _iter_macros(tex, name):
                group = _first_group_arg(macro, parent, idx)
                if not _group_contains_markup(group):
                    continue
                yield _violation(
                    tex=tex,
                    pos=macro.pos,
                    rule_id="JSS-PRE-006",
                    suggestion=(
                        f"Strip LaTeX macros from \\{name}{{}}: PDF metadata"
                        " must be plain text."
                    ),
                )


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


jss_pre_001 = _rule("JSS-PRE-001", check_jss_pre_001)
jss_pre_002 = _rule("JSS-PRE-002", check_jss_pre_002)
jss_pre_003 = _rule("JSS-PRE-003", check_jss_pre_003)
jss_pre_004 = _rule("JSS-PRE-004", check_jss_pre_004)
jss_pre_005 = _rule("JSS-PRE-005", check_jss_pre_005)
jss_pre_006 = _rule("JSS-PRE-006", check_jss_pre_006)
jss_pre_007 = _rule("JSS-PRE-007", check_jss_pre_007)
jss_pre_008 = _rule("JSS-PRE-008", check_jss_pre_008)


rules: tuple[Rule, ...] = (
    jss_pre_001,
    jss_pre_002,
    jss_pre_003,
    jss_pre_004,
    jss_pre_005,
    jss_pre_006,
    jss_pre_007,
    jss_pre_008,
)
