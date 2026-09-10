"""Drift check — the committed ``messages.json`` matches the fixtures.

``messages.json`` is the wording half of the rule-set fingerprint (spec
027 D4). It must be regenerated whenever a rule's message or suggestion
changes, because users' baseline entries are keyed on that text.
"""

from __future__ import annotations

from tools.generate_message_snapshot import main


def test_message_snapshot_is_fresh() -> None:
    exit_code = main(["--check"])
    assert exit_code == 0, (
        "specs/003-jss-rule-catalogue/messages.json is out of date with the "
        "violation fixtures. Run: python -m tools.generate_message_snapshot, "
        "then re-stamp the rule set with "
        "python -m tools.generate_catalogue_data --stamp-fingerprint "
        "--ruleset-version YYYY-MM-DD"
    )
