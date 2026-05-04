# Feature Specification: `jss-lint explain` Subcommand

**Feature Branch**: `009-explain-command`
**Created**: 2026-05-03
**Status**: Draft
**Input**: User description: "Add a new `explain` subcommand to `jss-lint`: `jss-lint explain RULE-ID [--example] [--format markdown|terminal]`. The subcommand prints the rule's full metadata (id, severity, category, JSS-guide section + URL from spec 007), a one-paragraph plain-language explanation, a \"bad\" example fragment, a \"good\" example fragment, and (when `--example` is passed) the corresponding fixture pair from `tests/fixtures/violations/`. `jss-lint explain` with no argument lists all rules grouped by category. `--format markdown` produces output that pastes cleanly into GitHub issues / PR comments. The explanation text lives in `_catalogue_data.RULES[rule_id][\"explanation\"]` (a new field) so explanations are version-controlled alongside the rule logic."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Author looks up a rule id (Priority: P1)

A JSS author sees `JSS-CITE-002` in their lint output and runs
`jss-lint explain JSS-CITE-002`. The terminal prints the rule's
human-readable explanation, the JSS guide section it cites (from
spec 007), a bad-example fragment, and a good-example fragment.
The author understands the rule without context-switching to a
browser.

**Why this priority**: P1 because rule ids alone make the tool
feel arbitrary. The explainer turns every violation into a
self-contained mini-lesson and is the bridge between "the linter
flagged this" and "I know what to do".

**Independent Test**: Given a fixture catalogue entry with a
populated `explanation` and `example_bad` / `example_good`,
running `jss-lint explain JSS-CITE-002` produces stdout containing
all four pieces (metadata, explanation, bad, good).

**Acceptance Scenarios**:

1. **Given** a catalogue entry for `JSS-CITE-002` with full
   metadata, **When** `jss-lint explain JSS-CITE-002` runs,
   **Then** stdout contains the rule id, severity, category, JSS
   guide section, the explanation paragraph, a bad-example
   fragment, and a good-example fragment.
2. **Given** an unknown rule id `JSS-FOO-999`, **When**
   `jss-lint explain JSS-FOO-999` runs, **Then** the CLI exits 2
   with a stderr message naming the unknown rule and listing the
   `did-you-mean?` candidates within edit distance 2.
3. **Given** a catalogue entry whose `example_bad` / `example_good`
   are `None`, **When** `jss-lint explain` runs, **Then** the bad
   / good sections render as `(no example available)` and the rest
   of the entry renders normally.

---

### User Story 2 - Markdown output for issue comments (Priority: P1)

A maintainer reviewing a PR wants to point a contributor at a rule.
They run `jss-lint explain JSS-CITE-002 --format markdown` and
copy-paste the output into a GitHub PR comment. The output
renders cleanly: heading for the rule id, list for the metadata,
fenced code blocks for the examples, an inline link for the JSS
guide section.

**Why this priority**: P1 because reviewer adoption depends on
mechanical sharing of rule explanations. Without markdown, every
explanation has to be re-typed for every PR comment.

**Independent Test**: Run `jss-lint explain JSS-CITE-002 --format
markdown` and pipe the output through a Markdown renderer; the
result has the expected structure (heading, list, code blocks,
link).

**Acceptance Scenarios**:

1. **Given** the same fixture as Story 1, **When**
   `--format markdown` is set, **Then** stdout starts with `#
   JSS-CITE-002` and contains a `## Bad` and `## Good` section,
   each followed by a fenced code block with the language tag
   `tex`.
2. **Given** the JSS guide section is `§3.2 Citations` with URL
   `https://...`, **When** the markdown is rendered, **Then** the
   output contains `[§3.2 Citations](https://...)`.

---

### User Story 3 - Browse all rules grouped by category (Priority: P2)

A new author runs `jss-lint explain` with no argument to see what
rules exist. The CLI prints a categorised listing: each category
header followed by a one-line summary per rule. The output is
sorted by category, then by rule id. The author scans for rules
they recognise and clicks through to detailed explanations as
needed.

**Why this priority**: P2 because the listing is the discovery
view; per-rule explain is the deep-dive view. Both are valuable;
listing is secondary because authors usually arrive via a
specific rule id from a violation.

**Independent Test**: `jss-lint explain` (no arg) prints output
whose section count equals the number of distinct categories in
`_catalogue_data.RULES`, and whose total rule-line count equals
the total catalogue size.

**Acceptance Scenarios**:

1. **Given** a 58-rule catalogue with 8 distinct categories,
   **When** `jss-lint explain` runs, **Then** stdout contains
   exactly 8 category headers and 58 rule lines.
2. **Given** the same catalogue, **When**
   `jss-lint explain --format markdown` runs, **Then** output is
   a Markdown document with `##` headers per category and bullet
   lists per rule.

---

### User Story 4 - Pull example fixtures into the output (Priority: P2)

The author runs `jss-lint explain JSS-CITE-002 --example`. In
addition to the inline example fragments, the explainer prints
the corresponding `tests/fixtures/violations/<RULE-ID>-bad.tex`
content (or its `.Rnw` / `.Rmd` variant) so the author sees a
real, in-corpus example.

**Why this priority**: P2 because synthetic-fragment examples
suffice for most rules; the fixture pull-through is a nice-to-have
for authors who want to see "the real thing".

**Independent Test**: `jss-lint explain JSS-CITE-002 --example`
produces output that includes the contents of the fixture file
when it exists; without `--example`, the output omits the
fixture pull-through.

**Acceptance Scenarios**:

1. **Given** `tests/fixtures/violations/JSS-CITE-002-bad.tex`
   exists with content `<X>`, **When** `--example` is set,
   **Then** the explainer output contains `<X>` in a fixture
   block.
2. **Given** the fixture file does not exist, **When**
   `--example` is set, **Then** the explainer prints `(no
   in-corpus fixture)` in the fixture-block position and does
   NOT exit 2.

---

### Edge Cases

- An explanation field is empty / `None`: the listing rendering
  fails the catalogue contract test from spec 007 (extended for
  this spec), so the situation never reaches a user.
- A rule id with mixed case (`jss-cite-002`): normalised to
  upper case before look-up.
- A rule id with surrounding whitespace: stripped before
  look-up.
- The `--format` value is unknown: the CLI exits 2 with a
  stderr message listing the legal values.
- The terminal is not a TTY (`jss-lint explain ... | less`):
  paging is OFF by default; the user pipes manually if they
  want it (per Clarifications, see research §3).
- A fixture file uses an encoding other than UTF-8: the
  explainer reads as UTF-8 with `errors="replace"`; non-UTF-8
  bytes are surfaced as the replacement character.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `jss-lint` MUST become a multi-command CLI: the
  default invocation `jss-lint <PATHS>` MUST continue to work
  unchanged (backward compatibility); a new subcommand `jss-lint
  explain [OPTIONS] [RULE-ID]` is added.
- **FR-002**: `jss-lint explain RULE-ID` MUST print rule
  metadata, a one-paragraph explanation, a bad-example
  fragment, and a good-example fragment.
- **FR-003**: `jss-lint explain` (no `RULE-ID`) MUST list every
  rule in the catalogue, grouped by category and sorted by rule
  id within each group.
- **FR-004**: `--format markdown` MUST emit Markdown that
  renders cleanly in GitHub: `#` heading for the rule id, `##`
  for sub-sections, fenced code blocks with `tex` language tag,
  inline links for URLs.
- **FR-005**: `--format terminal` (default) MUST emit ANSI-
  styled output suitable for an interactive terminal (using
  `rich` formatting, already a dep). Colour MUST be auto-
  disabled when stdout is not a TTY.
- **FR-006**: `--example` MUST pull through the contents of
  `tests/fixtures/violations/<RULE-ID>-bad.tex` (or `.Rnw` /
  `.Rmd` variant) when present, and surface `(no in-corpus
  fixture)` when absent. The flag is independent of `--format`.
- **FR-007**: An unknown rule id MUST cause exit 2 with a
  stderr error and a `did-you-mean?` suggestion list (edit
  distance ≤ 2 against the catalogue).
- **FR-008**: Three new fields are added to every catalogue
  entry: `explanation: str` (one paragraph plain-language),
  `example_bad: str | None`, `example_good: str | None`. The
  CI-enforced catalogue contract test from spec 007 MUST be
  extended to require non-empty `explanation` for every rule.
- **FR-009**: Tool-side rules (categories `internal`, `parse`)
  MAY have `example_bad = example_good = None`; the contract
  test allows this for these categories (mirrors the spec-007
  sentinel pattern).
- **FR-010**: An unknown `--format` value MUST cause exit 2
  with a stderr listing the legal values.
- **FR-011**: The listing view MUST be deterministic — the same
  catalogue produces the same output bytes (modulo the
  TTY-vs-pipe colour difference). Order is sort by category
  ascending, then rule id ascending.
- **FR-012**: The explain subcommand MUST NOT make any network
  calls. The `guide_url` from spec 007 is rendered as a link;
  it is not fetched.

### Key Entities

- **Rule (extended)**: Existing dataclass; gains
  `explanation: str`, `example_bad: str | None`,
  `example_good: str | None`. No other fields change.
- **Format**: Two-valued literal `"terminal" | "markdown"`. The
  CLI's `--format` flag accepts either; default is `"terminal"`.
- **Fixture pull-through**: When `--example` is set, the file
  at `tests/fixtures/violations/<RULE-ID>-bad.tex` (or `.Rnw`
  / `.Rmd`) is loaded and embedded in the output. Missing files
  produce a sentinel string.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of catalogue rules have a non-empty
  `explanation`. The contract test enforces this (extension of
  spec 007's catalogue contract).
- **SC-002**: `jss-lint explain RULE-ID` for every rule in the
  catalogue produces deterministic output (same bytes on
  repeated invocations).
- **SC-003**: `jss-lint explain RULE-ID --format markdown`
  produces output that, when piped through a CommonMark
  renderer, has zero rendering errors and the expected
  structural elements (one `#` heading, two `##` sub-sections,
  two fenced code blocks).
- **SC-004**: An unknown rule id `JSS-FOO-999` produces a
  stderr message containing the closest catalogue match within
  edit distance 2; if no match is within distance 2, the
  message lists rules in the same category prefix.
- **SC-005**: The `jss-lint <PATHS>` (no subcommand) entry-
  point continues to work unchanged; the existing test suite
  passes without modification.
- **SC-006**: README has a new section ("Learning the rules")
  documenting the explain subcommand with an example invocation
  and the format flag values.

## Assumptions

- Adding `explanation` / `example_bad` / `example_good` to
  every existing catalogue rule is a one-shot mechanical
  backfill in this spec. The text is written by the spec-009
  PR author; no automation generates it.
- `rich` (already a dep) is the right rendering library for
  terminal output; no new TUI library is introduced.
- Edit distance for `did-you-mean?` is plain Levenshtein
  computed in Python; no fuzzy-match library is added.
- A fixture pull-through reads at most a few KB; no streaming
  or paging is required.
- The Click sub-group migration is backward-compatible: the
  existing `jss-lint <PATHS>` call site is preserved as the
  group's default action OR as a `lint` subcommand alias.
  Either implementation choice satisfies FR-001; the plan
  picks the one with smaller surface (research §1).
