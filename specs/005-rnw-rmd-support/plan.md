# Implementation Plan: Rnw / Rmd Manuscript Support

**Branch**: `005-rnw-rmd-support` | **Date**: 2026-04-24 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/005-rnw-rmd-support/spec.md`

## Summary

Extend `jss-lint` to accept Sweave/Knitr (`.Rnw`) and R Markdown (`.Rmd`)
manuscripts alongside the existing `.tex` + `.bib` inputs. The approach
is **two thin adapters over the existing LaTeX pipeline**:

1. **`.Rnw` stripper** (`core/parser.py::strip_rnw_chunks`) — a
   line-preserving regex substitution that replaces R code chunks
   (`<<...>>=` … `@`) and inline `\Sexpr{...}` with equivalent-length
   whitespace, then feeds the result to the existing `parse_tex_file`.
   Existing LaTeX rules see native-looking TeX; line numbers remain
   source-authoritative.
2. **`.Rmd` tokenizer** (`core/rmd_parser.py`) — a small hand-rolled
   state-machine tokenizer (no Markdown-parser dependency) that yields
   `(kind, start_line, content)` tokens for frontmatter, headings,
   prose blocks, and fenced code blocks. Prose blocks are
   tex-parsed as raw-LaTeX islands so existing rules fire on inline
   `$math$` / `\macro{...}` fragments; code blocks are ignored by
   rules.

The existing catalogue keeps `formats=None` (apply to all inputs)
except the 8 preamble rules (`JSS-PRE-001..008`) which narrow to
`{"tex", "rnw"}`. A new `ComplianceReport.skipped_rules` field surfaces
format-mismatched skips in `--verbose` mode.

Corpus expansion ships alongside: 3–5 `.Rnw` vignettes + 2–3 `.Rmd`
vignettes fetched from CRAN via the existing `eval-jss corpus fetch`.
`eval-jss report` gains per-format precision slicing so the `.tex`
baseline stays isolated from new-format numbers.

**Spec drift reconciliation — one item:**

- **Markdown parser**: spec's Clarifications Q1 recorded
  `markdown-it-py` as the parser choice. The plan input supersedes
  this: we hand-roll a small tokenizer instead. Rationale: the Rmd
  surface we care about is shallow (frontmatter → heading / prose /
  fenced-code), `markdown-it-py` would ship a CommonMark AST we
  immediately flatten, and Constitution §X (Small Surface) prefers the
  50-line hand-rolled state machine over a 200 KB dep. The spec
  Clarifications section is updated to reflect the planning decision;
  research.md documents the alternatives-considered trail.

## Technical Context

**Language/Version**: Python ≥3.10, unchanged from specs 001–004.

**Primary Dependencies** (runtime):
- `pylatexenc>=2.10` (unchanged) — LaTeX parser used by the Rnw
  stripper output and the Rmd prose-block islands.
- `bibtexparser>=2.0.0b6` (unchanged).
- `click>=8.1`, `rich>=13.0`, `jinja2>=3.1` (unchanged).
- **NEW**: `pyyaml>=6.0` — promoted from dev-extra to a runtime dep for
  `.Rmd` frontmatter parsing. Graceful failure: if `yaml.safe_load`
  raises, we emit `JSS-PARSE-000` and leave frontmatter empty.

**No other new runtime deps.** The `.Rmd` body tokenizer is hand-rolled
per the plan input (avoid `markdown-it-py` / `mistune` per §X).

**Storage**: No new storage. The eval harness's SQLite DB gains no new
columns; per-format precision slicing derives the format tag from
`papers.path` suffix at report time.

**Testing**: `pytest` + `pytest-cov` (unchanged dev extras).
Constitution §IX continues to apply: 100% branch coverage for every
file under `src/texlint/journals/*/rules/`. New non-rules code
(`core/rmd_parser.py`, `core/parser.py::strip_rnw_chunks`) is covered
under ordinary engineering judgment per §IX.

**Target Platform**: POSIX primary (Linux / macOS), matching prior
specs. Windows unsupported.

**Project Type**: Python library + CLI (`jss-lint` entry point). Spec
005 extends `src/texlint/core/` (parser dispatch) and `src/texlint/api.py`
(new `ParsedRmdFile` dataclass, `Rule.formats` semantics extension,
`ComplianceReport.skipped_rules`). These are constitution §IV
concerns; see Constitution Check below.

**Performance Goals**: the `.Rnw` stripper is O(N) in source length
(single-pass regex). The `.Rmd` tokenizer is O(N) in line count. Rmd
prose blocks that contain raw LaTeX are parsed with pylatexenc, which
is already the cost envelope for `.tex` input. Target: a typical
`.Rmd` vignette (≤5 000 lines) lints in under 2 seconds end-to-end,
same envelope as `.tex` (spec 001 had <1s for a typical paper).

**Constraints**:
- Constitution §I determinism: the Rnw stripper and Rmd tokenizer are
  pure functions of the source string.
- Constitution §II AST-first: rules continue to walk the pylatexenc
  AST for tex-like input. Raw-source scans remain restricted to
  `JSS-WIDTH-001`; the Rnw stripper output is tex and therefore
  subject to the same AST-first mandate.
- Constitution §III non-fatal parse: malformed Rnw / Rmd produces
  `JSS-PARSE-000` on the returned `ParsedDocument`; never raises.
- Constitution §IV zero core edits for journals: this spec edits
  `src/texlint/core/` and `src/texlint/api.py`, but **not to add a
  journal** — the edits are cross-cutting parser-layer extensions
  that all journals benefit from. Documented in Complexity Tracking.
- Constitution §VI precision gate: the corpus-expansion deliverable
  (FR-019) makes per-rule precision measurable on `.Rnw` / `.Rmd`
  input for the first time. `eval-jss report` gains a per-format
  slicing mode so the `.tex` baseline stays uncontaminated.
- Constitution §IX 100% branch coverage on rule modules: unchanged;
  the 58 spec-004 rules continue to hold 100% coverage.
- Constitution §X small surface: hand-roll the Rmd tokenizer rather
  than add a Markdown-parser dep; preamble rules narrow their
  `formats`, everything else keeps `None`.
- Constitution §XII reproducible corpus: CRAN rows in the manifest
  are SHA256-pinned at fetch time, same as spec 002's jss_archive
  convention.

**Scale/Scope**: 2 new parser modules (`core/rmd_parser.py`,
`core/parser.py` extension), 1 new dataclass (`ParsedRmdFile`), 3 API
extensions (`Rule.formats` semantics, `ParsedDocument.rmd_files`,
`ComplianceReport.skipped_rules`), 1 engine dispatch change
(`parse_document`), 8 rule modules touched (preamble `formats`
narrowing — a single-line edit per module), ~6 new fixtures, ~8 new
CRAN corpus rows.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **§I Determinism** — The Rnw stripper is a regex substitution; the
      Rmd tokenizer is a single-pass state machine. Both are pure
      functions of the source string. No ML, no randomness, no time or
      filesystem reads. **PASS**.
- [x] **§II AST-First** — Rules continue to walk the pylatexenc AST for
      all tex-like input, including stripped Rnw and Rmd prose-block
      islands. Raw-source regex usage stays confined to
      `JSS-WIDTH-001`. The Rnw stripper itself is a source-text
      pre-pass (byte-level by necessity: Sweave chunk delimiters are
      not expressible in the pylatexenc AST) — documented as a
      parser-layer carve-out, not a rule-layer violation. **PASS**.
- [x] **§III Non-Fatal Parse** — Malformed Rnw (unclosed chunk
      delimiter), malformed YAML frontmatter, and malformed Rmd
      (unterminated fence) all surface as `JSS-PARSE-000` violations
      on the returned `ParsedDocument`. No code path raises. **PASS**.
- [x] **§IV Zero Core Edits for Journals** — this spec edits
      `src/texlint/core/parser.py` and `src/texlint/api.py`. **This is
      NOT a journal addition** — the edits extend the input-format
      surface shared across every journal. A journal-specific change
      would violate §IV; a parser-layer change benefiting all journals
      is correct. Documented in Complexity Tracking below. **PASS with
      documented amendment**.
- [x] **§V Authority Cited** — no new rules in this spec; the existing
      58 rules keep their authority citations. The `formats` narrowing
      on preamble rules is a scope change, not a metadata change —
      authority stays. **PASS**.
- [x] **§VI ≥90% Precision Gate** — FR-019 adds CRAN corpus rows;
      FR-016 / SC-006 adds per-format precision slicing in `eval-jss
      report`. Existing `.tex` precision stays unchanged (FR-015 /
      SC-003). **PASS by contract**.
- [x] **§VII Safe Auto-Fix** — no new `FixSuggestion` payloads in this
      spec. Every violation keeps `fix=None`. **PASS** (non-applicable
      subset).
- [x] **§VIII TDD** — tests for the Rnw stripper, Rmd tokenizer, and
      engine dispatch land before the implementation files per spec
      FR-006 / FR-014 / the plan input's test list. Tasks.md will
      order fixtures → failing tests → implementation. **PASS by task
      ordering**.
- [x] **§IX 100% Branch Coverage on Rule Modules** — no new rule
      modules. The 58 spec-004 rules continue to hold 100% coverage.
      The preamble `formats` narrowing edit is a one-line change per
      module; coverage is re-verified in CI. **PASS**.
- [x] **§X Small Surface** — the Rmd tokenizer is hand-rolled (no
      markdown-it-py / mistune dep); preamble rules narrow their
      `formats`, everything else keeps `None`; `ComplianceReport`
      grows one field (`skipped_rules`); `ParsedDocument` grows one
      field (`rmd_files`); `ParsedTexFile` is reused unchanged for Rmd
      raw-LaTeX islands. No speculative helpers. `doc.all_tex_like()`
      has ≥3 callers (every rule that iterates `doc.tex_files` today).
      **PASS**.
- [x] **§XII Reproducible Corpus** — FR-019's CRAN rows use the same
      `eval-jss corpus fetch` mechanism that spec 002 defined, with
      SHA256 pinning. Corpus manifest commit hash is cited in the
      end-of-spec summary. **PASS**.

All gates PASS. One documented amendment under §IV (parser-layer edit,
not a journal addition). See Complexity Tracking.

Post-Phase-1 re-check: all gates still PASS after the design pass. No
new gate concerns emerged from data-model / contracts work.

## Project Structure

### Documentation (this feature)

```text
specs/005-rnw-rmd-support/
├── plan.md                                  # This file
├── research.md                              # Phase 0: parser choices, drift reconciliation
├── data-model.md                            # Phase 1: ParsedRmdFile, Rule.formats, skipped_rules
├── quickstart.md                            # Phase 1: contributor onboarding for a new Rmd rule
├── contracts/
│   ├── rnw-stripper.md                      # Contract: chunk-stripping regex + invariants
│   ├── rmd-parser.md                        # Contract: token stream + line-number invariants
│   ├── rule-format-filter.md                # Contract: formats semantics + skipped_rules
│   └── engine-dispatch.md                   # Contract: parse_document extension map
└── checklists/
    └── requirements.md                      # Spec quality checklist (shipped with /speckit.specify)
```

### Source Code (repository root)

```text
# Parser layer — two new additions (FR-001 / FR-002)
src/texlint/core/
├── parser.py                                # MODIFIED — add strip_rnw_chunks, parse_rnw_file
└── rmd_parser.py                            # NEW — hand-rolled .Rmd tokenizer

# Public API — three additive extensions (FR-007, FR-008, FR-013)
src/texlint/api.py                           # MODIFIED:
                                             #  - ParsedRmdFile dataclass (new)
                                             #  - ParsedDocument.rmd_files (new field)
                                             #  - ParsedDocument.all_tex_like() (new helper)
                                             #  - ComplianceReport.skipped_rules (new field)
                                             #  - Rule.formats semantics: file-suffix → input-format filter

# Engine — dispatch + skip-list bookkeeping (FR-013, FR-008)
src/texlint/core/engine.py                   # MODIFIED — parse_document extension map,
                                             #            skipped_rules population in run()

# Rule format-filter audit — one-line edit per preamble rule (FR-020)
src/texlint/journals/jss/rules/preamble.py   # MODIFIED — formats=frozenset({"tex", "rnw"})
                                             #            on JSS-PRE-001..008 Rule instances
# (no other rule modules touched — default formats=None)

# Corpus manifest + report extension (FR-019, FR-016, SC-006)
eval/
├── corpus-manifest.csv                      # MODIFIED — append 3–5 .Rnw + 2–3 .Rmd CRAN rows
├── report.py                                # MODIFIED — --by-format flag for per-format slicing
└── scan.py                                  # UNCHANGED — extension dispatch is engine-level

# pyproject.toml — runtime deps (FR-002)
pyproject.toml                               # MODIFIED — add pyyaml>=6.0 to runtime deps

# Tests
tests/
├── unit/
│   ├── test_rnw_stripper.py                 # NEW — line-count invariant, multi-chunk, comment edge
│   ├── test_rmd_parser.py                   # NEW — frontmatter, headings, fences, inline code
│   ├── test_api.py                          # MODIFIED — round-trip tests for new fields
│   └── test_engine.py                       # MODIFIED — parse_document dispatch + skipped_rules
└── fixtures/
    ├── compliant/
    │   ├── minimal.Rnw                      # NEW — clean Sweave fixture
    │   └── minimal.Rmd                      # NEW — clean R Markdown fixture
    └── violations/
        ├── rnw/
        │   └── JSS-MARKUP-002-bad.Rnw       # NEW — chunk contains 'MASS'; rule fires on prose only
        └── rmd/
            └── JSS-MARKUP-002-bad.Rmd       # NEW — fenced code block contains 'MASS'; rule fires on prose only
```

**Structure Decision**: Spec 005 extends the existing `core/` layer
(parser dispatch + Rnw stripper) and adds a single new module
(`core/rmd_parser.py`). API surface grows by 1 dataclass + 2 fields +
1 helper method (minimal per §X). The JSS journal plugin is touched in
exactly one way: the preamble module's `Rule(...)` constructions gain
a `formats=frozenset({"tex", "rnw"})` argument. Corpus manifest gains
rows; `eval-jss report` gains a flag. No new packages, no new CLI
subcommands.

## Complexity Tracking

One documented amendment.

| Amendment | Why Needed | Alternative Rejected |
|-----------|------------|---------------------|
| Core edits to `src/texlint/core/` and `src/texlint/api.py` (§IV) | §IV prohibits core edits when *adding a journal*. This spec adds input-format support, not a journal — every journal benefits from `.Rnw` / `.Rmd` dispatch. The edits are: (a) parser-layer dispatch in `core/parser.py`, (b) public dataclass `ParsedRmdFile` in `api.py` that mirrors the existing `ParsedTexFile` / `ParsedBibFile` pattern, (c) the new `Rule.formats` semantics which extends (not breaks) the existing field. Equivalent to the `Severity.INFO` amendment in spec 004's Complexity Tracking. | **Ship Rnw/Rmd support as a separate package** — would require a public parser-plugin protocol in `api.py` first, which is a larger change than the direct extension. Rejected — the §X small-surface preference trumps the §IV "no core edits" preference when the alternative is to invent a plugin layer. **Put all parsing in `journals/jss/`** — parser is journal-agnostic; this would couple it unnecessarily to JSS. Rejected. |
