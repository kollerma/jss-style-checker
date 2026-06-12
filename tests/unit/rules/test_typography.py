"""Tests for JSS typography rules — 100% branch coverage target."""

from __future__ import annotations

from pathlib import Path

from texlint.api import Fix, ParsedDocument, ParsedTexFile, ToolConfig
from texlint.journals.jss.rules.typography import (
    check_jss_typo_001,
    check_jss_typo_002,
    check_jss_typo_003,
    check_jss_typo_004,
    jss_typo_001,
    jss_typo_002,
    jss_typo_003,
    jss_typo_004,
    rules,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "violations" / "typography"
AUTOFIX_DIR = REPO_ROOT / "tests" / "fixtures" / "auto-fix"


def _tex(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_rules_tuple_has_four_rules():
    assert len(rules) == 4


def test_rules_tuple_ids():
    assert {r.id for r in rules} == {f"JSS-TYPO-00{i}" for i in range(1, 5)}


# ---------------------------------------------------------------------------
# JSS-TYPO-001 — caption ends with period
# ---------------------------------------------------------------------------


class TestTypo001:
    def test_positive(self, run_rule):
        violations = run_rule(jss_typo_001, _tex("JSS-TYPO-001-bad.tex"))
        assert len(violations) == 1

    def test_good_silent(self, run_rule):
        assert run_rule(jss_typo_001, _tex("JSS-TYPO-001-good.tex")) == []

    def test_caption_outside_figure_silent(self, run_rule):
        # \caption outside a figure / table env is out of scope.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}\caption{floating}\end{document}"
        )
        assert run_rule(jss_typo_001, src) == []

    def test_caption_without_group_silent(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{figure}\caption\end{figure}" "\n"
            r"\end{document}"
        )
        assert run_rule(jss_typo_001, src) == []

    def test_empty_caption_silent(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{figure}\caption{}\end{figure}" "\n"
            r"\end{document}"
        )
        assert run_rule(jss_typo_001, src) == []

    def test_emits_safe_fix_payload(self, run_rule):
        """Spec 008 follow-up: each violation carries a Fix(...) payload
        whose insertion point lives just after the last visible
        non-whitespace character of the caption text and whose
        replacement is a single ``.``."""
        before = (AUTOFIX_DIR / "JSS-TYPO-001" / "before.tex").read_text(
            encoding="utf-8"
        )
        violations = run_rule(jss_typo_001, before)
        assert len(violations) == 1
        v = violations[0]
        assert isinstance(v.fix, Fix)
        assert v.fix.confidence == "safe"
        # 0-length insert at the same offset.
        assert v.fix.start == v.fix.end
        assert v.fix.replacement == "."
        # Insertion point lands just after the last non-whitespace
        # character of the caption text — i.e. the byte at v.fix.start
        # is the closing brace `}` of the caption argument (possibly
        # preceded by whitespace, but in this fixture it's adjacent).
        assert before[v.fix.start] == "}"

    def test_fix_application_matches_after_fixture(self, run_rule):
        before = (AUTOFIX_DIR / "JSS-TYPO-001" / "before.tex").read_text(
            encoding="utf-8"
        )
        after = (AUTOFIX_DIR / "JSS-TYPO-001" / "after.tex").read_text(
            encoding="utf-8"
        )
        violations = run_rule(jss_typo_001, before)
        fix = violations[0].fix
        assert isinstance(fix, Fix)
        applied = before[: fix.start] + fix.replacement + before[fix.end :]
        assert applied == after
        # Self-verify: re-linting the patched source must not re-fire.
        assert run_rule(jss_typo_001, applied) == []

    def test_fix_skips_caption_with_label_then_text(self, run_rule):
        # \caption{\label{fig:x} text without period} — the rule fires
        # and the fix inserts `.` after "period", before the closing
        # brace, ignoring the leading \label{} caption metadata.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{figure}" "\n"
            r"\caption{\label{fig:x} A caption with label and no period}" "\n"
            r"\end{figure}" "\n"
            r"\end{document}"
        )
        violations = run_rule(jss_typo_001, src)
        assert len(violations) == 1
        fix = violations[0].fix
        assert isinstance(fix, Fix)
        applied = src[: fix.start] + fix.replacement + src[fix.end :]
        assert "no period.}" in applied
        assert run_rule(jss_typo_001, applied) == []

    def test_fix_none_for_question_caption(self, run_rule):
        # Carve-out: a caption ending in `?` is a legitimate
        # interrogative — rule still fires (JSS prefers `.`), but no
        # automatic fix is offered.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{figure}\caption{Why does it work?}\end{figure}" "\n"
            r"\end{document}"
        )
        violations = run_rule(jss_typo_001, src)
        assert len(violations) == 1
        assert violations[0].fix is None

    def test_fix_none_for_exclamation_caption(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{figure}\caption{It works!}\end{figure}" "\n"
            r"\end{document}"
        )
        violations = run_rule(jss_typo_001, src)
        assert len(violations) == 1
        assert violations[0].fix is None

    def test_fix_none_when_caption_ends_with_macro(self, run_rule):
        # \caption{Some text \emph{bold}} — the chars-only projection
        # is "Some text " which doesn't end with `.`, so the rule
        # fires; the last visible content is the \emph macro, so the
        # insertion offset is ambiguous and we leave fix=None.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{figure}\caption{Some text \emph{bold}}\end{figure}" "\n"
            r"\end{document}"
        )
        violations = run_rule(jss_typo_001, src)
        assert len(violations) == 1
        assert violations[0].fix is None


# ---------------------------------------------------------------------------
# JSS-TYPO-002 — caption wholly wrapped in emphasis
# ---------------------------------------------------------------------------


class TestTypo002:
    def test_positive(self, run_rule):
        violations = run_rule(jss_typo_002, _tex("JSS-TYPO-002-bad.tex"))
        assert len(violations) == 1

    def test_good_silent(self, run_rule):
        assert run_rule(jss_typo_002, _tex("JSS-TYPO-002-good.tex")) == []

    def test_intra_caption_emphasis_silent(self, run_rule):
        # Emphasis on a phrase inside a longer caption doesn't fire.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{figure}" "\n"
            r"\caption{Overview of \emph{species} in the dataset.}" "\n"
            r"\end{figure}" "\n"
            r"\end{document}"
        )
        assert run_rule(jss_typo_002, src) == []

    def test_caption_outside_figure_silent(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}\caption{\emph{Stray}}\end{document}"
        )
        assert run_rule(jss_typo_002, src) == []

    def test_caption_without_group_silent(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{figure}\caption\end{figure}" "\n"
            r"\end{document}"
        )
        assert run_rule(jss_typo_002, src) == []


# ---------------------------------------------------------------------------
# JSS-TYPO-003 — \footnote inside table
# ---------------------------------------------------------------------------


class TestTypo003:
    def test_positive(self, run_rule):
        violations = run_rule(jss_typo_003, _tex("JSS-TYPO-003-bad.tex"))
        assert len(violations) == 1

    def test_good_silent(self, run_rule):
        assert run_rule(jss_typo_003, _tex("JSS-TYPO-003-good.tex")) == []

    def test_footnote_outside_table_silent(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}Prose\footnote{note}.\end{document}"
        )
        assert run_rule(jss_typo_003, src) == []


# ---------------------------------------------------------------------------
# JSS-TYPO-004 — caption after content
# ---------------------------------------------------------------------------


class TestTypo004:
    def test_positive(self, run_rule):
        violations = run_rule(jss_typo_004, _tex("JSS-TYPO-004-bad.tex"))
        assert len(violations) == 1

    def test_good_silent(self, run_rule):
        assert run_rule(jss_typo_004, _tex("JSS-TYPO-004-good.tex")) == []

    def test_figure_without_caption_silent(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{figure}\includegraphics{x}\end{figure}" "\n"
            r"\end{document}"
        )
        assert run_rule(jss_typo_004, src) == []

    def test_non_figure_env_silent(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{itemize}\item x\end{itemize}" "\n"
            r"\end{document}"
        )
        assert run_rule(jss_typo_004, src) == []

    def test_centering_before_caption_ok(self, run_rule):
        # \centering / \label before \caption are allowed (not "content").
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{figure}\centering\includegraphics{x}\caption{Ok.}\end{figure}" "\n"
            r"\end{document}"
        )
        assert run_rule(jss_typo_004, src) == []

    def test_only_centering_before_caption_still_flagged(self, run_rule):
        # If ONLY \centering is before \caption (no content), rule still
        # fires because there's no figure content visible before caption.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{figure}\centering\caption{Ok.}\includegraphics{x}\end{figure}" "\n"
            r"\end{document}"
        )
        assert len(run_rule(jss_typo_004, src)) == 1

    def test_stripped_knitr_chunk_treated_as_content(self, run_rule):
        # Many consecutive newlines (≥3) before \caption fingerprint a
        # stripped Sweave / knitr code chunk that produces the figure
        # via fig=TRUE; the rule should not fire.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{figure}" "\n"
            "\n\n\n\n\n"  # simulated stripped chunk: 5 blank lines
            r"\caption{Caption after chunk-produced figure.}" "\n"
            r"\end{figure}" "\n"
            r"\end{document}"
        )
        assert run_rule(jss_typo_004, src) == []

    def test_single_newline_before_caption_still_flagged(self, run_rule):
        # A single newline between \begin{figure} and \caption is
        # normal source formatting, NOT a chunk fingerprint — rule
        # still fires when there's no other content.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{figure}" "\n"
            r"\caption{Caption.}\includegraphics{x}\end{figure}" "\n"
            r"\end{document}"
        )
        assert len(run_rule(jss_typo_004, src)) == 1

    def test_table_caption_above_flagged(self, run_rule):
        # Updated 2026-06-11: JSS style places BOTH figure and table
        # captions BELOW the content (per recall-corpus annotations:
        # deSolve.Rnw:1849 et al. "Table caption should be below
        # table, not above"). The rule fires on table envs whose
        # ``\caption{}`` precedes the body content.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\begin{document}" "\n"
            r"\begin{table}[htb]" "\n"
            r"\caption{Caption above the table.}" "\n"
            r"\label{tab:x}" "\n"
            r"\begin{tabular}{ll}a & b\\\end{tabular}" "\n"
            r"\end{table}" "\n"
            r"\end{document}"
        )
        violations = run_rule(jss_typo_004, src)
        assert len(violations) == 1
        assert violations[0].rule_id == "JSS-TYPO-004"


def test_group_visible_children_skips_label(parse_tex_source):
    from pylatexenc.latexwalker import LatexGroupNode

    from texlint.journals.jss.rules.typography import _group_visible_children
    # `\label{x} some text` — inside the caption group, \label and its arg
    # are skipped; 'some text' remains.
    tex = parse_tex_source(r"{\label{x} some text}")
    group = next(n for n in tex.nodes if isinstance(n, LatexGroupNode))
    visible = _group_visible_children(group)
    assert visible  # at least one visible chars node


def test_first_group_arg_no_nodeargd():
    from pylatexenc.latexwalker import LatexMacroNode

    from texlint.journals.jss.rules.typography import _first_group_arg

    class FakeMacro(LatexMacroNode):
        def __init__(self):  # type: ignore[no-untyped-def]
            pass

    fake = FakeMacro()
    assert _first_group_arg(fake, (fake,), 0) is None


def test_first_group_arg_from_argnlist(parse_tex_source):
    # \emph is known to pylatexenc — its arg lives in argnlist so
    # _first_group_arg returns at the argnlist branch.
    from pylatexenc.latexwalker import LatexMacroNode

    from texlint.journals.jss.rules.typography import _first_group_arg
    tex = parse_tex_source(r"\emph{x}")
    mac = next(n for n in tex.nodes if isinstance(n, LatexMacroNode))
    idx = tex.nodes.index(mac)
    arg = _first_group_arg(mac, tex.nodes, idx)
    assert arg is not None


def test_strip_trailing_punct_keeps_real_text():
    from pylatexenc.latexwalker import LatexCharsNode

    from texlint.journals.jss.rules.typography import _strip_trailing_punct

    class FakeChars(LatexCharsNode):
        def __init__(self, text):  # type: ignore[no-untyped-def]
            self.chars = text

    a = FakeChars("hello")
    assert _strip_trailing_punct([a]) == [a]


def test_strip_trailing_punct_empty():
    from texlint.journals.jss.rules.typography import _strip_trailing_punct
    assert _strip_trailing_punct([]) == []


def test_first_group_arg_skips_non_group_in_argnlist(parse_tex_source):
    # \section[opts]{title} — argnlist has the optional arg before the
    # mandatory. Exercises the argnlist loop continuing past a non-group
    # entry to return the mandatory group.
    from pylatexenc.latexwalker import LatexMacroNode

    from texlint.journals.jss.rules.typography import _first_group_arg
    tex = parse_tex_source(r"\section[opts]{title}")
    mac = next(n for n in tex.nodes if isinstance(n, LatexMacroNode))
    idx = tex.nodes.index(mac)
    assert _first_group_arg(mac, tex.nodes, idx) is not None


def test_empty_tex_silent():
    tex = ParsedTexFile(path=Path("/tmp/x.tex"), source="", nodes=(), walker=None)
    doc = ParsedDocument(tex_files=(tex,))
    for check in (
        check_jss_typo_001, check_jss_typo_002,
        check_jss_typo_003, check_jss_typo_004,
    ):
        assert list(check(doc, ToolConfig())) == []
