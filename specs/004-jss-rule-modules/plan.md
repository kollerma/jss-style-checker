# Implementation Plan: JSS Rule Modules — Category-by-Category Implementation

**Branch**: `004-jss-rule-modules` | **Date**: 2026-04-23 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/004-jss-rule-modules/spec.md`

## Summary

Implement the 58 rules enumerated in spec 003's frozen `catalogue.yaml` as Python rule modules under `src/texlint/journals/jss/rules/`, one module per category. Rollout is category-by-category with a per-category precision gate (spec 002's `eval-jss`). Smoke rules from Step 1 retrofit or retire in the first PR of their subsuming category. The catalogue is the contract: rule metadata is sourced programmatically from the YAML so no duplicate-text drift is possible, and a CI test enforces the active/retired-id contract in both directions.

**Relationship to inherited specs**:
- **Spec 001** (linter foundation): `Rule`, `RuleCategory`, `ParsedDocument`, `ToolConfig`, `Violation`, `Severity` shapes. This plan adds one value to `Severity` (`INFO = "info"`) — a small API amendment landed as a Phase 2 foundational task, required by 4 info-severity rules in the catalogue. No other core-API changes.
- **Spec 002** (eval-jss harness): unchanged. Spec 004 consumes `eval-jss scan / human-review / report` and `eval/review-skip-list.toml` unchanged.
- **Spec 003** (rule catalogue): catalogue frozen as input. Spec 004 MUST NOT edit `catalogue.yaml` directly (FR-002); amendments (such as new retirements during precision-gate refinement) land via spec-003 PRs that merge before the dependent spec-004 PR. The `retired_rule_ids:` structured field (amendment commit `5f19c13`) is already in 004's ancestry via the 2026-04-23 rebase.

**Drift-preventing architecture**: rule metadata (`id`, `category`, `severity`, `message_template`, `authority`) never lives in two places. A generated `src/texlint/journals/jss/_catalogue_data.py` (produced by `python -m tools.generate_catalogue_data` from `catalogue.yaml`) is the single Python-side source of truth; rule modules import from it. The generated file is committed (zero runtime YAML dependency); a CI drift-check regenerates in-memory and compares to the committed file. See `contracts/catalogue-consistency.md`.

## Technical Context

**Language/Version**: Python ≥3.10, unchanged from specs 001/002/003.

**Primary Dependencies**: `pylatexenc>=2.10`, `bibtexparser>=2.0.0b6` (both already runtime deps), `click>=8.1`, `rich>=13.0`, `jinja2>=3.1` (all already present). **No new runtime deps.** `PyYAML>=6.0` remains a dev extra used by `tools/generate_catalogue_data.py` at build time and by the renderer / consistency tests; no rule module imports `yaml` at runtime.

**Storage**: No new storage. Spec 002's `eval/eval.db` SQLite remains the precision-gate labelling store, unchanged. The codegen output `_catalogue_data.py` is a Python module (not a data file); its bytes live in git.

**Testing**: `pytest` + `pytest-cov` (already in dev extras). One test module per category under `tests/unit/rules/test_<category>.py`; one CI-resident catalogue-consistency test under `tests/unit/journals/jss/test_catalogue_registration.py`; per-rule good/bad fixtures under `tests/fixtures/violations/<category>/`. Constitution §IX requires 100% branch coverage on every file under `src/texlint/journals/jss/rules/`; this is enforced via per-category `--cov-fail-under=100` in CI.

**Target Platform**: POSIX primary (Linux / macOS). Windows not explicitly supported, matching 001/002/003.

**Project Type**: Python library + CLI (`jss-lint` entry point). Spec 004 extends the existing `src/texlint/journals/jss/` tree; no new package directories.

**Performance Goals**: per-rule AST walks are O(N) in node count; the 58-rule × single-paper cost is ~58× the 3-rule baseline, empirically <100 ms for typical JSS papers (AST pass is the bottleneck, not individual rule logic). `jss-lint` must still complete in under 1 second on a typical `docs/jss-template/article.tex`.

**Constraints**:
- Constitution §I Determinism — every rule's `check` is a pure function of `(ParsedDocument, ToolConfig)`.
- Constitution §II AST-first — rule logic walks pylatexenc AST or bibtexparser entries; `raw_source` inspection is permitted only for `JSS-WIDTH-001` per the catalogue's `inspects: [raw_source]` declaration.
- Constitution §V Authority cited — already satisfied by the catalogue; no new authority work.
- Constitution §VI Precision gate — per-category, per spec 004 FR-012..FR-014.
- Constitution §VIII TDD — fixtures + failing tests land before `check` bodies; PR history shows the red-green transition.
- Constitution §IX 100% branch coverage on rule modules — hard CI gate, no `≥99%` wiggle.
- Constitution §X Small surface — private `_helpers.py` migrates shared walkers only after ≥3 concrete category-module callers cross the threshold.

**Scale/Scope**: 58 rules across 15 categories. One module per category (15 new files), one test module per category (15), ~116 fixture files (one good/bad pair per rule), plus the generated `_catalogue_data.py`, the `tools/generate_catalogue_data.py` script, the `_helpers.py` shared module, the `test_catalogue_registration.py` CI test, the `scripts/eval-category.sh` wrapper, and extensions to `JSSJournal.categories()`, `eval/review-skip-list.toml`, and one line on `texlint.api.Severity`.

**Spec drift reconciled — three items**.

1. **Check-callable naming**: spec 003's `contracts/rules-module.md` pinned `_check_jss_<category>_NNN` (private, underscore-prefixed). The plan input for this spec (`/speckit.plan` command args) standardised on `check_<rule_id_suffix>` (public, lowercase-with-underscores derived from the rule id, e.g., `check_jss_cite_002`). The user-supplied plan input is the authoritative shape for spec 004; spec 003's contract is superseded (spec 003 shipped catalogue-only per its scope narrowing, so its rule-module contract was never materialised). Public names let tests import the callable directly without having to pierce underscore-conventions; `Rule.check` binds the same callable.

2. **Rule metadata source**: spec 003's contract had rule modules hard-code `id`/`severity`/`authority` with a CI consistency test catching drift. The plan input for spec 004 asks for "`Rule.description` pulled from the catalogue … import the catalogue as data if possible". This plan adopts the build-time codegen path — `tools/generate_catalogue_data.py` reads `catalogue.yaml` and emits `src/texlint/journals/jss/_catalogue_data.py`, committed; rule modules import from the generated module. Zero runtime dependency on PyYAML. A CI drift-check regenerates in-memory and fails on mismatch. Replaces and improves on spec 003's hard-code + consistency-test approach.

3. **Severity enum extension**: spec 001's `Severity` has only `ERROR` and `WARNING`. Spec 003's catalogue added `info` as a third severity (4 rules: JSS-REFS-003, JSS-XREF-002, JSS-XREF-004, JSS-HOUSE-003). Spec 004 needs `Severity.INFO = "info"`. This is a minor API extension, landed as the first Phase 2 foundational task before any rule module referencing an info-severity rule can be registered. Downstream consumers that switched exhaustively on the enum (output renderers, eval harness) must be audited for `INFO` handling; spec-002's report already has a "not yet measured"-style bucket that maps cleanly to informational violations.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Standing gates from `.specify/memory/constitution.md` v1.0.0.

- [x] **§I Determinism** — rule `check` callables are pure functions of `(ParsedDocument, ToolConfig)`. No `random`, no `time.time()`, no module-level mutable state, no network. The shared `_helpers.py` walkers are pure generators over AST node lists. **PASS**.
- [x] **§II AST-First** — every rule walks the pylatexenc AST (`tex_files`) or the bibtexparser library (`bib_files`). Only `JSS-WIDTH-001` reads `raw_source`; that carve-out is justified in the catalogue's `notes` field (line-width is intrinsically textual) and declared via `inspects: [raw_source]`. `_helpers.py` exposes `_is_inside_verbatim(node)` / `_is_inside_comment(node)` so rules that must scan char nodes can skip verbatim / comment regions without reimplementing the safety check. **PASS**.
- [x] **§III Non-Fatal Parse** — rules see only `ParsedDocument`s whose parse step succeeded; the engine already surfaces `JSS-PARSE-000` separately. No rule raises on malformed input; `check` callables handle empty/partial AST gracefully. **PASS**.
- [x] **§IV Zero Core Edits for Journals** — no edits to `src/texlint/core/` or `src/texlint/api.py` except the one-value enum extension (`Severity.INFO`). That extension is API-additive (no existing consumer breaks) and is justified as a small backwards-compatible amendment supporting catalogue-pinned severities. **PASS with documented amendment** (see Complexity Tracking).
- [x] **§V Authority Cited** — every rule's `authority` comes directly from the catalogue row, sourced via codegen. The codegen refuses to emit an entry without a non-empty `authority` value (catalogue validator already enforces). **PASS**.
- [x] **§VI ≥90% Precision Gate** — spec 004 FR-012 through FR-014 formalise the gate per category. The `eval-category.sh` wrapper script drives `scan → human-review → report`. No category merges until its `≥10`-labelled-violation rules all show precision ≥0.90. **PASS by contract**.
- [x] **§VII Safe Auto-Fix** — no `FixSuggestion` data in this spec (spec 004 FR-025). Every emitted `Violation.fix = None`. **PASS** (non-applicable subset).
- [x] **§VIII TDD** — category PR structure pins the fixtures-and-failing-test-first order. Per-rule test template in `contracts/test-template.md` documents the expected pattern; each category's task list in `tasks.md` will order (a) create fixture pair → (b) write failing test → (c) implement check → (d) verify 100% branch coverage → (e) wire into journal → (f) precision gate. **PASS by task ordering**.
- [x] **§IX 100% Branch Coverage on Rule Modules** — enforced per-category via `pytest --cov=src/texlint/journals/jss/rules/<category> --cov-branch --cov-fail-under=100`. The CI gate rejects any category PR below 100%. **PASS by contract**.
- [x] **§X Small Surface** — `_helpers.py` starts empty; helpers move there only after ≥3 concrete category-module callers exist (the three-caller threshold). No speculative abstractions, no forward-compat shims. Generated `_catalogue_data.py` is a single flat dict of rule metadata — no hierarchy. Per-category modules have zero module-level state. **PASS**.
- [x] **§XII Reproducible Corpus** — spec 004 consumes spec 002's reproducibility mechanism unchanged. Each category's precision-gate report cites the corpus-manifest commit hash at the reporting commit. **PASS** (downstream consumer).

All gates PASS. One documented amendment (Severity.INFO enum extension) — justified in Complexity Tracking below.

Post-Phase-1 re-check (after writing research.md, data-model.md, contracts/, quickstart.md): all gates still PASS. The codegen strategy for rule metadata (Phase 0 decision) preserves §IV (the generated file is a spec-004 artefact living under `src/texlint/journals/jss/`, not a core edit) and §I (zero runtime YAML, pure imports). No new gate concerns emerged from design.

## Project Structure

### Documentation (this feature)

```text
specs/004-jss-rule-modules/
├── plan.md                                  # This file
├── research.md                              # Phase 0: codegen, helpers, skip-list, severity extension
├── data-model.md                            # Phase 1: per-category module shape, codegen, skip-list schema
├── quickstart.md                            # Phase 1: onboarding for a new-category PR
├── contracts/
│   ├── rules-module.md                      # Phase 1: canonical category module shape + check callable naming
│   ├── catalogue-consistency.md             # Phase 1: CI test contract (catalogue ↔ registered rules)
│   ├── ai-skip-list.md                      # Phase 1: eval/review-skip-list.toml schema + 14 pre-populated entries
│   └── test-template.md                     # Phase 1: per-rule pytest template (positive + near-miss + fixture)
└── checklists/
    └── requirements.md                      # Spec quality checklist (from /speckit.specify)
```

### Source Code (repository root)

```text
# Rule modules — one file per category, 15 total. Retrofit the 3 smoke rules
# in the same PR that introduces their subsuming category.
src/texlint/journals/jss/
├── __init__.py                              # JSSJournal.categories() grows 15 lazy imports + RuleCategory rows
├── _catalogue_data.py                       # NEW — generated from catalogue.yaml; one dict keyed by rule_id
├── terms.py                                 # UNCHANGED (shipped by spec 003)
└── rules/
    ├── __init__.py                          # unchanged
    ├── _helpers.py                          # NEW — private shared walkers / verbatim & comment safety helpers
    ├── preamble.py                          # NEW — 8 rules (PRE-001..008)
    ├── structure.py                         # NEW — 6 rules (STRUCT-001..006)
    ├── markup.py                            # NEW — 4 rules
    ├── citations.py                         # NEW — 3 rules; same PR deletes cite_001_emph.py + its test (FR-015)
    ├── references.py                        # NEW — 7 rules; same PR deletes bib_001_year.py + its test (FR-016)
    ├── bibtex.py                            # NEW — 4 rules
    ├── naming.py                            # NEW — 2 rules
    ├── capitalization.py                    # NEW — 4 rules
    ├── typography.py                        # NEW — 4 rules
    ├── abbreviations.py                     # NEW — 1 rule (ABBR-002 retired in spec 003)
    ├── code_style.py                        # NEW — 3 rules
    ├── code_width.py                        # NEW — 1 rule; same PR deletes src_001_width.py + its test (FR-017)
    ├── operators.py                         # NEW — 4 rules
    ├── crossrefs.py                         # NEW — 4 rules
    ├── house_style.py                       # NEW — 3 rules
    ├── bib_001_year.py                      # DELETED in the PR that adds references.py
    ├── cite_001_emph.py                     # DELETED in the PR that adds citations.py
    └── src_001_width.py                     # DELETED in the PR that adds code_width.py

# Severity API extension — lands in the first spec-004 foundational PR
src/texlint/api.py                           # MODIFIED — adds Severity.INFO = "info"

# Codegen + eval wrapper
tools/
├── generate_catalogue_data.py               # NEW — reads catalogue.yaml, writes _catalogue_data.py
├── _catalogue_validate.py                   # UNCHANGED (shipped by spec 003)
└── render_catalogue.py                      # UNCHANGED (shipped by spec 003)

scripts/
├── eval-category.sh                         # NEW — wraps scan → human-review → report --grep=<CATEGORY>
├── vtest.sh                                 # UNCHANGED
├── vlint.sh                                 # UNCHANGED
└── vpy.sh                                   # UNCHANGED

# Per-category test files + fixtures
tests/
├── unit/
│   ├── rules/
│   │   ├── test_preamble.py                 # NEW — 100% branch coverage on preamble.py
│   │   ├── test_structure.py                # NEW
│   │   ├── test_markup.py                   # NEW
│   │   ├── test_citations.py                # NEW
│   │   ├── test_references.py               # NEW — subsumes test_bib_001_year.py
│   │   ├── test_bibtex.py                   # NEW
│   │   ├── test_naming.py                   # NEW
│   │   ├── test_capitalization.py           # NEW
│   │   ├── test_typography.py               # NEW
│   │   ├── test_abbreviations.py            # NEW
│   │   ├── test_code_style.py               # NEW
│   │   ├── test_code_width.py               # NEW — subsumes test_src_001_width.py
│   │   ├── test_operators.py                # NEW
│   │   ├── test_crossrefs.py                # NEW
│   │   └── test_house_style.py              # NEW
│   └── journals/
│       └── jss/
│           ├── test_catalogue_registration.py # NEW — CI consistency test (FR-004)
│           ├── test_catalogue_data_fresh.py  # NEW — drift check on the generated _catalogue_data.py
│           ├── test_catalogue.py             # UNCHANGED (spec 003)
│           ├── test_render.py                # UNCHANGED (spec 003)
│           └── test_terms.py                 # UNCHANGED (spec 003)
└── fixtures/
    └── violations/                          # 116 new fixture files (58 rules × good/bad pair)
        ├── preamble/
        ├── structure/
        ├── ...
        └── house_style/

# Eval harness — one file extended
eval/
├── review-skip-list.toml                    # MODIFIED — pre-populate the 14 rules per FR-023
└── ...                                      # everything else unchanged

# Integration tests touched by the citations-category PR (flat-fixture cleanup per FR-018)
tests/integration/
├── test_cli_author_terminal.py              # MAY-MODIFY — references tests/fixtures/violations/JSS-CITE-001.tex
├── test_cli_reviewer_terminal.py            # MAY-MODIFY
├── test_cli_exit_codes.py                   # MAY-MODIFY
├── test_cli_config_merge.py                 # MAY-MODIFY
├── test_cli_html.py                         # MAY-MODIFY
├── test_cli_json.py                         # MAY-MODIFY
└── test_plugin_discovery.py                 # MAY-MODIFY
```

**Structure Decision**: spec 004 extends the existing `src/texlint/journals/jss/` tree with a per-category layout under `rules/`. The codegen artefact `_catalogue_data.py` lives alongside `terms.py` at the journal level (not inside `rules/`) because it's shared across all rule modules. `_helpers.py` lives inside `rules/` because its helpers are rule-specific (AST walkers tuned for the rule-authoring pattern). Retrofits delete the three Step 1 smoke rule files and their tests in the same commit as their replacement category modules (per FR-015..FR-017). No new top-level packages; no wheel-surface changes (all new code lives inside existing packaged directories).

## Complexity Tracking

One documented amendment.

| Amendment | Why Needed | Alternative Rejected |
|-----------|------------|---------------------|
| `Severity.INFO = "info"` in `texlint.api` | Spec 003's frozen catalogue has 4 rules with `severity: info` (JSS-REFS-003, JSS-XREF-002, JSS-XREF-004, JSS-HOUSE-003); spec 001's enum only has ERROR and WARNING. The enum extension is API-additive (no existing consumer breaks on the new value if they use exhaustive matching — caught at type-check time; if they use string comparison, the new value round-trips naturally). Lands as a Phase 2 foundational task before any info-severity rule registers. | **Map `info` to `warning` silently** — discards the catalogue's deliberate three-level severity distinction; reviewer explicitly wanted it for rules that "surface awareness but don't demand change". Rejected. **Skip info-severity rules entirely** — would retire 4 rules that the reviewer approved. Rejected; requires a spec-003 amendment. |
