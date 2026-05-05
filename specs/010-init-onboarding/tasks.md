---
description: "Tasks for `jss-lint init`"
---

# Tasks: `jss-lint init`

## Phase 1: Foundational

- [x] T001 Create `src/texlint/init.py::run(path, *, force, dry_run, threshold)`.
- [x] T002 Implement deterministic TOML rendering (hand-rolled, since
      we don't want a `tomli_w` dep just for this v1 ship).

## Phase 2: User Story 1 — Generate config (P1)

- [x] T003 [US1] Aggregate violations by rule; render
      `.jss-lint.toml` with `journal = "jss"` and an
      `ignore_rules` array (empty when no precision-DB suppression
      is available).
- [x] T004 [US1] Atomic write via tempfile + os.replace.
- [x] T005 [US1] `tests/unit/test_init.py` covering write,
      `--force`, `--dry-run`, refusal, threshold.

## Phase 3: Polish

- [x] T006 v1 ships without precision-DB integration. The
      generated TOML defaults to no suppressions; precision-aware
      suppression is a follow-up.

## Implementation Strategy

**MVP**: T001–T005. Skip CLI wiring (Click subgroup migration is
deferred per spec 009 strategy). Ship the Python API; CLI
integration follows.
