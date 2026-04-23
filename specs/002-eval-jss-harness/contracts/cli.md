# Contract — `eval-jss` CLI

Exit codes are the same convention as `jss-lint`: **0** = success, **1** = the operation completed but at least one thing warrants attention (e.g. a paper produced a `JSS-PARSE-000` during `scan`), **2** = the harness itself could not run (unknown subcommand, missing DB, linter not on PATH, unreadable corpus, malformed manifest).

stdout carries the user-facing output of each subcommand. stderr carries diagnostics and error messages. `scan`'s progress output (one line per paper, via `rich.progress`) goes to **stderr** so that `eval-jss scan 2>/dev/null` is a silent batch run.

## Top-level invocation

```
eval-jss [--db PATH] <subcommand> [options]
```

`--db PATH` overrides the default `eval/eval.db`. Useful in tests and when running against a scratch DB. Threaded through `click`'s context object to every subcommand.

## `eval-jss init`

```
eval-jss init [--db PATH]
```

Creates the schema at `--db` (default `eval/eval.db`). Idempotent — second invocation is a no-op. No other options. Exit 0 on success; exit 2 if the DB path's parent directory is not writable.

## `eval-jss scan`

```
eval-jss scan [--db PATH] [--corpus DIR] [--batch-size N] [--force]
```

- `--corpus DIR`: directory of the corpus. Default `examples/`.
- `--batch-size N`: maximum number of *un-scanned* papers to process in one invocation (default: process all). Useful for large full-scope corpora.
- `--force`: re-scan papers regardless of prior `status`. Dedup is still applied — `--force` never creates duplicate violation rows, it just re-invokes the linter and updates `papers.status`.

Behaviour:
1. Resolves `jss-lint` via `shutil.which`. Missing → exit 2 with `"jss-lint not on PATH"`.
2. Walks `corpus/` for subdirectories; each subdirectory is one paper. A new `papers` row is inserted the first time a subdirectory is seen; subsequent scans update `status` only.
3. Opens a single `runs` row at the start of the invocation; updates `papers_scanned` and `violations_found` on its in-memory copy; writes the row at the end.
4. Per paper: invoke the linter (see research.md §"Invoking `jss-lint`"), ingest violations with `INSERT OR IGNORE`, update `papers.status`.
5. Renders a rich progress bar to stderr.

Exit 0 if every paper scanned cleanly and no `JSS-PARSE-000`s appeared. Exit 1 if any paper produced violations **or** any `JSS-PARSE-000` was persisted (so CI can tell "something in this corpus pass warrants attention" from "pipeline broken"). Exit 2 if `jss-lint` is missing, corpus is unreadable, or the DB connection fails.

## `eval-jss human-review`

```
eval-jss human-review [--db PATH] [--limit N] [--rule RULE_ID] [--reviewer NAME]
```

- `--limit N`: stop after N verdicts.
- `--rule RULE_ID`: restrict to violations of a specific rule (useful when refining one rule at a time during Step 3).
- `--reviewer NAME`: override `os.environ['USER']` as the reviewer stamp.

Interactively walks violations where `verdict IS NULL OR verdict = 'uncertain'`, newest-run-first, then by paper and line. For each, renders the violation + ±3 lines of source context and prompts for `[t/f/u/s/q]`:

- `t` → `true_positive`
- `f` → `false_positive`
- `u` → `uncertain`
- `s` → skip (do not change verdict, move on)
- `q` → quit (exit the loop)

On `t` or `f`, additionally prompts for an optional `verdict_reason`. Every verdict is committed immediately (spec FR-015 — session-resumable).

Exit 0 on normal completion (loop exhausted or `q`). Exit 2 if DB missing/unreadable.

## `eval-jss review` (Phase B)

```
eval-jss review [--db PATH] [--limit N] [--confidence-threshold F] [--model NAME] [--base-url URL] [--skip-list PATH]
```

- `--confidence-threshold F`: default `0.8`. Labels below this stay `uncertain`.
- `--model NAME`: the model name to pass in the OpenAI-style request `"model"` field. Default `qwen3-30b-a3b`. The actual model is whatever `llama-server` was started with — this string is cosmetic, stored in `reviewer` as `ai:<NAME>`.
- `--base-url URL`: default `http://localhost:8080`. The `/v1/chat/completions` suffix is added internally.
- `--skip-list PATH`: default `eval/review-skip-list.toml`. Missing file → empty skip-list.

Walks violations where `verdict IS NULL`, sends each through the configured `LlamaServerClient`, writes back `(verdict, verdict_reason, reviewer="ai:<model>")` iff `confidence ≥ threshold`; else leaves the row `uncertain`.

Exit 0 on normal completion. Exit 2 if the AI server is unreachable on the first request (fail fast — don't label a third of the corpus before giving up).

## `eval-jss report`

```
eval-jss report [--db PATH] [--by-source] [--csv PATH]
```

- `--by-source` (Phase B): include per-source precision columns in the output and in the CSV history row.
- `--csv PATH`: default `eval/report.csv`. `"-"` disables the append (Phase A default behaviour is to skip the CSV append; Phase B flips the default to *append*).

Prints:
1. A per-rule precision table (via `rich.table.Table`) grouped by category, with `PASS`/`FAIL (<90%)`/`NOT MEASURED`/`NOT EXERCISED` status column.
2. A dedicated parse-failure panel if any `JSS-PARSE-000` rows exist.
3. *(Phase B)* A per-source breakdown table when `--by-source` is set.

Appends one row per rule (plus per-rule-per-source rows when `--by-source`) to the CSV. Header written iff the file didn't previously exist.

Exit 0 if every rule with labelled data passes the 90% gate. Exit 1 if any rule is below threshold (so CI can gate merges on precision). Exit 2 if the DB is missing or malformed.

## `eval-jss corpus fetch` (Phase B)

```
eval-jss corpus fetch [--manifest PATH] [--target DIR] [--gaps PATH]
```

- `--manifest PATH`: default `eval/corpus-manifest.csv`.
- `--target DIR`: default `examples/` — where `local_path` values are resolved against.
- `--gaps PATH`: default `eval/corpus-manifest-gaps.csv`.

For each manifest row: skip if `local_path` exists and SHA256 matches; else fetch from the immutable distribution URL, verify SHA256, extract (if tarball). Unreachable / mismatched entries appended to the gaps file.

Exit 0 if every manifest row was materialised or safely skipped. Exit 1 if any row ended up in the gaps file. Exit 2 if the manifest is malformed.

## `eval-jss corpus status` (Phase B)

```
eval-jss corpus status [--manifest PATH] [--target DIR]
```

Reports, as a rich table: rows materialised OK, rows pending (no local copy), rows with hash mismatch, rows needing manual placement (`jss_archive`, `manual`). Does not fetch. Exit 0 if everything is OK, exit 1 if anything is pending/mismatched.

## Summary table

| Subcommand           | Phase | Reads                          | Writes                                   | Exit 0 | Exit 1                   | Exit 2 |
|----------------------|-------|--------------------------------|------------------------------------------|--------|--------------------------|--------|
| `init`               | A     | —                              | schema                                   | ok     | —                        | unwritable / malformed db |
| `scan`               | A     | corpus dir, `jss-lint`         | `papers`, `violations`, `runs`           | clean  | violations or parse fail | linter missing / bad corpus |
| `human-review`       | A     | `violations`                   | `violations.verdict*`                    | ok     | —                        | db missing |
| `review`             | B     | `violations`, llama-server     | `violations.verdict*`                    | ok     | —                        | server unreachable |
| `report`             | A/B   | `violations`, `papers`         | stdout table, `eval/report.csv` (B)      | all rules pass | any rule below 90% | db missing |
| `corpus fetch`       | B     | manifest, remote URLs          | `examples/...`, `corpus-manifest-gaps.csv` | all rows OK | any gap | malformed manifest |
| `corpus status`      | B     | manifest, `examples/`          | stdout table                             | all OK | any gap/mismatch | malformed manifest |
