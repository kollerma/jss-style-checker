"""The shipped recall snapshot is fresh, complete, and honestly floored.

`specs/003-jss-rule-catalogue/recall.json` is what every recall surface
reads — the reviewer column, the author footer, JSON, SARIF, `explain`,
and the README badge (spec 027 FR-A-006). A stale or partial file would
have the tool telling authors a number the release never measured.
"""

from __future__ import annotations

import json

from eval.cli import RECALL_FLOOR
from tools.generate_recall_snapshot import MIN_PLANTS, OUTPUT_JSON, main

from eval import badge
from texlint.journals.jss import _catalogue_data


def _snapshot() -> dict:
    return json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))


def test_snapshot_matches_the_recorded_run() -> None:
    assert main(["--check"]) == 0, (
        "specs/003-jss-rule-catalogue/recall.json is out of date with "
        "eval/precision-history.db. Run: "
        "python -m tools.generate_recall_snapshot"
    )


def test_snapshot_only_names_active_rules() -> None:
    # A rule retired since the run would otherwise carry a recall claim
    # about a rule that no longer fires.
    unknown = set(_snapshot()["rules"]) - set(_catalogue_data.RULES)
    assert not unknown, f"snapshot names retired rules: {sorted(unknown)}"


def test_snapshot_records_its_provenance() -> None:
    snapshot = _snapshot()
    assert snapshot["min_plants"] == MIN_PLANTS
    assert snapshot["corpus_hash"]
    assert snapshot["run_timestamp"].endswith("Z")


def test_floor_is_within_ratchet_distance_of_the_snapshot() -> None:
    """Spec 027 D11 / FR-A-007: the floor tracks what we actually ship.

    The release checklist ratchets `RECALL_FLOOR` to
    `floor(snapshot - 0.03, 2 dp)`. This fails if the floor is ever left
    further below the measured aggregate than that, which would let a
    real regression pass the gate unnoticed.
    """
    aggregate = badge.pinned_recall_aggregate()
    assert RECALL_FLOOR <= aggregate, (
        f"floor {RECALL_FLOOR} exceeds the shipped aggregate {aggregate:.4f}"
    )
    assert RECALL_FLOOR >= round(aggregate - 0.03, 2) - 1e-9, (
        f"floor {RECALL_FLOOR} is more than 0.03 below the shipped "
        f"aggregate {aggregate:.4f}; ratchet it in the release checklist"
    )
