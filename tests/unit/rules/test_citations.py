"""Tests for JSS citations rules — 100% branch coverage target."""

from __future__ import annotations

from pathlib import Path

from texlint.api import Fix, ParsedDocument, Severity, ToolConfig
from texlint.journals.jss.rules.citations import (
    check_jss_cite_002,
    check_jss_cite_004,
    jss_cite_002,
    jss_cite_003,
    jss_cite_004,
    rules,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "violations" / "citations"
AUTOFIX_DIR = REPO_ROOT / "tests" / "fixtures" / "auto-fix"


# ---------------------------------------------------------------------------
# Module-level invariants
# ---------------------------------------------------------------------------

def test_rules_tuple_has_three_rules():
    assert len(rules) == 3


def test_rules_tuple_ids():
    assert {r.id for r in rules} == {"JSS-CITE-002", "JSS-CITE-003", "JSS-CITE-004"}


def test_all_rules_have_fix_none_by_construction():
    # Spec 004 FR-025: Rule.formats is None for every rule; Violation.fix
    # is None by construction (verified per-rule below).
    for r in rules:
        assert r.formats is None


# ---------------------------------------------------------------------------
# JSS-CITE-002 — \pkg{X} needs a citation in the same paragraph
# ---------------------------------------------------------------------------

class TestCite002:
    def test_positive(self, run_rule):
        bad = (FIXTURE_DIR / "JSS-CITE-002-bad.tex").read_text(encoding="utf-8")
        violations = run_rule(jss_cite_002, bad)
        assert len(violations) == 1
        v = violations[0]
        assert v.rule_id == "JSS-CITE-002"
        assert v.severity == Severity.WARNING
        assert v.line >= 1 and v.column >= 1
        assert v.fix is None

    def test_good_fixture_no_violation(self, run_rule):
        good = (FIXTURE_DIR / "JSS-CITE-002-good.tex").read_text(encoding="utf-8")
        assert run_rule(jss_cite_002, good) == []

    def test_citation_before_pkg_same_paragraph(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"See \citep{Wood:2006}. We use \pkg{mgcv} for this." "\n"
            r"\end{document}" "\n"
        )
        assert run_rule(jss_cite_002, src) == []

    def test_language_name_in_pkg_not_flagged(self, run_rule):
        # `\pkg{Python}` is markup misuse (a language, not a package); a
        # language is not citeable, so CITE-002 must stay silent and let
        # the MARKUP rules handle the mis-wrap. Corpus: pymc2 jss-gp.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"The model is implemented in \pkg{Python}." "\n"
            r"\end{document}" "\n"
        )
        assert run_rule(jss_cite_002, src) == []

    def test_bare_url_in_paragraph_satisfies_citation(self, run_rule):
        # A bare download URL beside the package (install lists) supplies
        # the reference — JSS accepts a URL when there is no citeable
        # paper. Corpus: pymcmc's Windows install itemize.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"Install \pkg{mingw} (http://www.mingw.org/) for the compiler." "\n"
            r"\end{document}" "\n"
        )
        assert run_rule(jss_cite_002, src) == []

    def test_url_macro_in_paragraph_satisfies_citation(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"Get \pkg{msys} from \url{http://www.mingw.org/wiki/MSYS}." "\n"
            r"\end{document}" "\n"
        )
        assert run_rule(jss_cite_002, src) == []

    def test_distant_url_next_sentence_still_flagged(self, run_rule):
        # A URL that references something else (a Colab notebook in the
        # next sentence) must NOT satisfy CITE-002 for the package.
        # Corpus regression: github_romc scikit-learn.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"We use the \pkg{scikit-learn} package. The reader can find "
            r"the example \url{https://colab.research.google.com/x} here." "\n"
            r"\end{document}" "\n"
        )
        assert len(run_rule(jss_cite_002, src)) == 1

    def test_pkg_without_url_or_cite_still_flagged(self, run_rule):
        # Guard: the URL relaxation must not silence a genuine first
        # mention that has neither a citation nor a URL.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"We rely on \pkg{somepkg} throughout." "\n"
            r"\end{document}" "\n"
        )
        assert len(run_rule(jss_cite_002, src)) == 1

    def test_citation_in_next_paragraph_still_flagged(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"We use \pkg{mgcv}." "\n\n"
            r"See \citep{Wood:2006}." "\n"
            r"\end{document}" "\n"
        )
        violations = run_rule(jss_cite_002, src)
        assert len(violations) == 1

    def test_first_pkg_only_per_name(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"We use \pkg{mgcv}. Later we also use \pkg{mgcv} elsewhere." "\n"
            r"\end{document}" "\n"
        )
        violations = run_rule(jss_cite_002, src)
        assert len(violations) == 1

    def test_pkg_with_empty_arg_skipped(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"We use \pkg{}." "\n"
            r"\end{document}" "\n"
        )
        assert run_rule(jss_cite_002, src) == []

    def test_pkg_inside_title_not_flagged(self, run_rule):
        # JSS style forbids citations in titles, so a \pkg{X} inside \title{}
        # can't satisfy CITE-002 — the rule should skip it. The first mention
        # outside the title (in the body) is the one that needs a citation.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\title{Bayesian Inference with \pkg{rstan}}" "\n"
            r"\begin{document}" "\n"
            r"\maketitle" "\n"
            r"We use \pkg{rstan} \citep{Stan:2024}." "\n"
            r"\end{document}" "\n"
        )
        assert run_rule(jss_cite_002, src) == []

    def test_pkg_inside_newcommand_not_flagged(self, run_rule):
        # \pkg{X} in a \newcommand body is a definition fragment,
        # not a first-mention; the actual mention is at expansion time.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\newcommand{\stochvol}{\pkg{stochvol}}" "\n"
            r"\begin{document}" "\n"
            r"We use \stochvol\ \citep{Kastner:2016}." "\n"
            r"\end{document}" "\n"
        )
        assert run_rule(jss_cite_002, src) == []

    def test_pkg_with_rmd_at_citation_not_flagged(self, run_rule):
        # Pandoc/Rmd cite syntax `[@key]` in the same paragraph as
        # the first \pkg{X} mention satisfies CITE-002.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\pkg{Forecast Pro} [@ForecastPro00] is well-known." "\n"
            r"\end{document}" "\n"
        )
        assert run_rule(jss_cite_002, src) == []

    def test_pkg_with_bare_at_citation_not_flagged(self, run_rule):
        # Bare `@key` (Pandoc inline citation) also counts.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"@TRAMOSEATS98 implemented this in \pkg{TRAMO}." "\n"
            r"\end{document}" "\n"
        )
        assert run_rule(jss_cite_002, src) == []

    def test_pkg_with_textual_author_year_citation_not_flagged(self, run_rule):
        # Reviewer-confirmed FPs from cran_aer (quote-env free-form
        # citation), cran_zoo: a free-form ``Author (year)`` /
        # ``Smith and Jones (year)`` / ``Brown et al. (year)`` string
        # in the same paragraph as ``\pkg{X}`` is the citation,
        # spelled out without a ``\citep{}`` macro.
        for citation in (
            "Henningsen (2008)",
            "Tsay (2005)",
            "Smith and Jones (2020)",
            "Brown et al. (2019)",
        ):
            src = (
                r"\documentclass[article]{jss}" "\n"
                r"\begin{document}" "\n"
                f"See {citation} for the analysis using \\pkg{{xyz}}.\n"
                r"\end{document}" "\n"
            )
            assert run_rule(jss_cite_002, src) == [], citation

    def test_textual_year_alone_still_flags(self, run_rule):
        # A bare year like "(2020)" without a leading ≥3-letter author
        # name is NOT a citation — short capitalised words ('In',
        # 'On', 'As') don't qualify. The rule should still fire.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"In (2020) we observed \pkg{xyz} in the analysis." "\n"
            r"\end{document}" "\n"
        )
        assert len(run_rule(jss_cite_002, src)) == 1

    def test_tabular_row_isolates_textual_citation(self, run_rule):
        # Reviewer-confirmed FP shape from cran_zoo's CRAN-packages
        # FAQ table: each row lists ``\pkg{X} & description`` and one
        # row's description happens to contain ``Tsay (2005)``. The
        # textual citation in that one row must NOT exempt OTHER rows.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{tabular}{ll}" "\n"
            r"\pkg{Foo} & Companion to Tsay (2005) Analysis. \\" "\n"
            r"\pkg{Bar} & Some description without a citation. \\" "\n"
            r"\end{tabular}" "\n"
            r"\end{document}" "\n"
        )
        violations = run_rule(jss_cite_002, src)
        # Only \pkg{Bar} should fire — \pkg{Foo}'s row has the citation.
        assert len(violations) == 1

    def test_pkg_inside_abstract_macro_not_flagged(self, run_rule):
        # JSS convention: abstracts introduce package names by short
        # reference; the actual \citep lands in §1 (Introduction). A
        # \pkg{X} inside \Abstract{...} can never satisfy CITE-002,
        # so don't fire here.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\title{Demo}" "\n"
            r"\Abstract{We present \pkg{rstan} for Bayesian inference.}" "\n"
            r"\begin{document}" "\n"
            r"We use \pkg{rstan} \citep{Stan:2024}." "\n"
            r"\end{document}" "\n"
        )
        assert run_rule(jss_cite_002, src) == []

    def test_pkg_inside_abstract_env_not_flagged(self, run_rule):
        # Plain-LaTeX `abstract` environment (non-JSS class fallback) —
        # same logic, environment ancestor instead of macro.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{abstract}" "\n"
            r"We present \pkg{rstan} for Bayesian inference." "\n"
            r"\end{abstract}" "\n"
            r"We use \pkg{rstan} \citep{Stan:2024}." "\n"
            r"\end{document}" "\n"
        )
        assert run_rule(jss_cite_002, src) == []

    def test_pkg_inside_plaintitle_not_flagged(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\Plaintitle{Inference with rstan via \pkg{rstan}}" "\n"
            r"\begin{document}" "\n"
            r"\end{document}" "\n"
        )
        assert run_rule(jss_cite_002, src) == []

    def test_pkg_inside_keywords_not_flagged(self, run_rule):
        # JSS \Keywords{} is a no-cite zone — citations don't belong in
        # the keywords list, so a \pkg{X} mention there can't satisfy
        # CITE-002. The first body mention must still carry a citation.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\Keywords{plotting, \pkg{plot3logit}, \proglang{R}}" "\n"
            r"\begin{document}" "\n"
            r"We use \pkg{plot3logit} \citep{plot3logit2021}." "\n"
            r"\end{document}" "\n"
        )
        assert run_rule(jss_cite_002, src) == []

    def test_pkg_inside_section_heading_not_flagged(self, run_rule):
        # JSS style forbids citations in section headings — a \pkg{X}
        # in a \section{} or \subsection{} title can't be satisfied
        # there, so don't flag it. First body mention is the one that
        # matters.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\subsection[Using doParallel]{Using \pkg{doParallel}}" "\n"
            r"We use \pkg{doParallel} \citep{doParallel:2023}." "\n"
            r"\end{document}" "\n"
        )
        assert run_rule(jss_cite_002, src) == []

    def test_pkg_in_body_after_section_mention_still_flagged(self, run_rule):
        # Section mention is skipped, so the first body mention is the
        # first-occurrence and must have a citation.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\section{Using \pkg{rstan}}" "\n"
            r"We use \pkg{rstan} extensively." "\n"
            r"\end{document}" "\n"
        )
        violations = run_rule(jss_cite_002, src)
        assert len(violations) == 1

    def test_pkg_inside_citep_optarg_not_flagged(self, run_rule):
        # `\pkg{X}` in the optional argument of `\citep[...]{key}` is
        # satisfied by the cite itself — the cite is an ancestor, not
        # a sibling, so the paragraph-level sibling check would miss it.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"We fit a Cox model "
            r"\citep[package \pkg{survival},][]{Therneau,pkg:survival}." "\n"
            r"\end{document}" "\n"
        )
        assert run_rule(jss_cite_002, src) == []

    def test_pkg_in_href_with_sibling_cite_not_flagged(self, run_rule):
        # `\href{url}{\pkg{X}} \citep{X}` — the citation sits beside the
        # \href wrapper, not as a sibling of \pkg. Regression: cna.Rnw:157.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"We use \href{https://cran.r-project.org/package=LogicReg}"
            r"{\pkg{LogicReg}} \citep{LogicReg} for the analysis." "\n"
            r"\end{document}" "\n"
        )
        assert run_rule(jss_cite_002, src) == []

    def test_pkg_in_mbox_with_paragraph_cite_not_flagged(self, run_rule):
        # `\mbox{\pkg{X}}` with a \citep elsewhere in the paragraph.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"The \mbox{\pkg{RcppArmadillo}} interface \citep{rcpparma}." "\n"
            r"\end{document}" "\n"
        )
        assert run_rule(jss_cite_002, src) == []

    def test_pkg_in_href_without_cite_still_flagged(self, run_rule):
        # The wrapper guard must NOT suppress a genuine uncited mention.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"We use \href{https://example.org}{\pkg{LonelyPkg}} here." "\n"
            r"\end{document}" "\n"
        )
        assert len(run_rule(jss_cite_002, src)) == 1

    def test_pkg_inside_citealp_optarg_not_flagged(self, run_rule):
        # Same as above, with \citealp.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"See \citealp[\pkg{coxinterval} package][]{pkg:coxinterval}." "\n"
            r"\end{document}" "\n"
        )
        assert run_rule(jss_cite_002, src) == []

    def test_pkg_inside_bibitem_not_flagged(self, run_rule):
        # \pkg{X} inside a \bibitem in thebibliography IS the bibliography
        # entry — that's the citation itself, not a prose mention that
        # needs its own \citep.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{thebibliography}{}" "\n"
            r"\bibitem[{Bendtsen(2012)}]{Bendtsen2012}" "\n"
            r"Bendtsen C (2012). \emph{\pkg{pso}: Particle Swarm Optimization}." "\n"
            r"\end{thebibliography}" "\n"
            r"\end{document}" "\n"
        )
        assert run_rule(jss_cite_002, src) == []

    def test_base_r_package_not_flagged(self, run_rule):
        # \pkg{parallel}, \pkg{methods}, \pkg{stats} ship with R; their
        # citation is covered by the R citation, so they don't trip
        # CITE-002 even without a same-paragraph \citep.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"We use \pkg{parallel} for multi-core support." "\n"
            r"\end{document}" "\n"
        )
        assert run_rule(jss_cite_002, src) == []

    def test_base_r_package_seen_covers_later_mentions(self, run_rule):
        # Even if a base-R package is mentioned multiple times, none of
        # them should fire.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"We use \pkg{stats} here." "\n\n"
            r"Later we use \pkg{stats} again." "\n"
            r"\end{document}" "\n"
        )
        assert run_rule(jss_cite_002, src) == []

    def test_abstract_with_cite_covers_body_mention(self, run_rule):
        # If \Abstract{} contains both \pkg{X} and a \citep{} for it,
        # the body mention is considered satisfied (the abstract IS the
        # cite site for this paper, not a separate reference site).
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\Abstract{We present \pkg{ggmcmc} for MCMC analysis "
            r"\citep{xfim:2016:jss}.}" "\n"
            r"\begin{document}" "\n"
            r"We discuss \pkg{ggmcmc} extensively below." "\n"
            r"\end{document}" "\n"
        )
        assert run_rule(jss_cite_002, src) == []

    def test_abstract_without_cite_does_not_cover_body_mention(self, run_rule):
        # The existing convention: \Abstract{} alone (without an inline
        # \citep) does NOT satisfy CITE-002 for the body. The body
        # mention still needs its own citation.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\Abstract{We present \pkg{ggmcmc} for MCMC analysis.}" "\n"
            r"\begin{document}" "\n"
            r"We discuss \pkg{ggmcmc} extensively below." "\n"
            r"\end{document}" "\n"
        )
        violations = run_rule(jss_cite_002, src)
        assert len(violations) == 1

    def test_pkg_in_body_after_title_mention_still_flagged(self, run_rule):
        # The title mention is skipped, so the first BODY mention is the
        # first-occurrence and must have a citation.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\title{Working with \pkg{rstan}}" "\n"
            r"\begin{document}" "\n"
            r"We use \pkg{rstan} extensively." "\n"
            r"\end{document}" "\n"
        )
        violations = run_rule(jss_cite_002, src)
        assert len(violations) == 1

    def test_citation_in_prev_paragraph_still_flagged(self, run_rule):
        # Blank line BEFORE \pkg means the cite in the prior paragraph does
        # not satisfy the "same paragraph" rule.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"See \citep{Wood:2006}." "\n\n"
            r"We use \pkg{mgcv}." "\n"
            r"\end{document}" "\n"
        )
        violations = run_rule(jss_cite_002, src)
        assert len(violations) == 1

    def test_empty_tex_no_violations(self, tmp_path: Path):
        from texlint.api import ParsedTexFile
        p = tmp_path / "empty.tex"
        p.write_text("", encoding="utf-8")
        tex = ParsedTexFile(path=p, source="", nodes=(), walker=None, violations=())
        doc = ParsedDocument(tex_files=(tex,))
        assert list(check_jss_cite_002(doc, ToolConfig())) == []


# ---------------------------------------------------------------------------
# JSS-CITE-003 — (\cite{...}) bracket-in-bracket
# ---------------------------------------------------------------------------

class TestCite003:
    def test_positive(self, run_rule):
        bad = (FIXTURE_DIR / "JSS-CITE-003-bad.tex").read_text(encoding="utf-8")
        violations = run_rule(jss_cite_003, bad)
        assert len(violations) == 1
        v = violations[0]
        assert v.rule_id == "JSS-CITE-003"
        assert v.severity == Severity.WARNING

    def test_good_fixture_no_violation(self, run_rule):
        good = (FIXTURE_DIR / "JSS-CITE-003-good.tex").read_text(encoding="utf-8")
        assert run_rule(jss_cite_003, good) == []

    def test_lone_citeyear_in_parens_ok(self, run_rule):
        # ``Author~(\citeyear{X})`` — narrative citation (names in prose,
        # year in parens), not a bracket-in-bracket (recall-corpus
        # HardyWeinberg "Puig, Ginebra and Graffelman~(\citeyear{Puig})").
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}"
            r"as proposed by Puig, Ginebra and Graffelman~(\citeyear{Puig})."
            r"\end{document}"
        )
        assert run_rule(jss_cite_003, src) == []

    def test_handrolled_citep_still_flagged(self, run_rule):
        # ``(\citeauthor{X} \citeyear{X})`` is a hand-rolled \citep — still
        # a bracket-in-bracket, caught via the \citeauthor branch.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}"
            r"the device (\citeauthor{Lindsey} \citeyear{Lindsey})."
            r"\end{document}"
        )
        assert len(run_rule(jss_cite_003, src)) == 1

    def test_cite_without_parens_ok(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"See \cite{Key}." "\n"
            r"\end{document}" "\n"
        )
        assert run_rule(jss_cite_003, src) == []

    def test_citep_in_parens_flagged(self, run_rule):
        # ``(\citep{Key})`` renders as ``((Author Year))`` —
        # bracket-in-bracket. The recommended fix is ``\citealp{}``
        # (cite without inner parens). Updated 2026-06-11 to align with
        # the recall-corpus annotations (DBR.Rnw:124, mdsOpt.ltx:72).
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"Regression models (\citep{Key}) are common." "\n"
            r"\end{document}" "\n"
        )
        violations = run_rule(jss_cite_003, src)
        assert len(violations) == 1
        assert violations[0].rule_id == "JSS-CITE-003"

    def test_cite_first_node_no_prev_sibling(self, run_rule):
        src = r"\cite{Key}"
        assert run_rule(jss_cite_003, src) == []

    def test_cite_last_node_no_next_sibling(self, run_rule):
        src = r"Text before \cite{Key}"
        assert run_rule(jss_cite_003, src) == []

    def test_open_paren_but_no_close(self, run_rule):
        src = r"Before (\cite{Key} rest"
        assert run_rule(jss_cite_003, src) == []

    def test_crlf_blank_line_stops_paragraph_scan(self, run_rule):
        # Regression (eRm.Rnw:572): on a CRLF file a blank line is
        # `\r\n\r\n`, so the paragraph-break guard must not require two
        # *adjacent* `\n`s. A stray `(` in a math paragraph above and a
        # `)` in a paragraph below must NOT pair with a bare `\citep`.
        src = (
            "A display with a paren: $\\frac{exp(x)}{1}$.\r\n"
            "\r\n"
            "A graphical test \\citep{Ra:60} is produced.\r\n"
            "\r\n"
            "Critical items can be eliminated (features).\r\n"
        )
        assert run_rule(jss_cite_003, src) == []

    def test_crlf_real_paren_cite_still_flagged(self, run_rule):
        # The CRLF fix must not suppress a genuine `(\citep{...})`: the
        # enclosing parens are right around the macro in the same line.
        src = (
            "Some text here for context.\r\n"
            "\r\n"
            "Regression models (\\citep{Key}) are common.\r\n"
        )
        violations = run_rule(jss_cite_003, src)
        assert len(violations) == 1
        assert violations[0].rule_id == "JSS-CITE-003"

    def test_lone_citeauthor_in_parens_not_flagged(self, run_rule):
        # `(... \citeauthor{X} ...)` renders the bare author name as a
        # prose noun ("(again using the Lindsey device)") — no year, no
        # doubled bracket. Regression: MM.Rnw:413 etc. bonsai false +ve.
        src = (
            "\\documentclass[article]{jss}\n"
            "\\begin{document}\n"
            "We fit a model (again using the \\citeauthor{lindsey1992} "
            "Poisson device).\n"
            "\\end{document}\n"
        )
        assert run_rule(jss_cite_003, src) == []

    def test_citeauthor_with_citeyear_companion_flagged(self, run_rule):
        # `(\citeauthor{X} \citeyear{X})` is a hand-rolled `\citep`
        # ("(Author year)") and SHOULD be flagged — the lone-author skip
        # must not suppress it. Regression: brms_overview.ltx:63.
        src = (
            "\\documentclass[article]{jss}\n"
            "\\begin{document}\n"
            "Bayesian inference (cf., \\citeauthor{fox2011} "
            "\\citeyear{fox2011}) is used.\n"
            "\\end{document}\n"
        )
        violations = run_rule(jss_cite_003, src)
        assert len(violations) >= 1
        assert all(v.rule_id == "JSS-CITE-003" for v in violations)

    def test_macro_definition_body_not_flagged(self, run_rule):
        # A cite inside a `\def`/`\newcommand` body carries a `#`
        # parameter in its key — a template, not a citation. Regression:
        # lbfgs/Vignette.Rnw:22-23, stm:66.
        src = (
            "\\documentclass[article]{jss}\n"
            "\\def\\citepos#1{\\citeauthor{#1}'s (\\citeyear{#1})}\n"
            "\\begin{document}\n"
            "Text.\n"
            "\\end{document}\n"
        )
        assert run_rule(jss_cite_003, src) == []

    def test_cite_after_macro_no_chars_siblings(self, run_rule):
        # \emph{x}\cite{Key} — the preceding sibling is a macro, not chars,
        # so the open-paren check must return False (line 116/123 branch).
        src = r"\emph{x}\cite{Key}"
        assert run_rule(jss_cite_003, src) == []

    def test_cite_followed_by_macro_no_chars_siblings(self, run_rule):
        # (\cite{Key})\emph{x} ends with macro after cite + close-paren chars;
        # but input here has no open-paren, exercise the non-chars "after" path.
        src = r"(\cite{Key}\emph{x}"
        assert run_rule(jss_cite_003, src) == []

    def test_emits_safe_fix_payload(self, run_rule):
        # Spec 008 follow-up: the rule emits a `Fix` whose byte range
        # covers the bracketed `(\cite{...})` span and whose
        # replacement is the canonical `\citep{...}` form.
        before = (AUTOFIX_DIR / "JSS-CITE-003" / "before.tex").read_text(
            encoding="utf-8"
        )
        violations = run_rule(jss_cite_003, before)
        assert len(violations) == 1
        v = violations[0]
        assert isinstance(v.fix, Fix)
        assert v.fix.confidence == "safe"
        # Span exactly covers `(\cite{Cameron+Trivedi:2013})`.
        assert before[v.fix.start : v.fix.end] == "(\\cite{Cameron+Trivedi:2013})"
        assert v.fix.replacement == "\\citep{Cameron+Trivedi:2013}"

    def test_fix_application_matches_after_fixture(self, run_rule):
        # Apply the fix in-memory and assert the result matches the
        # canonical `after.tex` golden byte-for-byte.
        before = (AUTOFIX_DIR / "JSS-CITE-003" / "before.tex").read_text(
            encoding="utf-8"
        )
        after = (AUTOFIX_DIR / "JSS-CITE-003" / "after.tex").read_text(
            encoding="utf-8"
        )
        violations = run_rule(jss_cite_003, before)
        assert len(violations) == 1
        fix = violations[0].fix
        assert isinstance(fix, Fix)
        applied = before[: fix.start] + fix.replacement + before[fix.end :]
        assert applied == after

    def test_fix_preserves_multi_key_argument(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"Foo (\cite{a,b,c}) bar." "\n"
            r"\end{document}" "\n"
        )
        violations = run_rule(jss_cite_003, src)
        assert len(violations) == 1
        fix = violations[0].fix
        assert isinstance(fix, Fix)
        assert fix.replacement == r"\citep{a,b,c}"


# ---------------------------------------------------------------------------
# JSS-CITE-004 — hardcoded (Author, YYYY)
# ---------------------------------------------------------------------------

class TestCite004:
    def test_positive(self, run_rule):
        bad = (FIXTURE_DIR / "JSS-CITE-004-bad.tex").read_text(encoding="utf-8")
        violations = run_rule(jss_cite_004, bad)
        assert len(violations) == 1
        v = violations[0]
        assert v.rule_id == "JSS-CITE-004"
        assert v.severity == Severity.WARNING

    def test_good_fixture_no_violation(self, run_rule):
        good = (FIXTURE_DIR / "JSS-CITE-004-good.tex").read_text(encoding="utf-8")
        assert run_rule(jss_cite_004, good) == []

    def test_month_name_date_not_flagged(self, run_rule):
        # `(April, 1961)` is a point-in-time reference, not an
        # author-year citation. The "surname" slot in the regex
        # matches month names because they're "[A-Z][a-z]+", so
        # we explicitly exempt month tokens.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"The April, 1961 storm caused damage (April, 1961)." "\n"
            r"\end{document}" "\n"
        )
        assert run_rule(jss_cite_004, src) == []

    def test_real_author_still_flagged_after_month_carveout(self, run_rule):
        # Sanity-check: the carve-out is narrow.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"This was shown (Knuth, 1984)." "\n"
            r"\end{document}" "\n"
        )
        assert len(run_rule(jss_cite_004, src)) == 1

    def test_masks_verbatim_env(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{verbatim}" "\n"
            r"(Knuth, 1984)" "\n"
            r"\end{verbatim}" "\n"
            r"\end{document}" "\n"
        )
        assert run_rule(jss_cite_004, src) == []

    def test_masks_code_macro(self, run_rule):
        # Put a citation-shaped string inside \code{} — it must be masked.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"Note \code{(Knuth, 1984)} here." "\n"
            r"\end{document}" "\n"
        )
        assert run_rule(jss_cite_004, src) == []

    def test_masks_url_macro(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"See \url{http://example.org/(Knuth, 1984)}." "\n"
            r"\end{document}" "\n"
        )
        assert run_rule(jss_cite_004, src) == []

    def test_author_et_al_form(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"Previous work (Doe et al., 2018) showed..." "\n"
            r"\end{document}" "\n"
        )
        violations = run_rule(jss_cite_004, src)
        assert len(violations) == 1

    def test_author_and_other_form(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"Later work (Doe and Roe, 2019) extended this." "\n"
            r"\end{document}" "\n"
        )
        violations = run_rule(jss_cite_004, src)
        assert len(violations) == 1

    def test_plain_parenthetical_year_ok(self, run_rule):
        # "In 2020 we..." — no author, no flag.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"In 2020 the method was popular." "\n"
            r"\end{document}" "\n"
        )
        assert run_rule(jss_cite_004, src) == []

    def test_masks_bibliography_env(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{thebibliography}{1}" "\n"
            r"\bibitem{key} (Knuth, 1984) Book title." "\n"
            r"\end{thebibliography}" "\n"
            r"\end{document}" "\n"
        )
        assert run_rule(jss_cite_004, src) == []

    def test_collect_ancestors_returns_none_when_not_found(self):
        # Exercises the "_collect_ancestors returns None" branch via the
        # `ancestors or []` fallback.
        from texlint.journals.jss.rules.citations import _collect_ancestors
        assert _collect_ancestors((), object()) is None

    def test_hardcoded_after_code_group(self, run_rule):
        # \code{x} appears first (its mask-group is traversed but doesn't
        # contain the target); then a hardcoded citation outside — still flagged.
        # Covers the `path.pop()` cleanup after a \code-masked group.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"Use \code{abc} and see (Knuth, 1984) for details." "\n"
            r"\end{document}" "\n"
        )
        violations = run_rule(jss_cite_004, src)
        assert len(violations) == 1

    def test_collect_ancestors_skips_macro_without_nodeargd(self):
        # Covers the `argd is None` branch in _collect_ancestors.
        from pylatexenc.latexwalker import LatexMacroNode

        from texlint.journals.jss.rules.citations import _collect_ancestors

        class FakeMacro(LatexMacroNode):
            def __init__(self):  # type: ignore[no-untyped-def]
                pass

        fake = FakeMacro()
        assert _collect_ancestors((fake,), object()) is None

    def test_empty_tex_no_violations(self, tmp_path: Path):
        from texlint.api import ParsedTexFile
        p = tmp_path / "empty.tex"
        p.write_text("", encoding="utf-8")
        tex = ParsedTexFile(path=p, source="", nodes=(), walker=None, violations=())
        doc = ParsedDocument(tex_files=(tex,))
        assert list(check_jss_cite_004(doc, ToolConfig())) == []
