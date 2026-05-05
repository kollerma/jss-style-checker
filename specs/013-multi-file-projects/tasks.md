---
description: "Tasks for multi-file projects"
---

# Tasks: Multi-file `\input` / `\include` Resolver

## Phase 1: Foundational

- [x] T001 `src/texlint/core/resolver.py::resolve(root)` walks
      `\input` / `\include` / `\subfile` / `\bibliography` macros
      and returns a list of resolved paths.

## Phase 2: User Story 1 — Lint a multi-file project (P1)

- [x] T002 [US1] Tests for the resolver: file relative to root,
      cycle detection, missing reference.

## Phase 3: Deferred

- [x] T003 Engine dispatch + cross-file rule API
      (`Rule.check_project`) is deferred to a follow-up; the
      resolver is the seam.

## Implementation Strategy

**MVP**: Ship the resolver + tests. CLI auto-resolve and engine
dispatch follow once the API is firm.
