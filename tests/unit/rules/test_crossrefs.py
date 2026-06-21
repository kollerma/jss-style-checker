"""Tests for JSS crossrefs rules — 100% branch coverage target."""

from __future__ import annotations

from pathlib import Path

from texlint.api import ParsedDocument, ParsedTexFile, Severity, ToolConfig
from texlint.journals.jss.rules.crossrefs import (
    check_jss_xref_001,
    check_jss_xref_002,
    check_jss_xref_003,
    check_jss_xref_004,
    check_jss_xref_005,
    check_jss_xref_006,
    jss_xref_001,
    jss_xref_002,
    jss_xref_003,
    jss_xref_004,
    jss_xref_005,
    jss_xref_006,
    rules,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "violations" / "crossrefs"


def _tex(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_rules_tuple_has_six_rules():
    assert len(rules) == 6


def test_rules_tuple_ids():
    assert {r.id for r in rules} == {f"JSS-XREF-00{i}" for i in range(1, 7)}


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


# ---------------------------------------------------------------------------
# JSS-XREF-005 — figures / tables carry \label{} and are referenced
# ---------------------------------------------------------------------------


class TestXref005:
    def test_positive_missing_label(self, run_rule):
        violations = run_rule(jss_xref_005, _tex("JSS-XREF-005-bad.tex"))
        assert len(violations) == 1
        assert violations[0].rule_id == "JSS-XREF-005"
        assert violations[0].severity == Severity.WARNING

    def test_good_fixture_silent(self, run_rule):
        assert run_rule(jss_xref_005, _tex("JSS-XREF-005-good.tex")) == []

    def test_orphan_label_fires(self, run_rule):
        # Captioned float with a \label that is never referenced.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{table}\caption{T}\label{tab:x}\end{table}" "\n"
            r"\end{document}"
        )
        violations = run_rule(jss_xref_005, src)
        assert len(violations) == 1
        assert "tab:x" in violations[0].suggestion

    def test_captionless_float_silent(self, run_rule):
        # No \caption -> unnumbered -> not a cross-ref target -> silent.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{figure}\includegraphics{x}\end{figure}" "\n"
            r"\end{document}"
        )
        assert run_rule(jss_xref_005, src) == []

    def test_starred_float_in_scope(self, run_rule):
        # figure* is a numbered float too; captioned + orphan label fires.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{figure*}\caption{F}\label{fig:wide}\end{figure*}" "\n"
            r"\end{document}"
        )
        assert len(run_rule(jss_xref_005, src)) == 1

    def test_referenced_via_autoref_silent(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{figure}\caption{F}\label{fig:x}\end{figure}" "\n"
            r"\autoref{fig:x} shows it." "\n"
            r"\end{document}"
        )
        assert run_rule(jss_xref_005, src) == []

    def test_referenced_via_vref_silent(self, run_rule):
        # \vref (varioref) has no pylatexenc spec, so its {label} parses as
        # a standalone group; _collect_referenced_labels must still pick it
        # up via the next-sibling-group fallback (regression for the
        # TraMineR fg_cluster-seqrplot false positive).
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{figure}\caption{F}\label{fig:x}\end{figure}" "\n"
            r"Figure~\vref{fig:x} shows it." "\n"
            r"\end{document}"
        )
        assert run_rule(jss_xref_005, src) == []

    def test_non_float_env_silent(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{itemize}\item x\end{itemize}" "\n"
            r"\end{document}"
        )
        assert run_rule(jss_xref_005, src) == []


class TestXref006:
    def test_figure_missing_caption_flagged(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{figure}\includegraphics{x}\end{figure}" "\n"
            r"\end{document}"
        )
        violations = run_rule(jss_xref_006, src)
        assert len(violations) == 1
        assert violations[0].rule_id == "JSS-XREF-006"
        assert violations[0].severity == Severity.WARNING
        assert "figure" in violations[0].suggestion

    def test_table_missing_caption_flagged(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{table}\begin{tabular}{c}1\end{tabular}\end{table}" "\n"
            r"\end{document}"
        )
        violations = run_rule(jss_xref_006, src)
        assert len(violations) == 1
        assert "table" in violations[0].suggestion

    def test_captioned_float_silent(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{figure}\includegraphics{x}\caption{F}\label{fig:x}\end{figure}" "\n"
            r"\end{document}"
        )
        assert run_rule(jss_xref_006, src) == []

    def test_captionof_counts_as_caption(self, run_rule):
        # \captionof (capt-of / floatrow idiom) also numbers the float.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{figure}\captionof{figure}{F}\end{figure}" "\n"
            r"\end{document}"
        )
        assert run_rule(jss_xref_006, src) == []

    def test_starred_float_in_scope(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{table*}\begin{tabular}{c}1\end{tabular}\end{table*}" "\n"
            r"\end{document}"
        )
        assert len(run_rule(jss_xref_006, src)) == 1

    def test_composite_subfloat_carveout_silent(self, run_rule):
        # A parent figure whose own caption is absent but which contains
        # subfigure panels is a composite float; the parent caption may
        # live on an inner panel, so do not flag the parent.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{figure}" "\n"
            r"\begin{subfigure}{0.5\textwidth}\includegraphics{a}\caption{A}\end{subfigure}" "\n"
            r"\begin{subfigure}{0.5\textwidth}\includegraphics{b}\caption{B}\end{subfigure}" "\n"
            r"\end{figure}" "\n"
            r"\end{document}"
        )
        assert run_rule(jss_xref_006, src) == []

    def test_non_float_env_silent(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{itemize}\item x\end{itemize}" "\n"
            r"\end{document}"
        )
        assert run_rule(jss_xref_006, src) == []


def test_all_checks_silent_on_empty_tex():
    tex = ParsedTexFile(path=Path("/tmp/x.tex"), source="", nodes=(), walker=None)
    doc = ParsedDocument(tex_files=(tex,))
    for check in (
        check_jss_xref_001, check_jss_xref_002,
        check_jss_xref_003, check_jss_xref_004, check_jss_xref_005,
        check_jss_xref_006,
    ):
        assert list(check(doc, ToolConfig())) == []
