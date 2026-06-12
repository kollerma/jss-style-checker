"""Unit tests for ``_neutralize_macro_definition_bodies`` and the
tolerant-parse retry in ``parse_tex_source``.

The canonical real-world carrier (strucchange-intro.Rnw line 16)::

    \\newenvironment{smallexample}{\\begin{alltt}\\small}{\\end{alltt}}

trips pylatexenc's strict environment tracking even though the
document is valid — \\begin and \\end live in different brace groups.
21% of the eval corpus failed to parse on this class before the
neutralization pass.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from texlint.api import Severity
from texlint.core.parser import (
    _neutralize_macro_definition_bodies,
    parse_tex_source,
)


def _no_parse_errors(source: str) -> None:
    parsed = parse_tex_source(source, Path("m.tex"))
    assert parsed.violations == (), [v.message for v in parsed.violations]
    assert parsed.nodes


class TestNeutralizePass:
    @pytest.mark.parametrize(
        "src",
        [
            r"\newenvironment{smallexample}{\begin{alltt}\small}{\end{alltt}}",
            r"\newcommand{\open}{\begin{quote}}",
            r"\renewcommand{\open}{\begin{quote}}",
            r"\providecommand{\open}{\begin{quote}}",
            r"\def\open{\begin{center}}",
            r"\renewenvironment{x}{\begin{a}}{\end{a}}",
            # Starred form + optional args + nested default group.
            r"\newcommand*{\y}[2][{dflt}]{\begin{x}#1#2\end{x}}",
            # Bare control-sequence name (no braces around \name).
            r"\newcommand\open{\begin{quote}}",
        ],
    )
    def test_unbalanced_begin_end_in_bodies_neutralized(self, src: str):
        out = _neutralize_macro_definition_bodies(src)
        assert len(out) == len(src)
        assert "\\begin" not in out
        assert "\\end" not in out

    def test_length_and_newlines_preserved(self):
        src = (
            "\\newenvironment{FIXME}{\n"
            "  \\begin{quote}\\strut\\marginpar{FIXME}}{\\end{quote}}\n"
        )
        out = _neutralize_macro_definition_bodies(src)
        assert len(out) == len(src)
        assert out.count("\n") == src.count("\n")

    def test_document_environments_untouched(self):
        src = (
            r"\begin{document}\newcommand{\z}{\begin{a}} body \end{document}"
        )
        out = _neutralize_macro_definition_bodies(src)
        assert out.startswith(r"\begin{document}")
        assert out.endswith(r"\end{document}")
        assert r"{ begin{a}}" in out

    def test_balanced_definition_body_other_content_intact(self):
        src = r"\newcommand{\email}[1]{\href{mailto:#1}{\texttt{#1}}}"
        assert _neutralize_macro_definition_bodies(src) == src

    def test_unclosed_body_left_untouched(self):
        # Never guess on imbalance.
        src = r"\newcommand{\x}{\begin{quote}"
        assert _neutralize_macro_definition_bodies(src) == src


class TestParseTexSourceRecovery:
    def test_newenvironment_with_split_begin_end_parses_clean(self):
        _no_parse_errors(
            "\\newenvironment{smallexample}{\\begin{alltt}\\small}"
            "{\\end{alltt}}\n"
            "\\begin{document}\nhello\n\\end{document}\n"
        )

    def test_def_with_split_begin_parses_clean(self):
        _no_parse_errors(
            "\\def\\open{\\begin{center}}\n"
            "\\begin{document}\nhello\n\\end{document}\n"
        )

    def test_tolerant_retry_yields_warning_and_nodes(self):
        # Genuinely mismatched environments in document text — the
        # strict parser fails, the tolerant retry recovers a node tree
        # and emits a warning-severity (degraded-parse) PARSE-000.
        src = (
            "\\begin{document}\n"
            "\\begin{tabular}{ll}\n"
            "\\end{itemize}\n"
            "prose after the damage\n"
            "\\end{document}\n"
        )
        parsed = parse_tex_source(src, Path("m.tex"))
        assert len(parsed.violations) == 1
        v = parsed.violations[0]
        assert v.rule_id == "JSS-PARSE-000"
        assert v.severity is Severity.WARNING
        assert "tolerant" in v.message
        assert parsed.nodes  # rules can still run
