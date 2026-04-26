"""Tests for JSS citations rules — 100% branch coverage target."""

from __future__ import annotations

from pathlib import Path

from texlint.api import ParsedDocument, Severity, ToolConfig
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

    def test_pkg_inside_plaintitle_not_flagged(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\Plaintitle{Inference with rstan via \pkg{rstan}}" "\n"
            r"\begin{document}" "\n"
            r"\end{document}" "\n"
        )
        assert run_rule(jss_cite_002, src) == []

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

    def test_cite_without_parens_ok(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"See \cite{Key}." "\n"
            r"\end{document}" "\n"
        )
        assert run_rule(jss_cite_003, src) == []

    def test_citep_in_parens_not_flagged(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"Regression models (\citep{Key}) are common." "\n"
            r"\end{document}" "\n"
        )
        assert run_rule(jss_cite_003, src) == []

    def test_cite_first_node_no_prev_sibling(self, run_rule):
        src = r"\cite{Key}"
        assert run_rule(jss_cite_003, src) == []

    def test_cite_last_node_no_next_sibling(self, run_rule):
        src = r"Text before \cite{Key}"
        assert run_rule(jss_cite_003, src) == []

    def test_open_paren_but_no_close(self, run_rule):
        src = r"Before (\cite{Key} rest"
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
