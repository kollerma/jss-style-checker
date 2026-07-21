"""Regression tests for tools/export_labels.py's control-character
hardening (roadmap/follow-ups.md: run-249 corruption). Two independent
layers, tested independently:

* `_normalize_text` — verdict_reason is flattened before it ever
  reaches the CSV writer.
* `_rows_to_csv_gz` — the writer itself must not shatter a row even
  if a raw control byte reaches it anyway (defense in depth).
"""

from __future__ import annotations

import csv
import gzip
import io
from pathlib import Path

from tools import export_labels

from eval import db as eval_db


def test_normalize_text_flattens_control_chars() -> None:
    assert (
        export_labels._normalize_text("wrong case\x0def{fig:x} used")
        == "wrong case ef{fig:x} used"
    )
    assert export_labels._normalize_text("a\tb\nc\rd") == "a b c d"
    assert export_labels._normalize_text("  padded  ") == "padded"


def test_rows_to_csv_gz_survives_bare_control_chars() -> None:
    """Even a hostile/un-normalized field with a bare \\r must not
    shatter the row when the export is written and re-read."""
    header = ("paper", "file", "rule_id", "line", "verdict", "reviewer_class", "verdict_reason")
    rows = [
        ("p1", "f1.tex", "JSS-XREF-002", "10", "false_positive", "human",
         "text with \r bare cr and \n newline and \t tab"),
        ("p2", "f2.tex", "JSS-CODE-003", "20", "true_positive", "ai_model", "clean row"),
    ]
    blob = export_labels._rows_to_csv_gz(header, rows)
    with gzip.open(io.BytesIO(blob), "rt", encoding="utf-8", newline="") as f:
        parsed = list(csv.reader(f))
    assert len(parsed) == 3  # header + 2 data rows, none shattered
    assert parsed[1] == list(rows[0])
    assert parsed[2] == list(rows[1])


def test_build_labels_export_normalizes_corrupted_verdict_reason(tmp_path: Path) -> None:
    """End-to-end: a verdict_reason with the exact run-249 corruption
    shape (bare CR where \\ref{...} was meant) round-trips through
    build_labels_export into a structurally intact, control-char-free
    CSV row."""
    db_path = tmp_path / "eval.db"
    eval_db.init(db_path)
    cx = eval_db.connect(db_path)
    try:
        cx.execute(
            "INSERT INTO runs (ts, tool_version, papers_scanned, violations_found) "
            "VALUES ('2026-07-20T00:00:00Z', '1.1.0', 1, 1)"
        )
        cx.execute(
            "INSERT INTO papers (path, source, status) VALUES ('examples/x', 'cran', 'scanned')"
        )
        cx.execute(
            "INSERT INTO violations (paper_id, rule_id, category, line, message, "
            "severity, verdict, verdict_reason, reviewer, first_seen_run_id) "
            "VALUES (1, 'JSS-XREF-002', 'xref', 10, 'msg', 'warning', "
            "'false_positive', 'Equation references use\x0def{trend} with lowercase', "
            "'ai:bonsai', 1)"
        )
    finally:
        cx.close()

    blob = export_labels.build_labels_export(db_path)
    with gzip.open(io.BytesIO(blob), "rt", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 1
    reason = rows[0]["verdict_reason"]
    assert reason == "Equation references use ef{trend} with lowercase"
    assert not any(c in reason for c in "\x08\x09\x0a\x0c\x0d")
