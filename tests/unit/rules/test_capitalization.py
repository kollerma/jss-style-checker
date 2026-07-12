"""Tests for JSS capitalization rules — 100% branch coverage target."""

from __future__ import annotations

from pathlib import Path

from texlint.api import ParsedDocument, ParsedTexFile, ToolConfig
from texlint.journals.jss.rules.capitalization import (
    check_jss_cap_001,
    check_jss_cap_002,
    check_jss_cap_004,
    jss_cap_001,
    jss_cap_002,
    jss_cap_004,
    rules,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "violations" / "capitalization"


def _tex(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_rules_tuple_has_three_rules():
    assert len(rules) == 3


def test_rules_tuple_ids():
    # JSS-CAP-003 was retired 2026-07-04 (see catalogue.yaml).
    assert {r.id for r in rules} == {"JSS-CAP-001", "JSS-CAP-002", "JSS-CAP-004"}


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

    def test_lowercase_first_keyword_ok(self, run_rule):
        # A fully-lowercase keyword list is the journal's published
        # convention (article.tex only asks for sentence case, i.e. no
        # Title Case across entries). \Keywords{robust statistics, R}
        # must NOT be flagged — CAP-004 no longer demands a leading
        # capital (F5, narrowing).
        src = r"\Keywords{robust statistics, R}"
        assert run_rule(jss_cap_004, src) == []

    def test_lowercase_first_keyword_multiword_ok(self, run_rule):
        # Lowercase first word with lowercase remaining entries: sentence
        # case is satisfied even without a leading capital.
        src = r"\Keywords{ternary plot, Q-Q plot, chi-square test}"
        assert run_rule(jss_cap_004, src) == []

    def test_title_case_across_entries_still_flagged(self, run_rule):
        # The retained defect: a non-first word capitalised within an
        # entry (Title Case) is still a sentence-case violation.
        src = r"\Keywords{robust statistics, Random Forests}"
        assert len(run_rule(jss_cap_004, src)) == 1

    def test_capitalised_first_keyword_silent(self, run_rule):
        src = r"\Keywords{Ternary plot, Q-Q plot, chi-square test}"
        assert run_rule(jss_cap_004, src) == []

    def test_markup_wrapped_first_keyword_silent(self, run_rule):
        # A \pkg{}-wrapped first keyword whose remaining entries are
        # lowercase keeps its lowercase package-name case.
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
        check_jss_cap_004,
    ):
        assert list(check(doc, ToolConfig())) == []
