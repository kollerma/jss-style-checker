# Data Model: Auto-fix

**Phase**: 1 (Design & Contracts)
**Spec**: [spec.md](spec.md)
**Plan**: [plan.md](plan.md)

## 1. `Fix` dataclass

Public type, lives in `texlint.api`:

```python
@dataclass(frozen=True)
class Fix:
    start: int
    end: int
    replacement: str
    description: str
    confidence: Literal["safe", "review"]
```

| Field         | Type                              | Semantics                                                                  |
| ------------- | --------------------------------- | -------------------------------------------------------------------------- |
| `start`       | `int`                             | 0-based byte offset, inclusive.                                            |
| `end`         | `int`                             | 0-based byte offset, exclusive. `start <= end`.                            |
| `replacement` | `str`                             | UTF-8 text to substitute. May be `""` (deletion).                          |
| `description` | `str`                             | One-line human-readable summary, e.g., `"wrap MASS in \\pkg{}"`.           |
| `confidence`  | `Literal["safe", "review"]`       | `"safe"` ⇒ engine applies in `--fix` without further gating.               |

Invariants (enforced by a small `__post_init__` if necessary):
- `start >= 0`, `end >= start`.
- `description` is non-empty.
- `confidence` is exactly one of the two literals.

Equality: structural equality via the dataclass; two `Fix`
objects with identical fields are interchangeable.

## 2. `Violation` extension

One additive optional field on the existing public dataclass:

```python
@dataclass(frozen=True)
class Violation:
    # ... existing fields ...
    fix: Fix | None = None
```

Backwards compatibility: every existing constructor call (rule
modules, tests, fixtures) continues to work; the default is
`None`.

## 3. `FixReport` (engine result)

```python
@dataclass(frozen=True)
class FixReport:
    applied: tuple[FixApplication, ...]
    skipped: tuple[FixSkip, ...]
    rejected: tuple[FixRejection, ...]

@dataclass(frozen=True)
class FixApplication:
    file: Path
    fix: Fix
    rule_id: str

@dataclass(frozen=True)
class FixSkip:
    file: Path
    fix: Fix
    rule_id: str
    reason: Literal["conflict", "rule-not-selected", "user-skipped"]

@dataclass(frozen=True)
class FixRejection:
    file: Path
    fix: Fix
    rule_id: str
    reason: Literal["regression", "permission-denied"]
```

`apply_fixes` returns `FixReport`. `cli.py` uses it to compute
the exit code (per research §8) and to format the exit summary.

## 4. Apply mode

```python
ApplyMode = Literal["write", "dry-run", "interactive"]
```

| Value           | CLI flag combination       | Behaviour                                                                |
| --------------- | -------------------------- | ------------------------------------------------------------------------ |
| `"write"`       | `--fix`                    | Write fixes to disk via tempfile + `os.replace`; re-validate.            |
| `"dry-run"`     | `--fix --dry-run`          | Print unified diff to stdout; do not write.                              |
| `"interactive"` | `--fix --apply`            | Per-fix `[y/n/a/q]` prompt; commit accepted fixes via the `"write"` path. |

`--fix-rule RULE-ID` is orthogonal to the mode and filters
the eligible fix set up-front.

## 5. `apply_fixes` signature

```python
def apply_fixes(
    report: ComplianceReport,
    document: ParsedDocument,
    *,
    mode: ApplyMode,
    rules: frozenset[str] | None,
    stdin: TextIO | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> FixReport: ...
```

| Parameter   | Purpose                                                                                |
| ----------- | -------------------------------------------------------------------------------------- |
| `report`    | The `ComplianceReport` produced by the read-only lint pass.                            |
| `document`  | The `ParsedDocument` (carries the file paths and the original bytes).                  |
| `mode`      | `"write"` / `"dry-run"` / `"interactive"`.                                             |
| `rules`     | If non-`None`, only fixes whose `Violation.rule_id` is in this set are eligible.       |
| `stdin/out/err` | Streams for the interactive prompt and the dry-run diff. Default to `sys.std*`.    |

The function is the single CLI entry-point into the engine. It
is pure I/O at the byte level; it does not call back into the
linter (the read-only lint produced `report`).

## 6. Conflict resolution algorithm

Pseudocode (matches research §1, §5):

```python
def _resolve_conflicts(fixes: list[FixCandidate]) -> tuple[list[FixCandidate], list[FixSkip]]:
    fixes_sorted = sorted(fixes, key=lambda f: f.fix.start)
    applied: list[FixCandidate] = []
    skipped: list[FixSkip] = []
    cluster: list[FixCandidate] = []
    cluster_end = -1

    def flush() -> None:
        if not cluster:
            return
        winner = min(cluster, key=lambda f: (
            0 if f.fix.confidence == "safe" else 1,
            f.rule_id,
            f.fix.start,
            f.fix.end,
        ))
        applied.append(winner)
        for c in cluster:
            if c is not winner:
                skipped.append(FixSkip(c.file, c.fix, c.rule_id, "conflict"))

    for c in fixes_sorted:
        if c.fix.start >= cluster_end:
            flush()
            cluster = [c]
            cluster_end = c.fix.end
        else:
            cluster.append(c)
            cluster_end = max(cluster_end, c.fix.end)
    flush()
    return applied, skipped
```

Determinism: every call with the same `fixes` produces the
same `(applied, skipped)`.

## 7. SARIF projection extension (over spec 006)

`runs[0].results[]` entries gain an optional `fixes` array
when the corresponding `Violation.fix is not None`. Shape per
research §7:

```json
{
  "ruleId": "...",
  "level": "...",
  "message": {"text": "..."},
  "locations": [...],
  "fixes": [{
    "description": {"text": "<Fix.description>"},
    "artifactChanges": [{
      "artifactLocation": {"uri": "<relativised path>"},
      "replacements": [{
        "deletedRegion": {
          "byteOffset": <Fix.start>,
          "byteLength": <Fix.end - Fix.start>
        },
        "insertedContent": {"text": "<Fix.replacement>"}
      }]
    }]
  }]
}
```

`fixes` is OMITTED (not `[]`) when the violation has no fix.
This matches spec 006's policy of emitting absent fields for
unknown values.

## 8. Out of scope

| Item                                            | Reason                                                                            |
| ----------------------------------------------- | --------------------------------------------------------------------------------- |
| Multi-file fixes (one `Fix` spans two files)    | Fix is single-file by definition (one `start`/`end` on one file).                 |
| `--fix-confidence safe` flag                    | Both confidence values are applied in `--fix`. Future spec if `review` is noisy.   |
| User-input-fix authoring UI                     | `fix=None` for those rules; description carries guidance.                          |
| Git stash / `.bak` backup                       | Atomic write + rollback is the safety net; the user's working copy is the truth.   |
| Concurrent multi-process fix runs               | Out — same lock semantics as any other tool that writes a file.                    |
