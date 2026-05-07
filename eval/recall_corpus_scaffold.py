"""Repopulate ``eval/recall-corpus/<paper>/`` manuscripts + bibs from the
precision corpus.

Annotations (``annotations.toml``) are committed. Manuscripts and
``.bib`` files are gitignored — they're CRAN-vendored vignettes whose
upstream licenses (typically GPL-2/3) are incompatible with bundling
into this MIT repo. This script copies them in from the local
precision corpus (``examples/cran_<package>/``), so any reviewer or CI
job can rebuild a working recall corpus by running:

    python -m eval.recall_corpus_scaffold

Idempotent: re-running overwrites manuscript / bib files but leaves
``annotations.toml`` untouched.
"""
from __future__ import annotations

import csv
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = REPO_ROOT / "examples"
MANIFEST = REPO_ROOT / "eval" / "corpus-manifest.csv"
CORPUS_ROOT = REPO_ROOT / "eval" / "recall-corpus"

# V1 paper picks (rationale: see eval/recall-corpus/README.md "V1 paper picks").
PICKS = (
    "robustlmm",
    "CARBayesST",
    "mdsOpt",
    "DBR",
    "pmclust",
    "cusp",
    "spacetime",
    "deSolve",
    "rstpm2",
    "clifford",
)


def _manifest_lookup() -> dict[str, tuple[Path, Path]]:
    """source_id -> (manuscript_path, manuscript_dir) within examples/."""
    out: dict[str, tuple[Path, Path]] = {}
    with MANIFEST.open() as f:
        for row in csv.DictReader(f):
            if row["source"] != "cran":
                continue
            local = EXAMPLES / row["local_path"].rstrip("/") / row["vignette_file"]
            out[row["source_id"]] = (local, local.parent)
    return out


def _copy_paper(paper_id: str, manuscript: Path, src_dir: Path) -> int:
    """Copy manuscript + sibling .bib into the paper directory.

    Returns the number of files copied. The annotations.toml file is
    never touched (it carries the hand-annotation work).
    """
    if not manuscript.exists():
        print(
            f"  ! {paper_id}: missing precision-corpus source at {manuscript} — "
            f"run `eval-jss corpus fetch` first",
            file=sys.stderr,
        )
        return 0
    dest = CORPUS_ROOT / paper_id
    dest.mkdir(parents=True, exist_ok=True)
    n = 0
    shutil.copy2(manuscript, dest / manuscript.name)
    n += 1
    for bib in sorted(src_dir.glob("*.bib")):
        shutil.copy2(bib, dest / bib.name)
        n += 1
    return n


def main() -> int:
    lookup = _manifest_lookup()
    missing = [p for p in PICKS if p not in lookup]
    if missing:
        print(
            f"manifest is missing entries for: {missing}; aborting",
            file=sys.stderr,
        )
        return 2
    total = 0
    for pid in PICKS:
        manuscript, src_dir = lookup[pid]
        n = _copy_paper(pid, manuscript, src_dir)
        if n:
            print(f"  ✓ {pid:<14} → {manuscript.name} (+ {n - 1} bib file(s))")
            total += n
    print(f"\ncopied {total} files across {len(PICKS)} paper directories")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
