"""Unit tests for JSS-BIB-001 — every bib entry must have a ``year`` field."""

from __future__ import annotations

from pathlib import Path

from texlint.api import ParsedDocument, ParsedTexFile, ToolConfig
from texlint.journals.jss.rules.bib_001_year import rule as bib_001


class TestFiresOnMissingYear:
    def test_entry_without_year_flags(self, run_rule):
        src = "@article{smith2020,\n  title = {A},\n  author = {B},\n}\n"
        violations = run_rule(bib_001, src, kind="bib")
        assert len(violations) == 1
        v = violations[0]
        assert v.rule_id == "JSS-BIB-001"
        assert v.line == 1  # entry start (1-based)
        assert v.column is None

    def test_multiple_entries_each_missing_year_each_flagged(self, run_rule):
        src = (
            "@article{a2020,\n  title = {A},\n}\n"
            "@article{b2021,\n  title = {B},\n}\n"
        )
        violations = run_rule(bib_001, src, kind="bib")
        assert len(violations) == 2


class TestDoesNotFireWhenYearPresent:
    def test_entry_with_year_passes(self, run_rule):
        src = (
            "@article{smith2020,\n"
            "  title = {A Study},\n"
            "  author = {Smith, J.},\n"
            "  year = {2020},\n"
            "}\n"
        )
        violations = run_rule(bib_001, src, kind="bib")
        assert violations == []

    def test_mixed_entries_only_missing_one_flagged(self, run_rule):
        src = (
            "@article{withyear,\n  year = {2020},\n}\n"
            "@article{withoutyear,\n  title = {T},\n}\n"
        )
        violations = run_rule(bib_001, src, kind="bib")
        assert len(violations) == 1


class TestEmptyLibrary:
    def test_no_entries_no_violations(self, run_rule):
        violations = run_rule(bib_001, "", kind="bib")
        assert violations == []


class TestFormatsFilter:
    def test_only_applies_to_bib(self):
        assert bib_001.formats == frozenset({".bib"})

    def test_tex_only_document_yields_no_violations(self, tmp_path: Path):
        p = tmp_path / "x.tex"
        p.write_text("", encoding="utf-8")
        tex = ParsedTexFile(path=p, source="", nodes=(), walker=None, violations=())
        doc = ParsedDocument(tex_files=(tex,))
        assert list(bib_001.check(doc, ToolConfig())) == []


class TestParseErrorBib:
    def test_no_duplicate_violation_when_library_is_none(self, tmp_path: Path):
        from texlint.api import ParsedBibFile

        p = tmp_path / "broken.bib"
        p.write_text("", encoding="utf-8")
        bib = ParsedBibFile(path=p, source="", library=None, violations=())
        doc = ParsedDocument(bib_files=(bib,))
        assert list(bib_001.check(doc, ToolConfig())) == []

    def test_entry_without_fields_dict_is_skipped(self, tmp_path: Path):
        """If a library entry has no fields_dict attribute we must not crash."""
        from texlint.api import ParsedBibFile

        class FakeEntry:
            fields_dict = None  # type: ignore[assignment]
            start_line = 0
            key = "x"

        class FakeLibrary:
            entries = (FakeEntry(),)

        p = tmp_path / "x.bib"
        p.write_text("", encoding="utf-8")
        bib = ParsedBibFile(path=p, source="", library=FakeLibrary(), violations=())
        doc = ParsedDocument(bib_files=(bib,))
        assert list(bib_001.check(doc, ToolConfig())) == []
