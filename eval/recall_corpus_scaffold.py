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
import re
import shutil
import sys
from pathlib import Path

# Match `\input{path}`, `\include{path}`, `\subfile{path}`, and the bib-side
# `\bibliography{path}`. Whitespace inside braces is rare but tolerated.
# Multiple bibs separated by commas (`\bibliography{a,b}`) are split below.
_INPUT_RE = re.compile(
    r"\\(?:input|include|subfile|bibliography)\s*\{\s*([^}]+?)\s*\}"
)

# Match `\usepackage[opts]{name}` and `\documentclass[opts]{name}`. Used to
# pull in custom .sty / .cls files that ship next to the manuscript (e.g.
# robustlmm's rlmer.sty, defining macros like \Rp). The scaffolder copies
# them for self-containment so a reviewer can grep them locally; they do
# NOT participate in the lint surface (the recall CLI's file filter
# excludes .sty / .cls — the linter has no parser for style files and
# treats jss.cls as the only authority).
_USEPACKAGE_RE = re.compile(
    r"\\(?:usepackage|documentclass)\s*(?:\[[^\]]*\])?\s*\{\s*([^}]+?)\s*\}"
)

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = REPO_ROOT / "examples"
MANIFEST = REPO_ROOT / "eval" / "corpus-manifest.csv"
CORPUS_ROOT = REPO_ROOT / "eval" / "recall-corpus"

# V1 paper picks (rationale: see eval/recall-corpus/README.md "V1 paper picks").
_PICKS_V1 = (
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

# V2 paper picks (rationale: see eval/recall-corpus/README.md "V2 paper picks").
# Two goals: (1) non-CRAN language coverage — Python/Julia JSS manuscripts
# fetched from GitHub; (2) close absent / thinly-observed rules.
_PICKS_V2 = (
    # Goal 1 — Python / Julia (github source). Also carry goal-2 coverage:
    "opentsne",    # Python; MARKUP-004 (absent), STRUCT-001/005 (thin)
    "romc",        # Python; OPER-002, CITE-002 (thin), CODE-001
    "trueskill",   # Julia (+Python); BIBTEX-005 (absent), BIBTEX-002/CAP-003 (thin)
    # Goal 2 — absent / thin rule sources (cran source):
    "HardyWeinberg",     # OPER-001 (thin -> rich, ~22 firings)
    "CUB",               # STRUCT-004 (absent) + PRE-006 (thin)
    "mlt.docreg",        # STRUCT-003 (absent) + CAP-003/BIBTEX-003 (thin)
    "SightabilityModel", # CITE-004 (thin -> rich, ~14 firings)
)

PICKS = _PICKS_V1 + _PICKS_V2


# Source prefixes stripped from a manifest `local_path` to yield the recall
# paper_id (= directory name). `cran_HardyWeinberg/` -> `HardyWeinberg`,
# `github_opentsne/` -> `opentsne`. Keying on the local_path basename (rather
# than `source_id`) unifies CRAN package names and GitHub `owner/repo` slugs
# into one clean id space that matches the on-disk recall directory names.
_SOURCE_PREFIXES = ("cran_", "github_")


def _paper_id(local_path: str) -> str:
    pid = local_path.rstrip("/")
    for pref in _SOURCE_PREFIXES:
        if pid.startswith(pref):
            return pid[len(pref):]
    return pid


def _manifest_lookup() -> dict[str, tuple[Path, Path]]:
    """paper_id -> (manuscript_path, manuscript_dir) within examples/.

    Covers both `cran` and `github` source rows; both pin a SHA256 and are
    materialised under `examples/` by `eval-jss corpus fetch`, so the recall
    scaffolder copies from the same place regardless of upstream source.
    """
    out: dict[str, tuple[Path, Path]] = {}
    with MANIFEST.open() as f:
        for row in csv.DictReader(f):
            if row["source"] not in ("cran", "github"):
                continue
            local = EXAMPLES / row["local_path"].rstrip("/") / row["vignette_file"]
            out[_paper_id(row["local_path"])] = (local, local.parent)
    return out


def _resolve_input_targets(
    manuscript: Path, src_dir: Path, *, _seen: set[Path] | None = None
) -> list[Path]:
    """Recursively follow ``\\input`` / ``\\include`` / ``\\bibliography``
    chains starting from ``manuscript`` and return every referenced file
    that exists, with paths relative to ``src_dir``-or-deeper preserved.

    LaTeX accepts both ``\\input{foo}`` and ``\\input{foo.tex}``; we try
    the bare path first then ``.tex`` / ``.cls`` / ``.bib`` extensions.
    Also picks up locally-shipped ``\\usepackage{name}`` / ``\\documentclass{name}``
    targets when a matching ``.sty`` / ``.cls`` sits next to the
    manuscript (e.g. robustlmm's rlmer.sty). Such files are reference
    material — they don't participate in the lint surface but make the
    paper directory self-contained.

    Targets we cannot resolve are skipped silently — most are figure /
    listing files outside the lint surface.
    """
    if _seen is None:
        _seen = set()
    out: list[Path] = []
    try:
        text = manuscript.read_text(errors="ignore")
    except OSError:
        return out
    # \input / \include / \subfile / \bibliography
    for m in _INPUT_RE.finditer(text):
        # \bibliography{a,b} → split.
        for raw in m.group(1).split(","):
            target = raw.strip()
            if not target:
                continue
            cmd_is_bib = m.group(0).startswith("\\bibliography")
            extensions = (".bib",) if cmd_is_bib else (".tex", "", ".cls")
            for ext in extensions:
                candidate = (manuscript.parent / f"{target}{ext}").resolve()
                if candidate.exists() and candidate.is_file():
                    if candidate not in _seen:
                        _seen.add(candidate)
                        out.append(candidate)
                        # Recurse only into .tex-class files
                        if candidate.suffix.lower() in {".tex", ".ltx"}:
                            out.extend(
                                _resolve_input_targets(
                                    candidate, src_dir, _seen=_seen
                                )
                            )
                    break
    # \usepackage{name} / \documentclass{name} — only pick up when a
    # local sibling file exists. Skip TeX-distribution-supplied packages
    # silently (we don't want to copy whatever happens to be installed
    # on the scaffolder's machine).
    for m in _USEPACKAGE_RE.finditer(text):
        for raw in m.group(1).split(","):
            target = raw.strip()
            if not target:
                continue
            ext = ".cls" if m.group(0).startswith("\\documentclass") else ".sty"
            candidate = (manuscript.parent / f"{target}{ext}").resolve()
            if candidate.exists() and candidate.is_file() and candidate not in _seen:
                _seen.add(candidate)
                out.append(candidate)
    return out


def _copy_paper(paper_id: str, manuscript: Path, src_dir: Path) -> int:
    """Copy manuscript + its \\input chain + sibling .bib files into the
    paper directory.

    Subdirectory structure is preserved relative to the manuscript so
    that any future ``\\input{./subdir/file}`` autoresolve walks the
    same path. Returns the number of files copied. ``annotations.toml``
    is never touched.
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
    # Sibling .bib files (most papers have these directly next to the
    # manuscript; covered here even when no \bibliography{} explicitly
    # references them).
    for bib in sorted(src_dir.glob("*.bib")):
        shutil.copy2(bib, dest / bib.name)
        n += 1
    # \input / \include / \bibliography chain, preserving subdir layout.
    for target in _resolve_input_targets(manuscript, src_dir):
        rel = target.relative_to(src_dir) if src_dir in target.parents else Path(target.name)
        out_path = dest / rel
        out_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(target, out_path)
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
