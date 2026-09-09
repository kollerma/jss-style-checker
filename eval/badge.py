"""Spec 017 — shields.io endpoint JSON for the precision / recall
README badges.

The badges read JSON files served from a static endpoint (e.g. via
GitHub Pages). Each call returns the shields.io v1 endpoint shape::

    {"schemaVersion": 1, "label": "...", "message": "0.94", "color": "..."}

Color buckets (per spec 017 data-model §6):

    >= 0.85   brightgreen
    >= 0.70   green
    >= 0.55   yellow
    <  0.55   red

Run via:

    python -m eval.badge precision 0.94
    python -m eval.badge recall    0.81

Aggregates are pinned rather than "whatever's latest", so the public
``jss-style-checker`` repo's badges reflect the release state and don't
silently drift as the dev repo keeps iterating after release.
``pinned_precision_aggregate`` reads a fixed iteration label from
``precision-history.db``; ``pinned_recall_aggregate`` reads the shipped
snapshot ``specs/003-jss-rule-catalogue/recall.json`` — the same file
the tool itself reports recall from (spec 027 FR-A-006), so the badge
and the author footer can never disagree. Bump
``PINNED_ITERATION_LABEL`` and regenerate the snapshot
(``tools/generate_recall_snapshot.py``) when cutting the next release.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from eval import history

# The iterations.label recorded for this release — see
# `eval iterate record v1.2.0-release`.
PINNED_ITERATION_LABEL = "v1.2.0-release"
# Recall is pinned by the shipped snapshot, not by a constant here:
# `specs/003-jss-rule-catalogue/recall.json` is the single source every
# recall surface reads (spec 027 FR-A-006), badge included.
RECALL_SNAPSHOT = (
    Path(__file__).resolve().parents[1]
    / "specs"
    / "003-jss-rule-catalogue"
    / "recall.json"
)


def _color_for(value: float) -> str:
    if value >= 0.85:
        return "brightgreen"
    if value >= 0.70:
        return "green"
    if value >= 0.55:
        return "yellow"
    return "red"


def _format_value(value: float) -> str:
    """Two-decimal text rendering, matching the existing
    `eval-jss report` precision column."""
    return f"{value:.2f}"


def _badge(label: str, value: float) -> dict[str, Any]:
    return {
        "schemaVersion": 1,
        "label": label,
        "message": _format_value(value),
        "color": _color_for(value),
    }


def precision_badge_json(aggregate: float) -> dict[str, Any]:
    return _badge("precision", aggregate)


def recall_badge_json(aggregate: float) -> dict[str, Any]:
    return _badge("recall", aggregate)


def f1_badge_json(value: float) -> dict[str, Any]:
    return _badge("F1", value)


def pinned_precision_aggregate(history_db: Path) -> float:
    """Full-corpus precision for the ``PINNED_ITERATION_LABEL`` iteration.

    ``0.0`` (not an error) if that label was never recorded — a bare
    ``SUM()`` query always returns exactly one row, with NULLs when
    nothing matches, so this degrades the same way an empty DB does.
    """
    cx = history.connect(history_db)
    try:
        row = cx.execute(
            "SELECT SUM(tp) AS tp, SUM(fp) AS fp "
            "FROM iteration_rule_stats "
            "WHERE iteration_id = ("
            "  SELECT id FROM iterations WHERE label = ? ORDER BY id DESC LIMIT 1"
            ") AND scope = 'full'",
            (PINNED_ITERATION_LABEL,),
        ).fetchone()
    finally:
        cx.close()
    tp = row["tp"] or 0
    fp = row["fp"] or 0
    return 0.0 if tp + fp == 0 else tp / (tp + fp)


def pinned_recall_aggregate(_history_db: Path | None = None) -> float:
    """Aggregate recall from the **shipped snapshot**.

    Reads ``specs/003-jss-rule-catalogue/recall.json`` rather than
    querying the history database, so the badge cannot disagree with
    what the tool itself reports to a user (spec 027 FR-A-006). The
    snapshot is generated from one pinned run by
    ``tools/generate_recall_snapshot.py``; before 1.2.0 this function
    carried its own timestamp constant, which had already drifted from
    the one the paper pinned.

    The parameter is kept so existing callers (and the CLI below) need
    no change; it is unused.
    """
    snapshot = json.loads(RECALL_SNAPSHOT.read_text(encoding="utf-8"))
    tp = sum(entry["tp"] for entry in snapshot["rules"].values())
    fn = sum(entry["fn"] for entry in snapshot["rules"].values())
    return 0.0 if tp + fn == 0 else tp / (tp + fn)


def pinned_recall_run_timestamp() -> str:
    """The run the shipped snapshot pins, for release notes and docs."""
    return json.loads(RECALL_SNAPSHOT.read_text(encoding="utf-8"))["run_timestamp"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m eval.badge",
        description="Emit a shields.io endpoint JSON document.",
    )
    parser.add_argument(
        "label",
        choices=("precision", "recall", "f1"),
        help="badge label",
    )
    parser.add_argument(
        "value",
        type=float,
        help="numeric value in [0, 1]",
    )
    args = parser.parse_args(argv)
    if not 0.0 <= args.value <= 1.0:
        print(
            f"error: value must be in [0, 1]; got {args.value}",
            file=sys.stderr,
        )
        return 2
    fn = {
        "precision": precision_badge_json,
        "recall": recall_badge_json,
        "f1": f1_badge_json,
    }[args.label]
    sys.stdout.write(json.dumps(fn(args.value), indent=2))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":  # pragma: no cover — CLI entry
    raise SystemExit(main())
