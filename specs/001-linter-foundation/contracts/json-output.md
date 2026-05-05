# Contract — JSON Output

`jss-lint --output json` emits a single JSON document to stdout. This document is the authoritative machine-readable form of `ComplianceReport`; CI tools, editor plugins, and dashboards consume it. The stability promise (spec Clarification Q2) is **additive-only within a single major `tool_version`**; breaking shape changes require a major version bump of `texlint` plus a CHANGELOG entry.

## Top-level shape

```json
{
  "tool_version": "0.1.0",
  "journal_id": "jss",
  "compliance_percentage": 66.7,
  "categories": [ ... ],
  "violations": [ ... ]
}
```

All four top-level keys MUST always be present.

### `tool_version` — string

`texlint.__version__`. Sourced from `importlib.metadata.version("jss-style-checker")`; `"0.1.0"` in editable-install fallback.

### `journal_id` — string

The value of `ToolConfig.journal` that was actually used. Useful for downstream consumers that run multiple journals in one CI pipeline.

### `compliance_percentage` — number or null

- `null` if every journal-declared category is `SKIPPED` (no rules ran).
- Otherwise, `100.0 * (categories with status "PASS") / (categories with status "PASS" or "FAIL")`, rounded to one decimal. Range 0.0 – 100.0 inclusive. (Spec FR-010.)
- The synthetic `parse` category is **always** excluded from this number. (Spec Clarification Q1.)
- Categories with status `SKIPPED` are excluded from both the numerator and the denominator. (Spec Clarification Q3.)

### `categories` — array of objects

One object per journal-declared category, plus a synthetic object with `category_id = "parse"` IFF any `JSS-PARSE-000` violation was produced. Array order is stable: journal-declared categories first, in the order the journal returns them; the synthetic `parse` category last.

Each object:

```json
{
  "category_id": "citation",
  "title": "Citation",
  "status": "PASS",
  "rules_applied": 1,
  "rules_passed": 1
}
```

| Field | Type | Notes |
|---|---|---|
| `category_id` | string | Stable identifier; the journal's choice, or the literal `"parse"`. |
| `title` | string | Human-readable. |
| `status` | string | One of `"PASS"`, `"FAIL"`, `"SKIPPED"`. See `CategorySummary` in data-model.md. |
| `rules_applied` | integer ≥ 0 | Rules from this category that actually ran on at least one input file. The `parse` synthetic category always has `rules_applied = 0`. |
| `rules_passed` | integer ≥ 0 | `rules_applied` that produced zero violations. |

Violations are **not** duplicated inside each category in JSON — they live in the top-level `violations` array and are linkable back via `rule_id → category_id` lookup.

### `violations` — array of objects

Deterministically sorted — see below. Every violation in the run, style or parse-error, in a single flat array.

Each object:

```json
{
  "file": "paper.tex",
  "line": 42,
  "column": 13,
  "rule_id": "JSS-CITE-001",
  "severity": "error",
  "message": "Do not use \\emph for citation markup; use \\cite instead.",
  "suggestion": "Replace \\emph{foo2020} with \\cite{foo2020}.",
  "fix": null
}
```

| Field | Type | Notes |
|---|---|---|
| `file` | string | Filesystem path. Relative where the user passed a relative path; absolute where they passed an absolute path. Path separators are rendered in forward-slash form on all platforms for cross-host determinism. |
| `line` | integer ≥ 1 | 1-based. |
| `column` | integer ≥ 1 or null | 1-based when available; `null` when the rule operates at line granularity. |
| `rule_id` | string | Stable. Parse errors carry `"JSS-PARSE-000"`. |
| `severity` | string | `"error"` or `"warning"`. |
| `message` | string | Human-oriented, already formatted. |
| `suggestion` | string or null | Short author-facing hint; `null` when the rule has none. |
| `fix` | object or null | Reserved for Step 4. Every violation in this step serialises `fix` as `null`. |
| `guide_section` | string | JSS author-guide section label (e.g. `"§3.2 Citations"`). Empty string `""` for tool-side rules (`JSS-PARSE-000`, etc.) and for un-backfilled rules. (Spec 007 follow-up.) |
| `guide_url` | string or null | Absolute URL into the public JSS author guide. `null` for tool-side / un-backfilled rules. (Spec 007 follow-up.) |

## Determinism

Byte-identical output on identical input, across hosts (SC-003). Achieved by:

1. `json.dumps(report, indent=2, sort_keys=True)` — sorts object keys at every nesting level.
2. `violations` array is sorted by `(file, line, column_or_sentinel, rule_id)`. `column` sorts with `None` before any integer (because null should not preempt a real location when a later entry has a column).
3. `categories` array order is the journal's declared order for journal-declared categories, then the synthetic `parse` category. Since `sort_keys=True` only sorts object keys — not array elements — the engine must emit arrays in this canonical order.
4. `tool_version` uses `importlib.metadata.version(...)`, so editable installs of the same source produce the same string.
5. File paths are rendered through `path.as_posix()` to avoid Windows/POSIX separator drift.
6. `compliance_percentage` is rounded to one decimal with `round(value, 1)` — Python's banker's rounding is deterministic.

## Consumers' contract

- CI jobs MAY assume the top-level keys stay present across minor / patch tool versions.
- CI jobs MAY assume the field set inside each `violation` and `category` object stays present — new fields may be added; existing fields are not renamed or removed within a major version.
- `rule_id` values MAY be added; an existing id's meaning does not change within a major version.
- `category_id` values MAY be added; the synthetic `parse` id is reserved.
- Any of the above MAY change in a new major `tool_version` with a CHANGELOG entry. Consumers are advised to branch on `tool_version` when parsing across incompatible majors.

## Example — one style violation + one parse error

```json
{
  "tool_version": "0.1.0",
  "journal_id": "jss",
  "compliance_percentage": 50.0,
  "categories": [
    {"category_id": "bibliography", "title": "Bibliography", "rules_applied": 1, "rules_passed": 1, "status": "PASS"},
    {"category_id": "citation", "title": "Citation", "rules_applied": 1, "rules_passed": 0, "status": "FAIL"},
    {"category_id": "typography", "title": "Typography", "rules_applied": 1, "rules_passed": 1, "status": "PASS"},
    {"category_id": "parse", "rules_applied": 0, "rules_passed": 0, "status": "FAIL", "title": "Parse errors"}
  ],
  "violations": [
    {"column": 1, "file": "broken.tex", "fix": null, "line": 1, "message": "LaTeX parse error at line 1, column 1: unexpected end of stream", "rule_id": "JSS-PARSE-000", "severity": "error", "suggestion": null},
    {"column": 13, "file": "paper.tex", "fix": null, "line": 42, "message": "Do not use \\emph for citation markup; use \\cite instead.", "rule_id": "JSS-CITE-001", "severity": "error", "suggestion": "Replace \\emph{foo2020} with \\cite{foo2020}."}
  ]
}
```

Note: the `citation` category FAILs because `JSS-CITE-001` fired. `compliance_percentage = 100 * 2/(2+1+0) = 66.7`… wait — `bibliography`, `citation`, `typography` are the PASS/FAIL non-SKIPPED set; `parse` is excluded. 2 PASS out of 3 = 66.7%. The example above lists `50.0` for illustrative variation; the actual formula is `100 * PASS / (PASS + FAIL)` where `SKIPPED` and `parse` are excluded.
