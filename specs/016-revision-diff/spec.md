# Feature Specification: `jss-lint diff` Between Runs

**Feature Branch**: `016-revision-diff`
**Created**: 2026-05-03
**Status**: Draft
**Input**: User description: "Add `jss-lint diff OLD.json NEW.json [--format terminal|markdown|json] [--ignore-line-drift]`. Output groups violations into `fixed` (in OLD, not in NEW), `introduced` (in NEW, not in OLD), and `unchanged`. Identity is `(rule_id, file, line, message_template)` by default; with `--ignore-line-drift`, identity drops `line` so a fix elsewhere in the file doesn't re-flag downstream violations as new. Terminal format uses colour and the same renderer as `jss-lint --mode reviewer`. Exit code is 0 when nothing introduced, 1 when new violations appear. Useful for both editorial revision rounds and CI regression detection on PR diffs."

## Clarifications

### Session 2026-05-03

- Q: Canonical identity tuple — should `severity` or `column` participate? → A: Default identity is `(rule_id, file, line, message)`. `severity` does NOT participate (a rule's severity should not change between runs of the same tool version; if it does, the violation has fundamentally changed and re-classifying as `introduced` is correct). `column` does NOT participate either: column drift on the same line is common (an author rewords a sentence) and adds no signal beyond `(file, line)`. With `--ignore-line-drift`, the tuple becomes `(rule_id, file, message)`.
- Q: When OLD and NEW are produced by different tool versions (rule renamed), do we map via a migration table or report as fixed+introduced? → A: Migration table. A `docs/jss-guide/rule-renames.json` file (initially empty) maps old rule ids to new ids. The diff command applies the map to OLD violations before identity comparison. When a rule is renamed in spec-NN, that spec's PR adds the entry to `rule-renames.json`. This avoids spurious "1 fixed, 1 introduced" on every cross-version diff.
- Q: Markdown output: GitHub-flavoured or CommonMark? → A: GitHub-flavoured CommonMark. Tables and inline code blocks render correctly on GitHub PR comments — the primary consumer of the markdown format. Pure CommonMark would force the consumer to flatten the summary count line into prose.
- Q: Is the diff three-way (vs. a baseline, e.g., "compared to clean template") ever in scope? → A: Out of scope for v1. Two-way is the headline use case (revision rounds, PR regression). Three-way introduces a transitivity question (is `unchanged` defined relative to baseline-vs-NEW or OLD-vs-NEW?) that needs its own design discussion. v1 leaves the CLI surface uncluttered for a future `--baseline` flag.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Editor sees what changed across revision rounds (Priority: P1)

A JSS editor reviews a revision (round 2 of an R&R). They run
`jss-lint manuscript.tex --output json > new.json`, then `jss-lint
diff old.json new.json` (where `old.json` is from round 1). Output
shows "fixed: 9, introduced: 2, unchanged: 12" with each group
listing the relevant violations.

**Why this priority**: P1 because the diff view is the canonical
revision-round signal. Without it, the editor reads two JSON
dumps and reconstructs the delta by hand.

**Independent Test**: Two fixture JSON files representing
before/after revisions; `jss-lint diff` produces exactly the
expected (fixed, introduced, unchanged) partition.

**Acceptance Scenarios**:

1. **Given** `old.json` with 14 violations and `new.json` with
   the same 14 minus 9 fixed plus 2 introduced (so 7 in NEW),
   **When** `jss-lint diff old.json new.json` runs, **Then**
   stdout reports `fixed: 9, introduced: 2, unchanged: 5`.
2. **Given** identical `old.json` and `new.json`, **When**
   `jss-lint diff` runs, **Then** the output reads `fixed: 0,
   introduced: 0, unchanged: N`.
3. **Given** `new.json` with strictly more violations than
   `old.json`, **When** `jss-lint diff` runs, **Then** exit
   code is 1.

---

### User Story 2 - CI regression check on PR diffs (Priority: P1)

A CI workflow runs `jss-lint --output json > new.json` on the
PR head, fetches `old.json` from the base branch's last build,
and runs `jss-lint diff old.json new.json`. When `introduced > 0`,
the CI step fails; when `introduced == 0`, the step passes
regardless of how many violations remain.

**Why this priority**: P1 because the regression check is the
practical answer to "we have 200 legacy violations; how do we
land new code without inheriting them?". The diff lets a
project ratchet the violation count down without blocking
unrelated PRs.

**Independent Test**: Two JSON fixtures simulating a
"untouched" lint run; `diff` exits 0. A "regression" pair;
`diff` exits 1.

**Acceptance Scenarios**:

1. **Given** PR base lint produced 50 violations and PR head
   lint produced the same 50 minus 1 (one fixed), **When**
   `jss-lint diff old.json new.json` runs, **Then** exit code
   is 0.
2. **Given** PR base lint produced 50 violations and PR head
   lint produced the same 50 plus 1 new, **When** `diff`
   runs, **Then** exit code is 1.

---

### User Story 3 - Line-drift normalisation (Priority: P2)

The author refactors `manuscript.tex` by inserting a new
section. Every violation downstream now has a different line
number, but the violations themselves are the same. With
`--ignore-line-drift`, identity drops `line` so the diff
recognises these as `unchanged`, not `fixed + introduced`.

**Why this priority**: P2 because line-drift false positives
are the most common diff-noise problem. Important enough to
ship in this spec; the default identity tuple is the
strict-line-aware comparison and `--ignore-line-drift` is
the practical mode.

**Independent Test**: A fixture where every violation in
NEW is shifted by +20 lines from OLD; with default identity
the diff reports all-fixed-and-all-introduced; with
`--ignore-line-drift` the diff reports all-unchanged.

**Acceptance Scenarios**:

1. **Given** OLD with 5 violations and NEW with the same 5
   violations shifted +20 lines, **When** `diff` runs with
   default identity, **Then** output is `fixed: 5,
   introduced: 5, unchanged: 0`.
2. **Given** the same setup with `--ignore-line-drift`,
   **When** `diff` runs, **Then** output is `fixed: 0,
   introduced: 0, unchanged: 5`.

---

### User Story 4 - Markdown output for PR comments (Priority: P2)

A maintainer's CI job runs `jss-lint diff --format markdown
old.json new.json` and posts the output as a PR comment. The
markdown renders cleanly: a summary line, three sub-sections
for fixed / introduced / unchanged, each with a bulleted
violation list.

**Why this priority**: P2 because the markdown format makes the
diff shareable on GitHub. Without it, CI workflows would have to
post the terminal output (with ANSI escapes) or roll their own
formatter.

**Independent Test**: Run `--format markdown`; the result has
three `##` sub-sections and renders correctly under CommonMark
(GitHub-flavoured for table support — Clarifications §3).

**Acceptance Scenarios**:

1. **Given** a non-trivial diff, **When** `--format markdown`
   runs, **Then** stdout contains `## Fixed`, `## Introduced`,
   `## Unchanged` headings and bulleted lists under each.

---

### User Story 5 - Tool-version migration via rule-rename map (Priority: P3)

Between OLD and NEW lints, a rule was renamed
(`JSS-MARKUP-005` → `JSS-MARKUP-005-A`). Without intervention
the diff reports it as one fixed (the old id) and one
introduced (the new id). With a migration map (per
Clarifications §2), the diff treats them as the same rule
and the violations show as `unchanged`.

**Why this priority**: P3 because rule renames are rare. Ship
the map mechanism in this spec but the migration data file is
empty until needed.

**Independent Test**: A migration map maps
`JSS-MARKUP-005` to `JSS-MARKUP-005-A`; OLD has one
`JSS-MARKUP-005` violation, NEW has one `JSS-MARKUP-005-A`
violation; the diff reports `unchanged: 1`.

**Acceptance Scenarios**:

1. **Given** the migration map and the fixtures above, **When**
   `diff` runs, **Then** output reports `unchanged: 1, fixed:
   0, introduced: 0`.
2. **Given** no migration map, **When** the same `diff` runs,
   **Then** output reports `unchanged: 0, fixed: 1, introduced:
   1` (the strict identity case).

---

### Edge Cases

- OLD or NEW JSON file does not exist: exit 2 with a clear
  stderr message.
- OLD or NEW JSON does not match the spec-001 schema: exit 2
  with a stderr message naming the offending file and the
  schema mismatch.
- Default identity = `(rule_id, file, line, message)`; the
  full violation message (NOT just a template) is part of the
  identity to distinguish two same-rule violations on the same
  line that flag different content.
- `--ignore-line-drift` drops `line` from the identity tuple;
  every other field is unchanged.
- `column` is NOT part of the identity (per Clarifications
  §1) — column drift is too noisy and adds no signal beyond
  line.
- A migration-map entry that maps a rule to itself is a no-op
  but legal; CI tools may produce these.
- The migration map's path is `docs/jss-guide/rule-renames.json`
  (or similar — plan picks the location); empty by default.
- Three-way diff (vs. a baseline): out of scope per
  Clarifications §4.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A new subcommand `jss-lint diff OLD.json
  NEW.json` MUST be added under the spec-009 Click group.
- **FR-002**: The subcommand MUST accept `--format
  {terminal,markdown,json}` (default `terminal`) and
  `--ignore-line-drift` (default off).
- **FR-003**: Default identity tuple:
  `(rule_id, file, line, message)`. With
  `--ignore-line-drift`, identity drops `line`.
- **FR-004**: Output groups violations into:
  - `fixed`: in OLD, not in NEW.
  - `introduced`: in NEW, not in OLD.
  - `unchanged`: in both (by identity).
- **FR-005**: Exit codes:
  - `0` when `len(introduced) == 0` (regardless of fixed
    / unchanged counts).
  - `1` when `len(introduced) > 0`.
  - `2` on usage error (missing file, schema mismatch,
    unknown `--format` value).
- **FR-006**: Terminal output MUST use the existing
  `--mode reviewer` rendering style (colour + grouped per
  rule; one-line per violation).
- **FR-007**: Markdown output uses GitHub-flavoured
  CommonMark (per Clarifications §3) with three
  sub-sections (`Fixed`, `Introduced`, `Unchanged`),
  bulleted lists, and a summary count line at the top.
- **FR-008**: JSON output MUST be deterministic (same
  inputs → same bytes) with top-level keys
  `(fixed, introduced, unchanged)` each holding an array
  of violation objects (the spec-001 violation schema).
- **FR-009**: A rule-rename migration map MUST be loaded
  from `docs/jss-guide/rule-renames.json` when present.
  Format: `{"old-rule-id": "new-rule-id", ...}`. The map
  is applied before identity comparison: every OLD
  violation's `rule_id` is replaced by its mapped value
  (when present) before the comparison runs.
- **FR-010**: When the migration map is missing, the
  comparison proceeds with no rule-rename normalisation.
  No error.
- **FR-011**: Schema validation: both JSON files MUST
  conform to the spec-001 `--output json` schema. The
  diff command validates each file before comparing; on
  mismatch, exits 2 with a stderr message.
- **FR-012**: The `unchanged` group's per-violation
  rendering uses the `line` from NEW (the current run);
  this is the line the user will see if they re-run
  `jss-lint`.

### Key Entities

- **DiffReport**: A frozen dataclass with three tuples:
  `fixed`, `introduced`, `unchanged`. Each entry is a
  spec-001 violation object.
- **Identity tuple**: A frozen tuple used as a set key for
  comparison. Default: `(rule_id, file, line, message)`.
  With `--ignore-line-drift`: `(rule_id, file, message)`.
- **Migration map**: `dict[str, str]` from old rule id to
  new rule id, loaded from JSON.
- **DiffReport renderer**: Three implementations
  (`terminal`, `markdown`, `json`) sharing the same
  `DiffReport` input.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For two identical JSON files, `diff` reports
  `(fixed=0, introduced=0, unchanged=N)` and exits 0.
- **SC-002**: For an OLD and NEW with strictly disjoint
  violations, `diff` reports
  `(fixed=|OLD|, introduced=|NEW|, unchanged=0)`.
- **SC-003**: With `--ignore-line-drift`, a NEW that is
  `OLD` shifted by a constant `Δline` reports `(fixed=0,
  introduced=0, unchanged=|OLD|)`.
- **SC-004**: A migration map that renames `R1 → R2`
  causes a single-rule rename between OLD and NEW to
  appear as `unchanged`.
- **SC-005**: Both terminal and markdown outputs are
  determinstic byte-for-byte (modulo terminal colour
  codes, which are forced off in tests).
- **SC-006**: Exit code is 0 iff `introduced == 0`,
  regardless of other counts.

## Assumptions

- The OLD and NEW files are produced by `jss-lint
  --output json` on (possibly different) runs of the same
  manuscript or a manuscript revision. They share the
  spec-001 JSON schema.
- The migration map's storage path is documented in the
  plan; the file is hand-edited and version-controlled.
- The diff is two-way only; three-way (vs. a baseline)
  is out of scope per Clarifications §4.
- `column` is not part of the identity tuple; column drift
  is too noisy on real LaTeX where small edits shift all
  subsequent column positions.
- A future spec may add `--from-baseline` for three-way
  comparisons; this spec leaves the surface free for it
  by namespacing all v1 flags under the established
  pattern.
- Terminal output reuses the existing reviewer-mode
  renderer (`output/terminal.py::render` with
  `cfg.mode = "reviewer"`); the diff command does not
  invent its own styling.
