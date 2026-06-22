"""Tests for JSS markup rules — 100% branch coverage target."""

from __future__ import annotations

from pathlib import Path

from texlint.api import Fix, ParsedDocument, ParsedTexFile, ToolConfig
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
AUTOFIX_DIR = REPO_ROOT / "tests" / "fixtures" / "auto-fix"
AUTOFIX_MARKUP_001 = AUTOFIX_DIR / "JSS-MARKUP-001"


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

    def test_skip_language_in_cite_key(self, run_rule):
        # `\citep{R:2018}` / `\cite{R}` — the language name is part of a
        # bibliography key, not a bare prose mention. A bare prose `R`
        # on the same line still fires.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"Statistical computing \citep{R:2018} with \cite{R}." "\n"
            r"\end{document}"
        )
        assert run_rule(jss_markup_001, src) == []

    def test_language_in_cite_key_but_prose_mention_still_flagged(
        self, run_rule
    ):
        # The cite-key guard must not suppress a genuine prose mention.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"We use R \citep{R:2018} for the analysis." "\n"
            r"\end{document}"
        )
        # Exactly the bare prose `R` fires, not the `R:2018` cite key.
        assert len(run_rule(jss_markup_001, src)) == 1

    def test_skip_pandoc_cite_key(self, run_rule):
        # `[@R-knitr]` — a pandoc / R Markdown citation key, not prose.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"The knitr package [@R-knitr] is an alternative." "\n"
            r"\end{document}"
        )
        assert run_rule(jss_markup_001, src) == []

    def test_skip_package_in_cite_key(self, run_rule):
        # `\citep{MASS}` — the package name is a bibliography key.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"Standard CLMs \citep{MASS} are implemented." "\n"
            r"\end{document}"
        )
        assert run_rule(jss_markup_002, src) == []

    def test_skip_initial(self, run_rule):
        # 'J. R. Statistical' — R is an initial, not the language.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"J. R. Statistical Society paper." "\n"
            r"\end{document}"
        )
        assert run_rule(jss_markup_001, src) == []

    def test_skip_emphasised_acronym_initial(self, run_rule):
        # \emph{C}ombination — the emphasised first letter of a word
        # (acronym device, e.g. CUB), not the C language (recall-corpus
        # CUB.Rnw:123/208 false positives).
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"the \emph{C}ombination of a \emph{U}niform model." "\n"
            r"\end{document}"
        )
        assert run_rule(jss_markup_001, src) == []

    def test_emphasised_standalone_language_still_fires(self, run_rule):
        # \emph{C} followed by a space is a standalone language mention,
        # not an acronym initial — it should still be flagged.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"written in \emph{C} for speed." "\n"
            r"\end{document}"
        )
        assert len(run_rule(jss_markup_001, src)) == 1

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

    def test_skip_lstlisting(self, run_rule):
        # Regression: lstlisting was neutralised by the parser but
        # missing from the rules' verbatim set, so MARKUP-001/002/003
        # fired (with "safe" auto-fixes) inside code listings.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{lstlisting}" "\n"
            r"library(zoo)" "\n"
            r'result <- Python.call("foo")' "\n"
            r"x = data.frame()" "\n"
            r"\end{lstlisting}" "\n"
            r"\end{document}"
        )
        assert run_rule(jss_markup_001, src) == []
        assert run_rule(jss_markup_002, src) == []
        assert run_rule(jss_markup_003, src) == []

    def test_skip_filename_extension(self, run_rule):
        # `foo.R` / `algo.tex` / `data.table.R` — the trailing letter
        # is a file extension, not a bare language reference.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"See foo.R, algo.tex, and data.table.R for examples." "\n"
            r"\end{document}"
        )
        assert run_rule(jss_markup_001, src) == []

    def test_real_R_mention_still_fires(self, run_rule):
        # Sanity check: prev-char-of-{`.`,`/`} skip must not silence
        # the canonical "use R for this" pattern.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"We use R for the analysis." "\n"
            r"\end{document}"
        )
        assert len(run_rule(jss_markup_001, src)) == 1

    def test_emits_safe_fix_payload(self, run_rule):
        source = (AUTOFIX_MARKUP_001 / "before.tex").read_text(
            encoding="utf-8"
        )
        violations = run_rule(jss_markup_001, source)
        assert len(violations) == 1
        v = violations[0]
        assert isinstance(v.fix, Fix)
        assert v.fix.confidence == "safe"
        # Byte range exactly covers the offending token.
        token = source[v.fix.start : v.fix.end]
        assert token == "Python"
        # Replacement wraps the token in \proglang{}.
        assert v.fix.replacement == "\\proglang{Python}"

    def test_fix_application_matches_after_fixture(self, run_rule):
        source = (AUTOFIX_MARKUP_001 / "before.tex").read_text(
            encoding="utf-8"
        )
        expected = (AUTOFIX_MARKUP_001 / "after.tex").read_text(
            encoding="utf-8"
        )
        violations = run_rule(jss_markup_001, source)
        assert len(violations) == 1
        fix = violations[0].fix
        assert isinstance(fix, Fix)
        rewritten = source[: fix.start] + fix.replacement + source[fix.end :]
        assert rewritten == expected

    def test_skip_listings_option_value(self, run_rule):
        # Reviewer-confirmed FPs from cran_psychotools:
        # ``\lstinputlisting[language=R, ...]`` — the ``R`` token is
        # the value of the listings ``language=`` option, not a bare
        # prose mention.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\lstinputlisting[firstline=9, lastline=34, "
            r"basicstyle=\ttfamily, language=R, numbers=left]{file.R}" "\n"
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

    def test_sandwich_estimator_not_flagged(self, run_rule):
        # "sandwich estimator" is a statistical method, not the
        # `sandwich` R package — disambiguate on the next word.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"We use the sandwich estimator for robust SEs." "\n"
            r"\end{document}"
        )
        assert run_rule(jss_markup_002, src) == []

    def test_sandwich_method_not_flagged(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"The sandwich method computes a robust covariance." "\n"
            r"\end{document}"
        )
        assert run_rule(jss_markup_002, src) == []

    def test_sandwich_alone_still_flagged(self, run_rule):
        # Bare "sandwich" not followed by a disambiguator IS the
        # package reference — keep flagging it.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"We rely on sandwich for robust inference." "\n"
            r"\end{document}"
        )
        assert len(run_rule(jss_markup_002, src)) == 1

    def test_sandwich_method_followers_not_flagged(self, run_rule):
        # Reviewer-confirmed FPs from cran_effects, cran_sandwich,
        # cran_clifford: "sandwich coefficient", "sandwich product",
        # "sandwich formula", "sandwich variance" are statistical-method
        # usages of the sandwich estimator, not references to the
        # `sandwich` R package.
        for follower in (
            "coefficient", "coefficients", "covariances",
            "variance", "variances", "formula", "formulae",
            "formulas", "product", "products", "meat", "bread",
        ):
            src = (
                r"\documentclass[article]{jss}" "\n"
                r"\begin{document}" "\n"
                f"The sandwich {follower} is robust.\n"
                r"\end{document}"
            )
            assert run_rule(jss_markup_002, src) == [], follower

    def test_emits_safe_fix_payload(self, run_rule):
        # Spec 008 follow-up: each violation carries a Fix(...) payload
        # whose byte range covers the bare package token and whose
        # replacement wraps the token in ``\pkg{...}``.
        before = (AUTOFIX_DIR / "JSS-MARKUP-002" / "before.tex").read_text(
            encoding="utf-8"
        )
        violations = run_rule(jss_markup_002, before)
        assert len(violations) == 1
        v = violations[0]
        assert isinstance(v.fix, Fix)
        assert v.fix.confidence == "safe"
        # Span exactly covers the bare ``MASS`` token.
        assert before[v.fix.start : v.fix.end] == "MASS"
        assert v.fix.replacement == r"\pkg{MASS}"

    def test_fix_application_matches_after_fixture(self, run_rule):
        # Apply the fix in-memory and assert the rewritten bytes match
        # the canonical ``after.tex`` golden byte-for-byte.
        before = (AUTOFIX_DIR / "JSS-MARKUP-002" / "before.tex").read_text(
            encoding="utf-8"
        )
        after = (AUTOFIX_DIR / "JSS-MARKUP-002" / "after.tex").read_text(
            encoding="utf-8"
        )
        violations = run_rule(jss_markup_002, before)
        assert len(violations) == 1
        fix = violations[0].fix
        assert isinstance(fix, Fix)
        applied = before[: fix.start] + fix.replacement + before[fix.end :]
        assert applied == after
        # Self-verification: re-linting the rewritten bytes does NOT
        # re-trigger MARKUP-002 on the now-wrapped token.
        assert run_rule(jss_markup_002, applied) == []


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

    # --- R sentinel value coverage (NULL / NA / TRUE / FALSE) -------------

    def test_bare_null_in_prose_flagged(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"The default is NULL and may be replaced." "\n"
            r"\end{document}"
        )
        violations = run_rule(jss_markup_003, src)
        assert len(violations) == 1
        assert violations[0].rule_id == "JSS-MARKUP-003"

    def test_sentinel_in_includegraphics_option_not_flagged(self, run_rule):
        # `\includegraphics[clip = TRUE]{...}` — TRUE is a graphics
        # boolean option, not a bare R sentinel in prose. Regression:
        # hetGP_vignette.Rnw:1632.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\includegraphics[width=0.49\textwidth, trim = 3 5 5 5, "
            r"clip = TRUE]{./figure/x.pdf}" "\n"
            r"\end{document}"
        )
        assert run_rule(jss_markup_003, src) == []

    def test_bare_na_true_false_in_prose_flagged(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"Set the flag to TRUE; missing entries become NA, not FALSE."
            "\n"
            r"\end{document}"
        )
        violations = run_rule(jss_markup_003, src)
        # TRUE, NA, FALSE → 3 hits.
        assert len(violations) == 3
        assert all(v.rule_id == "JSS-MARKUP-003" for v in violations)

    def test_na_subtypes_in_prose_flagged(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"Use NA_integer_ rather than NA_real_ for counts." "\n"
            r"\end{document}"
        )
        violations = run_rule(jss_markup_003, src)
        # NA_integer_, NA_real_ → 2 hits (no separate NA hits because the
        # tokenizer eats the underscored tail).
        assert len(violations) == 2

    def test_sentinel_inside_code_macro_skipped(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"The default is \code{NULL}." "\n"
            r"\end{document}"
        )
        assert run_rule(jss_markup_003, src) == []

    def test_substring_does_not_match(self, run_rule):
        # ``ANNULLED`` contains the substring ``NULL`` but the
        # word-boundary tokenizer must not flag it; same for ``NAtural``
        # / ``TRUEness`` / ``FALSEhood``.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"Their NAtural ANNULLED TRUEness was FALSEhood." "\n"
            r"\end{document}"
        )
        assert run_rule(jss_markup_003, src) == []

    def test_sentinel_inside_math_skipped(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"Let $X = \mathit{NA}$ when missing." "\n"
            r"\end{document}"
        )
        assert run_rule(jss_markup_003, src) == []

    def test_sentinel_inside_verbatim_skipped(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{verbatim}" "\n"
            r"x <- NULL" "\n"
            r"\end{verbatim}" "\n"
            r"\end{document}"
        )
        assert run_rule(jss_markup_003, src) == []

    def test_sentinel_emits_safe_fix(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"The default is NULL." "\n"
            r"\end{document}"
        )
        violations = run_rule(jss_markup_003, src)
        assert len(violations) == 1
        v = violations[0]
        assert v.fix is not None
        assert v.fix.replacement == "\\code{NULL}"
        assert v.fix.confidence == "safe"

    # --- \texttt{...} → \code{...} ---------------------------------------

    def test_texttt_in_prose_flagged(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"The function \texttt{glm} fits a model." "\n"
            r"\end{document}"
        )
        violations = run_rule(jss_markup_003, src)
        assert len(violations) == 1
        assert violations[0].rule_id == "JSS-MARKUP-003"

    def test_texttt_in_math_flagged(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"$y = \beta_1 \texttt{age} + \beta_2 \texttt{nodes}$" "\n"
            r"\end{document}"
        )
        violations = run_rule(jss_markup_003, src)
        # Two \texttt occurrences → 2 hits.
        assert len(violations) == 2

    def test_texttt_in_superscript_label_skipped(self, run_rule):
        # `\hat p^{\texttt{KMW}}` — \texttt is a method-abbreviation label
        # in a superscript, not inline code. Regression: TPmsm.Rnw:382.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"$\hat p_{12}^{\texttt{KMW}}(s,t) = \frac{a}{b}$" "\n"
            r"\end{document}"
        )
        assert run_rule(jss_markup_003, src) == []

    def test_code_alias_com_skipped(self, run_rule):
        # \Com / \Comt are paper-defined \code aliases (TraMineR,
        # WeightedCluster); their content is code, not prose.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\newcommand{\Com}[1]{\code{#1}}" "\n"
            r"\begin{document}" "\n"
            r"The \Com{seqtab()} function summarises the sequences." "\n"
            r"\end{document}"
        )
        assert run_rule(jss_markup_003, src) == []

    def test_texttt_inside_code_skipped(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\code{\texttt{glm}} oddly nested but already wrapped." "\n"
            r"\end{document}"
        )
        assert run_rule(jss_markup_003, src) == []

    def test_texttt_in_verbatim_skipped(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{verbatim}" "\n"
            r"\texttt{not_a_real_macro}" "\n"
            r"\end{verbatim}" "\n"
            r"\end{document}"
        )
        assert run_rule(jss_markup_003, src) == []

    def test_texttt_emits_safe_fix_replacing_macro_name(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"See \texttt{sample}." "\n"
            r"\end{document}"
        )
        violations = run_rule(jss_markup_003, src)
        assert len(violations) == 1
        v = violations[0]
        assert v.fix is not None
        assert v.fix.replacement == "\\code"
        assert v.fix.confidence == "safe"

    # --- \pkg{...()} (function name abused as package) -> \code{...} ------

    def test_pkg_with_parens_flagged(self, run_rule):
        # \pkg{} is for packages, which never contain parentheses; a "()"
        # inside means a function call was wrapped — it belongs in \code{}.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"In \pkg{MASS} the \pkg{polr()} function fits the model." "\n"
            r"\end{document}"
        )
        violations = run_rule(jss_markup_003, src)
        # Only the parenthesised \pkg{polr()} fires; \pkg{MASS} is fine.
        assert len(violations) == 1
        assert "polr()" in violations[0].suggestion
        assert "\\code{polr()}" in violations[0].suggestion

    def test_pkg_with_parens_emits_safe_fix(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}\pkg{lrm()} is available.\end{document}"
        )
        violations = run_rule(jss_markup_003, src)
        assert len(violations) == 1
        v = violations[0]
        assert v.fix is not None
        assert v.fix.replacement == "\\code"
        assert v.fix.confidence == "safe"

    def test_pkg_with_argument_call_flagged(self, run_rule):
        # Non-empty parens (a call with an argument) are still a function.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}\pkg{predict(model)} returns.\end{document}"
        )
        assert len(run_rule(jss_markup_003, src)) == 1

    def test_plain_pkg_silent(self, run_rule):
        # A normal package name (no parens) must not fire.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}We rely on \pkg{data.table} and \pkg{lme4}."
            r"\end{document}"
        )
        assert run_rule(jss_markup_003, src) == []

    def test_pkg_acronym_in_parens_silent(self, run_rule):
        # \pkg{Engine for likelihood-free inference (ELFI)} — the parens
        # hold an acronym in a descriptive name (space before "("), not a
        # function call. Misuse of \pkg{} perhaps, but NOT a code call, so
        # this rule must stay silent (no glued identifier-paren).
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}"
            r"\pkg{Engine for likelihood-free inference (ELFI)} is used."
            r"\end{document}"
        )
        assert run_rule(jss_markup_003, src) == []

    def test_pkg_with_parens_in_verbatim_skipped(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{verbatim}" "\n"
            r"\pkg{polr()}" "\n"
            r"\end{verbatim}" "\n"
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

    def test_emits_safe_fix_payload(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}\section{Some \pkg{foo} title}\end{document}"
        )
        violations = run_rule(jss_markup_004, src)
        assert len(violations) == 1
        v = violations[0]
        assert v.fix is not None
        # 0-length insert at the position immediately before the
        # mandatory ``{...}`` group.
        assert v.fix.start == v.fix.end
        assert v.fix.replacement.startswith("[")
        assert v.fix.replacement.endswith("]")
        assert v.fix.confidence == "safe"


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
