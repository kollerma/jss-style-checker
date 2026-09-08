"""Contract tests for ``guide-coverage.yaml`` (spec 027 FR-G-001/FR-G-002).

The file answers a question a first-time author actually asks — "what
does this tool *not* check?" — so an answer that has quietly gone stale
is worse than no answer. These tests are what keeps it honest: they fail
when a listed rule is retired, when a new rule is claimed by no
provision, or when a gap is recorded with no reason.
"""

from __future__ import annotations

import copy

import pytest
import yaml
from tools._coverage_validate import CoverageError, validate

from texlint.journals.jss import _catalogue_data

COVERAGE_YAML = (
    __import__("pathlib").Path(__file__).resolve().parents[4]
    / "specs"
    / "003-jss-rule-catalogue"
    / "guide-coverage.yaml"
)


@pytest.fixture(scope="module")
def doc() -> dict:
    return yaml.safe_load(COVERAGE_YAML.read_text(encoding="utf-8"))


def _errors(doc: dict) -> list[CoverageError]:
    return validate(doc, active_rule_ids=_catalogue_data.RULES)


def test_shipped_file_is_valid(doc: dict) -> None:
    errors = _errors(doc)
    assert errors == [], "\n".join(str(e) for e in errors)


def test_every_active_rule_is_claimed(doc: dict) -> None:
    """Constitution §V, mechanically: a rule with no provision behind it
    is an opinion, not a rule."""
    claimed = {r for d in doc["directives"] for r in d["rules"]}
    unclaimed = set(_catalogue_data.RULES) - claimed
    assert not unclaimed, (
        f"these active rules are claimed by no directive: {sorted(unclaimed)}. "
        "Add a directive for the provision each one enforces, or retire the rule."
    )


def test_no_retired_rule_is_credited(doc: dict) -> None:
    """The failure the markdown checklist shipped with for months: four
    retired rules still credited as covering provisions."""
    claimed = {r for d in doc["directives"] for r in d["rules"]}
    retired = claimed & set(_catalogue_data.RETIRED_RULE_IDS)
    assert not retired, f"directives credit retired rules: {sorted(retired)}"


def test_every_gap_carries_a_reason(doc: dict) -> None:
    for directive in doc["directives"]:
        if directive["status"] != "checked":
            assert directive.get("reason", "").strip(), (
                f"{directive['id']} is {directive['status']} with no reason; "
                "an unexplained gap is not an answer"
            )


def test_the_four_authorities_are_dated(doc: dict) -> None:
    for name, meta in doc["sources"].items():
        assert meta.get("date") or meta.get("fetched"), (
            f"source {name} records no date; the fetch date is the honest "
            "pin for a page with no edition"
        )


class TestValidatorRejects:
    """The validator has to fail on the shapes that would mislead a
    reader, not merely on malformed YAML."""

    def test_a_retired_rule(self, doc: dict) -> None:
        broken = copy.deepcopy(doc)
        broken["directives"][0]["rules"] = ["JSS-CAP-003"]
        assert any("not active" in str(e) for e in _errors(broken))

    def test_an_unclaimed_active_rule(self, doc: dict) -> None:
        broken = copy.deepcopy(doc)
        for directive in broken["directives"]:
            if "JSS-WIDTH-001" in directive["rules"]:
                directive["rules"] = [
                    r for r in directive["rules"] if r != "JSS-WIDTH-001"
                ]
                if not directive["rules"]:
                    directive["status"] = "not_checked"
                    directive["reason"] = "removed for the test"
        assert any("JSS-WIDTH-001" in str(e) for e in _errors(broken))

    def test_a_checked_row_with_no_rule(self, doc: dict) -> None:
        broken = copy.deepcopy(doc)
        broken["directives"][0]["rules"] = []
        assert any("requires at least one rule" in str(e) for e in _errors(broken))

    def test_an_out_of_scope_row_that_names_rules(self, doc: dict) -> None:
        broken = copy.deepcopy(doc)
        target = next(d for d in broken["directives"] if d["status"] == "out_of_scope")
        target["rules"] = ["JSS-WIDTH-001"]
        assert any("must not name rules" in str(e) for e in _errors(broken))

    def test_a_gap_without_a_reason(self, doc: dict) -> None:
        broken = copy.deepcopy(doc)
        target = next(d for d in broken["directives"] if d["status"] == "not_checked")
        target["reason"] = ""
        assert any("requires a reason" in str(e) for e in _errors(broken))

    def test_an_id_whose_prefix_contradicts_its_source(self, doc: dict) -> None:
        broken = copy.deepcopy(doc)
        broken["directives"][0]["id"] = "SG-999"
        assert any("prefix does not match" in str(e) for e in _errors(broken))

    def test_a_duplicate_id(self, doc: dict) -> None:
        broken = copy.deepcopy(doc)
        broken["directives"].append(copy.deepcopy(broken["directives"][0]))
        assert any("duplicate id" in str(e) for e in _errors(broken))

    def test_an_unresolvable_section(self, doc: dict) -> None:
        broken = copy.deepcopy(doc)
        broken["directives"][0]["section"] = "page 7, somewhere"
        assert any("section must be" in str(e) for e in _errors(broken))
