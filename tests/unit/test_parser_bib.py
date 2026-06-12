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


class TestDuplicateFieldKeyRecovery:
    """A duplicated field within an entry is recoverable: BibTeX itself
    tolerates it (last wins). The entry rejoins the library for bib
    rules and the defect surfaces as a warning-severity degraded-parse
    finding instead of failing the file (robustbase, distrMod et al.
    in the eval corpus)."""

    SRC = "@article{k, url = {a}, url = {b}, title = {T}}\n"

    def test_entry_recovered_into_library(self, tmp_path: Path):
        path = tmp_path / "refs.bib"
        path.write_text(self.SRC, encoding="utf-8")

        parsed = parse_bib_file(path)

        assert [e.key for e in parsed.library.entries] == ["k"]
        # Last occurrence of the duplicated field wins.
        assert parsed.library.entries[0].fields_dict["url"].value == "b"

    def test_warning_violation_names_field_and_entry(self, tmp_path: Path):
        path = tmp_path / "refs.bib"
        path.write_text(self.SRC, encoding="utf-8")

        parsed = parse_bib_file(path)

        assert len(parsed.violations) == 1
        v = parsed.violations[0]
        assert v.rule_id == "JSS-PARSE-000"
        assert v.severity.value == "warning"
        assert "url" in v.message
        assert "'k'" in v.message

    def test_unrecoverable_block_still_error(self, tmp_path: Path):
        path = tmp_path / "refs.bib"
        path.write_text("@article{x, title = {never closed\n", encoding="utf-8")

        parsed = parse_bib_file(path)

        assert len(parsed.violations) == 1
        assert parsed.violations[0].severity.value == "error"
        # The fallback text replaces the previously empty message.
        assert parsed.violations[0].message != "BibTeX parse error: "

    def test_no_stderr_noise_from_middleware(self, tmp_path: Path, capsys):
        path = tmp_path / "refs.bib"
        path.write_text(self.SRC, encoding="utf-8")

        parse_bib_file(path)

        captured = capsys.readouterr()
        assert "Unknown block type" not in captured.err

    def test_duplicate_block_keys_unchanged(self, tmp_path: Path):
        # Sibling behaviour guard: duplicate *citation keys* stay out
        # of the parse channel (JSS-BIBTEX-002 reports them).
        path = tmp_path / "refs.bib"
        path.write_text(
            "@article{k, title = {A}}\n@article{k, title = {B}}\n",
            encoding="utf-8",
        )

        parsed = parse_bib_file(path)

        assert parsed.violations == ()
