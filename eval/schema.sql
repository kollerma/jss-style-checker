-- eval-jss SQLite schema. Loaded via `cx.executescript()` by `eval.db.init()`.
-- Authoritative prose description: specs/002-eval-jss-harness/contracts/schema.md
--
-- All statements are idempotent (`CREATE TABLE IF NOT EXISTS`,
-- `CREATE INDEX IF NOT EXISTS`) so `eval-jss init` is safe to re-run.
-- `runs` is defined before `violations` so the FK resolves cleanly.

CREATE TABLE IF NOT EXISTS papers (
    id     INTEGER PRIMARY KEY AUTOINCREMENT,
    doi    TEXT UNIQUE,
    title  TEXT,
    year   INTEGER,
    path   TEXT NOT NULL,
    source TEXT NOT NULL,                   -- cran | bioc | arxiv | jss_archive | manual
    status TEXT NOT NULL DEFAULT 'pending', -- pending | scanned | scanned_clean | scan_failed
    doc_class TEXT                          -- jss | non-jss | unknown (set by scan); report --by-class dimension
);

CREATE TABLE IF NOT EXISTS runs (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    ts                TEXT    NOT NULL,    -- ISO 8601 UTC, e.g. "2026-04-23T14:30:22Z"
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
    verdict           TEXT,                 -- NULL | true_positive | false_positive | uncertain
    verdict_reason    TEXT,
    reviewer          TEXT,                 -- "ai:<model>" | "human:<user>" | NULL
    first_seen_run_id INTEGER NOT NULL REFERENCES runs(id),
    last_seen_run_id  INTEGER REFERENCES runs(id),  -- most recent run that re-emitted this violation; NULL only on pre-migration rows. Precision counts rows whose last_seen == the latest run, so guard-silenced / fixed violations stop counting.
    file_suffix       TEXT,                 -- '.tex' | '.bib' | '.Rnw' | '.Rmd' (spec 005) — NULL for pre-005 rows
    file              TEXT,                 -- source file path relative to the paper dir (e.g. 'dplyr/vignettes/rowwise.Rmd'); NULL for pre-p8 rows
    UNIQUE(paper_id, rule_id, line, message, file)
);

CREATE INDEX IF NOT EXISTS idx_viol_rule     ON violations(rule_id);
CREATE INDEX IF NOT EXISTS idx_viol_verdict  ON violations(verdict);
CREATE INDEX IF NOT EXISTS idx_viol_paper    ON violations(paper_id);
-- idx_viol_lastseen is created in db._migrate_violations_last_seen, not
-- here: on a legacy DB the column is added by that migration AFTER this
-- script runs, so indexing it here would fail with "no such column".
