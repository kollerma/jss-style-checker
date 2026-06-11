"""Deterministic JSON renderer for :class:`texlint.api.ComplianceReport`.

The output contract is documented in
``specs/001-linter-foundation/contracts/json-output.md``:

* top-level keys: ``tool_version``, ``journal_id``, ``compliance_percentage``,
  ``categories``, ``violations``;
* every nested object has its keys alphabetised by ``sort_keys=True``;
* the ``violations`` array is sorted by ``Violation.sort_key``;
* paths are rendered via ``Path.as_posix()`` so that the output is identical
  on Windows and POSIX hosts.

Spec 007 follow-up — every violation entry now carries
``guide_section`` (string; ``""`` for tool-side rules) and
``guide_url`` (string or ``null``) so JSON consumers can deep-link
into the JSS author guide without re-querying the catalogue.
"""

from __future__ import annotations

import json
import sys
from typing import Any

from texlint.api import ComplianceReport, ToolConfig, Violation


def _catalogue() -> dict[str, dict[str, Any]]:
    """Look up the JSS rule catalogue lazily; cached on the function
    object. Returns ``{}`` when the journal isn't installed (defensive
    — the CLI loads the journal before reaching the renderer)."""
    cached = getattr(_catalogue, "_cache", None)
    if cached is None:
        try:
            from texlint.journals.jss._catalogue_data import RULES
        except ImportError:  # pragma: no cover - journal absent
            cached = {}
        else:
            cached = {rid: dict(meta) for rid, meta in RULES.items()}
        _catalogue._cache = cached  # type: ignore[attr-defined]
    return cached


def _violation_dict(v: Violation) -> dict[str, Any]:
    meta = _catalogue().get(v.rule_id, {})
    return {
        "file": v.file.as_posix(),
        "line": v.line,
        "column": v.column,
        "rule_id": v.rule_id,
        "severity": v.severity.value,
        "message": v.message,
        "suggestion": v.suggestion,
        "fix": None,  # reserved for Step 4
        # Spec 007 follow-up — citation surface per violation.
        "guide_section": meta.get("guide_section") or "",
        "guide_url": meta.get("guide_url"),
        # Measured-precision confidence tier of the originating rule
        # ("high" / "medium" / "low"); "high" for tool-side rules and
        # rules without a narrowed tier in the catalogue.
        "confidence": meta.get("confidence", "high"),
    }


def _category_dict(c) -> dict[str, Any]:
    return {
        "category_id": c.category_id,
        "title": c.title,
        "status": c.status.value,
        "rules_applied": c.rules_applied,
        "rules_passed": c.rules_passed,
    }


def to_payload(report: ComplianceReport) -> dict[str, Any]:
    return {
        "tool_version": report.tool_version,
        "journal_id": report.journal_id,
        "compliance_percentage": report.compliance_percentage,
        "categories": [_category_dict(c) for c in report.categories],
        "violations": [_violation_dict(v) for v in report.violations],
        "skipped_rules": [
            {"rule_id": s.rule_id, "reason": s.reason}
            for s in report.skipped_rules
        ],
    }


def render(report: ComplianceReport, _config: ToolConfig) -> None:
    payload = to_payload(report)
    sys.stdout.write(json.dumps(payload, indent=2, sort_keys=True))
    sys.stdout.write("\n")
