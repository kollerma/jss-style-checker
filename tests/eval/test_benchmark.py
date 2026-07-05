"""Tests for `eval.benchmark` gold-set loading."""

from __future__ import annotations

from pathlib import Path

from eval import benchmark, db


def _seed_gold(cx, rows: list[tuple[str, str]]) -> None:
    """Seed (rule_id, reviewer) gold rows, all true_positive."""
    cx.execute(
        "INSERT INTO runs (ts, tool_version, papers_scanned, violations_found)"
        " VALUES ('2026-07-05T00:00:00Z', '0.1.0', 1, ?)",
        (len(rows),),
    )
    run_id = cx.execute("SELECT last_insert_rowid()").fetchone()[0]
    cx.execute(
        "INSERT INTO papers (path, source, status) VALUES ('p1', 'manual', 'scanned')"
    )
    paper_id = cx.execute("SELECT last_insert_rowid()").fetchone()[0]
    for i, (rule_id, reviewer) in enumerate(rows):
        cx.execute(
            "INSERT INTO violations (paper_id, rule_id, category, line, message,"
            " severity, verdict, reviewer, first_seen_run_id)"
            " VALUES (?, ?, 'x', ?, ?, 'warning', 'true_positive', ?, ?)",
            (paper_id, rule_id, 10 + i, f"m-{i}", reviewer, run_id),
        )


def test_load_gold_excludes_deterministic_rules(tmp_db: Path) -> None:
    cx = db.connect(tmp_db)
    try:
        _seed_gold(
            cx,
            [
                ("JSS-WIDTH-001", "human:unknown"),   # deterministic → out
                ("JSS-CITE-002", "human:unknown"),    # semantic → in
            ],
        )
    finally:
        cx.close()

    gold = benchmark._load_gold(
        tmp_db, deterministic_rule_ids={"JSS-WIDTH-001"}
    )
    ids = {r["rule_id"] for r in gold}
    assert "JSS-WIDTH-001" not in ids
    assert "JSS-CITE-002" in ids


def test_load_gold_default_excludes_catalogue_deterministic(tmp_db: Path) -> None:
    cx = db.connect(tmp_db)
    try:
        _seed_gold(cx, [("JSS-WIDTH-001", "human:unknown"), ("JSS-CITE-002", "human:unknown")])
    finally:
        cx.close()
    # No explicit set → catalogue default (JSS-WIDTH-001 is deterministic).
    ids = {r["rule_id"] for r in benchmark._load_gold(tmp_db)}
    assert "JSS-WIDTH-001" not in ids
    assert "JSS-CITE-002" in ids


def test_load_gold_still_excludes_machine_labels(tmp_db: Path) -> None:
    # The existing human:auto-* / claude-proxy exclusions still hold.
    cx = db.connect(tmp_db)
    try:
        _seed_gold(
            cx,
            [
                ("JSS-CITE-002", "human:unknown"),
                ("JSS-CITE-002", "human:auto-deterministic"),
                ("JSS-CITE-002", "human:claude-proxy"),
            ],
        )
    finally:
        cx.close()
    gold = benchmark._load_gold(tmp_db, deterministic_rule_ids=set())
    assert len(gold) == 1  # only the human:unknown row survives
    assert gold[0]["reviewer"] == "human:unknown"
