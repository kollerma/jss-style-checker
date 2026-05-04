# Research: Recall Measurement

**Phase**: 0
**Spec**: [spec.md](spec.md)
**Plan**: [plan.md](plan.md)

## 1. Annotation format: TOML

**Decision**: TOML, schema per FR-002.

**Rationale**:
- Reuses the `tomllib` reader already required by spec 001
  config loading.
- Matches the existing `eval/review-skip-list.toml` style;
  contributors familiar with one are familiar with both.
- Renders cleanly in PR diffs (no escaping quirks like CSV
  or YAML).

**Alternatives considered**:
- YAML: rejected — quoting rules are notoriously fragile
  for content with `:` characters.
- CSV: rejected — escaping is error-prone for free-text
  comments.
- JSON: rejected — comments are not part of the spec.

---

## 2. Corpus size: 10 minimum, ~30 ceiling

**Decision**: Ship 10 papers; encourage growth up to ~30;
explicitly document the ceiling.

**Rationale**:
- Per Clarifications §1: marginal recall-measurement value
  drops beyond ~30 papers; annotation cost grows linearly.
- 10 papers is enough for a defensible aggregate number;
  more than ~30 is surplus given the variance in real
  manuscripts.

**Alternatives considered**:
- Open-ended: rejected — invites contribution debt.
- Hard cap at 10: rejected — useful contributions in
  the 11-30 range should not be blocked.

---

## 3. Single annotator for v1

**Decision**: Manuel annotates v1. The README documents
this as a known limitation. v2 (a future spec) introduces
a second annotator + an inter-annotator-agreement metric.

**Rationale**:
- Inter-annotator agreement is a serious research problem;
  doing it half-way is worse than not doing it.
- Single-annotator measurements are the standard starting
  point in the lint-tool ecosystem (every tool that
  publishes recall numbers started with one annotator).
- Caveat-in-README is honest about the limitation.

**Alternatives considered**:
- Dual annotator from v1: rejected — doubles the
  spec-017 work and delays publication of the metric.
- No annotator information in the README: rejected —
  hides the limitation.

---

## 4. Public corpus

**Decision**: Publish the corpus openly under the same
license as the precision corpus.

**Rationale**:
- Per Clarifications §4: reproducibility is the entire
  point of the recall pipeline; a private corpus produces
  a number readers cannot verify.
- The JSS papers themselves are public (they're the
  vignettes shipped with R packages); only the
  annotations are novel.
- Tail-risk of training-data leakage is small given the
  scale.

**Alternatives considered**:
- Private annotations: rejected per rationale.
- License the annotations under a "no AI training" clause:
  rejected — unenforceable, and creates friction for
  reproducing benchmarks.

---

## 5. Aggregate threshold + per-rule regression check

**Decision**: Aggregate ≥ 0.70 hard floor; per-rule recall
regression > 0.05 vs. previous run also fails the gate.

**Rationale**:
- Aggregate covers "did the tool overall slip?"; per-rule
  catches surgical regressions in a specific rule.
- 0.70 is calibrated to be achievable with v1's 10-paper
  corpus; aggressive thresholds at v1 would force the
  team to game the corpus.
- Per-rule check uses the previous run's recall stored in
  the DB (the same pattern spec 002 uses for precision
  history).

**Alternatives considered**:
- Aggregate-only: rejected — would mask single-rule
  failures.
- Per-rule-only: rejected — would prevent the headline
  badge update.
- 0.80 / 0.90 thresholds: rejected for v1; corpus is too
  small to make those numbers meaningful.

---

## 6. F1 computation

**Decision**: F1 is computed at the *corpus-aggregate*
level: `F1 = 2 * (P * R) / (P + R)` where P and R are
aggregate precision and aggregate recall.

**Rationale**:
- Per-rule F1 averages misrepresent the underlying
  distribution (averaging F1s is statistically dubious;
  averaging precisions and recalls then deriving F1 is
  the standard approach).
- The README badge wants ONE F1 number; the
  corpus-aggregate is unambiguous.

**Alternatives considered**:
- Macro-averaged F1: rejected — averaging F1s is the
  noted statistical pitfall.
- Micro-averaged F1: equivalent to corpus-aggregate when
  computed across pooled TP/FP/FN; we use that
  formulation.

---

## 7. Badge endpoint hosting

**Decision**: Generate `precision.json` and `recall.json`
on every CI run; push to `gh-pages` branch; serve via
GitHub Pages at
`https://kollerma.github.io/jss-style-checker/badges/<name>.json`.

**Rationale**:
- shields.io accepts an "endpoint" pattern that fetches
  arbitrary JSON; static hosting is sufficient.
- GitHub Pages is free and always-on for the project.
- The CI workflow keeps the JSONs fresh.

**Alternatives considered**:
- Hard-code the badge values in the README: rejected —
  drift between README and reality.
- Use shields.io's dynamic endpoint pointing at the DB:
  rejected — would expose the SQLite file via an HTTP
  interface, more surface than needed.

---

## 8. Annotation walk-through documentation

**Decision**: `eval/recall-corpus/README.md` includes a
worked example: take a real fixture, walk through every
section of the manuscript, identify each violation,
record it in the TOML.

**Rationale**:
- An annotation protocol works only if the next
  contributor can follow it without consulting Manuel.
- A worked example is the cheapest way to make the
  protocol concrete.

**Alternatives considered**:
- Plain-text protocol with no example: rejected —
  contributors would still need to ask.
- Video walkthrough: rejected — falls out of date faster
  than text and is harder to update.

---

## Summary

All eight decisions follow from spec Clarifications and
Constitution §I, §VI, §X, §XII. No remaining `NEEDS
CLARIFICATION`. Ready for Phase 1.
