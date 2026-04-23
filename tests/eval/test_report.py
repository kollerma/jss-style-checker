"""Tests for `eval.report` — precision math, category grouping, thresholds.

Spec: FR-019, FR-020, FR-021 (parse-failure panel separate from precision).
"""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from eval import cli as cli_mod, db, report


def _seed(cx, rule_id: str, category: str, tp: int, fp: int, pending: int) -> None:
    cx.execute(
        "INSERT INTO runs (ts, tool_version, papers_scanned, violations_found)"
        " VALUES ('2026-04-23T00:00:00Z', '0.1.0', 1, ?)",
        (tp + fp + pending,),
    )
    run_id = cx.execute("SELECT last_insert_rowid()").fetchone()[0]
    cx.execute(
        "INSERT INTO papers (path, source, status) VALUES (?, 'manual', 'scanned')",
        (f"p_{rule_id}",),
    )
    paper_id = cx.execute("SELECT last_insert_rowid()").fetchone()[0]
    for i in range(tp):
        cx.execute(
            "INSERT INTO violations (paper_id, rule_id, category, line, message, severity,"
            " verdict, reviewer, first_seen_run_id) VALUES (?, ?, ?, ?, ?, 'warning',"
            " 'true_positive', 'human:t', ?)",
            (paper_id, rule_id, category, 100 + i, f"tp-{i}", run_id),
        )
    for i in range(fp):
        cx.execute(
            "INSERT INTO violations (paper_id, rule_id, category, line, message, severity,"
            " verdict, reviewer, first_seen_run_id) VALUES (?, ?, ?, ?, ?, 'warning',"
            " 'false_positive', 'human:t', ?)",
            (paper_id, rule_id, category, 200 + i, f"fp-{i}", run_id),
        )
    for i in range(pending):
        cx.execute(
            "INSERT INTO violations (paper_id, rule_id, category, line, message, severity,"
            " first_seen_run_id) VALUES (?, ?, ?, ?, ?, 'warning', ?)",
            (paper_id, rule_id, category, 300 + i, f"pend-{i}", run_id),
        )


def test_precision_math(tmp_db: Path) -> None:
    cx = db.connect(tmp_db)
    try:
        _seed(cx, "JSS-CITE-001", "citation", tp=9, fp=1, pending=0)
        _seed(cx, "JSS-BIB-001", "bibliography", tp=1, fp=0, pending=0)
        _seed(cx, "JSS-SRC-001", "typography", tp=5, fp=5, pending=0)
    finally:
        cx.close()

    table = report.compute_precision(tmp_db)
    by_rule = {r.rule_id: r for r in table.rows}

    assert by_rule["JSS-CITE-001"].tp == 9
    assert by_rule["JSS-CITE-001"].fp == 1
    assert by_rule["JSS-CITE-001"].precision == 0.9
    assert by_rule["JSS-CITE-001"].status == "PASS"
    assert by_rule["JSS-SRC-001"].status == "FAIL"
    assert by_rule["JSS-BIB-001"].precision == 1.0


def test_not_yet_measured_state(tmp_db: Path) -> None:
    cx = db.connect(tmp_db)
    try:
        _seed(cx, "JSS-CITE-001", "citation", tp=0, fp=0, pending=3)
    finally:
        cx.close()

    table = report.compute_precision(tmp_db)
    row = next(r for r in table.rows if r.rule_id == "JSS-CITE-001")
    assert row.status == "NOT MEASURED"
    assert row.precision is None
    assert row.pending == 3


def test_parse_failures_excluded_from_precision(tmp_db: Path) -> None:
    cx = db.connect(tmp_db)
    try:
        _seed(cx, "JSS-PARSE-000", "parse", tp=0, fp=0, pending=2)
        _seed(cx, "JSS-CITE-001", "citation", tp=10, fp=0, pending=0)
    finally:
        cx.close()

    table = report.compute_precision(tmp_db)
    rule_ids = {r.rule_id for r in table.rows}
    assert "JSS-PARSE-000" not in rule_ids
    assert table.parse_failures == 2


def test_report_cli_exit_code_reflects_threshold(tmp_db: Path) -> None:
    cx = db.connect(tmp_db)
    try:
        _seed(cx, "JSS-SRC-001", "typography", tp=1, fp=5, pending=0)
    finally:
        cx.close()

    runner = CliRunner()
    result = runner.invoke(cli_mod.cli, ["--db", str(tmp_db), "report"])
    assert result.exit_code == 1  # rule below 90% threshold


def test_report_cli_exit_code_when_all_pass(tmp_db: Path) -> None:
    cx = db.connect(tmp_db)
    try:
        _seed(cx, "JSS-CITE-001", "citation", tp=10, fp=0, pending=0)
    finally:
        cx.close()

    runner = CliRunner()
    result = runner.invoke(cli_mod.cli, ["--db", str(tmp_db), "report"])
    assert result.exit_code == 0


def test_report_cli_exit_code_no_measured_rules(tmp_db: Path) -> None:
    # No labelled data → no rule is below threshold → exit 0.
    cx = db.connect(tmp_db)
    try:
        _seed(cx, "JSS-CITE-001", "citation", tp=0, fp=0, pending=5)
    finally:
        cx.close()

    runner = CliRunner()
    result = runner.invoke(cli_mod.cli, ["--db", str(tmp_db), "report"])
    assert result.exit_code == 0
