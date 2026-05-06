"""Spec 015 follow-up — manuscript metadata extraction tests.

`texlint.report.extract_metadata(document)` walks the parsed
preamble and returns ``(title, author)`` extracted from
``\\title{}`` / ``\\Plaintitle{}`` and ``\\author{}`` /
``\\Plainauthor{}`` macros. The CLI ``report`` subcommand uses
these as defaults when the user does not pass ``--title`` /
``--author``.
"""

from __future__ import annotations

from pathlib import Path

from texlint.core.parser import parse_tex_file
from texlint.report import extract_metadata


def _doc_from_source(tmp_path: Path, source: str) -> ParsedDocument:  # noqa: F821
    from texlint.api import ParsedDocument

    p = tmp_path / "manuscript.tex"
    p.write_text(source, encoding="utf-8")
    parsed = parse_tex_file(p)
    return ParsedDocument(tex_files=(parsed,))


class TestExtractMetadata:
    def test_title_and_author(self, tmp_path: Path) -> None:
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\title{A Short Demo}" "\n"
            r"\author{Jane Doe}" "\n"
            r"\Abstract{Demo.}" "\n"
            r"\Keywords{demo}" "\n"
            r"\Address{Demo}" "\n"
            r"\begin{document}" "\n"
            r"Body." "\n"
            r"\end{document}" "\n"
        )
        title, author = extract_metadata(_doc_from_source(tmp_path, src))
        assert title == "A Short Demo"
        assert author == "Jane Doe"

    def test_plainauthor_wins_over_author(self, tmp_path: Path) -> None:
        """When both macros are present, the markup-free
        ``\\Plainauthor{}`` form should take priority."""
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\title{Foo}" "\n"
            r"\author{Jane \emph{Doe}}" "\n"
            r"\Plainauthor{Jane Doe}" "\n"
            r"\Abstract{Demo.}" "\n"
            r"\Keywords{demo}" "\n"
            r"\Address{Demo}" "\n"
            r"\begin{document}" "\n"
            r"Body." "\n"
            r"\end{document}" "\n"
        )
        _, author = extract_metadata(_doc_from_source(tmp_path, src))
        assert author == "Jane Doe"

    def test_missing_macros_return_none(self, tmp_path: Path) -> None:
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\Abstract{Demo.}" "\n"
            r"\Keywords{demo}" "\n"
            r"\Address{Demo}" "\n"
            r"\begin{document}" "\n"
            r"Body." "\n"
            r"\end{document}" "\n"
        )
        title, author = extract_metadata(_doc_from_source(tmp_path, src))
        assert title is None
        assert author is None

    def test_title_with_inline_markup_is_flattened(self, tmp_path: Path) -> None:
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\title{The \pkg{Foo} Package}" "\n"
            r"\Abstract{Demo.}" "\n"
            r"\Keywords{demo}" "\n"
            r"\Address{Demo}" "\n"
            r"\begin{document}" "\n"
            r"Body." "\n"
            r"\end{document}" "\n"
        )
        title, _ = extract_metadata(_doc_from_source(tmp_path, src))
        assert title is not None
        # The Foo from \pkg{Foo} survives; surrounding whitespace too.
        assert "Foo" in title
        assert "The" in title

    def test_empty_brace_returns_none(self, tmp_path: Path) -> None:
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\title{}" "\n"
            r"\author{}" "\n"
            r"\Abstract{Demo.}" "\n"
            r"\Keywords{demo}" "\n"
            r"\Address{Demo}" "\n"
            r"\begin{document}" "\n"
            r"Body." "\n"
            r"\end{document}" "\n"
        )
        title, author = extract_metadata(_doc_from_source(tmp_path, src))
        # Empty braces produce empty strings post-strip, which the
        # extractor reports as None per its contract.
        assert title is None
        assert author is None
