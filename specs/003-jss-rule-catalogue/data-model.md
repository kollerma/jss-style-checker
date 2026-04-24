# Phase 1 Data Model — JSS Rule Catalogue

This feature introduces **two** in-repo data artefacts: the catalogue YAML and the shared term list. Every other type (`Rule`, `Violation`, `ParsedDocument`, `ToolConfig`, `Severity`, `Category`, `FixSuggestion`, `RuleCategory`) is defined in spec 001 `data-model.md` and **unchanged here** — this spec only populates the rule corpus, it does not extend the type system.

## 1. `catalogue.yaml` — the rule catalogue

Hand-authored YAML at `specs/003-jss-rule-catalogue/catalogue.yaml`. Source of truth. `catalogue.md` is re-rendered from it by `python -m tools.render_catalogue`.

### Top-level shape

```yaml
version: 1                   # integer; bumped when schema changes
source_vendored_at: "2021-05-23"  # date of the vendored docs/jss-template/jss.cls
categories:                  # the authoritative category list (FR-005)
  - preamble
  - structure
  - markup
  - citations
  - references
  - bibtex
  - naming
  - capitalization
  - typography
  - abbreviations
  - code_style
  - code_width
  - operators
  - crossrefs
  - house_style
retired_rule_ids:            # optional; structured field for retirements (spec 004 amendment 2026-04-23)
  - JSS-CITE-001
  - JSS-ABBR-002
rules:                       # one entry per rule
  - rule_id: JSS-CITE-001
    category: citations
    # ... (fields below)
```

**Top-level fields**:

| Field | Type | Required | Notes |
|---|---|---|---|
| `version` | int | yes | Schema version, starts at `1`. Bump on backwards-incompatible change. |
| `source_vendored_at` | str (ISO-8601 date) | yes | `\filedate` of the vendored `jss.cls`. Updated on annual refresh. |
| `categories` | list[str] | yes | Pinned category list (FR-005). |
| `rules` | list[mapping] | yes | Active rule rows (per-rule fields below). |
| `retired_rule_ids` | list[str] | no | Optional; ids in this list are permanently reserved (FR-004). Each entry matches `^JSS-[A-Z]+-\d{3}$`; must be unique; MUST be disjoint from the set of `rule_id`s in `rules`. Added by spec 004 Session 2026-04-23 to make retirements machine-readable. |

### Per-rule fields

| Field | Type | Required | Constraints | Notes |
|---|---|---|---|---|
| `rule_id` | str | yes | matches `^JSS-[A-Z]+-\d{3}$`; unique across all rules | Retired ids are permanently reserved (spec FR-004); never reused. |
| `category` | str | yes | must appear in top-level `categories` list | Matches the filename `src/texlint/journals/jss/rules/<category>.py`. |
| `severity` | enum[str] | yes | one of `error`, `warning`, `info` | Default mapping: objective → `error`, stylistic → `warning`, informational → `info`; deviations explained in `notes`. |
| `description` | str | yes | one line; ≤ 120 chars | Human-readable, lint-style sentence; no trailing period. |
| `authority` | enum[str] | yes | one of `jss_cls`, `article_tex`, `style_guide`, `author_instructions` | When two authorities agree, pick the higher in the chain `jss_cls > article_tex > style_guide > author_instructions` (FR-003). |
| `authority_ref` | str | yes | format depends on `authority` (see §1.3 below) | Resolvable against `docs/jss-template/` for `jss_cls`/`article_tex`; URL anchor for `style_guide`/`author_instructions` (FR-008, FR-010). |
| `example_violation` | str | yes | YAML `\|` block scalar; valid LaTeX or BibTeX fragment | Minimal input that triggers the rule; a reviewer copies and runs it to understand the check. |
| `example_fix` | str | yes | same shape as `example_violation` | The violating fragment with the rule's complaint addressed. |
| `inspects` | list[str] | yes | non-empty subset of `{tex_files, bib_files, raw_source}` | Declares which `ParsedDocument` field the check reads (FR-011). `raw_source` requires a §II justification in `notes`. |
| `auto_fixable` | bool | yes | `true` or `false` only | Flag only; implementation deferred to Step 5 (FR-013). |
| `notes` | str | no | free text | Records losing authority when two authorities disagreed (FR-003); §II justification for `raw_source` inspection; any tightening that took the rule below its natural scope. |

### 1.3 `authority_ref` format by authority

| authority | format | validator |
|---|---|---|
| `jss_cls` | `"jss.cls:NNN"` (line number) or `"jss.cls:\\macroname"` | line-number form → `1 ≤ N ≤ len(lines(docs/jss-template/jss.cls))`; macroname form → exactly one hit for `\macroname` in `docs/jss-template/jss.cls` |
| `article_tex` | `"article.tex:NNN"` or `"article.tex:§section-label"` | line number present in file, or `\label{sec:…}` / `\label{app:…}` appears in `docs/jss-template/article.tex` |
| `style_guide` | `"#anchor-id"` — URL fragment, matches `^#[a-z0-9-]+$` | format-only validation (network not consulted per research §3) |
| `author_instructions` | `"manuscript-preparation"` or `"#anchor-id"` — section heading slug | format-only validation |

### 1.4 Enum values — canonical spellings

| Enum | Values | Source |
|---|---|---|
| `authority` | `jss_cls` \| `article_tex` \| `style_guide` \| `author_instructions` | spec FR-002 |
| `severity` | `error` \| `warning` \| `info` | spec FR-012 |
| `inspects` member | `tex_files` \| `bib_files` \| `raw_source` | matches `ParsedDocument` fields from spec 001 |

### 1.5 Invariants (enforced by `tests/unit/journals/jss/test_catalogue.py`)

1. Every `rule_id` is globally unique.
2. Every `category` listed on a rule appears in the top-level `categories` list.
3. Every top-level `categories` entry has ≥ 1 rule (no dangling categories).
3a. `retired_rule_ids` entries match `^JSS-[A-Z]+-\d{3}$`, are unique within the list, and are disjoint from the set of active `rule_id`s.
4. `authority` is one of the four enum values (no free-form).
5. `severity` is one of the three enum values.
6. `inspects` is a non-empty list; every element is one of the three enum values.
7. For every `jss_cls` / `article_tex` ref, the referenced line or macro resolves in `docs/jss-template/`.
8. For every `style_guide` / `author_instructions` ref, the format is `#anchor-id` or a section slug (no line numbers per FR-010).
9. Every rule has a non-empty `description`, `example_violation`, and `example_fix`.
10. Every `rule_id`'s counter portion (the `NNN`) is ≥ 001; counters within a category are contiguous unless a retired rule's id is documented in `notes` of a sibling or in a category-level retirement log.

## 2. `terms.py` — the shared term list

Module at `src/texlint/journals/jss/terms.py`. Plain Python, no serialisation. Imported by rule modules in `capitalization`, `naming`, `house_style`, and any other category that inspects a canonical form the list already knows about (FR-020 open-consumer policy).

### 2.1 Public surface

```python
from __future__ import annotations

from types import MappingProxyType
from typing import Mapping

LANGUAGES: frozenset[str] = frozenset({
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
    # … (grows with the catalogue; additions must carry a style-guide reference
    # or be observed in the corpus with a TP labelling)
})

R_PACKAGES: frozenset[str] = frozenset({
    "MASS",
    "ggplot2",
    "knitr",
    "pscl",
    "mgcv",
    # … (grows with the catalogue; additions carry a CRAN reference in the
    # accompanying rule-module test fixture)
})

_CANONICAL_RAW: Mapping[str, str] = {
    # style-guide SG-044..SG-052: canonical spellings
    "FORTRAN": "Fortran",
    "java": "Java",
    "JAVA": "Java",
    "Matlab": "MATLAB",
    "matlab": "MATLAB",
    "Splus": "S-PLUS",
    "S-Plus": "S-PLUS",
    # … (grows with corpus-observed misspellings)
}

CANONICAL: Mapping[str, str] = MappingProxyType(dict(_CANONICAL_RAW))


def canonical_form(token: str) -> str | None:
    """Return the canonical form of *token* or None if the token is unknown.

    - If *token* is a CANONICAL key, returns the corresponding canonical form.
    - If *token* is itself in LANGUAGES or R_PACKAGES, returns *token*
      (it is already canonical).
    - Otherwise returns None.
    """
    if token in CANONICAL:
        return CANONICAL[token]
    if token in LANGUAGES:
        return token
    if token in R_PACKAGES:
        return token
    return None
```

### 2.2 Invariants (enforced by `tests/unit/journals/jss/test_terms.py`)

1. Every value in `CANONICAL` is in `LANGUAGES | R_PACKAGES` (no canonical target that isn't itself canonical).
2. No key in `CANONICAL` is simultaneously in `LANGUAGES | R_PACKAGES` (you don't point at yourself).
3. `canonical_form(v) == v` for every `v` in `LANGUAGES | R_PACKAGES`.
4. `canonical_form(k) == CANONICAL[k]` for every key `k` in `CANONICAL`.
5. `canonical_form(x) is None` for any `x` not in `LANGUAGES ∪ R_PACKAGES ∪ CANONICAL.keys()` — the function does not partial-match, does not case-fold, does not Levenshtein-correct.
6. No rule module under `src/texlint/journals/jss/rules/` contains a string literal that equals a key in `LANGUAGES | R_PACKAGES | set(CANONICAL)` unless that module also imports `terms` (grep-heuristic, allowlist-of-exceptions in `test_terms.py`).

## 3. `RuleCategory` (unchanged from spec 001)

Referenced here for completeness. Each `src/texlint/journals/jss/rules/<category>.py` exposes `rules: tuple[Rule, ...]`; `JSSJournal.categories()` constructs:

```python
RuleCategory(id="citations", title="Citations", rules=citations.rules)
```

Field definitions and invariants live in spec 001 `data-model.md`.

## 4. No new types

This spec adds **no new Python types** to `texlint.api`, `texlint.core`, or `texlint.journals.jss`. The catalogue is YAML data, not a Python object graph. Contract validation happens at test time (loading YAML, iterating entries), not at runtime.

This is deliberate per Constitution §X (small surface): every rule check consumes `(ParsedDocument, ToolConfig)` and yields `Violation`s exactly as Step 1 established. The catalogue is a review artefact that describes what the linter does; it is not a runtime input.
