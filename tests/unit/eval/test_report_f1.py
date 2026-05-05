"""Spec 017 — F1 column in eval-jss report tests."""

from __future__ import annotations

import io

from rich.console import Console

from eval.report import PrecisionTable, RuleRow, _f1, render_terminal


def _row(rule_id: str, tp: int, fp: int, precision: float | None) -> RuleRow:
    return RuleRow(
        rule_id=rule_id,
        category="test",
        tp=tp,
        fp=fp,
        pending=0,
        precision=precision,
        status="PASS" if precision and precision >= 0.9 else "FAIL",
    )


class TestF1:
    def test_basic(self) -> None:
        # P=R=0.5 => F1=0.5
        assert abs(_f1(0.5, 0.5) - 0.5) < 1e-9

    def test_perfect(self) -> None:
        assert _f1(1.0, 1.0) == 1.0

    def test_missing_returns_none(self) -> None:
        assert _f1(None, 0.5) is None
        assert _f1(0.5, None) is None
        assert _f1(None, None) is None

    def test_both_zero_returns_none(self) -> None:
        assert _f1(0.0, 0.0) is None


class TestRenderWithRecall:
    def _render(
        self,
        table: PrecisionTable,
        recall: dict[str, float | None] | None = None,
    ) -> str:
        buf = io.StringIO()
        console = Console(file=buf, force_terminal=False, width=200)
        render_terminal(table, console=console, recall_per_rule=recall)
        return buf.getvalue()

    def test_no_recall_no_extra_columns(self) -> None:
        t = PrecisionTable(rows=[_row("JSS-A", 9, 1, 0.9)])
        out = self._render(t, recall=None)
        # No "Recall" header in the rendered terminal output.
        assert "Recall" not in out

    def test_with_recall_adds_recall_and_f1(self) -> None:
        t = PrecisionTable(rows=[_row("JSS-A", 9, 1, 0.9)])
        out = self._render(t, recall={"JSS-A": 0.8})
        assert "Recall" in out
        assert "F1" in out
        assert "JSS-A" in out

    def test_recall_dash_for_unmeasured(self) -> None:
        t = PrecisionTable(
            rows=[_row("JSS-A", 9, 1, 0.9), _row("JSS-B", 8, 2, 0.8)]
        )
        out = self._render(t, recall={"JSS-A": 0.8})  # JSS-B has no recall
        assert "Recall" in out

    def test_aggregate_row_present_with_recall(self) -> None:
        t = PrecisionTable(rows=[_row("JSS-A", 9, 1, 0.9)])
        out = self._render(t, recall={"JSS-A": 0.8})
        assert "aggregate" in out.lower()

    def test_aggregate_row_absent_without_recall(self) -> None:
        t = PrecisionTable(rows=[_row("JSS-A", 9, 1, 0.9)])
        out = self._render(t, recall=None)
        assert "aggregate" not in out.lower()
