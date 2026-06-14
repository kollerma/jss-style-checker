"""Unit tests for ``texlint.core.parser.parse_tex_file``."""

from __future__ import annotations

from pathlib import Path

from texlint.core.parser import parse_tex_file


def _write(tmp_path: Path, name: str, content: str | bytes) -> Path:
    p = tmp_path / name
    if isinstance(content, bytes):
        p.write_bytes(content)
    else:
        p.write_text(content, encoding="utf-8")
    return p


class TestParseTexHappyPath:
    def test_returns_parsed_file_with_nodes_and_walker(self, tmp_path: Path):
        src = r"\documentclass{article}\begin{document}hi\end{document}"
        path = _write(tmp_path, "doc.tex", src)

        parsed = parse_tex_file(path)

        assert parsed.path == path
        assert parsed.source == src
        assert parsed.walker is not None
        assert parsed.nodes  # non-empty
        assert parsed.violations == ()

    def test_empty_file_is_valid(self, tmp_path: Path):
        path = _write(tmp_path, "empty.tex", "")
        parsed = parse_tex_file(path)
        assert parsed.violations == ()


class TestParseTexBomHandling:
    def test_utf8_bom_is_stripped(self, tmp_path: Path):
        body = r"\documentclass{article}\begin{document}\end{document}"
        path = _write(tmp_path, "bom.tex", b"\xef\xbb\xbf" + body.encode("utf-8"))

        parsed = parse_tex_file(path)

        assert parsed.violations == ()
        assert not parsed.source.startswith("﻿")
        assert parsed.source == body


class TestParseTexEncoding:
    def test_non_utf8_recovered_via_latin1_fallback(self, tmp_path: Path):
        # latin-1 e-acute; not a valid UTF-8 sequence on its own.
        # Decoded via the Latin-1 fallback with a warning-severity
        # advisory (see TestLatin1Fallback for the full matrix).
        path = _write(tmp_path, "latin1.tex", b"caf\xe9\n")

        parsed = parse_tex_file(path)

        assert len(parsed.violations) == 1
        v = parsed.violations[0]
        assert v.rule_id == "JSS-PARSE-000"
        assert v.severity.value == "warning"
        assert parsed.source == "café\n"


class TestParseTexParseFailure:
    def test_unterminated_group_recovered_as_degraded_parse(
        self, tmp_path: Path
    ):
        # pylatexenc's strict parser raises on the unclosed group; the
        # tolerant retry recovers a node tree, so the finding is a
        # warning-severity (degraded-parse) PARSE-000, not a failure.
        path = _write(tmp_path, "bad.tex", r"\begin{document")

        parsed = parse_tex_file(path)

        assert len(parsed.violations) == 1
        v = parsed.violations[0]
        assert v.rule_id == "JSS-PARSE-000"
        assert v.severity.value == "warning"
        assert v.line >= 1
        assert parsed.nodes  # rules can still run
        # Does not raise.

    def test_unrecoverable_parse_produces_error(
        self, tmp_path: Path, monkeypatch
    ):
        # When the tolerant retry *also* fails, the finding stays an
        # error-severity PARSE-000 (exit-2 path).
        from pylatexenc.latexwalker import LatexWalkerError

        from texlint.core import parser as parser_mod

        class _AlwaysFails:
            def __init__(self, source, tolerant_parsing=False):
                pass

            def get_latex_nodes(self):
                raise LatexWalkerError("synthetic failure")

        monkeypatch.setattr(parser_mod, "LatexWalker", _AlwaysFails)
        path = _write(tmp_path, "bad.tex", r"\begin{document")

        parsed = parser_mod.parse_tex_file(path)

        assert len(parsed.violations) == 1
        v = parsed.violations[0]
        assert v.rule_id == "JSS-PARSE-000"
        assert v.severity.value == "error"
        assert parsed.nodes == ()


class TestParseTexVerbatimMacroArgs:
    """Pre-substitute TeX special chars inside \\code{...}, \\verb{...},
    etc. so a literal ``$`` doesn't enter math mode and trip the parser
    with a mismatched-brace error."""

    def test_dollar_inside_code_does_not_parse_error(self, tmp_path: Path):
        path = _write(
            tmp_path,
            "code-dollar.tex",
            r"\documentclass{article}\begin{document}"
            r"Use \code{$} for math.\end{document}",
        )
        parsed = parse_tex_file(path)
        assert parsed.violations == ()

    def test_percent_inside_code_does_not_parse_error(self, tmp_path: Path):
        path = _write(
            tmp_path,
            "code-percent.tex",
            r"\documentclass{article}\begin{document}\code{a%b}\end{document}",
        )
        parsed = parse_tex_file(path)
        assert parsed.violations == ()

    def test_underscore_inside_code_does_not_parse_error(self, tmp_path: Path):
        path = _write(
            tmp_path,
            "code-underscore.tex",
            r"\documentclass{article}\begin{document}\code{x_y}\end{document}",
        )
        parsed = parse_tex_file(path)
        assert parsed.violations == ()

    def test_normal_code_args_unchanged(self, tmp_path: Path):
        path = _write(
            tmp_path,
            "code-normal.tex",
            r"\documentclass{article}\begin{document}"
            r"\code{normal_code()} works.\end{document}",
        )
        parsed = parse_tex_file(path)
        assert parsed.violations == ()
        # Length preservation: line/column positions stay accurate.
        assert "normal" in parsed.source


class TestParseTexVerbatimEnvironments:
    """Sweave / knitr / JSS code-listing envs (Sinput, Soutput, Code,
    CodeInput, alltt, …) aren't in pylatexenc's default DB, so a stray
    ``$`` or ``%`` inside trips the parser. Pre-substitution makes
    these envs parse-error-free."""

    def test_sinput_with_dollar_silent(self, tmp_path: Path):
        path = _write(
            tmp_path,
            "sinput.tex",
            r"\documentclass{article}\begin{document}"
            "\\begin{Sinput}\nfoo $bar baz%\n\\end{Sinput}\n"
            r"\end{document}",
        )
        parsed = parse_tex_file(path)
        assert parsed.violations == ()

    def test_codeinput_with_underscore_silent(self, tmp_path: Path):
        path = _write(
            tmp_path,
            "codeinput.tex",
            r"\documentclass{article}\begin{document}"
            "\\begin{CodeInput}\nx_y = 1\n\\end{CodeInput}\n"
            r"\end{document}",
        )
        parsed = parse_tex_file(path)
        assert parsed.violations == ()

    def test_multiline_verbatim_env_preserves_line_count(self, tmp_path: Path):
        # 5 lines of body — line numbers must stay source-authoritative
        # so downstream rule firings report correct positions.
        body = "line1 $a\nline2 %b\nline3\nline4\nline5"
        src = (
            r"\documentclass{article}" + "\n"
            r"\begin{document}" + "\n"
            "\\begin{Sinput}\n" + body + "\n\\end{Sinput}\n"
            r"\end{document}" + "\n"
        )
        path = _write(tmp_path, "multi-sinput.tex", src)
        parsed = parse_tex_file(path)
        assert parsed.violations == ()
        # Line count unchanged after neutralisation.
        assert parsed.source.count("\n") == src.count("\n")


class TestParseTexMissingFile:
    def test_missing_path_produces_parse_error(self, tmp_path: Path):
        parsed = parse_tex_file(tmp_path / "nope.tex")
        assert len(parsed.violations) == 1
        assert parsed.violations[0].rule_id == "JSS-PARSE-000"


class TestLatin1Fallback:
    """A readable file that is not valid UTF-8 decodes as Latin-1 and
    lints fully, carrying a warning-severity degraded-parse advisory
    (pre-2015 CRAN vignettes commonly ship Latin-1 sources)."""

    def test_latin1_tex_parses_with_advisory(self, tmp_path: Path):
        path = tmp_path / "old.tex"
        path.write_bytes(
            b"\\begin{document}\ncaf\xe9 con leche\n\\end{document}\n"
        )

        parsed = parse_tex_file(path)

        assert len(parsed.violations) == 1
        v = parsed.violations[0]
        assert v.rule_id == "JSS-PARSE-000"
        assert v.severity.value == "warning"
        assert "Latin-1" in v.message
        assert "café" in parsed.source
        assert parsed.nodes  # rules can still run

    def test_latin1_rnw_parses_with_advisory(self, tmp_path: Path):
        from texlint.core.parser import parse_rnw_file

        path = tmp_path / "old.Rnw"
        path.write_bytes(
            b"text caf\xe9\n<<a>>=\nx <- 1\n@\nmore\n"
        )

        parsed = parse_rnw_file(path)

        severities = [v.severity.value for v in parsed.violations]
        assert severities == ["warning"]
        assert "Sinput" in parsed.source

    def test_latin1_bib_parses_with_advisory(self, tmp_path: Path):
        from texlint.core.parser import parse_bib_file

        path = tmp_path / "old.bib"
        path.write_bytes(
            b"@article{k, author = {Jos\xe9}, title = {T}}\n"
        )

        parsed = parse_bib_file(path)

        assert [v.severity.value for v in parsed.violations] == ["warning"]
        assert [e.key for e in parsed.library.entries] == ["k"]

    def test_latin1_rmd_parses_with_advisory(self, tmp_path: Path):
        from texlint.core.parser import parse_rmd_file

        path = tmp_path / "old.Rmd"
        path.write_bytes(b"---\ntitle: caf\xe9\n---\nprose\n")

        parsed = parse_rmd_file(path)

        assert any(
            v.severity.value == "warning" and "Latin-1" in v.message
            for v in parsed.violations
        )

    def test_unreadable_file_still_fatal(self, tmp_path: Path):
        path = tmp_path / "gone.tex"  # never created

        parsed = parse_tex_file(path)

        assert len(parsed.violations) == 1
        assert parsed.violations[0].severity.value == "error"


class TestRnwCommentedChunkHeader:
    """A commented-out chunk header (`% <<x>>=`) must NOT open a chunk;
    only column-0 `<<x>>=` does (Sweave/knitr requirement). Regression
    for cna.Rnw, where a commented `% # <<data type>>=` swallowed real
    LaTeX prose and blanked its markup."""

    def test_commented_header_does_not_swallow_prose(self, tmp_path: Path):
        from texlint.core.parser import parse_rnw_file

        src = (
            "<<real, eval=TRUE>>=\n"
            "x <- 1\n"
            "@\n"
            "% # <<commented, eval=F>>=\n"
            "% # foo()\n"
            "% # @\n"
            "\n"
            "Prose with \\code{configTable()} and \\pkg{cna}.\n"
        )
        path = tmp_path / "v.Rnw"
        path.write_text(src, encoding="utf-8")
        parsed = parse_rnw_file(path)
        # The real prose macros survive (backslashes/braces intact),
        # i.e. the phantom chunk did not blank them.
        assert "\\code{configTable()}" in parsed.source
        assert "\\pkg{cna}" in parsed.source
        # The real chunk body was still wrapped as Sinput.
        assert "Sinput" in parsed.source

    def test_real_column0_chunk_still_wrapped(self, tmp_path: Path):
        from texlint.core.parser import parse_rnw_file

        src = "<<c>>=\ny <- 2\n@\nprose\n"
        path = tmp_path / "v.Rnw"
        path.write_text(src, encoding="utf-8")
        parsed = parse_rnw_file(path)
        assert "Sinput" in parsed.source


class TestRnwChunkTrailingWhitespace:
    """Sweave/knitr accept trailing whitespace after >>= on the chunk
    header. Regression for multcomp generalsiminf.Rnw, where an
    `echo=FALSE` chunk with `>>=  ` trailing spaces wasn't recognised,
    so its hidden R code leaked into the linted prose."""

    def test_hidden_chunk_with_trailing_ws_is_blanked(self, tmp_path: Path):
        from texlint.core.parser import parse_rnw_file
        src = (
            "Prose before.\n"
            "<<demo, echo = FALSE>>=  \n"
            "x <- NULL\n"
            "@\n"
            "Prose after.\n"
        )
        path = tmp_path / "v.Rnw"
        path.write_text(src, encoding="utf-8")
        parsed = parse_rnw_file(path)
        # Hidden chunk blanked: the R code (and its NULL) is gone.
        assert "NULL" not in parsed.source
        assert "x <- " not in parsed.source

    def test_visible_chunk_trailing_ws_wrapped(self, tmp_path: Path):
        from texlint.core.parser import parse_rnw_file
        src = "<<demo>>=\t\ny <- 1\n@\n"
        path = tmp_path / "v.Rnw"
        path.write_text(src, encoding="utf-8")
        assert "Sinput" in parse_rnw_file(path).source
