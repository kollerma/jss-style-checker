---

description: "Tasks for SARIF 2.1.0 Output"
---

# Tasks: SARIF 2.1.0 Output

**Input**: Design documents from `/specs/006-sarif-output/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/sarif-output.md

**Tests**: Unit + golden-file tests are MANDATORY because the SARIF
contract is byte-deterministic (Constitution §I, §VIII).
`output/sarif.py` is not a rule module so §IX 100% branch coverage
does not apply, but ≥95% line coverage tracks the existing
`output/json_output.py` baseline.

## Phase 1: Setup

- [ ] T001 Add SARIF 2.1.0 schema fixture: download once, save to
      `tests/fixtures/sarif-2.1.0-schema.json` (vendored — research §2).

## Phase 2: Foundational (blocking)

- [ ] T002 Add `source_root: Path` field to `ToolConfig` in
      `src/texlint/api.py` with `default_factory=Path.cwd`. Ensure
      every existing constructor still works.
- [ ] T003 Add `--source-root DIR` Click option to `src/texlint/cli.py`
      that threads into `cli_overrides["source_root"]`. Silently
      accepted for non-SARIF outputs.
- [ ] T004 Extend `--output` Click `Choice` in `src/texlint/cli.py`
      to include `"sarif"`.

## Phase 3: User Story 1 — Upload to GitHub code scanning (P1)

**Goal**: `jss-lint --output sarif <paths>` emits valid SARIF 2.1.0
that GitHub code scanning consumes.

**Independent test**: Run linter on a fixture with one warning;
output validates against the vendored schema and contains exactly
one `result` with the right `ruleId` / `level` / `region`.

- [ ] T005 [US1] Create `src/texlint/output/sarif.py` exposing
      `render(report, cfg)` (matches `json_output.py` signature). Stub.
- [ ] T006 [US1] Implement the path-relativisation helper in
      `src/texlint/output/sarif.py::_relativise(file, source_root)`
      per data-model §3d.
- [ ] T007 [US1] Implement the severity map
      `_SARIF_LEVEL = {Severity.ERROR: "error", Severity.WARNING:
      "warning", Severity.INFO: "note"}` in
      `src/texlint/output/sarif.py`.
- [ ] T008 [US1] Implement `_rule_descriptor(rule)` projecting a
      catalogue rule to `tool.driver.rules[]` entry per data-model
      §3a, with `properties.tags = [rule.category]`.
- [ ] T009 [US1] Implement `_result(violation, source_root)` projecting
      a non-`JSS-PARSE-000` violation to a SARIF result per
      data-model §3b. Include `endLine` / `endColumn` only when set.
- [ ] T010 [US1] Wire `_dispatch_renderer` in `src/texlint/cli.py` to
      route `output == "sarif"` to the new module.
- [ ] T011 [US1] Create test
      `tests/unit/output/test_sarif.py::test_clean_run` with a
      golden fixture asserting byte-equality + schema validation.
- [ ] T012 [US1] Add
      `tests/unit/output/test_sarif.py::test_single_warning` covering
      a single warning fixture; assert `result[0].ruleId`,
      `level == "warning"`, region values.
- [ ] T013 [US1] Add `tests/unit/output/test_sarif.py::test_multi_file`
      with two-file fixture; assert per-result `artifactLocation.uri`
      values and ordering.
- [ ] T014 [US1] Generate goldens: `tests/fixtures/sarif/golden_clean.sarif`,
      `golden_single_error.sarif`, `golden_multi_file.sarif`.

## Phase 4: User Story 2 — Surface parse failures (P1)

**Goal**: `JSS-PARSE-000` emits as `toolExecutionNotifications`,
not as `results`.

**Independent test**: Linter on a malformed `.tex` produces a SARIF
with `results == []`, one `toolExecutionNotifications` entry with
`descriptor.id == "JSS-PARSE-000"`, and the right artifact URI.

- [ ] T015 [US2] Implement `_notification(violation, source_root)` in
      `src/texlint/output/sarif.py` per data-model §3e.
- [ ] T016 [US2] Update the top-level renderer to partition violations
      by `rule_id == "JSS-PARSE-000"`: parse failures → notifications,
      others → results. `executionSuccessful: true` always (parse
      failures don't flip it — only an internal exception does).
- [ ] T017 [US2] Ensure `--ignore-rules JSS-PARSE-000` does NOT
      suppress notifications (it filters `results` upstream of the
      renderer; notifications bypass that filter).
- [ ] T018 [US2] Add `tests/unit/output/test_sarif.py::test_parse_failure`
      with a fixture that triggers `JSS-PARSE-000`; assert
      `notifications[0]` shape; assert `results == []`.
- [ ] T019 [US2] Add
      `tests/unit/output/test_sarif.py::test_ignore_parse_does_not_silence`.
- [ ] T020 [US2] Generate golden `tests/fixtures/sarif/golden_parse_error.sarif`.

## Phase 5: User Story 3 — Reproducible SARIF (P2)

**Goal**: Two invocations against the same input produce
byte-identical SARIF.

**Independent test**: Run renderer twice on the same fixture; assert
sha256 of outputs match.

- [ ] T021 [US3] Sort `tool.driver.rules[]` ascending by `id` before
      serialisation.
- [ ] T022 [US3] Sort `runs[0].results[]` ascending by
      `(file, line, column, ruleId)` before serialisation.
- [ ] T023 [US3] Sort `toolExecutionNotifications[]` ascending by
      `(uri, line)` before serialisation.
- [ ] T024 [US3] Confirm `json.dumps(..., sort_keys=True, indent=2,
      ensure_ascii=False)` is the only path; no Python `dict`
      iteration order leaks.
- [ ] T025 [US3] Add
      `tests/unit/output/test_sarif.py::test_byte_deterministic`
      that invokes `render` twice on identical inputs and asserts
      byte equality.

## Phase 6: User Story 4 — Source-root relativisation (P2)

**Goal**: `--source-root` controls the base directory for
`artifactLocation.uri`; default is CWD.

**Independent test**: Run linter from one directory with
`--source-root` pointing elsewhere; assert URIs are relative to
that root.

- [ ] T026 [US4] Add
      `tests/unit/output/test_sarif.py::test_source_root_default_cwd`.
- [ ] T027 [US4] Add
      `tests/unit/output/test_sarif.py::test_source_root_explicit`.
- [ ] T028 [US4] Add
      `tests/unit/output/test_sarif.py::test_source_root_outside_emits_dotdot`.

## Phase 7: Cross-cutting + polish

- [ ] T029 [P] Update
      `specs/001-linter-foundation/contracts/cli.md` to note SARIF
      as a fourth peer format alongside terminal/json/html. (If the
      file is `cli.md`-named differently in spec 001, follow the
      spec's existing naming.)
- [ ] T030 [P] Add a JSON-output regression test asserting
      pre-spec-006 byte shape unchanged (FR-012 / SC-004).
- [ ] T031 [P] Run the full test suite (`pytest -q`) and confirm
      all 1127 pre-spec-006 tests still pass alongside the new
      SARIF tests.
- [ ] T032 [P] Confirm no new runtime dependencies in
      `pyproject.toml`. `jsonschema` is dev-only.

## Dependencies

```
T001 (schema fixture) → all schema-validation tests
T002, T003, T004 (config + CLI) → T010 (dispatch) → US1 tests
US1 → US2 (notifications path is built on the result-rendering scaffold)
US1 → US3 (determinism tests need a working renderer)
US1 → US4 (path-relativisation tests need the helper from T006)
T029, T030 in polish, runnable in parallel
```

## Implementation Strategy

**MVP**: User Story 1 (clean run + single error + multi-file). With
T001–T014 done, the SARIF surface exists and uploads to GitHub code
scanning. US2/US3/US4 sharpen correctness + reproducibility.

**Increment 1**: US1 (T001–T014). Cuts the headline functionality.
**Increment 2**: US2 + US4 (T015–T020, T026–T028). Parse-failure
visibility + source-root behaviour.
**Increment 3**: US3 + polish (T021–T025, T029–T032).
