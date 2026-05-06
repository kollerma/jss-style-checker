"""Tests for JSS structure rules — 100% branch coverage target."""

from __future__ import annotations

from pathlib import Path

from texlint.api import ParsedDocument, ParsedTexFile, Severity, ToolConfig
from texlint.journals.jss.rules.structure import (
    check_jss_struct_001,
    check_jss_struct_002,
    check_jss_struct_003,
    check_jss_struct_004,
    check_jss_struct_005,
    check_jss_struct_006,
    jss_struct_001,
    jss_struct_002,
    jss_struct_003,
    jss_struct_004,
    jss_struct_005,
    jss_struct_006,
    rules,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "violations" / "structure"


def _tex(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_rules_tuple_has_six_rules():
    assert len(rules) == 6


def test_rules_tuple_ids():
    assert {r.id for r in rules} == {f"JSS-STRUCT-00{i}" for i in range(1, 7)}


# ---------------------------------------------------------------------------
# JSS-STRUCT-001 — summary/discussion before bibliography
# ---------------------------------------------------------------------------


class TestStruct001:
    def test_positive(self, run_rule):
        violations = run_rule(jss_struct_001, _tex("JSS-STRUCT-001-bad.tex"))
        assert len(violations) == 1

    def test_good_silent(self, run_rule):
        assert run_rule(jss_struct_001, _tex("JSS-STRUCT-001-good.tex")) == []

    def test_no_bibliography_silent(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}\section{Intro}\end{document}"
        )
        assert run_rule(jss_struct_001, src) == []

    def test_no_section_before_bib_silent(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}\bibliography{refs}\end{document}"
        )
        assert run_rule(jss_struct_001, src) == []

    def test_discussion_title_accepted(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}\section{Discussion}\bibliography{refs}\end{document}"
        )
        assert run_rule(jss_struct_001, src) == []

    def test_thebibliography_env_counts_as_bibliography(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}\section{Results}" "\n"
            r"\begin{thebibliography}{99}\end{thebibliography}" "\n"
            r"\end{document}"
        )
        violations = run_rule(jss_struct_001, src)
        assert len(violations) == 1


# ---------------------------------------------------------------------------
# JSS-STRUCT-002 — Acknowledgments spelling
# ---------------------------------------------------------------------------


class TestStruct002:
    def test_positive(self, run_rule):
        violations = run_rule(jss_struct_002, _tex("JSS-STRUCT-002-bad.tex"))
        assert len(violations) == 1

    def test_good_silent(self, run_rule):
        assert run_rule(jss_struct_002, _tex("JSS-STRUCT-002-good.tex")) == []

    def test_singular_form_flagged(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}\section{Acknowledgement}\end{document}"
        )
        violations = run_rule(jss_struct_002, src)
        assert len(violations) == 1

    def test_section_with_other_title_silent(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}\section{Introduction}\end{document}"
        )
        assert run_rule(jss_struct_002, src) == []

    def test_non_section_macro_silent(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\emph{Acknowledgements}"
        )
        assert run_rule(jss_struct_002, src) == []


# ---------------------------------------------------------------------------
# JSS-STRUCT-003 — appendix has proper title
# ---------------------------------------------------------------------------


class TestStruct003:
    def test_positive(self, run_rule):
        violations = run_rule(jss_struct_003, _tex("JSS-STRUCT-003-bad.tex"))
        assert len(violations) == 1

    def test_good_silent(self, run_rule):
        assert run_rule(jss_struct_003, _tex("JSS-STRUCT-003-good.tex")) == []

    def test_appendices_plural_also_flagged(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{appendix}\section*{Appendices}proof\end{appendix}" "\n"
            r"\end{document}"
        )
        violations = run_rule(jss_struct_003, src)
        assert len(violations) == 1

    def test_no_appendix_env_silent(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}\section*{Appendix}\end{document}"
        )
        assert run_rule(jss_struct_003, src) == []

    def test_non_section_macros_in_appendix_silent(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{appendix}\emph{Appendix}\end{appendix}" "\n"
            r"\end{document}"
        )
        assert run_rule(jss_struct_003, src) == []


# ---------------------------------------------------------------------------
# JSS-STRUCT-004 — \bibliography instead of thebibliography env
# ---------------------------------------------------------------------------


class TestStruct004:
    def test_positive(self, run_rule):
        violations = run_rule(jss_struct_004, _tex("JSS-STRUCT-004-bad.tex"))
        assert len(violations) == 1
        assert violations[0].severity == Severity.ERROR

    def test_good_silent(self, run_rule):
        assert run_rule(jss_struct_004, _tex("JSS-STRUCT-004-good.tex")) == []


# ---------------------------------------------------------------------------
# JSS-STRUCT-005 — \and separator
# ---------------------------------------------------------------------------


class TestStruct005:
    def test_positive(self, run_rule):
        violations = run_rule(jss_struct_005, _tex("JSS-STRUCT-005-bad.tex"))
        assert len(violations) == 1

    def test_good_silent(self, run_rule):
        assert run_rule(jss_struct_005, _tex("JSS-STRUCT-005-good.tex")) == []

    def test_no_author_macro_silent(self, run_rule):
        src = r"\documentclass[article]{jss}" "\n\\begin{document}\\end{document}"
        assert run_rule(jss_struct_005, src) == []

    def test_author_with_no_group_arg_silent(self, run_rule):
        # \author X — unbraced arg; no group → skip.
        src = r"\author X"
        assert run_rule(jss_struct_005, src) == []

    def test_author_without_and_silent(self, run_rule):
        src = r"\author{Alice Smith}"
        assert run_rule(jss_struct_005, src) == []

    def test_first_group_arg_fallback(self, parse_tex_source):
        # Exercise the sibling-fallback path in _first_group_arg.
        from texlint.journals.jss.rules.structure import _first_group_arg
        tex = parse_tex_source(r"\someunknownmacro{inside}")
        from texlint.journals.jss.rules._helpers import _iter_with_parent
        for parent, idx, node in _iter_with_parent(tex.nodes):
            from pylatexenc.latexwalker import LatexMacroNode
            if isinstance(node, LatexMacroNode) and node.macroname == "someunknownmacro":
                grp = _first_group_arg(node, parent, idx)
                assert grp is not None
                return
        raise AssertionError("macro not found")

    def test_first_group_arg_no_nodeargd(self):
        from pylatexenc.latexwalker import LatexMacroNode

        from texlint.journals.jss.rules.structure import _first_group_arg

        class FakeMacro(LatexMacroNode):
            def __init__(self):  # type: ignore[no-untyped-def]
                pass

        fake = FakeMacro()
        assert _first_group_arg(fake, (fake,), 0) is None


# ---------------------------------------------------------------------------
# JSS-STRUCT-006 — pagebreak between bibliography and appendix
# ---------------------------------------------------------------------------


class TestStruct006:
    def test_positive(self, run_rule):
        violations = run_rule(jss_struct_006, _tex("JSS-STRUCT-006-bad.tex"))
        assert len(violations) == 1

    def test_good_silent(self, run_rule):
        assert run_rule(jss_struct_006, _tex("JSS-STRUCT-006-good.tex")) == []

    def test_clearpage_also_accepted(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\bibliography{refs}" "\n"
            r"\clearpage" "\n"
            r"\begin{appendix}\section{Details}x\end{appendix}" "\n"
            r"\end{document}"
        )
        assert run_rule(jss_struct_006, src) == []

    def test_no_bibliography_silent(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{appendix}\section{Details}x\end{appendix}" "\n"
            r"\end{document}"
        )
        assert run_rule(jss_struct_006, src) == []

    def test_no_appendix_silent(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}\bibliography{refs}\end{document}"
        )
        assert run_rule(jss_struct_006, src) == []

    def test_appendix_before_bibliography_silent(self, run_rule):
        # Some JSS layouts put appendix before bibliography.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{appendix}\section{Details}x\end{appendix}" "\n"
            r"\bibliography{refs}" "\n"
            r"\end{document}"
        )
        assert run_rule(jss_struct_006, src) == []

    def test_non_pagebreak_macro_between_silent(self, run_rule):
        # \par or other macros between don't suppress the rule.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\bibliography{refs}" "\n"
            r"\par" "\n"
            r"\begin{appendix}\section{Details}x\end{appendix}" "\n"
            r"\end{document}"
        )
        violations = run_rule(jss_struct_006, src)
        assert len(violations) == 1

    def test_pagebreak_outside_window_does_not_help(self, run_rule):
        # \newpage BEFORE \bibliography doesn't count.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\newpage" "\n"
            r"\bibliography{refs}" "\n"
            r"\begin{appendix}\section{Details}x\end{appendix}" "\n"
            r"\end{document}"
        )
        violations = run_rule(jss_struct_006, src)
        assert len(violations) == 1

    def test_emits_zero_length_newpage_fix(self, run_rule):
        # Spec 008 follow-up: STRUCT-006 must emit a Fix payload so it
        # participates in ``jss-lint --fix``. The fix is a 0-length
        # insertion of ``\newpage\n`` at the \begin{appendix} offset.
        violations = run_rule(jss_struct_006, _tex("JSS-STRUCT-006-bad.tex"))
        assert len(violations) == 1
        v = violations[0]
        assert v.fix is not None
        assert v.fix.start == v.fix.end  # 0-length insert
        assert "\\newpage" in v.fix.replacement
        assert v.fix.confidence == "safe"


def test_all_checks_silent_on_empty_tex():
    tex = ParsedTexFile(path=Path("/tmp/x.tex"), source="", nodes=(), walker=None)
    doc = ParsedDocument(tex_files=(tex,))
    for check in (
        check_jss_struct_001, check_jss_struct_002, check_jss_struct_003,
        check_jss_struct_004, check_jss_struct_005, check_jss_struct_006,
    ):
        assert list(check(doc, ToolConfig())) == []
