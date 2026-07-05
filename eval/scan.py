"""Run `jss-lint` over a corpus and persist the results.

Contract:
- One `subprocess.run` invocation per paper directory (spec FR-009).
- `INSERT OR IGNORE` via the `UNIQUE(paper_id, rule_id, line, message)`
  constraint is the dedup mechanism (spec FR-010).
- Parse failures flow through as `JSS-PARSE-000` violations (FR-011).
- A single `runs` audit row per invocation (FR-012).

The `_invoke_linter` function is the one seam tests monkeypatch — do not
reach deeper to `subprocess.run` globally.

**Category inference**: the linter's JSON output does not carry a
`category` field per violation (only at the top-level `categories`
block, and that doesn't expose rule-to-category membership). Until the
linter grows a per-violation `category` field, we infer category from a
rule-id prefix: `JSS-CITE-*` → citation, `JSS-BIB-*` → bibliography,
`JSS-SRC-*` → typography, `JSS-PARSE-*` → parse. Anything else falls
back to `unknown`. A later spec that extends the linter's JSON will
replace this inference with the real field.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import time
from pathlib import Path

from eval import api, db

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

_CATEGORY_BY_PREFIX = {
    "CITE": "citation",
    "BIB": "bibliography",
    "SRC": "typography",
    "PARSE": "parse",
}


def _infer_category(rule_id: str) -> str:
    """Map a rule id like `JSS-CITE-001` to a category like `citation`.

    Falls back to `"unknown"` when the prefix is not recognised. The set
    of known prefixes grows as Step 3 adds rules; update this map when
    the first `JSS-<NEW>-001` lands, or replace this helper entirely
    once the linter's JSON carries category per violation.
    """
    parts = rule_id.split("-")
    if len(parts) >= 2:
        return _CATEGORY_BY_PREFIX.get(parts[1], "unknown")
    return "unknown"


def _discover_papers(corpus_dir: Path) -> list[Path]:
    """Return corpus paper directories sorted by name, stable across runs.

    A subdirectory with no lintable source file anywhere the scanner looks
    (top level, then ``vignettes/`` / ``inst/doc/`` — see `_source_files`)
    is not a paper and is skipped. Otherwise the scanner would shell out to
    ``jss-lint`` with zero file arguments and record a spurious
    ``JSS-PARSE-000`` / ``scan_failed`` row — e.g. the ``jss5342-versions``
    recall-study directory, whose manuscripts live in per-version subdirs
    (``initial/``, ``resubmission/``, …) rather than under ``vignettes/``.
    """
    return sorted(
        p for p in corpus_dir.iterdir() if p.is_dir() and _source_files(p)
    )


_SOURCE_SUFFIXES = {".tex", ".ltx", ".bib", ".Rnw", ".Rmd"}

# Subdirectories where CRAN packages keep JSS-paper sources, in
# preference order. `vignettes/` is the canonical source location;
# `R CMD build` then COPIES those files into `inst/doc/` for the
# installed package. Walking both produces near-duplicates, so we
# only fall back to `inst/doc/` when `vignettes/` is empty.
_VIGNETTE_DIRS = ("vignettes", "inst/doc")


def _source_files(paper_dir: Path) -> list[Path]:
    """Return the source files in a paper dir, in a stable order.

    Top-level files win (manual/placeholder corpora). If the paper dir
    has none, walk `vignettes/`. Only fall back to `inst/doc/` when
    `vignettes/` yielded nothing — `inst/doc/` typically contains a
    build-time copy of the same vignettes plus their compiled outputs,
    so scanning both manufactures duplicate violations.

    Last fallback: *versioned* papers laid out as
    ``<paper>/<revision>/*.tex`` (e.g. ``jss5342-versions/{initial,
    resubmission,final}``). A ``final/`` revision wins outright when it
    has sources — every revision is a draft of the SAME manuscript, so
    scanning all of them would manufacture the duplicate-violation
    problem described above. Without a ``final/``, all non-hidden,
    non-underscore subdirectories are gathered (underscore dirs such as
    ``_analysis/`` hold tooling artifacts, not manuscript sources).
    Within a revision, the conventions documented in
    ``jss5342-versions/_analysis/analyze.py`` apply: the rendered
    ``.tex`` wins over a same-stem ``.Rnw`` (the .tex is the surface a
    JSS reviewer reads; linting both double-counts), and
    ``reviewer-comments*`` files are correspondence, not manuscript.
    """
    top = sorted(
        p for p in paper_dir.iterdir() if p.is_file() and p.suffix in _SOURCE_SUFFIXES
    )
    if top:
        return top
    for sub in _VIGNETTE_DIRS:
        nested = sorted(
            p
            for p in paper_dir.rglob(f"{sub}/*")
            if p.is_file() and p.suffix in _SOURCE_SUFFIXES
        )
        if nested:
            return nested
    final = _revision_files(paper_dir / "final")
    if final:
        return final
    return sorted(
        p
        for sub in sorted(paper_dir.iterdir())
        if sub.is_dir() and not sub.name.startswith((".", "_"))
        for p in _revision_files(sub)
    )


def _revision_files(revision_dir: Path) -> list[Path]:
    """Lintable files of one manuscript revision: skip correspondence
    (``reviewer-comments*``) and prefer the rendered ``.tex`` over a
    same-stem ``.Rnw`` (see ``_source_files`` docstring)."""
    if not revision_dir.is_dir():
        return []
    files = [
        p
        for p in revision_dir.iterdir()
        if p.is_file()
        and p.suffix in _SOURCE_SUFFIXES
        and not p.name.startswith("reviewer-comments")
    ]
    tex_stems = {p.stem for p in files if p.suffix == ".tex"}
    return sorted(
        p for p in files if not (p.suffix == ".Rnw" and p.stem in tex_stems)
    )


_DOCUMENTCLASS_RE = re.compile(
    r"^\s*\\documentclass(?:\[[^\]]*\])?\{([^}]+)\}"
)


def _detect_doc_class(paper_dir: Path) -> str:
    """Classify a paper as ``jss`` / ``non-jss`` / ``unknown`` by its
    document class.

    The corpus is meant to be JSS-paper counterparts, but ~10% of CRAN
    vignettes ship in ``\\documentclass{article}`` (or amsart/scrartcl)
    because CRAN can't always build ``jss.cls`` — even though the paper
    itself is a JSS publication. The report uses this dimension to show
    jss-class precision as the headline and non-jss-class as a
    robustness check, so the two aren't silently conflated.

    Detection: the first *uncommented* ``\\documentclass`` in any
    ``.tex`` / ``.Rnw`` / ``.ltx`` source decides it (``jss`` vs
    anything else). An ``.Rmd``-only paper is ``jss`` (corpus Rmds use
    the rmarkdown JSS template). No class found and no Rmd → ``unknown``
    (multi-file inputs whose class lives in an unscanned wrapper)."""
    files = _source_files(paper_dir)
    has_rmd = any(f.suffix.lower() == ".rmd" for f in files)
    for f in files:
        if f.suffix.lower() not in {".tex", ".rnw", ".ltx"}:
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for line in text.splitlines():
            if line.lstrip().startswith("%"):
                continue
            m = _DOCUMENTCLASS_RE.match(line)
            if m:
                return "jss" if m.group(1).strip() == "jss" else "non-jss"
    return "jss" if has_rmd else "unknown"


def _invoke_linter(paper_dir: Path, jss_lint: str) -> api.LinterResult:
    """Shell out to `jss-lint --output json`. This is the tested seam."""
    files = _source_files(paper_dir)
    t0 = time.perf_counter()
    proc = subprocess.run(
        [jss_lint, "--output", "json", "--", *(str(p) for p in files)],
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )
    elapsed = time.perf_counter() - t0
    return api.LinterResult(
        exit_code=proc.returncode,
        stdout=proc.stdout,
        stderr=proc.stderr,
        elapsed_seconds=elapsed,
    )


# -----------------------------------------------------------------------------
# Scan
# -----------------------------------------------------------------------------


def _ensure_paper(cx, paper_dir: Path) -> int:
    """Insert a new `papers` row if this dir is new; return its id either way."""
    row = cx.execute(
        "SELECT id FROM papers WHERE path = ?", (str(paper_dir),)
    ).fetchone()
    if row is not None:
        return int(row["id"])
    cx.execute(
        "INSERT INTO papers (path, source, status) VALUES (?, ?, 'pending')",
        (str(paper_dir), "manual"),
    )
    return int(cx.execute("SELECT last_insert_rowid()").fetchone()[0])


def _relative_file(raw: str | None, paper_dir: Path) -> str | None:
    """Return `raw` as a POSIX path relative to `paper_dir` when it lives
    beneath that directory; otherwise return the original string (or None).

    The eval harness pins one `vignette_file` per paper but the scanner
    walks every `vignettes/*` file for the paper. Storing a paper-relative
    path — matching the format in `corpus-manifest.csv::vignette_file`
    (e.g. `dplyr/vignettes/rowwise.Rmd`) — lets downstream slicing align
    the two without string munging.
    """
    if not raw:
        return None
    p = Path(raw)
    try:
        return p.resolve().relative_to(paper_dir.resolve()).as_posix()
    except ValueError:
        return p.as_posix()


def _persist_violations(
    cx,
    paper_id: int,
    paper_dir: Path,
    run_id: int,
    violations: list[dict],
) -> int:
    """Upsert all `violations` for one paper. New rows insert with
    first_seen = last_seen = run_id; rows that re-fire bump
    last_seen_run_id (verdict / reviewer are preserved). The report
    scopes precision to the latest run via last_seen_run_id, so a
    violation the tool no longer emits drops out instead of counting
    against precision forever. Returns count emitted."""
    rows = [
        (
            paper_id,
            v["rule_id"],
            _infer_category(v["rule_id"]),
            v.get("line"),
            v.get("column"),
            v["message"],
            v.get("severity", "error"),
            run_id,            # first_seen_run_id
            run_id,            # last_seen_run_id
            Path(v["file"]).suffix if v.get("file") else None,
            _relative_file(v.get("file"), paper_dir),
        )
        for v in violations
    ]
    if not rows:
        return 0
    cx.executemany(
        "INSERT INTO violations (paper_id, rule_id, category, line, column,"
        " message, severity, first_seen_run_id, last_seen_run_id, file_suffix, file)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        " ON CONFLICT(paper_id, rule_id, line, message, file)"
        " DO UPDATE SET last_seen_run_id = excluded.last_seen_run_id",
        rows,
    )
    return len(violations)


def _synthetic_parse_failure(message: str) -> list[dict]:
    """One `JSS-PARSE-000` violation covering a linter-level failure."""
    return [
        {
            "rule_id": "JSS-PARSE-000",
            "line": 1,
            "column": None,
            "message": message,
            "severity": "error",
        }
    ]


def _handle_one_paper(
    cx,
    paper_dir: Path,
    jss_lint: str,
    run_id: int,
) -> tuple[int, str, str]:
    """Scan one paper, persist its violations, return (count, status, tool_version)."""
    paper_id = _ensure_paper(cx, paper_dir)
    cx.execute(
        "UPDATE papers SET doc_class=? WHERE id=?",
        (_detect_doc_class(paper_dir), paper_id),
    )
    result = _invoke_linter(paper_dir, jss_lint)

    try:
        payload = json.loads(result.stdout) if result.stdout.strip() else {}
    except json.JSONDecodeError:
        payload = {}

    if not payload or not isinstance(payload, dict):
        msg = (
            f"jss-lint did not return JSON (exit {result.exit_code}): "
            f"{(result.stderr or result.stdout)[:200]}"
        )
        violations = _synthetic_parse_failure(msg)
        count = _persist_violations(cx, paper_id, paper_dir, run_id, violations)
        cx.execute("UPDATE papers SET status='scan_failed' WHERE id=?", (paper_id,))
        return count, "scan_failed", "unknown"

    tool_version = payload.get("tool_version", "unknown")
    violations = payload.get("violations", []) or []
    count = _persist_violations(cx, paper_id, paper_dir, run_id, violations)

    if result.exit_code == 2:
        # The linter reports exit 2 on invocation-level failure (e.g. missing
        # file). Any JSON the linter emitted is still ingested above; we
        # additionally mark the paper as scan-failed so reviewers see it.
        status = "scan_failed"
    elif violations:
        status = "scanned"
    else:
        status = "scanned_clean"
    cx.execute("UPDATE papers SET status=? WHERE id=?", (status, paper_id,))
    return count, status, tool_version


# -----------------------------------------------------------------------------
# Public entry point
# -----------------------------------------------------------------------------


def run(
    *,
    db_path: Path,
    corpus_dir: Path,
    batch_size: int | None,
    force: bool,
) -> int:
    """Scan `corpus_dir` and persist violations. Returns CLI exit code."""
    jss_lint = shutil.which("jss-lint")
    if not jss_lint:
        print(
            "eval-jss: `jss-lint` not found on PATH — is the package installed?",
            flush=True,
        )
        return 2

    if not corpus_dir.exists() or not corpus_dir.is_dir():
        print(f"eval-jss: corpus directory not readable: {corpus_dir}", flush=True)
        return 2

    paper_dirs = _discover_papers(corpus_dir)

    cx = db.connect(db_path)
    try:
        # Seed the audit row early so per-paper violations can reference its id.
        cx.execute(
            "INSERT INTO runs (ts, tool_version, papers_scanned, violations_found)"
            " VALUES (?, 'unknown', 0, 0)",
            (db.now_utc(),),
        )
        run_id = int(cx.execute("SELECT last_insert_rowid()").fetchone()[0])

        # Filter out already-scanned papers unless --force.
        if not force:
            scanned_paths = {
                r["path"]
                for r in cx.execute(
                    "SELECT path FROM papers WHERE status IN"
                    " ('scanned', 'scanned_clean')"
                ).fetchall()
            }
            paper_dirs = [p for p in paper_dirs if str(p) not in scanned_paths]

        if batch_size is not None:
            paper_dirs = paper_dirs[:batch_size]

        total_violations = 0
        any_parse_failure = False
        tool_version_observed = "unknown"
        papers_scanned = 0

        for paper_dir in paper_dirs:
            count, status, tool_version = _handle_one_paper(
                cx, paper_dir, jss_lint, run_id
            )
            total_violations += count
            papers_scanned += 1
            if status == "scan_failed":
                any_parse_failure = True
            if tool_version != "unknown":
                tool_version_observed = tool_version

        cx.execute(
            "UPDATE runs SET tool_version=?, papers_scanned=?, violations_found=?"
            " WHERE id=?",
            (tool_version_observed, papers_scanned, total_violations, run_id),
        )
    finally:
        cx.close()

    if total_violations > 0 or any_parse_failure:
        return 1
    return 0
