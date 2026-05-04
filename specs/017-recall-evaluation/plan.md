# Implementation Plan: Recall Measurement + README Badge

**Branch**: `017-recall-evaluation` | **Date**: 2026-05-03 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/017-recall-evaluation/spec.md`

## Summary

Stand up a recall evaluation pipeline that mirrors the existing
spec-002 precision harness:

1. **Corpus**: 10 hand-annotated JSS papers under
   `eval/recall-corpus/<paper-id>/`, each with the source file
   and an `annotations.toml` listing every ground-truth
   violation.
2. **Engine**: `eval/recall.py::compute_recall(corpus, rules)`
   loads annotations, runs the linter, computes per-rule TP /
   FN / recall, and writes results to a new `recall_history`
   table in the existing `eval/precision-history.db`.
3. **CLI**: `eval-jss recall` subcommand with `--gate` and
   `--validate` flags.
4. **Report integration**: `eval/report.py` is extended with a
   `--with-recall` flag that combines precision + recall + F1
   per rule.
5. **Badges**: A `eval/badge.py` script emits two shields.io
   JSON files (`precision.json`, `recall.json`) consumed by
   the README via GitHub Pages.
6. **Annotation README**: `eval/recall-corpus/README.md`
   documents the protocol so future contributors can extend
   the corpus.

## Technical Context

**Language/Version**: Python ≥3.10, unchanged.

**Primary Dependencies**: unchanged. The annotation files use
`tomllib` (stdlib on 3.11+; `tomli` on 3.10).

**Storage**: New table `recall_history` in the existing
`eval/precision-history.db` (spec-002 schema). The new table
schema is documented in data-model.md.

**Testing**:
- `tests/unit/eval/test_recall.py` — annotation loader,
  TP/FN computation, gate logic.
- `tests/integration/test_recall_cli.py` — end-to-end
  `eval-jss recall` invocation against a fixture corpus.
- `eval/recall-corpus/<paper-id>/annotations.toml` (10 of
  them) — the corpus itself, hand-edited.

**Target Platform**: POSIX, unchanged.

**Project Type**: Library + CLI (the `eval-jss` tool is the
spec-002 evaluation CLI, not the user-facing `jss-lint`).

**Performance Goals**: `eval-jss recall` on the 10-paper corpus
runs in <30 seconds (matches the precision harness envelope).

**Constraints**:
- Constitution §I determinism: the recall harness is a pure
  function of `(corpus, catalogue, DB-snapshot)`.
- Constitution §III non-fatal parse: annotation parse failures
  are reported as validation errors (`--validate` mode); the
  gate run continues over the remaining files.
- Constitution §IV zero core edits for journals: this spec
  adds files under `eval/`, plus a CI workflow update. No
  `src/texlint/journals/` or `src/texlint/core/` source is
  modified. Documented in Complexity Tracking.
- Constitution §V authority cited: each annotation cites the
  rule id (which itself cites JSS-guide section per spec
  007). The annotation file's `comment` field MAY add
  prose anchoring.
- Constitution §VI precision gate: this spec extends the
  empirical-quality framework with recall; it does NOT
  weaken the precision gate.
- Constitution §VII safe auto-fix: N/A.
- Constitution §VIII TDD: annotation loader + computation
  tests land before the engine body.
- Constitution §IX 100% branch coverage on rule modules:
  unchanged.
- Constitution §X small surface: one new module
  (`eval/recall.py`), one CLI subcommand, one DB table,
  one badge script.
- Constitution §XII reproducible corpus: the recall corpus
  is hash-pinned the same way as the precision corpus
  (per-paper SHA256 in a manifest sibling).

**Scale/Scope**: 10 corpus papers (~10 source files +
annotation TOMLs). 1 new module (`eval/recall.py`, ~250 LOC).
1 new CLI subcommand. 1 new DB table. 1 badge script. 1
annotation README. 2 new test modules. 1 README badge update.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **§I Determinism** — recall is a pure function.
      **PASS**.
- [x] **§II AST-First** — N/A; consumes existing engine
      output. **PASS**.
- [x] **§III Non-Fatal Parse** — validation errors reported,
      not raised. **PASS**.
- [x] **§IV Zero Core Edits for Journals** — `eval/` only.
      No `src/texlint/journals/` or `core/` touched.
      **PASS with documented amendment** (the spec adds
      to `eval-jss`, which itself sits outside the journal
      core; the amendment is for completeness).
- [x] **§V Authority Cited** — annotations cite rule ids.
      **PASS**.
- [x] **§VI ≥90% Precision Gate** — unchanged. **PASS**.
- [x] **§VII Safe Auto-Fix** — N/A. **PASS**.
- [x] **§VIII TDD** — tests land first. **PASS**.
- [x] **§IX 100% Branch Coverage on Rule Modules** —
      unchanged. **PASS**.
- [x] **§X Small Surface** — one module, one subcommand,
      one DB table, one script. **PASS**.
- [x] **§XII Reproducible Corpus** — recall corpus
      manifest is SHA256-pinned per spec 002 convention.
      **PASS**.

All gates PASS.

Post-Phase-1 re-check: gates still PASS.

## Project Structure

### Documentation (this feature)

```text
specs/017-recall-evaluation/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── annotation-schema.md
│   └── recall-cli.md
└── checklists/
    └── requirements.md
```

### Source Code (repository root)

```text
eval/
├── recall.py                                      # NEW — compute_recall(), load_annotations()
├── recall-corpus/
│   ├── README.md                                  # NEW — annotation protocol
│   ├── corpus-manifest.csv                        # NEW — SHA256-pinned per-paper rows
│   ├── <paper-id-1>/
│   │   ├── manuscript.tex
│   │   └── annotations.toml
│   ├── <paper-id-2>/
│   │   ├── manuscript.tex
│   │   └── annotations.toml
│   ... (10 papers total in v1)
├── badge.py                                       # NEW — emit precision.json + recall.json
├── report.py                                      # MODIFIED — --with-recall flag, F1 column
└── cli.py                                         # MODIFIED — `eval-jss recall` subcommand

eval/precision-history.db                          # MODIFIED — new recall_history table

.github/workflows/
├── eval.yml                                       # MODIFIED — add recall step
└── publish-badges.yml                             # NEW — push badge JSONs to gh-pages

README.md                                          # MODIFIED — add precision / recall / F1 badges

tests/
├── unit/
│   └── eval/
│       └── test_recall.py                         # NEW — loader + TP/FN + gate
└── integration/
    └── test_recall_cli.py                         # NEW — end-to-end
```

**Structure Decision**: All new files live under `eval/`.
The CLI extension is in `eval/cli.py` (the `eval-jss` group).
The DB schema gains one new table; the precision pipeline is
unchanged. README badges link to GitHub-Pages-served JSON
endpoints.

## Complexity Tracking

One documented amendment.

| Amendment | Why Needed | Alternative Rejected |
|-----------|------------|---------------------|
| Edits to `eval/cli.py` (new `recall` subcommand) and `eval/precision-history.db` (new table) (§IV documented as completeness — `eval/` sits outside the journal core, so the §IV "core edits" rule does not strictly apply, but the recall pipeline is a cross-cutting evaluation surface and the amendment is documented for clarity) | The recall pipeline extends the eval harness; the new table belongs alongside the precision history, not in a separate database. | **Separate DB for recall** — would split the eval data, breaking the joint precision/recall report. **Separate CLI binary for recall** — packaging surface inflation. Rejected. |
