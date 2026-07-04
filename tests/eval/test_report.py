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


def test_precision_exclusion_drops_matching_firings(
    tmp_db: Path, tmp_path: Path, monkeypatch
) -> None:
    cx = db.connect(tmp_db)
    try:
        _seed(cx, "JSS-OPER-002", "unknown", tp=5, fp=3, pending=0)
        _seed(cx, "JSS-CITE-001", "citation", tp=4, fp=1, pending=0)
    finally:
        cx.close()

    excl = tmp_path / "excl.toml"
    excl.write_text(
        '[[exclusions]]\npaper = "p_JSS-OPER-002"\n'
        'rule_id = "JSS-OPER-002"\nreason = "test"\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(report, "_EXCLUSIONS_PATH", excl)

    rows = {r.rule_id: r for r in report.compute_precision(tmp_db).rows}
    # OPER-002's firings on the matching paper are dropped (both TP and FP).
    assert rows.get("JSS-OPER-002", None) is None or (
        rows["JSS-OPER-002"].tp == 0 and rows["JSS-OPER-002"].fp == 0
    )
    # A different rule is unaffected.
    assert rows["JSS-CITE-001"].tp == 4 and rows["JSS-CITE-001"].fp == 1


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


# ---------------------------------------------------------------------------
# Spec 005 US4: Per-format precision breakdown
# ---------------------------------------------------------------------------


def _seed_with_format(
    cx, rule_id: str, category: str, file_suffix: str, tp: int, fp: int
) -> None:
    """Seed violations whose `file_suffix` is `file_suffix` (e.g. '.tex', '.Rnw')."""
    cx.execute(
        "INSERT INTO runs (ts, tool_version, papers_scanned, violations_found)"
        " VALUES ('2026-04-23T00:00:00Z', '0.1.0', 1, ?)",
        (tp + fp,),
    )
    run_id = cx.execute("SELECT last_insert_rowid()").fetchone()[0]
    cx.execute(
        "INSERT INTO papers (path, source, status) VALUES (?, 'manual', 'scanned')",
        (f"p_{rule_id}_{file_suffix}",),
    )
    paper_id = cx.execute("SELECT last_insert_rowid()").fetchone()[0]
    for i in range(tp):
        cx.execute(
            "INSERT INTO violations (paper_id, rule_id, category, line, message, severity,"
            " verdict, reviewer, first_seen_run_id, file_suffix) VALUES (?, ?, ?, ?, ?,"
            " 'warning', 'true_positive', 'human:t', ?, ?)",
            (paper_id, rule_id, category, 100 + i, f"{file_suffix}-tp-{i}",
             run_id, file_suffix),
        )
    for i in range(fp):
        cx.execute(
            "INSERT INTO violations (paper_id, rule_id, category, line, message, severity,"
            " verdict, reviewer, first_seen_run_id, file_suffix) VALUES (?, ?, ?, ?, ?,"
            " 'warning', 'false_positive', 'human:t', ?, ?)",
            (paper_id, rule_id, category, 200 + i, f"{file_suffix}-fp-{i}",
             run_id, file_suffix),
        )


def test_by_format_partitions_tex_rnw_rmd(tmp_db: Path) -> None:
    cx = db.connect(tmp_db)
    try:
        _seed_with_format(cx, "JSS-CITE-001", "citation", ".tex", tp=9, fp=1)
        _seed_with_format(cx, "JSS-CITE-001", "citation", ".Rnw", tp=4, fp=0)
        _seed_with_format(cx, "JSS-CITE-001", "citation", ".Rmd", tp=2, fp=3)
    finally:
        cx.close()

    table = report.compute_precision_by_format(tmp_db)
    per = {(r.rule_id, r.source): r for r in table.rows}

    # Overall merges all three formats: 15 TP / 19 total ≈ 78.9% → FAIL
    assert per[("JSS-CITE-001", "overall")].tp == 15
    assert per[("JSS-CITE-001", "overall")].fp == 4
    assert per[("JSS-CITE-001", "overall")].status == "FAIL"

    # Per-format rows reflect each suffix's own precision.
    assert per[("JSS-CITE-001", "tex")].precision == 0.9
    assert per[("JSS-CITE-001", "rnw")].precision == 1.0
    assert per[("JSS-CITE-001", "rmd")].precision == 0.4
    # breakdown label is "format" so the renderer uses "Per-format breakdown".
    assert table.breakdown == "format"


def test_by_format_csv_emits_overall_plus_per_format(
    tmp_db: Path, tmp_path: Path
) -> None:
    cx = db.connect(tmp_db)
    try:
        _seed_with_format(cx, "JSS-CITE-001", "citation", ".tex", tp=9, fp=1)
        _seed_with_format(cx, "JSS-CITE-001", "citation", ".Rmd", tp=1, fp=4)
    finally:
        cx.close()

    csv_path = tmp_path / "by_format.csv"
    runner = CliRunner()
    r = runner.invoke(
        cli_mod.cli,
        ["--db", str(tmp_db), "report", "--by-format", "--csv", str(csv_path)],
    )
    # Overall: 10 TP / 15 total ≈ 66% → FAIL → exit 1
    assert r.exit_code == 1, r.output

    import csv as _csv
    with csv_path.open(encoding="utf-8") as f:
        rows = list(_csv.DictReader(f))

    sources = {r["source"] for r in rows if r["rule_id"] == "JSS-CITE-001"}
    assert sources == {"overall", "tex", "rmd"}

    per = {(r["rule_id"], r["source"]): r for r in rows}
    assert per[("JSS-CITE-001", "tex")]["precision"] == "0.9000"
    assert per[("JSS-CITE-001", "rmd")]["precision"] == "0.2000"
    # tex passes the threshold; rmd does not.
    assert per[("JSS-CITE-001", "tex")]["below_threshold"] == "0"
    assert per[("JSS-CITE-001", "rmd")]["below_threshold"] == "1"


def test_by_format_null_suffix_bucketed_as_unknown(tmp_db: Path) -> None:
    # Pre-005 violations (no file_suffix) bucket as "unknown" in the
    # per-format breakdown. They still count toward overall precision.
    cx = db.connect(tmp_db)
    try:
        _seed_with_format(cx, "JSS-CITE-001", "citation", ".tex", tp=5, fp=0)
        # Legacy row without file_suffix (simulated via NULL).
        cx.execute(
            "INSERT INTO runs (ts, tool_version, papers_scanned, violations_found)"
            " VALUES ('2026-04-23T00:00:00Z', '0.1.0', 1, 1)"
        )
        run_id = cx.execute("SELECT last_insert_rowid()").fetchone()[0]
        cx.execute(
            "INSERT INTO papers (path, source, status)"
            " VALUES ('p_legacy', 'manual', 'scanned')"
        )
        paper_id = cx.execute("SELECT last_insert_rowid()").fetchone()[0]
        cx.execute(
            "INSERT INTO violations (paper_id, rule_id, category, line, message, severity,"
            " verdict, reviewer, first_seen_run_id) VALUES (?, 'JSS-CITE-001', 'citation',"
            " 1, 'legacy', 'warning', 'true_positive', 'human:t', ?)",
            (paper_id, run_id),
        )
    finally:
        cx.close()

    table = report.compute_precision_by_format(tmp_db)
    by_source = {r.source for r in table.rows if r.rule_id == "JSS-CITE-001"}
    assert "tex" in by_source
    assert "unknown" in by_source


def test_by_format_default_report_unchanged(tmp_db: Path) -> None:
    # Regression: `eval-jss report` (no flag) output is byte-identical
    # before and after the --by-format feature on the same inputs.
    cx = db.connect(tmp_db)
    try:
        _seed_with_format(cx, "JSS-CITE-001", "citation", ".tex", tp=9, fp=1)
        _seed_with_format(cx, "JSS-CITE-001", "citation", ".Rnw", tp=4, fp=0)
    finally:
        cx.close()

    default_table = report.compute_precision(tmp_db)
    # No breakdown rows, default dimension flag is "source".
    assert all(r.source == "overall" for r in default_table.rows)
    assert default_table.breakdown == "source"


def test_by_format_and_by_source_mutually_exclusive(tmp_db: Path) -> None:
    runner = CliRunner()
    r = runner.invoke(
        cli_mod.cli,
        ["--db", str(tmp_db), "report", "--by-format", "--by-source"],
    )
    assert r.exit_code == 2
    assert "mutually exclusive" in r.output


def _seed_with_class(cx, rule_id, category, doc_class, tp, fp):
    """Seed violations on a paper carrying the given doc_class. Reuses
    the latest run (one scan covers all papers) so last_seen_run_id
    stays at MAX(run) for every seeded row."""
    run_id = cx.execute("SELECT MAX(id) FROM runs").fetchone()[0]
    if run_id is None:
        cx.execute(
            "INSERT INTO runs (ts, tool_version, papers_scanned, violations_found)"
            " VALUES ('2026-04-23T00:00:00Z', '0.1.0', 1, ?)", (tp + fp,))
        run_id = cx.execute("SELECT last_insert_rowid()").fetchone()[0]
    cx.execute(
        "INSERT INTO papers (path, source, status, doc_class)"
        " VALUES (?, 'cran', 'scanned', ?)",
        (f"p_{rule_id}_{doc_class}", doc_class))
    pid = cx.execute("SELECT last_insert_rowid()").fetchone()[0]
    for i in range(tp):
        cx.execute(
            "INSERT INTO violations (paper_id, rule_id, category, line, message,"
            " severity, verdict, reviewer, first_seen_run_id, last_seen_run_id)"
            " VALUES (?, ?, ?, ?, ?, 'warning', 'true_positive', 'human:t', ?, ?)",
            (pid, rule_id, category, 100 + i, f"{doc_class}-tp-{i}", run_id, run_id))
    for i in range(fp):
        cx.execute(
            "INSERT INTO violations (paper_id, rule_id, category, line, message,"
            " severity, verdict, reviewer, first_seen_run_id, last_seen_run_id)"
            " VALUES (?, ?, ?, ?, ?, 'warning', 'false_positive', 'human:t', ?, ?)",
            (pid, rule_id, category, 200 + i, f"{doc_class}-fp-{i}", run_id, run_id))


def test_by_class_partitions_jss_and_non_jss(tmp_db: Path) -> None:
    from eval import report
    cx = db.connect(tmp_db)
    try:
        # Same rule, different document classes, different precision.
        _seed_with_class(cx, "JSS-MARKUP-001", "markup", "jss", tp=9, fp=1)
        _seed_with_class(cx, "JSS-MARKUP-001", "markup", "non-jss", tp=2, fp=8)
    finally:
        cx.close()
    table = report.compute_precision_by_class(tmp_db)
    by_class = {
        r.source: (r.tp, r.fp)
        for r in table.rows
        if r.rule_id == "JSS-MARKUP-001" and r.source in {"jss", "non-jss", "overall"}
    }
    assert by_class["jss"] == (9, 1)
    assert by_class["non-jss"] == (2, 8)
    assert by_class["overall"] == (11, 9)  # overall layer still aggregates both


def test_by_class_null_doc_class_bucketed_unknown(tmp_db: Path) -> None:
    from eval import report
    cx = db.connect(tmp_db)
    try:
        _seed(cx, "JSS-X-001", "x", tp=3, fp=0, pending=0)  # no doc_class set
    finally:
        cx.close()
    table = report.compute_precision_by_class(tmp_db)
    src = {r.source for r in table.rows if r.rule_id == "JSS-X-001"}
    assert "unknown" in src
