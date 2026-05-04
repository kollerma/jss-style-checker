# Feature Specification: SARIF 2.1.0 Output

**Feature Branch**: `006-sarif-output`
**Created**: 2026-05-03
**Status**: Draft
**Input**: User description: "Add SARIF 2.1.0 as a fourth value for `--output` in `jss-lint` (alongside `terminal`, `json`, `html`). The renderer maps each `Violation` to a SARIF `result` and each `Rule` in the active journal to an entry under `runs[0].tool.driver.rules`. Severity translates as `error -> error`, `warning -> warning`, `info -> note`. Each result carries `ruleId`, `message.text`, `level`, and a `locations[0]` with a `physicalLocation.artifactLocation.uri` (relative to CWD or to a new `--source-root` flag) and a `region` with `startLine`, `startColumn`, and (when known) `endLine` / `endColumn`. Parse failures (`JSS-PARSE-000`) emit `notification` objects under `runs[0].invocations[0].toolExecutionNotifications`. Output is deterministic byte-for-byte for identical inputs; a JSON-schema contract test asserts conformance to SARIF 2.1.0. The existing `--output json` shape is unchanged."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Upload lint results to GitHub code scanning (Priority: P1)

A JSS author maintains their manuscript repository on GitHub and wants
the lint feedback to appear in the GitHub "Code scanning" tab — the
same surface that hosts CodeQL findings — so reviewers see violations
inline on a pull request without installing the linter locally. The
author runs `jss-lint --output sarif manuscript.tex > results.sarif`
inside a CI workflow and uploads the file with the standard
`github/codeql-action/upload-sarif` action. Each violation appears as
an annotated comment on the diff, with the right severity, rule
identifier, and source line.

**Why this priority**: SARIF is the format GitHub, CodeQL, and most CI
platforms speak natively. Without it, every consumer needs to write
glue code from `--output json`. P1 because it unblocks the entire CI
adoption story (specs 014, 011) without further work.

**Independent Test**: Given a fixture `.tex` file with one known
warning, running `jss-lint --output sarif` produces a file that (a)
validates against the SARIF 2.1.0 schema, (b) contains exactly one
`result` with the correct `ruleId`, `level`, `message.text`, and
`physicalLocation`, and (c) lists every catalogue rule under
`runs[0].tool.driver.rules`.

**Acceptance Scenarios**:

1. **Given** a fixture `.tex` file that triggers a single
   `JSS-MARKUP-001` warning at line 12 column 4, **When** the author
   runs `jss-lint --output sarif fixture.tex`, **Then** stdout contains
   a SARIF 2.1.0 document with `runs[0].results[0].ruleId =
   "JSS-MARKUP-001"`, `level = "warning"`, and a
   `physicalLocation.region` of `startLine: 12, startColumn: 4`.
2. **Given** a fixture that triggers no violations, **When** the
   author runs `jss-lint --output sarif fixture.tex`, **Then** stdout
   contains a valid SARIF document with `runs[0].results == []` and
   `runs[0].tool.driver.rules` populated for every rule in the active
   journal.
3. **Given** the SARIF output from step 1 uploaded via
   `github/codeql-action/upload-sarif`, **When** GitHub processes the
   file, **Then** the violation appears on the pull-request "Files
   changed" tab as an annotation at line 12.

---

### User Story 2 - Surface parse failures without losing them (Priority: P1)

A `JSS-PARSE-000` error is special: it means the linter could not
analyse the file at all, so no other violation could possibly fire.
The author still needs to see this in the SARIF stream, otherwise a
broken file looks identical to a clean one. Parse failures appear as
SARIF `notification` objects under
`runs[0].invocations[0].toolExecutionNotifications`, with severity
`error`, the failing artifact URI, and the parser's diagnostic text.

**Why this priority**: P1 because a silently-skipped parse failure is
strictly worse than no SARIF output — it produces a green CI on a
manuscript that nothing checked.

**Independent Test**: Given a `.tex` file that fails to parse, running
`jss-lint --output sarif` produces a SARIF document whose
`runs[0].results == []` and whose
`runs[0].invocations[0].toolExecutionNotifications` contains exactly
one entry with `level = "error"`, `descriptor.id = "JSS-PARSE-000"`,
and a populated `locations[0].physicalLocation.artifactLocation.uri`.

**Acceptance Scenarios**:

1. **Given** a fixture `.tex` file with malformed syntax that the
   parser rejects, **When** the author runs `jss-lint --output sarif
   broken.tex`, **Then** the SARIF document contains a
   `toolExecutionNotifications[0]` with `descriptor.id =
   "JSS-PARSE-000"`, `level = "error"`, and the artifact URI of
   `broken.tex`.
2. **Given** the same broken file but with `--ignore-rules
   JSS-PARSE-000`, **When** the author runs the linter, **Then** the
   parse failure still appears in `toolExecutionNotifications` (it is
   a tool-execution event, not a result), but no `result` for
   `JSS-PARSE-000` is emitted.

---

### User Story 3 - Reproducible SARIF for diffing across runs (Priority: P2)

A maintainer who runs the linter on every commit wants to diff the
SARIF output across two revisions to see what changed. This requires
that two runs over identical inputs produce byte-for-byte identical
SARIF — no embedded timestamps, no map-iteration-order non-determinism,
no machine-specific paths.

**Why this priority**: P2 because deterministic JSON output is also
already true of `--output json` — this user story is about preserving
that property, not adding it. Important enough to gate the feature,
but not the headline value.

**Independent Test**: Running `jss-lint --output sarif fixture.tex >
a.sarif` twice (or on different machines with the same `--source-root`)
produces files where `sha256(a.sarif) == sha256(b.sarif)`.

**Acceptance Scenarios**:

1. **Given** a fixture run twice on the same machine, **When** the two
   SARIF outputs are byte-compared, **Then** they are identical.
2. **Given** a fixture run on two different working directories with
   `--source-root` set to the fixture's directory, **When** the two
   SARIF outputs are byte-compared, **Then** they are identical.

---

### User Story 4 - Locate sources relative to a project root (Priority: P2)

A monorepo author runs `jss-lint --output sarif --source-root
papers/jss-2026-foo papers/jss-2026-foo/manuscript.tex` from the repo
root. The SARIF artifact URIs should be relative to `papers/jss-2026-foo`,
not the CWD, so GitHub code scanning resolves the file paths to the
correct files in the repo.

**Why this priority**: P2 because the default (CWD-relative) covers
the simple case; the flag matters only for monorepos and CI matrices
that run from a different cwd than the source root. Still required
for the feature to be useful in those layouts.

**Independent Test**: Given a fixture at `papers/foo/manuscript.tex`
and the linter invoked from the repo root with `--source-root
papers/foo`, the SARIF document contains
`physicalLocation.artifactLocation.uri = "manuscript.tex"` (not
`papers/foo/manuscript.tex` and not an absolute path).

**Acceptance Scenarios**:

1. **Given** the linter invoked without `--source-root` from a
   directory containing `manuscript.tex`, **When** SARIF is rendered,
   **Then** `artifactLocation.uri = "manuscript.tex"`.
2. **Given** the linter invoked with `--source-root subdir` from the
   parent directory and `subdir/manuscript.tex` as input, **When**
   SARIF is rendered, **Then** `artifactLocation.uri =
   "manuscript.tex"`.
3. **Given** an input outside the source root, **When** SARIF is
   rendered, **Then** `artifactLocation.uri` is the relative path
   from the source root using normal POSIX `..` segments (no
   absolute paths leak).

---

### Edge Cases

- Empty input set (no files passed): SARIF still emits a syntactically
  valid document with `results == []` and the full rule catalogue
  under `tool.driver.rules`.
- Multi-file run: each violation's `artifactLocation.uri` reflects its
  own file; results from different files coexist in a single
  `runs[0].results` array.
- Rule with `endLine`/`endColumn` known vs. unknown: when known,
  `region` includes both; when unknown, `region` carries `startLine`
  and `startColumn` only (SARIF treats absent `endLine` as
  "to end of `startLine`").
- A violation suppressed by `--ignore-rules` does NOT appear in
  `results` and does NOT appear under `suppressions[]` (filtering is
  upstream of the renderer; this matches how `terminal` / `json` /
  `html` already behave).
- Output exceeds GitHub's 10 MB SARIF cap: the renderer does not
  split output across multiple runs; the user is expected to scope
  the input set if they hit the cap. (The 172-paper corpus produces
  far less than 10 MB — see Assumptions.)
- A future spec (008) introduces fixes; this spec does not emit
  `fixes[]` and downstream consumers must not rely on its absence
  meaning "no fix exists".

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `jss-lint --output sarif` MUST be accepted as a fourth
  value for `--output`, alongside the existing `terminal`, `json`, and
  `html` values.
- **FR-002**: The SARIF document MUST conform to the SARIF 2.1.0
  schema (OASIS standard, schema URL
  `https://json.schemastore.org/sarif-2.1.0.json`).
- **FR-003**: The SARIF document MUST contain exactly one element in
  `runs[0]` and use `runs[0].tool.driver.name = "jss-lint"` with the
  installed package version under `tool.driver.version`.
- **FR-004**: Every rule defined in the active journal's catalogue
  (i.e., every entry of `_catalogue_data.RULES` not filtered out by
  the journal) MUST appear under `runs[0].tool.driver.rules` with
  fields `id`, `name`, `shortDescription.text`, `fullDescription.text`,
  `defaultConfiguration.level`, and `helpUri` (when known). Rules with
  no hits MUST still appear there.
- **FR-005**: Every emitted `Violation` MUST become exactly one entry
  in `runs[0].results` with `ruleId` matching its rule, `level` from
  the severity mapping (`error→error`, `warning→warning`,
  `info→note`), `message.text` equal to the violation's rendered
  message, and a single `locations[0]` element.
- **FR-006**: `locations[0].physicalLocation.artifactLocation.uri`
  MUST be a relative POSIX-style path. By default it is relative to
  CWD; if `--source-root <DIR>` is provided, it is relative to
  `<DIR>`. Paths outside the source root are emitted with `..`
  segments rather than absolute paths.
- **FR-007**: `locations[0].physicalLocation.region` MUST contain
  `startLine` and `startColumn` (both 1-based, matching the
  violation's location). When the violation carries an `endLine` and
  `endColumn`, those MUST also be emitted.
- **FR-008**: `JSS-PARSE-000` events MUST be emitted as entries under
  `runs[0].invocations[0].toolExecutionNotifications` with
  `descriptor.id = "JSS-PARSE-000"`, `level = "error"`, the source
  artifact URI in `locations[0]`, and the parser diagnostic in
  `message.text`. They MUST NOT also appear under `runs[0].results`.
- **FR-009**: `runs[0].invocations[0]` MUST also carry
  `executionSuccessful: true` whenever the run completed without an
  internal crash (parse failures do not flip this; an uncaught
  exception in the linter does).
- **FR-010**: The SARIF rendering function MUST be deterministic:
  given the same `Report` and config, two invocations MUST produce
  byte-for-byte identical bytes. No timestamps, host names, PIDs,
  random GUIDs, or unsorted dicts may leak into output.
- **FR-011**: The renderer MUST honour `--ignore-rules` upstream: a
  violation filtered by `ignore_rules` MUST NOT appear in `results`
  and MUST NOT appear under `runs[0].results[].suppressions[]`. A
  rule that is fully ignored still appears under `tool.driver.rules`.
- **FR-012**: The existing `--output json` byte shape MUST remain
  unchanged by this feature. A regression test asserts equality with
  a stored golden artefact.
- **FR-013**: A contract test MUST validate the SARIF output against
  the official SARIF 2.1.0 JSON schema for at least: clean run, single
  warning, single error, multi-file run, parse-error run.
- **FR-014**: `--source-root` MUST default to the current working
  directory when not provided, and MUST be a string acceptable
  wherever `--output sarif` is meaningful (it is silently ignored for
  other output formats so a single CI invocation can be used).

### Key Entities

- **SARIF run**: The single `runs[0]` object — bundles one tool
  invocation, its rule descriptors, its results, and its tool-
  execution notifications.
- **SARIF tool driver**: `runs[0].tool.driver` — describes `jss-lint`
  itself: name, version, the URI of its information page, and the
  full rule catalogue.
- **SARIF result**: One per emitted violation. Carries the rule id,
  the human-readable message, the severity-mapped level, and the
  physical location (file URI + 1-based region).
- **SARIF notification**: One per `JSS-PARSE-000`. Lives under the
  invocation, not under results, because it describes a tool-
  execution failure rather than a finding within a successfully
  analysed file.
- **Source root**: A filesystem directory used as the base for all
  artifact URIs in the output. Defaults to CWD; overridable via
  `--source-root`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of SARIF documents produced by the renderer
  validate against the SARIF 2.1.0 JSON schema across the contract-
  test fixture set (clean run, single warning, single error,
  multi-file, parse-error).
- **SC-002**: Two invocations of `jss-lint --output sarif` over the
  same input on the same machine produce byte-identical output (sha256
  match) for 100% of the eval corpus (currently 172 manuscripts).
- **SC-003**: An author-style end-to-end test — running the linter on
  a pull request and uploading the SARIF via the standard GitHub
  action — surfaces every pre-existing violation as an inline
  annotation on the diff, with no SARIF schema rejection by GitHub.
- **SC-004**: The pre-existing `--output json` golden test passes
  unchanged after this feature is merged.
- **SC-005**: Adding the SARIF renderer adds zero new third-party
  runtime dependencies (the SARIF document is plain JSON; schema
  validation is a test-time dependency only).
- **SC-006**: SARIF output for the largest manuscript in the corpus
  remains under GitHub's 10 MB code-scanning cap.

## Assumptions

- The 172-paper eval corpus produces SARIF documents well under
  GitHub's 10 MB per-file cap, so multi-run pagination is not needed
  in this spec. (If a future user hits the cap, the workaround is to
  scope the input set; revisiting pagination is out of scope here.)
- A violation's `endLine`/`endColumn` may be unknown for some rules;
  callers of the renderer must accept absent end-positions as valid
  SARIF (the spec allows omitting them).
- `--ignore-rules` filtering is performed upstream of any renderer
  and is shared across `terminal`, `json`, `html`, and `sarif`. This
  spec does not change that filtering behaviour.
- `_catalogue_data.RULES` is the single source of truth for rule
  metadata used in `tool.driver.rules`. The catalogue is frozen as of
  spec 003; new rules added by future specs will be picked up
  automatically.
- Schema validation in tests uses the official SARIF 2.1.0 schema as
  a vendored test fixture or a `jsonschema`-loaded URL; the choice is
  a plan-level decision, not a spec-level one.
- Fixes (`fixes[]`) are deferred to spec 008. Consumers of SARIF must
  not infer "no fix is possible" from the absence of `fixes[]` in
  this spec's output.
- The `--source-root` flag is silently ignored for `--output
  terminal|json|html`; this lets a single CI invocation pass it
  unconditionally.
