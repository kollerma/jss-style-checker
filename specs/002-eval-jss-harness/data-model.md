# Phase 1 Data Model — `eval-jss` Harness

Two data models live side by side: the **SQLite schema** (authoritative at rest) and the **Python dataclasses** the harness uses in memory. The authoritative SQL is in `contracts/schema.md`; this document captures the intent, the invariants, and the Python-layer shapes.

## Python types

All types live in `eval.api` — a small module that other `eval/*.py` files import from to avoid circular imports.

### `Verdict`

```python
from enum import Enum

class Verdict(str, Enum):
    TRUE_POSITIVE  = "true_positive"
    FALSE_POSITIVE = "false_positive"
    UNCERTAIN      = "uncertain"
```

`str` enum so values serialise naturally to SQL text columns and to CSV. The SQL column is `TEXT` and admits `NULL` in addition to the three enum values; a `NULL` verdict is treated as "not yet labelled" everywhere, which is semantically distinct from `uncertain` (the reviewer looked and was unsure) only in the reporting UI — the precision math excludes both.

### `Severity` (re-used)

Imported from `texlint.api` *indirectly*, by parsing the linter's JSON output as text — the harness does **not** depend on `texlint.api` (spec Assumption). We therefore duplicate the enum here:

```python
class Severity(str, Enum):
    ERROR   = "error"
    WARNING = "warning"
```

If a future linter release introduces a new severity, the harness accepts the string and round-trips it through the DB unchanged — SQL column is plain `TEXT`.

### `Paper`

```python
from pathlib import Path
from dataclasses import dataclass

@dataclass(frozen=True)
class Paper:
    id: int | None              # None before first INSERT
    doi: str | None
    title: str | None
    year: int | None
    path: Path                  # directory containing the vignette
    source: str                 # cran | bioc | arxiv | jss_archive | manual
    status: str                 # pending | scanned | scanned_clean | scan_failed
```

**Invariants**:
1. `path` is a directory, not a file. `scan` discovers `.tex` / `.bib` inside it.
2. `doi` is unique when non-`NULL` (enforced by `papers.doi UNIQUE` in SQL). A manual-entry paper that has no DOI must have `doi IS NULL`, not `""`.
3. `source` is one of the five literal strings; the enum is enforced in application code, not in SQL (SQLite doesn't have a native enum type and we don't want a `CHECK` constraint that chokes when a future source is added).
4. `status` transitions: `pending` → `scanned` (violations found) | `scanned_clean` (zero violations) | `scan_failed` (the linter itself errored). Set by `scan`, never reset except by manual DB surgery.

### `Violation`

```python
@dataclass(frozen=True)
class Violation:
    id: int | None
    paper_id: int
    rule_id: str                # e.g. "JSS-CITE-001", "JSS-PARSE-000"
    category: str               # e.g. "citation", "parse"
    line: int | None
    column: int | None
    message: str
    severity: Severity
    verdict: Verdict | None
    verdict_reason: str | None
    reviewer: str | None        # "ai:qwen3-30b-a3b" | "human:kollerma" | None
    first_seen_run_id: int      # FK to runs.id
```

**Invariants**:
1. `(paper_id, rule_id, line, message)` is unique (SQL `UNIQUE` constraint). This is the scan dedup key — see §Dedup contract below.
2. `rule_id == "JSS-PARSE-000"` iff `category == "parse"`. The ingestion step sets both.
3. `line` is `NULL` only for degenerate parse-failure rows that could not localise (fallback is `line = 1`); in practice `line` is always non-`NULL`.
4. `verdict` may be `NULL`; `verdict_reason` and `reviewer` are `NULL` whenever `verdict` is `NULL`, and may be `NULL` even when `verdict` is set (the reviewer chose not to supply a reason). `reviewer` is set whenever `verdict` is set — either `ai:<model>` or `human:<user>`.
5. `first_seen_run_id` is immutable — it records which `runs` row first *inserted* this violation, not every run that observed it.

### `Run`

```python
@dataclass(frozen=True)
class Run:
    id: int | None
    ts: str                     # ISO 8601 UTC, e.g. "2026-04-23T14:30:22Z"
    tool_version: str           # from jss-lint's JSON output
    papers_scanned: int
    violations_found: int
```

**Invariants**:
1. `ts` is always UTC, always ISO 8601 with a `Z` suffix, written via `datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")`. No local timezones — reproducibility requires a deterministic format.
2. `violations_found` is the **total** violations discovered during the scan, not the number newly inserted (dedups-out don't subtract). Matches spec FR-008.
3. `tool_version` is read from the linter's JSON `tool_version` field (spec 001 FR-014). If the JSON is malformed and a `JSS-PARSE-000` synthetic is being recorded in place, `tool_version` is set to `"unknown"`.

### `ManifestRow` (Phase B)

```python
@dataclass(frozen=True)
class ManifestRow:
    jss_doi: str | None
    source: str                 # cran | bioc | arxiv | jss_archive | manual | swh
    source_id: str              # package name, arXiv id, etc.
    version: str                # CRAN cran_version | Bioc release | arXiv "vN" | SWHID | "manual"
    vignette_file: str          # relative to local_path
    local_path: Path            # on-disk location inside examples/
    sha256: str                 # lowercase hex, 64 chars
```

Parsed from `eval/corpus-manifest.csv`; unpopulated for the MVP corpus. Not stored in the DB — the manifest is the source of truth.

### `LinterResult` (internal scan seam)

```python
@dataclass(frozen=True)
class LinterResult:
    exit_code: int
    stdout: str
    stderr: str
    elapsed_seconds: float
```

Purely internal to `eval.scan`. The seam `_invoke_linter(paper_dir, jss_lint) -> LinterResult` is monkeypatched in tests.

## State transitions

### `Paper.status`

```
pending ──scan→ scanned          (violations found)
        ──scan→ scanned_clean    (zero violations)
        ──scan→ scan_failed      (linter itself errored; synthetic JSS-PARSE-000 recorded)

scanned       ──re-scan→ scanned         (INSERT OR IGNORE; no status change)
scanned_clean ──re-scan→ scanned         (new violations appeared — e.g. linter upgrade)
scan_failed   ──re-scan→ scanned_*       (previous failure cleared; fresh row set)
```

No reverse transitions. `scan` sets the terminal status for this run.

### `Violation.verdict`

```
NULL ──human-review→ true_positive | false_positive | uncertain
NULL ──ai-review────→ true_positive | false_positive | uncertain          (FR-016)

uncertain ──human-review→ true_positive | false_positive | uncertain       (overwrite allowed)
true_positive | false_positive ──re-label→ true_positive | false_positive  (overwrite allowed)
```

Every transition sets `verdict_reason` (optional) and `reviewer` (required). The only invariant is that `verdict IS NULL` implies `reviewer IS NULL` and `verdict_reason IS NULL`.

### `Run` — no transitions

A `Run` row is inserted once per `scan` and never updated.

## Dedup contract

The `violations` table carries `UNIQUE(paper_id, rule_id, line, message)`. `scan` uses `INSERT OR IGNORE`. Three specific scenarios:

1. **Same tool version, same corpus, re-run `scan`**: every violation is an exact match on the key; zero new rows; existing verdicts preserved. Spec SC-002.
2. **Linter version bump introduces a new violation on a previously-unseen line**: inserted as a new row; its `first_seen_run_id` points at the new run. Previously-labelled violations on the same paper are untouched.
3. **Linter version bump rewords an existing message**: the reworded message is a **new** row (the dedup key changed), and the old row is orphaned (still in the DB, still labelled, but no longer present in any fresh scan). This is accepted — message-wording changes are rare, and re-labelling the new version is the correct response. The old row is never auto-deleted.

## SQLite schema overview

(Full DDL in `contracts/schema.md`.) Three tables plus two indexes:

```
papers         (id, doi, title, year, path, source, status)
violations     (id, paper_id, rule_id, category, line, column, message, severity,
                verdict, verdict_reason, reviewer, first_seen_run_id)
runs           (id, ts, tool_version, papers_scanned, violations_found)

idx_viol_rule     ON violations(rule_id)
idx_viol_verdict  ON violations(verdict)
```

Relationships: `violations.paper_id REFERENCES papers(id) ON DELETE CASCADE`; `violations.first_seen_run_id REFERENCES runs(id)` (no cascade — `runs` is an audit log and should never be deleted).

**Added column vs. spec**: `violations.category` is present. The spec did not name it explicitly, but the report's per-category grouping requires it and the linter's JSON already carries category per rule. Carrying it on the violation row avoids a join back to a rule-catalogue table the harness doesn't own. See research.md §"Category attribution for violations".
