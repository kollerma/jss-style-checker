"""Tests for JSS crossrefs rules — 100% branch coverage target."""

from __future__ import annotations

from pathlib import Path

from texlint.api import ParsedDocument, ParsedTexFile, Severity, ToolConfig
from texlint.journals.jss.rules.crossrefs import (
    check_jss_xref_001,
    check_jss_xref_002,
    check_jss_xref_003,
    check_jss_xref_004,
    jss_xref_001,
    jss_xref_002,
    jss_xref_003,
    jss_xref_004,
    rules,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "violations" / "crossrefs"


def _tex(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_rules_tuple_has_four_rules():
    assert len(rules) == 4


def test_rules_tuple_ids():
    assert {r.id for r in rules} == {f"JSS-XREF-00{i}" for i in range(1, 5)}


# ---------------------------------------------------------------------------
# JSS-XREF-001 — Figure/Table N by number
# ---------------------------------------------------------------------------


class TestXref001:
    def test_positive(self, run_rule):
        violations = run_rule(jss_xref_001, _tex("JSS-XREF-001-bad.tex"))
        assert len(violations) == 1
        assert violations[0].rule_id == "JSS-XREF-001"

    def test_good_silent(self, run_rule):
        assert run_rule(jss_xref_001, _tex("JSS-XREF-001-good.tex")) == []

    def test_table_also_flagged(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}See Table 3 for results.\end{document}"
        )
        assert len(run_rule(jss_xref_001, src)) == 1

    def test_fig_abbrev_flagged(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}See Fig. 2 for results.\end{document}"
        )
        assert len(run_rule(jss_xref_001, src)) == 1

    def test_skip_inside_code(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}Use \code{Figure 2} literally.\end{document}"
        )
        assert run_rule(jss_xref_001, src) == []


# ---------------------------------------------------------------------------
# JSS-XREF-002 — (\ref{...}) paren-wrapped
# ---------------------------------------------------------------------------


class TestXref002:
    def test_positive(self, run_rule):
        violations = run_rule(jss_xref_002, _tex("JSS-XREF-002-bad.tex"))
        assert len(violations) == 1
        assert violations[0].severity == Severity.INFO

    def test_good_silent(self, run_rule):
        assert run_rule(jss_xref_002, _tex("JSS-XREF-002-good.tex")) == []

    def test_ref_without_parens_silent(self, run_rule):
        src = r"\ref{eq:mean}"
        assert run_rule(jss_xref_002, src) == []

    def test_ref_first_node_silent(self, run_rule):
        src = r"\ref{eq:mean}) trailing."
        assert run_rule(jss_xref_002, src) == []

    def test_ref_last_node_silent(self, run_rule):
        src = r"Leading (\ref{eq:mean}"
        assert run_rule(jss_xref_002, src) == []

    def test_emits_safe_fix(self, run_rule):
        src = r"Leading (\ref{eq:mean}) trailing."
        violations = run_rule(jss_xref_002, src)
        assert len(violations) == 1
        v = violations[0]
        assert v.fix is not None
        assert v.fix.confidence == "safe"
        # Replacement preserves the original \ref{label} verbatim.
        assert v.fix.replacement.startswith("Equation~\\ref{")
        assert v.fix.replacement == "Equation~\\ref{eq:mean}"
        # Span covers the entire ``(\ref{eq:mean})`` substring.
        assert src[v.fix.start : v.fix.end] == r"(\ref{eq:mean})"

    def test_eqref_flagged(self, run_rule):
        # \eqref{...} renders as "(N)" — same parenthesised form
        # reviewer P10 discourages, so it shares the rule id.
        src = r"See \eqref{eq:mean} for the derivation."
        violations = run_rule(jss_xref_002, src)
        assert len(violations) == 1
        assert violations[0].rule_id == "JSS-XREF-002"
        assert violations[0].severity == Severity.INFO

    def test_eqref_emits_safe_fix(self, run_rule):
        src = r"See \eqref{eq:mean} for the derivation."
        violations = run_rule(jss_xref_002, src)
        assert len(violations) == 1
        v = violations[0]
        assert v.fix is not None
        assert v.fix.confidence == "safe"
        # Autofix drops the ``eq`` and rewrites to ``Equation~\ref{label}``.
        assert v.fix.replacement == "Equation~\\ref{eq:mean}"
        # Span covers the entire ``\eqref{eq:mean}`` substring.
        assert src[v.fix.start : v.fix.end] == r"\eqref{eq:mean}"

    def test_eqref_non_equation_prefix_silent(self, run_rule):
        # A label like ``sec:intro`` is clearly not an equation, even
        # if someone wrote \eqref{sec:intro} — don't suggest renaming.
        src = r"See \eqref{sec:intro} for context."
        assert run_rule(jss_xref_002, src) == []


# ---------------------------------------------------------------------------
# JSS-XREF-003 — Subsection N.N
# ---------------------------------------------------------------------------


class TestXref003:
    def test_positive(self, run_rule):
        violations = run_rule(jss_xref_003, _tex("JSS-XREF-003-bad.tex"))
        assert len(violations) == 1

    def test_good_silent(self, run_rule):
        assert run_rule(jss_xref_003, _tex("JSS-XREF-003-good.tex")) == []

    def test_subsections_plural_flagged(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}See Subsections 3.2 and 3.3.\end{document}"
        )
        violations = run_rule(jss_xref_003, src)
        assert len(violations) == 1

    def test_skip_inside_code(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}Use \code{Subsection 3.2} literally.\end{document}"
        )
        assert run_rule(jss_xref_003, src) == []


# ---------------------------------------------------------------------------
# JSS-XREF-004 — numbered equation without \label
# ---------------------------------------------------------------------------


class TestXref004:
    def test_positive(self, run_rule):
        violations = run_rule(jss_xref_004, _tex("JSS-XREF-004-bad.tex"))
        assert len(violations) == 1
        assert violations[0].severity == Severity.INFO

    def test_good_silent(self, run_rule):
        assert run_rule(jss_xref_004, _tex("JSS-XREF-004-good.tex")) == []

    def test_align_env_flagged(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{align}x=1\end{align}" "\n"
            r"\end{document}"
        )
        assert len(run_rule(jss_xref_004, src)) == 1

    def test_unnumbered_equation_silent(self, run_rule):
        # equation* is not in _NUMBERED_EQ_ENVS.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{equation*}x=1\end{equation*}" "\n"
            r"\end{document}"
        )
        assert run_rule(jss_xref_004, src) == []

    def test_nonumber_equation_silent(self, run_rule):
        # Reviewer-confirmed FPs from cran_sphet, cran_synthpop:
        # \nonumber inside an equation env suppresses the equation
        # number, so it isn't a cross-ref target and a missing
        # \label{} is not a defect.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{equation}B \theta = 0 \nonumber\end{equation}" "\n"
            r"\end{document}"
        )
        assert run_rule(jss_xref_004, src) == []

    def test_align_with_nonumber_still_fires(self, run_rule):
        # Multi-line align with \nonumber on one line does NOT unnumber
        # the others — the env still needs a \label{}.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{align}x=1\nonumber \\ y=2\end{align}" "\n"
            r"\end{document}"
        )
        assert len(run_rule(jss_xref_004, src)) == 1

    def test_non_equation_env_silent(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{itemize}\item x\end{itemize}" "\n"
            r"\end{document}"
        )
        assert run_rule(jss_xref_004, src) == []


def test_all_checks_silent_on_empty_tex():
    tex = ParsedTexFile(path=Path("/tmp/x.tex"), source="", nodes=(), walker=None)
    doc = ParsedDocument(tex_files=(tex,))
    for check in (
        check_jss_xref_001, check_jss_xref_002,
        check_jss_xref_003, check_jss_xref_004,
    ):
        assert list(check(doc, ToolConfig())) == []
