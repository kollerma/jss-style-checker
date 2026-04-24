"""Spec 004 SC-001: every catalogue rule fires on its bad fixture.

For every active rule in ``_catalogue_data.RULES``, load its bad
fixture from ``tests/fixtures/violations/<category>/<rule_id>-bad.<ext>``
and run the JSS journal's full rule set against it. The target rule id
MUST appear in the output; this catches regressions where a rule's
check callable stops firing because (e.g.) an AST-walker helper was
narrowed too aggressively.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from texlint.api import ParsedDocument, ToolConfig
from texlint.core.parser import parse_bib_file, parse_tex_file
from texlint.journals.jss import JSSJournal, _catalogue_data

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "violations"


def _fixture_path(rule_id: str, category: str) -> Path:
    """Return the bad-fixture path for ``rule_id``; ``.bib`` for bib-only rules."""
    for suffix in (".tex", ".bib"):
        candidate = FIXTURES / category / f"{rule_id}-bad{suffix}"
        if candidate.exists():
            return candidate
    raise AssertionError(
        f"no bad fixture found for {rule_id} under {FIXTURES / category}/"
    )


@pytest.mark.parametrize(
    "rule_id", sorted(_catalogue_data.RULES.keys())
)
def test_rule_fires_on_its_bad_fixture(rule_id: str) -> None:
    meta = _catalogue_data.RULES[rule_id]
    fixture = _fixture_path(rule_id, meta["category"])

    if fixture.suffix == ".bib":
        doc = ParsedDocument(bib_files=(parse_bib_file(fixture),))
    else:
        doc = ParsedDocument(tex_files=(parse_tex_file(fixture),))

    journal = JSSJournal()
    cfg = ToolConfig()
    emitted: set[str] = set()
    for cat in journal.categories():
        for rule in cat.rules:
            for violation in rule.check(doc, cfg):
                emitted.add(violation.rule_id)

    assert rule_id in emitted, (
        f"{rule_id}'s bad fixture ({fixture.name}) did not trigger "
        f"the rule. Emitted: {sorted(emitted)}"
    )


def test_every_category_has_a_fixture_directory() -> None:
    """SC-001 housekeeping: one fixture dir per category."""
    for category in _catalogue_data.ROLLOUT_ORDER:
        assert (FIXTURES / category).is_dir(), (
            f"missing fixture directory: {FIXTURES / category}"
        )
