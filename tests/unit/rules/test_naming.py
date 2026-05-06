"""Tests for JSS naming rules — 100% branch coverage target."""

from __future__ import annotations

from pathlib import Path

from texlint.api import (
    Fix,
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

    def test_emits_safe_fix_payload(self, run_rule):
        """Spec 008 follow-up: each violation carries a Fix(...)
        payload whose byte range covers the offending token and
        whose replacement is the canonical capitalisation."""
        autofix_dir = REPO_ROOT / "tests" / "fixtures" / "auto-fix"
        before = (autofix_dir / "JSS-NAME-001" / "before.tex").read_text(
            encoding="utf-8"
        )
        violations = run_rule(jss_name_001, before)
        assert len(violations) == 1
        v = violations[0]
        assert isinstance(v.fix, Fix)
        assert v.fix.confidence == "safe"
        assert before[v.fix.start : v.fix.end] == "JAVA"
        assert v.fix.replacement == "Java"

    def test_fix_application_matches_after_fixture(self, run_rule):
        autofix_dir = REPO_ROOT / "tests" / "fixtures" / "auto-fix"
        before = (autofix_dir / "JSS-NAME-001" / "before.tex").read_text(
            encoding="utf-8"
        )
        after = (autofix_dir / "JSS-NAME-001" / "after.tex").read_text(
            encoding="utf-8"
        )
        violations = run_rule(jss_name_001, before)
        fix = violations[0].fix
        assert isinstance(fix, Fix)
        applied = before[: fix.start] + fix.replacement + before[fix.end :]
        assert applied == after


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

    def test_emits_safe_fix_payload(self, run_rule):
        """Spec 008 follow-up: each violation carries a Fix(...) payload
        whose byte range covers the literal field value (without the
        surrounding ``{}``/``""`` delimiters) and whose replacement is
        the JSS-canonical form.
        """
        autofix_dir = REPO_ROOT / "tests" / "fixtures" / "auto-fix"
        before = (autofix_dir / "JSS-NAME-002" / "before.bib").read_text(
            encoding="utf-8"
        )
        violations = run_rule(jss_name_002, before, kind="bib")
        assert len(violations) == 1
        v = violations[0]
        assert isinstance(v.fix, Fix)
        assert v.fix.confidence == "safe"
        # The Fix range must exclude the surrounding ``{}`` delimiters.
        assert before[v.fix.start : v.fix.end] == "Springer"
        assert v.fix.replacement == "Springer-Verlag"

    def test_fix_application_matches_after_fixture(self, run_rule):
        autofix_dir = REPO_ROOT / "tests" / "fixtures" / "auto-fix"
        before = (autofix_dir / "JSS-NAME-002" / "before.bib").read_text(
            encoding="utf-8"
        )
        after = (autofix_dir / "JSS-NAME-002" / "after.bib").read_text(
            encoding="utf-8"
        )
        violations = run_rule(jss_name_002, before, kind="bib")
        fix = violations[0].fix
        assert isinstance(fix, Fix)
        applied = before[: fix.start] + fix.replacement + before[fix.end :]
        assert applied == after

    def test_fix_handles_quote_delimited_value(self, run_rule):
        """Quote-wrapped (``journal = "JASA"``) field values must
        resolve to a Fix range that excludes the ``""`` delimiters."""
        src = (
            "@article{x,\n"
            "  author  = {Doe},\n"
            "  title   = {T},\n"
            '  journal = "JASA",\n'
            "  year    = {2020}\n"
            "}\n"
        )
        violations = run_rule(jss_name_002, src, kind="bib")
        assert len(violations) == 1
        fix = violations[0].fix
        assert isinstance(fix, Fix)
        assert src[fix.start : fix.end] == "JASA"
        assert fix.replacement == "Journal of the American Statistical Association"

    def test_fix_targets_correct_entry_when_value_repeats(self, run_rule):
        """Two entries, one already canonical (``Springer-Verlag``) and
        one not (``Springer``); the Fix must point at the offending
        entry's ``publisher`` value, not at the first textual match.
        """
        src = (
            "@book{a,\n"
            "  publisher = {Springer-Verlag}\n"
            "}\n"
            "@book{b,\n"
            "  publisher = {Springer}\n"
            "}\n"
        )
        violations = run_rule(jss_name_002, src, kind="bib")
        assert len(violations) == 1
        fix = violations[0].fix
        assert isinstance(fix, Fix)
        # The slice must read literal "Springer" (8 chars), not the
        # 15-char "Springer-Verlag" from entry ``a``.
        assert src[fix.start : fix.end] == "Springer"


def test_name_001_empty_tex_silent():
    tex = ParsedTexFile(path=Path("/tmp/x.tex"), source="", nodes=(), walker=None)
    doc = ParsedDocument(tex_files=(tex,))
    assert list(check_jss_name_001(doc, ToolConfig())) == []
