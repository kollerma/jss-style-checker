"""Pre-fill recall annotations for deterministic ("green list") structural
rules from the linter, so the annotator only has to *check* them while
reading rather than discover them.

Rationale: these rules sit at ~100% precision corpus-wide — the linter
never over-fires on them — so their firings are trustworthy ground truth.
We do NOT reimplement the rules (a raw-text re-derivation proved buggier
than the linter); we accept the linter's own firings.

Each added entry is tagged `[prefill: <rule>; verify]` in its comment, so
the annotator knows it is machine-proposed and confirms it while reading.
Idempotent and non-destructive: only appends (rule, file, line) tuples
not already present; never edits or removes existing annotations.

    python -m eval.prefill_structural            # dry-run: report per paper/rule
    python -m eval.prefill_structural --write     # append to annotations.toml
"""
from __future__ import annotations

import sys
from pathlib import Path

import tomllib

from texlint.config import load as load_config
from texlint.core.engine import load_journal, parse_document
from texlint.core.engine import run as run_engine
from texlint.journals.jss._catalogue_data import DETERMINISTIC_RULE_IDS

REPO = Path(__file__).resolve().parent.parent
RECALL = REPO / "eval" / "recall-corpus"
LINT_SUFFIXES = {".tex", ".ltx", ".rnw", ".rmd", ".bib"}

# The mechanically-decidable ("deterministic") rules — the linter is
# authoritative, so its firings are trustworthy ground truth to pre-fill.
# Single source of truth: ``deterministic_rule_ids`` in the catalogue
# (also drives eval/review.py's auto-labelling). Formerly a hard-coded
# GREEN_LIST here; unified to avoid two divergent lists.
GREEN_LIST = DETERMINISTIC_RULE_IDS


def _toml_str(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _lint(files):
    cfg = load_config({}, Path.cwd())
    journal = load_journal(cfg.journal)
    report = run_engine(cfg, parse_document(files), journal)
    out = []
    for v in report.violations:
        if v.rule_id in GREEN_LIST:
            out.append((v.rule_id, v.file.name, v.line, (v.suggestion or "").strip()))
    return out


def main(argv):
    write = "--write" in argv
    only = {a for a in argv if not a.startswith("--")}
    papers = sorted(
        p for p in RECALL.iterdir()
        if p.is_dir() and p.name != "__pycache__" and (not only or p.name in only)
    )
    grand = 0
    for d in papers:
        files = sorted(p for p in d.rglob("*") if p.is_file() and p.suffix.lower() in LINT_SUFFIXES)
        if not files:
            continue
        ann_path = d / "annotations.toml"
        doc = tomllib.load(open(ann_path, "rb"))
        have = {(v["rule_id"], v["file"], v["line"]) for v in doc.get("violations", [])}
        firings = _lint(files)
        new = []
        seen = set()
        for rule, fname, line, sugg in firings:
            key = (rule, fname, line)
            if key in have or key in seen:
                continue
            seen.add(key)
            new.append((rule, fname, line, sugg))
        if not new:
            continue
        grand += len(new)
        by_rule = {}
        for rule, *_ in new:
            by_rule[rule] = by_rule.get(rule, 0) + 1
        print(f"{d.name}: +{len(new)}  " + ", ".join(f"{r.split('-',1)[1]}={n}" for r, n in sorted(by_rule.items())))
        if write:
            blocks = []
            for rule, fname, line, sugg in new:
                # Full suggestion (no truncation) so the reviewer sees the
                # whole hint; _toml_str collapses nothing, just escapes.
                comment = f"[prefill: {rule}; verify] {sugg}".strip()
                blocks.append(
                    "\n[[violations]]\n"
                    f"rule_id = {_toml_str(rule)}\n"
                    f"file = {_toml_str(fname)}\n"
                    f"line = {line}\n"
                    f"comment = {_toml_str(comment)}\n"
                )
            with ann_path.open("a", encoding="utf-8") as f:
                f.write("".join(blocks))
    print(f"\n{'WROTE' if write else 'DRY-RUN'} total: {grand} entries across recall papers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
