# Data Model: Multi-file Projects

**Phase**: 1
**Spec**: [spec.md](spec.md)
**Plan**: [plan.md](plan.md)

## 1. `ParsedProject`

Public type, lives in `texlint.api`:

```python
@dataclass(frozen=True)
class ParsedProject:
    root: Path
    documents: tuple[ParsedDocument, ...]
    tree: dict[Path, tuple[Path, ...]]   # file -> direct refs
```

| Field        | Type                                  | Semantics                                                                |
| ------------ | ------------------------------------- | ------------------------------------------------------------------------ |
| `root`       | `Path`                                | The single root file the user invoked the linter against.                |
| `documents`  | `tuple[ParsedDocument, ...]`          | All reachable parsed files, in resolution order (depth-first).            |
| `tree`       | `dict[Path, tuple[Path, ...]]`        | Adjacency list: each file → its direct references via the four macros.   |

`ParsedDocument` is the existing union from spec 005:
`ParsedTexFile | ParsedRmdFile | ParsedBibFile`.

`tree` is built during resolution; the keys cover every file in
`documents`. A leaf file's value is the empty tuple.

## 2. `Rule.check_project` extension

Optional field on `texlint.api.Rule`:

```python
@dataclass(frozen=True)
class Rule:
    # ... existing fields ...
    check_project: Callable[[ParsedProject], Iterable[Violation]] | None = None
```

Backwards compatibility: every existing rule omits the field;
the default is `None`.

## 3. Engine dispatch

```python
def run(cfg: ToolConfig,
        target: ParsedDocument | ParsedProject,
        journal: JournalModule) -> ComplianceReport:
    violations: list[Violation] = []

    if isinstance(target, ParsedProject):
        for rule in journal.rules:
            if rule.check_project is not None:
                violations.extend(rule.check_project(target))
            else:
                for doc in target.documents:
                    violations.extend(rule.check(doc))
    else:
        for rule in journal.rules:
            violations.extend(rule.check(target))

    return ComplianceReport(...)
```

A rule with both `check` and `check_project` set runs both.

## 4. `core/resolver.py::resolve` signature

```python
def resolve(
    root: Path,
    *,
    texinputs: tuple[str, ...] = ...,    # default: split os.environ["TEXINPUTS"]
    bibinputs: tuple[str, ...] = ...,
) -> ParsedProject: ...
```

Pure function: same `(root, texinputs, bibinputs, filesystem
state)` produces the same `ParsedProject`.

The resolver internally:
1. Parses `root` via `parse_document`.
2. Walks the AST for the four macro names.
3. Resolves each reference via path-search (research §2).
4. Recurses; tracks the visit stack for cycle detection.
5. On cycle: emits `JSS-PROJECT-001` on the visiting file.
6. On missing reference: emits `JSS-PROJECT-002` on the
   visiting file.

Both rules' violations live on the parsed document of the
file that *contained* the reference (i.e., `Violation.file`
is the parent, not the missing child).

## 5. `JSS-PROJECT-001` (cycle)

| Field             | Value                                                             |
| ----------------- | ----------------------------------------------------------------- |
| `rule_id`         | `"JSS-PROJECT-001"`                                               |
| `category`        | `"project"` (new tool-side category)                              |
| `severity`        | `Severity.ERROR`                                                  |
| `guide_section`   | `"internal"` (sentinel per spec 007)                              |
| `guide_url`       | `None`                                                            |
| `message`         | `f"cycle detected: {a} -> {b} -> {a}"`                            |
| `fix`             | `None` (no auto-fix)                                              |

## 6. `JSS-PROJECT-002` (missing reference)

| Field             | Value                                                             |
| ----------------- | ----------------------------------------------------------------- |
| `rule_id`         | `"JSS-PROJECT-002"`                                               |
| `category`        | `"project"`                                                       |
| `severity`        | `Severity.ERROR`                                                  |
| `guide_section`   | `"internal"`                                                      |
| `guide_url`       | `None`                                                            |
| `message`         | `f"referenced file not found: {name}"`                            |
| `fix`             | `None`                                                            |

## 7. `--no-resolve` flag

CLI surface:

```text
Options:
  --no-resolve     disable auto-resolve; lint only the file you pass.
```

When set, the CLI builds a `ParsedDocument` directly via the
existing `parse_document` and bypasses the resolver. The engine
dispatches the `ParsedDocument` branch (no `check_project` calls).

## 8. Out of scope

| Item                                            | Reason                                                                  |
| ----------------------------------------------- | ----------------------------------------------------------------------- |
| `\subimport` (subfiles package)                 | Out per Clarifications §3.                                               |
| Per-file `.jss-lint.toml` precedence            | Out per Clarifications §4.                                               |
| `kpsewhich` shell-out for path search           | Out per research §2.                                                     |
| Migrating other cross-file-relevant rules       | Out — incremental; only abbreviations migrates in this spec.             |
| Windows path-search semantics                   | Out — POSIX-only per spec 005.                                            |
