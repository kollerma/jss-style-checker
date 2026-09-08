"""Generate ``specs/003-jss-rule-catalogue/recall.json``.

Invoke from the repository root::

    python -m tools.generate_recall_snapshot --run-timestamp 2026-07-19T10:30:02Z
    python -m tools.generate_recall_snapshot --check    # exit 1 if it drifts

The snapshot pins one `eval-jss recall` run — per-rule true positives
and false negatives — as *data shipped with the rule set*, next to the
catalogue. Everything that reports recall to a user reads it: the
reviewer table's `Recall` column, the author footer, JSON `rule_set`,
SARIF rule properties, `explain`, and the README badge.

Why a checked-in file rather than a query against
``eval/precision-history.db``: recall must be reportable from an
installed wheel, a WASM bundle, and a CRAN binary, none of which ship
the eval database — and the number a release claims must be the number
that release measured, not whatever the database says later.

The measurement itself is a lower bound (source-only linting; see
``eval/recall-corpus/README.md``), and rules with fewer than
``MIN_PLANTS`` annotated instances are reported as ``limited``, never as
a percentage — a rule with two plants at 50 % has not been measured.
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
import tempfile
from collections.abc import Sequence
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
HISTORY_DB = REPO_ROOT / "eval" / "precision-history.db"
RECALL_CORPUS = REPO_ROOT / "eval" / "recall-corpus"
OUTPUT_JSON = REPO_ROOT / "specs" / "003-jss-rule-catalogue" / "recall.json"

#: Annotated instances below which a rule's recall is reported as
#: ``limited (n=K)`` rather than as a percentage. Matches
#: ``eval/recall.py::partition_by_plants``'s default and the paper's.
MIN_PLANTS = 10


def _active_rule_ids() -> set[str]:
    from texlint.journals.jss import _catalogue_data

    return set(_catalogue_data.RULES)


def _paper_count(corpus_dir: Path) -> int:
    """Annotated papers in the recall corpus.

    Counted from the corpus rather than the database, which records no
    paper count: `eval-jss recall` reports "N papers" the same way. The
    footer quotes it because "81 %" means something different over 17
    papers than over 3, and the corpus is gitignored, so the number has
    to be captured when the snapshot is generated.
    """
    return len(sorted(corpus_dir.glob("*/annotations.toml")))


def collect(history_db: Path, run_timestamp: str, papers: int) -> dict:
    """Read one recall run, filtered to rules the catalogue still has.

    A rule retired since the run is dropped: reporting recall for a rule
    that no longer fires would be a claim about nothing.
    """
    connection = sqlite3.connect(history_db)
    try:
        rows = connection.execute(
            "SELECT rule_id, tp, fn, corpus_hash FROM recall_history "
            "WHERE run_timestamp = ? ORDER BY rule_id",
            (run_timestamp,),
        ).fetchall()
    finally:
        connection.close()
    if not rows:
        raise SystemExit(
            f"error: no recall_history rows for run_timestamp {run_timestamp!r}"
        )

    active = _active_rule_ids()
    rules = {
        rule_id: {"tp": tp, "fn": fn}
        for rule_id, tp, fn, _hash in rows
        if rule_id in active
    }
    return {
        "corpus_hash": rows[0][3],
        "generated_by": "tools/generate_recall_snapshot.py",
        "min_plants": MIN_PLANTS,
        "papers": papers,
        "run_timestamp": run_timestamp,
        "rules": rules,
    }


def render(snapshot: dict) -> str:
    return json.dumps(snapshot, indent=2, sort_keys=True) + "\n"


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", delete=False, dir=path.parent, prefix=path.name + "."
    ) as tmp:
        tmp.write(content)
        tmp_name = tmp.name
    os.replace(tmp_name, path)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m tools.generate_recall_snapshot",
        description="Pin one eval-jss recall run as shipped rule-set data.",
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--run-timestamp",
        default=None,
        help=(
            "recall_history.run_timestamp to pin. Defaults to the timestamp "
            "already recorded in the committed snapshot."
        ),
    )
    parser.add_argument("--history-db", type=Path, default=HISTORY_DB)
    parser.add_argument(
        "--corpus-dir",
        type=Path,
        default=RECALL_CORPUS,
        help="Recall corpus root, counted for the snapshot's `papers` field.",
    )
    parser.add_argument(
        "--papers",
        type=int,
        default=None,
        help=(
            "Override the paper count (for --check runs where the "
            "gitignored corpus is not materialised; defaults to the "
            "committed snapshot's value)."
        ),
    )
    parser.add_argument("--output-path", type=Path, default=OUTPUT_JSON)
    args = parser.parse_args(argv)

    run_timestamp = args.run_timestamp
    if run_timestamp is None:
        if not args.output_path.exists():
            print(
                "error: --run-timestamp is required when no snapshot exists yet",
                file=sys.stderr,
            )
            return 2
        run_timestamp = json.loads(args.output_path.read_text(encoding="utf-8"))[
            "run_timestamp"
        ]

    papers = args.papers
    if papers is None:
        papers = _paper_count(args.corpus_dir)
        if papers == 0 and args.output_path.exists():
            # `--check` on a machine without the corpus: keep the
            # committed count rather than reporting zero papers.
            papers = json.loads(args.output_path.read_text(encoding="utf-8")).get(
                "papers", 0
            )
    rendered = render(collect(args.history_db, run_timestamp, papers))

    if args.check:
        if not args.output_path.exists():
            print(
                f"error: {args.output_path} does not exist; run without --check first",
                file=sys.stderr,
            )
            return 1
        if args.output_path.read_text(encoding="utf-8") != rendered:
            print(
                f"error: {args.output_path} is out of date with "
                f"{args.history_db} at run {run_timestamp}. Re-run without --check.",
                file=sys.stderr,
            )
            return 1
        return 0

    _atomic_write(args.output_path, rendered)
    print(f"wrote {args.output_path}")
    return 0


if __name__ == "__main__":  # pragma: no cover — CLI entry point
    raise SystemExit(main())
