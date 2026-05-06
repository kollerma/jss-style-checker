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
CITE_003 = FIXTURES / "auto-fix" / "JSS-CITE-003"
PRE_008 = FIXTURES / "auto-fix" / "JSS-PRE-008"


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
