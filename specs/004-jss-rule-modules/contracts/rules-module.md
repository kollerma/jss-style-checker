# Contract: per-category rule module

**Path pattern**: `src/texlint/journals/jss/rules/<category>.py`
**One module per category** in `_catalogue_data.ROLLOUT_ORDER` (= `catalogue.yaml` `categories:`).

## Canonical shape

```python
"""<Category title> rules for the JSS journal plugin.

One check callable per rule, bound to a module-level Rule object. Rule
metadata comes from _catalogue_data.RULES (generated from catalogue.yaml);
this module never duplicates catalogue text.

Rules in this module:
  - JSS-<CAT>-NNN — <one-line description>
  - ...
"""

from __future__ import annotations

from collections.abc import Iterator

from pylatexenc.latexwalker import (
    LatexCharsNode, LatexEnvironmentNode, LatexGroupNode, LatexMacroNode,
    LatexMathNode,
)

from texlint.api import ParsedDocument, Rule, ToolConfig, Violation
from texlint.journals.jss import _catalogue_data
from texlint.journals.jss.rules import _helpers


# ---------------------------------------------------------------------------
# Check callables — one per rule. Name: check_<lowercased_rule_id_underscored>
# ---------------------------------------------------------------------------

def check_jss_<cat>_001(
    doc: ParsedDocument, cfg: ToolConfig
) -> Iterator[Violation]:
    """<one-line summary; catalogue description may be copied as docstring>."""
    meta = _catalogue_data.RULES["JSS-<CAT>-001"]
    for tex in doc.tex_files:
        for node in _helpers._walk(tex.nodes):
            if not _condition(node):
                continue
            line, col = _helpers._lineno_col(tex, node.pos)
            yield Violation(
                file=tex.path,
                line=line,
                column=col,
                rule_id="JSS-<CAT>-001",
                severity=meta["severity"],
                message=meta["message_template"],
                suggestion=_build_suggestion(node),
                fix=None,
            )


# ---------------------------------------------------------------------------
# Private helpers — rule-specific; shared patterns live in _helpers.py
# ---------------------------------------------------------------------------

def _condition(node) -> bool:
    ...


def _build_suggestion(node) -> str | None:
    ...


# ---------------------------------------------------------------------------
# Rule objects + module-level rules tuple
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
        formats=None,  # spec 004 FR-024: format narrowing is Step 4 scope.
    )


jss_<cat>_001 = _rule("JSS-<CAT>-001", check_jss_<cat>_001)
# jss_<cat>_002 = _rule("JSS-<CAT>-002", check_jss_<cat>_002)
# ...

rules: tuple[Rule, ...] = (
    jss_<cat>_001,
    # jss_<cat>_002,
    # ...
)
```

## Naming conventions

| Artefact | Convention | Example |
|---|---|---|
| Module filename | `<category>.py` matching `_catalogue_data.ROLLOUT_ORDER` | `citations.py` |
| Check callable | `check_<lowercased_rule_id_with_underscores>` (public) | `check_jss_cite_002` |
| Module-level Rule instance | `<lowercased_rule_id_with_underscores>` (public) | `jss_cite_002` |
| Private helpers | `_<snake_case>` (private to module) | `_condition`, `_build_suggestion` |
| Rules tuple | `rules: tuple[Rule, ...]` at module scope | — |

## Contract checklist

A category module MUST satisfy:

1. **Module name** matches a category in `_catalogue_data.ROLLOUT_ORDER`.
2. **`rules` tuple at module scope**, typed `tuple[Rule, ...]`. Immutable.
3. **Every `Rule` in `rules`** is constructed via the `_rule(rule_id, check_fn)` helper (or an equivalent inline construction that pulls every field from `_catalogue_data.RULES[rule_id]`). Hardcoding severity, category, message_template, or authority is forbidden — the CI consistency test catches drift, but the direct-lookup idiom prevents drift in the first place.
4. **Every `check_*` callable** is public (no underscore prefix) and named `check_<lowercased_rule_id_with_underscores>`. One per rule. `Rule.check` binds the same callable.
5. **No module-level mutable state**. `RULES` is imported fresh each invocation through `_catalogue_data`; rule callables are pure functions of `(ParsedDocument, ToolConfig)`.
6. **AST-first**: rule logic walks `tex.nodes` via `_helpers._walk` / `_helpers._iter_with_parent` unless the catalogue entry declares `inspects: [raw_source]` (currently only `JSS-WIDTH-001`). Raw-source rules MUST mask verbatim / comment regions per `_helpers._is_inside_*` helpers unless they document why (in the catalogue's `notes`).
7. **Violations carry `fix=None`**. Spec 004 FR-025. No exceptions.
8. **Every rule in the category's `catalogue.yaml` entries** has exactly one `Rule` instance in `rules`. Missing rules fail `test_catalogue_registration.py`.
9. **No retired rule ids** appear as `Rule.id`. Checked against `_catalogue_data.RETIRED_RULE_IDS`.
10. **100% branch coverage** on the module's file, verified by `pytest --cov=src/texlint/journals/jss/rules/<category> --cov-branch --cov-fail-under=100`.

## Imports — allowed and forbidden

**Allowed** (top-of-module):
- `collections.abc.Iterator`
- `pylatexenc.latexwalker.*` (any subclass of `LatexNode`)
- `pylatexenc.macrospec.*` (occasionally for argspec inspection)
- `texlint.api` (anything: `ParsedDocument`, `Rule`, `ToolConfig`, `Violation`, `Severity`)
- `texlint.journals.jss._catalogue_data`
- `texlint.journals.jss.rules._helpers`
- `texlint.journals.jss.terms` (for rules that consume the shared term list)
- Standard library (`re`, `typing`, `itertools`, etc.)

**Forbidden** anywhere in the module:
- `yaml` — runtime YAML parsing is not allowed; use `_catalogue_data` for catalogue-sourced metadata.
- Direct imports from `src/texlint/core/` — the journal plugin treats core as opaque. Use `texlint.api` for everything.
- Direct imports from another category's rule module — per-category modules are independent. Cross-module helpers move to `_helpers.py` when ≥3 concrete callers exist.
- Test-only or dev-only modules (`tests/*`, `tools/*`) — rule modules are production code.

## Lazy-import rationale

`JSSJournal.categories()` imports category modules **inside** the method body. `from texlint.journals.jss.rules import preamble` happens on first invocation, not on `import texlint`. This:

- Keeps `import texlint` cheap for consumers who never invoke the JSS journal.
- Avoids circular-import risk if a future category imports from `texlint.api` which imports from `texlint.journals.jss` (shouldn't happen, but lazy is the defensive choice).
- Matches what spec 003 already established in `JSSJournal.categories()` for the three smoke rules.

## Retrofit operations

Three categories retrofit Step 1 smoke rules in their first PR:

| Category | PR deletes | PR adds |
|---|---|---|
| `citations` | `rules/cite_001_emph.py`; `tests/unit/journals/jss/test_cite_001_emph.py`; and any integration-test references to the flat fixture `tests/fixtures/violations/JSS-CITE-001.tex` that assume JSS-CITE-001 exists (FR-018). | `rules/citations.py` with 3 rules (CITE-002, CITE-003, CITE-004); `tests/unit/rules/test_citations.py`; 3 fixture pairs under `tests/fixtures/violations/citations/`. No retrofit: JSS-CITE-001 is retired. |
| `references` | `rules/bib_001_year.py`; `tests/unit/journals/jss/test_bib_001_year.py`. | `rules/references.py` with 7 rules (REFS-001..007); `JSS-REFS-001` is the retrofit of `bib_001_year.py`'s year-presence check with a matching test + fixture pair. |
| `code_width` | `rules/src_001_width.py`; `tests/unit/journals/jss/test_src_001_width.py`. | `rules/code_width.py` with 1 rule (WIDTH-001); retrofit of `src_001_width.py`'s line-width check with the new configurable column limit from `ToolConfig`. |
