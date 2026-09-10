# Feature Specification: Release 1.2.0 — first-time-user gaps

**Feature Branch**: `027-first-time-user-gaps`
**Created**: 2026-09-06
**Status**: Draft (aligned with `plan.md` rev 4)
**Input**: User description: "Release 1.2.0 addresses the gaps a
first-time user hits when evaluating `jss-lint` for a real JSS submission:
recall transparency (P0-A), baseline mode (P0-B), fix safety (P1-C),
version and rule-set provenance (P1-D), coloured terminal output (P1-F),
Overleaf reach (P2-E), and — added during the planning interview — a
summary of which parts of the style guide the tool does *not* check."

Cross-references are to sections of [`plan.md`](plan.md).

## Clarifications

### Session 2026-09-06 (maintainer decisions, two external review rounds)

- Q: How is an accepted finding identified in a baseline so it survives
  line-number drift? → A: **D1.** By `(rule_id, path relative to the
  baseline file's directory, message, suggestion)` with an occurrence
  count. Line numbers and columns are excluded. `suggestion` was added
  after the jss5342 replay showed the message-only key masked eight
  genuinely new findings in one revision round (plan §5.7).
- Q: The Rust engine never implemented `% jss-lint: ignore`; ship the fix
  separately? → A: **D2.** It ships inside 1.2.0, as its own PR and its
  own CHANGELOG entry, and both inline ignores and the baseline go
  through one pre-bookkeeping suppression hook in both engines.
- Q: How is per-rule recall displayed when a rule has few annotated
  instances? → A: **D3.** Three states with a 10-plant threshold:
  `measured` (integer percent), `limited (n=K)` for 1–9 plants,
  `unmeasured` for 0. Per-category recall pools the category's plants.
- Q: What is the rule-set version and what may change in which release?
  → A: **D4.** A date-stamped `ruleset_version` in the catalogue, guarded
  by a fingerprint over the catalogue-declared contract fields **and** the
  message/suggestion wording (`messages.json`). Patch releases may only
  make findings disappear; minor releases may add rules or reword; major
  releases may retire or rename. CI users pin the tool minor; a minor bump
  may require `--update-baseline`.
- Q: Should `--fix` refuse to run on a dirty git tree? → A: **D5.** No.
  Spec 008 stands; `--fix` prints an applied/skipped summary line and the
  docs state the version-control expectation.
- Q: Overleaf: workflow docs, browser zip, CLI zip? → A: **D6.** Docs plus
  a browser zip drop on the native `DecompressionStream`; CLI zip is a
  follow-up.
- Q: Scope for 1.2.0? → A: **D7.** Everything, in three phases. After the
  reviews the scope lever is guide coverage (5 days), then colour and the
  zip drop (3 days). The maintainer keeps all of it in 1.2.0.
- Q: Where does "what is not checked" appear? → A: **D8.** A validated
  `guide-coverage.yaml` beside the catalogue; a "Not checked by jss-lint"
  block under the reviewer table (terminal and HTML, hence the web app); a
  `coverage` block in JSON; a `jss-lint coverage` subcommand; a one-line
  pointer in the author footer.
- Q: Must coloured output be byte-identical across engines? → A: **D9.**
  No. The plain stream stays byte-identical and the colour *decision* is
  one identical function in both CLIs; escape bytes are per-engine
  best-effort and recorded as a documented §XIII divergence.
- Q: Make generic suggestions token-specific now or later? → A: **D10.**
  Now, before any baseline exists, because `suggestion` is a key
  component and a fingerprint input. Final scope after prototyping: ten
  rules (plan §5A); `JSS-WIDTH-001` stays generic by explicit decision.
- Q: Keep the aggregate recall floor at 0.70? → A: **D11.** No. Floor
  0.78 now, ratcheted to the shipped snapshot minus 0.03 at each release
  (the decision spec 017 FR-011 deferred).
- Q: Author-mode footer on stdout or stderr? → A: stdout. The terminal
  report is the report; a saved text report of a clean run must not be
  empty.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A clean run is honest about what it proves (Priority: P1)

An author runs `jss-lint paper.tex refs.bib` on a manuscript that passes
every rule. Today the output is empty and exit 0, which reads as an
all-clear. In 1.2.0 the run ends with a footer that says no findings does
not mean compliant, states the measured recall with its corpus size, and
points at the coverage list. In reviewer mode each category carries a
recall column (`81%`, `limited (n=4)`, `unmeasured`), the compliance line
is followed by the measured recall, and the `project` category — which has
no annotated instances — renders `unmeasured`, never `100%`.

**Why this priority**: P1 because this is the trust contract of the
release. Precision has been visible since 1.0; recall and its limits have
not, so a clean run overstates what the tool checked.

**Independent Test**: Run author mode on `tests/fixtures/compliant/*.tex`
and assert stdout is non-empty and contains the statement; run reviewer
mode on any fixture and assert the `Recall` column and footer line; run
with the `stub` journal and assert the "no recall or coverage data" line.

**Acceptance Scenarios**:

1. **Given** a compliant manuscript, **When** `jss-lint paper.tex` runs,
   **Then** exit code is 0 and stdout contains
   `No findings does not mean compliant.` followed by the measured recall
   sentence.
2. **Given** any manuscript, **When** `--mode reviewer` runs, **Then** the
   table has a fifth `Recall` column whose cells are one of an integer
   percentage, `limited (n=K)`, or `unmeasured`, and the `project`
   category shows `unmeasured`.
3. **Given** `--output json`, **When** the report is parsed, **Then** each
   category object carries `recall: {state, tp, fn, percent}` and the
   top level carries `rule_set.recall` with `run_timestamp`,
   `corpus_hash`, `min_plants`, `tp`, `fn`, `percent`.
4. **Given** `jss-lint explain JSS-XREF-003`, **When** it runs, **Then**
   the output contains `Recall: unmeasured`.
5. **Given** both engines and the same input, **When** the plain terminal,
   JSON, SARIF, and HTML outputs are compared, **Then** they are
   byte-identical.

---

### User Story 2 - The author learns what is not checked (Priority: P1)

Before submitting, an author wants to know which style-guide requirements
the tool does not cover so they can proofread those by hand. In reviewer
mode a block titled `Not checked by jss-lint` lists the directives with
status `not checked` or `partial`, one line each with a reason. `jss-lint
coverage` prints the full matrix (checked, partial, not checked, out of
scope) grouped by source, in terminal, Markdown, or JSON. The author
footer counts checked directives and points at the subcommand.

**Why this priority**: P1 because "no findings" is only meaningful next
to "what was looked for". The data already exists as a markdown review
checklist but is stale (it credits four retired rules) and reaches no
user.

**Independent Test**: The contract test over `guide-coverage.yaml` fails
when a listed rule is retired or when an active rule appears in no
directive; the reviewer block and the `coverage` subcommand render
deterministically and identically in both engines.

**Acceptance Scenarios**:

1. **Given** the shipped `guide-coverage.yaml`, **When** the contract test
   runs, **Then** every listed rule is active, every active non-internal
   rule appears in at least one directive, and every non-`checked` entry
   has a reason.
2. **Given** `--mode reviewer`, **When** the report renders, **Then** a
   `Not checked by jss-lint` block follows the compliance footer, listing
   `partial` then `not_checked` directives sorted by id, and ends with a
   line giving the four counts and pointing at `jss-lint coverage`.
3. **Given** `jss-lint coverage --format json`, **When** parsed, **Then**
   it contains `counts` and every directive with `id`, `source`,
   `section`, `provision`, `status`, `rules`, `reason`.
4. **Given** the web app, **When** a folder is checked in reviewer mode,
   **Then** the same block appears in the HTML, with no web-app change.
5. **Given** the `stub` journal, **When** `jss-lint coverage` runs,
   **Then** it reports that no coverage data exists for that journal and
   exits 0.

---

### User Story 3 - Adopt the tool on an existing manuscript (Priority: P1)

A package maintainer runs the tool on a long-lived vignette and gets 212
findings. They run `--baseline .jss-lint-baseline.json --update-baseline`
once, commit the file, and from then on `--baseline` hides those findings,
exits 0, and fails only when a new finding appears. Editing sentences,
inserting paragraphs, and moving lines do not resurrect accepted
findings. The baseline file is JSON, stable across both engines, and
stamps the tool and rule-set versions. The GitHub Action accepts a
`baseline` input. Inline `% jss-lint: ignore` comments, which the Rust
engine (and so the web app, VS Code, PyO3, and R) silently ignored until
now, are honoured everywhere.

**Why this priority**: P1 because without it the tool cannot be adopted on
any manuscript that is not new, which is most of them.

**Independent Test**: Create a baseline on `examples/jss5342-versions/
initial`, apply the real `resubmission` sources, and assert the
matched/stale/new counts recorded in plan §5.7; run the suppression
fixtures through both engines and compare JSON byte for byte.

**Acceptance Scenarios**:

1. **Given** a manuscript with findings, **When**
   `--baseline b.json --update-baseline` runs, **Then** `b.json` is written
   atomically, sorted, without a timestamp, and both engines write
   byte-identical files.
2. **Given** that baseline, **When** the manuscript is linted with
   `--baseline b.json` after sentence edits and paragraph insertions,
   **Then** exit code is 0 and the summary line reads
   `Baseline: N findings hidden by b.json (0 stale, 0 unevaluated)`.
3. **Given** that baseline, **When** a violation whose
   `(rule, message, suggestion)` is not already accepted for that file is
   introduced, **Then** it is reported and the exit code is 1.
4. **Given** a baseline written with rule set `2026-09-15` and a tool
   whose rule set is `2026-11-02`, **When** linting, **Then** the summary
   line names both dates and recommends `--update-baseline`.
5. **Given** `--baseline` with `--min-confidence high`, **When** entries
   for medium-confidence rules go unmatched, **Then** they are counted as
   `unevaluated`, not `stale`.
6. **Given** a `.Rmd` whose prose block does not start at line 1,
   **When** a `% jss-lint: ignore` directive precedes a violating line,
   **Then** the finding is suppressed in both engines.
7. **Given** a baseline created with a different `journal`, **When**
   applied, **Then** the tool exits 2 with a message on stderr.
8. **Given** `--output sarif --baseline b.json`, **When** the document is
   produced, **Then** baselined results are absent and the Action's
   severity gate needs no change.

---

### User Story 4 - Baseline entries stay specific under revision (Priority: P1)

The maintainer from Story 3 fixes one caption and adds another
uncapitalised one in the same file. With generic suggestions the two
findings are interchangeable and the new one is masked. In 1.2.0 the
suggestions of ten rules quote a stable identifier (bib entry key,
equation label, section title, caption head, code fragment, ref label,
cite key, comment head), so the new finding is reported. The identifiers
change only when the violation itself changes, so persisting findings
keep matching.

**Why this priority**: P1 and sequenced before Story 3's implementation:
`suggestion` is a baseline-key component and a fingerprint input, so
sharpening it after baselines exist would invalidate every user's entries
for those rules.

**Independent Test**: The 30-paper audit shows the ten rules remove 94 %
of removable masking; the jss5342 replay (plan §5.7) shows distinct keys
on the initial version rise from 49 to about 80 with at most 4 re-keyed
persisting findings in the heaviest round.

**Acceptance Scenarios**:

1. **Given** two `\caption{}` findings of `JSS-TYPO-001` in one file,
   **When** rendered, **Then** their suggestions differ by the caption
   head and form two distinct baseline keys.
2. **Given** a `JSS-REFS-004` finding, **When** rendered, **Then** the
   suggestion names the BibTeX entry key.
3. **Given** a manuscript with several `JSS-WIDTH-001` findings, **When**
   rendered, **Then** the suggestions are identical (the rule is
   deliberately generic; plan §5A) and the documented masking limit
   applies.
4. **Given** the ten reworded rules, **When** the Python and Rust engines
   lint the fixtures, **Then** the suggestion strings are byte-identical
   and every touched rule module keeps 100 % branch coverage.

---

### User Story 5 - Preview and apply fixes with a receipt (Priority: P2)

An author runs `--fix --dry-run`, reads the unified diff, then runs
`--fix`. Both CLIs end the fix pass with one summary line: how many fixes
were applied to how many files, how many were skipped and why. No git
interaction happens; the docs say to commit or dry-run first.

**Why this priority**: P2 because the preview already exists (spec 008);
what is missing is the receipt and the documented expectation.

**Independent Test**: `fix_parity` cases assert the summary line for
write, dry-run, and interactive modes in both CLIs.

**Acceptance Scenarios**:

1. **Given** a fixture with three applicable fixes and one conflict,
   **When** `--fix` runs, **Then** stdout ends the fix pass with
   `Applied 3 fixes to 1 file (1 skipped: conflict 1).` before the report.
2. **Given** the same fixture, **When** `--fix --dry-run` runs, **Then**
   the diff is followed by
   `Dry run: 3 fixes would be applied to 1 file. Re-run without --dry-run to write.`
   and no file changes.
3. **Given** a dirty git working tree, **When** `--fix` runs, **Then** it
   proceeds exactly as on a clean tree.

---

### User Story 6 - Pin versions and read provenance (Priority: P2)

A CI maintainer wants to know which rule set their pinned tool applies
and what may change on upgrade. `--version` prints the tool version, the
engine, the rule-set date with the jss.cls edition, and the active
journal, identically in both CLIs except for the engine line. The WASM,
PyO3, and R bindings expose the same information. `docs/versions.md` maps
every distribution channel's version string to the engine and rule-set
versions and states the compatibility policy and what to pin.

**Why this priority**: P2 because distribution versions have already
diverged (CRAN `1.1.0-2`, CTAN `1.1.0`) and the baseline file needs a
rule-set stamp; nothing else can be explained without it.

**Independent Test**: `version_parity` compares lines 1, 3, and 4 of
`--version` across engines; the fingerprint guard fails when a
catalogue-declared field or a fixture message changes without a
`ruleset_version` bump.

**Acceptance Scenarios**:

1. **Given** either CLI, **When** `--version` runs, **Then** stdout is a
   four-line block `jss-lint <v>` / `engine: … <v>` /
   `rule set: <date> (jss.cls 3.3, vendored 2021-05-23)` /
   `journal: <id>` and the exit code is 0.
2. **Given** `--version --journal nope`, **When** it runs, **Then** the
   last line reads `journal: nope (not registered)` and the exit code is
   still 0.
3. **Given** a change to a rule's severity or to a fixture-emitted
   message, **When** the catalogue check runs without a date bump,
   **Then** it fails naming the stamp command.
4. **Given** `jsslintr::jsslint_version()`, **When** called, **Then** it
   returns the package version (`1.2.0-N`), the engine version, and the
   rule-set date.

---

### User Story 7 - Scan a long run by colour (Priority: P3)

An author runs the tool in a terminal and sees error, warning, and info
severities, PASS/FAIL/SKIPPED statuses, rule ids, and banners coloured
with the basic 16-colour palette. Piped or redirected output, JSON, SARIF,
and HTML are never coloured. `--color`, the TOML `color` key, `NO_COLOR`,
and `CLICOLOR_FORCE` behave the same in both CLIs. Colour is never the
only carrier: every coloured token is still a word.

**Why this priority**: P3 because it is convenience; nothing in the
release depends on it and it is the first thing to cut.

**Independent Test**: Stripping escape sequences from `--color always`
output yields the plain output byte for byte in both engines; the
decision matrix (flag × env × TOML × TTY) is unit-tested in both CLIs.

**Acceptance Scenarios**:

1. **Given** stdout is a pipe, **When** the tool runs with default
   settings, **Then** no escape sequence appears.
2. **Given** `NO_COLOR=1` and `CLICOLOR_FORCE=1`, **When** the tool runs,
   **Then** no escape sequence appears; **Given** additionally
   `--color always`, **Then** escape sequences appear.
3. **Given** `--output json --color always`, **When** the tool runs,
   **Then** the JSON contains no escape sequence.
4. **Given** `--color always` in both engines, **When** escape sequences
   are stripped, **Then** the results are byte-identical to each other
   and to the plain output.

---

### User Story 8 - Check an Overleaf project (Priority: P3)

An Overleaf author downloads the project source zip and drops it on the
browser app, which unpacks it locally and checks every lintable file
without uploading anything. The docs also describe the CLI path
(unzip, then lint the root file) and the GitHub Sync path (the Action runs
on every sync, with a baseline for existing projects).

**Why this priority**: P3 because a documented workflow already closes
most of the gap; the zip drop removes one manual step.

**Independent Test**: A zip built from `docs/jss-template/` dropped on the
app yields the same HTML report as picking the folder.

**Acceptance Scenarios**:

1. **Given** a browser with `DecompressionStream("deflate-raw")`,
   **When** a zip is dropped, **Then** its `.tex/.bib/.Rnw/.Rmd` entries
   are checked with their paths and `__MACOSX/` and `._*` entries are
   ignored.
2. **Given** a browser without that API, **When** a zip is dropped,
   **Then** a message points at the folder picker.
3. **Given** `docs/overleaf.md`, **When** read, **Then** it covers the
   zip, CLI, and GitHub Sync paths.

---

### Edge Cases

- A journal plugin ships no recall snapshot or coverage file: every
  recall state is `unmeasured`, `rule_set` fields are null, the coverage
  block is absent, the footer says so, and `--version` prints
  `rule set: n/a`.
- A rule is retired after it was listed in `guide-coverage.yaml`: the
  contract test fails until the directive's status and reason are updated.
- A baseline entry's rule was ignored via `--ignore-rules` or filtered by
  `--min-confidence`: the entry is `unevaluated`, never `stale`.
- The manuscript's main file is renamed between runs: every entry for the
  old path goes stale; the docs say to run `--update-baseline`.
- Two findings share `(rule, path, message, suggestion)` (for instance two
  over-long lines of `JSS-WIDTH-001`): fixing one and adding another is
  masked while the count holds. Documented limit.
- `JSS-PARSE-000` findings: never baselined, never inline-suppressed;
  error-severity parse failures still exit 2.
- A baseline file with `schema_version` ≠ 1, a malformed document, or a
  different `journal`: exit 2 with a stderr message; the error text may
  differ between engines (documented divergence).
- `--update-baseline` together with `--fix`: the baseline is written from
  the pre-fix findings; the docs recommend fixing first.
- `--color always` when stdout is a Windows legacy console: Python's rich
  and Rust's anstream translate or strip as they see fit; only "no escape
  sequence when off" is guaranteed.
- A recall run adds a paper with a weak rule: the aggregate may fall
  below 0.807 but stays above the 0.78 floor unless more than about 50
  new false negatives appear; the per-rule ≤ 0.05 regression check still
  fires for a sharp single-rule drop.
- Equation without `\label` for `JSS-OPER-003`/`JSS-XREF-004`: the
  suggestion quotes the head of the equation body instead.

## Requirements *(mandatory)*

### Functional Requirements

**A — Recall transparency (plan §7)**

- **FR-A-001**: Every rule of the active journal MUST carry a recall
  state derived from the shipped snapshot: `measured` with an integer
  percentage when annotated instances ≥ 10, `limited (n=K)` for 1–9,
  `unmeasured` for 0. The percentage MUST be computed with integer
  half-up rounding so both engines agree.
- **FR-A-002**: Each category MUST carry a pooled recall state over its
  rules' annotated instances; a category with zero instances MUST render
  `unmeasured`.
- **FR-A-003**: Reviewer-mode terminal and HTML output MUST show a
  `Recall` column and a `Measured recall:` line after the compliance
  percentage.
- **FR-A-004**: Author-mode terminal output MUST always end with a footer
  on stdout stating that no findings does not mean compliant, the
  measured recall with instance and paper counts, and the coverage
  counts with a pointer to `jss-lint coverage`; HTML author output MUST
  carry the same sentences.
- **FR-A-005**: JSON output MUST add `recall` to each category object and
  a top-level `rule_set` object; SARIF rule descriptors MUST add
  `properties.confidence` and `properties.recall`; `explain` MUST print a
  `Recall:` line for every rule.
- **FR-A-006**: The shipped recall snapshot MUST be generated from the
  recall history at a pinned run, vendored with the catalogue, and MUST
  be the single source for the README recall badge.
- **FR-A-007**: CI MUST run the recall gate (`eval-jss recall --gate
  --no-record`) with an aggregate floor of 0.78; the floor MUST be
  ratcheted to the shipped snapshot minus 0.03 at each release and a test
  MUST fail when the floor is below that.

**G — Guide coverage (plan §7)**

- **FR-G-001**: A hand-curated `guide-coverage.yaml` beside the catalogue
  MUST list every provision of the four authorities (jss.cls,
  article.tex, style guide, author instructions) with `status` ∈
  {`checked`, `partial`, `not_checked`, `out_of_scope`}, covering rules,
  and a reason, plus a `sources` block with editions and fetch dates.
- **FR-G-002**: A contract test MUST fail when a listed rule is not
  active, when an active non-internal rule appears in no directive, when
  a `checked`/`partial` entry lists no rule, or when a non-`checked` entry
  has no reason.
- **FR-G-003**: Reviewer-mode terminal and HTML output MUST render a
  `Not checked by jss-lint` block listing `partial` and `not_checked`
  directives and a counts line.
- **FR-G-004**: A `jss-lint coverage [--format terminal|markdown|json]`
  subcommand MUST exist in both CLIs and render the full matrix
  deterministically.
- **FR-G-005**: JSON output MUST add a top-level `coverage` object with
  counts and the `partial`/`not_checked` items.

**B — Baseline mode and inline ignores (plan §5)**

- **FR-B-001**: Both CLIs MUST accept `--baseline FILE` and
  `--update-baseline`, and the `baseline` key in `.jss-lint.toml`; there
  MUST be no automatic discovery of a baseline file.
- **FR-B-002**: The baseline file MUST be JSON with `schema_version`,
  `tool_version`, `ruleset_version`, `journal`, and `entries` of
  `{rule_id, path, message, suggestion, count}` sorted by
  `(path, rule_id, message, suggestion)`, with no timestamp, so both
  engines produce byte-identical files.
- **FR-B-003**: `path` MUST be the posix path relative to the baseline
  file's directory, computed from the canonical file path so that
  auto-resolve and `--no-resolve` runs produce the same key.
- **FR-B-004**: Matching MUST consume entries as a multiset in
  deterministic violation order; matched findings MUST be removed before
  category bookkeeping and exit-code computation; stale (rule ran) and
  unevaluated (rule did not run) remainders MUST be counted separately.
- **FR-B-005**: A baseline summary MUST appear as one terminal line, an
  always-present JSON `baseline` key (`null` when inactive), and an HTML
  note; a rule-set date mismatch MUST be named in the summary.
- **FR-B-006**: A baseline for a different journal or with an unknown
  schema MUST cause exit 2.
- **FR-B-007**: The Rust engine MUST honour `% jss-lint: ignore`
  directives with the same semantics as the Python reference, including
  `.Rmd` line offsets and `\n`-only line counting, and the fix MUST ship
  as its own change with its own CHANGELOG entry.
- **FR-B-008**: The GitHub Action MUST accept a `baseline` input and pass
  it through.

**S — Token-specific suggestions (plan §5A)**

- **FR-S-001**: The suggestions of `JSS-CODE-003`, `JSS-OPER-003`,
  `JSS-XREF-004`, `JSS-TYPO-001`, `JSS-REFS-004`, `JSS-REFS-007`,
  `JSS-CAP-002`, `JSS-CODE-001`, `JSS-XREF-002`, and `JSS-CITE-003` MUST
  quote a stable identifier (offending fragment, equation label or head,
  caption head, BibTeX entry key, section title, comment head, referenced
  label, cite key) normalised and length-capped identically in both
  engines.
- **FR-S-002**: `JSS-WIDTH-001` MUST keep its generic suggestion; the
  masking limit for it MUST be documented.
- **FR-S-003**: Item S MUST land before any baseline is written and before
  `messages.json` is generated; message text MUST NOT change.
- **FR-S-004**: Every touched rule module MUST keep 100 % branch coverage
  and MUST be changed test-first in the Python reference.

**C — Fix safety (plan §6)**

- **FR-C-001**: Both CLIs MUST print one summary line at the end of a fix
  pass in write and dry-run modes naming applied, skipped (with reasons),
  and file counts.
- **FR-C-002**: `--fix` MUST NOT inspect or modify version-control state;
  the documentation MUST state the expectation to commit or dry-run first.

**D — Version and rule-set provenance (plan §4)**

- **FR-D-001**: The catalogue MUST carry `ruleset_version` (ISO date),
  `ruleset_fingerprint`, and `guide_edition`.
- **FR-D-002**: The fingerprint MUST cover the catalogue-declared contract
  fields of every active rule and the message/suggestion pairs the
  reference engine emits on the per-rule fixtures (`messages.json`); a
  check MUST fail when the stored fingerprint differs from the computed
  one, and the stamp tool MUST refuse to keep the date when the
  fingerprint changed.
- **FR-D-003**: `--version` MUST print the four-line block of Story 6 in
  both CLIs, byte-identical except for the engine line, after resolving
  the journal from flags and configuration.
- **FR-D-004**: The WASM, PyO3, and R bindings MUST expose a version
  function returning tool version, engine, rule-set version, and guide
  source; the R function MUST also return the package version.
- **FR-D-005**: `docs/versions.md` MUST list every channel's
  version-string constraints, the distribution → engine → rule-set
  mapping, the compatibility policy, and pin advice, and MUST state that a
  minor release may require `--update-baseline`.

**F — Colour (plan §8)**

- **FR-F-001**: Both CLIs MUST accept `--color auto|always|never` (default
  `auto`) and the TOML `color` key, and MUST resolve the decision with the
  same precedence: flag, then `NO_COLOR`, then `CLICOLOR_FORCE`, then
  TOML, then TTY detection.
- **FR-F-002**: `--output json|sarif|html`, piped or redirected stdout
  under `auto`, and all non-terminal subcommand formats MUST never contain
  escape sequences.
- **FR-F-003**: Removing escape sequences from coloured output MUST yield
  the plain output byte for byte in each engine; colour MUST use only the
  16-colour palette and MUST never be the sole carrier of severity,
  status, confidence, or rule identity.
- **FR-F-004**: Coloured bytes MUST be documented as a §XIII divergence;
  the plain stream MUST remain byte-identical across engines.

**E — Overleaf (plan §9)**

- **FR-E-001**: `docs/overleaf.md` MUST describe the zip, CLI, and GitHub
  Sync workflows and be linked from the README and the web app.
- **FR-E-002**: The web app MUST accept a dropped or selected `.zip`,
  unpack it in the browser with no upload and no new dependency, ignore
  non-lintable and macOS metadata entries, and fall back to a message
  when the decompression API is unavailable.

### Key Entities

- **Baseline file**: accepted findings as multiset entries keyed by
  `(path, rule_id, message, suggestion)` with counts; stamped with tool
  version, rule-set version, and journal.
- **Baseline summary**: matched, stale, unevaluated counts, path, and the
  baseline's rule-set version; carried on the compliance report.
- **Recall snapshot**: pinned run timestamp, corpus hash, minimum plants,
  per-rule true-positive and false-negative counts.
- **Recall state**: `measured`/`limited`/`unmeasured` with `tp`, `fn`,
  and integer `percent`; per rule and pooled per category.
- **Coverage directive**: id, source, section, provision, status, covering
  rules, reason; plus per-source editions and fetch dates.
- **Rule-set info**: date version, fingerprint, guide source, recall run.
- **Journal metadata**: rule-set info, per-rule recall, coverage; supplied
  by the journal module with an empty default for third-party journals.
- **Messages snapshot**: per-rule message/suggestion pairs emitted on the
  fixtures; input to the fingerprint only.
- **Colour decision**: a pure function of flag, TOML value, environment,
  and TTY state.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: On every compliant fixture, author-mode stdout is non-empty
  and contains `No findings does not mean compliant.`; exit code stays 0.
- **SC-002**: Reviewer output shows a recall state for all 16 JSS
  categories; `project` shows `unmeasured`; 26 rules show a percentage,
  27 show `limited`, 9 show `unmeasured` on the shipped snapshot.
- **SC-003**: Every active JSS rule appears in at least one
  `guide-coverage.yaml` directive; the four retired rules appear in none;
  the contract test enforces both.
- **SC-004**: After `--update-baseline` on the jss5342 `initial` sources,
  the baseline holds at least 75 distinct keys (prototype: 80); the
  `resubmission` replay reports at most 4 re-keyed persisting findings.
- **SC-005**: After `--update-baseline`, sentence edits and paragraph
  insertions on the same manuscript exit 0; introducing a violation with
  a new `(rule, message, suggestion)` in that file exits 1.
- **SC-006**: `eval-jss recall --gate --no-record` exits 0 at floor 0.78
  on the shipped snapshot, and a test fails if the floor is set below the
  snapshot minus 0.03.
- **SC-007**: On the 30-paper audit, masking-prone findings for the ten
  item-S rules drop by at least 90 % (prototype: 94 %).
- **SC-008**: Plain terminal, JSON, SARIF, and HTML output remain
  byte-identical across engines with baseline, coverage, recall, and the
  new suggestions active; `--update-baseline` files are byte-identical.
- **SC-009**: `--version` output differs between engines only in the
  engine line; the fingerprint check fails on any rewording without a
  date bump.
- **SC-010**: Stripping escape sequences from `--color always` output
  yields the plain output in both engines; `NO_COLOR=1` alone yields no
  escape sequence in either.
- **SC-011**: Both CLIs print the fix summary line in write and dry-run
  modes and `fix_parity` passes.
- **SC-012**: The WASM bundle grows by less than 50 KB over 1.1.0 and no
  new runtime dependency enters core, WASM, PyO3, or R.
- **SC-013**: A zip of `docs/jss-template/` dropped on the browser app
  produces the same HTML report as the folder picker.

## Assumptions

- The recall corpus stays at 17 annotated papers with a single annotator
  for 1.2.0; the shipped numbers are the lower bound documented in the
  corpus README (source-only linting).
- The JSS author guide remains an undated web page; the honest edition pin
  is the vendored `jss.cls` 3.3 (2021-05-23) plus per-source fetch dates.
- Messages are rule descriptions and quote no source text (measured:
  258 of 259 on five corpus papers), so the baseline's fragility rests on
  `suggestion` content, which item S controls.
- The GitHub Action keeps installing the Python package; `version:
  latest` picks up 1.2.0 from PyPI.
- The R package is resubmitted to CRAN as `1.2.0-1`; CTAN receives the
  identifier `1.2.0`; both are manual.
- Baseline support in the R, PyO3, and WASM bindings is a follow-up; the
  matcher is pure and lives in core so that is cheap later.
- Windows colour behaviour is verified manually; there is no Windows CI
  job.
- Item S's deferred rules (`REFS-005`, `REFS-006`, `NAME-002`,
  `HOUSE-002`, `BIBTEX-003/004/005`, `TYPO-004`, `XREF-006`) may be
  sharpened in a later minor; users of baselines touching them will be
  told by the rule-set date mismatch line.
