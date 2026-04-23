"""Test fixture: a no-op journal plugin registered under ``texlint.journals``.

Used by texlint's integration tests to verify that journal modules declared
via the ``texlint.journals`` entry-point group are discovered and loadable,
and that ``--journal stub`` dispatches to this journal without any edits to
``src/texlint/core/`` or ``src/texlint/api.py`` (Constitution §IV).
"""

from __future__ import annotations

from texlint.api import JournalRuleModule, RuleCategory


class StubJournal(JournalRuleModule):
    id = "stub"

    def categories(self) -> tuple[RuleCategory, ...]:
        return ()


__all__ = ["StubJournal"]
