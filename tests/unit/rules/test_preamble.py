"""Tests for JSS preamble rules — 100% branch coverage target."""

from __future__ import annotations

from pathlib import Path

from texlint.api import Fix, ParsedDocument, ParsedTexFile, Severity, ToolConfig
from texlint.journals.jss.rules.preamble import (
    check_jss_pre_001,
    check_jss_pre_002,
    check_jss_pre_003,
    check_jss_pre_004,
    check_jss_pre_005,
    check_jss_pre_006,
    check_jss_pre_007,
    check_jss_pre_008,
    jss_pre_001,
    jss_pre_002,
    jss_pre_003,
    jss_pre_004,
    jss_pre_005,
    jss_pre_006,
    jss_pre_007,
    jss_pre_008,
    rules,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "violations" / "preamble"


def _tex(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_rules_tuple_has_eight_rules():
    assert len(rules) == 8


def test_rules_tuple_ids():
    assert {r.id for r in rules} == {f"JSS-PRE-00{i}" for i in range(1, 9)}


# ---------------------------------------------------------------------------
# JSS-PRE-001 — documentclass
# ---------------------------------------------------------------------------


class TestPre001:
    def test_positive_wrong_class(self, run_rule):
        violations = run_rule(jss_pre_001, _tex("JSS-PRE-001-bad.tex"))
        assert len(violations) == 1
        assert violations[0].severity == Severity.ERROR

    def test_good_fixture_silent(self, run_rule):
        assert run_rule(jss_pre_001, _tex("JSS-PRE-001-good.tex")) == []

    def test_no_documentclass_silent(self, run_rule):
        assert run_rule(jss_pre_001, "% no documentclass") == []

    def test_unknown_class_option_flagged(self, run_rule):
        src = r"\documentclass[weirdopt]{jss}" "\n\\begin{document}\\end{document}"
        violations = run_rule(jss_pre_001, src)
        assert len(violations) == 1
        assert "Unknown" in violations[0].suggestion

    def test_known_shortnames_option_ok(self, run_rule):
        src = (
            r"\documentclass[article,shortnames]{jss}" "\n"
            r"\begin{document}\end{document}"
        )
        assert run_rule(jss_pre_001, src) == []

    def test_documentclass_jss_no_options_ok(self, run_rule):
        src = r"\documentclass{jss}" "\n\\begin{document}\\end{document}"
        assert run_rule(jss_pre_001, src) == []


# ---------------------------------------------------------------------------
# JSS-PRE-002 — \Address{}
# ---------------------------------------------------------------------------


class TestPre002:
    def test_positive(self, run_rule):
        violations = run_rule(jss_pre_002, _tex("JSS-PRE-002-bad.tex"))
        assert len(violations) == 1
        assert violations[0].rule_id == "JSS-PRE-002"

    def test_good_fixture_silent(self, run_rule):
        assert run_rule(jss_pre_002, _tex("JSS-PRE-002-good.tex")) == []

    def test_non_jss_class_silent(self, run_rule):
        # Non-jss doc has no Address requirement.
        src = (
            r"\documentclass{article}" "\n"
            r"\begin{document}\end{document}"
        )
        assert run_rule(jss_pre_002, src) == []


# ---------------------------------------------------------------------------
# JSS-PRE-003 — title markup ↔ Plaintitle
# ---------------------------------------------------------------------------


class TestPre003:
    def test_positive(self, run_rule):
        violations = run_rule(jss_pre_003, _tex("JSS-PRE-003-bad.tex"))
        assert len(violations) == 1
        assert violations[0].rule_id == "JSS-PRE-003"

    def test_good_fixture_silent(self, run_rule):
        assert run_rule(jss_pre_003, _tex("JSS-PRE-003-good.tex")) == []

    def test_plain_title_no_companion_needed(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\title{A Plain Title}" "\n"
            r"\begin{document}\end{document}"
        )
        assert run_rule(jss_pre_003, src) == []

    def test_no_title_silent(self, run_rule):
        src = r"\documentclass[article]{jss}" "\n\\begin{document}\\end{document}"
        assert run_rule(jss_pre_003, src) == []


# ---------------------------------------------------------------------------
# JSS-PRE-004 — Abstract
# ---------------------------------------------------------------------------


class TestPre004:
    def test_positive_missing(self, run_rule):
        violations = run_rule(jss_pre_004, _tex("JSS-PRE-004-bad.tex"))
        assert len(violations) == 1

    def test_good_silent(self, run_rule):
        assert run_rule(jss_pre_004, _tex("JSS-PRE-004-good.tex")) == []

    def test_sentinel_flagged(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\Abstract{---!!!---an abstract is required---!!!---}" "\n"
            r"\begin{document}\end{document}"
        )
        violations = run_rule(jss_pre_004, src)
        assert len(violations) == 1
        assert "placeholder" in violations[0].suggestion

    def test_non_jss_class_silent(self, run_rule):
        src = r"\documentclass{article}" "\n\\begin{document}\\end{document}"
        assert run_rule(jss_pre_004, src) == []


# ---------------------------------------------------------------------------
# JSS-PRE-005 — Keywords
# ---------------------------------------------------------------------------


class TestPre005:
    def test_positive_missing(self, run_rule):
        violations = run_rule(jss_pre_005, _tex("JSS-PRE-005-bad.tex"))
        assert len(violations) == 1

    def test_good_silent(self, run_rule):
        assert run_rule(jss_pre_005, _tex("JSS-PRE-005-good.tex")) == []

    def test_sentinel_flagged(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\Keywords{---!!!---at least one keyword is required---!!!---}" "\n"
            r"\begin{document}\end{document}"
        )
        violations = run_rule(jss_pre_005, src)
        assert len(violations) == 1

    def test_non_jss_class_silent(self, run_rule):
        src = r"\documentclass{article}" "\n\\begin{document}\\end{document}"
        assert run_rule(jss_pre_005, src) == []


# ---------------------------------------------------------------------------
# JSS-PRE-006 — Plain* no-markup
# ---------------------------------------------------------------------------


class TestPre006:
    def test_positive(self, run_rule):
        violations = run_rule(jss_pre_006, _tex("JSS-PRE-006-bad.tex"))
        assert len(violations) == 1
        assert violations[0].severity == Severity.WARNING

    def test_good_silent(self, run_rule):
        assert run_rule(jss_pre_006, _tex("JSS-PRE-006-good.tex")) == []

    def test_catches_plainauthor_markup(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\Plainauthor{\textbf{Achim Zeileis}}" "\n"
            r"\begin{document}\end{document}"
        )
        violations = run_rule(jss_pre_006, src)
        assert len(violations) == 1

    def test_catches_plainkeywords_markup(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\Plainkeywords{\proglang{R}}" "\n"
            r"\begin{document}\end{document}"
        )
        violations = run_rule(jss_pre_006, src)
        assert len(violations) == 1

    def test_plain_text_silent(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\Plaintitle{plain}" "\n"
            r"\Plainauthor{someone}" "\n"
            r"\Plainkeywords{a,b,c}" "\n"
            r"\begin{document}\end{document}"
        )
        assert run_rule(jss_pre_006, src) == []

    def test_accents_and_control_space_silent(self, run_rule):
        # Reviewer-confirmed FPs from cran_GMCM, cran_GPareto, cran_TPmsm,
        # cran_WeightedCluster: PDF metadata fields tolerate accent
        # commands and the control-space \ — hyperref's \pdfstringdef
        # renders them cleanly. Only formatting macros like \proglang
        # / \pkg / \textbf justify a complaint.
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\Plainauthor{Bilgrau et.\ al., Micka\"el Binois,"
            r" Artur Ara\'ujo, Lu\'{\i}s Meira-Machado}" "\n"
            r"\Plaintitle{Le manuel: cr\'{e}ation de typologies}" "\n"
            r"\Plainkeywords{Analyse de s\'{e}quences, pond\'{e}ration}" "\n"
            r"\begin{document}\end{document}"
        )
        assert run_rule(jss_pre_006, src) == []

    def test_fix_strips_markup_inside_brace_arg(self, run_rule):
        """Spec 008 follow-up: PRE-006 emits a safe in-place Fix that
        replaces ONLY the brace-arg contents with the markup-stripped
        projection. Applying the fix to the source must yield the
        plain-text projection at the same byte range."""
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\Plaintitle{Some \pkg{foo} title}" "\n"
            r"\begin{document}\end{document}"
        )
        violations = run_rule(jss_pre_006, src)
        assert len(violations) == 1
        v = violations[0]
        assert isinstance(v.fix, Fix)
        assert v.fix.confidence == "safe"
        # Replacement is markup-free.
        assert "\\" not in v.fix.replacement
        assert "{" not in v.fix.replacement
        assert "}" not in v.fix.replacement
        # The fix range covers only the inside of the braces — the byte
        # just before ``start`` is ``{`` and the byte at ``end`` is ``}``.
        assert src[v.fix.start - 1] == "{"
        assert src[v.fix.end] == "}"
        # Applying it to the brace-arg yields the projected plain text.
        applied = src[: v.fix.start] + v.fix.replacement + src[v.fix.end :]
        assert r"\pkg" not in applied
        assert "Some foo title" in applied


# ---------------------------------------------------------------------------
# JSS-PRE-007 — author markup ↔ Plainauthor
# ---------------------------------------------------------------------------


class TestPre007:
    def test_positive(self, run_rule):
        violations = run_rule(jss_pre_007, _tex("JSS-PRE-007-bad.tex"))
        assert len(violations) == 1

    def test_good_silent(self, run_rule):
        assert run_rule(jss_pre_007, _tex("JSS-PRE-007-good.tex")) == []

    def test_plain_author_no_companion_needed(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\author{Jane Doe}" "\n"
            r"\begin{document}\end{document}"
        )
        assert run_rule(jss_pre_007, src) == []


# ---------------------------------------------------------------------------
# JSS-PRE-008 — Keywords markup ↔ Plainkeywords
# ---------------------------------------------------------------------------


class TestPre008:
    def test_positive(self, run_rule):
        violations = run_rule(jss_pre_008, _tex("JSS-PRE-008-bad.tex"))
        assert len(violations) == 1

    def test_good_silent(self, run_rule):
        assert run_rule(jss_pre_008, _tex("JSS-PRE-008-good.tex")) == []

    def test_plain_keywords_no_companion_needed(self, run_rule):
        src = (
            r"\documentclass[article]{jss}" "\n"
            r"\Keywords{regression, R, count data}" "\n"
            r"\begin{document}\end{document}"
        )
        assert run_rule(jss_pre_008, src) == []


# ---------------------------------------------------------------------------
# Helper-level coverage: _first_group_arg fallback, unknown macro args,
# markup detection on math nodes.
# ---------------------------------------------------------------------------


def test_math_in_title_counts_as_markup(run_rule):
    # $x$ inside \title{} — LatexMathNode triggers markup detection.
    src = (
        r"\documentclass[article]{jss}" "\n"
        r"\title{Study of $x$}" "\n"
        r"\begin{document}\end{document}"
    )
    violations = run_rule(jss_pre_003, src)
    assert len(violations) == 1


def test_empty_tex_no_violations():
    # _class_and_options returns None when there's no documentclass.
    # Build an empty ParsedTexFile directly.
    from pathlib import Path as P
    tex = ParsedTexFile(path=P("/tmp/empty.tex"), source="", nodes=(), walker=None)
    doc = ParsedDocument(tex_files=(tex,))
    for check in (
        check_jss_pre_001, check_jss_pre_002, check_jss_pre_003,
        check_jss_pre_004, check_jss_pre_005, check_jss_pre_006,
        check_jss_pre_007, check_jss_pre_008,
    ):
        assert list(check(doc, ToolConfig())) == []


def test_first_group_arg_fallback_via_unknown_macro(parse_tex_source):
    # Build a tex where an unknown macro's arg is a sibling group.
    from texlint.journals.jss.rules.preamble import (
        _first_group_arg,
        _first_macro,
    )
    tex = parse_tex_source(r"\someunknownmacro{content}")
    triple = _first_macro(tex, "someunknownmacro")
    assert triple is not None
    macro, parent, idx = triple
    grp = _first_group_arg(macro, parent, idx)
    assert grp is not None


def test_group_plain_text_on_none():
    from texlint.journals.jss.rules.preamble import _group_plain_text
    assert _group_plain_text(None) == ""


def test_group_contains_markup_on_none():
    from texlint.journals.jss.rules.preamble import _group_contains_markup
    assert _group_contains_markup(None) is False


def test_first_group_arg_with_nodeargd_none():
    # Covers the `argd is None` branch in _first_group_arg.
    from pylatexenc.latexwalker import LatexMacroNode

    from texlint.journals.jss.rules.preamble import _first_group_arg

    class FakeMacro(LatexMacroNode):
        def __init__(self):  # type: ignore[no-untyped-def]
            pass

    fake = FakeMacro()
    assert _first_group_arg(fake, (fake,), 0) is None


def test_first_group_arg_argnlist_has_non_group(parse_tex_source):
    # Covers the `if not isinstance(arg, LatexGroupNode)` path inside the
    # argnlist loop: `\emph X` binds X as a CharsNode (not a group) — no
    # group returned, falls through to the sibling check.
    from texlint.journals.jss.rules.preamble import (
        _first_group_arg,
        _first_macro,
    )
    tex = parse_tex_source(r"\emph X")
    triple = _first_macro(tex, "emph")
    assert triple is not None
    macro, parent, idx = triple
    # No sibling group either, so the whole lookup returns None.
    assert _first_group_arg(macro, parent, idx) is None


def test_class_and_options_argd_is_none():
    # Covers the `if argd is not None:` false branch in _class_and_options.
    from pathlib import Path as P

    from pylatexenc.latexwalker import LatexMacroNode

    from texlint.api import ParsedTexFile
    from texlint.journals.jss.rules.preamble import _class_and_options

    class FakeMacro(LatexMacroNode):
        def __init__(self):  # type: ignore[no-untyped-def]
            self.macroname = "documentclass"
            self.pos = 0
            # no nodeargd set

    fake = FakeMacro()
    tex = ParsedTexFile(
        path=P("/tmp/x.tex"), source="", nodes=(fake,), walker=None
    )
    macro, class_name, options = _class_and_options(tex)
    assert class_name is None
    assert options == []


def test_class_and_options_argnlist_has_non_group(parse_tex_source):
    # Covers the `if isinstance(arg, LatexGroupNode)` false branch in
    # _class_and_options — construct a \documentclass-like shape where
    # pylatexenc might leave a non-group entry in argnlist (e.g., optional
    # arg as a CharsNode wrapped in brackets). pylatexenc's standard
    # documentclass spec always produces groups, but we exercise the
    # guard via a fabricated macro.
    from pathlib import Path as P

    from pylatexenc.latexwalker import LatexMacroNode

    from texlint.api import ParsedTexFile
    from texlint.journals.jss.rules.preamble import _class_and_options

    class FakeArgd:
        argnlist = (object(),)  # not a LatexGroupNode

    class FakeMacro(LatexMacroNode):
        def __init__(self):  # type: ignore[no-untyped-def]
            self.macroname = "documentclass"
            self.pos = 0
            self.nodeargd = FakeArgd()

    fake = FakeMacro()
    tex = ParsedTexFile(
        path=P("/tmp/x.tex"), source="", nodes=(fake,), walker=None
    )
    macro, class_name, options = _class_and_options(tex)
    assert class_name is None
    assert options == []
