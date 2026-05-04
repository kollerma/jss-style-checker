"""Spec 010 — init renderer tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from texlint.api import ComplianceReport, Severity, Violation
from texlint.init import InitRefusedError, run


def _empty_report() -> ComplianceReport:
    return ComplianceReport(
        tool_version="0.0.0-test",
        journal_id="jss",
        violations=(),
        categories=(),
        compliance_percentage=100.0,
    )


def _violations_report() -> ComplianceReport:
    vs = (
        Violation(
            file=Path("manuscript.tex"),
            line=1,
            column=1,
            rule_id="JSS-CITE-002",
            severity=Severity.WARNING,
            message="x",
        ),
        Violation(
            file=Path("manuscript.tex"),
            line=2,
            column=1,
            rule_id="JSS-MARKUP-001",
            severity=Severity.WARNING,
            message="y",
        ),
    )
    return ComplianceReport(
        tool_version="0.0.0-test",
        journal_id="jss",
        violations=vs,
        categories=(),
        compliance_percentage=50.0,
    )


class TestInitRun:
    def test_writes_config(self, tmp_path: Path) -> None:
        result = run(tmp_path, report=_empty_report())
        assert result.wrote is True
        cfg = (tmp_path / ".jss-lint.toml").read_text()
        assert 'journal = "jss"' in cfg
        assert "ignore_rules = [" in cfg

    def test_dry_run_does_not_write(self, tmp_path: Path) -> None:
        result = run(tmp_path, report=_empty_report(), dry_run=True)
        assert result.wrote is False
        assert not (tmp_path / ".jss-lint.toml").exists()
        assert "journal" in result.contents

    def test_refuses_overwrite_without_force(self, tmp_path: Path) -> None:
        (tmp_path / ".jss-lint.toml").write_text("# existing\n")
        with pytest.raises(InitRefusedError):
            run(tmp_path, report=_empty_report())
        # File is untouched.
        assert (tmp_path / ".jss-lint.toml").read_text() == "# existing\n"

    def test_force_overwrites(self, tmp_path: Path) -> None:
        (tmp_path / ".jss-lint.toml").write_text("# existing\n")
        run(tmp_path, report=_empty_report(), force=True)
        cfg = (tmp_path / ".jss-lint.toml").read_text()
        assert 'journal = "jss"' in cfg

    def test_threshold_validation(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError):
            run(tmp_path, report=_empty_report(), threshold=1.5)
        with pytest.raises(ValueError):
            run(tmp_path, report=_empty_report(), threshold=-0.1)

    def test_must_fix_count_reflects_distinct_rules(self, tmp_path: Path) -> None:
        result = run(tmp_path, report=_violations_report())
        assert result.must_fix_count == 2
        assert result.total_violations == 2
