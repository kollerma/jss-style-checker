"""Deterministically adjudicate JSS-XREF-005 firings in eval.db.

XREF-005 (a captioned figure/table must carry a \\label{} and be referenced)
is a purely mechanical check, so it doesn't need an AI labeller with a small
context window. For each firing we re-derive the float's label(s) from the
rule, then grep EVERY tex-like source in the paper for a \\ref-family macro
naming that label:

  * missing-label firing            -> true_positive (numbered float, no label
                                       to reference)
  * label(s), none referenced       -> true_positive (orphan float)
  * some label referenced anywhere  -> false_positive (the AST ref-collection
                                       missed it; e.g. a macro variant)

Sets verdict / verdict_reason / reviewer='algo:xref005'. Idempotent.
"""
from __future__ import annotations

import re
import sqlite3
from pathlib import Path

from eval.scan import _source_files
from texlint.api import ToolConfig
from texlint.core.engine import parse_document
from texlint.journals.jss.rules.crossrefs import check_jss_xref_005

REPO = Path(__file__).resolve().parent.parent
DB = REPO / "eval" / "eval.db"
EXAMPLES = REPO / "examples"

# Broad \ref-family matcher (superset of crossrefs._REF_MACROS, plus the
# cleveref range macros), run as raw text over every source file.
REF_RE = re.compile(
    r"\\(?:ref|eqref|pageref|nameref|autoref|vref|Vref|cref|Cref|cref|"
    r"crefrange|Crefrange|labelcref|subref|Ref)\*?\{([^}]*)\}"
)


def _labels_from_suggestion(s: str):
    """(-> (is_missing, [label_keys]))."""
    if s.startswith("Add \\label"):
        return True, []
    m = re.search(r"label\(s\) '([^']*)'", s)
    keys = [k.strip() for k in m.group(1).split(",")] if m else []
    return False, keys


def _referenced_labels(paper_dir: Path) -> set[str]:
    refs: set[str] = set()
    for f in paper_dir.rglob("*"):
        if not f.is_file() or f.suffix.lower() not in {".tex", ".ltx", ".rnw", ".rmd"}:
            continue
        for m in REF_RE.finditer(f.read_text(errors="ignore")):
            for k in m.group(1).split(","):
                k = k.strip()
                if k:
                    refs.add(k)
    return refs


def main() -> int:
    cx = sqlite3.connect(DB)
    cx.row_factory = sqlite3.Row
    rows = cx.execute(
        "SELECT v.id, v.file, v.line, p.path FROM violations v "
        "JOIN papers p ON p.id = v.paper_id WHERE v.rule_id = 'JSS-XREF-005'"
    ).fetchall()
    by_paper: dict[str, list] = {}
    for r in rows:
        by_paper.setdefault(r["path"], []).append(r)

    tp = fp = 0
    for path, vrows in sorted(by_paper.items()):
        paper_dir = REPO / path
        files = _source_files(paper_dir)
        if not files:
            continue
        doc = parse_document(files)
        # firing map: (basename, line) -> (is_missing, label_keys)
        firing: dict[tuple[str, int], tuple[bool, list]] = {}
        for v in check_jss_xref_005(doc, ToolConfig()):
            firing[(v.file.name, v.line)] = _labels_from_suggestion(v.suggestion)
        referenced = _referenced_labels(paper_dir)

        for r in vrows:
            base = Path(r["file"]).name
            info = firing.get((base, r["line"]))
            if info is None:
                continue  # firing no longer reproduces; leave as-is
            is_missing, keys = info
            if is_missing:
                verdict, reason = "true_positive", "captioned float has no \\label{} (deterministic)"
            elif any(k in referenced for k in keys):
                hit = next(k for k in keys if k in referenced)
                verdict, reason = "false_positive", f"label {hit!r} IS referenced in the sources (deterministic)"
            else:
                verdict, reason = "true_positive", f"label(s) {', '.join(keys)} never referenced in any source (deterministic)"
            cx.execute(
                "UPDATE violations SET verdict=?, verdict_reason=?, reviewer='algo:xref005' WHERE id=?",
                (verdict, reason, r["id"]),
            )
            tp += verdict == "true_positive"
            fp += verdict == "false_positive"
    cx.commit()
    cx.close()
    print(f"XREF-005 adjudicated: TP={tp} FP={fp} (total {tp + fp})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
