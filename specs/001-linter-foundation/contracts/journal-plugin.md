# Contract — Journal Plugin System

Journals are registered through the standard Python `importlib.metadata` entry-point mechanism. Adding a journal — first-party or third-party — requires **zero edits** to files under `src/texlint/core/` or `src/texlint/api.py` (Constitution §IV, spec SC-005).

## Entry point group

The group name is **`texlint.journals`**. Distributions register journals by adding a `[project.entry-points."texlint.journals"]` table to their `pyproject.toml`:

```toml
[project.entry-points."texlint.journals"]
jss  = "texlint.journals.jss:JSSJournal"
stub = "stub_journal:StubJournal"
```

Each entry maps a **journal id** (the value passed to `jss-lint --journal`) to a dotted path `"<module>:<ClassName>"`. The class must be a subclass of `texlint.api.JournalRuleModule`.

## `JournalRuleModule` (ABC)

Defined in `texlint.api`:

```python
from abc import ABC, abstractmethod
from typing import ClassVar

class JournalRuleModule(ABC):
    id: ClassVar[str]

    @abstractmethod
    def categories(self) -> tuple[RuleCategory, ...]:
        """Return this journal's categories. MAY import rule modules lazily."""

    def rules(self) -> tuple[Rule, ...]:
        return tuple(r for c in self.categories() for r in c.rules)
```

**Contract requirements**:

1. `JournalRuleModule.id` is a `ClassVar[str]` matching the entry-point name (engine validates this on load).
2. `categories()` returns a tuple of `RuleCategory` instances — **not a list** (tuples are immutable; the engine trusts the return value).
3. `categories()` MAY perform imports of rule modules lazily. The engine calls it exactly once per run.
4. Each `Rule.id` MUST be unique within the journal. Duplicates raise `InvalidJournalError` and exit 2.
5. `JournalRuleModule` subclasses MUST be constructible with no arguments (`cls()` is how the engine instantiates them).

## Loading sequence

```
jss-lint --journal jss ...
            │
            ▼
   texlint.cli.main()
            │
            ▼
   texlint.core.engine.load_journal("jss")
            │
            ├── importlib.metadata.entry_points(group="texlint.journals")
            │         → returns EntryPoints selectable by name
            │
            ├── ep.load()        # imports the module, resolves the attribute
            │
            ├── validate: issubclass(obj, JournalRuleModule) ? — else InvalidJournalError
            │
            ├── instantiate: obj()
            │
            └── validate: instance.id == "jss" ? — else InvalidJournalError
                         │
                         ▼
                 returns JournalRuleModule instance
            │
            ▼
   texlint.core.engine.run(config, parsed_document)
            │
            ▼
   for each rule in journal.rules():
       for each file in parsed_document.files_for_rule(rule):
           if rule.id in config.ignore_rules: continue
           yield from rule.check(parsed_document, config)
```

## Errors

| Error | Raised when | CLI exit |
|---|---|---|
| `JournalNotFoundError` | No entry point with the given id. | 2 |
| `InvalidJournalError` | Entry point resolves to a non-`JournalRuleModule` object, or `id` ClassVar mismatches, or duplicate `Rule.id` within the journal. | 2 |

Both errors live in `texlint.api`; CLI catches them and writes the message to stderr before `sys.exit(2)`.

## Example — a minimal valid journal

```python
# my_pkg/__init__.py
from texlint.api import (
    JournalRuleModule, Rule, RuleCategory, Severity, Violation,
    ParsedDocument, ToolConfig,
)

def _no_figures_check(doc: ParsedDocument, cfg: ToolConfig):
    for tex in doc.tex_files:
        for node in tex.nodes:
            if getattr(node, "macroname", None) == "includegraphics":
                line, col = tex.walker.pos_to_lineno_colno(node.pos)
                yield Violation(
                    file=tex.path, line=line, column=col + 1,
                    rule_id="MYJRN-FIG-001", severity=Severity.WARNING,
                    message="No figures allowed in letters.",
                    suggestion=None, fix=None,
                )

_no_figures_rule = Rule(
    id="MYJRN-FIG-001",
    category="figures",
    severity=Severity.WARNING,
    message_template="No figures allowed in letters.",
    authority="my-journal style guide §3.1",
    check=_no_figures_check,
    formats=frozenset({".tex"}),
)

class MyJournal(JournalRuleModule):
    id = "myjrn"
    def categories(self):
        return (RuleCategory(
            id="figures", title="Figures", rules=(_no_figures_rule,),
        ),)
```

Paired with:

```toml
[project.entry-points."texlint.journals"]
myjrn = "my_pkg:MyJournal"
```

…and the package installed into the same environment as `texlint`, `jss-lint --journal myjrn paper.tex` now runs `MYJRN-FIG-001`. No fork of `texlint` was required.

## The `stub_journal` test fixture

`tests/fixtures/stub_journal/` is a local `pip install -e`-able package that registers a `StubJournal(JournalRuleModule)` with no categories and no rules. `tests/integration/test_plugin_discovery.py` installs (or arranges in-process sys.path / entry-point patching for) this fixture and asserts:

1. `jss-lint --journal stub paper.tex` dispatches to `StubJournal`, not `JSSJournal`.
2. The run produces zero violations and exit code 0.
3. No file under `src/texlint/core/` or `src/texlint/api.py` was modified to make this work.

The fixture's `__init__.py` — currently a placeholder dict — is rewritten as part of this plan's implementation to conform to the ABC.
