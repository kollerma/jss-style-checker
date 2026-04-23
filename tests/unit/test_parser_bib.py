"""Unit tests for ``texlint.core.parser.parse_bib_file``."""

from __future__ import annotations

from pathlib import Path

from texlint.core.parser import parse_bib_file


def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


COMPLIANT_BIB = """
@article{smith2020,
  author = {Smith, J.},
  title  = {A Study},
  year   = {2020},
}
"""


class TestParseBibHappyPath:
    def test_returns_parsed_file_with_library_and_source(self, tmp_path: Path):
        path = _write(tmp_path, "refs.bib", COMPLIANT_BIB)

        parsed = parse_bib_file(path)

        assert parsed.path == path
        assert parsed.source == COMPLIANT_BIB
        assert parsed.library is not None
        assert len(parsed.library.entries) == 1
        assert parsed.violations == ()


class TestParseBibFailedBlock:
    def test_failed_block_becomes_parse_error(self, tmp_path: Path):
        malformed = "@article{broken, author = {Unclosed,\n"
        path = _write(tmp_path, "bad.bib", malformed)

        parsed = parse_bib_file(path)

        assert any(v.rule_id == "JSS-PARSE-000" for v in parsed.violations)
        assert all(v.severity.value == "error" for v in parsed.violations)


class TestParseBibMissingFile:
    def test_missing_path_produces_parse_error(self, tmp_path: Path):
        parsed = parse_bib_file(tmp_path / "nope.bib")
        assert len(parsed.violations) == 1
        assert parsed.violations[0].rule_id == "JSS-PARSE-000"


class TestParseBibEncoding:
    def test_non_utf8_produces_parse_error(self, tmp_path: Path):
        path = tmp_path / "latin1.bib"
        path.write_bytes(b"@article{x, author={caf\xe9}, year={2020}}\n")
        parsed = parse_bib_file(path)
        assert len(parsed.violations) == 1
        assert parsed.violations[0].rule_id == "JSS-PARSE-000"
