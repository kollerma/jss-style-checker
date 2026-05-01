"""Tests for `eval-jss iterate guard` — per-rule precision regression gate."""

from __future__ import annotations

import sqlite3
import textwrap
from pathlib import Path

from eval.report import PrecisionTable, RuleRow

from eval import history, iterate


def _seed_eval_db(path: Path) -> None:
    """Minimal eval.db with a `runs` table and a `papers` row so
    `_corpus_size` / `_tool_version` don't trip up the helpers used by
    `run_guard` indirectly. The guard itself only needs the violations
    table for `compute_precision`.
    """
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
    path: Path, *, rule_id: str, scope: str, tp: int, fp: int,
    precision: float, status: str,
) -> None:
    """Drop a single (scope, rule_id) snapshot into precision-history.db."""
    history.init(path)
    cx = history.connect(path)
    cx.execute(
        "INSERT INTO iterations (ts, label, note, corpus_size, tool_version,"
        " full_parse_failures, pinned_parse_failures)"
        " VALUES ('2026-05-01T00:00:00Z', 'baseline', NULL, 0, '0.1.0', 0, 0)"
    )
    iter_id = cx.execute("SELECT last_insert_rowid()").fetchone()[0]
    cx.execute(
        "INSERT INTO iteration_rule_stats "
        "(iteration_id, scope, rule_id, category, tp, fp, pending, "
        " precision, status) VALUES (?, ?, ?, 'unknown', ?, ?, 0, ?, ?)",
        (iter_id, scope, rule_id, tp, fp, precision, status),
    )
    cx.close()


def _stub_compute_precision(table: PrecisionTable):
    """Monkeypatch `compute_precision` to return a fixed table."""
    def _fake(*_args, **_kwargs):
        return table
    return _fake


def _stub_pinned_pairs(*_args, **_kwargs):
    return set()


def _make_table(rows: list[RuleRow]) -> PrecisionTable:
    return PrecisionTable(rows=rows, parse_failures=0)


def _row(rule_id: str, tp: int, fp: int, precision: float | None,
         status: str = "PASS", source: str = "overall") -> RuleRow:
    return RuleRow(
        category="unknown", rule_id=rule_id, source=source,
        tp=tp, fp=fp, pending=0, precision=precision, status=status,
    )


def _policy_path(tmp_path: Path) -> Path:
    p = tmp_path / "policy.toml"
    p.write_text(textwrap.dedent("""
        [pass_criteria]
        precision_threshold = 0.90
        min_tp_for_pass = 10

        [fix_attempt]
        precision_drop_tolerance_pp = 3.0
    """), encoding="utf-8")
    return p


def test_no_prior_history_passes(tmp_path: Path, monkeypatch):
    eval_db = tmp_path / "eval.db"
    _seed_eval_db(eval_db)
    history_db = tmp_path / "history.db"  # doesn't exist yet
    monkeypatch.setattr(
        "eval.iterate.report_mod.compute_precision",
        _stub_compute_precision(_make_table([])),
    )
    monkeypatch.setattr(
        "eval.iterate.report_mod._pinned_pairs", _stub_pinned_pairs,
    )
    code = iterate.run_guard(
        eval_db=eval_db, history_db=history_db,
        manifest_path=tmp_path / "manifest.csv",
        corpus_dir=tmp_path / "examples",
        policy_path=_policy_path(tmp_path),
    )
    assert code == 0


def test_passing_rule_dropped_past_tolerance_blocks(tmp_path: Path, monkeypatch):
    eval_db = tmp_path / "eval.db"
    _seed_eval_db(eval_db)
    history_db = tmp_path / "history.db"
    _seed_history(
        history_db, rule_id="JSS-X-001", scope="full",
        tp=100, fp=2, precision=0.98, status="PASS",
    )
    # Current state: precision dropped 5pp (98% → 93%) — past tolerance
    monkeypatch.setattr(
        "eval.iterate.report_mod.compute_precision",
        _stub_compute_precision(_make_table([
            _row("JSS-X-001", tp=80, fp=6, precision=0.93),
        ])),
    )
    monkeypatch.setattr(
        "eval.iterate.report_mod._pinned_pairs", _stub_pinned_pairs,
    )
    code = iterate.run_guard(
        eval_db=eval_db, history_db=history_db,
        manifest_path=tmp_path / "manifest.csv",
        corpus_dir=tmp_path / "examples",
        policy_path=_policy_path(tmp_path),
    )
    assert code == 1


def test_passing_rule_dropped_within_tolerance_passes(
    tmp_path: Path, monkeypatch,
):
    eval_db = tmp_path / "eval.db"
    _seed_eval_db(eval_db)
    history_db = tmp_path / "history.db"
    _seed_history(
        history_db, rule_id="JSS-X-001", scope="full",
        tp=100, fp=2, precision=0.98, status="PASS",
    )
    monkeypatch.setattr(
        "eval.iterate.report_mod.compute_precision",
        # 2pp drop, within tolerance
        _stub_compute_precision(_make_table([
            _row("JSS-X-001", tp=98, fp=4, precision=0.96),
        ])),
    )
    monkeypatch.setattr(
        "eval.iterate.report_mod._pinned_pairs", _stub_pinned_pairs,
    )
    code = iterate.run_guard(
        eval_db=eval_db, history_db=history_db,
        manifest_path=tmp_path / "manifest.csv",
        corpus_dir=tmp_path / "examples",
        policy_path=_policy_path(tmp_path),
    )
    assert code == 0


def test_failing_rule_not_protected(tmp_path: Path, monkeypatch):
    """A rule that was already FAIL is allowed to keep failing (or get
    worse) — the guard only protects rules that WERE passing.
    """
    eval_db = tmp_path / "eval.db"
    _seed_eval_db(eval_db)
    history_db = tmp_path / "history.db"
    _seed_history(
        history_db, rule_id="JSS-X-001", scope="full",
        tp=10, fp=20, precision=0.33, status="FAIL",
    )
    monkeypatch.setattr(
        "eval.iterate.report_mod.compute_precision",
        _stub_compute_precision(_make_table([
            _row("JSS-X-001", tp=5, fp=30, precision=0.14, status="FAIL"),
        ])),
    )
    monkeypatch.setattr(
        "eval.iterate.report_mod._pinned_pairs", _stub_pinned_pairs,
    )
    code = iterate.run_guard(
        eval_db=eval_db, history_db=history_db,
        manifest_path=tmp_path / "manifest.csv",
        corpus_dir=tmp_path / "examples",
        policy_path=_policy_path(tmp_path),
    )
    assert code == 0


def test_pre_existing_low_tp_rule_not_flagged(tmp_path: Path, monkeypatch):
    """A rule that has always had TP < min_tp shouldn't trigger the guard
    just because the current state also has low TP.
    """
    eval_db = tmp_path / "eval.db"
    _seed_eval_db(eval_db)
    history_db = tmp_path / "history.db"
    _seed_history(
        history_db, rule_id="JSS-X-001", scope="full",
        tp=4, fp=0, precision=1.0, status="PASS",
    )
    monkeypatch.setattr(
        "eval.iterate.report_mod.compute_precision",
        _stub_compute_precision(_make_table([
            _row("JSS-X-001", tp=4, fp=0, precision=1.0),
        ])),
    )
    monkeypatch.setattr(
        "eval.iterate.report_mod._pinned_pairs", _stub_pinned_pairs,
    )
    code = iterate.run_guard(
        eval_db=eval_db, history_db=history_db,
        manifest_path=tmp_path / "manifest.csv",
        corpus_dir=tmp_path / "examples",
        policy_path=_policy_path(tmp_path),
    )
    assert code == 0


def test_tp_collapse_below_min_blocks(tmp_path: Path, monkeypatch):
    """A rule with TP ≥ min_tp before, < min_tp after — the change broke
    coverage, so block recording.
    """
    eval_db = tmp_path / "eval.db"
    _seed_eval_db(eval_db)
    history_db = tmp_path / "history.db"
    _seed_history(
        history_db, rule_id="JSS-X-001", scope="full",
        tp=50, fp=0, precision=1.0, status="PASS",
    )
    monkeypatch.setattr(
        "eval.iterate.report_mod.compute_precision",
        _stub_compute_precision(_make_table([
            _row("JSS-X-001", tp=5, fp=0, precision=1.0),
        ])),
    )
    monkeypatch.setattr(
        "eval.iterate.report_mod._pinned_pairs", _stub_pinned_pairs,
    )
    code = iterate.run_guard(
        eval_db=eval_db, history_db=history_db,
        manifest_path=tmp_path / "manifest.csv",
        corpus_dir=tmp_path / "examples",
        policy_path=_policy_path(tmp_path),
    )
    assert code == 1


def test_missing_eval_db_returns_two(tmp_path: Path):
    code = iterate.run_guard(
        eval_db=tmp_path / "does-not-exist.db",
        history_db=tmp_path / "history.db",
        manifest_path=tmp_path / "manifest.csv",
        corpus_dir=tmp_path / "examples",
        policy_path=_policy_path(tmp_path),
    )
    assert code == 2
