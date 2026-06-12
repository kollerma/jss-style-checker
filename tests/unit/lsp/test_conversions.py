"""Spec 011 — LSP conversion tests."""

from __future__ import annotations

from pathlib import Path

from texlint.api import Fix, Severity, Violation
from texlint.lsp.conversions import (
    LSP_SEVERITY,
    _byte_offset_to_lsp_position,
    fix_to_text_edit,
    violation_to_code_action,
    violation_to_diagnostic,
)


def _v(line: int, col: int | None, severity: Severity, fix: Fix | None = None) -> Violation:
    return Violation(
        file=Path("manuscript.tex"),
        line=line,
        column=col,
        rule_id="JSS-TEST-001",
        severity=severity,
        message="msg",
        fix=fix,
    )


class TestSeverityMap:
    def test_error_is_1(self) -> None:
        assert LSP_SEVERITY[Severity.ERROR] == 1

    def test_warning_is_2(self) -> None:
        assert LSP_SEVERITY[Severity.WARNING] == 2

    def test_info_is_3(self) -> None:
        assert LSP_SEVERITY[Severity.INFO] == 3


class TestDiagnostic:
    def test_basic_shape(self) -> None:
        d = violation_to_diagnostic(_v(42, 7, Severity.WARNING))
        assert d["range"]["start"] == {"line": 41, "character": 6}
        assert d["severity"] == 2
        assert d["code"] == "JSS-TEST-001"
        assert d["source"] == "jss-lint"
        assert d["message"] == "msg"

    def test_no_column_defaults_to_zero(self) -> None:
        d = violation_to_diagnostic(_v(1, None, Severity.INFO))
        assert d["range"]["start"]["character"] == 0

    def test_guide_url_carries(self) -> None:
        d = violation_to_diagnostic(_v(1, 1, Severity.ERROR), guide_url="https://x")
        assert d["codeDescription"] == {"href": "https://x"}

    def test_no_guide_url(self) -> None:
        d = violation_to_diagnostic(_v(1, 1, Severity.ERROR))
        assert "codeDescription" not in d


class TestPosition:
    def test_first_line(self) -> None:
        assert _byte_offset_to_lsp_position("hello\nworld", 0) == {"line": 0, "character": 0}

    def test_after_newline(self) -> None:
        assert _byte_offset_to_lsp_position("hello\nworld", 6) == {"line": 1, "character": 0}

    def test_mid_second_line(self) -> None:
        assert _byte_offset_to_lsp_position("hello\nworld", 9) == {"line": 1, "character": 3}


class TestCodeAction:
    def test_no_fix_returns_none(self) -> None:
        v = _v(1, 1, Severity.WARNING, fix=None)
        assert violation_to_code_action(v, source="x", uri="file:///x") is None

    def test_with_fix(self) -> None:
        v = _v(1, 1, Severity.WARNING, fix=Fix(0, 5, "JSS", description="rename"))
        action = violation_to_code_action(v, source="hello world", uri="file:///x")
        assert action is not None
        assert action["title"] == "rename"
        assert action["kind"] == "quickfix"
        edits = action["edit"]["changes"]["file:///x"]
        assert len(edits) == 1
        assert edits[0]["newText"] == "JSS"


class TestFixToTextEdit:
    def test_byte_range_to_lsp_range(self) -> None:
        text = "hello\nworld"
        edit = fix_to_text_edit(Fix(6, 11, "JSS", description="x"), text)
        assert edit["range"]["start"] == {"line": 1, "character": 0}
        assert edit["range"]["end"] == {"line": 1, "character": 5}
        assert edit["newText"] == "JSS"


class TestRangedDiagnostics:
    """With document text available, diagnostics span the offending
    token (or whole line) so editors render visible squiggles."""

    SRC = "first line\nWe use R daily here.\n   trailing ws line   \n"

    def _v(self, line, column):
        return Violation(
            file=Path("m.tex"),
            line=line,
            column=column,
            rule_id="JSS-X-001",
            severity=Severity.WARNING,
            message="msg",
        )

    def test_token_width_range(self):
        # column 8 (1-based) → the "R" token on line 2.
        d = violation_to_diagnostic(self._v(2, 8), source=self.SRC)
        assert d["range"]["start"] == {"line": 1, "character": 7}
        assert d["range"]["end"] == {"line": 1, "character": 8}

    def test_multichar_token(self):
        # column 4 → "use" spans 3 chars.
        d = violation_to_diagnostic(self._v(2, 4), source=self.SRC)
        assert d["range"]["end"]["character"] == 6

    def test_no_column_spans_line(self):
        d = violation_to_diagnostic(self._v(2, None), source=self.SRC)
        assert d["range"]["start"]["character"] == 0
        assert d["range"]["end"]["character"] == len("We use R daily here.")

    def test_column_past_eol_clamped(self):
        d = violation_to_diagnostic(self._v(1, 99), source=self.SRC)
        assert d["range"]["start"]["character"] == len("first line")
        assert d["range"]["end"]["character"] == len("first line")

    def test_line_past_eof_zero_width(self):
        d = violation_to_diagnostic(self._v(42, 3), source=self.SRC)
        assert d["range"]["start"] == d["range"]["end"]

    def test_no_source_back_compat_zero_width(self):
        d = violation_to_diagnostic(self._v(2, 8))
        assert d["range"]["start"] == d["range"]["end"]
        assert d["range"]["start"] == {"line": 1, "character": 7}
