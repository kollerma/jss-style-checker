"""Tests for `eval-jss iterate plan` — the loop driver decider."""

from __future__ import annotations

import json
import sqlite3
import textwrap
from pathlib import Path

import pytest
from eval.report import PrecisionTable, RuleRow

from eval import history, iterate


def _seed_eval_db(path: Path) -> None:
    cx = sqlite3.connect(path)
    cx.executescript(
        """
        CREATE TABLE runs (id INTEGER PRIMARY KEY, ts TEXT, tool_version TEXT,
                           papers_scanned INTEGER, violations_found INTEGER);
        INSERT INTO runs (ts, tool_version, papers_scanned, violations_found)
            VALUES ('2026-05-01T00:00:00Z', '0.1.0', 1, 0);
        CREATE TABLE papers (id INTEGER PRIMARY KEY, doi TEXT, title TEXT,
                             year INTEGER, path TEXT NOT NULL, source TEXT,
                             status TEXT NOT NULL);
        CREATE TABLE violations (
            id INTEGER PRIMARY KEY, paper_id INTEGER, rule_id TEXT,
            category TEXT, line INTEGER, column INTEGER, message TEXT,
            severity TEXT, verdict TEXT, verdict_reason TEXT,
            reviewer TEXT, first_seen_run_id INTEGER,
            file_suffix TEXT, file TEXT
        );
        """
    )
    cx.commit()
    cx.close()


def _seed_history(
    path: Path,
    iterations: list[dict],
) -> None:
    """Each ``iterations`` entry is ``{label, full_stats: [(rule, tp, fp, prec, status), ...]}``."""
    history.init(path)
    cx = history.connect(path)
    for it in iterations:
        cx.execute(
            "INSERT INTO iterations (ts, label, note, corpus_size, tool_version,"
            " full_parse_failures, pinned_parse_failures)"
            " VALUES ('2026-05-01T00:00:00Z', ?, NULL, 0, '0.1.0', 0, 0)",
            (it["label"],),
        )
        iter_id = cx.execute("SELECT last_insert_rowid()").fetchone()[0]
        for rule, tp, fp, prec, status in it.get("full_stats", []):
            cx.execute(
                "INSERT INTO iteration_rule_stats "
                "(iteration_id, scope, rule_id, category, tp, fp, pending, "
                " precision, status) VALUES (?, 'full', ?, 'unknown', ?, ?, 0, ?, ?)",
                (iter_id, rule, tp, fp, prec, status),
            )
    cx.close()


def _row(rule_id: str, *, tp: int, fp: int, status: str = "PASS",
         precision: float | None = None) -> RuleRow:
    if precision is None:
        precision = (tp / (tp + fp)) if (tp + fp) > 0 else 1.0
    return RuleRow(
        category="unknown", rule_id=rule_id, source="overall",
        tp=tp, fp=fp, pending=0, precision=precision, status=status,
    )


def _stub_compute_precision(rows: list[RuleRow]):
    table = PrecisionTable(rows=rows, parse_failures=0)

    def _fake(*_args, **_kwargs):
        return table
    return _fake


def _policy_path(tmp_path: Path, **overrides) -> Path:
    p = tmp_path / "policy.toml"
    base = textwrap.dedent("""
        [pass_criteria]
        precision_threshold = 0.90
        min_tp_for_pass = 10

        [fix_attempt]
        precision_drop_tolerance_pp = 3.0
        max_attempts_per_rule = 5

        [termination]
        max_consecutive_no_progress = 3
        min_progress_pp = 0.5
        max_iterations = 50

        [labeler_health]
        rebenchmark_every_n_iterations = 5
    """)
    p.write_text(base, encoding="utf-8")
    return p


def _capture_plan(monkeypatch, tmp_path, eval_rows, capsys, **kwargs):
    eval_db = tmp_path / "eval.db"
    _seed_eval_db(eval_db)
    history_db = tmp_path / "history.db"
    if "iterations" in kwargs:
        _seed_history(history_db, kwargs["iterations"])
    monkeypatch.setattr(
        "eval.iterate.report_mod.compute_precision",
        _stub_compute_precision(eval_rows),
    )
    monkeypatch.setattr(
        "eval.iterate.report_mod._pinned_pairs",
        lambda *a, **kw: set(),
    )
    code = iterate.run_plan(
        eval_db=eval_db,
        history_db=history_db,
        manifest_path=tmp_path / "manifest.csv",
        corpus_dir=tmp_path / "examples",
        policy_path=_policy_path(tmp_path),
    )
    assert code == 0
    out = capsys.readouterr().out
    return json.loads(out)


def test_plan_stop_when_all_pass(tmp_path, monkeypatch, capsys):
    rows = [_row("JSS-X-001", tp=20, fp=1, status="PASS")]
    decision = _capture_plan(monkeypatch, tmp_path, rows, capsys)
    assert decision["action"] == "stop"
    assert "All rules pass" in decision["reason"]


def test_plan_fix_rule_picks_highest_fp(tmp_path, monkeypatch, capsys):
    rows = [
        _row("JSS-X-001", tp=20, fp=1, status="PASS"),
        _row("JSS-X-002", tp=10, fp=5, status="FAIL", precision=0.67),
        _row("JSS-X-003", tp=10, fp=20, status="FAIL", precision=0.33),
        _row("JSS-X-004", tp=15, fp=2, status="FAIL", precision=0.88),
    ]
    decision = _capture_plan(monkeypatch, tmp_path, rows, capsys)
    assert decision["action"] == "fix_rule"
    assert decision["target"] == "JSS-X-003"  # 20 FPs is the most
    assert decision["fp"] == 20
    assert decision["attempts_used"] == 0
    assert decision["attempts_remaining"] == 5


def test_plan_fix_skips_rules_at_max_attempts(tmp_path, monkeypatch, capsys):
    rows = [
        _row("JSS-X-001", tp=10, fp=20, status="FAIL", precision=0.33),
        _row("JSS-X-002", tp=10, fp=5, status="FAIL", precision=0.67),
    ]
    # Precisions move enough each iteration to dodge the no-progress
    # streak (min_progress_pp=0.5pp, so deltas need to be >= 0.005).
    iterations = [
        {"label": f"post-JSS-X-001-attempt-{i}",
         "full_stats": [
             ("JSS-X-001", 10 + i, 20, 0.33 + 0.01 * i, "FAIL"),
         ]}
        for i in range(5)
    ]
    decision = _capture_plan(
        monkeypatch, tmp_path, rows, capsys, iterations=iterations,
    )
    assert decision["action"] == "fix_rule"
    assert decision["target"] == "JSS-X-002"  # JSS-X-001 capped


def test_plan_grow_corpus_when_all_failing_rules_capped(
    tmp_path, monkeypatch, capsys,
):
    rows = [
        _row("JSS-X-001", tp=10, fp=20, status="FAIL", precision=0.33),
    ]
    # Varying precisions to avoid the no-progress streak — we want to
    # exercise the "all rules capped" branch specifically.
    iterations = [
        {"label": f"post-JSS-X-001-attempt-{i}",
         "full_stats": [
             ("JSS-X-001", 10 + i, 20, 0.33 + 0.01 * i, "FAIL"),
         ]}
        for i in range(5)
    ]
    decision = _capture_plan(
        monkeypatch, tmp_path, rows, capsys, iterations=iterations,
    )
    assert decision["action"] == "grow_corpus"
    assert "max_attempts_per_rule" in decision["reason"]


def test_plan_grow_corpus_on_no_progress_streak(
    tmp_path, monkeypatch, capsys,
):
    rows = [_row("JSS-X-001", tp=10, fp=20, status="FAIL", precision=0.33)]
    # 4 iterations all at the same overall precision — streak of 3 (the
    # diff from iter1→iter2, iter2→iter3, iter3→iter4 are all 0pp).
    iterations = [
        {"label": f"iter-{i}", "full_stats": [("JSS-X-001", 100, 50, 0.6667, "FAIL")]}
        for i in range(4)
    ]
    decision = _capture_plan(
        monkeypatch, tmp_path, rows, capsys, iterations=iterations,
    )
    assert decision["action"] == "grow_corpus"
    assert "No overall-precision progress" in decision["reason"]


def test_plan_grow_corpus_when_below_min_tp(tmp_path, monkeypatch, capsys):
    """All rules pass precision but some don't have ≥min_tp TPs —
    corpus growth is the only way to fix that.
    """
    rows = [
        _row("JSS-X-001", tp=20, fp=0, status="PASS"),  # well-covered
        _row("JSS-X-002", tp=4, fp=0, status="PASS"),   # vacuous
    ]
    decision = _capture_plan(monkeypatch, tmp_path, rows, capsys)
    assert decision["action"] == "grow_corpus"
    assert "JSS-X-002" in decision["insufficient_rules"]


def test_plan_stop_when_max_iterations_reached(
    tmp_path, monkeypatch, capsys,
):
    # 50 iterations → max_iterations cap kicks in regardless of FAILs.
    rows = [_row("JSS-X-001", tp=10, fp=20, status="FAIL", precision=0.33)]
    iterations = [
        {"label": f"iter-{i}",
         "full_stats": [("JSS-X-001", 10 + i, 20, 0.33 + 0.01 * i, "FAIL")]}
        for i in range(50)
    ]
    decision = _capture_plan(
        monkeypatch, tmp_path, rows, capsys, iterations=iterations,
    )
    assert decision["action"] == "stop"
    assert "max_iterations" in decision["reason"]


def test_plan_rebenchmark_due_when_iter_multiple(
    tmp_path, monkeypatch, capsys,
):
    """At iteration 5/10/15/... the rebenchmark side-channel signal fires."""
    rows = [_row("JSS-X-001", tp=10, fp=20, status="FAIL", precision=0.33)]
    # Varying precision to avoid the no-progress trigger in this test.
    iterations = [
        {"label": f"iter-{i}",
         "full_stats": [("JSS-X-001", 10 + i, 20, 0.33 + 0.02 * i, "FAIL")]}
        for i in range(5)
    ]
    decision = _capture_plan(
        monkeypatch, tmp_path, rows, capsys, iterations=iterations,
    )
    # Primary action is still fix_rule, but rebenchmark_due is signalled.
    assert decision["action"] == "fix_rule"
    assert decision.get("rebenchmark_due") is True


def test_attempt_count_per_rule_parses_post_labels(tmp_path):
    """history.attempt_count_per_rule recognises post-JSS-XXX labels."""
    db = tmp_path / "history.db"
    _seed_history(db, [
        {"label": "iter-71-baseline", "full_stats": []},
        {"label": "post-JSS-CAP-003-months", "full_stats": []},
        {"label": "post-JSS-CAP-003-clusters", "full_stats": []},
        {"label": "post-JSS-OPER-004", "full_stats": []},
        {"label": "post-CAP-002-not-a-rule", "full_stats": []},  # missing JSS- prefix
    ])
    counts = history.attempt_count_per_rule(db)
    assert counts == {"JSS-CAP-003": 2, "JSS-OPER-004": 1}


def test_recent_overall_precision_returns_oldest_first(tmp_path):
    db = tmp_path / "history.db"
    _seed_history(db, [
        {"label": "i1", "full_stats": [("JSS-X-001", 100, 0, 1.0, "PASS")]},
        {"label": "i2", "full_stats": [("JSS-X-001", 100, 5, 0.952, "PASS")]},
        {"label": "i3", "full_stats": [("JSS-X-001", 100, 10, 0.909, "PASS")]},
    ])
    out = history.recent_overall_precision(db, n=3)
    assert [t[1] for t in out] == ["i1", "i2", "i3"]
    assert out[0][2] == pytest.approx(1.0)
    assert out[1][2] == pytest.approx(0.952, abs=0.001)
    assert out[2][2] == pytest.approx(0.909, abs=0.001)
