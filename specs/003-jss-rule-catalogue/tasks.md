---

description: "Tasks for feature 003 — JSS Rule Catalogue"
---

# Tasks: JSS Rule Catalogue — From 5 Smoke Rules to ~50 Production Rules

**Input**: Design documents from `/specs/003-jss-rule-catalogue/`
**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md)

**Tests**: Unit tests are **mandatory** for every task that creates or edits a file under `src/texlint/journals/jss/rules/` (Constitution §VIII TDD, §IX 100% branch coverage). The test task MUST precede the implementation task it covers. Tests for `terms.py` and for the catalogue data file are also mandatory per spec FR-020 / FR-008. CI will fail if a rule module lands without its matching 100%-branch-covered test file.

**Organization**: Phases are grouped by user story. US2 (category-by-category rollout) expands into 15 sub-phases, one per category, in the rollout order pinned by spec FR-017 and research §7. The per-category pattern is identical across all 15 sub-phases; see [quickstart.md §2](quickstart.md) for the canonical loop.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files, no dependencies)
- **[Story]**: US1 | US2 | US3 | US4, mapping to spec.md user stories
- **[Human]**: requires human-in-the-loop work (labelling, judgement) that cannot be fully automated
- Every task names exact file paths

## Path Conventions

Single-project layout rooted at `/workspace`. Rule modules live under `src/texlint/journals/jss/rules/`; tests under `tests/unit/`; fixtures under `tests/fixtures/violations/`; catalogue artefacts under `specs/003-jss-rule-catalogue/`; renderer under `tools/`.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: project tooling changes that every later phase consumes.

- [ ] T001 Add `"PyYAML>=6.0"` to `[project.optional-dependencies].dev` in `pyproject.toml` (the only new dependency added by this spec; `jss-lint` runtime deps are unchanged).
- [ ] T002 Add `"tools"` to `tool.hatch.build.targets.sdist.include` in `pyproject.toml` so `python -m tools.render_catalogue` works from a source install but the wheel is still `src/texlint`-only.
- [ ] T003 [P] Create empty package stubs: `tools/__init__.py`, `tests/unit/journals/jss/__init__.py`, and `tests/unit/rules/__init__.py`.
- [ ] T004 [P] Create fixture directory scaffolding: `tests/fixtures/violations/` with one empty `<category>/` subdirectory per category listed in `plan.md` and a `README.md` at `tests/fixtures/violations/README.md` explaining the per-rule good/bad pair naming convention (per contracts/rules-module.md §Test contract).

**Checkpoint**: `pip install -e '.[dev]'` succeeds; `python -c "import yaml"` works; empty test/fixture trees exist.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: small structural prereqs that every user story needs. The catalogue itself is US1's deliverable; only genuinely shared scaffolding lives here.

- [ ] T005 Create the category-abbreviation mapping table as a Python dict in `tools/_catalogue_validate.py` (see contracts/catalogue-schema.md `rule_id` prefix table). This module is imported by both the renderer and the catalogue tests, so it lands before either.
- [ ] T006 Verify `docs/jss-template/jss.cls` and `docs/jss-template/article.tex` exist at the paths the catalogue's `authority_ref` fields will reference; update `docs/jss-template/README.md` if the provenance section does not already record the upstream URL, fetch date, and SHA256 of the zip (spec FR-007). (Existing vendored copy is at commit `cf4e5be`; this task verifies completeness only.)

**Checkpoint**: shared validator module exists; vendored template's provenance is complete.

---

## Phase 3: User Story 1 — Authoritative, source-traceable rule catalogue (Priority: P1) 🎯 MVP BLOCKER

**Goal**: `catalogue.yaml` is drafted, validated, rendered to `catalogue.md`, and proves every structural invariant in contracts/catalogue-schema.md. Without this phase, no rule module can land — every rule implementation reads from this catalogue.

**Independent test**: `pytest tests/unit/journals/jss/test_catalogue.py tests/unit/journals/jss/test_render.py -x` is green; `specs/003-jss-rule-catalogue/catalogue.md` is checked in and matches what the renderer produces from `catalogue.yaml`.

### Tests for User Story 1 (mandatory)

> Write these tests FIRST, let them FAIL on an empty/invalid catalogue, then make them pass.

- [ ] T007 [P] [US1] Write `tests/unit/journals/jss/test_catalogue.py` covering all ten data-model.md §1.5 invariants plus the forbidden-keys check from contracts/catalogue-schema.md. Tests parse `catalogue.yaml` via `yaml.safe_load`, assert structure, and validate `authority_ref` resolvability against `docs/jss-template/` for `jss_cls` / `article_tex` rows.
- [ ] T008 [P] [US1] Write `tests/unit/journals/jss/test_render.py` covering: (a) rendering is deterministic (two runs produce identical output), (b) rendered markdown matches committed `catalogue.md` byte-for-byte, (c) `--check` CLI mode returns non-zero when the committed markdown drifts.

### Implementation for User Story 1

- [ ] T009 [US1] Draft `specs/003-jss-rule-catalogue/catalogue.yaml` with the top-level shape from contracts/catalogue-schema.md: `version: 1`, `source_vendored_at: "2021-05-23"`, the 15-category list, and one rule row per rule. Derive each row from the authority coverage matrices in `checklists/rule-catalogue-review.md` §§1.1–1.4; every row MUST cite at least one of `jss_cls` / `article_tex` / `style_guide` / `author_instructions` with a resolvable `authority_ref`. Include the three retrofitted Step 1 rules (JSS-CITE-001, JSS-REFS-001, JSS-WIDTH-001) as ordinary rows.
- [ ] T010 [P] [US1] Implement `tools/render_catalogue.py` per contracts/rendering.md — `yaml.safe_load` → sort by `(category_order_index, rule_id_counter_asc)` → emit header + per-category summary table + per-rule detail block → write atomically via `tempfile` + `os.replace`. Supports `--check` mode (compare without writing, exit 0/1). Reuses `tools/_catalogue_validate.py` (T005) for schema validation.
- [ ] T011 [US1] Run `python -m tools.render_catalogue` to produce `specs/003-jss-rule-catalogue/catalogue.md`. Check in both `catalogue.yaml` and `catalogue.md`.
- [ ] T012 [US1] Run `pytest tests/unit/journals/jss/test_catalogue.py tests/unit/journals/jss/test_render.py -x` and resolve any failures by editing `catalogue.yaml` (not by weakening tests). Iterate until green.
- [ ] T013 [US1] Walk `checklists/rule-catalogue-review.md` §1.1–1.4 and fill in the `covering_rule_ids` column for every enumerated provision. Every provision MUST have either ≥1 `covering_rule_ids` value or `status = out-of-scope` with a one-line rationale. Gaps (zero coverage, not out-of-scope) either close by adding rules to `catalogue.yaml` (loop back to T009) or explicitly convert to `out-of-scope`.
- [ ] T014 [US1] Re-render and re-test: `python -m tools.render_catalogue && pytest tests/unit/journals/jss/ -x`.
- [ ] T015 [US1] Open `checklists/rule-catalogue-review.md` §5 (Open questions) and close every item (answer or defer with rationale). §§2–4 remain empty until US2 implementations land.

**Checkpoint**: catalogue is drafted, validated, rendered; every provision in §§1.1–1.4 of the reviewer checklist is annotated. US2 category work is unblocked.

---

## Phase 4: User Story 4 — Shared term list (Priority: P2)

**Goal**: `src/texlint/journals/jss/terms.py` exists with the `LANGUAGES`, `R_PACKAGES`, `CANONICAL`, and `canonical_form(...)` surface; consuming rule modules (future US2 work) can import it. Independent of US1 in principle; landed here in priority order.

**Independent test**: `pytest tests/unit/journals/jss/test_terms.py -x` is green with all six invariants (T-01..T-06 in contracts/terms-list.md).

### Tests for User Story 4 (mandatory)

- [ ] T016 [P] [US4] Write `tests/unit/journals/jss/test_terms.py` covering invariants T-01..T-06 from contracts/terms-list.md: `CANONICAL.values()` ⊆ LANGUAGES ∪ R_PACKAGES; `CANONICAL` keys disjoint from LANGUAGES ∪ R_PACKAGES; `canonical_form` is a fixed point on canonical tokens; `canonical_form` resolves aliases; `canonical_form("")` and `canonical_form("  ")` return `None`; rule-module shadow-term grep with an explicit allowlist.

### Implementation for User Story 4

- [ ] T017 [US4] Implement `src/texlint/journals/jss/terms.py` per contracts/terms-list.md — `LANGUAGES: frozenset[str]`, `R_PACKAGES: frozenset[str]`, `CANONICAL: Mapping[str, str]` via `types.MappingProxyType`, `canonical_form(token: str) -> str | None`. Seed contents from research §5 and from style-guide directives SG-044..SG-052.
- [ ] T018 [US4] Run `pytest tests/unit/journals/jss/test_terms.py -x` and resolve failures by editing `terms.py` until green.

**Checkpoint**: `terms.py` is single-source-of-truth for canonical spellings. US2 categories that consume it (`capitalization`, `naming`, `house_style`, `references`, `markup`, `citations`, `abbreviations`) can import it when they land.

---

## Phase 5: User Story 2 / Category `citations` (Priority: P1 — rollout position #1)

**Goal**: all `citations` rules implemented; 100% branch coverage; N≥10 rules meeting ≥90% precision gate; the Step 1 smoke rule `cite_001_emph.py` is deleted.

**Independent test**: `pytest tests/unit/rules/test_citations.py --cov=src/texlint/journals/jss/rules/citations --cov-branch --cov-fail-under=100 -x` green; `eval-jss report` shows every `JSS-CITE-NNN` rule with ≥10 labelled violations at ≥90% precision.

- [ ] T019 [US2] Create fixture files under `tests/fixtures/violations/citations/` — one `JSS-CITE-NNN-good.{tex|bib}` and one `JSS-CITE-NNN-bad.{tex|bib}` per rule in the `citations` category of `catalogue.yaml`. Contents are the `example_violation` / `example_fix` values from the YAML.
- [ ] T020 [US2] Write `tests/unit/rules/test_citations.py` — for each rule in the category, one `test_<rule_id>_flags_bad` asserting the rule fires exactly once on the `-bad` fixture, and one `test_<rule_id>_passes_good` asserting zero violations on the `-good` fixture. Tests import the private `_check_jss_citations_NNN` callables from the (not-yet-existing) module; expected to fail.
- [ ] T021 [US2] Implement `src/texlint/journals/jss/rules/citations.py` per contracts/rules-module.md — private `_check_jss_citations_NNN` callables, module-level `Rule` instances with `check=` bound, module-level `rules: tuple[Rule, ...]`. Every emitted `Violation.fix = None` (spec FR-022).
- [ ] T022 [US2] Wire `citations` into `src/texlint/journals/jss/__init__.py` `JSSJournal.categories()` — add the lazy `from texlint.journals.jss.rules import citations` and the matching `RuleCategory(id="citations", title="Citations", rules=citations.rules)` entry. In the SAME commit, delete `src/texlint/journals/jss/rules/cite_001_emph.py` and `tests/unit/journals/jss/rules/test_cite_001_emph.py`, and remove the old `cite_001` import and `RuleCategory` line from `__init__.py`.
- [ ] T023 [US2] Verify 100% branch coverage: `pytest tests/unit/rules/test_citations.py --cov=src/texlint/journals/jss/rules/citations --cov-branch --cov-fail-under=100 -x`. Add fixtures for any uncovered branch; do not gate-skip.
- [ ] T024 [US2] [Human] Run the corpus precision gate — `eval-jss scan`, `eval-jss human-review` for the new `JSS-CITE-NNN` violations, `eval-jss report`. For every rule with ≥10 labelled violations, confirm precision ≥ 90%; refine or retire rules that fall short. Rules with <10 labelled violations ship as "not yet measured".

**Checkpoint**: `citations` commits green; Step 1 smoke rule `cite_001_emph.py` deleted; the rollout is off the ground.

---

## Phase 6: User Story 2 / Category `references` (Priority: P1 — rollout position #2)

**Goal**: all `references` (BibTeX content) rules implemented; smoke rule `bib_001_year.py` deleted.

**Independent test**: as Phase 5 template, substituting `references` and `JSS-REFS-NNN`.

- [ ] T025 [US2] Create fixture files under `tests/fixtures/violations/references/` — `JSS-REFS-NNN-{good,bad}.{tex|bib}` pairs from `catalogue.yaml`.
- [ ] T026 [US2] Write `tests/unit/rules/test_references.py` — per-rule flag/pass tests as for Phase 5.
- [ ] T027 [US2] Implement `src/texlint/journals/jss/rules/references.py`.
- [ ] T028 [US2] Wire `references` into `JSSJournal.categories()`; in the same commit, delete `src/texlint/journals/jss/rules/bib_001_year.py` and `tests/unit/journals/jss/rules/test_bib_001_year.py`, and remove the old `bib_001` import and line.
- [ ] T029 [US2] Verify 100% branch coverage on `rules/references.py`.
- [ ] T030 [US2] [Human] Run the corpus precision gate for `JSS-REFS-NNN`.

**Checkpoint**: `references` commits green; Step 1 smoke rule `bib_001_year.py` deleted.

---

## Phase 7: User Story 2 / Category `bibtex` (Priority: P1 — rollout position #3)

**Goal**: all `bibtex` (mechanical BibTeX) rules implemented.

- [ ] T031 [US2] Create fixture files under `tests/fixtures/violations/bibtex/` — `JSS-BIBTEX-NNN-{good,bad}.bib` pairs.
- [ ] T032 [US2] Write `tests/unit/rules/test_bibtex.py` — per-rule flag/pass tests.
- [ ] T033 [US2] Implement `src/texlint/journals/jss/rules/bibtex.py`.
- [ ] T034 [US2] Wire `bibtex` into `JSSJournal.categories()` + verify 100% branch coverage.
- [ ] T035 [US2] [Human] Run the corpus precision gate for `JSS-BIBTEX-NNN`.

**Checkpoint**: `bibtex` commits green.

---

## Phase 8: User Story 2 / Category `preamble` (rollout position #4)

- [ ] T036 [US2] Create fixture files under `tests/fixtures/violations/preamble/` — `JSS-PRE-NNN-{good,bad}.tex` pairs.
- [ ] T037 [US2] Write `tests/unit/rules/test_preamble.py`.
- [ ] T038 [US2] Implement `src/texlint/journals/jss/rules/preamble.py`.
- [ ] T039 [US2] Wire into `JSSJournal.categories()` + verify 100% branch coverage.
- [ ] T040 [US2] [Human] Run the corpus precision gate for `JSS-PRE-NNN`.

---

## Phase 9: User Story 2 / Category `structure` (rollout position #5)

- [ ] T041 [US2] Create fixtures under `tests/fixtures/violations/structure/`.
- [ ] T042 [US2] Write `tests/unit/rules/test_structure.py`.
- [ ] T043 [US2] Implement `src/texlint/journals/jss/rules/structure.py`.
- [ ] T044 [US2] Wire into `JSSJournal.categories()` + 100% branch coverage.
- [ ] T045 [US2] [Human] Precision gate for `JSS-STRUCT-NNN`.

---

## Phase 10: User Story 2 / Category `markup` (rollout position #6)

- [ ] T046 [US2] Create fixtures under `tests/fixtures/violations/markup/`.
- [ ] T047 [US2] Write `tests/unit/rules/test_markup.py`.
- [ ] T048 [US2] Implement `src/texlint/journals/jss/rules/markup.py` (consumes `terms.py` for `\proglang{}` / `\pkg{}` / `\code{}` classification).
- [ ] T049 [US2] Wire into `JSSJournal.categories()` + 100% branch coverage.
- [ ] T050 [US2] [Human] Precision gate for `JSS-MARKUP-NNN`.

---

## Phase 11: User Story 2 / Category `crossrefs` (rollout position #7)

- [ ] T051 [US2] Create fixtures under `tests/fixtures/violations/crossrefs/`.
- [ ] T052 [US2] Write `tests/unit/rules/test_crossrefs.py`.
- [ ] T053 [US2] Implement `src/texlint/journals/jss/rules/crossrefs.py`.
- [ ] T054 [US2] Wire into `JSSJournal.categories()` + 100% branch coverage.
- [ ] T055 [US2] [Human] Precision gate for `JSS-XREF-NNN`.

---

## Phase 12: User Story 2 / Category `code_style` (rollout position #8)

- [ ] T056 [US2] Create fixtures under `tests/fixtures/violations/code_style/`.
- [ ] T057 [US2] Write `tests/unit/rules/test_code_style.py`.
- [ ] T058 [US2] Implement `src/texlint/journals/jss/rules/code_style.py`.
- [ ] T059 [US2] Wire into `JSSJournal.categories()` + 100% branch coverage.
- [ ] T060 [US2] [Human] Precision gate for `JSS-CODE-NNN`.

---

## Phase 13: User Story 2 / Category `code_width` (rollout position #9)

**Goal**: retrofit the Step 1 smoke rule `src_001_width.py` into `rules/code_width.py` plus any additional `code_width` rules the catalogue lists.

- [ ] T061 [US2] Create fixtures under `tests/fixtures/violations/code_width/`.
- [ ] T062 [US2] Write `tests/unit/rules/test_code_width.py`.
- [ ] T063 [US2] Implement `src/texlint/journals/jss/rules/code_width.py`.
- [ ] T064 [US2] Wire `code_width` into `JSSJournal.categories()`; in the same commit, delete `src/texlint/journals/jss/rules/src_001_width.py` and `tests/unit/journals/jss/rules/test_src_001_width.py`, and remove the old `src_001` import / category line. Verify 100% branch coverage.
- [ ] T065 [US2] [Human] Precision gate for `JSS-WIDTH-NNN`.

**Checkpoint**: all three Step 1 smoke rules have now been retrofitted and deleted.

---

## Phase 14: User Story 2 / Category `naming` (rollout position #10)

- [ ] T066 [US2] Create fixtures under `tests/fixtures/violations/naming/`.
- [ ] T067 [US2] Write `tests/unit/rules/test_naming.py`.
- [ ] T068 [US2] Implement `src/texlint/journals/jss/rules/naming.py` (consumes `terms.py`).
- [ ] T069 [US2] Wire into `JSSJournal.categories()` + 100% branch coverage.
- [ ] T070 [US2] [Human] Precision gate for `JSS-NAME-NNN`.

---

## Phase 15: User Story 2 / Category `operators` (rollout position #11)

- [ ] T071 [US2] Create fixtures under `tests/fixtures/violations/operators/`.
- [ ] T072 [US2] Write `tests/unit/rules/test_operators.py`.
- [ ] T073 [US2] Implement `src/texlint/journals/jss/rules/operators.py`.
- [ ] T074 [US2] Wire into `JSSJournal.categories()` + 100% branch coverage.
- [ ] T075 [US2] [Human] Precision gate for `JSS-OPER-NNN`.

---

## Phase 16: User Story 2 / Category `abbreviations` (rollout position #12)

- [ ] T076 [US2] Create fixtures under `tests/fixtures/violations/abbreviations/`.
- [ ] T077 [US2] Write `tests/unit/rules/test_abbreviations.py`.
- [ ] T078 [US2] Implement `src/texlint/journals/jss/rules/abbreviations.py`.
- [ ] T079 [US2] Wire into `JSSJournal.categories()` + 100% branch coverage.
- [ ] T080 [US2] [Human] Precision gate for `JSS-ABBR-NNN`.

---

## Phase 17: User Story 2 / Category `house_style` (rollout position #13)

- [ ] T081 [US2] Create fixtures under `tests/fixtures/violations/house_style/`.
- [ ] T082 [US2] Write `tests/unit/rules/test_house_style.py`.
- [ ] T083 [US2] Implement `src/texlint/journals/jss/rules/house_style.py` (consumes `terms.py`).
- [ ] T084 [US2] Wire into `JSSJournal.categories()` + 100% branch coverage.
- [ ] T085 [US2] [Human] Precision gate for `JSS-HOUSE-NNN`.

---

## Phase 18: User Story 2 / Category `typography` (rollout position #14 — FP-prone, deliberate tail)

- [ ] T086 [US2] Create fixtures under `tests/fixtures/violations/typography/`.
- [ ] T087 [US2] Write `tests/unit/rules/test_typography.py`.
- [ ] T088 [US2] Implement `src/texlint/journals/jss/rules/typography.py`.
- [ ] T089 [US2] Wire into `JSSJournal.categories()` + 100% branch coverage.
- [ ] T090 [US2] [Human] Precision gate for `JSS-TYPO-NNN` — expect more corpus labelling churn than earlier categories; tune thresholds carefully.

---

## Phase 19: User Story 2 / Category `capitalization` (rollout position #15 — last, most FP-prone)

- [ ] T091 [US2] Create fixtures under `tests/fixtures/violations/capitalization/`.
- [ ] T092 [US2] Write `tests/unit/rules/test_capitalization.py`.
- [ ] T093 [US2] Implement `src/texlint/journals/jss/rules/capitalization.py` (consumes `terms.py`).
- [ ] T094 [US2] Wire into `JSSJournal.categories()` + 100% branch coverage.
- [ ] T095 [US2] [Human] Precision gate for `JSS-CAP-NNN`. Corpus should be at or near ~50 papers by this point so the N=10 floor is routinely attainable.

**Checkpoint**: every category has shipped; `JSSJournal.categories()` returns 15 `RuleCategory` entries in rollout order; every rule module hits 100% branch coverage; every rule with ≥10 labelled corpus violations clears the 90% precision gate.

---

## Phase 20: User Story 3 — Offline, reproducible rule derivation (Priority: P2)

**Goal**: confirm a contributor can derive any rule offline by following its `authority_ref` into `docs/jss-template/`, and that the annual re-fetch workflow is documented.

**Independent test**: disconnect from the network; run `pytest tests/unit/journals/jss/test_catalogue.py -x` and confirm `authority_ref` resolvability checks pass for every `jss_cls` / `article_tex` row.

- [ ] T096 [US3] Write `tests/unit/journals/jss/test_offline_resolvability.py` — a focused test that reads `docs/jss-template/jss.cls` and `article.tex` from disk only (no network), iterates every `jss_cls` / `article_tex` row in `catalogue.yaml`, and asserts the referenced line or macro resolves. This duplicates one assertion from `test_catalogue.py` but is kept separate as the named regression test for the offline contract.
- [ ] T097 [US3] Document the annual re-fetch cadence in `docs/jss-template/README.md` — add a "How to refresh" section (command to fetch the zip, how to diff, how to update `source_vendored_at` in `catalogue.yaml`, how to re-run `test_catalogue.py` to catch anchor drift). See quickstart.md §3.3 for the walkthrough.

**Checkpoint**: offline derivation is tested; annual refresh is documented.

---

## Phase 21: Polish & Cross-Cutting

**Purpose**: final cleanup after all user stories land.

- [ ] T098 [P] Run `jss-lint` against `docs/jss-template/article.tex` as a self-check; the canonical JSS demo article should produce zero violations (or only violations explicitly documented as `example_violation`s in `catalogue.yaml` that the template authors left in deliberately). Any unexplained violation on the canonical template is a bug.
- [ ] T099 [P] Run `eval-jss scan && eval-jss report` on the full corpus and verify every rule in every shipped category clears its gate: ≥90% precision for rules with ≥10 labelled violations; "not yet measured" for the rest; zero rules below 90% with ≥10 labelled violations.
- [ ] T100 [P] Update `CLAUDE.md`'s `<!-- SPECKIT START/END -->` block to advance the "current implementation plan" pointer if feature 003 is being closed and a later feature is starting. (No-op if 003 is the active feature.)
- [ ] T101 Walk `checklists/rule-catalogue-review.md` §§2–5 one final time: fill in §2 (rule inventory) with `approve` for every rule, §3 (category sanity checks), §4 (severity consistency), and close any remaining §5 items. Sign the sign-off block.
- [ ] T102 Commit the completed `checklists/rule-catalogue-review.md` and confirm `git log --follow src/texlint/journals/jss/rules/cite_001_emph.py` (and the two other retired smoke rules) still resolves to their pre-deletion history for future archaeology.

---

## Dependencies & Execution Order

### Phase dependencies

- **Phase 1 Setup** → no dependencies.
- **Phase 2 Foundational** → depends on Phase 1.
- **Phase 3 (US1)** and **Phase 4 (US4)** → both depend on Phase 2; independent of each other, may proceed in parallel if staffed (different files).
- **Phase 5 – Phase 19 (US2 per-category)** → each category phase depends on Phase 3 (catalogue) and, for categories that consume the shared term list, on Phase 4 (`terms.py`). Category phases are **sequential** among themselves — the rollout order is fixed and each category's commit lands before the next begins.
- **Phase 20 (US3)** → depends on Phase 3 (the catalogue is what's being tested offline). Independent of US2 category phases.
- **Phase 21 Polish** → depends on every US2 category phase completing.

### Within a category phase

Task order is fixed: fixtures → failing tests → implementation → wire-up + coverage → precision gate. Fixture and test tasks are prerequisites for the implementation task (spec FR-016, Constitution §VIII).

The precision gate task (`[Human]`) may loop back: if a rule fails precision, refine the rule (edit the implementation, add/retract fixtures, possibly drop the rule from `catalogue.yaml`) and re-run. This loop is internal to the phase; the category's commit lands once every gate condition is met.

### Parallel opportunities

- **Phase 1**: T003 and T004 are different files — [P].
- **Phase 3 vs Phase 4**: different files, no dependency — run in parallel if staffed.
- **Within a category phase**: no intra-phase parallelism — each task writes or tests the same file family.
- **Across category phases**: no cross-phase parallelism — the rollout is sequential by design (FR-017).

---

## Implementation Strategy

### MVP Scope

The minimum viable shipment of spec 003 is **Phase 1 + Phase 2 + Phase 3 (US1)** — the catalogue drafted, validated, rendered, and reviewed. At that commit:

- Every rule that will ship has an authority-cited row in `catalogue.yaml`.
- `catalogue.md` is readable by every reviewer.
- `rule-catalogue-review.md` has been walked through for §§1 and §5.

This is valuable in isolation: a JSS author or reviewer can read the catalogue and understand what the linter *will* check without waiting for the full implementation. The rule modules come next.

### Incremental Delivery

After the MVP catalogue lands:

1. Phase 4 (US4 `terms.py`) — small, independent, unblocks three US2 categories that consume it.
2. Phases 5–19 (US2 categories) — one per commit, in rollout order. Each category is an independently valuable delivery: `citations` landing on its own already improves the linter; an author running `jss-lint` before the `typography` phase ships sees the categories that have landed and nothing from those that haven't.
3. Phase 20 (US3 offline contract) — can land alongside or after any category; no sequence coupling.
4. Phase 21 (Polish) — closes the spec.

### Feedback loop

The per-category precision gate is the feedback loop. A rule that fails the gate does not block the next category — it blocks *its own* category's commit. If `citations` has 4 rules and one fails the gate, that one rule is refined or dropped (the other 3 can ship). This matches how Constitution §VI is phrased: per-rule, not per-release.

---

## Notes

- **[P]** means different files AND no unfinished dependencies — if two tasks touch the same file (e.g., `JSSJournal.__init__`), they are sequential regardless of phase.
- **[Human]** means the task cannot be fully automated. An LLM assistant can do the preparation work (stage fixtures, run `eval-jss scan`, pre-fill tentative labels) but the final labelling is the reviewer's judgement call.
- Commit after each task or logical group. Category phases commit in one PR per category; smoke-rule deletions land in the same PR as the replacement category.
- Every rule module edit touches a file under `src/texlint/journals/jss/rules/` and is therefore subject to Constitution §IX (100% branch coverage) and §VIII (tests before implementation).
- Avoid: vague tasks, same-file conflicts across parallel marks, rule modules that bypass `JSSJournal.categories()` wiring (spec FR-019).
