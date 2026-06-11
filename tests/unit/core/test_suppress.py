"""Unit tests for inline suppression (``% jss-lint: ignore``)."""

from __future__ import annotations

from pathlib import Path

from texlint.api import ParsedDocument, Severity, ToolConfig, Violation
from texlint.core.suppress import (
    ALL_RULES,
    build_index,
    directive_lines,
    is_suppressed,
)


def _v(file: str, line: int, rule_id: str) -> Violation:
    return Violation(
        file=Path(file),
        line=line,
        column=1,
        rule_id=rule_id,
        severity=Severity.WARNING,
        message="msg",
    )


class TestDirectiveLines:
    def test_no_directive_empty(self):
        assert directive_lines("plain prose\nmore prose\n") == {}

    def test_inline_bare_ignore_targets_own_line(self):
        src = "Uses R for things  % jss-lint: ignore\nnext line\n"
        assert directive_lines(src) == {1: frozenset({ALL_RULES})}

    def test_inline_with_rule_ids(self):
        src = "Uses R  % jss-lint: ignore JSS-MARKUP-001, JSS-CAP-002\n"
        assert directive_lines(src) == {
            1: frozenset({"JSS-MARKUP-001", "JSS-CAP-002"})
        }

    def test_standalone_targets_next_line_too(self):
        src = "% jss-lint: ignore JSS-MARKUP-001\nUses R for things\n"
        got = directive_lines(src)
        assert got[1] == frozenset({"JSS-MARKUP-001"})
        assert got[2] == frozenset({"JSS-MARKUP-001"})

    def test_keyword_case_insensitive_and_lowercase_ids(self):
        src = "text % JSS-LINT: IGNORE jss-markup-001\n"
        assert directive_lines(src) == {1: frozenset({"JSS-MARKUP-001"})}

    def test_trailing_rationale_without_ids_means_all(self):
        src = "text % jss-lint: ignore -- proper noun, not title case\n"
        assert directive_lines(src) == {1: frozenset({ALL_RULES})}

    def test_escaped_percent_is_not_a_directive(self):
        src = r"50\% jss-lint: ignore" + "\n"
        assert directive_lines(src) == {}

    def test_double_percent_banner_accepted(self):
        src = "%% jss-lint: ignore JSS-CAP-002\nSection Title Here\n"
        assert 2 in directive_lines(src)

    def test_two_directives_same_target_merge(self):
        src = (
            "% jss-lint: ignore JSS-A-001\n"
            "thing % jss-lint: ignore JSS-B-002\n"
        )
        got = directive_lines(src)
        assert got[2] == frozenset({"JSS-A-001", "JSS-B-002"})


class TestIsSuppressed:
    def test_matches_file_line_and_rule(self):
        index = {"a.tex": {3: frozenset({"JSS-MARKUP-001"})}}
        assert is_suppressed(index, _v("a.tex", 3, "JSS-MARKUP-001"))
        assert not is_suppressed(index, _v("a.tex", 3, "JSS-CAP-002"))
        assert not is_suppressed(index, _v("a.tex", 4, "JSS-MARKUP-001"))
        assert not is_suppressed(index, _v("b.tex", 3, "JSS-MARKUP-001"))

    def test_all_rules_wildcard(self):
        index = {"a.tex": {3: frozenset({ALL_RULES})}}
        assert is_suppressed(index, _v("a.tex", 3, "JSS-ANY-999"))


class TestBuildIndex:
    def test_collects_tex_and_bib_sources(
        self, parse_tex_source, parse_bib_source
    ):
        tex = parse_tex_source(
            "prose\nUses R % jss-lint: ignore JSS-MARKUP-001\n"
        )
        bib = parse_bib_source(
            "% jss-lint: ignore JSS-REFS-003\n"
            "@article{k, author={A}, title={T}, year={2020}}\n"
        )
        doc = ParsedDocument(tex_files=(tex,), bib_files=(bib,))
        index = build_index((doc,))
        assert is_suppressed(index, _v(str(tex.path), 2, "JSS-MARKUP-001"))
        assert is_suppressed(index, _v(str(bib.path), 2, "JSS-REFS-003"))

    def test_directive_inside_verbatim_env_inert(self, parse_tex_source):
        # The parser neutralises % inside verbatim envs before the
        # source is stored, so code comments cannot act as directives.
        tex = parse_tex_source(
            "\\begin{Sinput}\n# % jss-lint: ignore\n\\end{Sinput}\n"
            "Uses R here\n"
        )
        doc = ParsedDocument(tex_files=(tex,))
        assert build_index((doc,)) == {}


class TestEngineIntegration:
    """End-to-end through ``engine.run`` with the real jss journal."""

    def _run(self, parse_tex_source, src: str):
        from texlint.core.engine import load_journal, run

        doc = ParsedDocument(tex_files=(parse_tex_source(src),))
        return run(ToolConfig(), doc, load_journal("jss"))

    def test_inline_directive_silences_one_finding(self, parse_tex_source):
        bare = "We use R for everything.\n"
        report = self._run(parse_tex_source, bare)
        assert any(v.rule_id == "JSS-MARKUP-001" for v in report.violations)

        suppressed = (
            "We use R for everything. % jss-lint: ignore JSS-MARKUP-001\n"
        )
        report = self._run(parse_tex_source, suppressed)
        assert not any(
            v.rule_id == "JSS-MARKUP-001" for v in report.violations
        )

    def test_directive_is_rule_scoped(self, parse_tex_source):
        # Suppressing MARKUP-001 must not silence other rules on the
        # same line.
        src = (
            "We use R and call lm() here. "
            "% jss-lint: ignore JSS-MARKUP-001\n"
        )
        report = self._run(parse_tex_source, src)
        assert not any(
            v.rule_id == "JSS-MARKUP-001" for v in report.violations
        )
        assert any(v.rule_id == "JSS-MARKUP-003" for v in report.violations)

    def test_category_passes_when_all_findings_suppressed(
        self, parse_tex_source
    ):
        src = "We use R here. % jss-lint: ignore\n"
        report = self._run(parse_tex_source, src)
        by_id = {c.category_id: c for c in report.categories}
        markup = by_id["markup"]
        assert markup.violations == ()

    def test_parse_errors_never_suppressed(self, parse_tex_source):
        # An unrecoverable parse error stays visible even under a
        # blanket ignore on its line.
        src = "\\begin{tabular}{ll} % jss-lint: ignore\n"
        report = self._run(parse_tex_source, src)
        assert any(
            v.rule_id == "JSS-PARSE-000" for v in report.violations
        )
