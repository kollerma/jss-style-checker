# Contract — `eval/report.csv`

Append-only history of per-rule precision. Written by `eval-jss report`. Checked into the repository so that trends are visible in `git log -p eval/report.csv`.

## Schema

```
ts,tool_version,rule_id,category,tp,fp,pending,precision,source,below_threshold
```

| Column             | Type       | Description                                                                                |
|--------------------|------------|--------------------------------------------------------------------------------------------|
| `ts`               | ISO 8601 UTC | Timestamp of the `report` invocation (all rows from one invocation share the same `ts`). |
| `tool_version`     | string     | Linter version, read from the most recent `runs` row in the DB. Empty if no runs exist.   |
| `rule_id`          | string     | Rule identifier. `JSS-PARSE-000` rows are **excluded** from this CSV (spec FR-021).       |
| `category`         | string     | Rule category (e.g. `citation`, `bibliography`, `typography`).                            |
| `tp`               | int        | Count of `true_positive` verdicts.                                                        |
| `fp`               | int        | Count of `false_positive` verdicts.                                                       |
| `pending`          | int        | Count of rows with `verdict IS NULL` or `verdict = 'uncertain'`.                          |
| `precision`        | float \| "" | `tp / (tp + fp)` to 4 decimal places, or empty string when `tp + fp == 0` (not yet measured). |
| `source`           | string     | `"overall"` for the aggregate row; one of `cran`/`bioc`/`arxiv`/`jss_archive`/`manual` when `--by-source` emits per-source rows. |
| `below_threshold`  | bool (`0`/`1`) | `1` iff `precision < 0.90` AND `precision` is not empty. `0` otherwise.                |

## Invariants

1. **Header row present and exact**. The column set is additive-only within a major version of `eval-jss`; any breaking change requires a version bump and a CHANGELOG entry.
2. **One invocation writes a contiguous block**. Every row from one `report` call shares the same `ts` and `tool_version`.
3. **Overall row always present** for every rule with any activity. Per-source rows exist only when `--by-source` is passed.
4. **No dedup**. Two consecutive `report` invocations produce two identical-content blocks (modulo `ts`), because the purpose of the CSV is a trend history — consolidating on content would lose the signal that "nothing changed between these two runs".

## Writing

```python
with path.open("a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=FIELDS)
    if new_file:
        writer.writeheader()
    for row in rows:
        writer.writerow(row)
    f.flush()
```

`new_file` is `not path.exists()` evaluated **before** opening. Appending never rewrites history — a damaged prior row stays damaged. Operators who need to clean the CSV do so manually.

## Phase A / Phase B behaviour

- **Phase A** — `report` writes nothing to `eval/report.csv` by default. A `--csv PATH` flag is accepted and, when passed, enables append (so a Phase A operator who wants a history can get one). This keeps `eval/report.csv` out of `git diff` churn until Phase B is committed.
- **Phase B** — default flips to **append always** unless `--csv -` is passed. `eval/report.csv` becomes checked-in state that `git` tracks.

The column set is identical in both phases; only the default invocation differs.
