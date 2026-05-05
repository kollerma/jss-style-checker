---

description: "Tasks for Auto-fix"
---

# Tasks: Auto-fix (`--fix` / `--dry-run` / `--apply`)

**Input**: Design from `/specs/008-auto-fix/`
**Tests**: Unit + integration tests are mandatory: the engine
mutates files on disk; rollback semantics demand strict coverage
(Constitution §VII).

## Phase 1: Setup

- [x] T001 Create `tests/fixtures/auto-fix/` directory.

## Phase 2: Foundational

- [x] T002 Add `Fix` dataclass to `src/texlint/api.py`: `(start: int,
      end: int, replacement: str, description: str,
      confidence: Literal["safe", "review"])`. Frozen.
- [x] T003 Update `Violation` to gain optional
      `fix: Fix | None = None`. (Replaces the spec-001 stub
      `FixSuggestion`.)
- [x] T004 Add three CLI flags to `src/texlint/cli.py`:
      `--fix`, `--dry-run`, `--apply`, plus `--fix-rule RULE-ID`
      (multiple).

## Phase 3: User Story 1 — Apply all fixes (P1)

- [x] T005 [US1] Create `src/texlint/core/fixer.py` exporting
      `apply_fixes(report, document, *, mode, rules) -> FixReport`.
- [x] T006 [US1] Implement conflict resolution per data-model §6.
- [x] T007 [US1] Implement atomic write via tempfile + os.replace.
- [x] T008 [US1] Implement post-fix re-validation (re-parse + re-lint;
      rollback when any same-`(rule_id, line)` re-appears).
- [x] T009 [US1] Wire CLI dispatch when `--fix` is set.
- [x] T010 [US1] Migrate `JSS-CITE-002` (or another simple
      mechanical rule) to emit a `Fix` payload as the demo migration.
- [x] T011 [US1] `tests/unit/core/test_fixer.py` covering: apply
      one fix, apply multiple in reverse-position order, conflict
      resolution, rollback on regression.
- [x] T012 [US1] `tests/integration/test_fix_cli.py` covering
      `--fix` end-to-end against a `before`/`after` golden pair.

## Phase 4: User Story 2 — Dry-run (P1)

- [x] T013 [US2] Implement `mode = "dry-run"` in
      `src/texlint/core/fixer.py`: print unified diff via
      `difflib.unified_diff`; do NOT touch the filesystem.
- [x] T014 [US2] Wire CLI flag combination validation:
      `--dry-run` requires `--fix`, `--apply` requires `--fix`,
      `--dry-run` and `--apply` are mutually exclusive.
- [x] T015 [US2] `tests/integration/test_fix_cli.py::test_dry_run`
      asserts no on-disk mutation.

## Phase 5: User Story 3 — Interactive `--apply` (P2)

- [x] T016 [US3] Implement `mode = "interactive"` with
      `[y/n/a/q]` prompts (single-key; EOF treated as `q`).
- [x] T017 [US3] `tests/integration/test_fix_cli.py::test_apply_y`
      asserts a yes-to-all session applies every fix.

## Phase 6: User Story 4 — `--fix-rule` (P2)

- [x] T018 [US4] Honour `--fix-rule RULE-ID` filter in
      `apply_fixes`.
- [x] T019 [US4] Reject unknown rule ids with exit 2.

## Phase 7: User Story 5 — Atomic write + rollback (P1)

(Implementation lives in T007–T008; this phase contains just
the regression-rollback CLI integration test.)

- [x] T020 [US5] `tests/integration/test_fix_cli.py::test_rollback_on_regression`
      using a fixture rule whose Fix re-trips the rule.

## Phase 8: SARIF integration (FR-009)

- [x] T021 Update `src/texlint/output/sarif.py` to emit
      `runs[].results[].fixes[]` for fixable violations
      (data-model §7).

## Phase 9: Polish

- [x] T022 [P] `pytest -q` — confirm zero regressions.
- [x] T023 [P] Document the migration recipe for additional rules
      in spec 008's `quickstart.md` (already drafted).

## Implementation Strategy

**MVP**: T001–T012 (US1 + foundation). Auto-fix works end-to-end
for one rule. Subsequent increments add the dry-run / interactive
surfaces and SARIF integration.
