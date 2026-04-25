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
    """Return corpus paper directories sorted by name, stable across runs."""
    return sorted(p for p in corpus_dir.iterdir() if p.is_dir())


_SOURCE_SUFFIXES = {".tex", ".ltx", ".bib", ".Rnw", ".Rmd"}

# Subdirectories where CRAN packages keep JSS-paper sources. Order
# matters only for stable traversal — both are walked.
_VIGNETTE_DIRS = ("vignettes", "inst/doc")


def _source_files(paper_dir: Path) -> list[Path]:
    """Return the source files in a paper dir, in a stable order.

    Top-level files win (manual/placeholder corpora). If the paper dir
    has none, fall back to any of `vignettes/` or `inst/doc/`
    subdirectories — CRAN tarballs nest vignettes under
    `<pkg>/vignettes/`, but some JSS-paper packages place their
    canonical paper under `inst/doc/` instead.
    """
    top = sorted(
        p for p in paper_dir.iterdir() if p.is_file() and p.suffix in _SOURCE_SUFFIXES
    )
    if top:
        return top
    nested: list[Path] = []
    for sub in _VIGNETTE_DIRS:
        nested.extend(
            p
            for p in paper_dir.rglob(f"{sub}/*")
            if p.is_file() and p.suffix in _SOURCE_SUFFIXES
        )
    return sorted(nested)


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
    """Insert-or-ignore all `violations` for one paper. Returns count emitted."""
    rows = [
        (
            paper_id,
            v["rule_id"],
            _infer_category(v["rule_id"]),
            v.get("line"),
            v.get("column"),
            v["message"],
            v.get("severity", "error"),
            run_id,
            Path(v["file"]).suffix if v.get("file") else None,
            _relative_file(v.get("file"), paper_dir),
        )
        for v in violations
    ]
    if not rows:
        return 0
    db.executemany_ignore(
        cx,
        "INSERT OR IGNORE INTO violations (paper_id, rule_id, category, line, column,"
        " message, severity, first_seen_run_id, file_suffix, file)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
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
