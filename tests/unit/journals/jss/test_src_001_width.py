"""Unit tests for JSS-SRC-001 — source lines must not exceed ``code_width`` (default 80)."""

from __future__ import annotations

from pathlib import Path

from texlint.api import ParsedDocument, ParsedTexFile, ToolConfig
from texlint.journals.jss.rules.src_001_width import rule as src_001


class TestLineWidth:
    def test_line_at_limit_does_not_flag(self, run_rule):
        src = (
            r"\documentclass{article}\begin{document}"
            + "\n"
            + ("x" * 80)
            + "\n"
            + r"\end{document}"
        )
        violations = run_rule(src_001, src)
        assert violations == []

    def test_line_over_limit_flags(self, run_rule):
        # 81 chars on line 2
        src = (
            r"\documentclass{article}\begin{document}"
            + "\n"
            + ("x" * 81)
            + "\n"
            + r"\end{document}"
        )
        violations = run_rule(src_001, src)
        assert len(violations) == 1
        assert violations[0].rule_id == "JSS-SRC-001"
        assert violations[0].line == 2
        assert violations[0].column == 81

    def test_many_long_lines_all_flagged(self, run_rule):
        src = (
            r"\documentclass{article}\begin{document}"
            + "\n"
            + "\n".join(["y" * 90] * 3)
            + "\n"
            + r"\end{document}"
        )
        violations = run_rule(src_001, src)
        assert len(violations) == 3
        assert {v.line for v in violations} == {2, 3, 4}


class TestConfigurable:
    def test_code_width_override(self, run_rule):
        src = "x" * 100 + "\n"
        # With default (80), this flags.
        assert len(run_rule(src_001, src)) == 1
        # With 100, this does not.
        assert run_rule(src_001, src, ToolConfig(code_width=100)) == []

    def test_code_width_strict_inequality(self, run_rule):
        # Line of length 100 does NOT flag at code_width=100 (strict greater-than).
        src = "x" * 100 + "\n"
        assert run_rule(src_001, src, ToolConfig(code_width=100)) == []
        # Line of length 101 DOES flag at code_width=100.
        src2 = "x" * 101 + "\n"
        assert len(run_rule(src_001, src2, ToolConfig(code_width=100))) == 1


class TestUnicodeCounting:
    def test_counts_code_points_not_bytes(self, run_rule):
        # Accented 'é' is multibyte in UTF-8 but one code point.
        src = ("é" * 80) + "\n"
        assert run_rule(src_001, src) == []


class TestEveryFormat:
    def test_applies_to_bib_files(self, run_rule):
        # No formats filter means .bib is also scanned.
        src = "% " + ("x" * 90) + "\n"
        assert len(run_rule(src_001, src, kind="bib")) == 1

    def test_formats_is_none(self):
        assert src_001.formats is None


class TestEmptyFile:
    def test_empty_source_no_violations(self, run_rule):
        assert run_rule(src_001, "") == []

    def test_no_trailing_newline(self, run_rule):
        # 81-char line with no trailing \n should still flag.
        src = "x" * 81
        violations = run_rule(src_001, src)
        assert len(violations) == 1
        assert violations[0].line == 1


class TestParsedFileWithEmptySource:
    def test_empty_source_string_no_violations(self, tmp_path: Path):
        # ParsedTexFile with source="" (decode-failure path) must not produce
        # a spurious line-width violation.
        p = tmp_path / "x.tex"
        p.write_text("", encoding="utf-8")
        tex = ParsedTexFile(path=p, source="", nodes=(), walker=None, violations=())
        doc = ParsedDocument(tex_files=(tex,))
        assert list(src_001.check(doc, ToolConfig())) == []
