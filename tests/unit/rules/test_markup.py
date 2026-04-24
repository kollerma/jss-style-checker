"""Tests for JSS markup rules — 100% branch coverage target."""

from __future__ import annotations

from pathlib import Path

from texlint.api import ParsedDocument, ParsedTexFile, Severity, ToolConfig
from texlint.journals.jss.rules.markup import (
    check_jss_markup_001,
    check_jss_markup_002,
    check_jss_markup_003,
    check_jss_markup_004,
    jss_markup_001,
    jss_markup_002,
    jss_markup_003,
    jss_markup_004,
    rules,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "violations" / "markup"


def _tex(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_rules_tuple_has_four_rules():
    assert len(rules) == 4


def test_rules_tuple_ids():
    assert {r.id for r in rules} == {f"JSS-MARKUP-00{i}" for i in range(1, 5)}


# ---------------------------------------------------------------------------
# JSS-MARKUP-001 — language names
# ---------------------------------------------------------------------------


class TestMarkup001:
    def test_positive(self, run_rule):
        violations = run_rule(jss_markup_001, _tex("JSS-MARKUP-001-bad.tex"))
        # 'R' and 'Python' → 2 hits
        assert len(violations) == 2
        assert all(v.rule_id == "JSS-MARKUP-001" for v in violations)

    def test_good_silent(self, run_rule):
        assert run_rule(jss_markup_001, _tex("JSS-MARKUP-001-good.tex")) == []

    def test_skip_math_mode(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"Let $R$ be the covariance matrix." "\n"
            r"\end{document}"
        )
        assert run_rule(jss_markup_001, src) == []

    def test_skip_inside_code_macro(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"See \code{R CMD INSTALL}." "\n"
            r"\end{document}"
        )
        assert run_rule(jss_markup_001, src) == []

    def test_skip_initial(self, run_rule):
        # 'J. R. Statistical' — R is an initial, not the language.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"J. R. Statistical Society paper." "\n"
            r"\end{document}"
        )
        assert run_rule(jss_markup_001, src) == []

    def test_skip_section_title(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\section{Introduction to R}" "\n"
            r"\end{document}"
        )
        # MARKUP-004 handles section titles; MARKUP-001 skips them.
        assert run_rule(jss_markup_001, src) == []

    def test_skip_verbatim(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{verbatim}" "\n"
            r"Use R for this" "\n"
            r"\end{verbatim}" "\n"
            r"\end{document}"
        )
        assert run_rule(jss_markup_001, src) == []


# ---------------------------------------------------------------------------
# JSS-MARKUP-002 — package names
# ---------------------------------------------------------------------------


class TestMarkup002:
    def test_positive(self, run_rule):
        violations = run_rule(jss_markup_002, _tex("JSS-MARKUP-002-bad.tex"))
        assert len(violations) == 1

    def test_good_silent(self, run_rule):
        assert run_rule(jss_markup_002, _tex("JSS-MARKUP-002-good.tex")) == []

    def test_skip_already_wrapped(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"The \pkg{MASS} package." "\n"
            r"\end{document}"
        )
        assert run_rule(jss_markup_002, src) == []


# ---------------------------------------------------------------------------
# JSS-MARKUP-003 — function / command names
# ---------------------------------------------------------------------------


class TestMarkup003:
    def test_positive(self, run_rule):
        violations = run_rule(jss_markup_003, _tex("JSS-MARKUP-003-bad.tex"))
        assert len(violations) >= 1

    def test_good_silent(self, run_rule):
        assert run_rule(jss_markup_003, _tex("JSS-MARKUP-003-good.tex")) == []

    def test_skip_inside_code(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"Use \code{glm()} for this." "\n"
            r"\end{document}"
        )
        assert run_rule(jss_markup_003, src) == []


# ---------------------------------------------------------------------------
# JSS-MARKUP-004 — section titles with markup
# ---------------------------------------------------------------------------


class TestMarkup004:
    def test_positive(self, run_rule):
        violations = run_rule(jss_markup_004, _tex("JSS-MARKUP-004-bad.tex"))
        assert len(violations) == 1

    def test_good_silent(self, run_rule):
        assert run_rule(jss_markup_004, _tex("JSS-MARKUP-004-good.tex")) == []

    def test_plain_section_ok(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}\section{Plain title}\end{document}"
        )
        assert run_rule(jss_markup_004, src) == []

    def test_math_in_title_also_flagged(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}\section{Study of $\beta$}\end{document}"
        )
        assert len(run_rule(jss_markup_004, src)) == 1

    def test_non_section_macro_ignored(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}\emph{\proglang{R}}\end{document}"
        )
        assert run_rule(jss_markup_004, src) == []

    def test_has_optional_shim_without_nodeargd(self):
        from pylatexenc.latexwalker import LatexMacroNode
        from texlint.journals.jss.rules.markup import _has_optional_shim

        class FakeMacro(LatexMacroNode):
            def __init__(self):  # type: ignore[no-untyped-def]
                pass

        assert _has_optional_shim(FakeMacro()) is False

    def test_mandatory_arg_contains_markup_without_nodeargd(self):
        from pylatexenc.latexwalker import LatexMacroNode
        from texlint.journals.jss.rules.markup import (
            _mandatory_arg_contains_markup,
        )

        class FakeMacro(LatexMacroNode):
            def __init__(self):  # type: ignore[no-untyped-def]
                pass

        assert _mandatory_arg_contains_markup(FakeMacro()) is False

    def test_mandatory_arg_empty_argnlist(self):
        from pylatexenc.latexwalker import LatexMacroNode
        from texlint.journals.jss.rules.markup import (
            _mandatory_arg_contains_markup,
        )

        class FakeArgd:
            argnlist = ()

        class FakeMacro(LatexMacroNode):
            def __init__(self):  # type: ignore[no-untyped-def]
                self.nodeargd = FakeArgd()

        assert _mandatory_arg_contains_markup(FakeMacro()) is False

    def test_mandatory_arg_with_only_chars(self, run_rule):
        # \section{Plain title} — argnlist has a group with only chars, no markup.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}\section{Plain title}\end{document}"
        )
        assert run_rule(jss_markup_004, src) == []


def test_empty_tex_silent():
    tex = ParsedTexFile(path=Path("/tmp/x.tex"), source="", nodes=(), walker=None)
    doc = ParsedDocument(tex_files=(tex,))
    for check in (
        check_jss_markup_001, check_jss_markup_002,
        check_jss_markup_003, check_jss_markup_004,
    ):
        assert list(check(doc, ToolConfig())) == []


def test_is_initial_branches():
    from texlint.journals.jss.rules.markup import _is_initial
    # offset+1 at end-of-string → tail_start >= len(chars) → False.
    assert _is_initial("R", 0) is False
    # next char is period → True.
    assert _is_initial("R.", 0) is True
    # next char is not period → False.
    assert _is_initial("R;", 0) is False
