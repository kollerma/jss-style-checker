---
description: "Task breakdown for spec 005: Rnw / Rmd manuscript support"
---

# Tasks: Rnw / Rmd Manuscript Support

**Input**: Design documents from `/specs/005-rnw-rmd-support/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓ (4 files), quickstart.md ✓

**Tests**: The Rnw stripper, the Rmd parser, and the engine dispatch each have explicit test contracts in `contracts/*.md`. Per Constitution §VIII, unit tests are MANDATORY for any file under `src/texlint/journals/*/rules/` (the preamble `formats` edit in US3 is covered by the existing 100% branch-coverage gate). Elsewhere, tests are requested by the plan input and land per the standard fixtures → failing test → implementation ordering.

**Organization**: Tasks are grouped by user story. Phase 2 (foundational) contains the API and engine changes that every user story depends on; Phases 3–6 deliver one user story each.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no conflicting dependencies).
- **[Story]**: Maps the task to one or more user stories (US1/US2/US3/US4). Setup, Foundational, and Polish tasks omit the story tag.
- File paths are absolute within the repo; use as-is.

## Path Conventions

- **Repository root**: `/workspace`
- **Parser modules**: `src/texlint/core/`
- **API surface**: `src/texlint/api.py`
- **Engine**: `src/texlint/core/engine.py`
- **Rule modules (edited)**: `src/texlint/journals/jss/rules/preamble.py`
- **Tests**: `tests/unit/`, `tests/integration/`
- **Fixtures**: `tests/fixtures/compliant/`, `tests/fixtures/violations/rnw/`, `tests/fixtures/violations/rmd/`
- **Corpus**: `eval/corpus-manifest.csv`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Runtime dependency update and baseline capture.

- [ ] T001 Add `pyyaml>=6.0` to the runtime dependency list in `pyproject.toml` (move from `[project.optional-dependencies].dev` to `[project].dependencies` if it is currently dev-only). Run `pip install -e '.[dev]'` to sync the devcontainer.
- [ ] T002 Capture a baseline snapshot of `eval-jss report` on the current 6-paper corpus to `/tmp/report-before-005.txt` so US4's regression diff has a reference point. `scripts/eval-category.sh` requires no changes at this stage.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: API extensions (new dataclasses, `Rule.formats` semantics change, `skipped_rules` field) and engine dispatch that every user story depends on. **No user-story work can begin until T003–T014 are green.**

**⚠️ CRITICAL**: These tasks modify `src/texlint/api.py` and `src/texlint/core/`. Keep patches tight — Constitution §IV amendment tracking requires each core edit to stay narrow.

- [ ] T003 Add `ParsedRmdFile`, `RmdHeading`, `RmdProse`, `RmdCode` frozen dataclasses to `src/texlint/api.py` per `data-model.md §2`. Fields exactly as documented; all frozen; type-annotated.
- [ ] T004 [P] Add `SkippedRule` frozen dataclass to `src/texlint/api.py` and extend `ComplianceReport` with `skipped_rules: tuple[SkippedRule, ...] = ()` per `data-model.md §4`.
- [ ] T005 Extend `ParsedDocument` in `src/texlint/api.py`: add `rmd_files: tuple[ParsedRmdFile, ...] = ()`, extend `all_files()` to yield from `rmd_files`, and add new `all_tex_like()` helper per `data-model.md §3`. Also update `files_for_rule()` to filter by input-format instead of file-suffix per `research.md §4` and `contracts/rule-format-filter.md`. Depends on T003.
- [ ] T006 Update the `Rule.formats` docstring in `src/texlint/api.py` to reflect the input-format filter semantics (valid values: `None`, `frozenset({"tex", "rnw", "rmd"})` subset). No signature change. Add the `R-1` invariant note as a doctring comment.
- [ ] T007 [P] Extend `tests/unit/test_api.py` with:
  - Round-trip test for each new dataclass (`ParsedRmdFile`, `RmdHeading`, `RmdProse`, `RmdCode`, `SkippedRule`).
  - `all_tex_like()` invariants P-1 / P-2 from `data-model.md`.
  - `Rule.formats` well-formed invariant R-1.
  - `ComplianceReport.skipped_rules` default-empty + immutable.
- [ ] T008 Implement `parse_document(paths)` in `src/texlint/core/engine.py` per `contracts/engine-dispatch.md`: extension-dispatch map, case-insensitive suffix matching, `UnsupportedSuffixError` → CLI exit 2. Each parser sets a private `_input_format` attribute on the returned object.
- [ ] T009 Extend `engine.run(doc, journal_id, cfg)` in `src/texlint/core/engine.py` to:
  - Derive `input_formats = {f._input_format for f in doc.all_files()}`.
  - For each rule, apply the filter: `if rule.formats is not None and not (rule.formats & input_formats): append a SkippedRule and continue`.
  - Populate `ComplianceReport.skipped_rules` on return.
  - Ensure `CategorySummary.rules_applied` excludes skipped rules (invariant F-2).
- [ ] T010 [P] Extend `tests/unit/test_engine.py` to cover:
  - `parse_document` dispatch per `contracts/engine-dispatch.md` test-matrix.
  - `UnsupportedSuffixError` → exit 2.
  - Invariants F-1 (no rule both violated and skipped), F-2 (rules_applied excludes skipped), F-4 (non-verbose output byte-identical to pre-feature on `.tex + .bib` input).
- [ ] T011 [P] Update the terminal renderer (`src/texlint/output/terminal.py`): render a "Skipped rules" table after violations when `cfg.verbose` is true AND `skipped_rules` is non-empty. Default (non-verbose) output unchanged. Per `contracts/rule-format-filter.md`.
- [ ] T012 [P] Update the JSON renderer (`src/texlint/output/json_output.py`): always include a top-level `skipped_rules` key (possibly empty list) in the output. Additive, back-compat.
- [ ] T013 [P] Update the HTML renderer (`src/texlint/output/html_output.py`): render a "Skipped rules" section only when non-empty.
- [ ] T014 [P] Extend the renderer tests (`tests/integration/test_cli_author_terminal.py`, `test_cli_json.py`, `test_cli_html.py`) with a skipped-rules scenario: feed an `.Rmd` fixture, assert the preamble rules appear in `skipped_rules` (JSON) / in the verbose table (terminal) / in the HTML section.

**Checkpoint**: Foundation ready. API extensions, engine dispatch, renderer wiring all green. Per-category user stories can begin.

---

## Phase 3: User Story 1 — Lint a Sweave (`.Rnw`) manuscript (Priority: P1) 🎯 First deliverable [US1]

**Goal**: `jss-lint paper.Rnw` returns the same style-rule feedback as the equivalent `.tex` file, with chunk content ignored and line numbers source-authoritative.

**Independent Test**: A fixture `.Rnw` with a prose violation at a known line and a chunk containing text that would match the rule produces exactly one violation on the prose line. `scripts/vtest.sh tests/unit/test_rnw_stripper.py` passes.

### Fixtures + failing tests first (TDD)

- [ ] T015 [P] [US1] Create fixture `tests/fixtures/compliant/minimal.Rnw` — a Sweave document with valid preamble, one R chunk, and clean prose. Fixture must cover ≥2 chunk types (plain `<<>>=`, options `<<label, fig.width=5>>=`) and ≥1 `\Sexpr{…}` call.
- [ ] T016 [P] [US1] Create fixture `tests/fixtures/violations/rnw/JSS-MARKUP-002-bad.Rnw` — prose paragraph says "the MASS package" unwrapped; embedded R chunk contains `library(MASS)` at a different line. This is the canonical leak-test fixture.
- [ ] T017 [P] [US1] Write failing `tests/unit/test_rnw_stripper.py` per `contracts/rnw-stripper.md §Test matrix`: 11 test cases covering the `S-1..S-6` invariants plus the empty-string / no-chunk / multi-chunk / unclosed / bare-`@` / inline-`\Sexpr{…}` edges.

### Implementation

- [ ] T018 [US1] Implement `strip_rnw_chunks(src)` and `_RNW_CHUNK` / `_RNW_SEXPR` regexes in `src/texlint/core/parser.py` per `contracts/rnw-stripper.md`. Pure function; no I/O.
- [ ] T019 [US1] Implement `parse_rnw_file(path)` in `src/texlint/core/parser.py`: read file, call `strip_rnw_chunks`, pass to existing `parse_tex_file` via a source-override parameter (extend `parse_tex_file` if needed to accept pre-read source text). Returned `ParsedTexFile._input_format = "rnw"`.
- [ ] T020 [US1] Wire `.rnw` into the dispatch map from T008. Verify `scripts/vtest.sh tests/unit/test_rnw_stripper.py tests/unit/test_engine.py` is green.

### Integration + invariants

- [ ] T021 [US1] Add integration tests `tests/integration/test_rnw_end_to_end.py`: run `jss-lint` on each fixture from T015 / T016 and assert the acceptance scenarios from spec §US1 (rule fires on prose line; does not fire on chunk lines; preamble rules fire on `.Rnw` with missing `\Address{}`).
- [ ] T022 [US1] Verify the line-count invariant `S-1` holds on the real `docs/jss-template/article.Rnw` (if present) via a one-off smoke test. Skippable if the file is absent.

**Checkpoint**: US1 shipped. `jss-lint paper.Rnw` lints Sweave manuscripts end-to-end.

---

## Phase 4: User Story 2 — Lint an R Markdown (`.Rmd`) manuscript (Priority: P1) [US2]

**Goal**: `jss-lint paper.Rmd` parses frontmatter + body, lints prose and raw-LaTeX islands, ignores fenced code blocks, warns on missing `.bib`, and keeps line numbers source-authoritative.

**Independent Test**: An `.Rmd` fixture with a prose paragraph mentioning `MASS` and a fenced code block ALSO containing `MASS` produces exactly one violation on the prose line. Malformed YAML / unterminated fence surface as `JSS-PARSE-000` with the correct line number.

### Fixtures + failing tests first (TDD)

- [ ] T023 [P] [US2] Create fixture `tests/fixtures/compliant/minimal.Rmd` — valid YAML frontmatter, one heading, one prose paragraph with inline `$math$` and `` `r runif(1)` ``, one fenced `` ```{r} `` code block, no violations.
- [ ] T024 [P] [US2] Create fixture `tests/fixtures/violations/rmd/JSS-MARKUP-002-bad.Rmd` — prose says "the MASS package"; code block contains `library(MASS)`; assert MARKUP-002 fires on prose line only.
- [ ] T025 [P] [US2] Create auxiliary fixtures for parser edge cases: `tests/fixtures/violations/rmd/` plus three malformed files — `malformed-yaml.Rmd` (tab indent / bad structure), `unterminated-fence.Rmd` (open ``` with no close), `unterminated-frontmatter.Rmd` (leading `---` with no close).
- [ ] T026 [US2] Write failing `tests/unit/test_rmd_parser.py` per `contracts/rmd-parser.md §Test matrix`: 14 cases covering M-1..M-7 invariants (token ordering, line-coverage, malformed YAML / fence / frontmatter, inline R code stripping, fence language tag, prose-with-math).

### Implementation

- [ ] T027 [US2] Create `src/texlint/core/rmd_parser.py` implementing the state machine from `contracts/rmd-parser.md`:
  - `parse_rmd_source(path, src) -> ParsedRmdFile` pure function.
  - `parse_rmd_file(path) -> ParsedRmdFile` thin wrapper.
  - `_INLINE_R` regex for inline-code stripping on prose.
  - `yaml.safe_load` for frontmatter; emit `JSS-PARSE-000` on failure.
  - For each prose block, call `parse_tex_source(prose.text, path=f"{rmd.path}:block@{prose.line}")` and attach to `latex_fragments`. Set `_input_format = "rmd"` on the returned `ParsedRmdFile`.
- [ ] T028 [US2] Extend `src/texlint/core/parser.py` with a `parse_tex_source(src, path)` helper if it does not yet accept a pre-read source string. The helper is used by T027 for raw-LaTeX island parsing.
- [ ] T029 [US2] Wire `.rmd` into the dispatch map from T008; engine populates `ParsedDocument.rmd_files`. Verify `scripts/vtest.sh tests/unit/test_rmd_parser.py tests/unit/test_engine.py` is green.

### Engine integration for Rmd traversal

- [ ] T030 [US2] Audit every rule module under `src/texlint/journals/jss/rules/` for usages of `doc.tex_files` that should ALSO iterate raw-LaTeX islands on `.Rmd` input. Replace `doc.tex_files` with `doc.all_tex_like()` in rules whose check callable walks tex content and is appropriate for Rmd prose (markup, naming, crossrefs, code_style, citations, structure). Preamble rules stay on `doc.tex_files` because they are format-restricted to tex+rnw in US3.
- [ ] T031 [US2] Add integration tests `tests/integration/test_rmd_end_to_end.py`: run `jss-lint` on each fixture from T023–T025, assert the acceptance scenarios from spec §US2 (rule fires on prose only; YAML frontmatter produces zero violations; missing `.bib` → warning).

### Missing `.bib` warning (FR-012)

- [ ] T032 [US2] In `engine.run` (or cli.main), detect the case where `doc.rmd_files` is non-empty, citation-dependent rules exist, and `doc.bib_files` is empty. Emit a `JSS-PARSE-000`-style informational violation with `severity=Severity.INFO` and message "No sibling .bib file; bibliography-inspection rules skipped." Cite FR-012.

**Checkpoint**: US2 shipped. `jss-lint paper.Rmd` lints R Markdown manuscripts end-to-end including raw-LaTeX island support.

---

## Phase 5: User Story 3 — Format-filtering for rules (Priority: P2) [US3]

**Goal**: Preamble rules narrow their `formats` to `{"tex", "rnw"}`; `--verbose` output lists the skipped rules; non-verbose output is byte-identical to pre-feature on `.tex`+`.bib` input (FR-015 regression).

**Independent Test**: `jss-lint --verbose paper.Rmd` lists JSS-PRE-001..008 in a "Skipped rules" section; the same command without `--verbose` produces no skipped-rules output. `scripts/vtest.sh tests/` green with 100% branch coverage on `preamble.py`.

### Preamble `formats` narrowing

- [ ] T033 [US3] Extend the `_rule(rule_id, check_fn, formats=None)` helper in `src/texlint/journals/jss/rules/preamble.py` to accept an optional `formats` kwarg and pass it through to the `Rule(...)` constructor.
- [ ] T034 [US3] Update each of the 8 preamble `Rule` constructions in `src/texlint/journals/jss/rules/preamble.py` to pass `formats=frozenset({"tex", "rnw"})`. Add a one-line comment above each documenting the reason (per Constitution §X: "Rmd has no LaTeX preamble"). Per FR-020.
- [ ] T035 [US3] Re-run `scripts/vtest.sh tests/unit/rules/test_preamble.py --cov=texlint.journals.jss.rules.preamble --cov-branch --cov-fail-under=100` — confirm the one-line edits do not introduce coverage gaps.

### Skipped-rule behaviour tests

- [ ] T036 [US3] Add `tests/integration/test_skipped_rules.py`:
  - Run `jss-lint` on `minimal.Rmd` → all 8 preamble rule ids present in `ComplianceReport.skipped_rules`.
  - Run `jss-lint` on `minimal.tex` → `skipped_rules` empty.
  - Run `jss-lint` with `--verbose` on `minimal.Rmd` → terminal output includes "Skipped rules" section with 8 rows.
  - Run `jss-lint` without `--verbose` → terminal output does NOT include "Skipped rules" section (FR-009, F-4).

### FR-015 regression

- [ ] T037 [US3] Capture a `scripts/vtest.sh tests/` snapshot (test count + xfail / xpass counts) and confirm it matches the baseline from T002 before merging. Also run `eval-jss scan --force && eval-jss report` on the existing 6-paper `.tex`+`.bib` corpus; assert byte-identical per-rule violation counts vs the baseline from T002.

**Checkpoint**: US3 shipped. Format filter wiring and preamble narrowing are live; FR-015 regression verified.

---

## Phase 6: User Story 4 — Eval-harness regression + corpus expansion (Priority: P3) [US4]

**Goal**: CRAN corpus expansion lands with SHA256-pinned rows; `eval-jss report --by-format` slices per-rule precision by input format; the existing `.tex` precision baseline is isolated from new-format numbers.

**Independent Test**: `eval-jss corpus fetch` resolves every new row; `eval-jss report --by-format` emits per-format precision rows; the combined-rule precision figure (no flag) is byte-identical to T002's baseline for `.tex`-only rules.

### Corpus expansion

- [ ] T038 [US4] Curate a short-list of CRAN packages with JSS-style vignettes: target 3–5 `.Rnw` (e.g. `lme4`, `zoo`, `quantreg`, `survival`, `mgcv`) and 2–3 `.Rmd` (e.g. `ggplot2`, `brms`). Verify each tarball is reachable and contains the expected `.Rnw` / `.Rmd` file at `<pkg>/vignettes/*.{Rnw,Rmd}` or `<pkg>/inst/doc/*.{Rnw,Rmd}`. Document package/version choices in `specs/005-rnw-rmd-support/end-of-spec-summary.md` (stub for Polish phase).
- [ ] T039 [US4] Append rows to `eval/corpus-manifest.csv` for each curated package — one row per vignette file, `source=cran`, `vignette_file=<path-inside-tarball>`, `local_path=<slug>/`, `sha256=` left blank initially.
- [ ] T040 [US4] Run `scripts/vpy.sh -m eval.cli corpus fetch` (or `eval-jss corpus fetch`) to materialise each row; the tool pins `sha256` into `eval/corpus-manifest.csv`. Commit the populated hashes.
- [ ] T041 [US4] Run `eval-jss scan --force` over the expanded corpus. Confirm each new `.Rnw` / `.Rmd` paper scans without a `JSS-PARSE-000` violation; if any do, triage (malformed fixture? parser edge case?) and address.

### Per-format precision slicing

- [ ] T042 [US4] Implement `--by-format` on `eval-jss report` in `eval/report.py`: partition the violation set by `papers.path.suffix.lower()` and emit one row per rule per format (`tex` / `rnw` / `rmd`), with combined precision unchanged as the authoritative single-rule figure.
- [ ] T043 [US4] Extend `tests/eval/test_report.py` with:
  - A by-format partition test using synthetic rows for `.tex`, `.Rnw`, `.Rmd` papers.
  - A regression test asserting default (no-flag) output is byte-identical to pre-feature snapshot on the stock corpus.

### Regression diff

- [ ] T044 [US4] Compare `eval-jss report` output on the 6-paper `.tex` corpus after T042 vs the snapshot from T002. Must match byte-for-byte for every `.tex`-only rule. FR-015 / SC-003.

**Checkpoint**: US4 shipped. Corpus expanded; per-format precision slicing live; `.tex` baseline isolated.

---

## Phase 7: Polish & End-of-Spec Validation

**Purpose**: Cross-cutting validation and sign-off per spec §End-of-spec checkpoint and Constitution §XII.

- [ ] T045 Run `scripts/vtest.sh tests/` — full suite green, 0 xfailed, 0 xpassed. Target: 721 + roughly 70 new tests from this spec = ~790 passing.
- [ ] T046 [P] Run repo-wide branch-coverage gate: `scripts/vtest.sh tests/ --cov=texlint.journals.jss.rules --cov=texlint.core --cov-branch --cov-fail-under=100` (rules) and case-by-case for `core/parser.py` + `core/rmd_parser.py` + `core/engine.py`. Rule modules hold 100% per Constitution §IX; parser modules hold whatever ordinary engineering judgement yields (the contracts' invariants should make high coverage natural).
- [ ] T047 [P] Run the golden-path demo: `jss-lint docs/jss-template/article.tex docs/jss-template/refs.bib` — per-rule violation counts MUST match the spec-004 baseline (9 warnings from FP-free template findings). Then run `jss-lint docs/jss-template/article.Rnw` if a `.Rnw` sibling exists. Open follow-up issues for any unexpected new violation.
- [ ] T048 [P] Run the synthetic full-catalogue-coverage test: `scripts/vtest.sh tests/integration/test_full_catalogue_coverage.py` — every catalogue rule id fires on its bad fixture. SC-001 regression.
- [ ] T049 Produce `specs/005-rnw-rmd-support/end-of-spec-summary.md` — per-rule status after the spec (any newly-measurable rules on `.Rnw` / `.Rmd` via the expanded corpus), the CRAN packages selected with versions + SHA256 snippets, FR-015 regression evidence, and SC-006 by-format report slice snapshot.
- [ ] T050 [P] Update `CLAUDE.md` agent-context pointer to reference the end-of-spec summary. (The plan reference was already updated in `/speckit.plan`; this step is a sanity check.)
- [ ] T051 Close the checklists: `specs/005-rnw-rmd-support/checklists/requirements.md` passes all items.

**Checkpoint**: Spec 005 closes when T045–T051 are all done and the end-of-spec summary cites an FR-015 green regression diff and at least one newly-measurable rule on `.Rnw` / `.Rmd` (corpus permitting).

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: T001–T002 are one-time prep. T002 (baseline snapshot) blocks T037 and T044 regression diffs.
- **Foundational (Phase 2)**: T003–T014 block every user story.
  - T003 blocks T005, T007; T004 blocks T007.
  - T008 blocks T009; T009 blocks T011–T014.
  - T005 (ParsedDocument extensions) blocks T008 (parse_document) because the dispatch map populates `rmd_files`.
  - Parallelizable within Phase 2: {T004, T006, T007 after T003 and T005}; {T011, T012, T013, T014 after T009}.
- **Phase 3 US1 (Rnw)**: depends on T003–T010 completion. T017 (failing test) BEFORE T018 (implementation). T020 (wire dispatch) depends on T008. T021 (integration) depends on T020.
- **Phase 4 US2 (Rmd)**: depends on T003–T010 completion. T026 (failing test) BEFORE T027 (implementation). T030 (rule-module `doc.all_tex_like()` migration) can happen in parallel with T027 if both developers are aware.
- **Phase 5 US3 (Format filter)**: depends on T009 (skipped_rules populated in engine.run) + T011–T014 (renderer support). T033 (extend `_rule()`) BEFORE T034 (update preamble Rule constructions).
- **Phase 6 US4 (Corpus + by-format)**: depends on T008 (dispatch supports `.Rnw` / `.Rmd` — without it `eval-jss scan` can't process new corpus rows). T038 (curate) BEFORE T039 (manifest rows) BEFORE T040 (fetch + SHA256) BEFORE T041 (scan). T042 (by-format) is independent of corpus work.
- **Phase 7 Polish**: depends on every user story being complete.

### User Story Dependencies

- **US1 (Rnw, P1)** and **US2 (Rmd, P1)** are independent — Rnw uses only the stripper + existing `parse_tex_file`; Rmd introduces `ParsedRmdFile` and the tokenizer. They can be staffed in parallel after Phase 2.
- **US3 (Format filter, P2)** depends structurally on Phase 2 (engine/renderer skipped-rule wiring) but not on US1 / US2 code. It can ship before or after them; the preamble rules don't care which `.Rnw` / `.Rmd` support lands first.
- **US4 (Eval regression + corpus, P3)** depends on US1 and US2 because it runs `eval-jss scan` on `.Rnw` / `.Rmd` rows, which requires the parsers. The `--by-format` flag (T042) is independent and can ship earlier.

### Within Each User Story Phase

1. Fixtures (parallel across rules, within a phase)
2. Failing test module (depends on fixtures)
3. Implementation (depends on test)
4. Dispatch / wiring (depends on implementation)
5. Integration tests (depend on wiring)
6. Optional: coverage verification

### Parallel Opportunities

- Within Phase 2: {T004, T006} parallel after T003; {T007, T011, T012, T013, T014} parallel after T009.
- Between Phase 3 (Rnw) and Phase 4 (Rmd): both can proceed after Phase 2. Two-developer team.
- Within Phase 3: {T015, T016, T017} parallel.
- Within Phase 4: {T023, T024, T025} parallel.
- Within Phase 6: {T042, T043} parallel with the corpus-fetch chain.
- Polish phase: T046, T047, T048, T050 parallel (different scopes).

---

## Parallel Example: Phase 2 (Foundational)

```bash
# After T003 (dataclasses) lands:
Task: "[P] Add SkippedRule + ComplianceReport.skipped_rules"          # T004
Task: "[P] Update Rule.formats docstring semantics"                    # T006
Task: "[P] Extend test_api.py with new-dataclass round-trips"         # T007

# After T009 (engine.run skipped_rules) lands:
Task: "[P] Terminal renderer skipped-rules section"                   # T011
Task: "[P] JSON renderer skipped_rules field"                         # T012
Task: "[P] HTML renderer skipped-rules section"                       # T013
Task: "[P] Renderer integration tests"                                # T014
```

## Parallel Example: Phase 3 + Phase 4 in parallel

```bash
# After Phase 2 completes, two developers can work in parallel:
# Developer A: Phase 3 (Rnw)  — T015-T022
# Developer B: Phase 4 (Rmd)  — T023-T032
# Phase 5 (US3) joins after either ships because preamble narrowing
# is additive on both.
```

---

## Implementation Strategy

### MVP (Phases 1 + 2 + 3)

1. Phase 1: Setup (T001–T002).
2. Phase 2: Foundational (T003–T014).
3. Phase 3: US1 Rnw (T015–T022).
4. **STOP and VALIDATE**: `jss-lint paper.Rnw` works end-to-end; Rmd support and format-filter bookkeeping remain TODO. Ship as MVP.

### Incremental Delivery

Each subsequent phase is an independent PR:

- Phase 4 (Rmd) adds `.Rmd` support on top of the MVP.
- Phase 5 (format filter) narrows preamble rules once the engine/renderer wiring is in place.
- Phase 6 (corpus + by-format) extends the eval harness.
- Phase 7 closes the spec.

### Parallel Team Strategy

With ≥2 developers after Phase 2:

- Developer A: Phase 3 (Rnw) then Phase 5 (format filter — preamble edits are tiny).
- Developer B: Phase 4 (Rmd) — larger phase; tokenizer + raw-LaTeX islands.
- Shared follow-up: Phase 6 (corpus curation is serial; `--by-format` flag is independent).

### Closing Discipline

- Every new parser helper carries docstring references to its contract (`contracts/*.md`).
- Every failing test is committed (or staged) before the implementation it covers per §VIII.
- Every preamble-rule `formats` narrowing carries a one-line inline comment per §X (small surface: explain non-obvious narrowing; skip the comment if `formats=None`).
- No silent FR-015 drift: T037 and T044 both compare against T002's snapshot.
- When Phase 7 closes, `specs/005-rnw-rmd-support/end-of-spec-summary.md` is the authoritative status doc.

---

## Notes

- [P] = different files, no shared dependency at the moment the task runs.
- [Story] labels: US1 (Rnw), US2 (Rmd), US3 (format filter), US4 (eval regression).
- Per-phase PR is the default commit unit; small-group bundling is fine where contracts overlap (e.g., T011–T013 renderers could ship as one PR).
- Verify fixtures and failing tests before writing parser bodies (§VIII TDD — applies narrowly to rule modules per Constitution, but the plan input explicitly requests it for the parser work too).
- Branch-coverage gate on rule modules stays 100% (Constitution §IX, spec 004 baseline).
- Skip-list entries on the new skipped-rule payload are not involved here — the `eval/review-skip-list.toml` is about AI review, not about format-filter skipping.
- Avoid: broken FR-015 regression (T037 / T044 guards), new runtime dep beyond `pyyaml` (Constitution §X + spec Assumption), rule-module audit that accidentally narrows a rule's `formats` below `{tex, rnw}` (only preamble should narrow in this spec).
