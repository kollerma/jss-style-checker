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

    def test_skip_citation_key(self, run_rule):
        # A BibTeX key like ``R:2019`` inside \citep/\citet is not prose —
        # the leading ``R`` must not be flagged as an unwrapped language name.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"See \citep{R:2019} and \citet{R:Chambers:1998}." "\n"
            r"\end{document}"
        )
        assert run_rule(jss_markup_001, src) == []

    def test_flag_prose_R_alongside_citation_key(self, run_rule):
        # The bare prose ``R`` still fires; the ``R`` in the cite key does not.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"We use R for this \citep{R:2019}." "\n"
            r"\end{document}"
        )
        assert len(run_rule(jss_markup_001, src)) == 1

    def test_flag_prose_in_citation_optional_arg(self, run_rule):
        # Only the mandatory {key} of a citation is a BibTeX key; the
        # optional [prefix]/[postfix] arguments are prose, so a language
        # name there IS still flagged (``\citep[R package by][]{key}``).
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"See \citep[R package by][]{smith2020}." "\n"
            r"\end{document}"
        )
        assert len(run_rule(jss_markup_001, src)) == 1

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


# ---------------------------------------------------------------------------
# JSS-MARKUP-001 — context guards from labelled corpus FPs (iter-78+)
# ---------------------------------------------------------------------------


def _wrap(body: str) -> str:
    return (
        "\\documentclass[article]{jss}\n"
        "\\begin{document}\n"
        f"{body}\n"
        "\\end{document}"
    )


class TestMarkup001ContextGuards:
    """Each guard has a false-positive case (silent) and a nearby
    true-positive case (still fires) so precision gains never come
    from recall collapse."""

    # -- macro-definition lines ------------------------------------- #

    def test_macro_def_line_silent(self, run_rule):
        src = _wrap("\\def \\calC {\\mathcal C}\n\\newcolumntype{C}[1]{>{\\centering}p{#1}}")
        assert run_rule(jss_markup_001, src) == []

    def test_prose_after_macro_def_still_fires(self, run_rule):
        src = _wrap("\\def \\calC {\\mathcal C}\nWe implement it in R for speed.")
        assert len(run_rule(jss_markup_001, src)) == 1

    # -- macro-definition BODIES (head not at line start / multi-line) - #
    # The line-start guard above misses defs that are indented behind
    # other content or split across lines; the body-scope guard catches
    # the language letters inside their argument/body regardless.

    def test_def_body_letter_not_at_line_start_silent(self, run_rule):
        # ``\def`` behind other content on the same line.
        src = _wrap("Preamble \\def\\R{the R value here}")
        assert run_rule(jss_markup_001, src) == []

    def test_newcommand_body_letter_silent(self, run_rule):
        src = _wrap("\\@ifundefined{Rx}{\\newcommand{\\Rx}{use R here}}{}")
        assert run_rule(jss_markup_001, src) == []

    def test_newcolumntype_name_letter_silent(self, run_rule):
        src = _wrap("Text before \\newcolumntype{C}[1]{>{\\centering}p{#1}}")
        assert run_rule(jss_markup_001, src) == []

    def test_declaremathoperator_multiline_body_silent(self, run_rule):
        # Head on one line, letter-bearing body on the next (with a
        # ``%`` comment continuation) — still inside the def body.
        src = _wrap("\\DeclareMathOperator%\n{\\Rop}{R}")
        assert run_rule(jss_markup_001, src) == []

    def test_multiline_newcommand_body_silent(self, run_rule):
        src = _wrap("\\newcommand{\\Rp}%\n{written in R code}")
        assert run_rule(jss_markup_001, src) == []

    def test_bare_letter_after_def_body_still_fires(self, run_rule):
        # Regression guard: a genuine bare ``R`` in ordinary prose that
        # merely FOLLOWS a definition (outside its braces) must still fire.
        src = _wrap("Preamble \\def\\Q{q}\nWe rewrote the core in R for speed.")
        assert len(run_rule(jss_markup_001, src)) == 1

    # -- CRAN expansion: NOT guarded ----------------------------------- #

    def test_cran_expansion_fires(self, run_rule):
        # The hand-annotated recall corpus plants this phrase as a
        # genuine violation (CARBayesST:441); the AI precision labels
        # disagree with each other on it. Ground truth wins.
        src = _wrap("Available from the Comprehensive R Archive Network site.")
        assert len(run_rule(jss_markup_001, src)) == 1

    def test_bare_r_near_cran_still_fires(self, run_rule):
        src = _wrap("CRAN hosts R packages.")
        assert len(run_rule(jss_markup_001, src)) == 1

    # -- eponym / statistic letters ----------------------------------- #

    def test_possessive_eponym_silent(self, run_rule):
        src = _wrap("We compare Hubert's C with the gap statistic.")
        assert run_rule(jss_markup_001, src) == []

    def test_index_follower_silent(self, run_rule):
        src = _wrap("the Harell C index measures concordance")
        assert run_rule(jss_markup_001, src) == []

    def test_c_steps_silent(self, run_rule):
        src = _wrap("iteratively improve via C steps until convergence")
        assert run_rule(jss_markup_001, src) == []

    def test_plain_c_language_still_fires(self, run_rule):
        src = _wrap("rewritten in C for speed")
        assert len(run_rule(jss_markup_001, src)) == 1

    # -- enumeration / label letters ---------------------------------- #

    def test_panel_label_silent(self, run_rule):
        src = _wrap("as shown in panel C of the figure")
        assert run_rule(jss_markup_001, src) == []

    def test_compartment_enumeration_silent(self, run_rule):
        src = _wrap("a single compartment (S, I or R) as well as events")
        assert run_rule(jss_markup_001, src) == []

    def test_letter_list_silent(self, run_rule):
        src = _wrap("the groups A, B, C and D give identical results")
        assert run_rule(jss_markup_001, src) == []

    def test_r_and_python_still_fires_twice(self, run_rule):
        src = _wrap("implementations in R and Python exist")
        assert len(run_rule(jss_markup_001, src)) == 2

    def test_c_or_fortran_still_fires_twice(self, run_rule):
        src = _wrap("without having to write, say, C or Fortran code.")
        assert len(run_rule(jss_markup_001, src)) == 2

    # -- R\&D ---------------------------------------------------------- #

    def test_amp_compound_silent(self, run_rule):
        src = _wrap("patent applications, R\\&D spending and firm size")
        assert run_rule(jss_markup_001, src) == []

    # -- table cells ---------------------------------------------------- #

    def test_lone_table_cell_letter_silent(self, run_rule):
        src = _wrap(
            "\\begin{tabular}{lll}\n"
            "Model & R & S \\\\\n"
            "\\end{tabular}"
        )
        assert run_rule(jss_markup_001, src) == []

    def test_language_in_table_prose_still_fires(self, run_rule):
        src = _wrap(
            "\\begin{tabular}{ll}\n"
            "Implemented & in the R language \\\\\n"
            "\\end{tabular}"
        )
        assert len(run_rule(jss_markup_001, src)) == 1

    # -- path-segment prefix ------------------------------------------- #

    def test_path_prefix_silent(self, run_rule):
        src = _wrap("the class is defined in \\emph{R/models.R} files")
        assert run_rule(jss_markup_001, src) == []


class TestMarkup001GuardRecallProtection:
    """Surface forms one refinement away from the guards — all must
    still fire (sourced from labelled TPs the first guard draft
    swallowed)."""

    def test_slash_pair_r_s_still_fires(self, run_rule):
        src = _wrap("conversions between DBMS data types and R/S objects")
        assert len(run_rule(jss_markup_001, src)) >= 1

    def test_slash_pair_c_cpp_still_fires(self, run_rule):
        src = _wrap("commercial C/C++ applications and RDBMS")
        assert len(run_rule(jss_markup_001, src)) >= 1

    def test_pair_r_and_s_still_fires(self, run_rule):
        # NB: lone "S" is not in the LANGUAGES catalogue; the "R" of
        # the pair is the token at stake here.
        src = _wrap("the mapping is straightforward in R and S, but slow")
        assert len(run_rule(jss_markup_001, src)) == 1

    def test_label_word_with_colon_still_fires(self, run_rule):
        src = _wrap("Sightability Models: R SightabilityModel Package")
        assert len(run_rule(jss_markup_001, src)) >= 1

    def test_language_chain_without_label_word_still_fires(self, run_rule):
        # Identical surface form to a label enumeration, but no label
        # word nearby — these are languages (DBI-proposal).
        src = _wrap("self-contained tools (R, S, and C APIs) would be")
        assert len(run_rule(jss_markup_001, src)) >= 1


class TestMarkup003OptionValueGuard:
    """R sentinels that are the RHS of a key=value option (LaTeX optional
    args, knitr chunk options) are not bare prose — must not fire."""

    def test_includegraphics_clip_true_silent(self, run_rule):
        src = _wrap("See \\includegraphics[width=5cm, clip=TRUE]{fig}.")
        assert run_rule(jss_markup_003, src) == []

    def test_spaced_option_value_silent(self, run_rule):
        src = _wrap("Plot \\includegraphics[trim = 5 5, clip = TRUE]{f}.")
        assert run_rule(jss_markup_003, src) == []

    def test_bare_prose_sentinel_still_fires(self, run_rule):
        src = _wrap("The function returns NULL when the input is empty.")
        assert len(run_rule(jss_markup_003, src)) == 1


class TestMarkup003CustomCodeWrappers:
    """Paper-defined inline-code wrappers (\\def\\cmd{\\lstinline...},
    \\newcommand{\\cmdtxt}[1]{\\texttt{#1}}): tokens inside their USES are
    already code-marked, so the function-call / sentinel detectors must
    not flag them — but the wrapper DEFINITION's \\texttt still fires."""

    PREAMBLE = (
        "\\def\\cmd{\\lstinline[basicstyle=\\ttfamily]}\n"
        "\\newcommand{\\cmdtxt}[1]{\\texttt{#1}}\n"
    )

    def _doc(self, body: str) -> str:
        return (
            "\\documentclass[article]{jss}\n"
            + self.PREAMBLE
            + "\\begin{document}\n" + body + "\n\\end{document}"
        )

    def test_detects_wrapper_names(self):
        from texlint.journals.jss.rules.markup import (
            _custom_code_wrapper_macros,
        )
        names = _custom_code_wrapper_macros(self.PREAMBLE)
        assert names == frozenset({"cmd", "cmdtxt"})

    def test_funccall_inside_cmd_silent(self, run_rule):
        src = self._doc("Compare \\cmd{interp::triangles()} here.")
        # only the \cmdtxt definition's \texttt may fire, not the \cmd use
        out = run_rule(jss_markup_003, src)
        assert all(v.line != 4 for v in out) or out == []  # use line silent
        # no function-call violation for triangles()
        assert not any("triangles" in (v.suggestion or "") for v in out)

    def test_sentinel_inside_cmd_silent(self, run_rule):
        src = self._doc("If \\cmd{TRUE} then smooth.")
        assert not any("TRUE" in (v.suggestion or "") for v in run_rule(jss_markup_003, src))

    def test_funccall_in_plain_prose_still_fires(self, run_rule):
        src = self._doc("Compare interp::triangles() here.")
        assert any("triangles()" in (v.suggestion or "") for v in run_rule(jss_markup_003, src))

    def test_wrapper_definition_texttt_still_fires(self, run_rule):
        # \newcommand{\cmdtxt}[1]{\texttt{#1}} — the def-body \texttt is TP.
        src = self._doc("Body text without code.")
        out = run_rule(jss_markup_003, src)
        assert any(v.rule_id == "JSS-MARKUP-003" for v in out)


class TestMarkup003InvisibleMacros:
    """\\index{} (and \\nomenclature etc.) content is registered, not
    rendered as body text, so MARKUP-003 must not flag \\texttt /
    function calls / sentinels inside it."""

    def test_texttt_inside_index_silent(self, run_rule):
        src = _wrap("\\newcommand{\\fi}[1]{\\code{#1}\\index{\\texttt{#1}}}")
        assert run_rule(jss_markup_003, src) == []

    def test_funccall_inside_index_silent(self, run_rule):
        src = _wrap("\\index{triangles()}")
        assert run_rule(jss_markup_003, src) == []

    def test_sentinel_inside_index_silent(self, run_rule):
        src = _wrap("\\index{NULL}")
        assert run_rule(jss_markup_003, src) == []

    def test_def_body_texttt_still_fires(self, run_rule):
        # No \index here: a code-styling wrapper def is still a TP.
        src = _wrap("\\newcommand{\\cmdtxt}[1]{\\texttt{#1}}")
        assert len(run_rule(jss_markup_003, src)) == 1


class TestMarkup003NonCodeAndContexts:
    """Audit-driven FP guards: \\texttt of email/URL/DOI/numeric-label,
    algorithm-float pseudocode, plain short captions, possessive
    sentinels — without suppressing real code TPs."""

    def test_texttt_email_silent(self, run_rule):
        assert run_rule(jss_markup_003, _wrap("Mail \\texttt{a.b@cran.org}.")) == []

    def test_texttt_url_silent(self, run_rule):
        assert run_rule(jss_markup_003, _wrap("At \\texttt{https://x.org/p}.")) == []

    def test_texttt_doi_silent(self, run_rule):
        assert run_rule(jss_markup_003, _wrap("\\texttt{10.18637/jss.v067.i01}")) == []

    def test_texttt_numeric_label_silent(self, run_rule):
        assert run_rule(jss_markup_003, _wrap("Row \\texttt{13:} here.")) == []

    def test_texttt_r_sequence_still_fires(self, run_rule):
        # 1:10 is an R sequence (code), not a label — keep firing.
        assert len(run_rule(jss_markup_003, _wrap("Use \\texttt{1:10}."))) == 1

    def test_algorithm_pseudocode_silent(self, run_rule):
        src = _wrap("\\begin{algorithmic}\n\\STATE biclust(BCCC())\n\\end{algorithmic}")
        assert run_rule(jss_markup_003, src) == []

    def test_caption_short_optarg_silent(self, run_rule):
        src = _wrap("\\begin{table}\n\\caption[Args of texreg() here]{\\code{x}}\n\\end{table}")
        assert not any("texreg" in (v.suggestion or "") for v in run_rule(jss_markup_003, src))

    def test_possessive_NA_silent(self, run_rule):
        assert run_rule(jss_markup_003, _wrap("There are no NA's left.")) == []

    def test_body_texttt_still_fires(self, run_rule):
        assert len(run_rule(jss_markup_003, _wrap("Call \\texttt{configTable}."))) == 1

    def test_bare_null_still_fires(self, run_rule):
        assert len(run_rule(jss_markup_003, _wrap("Returns NULL when empty."))) == 1
