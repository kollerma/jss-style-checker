# Data Model: `jss-lint diff`

**Phase**: 1
**Spec**: [spec.md](spec.md)
**Plan**: [plan.md](plan.md)

## 1. `DiffReport`

```python
@dataclass(frozen=True)
class DiffReport:
    fixed: tuple[Violation, ...]
    introduced: tuple[Violation, ...]
    unchanged: tuple[Violation, ...]
```

Each tuple element is the spec-001 violation object (loaded
from JSON via the existing schema). Order:
- `fixed`: sort by `(file, line, rule_id)` ascending.
- `introduced`: sort by `(file, line, rule_id)` ascending.
- `unchanged`: sort by `(file, line, rule_id)` ascending,
  using NEW's values for `line` and `message` (research §7).

## 2. Identity tuple

Default:

```python
def _identity(v: dict, *, drop_line: bool) -> tuple:
    if drop_line:
        return (v["rule_id"], v["file"], v["message"])
    return (v["rule_id"], v["file"], v["line"], v["message"])
```

`severity` and `column` are intentionally absent
(research §1).

## 3. `compare` signature

```python
def compare(
    old: list[dict],
    new: list[dict],
    *,
    ignore_line_drift: bool = False,
    rule_renames: dict[str, str] | None = None,
) -> DiffReport:
    ...
```

Pure function. No I/O.

## 4. `rule-renames.json` shape

```json
{
  "renames": {
    "JSS-MARKUP-005": "JSS-MARKUP-005-A",
    "JSS-CITE-007":   "JSS-CITE-007-NEW"
  },
  "_provenance": {
    "JSS-MARKUP-005": "spec-018: split into 005-A and 005-B",
    "JSS-CITE-007":   "spec-019: renamed to disambiguate"
  }
}
```

The `renames` dict drives behaviour. `_provenance` is a
peer audit trail (one entry per rename, one PR cited per
entry). Schema-wise, `_provenance` keys MUST equal
`renames` keys; a contract test enforces this.

## 5. CLI surface

```text
Usage: jss-lint diff [OPTIONS] OLD.json NEW.json

Options:
  --format [terminal|markdown|json]
                                Output format (default: terminal).
  --ignore-line-drift           Drop `line` from the identity tuple.
  -h, --help                    Show this message and exit.
```

## 6. Exit codes

| Outcome                                                      | Code |
| ------------------------------------------------------------ | ---- |
| `len(introduced) == 0`                                       | 0    |
| `len(introduced) > 0`                                        | 1    |
| Usage error (missing file, schema mismatch, unknown format)  | 2    |

## 7. Renderer surfaces

| Format     | Implementation                                                 |
| ---------- | -------------------------------------------------------------- |
| `terminal` | Reuse spec-001 `output/terminal.py::render` with reviewer mode; emit three sub-blocks (fixed, introduced, unchanged) plus a header line with counts. |
| `markdown` | Small Jinja2 template in `output/templates/diff.md.j2`.        |
| `json`     | `json.dumps(asdict(diff_report), sort_keys=True, indent=2)`.    |

The terminal renderer is the reuse path; markdown and JSON
have small new code paths inside `diff.py`.

## 8. JSON output shape

```json
{
  "summary": {
    "fixed": 9,
    "introduced": 2,
    "unchanged": 5
  },
  "fixed": [<violation>, ...],
  "introduced": [<violation>, ...],
  "unchanged": [<violation>, ...]
}
```

Each `<violation>` matches the spec-001 schema. `sort_keys=True`
ensures deterministic key order.

## 9. Out of scope

| Item                                            | Reason                                                                  |
| ----------------------------------------------- | ----------------------------------------------------------------------- |
| Three-way (`--baseline`)                        | Out per Clarifications §4.                                               |
| Identity tuple including `column`               | Out per Clarifications §1.                                               |
| Network fetch of rule-rename map                | Out per research §2.                                                     |
| Diffing SARIF output directly                   | Out — the diff consumes the spec-001 JSON shape; SARIF would need its own diff command. |
| Diffing across journals                         | Out — a `--journal` change is a different lint configuration.            |
