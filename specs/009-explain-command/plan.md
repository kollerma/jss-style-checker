# Implementation Plan: `jss-lint explain` Subcommand

**Branch**: `009-explain-command` | **Date**: 2026-05-03 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/009-explain-command/spec.md`

## Summary

Convert `jss-lint` from a single-command CLI to a Click group while
preserving the existing `jss-lint <PATHS>` invocation as the
group's default action (Clarifications §5). Add `explain` as a
subcommand: `jss-lint explain [RULE-ID] [--example] [--format
{terminal,markdown}]`. Rule metadata is augmented with three new
catalogue fields (`explanation`, `example_bad`, `example_good`)
and the contract test from spec 007 extends to require non-empty
`explanation` for every rule.

The renderer is a small new module `src/texlint/explain.py`
exporting `render(rule_id_or_None, *, fmt, with_example) -> str`.
Two callers: the `explain` CLI subcommand, and (in spec 015) the
conformance-report renderer that needs the same projection.

A `did-you-mean?` helper lives next to the renderer and uses
`difflib.get_close_matches` (stdlib).

## Technical Context

**Language/Version**: Python ≥3.10, unchanged.

**Primary Dependencies**: unchanged (`click`, `rich`, `jinja2`,
`pylatexenc`, `bibtexparser`, `pyyaml`).

**Storage**: None.

**Testing**: New module
`tests/unit/test_explain.py` with golden-file expectations for
`(rule, format)` pairs across at least three rules. Catalogue
contract test extension: `test_every_rule_has_explanation` in
the existing `tests/unit/test_catalogue.py` from spec 007.

**Target Platform**: POSIX, unchanged.

**Project Type**: Library + CLI; gains one Click subcommand.

**Performance Goals**: per-invocation rendering is O(1) for
single-rule view, O(R) for the listing (R = catalogue size).
Sub-100 ms wall clock on the current catalogue.

**Constraints**:
- Constitution §I determinism: rendering is a pure function of
  `(rule_id, format, with_example, catalogue, fixture-bytes)`.
  TTY-detection is wrapped in a single function so test output
  is forced non-TTY for golden equality.
- Constitution §III non-fatal: an unknown rule id exits 2 (the
  same code as parse failure); the explainer never raises.
- Constitution §IV zero core edits for journals: this spec edits
  `src/texlint/api.py` (three new `Rule` fields) and
  `src/texlint/cli.py` (Click group + subcommand). NOT a journal
  addition; cross-cutting CLI + public-API surface. Documented
  in Complexity Tracking.
- Constitution §V authority cited: this spec extends the
  catalogue with prose; the prose cites the same JSS guide
  section that spec 007 already records.
- Constitution §VI precision gate: N/A.
- Constitution §VII safe auto-fix: N/A.
- Constitution §VIII TDD: golden tests for at least three rules
  land before the renderer body.
- Constitution §IX 100% branch coverage on rule modules:
  unchanged.
- Constitution §X small surface: one renderer module, three
  catalogue fields, one Click subcommand, one fixture-loader
  helper. The renderer has two concrete callers (`cli.py`
  subcommand, spec-015 conformance report). When spec 015
  ships, the count is two; today, the explain CLI is the only
  caller, with spec 015 as the documented second-caller.
- Constitution §XII reproducible corpus: N/A.

**Scale/Scope**: 3 catalogue fields × ~58 rules (backfill).
1 new renderer module (~250 LOC). 1 Click sub-group migration in
`cli.py`. 1 fixture-loader helper. 1 contract-test extension. 1
new test module with goldens for 3 rules × 2 formats = 6 goldens
plus the listing-view goldens for 1 format = 7 goldens total.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **§I Determinism** — pure function of catalogue +
      fixture bytes; TTY detection mocked in tests. **PASS**.
- [x] **§II AST-First** — N/A; metadata + rendering. **PASS**.
- [x] **§III Non-Fatal Parse** — unknown rule id exits 2 with
      a stderr suggestion list. The explainer never raises.
      **PASS**.
- [x] **§IV Zero Core Edits for Journals** — `api.py` (three
      new `Rule` fields) and `cli.py` (Click group migration).
      NOT a journal addition. **PASS with documented
      amendment**.
- [x] **§V Authority Cited** — explanation prose extends the
      authority surface from spec 007. **PASS**.
- [x] **§VI ≥90% Precision Gate** — N/A. **PASS**.
- [x] **§VII Safe Auto-Fix** — N/A. **PASS**.
- [x] **§VIII TDD** — golden tests for 3 rules × 2 formats
      land before the renderer body. **PASS by task ordering**.
- [x] **§IX 100% Branch Coverage on Rule Modules** —
      unchanged. **PASS**.
- [x] **§X Small Surface** — three catalogue fields, one
      module, one CLI subcommand. The renderer has the explain
      CLI as one caller today and spec 015 as the documented
      second; if spec 015 slips, an interim §X review is
      called. **PASS**.
- [x] **§XII Reproducible Corpus** — N/A. **PASS**.

All gates PASS. One documented amendment under §IV.

Post-Phase-1 re-check: gates still PASS.

## Project Structure

### Documentation (this feature)

```text
specs/009-explain-command/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── explain-cli.md
└── checklists/
    └── requirements.md
```

### Source Code (repository root)

```text
src/texlint/api.py                                 # MODIFIED:
                                                   #  - Rule.explanation: str
                                                   #  - Rule.example_bad: str | None
                                                   #  - Rule.example_good: str | None

src/texlint/journals/_catalogue_data.py            # MODIFIED — backfill three fields per rule

src/texlint/explain.py                             # NEW — render(rule_id, format, with_example) -> str
                                                   #       did_you_mean(unknown_id) -> list[str]

src/texlint/cli.py                                 # MODIFIED:
                                                   #  - migrate to click.Group with default action
                                                   #  - add `explain` subcommand
                                                   #  - preserve `jss-lint <PATHS>` semantics

tests/
├── unit/
│   ├── test_explain.py                            # NEW — golden tests for 3 rules × 2 formats
│   └── test_catalogue.py                          # MODIFIED — add test_every_rule_has_explanation
└── fixtures/
    └── explain/
        ├── golden_jss-cite-002_terminal.txt       # NEW
        ├── golden_jss-cite-002_markdown.md        # NEW
        ├── golden_jss-name-001_terminal.txt
        ├── golden_jss-name-001_markdown.md
        ├── golden_jss-cap-002_terminal.txt
        ├── golden_jss-cap-002_markdown.md
        └── golden_listing_terminal.txt            # NEW — full listing view
```

**Structure Decision**: One renderer module, one CLI sub-group
migration, three catalogue fields, one contract-test extension.
The Click group migration preserves the existing `jss-lint
<PATHS>` invocation by setting the default-action handler on the
group, so no editor / CI script needs to change.

## Complexity Tracking

One documented amendment.

| Amendment | Why Needed | Alternative Rejected |
|-----------|------------|---------------------|
| Edits to `src/texlint/api.py` (three new `Rule` fields) and `src/texlint/cli.py` (Click group migration) (§IV) | §IV prohibits core edits when *adding a journal*. This spec extends rule metadata across journals and migrates the CLI to a multi-command shape. Both are cross-cutting surfaces. | **Render explanations from a side file** (e.g., `docs/rules/<id>.md`) — would split the rule definition from its prose and create drift. **Add `explain` as a separate binary** — would multiply install / packaging surface for a feature that is fundamentally a query of the same catalogue. Rejected. |
