"""Spec 008 follow-up: SARIF ``runs[].results[].fixes[]`` projection.

These tests pin the contract from spec 008 data-model §7:

* a result entry whose backing ``Violation.fix`` is ``None`` MUST
  omit the ``fixes`` key entirely (no empty list);
* a result entry whose backing ``Violation.fix`` is a
  :class:`texlint.api.Fix` MUST gain a ``fixes`` array carrying the
  rule-author-supplied description, the relativised artifact URI,
  and a single replacement with byte-offset / byte-length /
  inserted text.

We exercise :func:`texlint.output.sarif.to_payload` directly with
hand-built :class:`ComplianceReport` values so the test does not
depend on any catalogue rule actually emitting ``Fix`` payloads
yet (spec 008 baseline migrations are tracked separately under
``roadmap/follow-ups.md``).
"""

from __future__ import annotations

from pathlib import Path

from texlint.api import (
    CategorySummary,
    ComplianceReport,
    Fix,
    Severity,
    ToolConfig,
    Violation,
)
from texlint.output.sarif import to_payload


def _find_result(payload: dict, rule_id: str) -> dict:
    results = [
        r for r in payload["runs"][0]["results"] if r["ruleId"] == rule_id
    ]
    assert len(results) == 1, f"expected exactly one {rule_id} result, got {results!r}"
    return results[0]


def _report_with_violation(violation: Violation) -> ComplianceReport:
    return ComplianceReport(
        tool_version="0.0.0-test",
        journal_id="jss",
        violations=(violation,),
        categories=(
            CategorySummary.build(
                category_id="TEST",
                title="Test category",
                rules_applied=1,
                rules_passed=0,
                violations=(violation,),
            ),
        ),
        compliance_percentage=0.0,
    )


def test_violation_without_fix_omits_fixes_key(tmp_path: Path) -> None:
    """Violations without a ``Fix`` MUST NOT emit a ``fixes`` key.

    Spec 008 §7: ``fixes`` is OMITTED (not ``[]``) when the
    violation has no fix.
    """
    target = tmp_path / "manuscript.tex"
    target.write_text("\\documentclass{article}\n", encoding="utf-8")

    violation = Violation(
        file=target,
        line=1,
        column=1,
        rule_id="JSS-TEST-NOFIX",
        severity=Severity.WARNING,
        message="example violation without a fix",
        fix=None,
    )
    cfg = ToolConfig(source_root=tmp_path)
    payload = to_payload(_report_with_violation(violation), cfg)

    result = _find_result(payload, "JSS-TEST-NOFIX")
    assert "fixes" not in result, f"expected fixes key to be absent, got {result!r}"


def test_violation_with_fix_emits_fixes_array(tmp_path: Path) -> None:
    """Violations whose ``fix`` is a :class:`Fix` MUST gain ``fixes[]``.

    The shape mirrors SARIF 2.1.0 §3.55 ``fix`` /
    §3.56 ``replacement`` / §3.57 ``artifactChange``.
    """
    target = tmp_path / "manuscript.tex"
    target.write_text("hello world\n", encoding="utf-8")

    fix = Fix(start=0, end=5, replacement="JSS", description="rename")
    violation = Violation(
        file=target,
        line=1,
        column=1,
        rule_id="JSS-TEST-FIXED",
        severity=Severity.WARNING,
        message="example violation with a fix",
        fix=fix,
    )
    cfg = ToolConfig(source_root=tmp_path)
    payload = to_payload(_report_with_violation(violation), cfg)

    result = _find_result(payload, "JSS-TEST-FIXED")
    assert "fixes" in result
    fixes = result["fixes"]
    assert isinstance(fixes, list)
    assert len(fixes) == 1
    assert fixes[0]["description"]["text"] == "rename"

    changes = fixes[0]["artifactChanges"]
    assert len(changes) == 1
    assert changes[0]["artifactLocation"]["uri"] == "manuscript.tex"

    replacements = changes[0]["replacements"]
    assert len(replacements) == 1
    assert replacements[0]["deletedRegion"] == {"byteOffset": 0, "byteLength": 5}
    assert replacements[0]["insertedContent"]["text"] == "JSS"


def test_violation_with_empty_replacement_emits_pure_deletion(tmp_path: Path) -> None:
    """``Fix.replacement = ""`` is a valid pure-deletion edit.

    Pinned because the renderer must not collapse the empty string
    into ``None`` or omit the ``insertedContent`` key — SARIF
    consumers expect the field to be present even for deletions.
    """
    target = tmp_path / "manuscript.tex"
    target.write_text("noisy   text\n", encoding="utf-8")

    fix = Fix(start=5, end=8, replacement="", description="collapse whitespace")
    violation = Violation(
        file=target,
        line=1,
        column=6,
        rule_id="JSS-TEST-DELETE",
        severity=Severity.INFO,
        message="example deletion fix",
        fix=fix,
    )
    cfg = ToolConfig(source_root=tmp_path)
    payload = to_payload(_report_with_violation(violation), cfg)

    result = _find_result(payload, "JSS-TEST-DELETE")
    replacement = result["fixes"][0]["artifactChanges"][0]["replacements"][0]
    assert replacement["deletedRegion"] == {"byteOffset": 5, "byteLength": 3}
    assert replacement["insertedContent"] == {"text": ""}


def test_fix_suggestion_legacy_type_does_not_emit_fixes(tmp_path: Path) -> None:
    """The legacy reserved :class:`FixSuggestion` carries no byte
    range and MUST NOT trigger the SARIF ``fixes[]`` projection.

    Only :class:`Fix` (spec 008) carries the data SARIF requires.
    """
    from texlint.api import FixSuggestion

    target = tmp_path / "manuscript.tex"
    target.write_text("hello\n", encoding="utf-8")

    violation = Violation(
        file=target,
        line=1,
        column=1,
        rule_id="JSS-TEST-LEGACY",
        severity=Severity.WARNING,
        message="example violation with a legacy suggestion",
        fix=FixSuggestion(description="legacy hint"),
    )
    cfg = ToolConfig(source_root=tmp_path)
    payload = to_payload(_report_with_violation(violation), cfg)

    result = _find_result(payload, "JSS-TEST-LEGACY")
    assert "fixes" not in result
