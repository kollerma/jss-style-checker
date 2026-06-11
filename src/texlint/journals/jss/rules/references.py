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
from texlint.journals.jss.rules import _helpers
from texlint.journals.jss.terms import LANGUAGES, R_PACKAGES

# Entry types that should carry a DOI per article.tex:421.
_DOI_ENTRY_TYPES: frozenset[str] = frozenset(
    {"article", "inproceedings", "incollection", "book"}
)

# CrossRef and the DOI system became the de-facto standard around 2000;
# pre-2000 publications mostly never received a retroactive DOI. Don't
# fault their bib entries for missing one — REFS-003 is an info-severity
# advisory, not a hard rule.
_DOI_ERA_CUTOFF_YEAR = 2000

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




def _iter_entries(doc: ParsedDocument) -> Iterator[tuple[Any, Any]]:
    """Yield ``(bib_file, entry)`` for every referenced BibTeX entry.

    Scope: entries cited from the tex surface (see
    ``_helpers._iter_referenced_entries``). Widens to all entries when
    the lint target is bib-only or the paper uses ``\\nocite{*}``.
    """
    yield from _helpers._iter_referenced_entries(doc)


# Catalogue-backed factories live in _helpers (one definition for all
# rule modules); the module-local names are kept for call-site brevity.
_violation = _helpers.entry_violation


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


def _strip_markup_content(text: str) -> str:
    """Drop ``\\macro{content}`` entirely (both wrapper and inner words).

    Companion to :func:`_strip_latex` for the REFS-006 principal-word
    check: we want to see only user-prose words, not author-dictated
    package/language identifiers wrapped in JSS markup macros. Iterates
    until no more `\\macro{...}` substrings remain so nested wrappers
    like ``\\code{\\pkg{x}}`` are fully removed.
    """
    prev: str | None = None
    while prev != text:
        prev = text
        text = re.sub(r"\\[A-Za-z]+\*?\s*\{[^{}]*\}", " ", text)
    return text.replace("{", "").replace("}", "")


# ---------------------------------------------------------------------------
# JSS-REFS-003 — DOI advisory (info severity)
# ---------------------------------------------------------------------------


def check_jss_refs_003(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for bib, entry in _iter_entries(doc):
        if entry.entry_type.lower() not in _DOI_ENTRY_TYPES:
            continue
        fields = _helpers._lc_fields(entry)
        if "doi" in fields:
            continue
        # Pre-DOI-era entries: skip the advisory.
        year_field = fields.get("year")
        if year_field is not None:
            year_match = re.search(r"\d{4}", str(year_field.value))
            if year_match and int(year_match.group(0)) < _DOI_ERA_CUTOFF_YEAR:
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


_TITLE_PACKAGE_PREFIX_RE = re.compile(
    # Identifier (letter then alphanum/dot, MixedCase or all-lowercase)
    # followed by ``:`` — the canonical ``pkgname: description`` form.
    # Tolerates BibTeX case-protection braces (``{pkgname}:`` /
    # ``{{pkgname}: ...}``) and a leading ``\pkg{`` (already-wrapped —
    # skip via the upstream ``_title_mentions_unwrapped`` exit).
    r"^\{*\s*\{?([A-Za-z][A-Za-z0-9.]*)\}?\s*:"
)


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
            continue
        # Pattern-based fallback for package titles whose name is NOT in
        # the R_PACKAGES set — the canonical ``pkgname: description``
        # shape (e.g., ``cascsim: Casualty Actuarial Society ...``,
        # ``pmclust: Parallel Model-Based Clustering``). If the source
        # title already starts with ``\pkg{...}`` or ``\proglang{...}``
        # the author-dictated wrapping wins and we skip.
        if _starts_with_markup(title):
            continue
        prefix_match = _TITLE_PACKAGE_PREFIX_RE.match(title)
        if prefix_match is None:
            continue
        name = prefix_match.group(1)
        # Don't fire on first-word stop words ("The ...:", "An ...:")
        # or canonical-author titles ("R: A Language ...") — keep the
        # check tight on package-shaped identifiers.
        if name.lower() in _TITLE_STOP_WORDS:
            continue
        if name in LANGUAGES:
            continue
        # Avoid double-firing when the language scan already matched
        # this name (defensive — the early-return above already handles
        # the common case).
        yield _violation(
            bib=bib,
            entry=entry,
            rule_id="JSS-REFS-004",
            suggestion=(
                f"The leading identifier {name!r} looks like a package "
                f"name; wrap it in \\pkg{{{name}}} in the title."
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


# A bibtex title that opens with a lowercase identifier followed by ``:``
# is conventionally an R-package citation in the form ``vegan: Community
# Ecology Package`` / ``latticeExtra: Extra Graphical Utilities ...``.
# CRAN package names are lowercase (or camelCase starting lowercase) by
# convention, so this leading token is the package name itself, not a
# title-case violation.
_PACKAGE_LIKE_TITLE_RE = re.compile(
    # ``vegan: ...`` (bare), ``{vegan}: ...`` (case-protection),
    # ``{{vegan}: ...}`` (BibTeX-wrapped). The leading-brace group is
    # optional but balanced via a non-capturing alternation.
    r"^\{*\s*\{?[a-z][a-zA-Z0-9._]*\}?\s*:"
)


def _starts_with_package_idiom(title: str) -> bool:
    return bool(_PACKAGE_LIKE_TITLE_RE.match(title))


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
        # author-dictated case wins. Also exempt the canonical
        # ``vegan: Community Ecology Package`` idiom where the title
        # opens with an unwrapped lowercase R-package identifier.
        if (
            not _starts_with_markup(title)
            and not _starts_with_package_idiom(title)
            and not _word_is_uppercase_start(words[0])
        ):
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
                continue
        # Sentence-case detection: walk principal words after the first;
        # flag when any are lowercase. JSS Chicago-style title case
        # capitalises every word that isn't a short stop word
        # (article, conjunction, short preposition). This catches the
        # large bib-FN class of "Flexible nonhomogeneous Markov models
        # for panel observed data" — first word capped but principals
        # like "nonhomogeneous", "models", "observed" left lowercase.
        #
        # Use a markup-aware projection: words inside `\pkg{...}`,
        # `\code{...}`, `\proglang{...}` are removed entirely so the
        # check sees only user-prose words. Without this, a title like
        # ``Unifying Algorithms: \pkg{optimx} for \proglang{R}`` would
        # falsely flag the lowercase ``optimx``.
        prose_only = _visible_words_for_titlecase(
            _strip_markup_content(title)
        )
        # Skip the first prose-only word; the first-word check above
        # already covered it via the original title context.
        offenders = [
            w for w in prose_only[1:] if _is_lowercase_principal(w)
        ]
        if offenders:
            sample = ", ".join(repr(w) for w in offenders[:3])
            yield _violation(
                bib=bib,
                entry=entry,
                rule_id="JSS-REFS-006",
                suggestion=(
                    f"Capitalize the principal words in the title "
                    f"(found lowercase: {sample})."
                ),
            )


# Chicago-style stop words that legally stay lowercase mid-title in
# JSS title case: articles, coordinating conjunctions, and the short
# prepositions (≤ 4 letters) listed in Chicago Manual of Style §8.159.
# Longer prepositions ("between", "across", "through", "within",
# "under") get capitalised, matching the user's per-paper FN comments.
_TITLE_STOP_WORDS: frozenset[str] = frozenset({
    "a", "an", "the",
    "and", "or", "but", "nor", "for", "yet", "so", "if",
    "as", "at", "by", "in", "of", "on", "to", "up", "via", "vs",
    "with", "from", "into", "onto", "than", "per", "off",
    # Latin connectives that appear in titles ("et al.", etc.)
    "et", "al",
    # Common short conjunctions / particles
    "is", "be", "do",
})


_PUNCT_TRIM_RE = re.compile(r"^[^A-Za-z]+|[^A-Za-z0-9]+$")


def _visible_words_for_titlecase(title: str) -> list[str]:
    """Whitespace-only tokenizer for the principal-word check.

    Differs from ``_visible_words`` (which also splits on hyphens and
    slashes): we want hyphenated compounds like ``Date-time`` and
    ``Spatio-temporal`` to stay intact so their leading capital
    suffices to mark them title-cased. Splitting them would falsely
    flag the lowercase second element of an author-chosen compound.
    """
    return [w for w in re.split(r"\s+", title) if re.search(r"[A-Za-z]", w)]


def _is_lowercase_principal(word: str) -> bool:
    """True if ``word`` looks like a principal word that should be
    capitalised under JSS title case but appears all lowercase.

    Strips wrapping punctuation (parens, quotes, commas, periods) so
    title-fragment tokens like ``(with`` and ``discussion).`` don't
    falsely trigger on their punctuation tail. Conservative on
    word-shape: skips short words (< 4 letters), known stop words,
    and known R-package identifiers (those are REFS-004 markup
    issues, not title-case issues).
    """
    stripped = _PUNCT_TRIM_RE.sub("", word)
    if not stripped:
        return False
    if stripped != stripped.lower():
        return False
    if len(stripped) < 4:
        return False
    if stripped in _TITLE_STOP_WORDS:
        return False
    if stripped in R_PACKAGES:
        return False
    return True


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


_rule = _helpers.make_rule


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
