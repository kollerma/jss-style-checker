"""Spec 017 — `eval-jss recall` CLI subcommand tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner
from eval.cli import cli


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


def _write_paper(
    corpus: Path,
    paper_id: str,
    *,
    manuscript: str,
    annotations_toml: str,
) -> None:
    paper_dir = corpus / paper_id
    paper_dir.mkdir(parents=True, exist_ok=True)
    (paper_dir / "manuscript.tex").write_text(manuscript, encoding="utf-8")
    (paper_dir / "annotations.toml").write_text(annotations_toml, encoding="utf-8")


_MIN_TEX = (
    "\\documentclass[article]{jss}\n"
    "\\title{T}\n"
    "\\author{A}\n"
    "\\Plainauthor{A}\n"
    "\\Abstract{D.}\n"
    "\\Keywords{k}\n"
    "\\Address{Z}\n"
    "\\begin{document}\nBody.\n\\end{document}\n"
)

_EMPTY_ANNOTATIONS = (
    '[meta]\n'
    'paper_id = "p1"\n'
    'annotator = "test"\n'
    'date = "2026-05-05"\n'
    '\n'
)


class TestEmptyCorpus:
    def test_no_papers_exits_zero(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        corpus = tmp_path / "corpus"
        corpus.mkdir()
        result = runner.invoke(
            cli,
            [
                "recall",
                "--corpus", str(corpus),
                "--no-record",
            ],
        )
        assert result.exit_code == 0
        assert "corpus is empty" in result.stdout

    def test_missing_corpus_dir_exits_two(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        result = runner.invoke(
            cli,
            ["recall", "--corpus", str(tmp_path / "no-such")],
        )
        assert result.exit_code == 2


class TestValidate:
    def test_valid_annotation_passes(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        corpus = tmp_path / "corpus"
        _write_paper(
            corpus, "p1",
            manuscript=_MIN_TEX,
            annotations_toml=_EMPTY_ANNOTATIONS,
        )
        result = runner.invoke(
            cli,
            ["recall", "--corpus", str(corpus), "--validate"],
        )
        assert result.exit_code == 0
        assert "validated 1" in result.stdout

    def test_missing_paper_id_fails(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        corpus = tmp_path / "corpus"
        _write_paper(
            corpus, "p1",
            manuscript=_MIN_TEX,
            annotations_toml='[meta]\nannotator = "x"\n',
        )
        result = runner.invoke(
            cli,
            ["recall", "--corpus", str(corpus), "--validate"],
        )
        assert result.exit_code == 2
        assert "missing meta.paper_id" in result.stderr

    def test_missing_violation_field_fails(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        bad = (
            '[meta]\npaper_id = "p1"\nannotator = "x"\ndate = "2026-05-05"\n'
            '\n[[violations]]\nrule_id = "JSS-X-001"\n# missing file + line\n'
        )
        corpus = tmp_path / "corpus"
        _write_paper(
            corpus, "p1", manuscript=_MIN_TEX, annotations_toml=bad,
        )
        result = runner.invoke(
            cli,
            ["recall", "--corpus", str(corpus), "--validate"],
        )
        assert result.exit_code == 2


class TestRunNoRecord:
    def test_clean_paper_runs_to_completion(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        corpus = tmp_path / "corpus"
        _write_paper(
            corpus, "p1",
            manuscript=_MIN_TEX,
            annotations_toml=_EMPTY_ANNOTATIONS,
        )
        result = runner.invoke(
            cli,
            [
                "recall",
                "--corpus", str(corpus),
                "--no-record",
                "--format", "json",
            ],
        )
        assert result.exit_code == 0, result.stderr
        # JSON parses; aggregate may be None when there are no
        # annotations to compute against.
        import json
        payload = json.loads(result.stdout)
        assert "per_rule" in payload
