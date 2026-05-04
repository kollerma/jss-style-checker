# Research: `jss-lint init` Interactive Bootstrap

**Phase**: 0
**Spec**: [spec.md](spec.md)
**Plan**: [plan.md](plan.md)

---

## 1. Threshold default and configurability

**Decision**: Default `--threshold 0.90`, matching Constitution §VI.
The flag accepts a float in `[0, 1]`.

**Rationale**:
- Aligning the user-facing default with the project's own
  precision gate avoids surprise: a user who runs `jss-lint
  init` with no flags gets a config that mirrors the project's
  internal standard.
- Configurability handles the strict-maintainer case (raise to
  0.95) and the generous-author case (lower to 0.80) without
  baking either into the binary.

**Alternatives considered**:
- Hard-code 0.90 with no flag: rejected — limits user agency
  for a five-line implementation cost.
- Default to a corpus-empirical value (e.g., median precision):
  rejected — non-deterministic across DB snapshots; surprise.

---

## 2. Precision data source

**Decision**: Read from the existing
`eval/precision-history.db` (spec 002) when present. Query the
*most recent* row for each rule. When the DB is missing, fall
back gracefully (no precision-based suppressions, summary note).

**Rationale**:
- The DB is already the project's source of truth for rule
  precision (spec 002).
- Reading the most recent row gives users the freshest data;
  averaging would dilute regressions.
- Graceful fall-back keeps `init` useful for users who installed
  the CLI without the eval extras.

**Alternatives considered**:
- Read all rows and average: rejected — dilutes recent
  regressions.
- Require the DB (refuse to run without it): rejected — too
  hostile for first-time users.
- Bundle a snapshot of precision data with the install:
  rejected — Constitution §X (Small Surface), and the snapshot
  would be stale immediately.

---

## 3. TOML serialisation: `tomli_w` vs. stdlib

**Decision**: Add `tomli_w>=1.0` as a runtime dep.

**Rationale**:
- Python 3.11+ stdlib `tomllib` is read-only. There is no
  stdlib write support as of Python 3.13.
- `tomli_w` is the de-facto companion writer to `tomli`; ~200
  LOC, pure-Python, no transitive deps. Constitution §X allows
  small surface additions when the alternative is a hand-rolled
  serialiser.
- A hand-rolled serialiser would have to handle escape rules,
  multi-line strings, comment placement — complexity worse
  than the dep.

**Alternatives considered**:
- Hand-roll a TOML writer: rejected per §X. The corner cases
  (escape rules, multiline strings) outweigh the dep cost.
- Emit a JSON config instead of TOML: rejected — the existing
  `.jss-lint.toml` (spec 001) is TOML; introducing a JSON
  variant breaks the single-format convention.
- Use `tomlkit` (preserves comments on parse): rejected —
  larger dep (~5x `tomli_w`), supports a feature we don't
  need (we generate from scratch, never round-trip).

---

## 4. Inline-comment placement

**Decision**: Emit comments as `# <text>` lines immediately
above the rule id they explain inside the `ignore_rules` array.
TOML does not natively support array-element-attached comments,
so the array is emitted as a multi-line literal:

```toml
ignore_rules = [
  # JSS-MARKUP-005: precision 0.74 (corpus-wide), below 0.90
  "JSS-MARKUP-005",
  # JSS-NAME-007: precision 0.82, below 0.90
  "JSS-NAME-007",
]
```

**Rationale**:
- The TOML grammar permits comments inside multi-line arrays.
- `tomli` (the existing reader) handles this shape correctly.
- The visual association between comment and array element is
  unambiguous.

**Alternatives considered**:
- Emit comments as a separate `[[suppression_rationale]]`
  table: rejected — adds a non-standard TOML structure, and
  pre-spec-010 config consumers would not understand it.
- Emit comments as a single block above the array: rejected
  — drift between rule list and rationale list is too easy.

---

## 5. PATH semantics: file vs. directory

**Decision**: Accept either. A directory triggers a recursive
glob for `*.tex`, `*.Rnw`, `*.Rmd` (matches the engine's input
set). A single-file PATH lints just that file. The generated
`.jss-lint.toml` is written next to PATH (its parent directory
for a file, PATH itself for a directory).

**Rationale**:
- A first-time user typically runs `jss-lint init
  manuscript.tex` from a project directory; the config lands
  next to the manuscript.
- A power user with multiple manuscripts in a directory wants
  one shared config; passing the directory does that.

**Alternatives considered**:
- Always require a directory: rejected — extra friction for
  the common single-file case.
- Always require a single file: rejected — multi-file
  projects need a shared config.

---

## 6. Refusal mechanics

**Decision**: When `.jss-lint.toml` exists at the target
directory and `--force` is not set, exit 2 with a stderr
message:

```
jss-lint: refusing to overwrite /path/to/.jss-lint.toml; pass --force to overwrite
```

The file is byte-untouched.

**Rationale**:
- Exit 2 (usage error) matches the spec-008 convention for
  "the user did something we cannot complete safely".
- The message names the file explicitly so the user knows
  where it lives.

**Alternatives considered**:
- Exit 1: rejected — would conflate with "lint found
  violations".
- Prompt the user interactively: rejected — would block
  scripted use (`jss-lint init` in CI / Makefile).

---

## 7. Atomic write semantics

**Decision**: Reuse the spec-008 atomic-write pattern:
`tempfile.NamedTemporaryFile(dir=parent_of_target, delete=False)`
+ `os.replace`.

**Rationale**:
- An interrupted `init` (Ctrl+C, OOM, power) must not leave a
  half-written `.jss-lint.toml` that pre-spec-010 consumers
  cannot parse.
- Spec 008 already documents and tests the pattern; reusing
  it minimises new code.

**Alternatives considered**:
- Direct write with `open(..., "w")`: rejected — non-atomic.
- Two-phase write with a `.bak` backup: rejected — clutter
  in the user's working tree.

---

## 8. Severity overrides

**Decision**: This spec emits `ignore_rules` only. Severity
overrides are listed in spec FR-004 but the implementation
emits them only when a per-rule policy explicitly requests it
(spec leaves the precise mapping for tasks.md to fill in).
For the spec-010 baseline, the severity-override surface is
empty.

**Rationale**:
- Constitution §X: ship the smaller surface first. Severity
  overrides are a possible future extension; they do not gate
  the headline UX.
- The `.jss-lint.toml` schema already supports per-rule
  severity overrides (spec 001), so a follow-up spec can wire
  the generation logic without a schema change.

**Alternatives considered**:
- Always emit severity overrides for every rule: rejected —
  bloats the config with no triage value.
- Emit overrides for the must-fix rules: rejected — the user
  may want to see those at the default severity.

---

## Summary

All eight decisions follow from spec Clarifications and
Constitution §I, §VI, §VII, §X. No remaining `NEEDS
CLARIFICATION`. Ready for Phase 1.
