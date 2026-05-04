# Implementation Plan: SARIF 2.1.0 Output

**Branch**: `006-sarif-output` | **Date**: 2026-05-03 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/006-sarif-output/spec.md`

## Summary

Add a fourth `--output` value, `sarif`, that emits a SARIF 2.1.0 JSON
document. The renderer is a single new module
(`src/texlint/output/sarif.py`) exporting `render(report, cfg)` —
identical signature to the existing `json_output.py` and
`html_output.py`. It pulls rule metadata from
`texlint.journals._catalogue_data.RULES` (so every catalogue rule
appears under `runs[0].tool.driver.rules`, not only those with hits)
and serialises with the standard-library `json` module using
`sort_keys=True, indent=2` for byte-deterministic output.

The CLI gets one new option, `--source-root <DIR>`, that controls how
artifact URIs are made relative. Default is CWD. The flag is silently
accepted (and ignored) for the other three output modes so a single
CI invocation can pass it unconditionally.

Parse failures (`JSS-PARSE-000`) emit SARIF `notification` entries
under `runs[0].invocations[0].toolExecutionNotifications`, distinct
from `runs[0].results`. They are NOT silenced by `--ignore-rules
JSS-PARSE-000` (per spec Clarifications: notifications describe
tool-execution events, not findings).

The existing `--output json` byte shape is preserved; a regression
test asserts equality with the stored golden artefact. The contract
test suite includes a SARIF-2.1.0-schema validator (test-time
dependency only — `jsonschema>=4.0` already in dev extras).

No new runtime dependencies. SARIF is plain JSON.

## Technical Context

**Language/Version**: Python ≥3.10, unchanged from specs 001–005.

**Primary Dependencies** (runtime):
- `pylatexenc>=2.10` (unchanged).
- `bibtexparser>=2.0.0b6` (unchanged).
- `click>=8.1`, `rich>=13.0`, `jinja2>=3.1` (unchanged).
- `pyyaml>=6.0` (added in spec 005, unchanged).
- **No new runtime deps.** SARIF is plain JSON; `tool.driver.rules`
  is built from already-loaded `_catalogue_data.RULES`.

**Primary Dependencies** (dev / test):
- `jsonschema>=4.0` — already present. Used only at test time to
  validate golden SARIF artefacts against the SARIF 2.1.0 schema.
- The official SARIF 2.1.0 JSON schema is vendored as a test fixture
  at `tests/fixtures/sarif-2.1.0-schema.json` (not loaded over the
  network at test time — Constitution §I determinism).

**Storage**: None. SARIF documents are produced on stdout (or
redirected by the user); the eval harness's SQLite database is
unchanged.

**Testing**: `pytest` + `pytest-cov` (unchanged). Constitution §IX
applies to rule modules; `output/sarif.py` is not a rule module and
is governed by ordinary engineering judgment, target ≥95% line
coverage in line with `output/json_output.py`.

**Target Platform**: POSIX primary (Linux / macOS), unchanged.

**Project Type**: Python library + CLI (`jss-lint` entry point). Spec
006 adds one renderer module (`src/texlint/output/sarif.py`), one
`--source-root` flag in `src/texlint/cli.py`, and one new
`ToolConfig` field (`source_root: Path`) in `src/texlint/api.py`. No
journal-layer changes.

**Performance Goals**: SARIF rendering is O(R + V) in the rule count
R and violation count V (single dict-construction pass plus one
`json.dumps`). For the eval corpus (172 papers, ~2k violations
total) the renderer adds <50 ms wall-clock to a full run. Unchanged
end-to-end target: <2 s per typical paper.

**Constraints**:
- Constitution §I determinism: `json.dumps(..., sort_keys=True,
  indent=2)` is deterministic. No timestamps, GUIDs, host names, or
  PIDs leak into output. Path normalisation uses `Path.as_posix()`
  followed by an explicit `Path.relative_to(source_root)` /
  `os.path.relpath()` fallback.
- Constitution §II AST-first: N/A — output rendering is downstream
  of any AST work.
- Constitution §III non-fatal parse: SARIF surfaces
  `JSS-PARSE-000` violations as `toolExecutionNotifications`. The
  renderer never raises on partial reports; absent end-positions
  yield SARIF regions with `startLine`/`startColumn` only.
- Constitution §IV zero core edits for journals: this spec adds a
  CLI flag and a `ToolConfig` field. Neither change adds a
  journal; the edits are output-layer + config-layer extensions
  shared across journals. Documented in Complexity Tracking.
- Constitution §VI precision gate: N/A — no new rules.
- Constitution §VII safe auto-fix: this spec emits NO `fixes[]`.
  Spec 008 owns `fixes[]` rendering.
- Constitution §VIII TDD: golden-file tests for
  `output/sarif.py` land before the renderer body per the plan
  input's test-list (clean run, single error, multi-file run,
  parse-error case). Tasks.md will order fixtures → failing tests
  → implementation.
- Constitution §IX 100% branch coverage on rule modules:
  unchanged. No rule modules touched.
- Constitution §X small surface: one new module, one new CLI
  flag, one new `ToolConfig` field. The renderer reuses the
  existing `Violation` / `Rule` / `_catalogue_data.RULES` surface;
  it does not introduce a SARIF builder helper layer or a SARIF
  type hierarchy. The output dict is constructed directly in the
  module.
- Constitution §XII reproducible corpus: N/A — no corpus
  expansion.

**Scale/Scope**: 1 new module (`output/sarif.py`, ~150 LOC). 1 CLI
flag (`--source-root`). 1 `ToolConfig` field (`source_root: Path`,
default `Path.cwd()`). 4 golden-file fixtures + 1 schema fixture +
1 test module (`tests/unit/output/test_sarif.py`). 1 contract doc
update (`specs/001-linter-foundation/contracts/cli.md`-style note
on SARIF as a peer format).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **§I Determinism** — `json.dumps(..., sort_keys=True,
      indent=2)` with no time/host/PID inputs. Pure function of
      `(report, cfg)`. **PASS**.
- [x] **§II AST-First** — N/A; output-layer module. **PASS by
      non-applicability**.
- [x] **§III Non-Fatal Parse** — `JSS-PARSE-000` violations
      surface as `toolExecutionNotifications`. The renderer never
      raises on partial reports. **PASS**.
- [x] **§IV Zero Core Edits for Journals** — this spec edits
      `src/texlint/cli.py` and `src/texlint/api.py` (`ToolConfig`).
      **This is NOT a journal addition** — the edits extend the
      output / config surface shared across every journal.
      Documented in Complexity Tracking below. **PASS with
      documented amendment**.
- [x] **§V Authority Cited** — N/A; no new rules. The catalogue
      keeps its existing authority citations and is rendered into
      `tool.driver.rules`. **PASS**.
- [x] **§VI ≥90% Precision Gate** — N/A; no new rules. **PASS**.
- [x] **§VII Safe Auto-Fix** — `fix=None` for every violation
      this spec emits. `fixes[]` deferred to spec 008. **PASS**.
- [x] **§VIII TDD** — golden-file tests for the four scenarios
      (clean, single-error, multi-file, parse-error) and the
      schema-validation contract test land before the renderer
      body per task ordering. **PASS by task ordering**.
- [x] **§IX 100% Branch Coverage on Rule Modules** — unchanged;
      no rule modules touched. **PASS**.
- [x] **§X Small Surface** — one new module, one CLI flag, one
      `ToolConfig` field. No SARIF builder helper layer; no
      SARIF type classes. The catalogue → `tool.driver.rules`
      projection is a direct dict-comprehension in the module.
      `--source-root` is silently accepted by other renderers
      so a single CI invocation works (rejected alternative:
      add the flag to *only* the SARIF subcommand and require
      callers to branch — would multiply CI surface). **PASS**.
- [x] **§XII Reproducible Corpus** — N/A; no corpus expansion.
      **PASS**.

All gates PASS. One documented amendment under §IV
(output-layer + config-layer edits, not a journal addition). See
Complexity Tracking.

Post-Phase-1 re-check: gates still PASS. The data-model entries
(`SarifLog`, `SarifRun`, etc.) are documentation projections of
the SARIF 2.1.0 schema, not new public API; no §IV / §X concerns
arose.

## Project Structure

### Documentation (this feature)

```text
specs/006-sarif-output/
├── plan.md                                  # This file
├── research.md                              # Phase 0: SARIF schema choice, source-root semantics, taxonomy decision
├── data-model.md                            # Phase 1: SarifLog projection, ToolConfig.source_root extension
├── quickstart.md                            # Phase 1: contributor onboarding for the SARIF renderer
├── contracts/
│   └── sarif-output.md                      # Contract: top-level invariants + golden-fixture catalogue
└── checklists/
    └── requirements.md                      # Spec quality checklist (shipped with /speckit.specify)
```

### Source Code (repository root)

```text
# Output layer — one new module
src/texlint/output/
├── sarif.py                                 # NEW — render(report, cfg); SARIF 2.1.0 producer
├── json_output.py                           # UNCHANGED — golden-equality regression
├── html_output.py                           # UNCHANGED
├── terminal.py                              # UNCHANGED
└── __init__.py                              # UNCHANGED

# CLI — wire the new option + flag
src/texlint/cli.py                           # MODIFIED:
                                             #  - add "sarif" to --output Choice
                                             #  - add --source-root <DIR> click.option
                                             #  - extend _dispatch_renderer for "sarif"
                                             #  - thread source_root into ToolConfig overrides

# Config — one new field
src/texlint/api.py                           # MODIFIED:
                                             #  - ToolConfig.source_root: Path = field(default_factory=Path.cwd)

# Catalogue access — already public (used by other renderers)
src/texlint/journals/_catalogue_data.py      # UNCHANGED — RULES exposed as-is

# Tests
tests/
├── unit/
│   └── output/
│       └── test_sarif.py                    # NEW — golden-file tests + schema validation
└── fixtures/
    ├── sarif-2.1.0-schema.json              # NEW — vendored OASIS SARIF 2.1.0 schema
    └── sarif/
        ├── golden_clean.sarif               # NEW — clean run golden
        ├── golden_single_error.sarif        # NEW — single error golden
        ├── golden_multi_file.sarif          # NEW — multi-file golden
        └── golden_parse_error.sarif         # NEW — parse failure golden

# Contracts (cross-spec doc update)
specs/001-linter-foundation/contracts/
└── cli.md                                   # MODIFIED — note SARIF as peer format alongside terminal/json/html
```

**Structure Decision**: Spec 006 adds exactly one new source module
(`src/texlint/output/sarif.py`) and one new test module
(`tests/unit/output/test_sarif.py`). The `cli.py` edit is two-line
(extend the `--output` Choice, add `--source-root` option) plus a
three-line addition to `_dispatch_renderer`. The `api.py` edit is a
one-field addition to `ToolConfig`. No new packages, no new CLI
subcommands, no new public types beyond a single config field. This
is the minimum-surface implementation per Constitution §X.

## Complexity Tracking

One documented amendment.

| Amendment | Why Needed | Alternative Rejected |
|-----------|------------|---------------------|
| Edits to `src/texlint/cli.py` and `src/texlint/api.py` (§IV) | §IV prohibits core edits when *adding a journal*. This spec adds an output renderer + a config flag, not a journal — every journal benefits from SARIF and from a `--source-root` flag. The edits are: (a) one new value in the `--output` Choice list, (b) one new `--source-root` Click option, (c) one new field on `ToolConfig`, (d) one new branch in `_dispatch_renderer`. Equivalent in scope to spec 005's parser-layer extension and spec 004's `Severity.INFO` addition. | **Implement SARIF as a separate package** — would require a public renderer-plugin protocol in `api.py`, a strictly larger change than the direct extension. Rejected per §X. **Make `--source-root` SARIF-only** — would require callers in CI to branch on output format. Rejected — silent acceptance for other formats is one extra line and zero behavioural change. |
