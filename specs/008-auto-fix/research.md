# Research: Auto-fix

**Phase**: 0 (Outline & Research)
**Spec**: [spec.md](spec.md)
**Plan**: [plan.md](plan.md)

## 1. Conflict resolution

**Decision**: When two fixes propose overlapping byte ranges
in the same file, sort all conflicting fixes by
`(confidence, rule_id, start, end)` ascending, apply the
first, drop the rest. `safe` (literal `"safe"`) sorts before
`review`. `rule_id` sorts lexicographically.

**Rationale**:
- Constitution §I (determinism): the sort key is total. Same
  fix set → same applied set, regardless of dict / list iteration
  order on the host platform.
- Highest-confidence-wins: a `safe` fix is by definition
  re-validated; a `review` fix is plausible-but-not-verified.
  Picking `safe` reduces the chance that a `review` fix
  triggers an FR-008 rollback.
- The loser is *skipped*, not rejected. Skipped is reported
  in the exit summary; rejected is reserved for FR-008
  regression failures (a fix that re-triggers its own rule
  after writing).

**Alternatives considered**:
- First-wins (lexicographic by source order): rejected — the
  output depends on which rule's check ran first, which is
  already non-deterministic in the current engine and would
  need stabilisation work first.
- Fail-loud (refuse to fix if any conflict exists): rejected
  — would block adoption for any rule pair that frequently
  overlaps.
- Highest-confidence-only with no tiebreaker (random or
  insertion-order): rejected — non-deterministic.

---

## 2. `--apply` interaction model

**Decision**: Single-key `[y/n/a/q]` prompt per fix. `a`
accepts the current fix and all remaining; `q` exits the
loop without applying further fixes (already-accepted
fixes are committed at exit).

**Rationale**:
- Linear walk-through is the simplest UX that supports
  consent. Bulk-by-rule was rejected per spec
  Clarifications.
- `a` (all) is the "I trust the rest" escape hatch.
- `q` (quit) is treated identically to EOF: stop prompting,
  apply already-accepted fixes, exit 0.

**Alternatives considered**:
- Per-rule batch prompts: rejected per Clarifications.
- Multi-character commands: rejected — slower, more error-
  prone, and `[y/n/a/q]` is the established `git add -p`
  convention.
- Curses / readline UI: rejected — Constitution §X (Small
  Surface) and tests would need a TTY.

---

## 3. Atomic write semantics

**Decision**: For each file F to be rewritten:

1. Read F's bytes into memory; cache as `original`.
2. Compute the rewritten bytes by applying fixes in
   reverse-position order.
3. Open `tempfile.NamedTemporaryFile(dir=parent_of(F),
   delete=False)`; write rewritten bytes; flush; fsync;
   close.
4. `os.replace(tmp.name, F)`.
5. Re-parse and re-lint F. If any
   `(rule_id, line)` from the supposed-to-be-fixed set
   re-appears in the post-fix report:
   - Open another tempfile in the same dir; write
     `original`; flush; fsync; close.
   - `os.replace(tmp2.name, F)`.
   - Log the rejection to stderr; continue with exit
     code 2.

**Rationale**:
- `os.replace` is atomic on POSIX and on Windows for
  same-volume moves. Tempfile in the same parent
  directory guarantees same-volume.
- Caching `original` in memory keeps rollback within a
  single I/O budget; JSS manuscripts are KB-scale so
  the cache is negligible.
- `fsync` before `os.replace` is the standard idiom for
  durability against power failure; we apply it even
  though our test surface does not.

**Alternatives considered**:
- `tempfile` with `delete=True`: rejected — `os.replace`
  unlinks the tempfile from its temporary name, but
  `delete=True` registers an unlink-at-close hook that
  would race with `os.replace`.
- Cross-volume tempfile (system temp dir): rejected —
  `os.replace` falls back to non-atomic copy across
  volumes.
- Two-phase commit with a `.bak` sidecar: rejected —
  `.bak` files clutter the user's working tree and
  introduce cleanup ambiguity.

---

## 4. Re-validation scope

**Decision**: After per-file rewrite, re-parse and re-lint
the *single file* (not the whole document). For each
violation that was supposed to be fixed (i.e., had `fix !=
None` and matched `--fix-rule` filter), the engine
records its `(rule_id, line)` pre-fix. If any of those
`(rule_id, line)` tuples appear in the post-fix report, the
file is rolled back and the rejection is logged.

**Rationale**:
- A fix that introduces a violation of the *same rule
  it was supposed to fix* is the strict §VII regression
  signal. Other rules' violations may legitimately appear
  (e.g., a wrap fix that pushes a line over the column
  limit) — those are not regressions of the fixing rule.
- Per-file re-parse is cheap; a whole-document re-parse
  would be O(file count) per multi-file run.
- Future spec extensions can tighten this (e.g., "fix
  rule X must not introduce violation of rule Y") via a
  separate contract; this spec ships the strict §VII
  invariant.

**Alternatives considered**:
- Full-document re-parse + diff: rejected — too aggressive,
  would block fixes that legitimately propagate side
  effects.
- No re-validation: rejected — Constitution §VII.

---

## 5. Conflict detection algorithm

**Decision**: Group fixes by file. Within each file, sort by
`start` ascending. Iterate; track the maximum `end` seen so
far. A new fix conflicts iff its `start < max_end`. When a
conflict is detected, sort the conflict cluster by the §1
key and keep only the winner.

**Rationale**:
- O(N log N) per file (the sort dominates). Linear scan
  detects clusters; in-cluster sort picks winners.
- The algorithm is identical to interval-merging
  problems solved in standard algorithm-design textbooks;
  it does not invent new structure.

**Alternatives considered**:
- Greedy first-wins after a single sort: rejected — non-
  deterministic depending on initial sort key.
- Interval tree: rejected — Constitution §X (Small
  Surface). Linear scan suffices for KB-scale files.

---

## 6. Selection of three rules to upgrade with `Fix` payloads

**Decision**: `JSS-CITE-003` (citation style), `JSS-NAME-001`
(package-name wrapping), `JSS-CAP-002` (capitalisation of
proper nouns) — or current equivalents in the catalogue at
implementation time.

**Rationale**:
- All three are mechanical (single-token replacement or
  wrapping with `\pkg{}` etc.).
- All three are over the precision gate (Constitution §VI)
  in the latest precision history.
- All three appear in the eval corpus often enough that
  the golden fixtures are realistic, not synthetic.

**Alternatives considered**:
- Upgrade all 58 rules at once: rejected — the spec is
  about the auto-fix engine; rule-by-rule upgrade is
  ongoing work that follows. Three rules is enough to
  exercise the engine's branches end-to-end.
- Upgrade only one rule: rejected — does not exercise
  the conflict-resolution path.

**Open**: the actual rule selection is finalised in
tasks.md based on the catalogue state at implementation
time. The three rules listed are the spec-008 baseline.

---

## 7. SARIF `fixes[]` projection

**Decision**: `runs[0].results[].fixes[]` is emitted only
when `violation.fix is not None`. The shape:

```json
"fixes": [{
  "description": {"text": "<Fix.description>"},
  "artifactChanges": [{
    "artifactLocation": {"uri": "<relativised path>"},
    "replacements": [{
      "deletedRegion": {
        "byteOffset": <Fix.start>,
        "byteLength": <Fix.end - Fix.start>
      },
      "insertedContent": {"text": "<Fix.replacement>"}
    }]
  }]
}]
```

`fixes[]` is omitted (not emitted as `[]`) when the
violation has no fix.

**Rationale**:
- Matches SARIF 2.1.0 schema for `fixes`.
- `byteOffset` / `byteLength` mirrors `Fix.(start,
  end)` directly.
- Suppression policy: a `--fix-rule`-skipped fix STILL
  appears in `fixes[]` if `violation.fix` is non-None;
  the SARIF output is the *available* fix set, not the
  *applied* set.

**Alternatives considered**:
- Emit only the fixes actually applied: rejected — would
  make SARIF dependent on `--fix-rule` flags; the
  consumer (GitHub code scanning) wants "what could be
  fixed", not "what was fixed".
- Always emit `fixes: []` for non-fixable violations:
  rejected — bloats the SARIF document for no value.

---

## 8. Exit code semantics

**Decision** (consolidates spec FR-014):

| Mode                 | Outcome                                              | Code |
| -------------------- | ---------------------------------------------------- | ---- |
| no fix flag          | clean run                                            | 0    |
| no fix flag          | violations remain                                    | 1    |
| no fix flag          | parse failure                                        | 2    |
| `--dry-run`          | any                                                  | 0    |
| `--fix`              | all fixes applied, no remaining violations           | 0    |
| `--fix`              | fixes applied, some unfixable violations remain      | 1    |
| `--fix`              | rollback occurred (FR-008 regression)                | 2    |
| `--fix`              | usage error (unknown `--fix-rule`, permission, etc.) | 2    |
| `--apply`, user `q`  | user quit; partial application committed             | 0    |

**Rationale**:
- `--dry-run` returning 0 lets shell pipelines treat the
  preview as informational.
- `--fix` returning 1 only when violations remain after
  the run gives CI a useful binary signal: "the linter is
  happy" vs "still work to do".
- Rollback returns 2 (the same code as parse failure)
  because the user's intervention is required either
  way.

---

## Summary

All eight decisions follow from the spec Clarifications and
Constitution §I, §III, §VII, §X. No remaining `NEEDS
CLARIFICATION`. Ready for Phase 1.
