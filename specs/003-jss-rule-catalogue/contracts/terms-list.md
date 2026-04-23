# Contract: `terms.py` — Shared Term List

**Path**: `src/texlint/journals/jss/terms.py`
**Purpose**: single source of truth for canonical spellings of programming-language, statistical-package, and code-like token names that rule modules cross-reference.
**Scope of consumers**: any rule module that inspects the canonical form of a token already known to the list (spec FR-020 open-consumer policy, clarify Q5).

## Public surface

The module exports exactly four names. Anything else is private.

### `LANGUAGES: frozenset[str]`

Canonical spellings of programming-language and large-programmable-system names as JSS authors reference them. Canonical means: the spelling JSS prefers per the style guide.

- Seed members: `"R"`, `"Python"`, `"Java"`, `"Fortran"`, `"MATLAB"`, `"S-PLUS"`, `"Stata"`, `"SAS"`, `"Julia"`, `"C"`, `"C++"`.
- Additions MUST be accompanied by a style-guide reference (for JSS-pinned spellings) or a corpus observation labelled TP (for new entries that emerge from manuscripts).
- No lowercase/alternate-case variants — those live as keys in `CANONICAL` (see below).

### `R_PACKAGES: frozenset[str]`

Canonical names of R packages the catalogue's rules reference. Canonical means: the exact string from CRAN's `DESCRIPTION` file.

- Seed members: `"MASS"`, `"ggplot2"`, `"knitr"`, `"pscl"`, `"mgcv"`, `"quantreg"`, `"sandwich"`, `"zoo"`, `"xts"`.
- Additions MUST carry a CRAN URL in the PR description and a test fixture that exercises the package name in a plausible LaTeX context.
- No lowercase/typo variants — those live in `CANONICAL`.

### `CANONICAL: Mapping[str, str]`

Read-only (`types.MappingProxyType`) lookup from non-canonical spelling to canonical spelling.

- Populated from style-guide directives SG-044..SG-052 (the explicit "use X not Y" pairs).
- Populated from corpus observations where a manuscript uses a non-canonical spelling that a `naming` or `capitalization` rule flags.
- Keys are non-canonical; values are canonical (i.e., the value MUST appear in `LANGUAGES | R_PACKAGES`).

Seed contents:

```python
{
    # SG-044
    "FORTRAN": "Fortran",
    # SG-045
    "java": "Java",
    "JAVA": "Java",
    # SG-046
    "Matlab": "MATLAB",
    "matlab": "MATLAB",
    # SG-047
    "Splus": "S-PLUS",
    "S-Plus": "S-PLUS",
    # corpus-observed R variants
    "ggplot": "ggplot2",
}
```

### `canonical_form(token: str) -> str | None`

Resolves a token to its canonical form.

**Semantics**:

- If `token` is a key in `CANONICAL`, return `CANONICAL[token]`.
- Else if `token` is in `LANGUAGES | R_PACKAGES`, return `token` (it is already canonical).
- Else return `None`.

**Non-semantics** (what the function does NOT do):

- No case folding. `canonical_form("r") is None`, not `"R"` — the lowercase form is either flagged by a rule or deliberately added to `CANONICAL` if JSS has an opinion.
- No substring matching. `canonical_form("Python 3") is None`.
- No Levenshtein / fuzzy matching. `canonical_form("Pythom") is None`.
- No side effects. Called from inside an AST walk; must be hashable-fast.

## Invariants (enforced by `tests/unit/journals/jss/test_terms.py`)

| # | Invariant | Rationale |
|---|---|---|
| T-01 | `CANONICAL.values() ⊆ LANGUAGES ∪ R_PACKAGES` | Every canonical-target is itself canonical. |
| T-02 | `CANONICAL.keys() ∩ (LANGUAGES ∪ R_PACKAGES) == ∅` | A term is not simultaneously canonical and aliased to itself. |
| T-03 | For every `v` in `LANGUAGES ∪ R_PACKAGES`, `canonical_form(v) == v`. | Canonical forms are fixed points. |
| T-04 | For every `k` in `CANONICAL`, `canonical_form(k) == CANONICAL[k]`. | Aliases resolve. |
| T-05 | `canonical_form("") is None` and `canonical_form("   ") is None`. | No accidental empty-string canonicalisation. |
| T-06 | No rule module under `src/texlint/journals/jss/rules/` contains a string literal equal to any element of `LANGUAGES ∪ R_PACKAGES ∪ CANONICAL.keys()` unless the same module imports `terms` or is explicitly allowlisted in `test_terms.py`. | Enforces FR-020: one source of truth for term spellings. |

## Consumer pattern

Typical use inside a `capitalization` rule's check:

```python
from texlint.journals.jss import terms

def _check_jss_capitalization_001(doc, _cfg):
    for tex in doc.tex_files:
        for node in _walk_chars(tex.nodes):
            token = node.chars.strip()
            canonical = terms.canonical_form(token)
            if canonical is not None and canonical != token:
                yield Violation(
                    file=tex.path,
                    line=...,
                    column=...,
                    rule_id="JSS-CAP-001",
                    severity=Severity.WARNING,
                    message=f"Non-canonical spelling {token!r}; use {canonical!r}.",
                    suggestion=f"Replace {token!r} with {canonical!r}.",
                    fix=None,
                )
```

## Non-goals

- `terms.py` is NOT a spellchecker. It does not know about every R package on CRAN; it knows about the packages the catalogue's rules reference.
- `terms.py` does NOT validate against CRAN at runtime (spec FR-023 explicitly excludes this).
- `terms.py` does NOT grow endlessly. When an entry stops being referenced by any rule module or test, it is a candidate for removal (Constitution §X — no dead data).
- `terms.py` does NOT expose the sets as lists or ordered collections; `frozenset` and `MappingProxyType` are the only types.

## Evolution policy

A PR that modifies `terms.py` MUST:

1. Add a catalogue `notes` entry on any rule whose behaviour depends on the new term, OR
2. Add a test fixture under `tests/fixtures/violations/<category>/` that exercises the new term, AND
3. Keep the three invariants T-01, T-02, T-06 satisfied.
