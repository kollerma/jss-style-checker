"""Rule-set provenance guards (spec 027 item D, FR-D-001/FR-D-002).

The stored ``ruleset_fingerprint`` must equal the computed one, and the
``ruleset_version`` date must be a real, plausible date. Users' baseline
entries are keyed on the message and suggestion wording the fingerprint
covers, so a rewording that ships without a date bump would silently
strand every baseline touching the reworded rules.
"""

from __future__ import annotations

import datetime as _dt
import json

import pytest
from tools.generate_catalogue_data import (
    CATALOGUE_YAML,
    MESSAGES_JSON,
    _load_doc,
    _load_messages,
    compute_fingerprint,
    main,
)

from texlint.journals.jss import _catalogue_data


@pytest.fixture(scope="module")
def doc() -> dict:
    return dict(_load_doc(CATALOGUE_YAML))


def test_stored_fingerprint_matches_computed(doc: dict) -> None:
    computed = compute_fingerprint(doc, _load_messages(MESSAGES_JSON))
    assert doc["ruleset_fingerprint"] == computed, (
        "the rule set changed without a re-stamp. Run: "
        "python -m tools.generate_message_snapshot && "
        "python -m tools.generate_catalogue_data --stamp-fingerprint "
        "--ruleset-version YYYY-MM-DD"
    )


def test_generator_check_is_clean() -> None:
    assert main(["--check"]) == 0


def test_ruleset_version_is_a_plausible_date(doc: dict) -> None:
    version = _dt.date.fromisoformat(doc["ruleset_version"])
    vendored = _dt.date.fromisoformat(doc["source_vendored_at"])
    assert vendored <= version <= _dt.date.today(), (
        "ruleset_version must lie between the vendored authority's date and today"
    )


def test_generated_module_mirrors_the_catalogue(doc: dict) -> None:
    assert _catalogue_data.RULESET_VERSION == doc["ruleset_version"]
    assert _catalogue_data.RULESET_FINGERPRINT == doc["ruleset_fingerprint"]
    assert _catalogue_data.GUIDE_EDITION == doc["guide_edition"]
    assert _catalogue_data.SOURCE_VENDORED_AT == doc["source_vendored_at"]
    assert _catalogue_data.GUIDE_SOURCE == (
        f"{doc['guide_edition']} ({doc['source_vendored_at']})"
    )


def test_check_fails_when_the_wording_moves(tmp_path) -> None:
    """The gate that makes a rewording a mandatory rule-set bump."""
    messages = dict(_load_messages(MESSAGES_JSON))
    rule_id, pairs = next(iter(sorted(messages.items())))
    messages[rule_id] = [[pairs[0][0], pairs[0][1] + " (reworded)"]]
    reworded = tmp_path / "messages.json"
    reworded.write_text(json.dumps(messages), encoding="utf-8")

    exit_code = main(["--check", f"--messages-path={reworded}"])
    assert exit_code == 1
