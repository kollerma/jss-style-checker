# Contract: SARIF 2.1.0 Output

**Phase**: 1 (Design & Contracts)
**Spec**: [../spec.md](../spec.md)
**Plan**: [../plan.md](../plan.md)

This contract documents the byte-level invariants that
`src/texlint/output/sarif.py::render(report, cfg)` MUST satisfy.
Every invariant has a corresponding test in
`tests/unit/output/test_sarif.py`.

## C-1 Top-level shape

The output is a single JSON object with exactly these top-level keys
(in the alphabetical order produced by `sort_keys=True`):

- `$schema` — string, equal to
  `"https://json.schemastore.org/sarif-2.1.0.json"`.
- `runs` — array of length 1.
- `version` — string, equal to `"2.1.0"`.

No other top-level keys are present.

## C-2 Single-run constraint

`runs.length == 1` always. The renderer never paginates across
multiple runs.

`runs[0]` has exactly these keys:
- `invocations` — array of length 1.
- `results` — array (possibly empty).
- `tool` — object.

## C-3 Tool driver

`runs[0].tool.driver` has exactly these keys:
- `informationUri` — string, the project URL constant.
- `name` — string, equal to `"jss-lint"`.
- `rules` — array. One entry per catalogue rule (see C-4).
- `version` — string, equal to `texlint.__version__`.

## C-4 Rule descriptors

`runs[0].tool.driver.rules` contains one entry per rule in
`texlint.journals._catalogue_data.RULES`, sorted by `id`. Each
entry has exactly these keys:

- `defaultConfiguration` — object with one key, `level` (one of
  `"error"`, `"warning"`, `"note"`).
- `fullDescription` — object with one key, `text`.
- `helpUri` — string, present iff the rule has a non-`None`
  `help_url`.
- `id` — string, equal to `Rule.rule_id`.
- `name` — string.
- `properties` — object with exactly one key, `tags`.
- `shortDescription` — object with one key, `text`.

`properties.tags` is a single-element array of strings: the rule's
`category` value (e.g., `["markup"]`).

## C-5 Result objects

Each entry of `runs[0].results` corresponds to a non-suppressed,
non-`JSS-PARSE-000` violation. Entries are sorted by
`(file, line, column, rule_id)` ascending.

Each entry has exactly these keys:
- `level` — one of `"error"`, `"warning"`, `"note"`.
- `locations` — array of length 1.
- `message` — object with one key, `text`.
- `ruleId` — string.

`locations[0].physicalLocation` has exactly two keys:
- `artifactLocation` — object with one key, `uri`.
- `region` — object.

`region` has the keys:
- `startLine` — int ≥ 1.
- `startColumn` — int ≥ 1.
- `endLine` — int ≥ `startLine`, present iff
  `Violation.end_line` is non-`None`.
- `endColumn` — int ≥ 1, present iff `Violation.end_column` is
  non-`None`.

When `endLine == startLine` and `endColumn == startColumn`, both
are still emitted (do NOT collapse).

## C-6 Notification objects

Each entry of `runs[0].invocations[0].toolExecutionNotifications`
corresponds to a `JSS-PARSE-000` violation. Entries are sorted by
`(artifactLocation.uri, line)` ascending.

Each entry has exactly these keys:
- `descriptor` — object with one key, `id`, equal to
  `"JSS-PARSE-000"`.
- `level` — equal to `"error"`.
- `locations` — array of length 1, same shape as C-5 (region may
  omit `startLine` if the parser had no line for the failure).
- `message` — object with one key, `text`.

`runs[0].invocations[0].executionSuccessful` is `true` whenever
the renderer is reached at all (the linter completed without an
internal exception). Parse failures do NOT flip this — they
appear in `toolExecutionNotifications`, not as a tool crash.

## C-7 Determinism

Two invocations of `render(report, cfg)` against equal `report`
and `cfg` MUST produce byte-identical output:
- Keys are alphabetised (`sort_keys=True`).
- Indentation is two spaces (`indent=2`).
- Trailing newline at end of file.
- No `$comment` keys, no UUIDs, no time stamps, no host names,
  no PIDs.
- `results[]` and `toolExecutionNotifications[]` are
  pre-sorted before `json.dumps` so that array-element order
  is stable across Python implementations.

The contract test runs `render` twice and asserts byte-equality.

## C-8 Schema conformance

`render(report, cfg)` output MUST validate against the SARIF
2.1.0 JSON schema (vendored at
`tests/fixtures/sarif-2.1.0-schema.json`). The contract test
runs `Draft202012Validator(schema).validate(doc)` against every
golden fixture and the live output for each parametrised
scenario.

## C-9 `--ignore-rules` interaction

A violation with `rule_id` in `cfg.ignore_rules` MUST NOT
appear in `runs[0].results`. It MUST NOT appear under
`runs[0].results[].suppressions[]` either (the field is
never populated). The rule's descriptor MUST still appear in
`runs[0].tool.driver.rules`.

`JSS-PARSE-000` is a special case: even if it appears in
`cfg.ignore_rules`, it MUST still appear in
`runs[0].invocations[0].toolExecutionNotifications` (per spec
FR-008).

## C-10 Source-root path normalisation

For each violation file path:
- If the file lives under `cfg.source_root`, the URI is
  `Path.relative_to(source_root).as_posix()`.
- Otherwise, the URI is
  `Path(os.path.relpath(file, source_root)).as_posix()` —
  may contain `..` segments.
- The URI never contains a drive letter, never starts with `/`,
  and never contains backslashes.

## C-11 No `fixes[]` in this spec

`runs[0].results[].fixes[]` MUST NOT be emitted in the spec-006
implementation. Spec 008 owns the `fixes[]` projection and adds
its own contract entry.

## C-12 Existing JSON output unchanged

This contract makes one cross-spec assertion: the byte shape of
`--output json` MUST be identical before and after spec 006
lands. The regression test compares the live `--output json`
output against the existing golden at
`tests/fixtures/json_output/golden.json` (or equivalent path
established by spec 001's contract).
