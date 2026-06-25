"""Tests for JSS capitalization rules — 100% branch coverage target."""

from __future__ import annotations

from pathlib import Path

from texlint.api import ParsedDocument, ParsedTexFile, ToolConfig
from texlint.journals.jss.rules.capitalization import (
    check_jss_cap_001,
    check_jss_cap_002,
    check_jss_cap_003,
    check_jss_cap_004,
    jss_cap_001,
    jss_cap_002,
    jss_cap_003,
    jss_cap_004,
    rules,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "violations" / "capitalization"


def _tex(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_rules_tuple_has_four_rules():
    assert len(rules) == 4


def test_rules_tuple_ids():
    assert {r.id for r in rules} == {f"JSS-CAP-00{i}" for i in range(1, 5)}


# ---------------------------------------------------------------------------
# JSS-CAP-001 — title style
# ---------------------------------------------------------------------------


class TestCap001:
    def test_positive(self, run_rule):
        violations = run_rule(jss_cap_001, _tex("JSS-CAP-001-bad.tex"))
        assert len(violations) == 1

    def test_good_silent(self, run_rule):
        assert run_rule(jss_cap_001, _tex("JSS-CAP-001-good.tex")) == []

    def test_no_title_silent(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}\end{document}"
        )
        assert run_rule(jss_cap_001, src) == []

    def test_title_without_group_silent(self, run_rule):
        src = r"\title"
        assert run_rule(jss_cap_001, src) == []

    def test_empty_title_silent(self, run_rule):
        src = r"\title{}"
        assert run_rule(jss_cap_001, src) == []

    def test_title_lowercase_first_word(self, run_rule):
        # Only first word is lowercase, rest capitalised.
        src = r"\title{regression Models in R}"
        assert len(run_rule(jss_cap_001, src)) == 1

    def test_title_own_package_first_word_silent(self, run_rule):
        # The conventional JSS title opens with the paper's own package
        # name in its native lowercase casing. The document wrapping
        # the same name in \pkg{} elsewhere is the signal — NOT the
        # filesystem path (the old cran_<name>/vignettes/ heuristic
        # never matched real submissions).
        src = (
            r"\title{flexsurv: A Platform for Parametric Survival "
            r"Modeling}" "\n"
            r"\begin{document}" "\n"
            r"The \pkg{flexsurv} package does things." "\n"
            r"\end{document}"
        )
        assert run_rule(jss_cap_001, src) == []

    def test_title_own_package_with_digits_silent(self, run_rule):
        # Digit-bearing package names (ggplot2-style) must compare
        # with digits intact.
        src = (
            r"\title{ggplot2: Elegant Graphics for Data Analysis}" "\n"
            r"\begin{document}" "\n"
            r"We extend \pkg{ggplot2} here." "\n"
            r"\end{document}"
        )
        assert run_rule(jss_cap_001, src) == []

    def test_title_lowercase_first_word_without_pkg_corroboration_fires(
        self, run_rule
    ):
        # A lowercase first word that the document never wraps in
        # \pkg{} anywhere is a plain title-case failure.
        src = (
            r"\title{regression: A Platform for Survival Modeling}" "\n"
            r"\begin{document}" "\n"
            r"Some prose." "\n"
            r"\end{document}"
        )
        assert len(run_rule(jss_cap_001, src)) == 1

    def test_title_leading_markup_hyphen_compound_silent(self, run_rule):
        # Reviewer-confirmed FP from cran_ReacTran: ``\proglang{R}-package``
        # is a hyphen-glued compound; the plain-text strip leaves
        # ``-package`` (lowercase) but author-dictated case inside the
        # wrapper acts as the title's first word.
        src = (
            r"\title{\proglang{R}-package \rt: "
            r"Reactive Transport Modelling in \R}"
        )
        assert run_rule(jss_cap_001, src) == []

    def test_title_leading_markup_then_lowercase_still_fires(self, run_rule):
        # Distinguish from cran_CARBayes: ``\pkg{CARBayes} version 6.1.1:
        # ...`` — the post-markup word ``version`` is whitespace-glued,
        # not hyphen-glued, so the title-case violation on ``version``
        # remains a real fail.
        src = (
            r"\title{\pkg{CARBayes} version 6.1.1: "
            r"An \proglang{R} Package for Modelling}"
        )
        assert len(run_rule(jss_cap_001, src)) == 1


# ---------------------------------------------------------------------------
# JSS-CAP-002 — sentence style on sections
# ---------------------------------------------------------------------------


class TestCap002:
    def test_positive(self, run_rule):
        violations = run_rule(jss_cap_002, _tex("JSS-CAP-002-bad.tex"))
        assert len(violations) == 1

    def test_good_silent(self, run_rule):
        assert run_rule(jss_cap_002, _tex("JSS-CAP-002-good.tex")) == []

    def test_section_with_proper_noun_ok(self, run_rule):
        src = r"\section{Regression in R}"
        assert run_rule(jss_cap_002, src) == []

    def test_single_offender_section_title_fires(self, run_rule):
        # ``\section{Models And Statistics}`` — even though "And" is a
        # stopword and only "Statistics" is a non-first non-stopword
        # offender, the JSS sentence-style rule for section titles fires
        # on single-word offenders too. Would render as "Models and
        # Statistics" in title case versus the expected sentence-style
        # "Models and statistics". Updated 2026-06-11 to align with the
        # recall-corpus annotations (DBR/DBR.Rnw:265 "Bayesian
        # Estimation" et al.).
        src = r"\section{Models And Statistics}"
        violations = run_rule(jss_cap_002, src)
        assert len(violations) == 1
        assert violations[0].rule_id == "JSS-CAP-002"

    def test_section_without_group_silent(self, run_rule):
        src = r"\section"
        assert run_rule(jss_cap_002, src) == []


# ---------------------------------------------------------------------------
# JSS-CAP-003 — sentence style on captions
# ---------------------------------------------------------------------------


class TestCap003:
    def test_positive(self, run_rule):
        violations = run_rule(jss_cap_003, _tex("JSS-CAP-003-bad.tex"))
        assert len(violations) == 1

    def test_good_silent(self, run_rule):
        assert run_rule(jss_cap_003, _tex("JSS-CAP-003-good.tex")) == []

    def test_caption_outside_figure_silent(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}\caption{Some Title Case Caption Here.}\end{document}"
        )
        assert run_rule(jss_cap_003, src) == []

    def test_caption_without_group_silent(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{figure}\caption\end{figure}" "\n"
            r"\end{document}"
        )
        assert run_rule(jss_cap_003, src) == []

    def test_hyphen_compound_proper_noun_silent(self, run_rule):
        # Hardy-Weinberg / Bradley-Terry: hyphenated capitalised compounds
        # are treated as a single proper-noun phrase, so a single such
        # compound in an otherwise-sentence-style caption never trips
        # the ≥2-offender threshold.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}\begin{figure}" "\n"
            r"\caption{The parabola represents Hardy-Weinberg equilibrium.}" "\n"
            r"\end{figure}\end{document}"
        )
        assert run_rule(jss_cap_003, src) == []

    def test_adjacent_capitalised_pair_anchored_silent(self, run_rule):
        # "Han Chinese" — Chinese is in the proper-noun list, anchoring
        # the run so Han comes along for free.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}\begin{figure}" "\n"
            r"\caption{Plot of 225 SNPs from a Han Chinese population.}" "\n"
            r"\end{figure}\end{document}"
        )
        assert run_rule(jss_cap_003, src) == []

    def test_plural_abbreviation_silent(self, run_rule):
        # Plurals like SNPs / EOFs / IDs (caps + lowercase 's') are
        # recognised as abbreviations, not as offending capitalisation.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}\begin{figure}" "\n"
            r"\caption{Quality control on SNPs and EOFs across runs.}" "\n"
            r"\end{figure}\end{document}"
        )
        assert run_rule(jss_cap_003, src) == []

    def test_long_capital_run_still_fires(self, run_rule):
        # 4+ consecutive capitalised words is the title-case signal — do
        # NOT collapse to a "proper-noun phrase".
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}\begin{figure}" "\n"
            r"\caption{Distribution Of Random Sample Variables Here.}" "\n"
            r"\end{figure}\end{document}"
        )
        assert len(run_rule(jss_cap_003, src)) == 1

    def test_calendar_months_silent(self, run_rule):
        # Months (full names + common abbreviations) are proper nouns;
        # JSS sentence-style retains their capitalisation. Reproduces
        # the cluster A FPs from cran_seasonal and similar time-series
        # vignettes whose captions enumerate calendar months.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}\begin{figure}" "\n"
            r"\caption{Seasonal component over January, February, March,"
            r" April, May, June, July, August, September, October, November,"
            r" and December.}" "\n"
            r"\end{figure}\end{document}"
        )
        assert run_rule(jss_cap_003, src) == []

    def test_repeated_proper_noun_counted_once(self, run_rule):
        # Same compound twice in a caption shouldn't double-count.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}\begin{figure}" "\n"
            r"\caption{Trajectories from the Rosenzweig-MacArthur model. " "\n"
            r"Right: Rosenzweig-MacArthur model.}" "\n"
            r"\end{figure}\end{document}"
        )
        assert run_rule(jss_cap_003, src) == []

    def test_subfigure_letter_labels_silent(self, run_rule):
        # Reviewer-confirmed FPs from cran_Langevin and cran_bbl: panel
        # labels ``(a)`` / ``(b)`` introducing subfigure descriptions
        # should anchor the post-label word as a sentence-start, the
        # same way ``(2)`` numbering already does. ``(a) Sketch of a
        # stochastic process ... (b) its corresponding ...`` is
        # sentence-style, not title-case.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}\begin{figure}" "\n"
            r"\caption{(a) Sketch of a stochastic process and (b) its"
            r" corresponding density.}" "\n"
            r"\end{figure}\end{document}"
        )
        assert run_rule(jss_cap_003, src) == []

    def test_subfigure_label_after_period_silent(self, run_rule):
        # Variant from cran_bbl: caption opens with a sentence, then
        # ``\n(a) Cross-validation ... (b-d) Comparison ...``. The
        # period anchors the next sub-sentence and the parens-letter
        # is transparent as numbering.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}\begin{figure}" "\n"
            r"\caption{Inference using simulated data. (a) Cross-validation"
            r" output. (b-d) Comparison of true and inferred parameters.}" "\n"
            r"\end{figure}\end{document}"
        )
        assert run_rule(jss_cap_003, src) == []

    def test_boundary_after_inner_punct_still_fires(self, run_rule):
        # Reviewer-confirmed FP from cran_robustlmm and cran_poweRlaw:
        # a caption containing ``... (solid: mean, dashed: quartiles).
        # Plot corresponds to ...`` should treat ``Plot`` as a
        # sentence-start. Earlier the greedy ``(\S+)`` capture in the
        # boundary regex consumed the trailing ``).`` and the final
        # period was no longer available to anchor the next clause.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}\begin{figure}" "\n"
            r"\caption{Mean values across designs. The yellow line shows"
            r" the classical fit (solid: mean, dashed: quartiles). Plot"
            r" corresponds to the figure.}" "\n"
            r"\end{figure}\end{document}"
        )
        # ``Mean`` is the first word; ``Plot`` is post-period sentence-
        # start; no other capitalised offenders remain → silent.
        assert run_rule(jss_cap_003, src) == []


# ---------------------------------------------------------------------------
# JSS-CAP-004 — Keywords sentence case
# ---------------------------------------------------------------------------


class TestCap004:
    def test_positive(self, run_rule):
        violations = run_rule(jss_cap_004, _tex("JSS-CAP-004-bad.tex"))
        assert len(violations) == 1

    def test_good_silent(self, run_rule):
        assert run_rule(jss_cap_004, _tex("JSS-CAP-004-good.tex")) == []

    def test_proper_noun_in_keyword_ok(self, run_rule):
        src = r"\Keywords{R packages, statistical software}"
        assert run_rule(jss_cap_004, src) == []

    def test_keywords_without_group_silent(self, run_rule):
        src = r"\Keywords"
        assert run_rule(jss_cap_004, src) == []

    def test_single_word_keywords_ok(self, run_rule):
        src = r"\Keywords{JSS, MASS, R}"
        assert run_rule(jss_cap_004, src) == []

    def test_lowercase_first_keyword_flagged(self, run_rule):
        # Keywords are sentence case: the first word of the list is
        # capitalised (recall-corpus HardyWeinberg:30).
        src = r"\Keywords{ternary plot, Q-Q plot, chi-square test}"
        assert len(run_rule(jss_cap_004, src)) == 1

    def test_capitalised_first_keyword_silent(self, run_rule):
        src = r"\Keywords{Ternary plot, Q-Q plot, chi-square test}"
        assert run_rule(jss_cap_004, src) == []

    def test_markup_wrapped_first_keyword_silent(self, run_rule):
        # A \pkg{}-wrapped first keyword keeps its lowercase package-name
        # case — don't demand a leading capital.
        src = r"\Keywords{\pkg{ggplot2}, visualization, R}"
        assert run_rule(jss_cap_004, src) == []

    def test_plainkeywords_never_fires(self, run_rule):
        # \Plainkeywords is PDF metadata the reader never sees — out of
        # scope for CAP-004 even with a lowercase first keyword.
        src = r"\Plainkeywords{ternary plot, q-q plot, chi-square test}"
        assert run_rule(jss_cap_004, src) == []

    def test_stopword_capitalised_not_offender(self, run_rule):
        src = r"\Keywords{Statistics And things}"
        # The "And" is stopword → no offender; single-offender threshold not met.
        assert run_rule(jss_cap_004, src) == []

    def test_allcaps_abbrev_in_keyword_silent(self, run_rule):
        # Reviewer-confirmed FPs from cran_shrinkTVP, cran_stochvol,
        # cran_simecol: parenthesised all-caps abbreviations like
        # (MCMC), (TVP), (OOP), GARCH, SV are conventionally written
        # upper-case even inside sentence-style keyword entries.
        src = (
            r"\Keywords{Bayesian inference, Markov chain Monte Carlo (MCMC),"
            r" time-varying parameter (TVP) models, GARCH, SV}"
        )
        assert run_rule(jss_cap_004, src) == []

    def test_hyphenated_proper_noun_keyword_silent(self, run_rule):
        # Reviewer-confirmed FP from cran_hyper2: 'Bradley-Terry' (the
        # ranking model named after Bradley and Terry) is a single
        # proper-noun compound and shouldn't be split into two cap
        # tokens by the keyword check.
        src = r"\Keywords{Dirichlet distribution, Bradley-Terry}"
        assert run_rule(jss_cap_004, src) == []


def test_group_plain_text_skips_markup_macros(parse_tex_source):
    from pylatexenc.latexwalker import LatexGroupNode

    from texlint.journals.jss.rules.capitalization import _group_plain_text
    # \pkg{MASS} is excluded — package names have their own case
    # convention and shouldn't be scanned for title/sentence style.
    # See docstring on _group_plain_text.
    tex = parse_tex_source(r"{prefix \pkg{MASS} suffix}")
    group = next(n for n in tex.nodes if isinstance(n, LatexGroupNode))
    text = _group_plain_text(group)
    assert "MASS" not in text
    assert "prefix" in text
    assert "suffix" in text


def test_is_capitalised_word_no_letters():
    from texlint.journals.jss.rules.capitalization import _is_capitalised_word
    assert _is_capitalised_word("123") is True
    assert _is_capitalised_word("") is True


def test_first_group_arg_no_nodeargd():
    from pylatexenc.latexwalker import LatexMacroNode

    from texlint.journals.jss.rules.capitalization import _first_group_arg

    class FakeMacro(LatexMacroNode):
        def __init__(self):  # type: ignore[no-untyped-def]
            pass

    fake = FakeMacro()
    assert _first_group_arg(fake, (fake,), 0) is None


def test_first_group_arg_skips_optional_bracket(parse_tex_source):
    from pylatexenc.latexwalker import LatexMacroNode

    from texlint.journals.jss.rules.capitalization import _first_group_arg
    tex = parse_tex_source(r"\section[opts]{title}")
    mac = next(n for n in tex.nodes if isinstance(n, LatexMacroNode))
    idx = tex.nodes.index(mac)
    arg = _first_group_arg(mac, tex.nodes, idx)
    # The returned group should be the mandatory {title}, not [opts].
    assert arg is not None


def test_cap_001_title_no_group_silent():
    from pathlib import Path as P

    from pylatexenc.latexwalker import LatexMacroNode

    class FakeArgd:
        argnlist = ()

    class FakeMacro(LatexMacroNode):
        def __init__(self):  # type: ignore[no-untyped-def]
            self.macroname = "title"
            self.pos = 0
            self.nodeargd = FakeArgd()

    fake = FakeMacro()
    tex = ParsedTexFile(
        path=P("/tmp/x.tex"), source="", nodes=(fake,), walker=None
    )
    doc = ParsedDocument(tex_files=(tex,))
    assert list(check_jss_cap_001(doc, ToolConfig())) == []


def test_cap_002_section_no_group_silent():
    from pathlib import Path as P

    from pylatexenc.latexwalker import LatexMacroNode

    class FakeArgd:
        argnlist = ()

    class FakeMacro(LatexMacroNode):
        def __init__(self):  # type: ignore[no-untyped-def]
            self.macroname = "section"
            self.pos = 0
            self.nodeargd = FakeArgd()

    fake = FakeMacro()
    tex = ParsedTexFile(
        path=P("/tmp/x.tex"), source="", nodes=(fake,), walker=None
    )
    doc = ParsedDocument(tex_files=(tex,))
    assert list(check_jss_cap_002(doc, ToolConfig())) == []


def test_sentence_style_offender_skips_non_letter_words(run_rule):
    src = r"\section{Models 123 With Numbers}"
    # "123" no letters → bare empty → continue; "With" is stopword;
    # "Numbers" is the sole capitalised offender. Under the
    # corpus-aligned single-offender threshold (CAP-002), this still
    # fires — single-word offenders in section titles are real
    # sentence-case violations.
    violations = run_rule(jss_cap_002, src)
    assert len(violations) == 1
    assert violations[0].rule_id == "JSS-CAP-002"


def test_cap_004_keyword_proper_noun_skipped(run_rule):
    src = r"\Keywords{The MASS package, other stuff}"
    assert run_rule(jss_cap_004, src) == []


def test_cap_004_keyword_non_letter_word(run_rule):
    src = r"\Keywords{Basic 123 test, other stuff}"
    assert run_rule(jss_cap_004, src) == []


def test_empty_tex_silent():
    tex = ParsedTexFile(path=Path("/tmp/x.tex"), source="", nodes=(), walker=None)
    doc = ParsedDocument(tex_files=(tex,))
    for check in (
        check_jss_cap_001, check_jss_cap_002,
        check_jss_cap_003, check_jss_cap_004,
    ):
        assert list(check(doc, ToolConfig())) == []
