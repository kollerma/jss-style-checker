# Data Model: JSS-guide Rule Mapping

**Phase**: 1 (Design & Contracts)
**Spec**: [spec.md](spec.md)
**Plan**: [plan.md](plan.md)

## 1. `Rule` dataclass extension

Two additive fields on the existing public `texlint.api.Rule`
dataclass. No other fields change.

| Field           | Type            | Default       | Semantics                                                                  |
| --------------- | --------------- | ------------- | -------------------------------------------------------------------------- |
| `guide_section` | `str`           | (required)    | Human-readable section label, e.g., `"§3.2 Citations"` or `"internal"`.    |
| `guide_url`     | `str \| None`   | `None`        | Absolute URL into the public JSS author guide; `None` for sentinel rules.  |

**Validity** (enforced by the catalogue contract test):
- `guide_section` is non-empty for every rule.
- For citable categories (`markup`, `style`, `naming`, `preamble`,
  `bibliography`, `width`):
  - `guide_section != "internal"`.
  - `guide_url` is non-`None`, starts with `https://`.
  - `guide_section` appears as a key in `index.json::sections`.
  - `guide_url == index.json::sections[guide_section]`.
- For sentinel categories (`internal`, `parse`):
  - `guide_section == "internal"`.
  - `guide_url is None`.

`Rule.help_url`, if present from spec 006, is removed in this spec
(research §7).

## 2. Citable category set

A single frozen set lives in `_catalogue_data.py`:

```python
CITABLE_CATEGORIES = frozenset({
    "markup", "style", "naming",
    "preamble", "bibliography", "width",
})
```

Membership in this set determines whether a rule is subject to
the "real URL" contract or the sentinel exception. The set is
exported for use by the catalogue contract test.

## 3. `docs/jss-guide/index.json`

```json
{
  "sections": {
    "§<n>[.<m>] <Title>": "https://...",
    ...
  }
}
```

Top-level shape:

| Key        | Type                  | Semantics                                                  |
| ---------- | --------------------- | ---------------------------------------------------------- |
| `sections` | `dict[str, str]`      | Section label → absolute URL.                              |

Constraints:
- Every value is an absolute `https://` URL.
- Every key is the same string used in `Rule.guide_section` for
  rules citing this section.
- Order is preserved on serialise (Python ≥3.7 dict semantics);
  no in-spec test asserts order, but contributors are encouraged
  to sort by section number.

## 4. `_guide_index.py` loader

A small module under `src/texlint/journals/jss/_guide_index.py`:

```python
@functools.cache
def load_guide_index() -> dict[str, str]:
    ...
```

Behaviour:
- Reads `docs/jss-guide/index.json` from the repo root via
  `importlib.resources` (or a `Path(__file__)`-relative fall-
  back if the file is shipped outside the package — TBD by
  the loader's first caller).
- Returns the `sections` dict.
- Cached for the process lifetime; if the file is malformed
  the load raises a typed error which the caller (catalogue
  contract test, SARIF renderer, HTML renderer) handles.

The loader is the *only* code path that reads `index.json`.

## 5. JSON output extension (per violation)

The existing per-violation JSON object gains exactly two keys:

| Key             | Type            | Source                        |
| --------------- | --------------- | ----------------------------- |
| `guide_section` | `str`           | `Rule.guide_section`          |
| `guide_url`     | `str \| null`   | `Rule.guide_url` (`null` for sentinels) |

Existing keys (`file`, `line`, `column`, `rule_id`, `severity`,
`message`, `category`, `fix`, …) retain their order under
`sort_keys=True`.

## 6. SARIF output extensions

Two changes to spec 006's `tool.driver.rules[]` entries:

| SARIF field                       | Spec-006 source     | Spec-007 source                                                                                        |
| --------------------------------- | ------------------- | ------------------------------------------------------------------------------------------------------ |
| `shortDescription.text`           | `Rule.title`        | `f"{Rule.title} ({Rule.guide_section})"` for citable rules; `Rule.title` for sentinel rules.            |
| `helpUri`                         | `Rule.help_url`     | `Rule.guide_url` (when non-`None`); omitted for sentinel rules.                                          |

`tool.driver.rules[].properties.tags` is unchanged
(`[<category>]`).

`runs[0].results[]` is unchanged — citation lives at the rule
descriptor, not the result.

## 7. HTML output extensions

The existing per-violation `<tr>` row gains a hyperlink in the
"section" cell:

| Spec-006 cell                | Spec-007 cell (citable rules)                                    | Sentinel rules                       |
| ---------------------------- | ----------------------------------------------------------------- | ------------------------------------ |
| n/a (no section column)      | `<a href="<guide_url>">§<section>"</a>`                           | plain text `internal`                |

A new column header is added to the table; existing columns are
unchanged.

## 8. Terminal output extension

The existing terminal violation line gains a parenthetical
suffix for citable rules:

| Existing line                                       | After spec 007                                                            |
| --------------------------------------------------- | ------------------------------------------------------------------------- |
| `JSS-CITE-002 line 42 col 7: prefer \citet{}`       | `JSS-CITE-002 line 42 col 7: prefer \citet{} (see §3.2 Citations)`         |
| `JSS-PARSE-000 line 1 col 1: parser failed`         | `JSS-PARSE-000 line 1 col 1: parser failed`                                |

## 9. Contract tests

Two new tests in `tests/unit/test_catalogue.py`:

- `test_every_rule_cites_guide` — iterates `_catalogue_data.RULES`,
  asserts FR-002 / FR-003.
- `test_guide_urls_resolve_through_index` — for every citable
  rule, asserts `guide_section ∈ index.json::sections` and
  `guide_url == index.json::sections[guide_section]`.

Failure messages name the rule id and the violated invariant.

## 10. Out of scope

| Item                                            | Reason                                                                  |
| ----------------------------------------------- | ----------------------------------------------------------------------- |
| Multi-section citations on a single rule        | Out per spec Clarifications (research §3).                              |
| `index.json` JSON schema enforcement            | Out — contract tests are the validation layer; schema is overkill here. |
| Live mirror of the JSS guide content            | Out per research §2.                                                    |
| Per-violation `helpUri` overrides               | Out — rule-level `helpUri` is sufficient for the surfaces we target.    |
