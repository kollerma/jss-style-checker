"""Unit tests for JSS-CITE-001 — no ``\\emph`` for citation markup.

Constitution §IX: this rule module must have 100% branch coverage.
"""

from __future__ import annotations

from pathlib import Path

from texlint.api import ParsedBibFile, ParsedDocument, ToolConfig
from texlint.journals.jss.rules.cite_001_emph import rule as cite_001


class TestFiresOnBibkeyLikeEmph:
    def test_flags_emph_with_bibkey_pattern(self, run_rule):
        src = r"\documentclass{article}\begin{document}See \emph{smith2020}.\end{document}"
        violations = run_rule(cite_001, src)
        assert len(violations) == 1
        v = violations[0]
        assert v.rule_id == "JSS-CITE-001"
        assert v.line == 1
        assert v.column is not None and v.column >= 1  # 1-based

    def test_flags_emph_with_author_year_no_space(self, run_rule):
        src = r"\documentclass{article}\begin{document}\emph{wickham2014}\end{document}"
        violations = run_rule(cite_001, src)
        assert len(violations) == 1


class TestDoesNotFireOnProseEmph:
    def test_emph_with_single_word_does_not_flag(self, run_rule):
        src = r"\documentclass{article}\begin{document}\emph{important}\end{document}"
        violations = run_rule(cite_001, src)
        assert violations == []

    def test_plain_text_does_not_flag(self, run_rule):
        src = r"\documentclass{article}\begin{document}smith2020\end{document}"
        violations = run_rule(cite_001, src)
        assert violations == []

    def test_cite_does_not_flag(self, run_rule):
        src = r"\documentclass{article}\begin{document}\cite{smith2020}\end{document}"
        violations = run_rule(cite_001, src)
        assert violations == []

    def test_emph_with_empty_group_does_not_flag(self, run_rule):
        src = r"\documentclass{article}\begin{document}\emph{}\end{document}"
        violations = run_rule(cite_001, src)
        assert violations == []

    def test_emph_with_nested_macro_does_not_flag(self, run_rule):
        # Group contains a nested macro (not plain chars); _emph_arg_text
        # should yield '' and the bibkey regex should not match.
        src = r"\documentclass{article}\begin{document}\emph{\textit{foo2020}}\end{document}"
        violations = run_rule(cite_001, src)
        assert violations == []

    def test_emph_with_unbraced_arg_does_not_flag(self, run_rule):
        # `\emph X` — pylatexenc binds X as a LatexCharsNode, not a group.
        src = r"\documentclass{article}\begin{document}\emph X\end{document}"
        violations = run_rule(cite_001, src)
        assert violations == []


class TestNestedContexts:
    def test_flags_inside_environment(self, run_rule):
        src = (
            r"\documentclass{article}\begin{document}"
            r"\begin{itemize}\item See \emph{jones2019}\end{itemize}"
            r"\end{document}"
        )
        violations = run_rule(cite_001, src)
        assert len(violations) == 1

    def test_flags_inside_group(self, run_rule):
        src = r"\documentclass{article}\begin{document}{\emph{smith2020}}\end{document}"
        violations = run_rule(cite_001, src)
        assert len(violations) == 1

    def test_does_not_flag_inside_math(self, run_rule):
        # \emph doesn't really happen in math, but nested walking should still
        # work without crashing on math nodes.
        src = r"\documentclass{article}\begin{document}$x = 1$\end{document}"
        violations = run_rule(cite_001, src)
        assert violations == []


class TestFormatsFilter:
    def test_only_applies_to_tex(self):
        assert cite_001.formats == frozenset({".tex"})

    def test_bib_only_document_yields_no_violations(self, tmp_path: Path):
        p = tmp_path / "refs.bib"
        p.write_text("", encoding="utf-8")
        bib = ParsedBibFile(path=p, source="", library=None, violations=())
        doc = ParsedDocument(bib_files=(bib,))
        assert list(cite_001.check(doc, ToolConfig())) == []


class TestUnparseableTex:
    def test_no_violations_when_nodes_empty(self, tmp_path: Path):
        # A ParsedTexFile with empty nodes (parse-error path) must not crash the rule.
        from texlint.api import ParsedTexFile

        p = tmp_path / "broken.tex"
        p.write_text("", encoding="utf-8")
        tex = ParsedTexFile(path=p, source="", nodes=(), walker=None, violations=())
        doc = ParsedDocument(tex_files=(tex,))
        assert list(cite_001.check(doc, ToolConfig())) == []
