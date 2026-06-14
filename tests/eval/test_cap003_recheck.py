"""Tests for the CAP-003 double-check (eval.cap003_recheck)."""

from __future__ import annotations

from pathlib import Path

from eval import cap003_recheck as rc
from eval import db


class TestExtractCaption:
    def test_single_line(self):
        src = "\\begin{figure}\n\\caption{A simple caption.}\n\\end{figure}\n"
        assert rc.extract_caption(src, 2) == "A simple caption."

    def test_multi_line_balanced(self):
        src = (
            "x\n"
            "\\caption{First part\n"
            "  second part with {nested} braces}\n"
        )
        body = rc.extract_caption(src, 2)
        assert body is not None
        assert "second part with {nested} braces" in body

    def test_skips_optional_short_caption(self):
        src = "\\caption[short]{The long form caption.}\n"
        assert rc.extract_caption(src, 1) == "The long form caption."

    def test_unbalanced_returns_none(self):
        src = "\\caption{never closed\n"
        assert rc.extract_caption(src, 1) is None

    def test_line_out_of_range(self):
        assert rc.extract_caption("\\caption{x}", 9) is None


class TestAnalyzeCaption:
    def test_title_case_flags_ordinary_capitals(self):
        a = rc.analyze_caption("Cluster Quality Measures Available in things")
        # first word excluded; Quality/Measures/Available are ordinary caps
        assert a.ordinary_capitals == ["Quality", "Measures", "Available"]
        assert a.heuristic_offenders == 3

    def test_proper_nouns_still_listed_for_judge(self):
        # The tool does NOT decide proper nouns — it surfaces ordinary
        # capitals (incl. proper nouns) for the judge. Joe is ordinary.
        a = rc.analyze_caption("Periodograms for Mrk obtained from a Joe copula")
        assert "Joe" in a.ordinary_capitals
        assert "Mrk" in a.ordinary_capitals

    def test_math_and_code_excluded(self):
        a = rc.analyze_caption(
            "Estimates of $Q_{xt}$ from \\texttt{WeightedCluster} runs"
        )
        # $...$ and \texttt{...} content must not appear as capitals.
        assert "Q" not in a.ordinary_capitals
        assert "WeightedCluster" not in a.ordinary_capitals

    def test_acronyms_and_numbers_tagged_not_ordinary(self):
        a = rc.analyze_caption("Plot for GROJ0422 and PARAFAC components")
        assert "GROJ0422" not in a.ordinary_capitals
        assert "PARAFAC" not in a.ordinary_capitals

    def test_single_letter_not_ordinary(self):
        a = rc.analyze_caption("Trends in X over time")
        assert "X" not in a.ordinary_capitals

    def test_label_construct_stripped(self):
        a = rc.analyze_caption("\\label{fig:x}The support curve shown")
        assert "fig" not in a.clean
        assert a.words[0].word == "The"

    def test_sentence_case_has_no_ordinary_capitals(self):
        a = rc.analyze_caption("Periodogram bars calculated from a spline model")
        assert a.ordinary_capitals == []
        assert a.heuristic_offenders == 0


def _seed_cap003(cx, *, line: int, verdict, reviewer, source: str,
                 paper="examples/p", file="m.tex") -> int:
    cx.execute(
        "INSERT INTO runs (ts, tool_version, papers_scanned, violations_found)"
        " VALUES ('2026-01-01T00:00:00Z', '0.1.0', 1, 1)"
    )
    run_id = cx.execute("SELECT MAX(id) FROM runs").fetchone()[0]
    cx.execute(
        "INSERT OR IGNORE INTO papers (path, source, status)"
        " VALUES (?, 'manual', 'scanned')",
        (paper,),
    )
    pid = cx.execute("SELECT id FROM papers WHERE path = ?", (paper,)).fetchone()[0]
    cx.execute(
        "INSERT INTO violations (paper_id, rule_id, category, line, message,"
        " severity, verdict, reviewer, first_seen_run_id, last_seen_run_id, file)"
        " VALUES (?, 'JSS-CAP-003', 'capitalization', ?, 'caption', 'info',"
        " ?, ?, ?, ?, ?)",
        (pid, line, verdict, reviewer, run_id, run_id, file),
    )
    return cx.execute("SELECT last_insert_rowid()").fetchone()[0]


class TestApplyVerdicts:
    def test_writes_pending_and_proxy_but_not_human(self, tmp_db: Path, tmp_path):
        db.init(tmp_db)
        cx = db.connect(tmp_db)
        try:
            human = _seed_cap003(cx, line=1, verdict="true_positive",
                                 reviewer="human:unknown", source="")
            proxy = _seed_cap003(cx, line=2, verdict="true_positive",
                                 reviewer="human:claude-proxy", source="")
            pending = _seed_cap003(cx, line=3, verdict=None,
                                   reviewer=None, source="")
            verdicts = [
                {"id": human, "verdict": "false_positive", "reason": "x"},
                {"id": proxy, "verdict": "false_positive", "reason": "y"},
                {"id": pending, "verdict": "true_positive", "reason": "z"},
            ]
            report = rc.apply_verdicts(cx, verdicts)

            # human row untouched, counted as a DISAGREEMENT
            row = cx.execute(
                "SELECT verdict, reviewer FROM violations WHERE id=?", (human,)
            ).fetchone()
            assert row["verdict"] == "true_positive"
            assert row["reviewer"] == "human:unknown"
            assert len(report.human_disagreements) == 1
            assert report.human_disagreements[0]["id"] == human

            # proxy + pending rewritten under the judge reviewer
            assert report.written == 2
            for vid, expect in ((proxy, "false_positive"),
                                (pending, "true_positive")):
                r = cx.execute(
                    "SELECT verdict, reviewer FROM violations WHERE id=?", (vid,)
                ).fetchone()
                assert r["verdict"] == expect
                assert r["reviewer"] == rc.JUDGE_REVIEWER
        finally:
            cx.close()

    def test_human_agreement_counted(self, tmp_db: Path):
        db.init(tmp_db)
        cx = db.connect(tmp_db)
        try:
            human = _seed_cap003(cx, line=1, verdict="true_positive",
                                 reviewer="human:unknown", source="")
            report = rc.apply_verdicts(
                cx, [{"id": human, "verdict": "true_positive", "reason": "ok"}]
            )
            assert report.human_agreements == 1
            assert report.human_agreement_rate == 1.0
            assert report.written == 0
        finally:
            cx.close()

    def test_unknown_id_ignored(self, tmp_db: Path):
        db.init(tmp_db)
        cx = db.connect(tmp_db)
        try:
            report = rc.apply_verdicts(
                cx, [{"id": 99999, "verdict": "true_positive", "reason": "x"}]
            )
            assert report.skipped_unknown_id == [99999]
            assert report.written == 0
        finally:
            cx.close()
