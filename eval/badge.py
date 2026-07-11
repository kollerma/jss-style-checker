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

Aggregates are pinned (spec 018, the 1.0.0 release): ``pinned_precision_
aggregate``/``pinned_recall_aggregate`` read a fixed iteration/snapshot
from ``precision-history.db`` rather than "whatever's latest," so the
public ``jss-style-checker`` repo's badges reflect the release state and
don't silently drift as the dev repo (``jss-style-checker-dev``) keeps
iterating after release. Bump ``PINNED_ITERATION_LABEL``/
``PINNED_RECALL_TIMESTAMP`` when cutting the next pinned release.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from eval import history

# The iterations.label recorded for this release — see
# `eval iterate record v1.0.0-release`.
PINNED_ITERATION_LABEL = "v1.0.0-release"
# The recall_history.run_timestamp of the latest recall snapshot as of
# this release. recall_history has no label column (spec 017 predates
# the pinning concept), so this freezes to whatever the most recent
# snapshot happened to be rather than any release-specific run — there
# was no fresh `eval-jss recall` pass as part of this release.
PINNED_RECALL_TIMESTAMP = "2026-07-06T15:05:08Z"


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


def pinned_recall_aggregate(history_db: Path) -> float:
    """Aggregate recall for the ``PINNED_RECALL_TIMESTAMP`` snapshot.

    ``0.0`` (not an error) if that timestamp has no rows — see
    ``pinned_precision_aggregate`` for why a bare ``SUM()`` never
    returns ``None`` for the row itself.
    """
    cx = history.connect(history_db)
    try:
        row = cx.execute(
            "SELECT SUM(tp) AS tp, SUM(fn) AS fn FROM recall_history "
            "WHERE run_timestamp = ?",
            (PINNED_RECALL_TIMESTAMP,),
        ).fetchone()
    finally:
        cx.close()
    tp = row["tp"] or 0
    fn = row["fn"] or 0
    return 0.0 if tp + fn == 0 else tp / (tp + fn)


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
