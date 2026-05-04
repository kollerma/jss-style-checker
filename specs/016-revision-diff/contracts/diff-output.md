# Contract: `jss-lint diff` Output

**Spec**: [../spec.md](../spec.md)
**Plan**: [../plan.md](../plan.md)

## C-1 Subcommand registration

`jss-lint diff` MUST be a subcommand of the spec-009 Click
group. Pre-spec-016 entry-points (`jss-lint <PATHS>`,
`explain`, `init`, `lsp`, `report`) MUST continue to work
unchanged.

## C-2 Identity tuple

Default identity:
`(rule_id, file, line, message)`.

With `--ignore-line-drift`:
`(rule_id, file, message)`.

Neither `severity` nor `column` participates.

## C-3 Rule-rename map

The diff command MUST load
`docs/jss-guide/rule-renames.json` (when present) and
apply its `renames` dict to OLD violations BEFORE
identity comparison.

When the file is missing, the diff proceeds with an empty
map. When the file is present but malformed, exit 2 with
a stderr message naming the file and the parse error.

## C-4 Partition correctness

Every input violation MUST appear in exactly one of
`fixed` / `introduced` / `unchanged`:
- `fixed`: identity in OLD's set but not NEW's.
- `introduced`: identity in NEW's set but not OLD's.
- `unchanged`: identity in both.

The three sets are pairwise disjoint and their union
covers every input violation.

## C-5 Exit codes

Per spec FR-005:
- `0` when `len(introduced) == 0`.
- `1` when `len(introduced) > 0`.
- `2` on usage error.

## C-6 Output sections

| Format     | Section markers                                                  |
| ---------- | ---------------------------------------------------------------- |
| `terminal` | `== Fixed ==` / `== Introduced ==` / `== Unchanged ==` headers.   |
| `markdown` | `## Fixed` / `## Introduced` / `## Unchanged` (CommonMark).        |
| `json`     | top-level keys `summary`, `fixed`, `introduced`, `unchanged`.     |

## C-7 Determinism

For the same `(old, new, ignore_line_drift, rule_renames,
format)`, two invocations MUST produce byte-identical
output (modulo terminal colour codes, forced off in
tests).

## C-8 `unchanged`-group rendering

For violations classified `unchanged`, the rendered
entry MUST use NEW's `line`, `column`, and `message`
(research §7). This makes the `unchanged` list
reflect the current source state.

## C-9 Schema validation

Both OLD and NEW MUST validate against the spec-001
`--output json` schema. On mismatch, the CLI exits 2
with stderr `<file>: schema mismatch — <path>: <reason>`.

## C-10 Empty inputs

`OLD = []` and/or `NEW = []` MUST be handled:
- Empty OLD + non-empty NEW: every NEW violation is
  `introduced`.
- Non-empty OLD + empty NEW: every OLD violation is
  `fixed`.
- Both empty: all three groups empty; exit 0.

## C-11 Cross-format consistency

For the same `(old, new, ignore_line_drift,
rule_renames)`, the three formats MUST partition the
violations identically. A test asserts the partition
counts match across format invocations.

## C-12 Backwards compatibility

The `--output json` schema (spec 001) is unchanged by
this spec. Older JSON files produced by pre-spec-016
runs of the linter remain valid input.
