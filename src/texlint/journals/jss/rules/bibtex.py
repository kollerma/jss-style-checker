"""BibTeX mechanical rules for the JSS journal plugin.

Rules in this module:
  - JSS-BIBTEX-001 — non-empty citation key.
  - JSS-BIBTEX-002 — unique citation keys within a database.
  - JSS-BIBTEX-003 — required fields present per entry type.
  - JSS-BIBTEX-004 — 6+ authors need ``\\shortcites`` or the
    ``shortnames`` class option.
  - JSS-BIBTEX-005 — no field key is repeated within a single entry.
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
    """Yield referenced ``(bib_file, entry)`` pairs. See
    ``_helpers._iter_referenced_entries`` for scope semantics."""
    yield from _helpers._iter_referenced_entries(doc)




# Catalogue-backed factories live in _helpers (one definition for all
# rule modules); the module-local names are kept for call-site brevity.
_violation = _helpers.entry_violation


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
            inner = getattr(block, "ignore_error_block", None)
            if inner is not None and type(inner).__name__ != "Entry":
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
        have = set(_helpers._lc_fields(entry))
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
    f = _helpers._lc_fields(entry).get("author")
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


def _entries_by_key(doc: ParsedDocument) -> dict[str, tuple[Any, Any]]:
    """Return ``key -> (bib_file, entry)`` for every non-empty-keyed entry
    in the document's bib databases. The first occurrence wins on duplicate
    keys (BIBTEX-002 reports the dupes separately)."""
    out: dict[str, tuple[Any, Any]] = {}
    for bib in doc.bib_files:
        if bib.library is None:
            continue
        for entry in getattr(bib.library, "entries", ()) or ():
            if entry.key and entry.key not in out:
                out[entry.key] = (bib, entry)
    return out


def _iter_cite_sites(
    doc: ParsedDocument,
) -> Iterator[tuple[Any, Any, Any, int, str]]:
    """Yield ``(tex, node, parent, idx, key)`` for every key referenced
    from a ``\\cite*`` / ``\\nocite`` macro in any tex-like island. The
    ``*`` wildcard from ``\\nocite{*}`` is skipped — it has no key."""
    for tex in doc.all_tex_like():
        for parent, idx, node in _helpers._iter_with_parent(tex.nodes):
            if not isinstance(node, LatexMacroNode):
                continue
            if node.macroname not in _helpers._CITE_MACROS_FOR_SCOPE:
                continue
            text = _helpers._macro_args_text(node, parent, idx)
            for raw in text.split(","):
                key = raw.strip()
                if key and key != "*":
                    yield tex, node, parent, idx, key


def check_jss_bibtex_004(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    shortnames_in_preamble = _mitigation_present(doc, set())
    if shortnames_in_preamble:
        return
    shortcited_keys = set(_iter_shortcites_keys(doc))
    entries = _entries_by_key(doc)
    meta = _catalogue_data.RULES["JSS-BIBTEX-004"]

    tex_like_present = any(True for _ in doc.all_tex_like())
    if not tex_like_present:
        # Bare-bib invocation: no cite sites exist, fall back to flagging the
        # bib entries themselves so the user still sees the warning.
        for bib, entry in _iter_entries(doc):
            if _author_count(entry) < _AUTHOR_THRESHOLD:
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
        return

    seen_keys: set[str] = set()
    for tex, node, _parent, _idx, key in _iter_cite_sites(doc):
        if key in seen_keys:
            continue
        if key in shortcited_keys:
            continue
        bib_entry = entries.get(key)
        if bib_entry is None:
            continue
        _bib, entry = bib_entry
        if _author_count(entry) < _AUTHOR_THRESHOLD:
            continue
        seen_keys.add(key)
        line, col = _helpers._lineno_col(tex, node.pos)
        yield Violation(
            file=tex.path,
            line=line,
            column=col,
            rule_id="JSS-BIBTEX-004",
            severity=meta["severity"],
            message=meta["message_template"],
            suggestion=(
                "Add the 'shortnames' option to \\documentclass{jss}, or "
                f"list this key in \\shortcites{{{key}}}."
            ),
            fix=None,
        )


# ---------------------------------------------------------------------------
# JSS-BIBTEX-005 — no duplicate field keys within an entry
# ---------------------------------------------------------------------------


def check_jss_bibtex_005(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    # bibtexparser keeps the first value of a repeated field and routes the
    # offending entry into `failed_blocks` as a DuplicateFieldKeyBlock (the
    # parser treats this as recoverable, not a JSS-PARSE-000 — see
    # texlint.core.parser._RECOVERABLE_BIB_BLOCKS). Surface it here so the
    # silently-dropped field is still reported.
    for bib in doc.bib_files:
        if bib.library is None:
            continue
        for block in getattr(bib.library, "failed_blocks", ()) or ():
            if type(block).__name__ != "DuplicateFieldKeyBlock":
                continue
            dup_fields = ", ".join(sorted(getattr(block, "duplicate_keys", ()) or ()))
            inner = getattr(block, "ignore_error_block", None)
            key = getattr(inner, "key", None)
            where = f"entry {key!r}" if key else "this entry"
            fields_msg = f" field(s) {dup_fields}" if dup_fields else " a field"
            yield _violation(
                bib=bib,
                entry=block,
                rule_id="JSS-BIBTEX-005",
                suggestion=(
                    f"Remove the duplicate{fields_msg} in {where}; BibTeX keeps "
                    "only the first occurrence and silently drops the rest."
                ),
            )


# ---------------------------------------------------------------------------
# Rule objects
# ---------------------------------------------------------------------------


_rule = _helpers.make_rule


jss_bibtex_001 = _rule("JSS-BIBTEX-001", check_jss_bibtex_001)
jss_bibtex_002 = _rule("JSS-BIBTEX-002", check_jss_bibtex_002)
jss_bibtex_003 = _rule("JSS-BIBTEX-003", check_jss_bibtex_003)
jss_bibtex_004 = _rule("JSS-BIBTEX-004", check_jss_bibtex_004)
jss_bibtex_005 = _rule("JSS-BIBTEX-005", check_jss_bibtex_005)


rules: tuple[Rule, ...] = (
    jss_bibtex_001,
    jss_bibtex_002,
    jss_bibtex_003,
    jss_bibtex_004,
    jss_bibtex_005,
)
