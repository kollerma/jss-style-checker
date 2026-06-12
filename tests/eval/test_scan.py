"""Tests for `eval.scan` — dedup contract, JSS-PARSE-000 handling, runs audit.

Spec: FR-009, FR-010, FR-011, FR-012, SC-002, and edge case "Linter not
installed".
"""

from __future__ import annotations

import json
from pathlib import Path

from tests.eval.conftest import FakeCorpus  # type: ignore[import-not-found]

from eval import api, db, scan


def _fake_result(
    paper_dir: Path, *, violations: list[dict], exit_code: int = 0
) -> api.LinterResult:
    """Build a fake `LinterResult` shaped like `jss-lint --output json`."""
    payload = {
        "tool_version": "0.1.0",
        "journal_id": "jss",
        "compliance_percentage": 100.0 if not violations else 50.0,
        "categories": [],
        "violations": [
            {
                **v,
                "file": str(paper_dir / v["file"]),
            }
            for v in violations
        ],
    }
    return api.LinterResult(
        exit_code=exit_code,
        stdout=json.dumps(payload),
        stderr="",
        elapsed_seconds=0.01,
    )


def _install_fake_linter(monkeypatch, fake_corpus: FakeCorpus) -> list[Path]:
    """Monkeypatch `_invoke_linter` to drive scan from `fake_corpus`.

    Returns the list of paper_dirs passed to the fake, in invocation order.
    """
    call_log: list[Path] = []

    def _fake_invoke(paper_dir: Path, jss_lint: str) -> api.LinterResult:
        call_log.append(paper_dir)
        name = paper_dir.name
        violations = fake_corpus.expected_violations.get(name, [])
        # JSS-PARSE-000 implies exit 1 (violations present) per linter contract.
        exit_code = 1 if violations else 0
        return _fake_result(paper_dir, violations=violations, exit_code=exit_code)

    monkeypatch.setattr(scan, "_invoke_linter", _fake_invoke)
    # Pretend jss-lint is on PATH regardless of the test environment.
    monkeypatch.setattr(scan.shutil, "which", lambda name: "/fake/bin/jss-lint")
    return call_log


def test_scan_persists_violations_and_runs_row(
    monkeypatch, tmp_db: Path, fake_corpus: FakeCorpus
) -> None:
    _install_fake_linter(monkeypatch, fake_corpus)

    code = scan.run(db_path=tmp_db, corpus_dir=fake_corpus.root, batch_size=None, force=False)

    # Exit 1 because fake_corpus includes violations + a parse failure.
    assert code == 1

    cx = db.connect(tmp_db)
    try:
        papers = cx.execute("SELECT path FROM papers ORDER BY path").fetchall()
        assert {Path(r["path"]).name for r in papers} == {
            "paper_clean",
            "paper_violations",
            "paper_parse_fail",
        }
        violations = cx.execute("SELECT rule_id FROM violations").fetchall()
        # 2 rule violations + 1 parse failure = 3
        assert len(violations) == 3
        rule_ids = {r["rule_id"] for r in violations}
        assert "JSS-PARSE-000" in rule_ids

        runs = cx.execute("SELECT * FROM runs").fetchall()
        assert len(runs) == 1
        assert runs[0]["tool_version"] == "0.1.0"
        assert runs[0]["papers_scanned"] == 3
        assert runs[0]["violations_found"] == 3
    finally:
        cx.close()


def test_scan_dedup_on_rerun(monkeypatch, tmp_db: Path, fake_corpus: FakeCorpus) -> None:
    _install_fake_linter(monkeypatch, fake_corpus)

    scan.run(db_path=tmp_db, corpus_dir=fake_corpus.root, batch_size=None, force=True)
    scan.run(db_path=tmp_db, corpus_dir=fake_corpus.root, batch_size=None, force=True)

    cx = db.connect(tmp_db)
    try:
        # Same rule+line+message pairs, so dedup kicks in. Still 3 violation rows.
        assert cx.execute("SELECT COUNT(*) FROM violations").fetchone()[0] == 3
        assert cx.execute("SELECT COUNT(*) FROM runs").fetchone()[0] == 2
    finally:
        cx.close()


def test_scan_preserves_verdicts_on_rerun(
    monkeypatch, tmp_db: Path, fake_corpus: FakeCorpus
) -> None:
    _install_fake_linter(monkeypatch, fake_corpus)

    scan.run(db_path=tmp_db, corpus_dir=fake_corpus.root, batch_size=None, force=False)
    cx = db.connect(tmp_db)
    try:
        cx.execute(
            "UPDATE violations SET verdict='true_positive', reviewer='human:test'"
            " WHERE rule_id='JSS-CITE-001'"
        )
    finally:
        cx.close()

    scan.run(db_path=tmp_db, corpus_dir=fake_corpus.root, batch_size=None, force=True)

    cx = db.connect(tmp_db)
    try:
        verdict = cx.execute(
            "SELECT verdict, reviewer FROM violations WHERE rule_id='JSS-CITE-001'"
        ).fetchone()
        assert verdict["verdict"] == "true_positive"
        assert verdict["reviewer"] == "human:test"
    finally:
        cx.close()


def test_scan_missing_linter_exits_2(monkeypatch, tmp_db: Path, fake_corpus: FakeCorpus) -> None:
    monkeypatch.setattr(scan.shutil, "which", lambda name: None)
    code = scan.run(db_path=tmp_db, corpus_dir=fake_corpus.root, batch_size=None, force=False)
    assert code == 2


def test_scan_missing_corpus_exits_2(monkeypatch, tmp_db: Path, tmp_path: Path) -> None:
    monkeypatch.setattr(scan.shutil, "which", lambda name: "/fake/bin/jss-lint")
    code = scan.run(
        db_path=tmp_db,
        corpus_dir=tmp_path / "does_not_exist",
        batch_size=None,
        force=False,
    )
    assert code == 2


def test_scan_empty_corpus_is_success(monkeypatch, tmp_db: Path, tmp_path: Path) -> None:
    (tmp_path / "empty").mkdir()
    monkeypatch.setattr(scan.shutil, "which", lambda name: "/fake/bin/jss-lint")

    code = scan.run(db_path=tmp_db, corpus_dir=tmp_path / "empty", batch_size=None, force=False)

    assert code == 0
    cx = db.connect(tmp_db)
    try:
        runs = cx.execute("SELECT papers_scanned, violations_found FROM runs").fetchall()
        assert len(runs) == 1
        assert runs[0]["papers_scanned"] == 0
        assert runs[0]["violations_found"] == 0
    finally:
        cx.close()


def test_scan_malformed_json_records_parse_failure(
    monkeypatch, tmp_db: Path, fake_corpus: FakeCorpus
) -> None:
    def _bad_invoke(paper_dir: Path, jss_lint: str) -> api.LinterResult:
        return api.LinterResult(
            exit_code=2, stdout="not-json", stderr="segfault-like", elapsed_seconds=0.01
        )

    monkeypatch.setattr(scan, "_invoke_linter", _bad_invoke)
    monkeypatch.setattr(scan.shutil, "which", lambda name: "/fake/bin/jss-lint")

    code = scan.run(db_path=tmp_db, corpus_dir=fake_corpus.root, batch_size=None, force=False)

    assert code == 1  # parse failures still produce a report; exit 1 per spec
    cx = db.connect(tmp_db)
    try:
        rule_ids = {r["rule_id"] for r in cx.execute("SELECT rule_id FROM violations").fetchall()}
        assert rule_ids == {"JSS-PARSE-000"}
        statuses = {r["status"] for r in cx.execute("SELECT status FROM papers").fetchall()}
        assert "scan_failed" in statuses
    finally:
        cx.close()


class TestVersionedPaperLayout:
    """`<paper>/<revision>/*.tex` layouts (jss5342-versions): final/
    wins, rendered .tex beats same-stem .Rnw, correspondence skipped."""

    def _mk(self, root: Path, rel: str) -> Path:
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("x", encoding="utf-8")
        return p

    def test_final_revision_wins(self, tmp_path: Path) -> None:
        from eval.scan import _source_files

        self._mk(tmp_path, "initial/article.tex")
        self._mk(tmp_path, "final/paper.tex")
        bib = self._mk(tmp_path, "final/refs.bib")
        self._mk(tmp_path, "_analysis/notes.tex")

        files = _source_files(tmp_path)

        assert files == [tmp_path / "final/paper.tex", bib]

    def test_tex_beats_same_stem_rnw_and_comments_skipped(
        self, tmp_path: Path
    ) -> None:
        from eval.scan import _source_files

        self._mk(tmp_path, "final/paper.Rnw")
        tex = self._mk(tmp_path, "final/paper.tex")
        other_rnw = self._mk(tmp_path, "final/extra.Rnw")
        self._mk(tmp_path, "final/reviewer-comments.tex")

        files = _source_files(tmp_path)

        assert files == [other_rnw, tex]

    def test_all_revisions_without_final(self, tmp_path: Path) -> None:
        from eval.scan import _source_files

        a = self._mk(tmp_path, "draft1/p.tex")
        b = self._mk(tmp_path, "draft2/p.tex")
        self._mk(tmp_path, ".hidden/x.tex")

        assert _source_files(tmp_path) == [a, b]

    def test_vignette_layout_still_preferred(self, tmp_path: Path) -> None:
        from eval.scan import _source_files

        v = self._mk(tmp_path, "pkg/vignettes/v.Rnw")
        self._mk(tmp_path, "final/decoy.tex")

        assert _source_files(tmp_path) == [v]
