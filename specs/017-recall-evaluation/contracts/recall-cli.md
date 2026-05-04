# Contract: `eval-jss recall` CLI

**Spec**: [../spec.md](../spec.md)
**Plan**: [../plan.md](../plan.md)

## C-1 Subcommand

`eval-jss recall` MUST be a subcommand of the `eval-jss` CLI
(the spec-002 evaluation tool). It MUST coexist with the
existing `scan`, `report`, and other subcommands.

## C-2 Recall formula

```
recall = TP / (TP + FN)
```

Where:
- TP = count of `(rule_id, file, line)` tuples present in
  BOTH the linter output AND the annotation set, per rule.
- FN = count of tuples in the annotation set but NOT in
  the linter output.

`(rule_id, file, line)` is the identity; `column` and
`message` are NOT part of recall identity (a violation
the annotator marked at line 42 and the linter caught at
line 42 column 12 both count as a TP regardless of
column).

## C-3 Aggregate

Aggregate recall = `sum(TP) / (sum(TP) + sum(FN))` across
ALL rules. A rule with `TP + FN == 0` contributes
nothing to the aggregate (excluded from numerator AND
denominator).

## C-4 F1

`F1 = 2 * P * R / (P + R)` where P is the latest aggregate
precision (queried from `precision_history` per spec 002)
and R is the aggregate recall computed in this run. F1 is
`None` when either P or R is unavailable.

## C-5 Gate semantics

`eval-jss recall --gate` exits 1 when:
- `aggregate_recall < 0.70`, OR
- ANY rule's recall regressed by `> 0.05` vs. the previous
  run on the same `corpus_hash`.

Otherwise exits 0.

## C-6 `--validate` mode

`--validate` parses every annotation file and exits 0 on
full-corpus validity. It does NOT run the linter. Useful
for pre-commit hooks or PR checks.

## C-7 DB persistence

After every non-`--validate` run, the harness writes one
row per rule to `recall_history` (per data-model §3). The
write is atomic per run.

## C-8 Output formats

| Format     | Use                                                           |
| ---------- | ------------------------------------------------------------- |
| `terminal` | rich-styled per-rule table + aggregate + F1.                  |
| `json`     | `{"per_rule": [...], "aggregate_recall": ..., "f1": ...}`.    |

`json` is consumed by the badge-generator script.

## C-9 Determinism

`eval-jss recall` is deterministic given the same
`(corpus, catalogue, DB-snapshot)`. The DB snapshot is
the only mutable input.

## C-10 Corpus-hash protection

The harness reads `corpus-manifest.csv`'s SHA256 column;
for each paper, computes the file's actual SHA256;
mismatches abort with exit 2 and a "corpus drift" message
naming the offending paper.

## C-11 Backwards compatibility

The pre-spec-017 `eval-jss` subcommands continue to work
unchanged. The new `recall` subcommand is purely additive.

## C-12 Badge endpoint

A separate small script `eval/badge.py` consumes the JSON
output and emits a shields.io endpoint document
(per data-model §6). The badge color follows the
documented thresholds.
