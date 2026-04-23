"""Tests for `eval.human_review` — scripted Prompt.ask, verdict persistence.

Spec: FR-013, FR-014, FR-015.
"""

from __future__ import annotations

from collections import deque
from pathlib import Path

from eval import db, human_review


def _seed_violations(cx, count: int = 3) -> list[int]:
    cx.execute(
        "INSERT INTO runs (ts, tool_version, papers_scanned, violations_found)"
        " VALUES ('2026-04-23T00:00:00Z', '0.1.0', 1, ?)",
        (count,),
    )
    run_id = cx.execute("SELECT last_insert_rowid()").fetchone()[0]
    cx.execute(
        "INSERT INTO papers (path, source, status) VALUES ('p1', 'manual', 'scanned')"
    )
    paper_id = cx.execute("SELECT last_insert_rowid()").fetchone()[0]
    ids: list[int] = []
    for i in range(count):
        cx.execute(
            "INSERT INTO violations (paper_id, rule_id, category, line, column, message,"
            " severity, first_seen_run_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                paper_id,
                f"JSS-CITE-00{i + 1}",
                "citation",
                10 + i,
                None,
                f"message {i}",
                "warning",
                run_id,
            ),
        )
        ids.append(cx.execute("SELECT last_insert_rowid()").fetchone()[0])
    return ids


def _script_prompts(monkeypatch, answers: list[str]) -> list[str]:
    """Make `rich.prompt.Prompt.ask` return answers from `answers` in order.

    Returns the list itself so tests can check consumption.
    """
    queue = deque(answers)

    def _fake_ask(*args, **kwargs):
        if not queue:
            return "q"
        return queue.popleft()

    monkeypatch.setattr(human_review.Prompt, "ask", staticmethod(_fake_ask))
    return list(queue)


def test_human_review_maps_tfu_verdicts(monkeypatch, tmp_db: Path) -> None:
    cx = db.connect(tmp_db)
    try:
        _seed_violations(cx, count=3)
    finally:
        cx.close()

    _script_prompts(monkeypatch, ["t", "", "f", "because", "u", "", "q"])

    code = human_review.run(db_path=tmp_db, limit=None, rule_id=None, reviewer="human:tester")
    assert code == 0

    cx = db.connect(tmp_db)
    try:
        rows = cx.execute(
            "SELECT rule_id, verdict, verdict_reason, reviewer FROM violations ORDER BY rule_id"
        ).fetchall()
        assert [r["verdict"] for r in rows] == ["true_positive", "false_positive", "uncertain"]
        assert rows[1]["verdict_reason"] == "because"
        assert all(r["reviewer"] == "human:tester" for r in rows)
    finally:
        cx.close()


def test_human_review_skip_leaves_row_unchanged(monkeypatch, tmp_db: Path) -> None:
    cx = db.connect(tmp_db)
    try:
        _seed_violations(cx, count=1)
    finally:
        cx.close()

    _script_prompts(monkeypatch, ["s", "q"])

    human_review.run(db_path=tmp_db, limit=None, rule_id=None, reviewer="human:tester")

    cx = db.connect(tmp_db)
    try:
        row = cx.execute("SELECT verdict, reviewer FROM violations").fetchone()
        assert row["verdict"] is None
        assert row["reviewer"] is None
    finally:
        cx.close()


def test_human_review_quit_stops_loop(monkeypatch, tmp_db: Path) -> None:
    cx = db.connect(tmp_db)
    try:
        _seed_violations(cx, count=3)
    finally:
        cx.close()

    _script_prompts(monkeypatch, ["t", "", "q"])

    human_review.run(db_path=tmp_db, limit=None, rule_id=None, reviewer="human:tester")

    cx = db.connect(tmp_db)
    try:
        labelled = cx.execute(
            "SELECT COUNT(*) FROM violations WHERE verdict IS NOT NULL"
        ).fetchone()[0]
        assert labelled == 1
    finally:
        cx.close()


def test_human_review_limit_respected(monkeypatch, tmp_db: Path) -> None:
    cx = db.connect(tmp_db)
    try:
        _seed_violations(cx, count=5)
    finally:
        cx.close()

    _script_prompts(monkeypatch, ["t", "", "t", "", "q"])

    human_review.run(db_path=tmp_db, limit=2, rule_id=None, reviewer="human:tester")

    cx = db.connect(tmp_db)
    try:
        labelled = cx.execute(
            "SELECT COUNT(*) FROM violations WHERE verdict IS NOT NULL"
        ).fetchone()[0]
        assert labelled == 2
    finally:
        cx.close()


def test_human_review_rule_filter(monkeypatch, tmp_db: Path) -> None:
    cx = db.connect(tmp_db)
    try:
        _seed_violations(cx, count=3)
    finally:
        cx.close()

    _script_prompts(monkeypatch, ["t", "", "q"])

    human_review.run(
        db_path=tmp_db, limit=None, rule_id="JSS-CITE-002", reviewer="human:tester"
    )

    cx = db.connect(tmp_db)
    try:
        row = cx.execute(
            "SELECT verdict FROM violations WHERE rule_id='JSS-CITE-002'"
        ).fetchone()
        assert row["verdict"] == "true_positive"
        # Other rules untouched
        others = cx.execute(
            "SELECT COUNT(*) FROM violations WHERE verdict IS NOT NULL"
        ).fetchone()[0]
        assert others == 1
    finally:
        cx.close()


def test_human_review_reviewer_defaults_to_env(monkeypatch, tmp_db: Path) -> None:
    cx = db.connect(tmp_db)
    try:
        _seed_violations(cx, count=1)
    finally:
        cx.close()

    monkeypatch.setenv("USER", "envuser")
    _script_prompts(monkeypatch, ["f", "", "q"])

    human_review.run(db_path=tmp_db, limit=None, rule_id=None, reviewer=None)

    cx = db.connect(tmp_db)
    try:
        row = cx.execute("SELECT reviewer FROM violations").fetchone()
        assert row["reviewer"] == "human:envuser"
    finally:
        cx.close()
