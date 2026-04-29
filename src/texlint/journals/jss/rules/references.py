"""References rules for the JSS journal plugin.

Rules in this module (rollout position: references):
  - JSS-REFS-001 — BibTeX entries must declare a year field.
  - JSS-REFS-002 — title is not entirely lowercase (tight title-case heuristic).
  - JSS-REFS-003 — article / inproceedings / incollection / book entries
    should declare a doi field (advisory).
  - JSS-REFS-004 — BibTeX titles use JSS markup (\\pkg, \\proglang) for
    common R package and programming language names.
  - JSS-REFS-005 — journal titles are not abbreviated.
  - JSS-REFS-006 — first word of a title (and first word after ':') is
    capitalised (loose title-case heuristic).
  - JSS-REFS-007 — journal titles are in title case.

JSS-REFS-001 retrofits the Step 1 smoke rule `bib_001_year.py`; that
file is deleted in the same PR.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from typing import Any

from texlint.api import ParsedDocument, Rule, ToolConfig, Violation
from texlint.journals.jss import _catalogue_data
from texlint.journals.jss.rules import _helpers
from texlint.journals.jss.terms import LANGUAGES, R_PACKAGES

# Entry types that should carry a DOI per article.tex:421.
_DOI_ENTRY_TYPES: frozenset[str] = frozenset(
    {"article", "inproceedings", "incollection", "book"}
)

# Journal-abbreviation signals.
_ABBREV_RE = re.compile(
    r"\b(?:"
    r"J|Jnl|Proc|Trans|Conf|Rev|Stat|Sci|Appl|Math|Comp|Comput|Softw|Bull|"
    r"Ann|Lett|Res|Assoc|Theor"
    r")\.",
    flags=re.IGNORECASE,
)

# Stop-words that legitimately remain lowercase in title-case titles.
_TITLE_STOPWORDS: frozenset[str] = frozenset(
    {
        "a", "an", "the", "and", "but", "or", "nor", "for", "so", "yet",
        "at", "by", "in", "of", "on", "to", "up", "via", "with", "as",
        "is", "vs", "per",
    }
)


def _field_value(entry: Any, name: str) -> str:
    f = _helpers._lc_fields(entry).get(name.lower())
    if f is None:
        return ""
    return str(f.value)


def _entry_line(entry: Any) -> int:
    start = getattr(entry, "start_line", 0) or 0
    return start + 1


def _iter_entries(doc: ParsedDocument) -> Iterator[tuple[Any, Any]]:
    """Yield ``(bib_file, entry)`` for every referenced BibTeX entry.

    Scope: entries cited from the tex surface (see
    ``_helpers._iter_referenced_entries``). Widens to all entries when
    the lint target is bib-only or the paper uses ``\\nocite{*}``.
    """
    yield from _helpers._iter_referenced_entries(doc)


def _violation(
    *,
    bib: Any,
    entry: Any,
    rule_id: str,
    suggestion: str,
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
# JSS-REFS-001 — year field required
# ---------------------------------------------------------------------------


def check_jss_refs_001(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for bib, entry in _iter_entries(doc):
        fields = _helpers._lc_fields(entry)
        if "year" in fields:
            continue
        # ``@incollection{X, crossref = {Y}}`` inherits all required
        # fields (year included) from the cross-referenced entry. Don't
        # flag X — its year IS effectively present via Y.
        if "crossref" in fields:
            continue
        key = entry.key or "<unknown>"
        yield _violation(
            bib=bib,
            entry=entry,
            rule_id="JSS-REFS-001",
            suggestion=f"Add a year field to entry {key!r}.",
        )


# ---------------------------------------------------------------------------
# JSS-REFS-002 — tight title-case heuristic (all-lowercase)
# ---------------------------------------------------------------------------


def _visible_words(title: str) -> list[str]:
    """Split on whitespace and punctuation; drop pure-punctuation tokens."""
    return [w for w in re.split(r"[\s\-/]+", title) if re.search(r"[A-Za-z]", w)]


def check_jss_refs_002(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for bib, entry in _iter_entries(doc):
        title = _field_value(entry, "title")
        if not title:
            continue
        # Strip LaTeX braces/macros to get the plain string.
        plain = _strip_latex(title)
        words = _visible_words(plain)
        if not words:
            continue
        if all(w == w.lower() for w in words):
            yield _violation(
                bib=bib,
                entry=entry,
                rule_id="JSS-REFS-002",
                suggestion="Capitalize the principal words in the title.",
            )


def _strip_latex(text: str) -> str:
    """Drop ``\\macro{...}`` wrappers so a macroed title like
    ``\\pkg{MASS}: ...`` isn't penalised by REFS-002/006/007."""
    # Very light normalisation: remove backslash-commands and braces.
    no_macros = re.sub(r"\\[A-Za-z]+\s*", "", text)
    return no_macros.replace("{", "").replace("}", "")


# ---------------------------------------------------------------------------
# JSS-REFS-003 — DOI advisory (info severity)
# ---------------------------------------------------------------------------


def check_jss_refs_003(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for bib, entry in _iter_entries(doc):
        if entry.entry_type.lower() not in _DOI_ENTRY_TYPES:
            continue
        if "doi" in _helpers._lc_fields(entry):
            continue
        key = entry.key or "<unknown>"
        yield _violation(
            bib=bib,
            entry=entry,
            rule_id="JSS-REFS-003",
            suggestion=f"Add a doi field to entry {key!r} if one is available.",
        )


# ---------------------------------------------------------------------------
# JSS-REFS-004 — markup for package / language names in titles
# ---------------------------------------------------------------------------


def _title_mentions_unwrapped(text: str, names: frozenset[str]) -> str | None:
    """Return the first name from ``names`` that appears in ``text`` without
    being wrapped in a ``\\macro{...}``. ``None`` if none match."""
    # Strip segments that are inside braces immediately after a backslash macro
    # (treat ``\pkg{MASS}`` as already wrapped).
    unwrapped = re.sub(r"\\[A-Za-z]+\s*\{[^{}]*\}", "", text)
    # Unwrap BibTeX case-protection braces (``{C}arlo``, ``{Hardy}-Weinberg``,
    # ``{R}``) so single-letter capitalisers don't masquerade as language /
    # package mentions. Without this, ``Monte {C}arlo`` and ``{L}ycosidae``
    # match the bare ``C`` / ``L`` token.
    unwrapped = re.sub(r"\{([^{}\\]*)\}", r"\1", unwrapped)
    for name in names:
        # Match the name as a standalone token.
        if re.search(rf"\b{re.escape(name)}\b", unwrapped):
            return name
    return None


def check_jss_refs_004(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for bib, entry in _iter_entries(doc):
        title = _field_value(entry, "title")
        if not title:
            continue
        lang = _title_mentions_unwrapped(title, LANGUAGES)
        if lang is not None:
            yield _violation(
                bib=bib,
                entry=entry,
                rule_id="JSS-REFS-004",
                suggestion=(
                    f"Wrap {lang!r} in \\proglang{{{lang}}} in the title."
                ),
            )
            continue
        pkg = _title_mentions_unwrapped(title, R_PACKAGES)
        if pkg is not None:
            yield _violation(
                bib=bib,
                entry=entry,
                rule_id="JSS-REFS-004",
                suggestion=(
                    f"Wrap {pkg!r} in \\pkg{{{pkg}}} in the title."
                ),
            )


# ---------------------------------------------------------------------------
# JSS-REFS-005 — journal not abbreviated
# ---------------------------------------------------------------------------


def check_jss_refs_005(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for bib, entry in _iter_entries(doc):
        journal = _field_value(entry, "journal")
        if not journal:
            continue
        plain = _strip_latex(journal)
        if _ABBREV_RE.search(plain):
            yield _violation(
                bib=bib,
                entry=entry,
                rule_id="JSS-REFS-005",
                suggestion=(
                    "Expand the journal name (e.g., 'J. Stat. Softw.' → "
                    "'Journal of Statistical Software')."
                ),
            )


# ---------------------------------------------------------------------------
# JSS-REFS-006 — loose title-case heuristic
# ---------------------------------------------------------------------------


def _word_is_uppercase_start(word: str) -> bool:
    letters = re.sub(r"[^A-Za-z]", "", word)
    if not letters:
        return True
    return letters[0].isupper()


# Markup macros whose argument has author-dictated case (package names,
# language names, code identifiers). When a bib title's first word — or
# the first word after a colon — is wrapped in one of these, the title
# isn't violating title-case; the package author's chosen casing wins.
_MARKUP_TITLE_MACROS = ("pkg", "proglang", "code", "fct", "verb")
_MARKUP_TITLE_RE = re.compile(
    r"\\(" + "|".join(_MARKUP_TITLE_MACROS) + r")\{"
)


def _starts_with_markup(title: str) -> bool:
    """True if the source title starts with ``\\pkg{...}`` (or another
    markup macro). Tolerates one optional outer brace from BibTeX
    case-protection (`{\\pkg{X}: ...}`)."""
    s = title.lstrip()
    if s.startswith("{"):
        s = s[1:].lstrip()
    return bool(_MARKUP_TITLE_RE.match(s))


def _after_colon_starts_with_markup(title: str) -> bool:
    """True if the first non-space token after a colon is a markup macro."""
    m = re.search(r":\s*(.+)", title, flags=re.DOTALL)
    if not m:
        return False
    rest = m.group(1).lstrip()
    if rest.startswith("{"):
        rest = rest[1:].lstrip()
    return bool(_MARKUP_TITLE_RE.match(rest))


def check_jss_refs_006(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for bib, entry in _iter_entries(doc):
        title = _field_value(entry, "title")
        if not title:
            continue
        plain = _strip_latex(title)
        words = _visible_words(plain)
        if not words:
            continue
        # REFS-002 already catches all-lowercase; don't double-fire.
        if all(w == w.lower() for w in words):
            continue
        # First word must be capitalised — unless the source wraps it in
        # \pkg{...} / \proglang{...} / \code{...}, in which case the
        # author-dictated case wins.
        if not _starts_with_markup(title) and not _word_is_uppercase_start(words[0]):
            yield _violation(
                bib=bib,
                entry=entry,
                rule_id="JSS-REFS-006",
                suggestion="Capitalize the first word of the title.",
            )
            continue
        # Word after ':' must be capitalised — same markup exemption.
        m = re.search(r":\s*(\S+)", plain)
        if m and not _after_colon_starts_with_markup(title):
            after = m.group(1)
            if not _word_is_uppercase_start(after):
                yield _violation(
                    bib=bib,
                    entry=entry,
                    rule_id="JSS-REFS-006",
                    suggestion=(
                        "Capitalize the first word after ':' in the title."
                    ),
                )


# ---------------------------------------------------------------------------
# JSS-REFS-007 — journal in title case
# ---------------------------------------------------------------------------


def check_jss_refs_007(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for bib, entry in _iter_entries(doc):
        journal = _field_value(entry, "journal")
        if not journal:
            continue
        plain = _strip_latex(journal)
        # Skip abbreviated names — REFS-005 handles those.
        if _ABBREV_RE.search(plain):
            continue
        words = _visible_words(plain)
        if not words:
            continue
        # Every non-stopword must start with an uppercase letter. The first
        # word is always checked (stop-words at the start still need caps).
        for idx, word in enumerate(words):
            low = re.sub(r"[^A-Za-z]", "", word).lower()
            if idx > 0 and low in _TITLE_STOPWORDS:
                continue
            if not _word_is_uppercase_start(word):
                yield _violation(
                    bib=bib,
                    entry=entry,
                    rule_id="JSS-REFS-007",
                    suggestion=(
                        "Capitalize the principal words of the journal title."
                    ),
                )
                break


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


jss_refs_001 = _rule("JSS-REFS-001", check_jss_refs_001)
jss_refs_002 = _rule("JSS-REFS-002", check_jss_refs_002)
jss_refs_003 = _rule("JSS-REFS-003", check_jss_refs_003)
jss_refs_004 = _rule("JSS-REFS-004", check_jss_refs_004)
jss_refs_005 = _rule("JSS-REFS-005", check_jss_refs_005)
jss_refs_006 = _rule("JSS-REFS-006", check_jss_refs_006)
jss_refs_007 = _rule("JSS-REFS-007", check_jss_refs_007)


rules: tuple[Rule, ...] = (
    jss_refs_001,
    jss_refs_002,
    jss_refs_003,
    jss_refs_004,
    jss_refs_005,
    jss_refs_006,
    jss_refs_007,
)
