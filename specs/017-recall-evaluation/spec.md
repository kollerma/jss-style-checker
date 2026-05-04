# Feature Specification: Recall Measurement + README Badge

**Feature Branch**: `017-recall-evaluation`
**Created**: 2026-05-03
**Status**: Draft
**Input**: User description: "Build a recall-evaluation pipeline alongside the existing precision harness. A new \"ground-truth\" corpus (`eval/recall-corpus/`) contains ~10 hand-annotated JSS papers where a human has labelled *every* JSS guide violation in the source, regardless of whether the tool fired. Annotations are per-paper TOML files keyed by `(rule_id, line)`. `eval-jss recall` runs the linter on these papers, compares the output to the ground-truth, and reports per-rule recall = `TP / (TP + FN)`. The output integrates with the existing precision report so the README can publish a \"precision/recall\" badge per rule and an aggregate F1. Recall regressions block CI on the recall corpus the same way precision regressions do today."

## Clarifications

### Session 2026-05-03

- Q: Corpus size — 10 papers minimum, but is there a target ceiling beyond which annotation cost exceeds value? → A: 10 papers minimum, ~30 papers ceiling. Beyond ~30 the marginal recall-measurement value drops while annotation cost grows linearly. The spec calls out the ceiling explicitly so contributors don't assume "more is always better". If a future spec demonstrates value beyond 30, the ceiling is revisited.
- Q: Annotation format — TOML, YAML, or CSV? → A: TOML. Matches the existing `eval/review-skip-list.toml` style; reuses the `tomli` reader; renders cleanly in PRs (no CSV escaping headaches, no YAML quoting traps). The schema is FR-002.
- Q: Inter-annotator agreement — single annotator (Manuel) v1, dual annotator v2? → A: Single annotator v1. Inter-annotator agreement is a real research problem; v1 ships with one annotator and a frank caveat in the README. v2 (a future spec) adds a second annotator and a Cohen-kappa-style agreement metric. v1's recall number is approximate; that's still a real upgrade over today's "no recall measurement at all".
- Q: Do we publish the corpus or keep annotations private to avoid the tool training on them? → A: Publish. Reproducibility is the entire point of the recall pipeline; a private corpus produces a number readers cannot verify. We accept the tail risk that future ML-assisted rule development may indirectly train on these annotations; the value of public reproducibility outweighs it. Also: the JSS papers themselves are public, so the corpus's main novelty is the annotation labels, not the source.
- Q: What's the recall threshold that gates a release — 80 %, 90 %, per-rule? → A: Aggregate 0.70 with per-rule "no big regression" tracking. Hard floor: aggregate recall ≥ 0.70. Per-rule: regression of >0.05 in any single rule's recall vs. the previous run also fails the gate. The aggregate threshold is calibrated to be achievable with v1's 10-paper corpus; the per-rule check catches surgical regressions in a specific rule that the aggregate would mask.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Editor sees the published recall (Priority: P1)

A JSS desk editor visits the project's README and sees badges:
`precision: 0.94 | recall: 0.81 | F1: 0.87`. They click through
the badge URL and read a one-page explanation of how recall is
measured (the ground-truth corpus, the annotation protocol, the
caveats). They now know what the tool catches AND what it
misses, and can make an informed adoption decision.

**Why this priority**: P1 because publishing recall is the trust
contract this feature exists to deliver. Without the badge, the
recall machinery is internal-only and doesn't address adoption
hesitation.

**Independent Test**: A README badge URL resolves to a
shields.io-formatted JSON document with the current recall
number; the badge image renders on a Markdown preview.

**Acceptance Scenarios**:

1. **Given** the recall pipeline produced an aggregate value
   `0.81`, **When** the badge endpoint is fetched, **Then** the
   JSON contains `{"label": "recall", "message": "0.81",
   "color": ...}`.
2. **Given** the README, **When** rendered in a Markdown
   preview, **Then** the badge image displays the recall
   number.

---

### User Story 2 - `eval-jss recall` reports per-rule recall (Priority: P1)

A maintainer adds a new rule. They run `eval-jss recall` against
the recall corpus and get a per-rule report: rule id, true
positives, false negatives, recall (`TP / (TP + FN)`). Rules
below the threshold are flagged.

**Why this priority**: P1 because recall measurement only has
value if the tool surfaces it for actionable triage. The
per-rule view is the maintainer's debugging surface; the
aggregate is the README badge.

**Independent Test**: Run `eval-jss recall` against a fixture
recall corpus. The report lists every rule that appears in the
ground truth with its TP / FN / recall numbers.

**Acceptance Scenarios**:

1. **Given** a recall corpus where rule X has 8 true
   violations and the linter caught 6, **When** `eval-jss
   recall` runs, **Then** the report lists `X: TP=6, FN=2,
   recall=0.75`.
2. **Given** the same setup, **When** the report renders the
   aggregate, **Then** the aggregate is computed across all
   rules' TP / FN sums.

---

### User Story 3 - CI gate on recall regression (Priority: P1)

A PR introduces a regression that drops a rule's recall from
0.85 to 0.62. CI runs `eval-jss recall --gate` and the step
fails because aggregate recall (or per-rule recall — see
Clarifications §5) fell below the threshold.

**Why this priority**: P1 because the gate is the mechanism
that keeps recall stable over time. Without it, every
refactor risks silently dropping recall.

**Independent Test**: A simulated regression in the recall
corpus triggers the CI gate's exit code 1; an unchanged corpus
yields exit 0.

**Acceptance Scenarios**:

1. **Given** the recall corpus and a baseline aggregate recall
   of 0.81, **When** a refactor lowers it to 0.79, **Then**
   `eval-jss recall --gate` exits 1.
2. **Given** an unchanged baseline, **When** the gate runs,
   **Then** it exits 0.

---

### User Story 4 - Document the annotation protocol (Priority: P2)

A future contributor wants to add a new paper to the recall
corpus. They read `eval/recall-corpus/README.md`, which
documents:
- How to choose a paper (citable JSS-paper-counterpart
  vignette).
- How to annotate every violation (per-rule walk-through).
- The TOML annotation file shape.
- The `eval-jss recall` workflow for verifying the
  annotation reproduces the expected counts.

They follow the protocol and add the new paper.

**Why this priority**: P2 because the protocol is what makes
the corpus extensible. The first 10 papers ship with the spec;
additional papers come from contributors.

**Independent Test**: The README contains five sections:
choose-a-paper, annotation-format, walk-through-example,
verification, contribution-flow.

**Acceptance Scenarios**:

1. **Given** `eval/recall-corpus/README.md`, **When** read,
   **Then** the five sections above are present.
2. **Given** the documented walk-through, **When** a
   contributor follows it on a new fixture, **Then** the
   resulting annotation file passes
   `eval-jss recall --validate`.

---

### User Story 5 - Ground-truth corpus stays small and maintainable (Priority: P2)

The corpus contains ~10 papers (the spec target). When a
contributor proposes adding a paper, they update the corpus,
re-run the recall harness, and verify the per-rule numbers move
predictably. The spec discourages corpus growth beyond ~30
papers (annotation cost grows linearly).

**Why this priority**: P2 because the corpus's value comes from
careful annotation. A 200-paper corpus with sloppy annotations
gives a worse recall measurement than a 10-paper corpus with
careful ones.

**Independent Test**: The spec's documentation includes a "size
target" section reading "10 papers minimum, ~30 papers ceiling".

**Acceptance Scenarios**:

1. **Given** the spec, **When** a maintainer reads it, **Then**
   the size target appears explicitly.

---

### Edge Cases

- An annotation file references a rule id that no longer
  exists (the rule was retired): the recall harness skips
  that annotation with a warning; the per-rule report doesn't
  list the retired rule.
- An annotation references a line that doesn't exist (typo or
  source drift): the harness flags it as a validation error;
  exit 2.
- The linter fires at a `(rule_id, line)` for which no
  annotation exists: this is NOT a false positive (precision
  is measured separately on the precision corpus); for recall
  purposes it's irrelevant unless the line lies inside a
  range the annotator marked. (Spec policy: only annotated
  `(rule_id, line)` pairs participate in TP/FN; everything
  else is ignored for recall.)
- A paper has zero violations: legal; its annotation file is
  the sentinel `[meta]\nviolations = []`.
- A rule has zero ground-truth instances across the corpus:
  recall is `n/a` for that rule; aggregate excludes it.
- An annotator forgets to annotate a real violation: this
  is the irreducible inter-annotator-agreement problem;
  Clarifications §3 limits the spec to single-annotator v1.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A new directory `eval/recall-corpus/` MUST
  contain at least 10 hand-annotated JSS papers. Each paper
  is a sub-directory `<paper-id>/` containing the source
  file(s) and an `annotations.toml`.
- **FR-002**: Annotation file shape:
  ```toml
  [meta]
  paper_id = "<id>"
  annotator = "<name>"
  date = "<ISO-8601>"
  notes = "<optional>"

  [[violations]]
  rule_id = "JSS-CITE-002"
  file = "manuscript.tex"
  line = 42
  comment = "<optional>"
  ```
- **FR-003**: A new subcommand `eval-jss recall` MUST be
  added. It runs the linter against every paper in the
  corpus, loads each `annotations.toml`, computes per-rule
  TP / FN / recall, and writes the result to the
  precision-history DB (new `recall_history` table) AND
  prints a report to stdout.
- **FR-004**: Recall formula: `recall = TP / (TP + FN)`,
  where TP is the count of `(rule_id, line)` pairs that
  appear in BOTH the linter output AND the annotation, and
  FN is the count that appears in the annotation but NOT
  the linter output.
- **FR-005**: Aggregate recall: pooled TP / (pooled TP +
  pooled FN) across all rules. F1 (precision + recall) is
  reported as well, computed from the latest precision +
  recall numbers.
- **FR-006**: A `--gate` flag MUST cause exit 1 when
  aggregate recall drops below the threshold OR when any
  rule's recall drops by more than 0.05 since the previous
  run on the same corpus. Both checks are independent; the
  worse of the two drives the exit code.
- **FR-007**: A README badge endpoint at a documented URL
  (e.g., `https://kollerma.github.io/jss-style-checker/badges/recall.json`)
  MUST serve a shields.io-formatted JSON object with the
  current aggregate recall. The endpoint is regenerated on
  every CI run.
- **FR-008**: A second badge endpoint MUST serve precision
  in the same format, so the README can place
  `precision: 0.94 | recall: 0.81 | F1: 0.87` side-by-side.
- **FR-009**: A `--validate` flag on `eval-jss recall` MUST
  verify each annotation file: every `rule_id` exists in
  the catalogue (warn on retired ids); every `line` falls
  within the file's line count.
- **FR-010**: An `eval/recall-corpus/README.md` MUST
  document: paper-selection criteria, annotation format,
  walk-through example, verification steps, contribution
  flow.
- **FR-011**: Aggregate recall threshold is 0.70 v1
  (Clarifications §5 documents the rationale). A rule
  whose recall is `n/a` (no ground-truth instances) is
  excluded from both numerator and denominator.
- **FR-012**: A new column `f1` MUST appear in the
  `eval-jss report` output combining precision and recall.

### Key Entities

- **Recall corpus**: ~10 hand-annotated JSS-paper-vignette
  pairs at `eval/recall-corpus/`.
- **Annotation file**: `annotations.toml` per paper,
  shape per FR-002.
- **Per-rule recall**: `(rule_id, TP, FN, recall)` tuple
  computed across the corpus.
- **Aggregate recall**: pooled `TP / (TP + FN)` across
  rules; F1 derives from precision + recall.
- **Badge endpoint**: shields.io JSON document at a
  pages-served URL; regenerated by CI.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: After spec-017 ships, the README displays
  three badges: precision, recall, F1. All render with
  their current numbers.
- **SC-002**: `eval-jss recall` produces a per-rule
  recall report deterministically (same corpus + same
  catalogue → same numbers).
- **SC-003**: The annotation TOML files validate against
  the documented schema; `eval-jss recall --validate`
  exits 0.
- **SC-004**: A CI gate run after a deliberate
  recall-regressing edit exits 1; an unchanged-baseline
  run exits 0.
- **SC-005**: The recall corpus contains exactly 10
  papers in the v1 ship; the README lists each paper's
  citation.
- **SC-006**: The annotation README walks a contributor
  through adding an 11th paper without further docs
  consultation (verified by a usability check during
  spec implementation).

## Assumptions

- Manuscripts in the recall corpus are hand-annotated by
  Manuel (single annotator v1; Clarifications §3
  defers dual annotation).
- The corpus is published openly (Clarifications §4).
  We accept the small risk that future training data
  may include these annotations; the value of public
  reproducibility outweighs it.
- The shields.io JSON endpoint format is stable; we
  generate it via a small script in CI and host the
  result on GitHub Pages.
- Aggregate recall is the primary public metric;
  per-rule recall is the maintainer-facing debugging
  surface.
- F1 is computed from corpus-aggregate precision and
  corpus-aggregate recall, not per-rule averaged. This
  matches the standard ML evaluation convention.
- The 0.70 threshold (FR-011) is calibrated to be
  achievable with v1's 10-paper corpus; the threshold
  ratchets up as the corpus and rule set mature
  (governed by an explicit decision in a future spec,
  not this one).
- The corpus shape (per-paper directory with
  source + `annotations.toml`) mirrors the existing
  precision corpus's per-paper layout, so the eval-jss
  CLI doesn't need a different traversal model for
  recall vs. precision.
