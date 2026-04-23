# Phase 1 Data Model — Linter Foundation

All types live in `texlint.api`. External consumers (rules, output renderers, third-party journal packages) import from `texlint.api` only; `texlint.core.*` and `texlint.output.*` are internal. Every dataclass is `@dataclass(frozen=True)` unless noted.

## Enums

```python
class Severity(str, Enum):
    ERROR = "error"
    WARNING = "warning"

class CategoryStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    SKIPPED = "SKIPPED"
```

Both are `str` enums so their values serialise naturally into JSON. `Severity` is used by `Violation.severity` and `Rule.severity`; `CategoryStatus` is used by `CategorySummary.status`.

## `FixSuggestion` (reserved)

```python
@dataclass(frozen=True)
class FixSuggestion:
    description: str
    # Additional fields (byte offsets, replacement text) land in Step 4.
```

Present now so the `Violation.fix: FixSuggestion | None` field type is stable. **Every smoke rule sets `fix = None`.** Step 4 populates the structure. (Spec FR-012, Assumption.)

## `Violation`

```python
@dataclass(frozen=True)
class Violation:
    file: Path
    line: int                           # 1-based
    column: int | None                  # 1-based when present; None when the rule cannot localise to a column
    rule_id: str                        # e.g. "JSS-CITE-001", or "JSS-PARSE-000" for parse failures
    severity: Severity
    message: str                        # human-readable, already formatted (no templating left)
    suggestion: str | None              # optional short author-facing hint
    fix: FixSuggestion | None = None    # reserved for Step 4
```

**Invariants**:

1. `line ≥ 1`. Converted at the API boundary from pylatexenc's 1-based line / 0-based column and from bibtexparser's 0-based line.
2. `column` is 1-based when set, or `None` when the rule operates at line granularity.
3. Sort order (for deterministic output, spec FR-014 / SC-003): primary `file` (string sort of `str(path)`), then `line`, then `column` with `None < any integer`, then `rule_id`. Implemented as `Violation.sort_key() -> tuple`.
4. Parse-error violations carry `rule_id = "JSS-PARSE-000"`, `severity = Severity.ERROR`, and belong to the synthetic `parse` category (by virtue of their rule id — the engine routes any `Violation` whose `rule_id == "JSS-PARSE-000"` into category `parse`).

## `Rule`

```python
RuleCheck = Callable[["ParsedDocument", "ToolConfig"], Iterator[Violation]]

@dataclass(frozen=True)
class Rule:
    id: str                             # e.g. "JSS-CITE-001"
    category: str                       # e.g. "citation"
    severity: Severity
    message_template: str               # human-oriented; rules format their own messages today
    authority: str                      # short citation: "jss.cls", "article.tex", "JSS style guide", or "author instructions"
    check: RuleCheck                    # pure function; no subclassing
    formats: frozenset[str] | None = None  # None ⇒ all; otherwise a subset of {".tex", ".bib"}
```

**Invariants**:

1. `id` is unique within a single `JournalRuleModule`. Uniqueness across journals is not required — `--journal` selects a single journal, and `ignore_rules` resolves against that journal.
2. `check` is a plain callable assigned at module scope. **No methods.** No `Rule` subclasses. (Principle X.)
3. `formats` is a `frozenset` so `Rule` remains hashable. `None` means "applies to every input"; a set restricts the rule to files whose suffix is in the set.

## `RuleCategory`

```python
@dataclass(frozen=True)
class RuleCategory:
    id: str                             # e.g. "citation"
    title: str                          # human-readable, for tables
    rules: tuple[Rule, ...]
```

The engine additionally synthesises the `parse` category (id `parse`, title `"Parse errors"`) at report-build time; it does not appear in any journal's declared categories.

## `CategorySummary`

```python
@dataclass(frozen=True)
class CategorySummary:
    category_id: str
    title: str
    status: CategoryStatus              # PASS | FAIL | SKIPPED
    rules_applied: int                  # rules from this category that actually ran (not ignored and formats-compatible)
    rules_passed: int                   # rules_applied that produced zero violations on this document
    violations: tuple[Violation, ...]   # violations attributed to this category (may be empty when PASS or SKIPPED)
```

**Derivation** (spec FR-010, Clarification Q3):

- `status = SKIPPED` iff `rules_applied == 0` (every rule in the category was in `ignore_rules`, or no input file matched any rule's `formats`).
- `status = FAIL` iff `rules_applied > 0` and `len(violations) > 0`.
- `status = PASS` otherwise.

The synthetic `parse` category populates `violations` from every `JSS-PARSE-000` violation produced across all parsed files; `rules_applied = 0`, `rules_passed = 0` (because no rule *ran* — parse errors pre-date the rule engine), `status` is `FAIL` when any `JSS-PARSE-000` is present, else `PASS`. The synthetic category is excluded from `compliance_percentage` regardless.

## `ComplianceReport`

```python
@dataclass(frozen=True)
class ComplianceReport:
    tool_version: str                   # texlint.__version__
    journal_id: str                     # e.g. "jss"
    violations: tuple[Violation, ...]   # all violations, sorted deterministically (see Violation §3)
    categories: tuple[CategorySummary, ...]  # all journal-declared categories + synthetic "parse" if any PARSE_ERROR occurred
    compliance_percentage: float | None # None when every category is SKIPPED; otherwise 0.0–100.0 inclusive
```

**Derivation**:

- `compliance_percentage`: given the `PASS`/`FAIL` (non-SKIPPED, non-synthetic-`parse`) subset of `categories`:
  - if that subset is empty: `None`
  - else: `100.0 * len([c for c in subset if c.status == PASS]) / len(subset)`, rounded to one decimal.
- The `violations` tuple is the flat concatenation of every category's `violations` (including the synthetic `parse` category's), sorted by `Violation.sort_key()`.

## `ToolConfig`

```python
@dataclass(frozen=True)
class ToolConfig:
    journal: str = "jss"
    mode: Literal["author", "reviewer"] = "author"
    output: Literal["terminal", "json", "html"] = "terminal"
    ignore_rules: frozenset[str] = frozenset()
    verbose: bool = False
    code_width: int = 80                # used by JSS-SRC-001; surfaces here so rules don't reach for globals
```

**Invariants**:

- `ignore_rules` is always a `frozenset` (set at `config.load()` time from the CLI comma-separated string or the TOML array).
- `ToolConfig()` with no arguments represents the built-in defaults. `config.load()` overlays `.jss-lint.toml` keys then CLI flags, producing a frozen instance.
- Unknown keys in `.jss-lint.toml` are warned (verbose only) but not errored — preserves cross-version portability (spec Edge Cases).

## `ParsedTexFile`

```python
@dataclass(frozen=True)
class ParsedTexFile:
    path: Path
    source: str                         # raw UTF-8 text, BOM stripped (spec FR-004)
    nodes: tuple[Any, ...]              # pylatexenc node list (opaque to the engine; rules inspect it)
    walker: Any                         # the LatexWalker instance, retained for pos_to_lineno_colno
    violations: tuple[Violation, ...]   # only JSS-PARSE-000 violations may appear here
```

**Notes**:

- `nodes` is typed as `tuple[Any, ...]` in the public API to avoid re-exporting pylatexenc's node-class names on our surface. Rules that walk the AST import concrete node types from `pylatexenc.latexwalker` directly.
- `walker.pos_to_lineno_colno(pos)` returns **(1-based line, 0-based column)**. Any rule that localises a finding to a column MUST add 1 to the column before constructing the `Violation`, or use the `api.violation_at(walker, pos, …)` helper which performs the conversion.

## `ParsedBibFile`

```python
@dataclass(frozen=True)
class ParsedBibFile:
    path: Path
    source: str                         # raw UTF-8 text — retained for future fix offsets (Step 5)
    library: Any                        # bibtexparser.library.Library
    violations: tuple[Violation, ...]   # only JSS-PARSE-000 violations may appear here
```

**Notes**:

- `library.entries[i].start_line` is **0-based**. Converted to 1-based exactly once, at the API boundary, when a rule constructs a `Violation`.
- `library.failed_blocks` is iterated at parse time and converted to `JSS-PARSE-000` violations directly on `ParsedBibFile.violations`.

## `ParsedDocument`

```python
@dataclass(frozen=True)
class ParsedDocument:
    tex_files: tuple[ParsedTexFile, ...]
    bib_files: tuple[ParsedBibFile, ...]

    def all_violations(self) -> Iterator[Violation]: ...
    def files_for_rule(self, rule: Rule) -> Iterator[ParsedTexFile | ParsedBibFile]: ...
```

`ParsedDocument` is the single unit of work presented to the rule engine. `files_for_rule` encapsulates the `Rule.formats` filter: if `rule.formats is None`, yields every file; otherwise, yields files whose suffix is in `rule.formats`.

## `JournalRuleModule` (ABC)

```python
class JournalRuleModule(ABC):
    id: ClassVar[str]                   # e.g. "jss"

    @abstractmethod
    def categories(self) -> tuple[RuleCategory, ...]:
        """Return the journal's categories and rules. Rule modules MAY be imported lazily in this method."""

    def rules(self) -> tuple[Rule, ...]:
        """Flatten categories into a rule list. Default implementation."""
        return tuple(r for c in self.categories() for r in c.rules)
```

**Entry-point contract**: `[project.entry-points."texlint.journals"] <id> = "<dotted.path>:<ClassName>"`. The engine instantiates the class with no arguments. Journals that need per-instance state encapsulate it in the class; journals that don't (the common case) keep everything at class level.

**Failure modes**:

- Unknown `--journal` name ⇒ `JournalNotFoundError`, CLI exit 2.
- Entry-point resolves to a non-`JournalRuleModule`-subclass ⇒ `InvalidJournalError`, CLI exit 2.

## Ownership / module map

| Class | Defined in | Re-exported from |
|---|---|---|
| `Severity`, `CategoryStatus` | `texlint.api` | — |
| `FixSuggestion`, `Violation` | `texlint.api` | — |
| `Rule`, `RuleCategory`, `CategorySummary`, `ComplianceReport` | `texlint.api` | — |
| `ToolConfig` | `texlint.api` | `texlint.config` (loader only) |
| `ParsedTexFile`, `ParsedBibFile`, `ParsedDocument` | `texlint.api` | — |
| `JournalRuleModule` | `texlint.api` | — |
| `JournalNotFoundError`, `InvalidJournalError` | `texlint.api` | — |
| `parse_tex_file`, `parse_bib_file` | `texlint.core.parser` | — |
| `load_journal`, `run` | `texlint.core.engine` | — |

`texlint.api` is the only public import surface for rule authors and third-party journals.
