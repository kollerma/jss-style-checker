"""BibTeX mechanical rules for the JSS journal plugin.

Rules in this module:
  - JSS-BIBTEX-001 — non-empty citation key.
  - JSS-BIBTEX-002 — unique citation keys within a database.
  - JSS-BIBTEX-003 — required fields present per entry type.
  - JSS-BIBTEX-004 — 6+ authors need ``\\shortcites`` or the
    ``shortnames`` class option.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from typing import Any

from pylatexenc.latexwalker import LatexGroupNode, LatexMacroNode

from texlint.api import ParsedDocument, Rule, ToolConfig, Violation
from texlint.journals.jss import _catalogue_data
from texlint.journals.jss.rules import _helpers


# Required-field matrix per the catalogue's BIBTEX-003 notes.
_REQUIRED_FIELDS: dict[str, tuple[frozenset[str], ...]] = {
    "article": (frozenset({"author"}), frozenset({"title"}),
                frozenset({"journal"}), frozenset({"year"})),
    "book": (frozenset({"author", "editor"}), frozenset({"title"}),
             frozenset({"publisher"}), frozenset({"year"})),
    "inproceedings": (frozenset({"author"}), frozenset({"title"}),
                      frozenset({"booktitle"}), frozenset({"year"})),
    "incollection": (frozenset({"author"}), frozenset({"title"}),
                     frozenset({"booktitle"}), frozenset({"publisher"}),
                     frozenset({"year"})),
    "inbook": (frozenset({"author", "editor"}), frozenset({"title"}),
               frozenset({"chapter", "pages"}), frozenset({"publisher"}),
               frozenset({"year"})),
    "manual": (frozenset({"title"}),),
    "mastersthesis": (frozenset({"author"}), frozenset({"title"}),
                      frozenset({"school"}), frozenset({"year"})),
    "phdthesis": (frozenset({"author"}), frozenset({"title"}),
                  frozenset({"school"}), frozenset({"year"})),
    "techreport": (frozenset({"author"}), frozenset({"title"}),
                   frozenset({"institution"}), frozenset({"year"})),
    "unpublished": (frozenset({"author"}), frozenset({"title"}),
                    frozenset({"note"}),),
    # misc has no required fields.
}

_AUTHOR_THRESHOLD = 6


def _iter_entries(doc: ParsedDocument) -> Iterator[tuple[Any, Any]]:
    for bib in doc.bib_files:
        if bib.library is None:
            continue
        for entry in getattr(bib.library, "entries", ()) or ():
            yield bib, entry


def _entry_line(entry: Any) -> int:
    start = getattr(entry, "start_line", 0) or 0
    return start + 1


def _violation(
    *, bib: Any, entry: Any, rule_id: str, suggestion: str
) -> Violation:
    meta = _catalogue_data.RULES[rule_id]
    return Violation(
        file=bib.path,
        line=_entry_line(entry),
        column=None,
        rule_id=rule_id,
        severity=meta["severity"],
        message=meta["message_template"],
        suggestion=suggestion,
        fix=None,
    )


# ---------------------------------------------------------------------------
# JSS-BIBTEX-001 — non-empty key
# ---------------------------------------------------------------------------


def check_jss_bibtex_001(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for bib, entry in _iter_entries(doc):
        if not entry.key:
            yield _violation(
                bib=bib,
                entry=entry,
                rule_id="JSS-BIBTEX-001",
                suggestion="Give this entry a non-empty citation key.",
            )


# ---------------------------------------------------------------------------
# JSS-BIBTEX-002 — unique keys
# ---------------------------------------------------------------------------


def check_jss_bibtex_002(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    # Duplicates per bib file (duplicates within a single DB).
    for bib in doc.bib_files:
        if bib.library is None:
            continue
        # bibtexparser 2 keeps the first occurrence in `.entries` and routes
        # subsequent same-key blocks into `.failed_blocks` as
        # DuplicateBlockKeyBlock. Both paths must yield a violation.
        for block in getattr(bib.library, "failed_blocks", ()) or ():
            if type(block).__name__ != "DuplicateBlockKeyBlock":
                continue
            key = getattr(block, "key", None)
            if not key:
                continue
            yield _violation(
                bib=bib,
                entry=block,
                rule_id="JSS-BIBTEX-002",
                suggestion=(
                    f"Citation key {key!r} is used more than once; "
                    "rename one (e.g., add a suffix 'a' / 'b')."
                ),
            )


# ---------------------------------------------------------------------------
# JSS-BIBTEX-003 — required fields per entry type
# ---------------------------------------------------------------------------


def check_jss_bibtex_003(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for bib, entry in _iter_entries(doc):
        requirements = _REQUIRED_FIELDS.get(entry.entry_type.lower())
        if requirements is None:
            continue  # unknown or 'misc' — no requirements
        have = set(entry.fields_dict)
        missing_groups: list[frozenset[str]] = [
            g for g in requirements if have.isdisjoint(g)
        ]
        if not missing_groups:
            continue
        missing_str = " / ".join(
            "|".join(sorted(g)) for g in missing_groups
        )
        yield _violation(
            bib=bib,
            entry=entry,
            rule_id="JSS-BIBTEX-003",
            suggestion=(
                f"Entry type {entry.entry_type!r} is missing required "
                f"field(s): {missing_str}."
            ),
        )


# ---------------------------------------------------------------------------
# JSS-BIBTEX-004 — 6+ authors need shortnames / shortcites
# ---------------------------------------------------------------------------


def _author_count(entry: Any) -> int:
    f = entry.fields_dict.get("author")
    if f is None:
        return 0
    # BibTeX separates authors with ' and '; splitting is safe for JSS style.
    return len(re.split(r"\s+and\s+", str(f.value).strip()))


def _mitigation_present(doc: ParsedDocument, mitigated_keys: set[str]) -> bool:
    """Return True if the paper's preamble declares ``shortnames`` as a
    ``jss`` class option."""
    for tex in doc.tex_files:
        for node in _helpers._walk(tex.nodes):
            if not isinstance(node, LatexMacroNode):
                continue
            if node.macroname != "documentclass":
                continue
            if _has_shortnames_option(node):
                return True
            break  # one \documentclass per preamble
    return False


def _has_shortnames_option(node: LatexMacroNode) -> bool:
    argd = getattr(node, "nodeargd", None)
    if argd is None:
        return False
    for arg in argd.argnlist or ():
        if isinstance(arg, LatexGroupNode):
            text = "".join(
                getattr(c, "chars", "")
                for c in (arg.nodelist or ())
            )
            if "shortnames" in text:
                return True
    return False


def _iter_shortcites_keys(doc: ParsedDocument) -> Iterator[str]:
    for tex in doc.tex_files:
        for parent, idx, node in _helpers._iter_with_parent(tex.nodes):
            if (
                isinstance(node, LatexMacroNode)
                and node.macroname == "shortcites"
            ):
                text = _helpers._macro_args_text(node, parent, idx)
                for key in text.split(","):
                    key = key.strip()
                    if key:
                        yield key


def check_jss_bibtex_004(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    shortnames_in_preamble = _mitigation_present(doc, set())
    shortcited_keys = set(_iter_shortcites_keys(doc))
    for bib, entry in _iter_entries(doc):
        if _author_count(entry) < _AUTHOR_THRESHOLD:
            continue
        if shortnames_in_preamble:
            continue
        if entry.key and entry.key in shortcited_keys:
            continue
        yield _violation(
            bib=bib,
            entry=entry,
            rule_id="JSS-BIBTEX-004",
            suggestion=(
                "Add the 'shortnames' option to \\documentclass{jss}, or "
                f"list this key in \\shortcites{{{entry.key}}}."
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


jss_bibtex_001 = _rule("JSS-BIBTEX-001", check_jss_bibtex_001)
jss_bibtex_002 = _rule("JSS-BIBTEX-002", check_jss_bibtex_002)
jss_bibtex_003 = _rule("JSS-BIBTEX-003", check_jss_bibtex_003)
jss_bibtex_004 = _rule("JSS-BIBTEX-004", check_jss_bibtex_004)


rules: tuple[Rule, ...] = (
    jss_bibtex_001,
    jss_bibtex_002,
    jss_bibtex_003,
    jss_bibtex_004,
)
