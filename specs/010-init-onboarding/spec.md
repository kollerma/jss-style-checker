# Feature Specification: `jss-lint init` Interactive Bootstrap

**Feature Branch**: `010-init-onboarding`
**Created**: 2026-05-03
**Status**: Draft
**Input**: User description: "Add `jss-lint init [PATH]` subcommand. Behaviour: scan the manuscript, run all rules, group violations by rule and confidence, then write a `.jss-lint.toml` next to the source with: severity overrides where the default is too noisy, an `ignore-rules` list for rules whose precision on this corpus is below a configurable threshold, and an inline comment explaining why each suppression was added. Print a summary table: \"Found 87 violations across 14 rules. Focus first on these 5 high-precision must-fix rules (23 violations).\" Refuse to overwrite an existing `.jss-lint.toml` without `--force`. Operate read-only when `--dry-run` is passed."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - First-time author bootstraps a config (Priority: P1)

A JSS author has never used the linter. Their manuscript has 87
mechanical violations across 14 rules. They run `jss-lint init
manuscript.tex` and the linter writes a `.jss-lint.toml` next to
the file with sensible suppressions, then prints a summary like
"Found 87 violations across 14 rules. Focus first on these 5
high-precision must-fix rules (23 violations)." The author runs
`jss-lint manuscript.tex` again and now sees 23 actionable
findings instead of 87.

**Why this priority**: P1 because the wall-of-warnings is the
single biggest adoption barrier. `init` converts "the linter is
too noisy" into "here are the 23 things you should fix today".

**Independent Test**: Given a fixture with 12 violations across
4 rules of varying precision, `jss-lint init fixture.tex` writes
a `.jss-lint.toml` whose `ignore_rules` field includes only the
rules whose corpus precision is below the threshold; the printed
summary names exactly the high-precision rules and their
violation counts.

**Acceptance Scenarios**:

1. **Given** a manuscript with 87 violations across 14 rules
   and a precision-history database where 9 of those rules
   have ≥90% precision, **When** `jss-lint init` runs, **Then**
   the written `.jss-lint.toml` includes the other 5 rules in
   `ignore_rules` and the summary names exactly 9 must-fix
   rules.
2. **Given** a manuscript with 0 violations, **When** `init`
   runs, **Then** the written `.jss-lint.toml` is the
   *minimal* config (no `ignore_rules`, no severity overrides)
   and the summary says `Found 0 violations`.

---

### User Story 2 - Refuse to overwrite without `--force` (Priority: P1)

The author runs `jss-lint init` again on a project that already
has a `.jss-lint.toml`. The CLI refuses to overwrite, exits
non-zero, and tells the user to pass `--force`. They re-run
with `--force` and the file is overwritten.

**Why this priority**: P1 because clobbering a hand-tuned config
silently is a P0 trust failure. The first-time `init` is
harmless; the second-time `init` must be opt-in.

**Independent Test**: Two consecutive `jss-lint init` calls in a
directory; the second exits non-zero and the file is
byte-identical to its post-first-run state.

**Acceptance Scenarios**:

1. **Given** an existing `.jss-lint.toml`, **When** `jss-lint
   init` runs without `--force`, **Then** exit code is 2,
   stderr says `refusing to overwrite ... use --force`, and
   the file is byte-unchanged.
2. **Given** the same setup with `--force`, **When** the user
   re-runs, **Then** the file is overwritten and the summary
   prints normally.

---

### User Story 3 - Audit mode (read-only summary) (Priority: P2)

The author wants to see what `init` *would* do without writing
a file. They run `jss-lint init --dry-run manuscript.tex`. The
linter prints the same summary table and the proposed config
contents to stdout; nothing is written.

**Why this priority**: P2 because the read-only preview is the
trust-building path before adoption. Important enough to ship in
this spec; not gating because the user can also pass `--force`
on the second run after reading their first config.

**Independent Test**: `jss-lint init --dry-run` prints the
proposed config to stdout and does NOT create or modify
`.jss-lint.toml` on disk.

**Acceptance Scenarios**:

1. **Given** a manuscript and no existing config, **When**
   `--dry-run` runs, **Then** stdout contains the full
   proposed TOML config including comments AND no
   `.jss-lint.toml` exists on disk.
2. **Given** an existing config and `--dry-run`, **When** the
   command runs, **Then** stdout shows the *would-be-new*
   config; the existing file is unchanged.

---

### User Story 4 - Inline comments explain each suppression (Priority: P2)

The author opens the generated `.jss-lint.toml`. Every entry in
`ignore_rules` is preceded by a comment explaining why it was
suppressed (e.g., `# JSS-MARKUP-005: precision 0.74 on this
corpus, below the 0.90 threshold`). The author can decide
whether to keep the suppression or remove it.

**Why this priority**: P2 because annotated config is what turns
a black-box generated file into a maintainable artefact. Without
the comments, every suppression is a mystery on the next
re-`init`.

**Independent Test**: Run `jss-lint init` on a fixture where one
rule is suppressed; the generated TOML contains a comment naming
that rule and giving the precision value.

**Acceptance Scenarios**:

1. **Given** a fixture and a precision-history DB where
   `JSS-MARKUP-005` has precision 0.74, **When** `init` runs
   with threshold 0.90, **Then** the TOML contains a comment
   `# JSS-MARKUP-005: precision 0.74 (corpus-wide), below 0.90`
   immediately above the rule id in `ignore_rules`.

---

### User Story 5 - Configurable precision threshold (Priority: P3)

A maintainer with strict standards wants the threshold raised
to 95%. They run `jss-lint init --threshold 0.95
manuscript.tex`. The generated config suppresses any rule whose
corpus precision is below 0.95.

**Why this priority**: P3 because the default 0.90 (matching
Constitution §VI) covers the headline use case. The flag is a
small affordance for power users.

**Independent Test**: Same fixture, two `init` runs at
threshold 0.85 and 0.95; the second produces strictly more
suppressions.

**Acceptance Scenarios**:

1. **Given** a fixture with rules at precision 0.92 and 0.97,
   **When** `--threshold 0.95` runs, **Then** the rule at
   0.92 is suppressed and the rule at 0.97 is not.

---

### Edge Cases

- The precision-history DB is missing (no spec-002 install): the
  threshold check is skipped; no rule is suppressed by precision
  alone. The summary names this gracefully ("no precision data
  available; suppressing nothing automatically").
- The DB exists but has no row for a rule (e.g., a brand-new
  rule): treat as "unknown precision", do NOT suppress, list
  the rule in the summary as "untriaged".
- `--threshold` is outside `[0, 1]`: exit 2 with stderr error.
- The PATH argument points to a directory: scan all `.tex` /
  `.Rnw` / `.Rmd` files in it, aggregate violations across
  files, write a single `.jss-lint.toml` at the directory root.
- The manuscript has 0 violations: the generated config is
  minimal (no `ignore_rules`); the summary says `0 violations`.
- The user has set `JSS_LINT_HOME` (a hypothetical env var)
  to a custom config dir: out of scope for this spec; `init`
  always writes next to the source / scan root.
- Generated TOML is written via tempfile + `os.replace`
  (atomic, mirrors spec 008's auto-fix safety).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `jss-lint init [PATH]` MUST be added as a
  subcommand. PATH may be a single file or a directory; default
  is the current directory.
- **FR-002**: `init` MUST run the read-only lint pass against
  PATH and aggregate the resulting violations by `rule_id`.
- **FR-003**: When the precision-history DB
  (`eval/precision-history.db`) is available locally, `init`
  MUST consult it for each rule's corpus-wide precision.
- **FR-004**: `init` MUST write a `.jss-lint.toml` next to PATH
  (same directory) containing:
  - An `ignore_rules` list of rule ids whose precision is below
    the threshold.
  - A comment above each suppressed rule explaining the
    precision value and the threshold.
  - Top-level `journal = "jss"` (current default; reflective).
- **FR-005**: `init` MUST refuse to overwrite an existing
  `.jss-lint.toml` unless `--force` is set. Refusal exits 2
  with a stderr message naming the file.
- **FR-006**: `--dry-run` MUST print the proposed TOML to
  stdout AND the summary table to stderr; it MUST NOT write
  to disk.
- **FR-007**: `--threshold T` MUST accept a float in `[0, 1]`;
  default is `0.90` (matches Constitution §VI). An out-of-range
  value MUST exit 2 with a stderr error.
- **FR-008**: The summary table MUST list the *must-fix* rules
  (those above the threshold AND with at least one violation),
  sorted by violation count descending. The table is printed
  to stderr; the proposed config (under `--dry-run`) goes to
  stdout.
- **FR-009**: When the precision-history DB is missing, `init`
  MUST proceed with NO precision-based suppressions and MUST
  print a stderr note: `no precision data available;
  suppressing nothing automatically`.
- **FR-010**: When a rule has no row in the DB, `init` MUST
  treat it as "untriaged" — NOT suppressed, but mentioned in
  the summary.
- **FR-011**: The generated TOML's structure MUST be a valid
  superset of the existing `.jss-lint.toml` schema (per spec
  001's config contract); existing config consumers in the
  CLI MUST parse the generated file without modification.
- **FR-012**: `init` MUST NOT modify any file other than the
  generated `.jss-lint.toml`. The source manuscripts are
  read-only.
- **FR-013**: `init` MUST be deterministic: given the same
  input set + DB + threshold, two invocations produce
  byte-identical TOML.
- **FR-014**: The summary table MUST include both the
  total-violations count and the unique-line-violations count
  (some rules can re-fire on the same line). The two numbers
  give the user a sense of "how many distinct things are
  wrong".

### Key Entities

- **Triage classification**: One of `must-fix` (precision ≥
  threshold), `suppressed` (precision < threshold), or
  `untriaged` (no DB row).
- **Generated config**: A TOML document written by `init` with
  inline comments. The schema is the standard
  `.jss-lint.toml`; the comments are additive.
- **Threshold**: A float in `[0, 1]`, default `0.90`. Drives
  the `must-fix` / `suppressed` partition.
- **Summary table**: A two-section presentation: (1) totals,
  (2) per-rule rows for must-fix rules, sorted by violation
  count.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For a manuscript with N violations across R
  rules, where K rules have precision ≥ threshold, the
  summary table lists exactly K rules and the generated
  `.jss-lint.toml` `ignore_rules` list contains exactly the
  R-K rules below threshold.
- **SC-002**: Re-running `jss-lint <manuscript.tex>` against
  the generated config produces a violation set whose rule
  ids are a subset of the must-fix rule list.
- **SC-003**: `--dry-run` produces zero filesystem mutations
  across the entire scan tree.
- **SC-004**: An existing `.jss-lint.toml` is byte-identical
  before and after a no-`--force` `init` run.
- **SC-005**: With `--force`, the generated TOML is byte-
  identical to a fresh `init` invocation in the same
  directory.
- **SC-006**: When the precision DB is absent, `init`
  succeeds, the generated config has no `ignore_rules`,
  and the stderr note is printed exactly once.

## Assumptions

- The precision-history DB schema (spec 002) exposes a
  per-rule corpus-wide precision number; `init` queries the
  most recent run.
- TOML output uses `tomli_w` (a small read/write companion to
  the existing `tomli` runtime dep). If the standard library
  Python ≥3.11 `tomllib` ever gains write support, that's the
  preferred path; the plan picks the right answer at
  implementation time.
- The summary table is rendered with `rich`'s `Table`
  primitive; no curses, no full-screen UI.
- Atomic write semantics mirror spec 008 auto-fix: tempfile
  + `os.replace` in the parent directory.
- The generated TOML is written with two-space indent and a
  trailing newline; deterministic across hosts.
- The current spec ships only the precision-based
  suppression logic. Future iterations may add user-driven
  per-rule prompts ("the linter found 12 of these — do you
  want to suppress?") in a follow-up spec.
