"""Tests for ``src/texlint/journals/jss/terms.py``.

Covers invariants T-01..T-06 from
``specs/003-jss-rule-catalogue/contracts/terms-list.md``:

 * T-01 — ``CANONICAL.values()`` ⊆ ``LANGUAGES ∪ R_PACKAGES``
 * T-02 — ``CANONICAL`` keys disjoint from ``LANGUAGES ∪ R_PACKAGES``
 * T-03 — ``canonical_form(v) == v`` for every v in LANGUAGES ∪ R_PACKAGES
 * T-04 — ``canonical_form(k) == CANONICAL[k]`` for every k in CANONICAL
 * T-05 — empty / whitespace-only input returns None
 * T-06 — no rule module re-declares a known term as a string literal
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

from texlint.journals.jss import terms

REPO_ROOT = Path(__file__).resolve().parents[4]
RULES_DIR = REPO_ROOT / "src" / "texlint" / "journals" / "jss" / "rules"


# Allowlist: rule modules that are legitimately permitted to contain a literal
# from the shared list (typically because the rule exists to rewrite that
# specific literal and importing from ``terms.py`` would be circular).
_SHADOW_ALLOWLIST: frozenset[str] = frozenset()


# ---------------------------------------------------------------------------
# T-01 .. T-04 — structural invariants of the term tables
# ---------------------------------------------------------------------------


def test_t01_canonical_values_are_canonical() -> None:
    known = terms.LANGUAGES | terms.R_PACKAGES
    stray = {v for v in terms.CANONICAL.values() if v not in known}
    assert not stray, f"CANONICAL values not in LANGUAGES | R_PACKAGES: {sorted(stray)}"


def test_t02_canonical_keys_disjoint_from_canonical_targets() -> None:
    known = terms.LANGUAGES | terms.R_PACKAGES
    overlap = set(terms.CANONICAL) & known
    assert not overlap, f"CANONICAL keys overlap with LANGUAGES / R_PACKAGES: {sorted(overlap)}"


def test_t03_canonical_form_is_fixed_point_on_canonical_tokens() -> None:
    for token in terms.LANGUAGES | terms.R_PACKAGES:
        got = terms.canonical_form(token)
        assert got == token, f"canonical_form({token!r}) returned {got!r}; expected {token!r}"


def test_t04_canonical_form_resolves_aliases() -> None:
    for alias, canonical in terms.CANONICAL.items():
        got = terms.canonical_form(alias)
        assert got == canonical, (
            f"canonical_form({alias!r}) returned {got!r}; expected {canonical!r}"
        )


# ---------------------------------------------------------------------------
# T-05 — negative-input handling
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("bad_input", ["", "   ", "\t", "\n"])
def test_t05_empty_or_whitespace_returns_none(bad_input: str) -> None:
    assert terms.canonical_form(bad_input) is None


def test_t05_unknown_token_returns_none() -> None:
    assert terms.canonical_form("Pythom") is None  # typo
    assert terms.canonical_form("r") is None  # lowercase not aliased by default
    assert terms.canonical_form("some random phrase") is None


# ---------------------------------------------------------------------------
# T-06 — no rule module re-declares a known term (FR-020 open-consumer policy)
# ---------------------------------------------------------------------------


def _string_literals(py_path: Path) -> set[str]:
    """Extract every ``str`` literal found in *py_path*'s AST."""
    tree = ast.parse(py_path.read_text(encoding="utf-8"))
    literals: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            literals.add(node.value)
    return literals


def test_t06_no_shadow_terms_in_rule_modules() -> None:
    known: frozenset[str] = (
        terms.LANGUAGES | terms.R_PACKAGES | frozenset(terms.CANONICAL)
    )
    offenders: list[tuple[str, set[str]]] = []
    for py_path in sorted(RULES_DIR.rglob("*.py")):
        if py_path.name == "__init__.py":
            continue
        if py_path.stem in _SHADOW_ALLOWLIST:
            continue
        # If the module imports from terms, exempt it — it's using the shared
        # list legitimately and the literal is an intended reference.
        source = py_path.read_text(encoding="utf-8")
        import_re = r"from\s+texlint\.journals\.jss(?:\s+import\s+terms|\.terms\s+import)"
        if re.search(import_re, source):
            continue
        if "import texlint.journals.jss.terms" in source:
            continue
        shadowed = _string_literals(py_path) & known
        if shadowed:
            offenders.append((py_path.name, shadowed))
    assert not offenders, (
        "These rule modules hard-code tokens already in terms.py:\n"
        + "\n".join(f"  {name}: {sorted(shadow)}" for name, shadow in offenders)
        + "\nImport from texlint.journals.jss.terms instead (FR-020)."
    )
