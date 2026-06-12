"""Naming rules for the JSS journal plugin.

Rules in this module:
  - JSS-NAME-001 — programming-language names use canonical capitalisation
    (e.g., "JAVA" → "Java"); driven by terms.CANONICAL.
  - JSS-NAME-002 — BibTeX publisher / journal fields use canonical forms
    per style-guide SG-048..SG-052; driven by terms.PUBLISHER_CANONICAL
    and terms.JOURNAL_CANONICAL.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from typing import Any

from pylatexenc.latexwalker import LatexCharsNode

from texlint.api import Fix, ParsedDocument, Rule, ToolConfig, Violation
from texlint.journals.jss.rules import _helpers
from texlint.journals.jss.terms import (
    CANONICAL,
    JOURNAL_CANONICAL,
    PUBLISHER_CANONICAL,
    PUBLISHER_PREFIX_CANONICAL,
)


def _publisher_canonical(value: str) -> str | None:
    """Resolve a publisher field to its JSS-canonical form.

    Checks the exact-match map first (``PUBLISHER_CANONICAL``), then
    the prefix-match table (``PUBLISHER_PREFIX_CANONICAL``) so corpus
    variants like ``"Springer, Heidelberg, New York"`` still
    canonicalise to ``"Springer-Verlag"``. Returns ``None`` when no
    canonical form is known.
    """
    direct = PUBLISHER_CANONICAL.get(value)
    if direct is not None:
        return direct
    for prefix, canonical in PUBLISHER_PREFIX_CANONICAL:
        # Match the prefix at a word boundary so ``Springerwell`` (a
        # hypothetical other publisher) does not match.
        if (
            value == prefix
            or value.startswith(prefix + " ")
            or value.startswith(prefix + ",")
        ):
            return canonical
    return None

_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9+\-]*")

# Bare URL spans in prose. NAME-001 should not fire on tokens inside
# them — ``http://java.sun.com/docs`` contains the substring ``java``,
# which CANONICAL would otherwise rewrite to ``Java`` (nonsensical
# inside a URL).
_BARE_URL_RE = re.compile(
    r"\b(?:https?|ftp|ftps|file)://\S+",
    flags=re.IGNORECASE,
)


# Catalogue-backed factories live in _helpers (one definition for all
# rule modules); the module-local names are kept for call-site brevity.
_violation = _helpers.make_violation


# ---------------------------------------------------------------------------
# JSS-NAME-001 — language canonical capitalisation in prose
# ---------------------------------------------------------------------------


def check_jss_name_001(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.all_tex_like():
        for node, ancestors in _helpers._walk_with_ancestors(tex.nodes):
            if not isinstance(node, LatexCharsNode):
                continue
            if not _helpers._is_in_prose_context(ancestors):
                continue
            url_spans = [m.span() for m in _BARE_URL_RE.finditer(node.chars)]
            for match in _TOKEN_RE.finditer(node.chars):
                token = match.group(0)
                if token not in CANONICAL:
                    continue
                # Skip tokens inside bare URLs — ``java.sun.com`` is
                # not the language reference.
                if any(s <= match.start() < e for s, e in url_spans):
                    continue
                # Skip function calls — `ggplot(` is the R function
                # invocation, not the package name. The lookahead for
                # `(` (with optional whitespace) catches `ggplot(`,
                # `ggplot (...)`.
                end = match.end()
                trailing = node.chars[end:end + 4]
                if trailing.lstrip().startswith("("):
                    continue
                canonical = CANONICAL[token]
                abs_pos = node.pos + match.start()
                abs_end = node.pos + match.end()
                line, col = _helpers._lineno_col(tex, abs_pos)
                yield _violation(
                    file=tex.path,
                    line=line,
                    column=col,
                    rule_id="JSS-NAME-001",
                    suggestion=(
                        f"Use canonical form {canonical!r} instead of "
                        f"{token!r}."
                    ),
                    fix=Fix(
                        start=abs_pos,
                        end=abs_end,
                        replacement=canonical,
                        description=(
                            f"Replace {token!r} with canonical {canonical!r}."
                        ),
                        confidence="safe",
                    ),
                )


# ---------------------------------------------------------------------------
# JSS-NAME-002 — BibTeX publisher / journal canonical forms
# ---------------------------------------------------------------------------


def _field_value(entry: Any, name: str) -> str:
    f = _helpers._lc_fields(entry).get(name.lower())
    if f is None:
        return ""
    return str(f.value).strip()


_entry_line = _helpers.entry_line


def _entry_source_span(source: str, entry: Any) -> tuple[int, int]:
    """Resolve the byte-offset slice in *source* covering *entry*.

    bibtexparser 2.x exposes only ``entry.start_line`` (0-based); fields
    have a ``start_line`` but no byte offsets. To find the literal range
    of a particular field value we first narrow to the entry's slice
    (start of its ``@type{key,...`` line through just before the next
    ``@``-at-line-start), then scan within.
    """
    start_line = getattr(entry, "start_line", 0) or 0
    # Translate 0-based line index → byte offset of that line's start.
    offset = 0
    cur_line = 0
    while cur_line < start_line:
        nl = source.find("\n", offset)
        if nl == -1:
            offset = len(source)
            break
        offset = nl + 1
        cur_line += 1
    # End of entry: first ``@`` at column 0 after the start, else EOF.
    end = len(source)
    next_at = re.search(r"(?m)^@", source[offset + 1 :])
    if next_at is not None:
        end = offset + 1 + next_at.start()
    return offset, end


# Match ``<name> = <delim><value><delim>`` for a single bib field. The
# value is captured as the literal source bytes between the opening and
# closing delimiter (``{...}`` or ``"..."``); only the captured group
# becomes the Fix range, so the surrounding ``{}`` / ``""`` stays put.
def _field_value_span(
    source: str, entry: Any, field_name: str, expected_value: str,
) -> tuple[int, int] | None:
    es, ee = _entry_source_span(source, entry)
    block = source[es:ee]
    pattern = re.compile(
        r"(?im)(?<![A-Za-z0-9_])"
        + re.escape(field_name)
        + r"\s*=\s*(?:\{(?P<bv>[^{}]*)\}|\"(?P<qv>[^\"]*)\")"
    )
    for match in pattern.finditer(block):
        value = match.group("bv")
        delim = "brace"
        if value is None:
            value = match.group("qv")
            delim = "quote"
        # bibtexparser strips surrounding whitespace from the value; we
        # match against the raw delimiter contents stripped the same way
        # so cosmetic ``{ Springer }`` still resolves.
        if value.strip() != expected_value:
            continue
        group_name = "bv" if delim == "brace" else "qv"
        # Use the captured-group span so the Fix range covers ONLY the
        # literal value bytes (excluding the {}/"" delimiters).
        v_start = es + match.start(group_name)
        v_end = es + match.end(group_name)
        # Trim leading/trailing whitespace inside the delimiters — the
        # canonical replacement should not pad whitespace into the
        # delimiters either.
        literal = source[v_start:v_end]
        lstripped = literal.lstrip()
        rstripped = lstripped.rstrip()
        v_start += len(literal) - len(lstripped)
        v_end -= len(lstripped) - len(rstripped)
        return v_start, v_end
    return None


def _build_fix(
    source: str,
    entry: Any,
    field_name: str,
    raw_value: str,
    canonical: str,
) -> Fix | None:
    span = _field_value_span(source, entry, field_name, raw_value)
    if span is None:
        return None
    start, end = span
    return Fix(
        start=start,
        end=end,
        replacement=canonical,
        description=f"use canonical form {canonical!r}",
        confidence="safe",
    )


def check_jss_name_002(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for bib, entry in _helpers._iter_referenced_entries(doc):
        publisher = _field_value(entry, "publisher")
        if publisher:
            canonical = _publisher_canonical(publisher)
            if canonical is not None and canonical != publisher:
                yield _violation(
                    file=bib.path,
                    line=_entry_line(entry),
                    column=None,
                    rule_id="JSS-NAME-002",
                    suggestion=(
                        f"Replace publisher {publisher!r} with "
                        f"{canonical!r}."
                    ),
                    fix=_build_fix(
                        bib.source, entry, "publisher",
                        publisher, canonical,
                    ),
                )
        journal = _field_value(entry, "journal")
        if journal and journal in JOURNAL_CANONICAL:
            canonical = JOURNAL_CANONICAL[journal]
            yield _violation(
                file=bib.path,
                line=_entry_line(entry),
                column=None,
                rule_id="JSS-NAME-002",
                suggestion=(
                    f"Replace journal {journal!r} with "
                    f"{canonical!r}."
                ),
                fix=_build_fix(
                    bib.source, entry, "journal", journal, canonical,
                ),
            )


# ---------------------------------------------------------------------------
# Rule objects
# ---------------------------------------------------------------------------


_rule = _helpers.make_rule


jss_name_001 = _rule("JSS-NAME-001", check_jss_name_001)
jss_name_002 = _rule("JSS-NAME-002", check_jss_name_002)


rules: tuple[Rule, ...] = (jss_name_001, jss_name_002)
