"""Tests for `eval.report` — precision math, category grouping, thresholds.

Spec: FR-019, FR-020, FR-021 (parse-failure panel separate from precision).
"""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from eval import cli as cli_mod
from eval import db, report


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


# ---------------------------------------------------------------------------
# US4: CSV precision history
# ---------------------------------------------------------------------------


def test_csv_append_writes_header_once(tmp_db: Path, tmp_path: Path) -> None:
    cx = db.connect(tmp_db)
    try:
        _seed(cx, "JSS-CITE-001", "citation", tp=9, fp=1, pending=0)
    finally:
        cx.close()

    csv_path = tmp_path / "report.csv"
    runner = CliRunner()

    r1 = runner.invoke(cli_mod.cli, ["--db", str(tmp_db), "report", "--csv", str(csv_path)])
    assert r1.exit_code == 0, r1.output
    first_contents = csv_path.read_text(encoding="utf-8").splitlines()
    assert first_contents[0].startswith("ts,tool_version,rule_id,category,tp,fp")
    assert len(first_contents) == 2  # header + 1 rule row

    r2 = runner.invoke(cli_mod.cli, ["--db", str(tmp_db), "report", "--csv", str(csv_path)])
    assert r2.exit_code == 0, r2.output
    second_contents = csv_path.read_text(encoding="utf-8").splitlines()
    # Header preserved, not re-written; one new row appended.
    assert second_contents[0] == first_contents[0]
    assert len(second_contents) == 3


def test_csv_dash_disables_append(tmp_db: Path, tmp_path: Path) -> None:
    cx = db.connect(tmp_db)
    try:
        _seed(cx, "JSS-CITE-001", "citation", tp=9, fp=1, pending=0)
    finally:
        cx.close()

    csv_path = tmp_path / "never.csv"
    runner = CliRunner()
    r = runner.invoke(cli_mod.cli, ["--db", str(tmp_db), "report", "--csv", "-"])
    assert r.exit_code == 0, r.output
    assert not csv_path.exists()


def test_csv_rows_carry_below_threshold_flag(tmp_db: Path, tmp_path: Path) -> None:
    cx = db.connect(tmp_db)
    try:
        _seed(cx, "JSS-CITE-001", "citation", tp=9, fp=1, pending=0)   # 90% PASS
        _seed(cx, "JSS-SRC-001", "typography", tp=1, fp=5, pending=0)  # FAIL
        _seed(cx, "JSS-BIB-001", "bibliography", tp=0, fp=0, pending=3)  # NOT MEASURED
    finally:
        cx.close()

    csv_path = tmp_path / "trend.csv"
    runner = CliRunner()
    r = runner.invoke(cli_mod.cli, ["--db", str(tmp_db), "report", "--csv", str(csv_path)])
    assert r.exit_code == 1, r.output

    import csv as _csv
    with csv_path.open(encoding="utf-8") as f:
        rows = list(_csv.DictReader(f))
    by_rule = {r["rule_id"]: r for r in rows}
    assert by_rule["JSS-CITE-001"]["below_threshold"] == "0"
    assert by_rule["JSS-SRC-001"]["below_threshold"] == "1"
    # NOT MEASURED rule: empty precision, below_threshold=0.
    assert by_rule["JSS-BIB-001"]["precision"] == ""
    assert by_rule["JSS-BIB-001"]["below_threshold"] == "0"
    # All rows from one invocation share a single ts.
    assert len({r["ts"] for r in rows}) == 1


# ---------------------------------------------------------------------------
# US5: Per-source precision breakdown
# ---------------------------------------------------------------------------


def _seed_with_source(
    cx, rule_id: str, category: str, source: str, tp: int, fp: int
) -> None:
    """Seed violations belonging to a paper with the given `source` value."""
    cx.execute(
        "INSERT INTO runs (ts, tool_version, papers_scanned, violations_found)"
        " VALUES ('2026-04-23T00:00:00Z', '0.1.0', 1, ?)",
        (tp + fp,),
    )
    run_id = cx.execute("SELECT last_insert_rowid()").fetchone()[0]
    cx.execute(
        "INSERT INTO papers (path, source, status) VALUES (?, ?, 'scanned')",
        (f"p_{rule_id}_{source}", source),
    )
    paper_id = cx.execute("SELECT last_insert_rowid()").fetchone()[0]
    for i in range(tp):
        cx.execute(
            "INSERT INTO violations (paper_id, rule_id, category, line, message, severity,"
            " verdict, reviewer, first_seen_run_id) VALUES (?, ?, ?, ?, ?, 'warning',"
            " 'true_positive', 'human:t', ?)",
            (paper_id, rule_id, category, 100 + i, f"{source}-tp-{i}", run_id),
        )
    for i in range(fp):
        cx.execute(
            "INSERT INTO violations (paper_id, rule_id, category, line, message, severity,"
            " verdict, reviewer, first_seen_run_id) VALUES (?, ?, ?, ?, ?, 'warning',"
            " 'false_positive', 'human:t', ?)",
            (paper_id, rule_id, category, 200 + i, f"{source}-fp-{i}", run_id),
        )


def test_by_source_csv_emits_overall_plus_per_source(
    tmp_db: Path, tmp_path: Path
) -> None:
    cx = db.connect(tmp_db)
    try:
        # JSS-CITE-001 fires on CRAN (all TP) and arXiv (all FP)
        _seed_with_source(cx, "JSS-CITE-001", "citation", "cran", tp=10, fp=0)
        _seed_with_source(cx, "JSS-CITE-001", "citation", "arxiv", tp=2, fp=8)
    finally:
        cx.close()

    csv_path = tmp_path / "by_source.csv"
    runner = CliRunner()
    r = runner.invoke(
        cli_mod.cli,
        ["--db", str(tmp_db), "report", "--by-source", "--csv", str(csv_path)],
    )
    # Overall JSS-CITE-001: 12 TP / 20 total = 60% → FAIL → exit 1
    assert r.exit_code == 1, r.output

    import csv as _csv
    with csv_path.open(encoding="utf-8") as f:
        rows = list(_csv.DictReader(f))

    sources = {r["source"] for r in rows if r["rule_id"] == "JSS-CITE-001"}
    assert sources == {"overall", "cran", "arxiv"}

    per = {(r["rule_id"], r["source"]): r for r in rows}
    assert per[("JSS-CITE-001", "cran")]["precision"] == "1.0000"
    assert per[("JSS-CITE-001", "arxiv")]["precision"] == "0.2000"
    assert per[("JSS-CITE-001", "cran")]["below_threshold"] == "0"
    assert per[("JSS-CITE-001", "arxiv")]["below_threshold"] == "1"


def test_by_source_skips_sources_without_data(tmp_db: Path) -> None:
    cx = db.connect(tmp_db)
    try:
        _seed_with_source(cx, "JSS-CITE-001", "citation", "cran", tp=5, fp=0)
        # No arXiv data for this rule.
    finally:
        cx.close()

    from eval import report
    table = report.compute_precision_by_source(tmp_db)
    # Only sources with actual data should appear for this rule.
    sources_for_rule = {
        (r.source, r.rule_id) for r in table.rows if r.rule_id == "JSS-CITE-001"
    }
    assert ("cran", "JSS-CITE-001") in sources_for_rule
    # arXiv should NOT be synthesised as a zero-data row.
    assert ("arxiv", "JSS-CITE-001") not in sources_for_rule
