# JSS Recall Corpus — Annotation Protocol

> **Status (spec 017):** infrastructure ships in v1 — the engine
> (`eval/recall.py`) and the annotation TOML schema (below). The
> first 10 hand-annotated JSS papers are a separate
> contribution stream tracked under "follow-up: recall corpus
> v1 contents".

## What this corpus is for

Recall measurement: when the linter fires, how often is it
right? Precision (the existing `eval/precision-history.db`
metric) answers that. Recall — when the linter does NOT fire,
how often is there really nothing to flag? — needs a hand-
annotated ground truth to compute.

## Per-paper directory layout

```
eval/recall-corpus/
├── README.md                    (this file)
├── <paper-id>/
│   ├── manuscript.tex           (the source — ASCII or UTF-8)
│   └── annotations.toml         (every ground-truth violation)
└── (more papers...)
```

## Annotation file shape

```toml
[meta]
paper_id = "<id>"               # equals the directory name
annotator = "<name>"
date = "2026-05-04"             # ISO-8601
notes = "<optional>"

[[violations]]
rule_id = "JSS-CITE-002"
file = "manuscript.tex"
line = 42
comment = "<optional rationale>"

# ... one entry per ground-truth violation
```

## Annotation walk-through

1. Pick a JSS-paper-counterpart vignette (see the precision
   corpus selection rules — same authority).
2. Read the manuscript end-to-end. For each violation you spot,
   identify the rule id (`jss-lint explain RULE-ID` helps once
   the explain subcommand ships).
3. Record `(rule_id, file, line, comment?)` in
   `annotations.toml`.
4. Run `eval-jss recall --validate` (when the CLI surface
   ships) to verify every annotation parses + every rule id
   exists + every line is in range.
5. Open a PR. The CI checks the corpus manifest hash and runs
   `eval-jss recall` to record the new aggregate.

## Identity tuple

`(rule_id, file, line)`. Column does NOT participate. A
violation the annotator marked at line 42 column 1 and the
linter caught at line 42 column 12 both count as a TP.

## Inter-annotator agreement

V1 ships single-annotator; v2 (a future spec) introduces a
second annotator and a Cohen-kappa-style agreement metric.

## License

Annotations are released under the same license as the
linter: MIT. See research §4 for the rationale on publishing
the corpus rather than keeping it private.
