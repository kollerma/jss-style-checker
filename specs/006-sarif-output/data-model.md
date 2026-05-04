# Data Model: SARIF 2.1.0 Output

**Phase**: 1 (Design & Contracts)
**Spec**: [spec.md](spec.md)
**Plan**: [plan.md](plan.md)

This file inventories the data shapes touched by spec 006.

The SARIF document itself is **not** a public Python type — it is a
nested `dict[str, Any]` produced by `output/sarif.py::render` and
serialised with `json.dumps(..., sort_keys=True, indent=2)`. The
shape is documented here as a projection of SARIF 2.1.0; callers
who want a typed view validate against the schema fixture.

## 1. Public API extension: `ToolConfig.source_root`

One additive field on the existing `texlint.api.ToolConfig`
dataclass.

| Field         | Type   | Default              | Semantics                                                |
| ------------- | ------ | -------------------- | -------------------------------------------------------- |
| `source_root` | `Path` | `Path.cwd()` (lazy)  | Base directory for relative `artifactLocation.uri` paths |

**Construction**:

```python
@dataclass(frozen=True)
class ToolConfig:
    # ... existing fields unchanged ...
    source_root: Path = field(default_factory=Path.cwd)
```

**Validation**: none beyond existing `ToolConfig` invariants. The
field is an arbitrary `Path` at config-load time; the renderer
treats it as an opaque base for `relative_to` / `relpath`.

**Backwards compatibility**: additive — every existing call site
that constructs a `ToolConfig` (config loader, test fixtures, CLI
overrides) continues to work; the default is `Path.cwd()`, which is
the implicit behaviour today.

## 2. CLI surface extension

| Option               | Type            | Default     | Semantics                                                            |
| -------------------- | --------------- | ----------- | -------------------------------------------------------------------- |
| `--output sarif`     | `Choice` value  | n/a         | Selects the SARIF renderer (joins `terminal`, `json`, `html`).       |
| `--source-root DIR`  | `Path` (string) | CWD         | Sets `ToolConfig.source_root`. Silently accepted for other outputs.  |

`--source-root` is a flag-with-value Click option; it accepts an
existing directory. If the directory does not exist the CLI exits
with code 2 and an error on stderr, mirroring how other path-typed
flags handle invalid paths today.

## 3. SARIF document projection

Top-level shape produced by `render(report, cfg)`:

```text
{
  "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
  "version": "2.1.0",
  "runs": [
    {
      "tool": {
        "driver": {
          "name": "jss-lint",
          "version": "<package version>",
          "informationUri": "https://github.com/.../jss-style-checker",
          "rules": [<RuleDescriptor>, ...]
        }
      },
      "invocations": [
        {
          "executionSuccessful": true,
          "toolExecutionNotifications": [<Notification>, ...]
        }
      ],
      "results": [<Result>, ...]
    }
  ]
}
```

### 3a. `RuleDescriptor` projection (one per catalogue rule)

| SARIF field                                  | Source                                              | Notes                                                                  |
| -------------------------------------------- | --------------------------------------------------- | ---------------------------------------------------------------------- |
| `id`                                         | `Rule.rule_id`                                      | E.g., `"JSS-MARKUP-001"`.                                              |
| `name`                                       | `Rule.short_name` if present, else `Rule.rule_id`   | Per existing rule metadata. `short_name` is optional.                  |
| `shortDescription.text`                      | `Rule.title`                                        | One-line summary, already present on every catalogue rule.             |
| `fullDescription.text`                       | `Rule.description`                                  | Multi-line; falls back to `Rule.title` when absent.                    |
| `defaultConfiguration.level`                 | severity map (see §3c)                              | From `Rule.severity` (or `Rule.default_severity` if both fields exist).|
| `helpUri`                                    | `Rule.help_url`                                     | Optional; omitted when `None`.                                         |
| `properties.tags`                            | `[Rule.category]`                                   | Single-element list; e.g., `["markup"]`.                               |

### 3b. `Result` projection (one per `Violation` not filtered upstream)

| SARIF field                                                       | Source                                  | Notes                                                                                               |
| ----------------------------------------------------------------- | --------------------------------------- | --------------------------------------------------------------------------------------------------- |
| `ruleId`                                                          | `Violation.rule_id`                     |                                                                                                     |
| `level`                                                           | severity map (see §3c)                  |                                                                                                     |
| `message.text`                                                    | `Violation.message`                     | Verbatim — no SARIF placeholder substitution.                                                        |
| `locations[0].physicalLocation.artifactLocation.uri`              | path-relativisation (see §3d)           | POSIX-style relative path.                                                                          |
| `locations[0].physicalLocation.region.startLine`                  | `Violation.line`                        | 1-based, matches `Violation` semantics.                                                              |
| `locations[0].physicalLocation.region.startColumn`                | `Violation.column`                      | 1-based.                                                                                             |
| `locations[0].physicalLocation.region.endLine`                    | `Violation.end_line` (when present)     | Omitted when unknown; SARIF treats absence as "to end of `startLine`".                              |
| `locations[0].physicalLocation.region.endColumn`                  | `Violation.end_column` (when present)   | Omitted when unknown.                                                                                |

### 3c. Severity map

| `Severity` enum    | SARIF `level`  |
| ------------------ | -------------- |
| `Severity.ERROR`   | `"error"`      |
| `Severity.WARNING` | `"warning"`    |
| `Severity.INFO`    | `"note"`       |

Severity is the only translation layer between
`texlint.api.Severity` and SARIF; the mapping lives as a module-
level constant in `output/sarif.py`.

### 3d. Path relativisation

For each `Violation.file` (a `Path`):

```python
def _relativise(file: Path, source_root: Path) -> str:
    abs_file = file.resolve()
    abs_root = source_root.resolve()
    try:
        rel = abs_file.relative_to(abs_root)
    except ValueError:
        rel = Path(os.path.relpath(abs_file, abs_root))
    return rel.as_posix()
```

Invariants:
- Output is always a string with `/` separators.
- Output never contains drive letters or `\`.
- Output may contain `..` segments when the file is outside
  `source_root`.

### 3e. `Notification` projection (one per `JSS-PARSE-000` violation)

| SARIF field                                          | Source                                  | Notes                                                                  |
| ---------------------------------------------------- | --------------------------------------- | ---------------------------------------------------------------------- |
| `descriptor.id`                                      | `"JSS-PARSE-000"`                       | Constant.                                                              |
| `level`                                              | `"error"`                               | Constant — parse failures are always errors.                           |
| `message.text`                                       | `Violation.message`                     | The parser diagnostic text.                                            |
| `locations[0].physicalLocation.artifactLocation.uri` | path-relativisation (see §3d)           |                                                                        |
| `locations[0].physicalLocation.region.startLine`     | `Violation.line` (when present, ≥1)     | Some parse failures have no line; field omitted in that case.          |

`runs[0].invocations[0].executionSuccessful` is `true` when the
linter completed without an internal exception. Parse failures do
not flip this — they are user-facing input errors, not tool
crashes.

### 3f. `--ignore-rules` interaction

`--ignore-rules` filters `report.violations` upstream of every
renderer (existing behaviour, unchanged). The SARIF renderer:
- Emits `tool.driver.rules[]` for **every** catalogue rule, even
  ones fully ignored. The catalogue is the contract; suppression
  is per-run.
- Emits `results[]` only for **non-ignored** violations.
- Emits `toolExecutionNotifications[]` for **all**
  `JSS-PARSE-000` violations regardless of `--ignore-rules`
  (per spec FR-008).

`runs[0].results[].suppressions[]` is NEVER populated; suppressed
violations are absent, not annotated. This matches existing
`terminal` / `json` / `html` behaviour.

## 4. Testing surface (golden + schema)

| Artefact                                                | Purpose                                                                           |
| ------------------------------------------------------- | --------------------------------------------------------------------------------- |
| `tests/fixtures/sarif-2.1.0-schema.json`                | Vendored OASIS SARIF 2.1.0 schema; used by every contract test.                   |
| `tests/fixtures/sarif/golden_clean.sarif`               | Empty-results run; full `tool.driver.rules`; `executionSuccessful: true`.         |
| `tests/fixtures/sarif/golden_single_error.sarif`        | One result; severity-error → SARIF `level: error`.                                |
| `tests/fixtures/sarif/golden_multi_file.sarif`          | Three results across two files; URIs are POSIX-relative to fixture dir.           |
| `tests/fixtures/sarif/golden_parse_error.sarif`         | One notification, zero results; `executionSuccessful: true`.                      |
| `tests/unit/output/test_sarif.py`                       | Asserts byte-equality with each golden + schema-validates each.                   |

Schema validation is `jsonschema.Draft202012Validator(schema).validate(doc)`.

## 5. Out of scope (deferred)

| Item                                            | Owner                                                                     |
| ----------------------------------------------- | ------------------------------------------------------------------------- |
| `runs[0].results[].fixes[]`                     | Spec 008 (auto-fix). Adds the rendering when fix data exists.             |
| Multi-run pagination for >10 MB output          | Not planned. Eval corpus is far below the cap; revisit if a user hits it. |
| `runs[0].artifacts[]` array (per-file metadata) | Not planned. SARIF allows omission; GitHub does not require it.           |
| `taxonomies[]` for cross-tool standards         | Not planned. JSS rule categories are tool-internal (research §4).         |
| Inline `region.snippet`                         | Not planned. The CLI does not have the snippet handy at render time.       |
