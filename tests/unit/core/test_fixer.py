"""Unit tests for the spec-008 auto-fix engine."""

from __future__ import annotations

import io
from pathlib import Path

from texlint.api import (
    ComplianceReport,
    Fix,
    Severity,
    Violation,
)
from texlint.core.fixer import _apply_to_text, _Candidate, _resolve_conflicts, apply_fixes


def _violation(file: Path, fix: Fix, rule_id: str = "TEST-001") -> Violation:
    return Violation(
        file=file,
        line=1,
        column=1,
        rule_id=rule_id,
        severity=Severity.WARNING,
        message="test",
        fix=fix,
    )


def _report(violations: tuple[Violation, ...]) -> ComplianceReport:
    return ComplianceReport(
        tool_version="0.0.0-test",
        journal_id="jss",
        violations=violations,
        categories=(),
        compliance_percentage=None,
    )


class TestApplyToText:
    def test_single_replacement(self) -> None:
        text = "Hello World"
        cand = _Candidate(
            Path("x"),
            Fix(start=6, end=11, replacement="JSS", description="hello -> JSS"),
            "R",
            line=1,
        )
        assert _apply_to_text(text, [cand]) == "Hello JSS"

    def test_multiple_in_reverse_order(self) -> None:
        text = "MASS provides foo and BAR provides bar."
        c1 = _Candidate(
            Path("x"),
            Fix(start=0, end=4, replacement="\\pkg{MASS}", description="wrap MASS"),
            "R1",
            line=1,
        )
        c2 = _Candidate(
            Path("x"),
            Fix(start=22, end=25, replacement="\\pkg{BAR}", description="wrap BAR"),
            "R2",
            line=1,
        )
        result = _apply_to_text(text, [c1, c2])
        assert result == "\\pkg{MASS} provides foo and \\pkg{BAR} provides bar."


class TestConflictResolution:
    def test_disjoint_ranges_all_apply(self) -> None:
        c1 = _Candidate(Path("x"), Fix(0, 5, "a", description="d1"), "R1", 1)
        c2 = _Candidate(Path("x"), Fix(10, 15, "b", description="d2"), "R2", 1)
        applied, skipped = _resolve_conflicts([c1, c2])
        assert len(applied) == 2
        assert skipped == []

    def test_overlap_safe_beats_review(self) -> None:
        c_review = _Candidate(
            Path("x"),
            Fix(0, 10, "review", description="d-review", confidence="review"),
            "R-review",
            1,
        )
        c_safe = _Candidate(
            Path("x"),
            Fix(5, 15, "safe", description="d-safe", confidence="safe"),
            "R-safe",
            1,
        )
        applied, skipped = _resolve_conflicts([c_review, c_safe])
        assert len(applied) == 1
        assert applied[0].rule_id == "R-safe"
        assert len(skipped) == 1
        assert skipped[0].reason == "conflict"

    def test_overlap_lex_tiebreaker(self) -> None:
        c1 = _Candidate(Path("x"), Fix(0, 5, "a", description="d1"), "R-001", 1)
        c2 = _Candidate(Path("x"), Fix(2, 7, "b", description="d2b"), "R-002", 1)
        applied, _ = _resolve_conflicts([c1, c2])
        # Same confidence, different rule_id; R-001 < R-002.
        assert applied[0].rule_id == "R-001"


class TestApplyFixes:
    def test_dry_run_does_not_write(self, tmp_path: Path) -> None:
        target = tmp_path / "manuscript.tex"
        target.write_text("Hello World", encoding="utf-8")
        violation = _violation(
            target,
            Fix(start=6, end=11, replacement="JSS", description="hello -> JSS"),
            "JSS-TEST-001",
        )
        report = _report((violation,))

        out = io.StringIO()
        result = apply_fixes(report, mode="dry-run", stdout=out)
        # File untouched.
        assert target.read_text(encoding="utf-8") == "Hello World"
        # Diff printed.
        assert "Hello World" in out.getvalue()
        assert "Hello JSS" in out.getvalue()
        assert len(result.applied) == 1
        assert result.rejected == ()

    def test_write_applies_fix_atomically(self, tmp_path: Path) -> None:
        target = tmp_path / "manuscript.tex"
        target.write_text("Hello World", encoding="utf-8")
        violation = _violation(
            target,
            Fix(start=6, end=11, replacement="JSS", description="hello -> JSS"),
            "JSS-TEST-001",
        )
        report = _report((violation,))
        result = apply_fixes(report, mode="write")
        assert target.read_text(encoding="utf-8") == "Hello JSS"
        # No leftover tempfile.
        assert sorted(p.name for p in tmp_path.iterdir()) == ["manuscript.tex"]
        assert len(result.applied) == 1

    def test_fix_rule_filter(self, tmp_path: Path) -> None:
        target = tmp_path / "manuscript.tex"
        target.write_text("foo bar baz", encoding="utf-8")
        v1 = _violation(target, Fix(0, 3, "FOO", description="upcase foo"), "JSS-A-001")
        v2 = _violation(target, Fix(8, 11, "BAZ", description="upcase baz"), "JSS-B-001")
        report = _report((v1, v2))

        out = io.StringIO()
        result = apply_fixes(
            report, mode="dry-run", rules=frozenset({"JSS-A-001"}), stdout=out
        )
        # Only v1 was eligible.
        assert len(result.applied) == 1
        assert result.applied[0].rule_id == "JSS-A-001"
        assert any(s.reason == "rule-not-selected" for s in result.skipped)
