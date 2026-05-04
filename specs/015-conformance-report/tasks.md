---
description: "Tasks for conformance report"
---

# Tasks: Conformance Report

## Phase 1: Foundational

- [ ] T001 `src/texlint/report.py::render_report(report, *,
      fmt, title, author)` — markdown only in v1; PDF / HTML are
      deferred behind the optional `[pdf]` extra.
- [ ] T002 `tests/unit/test_report.py` — score formula, top-5
      ordering, fix-me-first ordering, fall-back when DB absent.

## Phase 2: Deferred

- [ ] T003 PDF rendering via WeasyPrint (gated behind `[pdf]`).
- [ ] T004 HTML rendering via the existing Jinja2 stack.
- [ ] T005 CLI subcommand wiring (Click sub-group migration —
      deferred to spec 009 follow-up).

## Implementation Strategy

**MVP**: Markdown rendering + tests. PDF/HTML/CLI follow.
