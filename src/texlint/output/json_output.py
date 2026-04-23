"""Deterministic JSON renderer for :class:`texlint.api.ComplianceReport`.

The output contract is documented in
``specs/001-linter-foundation/contracts/json-output.md``:

* top-level keys: ``tool_version``, ``journal_id``, ``compliance_percentage``,
  ``categories``, ``violations``;
* every nested object has its keys alphabetised by ``sort_keys=True``;
* the ``violations`` array is sorted by ``Violation.sort_key``;
* paths are rendered via ``Path.as_posix()`` so that the output is identical
  on Windows and POSIX hosts.
"""

from __future__ import annotations

import json
import sys
from typing import Any

from texlint.api import ComplianceReport, ToolConfig, Violation


def _violation_dict(v: Violation) -> dict[str, Any]:
    return {
        "file": v.file.as_posix(),
        "line": v.line,
        "column": v.column,
        "rule_id": v.rule_id,
        "severity": v.severity.value,
        "message": v.message,
        "suggestion": v.suggestion,
        "fix": None,  # reserved for Step 4
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
    }


def render(report: ComplianceReport, _config: ToolConfig) -> None:
    payload = to_payload(report)
    sys.stdout.write(json.dumps(payload, indent=2, sort_keys=True))
    sys.stdout.write("\n")
