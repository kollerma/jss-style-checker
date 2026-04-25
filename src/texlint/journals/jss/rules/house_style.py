"""House-style rules for the JSS journal plugin.

Rules:
  - JSS-HOUSE-001 — "e.g." and "i.e." are followed by a comma.
  - JSS-HOUSE-002 — book editions are "2nd" / "3rd" / etc., not
    "second" / "2e".
  - JSS-HOUSE-003 (info) — preamble avoids \\usepackage for packages
    jss.cls already loads (graphicx, xcolor, ae, fancyvrb, hyperref).
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from typing import Any

from pylatexenc.latexwalker import (
    LatexCharsNode,
    LatexGroupNode,
    LatexMacroNode,
)

from texlint.api import ParsedDocument, Rule, ToolConfig, Violation
from texlint.journals.jss import _catalogue_data
from texlint.journals.jss.rules import _helpers

_EG_IE_RE = re.compile(r"\b(e\.g\.|i\.e\.)(?!,)")

_WORDY_EDITION_RE = re.compile(
    r"^(?:first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|"
    r"1e|2e|3e|4e|5e|6e|7e|8e|9e|10e)$",
    flags=re.IGNORECASE,
)

# Packages that jss.cls already loads (per catalogue note on HOUSE-003).
_JSS_LOADED_PACKAGES: frozenset[str] = frozenset(
    {"graphicx", "xcolor", "ae", "fancyvrb", "hyperref"}
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
# JSS-HOUSE-001 — "e.g." / "i.e." need a comma
# ---------------------------------------------------------------------------


def check_jss_house_001(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.all_tex_like():
        for node, ancestors in _helpers._walk_with_ancestors(tex.nodes):
            if not isinstance(node, LatexCharsNode):
                continue
            if not _helpers._is_in_prose_context(ancestors):
                continue
            for match in _EG_IE_RE.finditer(node.chars):
                abs_pos = node.pos + match.start()
                yield _violation(
                    tex=tex,
                    pos=abs_pos,
                    rule_id="JSS-HOUSE-001",
                    suggestion=(
                        f"Add a comma after {match.group(0)!r}: "
                        f"'{match.group(0)},'."
                    ),
                )


# ---------------------------------------------------------------------------
# JSS-HOUSE-002 — edition in BibTeX
# ---------------------------------------------------------------------------


def _iter_bib_entries(doc: ParsedDocument) -> Iterator[tuple[Any, Any]]:
    """Yield referenced ``(bib_file, entry)`` pairs. See
    ``_helpers._iter_referenced_entries`` for scope semantics."""
    yield from _helpers._iter_referenced_entries(doc)


def check_jss_house_002(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for bib, entry in _iter_bib_entries(doc):
        field = _helpers._lc_fields(entry).get("edition")
        if field is None:
            continue
        value = str(field.value).strip()
        if not _WORDY_EDITION_RE.match(value):
            continue
        start = getattr(entry, "start_line", 0) or 0
        meta = _catalogue_data.RULES["JSS-HOUSE-002"]
        yield Violation(
            file=bib.path,
            line=start + 1,
            column=None,
            rule_id="JSS-HOUSE-002",
            severity=meta["severity"],
            message=meta["message_template"],
            suggestion=(
                f"Replace edition {value!r} with an ordinal form "
                "(e.g., '2nd', '3rd')."
            ),
            fix=None,
        )


# ---------------------------------------------------------------------------
# JSS-HOUSE-003 (info) — duplicate \usepackage
# ---------------------------------------------------------------------------


def check_jss_house_003(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.all_tex_like():
        for parent, idx, node in _helpers._iter_with_parent(tex.nodes):
            if not (
                isinstance(node, LatexMacroNode)
                and node.macroname == "usepackage"
            ):
                continue
            name = _usepackage_name(node, parent, idx)
            if not name:
                continue
            if name not in _JSS_LOADED_PACKAGES:
                continue
            yield _violation(
                tex=tex,
                pos=node.pos,
                rule_id="JSS-HOUSE-003",
                suggestion=(
                    f"Remove \\usepackage{{{name}}} — jss.cls already "
                    "loads it."
                ),
            )


def _usepackage_name(macro: Any, parent: Any, idx: int) -> str:
    """Extract the first mandatory arg of ``\\usepackage`` — the package name."""
    argd = getattr(macro, "nodeargd", None)
    if argd is not None:
        for arg in argd.argnlist or ():
            if isinstance(arg, LatexGroupNode):
                delim = getattr(arg, "delimiters", None)
                if delim and delim[0] == "[":
                    continue  # skip the [options] arg
                return _group_chars(arg)
    sibling = _helpers._next_group_arg(parent, idx)
    if sibling is not None:
        return _group_chars(sibling)
    return ""


def _group_chars(group: Any) -> str:
    parts: list[str] = []
    for child in group.nodelist or ():
        if isinstance(child, LatexCharsNode):
            parts.append(child.chars)
    return "".join(parts).strip()


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


jss_house_001 = _rule("JSS-HOUSE-001", check_jss_house_001)
jss_house_002 = _rule("JSS-HOUSE-002", check_jss_house_002)
jss_house_003 = _rule("JSS-HOUSE-003", check_jss_house_003)


rules: tuple[Rule, ...] = (jss_house_001, jss_house_002, jss_house_003)
