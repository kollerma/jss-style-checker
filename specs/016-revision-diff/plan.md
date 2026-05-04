# Implementation Plan: `jss-lint diff` Between Runs

**Branch**: `016-revision-diff` | **Date**: 2026-05-03 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/016-revision-diff/spec.md`

## Summary

Add `jss-lint diff OLD.json NEW.json` as the fifth subcommand
(after `explain`, `init`, `lsp`, `report`). Implementation lives
in `src/texlint/diff.py::compare(old, new, *, ignore_line_drift,
rule_renames) -> DiffReport`, plus three small renderers.

The comparison is set-based:
1. Load both JSONs, validate each against the spec-001 schema.
2. Apply the rule-rename map to OLD violations.
3. Build identity tuples for each side (with or without `line`
   based on the flag).
4. Partition into `fixed` / `introduced` / `unchanged`.
5. Render in the selected format.

The terminal format reuses the existing reviewer-mode renderer
from spec 001 (`output/terminal.py::render` with `cfg.mode =
"reviewer"`). The markdown format ships as a small new template.
The JSON format dumps a structured object with three keys.

## Technical Context

**Language/Version**: Python ≥3.10, unchanged.

**Primary Dependencies**: unchanged.

**Storage**: Reads `docs/jss-guide/rule-renames.json` (a small
hand-edited file; ~10 entries at any time). The file is shipped
in the repo; missing-file handling is graceful.

**Testing**:
- `tests/unit/test_diff.py` — comparison + line-drift +
  rule-rename + identical-input cases.
- `tests/integration/test_diff_cli.py` — end-to-end CLI.

**Target Platform**: POSIX, unchanged.

**Project Type**: Library + CLI; gains a fifth subcommand.

**Performance Goals**: O(N + M) where N / M are the violation
counts. For typical reports (~100 violations), end-to-end <100
ms.

**Constraints**:
- Constitution §I determinism: comparison and rendering are
  pure functions of `(old, new, ignore_line_drift,
  rule_renames)`.
- Constitution §III non-fatal: malformed input JSON exits 2
  with a clear error; the diff itself never raises.
- Constitution §IV zero core edits for journals: this spec
  adds one new module + one CLI subcommand. No
  `src/texlint/journals/` or `src/texlint/core/` source is
  modified.
- Constitution §V authority cited: rule-rename entries cite
  the spec PR that introduced the rename in a comment-style
  field (the JSON format permits per-entry comments).
- Constitution §VI precision gate: N/A.
- Constitution §VII safe auto-fix: N/A.
- Constitution §VIII TDD: comparison tests + line-drift
  tests + rule-rename tests land before the diff body.
- Constitution §IX 100% branch coverage on rule modules:
  unchanged.
- Constitution §X small surface: one new module, one CLI
  subcommand, one optional rename-map file.
- Constitution §XII reproducible corpus: N/A.

**Scale/Scope**: 1 new module (`src/texlint/diff.py`,
~250 LOC). 3 small renderers (terminal reuses spec-001;
markdown ~50 LOC; json ~30 LOC). 1 CLI subcommand. ~6
fixture pairs (identical, fix-only, introduce-only, mixed,
line-drift, rule-rename).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **§I Determinism** — pure comparison + rendering.
      **PASS**.
- [x] **§II AST-First** — N/A; consumes JSON. **PASS**.
- [x] **§III Non-Fatal Parse** — malformed JSON exits 2;
      no raises. **PASS**.
- [x] **§IV Zero Core Edits for Journals** — `cli.py`
      (subcommand) only, plus a new module. NO journals
      core touched. **PASS**.
- [x] **§V Authority Cited** — rename map entries are
      hand-cited. **PASS**.
- [x] **§VI ≥90% Precision Gate** — N/A. **PASS**.
- [x] **§VII Safe Auto-Fix** — N/A. **PASS**.
- [x] **§VIII TDD** — tests land first. **PASS**.
- [x] **§IX 100% Branch Coverage on Rule Modules** —
      unchanged. **PASS**.
- [x] **§X Small Surface** — one module, one subcommand.
      **PASS**.
- [x] **§XII Reproducible Corpus** — N/A. **PASS**.

All gates PASS. No amendments required.

Post-Phase-1 re-check: gates still PASS.

## Project Structure

### Documentation (this feature)

```text
specs/016-revision-diff/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── diff-output.md
└── checklists/
    └── requirements.md
```

### Source Code (repository root)

```text
src/texlint/diff.py                                # NEW — compare() + DiffReport + renderers
src/texlint/cli.py                                 # MODIFIED — register `diff` subcommand

docs/jss-guide/
└── rule-renames.json                              # NEW — initially {} (empty map)

tests/
├── unit/
│   └── test_diff.py                               # NEW — comparison + edge cases
├── integration/
│   └── test_diff_cli.py                           # NEW — CLI end-to-end
└── fixtures/
    └── diff/
        ├── old_clean.json
        ├── new_clean.json
        ├── old_mixed.json
        ├── new_mixed.json
        ├── old_drifted.json
        ├── new_drifted.json
        ├── old_renamed.json
        └── new_renamed.json
```

**Structure Decision**: One module, one CLI subcommand, one
hand-edited rename-map file. No core engine touched; the
diff is downstream of every other linter behaviour.

## Complexity Tracking

No amendments.
