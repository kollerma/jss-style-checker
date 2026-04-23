# Contract — SQLite Schema

The authoritative DDL lives in `eval/schema.sql` and is loaded verbatim by `db.init()` via `cx.executescript()`. This document is the canonical prose description.

## Connection

Every command opens its connection with:

```python
cx = sqlite3.connect(path, isolation_level=None)  # autocommit; explicit BEGIN/COMMIT
cx.execute("PRAGMA journal_mode=WAL")
cx.execute("PRAGMA foreign_keys=ON")
cx.execute("PRAGMA synchronous=NORMAL")
cx.row_factory = sqlite3.Row
```

`row_factory = sqlite3.Row` gives name-based access (`row["rule_id"]`), which makes the query helpers readable.

## DDL

```sql
CREATE TABLE IF NOT EXISTS papers (
    id     INTEGER PRIMARY KEY AUTOINCREMENT,
    doi    TEXT UNIQUE,
    title  TEXT,
    year   INTEGER,
    path   TEXT NOT NULL,
    source TEXT NOT NULL,                 -- cran | bioc | arxiv | jss_archive | manual
    status TEXT NOT NULL DEFAULT 'pending' -- pending | scanned | scanned_clean | scan_failed
);

CREATE TABLE IF NOT EXISTS runs (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    ts                TEXT    NOT NULL,  -- ISO 8601 UTC (e.g. "2026-04-23T14:30:22Z")
    tool_version      TEXT    NOT NULL,
    papers_scanned    INTEGER NOT NULL,
    violations_found  INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS violations (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    paper_id          INTEGER NOT NULL REFERENCES papers(id) ON DELETE CASCADE,
    rule_id           TEXT    NOT NULL,
    category          TEXT    NOT NULL,
    line              INTEGER,
    column            INTEGER,
    message           TEXT    NOT NULL,
    severity          TEXT    NOT NULL,
    verdict           TEXT,               -- NULL | true_positive | false_positive | uncertain
    verdict_reason    TEXT,
    reviewer          TEXT,               -- "ai:<model>" | "human:<user>" | NULL
    first_seen_run_id INTEGER NOT NULL REFERENCES runs(id),
    UNIQUE(paper_id, rule_id, line, message)
);

CREATE INDEX IF NOT EXISTS idx_viol_rule    ON violations(rule_id);
CREATE INDEX IF NOT EXISTS idx_viol_verdict ON violations(verdict);
CREATE INDEX IF NOT EXISTS idx_viol_paper   ON violations(paper_id);
```

Notes:

1. **`runs` is defined before `violations`** so the `first_seen_run_id REFERENCES runs(id)` constraint resolves cleanly.
2. **`idx_viol_paper`** is not in the `/speckit.plan` input — added because the report's join against `papers` (for the `--by-source` breakdown) and `human-review`'s paper-ordered iteration both benefit. Three indexes total remain within sensible bounds.
3. **No `CHECK` constraint on `verdict`**: the enum contract is enforced in application code. A future `uncertain_but_leaning_false_positive` type would otherwise require a schema migration.
4. **No `CHECK` constraint on `source` or `severity`**: same rationale — SQLite's migration story is awkward and the strings are short, enumerable, and enforced at write time.
5. **`ON DELETE CASCADE` from `papers` to `violations`**: deleting a paper row drops its violations. This is deliberate — a paper removed from the corpus should not leave orphan violation rows that confuse the report. `runs` rows are never cascaded because they are the audit log.

## Dedup contract (spec FR-010 / SC-002)

The `UNIQUE(paper_id, rule_id, line, message)` constraint, combined with `INSERT OR IGNORE INTO violations (...) VALUES (...)`, is the dedup mechanism. Re-running `scan` on an unchanged corpus produces zero new rows; existing `verdict`, `verdict_reason`, and `reviewer` columns are preserved untouched.

The harness never runs a `DELETE` on `violations` as part of normal operation. (The `ON DELETE CASCADE` from `papers` only fires if an operator manually deletes a paper, which is out of spec for the MVP.)

## Timezone contract

All `ts` fields are **ISO 8601 in UTC** with a trailing `Z`:

```
2026-04-23T14:30:22Z
```

Written by:

```python
from datetime import datetime, UTC
ts = datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
```

Never `datetime.now()` without a timezone; never `datetime.utcnow()` (deprecated in 3.12). Never a local-timezone offset. The `Z` form is byte-identical across hosts.

## Schema evolution policy

Additions are free (add a column, add a table, add an index). Renames and removals need a migration story; this spec does not ship any migration machinery because there is nothing to migrate from. When a later spec needs to change an existing column's semantics:

- **Backward-compatible change** (add column, add index): just edit `schema.sql` and rely on `CREATE TABLE IF NOT EXISTS` — an existing DB keeps its old schema, and the query layer should tolerate the missing column. Preferred.
- **Backward-incompatible change**: ship an explicit `ALTER TABLE` migration in a new `eval/migrations/NNNN_<name>.sql` and an `eval-jss migrate` subcommand. Out of scope here.
