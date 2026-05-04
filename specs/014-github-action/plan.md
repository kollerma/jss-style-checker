# Implementation Plan: Reusable GitHub Action

**Branch**: `014-github-action` | **Date**: 2026-05-03 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/014-github-action/spec.md`

## Summary

Ship a composite GitHub Action at `action/action.yml` in this
repo (Clarifications §1) and publish it to the GitHub
Marketplace at `kollerma/jss-style-checker-action`. The Action
is a thin orchestration layer around five existing actions:
`actions/checkout`, `actions/setup-python`, a pip-install step,
the linter invocation, `github/codeql-action/upload-sarif@v3`,
and `actions/github-script@v7` for the PR-review post.

Two release workflows ship in this spec:
- `.github/workflows/release-action.yml` — on each `v*` tag,
  updates the rolling `v<MAJOR>` tag in the
  `kollerma/jss-style-checker-action` repo.
- `.github/workflows/test-action.yml` — runs the Action against
  a fixture and asserts the SARIF artefact appears.

## Technical Context

**Language/Version**: YAML for the manifest. JavaScript inside
`actions/github-script` for the review-posting logic. Python
≥3.10 for the linter (already shipped).

**Primary Dependencies**: GitHub-side actions —
`actions/checkout@v4`, `actions/setup-python@v5`,
`github/codeql-action/upload-sarif@v3`,
`actions/github-script@v7`. No new Python deps.

**Storage**: SARIF artefact attached to the workflow run; PR
review comments via the GitHub REST API.

**Testing**:
- `tests/integration/test_action_smoke.py` (Python) parses the
  output of the test-action workflow's run logs and asserts
  the violation count.
- The smoke-test workflow itself is the integration test —
  exercised on every PR via the existing CI.

**Target Platform**: `ubuntu-latest` runners. macOS / Windows
are out of scope.

**Project Type**: Multi-language repo gains a YAML-based action
manifest.

**Performance Goals**: end-to-end Action runtime <60 s for a
typical manuscript (Python install + lint + upload).

**Constraints**:
- Constitution §I determinism: Action output (SARIF, exit
  code) is deterministic given the same Python version, the
  same `jss-lint` version, and the same input set.
- Constitution §III non-fatal parse: parse failures surface
  as SARIF notifications (per spec 006); the Action does
  NOT fail the workflow on parse failure unless
  `fail-on-severity` includes `error` (the default).
- Constitution §IV zero core edits for journals: this spec
  adds top-level `action/` and `.github/workflows/` files. No
  Python source under `src/texlint/` is modified.
- Constitution §V authority cited: review comments embed the
  spec-007 `guide_url` link.
- Constitution §VI precision gate: N/A.
- Constitution §VII safe auto-fix: out of scope; the Action
  is read-only at the repo level.
- Constitution §VIII TDD: smoke-test workflow lands first.
- Constitution §IX 100% branch coverage on rule modules:
  unchanged.
- Constitution §X small surface: composite Action (no Docker
  image), one manifest file, one JS payload (~80 LOC) inside
  `github-script`.
- Constitution §XI cross-cutting work: the Action touches the
  CI / workflow surface; spec-kit invocation is appropriate.
- Constitution §XII reproducible corpus: N/A.

**Scale/Scope**: 1 manifest file (`action/action.yml`, ~80
lines). 1 JS payload (~80 LOC) embedded in
`github-script`. 1 README beside the manifest. 2 workflow
files. 1 smoke-test fixture (`docs/jss-template/` or
equivalent).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **§I Determinism** — Action is a pure orchestration
      layer over the deterministic linter. **PASS**.
- [x] **§II AST-First** — N/A; Action consumes the linter's
      already-AST-derived output. **PASS**.
- [x] **§III Non-Fatal Parse** — parse failures become
      SARIF notifications; Action exit code respects
      `fail-on-severity`. **PASS**.
- [x] **§IV Zero Core Edits for Journals** — top-level
      `action/` and `.github/workflows/` only. NO
      `src/texlint/` source modified. **PASS**.
- [x] **§V Authority Cited** — review comments embed
      `guide_url`. **PASS**.
- [x] **§VI ≥90% Precision Gate** — N/A. **PASS**.
- [x] **§VII Safe Auto-Fix** — Action is read-only at the
      repo level (no commits, no force-pushes). **PASS**.
- [x] **§VIII TDD** — smoke-test workflow lands first.
      **PASS**.
- [x] **§IX 100% Branch Coverage on Rule Modules** —
      unchanged. **PASS**.
- [x] **§X Small Surface** — composite (no Docker), one
      manifest, one short JS payload. **PASS**.
- [x] **§XII Reproducible Corpus** — N/A. **PASS**.

All gates PASS. No amendments required.

Post-Phase-1 re-check: gates still PASS.

## Project Structure

### Documentation (this feature)

```text
specs/014-github-action/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── action-manifest.md
│   └── pr-review.md
└── checklists/
    └── requirements.md
```

### Source Code (repository root)

```text
action/
├── action.yml                                     # NEW — composite Action manifest
├── README.md                                      # NEW — marketplace listing copy
└── scripts/
    └── post-review.js                             # NEW — PR-review payload (used by github-script)

.github/workflows/
├── release-action.yml                             # NEW — rolling v<MAJOR> tag updater
└── test-action.yml                                # NEW — smoke-test the Action

docs/jss-template/                                 # POSSIBLY NEW — fixture for the smoke test
└── manuscript.tex                                  # ... known violation count

tests/integration/
└── test_action_smoke.py                            # NEW — Python-side smoke assertions

README.md                                           # MODIFIED — add Action usage example
```

**Structure Decision**: Composite Action at `action/`. The
release workflow runs on `v*` tags and pushes the matching
artefact to the `kollerma/jss-style-checker-action` Marketplace
repo. The smoke-test workflow runs the Action on every PR
against `docs/jss-template/`.

## Complexity Tracking

No amendments. The Action lives entirely in new top-level
directories; no Python source is modified.
