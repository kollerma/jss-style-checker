# Implementation Plan: One-page Editor Conformance Report

**Branch**: `015-conformance-report` | **Date**: 2026-05-03 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/015-conformance-report/spec.md`

## Summary

Add `jss-lint report PATH` as the fourth subcommand (after
`explain`, `init`, `lsp`). Implementation lives in
`src/texlint/report.py::render_report(report, doc, fmt, out)`. The
function reuses the existing engine output (`ComplianceReport`)
and the spec-002 / 010 precision-history DB to produce a six-
section one-page summary in markdown, HTML, or PDF.

Three Jinja2 templates ship under `src/texlint/output/templates/`:
`conformance.md.j2`, `conformance.html.j2`,
`conformance.pdf.j2` (HTML used as input to WeasyPrint). Markdown
is the canonical surface; the other two are renderings of the
same template logic.

## Technical Context

**Language/Version**: Python ≥3.10, unchanged.

**Primary Dependencies** (runtime, core): unchanged.

**Primary Dependencies** (`[pdf]` extra): `weasyprint>=60`
(transitively pulls in `cairo`, `pango`, `GLib`).

**Storage**: Reads `eval/precision-history.db` (spec 002) when
present.

**Testing**:
- `tests/unit/test_report.py` — golden-file markdown for three
  fixtures (clean, single-error, mixed).
- `tests/unit/test_report_pdf.py` — PDF output asserts page
  count + minimal text-extraction sanity (skipped when
  `[pdf]` extra not installed).
- `tests/integration/test_report_cli.py` — end-to-end CLI
  invocation.

**Target Platform**: POSIX, unchanged.

**Project Type**: Library + CLI; gains a fourth subcommand.

**Performance Goals**: end-to-end <1 s for markdown; <3 s for
PDF (WeasyPrint dominates).

**Constraints**:
- Constitution §I determinism: report rendering is a pure
  function of `(ComplianceReport, ParsedDocument, fmt,
  precision-DB-snapshot)` modulo the run-date line.
- Constitution §III non-fatal: a missing precision DB falls
  back to lexicographic ordering with a documented footer
  note; rendering never raises on partial data.
- Constitution §IV zero core edits for journals: this spec
  adds one new module, three templates, one CLI subcommand,
  and one optional dep. Documented in Complexity Tracking.
- Constitution §V authority cited: top-5 entries link to
  the spec-007 `guide_url`.
- Constitution §VI precision gate: this spec *consumes*
  precision data to order the fix-me-first list; it does
  not change any rule's precision.
- Constitution §VII safe auto-fix: N/A.
- Constitution §VIII TDD: golden tests for markdown land
  before the renderer body.
- Constitution §IX 100% branch coverage on rule modules:
  unchanged.
- Constitution §X small surface: one renderer module,
  three templates, one optional dep, one subcommand.
- Constitution §XII reproducible corpus: N/A.

**Scale/Scope**: 1 new module (`src/texlint/report.py`,
~200 LOC). 3 Jinja2 templates. 1 PDF helper module
(`src/texlint/output/pdf.py`, ~50 LOC, gated behind
`[pdf]`). 1 CLI subcommand. ~6 fixture pairs.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **§I Determinism** — pure rendering modulo run-date.
      **PASS**.
- [x] **§II AST-First** — N/A. **PASS**.
- [x] **§III Non-Fatal Parse** — DB absence falls back
      gracefully. **PASS**.
- [x] **§IV Zero Core Edits for Journals** — `cli.py`
      (subcommand) and `pyproject.toml` (extra). NOT a
      journal addition. **PASS with documented amendment**.
- [x] **§V Authority Cited** — top-5 links to `guide_url`.
      **PASS**.
- [x] **§VI ≥90% Precision Gate** — N/A; consumes data.
      **PASS**.
- [x] **§VII Safe Auto-Fix** — N/A. **PASS**.
- [x] **§VIII TDD** — golden tests land first. **PASS**.
- [x] **§IX 100% Branch Coverage on Rule Modules** —
      unchanged. **PASS**.
- [x] **§X Small Surface** — one module, three templates,
      one extra, one subcommand. **PASS**.
- [x] **§XII Reproducible Corpus** — N/A. **PASS**.

All gates PASS. One documented amendment under §IV.

Post-Phase-1 re-check: gates still PASS.

## Project Structure

### Documentation (this feature)

```text
specs/015-conformance-report/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── report-cli.md
└── checklists/
    └── requirements.md
```

### Source Code (repository root)

```text
src/texlint/report.py                              # NEW — render_report(report, doc, fmt, out)
src/texlint/output/
├── pdf.py                                         # NEW — render_pdf(html_str) (gated behind [pdf])
└── templates/
    ├── conformance.md.j2                          # NEW
    ├── conformance.html.j2                        # NEW
    └── conformance.pdf.j2                         # NEW (PDF-styled HTML)

src/texlint/cli.py                                 # MODIFIED — register `report` subcommand

pyproject.toml                                     # MODIFIED:
                                                   #  [project.optional-dependencies]
                                                   #  pdf = ["weasyprint>=60"]

tests/
├── unit/
│   ├── test_report.py                             # NEW — markdown goldens
│   └── test_report_pdf.py                         # NEW — PDF page-count assertion
├── integration/
│   └── test_report_cli.py                         # NEW — end-to-end
└── fixtures/
    └── report/
        ├── clean.tex
        ├── clean.golden.md
        ├── single_error.tex
        ├── single_error.golden.md
        ├── mixed.tex
        └── mixed.golden.md

README.md                                          # MODIFIED — "For editors" section
```

**Structure Decision**: One renderer module, three Jinja2
templates, one PDF helper gated behind `[pdf]`, one CLI
subcommand. The CLI's `report` and the existing `--output
html` are independent surfaces — `report` is the editor-
facing summary; `--output html` remains the raw violation
list.

## Complexity Tracking

One documented amendment.

| Amendment | Why Needed | Alternative Rejected |
|-----------|------------|---------------------|
| Edits to `src/texlint/cli.py` (new subcommand) and `pyproject.toml` (new optional `[pdf]` extra) (§IV) | §IV prohibits core edits when *adding a journal*. This spec adds a CLI subcommand + optional dep that operate over the existing journal output; no journal is registered. | **Implement `report` as a separate binary** — packaging-surface inflation. **Bundle WeasyPrint as a core runtime dep** — would force every user to install cairo/pango. Rejected per Clarifications §1. |
