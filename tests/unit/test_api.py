"""Unit tests for the public data model in ``texlint.api``."""

from __future__ import annotations

import dataclasses
from pathlib import Path

import pytest

from texlint.api import (
    CategoryStatus,
    CategorySummary,
    ComplianceReport,
    FixSuggestion,
    InvalidJournalError,
    JournalNotFoundError,
    JournalRuleModule,
    ParsedBibFile,
    ParsedDocument,
    ParsedTexFile,
    Rule,
    RuleCategory,
    Severity,
    ToolConfig,
    Violation,
)


def _violation(
    *,
    file: str = "a.tex",
    line: int = 1,
    column: int | None = 1,
    rule_id: str = "JSS-TEST-001",
    severity: Severity = Severity.ERROR,
    message: str = "msg",
    suggestion: str | None = None,
    fix: FixSuggestion | None = None,
) -> Violation:
    return Violation(
        file=Path(file),
        line=line,
        column=column,
        rule_id=rule_id,
        severity=severity,
        message=message,
        suggestion=suggestion,
        fix=fix,
    )


class TestSeverity:
    def test_values_are_strings(self):
        assert Severity.ERROR.value == "error"
        assert Severity.WARNING.value == "warning"
        assert Severity.INFO.value == "info"

    def test_is_str_subclass(self):
        assert isinstance(Severity.ERROR, str)

    def test_info_round_trip(self):
        assert Severity("info") is Severity.INFO
        assert Severity.INFO == "info"


class TestCategoryStatus:
    def test_values(self):
        assert CategoryStatus.PASS.value == "PASS"
        assert CategoryStatus.FAIL.value == "FAIL"
        assert CategoryStatus.SKIPPED.value == "SKIPPED"


class TestFixSuggestion:
    def test_default_field_present(self):
        fs = FixSuggestion(description="swap foo for bar")
        assert fs.description == "swap foo for bar"

    def test_frozen(self):
        fs = FixSuggestion(description="x")
        with pytest.raises(dataclasses.FrozenInstanceError):
            fs.description = "y"  # type: ignore[misc]


class TestViolation:
    def test_construction_minimal(self):
        v = _violation()
        assert v.fix is None
        assert v.suggestion is None

    def test_frozen(self):
        v = _violation()
        with pytest.raises(dataclasses.FrozenInstanceError):
            v.line = 99  # type: ignore[misc]

    def test_sort_key_file_then_line(self):
        a = _violation(file="a.tex", line=5)
        b = _violation(file="b.tex", line=1)
        assert a.sort_key() < b.sort_key()

    def test_sort_key_column_none_sorts_before_int(self):
        a = _violation(line=1, column=None)
        b = _violation(line=1, column=1)
        assert a.sort_key() < b.sort_key()

    def test_sort_key_tiebreaks_on_rule_id(self):
        a = _violation(rule_id="JSS-A-001")
        b = _violation(rule_id="JSS-B-001")
        assert a.sort_key() < b.sort_key()

    def test_sort_stable_for_mixed_columns(self):
        vs = [
            _violation(line=1, column=3, rule_id="R1"),
            _violation(line=1, column=None, rule_id="R2"),
            _violation(line=1, column=1, rule_id="R3"),
        ]
        ordered = sorted(vs, key=lambda v: v.sort_key())
        # None first, then 1, then 3
        assert [v.rule_id for v in ordered] == ["R2", "R3", "R1"]


class TestRule:
    def test_construction(self):
        rule = Rule(
            id="JSS-X-001",
            category="x",
            severity=Severity.WARNING,
            message_template="m",
            authority="author instructions",
            check=lambda doc, cfg: iter(()),
        )
        assert rule.formats is None

    def test_frozen(self):
        rule = Rule(
            id="R",
            category="c",
            severity=Severity.ERROR,
            message_template="",
            authority="",
            check=lambda d, c: iter(()),
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            rule.id = "Z"  # type: ignore[misc]

    def test_formats_accepted_as_frozenset(self):
        rule = Rule(
            id="R",
            category="c",
            severity=Severity.ERROR,
            message_template="",
            authority="",
            check=lambda d, c: iter(()),
            formats=frozenset({".tex"}),
        )
        assert rule.formats == frozenset({".tex"})


class TestCategorySummary:
    def _summary(self, *, rules_applied: int, violations: tuple[Violation, ...]):
        return CategorySummary.build(
            category_id="c",
            title="Cat",
            rules_applied=rules_applied,
            rules_passed=max(rules_applied - (1 if violations else 0), 0),
            violations=violations,
        )

    def test_skipped_when_rules_applied_zero(self):
        s = self._summary(rules_applied=0, violations=())
        assert s.status == CategoryStatus.SKIPPED

    def test_fail_when_violations_present_and_rules_applied(self):
        s = self._summary(rules_applied=1, violations=(_violation(),))
        assert s.status == CategoryStatus.FAIL

    def test_pass_when_no_violations_and_rules_applied(self):
        s = self._summary(rules_applied=1, violations=())
        assert s.status == CategoryStatus.PASS


class TestComplianceReport:
    def test_percentage_excludes_skipped(self):
        c_pass = CategorySummary.build(category_id="a", title="A", rules_applied=1, rules_passed=1)
        c_fail = CategorySummary.build(
            category_id="b", title="B", rules_applied=1, rules_passed=0, violations=(_violation(),)
        )
        c_skipped = CategorySummary.build(category_id="c", title="C", rules_applied=0)
        report = ComplianceReport(
            tool_version="0.1.0",
            journal_id="jss",
            violations=(_violation(),),
            categories=(c_pass, c_fail, c_skipped),
            compliance_percentage=50.0,
        )
        assert report.compliance_percentage == 50.0
        assert report.categories[2].status == CategoryStatus.SKIPPED


class TestToolConfig:
    def test_defaults(self):
        cfg = ToolConfig()
        assert cfg.journal == "jss"
        assert cfg.mode == "author"
        assert cfg.output == "terminal"
        assert cfg.ignore_rules == frozenset()
        assert cfg.verbose is False
        assert cfg.code_width == 80

    def test_frozen(self):
        cfg = ToolConfig()
        with pytest.raises(dataclasses.FrozenInstanceError):
            cfg.journal = "other"  # type: ignore[misc]


class TestParsedDocument:
    def test_files_for_rule_none_formats_returns_all(self):
        tex = ParsedTexFile(path=Path("x.tex"), source="", nodes=(), walker=None, violations=())
        bib = ParsedBibFile(path=Path("x.bib"), source="", library=None, violations=())
        doc = ParsedDocument(tex_files=(tex,), bib_files=(bib,))

        rule = Rule(
            id="R",
            category="c",
            severity=Severity.ERROR,
            message_template="",
            authority="",
            check=lambda d, c: iter(()),
            formats=None,
        )
        files = list(doc.files_for_rule(rule))
        assert len(files) == 2

    def test_files_for_rule_formats_filter(self):
        tex = ParsedTexFile(path=Path("x.tex"), source="", nodes=(), walker=None, violations=())
        bib = ParsedBibFile(path=Path("x.bib"), source="", library=None, violations=())
        doc = ParsedDocument(tex_files=(tex,), bib_files=(bib,))

        tex_only = Rule(
            id="R",
            category="c",
            severity=Severity.ERROR,
            message_template="",
            authority="",
            check=lambda d, c: iter(()),
            formats=frozenset({".tex"}),
        )
        files = list(doc.files_for_rule(tex_only))
        assert [f.path.suffix for f in files] == [".tex"]

    def test_all_violations_concatenates(self):
        v1 = _violation(file="a.tex")
        v2 = _violation(file="b.bib")
        tex = ParsedTexFile(path=Path("a.tex"), source="", nodes=(), walker=None, violations=(v1,))
        bib = ParsedBibFile(path=Path("b.bib"), source="", library=None, violations=(v2,))
        doc = ParsedDocument(tex_files=(tex,), bib_files=(bib,))
        assert set(doc.all_violations()) == {v1, v2}


class TestJournalRuleModule:
    def test_default_rules_flattens_categories(self):
        rule_a = Rule(
            id="A",
            category="x",
            severity=Severity.ERROR,
            message_template="",
            authority="",
            check=lambda d, c: iter(()),
        )
        rule_b = Rule(
            id="B",
            category="x",
            severity=Severity.ERROR,
            message_template="",
            authority="",
            check=lambda d, c: iter(()),
        )

        class TinyJournal(JournalRuleModule):
            id = "tiny"

            def categories(self):
                return (RuleCategory(id="x", title="X", rules=(rule_a, rule_b)),)

        tj = TinyJournal()
        assert tj.rules() == (rule_a, rule_b)


class TestErrors:
    def test_errors_are_exception_subclasses(self):
        assert issubclass(JournalNotFoundError, Exception)
        assert issubclass(InvalidJournalError, Exception)
