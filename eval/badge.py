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
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any


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
