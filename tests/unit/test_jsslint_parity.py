"""Spec 018 Phase 5 — in-process differential test for the `jsslint`
PyO3 binding (PyPI package `jsslint`, built from `rust/jsslint-py/`):
calls both the real `texlint` Python engine and `jsslint.render` on the
same in-memory file contents (no subprocess, no disk round-trip) and
diffs the JSON output. This is the "in-process parity oracle" the
porting plan calls out as the payoff of the Python binding — every
other Rust-vs-Python differential test in this port
(`rust/*/tests/*_parity.rs`) shells out to the compiled CLI binary
instead.

Skips entirely if `jsslint` isn't installed (built locally via
`maturin develop` in `rust/jsslint-py/`; not part of the default
Python environment).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

jsslint = pytest.importorskip("jsslint")

from texlint.config import load as load_config  # noqa: E402
from texlint.core.engine import load_journal, parse_document, run  # noqa: E402
from texlint.output.json_output import to_payload  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]

# (paper directory, file names, ignore_rules).
PAPERS = [
    ("eval/recall-corpus/opentsne", ["main.tex", "references.bib"], []),
    (
        "eval/recall-corpus/trueskill",
        ["article.tex", "gaming.bib", "journalsAbbr.bib"],
        [],
    ),
]


def _python_oracle_json(paper_dir: Path, files: list[str], ignore_rules: list[str]) -> str:
    paths = [paper_dir / f for f in files]
    sources = {p: p.read_text(encoding="utf-8") for p in paths}
    document = parse_document(paths, sources=sources)
    cli_overrides = {"ignore_rules": ",".join(ignore_rules)} if ignore_rules else {}
    cfg = load_config(cli_overrides, paper_dir)
    journal = load_journal(cfg.journal)
    report = run(cfg, document, journal)
    return json.dumps(to_payload(report), indent=2, sort_keys=True) + "\n"


@pytest.mark.parametrize("paper_dir,files,ignore_rules", PAPERS)
def test_jsslint_matches_python_engine(
    paper_dir: str, files: list[str], ignore_rules: list[str]
) -> None:
    full_paper_dir = REPO_ROOT / paper_dir
    missing = [f for f in files if not (full_paper_dir / f).exists()]
    if missing:
        pytest.skip(
            f"recall corpus not materialized ({paper_dir}: missing {missing}); "
            "run `eval-jss corpus fetch` then "
            "`python -m eval.recall_corpus_scaffold` to fetch it"
        )
    rust_files = [
        (str(full_paper_dir / f), (full_paper_dir / f).read_text(encoding="utf-8"))
        for f in files
    ]

    expected = _python_oracle_json(full_paper_dir, files, ignore_rules)
    actual = jsslint.render(
        rust_files,
        output="json",
        ignore_rules=",".join(ignore_rules) if ignore_rules else None,
    )

    assert actual == expected
