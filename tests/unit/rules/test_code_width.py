"""Tests for JSS code_width rule — 100% branch coverage target."""

from __future__ import annotations

from pathlib import Path

from texlint.api import ParsedDocument, ParsedTexFile, Severity, ToolConfig
from texlint.journals.jss.rules.code_width import (
    check_jss_width_001,
    jss_width_001,
    rules,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "violations" / "code_width"


def _tex(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_rules_tuple_has_one_rule():
    assert len(rules) == 1


def test_rule_id():
    assert rules[0].id == "JSS-WIDTH-001"


class TestWidth001:
    def test_positive(self, run_rule):
        violations = run_rule(jss_width_001, _tex("JSS-WIDTH-001-bad.tex"))
        assert len(violations) == 1
        v = violations[0]
        assert v.rule_id == "JSS-WIDTH-001"
        assert v.severity == Severity.WARNING
        # The offending column count exceeds 80.
        assert v.column > 80

    def test_good_silent(self, run_rule):
        assert run_rule(jss_width_001, _tex("JSS-WIDTH-001-good.tex")) == []

    def test_non_code_env_silent(self, run_rule):
        # Long prose line outside a code env doesn't fire WIDTH-001.
        long_line = "x" * 100
        src = (
            "\\documentclass[article]{jss}\n"
            "\\begin{document}\n"
            f"{long_line}\n"
            "\\end{document}\n"
        )
        assert run_rule(jss_width_001, src) == []

    def test_configurable_limit(self, run_rule):
        # Custom limit of 60 — a 70-char line in CodeInput fires.
        long = "x" * 70
        src = (
            "\\documentclass[article]{jss}\n"
            "\\begin{document}\n"
            "\\begin{CodeInput}\n"
            f"{long}\n"
            "\\end{CodeInput}\n"
            "\\end{document}\n"
        )
        violations = run_rule(
            jss_width_001, src, config=ToolConfig(code_width=60)
        )
        assert len(violations) == 1

    def test_trailing_whitespace_not_counted(self, run_rule):
        # 80 visible columns + trailing spaces: invisible in the rendered
        # listing, so it fits and must not fire. Corpus regression: DAKS /
        # CARBayes CodeInput lines of exactly 80 chars plus a stray space.
        line = "x" * 80 + "   "
        src = (
            "\\documentclass[article]{jss}\n"
            "\\begin{document}\n"
            "\\begin{CodeInput}\n"
            f"{line}\n"
            "\\end{CodeInput}\n"
            "\\end{document}\n"
        )
        assert run_rule(jss_width_001, src) == []

    def test_visible_width_over_limit_flagged(self, run_rule):
        # 81 visible columns (even with no trailing space) still overflows.
        line = "x" * 81
        src = (
            "\\documentclass[article]{jss}\n"
            "\\begin{document}\n"
            "\\begin{CodeInput}\n"
            f"{line}\n"
            "\\end{CodeInput}\n"
            "\\end{document}\n"
        )
        violations = run_rule(jss_width_001, src)
        assert len(violations) == 1
        # Reported width is the visible width, not the raw length.
        assert violations[0].column == 81

    def test_reported_length_excludes_trailing_ws(self, run_rule):
        # 85 visible + trailing spaces -> flagged, but width reported is 85.
        line = "x" * 85 + "     "
        src = (
            "\\documentclass[article]{jss}\n"
            "\\begin{document}\n"
            "\\begin{CodeInput}\n"
            f"{line}\n"
            "\\end{CodeInput}\n"
            "\\end{document}\n"
        )
        violations = run_rule(jss_width_001, src)
        assert len(violations) == 1
        assert violations[0].column == 85

    def test_empty_env_silent(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{CodeInput}\end{CodeInput}" "\n"
            r"\end{document}"
        )
        assert run_rule(jss_width_001, src) == []

    def test_multiple_code_envs(self, run_rule):
        long_line = "x" * 100
        src = (
            "\\documentclass[article]{jss}\n"
            "\\begin{document}\n"
            "\\begin{CodeInput}\n"
            f"{long_line}\n"
            "\\end{CodeInput}\n"
            "\n"
            "\\begin{Sinput}\n"
            f"{long_line}\n"
            "\\end{Sinput}\n"
            "\\end{document}\n"
        )
        violations = run_rule(jss_width_001, src)
        assert len(violations) == 2


def test_empty_source_silent():
    tex = ParsedTexFile(path=Path("/tmp/x.tex"), source="", nodes=(), walker=None)
    doc = ParsedDocument(tex_files=(tex,))
    assert list(check_jss_width_001(doc, ToolConfig())) == []


def test_env_content_span_empty_nodelist():
    from texlint.journals.jss.rules.code_width import _env_content_span

    class FakeEnv:
        nodelist = ()

    assert _env_content_span(FakeEnv()) == (None, None)


def test_env_content_span_missing_pos():
    from texlint.journals.jss.rules.code_width import _env_content_span

    class FakeNode:
        pos = None
        len = 0

    class FakeEnv:
        nodelist = (FakeNode(),)

    assert _env_content_span(FakeEnv()) == (None, None)
