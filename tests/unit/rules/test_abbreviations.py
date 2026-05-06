"""Tests for JSS abbreviations rule — 100% branch coverage target."""

from __future__ import annotations

from pathlib import Path

from texlint.api import ParsedDocument, ParsedTexFile, ToolConfig
from texlint.journals.jss.rules.abbreviations import (
    check_jss_abbr_001,
    jss_abbr_001,
    rules,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "violations" / "abbreviations"


def _tex(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_rules_tuple_has_one_rule():
    assert len(rules) == 1
    assert rules[0].id == "JSS-ABBR-001"


class TestAbbr001:
    def test_positive(self, run_rule):
        violations = run_rule(jss_abbr_001, _tex("JSS-ABBR-001-bad.tex"))
        assert len(violations) == 1
        assert violations[0].suggestion.startswith("Replace 'U.S.A.'")

    def test_good_silent(self, run_rule):
        assert run_rule(jss_abbr_001, _tex("JSS-ABBR-001-good.tex")) == []

    def test_single_letter_abbrev_silent(self, run_rule):
        # "J. Smith" — single letter with period is an initial, not an abbrev.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}J. Smith wrote this.\end{document}"
        )
        assert run_rule(jss_abbr_001, src) == []

    def test_skip_inside_code(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}See \code{U.S.A.} literally.\end{document}"
        )
        assert run_rule(jss_abbr_001, src) == []

    def test_lowercase_abbrev_silent(self, run_rule):
        # 'e.g.' / 'i.e.' are lowercase; the rule targets uppercase
        # initialisms (the catalogue's own description).
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}e.g., this example.\end{document}"
        )
        assert run_rule(jss_abbr_001, src) == []

    def test_longer_abbrev_flagged(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}The I.R.S. rules apply.\end{document}"
        )
        violations = run_rule(jss_abbr_001, src)
        assert len(violations) == 1

    def test_emits_safe_fix_payload(self, run_rule):
        violations = run_rule(jss_abbr_001, _tex("JSS-ABBR-001-bad.tex"))
        assert len(violations) == 1
        v = violations[0]
        assert v.fix is not None
        assert v.fix.replacement == "USA"
        assert v.fix.confidence == "safe"
        assert v.fix.end > v.fix.start


def test_empty_tex_silent():
    tex = ParsedTexFile(path=Path("/tmp/x.tex"), source="", nodes=(), walker=None)
    doc = ParsedDocument(tex_files=(tex,))
    assert list(check_jss_abbr_001(doc, ToolConfig())) == []
