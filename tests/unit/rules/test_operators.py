"""Tests for JSS operators rules — 100% branch coverage target."""

from __future__ import annotations

import re
from pathlib import Path

from texlint.api import Fix, ParsedDocument, ParsedTexFile, ToolConfig
from texlint.journals.jss.rules.operators import (
    check_jss_oper_001,
    check_jss_oper_002,
    check_jss_oper_003,
    check_jss_oper_004,
    jss_oper_001,
    jss_oper_002,
    jss_oper_003,
    jss_oper_004,
    rules,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "violations" / "operators"


def _tex(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_rules_tuple_has_four_rules():
    assert len(rules) == 4


def test_rules_tuple_ids():
    assert {r.id for r in rules} == {f"JSS-OPER-00{i}" for i in range(1, 5)}


# ---------------------------------------------------------------------------
# JSS-OPER-001 — p-value, t-statistic, …
# ---------------------------------------------------------------------------


class TestOper001:
    def test_positive(self, run_rule):
        violations = run_rule(jss_oper_001, _tex("JSS-OPER-001-bad.tex"))
        assert len(violations) == 2  # p-value + t-statistic

    def test_good_silent(self, run_rule):
        assert run_rule(jss_oper_001, _tex("JSS-OPER-001-good.tex")) == []

    def test_skip_inside_code(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}Use \code{p-value} literally.\end{document}"
        )
        assert run_rule(jss_oper_001, src) == []

    def test_emits_safe_fix_payload(self, run_rule):
        """Spec 008 follow-up: each violation carries a Fix(...)
        payload whose byte range covers the offending span and whose
        replacement is the canonical ``$<sym>$~<noun>`` form."""
        autofix_dir = REPO_ROOT / "tests" / "fixtures" / "auto-fix"
        before = (autofix_dir / "JSS-OPER-001" / "before.tex").read_text(
            encoding="utf-8"
        )
        violations = run_rule(jss_oper_001, before)
        assert len(violations) == 1
        v = violations[0]
        assert isinstance(v.fix, Fix)
        assert v.fix.confidence == "safe"
        assert v.fix.start < v.fix.end
        assert re.match(r"^\$.\$~.+$", v.fix.replacement)
        assert before[v.fix.start : v.fix.end] == "p-value"
        assert v.fix.replacement == "$p$~value"

    def test_fix_application_matches_after_fixture(self, run_rule):
        autofix_dir = REPO_ROOT / "tests" / "fixtures" / "auto-fix"
        before = (autofix_dir / "JSS-OPER-001" / "before.tex").read_text(
            encoding="utf-8"
        )
        after = (autofix_dir / "JSS-OPER-001" / "after.tex").read_text(
            encoding="utf-8"
        )
        violations = run_rule(jss_oper_001, before)
        fix = violations[0].fix
        assert isinstance(fix, Fix)
        applied = before[: fix.start] + fix.replacement + before[fix.end :]
        assert applied == after


# ---------------------------------------------------------------------------
# JSS-OPER-002 — transpose with \top
# ---------------------------------------------------------------------------


class TestOper002:
    def test_positive(self, run_rule):
        violations = run_rule(jss_oper_002, _tex("JSS-OPER-002-bad.tex"))
        assert len(violations) == 1

    def test_good_silent(self, run_rule):
        assert run_rule(jss_oper_002, _tex("JSS-OPER-002-good.tex")) == []

    def test_outside_math_silent(self, run_rule):
        # '^T' outside math mode doesn't match.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}Literal text.\end{document}"
        )
        assert run_rule(jss_oper_002, src) == []


# ---------------------------------------------------------------------------
# JSS-OPER-003 — blank lines around display equations
# ---------------------------------------------------------------------------


class TestOper003:
    def test_positive(self, run_rule):
        violations = run_rule(jss_oper_003, _tex("JSS-OPER-003-bad.tex"))
        assert len(violations) == 1

    def test_good_silent(self, run_rule):
        assert run_rule(jss_oper_003, _tex("JSS-OPER-003-good.tex")) == []

    def test_period_carveout_silent(self, run_rule):
        # Equation body ends with a period → sentence ends; no violation.
        src = (
            "\\documentclass[article]{jss}\n"
            "\\begin{document}\n"
            "Intro.\n"
            "\n"
            "\\begin{equation}x = 1.\\end{equation}\n"
            "\n"
            "Next paragraph starts.\n"
            "\\end{document}\n"
        )
        assert run_rule(jss_oper_003, src) == []

    def test_non_display_env_silent(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{itemize}\item x\end{itemize}" "\n"
            r"\end{document}"
        )
        assert run_rule(jss_oper_003, src) == []

    def test_first_node_silent(self, run_rule):
        # Equation at the start of the document with no blank line before it.
        src = (
            r"\begin{equation}x = 1\end{equation}"
        )
        assert run_rule(jss_oper_003, src) == []

    def test_equation_body_non_chars_tail(self, run_rule):
        # Body ends with a macro, not chars → _equation_body_ends_with_period
        # returns False; rule fires if blank lines surround.
        src = (
            "\\documentclass[article]{jss}\n"
            "\\begin{document}\n"
            "Intro.\n"
            "\n"
            "\\begin{equation}\\label{eq:a}x=1\\end{equation}\n"
            "\n"
            "Next.\n"
            "\\end{document}\n"
        )
        violations = run_rule(jss_oper_003, src)
        assert len(violations) == 1

    def test_equation_body_whitespace_tail_before_period(self):
        # Direct unit test of _equation_body_ends_with_period: fabricate
        # an env whose tail children are [CharsNode("x = 1."), CharsNode("   ")]
        # so the reversed iteration skips the whitespace-only last node
        # via the `continue` branch, then reads the period-terminated one.
        from pylatexenc.latexwalker import LatexCharsNode, LatexEnvironmentNode

        from texlint.journals.jss.rules.operators import (
            _equation_body_ends_with_period,
        )

        class FakeChars(LatexCharsNode):
            def __init__(self, text):  # type: ignore[no-untyped-def]
                self.chars = text

        class FakeEnv(LatexEnvironmentNode):
            def __init__(self, children):  # type: ignore[no-untyped-def]
                self.nodelist = children

        env = FakeEnv([FakeChars("x = 1."), FakeChars("   ")])
        assert _equation_body_ends_with_period(env) is True

    def test_equation_body_empty(self, run_rule):
        # Empty nodelist → no period detection, rule checks surrounding lines.
        src = (
            "\\documentclass[article]{jss}\n"
            "\\begin{document}\n"
            "Intro.\n"
            "\n"
            "\\begin{equation}\\end{equation}\n"
            "Next.\n"
            "\\end{document}\n"
        )
        violations = run_rule(jss_oper_003, src)
        assert len(violations) == 1


# ---------------------------------------------------------------------------
# JSS-OPER-004 — jss.cls shortcuts
# ---------------------------------------------------------------------------


class TestOper004:
    def test_positive(self, run_rule):
        violations = run_rule(jss_oper_004, _tex("JSS-OPER-004-bad.tex"))
        assert len(violations) == 1

    def test_good_silent(self, run_rule):
        assert run_rule(jss_oper_004, _tex("JSS-OPER-004-good.tex")) == []

    def test_pr_alone_silent(self, run_rule):
        # Papers that use \Pr exclusively (no \Prob) have chosen the
        # LaTeX built-in as their canonical form. Reproduces the
        # reviewer-confirmed FPs from cran_medflex (6 \Pr cases all
        # marked FP).
        src = (
            "\\documentclass[article]{jss}\n"
            "\\begin{document}$\\Pr(X \\le x)$.\\end{document}\n"
        )
        assert run_rule(jss_oper_004, src) == []

    def test_pr_with_prob_elsewhere_flagged(self, run_rule):
        # Inconsistent notation: paper uses both \Pr and \Prob — flag
        # the \Pr so the author can pick one.
        src = (
            "\\documentclass[article]{jss}\n"
            "\\begin{document}$\\Pr(X \\le x)$. Also $\\Prob(Y)$.\\end{document}\n"
        )
        assert len(run_rule(jss_oper_004, src)) == 1

    def test_pr_with_redefining_newcommand_flagged(self, run_rule):
        # \newcommand{\Pr}{...} proves the author knows about \Prob
        # and chose to redefine \Pr — that's still a JSS deviation.
        src = (
            "\\documentclass[article]{jss}\n"
            "\\newcommand{\\Pr}{\\mathbb{P}}\n"
            "\\begin{document}$\\Pr(X)$.\\end{document}\n"
        )
        assert len(run_rule(jss_oper_004, src)) == 1

    def test_var_flagged(self, run_rule):
        src = (
            "\\documentclass[article]{jss}\n"
            "\\begin{document}$\\mathsf{Var}(X)$.\\end{document}\n"
        )
        assert len(run_rule(jss_oper_004, src)) == 1

    def test_operatorname_cov_flagged(self, run_rule):
        src = (
            "\\documentclass[article]{jss}\n"
            "\\begin{document}$\\operatorname{Cov}(X, Y)$.\\end{document}\n"
        )
        assert len(run_rule(jss_oper_004, src)) == 1

    def test_outside_math_silent(self, run_rule):
        # \mathbb{E} outside math mode is unusual but the rule skips it.
        src = (
            "\\documentclass[article]{jss}\n"
            "\\begin{document}\\mathbb{E}\\end{document}\n"
        )
        assert run_rule(jss_oper_004, src) == []

    def test_unrelated_macro_silent(self, run_rule):
        src = (
            "\\documentclass[article]{jss}\n"
            "\\begin{document}$\\alpha + \\beta$.\\end{document}\n"
        )
        assert run_rule(jss_oper_004, src) == []

    def test_mathbb_with_non_matching_arg_silent(self, run_rule):
        src = (
            "\\documentclass[article]{jss}\n"
            "\\begin{document}$\\mathbb{R}$.\\end{document}\n"
        )
        assert run_rule(jss_oper_004, src) == []

    def test_non_canonical_without_group_silent(self, run_rule):
        # \mathbb X in math — no sibling group to match against, so the
        # _NONCANON_PROB_ARGS lookup returns "" which isn't in the set.
        src = (
            "\\documentclass[article]{jss}\n"
            "\\begin{document}$\\mathbb X$.\\end{document}\n"
        )
        assert run_rule(jss_oper_004, src) == []


def test_all_checks_silent_on_empty_tex():
    tex = ParsedTexFile(path=Path("/tmp/x.tex"), source="", nodes=(), walker=None)
    doc = ParsedDocument(tex_files=(tex,))
    for check in (
        check_jss_oper_001, check_jss_oper_002,
        check_jss_oper_003, check_jss_oper_004,
    ):
        assert list(check(doc, ToolConfig())) == []
