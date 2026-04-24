---
description: "Task breakdown for spec 004: JSS Rule Modules — 15-category rollout"
---

# Tasks: JSS Rule Modules — Category-by-Category Implementation of the Spec-003 Catalogue

**Input**: Design documents from `/specs/004-jss-rule-modules/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓ (4 files), quickstart.md ✓

**Tests**: Unit tests are MANDATORY for every file created under `src/texlint/journals/jss/rules/` (Constitution §VIII TDD, §IX 100% branch coverage). Each category's test module MUST be committed (or staged in the branch) before its rule module's check bodies are written; the failing-then-passing transition must be visible in PR history.

**Organization**: Tasks are grouped by user story and implementation phase. Per-category rollout phases (Phase 3 through Phase 17) each deliver one `<category>.py` rule module and contribute to all four user stories (US1 rule coverage, US2 precision gate, US3 smoke-rule retrofit where applicable, US4 catalogue consistency).

**Category allowlist for small-group PRs** (per 2026-04-23 clarification): small groups of ≤3 closely-related categories MAY ship in the same PR. Documented pairings:
- `references` + `bibtex` — both inspect `ParsedDocument.bib_files`.
- `markup` + `naming` — both consume `terms.py`.
- Other groupings MUST be approved in a PR description before bundling.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no conflicting dependencies).
- **[Story]**: Maps the task to one or more user stories (US1/US2/US3/US4). Setup, Foundational, and Polish tasks omit the story tag.
- File paths are absolute within the repo; use as-is.

## Path Conventions

- **Repository root**: `/workspace`
- **Rule modules**: `src/texlint/journals/jss/rules/<category>.py`
- **Tests**: `tests/unit/rules/test_<category>.py`
- **Fixtures**: `tests/fixtures/violations/<category>/<rule_id>-{good,bad}.{tex,bib}`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: One-time environment / scripting prep. No existing-code edits.

- [ ] T001 Confirm `pip install -e '.[dev]'` is satisfied (PyYAML + pytest-cov present); if not, run the install. No code change — sanity check before Phase 2.
- [ ] T002 Create `scripts/eval-category.sh` wrapping `pytest --cov … && eval-jss scan && eval-jss human-review && eval-jss report --grep=<CATEGORY>` per `quickstart.md §2.7`. Make executable (`chmod +x`). Positional arg: `<category>` (lowercase, matches `catalogue.yaml` category id).

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Infrastructure that every category PR depends on — severity extension, codegen, private helpers, CI consistency tests, and the skeleton `JSSJournal.categories()`. **No category rollout begins until this phase is complete.**

**⚠️ CRITICAL**: No rule-module work can start until T003–T012 are green.

- [ ] T003 Extend `src/texlint/api.py`: add `Severity.INFO = "info"` to the `Severity` enum. Required by 4 info-severity catalogue rules (JSS-REFS-003, JSS-XREF-002, JSS-XREF-004, JSS-HOUSE-003).
- [ ] T004 [P] Audit existing `Severity.*` consumers. Run `grep -rn "Severity\." src/texlint/output/ eval/ | grep -v test_` and update each match to handle `INFO` sensibly: author/reviewer terminal renderers treat INFO like WARNING by default; `eval-jss report` surfaces INFO in its own bucket (see `data-model.md §1.2`). Per-file edits under `src/texlint/output/` and `eval/report.py` (if touched).
- [ ] T005 [P] Extend `tests/unit/api/test_severity.py` (or equivalent) to cover the new `Severity.INFO` round-trip: string value is `"info"`, enum ordering preserved.
- [ ] T006 Create `tools/generate_catalogue_data.py`: reads `specs/003-jss-rule-catalogue/catalogue.yaml`, emits `src/texlint/journals/jss/_catalogue_data.py` with three module-level exports — `RULES: dict[str, dict]` (keyed by rule_id, values have `category`, `severity: Severity`, `message_template`, `authority`, `authority_ref`, `inspects`, `auto_fixable`, `notes`), `RETIRED_RULE_IDS: frozenset[str]` (sourced from the catalogue's `retired_rule_ids` top-level field added in the spec-003 amendment), and `ROLLOUT_ORDER: tuple[str, ...]` (the 15 categories in the rollout order from spec 003 `tasks.md`). Script supports `--check` mode that regenerates in-memory and exits non-zero on drift. Format the output with the project's standard (match `ruff format` on write).
- [ ] T007 Generate the initial `src/texlint/journals/jss/_catalogue_data.py` by running `python -m tools.generate_catalogue_data` and commit it. Depends on T006.
- [ ] T008 [P] Add `tests/unit/journals/jss/test_catalogue_data_fresh.py` — asserts `python -m tools.generate_catalogue_data --check` exits 0. Runs in CI; fails when `catalogue.yaml` is amended without regenerating. Depends on T006.
- [ ] T009 [P] Create `src/texlint/journals/jss/rules/_helpers.py` with the 7 helpers enumerated in `data-model.md §3`: `_walk`, `_iter_with_parent`, `_lineno_col`, `_macro_args_text`, `_is_inside_verbatim`, `_is_inside_comment`, `_is_inside_math`. Pure functions; no module-level state. See `contracts/rules-module.md §Helpers` for canonical signatures.
- [ ] T010 [P] Write `tests/unit/journals/jss/rules/test_helpers.py` covering `_helpers.py` at 100% branch coverage. Run `scripts/vtest.sh tests/unit/journals/jss/rules/test_helpers.py --cov=src/texlint/journals/jss/rules/_helpers --cov-branch --cov-fail-under=100` to verify. Depends on T009.
- [ ] T011 Modify `src/texlint/journals/jss/__init__.py`: add skeleton `JSSJournal.categories()` with 15 lazy imports that return `RuleCategory` objects whose `rules: tuple[Rule, ...]` is empty `()` for every category not yet implemented. Categories returned in `_catalogue_data.ROLLOUT_ORDER`. This allows `test_catalogue_registration.py` to load without ImportError during early rollout.
- [ ] T012 [P] Create `tests/unit/journals/jss/test_catalogue_registration.py` per `contracts/catalogue-consistency.md` — 9 assertions (R-1..R-9). Depends on T007 and T011. Note: R-1/R-6 will fail on the empty-tuple skeleton until categories land; mark those `pytest.mark.xfail(strict=False, reason="rollout in progress")` and remove the xfail decoration per category as each category's module ships (a small per-category edit in the category PRs).

**Checkpoint**: Foundation ready when T003–T012 are green and committed. Per-category rollout (Phase 3+) can now begin. `test_catalogue_registration.py` runs in CI with xfail on incomplete categories; the drift-check test (`test_catalogue_data_fresh.py`) is green.

---

## Phase 3: Citations Category — 3 rules (Priority: P1) 🎯 First deliverable [US1, US2, US3, US4]

**Goal**: Ship `rules/citations.py` with JSS-CITE-002/003/004. Retire `cite_001_emph.py` (JSS-CITE-001 was retired in spec 003). Category owns 1 pre-populated skip-list entry (JSS-CITE-004).

**Independent Test**: After merge, `scripts/vtest.sh tests/unit/rules/test_citations.py --cov=src/texlint/journals/jss/rules/citations --cov-branch --cov-fail-under=100` passes; `scripts/eval-category.sh citations` shows each rule's precision ≥0.90 for rules with ≥10 labelled violations.

### Tests for citations (TDD — write and commit/stage first)

- [ ] T013 [P] [US1] Create fixture pair `tests/fixtures/violations/citations/JSS-CITE-002-{bad,good}.tex` from catalogue `example_violation`/`example_fix` wrapped in a minimal compilable JSS document per `contracts/test-template.md §Fixture file format`.
- [ ] T014 [P] [US1] Create fixture pair `tests/fixtures/violations/citations/JSS-CITE-003-{bad,good}.tex`.
- [ ] T015 [P] [US1] Create fixture pair `tests/fixtures/violations/citations/JSS-CITE-004-{bad,good}.tex`.
- [ ] T016 [US1, US4] Write failing `tests/unit/rules/test_citations.py` per `contracts/test-template.md` canonical shape: `test_rules_tuple_has_three_rules`, `test_rules_tuple_ids`, plus per-rule `TestCite002/003/004` classes (positive + good-fixture negative + ≥1 near-miss negative per rule). Confirm run fails with `ImportError` on `from texlint.journals.jss.rules.citations import ...`.

### Implementation for citations

- [ ] T017 [US1, US3] Create `src/texlint/journals/jss/rules/citations.py` per `contracts/rules-module.md` canonical shape: `check_jss_cite_002/003/004` callables, `_rule()` helper, module-level `rules: tuple[Rule, ...]` of 3 rules. Honour catalogue notes: CITE-002 strict same-paragraph scope (token span bounded by char nodes with blank lines); CITE-004 regex masks `\code{}`/`\verb{}`/verbatim/Code/CodeInput/CodeOutput/Sinput/Soutput/Scode envs (use `_helpers._is_inside_verbatim` and a code-mask helper).
- [ ] T018 [US3] Delete `src/texlint/journals/jss/rules/cite_001_emph.py` and `tests/unit/journals/jss/test_cite_001_emph.py` (JSS-CITE-001 retired; FR-015).
- [ ] T019 [US3] Update integration tests referencing `tests/fixtures/violations/JSS-CITE-001.tex` per FR-018. Audit: `grep -rn "JSS-CITE-001" tests/integration/` — for each match, remove the assertion, replace with a still-valid fixture (e.g., one of the new citations fixtures), or rename/delete the fixture file as appropriate.
- [ ] T020 [US1] Remove the `xfail` marker from the citations-relevant R-1/R-6 assertions in `test_catalogue_registration.py` (or remove xfail wholesale if citations is the only outstanding category in that test's param list). Remove the empty-tuple skeleton for citations in `JSSJournal.categories()` so it imports and returns `citations.rules`.
- [ ] T021 [US1] Verify 100% branch coverage: `scripts/vtest.sh tests/unit/rules/test_citations.py --cov=src/texlint/journals/jss/rules/citations --cov-branch --cov-fail-under=100`. Add auxiliary fixtures per FR-011 naming (`JSS-CITE-NNN-<descriptor>.tex`) for any uncovered branch. Loop until 100%.
- [ ] T022 [US2] Add `[[rules]]` entry for `JSS-CITE-004` to `eval/review-skip-list.toml` per `contracts/ai-skip-list.md`. `reason = "Regex-over-prose with code/verbatim masking; AI labeller rubber-stamps matches."`, `added_in_spec = "004"`.
- [ ] T023 [US2] Run `scripts/eval-category.sh citations`. Confirm every CITE-NNN rule with ≥10 labelled corpus violations shows precision ≥0.90. Rules below N=10 ship flagged "not yet measured" with a re-measurement plan recorded in the PR description per FR-013.
- [ ] T024 [US1, US2, US3, US4] Commit citations PR with precision-gate report in the commit message (`quickstart.md §2.8` format). Review consumes the report; CI enforces catalogue consistency + 100% branch coverage.

**Checkpoint**: citations category shipped. `test_catalogue_registration.py` passes for citations. Smoke rule `cite_001_emph.py` is gone.

---

## Phase 4: References Category — 7 rules (Priority: P1) [US1, US2, US3, US4]

**Goal**: Ship `rules/references.py` with JSS-REFS-001..007. Retire `bib_001_year.py`; JSS-REFS-001 semantically retrofits it. Category owns 3 pre-populated skip-list entries (JSS-REFS-002/005/006).

**Independent Test**: `scripts/vtest.sh tests/unit/rules/test_references.py --cov=... --cov-branch --cov-fail-under=100` green; `scripts/eval-category.sh references` precision gate passes.

- [ ] T025 [P] [US1] Create fixture pairs for all 7 references rules under `tests/fixtures/violations/references/`: `JSS-REFS-001-{bad,good}.bib` through `JSS-REFS-007-{bad,good}.bib` (or `.tex` if the catalogue declares tex-inspection for a given rule). Seed content from catalogue `example_violation`/`example_fix`.
- [ ] T026 [US1, US4] Write failing `tests/unit/rules/test_references.py` — 7 rules × (positive + good-fixture negative + ≥1 near-miss negative) + module-level invariants. Confirm ImportError.
- [ ] T027 [US1, US3] Create `src/texlint/journals/jss/rules/references.py` with `check_jss_refs_001..007` and module-level `rules` tuple of 7. JSS-REFS-001 reproduces `bib_001_year.py`'s year-presence check semantics.
- [ ] T028 [US3] Delete `src/texlint/journals/jss/rules/bib_001_year.py` and `tests/unit/journals/jss/test_bib_001_year.py` (FR-016) in the same commit.
- [ ] T029 [US1] Remove xfail for references in `test_catalogue_registration.py`; wire `references.rules` into `JSSJournal.categories()` (remove empty-tuple skeleton).
- [ ] T030 [US1] Verify 100% branch coverage with auxiliary fixtures as needed.
- [ ] T031 [US2] Add `JSS-REFS-002`, `JSS-REFS-005`, `JSS-REFS-006` to `eval/review-skip-list.toml` per `contracts/ai-skip-list.md`.
- [ ] T032 [US2] Run `scripts/eval-category.sh references` and capture precision-gate report.
- [ ] T033 [US1, US2, US3, US4] Commit references PR.

**Checkpoint**: references category shipped. `bib_001_year.py` retrofit complete.

---

## Phase 5: Bibtex Category — 4 rules (Priority: P1) [US1, US2, US4]

**Goal**: Ship `rules/bibtex.py` with JSS-BIBTEX-001..004. No retrofit. No skip-list entries.

**Note (bundling)**: MAY ship in the same PR as references per the allowlist (both inspect `bib_files`). If bundled, the PR description MUST include two separate precision-gate report blocks — one per category.

- [ ] T034 [P] [US1] Create fixture pairs for 4 bibtex rules under `tests/fixtures/violations/bibtex/`.
- [ ] T035 [US1, US4] Write failing `tests/unit/rules/test_bibtex.py`.
- [ ] T036 [US1] Create `src/texlint/journals/jss/rules/bibtex.py`.
- [ ] T037 [US1] Remove xfail + wire into `JSSJournal.categories()`.
- [ ] T038 [US1] Verify 100% branch coverage.
- [ ] T039 [US2] Run `scripts/eval-category.sh bibtex`.
- [ ] T040 [US1, US2, US4] Commit bibtex PR (or bundled references+bibtex PR).

**Checkpoint**: bibtex category shipped.

---

## Phase 6: Preamble Category — 8 rules (Priority: P1) [US1, US2, US4]

**Goal**: Ship `rules/preamble.py` with JSS-PRE-001..008. No retrofit. No skip-list entries. Largest category (8 rules).

**Note**: JSS-PRE-003/PRE-007/PRE-008 fire only when the target command (`\title`/`\author`/`\Keywords`) contains LaTeX markup; presence-only is silent (FR-019).

- [ ] T041 [P] [US1] Create fixture pairs for all 8 preamble rules under `tests/fixtures/violations/preamble/`.
- [ ] T042 [US1, US4] Write failing `tests/unit/rules/test_preamble.py`.
- [ ] T043 [US1] Create `src/texlint/journals/jss/rules/preamble.py`. Honour the markup-only firing contract for PRE-003/007/008.
- [ ] T044 [US1] Remove xfail + wire.
- [ ] T045 [US1] Verify 100% branch coverage. Add auxiliary fixtures for the "no markup → no flag" branch on PRE-003/007/008.
- [ ] T046 [US2] Run `scripts/eval-category.sh preamble`.
- [ ] T047 [US1, US2, US4] Commit preamble PR.

**Checkpoint**: preamble category shipped.

---

## Phase 7: Structure Category — 6 rules (Priority: P1) [US1, US2, US4]

**Goal**: Ship `rules/structure.py` with JSS-STRUCT-001..006. No retrofit. No skip-list entries.

- [ ] T048 [P] [US1] Create fixture pairs for 6 structure rules.
- [ ] T049 [US1, US4] Write failing `tests/unit/rules/test_structure.py`.
- [ ] T050 [US1] Create `src/texlint/journals/jss/rules/structure.py`.
- [ ] T051 [US1] Remove xfail + wire.
- [ ] T052 [US1] Verify 100% branch coverage.
- [ ] T053 [US2] Run `scripts/eval-category.sh structure`.
- [ ] T054 [US1, US2, US4] Commit structure PR.

**Checkpoint**: structure category shipped.

---

## Phase 8: Markup Category — 4 rules (Priority: P1) [US1, US2, US4]

**Goal**: Ship `rules/markup.py` with JSS-MARKUP-001..004. No retrofit. Category owns 1 skip-list entry (JSS-MARKUP-001).

**Note**: JSS-MARKUP-001 masks math-mode content (use `_helpers._is_inside_math`), skips "Pascal", and filters single-letter initials before token-match (FR-019).

- [ ] T055 [P] [US1] Create fixture pairs for 4 markup rules (auxiliary fixtures expected for JSS-MARKUP-001's math/Pascal/initial branches).
- [ ] T056 [US1, US4] Write failing `tests/unit/rules/test_markup.py`.
- [ ] T057 [US1] Create `src/texlint/journals/jss/rules/markup.py`. Uses `terms.py`.
- [ ] T058 [US1] Remove xfail + wire.
- [ ] T059 [US1] Verify 100% branch coverage (math/Pascal/initial auxiliary fixtures).
- [ ] T060 [US2] Add `JSS-MARKUP-001` to `eval/review-skip-list.toml`.
- [ ] T061 [US2] Run `scripts/eval-category.sh markup`.
- [ ] T062 [US1, US2, US4] Commit markup PR.

**Checkpoint**: markup category shipped.

---

## Phase 9: Crossrefs Category — 4 rules (Priority: P1) [US1, US2, US4]

**Goal**: Ship `rules/crossrefs.py` with JSS-XREF-001..004. Two info-severity rules (XREF-002, XREF-004).

- [ ] T063 [P] [US1] Create fixture pairs for 4 crossrefs rules.
- [ ] T064 [US1, US4] Write failing `tests/unit/rules/test_crossrefs.py`.
- [ ] T065 [US1] Create `src/texlint/journals/jss/rules/crossrefs.py`.
- [ ] T066 [US1] Remove xfail + wire.
- [ ] T067 [US1] Verify 100% branch coverage.
- [ ] T068 [US2] Run `scripts/eval-category.sh crossrefs`.
- [ ] T069 [US1, US2, US4] Commit crossrefs PR.

**Checkpoint**: crossrefs category shipped.

---

## Phase 10: Code Style Category — 3 rules (Priority: P1) [US1, US2, US4]

**Goal**: Ship `rules/code_style.py` with JSS-CODE-001..003. Category owns 1 skip-list entry (JSS-CODE-003).

- [ ] T070 [P] [US1] Create fixture pairs for 3 code_style rules.
- [ ] T071 [US1, US4] Write failing `tests/unit/rules/test_code_style.py`.
- [ ] T072 [US1] Create `src/texlint/journals/jss/rules/code_style.py`.
- [ ] T073 [US1] Remove xfail + wire.
- [ ] T074 [US1] Verify 100% branch coverage.
- [ ] T075 [US2] Add `JSS-CODE-003` to `eval/review-skip-list.toml`.
- [ ] T076 [US2] Run `scripts/eval-category.sh code_style`.
- [ ] T077 [US1, US2, US4] Commit code_style PR.

**Checkpoint**: code_style category shipped.

---

## Phase 11: Code Width Category — 1 rule (Priority: P1) [US1, US2, US3, US4]

**Goal**: Ship `rules/code_width.py` with JSS-WIDTH-001. Retire `src_001_width.py`; WIDTH-001 retrofits it with a configurable column limit via `ToolConfig` (FR-017, FR-019). This is the only rule that inspects `raw_source`.

- [ ] T078 [P] [US1] Create fixture pair `tests/fixtures/violations/code_width/JSS-WIDTH-001-{bad,good}.tex` plus an auxiliary fixture exercising the configurable-limit path (e.g., `JSS-WIDTH-001-custom-limit.tex`).
- [ ] T079 [US1, US4] Write failing `tests/unit/rules/test_code_width.py` including a test that passes a custom `ToolConfig` column limit (e.g., 100) and asserts the rule respects it.
- [ ] T080 [US1, US3] Create `src/texlint/journals/jss/rules/code_width.py`. Default limit 80 columns; read override from `ToolConfig` per FR-019. Reads `raw_source` per catalogue's `inspects: [raw_source]` declaration — must skip comment lines and verbatim blocks via `_helpers._is_inside_verbatim`/`_is_inside_comment`.
- [ ] T081 [US3] Delete `src/texlint/journals/jss/rules/src_001_width.py` and `tests/unit/journals/jss/test_src_001_width.py` (FR-017) in the same commit.
- [ ] T082 [US1] Remove xfail + wire into `JSSJournal.categories()`.
- [ ] T083 [US1] Verify 100% branch coverage.
- [ ] T084 [US2] Run `scripts/eval-category.sh code_width`.
- [ ] T085 [US1, US2, US3, US4] Commit code_width PR.

**Checkpoint**: code_width category shipped. `src_001_width.py` retrofit complete. All three Step 1 smoke rules are now retired (citations, references, code_width phases done).

---

## Phase 12: Naming Category — 2 rules (Priority: P1) [US1, US2, US4]

**Goal**: Ship `rules/naming.py` with JSS-NAMING-001..002. Uses `terms.py`. No skip-list entries.

**Note (bundling)**: MAY ship with `markup` per the allowlist (both consume `terms.py`); if bundled, include two precision-gate reports.

- [ ] T086 [P] [US1] Create fixture pairs for 2 naming rules.
- [ ] T087 [US1, US4] Write failing `tests/unit/rules/test_naming.py`.
- [ ] T088 [US1] Create `src/texlint/journals/jss/rules/naming.py`.
- [ ] T089 [US1] Remove xfail + wire.
- [ ] T090 [US1] Verify 100% branch coverage.
- [ ] T091 [US2] Run `scripts/eval-category.sh naming`.
- [ ] T092 [US1, US2, US4] Commit naming PR (or bundled markup+naming PR).

**Checkpoint**: naming category shipped.

---

## Phase 13: Operators Category — 4 rules (Priority: P1) [US1, US2, US4]

**Goal**: Ship `rules/operators.py` with JSS-OPER-001..004. Category owns 1 skip-list entry (JSS-OPER-001).

**Note**: JSS-OPER-003 has a carve-out — no-blank-line-around-equation is SILENT when the equation body ends with a period (natural paragraph end; FR-019).

- [ ] T093 [P] [US1] Create fixture pairs for 4 operators rules (auxiliary fixture for OPER-003's period carve-out).
- [ ] T094 [US1, US4] Write failing `tests/unit/rules/test_operators.py`.
- [ ] T095 [US1] Create `src/texlint/journals/jss/rules/operators.py`. Honour OPER-003 carve-out.
- [ ] T096 [US1] Remove xfail + wire.
- [ ] T097 [US1] Verify 100% branch coverage (OPER-003 period carve-out branch).
- [ ] T098 [US2] Add `JSS-OPER-001` to `eval/review-skip-list.toml`.
- [ ] T099 [US2] Run `scripts/eval-category.sh operators`.
- [ ] T100 [US1, US2, US4] Commit operators PR.

**Checkpoint**: operators category shipped.

---

## Phase 14: Abbreviations Category — 1 rule (Priority: P1) [US1, US2, US4]

**Goal**: Ship `rules/abbreviations.py` with JSS-ABBR-001 (ABBR-002 retired in spec 003). Category owns 1 skip-list entry (JSS-ABBR-001).

- [ ] T101 [P] [US1] Create fixture pair for JSS-ABBR-001.
- [ ] T102 [US1, US4] Write failing `tests/unit/rules/test_abbreviations.py`.
- [ ] T103 [US1] Create `src/texlint/journals/jss/rules/abbreviations.py`.
- [ ] T104 [US1] Remove xfail + wire.
- [ ] T105 [US1] Verify 100% branch coverage.
- [ ] T106 [US2] Add `JSS-ABBR-001` to `eval/review-skip-list.toml`.
- [ ] T107 [US2] Run `scripts/eval-category.sh abbreviations`.
- [ ] T108 [US1, US2, US4] Commit abbreviations PR.

**Checkpoint**: abbreviations category shipped.

---

## Phase 15: House Style Category — 3 rules (Priority: P1) [US1, US2, US4]

**Goal**: Ship `rules/house_style.py` with JSS-HOUSE-001..003. Category owns 1 skip-list entry (JSS-HOUSE-001). One info-severity rule (HOUSE-003).

- [ ] T109 [P] [US1] Create fixture pairs for 3 house_style rules.
- [ ] T110 [US1, US4] Write failing `tests/unit/rules/test_house_style.py`.
- [ ] T111 [US1] Create `src/texlint/journals/jss/rules/house_style.py`.
- [ ] T112 [US1] Remove xfail + wire.
- [ ] T113 [US1] Verify 100% branch coverage.
- [ ] T114 [US2] Add `JSS-HOUSE-001` to `eval/review-skip-list.toml`.
- [ ] T115 [US2] Run `scripts/eval-category.sh house_style`.
- [ ] T116 [US1, US2, US4] Commit house_style PR.

**Checkpoint**: house_style category shipped.

---

## Phase 16: Typography Category — 4 rules (Priority: P1) [US1, US2, US4]

**Goal**: Ship `rules/typography.py` with JSS-TYPO-001..004. No skip-list entries.

- [ ] T117 [P] [US1] Create fixture pairs for 4 typography rules.
- [ ] T118 [US1, US4] Write failing `tests/unit/rules/test_typography.py`.
- [ ] T119 [US1] Create `src/texlint/journals/jss/rules/typography.py`.
- [ ] T120 [US1] Remove xfail + wire.
- [ ] T121 [US1] Verify 100% branch coverage.
- [ ] T122 [US2] Run `scripts/eval-category.sh typography`.
- [ ] T123 [US1, US2, US4] Commit typography PR.

**Checkpoint**: typography category shipped.

---

## Phase 17: Capitalization Category — 4 rules (Priority: P1) [US1, US2, US4]

**Goal**: Ship `rules/capitalization.py` with JSS-CAP-001..004. Category owns 4 skip-list entries (JSS-CAP-001/002/003/004) — most of any category. Last category in the rollout.

- [ ] T124 [P] [US1] Create fixture pairs for 4 capitalization rules.
- [ ] T125 [US1, US4] Write failing `tests/unit/rules/test_capitalization.py`.
- [ ] T126 [US1] Create `src/texlint/journals/jss/rules/capitalization.py`. Uses `terms.py`.
- [ ] T127 [US1] Remove xfail + wire (this removes the last xfail from `test_catalogue_registration.py`).
- [ ] T128 [US1] Verify 100% branch coverage.
- [ ] T129 [US2] Add `JSS-CAP-001`, `JSS-CAP-002`, `JSS-CAP-003`, `JSS-CAP-004` to `eval/review-skip-list.toml`. With this update, all 13 pre-populated skip-list entries are in place per `contracts/ai-skip-list.md`.
- [ ] T130 [US2] Run `scripts/eval-category.sh capitalization`.
- [ ] T131 [US1, US2, US4] Commit capitalization PR.

**Checkpoint**: all 15 categories shipped. `test_catalogue_registration.py` is fully green with no xfails. The catalogue-registered rule set equals the 58-rule active catalogue.

---

## Phase 18: Polish & End-of-Spec Validation

**Purpose**: Final cross-cutting validation per `quickstart.md §5` end-of-spec checkpoint.

- [ ] T132 Run the full test suite: `scripts/vtest.sh tests/`. All tests green including `test_catalogue_registration.py` (R-1..R-9 all passing), `test_catalogue_data_fresh.py`, every `tests/unit/rules/test_<category>.py`.
- [ ] T133 [P] Run repo-wide branch-coverage gate: `pytest --cov=src/texlint/journals/jss/rules --cov-branch --cov-fail-under=100`. Must be green across every rule module.
- [ ] T134 [P] Run the golden-path demo: `jss-lint docs/jss-template/article.tex docs/jss-template/refs.bib`. Expect zero violations (or only violations whose rules are on the template-allowlist per SC-002). Any unexpected violation → open a follow-up issue; do NOT suppress in the template.
- [ ] T135 [P] Run a synthetic "one-bad-fixture-per-rule" aggregate and assert that every catalogue rule id appears at least once in the output, with the catalogue-declared severity (SC-001). This test can live under `tests/integration/test_full_catalogue_coverage.py`.
- [ ] T136 Produce the end-of-spec summary: every rule above the N=10 floor clears 90% precision; every rule still at "not yet measured" has a documented re-measurement plan (issue id, corpus milestone, or scheduled refresh per FR-013). Close the spec against SC-010.
- [ ] T137 [P] Update `docs/` contributor pointers (if any) to reference the new rule-module layout. `quickstart.md` is the authoritative contributor onboarding; minimise doc duplication.
- [ ] T138 Fill in the final sign-off in `specs/003-jss-rule-catalogue/checklists/rule-catalogue-review.md` OQ-11 (corpus growth to ~50 papers), now satisfied by the rollout corpus expansion.

**Checkpoint**: spec 004 closes when T132–T138 are all done and SC-010 is satisfied.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: T001–T002 are one-time prep; T002 can happen any time before Phase 17.
- **Foundational (Phase 2)**: T003–T012 block every category PR. Within Phase 2:
  - T003 blocks T004, T005.
  - T006 blocks T007 blocks T008.
  - T009 blocks T010.
  - T007, T011 block T012.
  - Parallelizable within Phase 2: {T004, T005} (depend on T003); {T008} (depends on T007); {T009→T010}; {T011} (depends on T007).
- **Category phases (Phase 3–17)**: each phase depends on Phase 2 completion. Categories are **largely independent** of each other and can ship in any order, subject to:
  - The three smoke-rule retrofits (citations → cite_001, references → bib_001, code_width → src_001) must ship ≤ one-per-PR and the smoke file's deletion is in the same commit as the category's addition.
  - PRs bundled under the allowlist (≤3 categories, shared `inspects` or `_helpers`/`terms.py` consumer overlap) must run each bundled category's precision gate separately.
  - If the rollout order from `catalogue.yaml` differs from a reviewer's preference, categories can be re-ordered freely — the PR dependency graph is otherwise flat.
- **Polish (Phase 18)**: depends on all 15 category phases. T136 (SC-010 sign-off) is the ultimate closing task.

### User Story Dependencies

- **US1 (rule coverage, P1)**: contributed to by every category phase. Delivered when all 15 categories ship.
- **US2 (precision gate, P1)**: contributed to by every category phase (precision-gate report per PR). Delivered in full at Phase 18 (T136) when every rule is either cleared or has a re-measurement plan.
- **US3 (smoke-rule retrofit, P2)**: delivered across Phase 3 (citations, retire cite_001), Phase 4 (references, retrofit bib_001), and Phase 11 (code_width, retrofit src_001). US3 is complete after Phase 11.
- **US4 (catalogue consistency, P1)**: enforced structurally by Phase 2 (T012) plus each category phase's xfail-removal task. Fully delivered when Phase 17 removes the last xfail.

### Within Each Category Phase

Within each Phase 3–17 (template):

1. Fixtures task (parallel across rules, within category)
2. Failing test module (depends on fixtures; ONE test file per category)
3. Rule module implementation (depends on test; plus retrofit deletions in Phases 3/4/11)
4. Xfail removal + wire (depends on implementation)
5. Branch-coverage gate (depends on wire; may iterate with new auxiliary fixtures)
6. Skip-list update (if applicable; independent of 3–5)
7. Precision-gate run (depends on everything above + current corpus state)
8. Commit (PR)

Steps 1 and 6 can be parallel with 2–5 if fixture-free. Step 7 is strictly the last per-category step before the commit.

### Parallel Opportunities

- Within Phase 2: T004+T005 parallel after T003; T010 parallel with T011; T008 parallel with T009/T010/T011 after T007.
- Between categories: all 15 category phases are independent of each other; a two-developer team can work Phase 3 and Phase 4 in parallel after Phase 2.
- Within each category phase: all fixture-creation subtasks are trivially parallelizable (different files).
- Polish phase: T133/T134/T135/T137 are parallel (different scopes).

---

## Parallel Example: Phase 2 (Foundational)

```bash
# After T003 (Severity.INFO) lands:
Task: "[P] Audit Severity consumers for INFO handling"                # T004
Task: "[P] Add test_severity round-trip for INFO"                     # T005

# After T007 (generated _catalogue_data.py committed) lands:
Task: "[P] Add test_catalogue_data_fresh.py drift check"              # T008
Task: "[P] Write _helpers.py + test_helpers.py with 100% coverage"    # T009+T010
```

## Parallel Example: Phase 3 (Citations) fixtures

```bash
# Fixtures can be written in parallel — one developer per rule:
Task: "[P] Create JSS-CITE-002 fixture pair"                          # T013
Task: "[P] Create JSS-CITE-003 fixture pair"                          # T014
Task: "[P] Create JSS-CITE-004 fixture pair"                          # T015
```

## Parallel Example: Two-developer category rollout

```bash
# After Phase 2 completes, two developers can work different categories in parallel:
# Developer A: Phase 3 (citations) — 12 tasks
# Developer B: Phase 5 (bibtex)    — 7 tasks
# Neither category depends on the other; PRs land independently.
```

---

## Implementation Strategy

### MVP (First Category)

1. Complete Phase 1 (Setup): T001, T002.
2. Complete Phase 2 (Foundational): T003–T012.
3. Complete Phase 3 (Citations): T013–T024.
4. **STOP and VALIDATE**: 3 rules live, `test_catalogue_registration.py` green for citations, `cite_001_emph.py` retired, `JSS-CITE-004` in skip-list, precision gate passed.
5. With the MVP in hand, every subsequent category follows the same 8–13-task template.

### Incremental Delivery

Each of Phases 3–17 is an independent PR (or small-bundle PR). After each:

- Merge adds ~2–8 rules to `jss-lint`'s active set.
- CI gate enforces 100% branch coverage + catalogue consistency on merge.
- Precision-gate report attached to the PR description.
- Documentation and `quickstart.md` guide the next contributor.

### Parallel Team Strategy

With ≥2 developers after Phase 2:

- Categories split among developers. Each dev picks any category not-yet-shipped.
- Smoke-retrofit phases (3, 4, 11) can be interleaved with non-retrofit phases freely.
- Precision-gate labelling is the human-in-the-loop bottleneck; schedule it first.

### Closing Discipline

- No "I'll fix branch coverage later" — each category PR must hit 100% before merge.
- No silent precision-gate failures — every PR description cites the report.
- No catalogue drift — any rule retirement or refinement during the rollout goes through a spec-003 amendment PR, NEVER a direct `catalogue.yaml` edit in a 004 branch.
- When all 15 categories have shipped, run Phase 18 and close the spec against SC-010.

---

## Notes

- [P] = different files, no shared dependency at the moment the task runs.
- [Story] labels: US1 (rule coverage), US2 (precision gate), US3 (smoke retrofit), US4 (catalogue consistency).
- Per-category PR is the default commit unit; small-group bundling allowed per the allowlist.
- Verify fixtures and failing tests before writing check bodies (§VIII TDD).
- Branch-coverage failures are category-blocking, not deferrable.
- Skip-list entries land with their category's PR, not in a separate PR.
- Avoid: duplicate rule registrations, category drift, catalogue-source-of-truth bypass, speculative cross-category helpers.
