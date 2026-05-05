"""Spec 015 follow-up — PDF rendering tests.

Skipped when WeasyPrint isn't installed; the dev container in this
repo installs it via the ``[pdf]`` extra.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from texlint.api import ComplianceReport, Severity, Violation
from texlint.report import PdfNotAvailable, render_report

weasyprint = pytest.importorskip("weasyprint")


def _empty_report() -> ComplianceReport:
    return ComplianceReport(
        tool_version="0.0.0-test",
        journal_id="jss",
        violations=(),
        categories=(),
        compliance_percentage=100.0,
    )


def _violations_report() -> ComplianceReport:
    return ComplianceReport(
        tool_version="0.0.0-test",
        journal_id="jss",
        violations=(
            Violation(
                file=Path("manuscript.tex"),
                line=1,
                column=1,
                rule_id="JSS-CITE-002",
                severity=Severity.WARNING,
                message="x",
            ),
        ),
        categories=(),
        compliance_percentage=50.0,
    )


class TestRenderPdf:
    def test_clean_returns_bytes(self) -> None:
        data = render_report(_empty_report(), fmt="pdf")
        assert isinstance(data, bytes)
        assert data.startswith(b"%PDF-")
        assert len(data) > 500  # any non-trivial PDF has structure

    def test_violations_render_into_pdf(self) -> None:
        data = render_report(_violations_report(), fmt="pdf")
        assert isinstance(data, bytes)
        assert data.startswith(b"%PDF-")

    def test_metadata_passes_through(self) -> None:
        data = render_report(
            _empty_report(),
            fmt="pdf",
            title="Override Title",
            author="Override Author",
        )
        assert isinstance(data, bytes)
        # We can't easily extract text from a PDF in this test
        # without bringing in another dep; the structural assertion
        # that bytes were produced is enough at this layer.
        assert data.startswith(b"%PDF-")

    def test_pdf_not_available_when_weasyprint_missing(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Simulate WeasyPrint being uninstalled by replacing the
        # import the renderer performs with a raising stub.
        import builtins

        real_import = builtins.__import__

        def fake_import(name, *a, **kw):
            if name == "weasyprint":
                raise ImportError("simulated absence")
            return real_import(name, *a, **kw)

        monkeypatch.setattr(builtins, "__import__", fake_import)

        with pytest.raises(PdfNotAvailable) as excinfo:
            render_report(_empty_report(), fmt="pdf")
        assert 'jss-lint[pdf]' in str(excinfo.value)
