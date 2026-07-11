"""Tests for JSS code_style rules — 100% branch coverage target."""

from __future__ import annotations

from pathlib import Path

from texlint.api import ParsedDocument, ParsedTexFile, ToolConfig
from texlint.journals.jss.rules.code_style import (
    check_jss_code_001,
    check_jss_code_002,
    check_jss_code_003,
    jss_code_001,
    jss_code_002,
    jss_code_003,
    rules,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "violations" / "code_style"


def _tex(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_rules_tuple_has_three_rules():
    assert len(rules) == 3


def test_rules_tuple_ids():
    assert {r.id for r in rules} == {f"JSS-CODE-00{i}" for i in range(1, 4)}


# ---------------------------------------------------------------------------
# JSS-CODE-001 — comments inside code envs
# ---------------------------------------------------------------------------


class TestCode001:
    def test_positive(self, run_rule):
        violations = run_rule(jss_code_001, _tex("JSS-CODE-001-bad.tex"))
        assert len(violations) == 1

    def test_good_silent(self, run_rule):
        assert run_rule(jss_code_001, _tex("JSS-CODE-001-good.tex")) == []

    def test_comment_outside_codeinput_silent(self, run_rule):
        # A '#' in prose is not a code comment.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}See issue #5 later.\end{document}"
        )
        assert run_rule(jss_code_001, src) == []

    def test_non_code_env_silent(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{itemize}\item x\end{itemize}" "\n"
            r"\end{document}"
        )
        assert run_rule(jss_code_001, src) == []

    def test_only_first_comment_per_block(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{CodeInput}" "\n"
            r"# one" "\n"
            r"# two" "\n"
            r"\end{CodeInput}" "\n"
            r"\end{document}"
        )
        violations = run_rule(jss_code_001, src)
        # Only one violation per code block (break after first hit).
        assert len(violations) == 1

    def test_non_chars_children_silent(self, run_rule):
        # CodeInput wrapping a macro (unusual) — no chars, no comments.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{CodeInput}\relax\end{CodeInput}" "\n"
            r"\end{document}"
        )
        assert run_rule(jss_code_001, src) == []


# ---------------------------------------------------------------------------
# JSS-CODE-002 — unquoted library() / data()
# ---------------------------------------------------------------------------


class TestCode002:
    def test_positive(self, run_rule):
        violations = run_rule(jss_code_002, _tex("JSS-CODE-002-bad.tex"))
        # Both library(MASS) and data(quine) unquoted.
        assert len(violations) == 2

    def test_good_silent(self, run_rule):
        assert run_rule(jss_code_002, _tex("JSS-CODE-002-good.tex")) == []

    def test_require_also_flagged(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{CodeInput}require(MASS)\end{CodeInput}" "\n"
            r"\end{document}"
        )
        assert len(run_rule(jss_code_002, src)) == 1

    def test_outside_code_env_silent(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}library(MASS)\end{document}"
        )
        assert run_rule(jss_code_002, src) == []

    def test_non_chars_in_code_env_silent(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{CodeInput}\relax\end{CodeInput}" "\n"
            r"\end{document}"
        )
        assert run_rule(jss_code_002, src) == []

    def test_non_code_env_silent(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{itemize}\item x\end{itemize}" "\n"
            r"\end{document}"
        )
        assert run_rule(jss_code_002, src) == []

    def test_emits_safe_fix_payload(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{CodeInput}library(MASS)\end{CodeInput}" "\n"
            r"\end{document}"
        )
        violations = run_rule(jss_code_002, src)
        assert len(violations) == 1
        v = violations[0]
        assert v.fix is not None
        assert v.fix.replacement.startswith('"')
        assert v.fix.replacement.endswith('"')
        assert v.fix.replacement == '"MASS"'
        assert v.fix.confidence == "safe"
        assert v.fix.end > v.fix.start
        # Apply the fix to the original source and confirm the
        # bareword is now wrapped in double quotes.
        before = src
        rewritten = (
            before[: v.fix.start] + v.fix.replacement + before[v.fix.end :]
        )
        assert "library(MASS)" not in rewritten
        assert 'library("MASS")' in rewritten


# ---------------------------------------------------------------------------
# JSS-CODE-003 — missing spaces in \code{}
# ---------------------------------------------------------------------------


class TestCode003:
    def test_positive(self, run_rule):
        violations = run_rule(jss_code_003, _tex("JSS-CODE-003-bad.tex"))
        assert len(violations) == 1

    def test_good_silent(self, run_rule):
        assert run_rule(jss_code_003, _tex("JSS-CODE-003-good.tex")) == []

    def test_code_with_no_arg_silent(self, run_rule):
        src = r"\code"
        assert run_rule(jss_code_003, src) == []

    def test_empty_code_silent(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}\code{}\end{document}"
        )
        assert run_rule(jss_code_003, src) == []

    def test_code_with_comma_no_space_flagged(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}\code{f(a,b)}\end{document}"
        )
        assert len(run_rule(jss_code_003, src)) == 1

    def test_code_with_only_chars_well_spaced(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}\code{abc}\end{document}"
        )
        assert run_rule(jss_code_003, src) == []

    def test_assignment_arrow_no_spaces_flagged(self, run_rule):
        # R assignment ``<-`` needs surrounding spaces; ``x<-y`` was missed
        # because ``<`` is not a single-char operator (recall-corpus
        # CUB.Rnw:798/931).
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}\code{pai1<-coef(x)}\end{document}"
        )
        assert len(run_rule(jss_code_003, src)) == 1

    def test_assignment_arrow_well_spaced_silent(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}\code{x <- coef(y)}\end{document}"
        )
        assert run_rule(jss_code_003, src) == []

    def test_right_and_super_assign_flagged(self, run_rule):
        for op in ("->", "<<-"):
            src = (
                r"\documentclass[article]{jss}" "\n"
                rf"\begin{{document}}\code{{a{op}b}}\end{{document}}"
            )
            assert len(run_rule(jss_code_003, src)) == 1, op

    def test_comparison_operators_no_spaces_flagged(self, run_rule):
        for op in ("==", "!=", "<=", ">="):
            src = (
                r"\documentclass[article]{jss}" "\n"
                rf"\begin{{document}}\code{{n{op}10}}\end{{document}}"
            )
            assert len(run_rule(jss_code_003, src)) == 1, op

    def test_comparison_operators_well_spaced_silent(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}\code{n <= 10}\end{document}"
        )
        assert run_rule(jss_code_003, src) == []

    def test_cli_flag_silent(self, run_rule):
        # `--fix` is option syntax, not a missing-space subtraction
        # (surfaced by linting this project's own manuscript, which
        # documents its command-line interface).
        for content in ("--fix", "--min-confidence", "-v"):
            src = (
                r"\documentclass[article]{jss}" "\n"
                rf"\begin{{document}}\code{{{content}}}\end{{document}}"
            )
            assert run_rule(jss_code_003, src) == [], content

    def test_command_words_silent(self, run_rule):
        # Space-separated command words / flags / dotfiles / paths are
        # names, not operator expressions.
        for content in (
            "--fix --dry-run",
            "cargo install jsslint-cli",
            ".jss-lint.toml",
            "jss-lint examples/demo.tex",
        ):
            src = (
                r"\documentclass[article]{jss}" "\n"
                rf"\begin{{document}}\code{{{content}}}\end{{document}}"
            )
            assert run_rule(jss_code_003, src) == [], content

    def test_command_words_with_expression_still_flagged(self, run_rule):
        # A name-like prefix must not shadow a real spacing defect in a
        # later token.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}\code{Rscript -e x<-coef(y)}\end{document}"
        )
        assert len(run_rule(jss_code_003, src)) == 1

    def test_dash_inside_string_literal_silent(self, run_rule):
        # \code{vignette("plot3logit-overview")} — the dash in the
        # string literal is a vignette filename, not a subtraction
        # operator. Mask string literals before the operator check.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r'\begin{document}\code{vignette("plot3logit-overview")}\end{document}'
        )
        assert run_rule(jss_code_003, src) == []

    def test_code_env_violation_anchored_at_env_opening(self, run_rule):
        # A code-env (Sinput / CodeInput / chunk) violation reports at the
        # env opening (``\begin{...}`` column), consistent with the
        # ``\code{}`` pass reporting at the macro ``\`` — not mid-line at
        # the content offset after the ``\begin`` tag.
        src = (
            "\\documentclass[article]{jss}\n"
            "\\begin{document}\n"
            "\\begin{CodeInput}\n"
            "f(x=1)\n"
            "\\end{CodeInput}\n"
            "\\end{document}\n"
        )
        violations = run_rule(jss_code_003, src)
        assert len(violations) == 1
        # `\begin{CodeInput}` is on line 3, column 1.
        assert violations[0].line == 3
        assert violations[0].column == 1

    def test_code_output_env_not_flagged(self, run_rule):
        # Program output (CodeOutput / Soutput) is verbatim tool output,
        # not author-written code, so CODE-003 must not fire on it — you
        # cannot restyle what R printed. Real corpus regressions: a
        # "p-value" / "R-squared" hyphen and a "k=4" summary line inside a
        # CodeOutput block were being misread as unspaced operators.
        src = (
            "\\documentclass[article]{jss}\n"
            "\\begin{document}\n"
            "\\begin{CodeOutput}\n"
            "z =  2.2666  p-value =  0.0117\n"
            "Mean R-squared: 0.7523  k=4\n"
            "\\end{CodeOutput}\n"
            "\\end{document}\n"
        )
        assert run_rule(jss_code_003, src) == []

    def test_soutput_env_not_flagged(self, run_rule):
        # Same contract for the Sweave-style output env.
        src = (
            "\\documentclass[article]{jss}\n"
            "\\begin{document}\n"
            "\\begin{Soutput}\n"
            "delta:  10  type: under,rounds=250\n"
            "\\end{Soutput}\n"
            "\\end{document}\n"
        )
        assert run_rule(jss_code_003, src) == []

    def test_keyword_arg_flagged(self, run_rule):
        # JSS style requires spaces around ``=`` even in function-
        # argument keyword position. Updated 2026-06-11 to align with
        # the recall-corpus hand annotations (CARBayesST.Rnw:52 et al.):
        # the previous reviewer "FP" classification was over-cautious —
        # JSS overrides R/Python convention here.
        for snippet in (
            "n.cores=1",
            "W.binary=TRUE",
            "interaction=TRUE",
            'method="exact"',
            "n=100",
            "x=NA",
        ):
            src = (
                r"\documentclass[article]{jss}" "\n"
                r"\begin{document}"
                f"\\code{{{snippet}}}"
                r"\end{document}"
            )
            assert len(run_rule(jss_code_003, src)) == 1, snippet

    def test_assignment_with_operator_still_flagged(self, run_rule):
        # ``y=a+b`` — has multiple operators, not a keyword-arg form;
        # the rule should still flag it.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}\code{y=a+b}\end{document}"
        )
        assert len(run_rule(jss_code_003, src)) == 1

    def test_dash_inside_single_quoted_string_silent(self, run_rule):
        # Same exemption for single-quoted strings.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}\code{f('a-b')}\end{document}"
        )
        assert run_rule(jss_code_003, src) == []

    def test_first_group_arg_fallback(self, parse_tex_source):
        from texlint.journals.jss.rules.code_style import _first_group_arg
        tex = parse_tex_source(r"\someunknownmacro{inside}")
        from pylatexenc.latexwalker import LatexMacroNode

        from texlint.journals.jss.rules._helpers import _iter_with_parent
        for parent, idx, node in _iter_with_parent(tex.nodes):
            if isinstance(node, LatexMacroNode) and node.macroname == "someunknownmacro":
                assert _first_group_arg(node, parent, idx) is not None
                return
        raise AssertionError("macro not found")

    def test_first_group_arg_no_nodeargd(self):
        from pylatexenc.latexwalker import LatexMacroNode

        from texlint.journals.jss.rules.code_style import _first_group_arg

        class FakeMacro(LatexMacroNode):
            def __init__(self):  # type: ignore[no-untyped-def]
                pass

        assert _first_group_arg(FakeMacro(), (FakeMacro(),), 0) is None

    def test_first_group_arg_skips_non_group_before_group(self, parse_tex_source):
        # Construct a fake macro whose argnlist has a non-group entry first,
        # then a real LatexGroupNode — exercises the `isinstance` false branch.
        from pylatexenc.latexwalker import LatexMacroNode

        from texlint.journals.jss.rules.code_style import _first_group_arg
        tex = parse_tex_source(r"\emph{inside}")
        emph = next(n for n in tex.nodes if isinstance(n, LatexMacroNode))
        group = emph.nodeargd.argnlist[0]

        class FakeArgd:
            def __init__(self, items):  # type: ignore[no-untyped-def]
                self.argnlist = items

        class FakeMacro(LatexMacroNode):
            def __init__(self, argd):  # type: ignore[no-untyped-def]
                self.nodeargd = argd

        # First arg is a non-group object; second is a real group.
        fake = FakeMacro(FakeArgd([object(), group]))
        assert _first_group_arg(fake, (fake,), 0) is group

    def test_first_group_arg_from_argnlist(self, parse_tex_source):
        # pylatexenc knows \emph → its arg is in argnlist as a LatexGroupNode.
        from pylatexenc.latexwalker import LatexMacroNode

        from texlint.journals.jss.rules.code_style import _first_group_arg
        tex = parse_tex_source(r"\emph{inside}")
        emph = next(n for n in tex.nodes if isinstance(n, LatexMacroNode))
        idx = tex.nodes.index(emph)
        arg = _first_group_arg(emph, tex.nodes, idx)
        assert arg is not None

    def test_group_plain_text_skips_non_chars(self, run_rule):
        # \code{\emph{x}} — nested macro child; _group_plain_text returns ''
        # after skipping the non-CharsNode, so the rule stays silent.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}\code{\emph{x}}\end{document}"
        )
        assert run_rule(jss_code_003, src) == []


def test_all_silent_on_empty_tex():
    tex = ParsedTexFile(path=Path("/tmp/x.tex"), source="", nodes=(), walker=None)
    doc = ParsedDocument(tex_files=(tex,))
    for check in (check_jss_code_001, check_jss_code_002, check_jss_code_003):
        assert list(check(doc, ToolConfig())) == []
