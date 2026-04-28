"""Tests for JSS naming rules — 100% branch coverage target."""

from __future__ import annotations

from pathlib import Path

from texlint.api import (
    ParsedBibFile,
    ParsedDocument,
    ParsedTexFile,
    Severity,
    ToolConfig,
)
from texlint.journals.jss.rules.naming import (
    check_jss_name_001,
    check_jss_name_002,
    jss_name_001,
    jss_name_002,
    rules,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "violations" / "naming"


def _tex(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def _bib(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_rules_tuple_has_two_rules():
    assert len(rules) == 2


def test_rules_tuple_ids():
    assert {r.id for r in rules} == {"JSS-NAME-001", "JSS-NAME-002"}


# ---------------------------------------------------------------------------
# JSS-NAME-001 — language canonical capitalisation
# ---------------------------------------------------------------------------


class TestName001:
    def test_positive(self, run_rule):
        violations = run_rule(jss_name_001, _tex("JSS-NAME-001-bad.tex"))
        # 'JAVA' and 'matlab' → 2 hits
        assert len(violations) == 2
        assert all(v.severity == Severity.WARNING for v in violations)

    def test_good_silent(self, run_rule):
        assert run_rule(jss_name_001, _tex("JSS-NAME-001-good.tex")) == []

    def test_already_canonical_silent(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"We wrote code in Java." "\n"
            r"\end{document}"
        )
        # 'Java' already canonical → no flag.
        assert run_rule(jss_name_001, src) == []

    def test_skip_inside_code(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"Use \code{matlab} in shell." "\n"
            r"\end{document}"
        )
        assert run_rule(jss_name_001, src) == []


# ---------------------------------------------------------------------------
# JSS-NAME-002 — BibTeX publisher / journal canonical
# ---------------------------------------------------------------------------


class TestName002:
    def test_positive(self, run_rule):
        violations = run_rule(
            jss_name_002, _bib("JSS-NAME-002-bad.bib"), kind="bib"
        )
        assert len(violations) == 1
        assert violations[0].severity == Severity.WARNING

    def test_good_silent(self, run_rule):
        assert (
            run_rule(jss_name_002, _bib("JSS-NAME-002-good.bib"), kind="bib")
            == []
        )

    def test_journal_canonical(self, run_rule):
        src = (
            "@article{x,\n"
            "  author  = {Doe},\n"
            "  title   = {T},\n"
            "  journal = {JASA},\n"
            "  year    = {2020}\n"
            "}\n"
        )
        violations = run_rule(jss_name_002, src, kind="bib")
        assert len(violations) == 1

    def test_both_publisher_and_journal_flagged(self, run_rule):
        src = (
            "@article{x,\n"
            "  author    = {Doe},\n"
            "  title     = {T},\n"
            "  journal   = {JASA},\n"
            "  publisher = {Springer},\n"
            "  year      = {2020}\n"
            "}\n"
        )
        violations = run_rule(jss_name_002, src, kind="bib")
        assert len(violations) == 2

    def test_missing_publisher_silent(self, run_rule):
        src = "@article{x, title={T}, year={2020}}\n"
        assert run_rule(jss_name_002, src, kind="bib") == []

    def test_library_none_silent(self, tmp_path: Path):
        broken = ParsedBibFile(
            path=tmp_path / "b.bib", source="", library=None, violations=()
        )
        doc = ParsedDocument(bib_files=(broken,))
        assert list(check_jss_name_002(doc, ToolConfig())) == []


def test_name_001_empty_tex_silent():
    tex = ParsedTexFile(path=Path("/tmp/x.tex"), source="", nodes=(), walker=None)
    doc = ParsedDocument(tex_files=(tex,))
    assert list(check_jss_name_001(doc, ToolConfig())) == []
