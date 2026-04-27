"""Tests for the `.Rmd` tokenizer (`core/rmd_parser.py`).

Per spec 005 `contracts/rmd-parser.md`. Covers invariants M-1..M-7 and
the test matrix.
"""

from __future__ import annotations

from pathlib import Path

from texlint.core.rmd_parser import parse_rmd_source


def _parse(src: str):
    return parse_rmd_source(src, Path("/tmp/x.Rmd"))


class TestFrontmatter:
    def test_empty_file(self):
        r = _parse("")
        assert r.yaml_frontmatter == {}
        assert r.headings == ()
        assert r.prose_blocks == ()
        assert r.code_blocks == ()
        assert r.violations == ()

    def test_frontmatter_only(self):
        r = _parse("---\ntitle: Demo\nauthor: Jane\n---\n")
        assert r.yaml_frontmatter == {"title": "Demo", "author": "Jane"}
        assert r.headings == ()
        assert r.prose_blocks == ()

    def test_frontmatter_plus_body(self):
        r = _parse("---\ntitle: Demo\n---\n\n# Intro\n\nProse.\n")
        assert r.yaml_frontmatter["title"] == "Demo"
        assert len(r.headings) == 1
        assert r.headings[0].text == "Intro"
        assert len(r.prose_blocks) == 1
        assert "Prose." in r.prose_blocks[0].text

    def test_no_frontmatter(self):
        r = _parse("# Intro\n\nProse.\n")
        assert r.yaml_frontmatter == {}
        assert r.headings[0].line == 1

    def test_malformed_yaml_graceful(self):
        src = "---\ntitle: \"Broken\nauthor: : invalid\n---\n\nBody.\n"
        r = _parse(src)
        assert r.yaml_frontmatter == {}
        assert len(r.violations) == 1
        assert r.violations[0].rule_id == "JSS-PARSE-000"
        # Reports the frontmatter start line.
        assert r.violations[0].line == 1


class TestHeadings:
    def test_multiple_heading_levels(self):
        src = "# H1\n\n## H2\n\n### H3\n"
        r = _parse(src)
        assert [h.level for h in r.headings] == [1, 2, 3]
        assert [h.text for h in r.headings] == ["H1", "H2", "H3"]

    def test_heading_line_numbers_1_based(self):
        src = "Prose\n\n# H1\n"
        r = _parse(src)
        assert r.headings[0].line == 3

    def test_hashes_without_space_not_heading(self):
        src = "#NotAHeading\n"
        r = _parse(src)
        assert r.headings == ()
        assert len(r.prose_blocks) == 1


class TestFencedCode:
    def test_fence_with_r_tag(self):
        src = "```{r}\nx <- 1\n```\n"
        r = _parse(src)
        assert len(r.code_blocks) == 1
        cb = r.code_blocks[0]
        assert cb.lang == "r"
        assert "x <- 1" in cb.body
        assert cb.open_line == 1
        assert cb.close_line == 3

    def test_fence_with_options(self):
        src = "```{r, fig.width=5}\nplot(1)\n```\n"
        r = _parse(src)
        assert r.code_blocks[0].lang == "r"

    def test_fence_with_python_tag(self):
        src = "```python\nprint('x')\n```\n"
        r = _parse(src)
        assert r.code_blocks[0].lang == "python"

    def test_plain_fence(self):
        src = "```\nunknown\n```\n"
        r = _parse(src)
        assert r.code_blocks[0].lang == ""

    def test_unterminated_fence_graceful(self):
        src = "```{r}\nx <- 1\n"
        r = _parse(src)
        assert len(r.violations) == 1
        assert r.violations[0].rule_id == "JSS-PARSE-000"
        assert r.violations[0].line == 1  # fence open line


class TestInlineR:
    def test_inline_r_stripped(self):
        src = "The answer is `r 1 + 1` here.\n"
        r = _parse(src)
        prose = r.prose_blocks[0].text
        assert "1 + 1" not in prose
        # Width preserved: the span `r 1 + 1` has length 10.
        assert len(prose) == len(src.rstrip("\n"))

    def test_generic_backtick_span_also_stripped(self):
        # Plain Markdown inline code is the author's own "this is code"
        # signal — the Rmd equivalent of LaTeX \code{…}. Strip to
        # equivalent-length whitespace so MARKUP-001/002/003 don't fire
        # on bare tokens inside backticks.
        src = "Just `code` inline.\n"
        r = _parse(src)
        prose = r.prose_blocks[0].text
        assert "code" not in prose
        assert "`" not in prose
        # Width preserved so column offsets stay source-accurate.
        assert len(prose) == len(src.rstrip("\n"))

    def test_html_comment_stripped(self):
        # `<!-- ... -->` are commented-out blocks. Their contents are not
        # user-visible prose, so MARKUP-001/002/003 should not fire on
        # bare token names inside them.
        src = "Visible.\n<!-- hidden \\pkg{secret} content -->\n\nMore.\n"
        r = _parse(src)
        joined = "".join(p.text for p in r.prose_blocks)
        assert "secret" not in joined
        assert "<!--" not in joined

    def test_autolink_url_stripped(self):
        # `<https://yihui.org/knitr/>` — the path contains "knitr"; the
        # rule should not flag it as a bare package mention.
        src = "See <https://yihui.org/knitr/> for docs.\n"
        r = _parse(src)
        prose = r.prose_blocks[0].text
        assert "knitr" not in prose

    def test_inline_link_url_stripped(self):
        # `[text](url)` — the parenthesised URL portion gets blanked.
        src = "[hooks](https://yihui.org/knitr/hooks/)\n"
        r = _parse(src)
        prose = r.prose_blocks[0].text
        assert "knitr" not in prose

    def test_bare_url_stripped(self):
        src = "See https://github.com/yihui/knitr in source.\n"
        r = _parse(src)
        prose = r.prose_blocks[0].text
        assert "knitr" not in prose

    def test_multiline_html_comment_preserves_newlines(self):
        # Multi-line HTML comments must keep their interior newlines
        # so subsequent rule firings report source-accurate lines.
        src = (
            "Visible above.\n"
            "<!-- line 1\nline 2\nline 3 -->\n"
            "Visible below.\n"
        )
        r = _parse(src)
        # Confirm: the prose blocks together span the full line range
        # (no shrinkage from the multi-line comment).
        max_line = max((p.line + p.n_lines - 1) for p in r.prose_blocks)
        assert max_line >= 5


class TestKnitrYamlTag:
    def test_r_tag_in_frontmatter_does_not_parse_error(self):
        # knitr allows `!r ...` in YAML frontmatter to evaluate R at
        # knit time. Default PyYAML SafeLoader rejects the unknown tag;
        # our custom loader treats it as the underlying scalar value.
        src = (
            "---\n"
            "title: \"Demo\"\n"
            "params:\n"
            "  threshold: !r 0.5\n"
            "  cutoff: !r seq(0, 1, by = 0.1)\n"
            "---\n"
            "\nProse here.\n"
        )
        r = _parse(src)
        # No parse errors.
        parse_errs = [v for v in r.violations if v.rule_id == "JSS-PARSE-000"]
        assert parse_errs == []


class TestProseBlocks:
    def test_blank_line_flushes_prose(self):
        src = "Para one.\n\nPara two.\n"
        r = _parse(src)
        assert len(r.prose_blocks) == 2
        assert r.prose_blocks[0].text == "Para one."
        assert r.prose_blocks[1].text == "Para two."

    def test_line_numbers_on_prose(self):
        src = "\n\nLine 3 prose.\n"
        r = _parse(src)
        assert r.prose_blocks[0].line == 3


class TestLatexFragments:
    def test_raw_math_in_prose_parsed(self):
        src = "We compute $x^2$ directly.\n"
        r = _parse(src)
        assert len(r.latex_fragments) == 1
        # Fragment should have a math node or at least parse without error.
        assert r.latex_fragments[0].violations == ()

    def test_latex_macro_in_prose_parsed(self):
        src = "See \\ref{eq:1} for details.\n"
        r = _parse(src)
        assert len(r.latex_fragments) == 1

    def test_prose_with_only_whitespace_skipped(self):
        src = "# Intro\n\n   \n\n# Next\n"
        r = _parse(src)
        # Two blocks of whitespace-only prose → no fragments emitted.
        # (Whitespace prose blocks are skipped in latex_fragments creation.)
        assert r.latex_fragments == ()
