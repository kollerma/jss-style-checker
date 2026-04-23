# Phase 0 Research — Linter Foundation

The `/speckit.plan` input fixed most library and API choices. This document records the decisions, the rationale, and alternatives that were considered and rejected. It also resolves the remaining NEEDS CLARIFICATION items from plan Technical Context.

## Library choices

### LaTeX AST — `pylatexenc` 2.x

- **Decision**: Use `pylatexenc.latexwalker.LatexWalker(source)`; call `walker.get_latex_nodes()` to obtain `(nodes, pos, length)`. Store both `nodes` **and** the `walker` on `ParsedTexFile` so that rule code can call `walker.pos_to_lineno_colno(pos)` to resolve any node's position back to line/column.
- **Rationale**: pylatexenc is the only mature, pip-installable LaTeX AST parser with node-type coverage sufficient for style checks. It is already a project dependency. Retaining the walker on `ParsedTexFile` avoids each rule reimplementing position lookup.
- **Position conventions**: `pos_to_lineno_colno` returns `(line, col)` with **1-based line, 0-based column**. Convert column to 1-based **exactly once** at the API boundary (inside `Violation.__init__` or the factory that produces it). Rules never perform this conversion. Documented as an invariant in `data-model.md`.
- **Parse-error handling**: wrap the `LatexWalker` construction + `get_latex_nodes()` call in a `try/except pylatexenc.latexwalker.LatexWalkerError`. On error, return a `ParsedTexFile` whose `nodes` is empty and whose `violations` contains a single `JSS-PARSE-000` entry with line/column derived from the exception's `pos` attribute (falling back to `(1, 1)` if unavailable). No raise propagates out of `parse_tex_file`. (Spec FR-005.)
- **Node types the engine and rules rely on**: `LatexMacroNode`, `LatexEnvironmentNode`, `LatexGroupNode`, `LatexCharsNode`, `LatexCommentNode`, `LatexMathNode`. Documented in `data-model.md` under `ParsedTexFile`.
- **Alternatives considered**:
  - *TexSoup* — abandoned, incomplete macro handling.
  - *plasTeX* — aims at macro expansion / rendering, heavier than needed for style checks.
  - *Pandoc* (as a parser) — external binary, not a Python AST, adds a non-Python dependency for packaging.

### BibTeX AST — `bibtexparser` v2

- **Decision**: Use `bibtexparser.parse_file(path)`, which returns a `Library`. Iterate `library.entries`; each entry exposes `.entry_type`, `.key`, `.fields_dict`, `.start_line`. Surface `library.failed_blocks` as `JSS-PARSE-000` violations.
- **Position conventions**: `entry.start_line` and `failed_block.start_line` are **0-based**. Convert to 1-based at the API boundary, same invariant as TeX positions.
- **Raw source retained**: keep `ParsedBibFile.source` as the original file text. Step 5 (`--fix`) needs byte offsets for splice fixes, and `bibtexparser`'s round-trip is lossy (reordering, whitespace normalisation). Storing the raw text costs memory measured in kilobytes; acceptable.
- **Parse-error handling**: `parse_file` does not raise on per-entry errors — they populate `failed_blocks`. We emit one `JSS-PARSE-000` per failed block. Hard I/O errors (file not found, permission denied) are caught one level up in `parse_bib_file` and emitted as a single `JSS-PARSE-000` with line 1.
- **Alternatives considered**:
  - *bibtexparser v1* — its "middleware" architecture is string mangling at parse time; v2's `Library` / `Block` model is a proper AST and exposes `failed_blocks` as first-class.
  - *pybtex* — aimed at formatting / rendering, less ergonomic for AST-level checks.

### CLI — `click` 8.1+

- **Decision**: `click` for the CLI. `main()` returns via `sys.exit(exit_code)` so that `click.testing.CliRunner.invoke(...).exit_code` round-trips cleanly.
- **`CliRunner` caveat**: `click` 8.2 removed the `mix_stderr=` parameter from `CliRunner`. Tests use bare `CliRunner()` and assert on `result.output` alone; when stderr is under test, use `result.stderr_bytes` (click ≥8.1).
- **`--ignore-rules`**: declared as `str` on the click command and parsed to a normalised `frozenset[str]` exactly once, inside `config.load()`. Rules never see the comma-separated string.
- **Alternatives considered**: `argparse` (stdlib but boilerplatey — parameters declared via decorators in click are easier to review); `typer` (wrapper over click, adds an indirection layer the constitution §X discourages).

### Config — `tomllib` / `tomli`

- **Decision**: Import `tomllib` on Python ≥3.11, fall back to `tomli` on Python 3.10. Both expose `.loads(bytes)` identically:
  ```python
  import sys
  if sys.version_info >= (3, 11):
      import tomllib
  else:
      import tomli as tomllib
  ```
- **Merge order**: `ToolConfig()` built-in defaults → overlay keys from `.jss-lint.toml` (if CWD has one) → overlay CLI flags (only where the user explicitly set them). Done once inside `config.load()` which returns a `@dataclass(frozen=True)` `ToolConfig`. Precedence order is exactly the spec FR-003 statement.
- **File location**: CWD only. The spec is explicit. No parent-directory search, no XDG lookup.
- **Alternatives considered**: `tomlkit` — preserves formatting, not needed for a read-only path.

### Terminal rendering — `rich`

- **Decision**: `rich.console.Console(file=sys.stdout)`. Group violations per source file using `console.rule(f"[bold]{file_path}")` followed by a `rich.table.Table`. Severity colouring: `error` → red, `warning` → yellow. Reviewer mode uses a single `Table` with one row per category showing status (`PASS` green / `FAIL` red / `SKIPPED` dim) and `rules_applied` / `rules_passed` counts.
- **Alternatives considered**: raw ANSI codes (fragile; no table layout); `colorama` alone (no table primitive).

### JSON — stdlib `json`

- **Decision**: Build a plain `dict` matching the schema in `contracts/json-output.md` and serialise with `json.dumps(report, indent=2, sort_keys=True)`. `sort_keys=True` on every nested level plus the deterministic violation-ordering rule (file → line → column with `None` sorting before integers → rule_id) guarantees byte-identical output on identical input (SC-003).
- **`tool_version`**: sourced from `texlint.__version__`, which in turn is set by `importlib.metadata.version("jss-style-checker")` (falling back to `"0.1.0"` in editable installs).
- **Alternatives considered**: `orjson` (faster but not deterministic without extra effort); a hand-written stable-JSON writer (reinventing `sort_keys`).

### HTML — `jinja2`

- **Decision**: `jinja2.Environment(loader=jinja2.PackageLoader("texlint.output", "templates"), autoescape=True)`. Ship `author.html.j2` and `reviewer.html.j2`. No CSS framework — inline minimal styling in a `<style>` block inside each template so the rendered HTML is a self-contained file.
- **`autoescape=True`** is mandatory: rule messages and file paths are untrusted by the renderer.
- **Alternatives considered**: `string.Template` (no loops / conditionals); raw f-strings (unsafe for HTML); `markupsafe` alone (no templating layer).

## Journal plugin registration

- **Decision**: `pyproject.toml` adds
  ```toml
  [project.entry-points."texlint.journals"]
  jss = "texlint.journals.jss:JSSJournal"
  ```
  `load_journal(journal_id)` uses `importlib.metadata.entry_points(group="texlint.journals")` (the Python 3.10+ selectable API) and resolves by name. On miss, it raises `JournalNotFoundError`, which `cli.main()` catches and maps to exit code 2 with an error message on stderr.
- **Lazy rule import**: `JSSJournal.categories()` imports rule modules on first call, not at `import texlint`. Keeps the core import cheap for third-party packages that depend on `texlint` as a library but don't want to pay for every installed journal's rules.
- **Alternatives considered**: registering a hard-coded dict in `core/engine.py` (violates Principle IV); package-discovery by naming convention (slower, less explicit).

## Rule data model

- **Decision**: `Rule` is a `@dataclass(frozen=True)` whose `check` field is of type `Callable[[ParsedDocument, ToolConfig], Iterator[Violation]]`. No subclasses. Metadata (id, category, severity, message_template, formats, authority) are all dataclass fields. The rule callable is set at module scope and assigned to the dataclass — not a method.
- **`ToolConfig` in signature**: rules receive `ToolConfig` so they can read knobs like `code_width` and (future) `ignore_abbreviations` without reaching for a global. For this foundation step only `JSS-SRC-001` actually reads a config value (`code_width`, default 80); the other two ignore their `config` argument.
- **Rationale**: constitution §X ("Small Surface, Known Semantics") — a subclass hierarchy implies inheritance-based behaviour we do not need; data + Callable is strictly less machinery.
- **Alternatives considered**: `Rule` as ABC with a `check` abstract method; functional decorator (`@rule(...)` producing a Rule at import time — sugar but inversion-of-control makes entry-point lazy-loading fiddly).

## Parse-error rule id

- **Decision**: Rule id for parse failures is `JSS-PARSE-000`. Severity is `error`. Category is the synthetic `parse` category (excluded from `compliance_percentage`, per spec Clarification Q1).
- **Relation to the spec clarification**: the spec's Clarification Q1 locked down the *shape* (synthetic rule id, synthetic `parse` category, excluded from the percentage). The exact string `PARSE_ERROR` was placeholder; the plan concretises it to `JSS-PARSE-000` to match the journal-prefixed rule-id convention every JSS rule uses (`JSS-CITE-001`, `JSS-BIB-001`, …). Spec FR-005 and the Clarifications bullet are updated correspondingly in a companion edit (see plan.md §Summary).
- **Future-proofing**: parse errors are produced by `core.parser`, which doesn't know which journal is active. We pick the `JSS-` prefix because (a) this tool is `jss-style-checker`, (b) a later multi-journal build can either share the `JSS-PARSE-000` id or introduce a journal-neutral `CORE-PARSE-000` alias in a minor release — both are additive.

## Smoke rules (authority citations — §V)

Three rules ship in the `jss` journal. Each exercises one rule shape.

| Rule id | Category | Shape | Authority |
|---|---|---|---|
| `JSS-CITE-001` | `citation` | LaTeX AST: `LatexMacroNode` walk, flags `\emph{...}` whose argument matches a bibkey pattern (used instead of `\cite`) | JSS author instructions: citations use `\cite{...}` family; `\emph` is reserved for emphasis |
| `JSS-BIB-001` | `bibliography` | BibTeX: iterate `library.entries`, flag any entry whose `fields_dict` lacks a `year` | JSS author instructions: every bibliography entry carries a publication year |
| `JSS-SRC-001` | `typography` | Source scan: any line with `len(line.rstrip("\n")) > config.code_width` (default 80) | `article.tex` style convention for code-block width (JSS style guide recommends ≤80 chars for readability of verbatim blocks) |

Two optional additional rules are deliberately **not** shipped in this step. The spec permits 3–5; three is enough to exercise all rule shapes, and Principle X favours the smaller surface.

## Open items (plan-time decisions)

### Compliant fixture preamble source

- **Issue**: the plan-input prompt states that `tests/fixtures/compliant/minimal.tex` should use "the real `article.tex` template preamble from `docs/jss-template/` (checked in during Step 0.5)". `docs/jss-template/` does not exist in the repository at the time of planning — Step 0.5 has not run.
- **Decision**: land a **hand-authored minimal preamble** in `tests/fixtures/compliant/minimal.tex` that deliberately satisfies the three smoke rules (contains only `\cite{...}` for citations, bibliography entries all have `year`, and every line is ≤80 chars). Leave a `TODO(step-0.5): replace with docs/jss-template/article.tex preamble once it lands.` comment at the top of the file.
- **Why this is safe**: the three smoke rules are verifying framework plumbing, not real JSS style enforcement. The framework's correctness does not depend on which preamble the compliant fixture uses, only that the fixture passes every smoke rule. Step 2, which introduces the real rule catalogue, is the point at which the fixture preamble must be authoritative.
- **Alternative considered**: block this plan on Step 0.5 — rejected because it would defer the entire foundation for a fixture-content upgrade the framework does not need.

### Existing `tests/fixtures/stub_journal/` package

- **Issue**: the pre-committed `stub_journal/__init__.py` defines `JOURNAL = {"name": "stub", "rules": ()}` (a plain dict), but the plan-input prompt specifies that `JSSJournal` subclasses the `JournalRuleModule` ABC. The entry point in the stub fixture's `pyproject.toml` currently resolves to the dict.
- **Decision**: rewrite `tests/fixtures/stub_journal/src/stub_journal/__init__.py` so that it defines a `StubJournal(JournalRuleModule)` subclass with an empty `rules` list, and update its `pyproject.toml` entry point to point at the class: `stub = "stub_journal:StubJournal"`. The test that proves zero-core-edit journal registration (tests/integration/test_plugin_discovery.py) then exercises the real ABC contract.
- **Rationale**: a journal fixture that doesn't conform to the final ABC doesn't prove §IV. Updating it is part of this plan's scope (not a new feature — it brings a pre-committed stub into alignment with the ABC the plan creates).

### Stream semantics (stdout / stderr)

- **Decision**: renderer output (`terminal` / `json` / `html`) is always written to **stdout**. Tool diagnostics, parse errors of the *shell-level* kind (file not found, unknown journal), and error messages for exit-2 conditions are written to **stderr**. For `--output json`, stdout is always valid JSON — even on exit 2 the JSON contains the parse-error violations inside `violations` (spec Story 3 scenario 3).
- **Rationale**: standard Unix convention; allows `jss-lint file.tex > report.json` to work regardless of violations, and `jss-lint file.tex 2>/dev/null` to suppress diagnostics without losing data.
- **Testing**: `tests/integration/test_cli_exit_codes.py` asserts stream separation.

### Deferred / out-of-scope (per spec)

- `--fix` / `--dry-run`: Step 4.
- `.Rnw` / `.Rmd`: Step 3.
- Full JSS rule catalogue (53 rules): Step 2.
- `eval-jss` CLI, eval corpus, ≥90% precision gate (Constitution §VI, §XII): Step 5.
- AI client: not this project.

No research action needed for any of the above — they do not block this plan.
