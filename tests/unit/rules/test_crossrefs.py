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
    check_jss_xref_007,
    jss_xref_001,
    jss_xref_002,
    jss_xref_003,
    jss_xref_004,
    jss_xref_005,
    jss_xref_006,
    jss_xref_007,
    rules,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "violations" / "crossrefs"


def _tex(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_rules_tuple_has_seven_rules():
    assert len(rules) == 7


def test_rules_tuple_ids():
    assert {r.id for r in rules} == {f"JSS-XREF-00{i}" for i in range(1, 8)}


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

    def test_cite_locator_not_flagged(self, run_rule):
        # ``\citet[Table 2.5]{X}`` — the optional arg is a locator into the
        # cited work, not a manuscript cross-ref (recall-corpus
        # HardyWeinberg \citet[Table ...]/\cite[Table ...]).
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}"
            r"compiled by~\citet[Table 2.5]{Mourant} originally."
            r"\end{document}"
        )
        assert run_rule(jss_xref_001, src) == []

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

    def test_label_with_embedded_newline_matches_ref(self, run_rule):
        # A \label{} key wrapped across a source newline (TeX folds the
        # newline + indentation to a single space) must still match its
        # \ref{}. Real corpus regression: pymcmc's `eq:observation ar`
        # was written `\label{eq:observation\n    ar}` and \ref'd on one
        # line, so the equation is referenced and must stay silent.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{equation}" "\n"
            r"x = 1,\label{eq:observation" "\n"
            r"    ar}" "\n"
            r"\end{equation}" "\n"
            r"See Equation~\ref{eq:observation ar}." "\n"
            r"\end{document}"
        )
        assert run_rule(jss_xref_004, src) == []

    def test_multiline_per_label_orphan_flagged(self, run_rule):
        # gather numbers each line; one label referenced, the other an
        # orphan — the orphan must still fire (recall-corpus romc
        # eq:1D_example). Per-env "any referenced" missed this.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{gather} \label{eq:a}" "\n"
            r"x = 1 \\ \label{eq:b}" "\n"
            r"y = 2" "\n"
            r"\end{gather}" "\n"
            r"See Equation~\ref{eq:b}." "\n"
            r"\end{document}"
        )
        violations = run_rule(jss_xref_004, src)
        assert len(violations) == 1
        assert "eq:a" in violations[0].suggestion
        assert "eq:b" not in violations[0].suggestion

    def test_multiline_all_referenced_silent(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{align} x = 1 \label{eq:a} \\ y = 2 \label{eq:b} \end{align}" "\n"
            r"Equations~\ref{eq:a} and \ref{eq:b}." "\n"
            r"\end{document}"
        )
        assert run_rule(jss_xref_004, src) == []

    def test_tagged_equation_silent(self, run_rule):
        # \tag{} replaces the auto-number with a custom label, so the
        # equation isn't a standard numbered cross-ref target — exempt,
        # like \nonumber (recall-corpus trueskill \tag'd equations).
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{equation}\label{eq:x} \tag{approx()}" "\n"
            r"x = 1" "\n"
            r"\end{equation}" "\n"
            r"\end{document}"
        )
        assert run_rule(jss_xref_004, src) == []

    def test_multiline_with_nonumber_falls_back(self, run_rule):
        # A \nonumber in the env -> conservative per-env check: one
        # referenced label keeps it silent (avoids flagging the label on
        # the unnumbered line).
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{align} x = 1 \label{eq:a} \\ y = 2 \nonumber \label{eq:b} \end{align}" "\n"
            r"See Equation~\ref{eq:a}." "\n"
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

    def test_multiline_orphan_reported_at_label_line(self, run_rule):
        # Mixed env (one row referenced, one orphan): the orphan is
        # pinpointed at its OWN \label source line, not the \begin line
        # (recall-corpus rstpm2 multistate align).
        src = (
            r"\documentclass[article]{jss}" "\n"   # line 1
            r"\begin{document}" "\n"               # line 2
            r"\begin{align}" "\n"                  # line 3
            r"  x = 1 \label{eq:a} \\" "\n"        # line 4
            r"  y = 2 \label{eq:b}" "\n"           # line 5
            r"\end{align}" "\n"                    # line 6
            r"See Equation~\ref{eq:a}." "\n"       # line 7
            r"\end{document}"
        )
        violations = run_rule(jss_xref_004, src)
        assert len(violations) == 1
        assert violations[0].line == 5  # eq:b's label line, not \begin (3)
        assert "eq:b" in violations[0].suggestion

    def test_multiline_numbered_row_without_label_flagged(self, run_rule):
        # Mixed env whose second row is numbered but carries NO \label —
        # it gets an equation number that can never be referenced
        # (recall-corpus SightabilityModel V_2 row). Reported at the env.
        src = (
            r"\documentclass[article]{jss}" "\n"   # line 1
            r"\begin{document}" "\n"               # line 2
            r"\begin{align}" "\n"                  # line 3
            r"  x = 1 \label{eq:a} \\" "\n"        # line 4
            r"  y = 2" "\n"                        # line 5
            r"\end{align}" "\n"                    # line 6
            r"See Equation~\ref{eq:a}." "\n"       # line 7
            r"\end{document}"
        )
        violations = run_rule(jss_xref_004, src)
        assert len(violations) == 1
        assert violations[0].line == 3
        assert "carries no" in violations[0].suggestion

    def test_multiline_all_orphan_collapses_to_env(self, run_rule):
        # No row is referenced: a single report at the \begin line listing
        # every orphan key (recall-corpus CARBayesST / HardyWeinberg),
        # rather than one violation per label line.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{align} x = 1 \label{eq:a} \\ y = 2 \label{eq:b} \end{align}" "\n"
            r"\end{document}"
        )
        violations = run_rule(jss_xref_004, src)
        assert len(violations) == 1
        assert "eq:a" in violations[0].suggestion
        assert "eq:b" in violations[0].suggestion

    def test_subequations_own_labels_flagged(self, run_rule):
        # A subequations block whose inner align rows carry their OWN
        # unreferenced labels: each is a separately-numbered sub-equation
        # and is flagged at its label line (recall-corpus DBR).
        src = (
            r"\documentclass[article]{jss}" "\n"   # 1
            r"\begin{document}" "\n"               # 2
            r"\begin{subequations}" "\n"           # 3
            r"\begin{align}" "\n"                  # 4
            r"  a = b \label{eq:x} \\" "\n"        # 5
            r"  c = d \label{eq:y}" "\n"           # 6
            r"\end{align}" "\n"                    # 7
            r"\end{subequations}" "\n"             # 8
            r"\end{document}"
        )
        violations = run_rule(jss_xref_004, src)
        assert {v.line for v in violations} == {5, 6}

    def test_subequations_shared_label_silent(self, run_rule):
        # Inner rows without their own label share the outer block's label
        # (the classic subequations carve-out) — stay silent.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{subequations}\label{eq:grp}" "\n"
            r"\begin{align} a = b \\ c = d \end{align}" "\n"
            r"\end{subequations}" "\n"
            r"See Equation~\ref{eq:grp}." "\n"
            r"\end{document}"
        )
        assert run_rule(jss_xref_004, src) == []

    def test_label_carried_past_nonumber_lead_line(self, run_rule):
        # A \label at the env top followed by a \nonumber lead line
        # attaches (in LaTeX) to the next NUMBERED row, so a referenced
        # such label must NOT be reported as a label-less numbered row
        # (regression: mixtools mixturetest / isotone eq:convexAx).
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{eqnarray}\label{eq:m}" "\n"
            r"\nonumber" "\n"
            r"H_0 : k = k_0 \\" "\n"
            r"H_1 : k = k_0 + 1" "\n"
            r"\end{eqnarray}" "\n"
            r"See Equation~\ref{eq:m}." "\n"
            r"\end{document}"
        )
        assert run_rule(jss_xref_004, src) == []

    def test_multiline_all_nonumber_silent(self, run_rule):
        # Every row suppressed with \nonumber -> the env is unnumbered, so
        # a missing \label is not a defect (per-row \nonumber handling;
        # the old per-env code over-fired here).
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{align} x = 1 \nonumber \\ y = 2 \nonumber \end{align}" "\n"
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

    # --- lstlisting code-listing floats (caption/label are options, not
    # macros). A captioned listing is a numbered "Listing N" float and must
    # be referenced. Corpus: trueskill (all its code listings). ---

    def test_lstlisting_captioned_labeled_unreferenced_flagged(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{lstlisting}[caption={A demo.},label=lst:demo]" "\n"
            r"print(x)" "\n"
            r"\end{lstlisting}" "\n"
            r"\end{document}"
        )
        assert len(run_rule(jss_xref_005, src)) == 1

    def test_lstlisting_captioned_labeled_referenced_silent(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{lstlisting}[caption={A demo.},label=lst:demo]" "\n"
            r"print(x)" "\n"
            r"\end{lstlisting}" "\n"
            r"Listing~\ref{lst:demo} shows it." "\n"
            r"\end{document}"
        )
        assert run_rule(jss_xref_005, src) == []

    def test_lstlisting_uncaptioned_silent(self, run_rule):
        # No caption -> an inline snippet, not a numbered float; even a
        # stray label doesn't make it a cross-ref target.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{lstlisting}[label=lst:demo]" "\n"
            r"print(x)" "\n"
            r"\end{lstlisting}" "\n"
            r"\end{document}"
        )
        assert run_rule(jss_xref_005, src) == []

    def test_lstlisting_captioned_no_label_flagged(self, run_rule):
        # Captioned but no label -> unreferenceable (rstpm2 / trueskill
        # missing-label case).
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{lstlisting}[caption={A demo.}]" "\n"
            r"print(x)" "\n"
            r"\end{lstlisting}" "\n"
            r"\end{document}"
        )
        assert len(run_rule(jss_xref_005, src)) == 1

    def test_lstlisting_caption_with_comma_and_bracket_parsed(self, run_rule):
        # Brace-aware option split: a comma and a ``]`` inside caption={...}
        # must not truncate the option list or hide the label.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{lstlisting}[caption={A, b [c] demo.},label=lst:demo]" "\n"
            r"print(x)" "\n"
            r"\end{lstlisting}" "\n"
            r"Listing~\ref{lst:demo}." "\n"
            r"\end{document}"
        )
        # caption + label both parsed, and it IS referenced -> silent.
        assert run_rule(jss_xref_005, src) == []

    def test_lstlisting_body_caption_text_not_scanned(self, run_rule):
        # A listing with no option block whose *body* contains ``caption=``
        # text must not be treated as captioned.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{lstlisting}" "\n"
            r"caption=5, label=oops" "\n"
            r"\end{lstlisting}" "\n"
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


class TestXref007:
    def test_positive(self, run_rule):
        violations = run_rule(jss_xref_007, _tex("JSS-XREF-007-bad.tex"))
        assert len(violations) == 1
        assert violations[0].rule_id == "JSS-XREF-007"

    def test_good_silent(self, run_rule):
        assert run_rule(jss_xref_007, _tex("JSS-XREF-007-good.tex")) == []

    def test_abbrev_variants_flagged(self, run_rule):
        for body in (
            r"See Fig.~\ref{fig:x}.", r"in Sec. \ref{sec:x}",
            r"Tab.\ref{tab:x}", r"Figs.~\ref{fig:a}", r"lowercase fig.~\ref{x}",
        ):
            src = (
                r"\documentclass[article]{jss}" "\n"
                rf"\begin{{document}}{body}\end{{document}}"
            )
            assert len(run_rule(jss_xref_007, src)) == 1, body

    def test_autoref_and_spelled_out_silent(self, run_rule):
        for body in (
            r"Figure~\ref{fig:x}", r"Section~\ref{sec:x}",
            r"\autoref{fig:x}", r"in consec.~\ref{x}",
        ):
            src = (
                r"\documentclass[article]{jss}" "\n"
                rf"\begin{{document}}{body}\end{{document}}"
            )
            assert run_rule(jss_xref_007, src) == [], body

    def test_autofix_rewrites_to_spelled_out(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}See Fig.~\ref{fig:x}.\end{document}"
        )
        v = run_rule(jss_xref_007, src)[0]
        assert v.fix is not None
        assert v.fix.replacement == r"Figure~\ref{fig:x}"


def test_all_checks_silent_on_empty_tex():
    tex = ParsedTexFile(path=Path("/tmp/x.tex"), source="", nodes=(), walker=None)
    doc = ParsedDocument(tex_files=(tex,))
    for check in (
        check_jss_xref_001, check_jss_xref_002,
        check_jss_xref_003, check_jss_xref_004, check_jss_xref_005,
        check_jss_xref_006, check_jss_xref_007,
    ):
        assert list(check(doc, ToolConfig())) == []
