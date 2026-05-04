# Implementation Plan: JSS-guide Rule Mapping

**Branch**: `007-jss-guide-mapping` | **Date**: 2026-05-03 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/007-jss-guide-mapping/spec.md`

## Summary

Add two fields, `guide_section: str` and `guide_url: str | None`, to
the existing `texlint.api.Rule` dataclass and to every entry of
`texlint.journals._catalogue_data.RULES`. Centralise URL management
in a new `docs/jss-guide/index.json` mapping, so re-publication of
the JSS author guide is a single-file edit.

The four existing renderers (terminal, JSON, HTML, SARIF) gain
minimal additions:

- **terminal**: `(see <guide_section>)` suffix for citable rules;
  no suffix for sentinel rules.
- **JSON**: two new keys (`guide_section`, `guide_url`) per
  violation entry — `null` for sentinel rules.
- **SARIF**: `tool.driver.rules[].helpUri = guide_url` (when
  non-`None`) and `shortDescription.text` augmented with the
  section number.
- **HTML**: `guide_section` rendered as `<a href="guide_url">`,
  plain text for sentinels.

A new test module `tests/unit/test_catalogue.py` enforces the
catalogue contract: every rule has `guide_section`; every
citable-category rule has a non-`None` `guide_url` that resolves
through `index.json`.

The 50+ existing rules in spec 003's catalogue are backfilled in
this spec — one PR, one mechanical pass over `_catalogue_data.py`.

## Technical Context

**Language/Version**: Python ≥3.10, unchanged.

**Primary Dependencies**: unchanged. No new runtime deps.
`docs/jss-guide/index.json` is plain JSON loaded with the
standard-library `json` module; the loader sits in
`src/texlint/journals/jss/_guide_index.py` (a small lookup helper,
not a public API).

**Storage**: A new tracked-but-data-only file at
`docs/jss-guide/index.json`. ~50 lines, hand-edited.

**Testing**: `pytest`. New tests:
- `tests/unit/test_catalogue.py::test_every_rule_cites_guide`
- `tests/unit/test_catalogue.py::test_guide_urls_resolve_through_index`
- Renderer golden updates: terminal, JSON, HTML, SARIF goldens
  regenerate to include the new fields.

**Target Platform**: POSIX, unchanged.

**Project Type**: Library + CLI, unchanged.

**Performance Goals**: catalogue load gains a single
`json.load(open("docs/jss-guide/index.json"))` at process start;
~1 ms overhead. Renderer overhead per violation is ≤2 dict
look-ups.

**Constraints**:
- Constitution §I determinism: pure data; no time/host/PID inputs.
- Constitution §II AST-first: N/A; metadata extension.
- Constitution §III non-fatal parse: a malformed `index.json`
  surfaces as `JSS-PARSE-000` (not raised); the
  catalogue-contract test catches malformed structure during CI.
- Constitution §IV zero core edits for journals: this spec edits
  `src/texlint/api.py` (two new `Rule` fields) and
  `src/texlint/journals/_catalogue_data.py` (backfill). Both are
  cross-cutting metadata extensions — every journal that adopts
  the catalogue benefits — not journal-specific. Documented in
  Complexity Tracking.
- Constitution §V authority cited: this spec strengthens §V — it
  *materially upgrades* the existing citation contract from
  "metadata MUST reference an authority" to "metadata MUST link
  to a public URL". No regression.
- Constitution §VI precision gate: N/A; no rule logic changes.
- Constitution §VII safe auto-fix: N/A.
- Constitution §VIII TDD: catalogue contract tests land before
  the catalogue backfill.
- Constitution §IX 100% branch coverage on rule modules:
  unchanged. Rule files do not gain or lose branches; the
  metadata is pure data.
- Constitution §X small surface: two new fields on `Rule`, one
  new JSON file, one new test module, one tiny loader. No new
  abstractions.
- Constitution §XII reproducible corpus: N/A.

**Scale/Scope**: 1 dataclass extension (2 fields). 1 catalogue
backfill (~58 entries). 1 new file (`docs/jss-guide/index.json`).
1 new test module (~80 LOC). 4 renderer edits (terminal, JSON,
HTML, SARIF). 1 small loader module
(`src/texlint/journals/jss/_guide_index.py`). 4 golden-fixture
regenerations.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **§I Determinism** — pure data load; deterministic
      serialisation. **PASS**.
- [x] **§II AST-First** — N/A; metadata. **PASS**.
- [x] **§III Non-Fatal Parse** — `index.json` parse failures
      surface as `JSS-PARSE-000` violations on the load path;
      malformed structure trips the catalogue contract test in
      CI. **PASS**.
- [x] **§IV Zero Core Edits for Journals** — edits to
      `src/texlint/api.py` (two new `Rule` fields) and
      `_catalogue_data.py` (backfill). NOT a journal addition.
      Cross-cutting metadata extension shared across journals.
      Documented in Complexity Tracking. **PASS with documented
      amendment**.
- [x] **§V Authority Cited** — strengthened: this spec adds the
      URL anchor that §V already required prose-level. **PASS**.
- [x] **§VI ≥90% Precision Gate** — N/A; no rule logic.
      **PASS**.
- [x] **§VII Safe Auto-Fix** — N/A; no fix data. **PASS**.
- [x] **§VIII TDD** — catalogue contract test lands before
      catalogue backfill. **PASS by task ordering**.
- [x] **§IX 100% Branch Coverage on Rule Modules** —
      unchanged. **PASS**.
- [x] **§X Small Surface** — two new dataclass fields, one
      new JSON file, one tiny loader. The loader has three
      callers: the catalogue contract test, the SARIF rule
      descriptor projection, and the HTML renderer.
      `_guide_index.py` therefore satisfies §X's "≥3 concrete
      callers" rule. **PASS**.
- [x] **§XII Reproducible Corpus** — N/A. **PASS**.

All gates PASS. One documented amendment under §IV.

Post-Phase-1 re-check: gates still PASS. The data-model addition
(two scalar fields) is the minimum increment.

## Project Structure

### Documentation (this feature)

```text
specs/007-jss-guide-mapping/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── catalogue-citation.md
└── checklists/
    └── requirements.md
```

### Source Code (repository root)

```text
# Public API extension — two new Rule fields
src/texlint/api.py                                # MODIFIED:
                                                  #  - Rule.guide_section: str
                                                  #  - Rule.guide_url: str | None

# Catalogue backfill
src/texlint/journals/_catalogue_data.py           # MODIFIED — every RULES entry
                                                  #            gains guide_section / guide_url

# Guide-URL index loader (small helper)
src/texlint/journals/jss/_guide_index.py          # NEW — load_guide_index() -> dict[str, str]
                                                  #       used by SARIF + HTML renderers and
                                                  #       the catalogue contract test

# Renderer edits
src/texlint/output/terminal.py                    # MODIFIED — append "(see <section>)" for citable rules
src/texlint/output/json_output.py                 # MODIFIED — emit guide_section / guide_url per violation
src/texlint/output/sarif.py                       # MODIFIED — wire guide_url -> helpUri
                                                  #            wire guide_section into shortDescription
src/texlint/output/html_output.py                 # MODIFIED — render section as anchor for citable rules

# Single source of truth for guide URLs
docs/
└── jss-guide/
    └── index.json                                # NEW — { "sections": { "§3.2 Citations": "...", ... } }

# Tests
tests/
├── unit/
│   ├── test_catalogue.py                         # NEW — citation contract tests
│   └── output/
│       ├── test_terminal.py                      # MODIFIED — golden regen for "(see ...)"
│       ├── test_json_output.py                   # MODIFIED — golden regen for new keys
│       ├── test_sarif.py                         # MODIFIED — golden regen for helpUri / shortDescription
│       └── test_html_output.py                   # MODIFIED — golden regen for anchor element
```

**Structure Decision**: One small loader module
(`_guide_index.py`), one new JSON data file
(`docs/jss-guide/index.json`), one new test module, plus a
two-field extension to the public `Rule` dataclass. Every
existing renderer is touched but with a strictly additive
projection — pre-existing fields and ordering are preserved
(spec FR-012, contract test C-12).

## Complexity Tracking

One documented amendment.

| Amendment | Why Needed | Alternative Rejected |
|-----------|------------|---------------------|
| Edits to `src/texlint/api.py` (two new `Rule` fields) and `_catalogue_data.py` (backfill) (§IV) | §IV prohibits core edits when *adding a journal*. This spec extends rule metadata across every journal — every journal that adopts the catalogue inherits the new fields. The edits are: (a) two scalar fields on the public `Rule` dataclass, (b) a backfill of the existing catalogue entries. Equivalent in scope to spec 005's `ParsedRmdFile` addition. | **Carry guide_section as a tag in `properties`-style dict** — would couple every renderer to a tag-name string and bypass type checking. Rejected per §X. **Make the JSS journal own the citation surface privately** — would split it from the public `Rule`, blocking SARIF and HTML from using it. Rejected — the data is rule-level, not journal-internal. |
