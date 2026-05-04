# Contract: `jss-lint init` CLI

**Spec**: [../spec.md](../spec.md)
**Plan**: [../plan.md](../plan.md)

## C-1 Subcommand registration

`jss-lint init` MUST be a subcommand of the spec-009 Click
group. The pre-spec-009 entry-point `jss-lint <PATHS>` and the
spec-009 `jss-lint explain` MUST continue to work unchanged.

## C-2 Generated TOML — top-level shape

The first non-comment line MUST be `journal = "jss"` (or the
journal selected by an existing `.jss-lint.toml` if running
under `--force`; for a fresh `init`, always `"jss"`).

The next block MUST be the `ignore_rules` array (possibly
empty when no rules are suppressed). No other top-level keys
are emitted in this spec.

## C-3 Generated TOML — `ignore_rules` shape

`ignore_rules` MUST be a multi-line array. Each element MUST
be preceded by exactly one `# <rule-id>: ...` comment line.
The comment includes the rule id, the precision value
(formatted to two decimal places), and the threshold.

Order: ascending by `rule_id`.

## C-4 Determinism

For the same `(source-file-set, db-snapshot, threshold)`, two
`init` invocations MUST produce byte-identical output —
generated TOML AND printed summary AND stderr notes.

The "auto-generated on YYYY-MM-DD" comment line is the only
ambient-time data; it is stable within a single calendar day
and is omitted from the byte-equality test (the test compares
the body, not the date line). Date is rendered in
ISO-8601 calendar form.

## C-5 Refusal

When `.jss-lint.toml` exists at the target directory and
`--force` is NOT set, the CLI MUST:
- Exit 2.
- Write `jss-lint: refusing to overwrite <abspath>; pass
  --force to overwrite` to stderr.
- NOT touch the existing file (byte-equality before and
  after).

## C-6 `--dry-run`

`--dry-run` MUST:
- Print the proposed TOML to stdout.
- Print the summary table to stderr.
- NOT create or modify any file under the target directory.

`--dry-run` is independent of `--force` (both can be set
simultaneously; `--force` is a no-op when `--dry-run` is
also set).

## C-7 Threshold validation

`--threshold T` MUST validate `0 <= T <= 1`. Out-of-range
input causes exit 2 with stderr `--threshold must be between
0 and 1; got <T>`.

## C-8 Atomic write

The actual file write (when not `--dry-run`) MUST go through
the same tempfile + `os.replace` pattern as spec 008. A
crash mid-write MUST NOT leave a partial `.jss-lint.toml` on
disk.

## C-9 Missing precision DB

When `eval/precision-history.db` does not exist:
- `init` proceeds.
- The generated TOML's `ignore_rules` array is empty.
- The summary's stderr block contains the literal:
  `note: no precision data available; suppressing nothing automatically`.
- Exit code 0.

## C-10 Untriaged rules

When the DB exists but lacks a row for a rule that has
violations:
- The rule is classified `untriaged`.
- It is NOT added to `ignore_rules`.
- The summary lists it under an `untriaged` heading.

## C-11 Summary table totals

The summary's header block MUST include both:
- `total violations: <N>` (sum of all violation counts).
- `unique line violations: <M>` (count of distinct
  `(file, line)` pairs).

## C-12 Backwards compatibility

The generated `.jss-lint.toml` MUST be parseable by every
pre-spec-010 release of the CLI. The schema is a subset of
the established spec-001 config schema; this contract is
verified by a test that parses the generated TOML with the
existing config loader.

## C-13 No network calls

`init` MUST NOT make any network requests. The spec-007
`guide_url` values are not fetched; the precision DB is
read locally; and no remote starter config is ever
retrieved.
