"""The JSS journal plugin.

Categories and rules are imported lazily inside :py:meth:`JSSJournal.categories`
so that ``import texlint`` stays cheap for downstream consumers.
"""

from __future__ import annotations

from importlib import import_module

from texlint.api import JournalRuleModule, Rule, RuleCategory

_TITLE_MAP: dict[str, str] = {
    "preamble": "Preamble",
    "structure": "Structure",
    "markup": "Markup",
    "citations": "Citations",
    "references": "References",
    "bibtex": "BibTeX",
    "naming": "Naming",
    "capitalization": "Capitalization",
    "typography": "Typography",
    "abbreviations": "Abbreviations",
    "code_style": "Code style",
    "code_width": "Code width",
    "operators": "Operators",
    "crossrefs": "Cross-references",
    "house_style": "House style",
}


class JSSJournal(JournalRuleModule):
    id = "jss"

    def categories(self) -> tuple[RuleCategory, ...]:
        # Lazy imports: each rule module is pulled in only when the engine
        # actually runs this journal. Third-party consumers who import
        # `texlint` but never load the JSS rules pay nothing for them.
        from texlint.journals.jss import _catalogue_data

        out: list[RuleCategory] = []
        for cat in _catalogue_data.ROLLOUT_ORDER:
            rules = _load_category_rules(cat)
            out.append(
                RuleCategory(id=cat, title=_TITLE_MAP[cat], rules=rules)
            )
        return tuple(out)


def _load_category_rules(category: str) -> tuple[Rule, ...]:
    """Import ``rules/<category>.py`` and return its ``rules`` tuple.

    During the spec-004 rollout, some category modules may not exist yet;
    this function returns an empty tuple for those so the journal can
    still be instantiated and other categories can land incrementally.
    """
    try:
        module = import_module(f"texlint.journals.jss.rules.{category}")
    except ModuleNotFoundError:
        return ()
    rules = getattr(module, "rules", None)
    if rules is None:
        return ()
    return tuple(rules)
