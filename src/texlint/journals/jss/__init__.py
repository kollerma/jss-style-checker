"""The JSS journal plugin.

Categories and rules are imported lazily inside :py:meth:`JSSJournal.categories`
so that ``import texlint`` stays cheap for downstream consumers.
"""

from __future__ import annotations

from texlint.api import JournalRuleModule, RuleCategory


class JSSJournal(JournalRuleModule):
    id = "jss"

    def categories(self) -> tuple[RuleCategory, ...]:
        # Lazy imports: each rule module is pulled in only when the engine
        # actually runs this journal. Third-party consumers who import
        # `texlint` but never load the JSS rules pay nothing for them.
        from texlint.journals.jss.rules.bib_001_year import rule as bib_001
        from texlint.journals.jss.rules.cite_001_emph import rule as cite_001
        from texlint.journals.jss.rules.src_001_width import rule as src_001

        return (
            RuleCategory(id="citation", title="Citation", rules=(cite_001,)),
            RuleCategory(id="bibliography", title="Bibliography", rules=(bib_001,)),
            RuleCategory(id="typography", title="Typography", rules=(src_001,)),
        )
