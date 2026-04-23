"""Shared fixtures for `tests/eval/`.

- `tmp_db` — a freshly initialised SQLite database under `tmp_path`.
- `fake_corpus` — three placeholder vignettes under `tmp_path/examples`
  with known expected violations, for driving scan tests.
- `fake_client` — a `ReviewClient` test double with per-rule-id canned
  verdicts (added when US2 / `eval.review` lands).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pytest

from eval import db


@dataclass
class FakeCorpus:
    root: Path
    papers: list[Path] = field(default_factory=list)
    # Per-paper expected violations, keyed by paper directory name.
    # Each violation is a dict matching the linter's JSON output shape.
    expected_violations: dict[str, list[dict]] = field(default_factory=dict)


@pytest.fixture
def tmp_db(tmp_path: Path) -> Path:
    """Return a path to a freshly initialised SQLite database."""
    path = tmp_path / "eval.db"
    db.init(path)
    return path


@pytest.fixture
def fake_corpus(tmp_path: Path) -> FakeCorpus:
    """Create three papers under `tmp_path/examples/` with known fixtures.

    Each paper has a `.tex` and a `.bib`; the linter output is driven by
    monkeypatching `eval.scan._invoke_linter` — the file contents are
    placeholders, not real JSS vignettes.
    """
    root = tmp_path / "examples"
    root.mkdir()
    fake = FakeCorpus(root=root)

    papers = [
        ("paper_clean", []),
        (
            "paper_violations",
            [
                {
                    "file": "article.tex",
                    "line": 3,
                    "column": 5,
                    "rule_id": "JSS-CITE-001",
                    "severity": "warning",
                    "message": "Looks like a citation key; use \\cite{...}.",
                    "suggestion": None,
                    "fix": None,
                },
                {
                    "file": "article.tex",
                    "line": 42,
                    "column": None,
                    "rule_id": "JSS-SRC-001",
                    "severity": "warning",
                    "message": "Line exceeds 80 characters.",
                    "suggestion": None,
                    "fix": None,
                },
            ],
        ),
        (
            "paper_parse_fail",
            [
                {
                    "file": "article.tex",
                    "line": 1,
                    "column": None,
                    "rule_id": "JSS-PARSE-000",
                    "severity": "error",
                    "message": "Parse error: unbalanced braces.",
                    "suggestion": None,
                    "fix": None,
                },
            ],
        ),
    ]

    for name, violations in papers:
        paper_dir = root / name
        paper_dir.mkdir()
        (paper_dir / "article.tex").write_text(
            "\\documentclass{jss}\n\\begin{document}\nplaceholder\n\\end{document}\n",
            encoding="utf-8",
        )
        (paper_dir / "refs.bib").write_text(
            "@article{smith2020, title = {Example}, year = {2020}}\n",
            encoding="utf-8",
        )
        (paper_dir / "README.md").write_text(f"Placeholder vignette `{name}`.\n", encoding="utf-8")
        fake.papers.append(paper_dir)
        fake.expected_violations[name] = violations

    return fake
