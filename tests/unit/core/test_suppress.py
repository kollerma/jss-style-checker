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


class TestLineCounting:
    """`directive_lines` must count lines the way the parsers do.

    `str.splitlines()` also breaks on form feed, vertical tab, `\x1c`-`\x1f`
    and `\x85`, while every line number a violation carries comes from
    counting `\n`. A single form feed in a manuscript therefore shifted
    every directive below it by one line, silently suppressing the wrong
    line (spec 027 §2).
    """

    def test_form_feed_does_not_start_a_new_line(self):
        src = "first\x0cstill first\nUses R % jss-lint: ignore\n"
        assert directive_lines(src) == {2: frozenset({ALL_RULES})}

    def test_vertical_tab_does_not_start_a_new_line(self):
        src = "first\x0bstill first\nUses R % jss-lint: ignore\n"
        assert directive_lines(src) == {2: frozenset({ALL_RULES})}

    def test_next_line_character_does_not_start_a_new_line(self):
        src = "first\x85still first\nUses R % jss-lint: ignore\n"
        assert directive_lines(src) == {2: frozenset({ALL_RULES})}

    def test_carriage_return_newline_counts_once(self):
        src = "first\r\nUses R % jss-lint: ignore\r\n"
        assert directive_lines(src) == {2: frozenset({ALL_RULES})}


class TestRmdAndRnwOffsets:
    """A directive in an `.Rmd`/`.Rnw` must target the line the author sees.

    `.Rmd` prose blocks are parsed as standalone LaTeX fragments whose
    `source` starts at line 1, while violations carry file-authoritative
    line numbers. Without `line_offset` a directive only ever worked when
    the prose block happened to start on line 1 (spec 027 §2).
    """

    def _report(self, path):
        from texlint.core.engine import load_journal, parse_document, run

        return run(ToolConfig(), parse_document([path]), load_journal("jss"))

    def test_rmd_directive_below_the_first_block(self, tmp_path):
        rmd = tmp_path / "paper.Rmd"
        rmd.write_text(
            "---\ntitle: Demo\n---\n\n"
            "Some opening prose without findings.\n\n"
            "```{r}\nx <- 1\n```\n\n"
            "We use R here. % jss-lint: ignore JSS-MARKUP-001\n",
            encoding="utf-8",
        )
        report = self._report(rmd)
        assert not any(
            v.rule_id == "JSS-MARKUP-001" for v in report.violations
        ), "the directive did not reach the line it annotates"

    def test_rmd_finding_without_a_directive_is_reported(self, tmp_path):
        rmd = tmp_path / "paper.Rmd"
        rmd.write_text(
            "---\ntitle: Demo\n---\n\n"
            "Some opening prose without findings.\n\n"
            "```{r}\nx <- 1\n```\n\n"
            "We use R here.\n",
            encoding="utf-8",
        )
        report = self._report(rmd)
        assert any(v.rule_id == "JSS-MARKUP-001" for v in report.violations)

    def test_rnw_directive_below_a_chunk(self, tmp_path):
        rnw = tmp_path / "paper.Rnw"
        rnw.write_text(
            "\\documentclass[article]{jss}\n"
            "\\begin{document}\n"
            "<<setup>>=\nx <- 1\n@\n"
            "We use R here. % jss-lint: ignore JSS-MARKUP-001\n"
            "\\end{document}\n",
            encoding="utf-8",
        )
        report = self._report(rnw)
        assert not any(
            v.rule_id == "JSS-MARKUP-001" for v in report.violations
        )


class TestSuppressorHook:
    """`engine.run(suppress=...)` — the seam the baseline matcher uses.

    Order matters (spec 027 §5.2): findings are sorted, inline-ignored
    ones are dropped, and only what survives is offered to the caller's
    suppressor. An inline-ignored finding must never consume a baseline
    count — the author already signed off on it.
    """

    def _run(self, parse_tex_source, src: str, suppress=None):
        from texlint.core.engine import load_journal, run

        doc = ParsedDocument(tex_files=(parse_tex_source(src),))
        return run(ToolConfig(), doc, load_journal("jss"), suppress=suppress)

    def test_suppressor_drops_what_it_selects(self, parse_tex_source):
        src = "We use R and call lm() here.\n"
        report = self._run(
            parse_tex_source, src, lambda v: v.rule_id == "JSS-MARKUP-001"
        )
        assert not any(
            v.rule_id == "JSS-MARKUP-001" for v in report.violations
        )
        assert any(v.rule_id == "JSS-MARKUP-003" for v in report.violations)

    def test_inline_ignored_findings_never_reach_the_suppressor(
        self, parse_tex_source
    ):
        src = "We use R here. % jss-lint: ignore JSS-MARKUP-001\n"
        seen: list[str] = []
        self._run(parse_tex_source, src, lambda v: seen.append(v.rule_id) or False)
        assert "JSS-MARKUP-001" not in seen

    def test_findings_arrive_in_sort_order(self, parse_tex_source):
        src = "We use R here.\nAnd R again there.\nAnd R once more.\n"
        seen: list[int] = []
        self._run(
            parse_tex_source,
            src,
            lambda v: seen.append(v.line) if v.rule_id == "JSS-MARKUP-001" else False,
        )
        assert seen == sorted(seen)

    def test_parse_errors_bypass_the_suppressor(self, parse_tex_source):
        src = "\\begin{tabular}{ll}\n"
        report = self._run(parse_tex_source, src, lambda v: True)
        assert any(v.rule_id == "JSS-PARSE-000" for v in report.violations)

    def test_category_passes_when_the_suppressor_hides_everything(
        self, parse_tex_source
    ):
        src = "We use R here.\n"
        report = self._run(
            parse_tex_source, src, lambda v: v.rule_id == "JSS-MARKUP-001"
        )
        markup = {c.category_id: c for c in report.categories}["markup"]
        assert markup.violations == ()
