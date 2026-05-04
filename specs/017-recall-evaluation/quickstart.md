# Quickstart: Recall Pipeline

## For a maintainer

### Run the recall harness

```sh
eval-jss recall
```

Output:

```
Recall corpus: eval/recall-corpus (10 papers)
Aggregate: 0.81 (TP=145, FN=34)
F1: 0.87

Per-rule:
  JSS-CITE-002: TP=12, FN=1, recall=0.92
  JSS-NAME-001: TP=8,  FN=2, recall=0.80
  ...
```

### Gate a CI run

```sh
eval-jss recall --gate
```

Exit 1 when aggregate falls below 0.70 OR any rule regresses
> 0.05 vs. the last run on the same corpus.

### Validate annotations only

```sh
eval-jss recall --validate
```

Exits 0 when every annotation file parses + every rule id
exists + every line is in range. Does NOT run the linter.

### Add a new paper to the recall corpus

1. Choose the paper (must be a JSS-paper-counterpart vignette,
   per the existing corpus rules).
2. Create `eval/recall-corpus/<paper-id>/`.
3. Drop the source file(s) inside.
4. Read the manuscript end-to-end. For each violation you
   spot:
   - Identify the rule id (`jss-lint explain RULE-ID` helps).
   - Record `(rule_id, file, line, comment?)` in
     `annotations.toml`.
5. Run `eval-jss recall --validate` — fix any errors.
6. Run `eval-jss recall` — inspect how the new paper shifts
   per-rule numbers.
7. Update `eval/recall-corpus/corpus-manifest.csv` with the
   paper's source URL + SHA256.
8. Open a PR.

### Update the README badges

The CI workflow regenerates the badge JSONs and pushes to
`gh-pages`. Manual update:

```sh
eval-jss recall --format json | python eval/badge.py recall > badges/recall.json
git checkout gh-pages
cp badges/* badges/
git commit -am "badges: refresh"
git push
```

## For a contributor

### Where things live

```text
eval/recall.py                                     # the engine
eval/recall-corpus/                                # the corpus
eval/recall-corpus/README.md                       # annotation protocol
eval/badge.py                                      # shields.io JSON emitter
eval/cli.py                                        # `eval-jss recall` subcommand
eval/report.py                                     # combined report (precision + recall + F1)
tests/unit/eval/test_recall.py                     # engine tests
tests/integration/test_recall_cli.py               # CLI tests
.github/workflows/eval.yml                         # CI gate
.github/workflows/publish-badges.yml               # gh-pages push
```

### Run the tests

```sh
pytest tests/unit/eval/test_recall.py tests/integration/test_recall_cli.py -v
```

### Common pitfalls

- **Annotating a violation the linter doesn't recognise**:
  use the closest catalogue rule. If no rule applies, do
  NOT add a synthetic id; instead, file an issue
  documenting the missing rule. Future spec adds the rule;
  the corpus is re-validated.
- **Inter-annotator disagreement**: single-annotator v1.
  When v2 introduces a second annotator, the agreement
  metric will tell us how much the v1 numbers were
  trustworthy.
- **Drift between the source and the annotation**: if a
  paper in the corpus is updated upstream and the line
  numbers shift, the annotation needs a one-shot pass to
  re-anchor every line. The corpus-manifest's SHA256
  guards against silent drift; a hash mismatch fails the
  validation step.
- **Padding the corpus to game the aggregate**: don't.
  The Constitution §X "small surface" applies to the
  corpus too — quality over quantity.

### Where to extend

- **Dual annotator + Cohen-kappa**: future spec; v1 is
  single-annotator.
- **Confidence intervals**: future spec; sample size too
  small in v1 to publish meaningful intervals.
- **Auto-extraction of "violations the linter caught but
  the annotator missed"**: out of scope. That would mix
  recall and precision evaluation.
