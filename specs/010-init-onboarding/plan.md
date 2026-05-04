# Implementation Plan: `jss-lint init` Interactive Bootstrap

**Branch**: `010-init-onboarding` | **Date**: 2026-05-03 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/010-init-onboarding/spec.md`

## Summary

Add `jss-lint init [PATH]` as the second new subcommand (after spec
009's `explain`). Implementation lives in
`src/texlint/init.py::run(path, *, force, dry_run, threshold)`. The
flow is:

1. Resolve `PATH` to one or more source files (single file or
   directory scan).
2. Run the existing read-only lint pass (re-using `engine.run`).
3. Aggregate violations by `rule_id`.
4. Open the precision-history DB at `eval/precision-history.db` if
   present; query each rule's most-recent corpus-wide precision.
5. Partition rules into `must-fix` / `suppressed` / `untriaged`.
6. Render a TOML config with inline comments via `tomli_w` (or the
   stdlib path if available — research §3).
7. Refuse / `--force` / `--dry-run` semantics gate the actual
   write.
8. Print the summary table to stderr (rich `Table`).

The atomic-write semantics from spec 008 are reused (tempfile +
`os.replace`).

## Technical Context

**Language/Version**: Python ≥3.10, unchanged.

**Primary Dependencies** (runtime): unchanged from spec 009; gains
**`tomli_w>=1.0`** as a runtime dep for TOML serialisation. The
existing `tomli` covers reads (Python <3.11 fallback;
`tomllib` is stdlib on ≥3.11). `tomli_w` is ~200 LOC and has no
transitive deps.

**Storage**: Reads `eval/precision-history.db` (SQLite, established
in spec 002) when present; never writes to it. The generated
`.jss-lint.toml` is the only on-disk side effect.

**Testing**:
- `tests/unit/test_init.py` — clean manuscript, noisy manuscript,
  refusal, `--force`, `--dry-run`.
- `tests/integration/test_init_cli.py` — end-to-end CLI run.
- Fixture pair: a manuscript + a precision-DB snapshot →
  golden-byte-equal `.jss-lint.toml`.

**Target Platform**: POSIX, unchanged.

**Project Type**: Library + CLI; gains a second subcommand.

**Performance Goals**: `init` is a single read-only lint pass +
DB query. For a typical manuscript (≤5k lines), end-to-end <2 s.
For a directory scan, O(file count) lint passes.

**Constraints**:
- Constitution §I determinism: `init` is a pure function of (source
  files, precision-history DB snapshot, threshold). Inline comments
  use the rule's metadata, not free-form generated prose.
- Constitution §III non-fatal: a missing DB or unparseable manuscript
  surfaces as a graceful note in the summary; `init` exits 0 in
  both cases (it has done its part).
- Constitution §IV zero core edits for journals: this spec edits
  `cli.py` (one new subcommand under the spec-009 group) and adds
  one new top-level module. NOT a journal addition. Documented in
  Complexity Tracking.
- Constitution §V authority cited: comments in the generated TOML
  cite "Constitution §VI threshold 0.90" inline.
- Constitution §VI precision gate: this spec *applies* §VI as a
  user-facing tool. The threshold default matches §VI exactly.
- Constitution §VII safe auto-fix: not auto-fix per se, but the
  same atomic-write pattern (tempfile + `os.replace`) protects
  the user's existing config.
- Constitution §VIII TDD: unit tests land before the `init.py`
  body.
- Constitution §IX 100% branch coverage on rule modules:
  unchanged.
- Constitution §X small surface: one new module, one CLI
  subcommand, one runtime dep (`tomli_w`). The dep is justified
  in research §3.
- Constitution §XII reproducible corpus: N/A; this spec consumes
  the precision history but does not extend the corpus.

**Scale/Scope**: 1 new module (`src/texlint/init.py`, ~300 LOC).
1 new runtime dep (`tomli_w`). 1 new CLI subcommand. 2 new test
modules (~150 LOC). 4-6 fixtures (manuscript + DB snapshot pair).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **§I Determinism** — pure function of inputs. **PASS**.
- [x] **§II AST-First** — N/A; `init` consumes the existing
      AST-first lint output. **PASS**.
- [x] **§III Non-Fatal Parse** — `init` reuses the engine; parse
      failures surface as part of the summary. **PASS**.
- [x] **§IV Zero Core Edits for Journals** — `cli.py` (one new
      subcommand) and one new top-level module. NOT a journal
      addition. **PASS with documented amendment**.
- [x] **§V Authority Cited** — generated TOML comments cite the
      precision value AND Constitution §VI as the threshold
      anchor. **PASS**.
- [x] **§VI ≥90% Precision Gate** — this spec applies §VI as a
      user-facing tool. **PASS**.
- [x] **§VII Safe Auto-Fix** — atomic write protects existing
      `.jss-lint.toml`. **PASS**.
- [x] **§VIII TDD** — unit / integration tests land before the
      module body. **PASS by task ordering**.
- [x] **§IX 100% Branch Coverage on Rule Modules** — unchanged.
      **PASS**.
- [x] **§X Small Surface** — `init.py` has one caller (the CLI
      subcommand). The `tomli_w` dep is justified by the lack
      of stdlib write support before Python 3.11+; and even
      Python 3.13 does not ship a TOML writer. The dep is
      ~200 LOC and pure-Python. **PASS**.
- [x] **§XII Reproducible Corpus** — N/A. **PASS**.

All gates PASS. One documented amendment under §IV.

Post-Phase-1 re-check: gates still PASS.

## Project Structure

### Documentation (this feature)

```text
specs/010-init-onboarding/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── init-cli.md
└── checklists/
    └── requirements.md
```

### Source Code (repository root)

```text
src/texlint/init.py                                # NEW — run(path, *, force, dry_run, threshold)
                                                   #       _classify_rules(violations, db, threshold)
                                                   #       _render_toml(classification) -> str
                                                   #       _atomic_write(target, contents) (reused pattern)

src/texlint/cli.py                                 # MODIFIED — register `init` subcommand under the
                                                   #            spec-009 Click group

pyproject.toml                                     # MODIFIED — runtime dep: tomli_w>=1.0

tests/
├── unit/
│   └── test_init.py                               # NEW — classification + TOML rendering
├── integration/
│   └── test_init_cli.py                           # NEW — end-to-end CLI invocation
└── fixtures/
    └── init/
        ├── manuscript_clean.tex
        ├── manuscript_noisy.tex
        ├── precision_db_snapshot.sqlite           # NEW — small fixture DB
        ├── golden_clean.toml                      # NEW — expected output for clean manuscript
        └── golden_noisy.toml                      # NEW — expected output for noisy manuscript

README.md                                          # MODIFIED — "Quick start" gains step 0:
                                                   #            jss-lint init manuscript.tex
```

**Structure Decision**: One module under `src/texlint/init.py`,
one CLI subcommand, one runtime dep, one new fixture DB snapshot.
The module is self-contained: it re-uses the engine for linting
and the spec-002 DB schema for precision queries; it does not
modify either.

## Complexity Tracking

One documented amendment.

| Amendment | Why Needed | Alternative Rejected |
|-----------|------------|---------------------|
| Edit to `src/texlint/cli.py` (new subcommand) and new module `src/texlint/init.py` (§IV) | §IV prohibits core edits when *adding a journal*. This spec adds a CLI subcommand + module that operate on top of the journal layer; they do not register a journal. | **Implement `init` as a separate binary** — packaging-surface inflation. Rejected. **Embed `init` in `cli.py` directly** — would push 300+ LOC into the CLI module; `init.py` is a clean cut. Rejected. |
