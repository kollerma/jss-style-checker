# Contract: Auto-fix CLI flags

**Spec**: [../spec.md](../spec.md)
**Plan**: [../plan.md](../plan.md)

This contract documents the CLI surface added by spec 008.

## C-1 Flags

| Flag                  | Type            | Notes                                                      |
| --------------------- | --------------- | ---------------------------------------------------------- |
| `--fix`               | `bool`          | Enables auto-fix.                                          |
| `--dry-run`           | `bool`          | Requires `--fix`. Print unified diff; do not write.        |
| `--apply`             | `bool`          | Requires `--fix`. Interactive `[y/n/a/q]` per fix.          |
| `--fix-rule RULE-ID`  | `str` (multiple)| Repeatable. Limits eligible fixes to the named rule ids.   |

## C-2 Flag-combination validation

| Flags                    | Behaviour                                                                |
| ------------------------ | ------------------------------------------------------------------------ |
| (none)                   | Read-only lint (existing behaviour).                                     |
| `--fix`                  | `mode = "write"`.                                                         |
| `--fix --dry-run`        | `mode = "dry-run"`.                                                       |
| `--fix --apply`          | `mode = "interactive"`.                                                   |
| `--dry-run` (alone)      | Exit 2; stderr `--dry-run requires --fix`.                                |
| `--apply` (alone)        | Exit 2; stderr `--apply requires --fix`.                                  |
| `--dry-run --apply`      | Exit 2; stderr `--dry-run and --apply are mutually exclusive`.            |
| `--fix-rule X`           | Filter applies. With or without `--fix` (filter is a no-op without `--fix`).|

`--fix-rule` validation: an unknown rule id (one not present in
`_catalogue_data.RULES`) MUST cause exit 2 with a stderr message
naming the unknown id.

## C-3 Output streams

| Mode             | stdout                            | stderr                                  |
| ---------------- | --------------------------------- | --------------------------------------- |
| `"write"`        | exit summary (`N applied, …`)     | rejected-fix log; permission errors      |
| `"dry-run"`      | unified diff                      | exit summary on stderr                  |
| `"interactive"`  | per-fix prompt + diff hunk        | exit summary on stderr                   |

The dry-run unified-diff format is the standard `difflib.unified_diff`
output, prefixed per file:

```
--- <file>
+++ <file>
@@ -L,n +L,n @@
 context
-old
+new
 context
```

## C-4 Exit codes

Per research §8 (consolidated here):

| Mode                  | Outcome                                              | Code |
| --------------------- | ---------------------------------------------------- | ---- |
| (no fix flag)         | clean run                                            | 0    |
| (no fix flag)         | violations remain                                    | 1    |
| (no fix flag)         | parse failure                                        | 2    |
| `--fix --dry-run`     | any                                                  | 0    |
| `--fix`               | all fixes applied, no remaining violations           | 0    |
| `--fix`               | fixes applied, some unfixable violations remain      | 1    |
| `--fix`               | rollback occurred (FR-008 regression)                | 2    |
| `--fix`               | usage error (unknown `--fix-rule`, permission, etc.) | 2    |
| `--fix --apply`, `q`  | user quit; partial application committed             | 0    |

## C-5 No flag-name collisions

The four spec-008 flags do not collide with any pre-spec-008
flag. `--source-root` (spec 006) and `--ignore-rules` (spec 001)
remain orthogonal.

## C-6 Default behaviour preserved

When invoked without any of the four new flags, `jss-lint`
behaviour is byte-identical to the spec-007 baseline. The
existing CLI tests (terminal, JSON, HTML, SARIF goldens) pass
unchanged after this spec lands.

## C-7 SARIF integration

`--output sarif` is orthogonal to the fix flags. With or
without `--fix`, SARIF emits `runs[0].results[].fixes[]` for
every violation whose `Violation.fix is not None`.

If both `--fix` and `--output sarif` are set, the SARIF is
rendered AFTER the fix run, against the *post-fix* report —
i.e., violations that were successfully fixed do not appear
in the SARIF results. This matches the user expectation:
SARIF is the report on the final state.
