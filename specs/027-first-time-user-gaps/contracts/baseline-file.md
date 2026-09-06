# Contract: Baseline file

**Plan**: [../plan.md](../plan.md) §5.3, §5.4, §5.7
**Data model**: [../data-model.md](../data-model.md) §2

## C-1 File shape

`.jss-lint-baseline.json` (any name; the path is given by `--baseline` or
the TOML `baseline` key):

```json
{
  "entries": [
    {
      "count": 1,
      "message": "BibTeX entries include a doi field where one is available (advisory)",
      "path": "refs.bib",
      "rule_id": "JSS-REFS-003",
      "suggestion": "Add a doi field to entry 'koller2023' if one is available."
    }
  ],
  "journal": "jss",
  "ruleset_version": "2026-09-15",
  "schema_version": 1,
  "tool_version": "1.2.0"
}
```

| Field | Type | Notes |
|---|---|---|
| `schema_version` | int | MUST be `1`; anything else → exit 2 |
| `tool_version` | string | informational |
| `ruleset_version` | string or null | stamped from the catalogue; mismatch → stderr note, not an error |
| `journal` | string | MUST equal the active journal id; mismatch → exit 2 |
| `entries[]` | array | sorted by `(path, rule_id, message, suggestion)`; each `count ≥ 1` |

No timestamp and no host-specific field, so `--update-baseline` output is
byte-identical across engines and across runs on identical input.
Serialisation: `json.dumps(indent=2, sort_keys=True) + "\n"`; Rust writes
through `json_output::write_value` for byte equality (`ensure_ascii`).

## C-2 Key

An entry identifies findings by

```
(rule_id, path, message, suggestion)
```

`line` and `column` deliberately do not participate. `suggestion` is
`""` when the violation carries none. Rationale and measurements:
plan §5.7.

## C-3 Path relativisation

`path` is posix-form, relative to the **baseline file's directory**,
computed at the CLI layer from the canonical (resolved) path of each
parsed file. Auto-resolve (absolute canonical `Violation.file`) and
`--no-resolve` (literal argument) therefore produce the same `path`.
Files outside the baseline directory get `../` prefixes. On Windows the
`\\?\` prefix is stripped and separators are `/`.

## C-4 Matching semantics

1. Entries form a multiset keyed by C-2 with `count` remaining.
2. Findings are offered to the matcher in `Violation.sort_key` order
   within each rule's list, after inline suppression, before category
   bookkeeping.
3. A finding whose key has `remaining > 0` is hidden and the count is
   decremented; otherwise it is reported.
4. After the run: `matched` = hidden findings; `stale` = remaining counts
   for rules that ran; `unevaluated` = remaining counts for rules that
   did not run (in `--ignore-rules`, below `--min-confidence`,
   format-skipped, unknown/retired).
5. `JSS-PARSE-000` is never matched and never written.

## C-5 `--update-baseline`

Runs the lint with no suppressor, builds entries from every reported
violation except `JSS-PARSE-000`, writes atomically (tempfile +
`os.replace`, §VII), prints `jss-lint: wrote N baseline entries to
<path>` on stderr, exits 0 (2 on an error-severity parse failure).
Re-running it prunes stale entries and adds new ones; it is the only
pruning mechanism.

## C-6 Reporting

Terminal (author and reviewer, after the footer):

```
Baseline: 12 findings hidden by .jss-lint-baseline.json (3 stale, 0 unevaluated)
```

with ` — written for rule set 2026-09-15, current 2026-11-02; run
--update-baseline` appended when the stamped date differs from the
tool's. JSON: `json-output-1.2.md` C-2. HTML: one `<p class="note">`.
SARIF: hidden findings are simply absent.

## C-7 Interaction with other options

| Option | Behaviour |
|---|---|
| `--fix`, `--dry-run`, `--apply` | Operate on the visible report only; run without `--baseline` to fix accepted findings. |
| `--ignore-rules`, `--min-confidence`, `--fail-on` | Applied first; affected entries count as `unevaluated`. |
| `--mode reviewer` | `compliance_percentage` and category status are post-suppression, like inline ignores. |
| `jss-lint diff` | Unchanged; diffing a baselined report against an unbaselined one shows hidden findings as resolved. |
| Inline `% jss-lint: ignore` | Checked first; never consumes a baseline count. |
| GitHub Action | `baseline:` input forwards `--baseline`. |

## C-8 Documented limits

1. **Same-shape masking.** Findings with identical keys are
   interchangeable: fix one and add another of the same shape in the same
   file and the new one is hidden while the count holds. After item S this
   is confined to `JSS-WIDTH-001` (generic by decision, plan §5A) and to
   rules whose quoted token inherently repeats (`MARKUP-001/003`,
   `OPER-001/004`, `CODE-002`), plus the deferred tail of
   `suggestions.md` C-4.
2. **Renames.** Moving or renaming a file invalidates its entries; run
   `--update-baseline` afterwards.
3. **Rule-set bumps.** A minor release may reword a message or
   suggestion; the rule-set date bumps, that rule's entries go stale and
   its findings reappear as new; `--update-baseline` is expected.
   `docs/versions.md` states this.

## C-9 Bindings

Not exposed by the WASM, PyO3, or R bindings in 1.2.0 (documented in
`rust/README.md`); the matcher is pure and in core so an in-memory
variant is a follow-up.

## C-10 Parity

`rust/jsslint-cli/tests/baseline_parity.rs`: identical `--update-baseline`
bytes; identical stdout and exit code for terminal, json, sarif with
`--baseline`; drift, TOML key, subdirectory, and journal-mismatch cases.
Only the error text for a malformed file may differ (exit code 2 is
guaranteed), as for `diff`.
