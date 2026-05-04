# Implementation Plan: Multi-file `\input` / `\include` Resolver

**Branch**: `013-multi-file-projects` | **Date**: 2026-05-03 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/013-multi-file-projects/spec.md`

## Summary

Add a project model. When `jss-lint` is invoked on a single root
file, the resolver walks `\input`, `\include`, `\subfile`, and
`\bibliography` macros via the existing pylatexenc AST and produces
a `ParsedProject` aggregating every reachable file. Cycle detection
emits `JSS-PROJECT-001`; missing references emit
`JSS-PROJECT-002`.

Rule API extension: rules opt into cross-file scope by exposing a
`check_project(project: ParsedProject) -> Iterable[Violation]`
method (Clarifications §5). Single-file rules keep the existing
`check(doc: ParsedDocument)` signature unchanged. The engine
dispatches both signatures on every run.

The abbreviations rule (the canonical cross-file rule) migrates to
the project-mode signature in this spec; other rules migrate
incrementally in future work.

## Technical Context

**Language/Version**: Python ≥3.10, unchanged.

**Primary Dependencies**: unchanged. The resolver uses pylatexenc
(already a runtime dep) for macro walking.

**Storage**: None.

**Testing**:
- `tests/unit/core/test_resolver.py` — single-file project,
  cycle detection, missing reference, `\bibliography`
  resolution, `TEXINPUTS` honoured, `--no-resolve` bypass.
- `tests/integration/test_multi_file_project.py` — fixture
  with 3 files, end-to-end CLI invocation, golden-file report.
- `tests/unit/test_engine.py` — extension to dispatch
  `check_project` alongside `check`.
- `tests/unit/journals/jss/rules/test_abbreviations.py` —
  cross-file abbreviation cases.

**Target Platform**: POSIX, unchanged.

**Project Type**: Library + CLI, unchanged.

**Performance Goals**: For an N-file project, the resolver is
O(N) parses, each O(file-length). For a 5-file fixture (SC-006),
end-to-end <2 seconds.

**Constraints**:
- Constitution §I determinism: the resolver is a pure function of
  `(root, filesystem state, env vars)`. The two env-var entries
  (`TEXINPUTS`, `BIBINPUTS`) are an explicit, documented input;
  the resolver records them in the project graph for
  reproducibility.
- Constitution §II AST-first: pylatexenc AST traversal locates
  the macros; no regex over source.
- Constitution §III non-fatal parse: a missing reference is a
  violation (`JSS-PROJECT-002`), not a raise. A cycle is a
  violation (`JSS-PROJECT-001`), not a raise.
- Constitution §IV zero core edits for journals: this spec edits
  `src/texlint/api.py` (`ParsedProject` dataclass + `Rule`
  optional `check_project` signature) and `src/texlint/core/
  engine.py` (dispatch). Cross-cutting; NOT a journal addition.
  Documented in Complexity Tracking.
- Constitution §V authority cited: the two new tool-side rules
  use the spec-007 sentinel (`guide_section = "internal"`,
  `guide_url = None`).
- Constitution §VI precision gate: the abbreviations rule's
  precision is RE-MEASURED post-migration, since the cross-file
  scope changes its denominator.
- Constitution §VII safe auto-fix: N/A; no auto-fix in this
  spec.
- Constitution §VIII TDD: resolver tests + cycle tests +
  missing-ref tests land before the resolver body.
- Constitution §IX 100% branch coverage on rule modules:
  preserved for the abbreviations rule; the migrated
  `check_project` is fully test-covered.
- Constitution §X small surface: one new module
  (`core/resolver.py`), one new dataclass (`ParsedProject`),
  one optional rule field (`check_project`). The engine
  dispatch grows by one branch.
- Constitution §XII reproducible corpus: corpus fixtures gain
  one multi-file entry; SHA256-pinned per spec 002.

**Scale/Scope**: 1 new module (`core/resolver.py`, ~250 LOC).
1 new dataclass (`ParsedProject`). 2 new tool-side rules
(`JSS-PROJECT-001`, `JSS-PROJECT-002`). 1 cross-file rule
migration (abbreviations). 1 engine dispatch extension. 4 new
test modules / extensions. ~6 fixtures.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **§I Determinism** — env var inputs documented;
      resolver pure. **PASS**.
- [x] **§II AST-First** — pylatexenc traversal. **PASS**.
- [x] **§III Non-Fatal Parse** — cycle / missing-ref are
      violations, never raises. **PASS**.
- [x] **§IV Zero Core Edits for Journals** — `api.py` (new
      dataclass + optional rule field) and `engine.py`
      (dispatch). NOT a journal addition. **PASS with
      documented amendment**.
- [x] **§V Authority Cited** — tool-side rules use sentinel.
      **PASS**.
- [x] **§VI ≥90% Precision Gate** — abbreviations rule
      re-measured post-migration. **PASS by re-measure**.
- [x] **§VII Safe Auto-Fix** — N/A. **PASS**.
- [x] **§VIII TDD** — resolver tests land first. **PASS**.
- [x] **§IX 100% Branch Coverage on Rule Modules** —
      preserved. **PASS**.
- [x] **§X Small Surface** — one resolver module, one
      dataclass, one optional rule field. **PASS**.
- [x] **§XII Reproducible Corpus** — multi-file fixture is
      hash-pinned per spec 002. **PASS**.

All gates PASS. One documented amendment under §IV.

Post-Phase-1 re-check: gates still PASS.

## Project Structure

### Documentation (this feature)

```text
specs/013-multi-file-projects/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── resolver.md
│   └── project-rule-api.md
└── checklists/
    └── requirements.md
```

### Source Code (repository root)

```text
src/texlint/api.py                                 # MODIFIED:
                                                   #  - ParsedProject dataclass (new)
                                                   #  - Rule.check_project: Callable | None (new)

src/texlint/core/
├── resolver.py                                    # NEW — resolve(root) -> ParsedProject
└── engine.py                                      # MODIFIED — dispatch check + check_project

src/texlint/journals/jss/rules/
├── abbreviations.py                               # MODIFIED — migrate to check_project
└── project.py                                     # NEW — JSS-PROJECT-001, JSS-PROJECT-002

src/texlint/cli.py                                 # MODIFIED:
                                                   #  - --no-resolve flag
                                                   #  - single-arg → resolve; multi-arg → explicit list

tests/
├── unit/
│   ├── core/
│   │   └── test_resolver.py                       # NEW
│   ├── test_engine.py                             # MODIFIED — dispatch tests
│   └── journals/jss/rules/
│       └── test_abbreviations.py                  # MODIFIED — cross-file cases
├── integration/
│   └── test_multi_file_project.py                 # NEW
└── fixtures/
    └── multi_file/
        ├── paper.tex
        ├── intro.tex
        ├── methods.tex
        ├── refs.bib
        ├── cycle_a.tex
        └── cycle_b.tex
```

**Structure Decision**: One new resolver module, one
`ParsedProject` dataclass, one optional rule field, two new
tool-side rules under a new `journals/jss/rules/project.py`.
The engine dispatch grows by one branch. Existing single-file
rules require ZERO changes; cross-file scope is opt-in.

## Complexity Tracking

One documented amendment.

| Amendment | Why Needed | Alternative Rejected |
|-----------|------------|---------------------|
| Edits to `src/texlint/api.py` (`ParsedProject` + optional `Rule.check_project`) and `src/texlint/core/engine.py` (dispatch) (§IV) | §IV prohibits core edits when *adding a journal*. This spec extends the input model and the rule API across journals; every journal that adopts the engine inherits the project-level capability. NOT a journal addition. | **Push the resolver into `journals/jss/`** — would couple the input model to JSS, blocking other journals from using projects. Rejected. **Implement projects via CLI loop alone** (no `ParsedProject` type) — would deny rules the cross-file scope they need. Rejected. |
