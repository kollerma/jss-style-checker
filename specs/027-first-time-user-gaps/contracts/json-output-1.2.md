# Contract: JSON output additions (1.2.0)

**Plan**: [../plan.md](../plan.md) §5.4, §7.3
**Extends**: `specs/001-linter-foundation/contracts/json-output.md`
(additive-only within the 1.x major, per its stability promise).

> The spec-001 document is stale: it does not document the per-violation
> `guide_section`, `guide_url`, `confidence` keys (spec 007 and the
> confidence-tier follow-up) nor the top-level `skipped_rules` key (spec
> 005). Refreshing it to the shape actually emitted is part of this
> release; this contract lists only what 1.2.0 adds.

## C-1 Top-level keys

After 1.2.0 the top-level object always carries exactly these keys:

```
tool_version, journal_id, compliance_percentage, categories, violations,
skipped_rules, baseline, rule_set, coverage
```

All nine are always present. `sort_keys=True` ordering applies as before.

## C-2 `baseline`

`null` when no baseline was applied; otherwise:

```json
"baseline": {
  "matched": 12,
  "path": ".jss-lint-baseline.json",
  "ruleset_version": "2026-09-15",
  "stale": 3,
  "unevaluated": 0
}
```

`path` is the string the user supplied (flag or TOML), not resolved.
Baselined violations are absent from `violations` and excluded from
category bookkeeping and `compliance_percentage`.

## C-3 `rule_set`

```json
"rule_set": {
  "fingerprint": "sha256:…",
  "guide_source": "jss.cls 3.3 (2021-05-23)",
  "recall": {
    "corpus_hash": "70951d5371df0734",
    "fn": 380,
    "min_plants": 10,
    "percent": 81,
    "run_timestamp": "2026-07-19T10:30:02Z",
    "tp": 1587
  },
  "version": "2026-09-15"
}
```

For a journal without metadata (e.g. the `stub` fixture): `"version"`,
`"fingerprint"`, `"guide_source"`, and `"recall"` are `null`.

## C-4 `coverage`

```json
"coverage": {
  "counts": {"checked": 71, "not_checked": 9, "out_of_scope": 34, "partial": 6},
  "items": [
    {"id": "SG-020", "reason": "…", "section": "#how-should-abbrevations-be-formatted",
     "source": "style_guide", "status": "not_checked"}
  ]
}
```

`items` lists only `partial` and `not_checked` directives, sorted by
`(status, id)`, without the provision text (identical for every report;
`jss-lint coverage --format json` carries it). `null` for a journal
without coverage data.

## C-5 Per-category `recall`

Each object in `categories` gains:

```json
"recall": {"fn": 20, "percent": 78, "state": "measured", "tp": 70}
```

`state` ∈ `measured | limited | unmeasured`; `percent` is an integer
(half-up, see data-model §3.1) and `null` unless `measured`. With no
journal data every category carries
`{"fn": 0, "percent": null, "state": "unmeasured", "tp": 0}`. The
synthetic `parse` category carries the same unmeasured shape.

## C-6 Per-violation `suggestion` (item S)

No shape change. For the ten rules in `suggestions.md` the string content
now embeds a stable identifier; consumers that keyed on suggestion text
will see new values once (rule-set bump, see `baseline-file.md` C-8).

## C-7 SARIF

Rule descriptors in `runs[0].tool.driver.rules[]` gain
`properties.confidence` (`"high"|"medium"|"low"`) and `properties.recall`
(same shape as C-5). Baselined results are absent from `results[]`;
SARIF `baselineState` is not emitted.

## C-8 Determinism

Unchanged mechanism: `json.dumps(indent=2, sort_keys=True)`; all new
numbers are integers; array orders are the journal's declared category
order (categories) and `(status, id)` (coverage items).

## C-9 Consumers' contract

- Existing consumers see three new top-level keys and one new
  per-category key; nothing existing is renamed or removed.
- `jss-lint diff` validates only the spec-001 required keys and keeps
  diffing 1.1.x against 1.2.x reports.
- `tests/integration/test_cli_json.py` (exact key-set assertion) and the
  paper's `generate_paper_stats --check` (reads `categories` only) are
  updated/verified in the same PR.
