# Implementation Plan: Linter Foundation — `jss-style-checker` Core

**Branch**: `001-linter-foundation` | **Date**: 2026-04-22 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-linter-foundation/spec.md`

## Summary

Build the `texlint` package — a deterministic, rule-based LaTeX style linter invoked as `jss-lint` — with the public data model, core parser/engine, configuration loader, CLI, three output renderers (terminal / JSON / HTML), and one journal plugin (`jss`) carrying 3 smoke-test rules that exercise the three rule shapes (LaTeX-AST, BibTeX, source-scan). Parse errors are non-fatal (`JSS-PARSE-000` violations). Fixtures and tests ship alongside. The full 53-rule JSS catalogue, `.Rnw`/`.Rmd` dispatch, `--fix`, and `eval-jss` are deferred to later steps.

**Spec drift reconciled**: the spec Clarification Q1 referenced the parse-error rule id as `"PARSE_ERROR"`; the plan concretises it to `"JSS-PARSE-000"` to match the journal-prefixed convention every other rule id uses. Spec FR-005 and the Q1 clarification bullet are updated in lockstep (see companion edit below plan.md).

## Technical Context

**Language/Version**: Python ≥3.10 (tested on 3.10, 3.11, 3.12)
**Primary Dependencies**: `pylatexenc>=2.10`, `bibtexparser>=2.0.0b6`, `click>=8.1`, `rich>=13.0`, `jinja2>=3.1`, `tomli>=2.0` (Python <3.11 fallback; `tomllib` on ≥3.11)
**Storage**: Filesystem only — reads `.tex` / `.bib` / `.jss-lint.toml`, writes nothing (no DB, no network)
**Testing**: `pytest`, `pytest-cov` (branch coverage via `--cov-branch`), `click.testing.CliRunner` for CLI integration tests
**Target Platform**: Any POSIX / Windows with Python 3.10+; distributed as a wheel
**Project Type**: Single Python package + CLI (`src/` layout, hatchling backend)
**Performance Goals**: Full run on a typical single-chapter JSS manuscript (tens of `.tex` files, one `.bib`) in under 5 seconds on ordinary developer hardware (SC-009)
**Constraints**: Byte-deterministic JSON output across runs (SC-003); zero core edits to add a journal (SC-005 / Constitution §IV); 100% branch coverage on every `src/texlint/journals/*/rules/` file (Constitution §IX)
**Scale/Scope**: Foundation step — ~10 modules under `src/texlint/`, 3 smoke rules, ~one integration test per output format × mode, unit tests per parser + engine + config

## Constitution Check

- [x] **§I Determinism**: Rule `check` callables are pure `(ParsedDocument, ToolConfig) → Iterator[Violation]` functions. No RNG, clock, or network. The parser and engine are likewise deterministic. **PASS.**
- [x] **§II AST-First**: Rule A (`JSS-CITE-001`, no `\emph` for citation markup) walks the pylatexenc `LatexMacroNode` AST. Rule B (`JSS-BIB-001`, every entry has `year`) iterates `Library.entries`. Rule C (`JSS-SRC-001`, line width ≤80 chars) is an explicit raw-source scan, which is the constitution-approved case. **PASS.**
- [x] **§III Non-Fatal Parse**: `parse_tex_file` wraps `LatexWalker` in a `try/except LatexWalkerError` and emits a `JSS-PARSE-000` violation; `parse_bib_file` surfaces `library.failed_blocks` as `JSS-PARSE-000` violations. Neither raises. **PASS.**
- [x] **§IV Zero Core Edits for Journals**: The `jss` journal is registered via the `[project.entry-points."texlint.journals"]` table in `pyproject.toml`. The engine imports `texlint.journals.jss` **only** through `importlib.metadata`. The `tests/fixtures/stub_journal/` package proves the plugin contract without editing core. **PASS.**
- [x] **§V Authority Cited**: Each smoke rule cites a plausible authority (see research.md §Smoke rules). **PASS** for this step — formal authority review gates rules in Step 2.
- [ ] **§VI ≥90% Precision Gate**: **N/A for this step.** Spec Assumptions and research.md §Deferred explicitly defer the eval corpus and `eval-jss` to Step 5; these smoke rules are foundational infrastructure, not precision-graded content.
- [ ] **§VII Safe Auto-Fix**: **N/A for this step.** Spec out-of-scope defers `--fix` to Step 4; `FixSuggestion` is present but every smoke rule leaves `violation.fix = None`.
- [x] **§VIII TDD**: `tasks.md` (produced by `/speckit.tasks`) will order the per-rule test task before the per-rule implementation task. Parser, engine, and config tests likewise precede their implementations.
- [x] **§IX Branch Coverage**: `pyproject.toml` adds `--cov=src/texlint/journals --cov-branch --cov-fail-under=100` to `pytest`'s `addopts` (scoped to the journals tree — matches Principle IX wording). Every smoke rule lands with full-branch tests in `tests/unit/journals/jss/`.
- [x] **§X Small Surface**: `Rule` is a `@dataclass(frozen=True)` with a `Callable` field; no subclasses. No speculative helpers. No compat shims. `FixSuggestion` is the one reserved-but-unused surface, justified by the spec Assumption.
- [ ] **§XII Reproducible Corpus**: **N/A for this step.** No precision claim is made.

All gates are PASS or documented N/A. **No Complexity Tracking entries required.**

Post-Phase-1 re-check (after writing research.md, data-model.md, contracts/, quickstart.md): all gates still PASS or N/A. No surprises emerged during Phase 1.

## Project Structure

### Documentation (this feature)

```text
specs/001-linter-foundation/
├── plan.md                  # This file
├── research.md              # Phase 0: decisions + rationales
├── data-model.md            # Phase 1: public data-model schemas
├── quickstart.md            # Phase 1: dev onboarding & smoke-run walkthrough
├── contracts/
│   ├── cli.md               # Phase 1: CLI surface (flags, exit codes, streams)
│   ├── json-output.md       # Phase 1: JSON ComplianceReport schema
│   └── journal-plugin.md    # Phase 1: JournalRuleModule ABC + entry point contract
└── checklists/
    └── requirements.md      # Spec quality checklist (from /speckit.specify)
```

### Source Code (repository root)

```text
src/texlint/
├── __init__.py                    # exposes __version__
├── api.py                         # public data model (Violation, Rule, RuleCategory, CategorySummary, ComplianceReport, ToolConfig, ParsedTexFile, ParsedBibFile, ParsedDocument, JournalRuleModule ABC, FixSuggestion, Severity, CategoryStatus, errors)
├── config.py                      # .jss-lint.toml loader + CLI overlay; config.load() returns frozen ToolConfig
├── cli.py                         # click entry; main() returns via sys.exit(code)
├── core/
│   ├── __init__.py
│   ├── parser.py                  # parse_tex_file / parse_bib_file; captures JSS-PARSE-000 violations
│   └── engine.py                  # load_journal() + run(config, parsed_document) -> ComplianceReport
├── output/
│   ├── __init__.py
│   ├── terminal.py                # rich-based renderer (author + reviewer modes)
│   ├── json_output.py             # deterministic JSON (sort_keys=True, indent=2)
│   ├── html_output.py             # Jinja2 PackageLoader renderer
│   └── templates/
│       ├── author.html.j2
│       └── reviewer.html.j2
└── journals/
    ├── __init__.py                # namespace only
    └── jss/
        ├── __init__.py            # defines JSSJournal(JournalRuleModule)
        └── rules/
            ├── __init__.py
            ├── cite_001_emph.py   # JSS-CITE-001 — AST rule
            ├── bib_001_year.py    # JSS-BIB-001 — BibTeX rule
            └── src_001_width.py   # JSS-SRC-001 — source-scan rule

tests/
├── conftest.py                    # parse_tex_source(src) / run_rule(rule, src) helpers
├── fixtures/
│   ├── compliant/
│   │   ├── minimal.tex            # passes every smoke rule (mirrors docs/jss-template/article.tex preamble — landed via Step 0.5)
│   │   └── minimal.bib
│   ├── violations/
│   │   ├── JSS-CITE-001.tex
│   │   ├── JSS-BIB-001.bib
│   │   ├── JSS-SRC-001.tex
│   │   └── JSS-PARSE-000.tex      # intentionally malformed
│   └── stub_journal/              # pre-existing test package; its __init__.py updated to subclass JournalRuleModule
│       ├── pyproject.toml
│       └── src/stub_journal/__init__.py
├── unit/
│   ├── test_api.py                # dataclass invariants, frozen, Violation.sort_key
│   ├── test_parser_tex.py
│   ├── test_parser_bib.py
│   ├── test_config.py             # defaults < file < CLI precedence
│   ├── test_engine.py             # category PASS/FAIL/SKIPPED, compliance_percentage math, ignore_rules, formats filter
│   └── journals/jss/
│       ├── test_cite_001_emph.py
│       ├── test_bib_001_year.py
│       └── test_src_001_width.py
└── integration/
    ├── test_cli_author_terminal.py
    ├── test_cli_reviewer_terminal.py
    ├── test_cli_json.py           # byte-determinism check
    ├── test_cli_html.py
    ├── test_cli_exit_codes.py     # 0 / 1 / 2, stream separation
    ├── test_cli_config_merge.py
    └── test_plugin_discovery.py   # uses tests/fixtures/stub_journal/
```

**Structure Decision**: Single-package Python project under `src/texlint/`, mirroring the module layout the spec's Assumptions section fixed. Test tree splits into `unit/`, `integration/`, and `fixtures/`. The existing `tests/fixtures/stub_journal/` package is rewired in `__init__.py` to subclass `JournalRuleModule` (the dict stub it currently holds predates the ABC and must be updated to exercise the real contract — see research.md §Open items).

## Complexity Tracking

No constitution gates are violated. **Table omitted.**
