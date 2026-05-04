---
description: "Tasks for `jss-lint diff`"
---

# Tasks: `jss-lint diff`

## Phase 1: Foundational

- [ ] T001 `src/texlint/diff.py::compare(old, new, *,
      ignore_line_drift, rule_renames) -> DiffReport`. Pure
      function over the spec-001 JSON shape.
- [ ] T002 `tests/unit/test_diff.py` covering identical inputs,
      fix-only, introduce-only, line-drift, rule-rename.
- [ ] T003 `docs/jss-guide/rule-renames.json` — initially empty
      map; loaded by `compare`.

## Implementation Strategy

**MVP**: Pure-Python comparison API + tests. Markdown / JSON
renderers + CLI wiring follow.
