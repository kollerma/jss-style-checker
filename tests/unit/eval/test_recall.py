"""Spec 017 — recall engine tests."""

from __future__ import annotations

from eval.recall import RuleRecall, compute_recall, partition_by_plants


def _v(rule_id: str, file: str = "m.tex", line: int = 1) -> dict:
    return {"rule_id": rule_id, "file": file, "line": line}


class TestPartitionByPlants:
    def test_splits_and_pools_thin_rules(self) -> None:
        per_rule = (
            RuleRecall("BIG", tp=8, fn=4, recall=8 / 12),      # 12 plants
            RuleRecall("EXACT", tp=6, fn=4, recall=0.6),        # 10 plants (boundary in)
            RuleRecall("THIN1", tp=1, fn=1, recall=0.5),        # 2 plants
            RuleRecall("THIN2", tp=0, fn=3, recall=0.0),        # 3 plants
        )
        measured, pooled = partition_by_plants(per_rule, min_plants=10)
        assert [r.rule_id for r in measured] == ["BIG", "EXACT"]
        assert pooled.rule_count == 2
        assert pooled.tp == 1 and pooled.fn == 4
        assert pooled.recall == 1 / 5
        assert pooled.rule_ids == ("THIN1", "THIN2")

    def test_empty_pool_when_all_measured(self) -> None:
        per_rule = (RuleRecall("R", tp=20, fn=0, recall=1.0),)
        measured, pooled = partition_by_plants(per_rule, min_plants=10)
        assert len(measured) == 1
        assert pooled.rule_count == 0
        assert pooled.recall is None  # tp + fn == 0 in the empty pool


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


class TestRetiredRuleExclusion:
    """Retired rule IDs (e.g. JSS-CAP-003) no longer exist in the linter,
    so their historical plants must be inert — excluded from per-rule and
    aggregate recall rather than scored as 0/N false negatives."""

    def test_retired_plants_excluded_explicit(self) -> None:
        # CAP-003 has 16 plants, all FN (the rule is gone). It must not
        # appear in per_rule nor drag the aggregate down.
        annot = [
            _v("JSS-CAP-003", line=1),
            _v("JSS-CAP-003", line=2),
            _v("LIVE", line=1),
        ]
        linter = [_v("LIVE", line=1)]
        rep = compute_recall(linter, annot, retired_rule_ids={"JSS-CAP-003"})
        assert "JSS-CAP-003" not in {r.rule_id for r in rep.per_rule}
        assert rep.aggregate_recall == 1.0  # only LIVE: 1 TP / 0 FN

    def test_retired_default_loads_from_catalogue(self) -> None:
        # With no explicit set, the retired IDs come from the JSS
        # catalogue; JSS-CAP-003 is retired there, so its plant is inert.
        annot = [_v("JSS-CAP-003", line=1), _v("LIVE", line=1)]
        rep = compute_recall([_v("LIVE", line=1)], annot)
        assert "JSS-CAP-003" not in {r.rule_id for r in rep.per_rule}

    def test_retired_filtered_from_linter_side_too(self) -> None:
        # Defensive: even a stray retired-rule linter result is ignored.
        annot = [_v("LIVE", line=1)]
        linter = [_v("LIVE", line=1), _v("JSS-REFS-002", line=5)]
        rep = compute_recall(linter, annot, retired_rule_ids={"JSS-REFS-002"})
        assert "JSS-REFS-002" not in {r.rule_id for r in rep.per_rule}

    def test_retired_excluded_through_partition(self) -> None:
        # End-to-end: a retired rule reaches neither measured nor pooled.
        annot = [_v("JSS-CAP-003", line=i) for i in range(1, 4)] + [
            _v("LIVE", line=1)
        ]
        rep = compute_recall([_v("LIVE", line=1)], annot, retired_rule_ids={"JSS-CAP-003"})
        measured, pooled = partition_by_plants(rep.per_rule, min_plants=10)
        allids = {r.rule_id for r in measured} | set(pooled.rule_ids)
        assert "JSS-CAP-003" not in allids

    def test_empty_retired_set_scores_everything(self) -> None:
        # Passing an explicit empty set disables the catalogue default.
        annot = [_v("JSS-CAP-003", line=1)]
        rep = compute_recall([], annot, retired_rule_ids=set())
        assert rep.per_rule[0].rule_id == "JSS-CAP-003"
        assert rep.aggregate_recall == 0.0
