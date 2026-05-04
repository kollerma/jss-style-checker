# Implementation Plan: Auto-fix (`--fix` / `--dry-run` / `--apply`)

**Branch**: `008-auto-fix` | **Date**: 2026-05-03 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/008-auto-fix/spec.md`

## Summary

Auto-fix is a self-contained feature with three flag entry points
(`--fix`, `--dry-run`, `--apply`) and one rule-side opt-in (a
`Fix` payload on a violation). The implementation has four
moving parts:

1. **`Fix` dataclass** in `src/texlint/api.py` — byte-range
   replacement + description + confidence literal.
2. **`Violation.fix: Fix | None`** field — additive on the
   existing dataclass.
3. **`core/fixer.py`** — single new module, exports
   `apply_fixes(report, document, mode, rules) -> FixReport`.
   Modes: `"write"`, `"dry-run"`, `"interactive"`. Atomic write
   via `tempfile.NamedTemporaryFile(dir=parent)` + `os.replace`.
4. **`cli.py`** wires the three flags + `--fix-rule
   RULE-ID` (repeatable) and dispatches to `apply_fixes`.

Re-validation: after each per-file rewrite, the engine re-parses
the new bytes and re-lints them. If any `(rule_id, line)` from
the supposed-to-be-fixed set re-appears, the engine writes the
cached pre-fix bytes back via the same tempfile mechanism and
exits 2 with a stderr report — Constitution §VII.

Three catalogue rules ship with `Fix` payloads in this spec to
exercise the engine end-to-end: `JSS-CITE-003`, `JSS-NAME-001`,
`JSS-CAP-002` (or current equivalents — research §6 confirms
which three remain the most deterministic in the catalogue).
Each ships a `before.tex` / `after.tex` golden pair.

SARIF integration (`runs[0].results[].fixes[]`) activates the
deferral noted in spec 006 FR-015.

## Technical Context

**Language/Version**: Python ≥3.10, unchanged.

**Primary Dependencies**: unchanged. The interactive prompt
uses `click.prompt` (already a dep) for `[y/n/a/q]`.
`difflib.unified_diff` is stdlib.

**Storage**: None. Files are rewritten on disk via tempfile +
`os.replace`.

**Testing**: `pytest` + `pytest-cov`. New modules:
- `tests/unit/core/test_fixer.py` — engine unit tests +
  conflict resolution + rollback.
- `tests/integration/test_fix_cli.py` — end-to-end CLI tests
  for `--fix`, `--dry-run`, `--apply`, `--fix-rule`.
- Golden pairs under `tests/fixtures/auto-fix/` —
  `before.tex` / `after.tex` for each rule that ships fixes.

**Target Platform**: POSIX primary; `os.replace` covers
Windows for files on the same volume.

**Project Type**: Library + CLI, unchanged.

**Performance Goals**: per-file rewrite is O(N) in source
length plus one re-parse. For a typical JSS manuscript
(~10k lines) this is well under 1 second of overhead atop
the existing lint pass.

**Constraints**:
- Constitution §I determinism: conflict resolution is a
  fully ordered tiebreaker (research §1). The same input
  always produces the same set of applied fixes.
- Constitution §II AST-first: rules compute byte offsets
  from pylatexenc node positions in their own code; the
  engine treats the result as opaque text edits.
- Constitution §III non-fatal parse: the post-fix re-parse
  failure (a fix that produces unparseable LaTeX) is
  treated as a regression — the engine rolls back and
  exits 2.
- Constitution §IV zero core edits for journals: this spec
  edits `src/texlint/api.py` (`Fix` dataclass, `Violation.fix`
  field) and `src/texlint/cli.py` (three new flags). NOT a
  journal addition. Cross-cutting CLI + public-API surface.
  Documented in Complexity Tracking.
- Constitution §V authority cited: rules that ship `Fix`
  payloads continue to cite the same JSS authority that
  motivates the rule itself.
- Constitution §VI precision gate: existing rule precision
  is unaffected. Rules that ship `Fix` payloads are subject
  to a stricter implicit gate — if applying the fix
  introduces a new violation of the same rule, FR-008
  rolls back.
- Constitution §VII safe auto-fix: this spec *implements* §VII.
  Tempfile + `os.replace`, post-fix re-validation, rollback
  on regression. Unsafe fixes leave `fix=None`.
- Constitution §VIII TDD: golden pairs and rejection tests
  land before the engine body and before any rule's `Fix`
  payload.
- Constitution §IX 100% branch coverage on rule modules:
  unchanged. The three rules adding `Fix` payloads keep
  100% coverage; new branches in those rules are
  test-covered by the golden pair.
- Constitution §X small surface: one new dataclass, one
  new field, one new engine module, one CLI section.
- Constitution §XII reproducible corpus: N/A.

**Scale/Scope**: 1 new dataclass (`Fix`). 1 additive field
(`Violation.fix`). 1 new module (`core/fixer.py`, ~250 LOC).
3 CLI flags + 1 repeatable option. 3 rules upgraded with
`Fix` payloads (~30 LOC each). 6 new fixtures (3 rules ×
{before, after}). 2 new test modules. 1 SARIF projection
extension (`fixes[]`).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **§I Determinism** — conflict resolution is fully
      ordered. Same input → same applied fix set. **PASS**.
- [x] **§II AST-First** — rule-side responsibility; engine
      is text-only by design. **PASS**.
- [x] **§III Non-Fatal Parse** — post-fix parse failure is
      treated as a regression and rolled back. The engine
      itself never raises on malformed input. **PASS**.
- [x] **§IV Zero Core Edits for Journals** — `src/texlint/
      api.py` (Fix dataclass + Violation.fix field) and
      `src/texlint/cli.py` (three flags). Cross-cutting; NOT
      a journal addition. Documented in Complexity Tracking.
      **PASS with documented amendment**.
- [x] **§V Authority Cited** — rule-side responsibility;
      this spec adds an enforcement mode for already-cited
      rules. **PASS**.
- [x] **§VI ≥90% Precision Gate** — unchanged. The three
      rules that gain `Fix` are already over the gate.
      **PASS**.
- [x] **§VII Safe Auto-Fix** — this spec *implements* §VII.
      Tempfile + atomic replace, post-fix re-lint,
      regression rollback. **PASS by implementation**.
- [x] **§VIII TDD** — golden pairs and rejection-test
      fixtures land before the engine body. **PASS by task
      ordering**.
- [x] **§IX 100% Branch Coverage on Rule Modules** —
      preserved for the three upgraded rules; new
      branches in `Fix`-emitting code are exercised by
      the golden pair. **PASS**.
- [x] **§X Small Surface** — one dataclass, one field,
      one engine module, three CLI flags. The `apply_fixes`
      function has three concrete callers (the three CLI
      modes). **PASS**.
- [x] **§XII Reproducible Corpus** — N/A. **PASS**.

All gates PASS. One documented amendment under §IV.

Post-Phase-1 re-check: gates still PASS.

## Project Structure

### Documentation (this feature)

```text
specs/008-auto-fix/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── fix-engine.md            # apply_fixes() contract
│   └── cli-flags.md             # --fix / --dry-run / --apply / --fix-rule contract
└── checklists/
    └── requirements.md
```

### Source Code (repository root)

```text
src/texlint/api.py                                 # MODIFIED:
                                                   #  - Fix dataclass (new)
                                                   #  - Violation.fix: Fix | None (new field)

src/texlint/core/
└── fixer.py                                       # NEW — apply_fixes(), conflict resolution,
                                                   #       atomic write + rollback

src/texlint/cli.py                                 # MODIFIED:
                                                   #  - --fix flag
                                                   #  - --dry-run flag (requires --fix)
                                                   #  - --apply flag (requires --fix)
                                                   #  - --fix-rule RULE-ID (repeatable)
                                                   #  - dispatch into apply_fixes() and exit codes

src/texlint/output/sarif.py                        # MODIFIED — emit runs[0].results[].fixes[] when
                                                   #            violation.fix is not None

# Three rule modules upgraded with Fix payloads
src/texlint/journals/jss/rules/
├── citations.py                                   # MODIFIED — JSS-CITE-003 fix
├── naming.py                                      # MODIFIED — JSS-NAME-001 fix
└── capitalisation.py                              # MODIFIED — JSS-CAP-002 fix

tests/
├── unit/
│   └── core/
│       └── test_fixer.py                          # NEW — apply_fixes() unit tests
├── integration/
│   └── test_fix_cli.py                            # NEW — end-to-end CLI tests
├── unit/output/
│   └── test_sarif.py                              # MODIFIED — fixes[] golden + scenario
└── fixtures/
    └── auto-fix/
        ├── jss-cite-003-before.tex
        ├── jss-cite-003-after.tex
        ├── jss-name-001-before.tex
        ├── jss-name-001-after.tex
        ├── jss-cap-002-before.tex
        └── jss-cap-002-after.tex
```

**Structure Decision**: Auto-fix is a self-contained engine
under `core/fixer.py`, plus a small public-API extension
(`Fix` + `Violation.fix`). Three rule modules opt in by
adding a `Fix(...)` payload to their existing violations;
the rule-author surface is one constructor call. The CLI
dispatches into the engine in three modes; existing read-
only behaviour is preserved when no fix flag is set.

## Complexity Tracking

One documented amendment.

| Amendment | Why Needed | Alternative Rejected |
|-----------|------------|---------------------|
| Edits to `src/texlint/api.py` (Fix dataclass + Violation.fix field) and `src/texlint/cli.py` (three new flags) (§IV) | §IV prohibits core edits when *adding a journal*. This spec adds a public-API extension and CLI surface that every journal benefits from — the auto-fix engine is journal-agnostic, journals merely emit `Fix` payloads on the violations they already produce. | **Implement auto-fix as a separate package** — would require a `Fix` extension protocol on `Violation`, a strictly larger change than the additive field. **Move the engine into `journals/jss/`** — would couple atomic write + rollback semantics to the JSS journal, blocking other journals from using auto-fix. Rejected. |
