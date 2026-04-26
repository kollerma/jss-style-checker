"""Tests for JSS bibtex rules — 100% branch coverage target."""

from __future__ import annotations

from pathlib import Path

from texlint.api import (
    ParsedBibFile,
    ParsedDocument,
    Severity,
    ToolConfig,
)
from texlint.journals.jss.rules.bibtex import (
    check_jss_bibtex_001,
    check_jss_bibtex_002,
    check_jss_bibtex_004,
    jss_bibtex_001,
    jss_bibtex_002,
    jss_bibtex_003,
    jss_bibtex_004,
    rules,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "violations" / "bibtex"


def _bib_from_fixture(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_rules_tuple_has_four_rules():
    assert len(rules) == 4


def test_rules_tuple_ids():
    assert {r.id for r in rules} == {
        f"JSS-BIBTEX-00{i}" for i in range(1, 5)
    }


# ---------------------------------------------------------------------------
# JSS-BIBTEX-001 — non-empty key
# ---------------------------------------------------------------------------


class TestBibtex001:
    def test_positive(self, run_rule):
        violations = run_rule(
            jss_bibtex_001,
            _bib_from_fixture("JSS-BIBTEX-001-bad.bib"),
            kind="bib",
        )
        assert len(violations) == 1
        assert violations[0].rule_id == "JSS-BIBTEX-001"
        assert violations[0].severity == Severity.ERROR

    def test_good_fixture_silent(self, run_rule):
        assert (
            run_rule(
                jss_bibtex_001,
                _bib_from_fixture("JSS-BIBTEX-001-good.bib"),
                kind="bib",
            )
            == []
        )

    def test_library_none_silent(self, tmp_path: Path):
        broken = ParsedBibFile(
            path=tmp_path / "b.bib", source="", library=None, violations=()
        )
        doc = ParsedDocument(bib_files=(broken,))
        assert list(check_jss_bibtex_001(doc, ToolConfig())) == []


# ---------------------------------------------------------------------------
# JSS-BIBTEX-002 — unique keys
# ---------------------------------------------------------------------------


class TestBibtex002:
    def test_positive(self, run_rule):
        violations = run_rule(
            jss_bibtex_002,
            _bib_from_fixture("JSS-BIBTEX-002-bad.bib"),
            kind="bib",
        )
        # The second occurrence of the duplicated key is reported.
        assert len(violations) == 1
        assert violations[0].rule_id == "JSS-BIBTEX-002"

    def test_good_fixture_silent(self, run_rule):
        assert (
            run_rule(
                jss_bibtex_002,
                _bib_from_fixture("JSS-BIBTEX-002-good.bib"),
                kind="bib",
            )
            == []
        )

    def test_empty_key_not_counted_as_duplicate(self, run_rule):
        # Two entries with empty keys — BIBTEX-001 handles those; BIBTEX-002
        # must NOT flag them as duplicates of each other.
        src = "@article{, year={2020}}\n@article{, year={2021}}\n"
        assert run_rule(jss_bibtex_002, src, kind="bib") == []

    def test_library_none_silent(self, tmp_path: Path):
        broken = ParsedBibFile(
            path=tmp_path / "b.bib", source="", library=None, violations=()
        )
        doc = ParsedDocument(bib_files=(broken,))
        assert list(check_jss_bibtex_002(doc, ToolConfig())) == []


# ---------------------------------------------------------------------------
# JSS-BIBTEX-003 — required fields
# ---------------------------------------------------------------------------


class TestBibtex003:
    def test_positive_article_missing_title_journal(self, run_rule):
        violations = run_rule(
            jss_bibtex_003,
            _bib_from_fixture("JSS-BIBTEX-003-bad.bib"),
            kind="bib",
        )
        assert len(violations) == 1
        assert violations[0].rule_id == "JSS-BIBTEX-003"

    def test_good_fixture_silent(self, run_rule):
        assert (
            run_rule(
                jss_bibtex_003,
                _bib_from_fixture("JSS-BIBTEX-003-good.bib"),
                kind="bib",
            )
            == []
        )

    def test_book_needs_author_or_editor(self, run_rule):
        src = "@book{a, title={T}, publisher={P}, year={2020}}\n"
        violations = run_rule(jss_bibtex_003, src, kind="bib")
        assert len(violations) == 1
        # editor form is equally valid
        src2 = (
            "@book{a, editor={Ed.}, title={T}, publisher={P}, year={2020}}\n"
        )
        assert run_rule(jss_bibtex_003, src2, kind="bib") == []

    def test_misc_has_no_requirements(self, run_rule):
        src = "@misc{a}\n"
        assert run_rule(jss_bibtex_003, src, kind="bib") == []

    def test_unknown_entry_type_silent(self, run_rule):
        src = "@widget{a, title={T}, year={2020}}\n"
        assert run_rule(jss_bibtex_003, src, kind="bib") == []


# ---------------------------------------------------------------------------
# JSS-BIBTEX-004 — 6+ authors without mitigation
# ---------------------------------------------------------------------------


class TestBibtex004:
    def test_positive_seven_authors_bare_bib(self, run_rule):
        violations = run_rule(
            jss_bibtex_004,
            _bib_from_fixture("JSS-BIBTEX-004-bad.bib"),
            kind="bib",
        )
        # No paired .tex → no mitigation visible → fires.
        assert len(violations) == 1
        assert violations[0].rule_id == "JSS-BIBTEX-004"

    def test_five_authors_silent(self, run_rule):
        # Five authors — below the six-author threshold.
        assert (
            run_rule(
                jss_bibtex_004,
                _bib_from_fixture("JSS-BIBTEX-004-good.bib"),
                kind="bib",
            )
            == []
        )

    def test_missing_author_silent(self, run_rule):
        src = "@article{a, title={T}, year={2020}}\n"
        assert run_rule(jss_bibtex_004, src, kind="bib") == []

    def test_shortnames_class_option_suppresses(
        self, tmp_path: Path, parse_tex_source, parse_bib_source
    ):
        tex_src = (
            r"\documentclass[article,shortnames]{jss}" "\n"
            r"\begin{document}" r"\end{document}" "\n"
        )
        bib_src = _bib_from_fixture("JSS-BIBTEX-004-bad.bib")
        doc = ParsedDocument(
            tex_files=(parse_tex_source(tex_src),),
            bib_files=(parse_bib_source(bib_src),),
        )
        assert list(check_jss_bibtex_004(doc, ToolConfig())) == []

    def test_shortcites_suppresses_per_key(
        self, parse_tex_source, parse_bib_source
    ):
        tex_src = (
            r"\documentclass[article]{jss}" "\n"
            r"\shortcites{Many}" "\n"
            r"\begin{document}\cite{Many}\end{document}" "\n"
        )
        bib_src = _bib_from_fixture("JSS-BIBTEX-004-bad.bib")
        doc = ParsedDocument(
            tex_files=(parse_tex_source(tex_src),),
            bib_files=(parse_bib_source(bib_src),),
        )
        assert list(check_jss_bibtex_004(doc, ToolConfig())) == []

    def test_empty_key_entries_not_flagged(
        self, parse_tex_source, parse_bib_source
    ):
        # New behaviour: rule fires at the cite site, so an entry with an
        # empty key cannot be referenced by name and therefore never fires.
        # \nocite{*} no longer widens scope into the rule.
        tex_src = (
            r"\documentclass[article]{jss}" "\n"
            r"\nocite{*}" "\n"
            r"\begin{document}\end{document}" "\n"
        )
        bib_src = (
            "@article{,\n"
            "  author = {A and B and C and D and E and F and G},\n"
            "  title  = {T}, journal = {J}, year = {2020}\n}\n"
        )
        doc = ParsedDocument(
            tex_files=(parse_tex_source(tex_src),),
            bib_files=(parse_bib_source(bib_src),),
        )
        assert list(check_jss_bibtex_004(doc, ToolConfig())) == []

    def test_fires_at_cite_site_in_tex(
        self, parse_tex_source, parse_bib_source
    ):
        tex_src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"See \citep{Many} for details." "\n"
            r"\end{document}" "\n"
        )
        bib_src = _bib_from_fixture("JSS-BIBTEX-004-bad.bib")
        tex = parse_tex_source(tex_src)
        doc = ParsedDocument(
            tex_files=(tex,),
            bib_files=(parse_bib_source(bib_src),),
        )
        violations = list(check_jss_bibtex_004(doc, ToolConfig()))
        assert len(violations) == 1
        v = violations[0]
        assert v.file == tex.path
        assert v.line == 3  # the \citep line

    def test_dedup_one_violation_per_key(
        self, parse_tex_source, parse_bib_source
    ):
        # Same key cited five times → one warning at the first cite site.
        tex_src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\citep{Many} \citep{Many} \citep{Many} \citep{Many} \citep{Many}" "\n"
            r"\end{document}" "\n"
        )
        bib_src = _bib_from_fixture("JSS-BIBTEX-004-bad.bib")
        doc = ParsedDocument(
            tex_files=(parse_tex_source(tex_src),),
            bib_files=(parse_bib_source(bib_src),),
        )
        violations = list(check_jss_bibtex_004(doc, ToolConfig()))
        assert len(violations) == 1

    def test_uncited_entry_not_flagged_when_tex_present(
        self, parse_tex_source, parse_bib_source
    ):
        # Bib has the high-author entry but no .tex file cites it: with a
        # tex file present (so cite scope is observable), no warning.
        tex_src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}\end{document}" "\n"
        )
        bib_src = _bib_from_fixture("JSS-BIBTEX-004-bad.bib")
        doc = ParsedDocument(
            tex_files=(parse_tex_source(tex_src),),
            bib_files=(parse_bib_source(bib_src),),
        )
        assert list(check_jss_bibtex_004(doc, ToolConfig())) == []

    def test_documentclass_without_options_still_fires(
        self, parse_tex_source, parse_bib_source
    ):
        tex_src = (
            r"\documentclass{jss}" "\n"
            r"\begin{document}" r"\cite{Many}" r"\end{document}" "\n"
        )
        bib_src = _bib_from_fixture("JSS-BIBTEX-004-bad.bib")
        doc = ParsedDocument(
            tex_files=(parse_tex_source(tex_src),),
            bib_files=(parse_bib_source(bib_src),),
        )
        violations = list(check_jss_bibtex_004(doc, ToolConfig()))
        assert len(violations) == 1

    def test_documentclass_missing_nodeargd(self):
        # Defensive: pylatexenc strict-parse normally always supplies
        # nodeargd, but the helper guards against None — exercise the branch
        # via a dummy macro object.
        from pylatexenc.latexwalker import LatexMacroNode

        from texlint.journals.jss.rules.bibtex import _has_shortnames_option

        class FakeMacro(LatexMacroNode):
            def __init__(self):  # type: ignore[no-untyped-def]
                pass

        assert _has_shortnames_option(FakeMacro()) is False

    def test_non_macro_nodes_before_documentclass(
        self, parse_tex_source, parse_bib_source
    ):
        # Prose / comments before \documentclass exercise the "not a macro"
        # branch of _mitigation_present's walk.
        tex_src = (
            "% A comment\n"
            "some stray text\n"
            r"\documentclass[article,shortnames]{jss}" "\n"
            r"\begin{document}" r"\end{document}" "\n"
        )
        bib_src = _bib_from_fixture("JSS-BIBTEX-004-bad.bib")
        doc = ParsedDocument(
            tex_files=(parse_tex_source(tex_src),),
            bib_files=(parse_bib_source(bib_src),),
        )
        assert list(check_jss_bibtex_004(doc, ToolConfig())) == []

    def test_other_macros_before_documentclass(
        self, parse_tex_source, parse_bib_source
    ):
        # A macro that is NOT \documentclass exercises the 'continue' branch.
        tex_src = (
            r"\NeedsTeXFormat{LaTeX2e}" "\n"
            r"\documentclass[article,shortnames]{jss}" "\n"
            r"\begin{document}" r"\end{document}" "\n"
        )
        bib_src = _bib_from_fixture("JSS-BIBTEX-004-bad.bib")
        doc = ParsedDocument(
            tex_files=(parse_tex_source(tex_src),),
            bib_files=(parse_bib_source(bib_src),),
        )
        assert list(check_jss_bibtex_004(doc, ToolConfig())) == []

    def test_empty_tex_file_falls_through(
        self, parse_tex_source, parse_bib_source
    ):
        # No \documentclass in the tex → _mitigation_present's preamble
        # walk exits immediately. \cite{Many} is still enough to bring
        # the entry into scope so the violation fires.
        tex_src = r"\cite{Many}"
        bib_src = _bib_from_fixture("JSS-BIBTEX-004-bad.bib")
        doc = ParsedDocument(
            tex_files=(parse_tex_source(tex_src),),
            bib_files=(parse_bib_source(bib_src),),
        )
        violations = list(check_jss_bibtex_004(doc, ToolConfig()))
        assert len(violations) == 1

    def test_shortcites_with_empty_entry_piece(
        self, parse_tex_source, parse_bib_source
    ):
        # \shortcites{,Foo,} — empty trailing and leading pieces exercise
        # the `if key:` filter in _iter_shortcites_keys.
        tex_src = (
            r"\documentclass[article]{jss}" "\n"
            r"\shortcites{,Many,}" "\n"
            r"\begin{document}" r"\end{document}" "\n"
        )
        bib_src = _bib_from_fixture("JSS-BIBTEX-004-bad.bib")
        doc = ParsedDocument(
            tex_files=(parse_tex_source(tex_src),),
            bib_files=(parse_bib_source(bib_src),),
        )
        assert list(check_jss_bibtex_004(doc, ToolConfig())) == []


def test_bibtex002_ignores_non_duplicate_failed_blocks(tmp_path: Path):
    # bibtexparser can produce failed_blocks that are NOT
    # DuplicateBlockKeyBlock (e.g., ParsingFailedBlock). Exercise the
    # `if type != DuplicateBlockKeyBlock: continue` guard.
    from texlint.api import ParsedBibFile
    from texlint.journals.jss.rules.bibtex import check_jss_bibtex_002

    class FakeLib:
        entries: list = []
        failed_blocks: list = [object()]  # not a DuplicateBlockKeyBlock

    fake_bib = ParsedBibFile(
        path=tmp_path / "b.bib", source="", library=FakeLib(), violations=()
    )
    doc = ParsedDocument(bib_files=(fake_bib,))
    assert list(check_jss_bibtex_002(doc, ToolConfig())) == []
