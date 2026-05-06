"""Tests for JSS house_style rules — 100% branch coverage target."""

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
from texlint.journals.jss.rules.house_style import (
    check_jss_house_001,
    check_jss_house_002,
    check_jss_house_003,
    jss_house_001,
    jss_house_002,
    jss_house_003,
    rules,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "violations" / "house_style"


def _tex(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def _bib(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_rules_tuple_has_three_rules():
    assert len(rules) == 3


def test_rules_tuple_ids():
    assert {r.id for r in rules} == {f"JSS-HOUSE-00{i}" for i in range(1, 4)}


# ---------------------------------------------------------------------------
# JSS-HOUSE-001 — comma after e.g. / i.e.
# ---------------------------------------------------------------------------


class TestHouse001:
    def test_positive(self, run_rule):
        violations = run_rule(jss_house_001, _tex("JSS-HOUSE-001-bad.tex"))
        assert len(violations) == 1

    def test_good_silent(self, run_rule):
        assert run_rule(jss_house_001, _tex("JSS-HOUSE-001-good.tex")) == []

    def test_ie_also_flagged(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}i.e. this.\end{document}"
        )
        assert len(run_rule(jss_house_001, src)) == 1

    def test_skip_inside_code(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}See \code{e.g.} literally.\end{document}"
        )
        assert run_rule(jss_house_001, src) == []

    def test_emits_safe_fix_payload(self, run_rule):
        """Spec 008 follow-up: each violation carries a Fix(...)
        payload whose 1-byte range covers the trailing `.` and whose
        replacement is `.,`."""
        autofix_dir = REPO_ROOT / "tests" / "fixtures" / "auto-fix"
        before = (autofix_dir / "JSS-HOUSE-001" / "before.tex").read_text(
            encoding="utf-8"
        )
        violations = run_rule(jss_house_001, before)
        assert len(violations) == 1
        v = violations[0]
        assert isinstance(v.fix, Fix)
        assert v.fix.confidence == "safe"
        assert v.fix.end == v.fix.start + 1
        assert before[v.fix.start : v.fix.end] == "."
        assert v.fix.replacement == ".,"

    def test_fix_application_matches_after_fixture(self, run_rule):
        autofix_dir = REPO_ROOT / "tests" / "fixtures" / "auto-fix"
        before = (autofix_dir / "JSS-HOUSE-001" / "before.tex").read_text(
            encoding="utf-8"
        )
        after = (autofix_dir / "JSS-HOUSE-001" / "after.tex").read_text(
            encoding="utf-8"
        )
        violations = run_rule(jss_house_001, before)
        fix = violations[0].fix
        assert isinstance(fix, Fix)
        applied = before[: fix.start] + fix.replacement + before[fix.end :]
        assert applied == after


# ---------------------------------------------------------------------------
# JSS-HOUSE-002 — edition field
# ---------------------------------------------------------------------------


class TestHouse002:
    def test_positive(self, run_rule):
        violations = run_rule(
            jss_house_002, _bib("JSS-HOUSE-002-bad.bib"), kind="bib"
        )
        assert len(violations) == 1

    def test_good_silent(self, run_rule):
        assert (
            run_rule(jss_house_002, _bib("JSS-HOUSE-002-good.bib"), kind="bib")
            == []
        )

    def test_2e_flagged(self, run_rule):
        src = "@book{a, edition={2e}, year={2020}}\n"
        assert len(run_rule(jss_house_002, src, kind="bib")) == 1

    def test_no_edition_silent(self, run_rule):
        src = "@book{a, title={T}, year={2020}}\n"
        assert run_rule(jss_house_002, src, kind="bib") == []

    def test_library_none_silent(self, tmp_path: Path):
        broken = ParsedBibFile(
            path=tmp_path / "b.bib", source="", library=None, violations=()
        )
        doc = ParsedDocument(bib_files=(broken,))
        assert list(check_jss_house_002(doc, ToolConfig())) == []

    # -------- spec 008 follow-up: Fix payload ----------------------------

    def test_emits_safe_fix_payload(self, run_rule):
        """Each violation carries a Fix(...) payload whose byte range
        covers the offending edition value and whose replacement is
        the JSS-canonical short ordinal."""
        autofix_dir = REPO_ROOT / "tests" / "fixtures" / "auto-fix"
        before = (autofix_dir / "JSS-HOUSE-002" / "before.bib").read_text(
            encoding="utf-8"
        )
        violations = run_rule(jss_house_002, before, kind="bib")
        assert len(violations) == 1
        v = violations[0]
        assert isinstance(v.fix, Fix)
        assert v.fix.confidence == "safe"
        assert before[v.fix.start : v.fix.end] == "second"
        assert v.fix.replacement == "2nd"

    def test_fix_application_matches_after_fixture(self, run_rule):
        autofix_dir = REPO_ROOT / "tests" / "fixtures" / "auto-fix"
        before = (autofix_dir / "JSS-HOUSE-002" / "before.bib").read_text(
            encoding="utf-8"
        )
        after = (autofix_dir / "JSS-HOUSE-002" / "after.bib").read_text(
            encoding="utf-8"
        )
        violations = run_rule(jss_house_002, before, kind="bib")
        fix = violations[0].fix
        assert isinstance(fix, Fix)
        applied = before[: fix.start] + fix.replacement + before[fix.end :]
        assert applied == after

    def test_2e_fix_replacement(self, run_rule):
        src = "@book{a, edition={2e}, year={2020}}\n"
        violations = run_rule(jss_house_002, src, kind="bib")
        assert len(violations) == 1
        fix = violations[0].fix
        assert isinstance(fix, Fix)
        assert fix.replacement == "2nd"
        assert src[fix.start : fix.end] == "2e"

    def test_quoted_value_fix(self, run_rule):
        src = '@book{a, edition="third", year={2020}}\n'
        violations = run_rule(jss_house_002, src, kind="bib")
        assert len(violations) == 1
        fix = violations[0].fix
        assert isinstance(fix, Fix)
        assert fix.replacement == "3rd"
        assert src[fix.start : fix.end] == "third"

    def test_self_verify_no_refire(self, run_rule):
        """Re-linting the patched bib MUST NOT re-fire HOUSE-002."""
        src = "@book{a, edition={fourth}, year={2020}}\n"
        violations = run_rule(jss_house_002, src, kind="bib")
        fix = violations[0].fix
        assert isinstance(fix, Fix)
        patched = src[: fix.start] + fix.replacement + src[fix.end :]
        assert run_rule(jss_house_002, patched, kind="bib") == []


# ---------------------------------------------------------------------------
# JSS-HOUSE-003 — redundant \usepackage
# ---------------------------------------------------------------------------


class TestHouse003:
    def test_positive(self, run_rule):
        violations = run_rule(jss_house_003, _tex("JSS-HOUSE-003-bad.tex"))
        # graphicx + hyperref → 2 violations
        assert len(violations) == 2
        assert all(v.severity == Severity.INFO for v in violations)

    def test_good_silent(self, run_rule):
        assert run_rule(jss_house_003, _tex("JSS-HOUSE-003-good.tex")) == []

    def test_unrelated_usepackage_silent(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\usepackage{amsmath}" "\n"
            r"\begin{document}\end{document}"
        )
        assert run_rule(jss_house_003, src) == []

    def test_usepackage_with_options(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\usepackage[utf8]{graphicx}" "\n"
            r"\begin{document}\end{document}"
        )
        violations = run_rule(jss_house_003, src)
        assert len(violations) == 1

    def test_usepackage_missing_group_silent(self, run_rule):
        # Malformed \usepackage with no arg (edge case).
        src = r"\usepackage"
        assert run_rule(jss_house_003, src) == []

    def test_non_usepackage_macro_silent(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\emph{graphicx}" "\n"
            r"\begin{document}\end{document}"
        )
        assert run_rule(jss_house_003, src) == []

    def test_usepackage_no_nodeargd(self):
        from pylatexenc.latexwalker import LatexMacroNode

        from texlint.journals.jss.rules.house_style import _usepackage_name

        class FakeMacro(LatexMacroNode):
            def __init__(self):  # type: ignore[no-untyped-def]
                pass

        fake = FakeMacro()
        assert _usepackage_name(fake, (fake,), 0) == ""

    def test_usepackage_empty_group_silent(self, run_rule):
        # \usepackage{} — empty package name; rule skips via line 143.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\usepackage{}" "\n"
            r"\begin{document}\end{document}"
        )
        assert run_rule(jss_house_003, src) == []

    def test_usepackage_name_via_sibling(self, parse_tex_source):
        # If nodeargd exists but argnlist is empty, the sibling-group
        # lookup kicks in (lines 167-169).
        from pylatexenc.latexwalker import LatexGroupNode, LatexMacroNode

        from texlint.journals.jss.rules.house_style import _usepackage_name
        tex2 = parse_tex_source(r"{hyperref}")
        group = next(
            n for n in tex2.nodes if isinstance(n, LatexGroupNode)
        )

        class FakeArgd:
            argnlist = ()

        class FakeMacro(LatexMacroNode):
            def __init__(self):  # type: ignore[no-untyped-def]
                self.nodeargd = FakeArgd()

        fake = FakeMacro()
        parent = (fake, group)
        assert _usepackage_name(fake, parent, 0) == "hyperref"

    def test_group_chars_skips_non_chars(self):
        from pylatexenc.latexwalker import LatexGroupNode, LatexMacroNode

        from texlint.journals.jss.rules.house_style import _group_chars

        class FakeMacro(LatexMacroNode):
            def __init__(self):  # type: ignore[no-untyped-def]
                pass

        class FakeGroup(LatexGroupNode):
            def __init__(self, items):  # type: ignore[no-untyped-def]
                self.nodelist = items

        assert _group_chars(FakeGroup([FakeMacro()])) == ""


def test_empty_tex_silent():
    tex = ParsedTexFile(path=Path("/tmp/x.tex"), source="", nodes=(), walker=None)
    doc = ParsedDocument(tex_files=(tex,))
    for check in (check_jss_house_001, check_jss_house_003):
        assert list(check(doc, ToolConfig())) == []
