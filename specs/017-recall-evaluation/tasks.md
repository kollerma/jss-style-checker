---
description: "Tasks for recall evaluation"
---

# Tasks: Recall Measurement + README Badge

## Phase 1: Foundational

- [ ] T001 `eval/recall.py::compute_recall(linter_results,
      annotations) -> RecallReport`. Pure-Python; no I/O.
- [ ] T002 `tests/unit/eval/test_recall.py` covering TP / FN
      computation, aggregate, F1.

## Phase 2: Corpus scaffold

- [ ] T003 `eval/recall-corpus/README.md` — annotation protocol.
- [ ] T004 (deferred) Hand-annotate 10 JSS papers — substantial
      manual work; v1 ships the engine + protocol so the
      corpus can be built incrementally.

## Phase 3: Deferred

- [ ] T005 (deferred) `eval-jss recall` CLI subcommand.
- [ ] T006 (deferred) Badge endpoint + GitHub Pages workflow.

## Implementation Strategy

**MVP (this PR)**: The pure-Python recall engine + tests + the
annotation-protocol README. The corpus itself (real annotated
papers) is hand-curated work that follows; v1 delivers the
infrastructure.
