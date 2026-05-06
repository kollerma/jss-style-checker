"""Spec 015 follow-up — HTML rendering of the conformance report."""

from __future__ import annotations

from pathlib import Path

import pytest

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


class TestHtmlReport:
    def test_html_basic_shape(self) -> None:
        out = render_report(_report(()), fmt="html", title="Foo")
        # Must look like an HTML document and carry the expected scaffolding.
        assert out.lstrip().lower().startswith("<!doctype html>")
        assert "<html" in out.lower()
        assert "<h1>" in out
        assert "Foo" in out
        # Clean run -> 100 % score, matching the markdown form.
        assert "100 %" in out

    def test_html_top_five_table(self) -> None:
        viols = (
            _v("JSS-CITE-002"),
            _v("JSS-CITE-002"),
            _v("JSS-MARKUP-001"),
        )
        out = render_report(_report(viols), fmt="html")
        assert "<table>" in out
        assert "JSS-CITE-002" in out
        assert "JSS-MARKUP-001" in out

    def test_html_score_under_100(self) -> None:
        out = render_report(_report((_v("JSS-CITE-002"),)), fmt="html")
        assert "%" in out
        assert "100 %" not in out

    def test_html_metadata_pass_through(self) -> None:
        out = render_report(
            _report(()),
            fmt="html",
            title="Foo",
            author="Bar",
        )
        assert "Foo" in out
        assert "Bar" in out

    def test_pdf_returns_bytes_when_weasyprint_available(self) -> None:
        """Spec 015 follow-up — fmt='pdf' is supported via the
        optional [pdf] extra. Skipped on environments without
        WeasyPrint (e.g. the GitHub Actions matrix); when present
        (dev container, ``pip install jss-lint[pdf]``), the call
        returns PDF bytes."""
        pytest.importorskip("weasyprint")
        out = render_report(_report(()), fmt="pdf")
        assert isinstance(out, bytes)
        assert out.startswith(b"%PDF-")
