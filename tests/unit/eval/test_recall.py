"""Spec 017 — recall engine tests."""

from __future__ import annotations

from eval.recall import compute_recall


def _v(rule_id: str, file: str = "m.tex", line: int = 1) -> dict:
    return {"rule_id": rule_id, "file": file, "line": line}


class TestRecall:
    def test_perfect_recall(self) -> None:
        annot = [_v("R", line=1), _v("R", line=2)]
        linter = list(annot)
        rep = compute_recall(linter, annot)
        assert rep.aggregate_recall == 1.0
        assert rep.per_rule[0].tp == 2
        assert rep.per_rule[0].fn == 0
        assert rep.per_rule[0].recall == 1.0

    def test_zero_recall(self) -> None:
        annot = [_v("R", line=1), _v("R", line=2)]
        rep = compute_recall([], annot)
        assert rep.aggregate_recall == 0.0
        assert rep.per_rule[0].tp == 0
        assert rep.per_rule[0].fn == 2

    def test_partial_recall(self) -> None:
        annot = [_v("R", line=1), _v("R", line=2), _v("R", line=3)]
        linter = [_v("R", line=1), _v("R", line=3)]
        rep = compute_recall(linter, annot)
        assert rep.per_rule[0].tp == 2
        assert rep.per_rule[0].fn == 1
        assert abs(rep.aggregate_recall - 2 / 3) < 1e-9

    def test_per_rule_split(self) -> None:
        annot = [_v("R1", line=1), _v("R2", line=1)]
        linter = [_v("R1", line=1)]
        rep = compute_recall(linter, annot)
        per = {r.rule_id: r for r in rep.per_rule}
        assert per["R1"].recall == 1.0
        assert per["R2"].recall == 0.0
        assert rep.aggregate_recall == 0.5

    def test_empty_annot_aggregate_none(self) -> None:
        rep = compute_recall([], [])
        assert rep.aggregate_recall is None
        assert rep.per_rule == ()

    def test_f1_with_precision(self) -> None:
        annot = [_v("R", line=1), _v("R", line=2)]
        linter = [_v("R", line=1)]   # recall = 0.5
        rep = compute_recall(linter, annot, precision=1.0)
        # F1 = 2 * 1 * 0.5 / (1 + 0.5) = 0.6667
        assert rep.f1 is not None
        assert abs(rep.f1 - 2 / 3) < 1e-9

    def test_f1_none_without_precision(self) -> None:
        annot = [_v("R", line=1)]
        rep = compute_recall([_v("R", line=1)], annot)
        assert rep.f1 is None

    def test_extra_linter_results_dont_affect_recall(self) -> None:
        # The linter found extra violations the annotator missed.
        # That's a precision concern, not a recall concern.
        annot = [_v("R", line=1)]
        linter = [_v("R", line=1), _v("R", line=99)]
        rep = compute_recall(linter, annot)
        assert rep.per_rule[0].tp == 1
        assert rep.per_rule[0].fn == 0
        assert rep.aggregate_recall == 1.0
