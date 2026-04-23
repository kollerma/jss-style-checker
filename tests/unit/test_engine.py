"""Unit tests for ``texlint.core.engine``."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pytest

from texlint.api import (
    CategoryStatus,
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
from texlint.core.engine import load_journal, run


def _v(
    *,
    file: str = "a.tex",
    line: int = 1,
    column: int | None = 1,
    rule_id: str = "JSS-X-001",
) -> Violation:
    return Violation(
        file=Path(file),
        line=line,
        column=column,
        rule_id=rule_id,
        severity=Severity.ERROR,
        message="msg",
    )


def _rule(rule_id: str, *, category: str = "x", fires_on: Iterable[str] = ()) -> Rule:
    fires = tuple(fires_on)

    def _check(doc, cfg):
        for tex in doc.tex_files:
            if str(tex.path) in fires:
                yield _v(file=str(tex.path), rule_id=rule_id)

    return Rule(
        id=rule_id,
        category=category,
        severity=Severity.ERROR,
        message_template="",
        authority="",
        check=_check,
        formats=frozenset({".tex"}),
    )


class _Journal(JournalRuleModule):
    def __init__(self, id_: str, categories: tuple[RuleCategory, ...]):
        self._id = id_
        self._categories = categories

    @property
    def id(self) -> str:  # type: ignore[override]
        return self._id

    def categories(self):
        return self._categories


def _make_doc(tmp_path: Path, *names: str) -> ParsedDocument:
    tex_files = []
    for n in names:
        p = tmp_path / n
        p.write_text("", encoding="utf-8")
        tex_files.append(
            ParsedTexFile(path=p, source="", nodes=(), walker=None, violations=())
        )
    return ParsedDocument(tex_files=tuple(tex_files))


class TestLoadJournal:
    def test_loads_registered_journal(self):
        # 'jss' is registered via entry points in pyproject.toml.
        journal = load_journal("jss")
        assert journal.id == "jss"

    def test_missing_raises_journal_not_found(self):
        with pytest.raises(JournalNotFoundError):
            load_journal("does-not-exist-journal-xyz")

    def test_non_module_subclass_raises_invalid(self, monkeypatch):
        import importlib.metadata as im

        class FakeEP:
            name = "fake"
            value = "fake:obj"

            def load(self):
                return {"not": "a journal"}

        class FakeEPs(list):
            def select(self, *, name):
                return [ep for ep in self if ep.name == name]

        monkeypatch.setattr(
            im,
            "entry_points",
            lambda group: FakeEPs([FakeEP()]) if group == "texlint.journals" else [],
        )
        with pytest.raises(InvalidJournalError):
            load_journal("fake")


class TestRunEmpty:
    def test_no_rules_no_violations_percentage_none(self, tmp_path: Path):
        journal = _Journal("j", ())
        doc = _make_doc(tmp_path, "a.tex")
        report = run(ToolConfig(), doc, journal)
        assert report.violations == ()
        assert report.categories == ()
        assert report.compliance_percentage is None


class TestRunPass:
    def test_single_category_no_violations_is_pass_100(self, tmp_path: Path):
        rule = _rule("JSS-X-001")
        journal = _Journal("j", (RuleCategory(id="x", title="X", rules=(rule,)),))
        doc = _make_doc(tmp_path, "a.tex")
        report = run(ToolConfig(), doc, journal)
        assert len(report.categories) == 1
        assert report.categories[0].status == CategoryStatus.PASS
        assert report.compliance_percentage == 100.0


class TestRunFail:
    def test_single_violation_fails_category_and_zero_percent(self, tmp_path: Path):
        doc = _make_doc(tmp_path, "a.tex")
        tex = doc.tex_files[0]
        rule = _rule("JSS-X-001", fires_on=(str(tex.path),))
        journal = _Journal("j", (RuleCategory(id="x", title="X", rules=(rule,)),))
        report = run(ToolConfig(), doc, journal)
        assert report.categories[0].status == CategoryStatus.FAIL
        assert report.compliance_percentage == 0.0
        assert len(report.violations) == 1


class TestRunSkipped:
    def test_all_rules_in_category_ignored_skipped_and_excluded(self, tmp_path: Path):
        rule_a = _rule("JSS-A-001", category="a")
        rule_b = _rule("JSS-B-001", category="b")
        doc = _make_doc(tmp_path, "a.tex")
        tex = doc.tex_files[0]
        rule_a = _rule("JSS-A-001", category="a", fires_on=(str(tex.path),))
        journal = _Journal(
            "j",
            (
                RuleCategory(id="a", title="A", rules=(rule_a,)),
                RuleCategory(id="b", title="B", rules=(rule_b,)),
            ),
        )
        cfg = ToolConfig(ignore_rules=frozenset({"JSS-A-001"}))
        report = run(cfg, doc, journal)
        status_by_id = {c.category_id: c.status for c in report.categories}
        assert status_by_id["a"] == CategoryStatus.SKIPPED
        assert status_by_id["b"] == CategoryStatus.PASS
        # Percentage excludes skipped: only 'b' counts, which is PASS.
        assert report.compliance_percentage == 100.0


class TestRunParseError:
    def test_parse_error_adds_synthetic_parse_category_excluded_from_percentage(
        self, tmp_path: Path
    ):
        rule = _rule("JSS-X-001")
        journal = _Journal("j", (RuleCategory(id="x", title="X", rules=(rule,)),))
        # Build a doc containing a pre-existing parse-error violation.
        p = tmp_path / "bad.tex"
        p.write_text("", encoding="utf-8")
        pe = Violation(
            file=p,
            line=1,
            column=None,
            rule_id="JSS-PARSE-000",
            severity=Severity.ERROR,
            message="synthetic parse error",
        )
        tex = ParsedTexFile(
            path=p, source="", nodes=(), walker=None, violations=(pe,)
        )
        doc = ParsedDocument(tex_files=(tex,))
        report = run(ToolConfig(), doc, journal)

        assert any(c.category_id == "parse" for c in report.categories)
        parse_cat = next(c for c in report.categories if c.category_id == "parse")
        assert parse_cat.status == CategoryStatus.FAIL
        # compliance_percentage excludes parse
        assert report.compliance_percentage == 100.0


class TestRunAllSkipped:
    def test_percentage_none_when_every_journal_category_skipped(self, tmp_path: Path):
        rule = _rule("JSS-X-001")
        journal = _Journal("j", (RuleCategory(id="x", title="X", rules=(rule,)),))
        doc = _make_doc(tmp_path, "a.tex")
        cfg = ToolConfig(ignore_rules=frozenset({"JSS-X-001"}))
        report = run(cfg, doc, journal)
        assert report.categories[0].status == CategoryStatus.SKIPPED
        assert report.compliance_percentage is None


class TestDeterministicOrdering:
    def test_violations_sorted_deterministically(self, tmp_path: Path):
        doc = _make_doc(tmp_path, "z.tex", "a.tex")
        tex_z, tex_a = doc.tex_files

        def _check(document, cfg):
            yield _v(file=str(tex_z.path), line=5, column=None, rule_id="JSS-Z-002")
            yield _v(file=str(tex_a.path), line=10, column=1, rule_id="JSS-Z-001")
            yield _v(file=str(tex_a.path), line=10, column=None, rule_id="JSS-Z-003")

        rule = Rule(
            id="JSS-Z-001",
            category="z",
            severity=Severity.ERROR,
            message_template="",
            authority="",
            check=_check,
            formats=frozenset({".tex"}),
        )
        journal = _Journal("j", (RuleCategory(id="z", title="Z", rules=(rule,)),))
        report = run(ToolConfig(), doc, journal)
        # Deterministic: by file, then line, then column (None first), then rule_id.
        keys = [(str(v.file), v.line, v.column, v.rule_id) for v in report.violations]
        assert keys == sorted(keys, key=lambda t: (t[0], t[1], (0, 0) if t[2] is None else (1, t[2]), t[3]))


class TestFormatsFilter:
    def test_tex_only_rule_skipped_on_bib_files(self, tmp_path: Path):
        bib_path = tmp_path / "x.bib"
        bib_path.write_text("", encoding="utf-8")
        doc = ParsedDocument(
            bib_files=(
                ParsedBibFile(path=bib_path, source="", library=None, violations=()),
            )
        )
        rule = _rule("JSS-X-001")  # formats={".tex"}
        journal = _Journal("j", (RuleCategory(id="x", title="X", rules=(rule,)),))
        report = run(ToolConfig(), doc, journal)
        # No files match -> category is SKIPPED
        assert report.categories[0].status == CategoryStatus.SKIPPED
