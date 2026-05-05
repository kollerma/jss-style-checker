"""Spec 010 — init renderer tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from texlint.api import ComplianceReport, Severity, Violation
from texlint.init import InitRefusedError, run


def _empty_report() -> ComplianceReport:
    return ComplianceReport(
        tool_version="0.0.0-test",
        journal_id="jss",
        violations=(),
        categories=(),
        compliance_percentage=100.0,
    )


def _violations_report() -> ComplianceReport:
    vs = (
        Violation(
            file=Path("manuscript.tex"),
            line=1,
            column=1,
            rule_id="JSS-CITE-002",
            severity=Severity.WARNING,
            message="x",
        ),
        Violation(
            file=Path("manuscript.tex"),
            line=2,
            column=1,
            rule_id="JSS-MARKUP-001",
            severity=Severity.WARNING,
            message="y",
        ),
    )
    return ComplianceReport(
        tool_version="0.0.0-test",
        journal_id="jss",
        violations=vs,
        categories=(),
        compliance_percentage=50.0,
    )


class TestInitRun:
    def test_writes_config(self, tmp_path: Path) -> None:
        result = run(tmp_path, report=_empty_report())
        assert result.wrote is True
        cfg = (tmp_path / ".jss-lint.toml").read_text()
        assert 'journal = "jss"' in cfg
        assert "ignore_rules = [" in cfg

    def test_dry_run_does_not_write(self, tmp_path: Path) -> None:
        result = run(tmp_path, report=_empty_report(), dry_run=True)
        assert result.wrote is False
        assert not (tmp_path / ".jss-lint.toml").exists()
        assert "journal" in result.contents

    def test_refuses_overwrite_without_force(self, tmp_path: Path) -> None:
        (tmp_path / ".jss-lint.toml").write_text("# existing\n")
        with pytest.raises(InitRefusedError):
            run(tmp_path, report=_empty_report())
        # File is untouched.
        assert (tmp_path / ".jss-lint.toml").read_text() == "# existing\n"

    def test_force_overwrites(self, tmp_path: Path) -> None:
        (tmp_path / ".jss-lint.toml").write_text("# existing\n")
        run(tmp_path, report=_empty_report(), force=True)
        cfg = (tmp_path / ".jss-lint.toml").read_text()
        assert 'journal = "jss"' in cfg

    def test_threshold_validation(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError):
            run(tmp_path, report=_empty_report(), threshold=1.5)
        with pytest.raises(ValueError):
            run(tmp_path, report=_empty_report(), threshold=-0.1)

    def test_must_fix_count_reflects_distinct_rules(self, tmp_path: Path) -> None:
        result = run(tmp_path, report=_violations_report())
        assert result.must_fix_count == 2
        assert result.total_violations == 2


class TestPrecisionDbSuppression:
    """Spec 010 follow-up: when an eval-jss precision DB is available,
    rules with measured precision below `--threshold` are added to
    `ignore_rules` automatically with an inline-comment audit trail."""

    @staticmethod
    def _make_db(path: Path, rule_precisions: dict[str, float | None]) -> None:
        """Create a minimal eval-jss SQLite schema at *path* and seed
        one ``iterations`` row + per-rule rows."""
        import sqlite3

        path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(path)
        try:
            conn.executescript(
                """
                CREATE TABLE iterations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TEXT NOT NULL,
                    label TEXT,
                    note TEXT,
                    corpus_size INTEGER,
                    tool_version TEXT,
                    full_parse_failures INTEGER,
                    pinned_parse_failures INTEGER
                );
                CREATE TABLE iteration_rule_stats (
                    iteration_id INTEGER NOT NULL,
                    scope TEXT NOT NULL,
                    rule_id TEXT NOT NULL,
                    category TEXT,
                    tp INTEGER,
                    fp INTEGER,
                    pending INTEGER,
                    precision REAL,
                    status TEXT
                );
                """
            )
            conn.execute(
                "INSERT INTO iterations (ts, label) VALUES (?, ?)",
                ("2026-05-04T00:00:00Z", "test-iteration"),
            )
            iter_id = conn.execute("SELECT MAX(id) FROM iterations").fetchone()[0]
            for rid, p in rule_precisions.items():
                conn.execute(
                    "INSERT INTO iteration_rule_stats "
                    "(iteration_id, scope, rule_id, category, tp, fp, pending, "
                    "precision, status) VALUES (?, 'full', ?, 'test', 0, 0, 0, "
                    "?, ?)",
                    (iter_id, rid, p, "PASS" if p and p >= 0.9 else "FAIL"),
                )
            conn.commit()
        finally:
            conn.close()

    def test_db_below_threshold_rules_are_suppressed(
        self, tmp_path: Path
    ) -> None:
        db_path = tmp_path / "eval" / "precision-history.db"
        self._make_db(
            db_path,
            {
                "JSS-FAKE-001": 0.50,  # below 0.90 — must be suppressed
                "JSS-FAKE-002": 0.95,  # above 0.90 — must NOT be suppressed
            },
        )
        result = run(
            tmp_path,
            report=_empty_report(),
            precision_db_path=db_path,
        )
        assert result.suppressed_count == 1
        cfg = (tmp_path / ".jss-lint.toml").read_text()
        assert '"JSS-FAKE-001"' in cfg
        assert '"JSS-FAKE-002"' not in cfg
        assert "precision 0.50" in cfg
        assert "test-iteration" in cfg

    def test_threshold_argument_is_honoured(self, tmp_path: Path) -> None:
        db_path = tmp_path / "eval" / "precision-history.db"
        self._make_db(db_path, {"JSS-FAKE-A": 0.85})
        # At threshold 0.90 the rule (0.85) IS suppressed.
        r1 = run(
            tmp_path,
            report=_empty_report(),
            precision_db_path=db_path,
            threshold=0.90,
        )
        assert r1.suppressed_count == 1
        # At threshold 0.80 the same rule is NOT suppressed; force-overwrite.
        r2 = run(
            tmp_path,
            report=_empty_report(),
            precision_db_path=db_path,
            threshold=0.80,
            force=True,
        )
        assert r2.suppressed_count == 0

    def test_missing_db_falls_back_gracefully(self, tmp_path: Path) -> None:
        # No DB at the explicit path; suppression list stays empty.
        result = run(
            tmp_path,
            report=_empty_report(),
            precision_db_path=tmp_path / "no-such.db",
        )
        assert result.suppressed_count == 0

    def test_unmeasured_rule_is_not_suppressed(self, tmp_path: Path) -> None:
        # A rule with NULL precision is "NOT MEASURED"; we must not
        # silently suppress it just because we can't prove it's
        # high-precision.
        db_path = tmp_path / "eval" / "precision-history.db"
        self._make_db(db_path, {"JSS-FAKE-X": None})
        result = run(
            tmp_path,
            report=_empty_report(),
            precision_db_path=db_path,
        )
        assert result.suppressed_count == 0
