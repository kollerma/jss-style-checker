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
        "S-PLUS",
        "Stata",
        "SAS",
        "Julia",
        "C",
        "C++",
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
    # SG-046: MATLAB
    "Matlab": "MATLAB",
    "matlab": "MATLAB",
    # SG-047: S-PLUS
    "Splus": "S-PLUS",
    "S-Plus": "S-PLUS",
    # corpus-observed R package spellings
    "ggplot": "ggplot2",
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
    # SG-048: Springer is published by Springer-Verlag
    "Springer": "Springer-Verlag",
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
