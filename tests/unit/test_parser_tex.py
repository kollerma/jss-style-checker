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
    def test_non_utf8_produces_parse_error(self, tmp_path: Path):
        # latin-1 e-acute; not a valid UTF-8 sequence on its own.
        path = _write(tmp_path, "latin1.tex", b"caf\xe9\n")

        parsed = parse_tex_file(path)

        assert len(parsed.violations) == 1
        v = parsed.violations[0]
        assert v.rule_id == "JSS-PARSE-000"
        assert v.severity.value == "error"
        assert v.line == 1
        # source is empty / sentinel because decoding failed
        assert parsed.nodes == ()


class TestParseTexParseFailure:
    def test_unterminated_group_produces_parse_error(self, tmp_path: Path):
        # pylatexenc raises LatexWalkerError on unclosed group / bad token.
        path = _write(tmp_path, "bad.tex", r"\begin{document")

        parsed = parse_tex_file(path)

        assert len(parsed.violations) == 1
        v = parsed.violations[0]
        assert v.rule_id == "JSS-PARSE-000"
        assert v.severity.value == "error"
        assert v.line >= 1
        # Does not raise.


class TestParseTexMissingFile:
    def test_missing_path_produces_parse_error(self, tmp_path: Path):
        parsed = parse_tex_file(tmp_path / "nope.tex")
        assert len(parsed.violations) == 1
        assert parsed.violations[0].rule_id == "JSS-PARSE-000"
