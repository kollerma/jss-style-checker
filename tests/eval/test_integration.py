"""End-to-end integration test for Phase A MVP.

Drives the full pipeline `init → scan → human-review → report` against
the 3-paper `fake_corpus` fixture. Asserts per-rule precision numbers
match hand-computed values and the whole run finishes quickly (spec SC-005).

Spec: FR-028. User Story 1 independent test.
"""

from __future__ import annotations

import json
import time
from collections import deque
from pathlib import Path

from click.testing import CliRunner

from eval import api, cli as cli_mod, db, human_review, scan
from tests.eval.conftest import FakeCorpus  # type: ignore[import-not-found]


def _install_fake_linter(monkeypatch, fake_corpus: FakeCorpus) -> None:
    def _fake_invoke(paper_dir: Path, jss_lint: str) -> api.LinterResult:
        name = paper_dir.name
        violations_for_paper = fake_corpus.expected_violations.get(name, [])
        payload = {
            "tool_version": "0.1.0",
            "journal_id": "jss",
            "compliance_percentage": 100.0,
            "categories": [],
            "violations": [
                {**v, "file": str(paper_dir / v["file"])}
                for v in violations_for_paper
            ],
        }
        return api.LinterResult(
            exit_code=1 if violations_for_paper else 0,
            stdout=json.dumps(payload),
            stderr="",
            elapsed_seconds=0.01,
        )

    monkeypatch.setattr(scan, "_invoke_linter", _fake_invoke)
    monkeypatch.setattr(scan.shutil, "which", lambda _n: "/fake/bin/jss-lint")


def test_full_phase_a_pipeline_under_10s(monkeypatch, tmp_path: Path, fake_corpus: FakeCorpus) -> None:
    _install_fake_linter(monkeypatch, fake_corpus)

    # Scripted answers for human-review: three violations in review order.
    # Order is alphabetical by paper path, then line, so:
    #   1. paper_parse_fail/  → JSS-PARSE-000 (line 1) → "t" TP
    #   2. paper_violations/  → JSS-CITE-001  (line 3) → "f" FP, reason "noisy"
    #   3. paper_violations/  → JSS-SRC-001   (line 42) → "t" TP
    answers = deque(["t", "", "f", "noisy", "t", "", "q"])
    monkeypatch.setattr(
        human_review.Prompt, "ask", staticmethod(lambda *a, **k: answers.popleft() if answers else "q")
    )

    db_path = tmp_path / "eval.db"
    runner = CliRunner()

    t0 = time.perf_counter()

    r = runner.invoke(cli_mod.cli, ["--db", str(db_path), "init"])
    assert r.exit_code == 0, r.output

    r = runner.invoke(cli_mod.cli, ["--db", str(db_path), "scan", "--corpus", str(fake_corpus.root)])
    assert r.exit_code == 1, r.output  # violations present

    r = runner.invoke(
        cli_mod.cli,
        ["--db", str(db_path), "human-review", "--reviewer", "human:integ"],
    )
    assert r.exit_code == 0, r.output

    r = runner.invoke(cli_mod.cli, ["--db", str(db_path), "report"])
    # JSS-CITE-001 at 0% precision (1 FP, 0 TP) → exit 1.
    assert r.exit_code == 1, r.output

    elapsed = time.perf_counter() - t0
    assert elapsed < 10.0, f"pipeline took {elapsed:.1f}s (spec SC-005 target: <10s)"

    # Verify the DB contents match hand-computed expectations.
    cx = db.connect(db_path)
    try:
        rows = cx.execute(
            "SELECT rule_id, verdict FROM violations ORDER BY rule_id"
        ).fetchall()
        by_rule = {r["rule_id"]: r["verdict"] for r in rows}
        assert by_rule == {
            "JSS-PARSE-000": "true_positive",
            "JSS-CITE-001": "false_positive",
            "JSS-SRC-001": "true_positive",
        }
    finally:
        cx.close()
