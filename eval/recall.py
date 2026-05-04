"""Spec 017 — recall evaluation engine.

Pure-Python computation of per-rule recall (TP / (TP + FN)) over a
linter run vs. a hand-annotated ground-truth set. The corpus itself
is hand-curated under ``eval/recall-corpus/`` (see its README).

Identity tuple: ``(rule_id, file, line)``. Column does NOT
participate (matches spec-016 semantics).
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(frozen=True)
class RuleRecall:
    rule_id: str
    tp: int
    fn: int
    recall: float | None         # None when tp + fn == 0


@dataclass(frozen=True)
class RecallReport:
    per_rule: tuple[RuleRecall, ...]
    aggregate_recall: float | None
    f1: float | None             # None unless precision is provided


def _key(item: dict) -> tuple[str, str, int]:
    return (item["rule_id"], item["file"], item["line"])


def compute_recall(
    linter_results: Iterable[dict],
    annotations: Iterable[dict],
    *,
    precision: float | None = None,
) -> RecallReport:
    """Compute per-rule + aggregate recall.

    Both inputs are iterables of dicts with at least
    ``rule_id``, ``file``, and ``line`` keys (the spec-001
    violation shape suffices).
    """
    linter_set = {_key(v) for v in linter_results}
    annot_set = {_key(v) for v in annotations}

    by_rule_tp: dict[str, int] = {}
    by_rule_fn: dict[str, int] = {}

    # Iterate annotations to build TP / FN per rule.
    for k in annot_set:
        rid = k[0]
        if k in linter_set:
            by_rule_tp[rid] = by_rule_tp.get(rid, 0) + 1
        else:
            by_rule_fn[rid] = by_rule_fn.get(rid, 0) + 1

    rules = sorted(set(by_rule_tp) | set(by_rule_fn))
    per_rule = []
    pooled_tp = 0
    pooled_fn = 0
    for rid in rules:
        tp = by_rule_tp.get(rid, 0)
        fn = by_rule_fn.get(rid, 0)
        recall = tp / (tp + fn) if (tp + fn) else None
        per_rule.append(RuleRecall(rid, tp, fn, recall))
        pooled_tp += tp
        pooled_fn += fn

    if pooled_tp + pooled_fn == 0:
        agg = None
    else:
        agg = pooled_tp / (pooled_tp + pooled_fn)

    if precision is None or agg is None or precision + agg == 0:
        f1 = None
    else:
        f1 = 2 * precision * agg / (precision + agg)

    return RecallReport(
        per_rule=tuple(per_rule),
        aggregate_recall=agg,
        f1=f1,
    )
