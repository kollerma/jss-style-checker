---
description: "Tasks for `jss-lint explain` subcommand"
---

# Tasks: `jss-lint explain` Subcommand

## Phase 1: Foundational

- [x] T001 Migrate `jss-lint` to a `click.Group` with the existing
      lint as the default action (`invoke_without_command=True`).
- [x] T002 Add a small `Explainer` module reading rule metadata
      from the catalogue.

## Phase 2: User Story 1 — Single-rule explain (P1)

- [x] T003 [US1] Implement `src/texlint/explain.py::render(rule_id,
      *, fmt) -> str` (terminal + markdown).
- [x] T004 [US1] Wire `jss-lint explain RULE-ID` subcommand.
- [x] T005 [US1] Tests: terminal + markdown formats; unknown rule
      exits 2; listing view (no rule).

## Phase 3: Catalogue extension (deferred)

- [x] T006 Catalogue fields `explanation`, `example_bad`,
      `example_good` are reserved as optional; full backfill is a
      follow-up. v1 ships rendering against the existing
      `message_template` + authority surface.

## Implementation Strategy

**MVP**: T001–T005. The Click-group migration must preserve
existing CLI behaviour byte-for-byte. The explain output draws
from `message_template` for v1; the prose-explanation backfill
ships in a later spec.
