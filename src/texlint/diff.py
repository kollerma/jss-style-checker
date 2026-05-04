"""Spec 016 — `jss-lint diff` engine.

Pure-Python comparison over the spec-001 ``--output json`` shape.
The CLI subcommand and renderer wiring follow once the Click sub-
group migration ships.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(frozen=True)
class DiffReport:
    fixed: tuple[dict, ...]
    introduced: tuple[dict, ...]
    unchanged: tuple[dict, ...]


def _identity(v: dict, *, drop_line: bool) -> tuple:
    if drop_line:
        return (v["rule_id"], v["file"], v["message"])
    return (v["rule_id"], v["file"], v["line"], v["message"])


def _apply_renames(violations: Iterable[dict], renames: dict[str, str]) -> list[dict]:
    out = []
    for v in violations:
        new_id = renames.get(v["rule_id"], v["rule_id"])
        if new_id != v["rule_id"]:
            v = {**v, "rule_id": new_id}
        out.append(v)
    return out


def _sort_key(v: dict) -> tuple:
    return (v["file"], v["line"], v["rule_id"])


def compare(
    old: list[dict],
    new: list[dict],
    *,
    ignore_line_drift: bool = False,
    rule_renames: dict[str, str] | None = None,
) -> DiffReport:
    """Compare two spec-001 violation lists. See spec 016 contract C-2."""
    renames = rule_renames or {}
    old_norm = _apply_renames(old, renames)

    old_index = {_identity(v, drop_line=ignore_line_drift): v for v in old_norm}
    new_index = {_identity(v, drop_line=ignore_line_drift): v for v in new}

    old_keys = set(old_index)
    new_keys = set(new_index)

    fixed = sorted(
        (old_index[k] for k in old_keys - new_keys), key=_sort_key
    )
    introduced = sorted(
        (new_index[k] for k in new_keys - old_keys), key=_sort_key
    )
    # `unchanged` uses NEW's values (research §7).
    unchanged = sorted(
        (new_index[k] for k in old_keys & new_keys), key=_sort_key
    )

    return DiffReport(
        fixed=tuple(fixed),
        introduced=tuple(introduced),
        unchanged=tuple(unchanged),
    )
