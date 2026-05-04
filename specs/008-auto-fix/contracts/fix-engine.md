# Contract: `apply_fixes` engine

**Spec**: [../spec.md](../spec.md)
**Plan**: [../plan.md](../plan.md)

This contract documents the byte-level invariants of
`src/texlint/core/fixer.py::apply_fixes`. Every invariant has
a corresponding test in `tests/unit/core/test_fixer.py` (engine
unit) and `tests/integration/test_fix_cli.py` (CLI end-to-end).

## C-1 No-flag invariance

`apply_fixes` is NEVER called when no fix flag is set. The
read-only path in `cli.py` skips the function entirely. The
CLI's behaviour without fix flags MUST be byte-identical to
the spec-007 baseline (verified by the existing terminal /
JSON / HTML / SARIF golden tests, modulo the SARIF `fixes[]`
deferral activation).

## C-2 Conflict resolution determinism

Given a fix list F over a single file, the partition
`(applied, skipped)` produced by the conflict-resolution
algorithm depends only on `F`. Two invocations with equal
`F` (in any order) produce the same `applied` set and the
same `skipped` set.

The applied set is computed by the algorithm in
`data-model.md §6`.

## C-3 Reverse-position application

Fixes within a file's `applied` set are written in
descending order of `Fix.start`. After application, every
`Fix.start` and `Fix.end` of the *unwritten* fixes still
references valid byte offsets in the original source — they
are never shifted by earlier writes.

## C-4 Atomic write + rollback

For each file F in scope:
1. The pre-fix bytes are read fully into memory.
2. The post-fix bytes are computed.
3. A tempfile is created in `parent(F)` (same volume).
4. The post-fix bytes are written + flushed + fsynced.
5. `os.replace(tmp.name, F)` swaps in the new content.
6. The new content is re-parsed and re-linted.
7. If any `(rule_id, line)` whose violation had `fix !=
   None` AND was selected (i.e., it was a candidate for
   application) re-appears in the post-fix report, a
   second tempfile is written with the cached pre-fix
   bytes and `os.replace`'d into F.

Failure modes:
- A write that fails between (3) and (5): the original F
  is intact (untouched on disk); the tempfile is unlinked
  in a `finally` block.
- A write that fails after (5) on the rollback path: the
  rejection is escalated to a stderr fatal; exit code 2.

## C-5 Re-validation scope

Re-validation re-parses ONLY the rewritten file(s). Other
files in the same `ParsedDocument` are not re-parsed and
not re-linted by the engine. Cross-file regressions are
out of scope for spec 008 (per research §4).

## C-6 `--dry-run` is read-only

In `mode = "dry-run"`, the engine MUST NOT touch the
filesystem. No tempfile is created, no `os.replace` is
called. Output is a unified diff written to `stdout`
(injected by the caller for testing).

The unified diff uses `difflib.unified_diff(original,
patched, lineterm="\n")` with `fromfile=str(file)` and
`tofile=str(file)`.

## C-7 Interactive prompt invariants

In `mode = "interactive"`:
- One prompt is issued per fix, in the order the engine
  would write them (reverse-position within each file,
  files in lexicographic order).
- The prompt accepts only `y`, `n`, `a`, `q` (single
  character). Any other input re-prompts on the same fix.
- EOF on stdin is treated as `q`.
- After `a`, no further prompts are issued in this
  session; remaining fixes are applied via the `"write"`
  path.
- After `q`, accepted fixes (those answered `y` or
  applied via earlier `a`) are committed; remaining
  fixes are skipped with `reason="user-skipped"`.

## C-8 `--fix-rule` semantics

When `rules` is non-`None`, only fixes whose
`Violation.rule_id in rules` are eligible for application.
Fixes that are filtered out:
- Are NOT included in conflict resolution (i.e., they
  cannot displace a `--fix-rule`-eligible fix).
- ARE included in `FixReport.skipped` with
  `reason="rule-not-selected"` so the exit summary tells
  the user how many fixes their flag suppressed.

## C-9 Exit codes

Mapped per research §8 / spec FR-014.

The engine returns a `FixReport`; the CLI computes the
exit code from `(mode, FixReport, remaining-violations)`.
The mapping is fully deterministic and documented in the
CLI contract.

## C-10 SARIF `fixes[]` activation

When `--output sarif` is set:
- Every `Result` whose corresponding `Violation.fix is not
  None` MUST emit a `fixes[]` array (one element per
  `Fix`, which is always exactly one in this spec).
- The shape matches data-model §7.
- The activation is independent of the fix flags: SARIF
  emits `fixes[]` for what *could* be fixed, not what
  *was* applied. (Research §7.)

## C-11 No new runtime dependencies

The engine uses only `tempfile`, `os`, `pathlib`,
`difflib`, `click` (already present). No new runtime
deps land with this spec.
