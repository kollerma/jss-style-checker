"""Seed recall-corpus ``annotations.toml`` stubs from precision-review verdicts.

The precision corpus (``eval/eval.db``) records, for every linter firing on
a paper, a human/AI verdict (true_positive / false_positive) plus a reason.
Those decisions are a strong head-start for recall annotation:

  * a confirmed **true positive** is a real violation the linter caught, so
    it belongs in the recall ground truth → emitted as a ``[[violations]]``
    entry (the annotator should still VERIFY it and, crucially, add the
    *false negatives* the linter missed — those aren't in eval.db).
  * a reviewed **false positive** is NOT ground truth, so it is recorded
    only as a commented decision log so the annotator doesn't re-add it.

Only violations whose file is actually present in the recall paper directory
are seeded — the precision scan may cover secondary vignettes that the recall
scaffold (one JSS-counterpart manuscript + its bibs/\\input chain) does not
ship; seeding those would manufacture permanent false negatives.

SAFE: a paper's ``annotations.toml`` is only (re)written while it is still a
stub (``annotator = "TODO"`` and no ``[[violations]]``). Hand-annotated files
are never clobbered.

    python -m eval.recall_corpus_seed            # seed the V2 batch
    python -m eval.recall_corpus_seed --check     # report, write nothing
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - py<3.11
    import tomli as tomllib  # type: ignore

REPO_ROOT = Path(__file__).resolve().parent.parent
DB = REPO_ROOT / "eval" / "eval.db"
CORPUS_ROOT = REPO_ROOT / "eval" / "recall-corpus"

# V2 batch: recall paper_id -> (precision-corpus path, header rationale block).
SEED_CONFIG: dict[str, tuple[str, str]] = {
    "opentsne": ("examples/github_opentsne",
        "Goal 1 (non-CRAN language coverage): openTSNE Python manuscript "
        "(JSS v109.i03). Helps cover MARKUP-004 (absent), STRUCT-001/005 (thin)."),
    "romc": ("examples/github_romc",
        "Goal 1 (non-CRAN language coverage): ROMC Python manuscript "
        "(JSS v110.i02). Helps cover OPER-002, CITE-002 (thin), CODE-001."),
    "trueskill": ("examples/github_trueskill",
        "Goal 1 (non-CRAN language coverage): TrueSkillThroughTime manuscript "
        "(Julia + Python, JSS v112.i06). Sole natural source of BIBTEX-005 "
        "(absent); also BIBTEX-002 / CAP-003 (thin)."),
    "HardyWeinberg": ("examples/cran_HardyWeinberg",
        "Goal 2 (rule coverage): rich source of OPER-001 (thin -> measurable)."),
    "CUB": ("examples/cran_CUB",
        "Goal 2 (rule coverage): closes STRUCT-004 (absent) + de-thins PRE-006. "
        "No separate .bib (inline thebibliography), so BIBTEX-* cannot fire."),
    "mlt.docreg": ("examples/cran_mlt.docreg",
        "Goal 2 (rule coverage): closes STRUCT-003 (absent) + de-thins "
        "CAP-003 / BIBTEX-003."),
    "SightabilityModel": ("examples/cran_SightabilityModel",
        "Goal 2 (rule coverage): rich source of CITE-004 (thin -> measurable)."),
}

SEED_DATE = "2026-06-17"

# Rules NOT seeded as ground-truth from review verdicts because they have a
# dedicated, more authoritative annotation source. JSS-REFS-003 (missing DOI)
# is produced by `eval.crossref_doi_lookup`, which records the actual
# Crossref-found DOI — seeding the review's bare firings here would block that
# tool (it skips lines already carrying a REFS-003 annotation).
SEED_EXCLUDE_RULES = frozenset({"JSS-REFS-003"})


def _clean(s: str) -> str:
    """Collapse all whitespace (incl. stray tabs/newlines that some review
    reasons carry — e.g. an AI labeller's JSON mangled ``\\texttt`` into a
    literal tab) to single spaces, so a seeded comment is one tidy line."""
    return " ".join((s or "").split())


def _toml_basic(s: str) -> str:
    """Render ``s`` as a single-line TOML basic string."""
    out = _clean(s).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{out}"'


def _is_safe_to_seed(path: Path) -> bool:
    """True unless a human has annotated the file. We may (re)seed a file
    that is absent or still carries ``annotator = "TODO"`` — that marks it
    as seed-only — but never one a human has put their name on."""
    if not path.exists():
        return True
    with path.open("rb") as f:
        doc = tomllib.load(f)
    return (doc.get("meta") or {}).get("annotator", "TODO") == "TODO"


def _reviewed(cx: sqlite3.Connection, examples_path: str):
    cx.row_factory = sqlite3.Row
    return cx.execute(
        "SELECT v.rule_id, v.file, v.line, v.verdict, v.verdict_reason, v.reviewer "
        "FROM papers p JOIN violations v ON v.paper_id = p.id "
        "WHERE p.path = ? AND v.verdict IS NOT NULL "
        "ORDER BY v.file, v.line, v.rule_id",
        (examples_path,),
    ).fetchall()


def _seed_one(cx, pid: str, examples_path: str, rationale: str, *, write: bool) -> str:
    dest_dir = CORPUS_ROOT / pid
    ann = dest_dir / "annotations.toml"
    if not _is_safe_to_seed(ann):
        return f"  - {pid}: human-annotated — skipped (left untouched)"
    present = {p.name for p in dest_dir.iterdir() if p.name != "annotations.toml"}

    tp: dict[tuple[str, str, int], dict] = {}
    fp: list[dict] = []
    skipped_off_surface = 0
    for r in _reviewed(cx, examples_path):
        base = Path(r["file"]).name if r["file"] else ""
        if base not in present:
            skipped_off_surface += 1
            continue
        if r["verdict"] == "true_positive":
            if r["rule_id"] in SEED_EXCLUDE_RULES:
                continue
            key = (r["rule_id"], base, r["line"])
            cur = tp.get(key)
            reason = (r["verdict_reason"] or "").strip()
            if cur is None:
                tp[key] = {"reasons": {reason} if reason else set(),
                           "reviewers": {r["reviewer"]}}
            else:
                if reason:
                    cur["reasons"].add(reason)
                cur["reviewers"].add(r["reviewer"])
        elif r["verdict"] == "false_positive":
            fp.append(dict(r) | {"base": base})

    lines: list[str] = []
    lines.append(f'# Hand-annotated ground truth for paper "{pid}".')
    lines.append("#")
    lines.append("# Read the rendered manuscript end-to-end and record EVERY")
    lines.append("# JSS-guide violation. Identity tuple is (rule_id, file, line);")
    lines.append("# column does NOT participate. See ../README.md for the protocol.")
    lines.append("#")
    for rl in rationale.split(". "):
        rl = rl.strip()
        if rl:
            lines.append(f"# {rl}{'' if rl.endswith('.') else '.'}")
    lines.append("#")
    lines.append(f"# The [[violations]] below are SEEDED from precision-review")
    lines.append(f"# verdicts (eval.db, {SEED_DATE}): each is a review-confirmed")
    lines.append(f"# TRUE POSITIVE — VERIFY it, and add the false negatives the")
    lines.append(f"# linter missed (those are not in eval.db). Reviewed FALSE")
    lines.append(f"# POSITIVES are listed (commented) at the bottom: do NOT add")
    lines.append(f"# them as violations, but confirm the FP judgement as you read.")
    if SEED_EXCLUDE_RULES:
        excl = ", ".join(sorted(SEED_EXCLUDE_RULES))
        lines.append("#")
        lines.append(f"# {excl} is NOT seeded here — it is populated separately by")
        lines.append(f"# `python -m eval.crossref_doi_lookup` (records the actual DOI).")
    lines.append("")
    lines.append("[meta]")
    lines.append(f'paper_id = "{pid}"')
    lines.append('annotator = "TODO"')
    lines.append('date = "TODO"')
    note = (f"Seeded from precision review on {SEED_DATE}: "
            f"{len(tp)} confirmed-TP entries to verify, {len(fp)} reviewed FPs "
            f"recorded below.")
    if skipped_off_surface:
        note += (f" {skipped_off_surface} review decisions on secondary "
                 f"vignettes outside this recall surface were omitted.")
    lines.append(f"notes = {_toml_basic(note)}")
    lines.append("")

    for (rule_id, base, line), info in sorted(
        tp.items(), key=lambda kv: (kv[0][1], kv[0][2], kv[0][0])
    ):
        reason = "; ".join(sorted(info["reasons"]))
        rev = ", ".join(sorted(info["reviewers"]))
        comment = (f"{reason}  [seeded from review: {rev}]" if reason
                   else f"[seeded from review: {rev}]")
        lines.append("[[violations]]")
        lines.append(f'rule_id = "{rule_id}"')
        lines.append(f'file = "{base}"')
        lines.append(f"line = {line}")
        lines.append(f"comment = {_toml_basic(comment)}")
        lines.append("")

    if fp:
        lines.append("# ---------------------------------------------------------")
        lines.append("# Reviewed FALSE POSITIVES (NOT ground truth — do not add).")
        lines.append("# Recorded so the linter's over-fires here are documented.")
        lines.append("# ---------------------------------------------------------")
        for r in sorted(fp, key=lambda r: (r["base"], r["line"] or 0, r["rule_id"])):
            reason = _clean(r["verdict_reason"] or "")
            lines.append(
                f"#   {r['rule_id']}  {r['base']}:{r['line']}  "
                f"— {reason}  ({r['reviewer']})"
            )

    content = "\n".join(lines).rstrip() + "\n"
    if write:
        ann.write_text(content, encoding="utf-8")
    return (f"  - {pid}: {len(tp)} TP seeded, {len(fp)} FP logged"
            + (f", {skipped_off_surface} off-surface omitted" if skipped_off_surface else ""))


def main(argv: list[str]) -> int:
    write = "--check" not in argv
    if not DB.exists():
        print(f"eval.db not found at {DB}", file=sys.stderr)
        return 2
    cx = sqlite3.connect(DB)
    try:
        print(f"Seeding recall stubs from {DB} ({'WRITE' if write else 'CHECK'}):")
        for pid, (path, rationale) in SEED_CONFIG.items():
            print(_seed_one(cx, pid, path, rationale, write=write))
    finally:
        cx.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
