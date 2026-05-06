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

from texlint.api import Fix, ParsedDocument, Rule, ToolConfig, Violation
from texlint.journals.jss import _catalogue_data
from texlint.journals.jss.rules import _helpers

_EG_IE_RE = re.compile(r"\b(e\.g\.|i\.e\.)(?!,)")

_WORDY_EDITION_RE = re.compile(
    r"^(?:first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|"
    r"1e|2e|3e|4e|5e|6e|7e|8e|9e|10e)$",
    flags=re.IGNORECASE,
)

# Mapping from non-canonical edition shorthand to the JSS-canonical
# short-ordinal form. Covers every form `_WORDY_EDITION_RE` matches.
_EDITION_CANONICAL: dict[str, str] = {
    "first":   "1st",
    "second":  "2nd",
    "third":   "3rd",
    "fourth":  "4th",
    "fifth":   "5th",
    "sixth":   "6th",
    "seventh": "7th",
    "eighth":  "8th",
    "ninth":   "9th",
    "tenth":   "10th",
    "1e":  "1st",
    "2e":  "2nd",
    "3e":  "3rd",
    "4e":  "4th",
    "5e":  "5th",
    "6e":  "6th",
    "7e":  "7th",
    "8e":  "8th",
    "9e":  "9th",
    "10e": "10th",
}

# Packages that jss.cls already loads (per catalogue note on HOUSE-003).
_JSS_LOADED_PACKAGES: frozenset[str] = frozenset(
    {"graphicx", "xcolor", "ae", "fancyvrb", "hyperref"}
)


def _violation(
    *,
    tex: Any,
    pos: int,
    rule_id: str,
    suggestion: str,
    fix: Fix | None = None,
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
        fix=fix,
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
                # The fix swaps the trailing `.` for `.,` — a 1-byte
                # range whose replacement is the same `.` followed by
                # the missing comma. The rule only fires in prose
                # context (math/verbatim/code already filtered above),
                # so the fix is unambiguous; confidence "safe".
                dot_pos = node.pos + match.end() - 1
                yield _violation(
                    tex=tex,
                    pos=abs_pos,
                    rule_id="JSS-HOUSE-001",
                    suggestion=(
                        f"Add a comma after {match.group(0)!r}: "
                        f"'{match.group(0)},'."
                    ),
                    fix=Fix(
                        start=dot_pos,
                        end=dot_pos + 1,
                        replacement=".,",
                        description="insert comma after e.g. / i.e.",
                        confidence="safe",
                    ),
                )


# ---------------------------------------------------------------------------
# JSS-HOUSE-002 — edition in BibTeX
# ---------------------------------------------------------------------------


def _iter_bib_entries(doc: ParsedDocument) -> Iterator[tuple[Any, Any]]:
    """Yield referenced ``(bib_file, entry)`` pairs. See
    ``_helpers._iter_referenced_entries`` for scope semantics."""
    yield from _helpers._iter_referenced_entries(doc)


def _line_start_offsets(text: str) -> list[int]:
    """Return the absolute char offset of the start of every line in
    ``text`` (line 0 starts at offset 0)."""
    offsets = [0]
    for i, ch in enumerate(text):
        if ch == "\n":
            offsets.append(i + 1)
    return offsets


def _locate_edition_value(
    source: str, field_start_line: int, value: str
) -> tuple[int, int] | None:
    """Locate the byte span of an edition ``value`` inside ``source``.

    The bibtex parser strips the surrounding ``{...}`` / ``"..."`` from
    the field value, so we re-locate it by scanning forward from the
    line on which the field starts. We accept whitespace between the
    delimiter and the value so ``edition = { second }`` still resolves.
    """
    offsets = _line_start_offsets(source)
    if field_start_line < 0 or field_start_line >= len(offsets):
        return None
    line_pos = offsets[field_start_line]
    pat = re.compile(
        r"\{\s*(" + re.escape(value) + r")\s*\}"
        r"|\"\s*(" + re.escape(value) + r")\s*\"",
        flags=re.IGNORECASE,
    )
    m = pat.search(source, pos=line_pos)
    if m is None:
        return None
    if m.group(1) is not None:
        return m.start(1), m.end(1)
    return m.start(2), m.end(2)


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

        # Auto-fix: emit a safe Fix(...) payload covering exactly the
        # edition value (without the surrounding ``{}`` / ``""``) so
        # the rewrite preserves the surrounding delimiter style.
        canonical = _EDITION_CANONICAL.get(value.lower())
        fix: Fix | None = None
        if canonical is not None:
            field_line = getattr(field, "start_line", None)
            if field_line is None:
                field_line = start
            span = _locate_edition_value(bib.source, field_line, value)
            if span is not None:
                fix_start, fix_end = span
                fix = Fix(
                    start=fix_start,
                    end=fix_end,
                    replacement=canonical,
                    description=(
                        f"use {canonical!r} for edition shorthand"
                    ),
                    confidence="safe",
                )

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
            fix=fix,
        )


# ---------------------------------------------------------------------------
# JSS-HOUSE-003 (info) — duplicate \usepackage
# ---------------------------------------------------------------------------


def check_jss_house_003(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    from texlint.journals.jss.rules.preamble import _has_jss_class

    for tex in doc.all_tex_like():
        # The "already loaded" claim only applies when the document
        # actually uses ``\\documentclass{jss}``. Non-jss vignettes that
        # share JSS conventions (``article``/``report`` class) need to
        # \\usepackage these themselves; the rule must not flag them.
        if not _has_jss_class(tex):
            continue
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
            macro_end = node.pos + (node.len or 0)
            line_range = _whole_line_range(tex.source, node.pos, macro_end)
            fix: Fix | None = None
            if line_range is not None:
                line_start, line_end = line_range
                fix = Fix(
                    start=line_start,
                    end=line_end,
                    replacement="",
                    description=f"delete redundant \\usepackage{{{name}}}",
                    confidence="safe",
                )
            v = _violation(
                tex=tex,
                pos=node.pos,
                rule_id="JSS-HOUSE-003",
                suggestion=(
                    f"Remove \\usepackage{{{name}}} — jss.cls already "
                    "loads it."
                ),
            )
            if fix is not None:
                # Violation is frozen — rebuild with the fix payload.
                v = Violation(
                    file=v.file,
                    line=v.line,
                    column=v.column,
                    rule_id=v.rule_id,
                    severity=v.severity,
                    message=v.message,
                    suggestion=v.suggestion,
                    fix=fix,
                )
            yield v


def _whole_line_range(
    source: str, macro_start: int, macro_end: int
) -> tuple[int, int] | None:
    """Return ``(line_start, line_end_after_newline)`` if the line
    containing ``\\usepackage{...}`` consists only of that macro and
    optional surrounding whitespace; otherwise return ``None``.

    ``line_start`` is the index just after the previous ``\\n`` (or 0
    at buffer start). ``line_end`` is one past the trailing ``\\n``
    (or ``len(source)`` if the line has no trailing newline). Slicing
    ``source[line_start:line_end]`` therefore yields the whole line
    including its newline, suitable as a deletion range.
    """
    prev_nl = source.rfind("\n", 0, macro_start)
    line_start = 0 if prev_nl == -1 else prev_nl + 1
    next_nl = source.find("\n", macro_end)
    line_end = len(source) if next_nl == -1 else next_nl + 1

    before = source[line_start:macro_start]
    # ``line_end`` includes the trailing newline; everything after the
    # macro on the same line lives in ``[macro_end, next_nl)``.
    after_end = next_nl if next_nl != -1 else len(source)
    after = source[macro_end:after_end]
    if before.strip() != "" or after.strip() != "":
        return None
    return line_start, line_end


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
