# Data Model: Recall Measurement

**Phase**: 1
**Spec**: [spec.md](spec.md)
**Plan**: [plan.md](plan.md)

## 1. Annotation file shape

```toml
[meta]
paper_id = "<id>"               # matches the directory name
annotator = "<name>"
date = "2026-05-03"             # ISO-8601
notes = "<optional prose>"

[[violations]]
rule_id = "JSS-CITE-002"
file = "manuscript.tex"
line = 42
comment = "<optional rationale>"

[[violations]]
# ... one entry per ground-truth violation
```

Validity:
- `paper_id` MUST equal the directory name
  (`eval/recall-corpus/<paper-id>/`).
- `rule_id` MUST exist in the catalogue (warn on retired
  ids; do not fail).
- `line` MUST be ≥ 1 and ≤ the file's line count.
- `file` MUST be a relative path under the paper's
  directory.

## 2. `compute_recall` signature

```python
@dataclass(frozen=True)
class RuleRecall:
    rule_id: str
    tp: int
    fn: int
    recall: float | None     # None when tp + fn == 0

@dataclass(frozen=True)
class RecallReport:
    per_rule: tuple[RuleRecall, ...]
    aggregate_recall: float
    f1: float | None         # None when precision is unknown
    corpus_id: str
    corpus_hash: str

def compute_recall(
    corpus_root: Path,
    *,
    catalogue: tuple[Rule, ...],
    journal: JournalModule,
    db_path: Path | None = None,
) -> RecallReport: ...
```

The function:
1. Globs `<corpus_root>/*/annotations.toml`.
2. For each paper: parses the TOML, runs the linter, builds
   the `(rule_id, file, line)` set on both sides.
3. TP = intersection size (per rule).
4. FN = annotation-only size (per rule).
5. Aggregate recall = sum(TPs) / (sum(TPs) + sum(FNs)).
6. F1 = `2 * P * R / (P + R)` if precision available.

## 3. `recall_history` table schema

```sql
CREATE TABLE recall_history (
  run_id        INTEGER PRIMARY KEY,
  run_timestamp TEXT NOT NULL,        -- ISO-8601
  corpus_hash   TEXT NOT NULL,        -- SHA256 of corpus-manifest.csv
  rule_id       TEXT NOT NULL,
  tp            INTEGER NOT NULL,
  fn            INTEGER NOT NULL,
  recall        REAL,                 -- nullable when tp + fn == 0
  UNIQUE (run_timestamp, rule_id)
);
```

The aggregate recall and F1 are NOT stored as separate
rows; they are derived per-query:

```sql
SELECT
  SUM(tp) * 1.0 / (SUM(tp) + SUM(fn)) AS aggregate_recall
FROM recall_history
WHERE run_timestamp = ?;
```

## 4. `eval-jss recall` CLI surface

```text
Usage: eval-jss recall [OPTIONS]

Options:
  --corpus DIR        Recall corpus root (default: eval/recall-corpus).
  --gate              Exit 1 when aggregate < 0.70 OR any rule
                      regresses by > 0.05 since the previous run.
  --validate          Validate annotation files; do not run linter.
  --format [terminal|json]
                      Output format (default: terminal).
  -h, --help          Show this message and exit.
```

## 5. Gate logic

```python
def evaluate_gate(report: RecallReport, prev: RecallReport | None) -> int:
    if report.aggregate_recall < 0.70:
        return 1
    if prev is None:
        return 0
    by_id = {r.rule_id: r for r in report.per_rule}
    for prev_rule in prev.per_rule:
        cur = by_id.get(prev_rule.rule_id)
        if cur is None or prev_rule.recall is None or cur.recall is None:
            continue
        if (prev_rule.recall - cur.recall) > 0.05:
            return 1
    return 0
```

## 6. Badge JSON shape (shields.io endpoint)

```json
{
  "schemaVersion": 1,
  "label": "recall",
  "message": "0.81",
  "color": "green"
}
```

`color` is computed from `aggregate_recall`:
- `>= 0.85`: `brightgreen`.
- `>= 0.70`: `green`.
- `>= 0.55`: `yellow`.
- `< 0.55`: `red`.

The same logic applies to the precision badge (consuming
spec-002's existing aggregate precision).

## 7. `eval-jss report --with-recall` integration

The combined report adds three columns to the per-rule
table:

| Column      | Source                              |
| ----------- | ----------------------------------- |
| `recall`    | `RuleRecall.recall` (or `n/a`)       |
| `f1`        | per-rule F1 = `2*P*R/(P+R)` or `n/a` |
| `Δ recall`  | `recall - prev_recall` (signed)     |

When `--with-recall` is omitted, the report is the spec-002
shape (precision-only).

## 8. Out of scope

| Item                                            | Reason                                                                  |
| ----------------------------------------------- | ----------------------------------------------------------------------- |
| Inter-annotator agreement                       | Out per Clarifications §3 (single annotator v1).                         |
| Per-rule recall thresholds                      | Out — only the aggregate floor + per-rule regression check are gating.  |
| Auto-detection of "real" violations the linter caught but the annotator missed | Out — would conflate precision and recall measurement. |
| Corpus growth automation                        | Out — corpus growth is hand-curated.                                     |
| Confidence intervals on recall                  | Out — sample size is too small to publish meaningful intervals; v2 may add bootstrapping. |
