"""Unit tests for the ``citations`` rule category.

Rules:
 * JSS-CITE-001 — ``\\emph`` used where a citation key is meant
 * JSS-CITE-002 — software package mentioned without a nearby citation
 * JSS-CITE-003 — bracket-in-bracket ``(\\cite{...})`` construct
 * JSS-CITE-004 — hardcoded parenthetical ``(Author, YYYY)`` text

Constitution §IX: this module must have 100% branch coverage on
``src/texlint/journals/jss/rules/citations.py``.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from texlint.api import (
    ParsedBibFile,
    ParsedDocument,
    ParsedTexFile,
    ToolConfig,
    Violation,
)
from texlint.core.parser import parse_tex_file
from texlint.journals.jss.rules import citations

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "violations" / "citations"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _rule(rule_id: str):
    return next(r for r in citations.rules if r.id == rule_id)


def _run(rule_id: str, filename: str) -> list[Violation]:
    tex = parse_tex_file(FIXTURES / filename)
    doc = ParsedDocument(tex_files=(tex,))
    return list(_rule(rule_id).check(doc, ToolConfig()))


def _run_src(
    rule_id: str,
    src: str,
    parse_tex_source: Callable[[str], ParsedTexFile],
) -> list[Violation]:
    doc = ParsedDocument(tex_files=(parse_tex_source(src),))
    return list(_rule(rule_id).check(doc, ToolConfig()))


# ===========================================================================
# JSS-CITE-001 — \emph for citation
# ===========================================================================


class TestJssCite001:
    def test_flags_bad(self) -> None:
        violations = _run("JSS-CITE-001", "JSS-CITE-001-bad.tex")
        assert len(violations) == 1
        v = violations[0]
        assert v.rule_id == "JSS-CITE-001"
        assert v.line >= 1
        assert v.column is not None and v.column >= 1

    def test_passes_good(self) -> None:
        assert _run("JSS-CITE-001", "JSS-CITE-001-good.tex") == []

    def test_emph_with_non_bibkey_does_not_flag(self, parse_tex_source) -> None:
        src = r"\documentclass[article]{jss}\begin{document}\emph{important}\end{document}"
        assert _run_src("JSS-CITE-001", src, parse_tex_source) == []

    def test_emph_with_empty_group_does_not_flag(self, parse_tex_source) -> None:
        src = r"\documentclass[article]{jss}\begin{document}\emph{}\end{document}"
        assert _run_src("JSS-CITE-001", src, parse_tex_source) == []

    def test_emph_with_nested_macro_does_not_flag(self, parse_tex_source) -> None:
        # Group contains a macro, not plain chars — arg text is empty.
        src = (
            r"\documentclass[article]{jss}\begin{document}"
            r"\emph{\textit{foo2020}}\end{document}"
        )
        assert _run_src("JSS-CITE-001", src, parse_tex_source) == []

    def test_emph_with_unbraced_arg_does_not_flag(self, parse_tex_source) -> None:
        # pylatexenc binds X as a LatexCharsNode, not a group.
        src = r"\documentclass[article]{jss}\begin{document}\emph X\end{document}"
        assert _run_src("JSS-CITE-001", src, parse_tex_source) == []

    def test_flags_inside_environment(self, parse_tex_source) -> None:
        src = (
            r"\documentclass[article]{jss}\begin{document}"
            r"\begin{itemize}\item See \emph{jones2019}\end{itemize}"
            r"\end{document}"
        )
        assert len(_run_src("JSS-CITE-001", src, parse_tex_source)) == 1

    def test_flags_inside_group(self, parse_tex_source) -> None:
        src = (
            r"\documentclass[article]{jss}\begin{document}"
            r"{\emph{smith2020}}\end{document}"
        )
        assert len(_run_src("JSS-CITE-001", src, parse_tex_source)) == 1

    def test_walker_tolerates_math_nodes(self, parse_tex_source) -> None:
        src = r"\documentclass[article]{jss}\begin{document}$x = 1$\end{document}"
        assert _run_src("JSS-CITE-001", src, parse_tex_source) == []

    def test_bib_only_document_yields_no_violations(self, tmp_path: Path) -> None:
        p = tmp_path / "refs.bib"
        p.write_text("", encoding="utf-8")
        bib = ParsedBibFile(path=p, source="", library=None, violations=())
        doc = ParsedDocument(bib_files=(bib,))
        assert list(_rule("JSS-CITE-001").check(doc, ToolConfig())) == []

    def test_no_violations_when_nodes_empty(self, tmp_path: Path) -> None:
        p = tmp_path / "broken.tex"
        p.write_text("", encoding="utf-8")
        tex = ParsedTexFile(path=p, source="", nodes=(), walker=None, violations=())
        doc = ParsedDocument(tex_files=(tex,))
        assert list(_rule("JSS-CITE-001").check(doc, ToolConfig())) == []


# ===========================================================================
# JSS-CITE-002 — \pkg without nearby citation
# ===========================================================================


class TestJssCite002:
    def test_flags_bad(self) -> None:
        violations = _run("JSS-CITE-002", "JSS-CITE-002-bad.tex")
        assert len(violations) == 1
        v = violations[0]
        assert v.rule_id == "JSS-CITE-002"

    def test_passes_good(self) -> None:
        # \pkg{mgcv} has \citep{Wood:2006} within the same paragraph.
        assert _run("JSS-CITE-002", "JSS-CITE-002-good.tex") == []

    def test_citet_also_satisfies_requirement(self, parse_tex_source) -> None:
        src = (
            r"\documentclass[article]{jss}\begin{document}"
            r"\citet{Wood:2006} wrote \pkg{mgcv}."
            r"\end{document}"
        )
        assert _run_src("JSS-CITE-002", src, parse_tex_source) == []

    def test_citealp_also_satisfies(self, parse_tex_source) -> None:
        src = (
            r"\documentclass[article]{jss}\begin{document}"
            r"We use \pkg{mgcv} \citealp{Wood:2006} here."
            r"\end{document}"
        )
        assert _run_src("JSS-CITE-002", src, parse_tex_source) == []

    def test_only_first_mention_flagged(self, parse_tex_source) -> None:
        # \pkg{mgcv} appears twice without citation — only first flagged.
        src = (
            r"\documentclass[article]{jss}\begin{document}"
            r"We use \pkg{mgcv} and then \pkg{mgcv} again."
            r"\end{document}"
        )
        violations = _run_src("JSS-CITE-002", src, parse_tex_source)
        assert len(violations) == 1

    def test_different_packages_flagged_independently(self, parse_tex_source) -> None:
        src = (
            r"\documentclass[article]{jss}\begin{document}"
            r"We use \pkg{mgcv} and \pkg{quantreg}."
            r"\end{document}"
        )
        assert len(_run_src("JSS-CITE-002", src, parse_tex_source)) == 2

    def test_citation_far_away_does_not_satisfy(self, parse_tex_source) -> None:
        # 600 chars of filler between \pkg and its citation — outside the
        # paragraph window.
        filler = "x " * 300
        src = (
            r"\documentclass[article]{jss}\begin{document}"
            r"\pkg{mgcv}. " + filler + r" \citep{Wood:2006}."
            r"\end{document}"
        )
        assert len(_run_src("JSS-CITE-002", src, parse_tex_source)) == 1

    def test_pkg_without_arg_group_does_not_crash(self, parse_tex_source) -> None:
        # \pkg without a braced argument — the rule shouldn't flag because
        # there's nothing to identify.
        src = (
            r"\documentclass[article]{jss}\begin{document}"
            r"Just \pkg and nothing else."
            r"\end{document}"
        )
        # No crash; either no flag or the rule degrades gracefully.
        _run_src("JSS-CITE-002", src, parse_tex_source)

    def test_pkg_with_empty_arg_does_not_flag(self, parse_tex_source) -> None:
        # \pkg{} — empty braced arg, no package name to identify.
        src = (
            r"\documentclass[article]{jss}\begin{document}"
            r"We use \pkg{} here."
            r"\end{document}"
        )
        assert _run_src("JSS-CITE-002", src, parse_tex_source) == []

    def test_empty_doc_yields_no_violations(self, tmp_path: Path) -> None:
        p = tmp_path / "broken.tex"
        p.write_text("", encoding="utf-8")
        tex = ParsedTexFile(path=p, source="", nodes=(), walker=None, violations=())
        doc = ParsedDocument(tex_files=(tex,))
        assert list(_rule("JSS-CITE-002").check(doc, ToolConfig())) == []


# ===========================================================================
# JSS-CITE-003 — (\cite{...}) bracket-in-bracket
# ===========================================================================


class TestJssCite003:
    def test_flags_bad(self) -> None:
        violations = _run("JSS-CITE-003", "JSS-CITE-003-bad.tex")
        assert len(violations) == 1
        assert violations[0].rule_id == "JSS-CITE-003"

    def test_passes_good(self) -> None:
        assert _run("JSS-CITE-003", "JSS-CITE-003-good.tex") == []

    def test_flags_citet_variant(self, parse_tex_source) -> None:
        src = (
            r"\documentclass[article]{jss}\begin{document}"
            r"Models (\citet{foo2020}) are popular."
            r"\end{document}"
        )
        assert len(_run_src("JSS-CITE-003", src, parse_tex_source)) == 1

    def test_does_not_flag_citep(self, parse_tex_source) -> None:
        # \citep already produces parentheses; no bracket-in-bracket.
        src = (
            r"\documentclass[article]{jss}\begin{document}"
            r"Models \citep{foo2020} are popular."
            r"\end{document}"
        )
        assert _run_src("JSS-CITE-003", src, parse_tex_source) == []

    def test_does_not_flag_cite_without_outer_parens(self, parse_tex_source) -> None:
        src = (
            r"\documentclass[article]{jss}\begin{document}"
            r"Models are described by \cite{foo2020}."
            r"\end{document}"
        )
        assert _run_src("JSS-CITE-003", src, parse_tex_source) == []

    def test_does_not_flag_cite_with_only_opening_paren(
        self, parse_tex_source
    ) -> None:
        src = (
            r"\documentclass[article]{jss}\begin{document}"
            r"Models (see \cite{foo2020} for details."
            r"\end{document}"
        )
        # Missing close paren after cite — no double-bracket construct.
        assert _run_src("JSS-CITE-003", src, parse_tex_source) == []

    def test_cite_at_start_of_document_does_not_crash(self, parse_tex_source) -> None:
        src = r"\documentclass[article]{jss}\begin{document}\cite{foo2020}\end{document}"
        _run_src("JSS-CITE-003", src, parse_tex_source)

    def test_cite_after_macro_with_no_chars_in_between(
        self, parse_tex_source
    ) -> None:
        # \emph{x}\cite{foo} — prev sibling is the \emph macro, not a chars
        # node; _prev_char_ends_with_open_paren must return False.
        src = (
            r"\documentclass[article]{jss}\begin{document}"
            r"\emph{x}\cite{foo2020}\end{document}"
        )
        assert _run_src("JSS-CITE-003", src, parse_tex_source) == []

    def test_cite_followed_by_macro_not_chars(self, parse_tex_source) -> None:
        # "( \cite{foo}\cite{bar})" — prev of the second cite is a macro, not
        # a chars node; and prev of the first cite is the "(" chars node but
        # next of the first cite is the second \cite macro (not chars).
        src = (
            r"\documentclass[article]{jss}\begin{document}"
            r"See (\cite{foo2020}\cite{bar2021})."
            r"\end{document}"
        )
        # Neither cite qualifies: the first has a macro after it, the
        # second has a macro before it.
        assert _run_src("JSS-CITE-003", src, parse_tex_source) == []

    def test_cite_at_end_of_container_has_no_next_sibling(
        self, parse_tex_source
    ) -> None:
        # (\cite{foo} as the last siblings inside the document env — no
        # closing paren before \end{document}.
        src = r"\documentclass[article]{jss}\begin{document}(\cite{foo2020}\end{document}"
        assert _run_src("JSS-CITE-003", src, parse_tex_source) == []

    def test_empty_doc_yields_no_violations(self, tmp_path: Path) -> None:
        p = tmp_path / "broken.tex"
        p.write_text("", encoding="utf-8")
        tex = ParsedTexFile(path=p, source="", nodes=(), walker=None, violations=())
        doc = ParsedDocument(tex_files=(tex,))
        assert list(_rule("JSS-CITE-003").check(doc, ToolConfig())) == []


# ===========================================================================
# JSS-CITE-004 — hardcoded (Author, YYYY) text
# ===========================================================================


class TestJssCite004:
    def test_flags_bad(self) -> None:
        violations = _run("JSS-CITE-004", "JSS-CITE-004-bad.tex")
        assert len(violations) == 1
        assert violations[0].rule_id == "JSS-CITE-004"

    def test_passes_good(self) -> None:
        assert _run("JSS-CITE-004", "JSS-CITE-004-good.tex") == []

    def test_flags_and_pattern(self, parse_tex_source) -> None:
        src = (
            r"\documentclass[article]{jss}\begin{document}"
            r"Following (Cameron and Trivedi, 2013) we extend this..."
            r"\end{document}"
        )
        assert len(_run_src("JSS-CITE-004", src, parse_tex_source)) == 1

    def test_flags_et_al_pattern(self, parse_tex_source) -> None:
        src = (
            r"\documentclass[article]{jss}\begin{document}"
            r"Earlier (Smith et al., 2020) showed this."
            r"\end{document}"
        )
        assert len(_run_src("JSS-CITE-004", src, parse_tex_source)) == 1

    def test_flags_year_suffix(self, parse_tex_source) -> None:
        src = (
            r"\documentclass[article]{jss}\begin{document}"
            r"Earlier (Smith, 2020a) showed this."
            r"\end{document}"
        )
        assert len(_run_src("JSS-CITE-004", src, parse_tex_source)) == 1

    def test_does_not_flag_section_reference(self, parse_tex_source) -> None:
        src = (
            r"\documentclass[article]{jss}\begin{document}"
            r"See (Section 3.2) for details."
            r"\end{document}"
        )
        assert _run_src("JSS-CITE-004", src, parse_tex_source) == []

    def test_does_not_flag_cf_reference(self, parse_tex_source) -> None:
        src = (
            r"\documentclass[article]{jss}\begin{document}"
            r"See (cf. Knuth) for details."
            r"\end{document}"
        )
        assert _run_src("JSS-CITE-004", src, parse_tex_source) == []

    def test_does_not_flag_non_parenthetical_author_year(
        self, parse_tex_source
    ) -> None:
        src = (
            r"\documentclass[article]{jss}\begin{document}"
            r"The work of Knuth 1984 predates this."
            r"\end{document}"
        )
        # No parens around the author-year — not flagged.
        assert _run_src("JSS-CITE-004", src, parse_tex_source) == []

    def test_empty_doc_yields_no_violations(self, tmp_path: Path) -> None:
        p = tmp_path / "broken.tex"
        p.write_text("", encoding="utf-8")
        tex = ParsedTexFile(path=p, source="", nodes=(), walker=None, violations=())
        doc = ParsedDocument(tex_files=(tex,))
        assert list(_rule("JSS-CITE-004").check(doc, ToolConfig())) == []


# ===========================================================================
# Module-level contract
# ===========================================================================


class TestModuleContract:
    def test_rules_tuple_has_four_entries(self) -> None:
        assert len(citations.rules) == 4

    def test_rule_ids_match_catalogue(self) -> None:
        ids = {r.id for r in citations.rules}
        assert ids == {"JSS-CITE-001", "JSS-CITE-002", "JSS-CITE-003", "JSS-CITE-004"}

    def test_all_rules_category_citations(self) -> None:
        for r in citations.rules:
            assert r.category == "citations"

    def test_all_rules_have_check_callable(self) -> None:
        for r in citations.rules:
            assert callable(r.check)
