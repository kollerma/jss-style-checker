# 017 — Recall measurement + README badge

**Phase:** Trust
**Depends on:** —
**Unblocks:** —

## Why

The eval harness measures *precision* — when the tool fires, is it
correct? It does not measure *recall* — does the tool fire on every
real violation? Editors won't trust the tool until they know what it
*misses*. Publishing recall on the README converts hesitation to
adoption.

## /speckit.specify prompt

Build a recall-evaluation pipeline alongside the existing precision
harness. A new "ground-truth" corpus (`eval/recall-corpus/`)
contains ~10 hand-annotated JSS papers where a human has labelled
*every* JSS guide violation in the source, regardless of whether
the tool fired. Annotations are per-paper TOML files keyed by
`(rule_id, line)`. `eval-jss recall` runs the linter on these
papers, compares the output to the ground-truth, and reports
per-rule recall = `TP / (TP + FN)`. The output integrates with the
existing precision report so the README can publish a
"precision/recall" badge per rule and an aggregate F1. Recall
regressions block CI on the recall corpus the same way precision
regressions do today.

## /speckit.clarify prompt

Probe: (a) corpus size — 10 papers minimum, but is there a target
ceiling beyond which annotation cost exceeds value? (b) annotation
format — TOML (matches existing `review-skip-list.toml` style) or
YAML or a CSV? (c) inter-annotator agreement — single annotator
(Manuel) v1, dual annotator v2? (d) do we publish the corpus or
keep annotations private to avoid the tool training on them?
(e) what's the recall threshold that gates a release — 80 %, 90 %,
per-rule?

## /speckit.plan prompt

Add `eval/recall.py` with a loader for the per-paper TOML
annotations and a `compute_recall(corpus, db)` function. New
`eval-jss recall` subcommand. Annotation files live under
`eval/recall-corpus/<paper-id>/annotations.toml`. Persist recall
history in the existing `eval/precision-history.db` schema (rename
or add `recall_history` table). Update `eval/report.py` to emit
combined precision/recall + F1. Add a README badge generator
(shields.io endpoint JSON) and a CI check that fails when aggregate
recall drops below the threshold. Document the annotation protocol
in `eval/recall-corpus/README.md`.
