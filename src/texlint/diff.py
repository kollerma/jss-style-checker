"""Spec 016 — `jss-lint diff` engine + renderers.

Pure-Python comparison over the spec-001 ``--output json`` shape.
Three output formats: terminal (rich text), markdown
(GitHub-flavoured CommonMark, the canonical PR-comment surface),
and json (deterministic, machine-readable).
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass

# Spec-001 JSON top-level keys. Used for schema validation of
# the OLD / NEW inputs to `compare`. The `violations` array's
# per-element keys (rule_id, file, line, message, severity, etc.)
# are validated by the diff itself when it builds identity tuples.
_SPEC_001_REQUIRED_KEYS: frozenset[str] = frozenset(
    {"tool_version", "journal_id", "violations"}
)


class SchemaMismatch(ValueError):
    """Raised when an input file is not a spec-001 jss-lint JSON
    report. Caught at the CLI boundary; converted to exit 2 with
    a descriptive stderr message."""


def validate_payload(payload: object, source: str) -> list[dict]:
    """Validate a parsed JSON payload against the spec-001 shape
    and return its ``violations`` list.

    *source* is a short human-readable identifier (typically a
    file path) included in the error message.
    """
    if not isinstance(payload, dict):
        raise SchemaMismatch(
            f"{source}: top-level value is not a JSON object"
        )
    missing = _SPEC_001_REQUIRED_KEYS - set(payload)
    if missing:
        raise SchemaMismatch(
            f"{source}: missing required key(s) {sorted(missing)} — "
            "not a spec-001 jss-lint JSON report"
        )
    violations = payload["violations"]
    if not isinstance(violations, list):
        raise SchemaMismatch(
            f"{source}: 'violations' must be a list (got "
            f"{type(violations).__name__})"
        )
    # Per-element shape: each violation must have at least
    # rule_id, file, line, message — the keys the identity tuple
    # uses.
    per_violation_required = {"rule_id", "file", "line", "message"}
    for i, v in enumerate(violations):
        if not isinstance(v, dict):
            raise SchemaMismatch(
                f"{source}: violations[{i}] is not an object"
            )
        v_missing = per_violation_required - set(v)
        if v_missing:
            raise SchemaMismatch(
                f"{source}: violations[{i}] missing key(s) {sorted(v_missing)}"
            )
    return violations


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


# ---------------------------------------------------------------------------
# Renderers
# ---------------------------------------------------------------------------


def _v_summary(v: dict) -> str:
    """One-line-per-violation summary used by the terminal and
    markdown renderers."""
    return (
        f"{v['rule_id']} {v['file']}:{v['line']}: {v['message']}"
    )


def render_terminal(diff: DiffReport) -> str:
    """ANSI-free plain-text rendering. Suitable for piping; the
    Click runner does not auto-attach a TTY in tests, so we keep
    this format dep-free."""
    lines: list[str] = [
        (
            f"fixed: {len(diff.fixed)} "
            f"introduced: {len(diff.introduced)} "
            f"unchanged: {len(diff.unchanged)}"
        ),
    ]
    for label, group in (
        ("Fixed", diff.fixed),
        ("Introduced", diff.introduced),
        ("Unchanged", diff.unchanged),
    ):
        if not group:
            continue
        lines.append("")
        lines.append(f"== {label} ==")
        for v in group:
            lines.append(f"  {_v_summary(v)}")
    return "\n".join(lines) + "\n"


def render_markdown(diff: DiffReport) -> str:
    """GitHub-flavoured CommonMark. Three ## sub-sections with
    bulleted violation lists. The spec calls this the canonical
    PR-comment surface."""
    parts: list[str] = []
    parts.append(
        f"**fixed:** {len(diff.fixed)} | "
        f"**introduced:** {len(diff.introduced)} | "
        f"**unchanged:** {len(diff.unchanged)}"
    )
    parts.append("")
    for label, group in (
        ("Fixed", diff.fixed),
        ("Introduced", diff.introduced),
        ("Unchanged", diff.unchanged),
    ):
        parts.append(f"## {label}")
        if not group:
            parts.append("")
            parts.append("(none)")
            parts.append("")
            continue
        parts.append("")
        for v in group:
            parts.append(f"- `{v['rule_id']}` {v['file']}:{v['line']}: {v['message']}")
        parts.append("")
    return "\n".join(parts).rstrip() + "\n"


def render_json(diff: DiffReport) -> str:
    """Deterministic JSON output. Top-level keys: ``summary``
    (counts), ``fixed``, ``introduced``, ``unchanged``. Violations
    use the spec-001 shape verbatim."""
    payload = {
        "summary": {
            "fixed": len(diff.fixed),
            "introduced": len(diff.introduced),
            "unchanged": len(diff.unchanged),
        },
        "fixed": list(diff.fixed),
        "introduced": list(diff.introduced),
        "unchanged": list(diff.unchanged),
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"
