# Feature Specification: JSS-guide Rule Mapping

**Feature Branch**: `007-jss-guide-mapping`
**Created**: 2026-05-03
**Status**: Draft
**Input**: User description: "Extend the existing `Rule` dataclass and `_catalogue_data.RULES` metadata so every rule carries a `guide_section` string (e.g., `\"§3.2 Citations\"`) and a `guide_url` URL pointing to the public JSS author-guide HTML/PDF anchor that defines the rule. Render `guide_section` in terminal output (\"see §3.2\"), include both fields in JSON output, include them in SARIF (006) as `helpUri` and `shortDescription`, and in HTML output as a hyperlink. Add a contract test that fails CI when any rule in the catalogue is missing either field. A JSON file under `docs/jss-guide/index.json` lists the canonical anchor URLs so they can be updated centrally when the JSS guide is republished."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Author sees the canonical guide section in terminal output (Priority: P1)

A JSS author runs `jss-lint manuscript.tex` and gets back a list of
violations. For every violation the terminal output cites the JSS
author guide section that defines the rule (e.g., `JSS-CITE-002 line
42 col 7: prefer \citet{} over \cite{} (see §3.2 Citations)`). The
author can immediately consult the guide instead of guessing what
"the rule" means or asking the editor.

**Why this priority**: P1 because the entire value of the linter to
authors is "tell me what the journal expects, with proof". An
internal rule id without a guide reference is a black box. With the
section number every violation becomes self-explanatory.

**Independent Test**: Given a fixture that triggers a single rule,
running `jss-lint --output terminal` produces output containing the
exact `Rule.guide_section` string for that rule.

**Acceptance Scenarios**:

1. **Given** a fixture that violates `JSS-CITE-002` and a catalogue
   entry with `guide_section = "§3.2 Citations"`, **When** the author
   runs `jss-lint manuscript.tex`, **Then** stdout contains
   `(see §3.2 Citations)` on the violation's line.
2. **Given** a fixture that triggers a tool-side rule (e.g., a
   parse failure mapped to `JSS-PARSE-000`), **When** the author runs
   the linter, **Then** the violation line does NOT contain a
   `(see ...)` suffix (sentinel rules suppress the cite).

---

### User Story 2 - Editor follows the guide URL from JSON / SARIF / HTML (Priority: P1)

A JSS desk editor runs the linter on a submitted manuscript and
reads the SARIF or HTML report. Every entry includes a hyperlink to
the JSS author-guide URL that defines the rule. Clicking through
takes the editor (or a web reviewer) to the exact paragraph that
the violation cites.

**Why this priority**: P1 because reviewers and editors do not
memorise rule ids — they need a URL to verify a finding before
asking the author to fix it.

**Independent Test**: Given a fixture that triggers a single rule
whose `guide_url` resolves to a real URL via `docs/jss-guide/
index.json`, the JSON output's violation entry contains a
`guide_url` field equal to that URL, the SARIF output's rule
descriptor carries it as `helpUri`, and the HTML output renders an
anchor.

**Acceptance Scenarios**:

1. **Given** a fixture triggering `JSS-CITE-002`, **When** `jss-lint
   --output json` runs, **Then** the violation entry has
   `"guide_section": "§3.2 Citations"` and `"guide_url":
   "https://www.jstatsoft.org/.../section-3-2"`.
2. **Given** the same fixture with `--output sarif`, **When** SARIF
   is rendered, **Then** the `tool.driver.rules` entry for
   `JSS-CITE-002` carries `helpUri` equal to the same URL and
   `shortDescription.text` references the guide section.
3. **Given** the same fixture with `--output html`, **When** the
   HTML is rendered, **Then** the violation row contains an anchor
   `<a href="...">§3.2 Citations</a>`.

---

### User Story 3 - Catalogue contract test fails CI when a citation is missing (Priority: P1)

A contributor adds a new rule to `_catalogue_data.RULES` and forgets
to populate `guide_section` / `guide_url`. CI fails with a clear
message naming the rule and the missing field, before the rule can
be merged.

**Why this priority**: P1 because the value of the citation
contract is enforcement — if it can drift, it will drift, and
within a few releases citations become unreliable.

**Independent Test**: Run `pytest tests/unit/test_catalogue.py::
test_every_rule_cites_guide` against a deliberately-broken catalogue
that drops `guide_section` from one rule. The test must fail with
the rule id named in the failure message.

**Acceptance Scenarios**:

1. **Given** a catalogue where every citable-category rule has
   `guide_section` and `guide_url` populated, **When** the contract
   test runs, **Then** it passes.
2. **Given** a catalogue where one citable-category rule has
   `guide_section = ""`, **When** the contract test runs, **Then**
   it fails with a message naming the rule id and `guide_section`.
3. **Given** a catalogue where a tool-side rule has `guide_section =
   "internal"` and `guide_url = None`, **When** the contract test
   runs, **Then** it passes (sentinel is valid).

---

### User Story 4 - Centralised URL update when JSS republishes the guide (Priority: P2)

The JSS author guide is republished and every section gets a new
URL. A maintainer updates `docs/jss-guide/index.json` in a single
PR; no edits to `_catalogue_data.RULES` are needed and every
renderer's URLs update accordingly.

**Why this priority**: P2 because re-publication is rare (every
1–3 years) but the cost of *not* having central indirection is
~50 line edits scattered across the catalogue every time, with the
attendant risk of misses.

**Independent Test**: Edit `docs/jss-guide/index.json` to change one
section's URL, run the renderers against a fixture that hits that
rule, and confirm the rendered URL changed.

**Acceptance Scenarios**:

1. **Given** an updated `index.json` with a new URL for `§3.2
   Citations`, **When** the linter runs against a fixture that hits
   `JSS-CITE-002`, **Then** terminal/JSON/SARIF/HTML all show the
   new URL.
2. **Given** an `index.json` that omits a section that a rule
   references, **When** the catalogue contract test runs, **Then**
   it fails with a message naming the rule id and the missing
   section.

---

### Edge Cases

- A rule cites a section that exists in `index.json` but the URL
  field is null: contract test fails with `guide_url=null`.
- The same `guide_section` is cited by multiple rules (expected,
  e.g., several `JSS-CITE-*` rules under §3.2 Citations): each
  rule independently records the same section + URL; the catalogue
  test does not require uniqueness.
- A rule's `guide_section` contains the section number but no
  title (e.g., `"§3.2"`): treat as legal but discouraged; renderers
  treat the entire string as opaque.
- Tool-side rule (sentinel `"internal"`) violations from
  `JSS-PARSE-000` etc. render WITHOUT the `(see ...)` suffix in
  terminal output and WITHOUT a hyperlink in HTML; the JSON entry
  contains `guide_section: "internal", guide_url: null`.
- The JSS author-guide page does not expose an anchor for the
  cited paragraph: `index.json` records the page-level URL; the
  citation is still valid (page-level coverage > nothing).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The public `Rule` dataclass MUST gain two fields:
  `guide_section: str` and `guide_url: str | None`. Both fields are
  exposed as part of the public catalogue (no leading-underscore
  attribute).
- **FR-002**: Every rule in `_catalogue_data.RULES` MUST populate
  `guide_section`. Rules in citable categories (`markup`, `style`,
  `naming`, `preamble`, `bibliography`, `width`) MUST also populate
  `guide_url` with a non-empty string that resolves through
  `docs/jss-guide/index.json`.
- **FR-003**: Tool-side rules (categories `internal`, `parse`)
  MUST populate `guide_section = "internal"` and `guide_url = None`.
  This sentinel is the only legal way to opt out of a real
  citation.
- **FR-004**: A new file `docs/jss-guide/index.json` MUST be the
  single source of truth for guide URLs. Schema:
  `{"sections": {"§3.2 Citations": "https://...", ...}}`. Every
  citable rule's `guide_url` MUST appear as a value in this map (or
  resolve via the section name as the key).
- **FR-005**: Terminal output MUST render the violation message
  followed by `(see <guide_section>)` for citable rules. Sentinel
  rules MUST render without the `(see ...)` suffix.
- **FR-006**: JSON output MUST include `guide_section` and
  `guide_url` on every violation entry, with `null` for sentinel
  rules. The pre-spec-007 JSON shape gains exactly two new keys per
  violation; existing keys retain their order under
  `sort_keys=True`.
- **FR-007**: SARIF output MUST emit `guide_url` as the
  `helpUri` of each `runs[0].tool.driver.rules[]` entry (when
  non-`None`) and MUST include `guide_section` in the rule's
  `shortDescription.text` (e.g., `"<title> (§3.2 Citations)"`).
  Sentinel rules omit `helpUri`.
- **FR-008**: HTML output MUST render `guide_section` as an
  `<a>` element pointing at `guide_url`. Sentinel rules render the
  section as plain text without an anchor.
- **FR-009**: A contract test
  `tests/unit/test_catalogue.py::test_every_rule_cites_guide`
  MUST fail CI when any rule's required field is missing or
  malformed (per FR-002 / FR-003). The failure message MUST name
  the offending rule id and the offending field.
- **FR-010**: A second contract test MUST verify that every
  citable-category rule's `guide_url` corresponds to some value
  in `docs/jss-guide/index.json` (or the rule's `guide_section`
  appears as a key in the map). Inconsistencies fail CI with a
  message naming the rule and the orphan key.
- **FR-011**: The 50+ existing rules in the catalogue MUST be
  backfilled with `guide_section` / `guide_url` values during
  this spec. Backfill values cite the public JSS author guide at
  `https://www.jstatsoft.org/about/submissions` (or its successor
  URL recorded in `index.json`).
- **FR-012**: Renderer changes MUST preserve every other byte of
  the existing terminal / JSON / HTML / SARIF output (modulo the
  two new keys / one new attribute per renderer). Existing
  golden-fixture tests update accordingly in this spec; later
  specs do not regress them.

### Key Entities

- **Rule (extended)**: Existing dataclass; gains
  `guide_section: str` and `guide_url: str | None`. No other
  fields change.
- **Guide-URL index** (`docs/jss-guide/index.json`): Mapping of
  human-readable section labels (e.g., `"§3.2 Citations"`) to
  public URLs. The single point of update when the JSS guide is
  republished.
- **Citable category set**: The frozen set `{"markup", "style",
  "naming", "preamble", "bibliography", "width"}`. Membership in
  this set determines whether `guide_url` is mandatory.
- **Sentinel value**: The literal string `"internal"` for
  `guide_section` paired with `None` for `guide_url`, used by
  tool-side rules.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of catalogue rules have `guide_section`
  populated; 100% of citable-category rules have a non-`None`
  `guide_url`. The contract test enforces both numbers.
- **SC-002**: 100% of citable-category rules' `guide_url` values
  resolve through `docs/jss-guide/index.json` (no orphan URLs in
  the catalogue).
- **SC-003**: Terminal output for a citable-category violation
  contains `(see <guide_section>)` exactly once. Terminal output
  for a sentinel violation contains zero `(see ...)` suffixes.
- **SC-004**: For every existing renderer (terminal, JSON, HTML,
  SARIF) the byte shape is unchanged except for the documented
  per-violation additions; the existing per-format golden-fixture
  tests pass after the additions are accounted for.
- **SC-005**: Re-publication exercise: changing a single URL in
  `docs/jss-guide/index.json` updates every rendered URL for the
  affected section without any other source edit. The contract
  test confirms no orphan citations remain.
- **SC-006**: Contributor onboarding: adding a new rule with
  missing `guide_section` results in a CI failure whose message
  names the rule and the missing field within 1 second of test
  startup.

## Assumptions

- The public JSS author guide
  (https://www.jstatsoft.org/about/submissions) is stable enough
  that mid-spec re-publication is unlikely; if it changes during
  this spec, the maintainer updates `index.json` and re-runs the
  contract tests.
- The 6 citable categories listed in FR-002 cover the entire
  current 58-rule catalogue from spec 003; new categories added in
  later specs (e.g., a hypothetical `figures` category) extend the
  set as a one-line edit in `_catalogue_data.py`.
- A rule whose `guide_section` cites multiple paragraphs records
  only the single most-canonical (highest-numbered) one; the
  description carries the rest. This keeps every renderer's
  surface scalar.
- `helpUri` already exists on SARIF rule descriptors (spec 006);
  spec 007 wires `guide_url` into it, replacing the previous
  `helpUri` source.
- The `docs/jss-guide/index.json` file is plain JSON and edited
  by hand. There is no JSON-schema for `index.json` in this spec;
  the contract tests are the validation layer.
