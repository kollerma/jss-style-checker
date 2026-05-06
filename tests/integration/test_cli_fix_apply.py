"""Integration tests for spec-008 ``--fix --apply`` and the
regression-rollback path, exercised end-to-end through the Click
CLI runner.

Two follow-ups from ``roadmap/follow-ups.md`` (Feature 008) close
here:

1. ``Integration test for --apply interactive prompt`` —
   :class:`TestApplyInteractive` scripts ``y\\n`` and ``n\\n`` over
   stdin against the JSS-CITE-003 ``before.tex`` fixture and
   asserts the file matches ``after.tex`` (or stays byte-identical
   on decline).

2. ``Regression-rollback CLI integration test`` —
   :class:`TestRegressionRollback` registers a synthetic
   ``regression`` journal whose only rule emits a Fix that re-trips
   itself on rewrite, then drives ``jss-lint --journal regression
   --fix <file>`` and asserts:
     * exit code 2 (rejected fixes)
     * the file is byte-identical to its pre-fix bytes
     * stderr names the rule id and mentions ``rolled back``.
"""

from __future__ import annotations

import importlib.metadata as _im
import shutil
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from click.testing import CliRunner

from texlint.api import (
    Fix,
    JournalRuleModule,
    ParsedDocument,
    Rule,
    RuleCategory,
    Severity,
    ToolConfig,
    Violation,
)
from texlint.cli import main

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
ABBR_001 = FIXTURES / "auto-fix" / "JSS-ABBR-001"
CITE_003 = FIXTURES / "auto-fix" / "JSS-CITE-003"
HOUSE_003 = FIXTURES / "auto-fix" / "JSS-HOUSE-003"
MARKUP_001 = FIXTURES / "auto-fix" / "JSS-MARKUP-001"
MARKUP_002 = FIXTURES / "auto-fix" / "JSS-MARKUP-002"
MARKUP_004 = FIXTURES / "auto-fix" / "JSS-MARKUP-004"
NAME_002 = FIXTURES / "auto-fix" / "JSS-NAME-002"
PRE_003 = FIXTURES / "auto-fix" / "JSS-PRE-003"
PRE_007 = FIXTURES / "auto-fix" / "JSS-PRE-007"
PRE_008 = FIXTURES / "auto-fix" / "JSS-PRE-008"
STRUCT_005 = FIXTURES / "auto-fix" / "JSS-STRUCT-005"
STRUCT_006 = FIXTURES / "auto-fix" / "JSS-STRUCT-006"
TYPO_001 = FIXTURES / "auto-fix" / "JSS-TYPO-001"
XREF_002 = FIXTURES / "auto-fix" / "JSS-XREF-002"


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


# ---------------------------------------------------------------------------
# 1. --apply interactive
# ---------------------------------------------------------------------------


class TestApplyInteractive:
    """End-to-end test of the ``[y/n/a/q]`` interactive prompt.

    The JSS-CITE-003 fixture has exactly one violation (a single
    ``(\\cite{...})`` form). With one fix, ``y`` and ``a`` both
    accept; ``n`` and ``q`` both leave the file untouched. We
    exercise ``y`` (accept the only fix) and ``n`` (decline).
    """

    def test_y_applies_fix(self, tmp_path: Path, runner: CliRunner) -> None:
        target = tmp_path / "manuscript.tex"
        shutil.copyfile(CITE_003 / "before.tex", target)

        result = runner.invoke(main, ["--fix", "--apply", str(target)], input="y\n")

        # The CLI exits with the report's exit code (1, because the
        # in-memory report still carries the JSS-CITE-003 violation
        # — the report is computed before the fixer rewrites the
        # file). The point of the assertion is the rewrite, not the
        # exit status: see the byte-equality check below.
        assert result.exit_code == 1, result.output
        # File now matches the after fixture, byte-for-byte.
        expected = (CITE_003 / "after.tex").read_bytes()
        assert target.read_bytes() == expected
        # Prompt rendered.
        assert "Apply fix for JSS-CITE-003" in result.output

    def test_n_declines(self, tmp_path: Path, runner: CliRunner) -> None:
        target = tmp_path / "manuscript.tex"
        shutil.copyfile(CITE_003 / "before.tex", target)
        before_bytes = target.read_bytes()

        result = runner.invoke(main, ["--fix", "--apply", str(target)], input="n\n")

        assert result.exit_code == 1, result.output
        # File untouched.
        assert target.read_bytes() == before_bytes
        # Prompt rendered, but the file did not gain ``\citep{``.
        assert "Apply fix for JSS-CITE-003" in result.output

    def test_y_applies_jss_name_002_bib_fix(
        self, tmp_path: Path, runner: CliRunner,
    ) -> None:
        """Spec 008 follow-up: ``--apply`` rewrites the BibTeX
        ``publisher = {Springer}`` literal to ``Springer-Verlag``,
        leaving the surrounding ``{}`` intact."""
        target = tmp_path / "refs.bib"
        shutil.copyfile(NAME_002 / "before.bib", target)

        result = runner.invoke(
            main, ["--fix", "--apply", str(target)], input="y\n",
        )

        # Exit 1: the in-memory report still carries the violation
        # (computed before the fixer rewrites). The byte-equality
        # check below proves the rewrite landed.
        assert result.exit_code == 1, result.output
        expected = (NAME_002 / "after.bib").read_bytes()
        assert target.read_bytes() == expected
        assert "Apply fix for JSS-NAME-002" in result.output


class TestMarkup002Fix:
    """End-to-end test of the JSS-MARKUP-002 \\pkg{} fix applied
    through ``jss-lint --fix`` on the canonical fixture."""

    def test_fix_wraps_bare_package_in_pkg(
        self, tmp_path: Path, runner: CliRunner
    ) -> None:
        target = tmp_path / "manuscript.tex"
        shutil.copyfile(MARKUP_002 / "before.tex", target)

        result = runner.invoke(main, ["--fix", str(target)])

        # Exit 1: the report is computed BEFORE the fixer rewrites
        # (see TestApplyInteractive::test_y_applies_fix above for the
        # precedent); the byte-equality assertion is the load-bearing
        # check that the rewrite happened.
        assert result.exit_code == 1, result.output
        expected = (MARKUP_002 / "after.tex").read_bytes()
        assert target.read_bytes() == expected


# ---------------------------------------------------------------------------
# 1b. JSS-MARKUP-001 end-to-end --fix
# ---------------------------------------------------------------------------


class TestMarkup001Fix:
    """``jss-lint --fix`` against the JSS-MARKUP-001 before fixture
    rewrites the file in place to match the after fixture.

    The before fixture has exactly one ``Python`` mention that the rule
    flags; the fix wraps it in ``\\proglang{Python}``.
    """

    def test_fix_rewrites_to_after_fixture(
        self, tmp_path: Path, runner: CliRunner
    ) -> None:
        target = tmp_path / "manuscript.tex"
        shutil.copyfile(MARKUP_001 / "before.tex", target)

        result = runner.invoke(main, ["--fix", str(target)])

        # Exit 1: in-memory report still carries the violation. The
        # rewrite happens after the report is built.
        assert result.exit_code == 1, result.output
        expected = (MARKUP_001 / "after.tex").read_bytes()
        assert target.read_bytes() == expected


# ---------------------------------------------------------------------------
# 1c. JSS-TYPO-001 end-to-end --fix
# ---------------------------------------------------------------------------


class TestTypo001Fix:
    """``jss-lint --fix`` against the JSS-TYPO-001 before fixture
    rewrites the file in place to match the after fixture by
    appending ``.`` to a figure caption that lacks a trailing
    period."""

    def test_fix_appends_period_to_caption(
        self, tmp_path: Path, runner: CliRunner
    ) -> None:
        target = tmp_path / "manuscript.tex"
        shutil.copyfile(TYPO_001 / "before.tex", target)

        result = runner.invoke(main, ["--fix", str(target)])

        # Exit 1: in-memory report still carries the violation. The
        # rewrite happens after the report is built.
        assert result.exit_code == 1, result.output
        expected = (TYPO_001 / "after.tex").read_bytes()
        assert target.read_bytes() == expected


# ---------------------------------------------------------------------------
# 1d. JSS-STRUCT-005 end-to-end --fix
# ---------------------------------------------------------------------------


class TestStruct005Fix:
    """``jss-lint --fix`` against the JSS-STRUCT-005 before fixture
    rewrites the file in place to match the after fixture.

    The before fixture has exactly one lowercase ``\\and`` separator
    inside ``\\author{}``; the fix swaps it for the JSS-canonical
    ``\\And``.
    """

    def test_fix_rewrites_to_after_fixture(
        self, tmp_path: Path, runner: CliRunner
    ) -> None:
        target = tmp_path / "manuscript.tex"
        shutil.copyfile(STRUCT_005 / "before.tex", target)

        result = runner.invoke(main, ["--fix", str(target)])

        assert result.exit_code == 1, result.output
        expected = (STRUCT_005 / "after.tex").read_bytes()
        assert target.read_bytes() == expected


# ---------------------------------------------------------------------------
# 1b. JSS-STRUCT-006 --fix end-to-end
# ---------------------------------------------------------------------------


class TestStruct006Fix:
    """End-to-end test that ``jss-lint --fix`` rewrites a STRUCT-006
    violation by inserting ``\\newpage`` between ``\\bibliography{}``
    and ``\\begin{appendix}``.
    """

    def test_fix_inserts_newpage(self, tmp_path: Path, runner: CliRunner) -> None:
        target = tmp_path / "manuscript.tex"
        shutil.copyfile(STRUCT_006 / "before.tex", target)

        result = runner.invoke(main, ["--fix", str(target)])

        # Exit 1: the in-memory compliance report still carries the
        # JSS-STRUCT-006 violation (it's computed before the fixer
        # rewrites the file). The contract under test is the rewrite
        # itself — see the byte-equality check below.
        assert result.exit_code == 1, result.output
        # File now matches the after fixture, byte-for-byte.
        expected = (STRUCT_006 / "after.tex").read_bytes()
        assert target.read_bytes() == expected


# ---------------------------------------------------------------------------
# 1b. JSS-PRE-003 — \title{} markup ⇒ insert \Plaintitle{}
# ---------------------------------------------------------------------------


class TestPre003Fix:
    """End-to-end ``--fix`` test for JSS-PRE-003.

    The fixture pair ``before.tex`` / ``after.tex`` differs only by
    a single inserted ``\\Plaintitle{...}`` line — exactly what the
    rule's spec-008 ``Fix`` payload should produce when ``--fix`` is
    invoked.
    """

    def test_fix_writes_plaintitle(
        self, tmp_path: Path, runner: CliRunner
    ) -> None:
        target = tmp_path / "manuscript.tex"
        shutil.copyfile(PRE_003 / "before.tex", target)

        result = runner.invoke(main, ["--fix", str(target)])

        # Report still carries the original violation — exit 1 is the
        # expected rendering of "violations seen". The point is the
        # rewrite, asserted byte-for-byte.
        assert result.exit_code == 1, result.output
        expected = (PRE_003 / "after.tex").read_bytes()
        assert target.read_bytes() == expected


# ---------------------------------------------------------------------------
# 1b. JSS-PRE-007 Plainauthor insertion
# ---------------------------------------------------------------------------


class TestPre007Fix:
    """End-to-end ``jss-lint --fix`` rewrite for JSS-PRE-007.

    The fixture's ``\\author{}`` carries markup (``\\pkg{}``) and
    ``\\Plainauthor{}`` is missing. The fixer should insert
    ``\\Plainauthor{<projected plain text>}`` immediately after
    ``\\author{...}`` and the file should match ``after.tex``
    byte-for-byte.
    """

    def test_fix_inserts_plainauthor(
        self, tmp_path: Path, runner: CliRunner
    ) -> None:
        target = tmp_path / "manuscript.tex"
        shutil.copyfile(PRE_007 / "before.tex", target)

        result = runner.invoke(main, ["--fix", str(target)])

        # Exit 1 because the in-memory report still carries the
        # JSS-PRE-007 violation (computed pre-rewrite); the rewrite
        # itself succeeds and the byte-equality check below proves it.
        assert result.exit_code == 1, result.output
        expected = (PRE_007 / "after.tex").read_bytes()
        assert target.read_bytes() == expected


# ---------------------------------------------------------------------------
# JSS-PRE-008 — \Keywords markup → insert \Plainkeywords{}
# ---------------------------------------------------------------------------


class TestPre008Fix:
    """End-to-end ``jss-lint --fix`` for JSS-PRE-008.

    The before fixture has ``\\Keywords{JSS, style guide, \\proglang{R}}``
    with no companion ``\\Plainkeywords{}``; the rule's safe Fix
    inserts ``\\Plainkeywords{JSS, style guide, R}`` (markup dropped,
    macro brace-args projected) immediately after the ``\\Keywords``
    closing brace.
    """

    def test_fix_writes_plainkeywords_after_keywords(
        self, tmp_path: Path, runner: CliRunner
    ) -> None:
        target = tmp_path / "manuscript.tex"
        shutil.copyfile(PRE_008 / "before.tex", target)

        result = runner.invoke(main, ["--fix", str(target)])

        # Exit code is from the report (PRE-008 violation present
        # in the report computed before the rewrite).
        assert result.exit_code == 1, result.output
        expected = (PRE_008 / "after.tex").read_bytes()
        assert target.read_bytes() == expected


# ---------------------------------------------------------------------------
# 1b. JSS-ABBR-001 --fix end-to-end byte equality
# ---------------------------------------------------------------------------


class TestAbbr001Fix:
    """End-to-end ``--fix`` for JSS-ABBR-001.

    Drives the CLI in non-interactive write mode against the
    ``before.tex`` fixture and asserts the rewritten file is
    byte-identical to ``after.tex``.
    """

    def test_fix_rewrites_to_after(
        self, tmp_path: Path, runner: CliRunner
    ) -> None:
        target = tmp_path / "manuscript.tex"
        shutil.copyfile(ABBR_001 / "before.tex", target)

        result = runner.invoke(main, ["--fix", str(target)])

        # The in-memory report carries the violation (computed before
        # the rewrite), so exit_code is 1 — the post-fix byte equality
        # below is the load-bearing assertion.
        assert result.exit_code == 1, result.output
        expected = (ABBR_001 / "after.tex").read_bytes()
        assert target.read_bytes() == expected


# ---------------------------------------------------------------------------
# 1b. JSS-XREF-002 end-to-end --fix
# ---------------------------------------------------------------------------


class TestXref002Fix:
    """End-to-end ``jss-lint --fix`` over the JSS-XREF-002 fixture.

    The before fixture has a single ``(\\ref{eq:mean})`` violation.
    Running ``--fix`` (no ``--apply``, so the fixer applies all safe
    fixes non-interactively) must rewrite the file byte-for-byte to
    the after fixture.
    """

    def test_fix_rewrites_file(
        self, tmp_path: Path, runner: CliRunner
    ) -> None:
        target = tmp_path / "manuscript.tex"
        shutil.copyfile(XREF_002 / "before.tex", target)

        result = runner.invoke(main, ["--fix", str(target)])

        # The CLI exits with the report's exit code (1 — the in-memory
        # report carries the JSS-XREF-002 violation, computed before
        # the fixer rewrote the file). The point of this test is the
        # post-rewrite byte-equality below.
        assert result.exit_code == 1, result.output
        expected = (XREF_002 / "after.tex").read_bytes()
        assert target.read_bytes() == expected


class TestMarkup004Fix:
    """End-to-end test of the JSS-MARKUP-004 auto-fix.

    The fixture has a single ``\\section{Some \\pkg{foo} title}``
    without the required plain-text optional arg. ``jss-lint --fix``
    should rewrite the file to match ``after.tex`` byte-for-byte.
    """

    def test_fix_inserts_plain_text_optional_arg(
        self, tmp_path: Path, runner: CliRunner
    ) -> None:
        target = tmp_path / "manuscript.tex"
        shutil.copyfile(MARKUP_004 / "before.tex", target)

        result = runner.invoke(main, ["--fix", str(target)])

        # The CLI exits with the report's exit code; the in-memory
        # report still carries the JSS-MARKUP-004 violation since the
        # report is computed before the fixer rewrites the file. The
        # point of the assertion is the rewrite, not the exit status.
        assert result.exit_code == 1, result.output
        expected = (MARKUP_004 / "after.tex").read_bytes()
        assert target.read_bytes() == expected


# ---------------------------------------------------------------------------
# 2. Regression-rollback CLI integration test
# ---------------------------------------------------------------------------


_REGRESSION_RULE_ID = "REG-001"
_BAD_TOKEN = "BAD"


def _check_regression(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    """Fire on every literal ``BAD`` substring in the source.

    The emitted ``Fix`` replaces ``BAD`` with itself — applied, the
    rule re-fires at the same line, which trips the engine's
    re-validation guard and forces a rollback (Constitution §VII /
    spec 008 data-model §6).
    """
    for tex in doc.all_tex_like():
        text: str = tex.source
        idx = 0
        while True:
            hit = text.find(_BAD_TOKEN, idx)
            if hit == -1:
                break
            line = text.count("\n", 0, hit) + 1
            col = hit - (text.rfind("\n", 0, hit) + 1) + 1
            yield Violation(
                file=tex.path,
                line=line,
                column=col,
                rule_id=_REGRESSION_RULE_ID,
                severity=Severity.WARNING,
                message="regression-test rule fires on BAD token",
                suggestion="(test fixture) replace BAD with BAD",
                fix=Fix(
                    start=hit,
                    end=hit + len(_BAD_TOKEN),
                    replacement=_BAD_TOKEN,  # same text => re-trips
                    description="(test fixture) no-op replacement",
                    confidence="safe",
                ),
            )
            idx = hit + len(_BAD_TOKEN)


_REGRESSION_RULE = Rule(
    id=_REGRESSION_RULE_ID,
    category="regression-test",
    severity=Severity.WARNING,
    message_template="regression-test rule fires on BAD token",
    authority="(test fixture)",
    check=_check_regression,
    formats=frozenset({"tex"}),
)

_REGRESSION_CATEGORY = RuleCategory(
    id="regression-test",
    title="Regression test",
    rules=(_REGRESSION_RULE,),
)


class _RegressionJournal(JournalRuleModule):
    id = "regression"

    def categories(self) -> tuple[RuleCategory, ...]:
        return (_REGRESSION_CATEGORY,)


class _FakeEP:
    """Minimal duck-type for ``importlib.metadata.EntryPoint``.

    The engine's :func:`load_journal` only ever calls ``.name``,
    ``.value`` (debug only), and ``.load()``.
    """

    def __init__(self, name: str, target: Any) -> None:
        self.name = name
        self.value = f"<test:{name}>"
        self._target = target

    def load(self) -> Any:
        return self._target


class _FakeEPs(list):
    """Mimics ``importlib.metadata.EntryPoints`` selectable API."""

    def select(self, *, name: str) -> list[_FakeEP]:
        return [ep for ep in self if ep.name == name]


@pytest.fixture
def regression_journal(monkeypatch: pytest.MonkeyPatch) -> None:
    """Register the ``regression`` journal under the
    ``texlint.journals`` entry-point group for the duration of one
    test. The CLI's ``load_journal`` and the fixer's
    ``_re_validate`` both go through ``importlib.metadata.entry_points``,
    so a single monkeypatch covers both call sites.
    """
    real_entry_points = _im.entry_points
    fake = _FakeEPs([_FakeEP("regression", _RegressionJournal)])

    def _patched(*args: Any, **kwargs: Any) -> Any:
        group = kwargs.get("group") if kwargs else (args[0] if args else None)
        if group == "texlint.journals":
            return fake
        return real_entry_points(*args, **kwargs)

    monkeypatch.setattr(_im, "entry_points", _patched)


class TestRegressionRollback:
    """A Fix that re-trips its own rule must roll the file back to
    its pre-fix bytes and exit 2 (FixReport.rejected non-empty).
    """

    def test_regression_fix_rolls_back_and_exits_two(
        self,
        tmp_path: Path,
        runner: CliRunner,
        regression_journal: None,
    ) -> None:
        target = tmp_path / "manuscript.tex"
        original = "Some BAD content here.\n"
        target.write_text(original, encoding="utf-8")
        # The fixer's ``_re_validate`` reloads ``ToolConfig`` from
        # ``target.parent`` (it does not see the CLI's ``--journal``
        # flag). Persist the journal id in a sibling ``.jss-lint.toml``
        # so the re-lint pass loads our synthetic journal and the
        # rule actually re-fires; without this, the engine reloads the
        # default ``jss`` journal which has no ``REG-001`` rule and the
        # rollback never triggers.
        (tmp_path / ".jss-lint.toml").write_text(
            'journal = "regression"\n', encoding="utf-8"
        )

        before_bytes = target.read_bytes()
        result = runner.invoke(
            main,
            ["--journal", "regression", "--fix", str(target)],
        )

        # Exit 2: at least one rejected fix.
        assert result.exit_code == 2, (
            f"expected exit 2, got {result.exit_code}; output:\n{result.output}"
        )
        # File byte-identical to the pre-fix snapshot.
        assert target.read_bytes() == before_bytes
        # stderr / output names the rule id and the rollback.
        assert _REGRESSION_RULE_ID in result.output
        assert "rolled back" in result.output


# ---------------------------------------------------------------------------
# 3. JSS-HOUSE-003 — delete redundant \usepackage line
# ---------------------------------------------------------------------------


class TestHouse003Fix:
    """End-to-end check that ``jss-lint --fix`` removes a redundant
    ``\\usepackage{graphicx}`` line in its entirety. The resulting
    file must be byte-identical to ``after.tex``.
    """

    def test_fix_deletes_redundant_usepackage_line(
        self, tmp_path: Path, runner: CliRunner
    ) -> None:
        target = tmp_path / "manuscript.tex"
        shutil.copyfile(HOUSE_003 / "before.tex", target)

        result = runner.invoke(main, ["--fix", str(target)])

        # The remaining manuscript still triggers other JSS-* rules
        # (no real abstract / keywords text, etc.) so we don't pin the
        # exit code; the load-bearing assertion is the byte equality.
        assert result.exit_code in (0, 1), result.output
        expected = (HOUSE_003 / "after.tex").read_bytes()
        assert target.read_bytes() == expected
