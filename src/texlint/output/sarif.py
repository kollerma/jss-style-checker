"""Deterministic SARIF 2.1.0 renderer for :class:`texlint.api.ComplianceReport`.

The output contract is documented in
``specs/006-sarif-output/contracts/sarif-output.md``.

* the document is a single ``runs[0]`` SARIF log;
* every catalogue rule appears in ``runs[0].tool.driver.rules``,
  whether or not it produced a violation;
* :class:`Severity` maps to SARIF ``level`` per
  ``error -> error``, ``warning -> warning``, ``info -> note``;
* :data:`JSS_PARSE_RULE_ID` violations are emitted as
  ``runs[0].invocations[0].toolExecutionNotifications`` entries —
  not as results;
* paths are relativised against ``cfg.source_root`` and rendered as
  POSIX-style strings, so the output is host-independent.
* arrays are pre-sorted before serialisation; the document is
  byte-deterministic across Python implementations.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

from texlint import __version__
from texlint.api import ComplianceReport, Fix, Severity, ToolConfig, Violation

JSS_PARSE_RULE_ID = "JSS-PARSE-000"

_INFORMATION_URI = "https://github.com/kollerma/jss-style-checker"
_SCHEMA_URI = "https://json.schemastore.org/sarif-2.1.0.json"

_SARIF_LEVEL: dict[Severity, str] = {
    Severity.ERROR: "error",
    Severity.WARNING: "warning",
    Severity.INFO: "note",
}


def _relativise(file: Path, source_root: Path) -> str:
    """Render *file* as a POSIX-style relative path against *source_root*.

    Paths inside the source root use :meth:`Path.relative_to` directly;
    paths outside the source root fall back to :func:`os.path.relpath`,
    which yields a path with leading ``..`` segments. Output never
    contains drive letters or ``\\`` separators.
    """
    abs_file = file.resolve() if file.is_absolute() else (source_root / file).resolve()
    abs_root = source_root.resolve()
    try:
        rel = abs_file.relative_to(abs_root)
    except ValueError:
        rel = Path(os.path.relpath(abs_file, abs_root))
    return rel.as_posix()


def _location(violation: Violation, source_root: Path) -> dict[str, Any]:
    region: dict[str, Any] = {
        "startLine": violation.line,
    }
    if violation.column is not None:
        region["startColumn"] = violation.column
    return {
        "physicalLocation": {
            "artifactLocation": {"uri": _relativise(violation.file, source_root)},
            "region": region,
        }
    }


def _result(violation: Violation, source_root: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "ruleId": violation.rule_id,
        "level": _SARIF_LEVEL[violation.severity],
        "message": {"text": violation.message},
        "locations": [_location(violation, source_root)],
    }
    # Spec 008 §7: project structured Fix payloads as SARIF
    # ``fixes[]``. ``FixSuggestion`` (the legacy reserved type) carries
    # no byte-range data and is intentionally excluded; the key is
    # OMITTED entirely when the violation has no fix, mirroring spec
    # 006's policy of not emitting absent fields.
    if isinstance(violation.fix, Fix):
        fix = violation.fix
        result["fixes"] = [
            {
                "description": {"text": fix.description},
                "artifactChanges": [
                    {
                        "artifactLocation": {
                            "uri": _relativise(violation.file, source_root)
                        },
                        "replacements": [
                            {
                                "deletedRegion": {
                                    "byteOffset": fix.start,
                                    "byteLength": fix.end - fix.start,
                                },
                                "insertedContent": {"text": fix.replacement},
                            }
                        ],
                    }
                ],
            }
        ]
    return result


def _notification(violation: Violation, source_root: Path) -> dict[str, Any]:
    """Project a parse-failure violation to a SARIF notification entry.

    Notifications live under
    ``runs[0].invocations[0].toolExecutionNotifications`` because they
    describe a tool-execution event (the parser could not analyse the
    file) rather than a finding within a successfully analysed file.
    The level is always ``"error"``.
    """
    return {
        "descriptor": {"id": JSS_PARSE_RULE_ID},
        "level": "error",
        "message": {"text": violation.message},
        "locations": [_location(violation, source_root)],
    }


def _rule_descriptor(rule_id: str, meta: dict[str, Any]) -> dict[str, Any]:
    """Project a catalogue entry to a SARIF rule descriptor.

    Required catalogue keys: ``category``, ``severity``,
    ``message_template``. Optional keys: ``guide_section`` and
    ``guide_url`` (spec 007). The descriptor's ``properties.tags``
    carries the rule's category as a single-element list — the
    SARIF-blessed surface for tool-internal labels (spec 006 §4).
    """
    severity = meta["severity"]
    category = meta["category"]
    message = meta["message_template"]
    guide_section = meta.get("guide_section") or ""
    guide_url = meta.get("guide_url")

    short_text = (
        f"{message} ({guide_section})"
        if guide_section and guide_section != "internal"
        else message
    )
    descriptor: dict[str, Any] = {
        "id": rule_id,
        "name": rule_id,
        "shortDescription": {"text": short_text},
        "fullDescription": {"text": message},
        "defaultConfiguration": {"level": _SARIF_LEVEL[severity]},
        "properties": {"tags": [category]},
    }
    if guide_url:
        descriptor["helpUri"] = guide_url
    return descriptor


def _catalogue_rules() -> list[dict[str, Any]]:
    """Build the ``tool.driver.rules`` array from every active catalogue
    entry, sorted by id ascending."""
    # Spec 006 plan: pull rule metadata from _catalogue_data.RULES so
    # every rule definition appears in tool.driver.rules, not only rules
    # with hits. The catalogue is JSS-specific in the current codebase;
    # other journals would import their own catalogue here when SARIF
    # output is requested for them.
    from texlint.journals.jss._catalogue_data import RULES

    rules = [_rule_descriptor(rid, dict(meta)) for rid, meta in RULES.items()]
    rules.append(_internal_parse_rule_descriptor())
    rules.sort(key=lambda r: r["id"])
    return rules


def _internal_parse_rule_descriptor() -> dict[str, Any]:
    """The synthetic JSS-PARSE-000 rule descriptor.

    Parse failures are reported as notifications, not results, but the
    rule still appears under ``tool.driver.rules`` so downstream
    SARIF consumers can render its name in their UI.
    """
    return {
        "id": JSS_PARSE_RULE_ID,
        "name": JSS_PARSE_RULE_ID,
        "shortDescription": {"text": "Parser failed to process the input file."},
        "fullDescription": {
            "text": (
                "Emitted when the parser could not analyse a file. "
                "The file is reported under "
                "runs[0].invocations[0].toolExecutionNotifications "
                "rather than runs[0].results."
            )
        },
        "defaultConfiguration": {"level": "error"},
        "properties": {"tags": ["parse"]},
    }


def _violation_sort_key(v: Violation) -> tuple[str, int, int, str]:
    return (v.file.as_posix(), v.line, v.column or 0, v.rule_id)


def to_payload(report: ComplianceReport, cfg: ToolConfig) -> dict[str, Any]:
    """Build the full SARIF document as a nested ``dict``.

    Pure function: same ``(report, cfg)`` produces the same dict, byte-
    identical after :func:`json.dumps` with ``sort_keys=True``.
    """
    source_root = cfg.source_root

    parse_failures: list[Violation] = []
    other_violations: list[Violation] = []
    for v in report.violations:
        if v.rule_id == JSS_PARSE_RULE_ID:
            parse_failures.append(v)
        else:
            other_violations.append(v)

    parse_failures.sort(key=_violation_sort_key)
    other_violations.sort(key=_violation_sort_key)

    results = [_result(v, source_root) for v in other_violations]
    notifications = [_notification(v, source_root) for v in parse_failures]

    return {
        "$schema": _SCHEMA_URI,
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "jss-lint",
                        "version": __version__,
                        "informationUri": _INFORMATION_URI,
                        "rules": _catalogue_rules(),
                    }
                },
                "invocations": [
                    {
                        "executionSuccessful": True,
                        "toolExecutionNotifications": notifications,
                    }
                ],
                "results": results,
            }
        ],
    }


def render(report: ComplianceReport, cfg: ToolConfig) -> None:
    payload = to_payload(report, cfg)
    sys.stdout.write(json.dumps(payload, indent=2, sort_keys=True))
    sys.stdout.write("\n")
