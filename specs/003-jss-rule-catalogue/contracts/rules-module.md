# Contract: Per-Category Rule Module

**Path**: `src/texlint/journals/jss/rules/<category>.py`
**One module per category**, matching the top-level `categories` list in `catalogue.yaml`.

## Module shape

Every rule module conforms to this layout (copy-ready template):

```python
"""<Category> rules for the JSS journal plugin.

Implements rules from spec 003's catalogue under the `<category>` category.
Each rule's provenance is the catalogue row with the matching `rule_id`;
see specs/003-jss-rule-catalogue/catalogue.yaml.
"""

from __future__ import annotations

from collections.abc import Iterator

# pylatexenc / bibtexparser imports as the checks need them, e.g.:
# from pylatexenc.latexwalker import LatexMacroNode, LatexGroupNode

from texlint.api import ParsedDocument, Rule, Severity, ToolConfig, Violation

# Optional: import the shared term list if this category consumes it
# from texlint.journals.jss import terms


# ---------------------------------------------------------------------------
# Private check callables — one per rule. Named _check_jss_<category>_NNN.
# ---------------------------------------------------------------------------

def _check_jss_<category>_001(doc: ParsedDocument, _cfg: ToolConfig) -> Iterator[Violation]:
    """<Rule description from catalogue.yaml, wrapped to 88 chars.>"""
    for tex in doc.tex_files:
        ...
        yield Violation(
            file=tex.path,
            line=...,
            column=...,
            rule_id="JSS-<CAT>-001",
            severity=Severity.WARNING,  # mirror catalogue.yaml severity
            message=...,
            suggestion=...,
            fix=None,  # flag-only per spec FR-022; Step 5 populates.
        )


def _check_jss_<category>_002(doc: ParsedDocument, _cfg: ToolConfig) -> Iterator[Violation]:
    ...


# ---------------------------------------------------------------------------
# Module-level Rule objects — exported as a tuple in definition order.
# JSSJournal.categories() reads this tuple.
# ---------------------------------------------------------------------------

_rule_jss_<category>_001 = Rule(
    id="JSS-<CAT>-001",
    category="<category>",
    severity=Severity.WARNING,
    message_template="...",
    authority="<authority-name-as-it-appears-in-catalogue.yaml>",
    check=_check_jss_<category>_001,
    formats=None,  # spec FR-014: all formats; narrowing is Step 4.
)


_rule_jss_<category>_002 = Rule(
    id="JSS-<CAT>-002",
    ...
)


rules: tuple[Rule, ...] = (
    _rule_jss_<category>_001,
    _rule_jss_<category>_002,
)
```

## Contract checklist

Every rule module MUST satisfy:

1. **Module name** matches a category in `catalogue.yaml`'s top-level `categories` list.
2. **`rules` tuple at module scope**, ordered by ascending `rule_id` counter. `JSSJournal.categories()` treats this tuple as the ordered rule set for the category.
3. **Each `Rule`'s `id`** matches a `rule_id` in `catalogue.yaml`'s `rules` list for this category; conversely, every `catalogue.yaml` rule whose category equals this module's name has exactly one matching `Rule` instance here.
4. **Each `Rule`'s `severity`** matches the catalogue row's `severity`. (A CI test cross-checks.)
5. **Each `Rule`'s `category`** matches the module name. (Not the catalogue's rule `category` — but they will be identical by construction of point 1.)
6. **Each `Rule`'s `check` callable** is a private function named `_check_jss_<category>_NNN` defined in the same file. No lambdas; no inlining.
7. **Each `Rule`'s `formats`** is `None` (spec FR-014 pins this for spec 003).
8. **Each `Rule`'s `fix` field does not exist** (the foundation's `Rule` dataclass has no `fix`; fix payloads live on `Violation`). Every emitted `Violation.fix` MUST be `None` (spec FR-022).
9. **Every `check` callable** is a pure function of `(ParsedDocument, ToolConfig)`. No globals mutated, no file I/O, no imports side-effectful at call time.
10. **AST-first or justified raw-source** (Constitution §II): a check using raw source (e.g., line-width rules scanning `tex.source_lines`) has a catalogue `notes` entry recording the §II justification.
11. **Deterministic** (Constitution §I): no randomness, no time/host-dependent branches.

## `JSSJournal.categories()` integration

`src/texlint/journals/jss/__init__.py` grows to match the category set:

```python
from __future__ import annotations

from texlint.api import JournalRuleModule, RuleCategory


class JSSJournal(JournalRuleModule):
    id = "jss"

    def categories(self) -> tuple[RuleCategory, ...]:
        # Lazy imports — each category module is loaded only when the engine
        # runs this journal. Third-party consumers who import `texlint` but
        # never load the JSS rules pay nothing for them.
        from texlint.journals.jss.rules import (
            abbreviations,
            bibtex,
            capitalization,
            citations,
            code_style,
            code_width,
            crossrefs,
            house_style,
            markup,
            naming,
            operators,
            preamble,
            references,
            structure,
            typography,
        )

        return (
            RuleCategory(id="preamble",        title="Preamble",        rules=preamble.rules),
            RuleCategory(id="structure",       title="Structure",       rules=structure.rules),
            RuleCategory(id="markup",          title="Markup",          rules=markup.rules),
            RuleCategory(id="citations",       title="Citations",       rules=citations.rules),
            RuleCategory(id="references",      title="References",      rules=references.rules),
            RuleCategory(id="bibtex",          title="BibTeX",          rules=bibtex.rules),
            RuleCategory(id="naming",          title="Naming",          rules=naming.rules),
            RuleCategory(id="capitalization",  title="Capitalization",  rules=capitalization.rules),
            RuleCategory(id="typography",      title="Typography",      rules=typography.rules),
            RuleCategory(id="abbreviations",   title="Abbreviations",   rules=abbreviations.rules),
            RuleCategory(id="code_style",      title="Code style",      rules=code_style.rules),
            RuleCategory(id="code_width",      title="Code width",      rules=code_width.rules),
            RuleCategory(id="operators",       title="Operators",       rules=operators.rules),
            RuleCategory(id="crossrefs",       title="Cross-references", rules=crossrefs.rules),
            RuleCategory(id="house_style",     title="House style",     rules=house_style.rules),
        )
```

This is the only place rules are registered (spec FR-019). No entry-point registration, no decorator registration, no runtime discovery.

## Category rollout order

Per spec FR-017 and research §7: `citations`, `references`, `bibtex`, `preamble`, `structure`, `markup`, `crossrefs`, `code_style`, `code_width`, `naming`, `operators`, `abbreviations`, `house_style`, `typography`, `capitalization`. The `JSSJournal.categories()` method returns categories in this order so `jss-lint`'s default output groups violations by rollout-order — the reader encounters citation issues before capitalisation edge cases.

## Test contract

Each category module has exactly one corresponding unit-test file:

- **Path**: `tests/unit/rules/test_<category>.py`
- **Coverage**: 100% branch coverage on `src/texlint/journals/jss/rules/<category>.py` (Constitution §IX).
- **Fixtures**: for each rule, one good and one bad fixture under `tests/fixtures/violations/<category>/<rule_id>-{good,bad}.{tex,bib}`.
- **Test shape**: one `test_<rule_id>_flags_bad` + one `test_<rule_id>_passes_good` per rule, plus any additional tests the branch-coverage report requires.

A failing branch-coverage measurement on a rule module is a blocker for the category's PR.

## Retrofit of Step 1 smoke rules

Per spec FR-024 and clarify Q2, three smoke rules migrate during the first PR of their category:

| New category | Retrofitted smoke rule | PR deletes | PR adds |
|---|---|---|---|
| `citations` | `cite_001_emph.py` (JSS-CITE-001) | `src/texlint/journals/jss/rules/cite_001_emph.py`, `tests/unit/journals/jss/rules/test_cite_001_emph.py` | `src/texlint/journals/jss/rules/citations.py` with `_check_jss_citations_001`; `tests/unit/rules/test_citations.py` |
| `references` | `bib_001_year.py` | same shape | `references.py`, `test_references.py` |
| `code_width` | `src_001_width.py` | same shape | `code_width.py`, `test_code_width.py` |

No compatibility shims, no re-exports, no parallel registration — the retrofit is a clean delete-and-rewrite in the same commit that adds the category module.
