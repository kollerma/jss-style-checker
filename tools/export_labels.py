"""Export committed, auditable label artifacts from the eval database.

Invoke from the repository root::

    python -m tools.export_labels          # write the artifacts
    python -m tools.export_labels --check   # exit 1 if any artifact drifts

The eval database (``eval/eval.db``) is gitignored, so the headline
precision number in the paper is not independently auditable from the
repository alone (review finding F4). This tool materialises the label
evidence into *committed* gzip-CSV artifacts a referee can inspect and
recompute from:

* ``eval/labels-export.csv.gz`` — one row per **live** labelled
  violation (the tool still emits it in the latest run, verdict is
  ``true_positive`` / ``false_positive``). This is the population the
  paper's provenance macros count over.

* ``eval/gold-set-export.csv.gz`` — the 1,410-row model-scope gold set
  the labeler benchmark scored (2026-07-07 snapshot), with the human
  gold verdict and each model's verdict, so the agreement and
  TP-error numbers are recomputable from committed files.

The reviewer routing table (``eval/review-routing.toml``) is already
committed; this tool only verifies its presence.

Reviewer-class mapping (finding F1 — label provenance)
------------------------------------------------------
The ``reviewer`` column carries fine-grained provenance tags. For the
paper we collapse them into four classes. The mapping is derived from
the actual reviewer values in the DB (``SELECT reviewer, COUNT(*) ...
GROUP BY reviewer``) and reproduces the review's cited figures
(AI-issued share 88.5%; human-only precision 94.1%):

* ``ai_model`` — any tag whose underlying reviewer starts with ``ai:``
  (including the ``line-shifted:``/``migrated:`` provenance-transform
  prefixes). These are labels issued by an AI classifier (Bonsai-8B,
  Qwen3-30B, and a small Claude consistency pass).
* ``human`` — a bare ``human:`` tag that is NOT ``human:auto-*``
  (``human:unknown`` = independent human review; ``human:claude-proxy``
  = human-adjudicated via proxy). This is the decontaminated human tag
  the benchmark treats as ground truth's namespace; per the 2026-07-06
  decontamination (``eval/labeler-benchmark-summary.md``) every
  AI-generated adjudication was re-namespaced OUT of the bare
  ``human:`` space into ``human:auto-*``.
* ``auto_deterministic`` — labels the linter/algorithmic verifiers
  assign for mechanically-decidable rules (``algo:*`` and, if present,
  ``human:auto-deterministic``).
* ``auto_other`` — other automated adjudication workflows in the
  ``human:auto-*`` namespace (auto-correction, auto-fix-iter, opus
  subagent re-adjudication, xref verify passes). These are automated
  but not attributable to one benchmarked model.

For the three-way paper split we report ``ai_model`` as AI,
``human`` as human, and ``auto_deterministic`` + ``auto_other`` as
auto. ``auto_other`` is a small, mostly-AI-adjacent bucket; keeping it
distinct in the CSV lets a referee re-slice it either way.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import io
import json
import sqlite3
import sys
from collections.abc import Sequence
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EVAL_DB = REPO_ROOT / "eval" / "eval.db"
LABELS_OUT = REPO_ROOT / "eval" / "labels-export.csv.gz"
GOLD_OUT = REPO_ROOT / "eval" / "gold-set-export.csv.gz"
ROUTING_TABLE = REPO_ROOT / "eval" / "review-routing.toml"
GOLD_QWEN_JSONL = REPO_ROOT / "eval" / "benchmark-runs" / "20260707-qwen3-gold1410.jsonl"
GOLD_BONSAI_JSONL = REPO_ROOT / "eval" / "benchmark-runs" / "20260707-bonsai-gold1410.jsonl"

_LIVE_LABELS_SQL = """
    SELECT p.path            AS paper,
           v.file            AS file,
           v.rule_id         AS rule_id,
           v.line            AS line,
           v.verdict         AS verdict,
           v.reviewer        AS reviewer,
           v.verdict_reason  AS verdict_reason
      FROM violations v JOIN papers p ON p.id = v.paper_id
     WHERE v.rule_id != 'JSS-PARSE-000'
       -- "live" == the tool still emits it in the latest run (or the
       -- staleness column predates the migration); same filter the
       -- precision report uses (eval/report.py).
       AND (v.last_seen_run_id = (SELECT MAX(id) FROM runs)
            OR v.last_seen_run_id IS NULL)
       AND v.verdict IN ('true_positive', 'false_positive')
"""


def reviewer_class(reviewer: str | None) -> str:
    """Collapse a raw reviewer tag into {human, ai_model,
    auto_deterministic, auto_other}. See module docstring for the
    rationale and the figures this reproduces."""
    r = reviewer or ""
    # Strip provenance-transform prefixes so the underlying labeller
    # decides the class (a line-shifted AI label is still an AI label).
    for prefix in ("line-shifted:", "migrated:"):
        if r.startswith(prefix):
            r = r[len(prefix):]
    if r.startswith("ai:"):
        return "ai_model"
    if r.startswith("algo:") or r == "human:auto-deterministic":
        return "auto_deterministic"
    if r.startswith("human:auto-"):
        return "auto_other"
    if r.startswith("human:"):
        return "human"
    return "auto_other"


def _rows_to_csv_gz(header: Sequence[str], rows: Sequence[Sequence[object]]) -> bytes:
    """Serialise rows to a byte-stable gzip-CSV blob (mtime pinned to 0,
    LF line endings, fixed compression level)."""
    text = io.StringIO()
    writer = csv.writer(text, lineterminator="\n")
    writer.writerow(header)
    writer.writerows(rows)
    raw = text.getvalue().encode("utf-8")
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", compresslevel=9, mtime=0) as gz:
        gz.write(raw)
    return buf.getvalue()


def build_labels_export(db_path: Path) -> bytes:
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    try:
        rows = con.execute(_LIVE_LABELS_SQL).fetchall()
    finally:
        con.close()
    out = [
        (
            r["paper"],
            r["file"],
            r["rule_id"],
            r["line"] if r["line"] is not None else "",
            r["verdict"],
            reviewer_class(r["reviewer"]),
            (r["verdict_reason"] or "").replace("\r\n", " ").replace("\n", " ").strip(),
        )
        for r in rows
    ]
    # Deterministic ordering so regeneration is byte-stable.
    out.sort(key=lambda t: (t[0], t[1], t[2], _line_key(t[3]), t[4], t[5], t[6]))
    header = (
        "paper",
        "file",
        "rule_id",
        "line",
        "verdict",
        "reviewer_class",
        "verdict_reason",
    )
    return _rows_to_csv_gz(header, out)


def _line_key(line: object) -> tuple[int, int]:
    """Sort key that keeps blank lines last, numeric lines in order."""
    if line == "" or line is None:
        return (1, 0)
    return (0, int(line))


def _load_outcomes(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))["outcomes"]


def build_gold_export() -> bytes:
    qwen = _load_outcomes(GOLD_QWEN_JSONL)
    bonsai = _load_outcomes(GOLD_BONSAI_JSONL)
    if len(qwen) != len(bonsai):
        raise SystemExit(
            f"gold jsonl row-count mismatch: qwen={len(qwen)} bonsai={len(bonsai)}"
        )
    rows = []
    for i, (q, b) in enumerate(zip(qwen, bonsai, strict=True)):
        if q["rule_id"] != b["rule_id"] or q["human"] != b["human"]:
            raise SystemExit(
                f"gold jsonl rows diverge at index {i}: "
                f"{q['rule_id']}/{q['human']} vs {b['rule_id']}/{b['human']}"
            )
        # The human column is the decontaminated human:unknown gold
        # verdict; both models were scored on the SAME 1,410 rows.
        rows.append((i, q["rule_id"], q["human"], q["model"], b["model"]))
    header = ("row", "rule_id", "verdict", "qwen3_verdict", "bonsai_verdict")
    return _rows_to_csv_gz(header, rows)


def _write_or_check(path: Path, blob: bytes, *, check: bool) -> int:
    if check:
        if not path.exists():
            print(
                f"error: {path} does not exist; run without --check first",
                file=sys.stderr,
            )
            return 1
        if path.read_bytes() != blob:
            print(
                f"error: {path} is out of date. Re-run without --check.",
                file=sys.stderr,
            )
            return 1
        return 0
    path.write_bytes(blob)
    print(f"wrote {path} ({len(blob)} bytes)")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m tools.export_labels",
        description="Export committed, auditable label artifacts from eval.db.",
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--db-path", type=Path, default=EVAL_DB)
    args = parser.parse_args(argv)

    if not ROUTING_TABLE.exists():
        print(f"error: routing table {ROUTING_TABLE} is missing", file=sys.stderr)
        return 1

    if not args.db_path.exists():
        print(f"error: {args.db_path} does not exist", file=sys.stderr)
        return 2

    rc = 0
    rc |= _write_or_check(
        LABELS_OUT, build_labels_export(args.db_path), check=args.check
    )
    rc |= _write_or_check(GOLD_OUT, build_gold_export(), check=args.check)
    return rc


if __name__ == "__main__":  # pragma: no cover — CLI entry point
    raise SystemExit(main())
