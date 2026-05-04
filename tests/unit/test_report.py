"""Spec 015 — conformance report tests."""

from __future__ import annotations

from pathlib import Path

from texlint.api import ComplianceReport, Severity, Violation
from texlint.report import render_report


def _v(rule_id: str, severity: Severity = Severity.WARNING, line: int = 1) -> Violation:
    return Violation(
        file=Path("manuscript.tex"),
        line=line,
        column=1,
        rule_id=rule_id,
        severity=severity,
        message=f"violation of {rule_id}",
    )


def _report(violations: tuple[Violation, ...]) -> ComplianceReport:
    return ComplianceReport(
        tool_version="0.0.0-test",
        journal_id="jss",
        violations=violations,
        categories=(),
        compliance_percentage=None,
    )


class TestRenderReport:
    def test_clean_run_score_100(self) -> None:
        out = render_report(_report(()))
        assert "100 %" in out
        assert "Errors: 0" in out
        assert "(no violations)" in out

    def test_violations_drop_score(self) -> None:
        out = render_report(_report((_v("JSS-CITE-002"),)))
        # Score should be < 100 since at least one rule has a violation.
        assert "%" in out
        assert "100 %" not in out

    def test_top_five_present(self) -> None:
        # Mix of rules; one fires more than another.
        viols = (
            _v("JSS-CITE-002"),
            _v("JSS-CITE-002"),
            _v("JSS-CITE-002"),
            _v("JSS-MARKUP-001"),
        )
        out = render_report(_report(viols))
        assert "JSS-CITE-002" in out
        assert "JSS-MARKUP-001" in out

    def test_fix_me_first_orders_by_severity(self) -> None:
        # Use real catalogue rule ids; `_active_rules` filters to known rules.
        viols = (
            _v("JSS-CITE-002", Severity.WARNING),
            _v("JSS-PRE-001", Severity.ERROR),
        )
        out = render_report(_report(viols))
        fix_me = out.split("## Fix me first", 1)[1]
        # Errors come before warnings in fix-me-first.
        assert fix_me.index("`JSS-PRE-001`") < fix_me.index("`JSS-CITE-002`")

    def test_metadata_appears_in_header(self) -> None:
        out = render_report(_report(()), title="Foo", author="Bar")
        assert "JSS conformance report — Foo" in out
        assert "Author:** Bar" in out
