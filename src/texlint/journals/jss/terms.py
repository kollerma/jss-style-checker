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
