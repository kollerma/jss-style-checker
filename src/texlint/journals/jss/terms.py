"""Shared canonical-form list for the JSS journal plugin.

Single source of truth for programming-language, statistical-package,
and code-like token names that rule modules cross-reference. See
``specs/003-jss-rule-catalogue/contracts/terms-list.md`` for the
public-surface contract and ``tests/unit/journals/jss/test_terms.py``
for the invariants.

FR-020 (spec 003): any rule module that inspects the canonical casing,
canonical form, or proper-noun spelling of a token listed here MUST
consume this module rather than re-declaring the token. Shadowing is
blocked by ``test_terms.test_t06_no_shadow_terms_in_rule_modules``.
"""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType

# ---------------------------------------------------------------------------
# Canonical forms
# ---------------------------------------------------------------------------

LANGUAGES: frozenset[str] = frozenset(
    {
        "R",
        "Python",
        "Java",
        "Fortran",
        "MATLAB",
        # Accept "Matlab" alongside "MATLAB" — MathWorks' own materials
        # use both. JSS has historically accepted both spellings.
        "Matlab",
        "S-PLUS",
        # Accept "S-Plus" alongside "S-PLUS" — Insightful / TIBCO
        # branding used the mixed-case form in product documentation.
        "S-Plus",
        "Stata",
        "SAS",
        "Julia",
        "C",
        "C++",
        "Stan",
    }
)

R_PACKAGES: frozenset[str] = frozenset(
    {
        "MASS",
        "ggplot2",
        "knitr",
        "pscl",
        "mgcv",
        "quantreg",
        "sandwich",
        "zoo",
        "xts",
    }
)


# ---------------------------------------------------------------------------
# Non-canonical → canonical mapping
# ---------------------------------------------------------------------------

_CANONICAL_RAW: Mapping[str, str] = {
    # Style-guide SG-044: Fortran
    "FORTRAN": "Fortran",
    "fortran": "Fortran",
    # SG-045: Java
    "java": "Java",
    "JAVA": "Java",
    # SG-046: MATLAB. MathWorks accepts both "MATLAB" and "Matlab" in
    # their own materials; only catch the all-lowercase form.
    "matlab": "MATLAB",
    # SG-047: S-PLUS. The vendor (Insightful, then TIBCO) used "S-Plus"
    # as the brand spelling; "S-PLUS" is also seen in JSS papers but
    # both are accepted. Catch only the clearly-wrong "Splus" /
    # "splus" / "SPLUS" forms.
    "Splus": "S-Plus",
    "splus": "S-Plus",
    "SPLUS": "S-Plus",
    # `ggplot` (without trailing 2) was previously mapped to "ggplot2"
    # but is widely used as casual shorthand for the package and as
    # the name of grob objects (`ggplot object`); the rule's
    # function-call exemption already covers `ggplot(` invocations.
    # Reviewers consistently labelled bare-prose mentions as FP, so
    # the mapping is removed.
}

CANONICAL: Mapping[str, str] = MappingProxyType(dict(_CANONICAL_RAW))


# ---------------------------------------------------------------------------
# Publisher / journal canonical forms (spec 004 FR-020 additive)
# ---------------------------------------------------------------------------
#
# SG-048..SG-052 pin canonical forms for a handful of publishers and
# journals that appear frequently in JSS references. JSS-NAME-002 looks
# up BibTeX ``publisher`` and ``journal`` fields against this mapping.

_PUBLISHER_CANONICAL_RAW: Mapping[str, str] = {
    # SG-048 originally pinned "Springer" → "Springer-Verlag", but
    # modern JSS bibliographies (post-2010) accept plain "Springer";
    # human-review labels split ~50/50 on this rule firing, indicating
    # reviewer disagreement rather than a clear convention. Dropped to
    # avoid penalising the now-canonical short form.
    # SG-049: Chapman & Hall / CRC
    "Chapman and Hall": "Chapman & Hall/CRC",
    "Chapman and Hall/CRC": "Chapman & Hall/CRC",
    # SG-050: Wiley canonical
    "John Wiley": "John Wiley & Sons",
    "Wiley": "John Wiley & Sons",
}

_JOURNAL_CANONICAL_RAW: Mapping[str, str] = {
    # SG-051: Annals of Statistics → "The Annals of Statistics"
    "Annals of Statistics": "The Annals of Statistics",
    # SG-052: JASA canonical
    "JASA": "Journal of the American Statistical Association",
}

PUBLISHER_CANONICAL: Mapping[str, str] = MappingProxyType(dict(_PUBLISHER_CANONICAL_RAW))
JOURNAL_CANONICAL: Mapping[str, str] = MappingProxyType(dict(_JOURNAL_CANONICAL_RAW))


def canonical_form(token: str) -> str | None:
    """Resolve *token* to its canonical form.

    Returns:
        The canonical form when *token* is a known alias (``CANONICAL`` key)
        or already canonical (``LANGUAGES`` or ``R_PACKAGES`` member).
        Returns ``None`` when *token* is unknown, empty, or
        whitespace-only.

    Semantics:
        * No case folding.
        * No substring matching.
        * No fuzzy / Levenshtein matching.

    See ``tests/unit/journals/jss/test_terms.py`` for the invariants.
    """
    if not token or not token.strip():
        return None
    if token in CANONICAL:
        return CANONICAL[token]
    if token in LANGUAGES:
        return token
    if token in R_PACKAGES:
        return token
    return None
