---
description: "Task list for Linter Foundation (001-linter-foundation)"
---

# Tasks: Linter Foundation — `jss-style-checker` Core

**Input**: Design documents from `/specs/001-linter-foundation/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli.md, contracts/json-output.md, contracts/journal-plugin.md, quickstart.md

**Tests**: Unit tests are **MANDATORY** for every file under `src/texlint/journals/*/rules/` (Constitution §VIII TDD + §IX 100% branch coverage); the rule test task MUST precede the rule implementation task it covers. The spec additionally requests unit tests for parser, engine, and config, and integration tests for the CLI covering the three output formats and both modes — those are listed below as first-class tasks. Tests outside that scope are optional and omitted here.

**Organization**: Tasks are grouped by user story (from spec.md). Setup and Foundational phases block all user stories; after them, user stories may proceed in priority order or (with multiple developers) in parallel.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on an incomplete task in the same phase)
- **[Story]**: Which user story this task serves (US1…US6); setup / foundational / polish tasks carry no story label
- Every task names the exact file(s) it touches

---

## Phase 1: Setup

**Purpose**: Align the pre-existing skeleton (pyproject.toml, `src/texlint/`, `tests/`) with what the plan requires before any foundational work lands.

- [ ] T001 Add the `jss` journal entry point in `pyproject.toml` under `[project.entry-points."texlint.journals"]`: `jss = "texlint.journals.jss:JSSJournal"`.
- [ ] T002 [P] Create empty package directories with `__init__.py` files: `src/texlint/core/`, `src/texlint/output/`, `src/texlint/output/templates/`, `src/texlint/journals/`, `src/texlint/journals/jss/`, `src/texlint/journals/jss/rules/`.
- [ ] T003 [P] Create `tests/unit/journals/jss/__init__.py` (empty) so pytest collects rule-module tests under a matching package path.
- [ ] T004 [P] Create `tests/fixtures/compliant/` and `tests/fixtures/violations/` directories (empty for now; fixture files land in the US1 phase).
- [ ] T005 Verify editable installs work end-to-end: `pip install -e '.[dev]'` and `pip install -e tests/fixtures/stub_journal` both succeed, and `python -c "from importlib.metadata import entry_points; print(list(entry_points(group='texlint.journals')))"` lists the `stub` entry point. (The `jss` entry point appears only after T025 lands the class it points at.)

**Checkpoint**: Project skeleton and package structure match plan.md §Project Structure.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Everything every user story needs: the public data model, the parser, the rule engine, the config loader, the three smoke rules, the JSS journal module, and the `stub_journal` fixture fix.

**⚠️ CRITICAL**: No user story work (Phase 3+) can begin until this phase is complete.

### Public data model (`texlint.api`)

- [ ] T006 [P] Write `tests/unit/test_api.py` covering: `Severity` / `CategoryStatus` enum string values, `Violation` frozenness, `Violation.sort_key` ordering (file → line → column with `None < any int` → rule_id), `CategorySummary` status derivation from `rules_applied` / violations, `FixSuggestion` default `None`. Must fail on import before T007.
- [ ] T007 Implement `src/texlint/api.py`: `Severity`, `CategoryStatus`, `FixSuggestion`, `Violation` (with `sort_key()`), `Rule`, `RuleCategory`, `CategorySummary` (with `status` derivation), `ComplianceReport`, `ToolConfig`, `ParsedTexFile`, `ParsedBibFile`, `ParsedDocument` (with `all_violations()` and `files_for_rule()`), `JournalRuleModule` ABC (with default `rules()`), and the errors `JournalNotFoundError`, `InvalidJournalError`. Makes T006 pass.

### Parser (`texlint.core.parser`)

- [ ] T008 [P] Write `tests/unit/test_parser_tex.py` covering: happy-path parse of a minimal document; `LatexWalkerError` → single `JSS-PARSE-000` violation on `ParsedTexFile.violations`, no raise; UTF-8 BOM silently stripped before parsing; non-UTF-8 input → single `JSS-PARSE-000` violation at line 1; the returned `ParsedTexFile` retains both `nodes` and `walker`.
- [ ] T009 Implement `parse_tex_file(path: Path) -> ParsedTexFile` in `src/texlint/core/parser.py`. Open the file as bytes, strip a leading UTF-8 BOM, decode as UTF-8 (non-UTF-8 → `JSS-PARSE-000`), instantiate `LatexWalker(source)`, call `walker.get_latex_nodes()` inside a `try/except LatexWalkerError`. Makes T008 pass.
- [ ] T010 [P] Write `tests/unit/test_parser_bib.py` covering: happy-path parse returns `library` with at least one `entry`; a malformed block becomes one `JSS-PARSE-000` per `failed_block`; `entry.start_line` (0-based at source) surfaces as 1-based on any constructed `Violation`; `ParsedBibFile.source` equals the raw file text.
- [ ] T011 Implement `parse_bib_file(path: Path) -> ParsedBibFile` in `src/texlint/core/parser.py`. Read raw text, call `bibtexparser.parse_file(path)` (or `parse_string(source)` to keep `source` and parse under one read), map every `library.failed_blocks` entry to a `JSS-PARSE-000` violation. Makes T010 pass.

### Test-helper conftest

- [ ] T012 Implement `tests/conftest.py`: `parse_tex_source(src: str) -> ParsedTexFile` (writes `src` to a `tmp_path` file and calls `parse_tex_file`) and `run_rule(rule: Rule, src: str) -> list[Violation]` (constructs a single-file `ParsedDocument`, applies the rule's `check`, returns the list). Both exposed as pytest fixtures.

### Config loader (`texlint.config`)

- [ ] T013 [P] Write `tests/unit/test_config.py` covering: `ToolConfig()` defaults match the plan's documented defaults (journal=`jss`, mode=`author`, output=`terminal`, ignore_rules=empty, verbose=False, code_width=80); `.jss-lint.toml` values overlay defaults; CLI-flag values overlay file values (defaults < file < CLI); CLI flag **not set** by the user does NOT override a file value; `ignore_rules` normalised to `frozenset[str]` whether from CSV CLI or TOML list; unknown keys tolerated silently (warning printed only if `verbose=True`).
- [ ] T014 Implement `src/texlint/config.py`: import `tomllib` (Py≥3.11) or `tomli` (Py 3.10) behind a `sys.version_info` guard; `load(cli_overrides: dict, cwd: Path) -> ToolConfig` — build `ToolConfig()` defaults, deep-merge `.jss-lint.toml`, then deep-merge CLI overrides (only keys the user actually set). Return a frozen `ToolConfig`. Makes T013 pass.

### Rule engine (`texlint.core.engine`)

- [ ] T015 [P] Write `tests/unit/test_engine.py` covering: `load_journal("jss")` returns a `JSSJournal` instance via `importlib.metadata` — use `monkeypatch` or an in-process `EntryPoints` patch to avoid coupling to installation state; `load_journal("does-not-exist")` raises `JournalNotFoundError`; entry-point resolving to a non-`JournalRuleModule` raises `InvalidJournalError`; `run(config, parsed_document)` with a fabricated single-rule/single-category journal produces the correct `ComplianceReport` for (a) zero violations (status PASS, percentage 100.0), (b) one violation (status FAIL, percentage 0.0), (c) every rule in a category ignored (status SKIPPED, category excluded from percentage), (d) one `JSS-PARSE-000` violation on an input file (synthetic `parse` category appears, excluded from percentage), (e) every journal category SKIPPED (`compliance_percentage == None`); `Violation.sort_key()` applied consistently so `report.violations` is deterministically ordered; `rule.formats` filter excludes rules from files whose suffix is not in the set.
- [ ] T016 Implement `src/texlint/core/engine.py`: `load_journal(journal_id: str) -> JournalRuleModule` (uses `importlib.metadata.entry_points(group="texlint.journals")`, validates subclass + `id` match), `run(config: ToolConfig, parsed_document: ParsedDocument) -> ComplianceReport` (iterate rules, respect `ignore_rules`, respect `formats` via `ParsedDocument.files_for_rule`, collect + sort violations, compute `CategorySummary` with PASS/FAIL/SKIPPED, synthesise the `parse` category when any `JSS-PARSE-000` is present, compute `compliance_percentage` excluding SKIPPED and synthetic-`parse` categories). Makes T015 pass.

### `stub_journal` fixture (ABC conformance)

- [ ] T017 Rewrite `tests/fixtures/stub_journal/src/stub_journal/__init__.py` to define `class StubJournal(JournalRuleModule)` with `id = "stub"` and `categories()` returning `()`. Update `tests/fixtures/stub_journal/pyproject.toml` entry point from `stub = "stub_journal:JOURNAL"` to `stub = "stub_journal:StubJournal"`. Re-run `pip install -e tests/fixtures/stub_journal` to re-register the entry point.

### JSS smoke rules (TDD — test precedes impl; rule modules require 100% branch coverage per §IX)

- [ ] T018 [P] Write `tests/unit/journals/jss/test_cite_001_emph.py` — covers: `\emph{someref2020}` in prose flags `JSS-CITE-001`; `\emph{word}` (not a bibkey pattern) does not flag; `\cite{someref2020}` does not flag; line / column are the macro's 1-based position (validates api-boundary column conversion); file-format filter (`formats={".tex"}`) means a `.bib`-only `ParsedDocument` yields zero violations. Uses the `run_rule` fixture.
- [ ] T019 Implement `src/texlint/journals/jss/rules/cite_001_emph.py`: module-level `rule = Rule(id="JSS-CITE-001", category="citation", severity=Severity.WARNING, message_template=..., authority="JSS author instructions", check=_check, formats=frozenset({".tex"}))`. `_check` walks `ParsedTexFile.nodes` (depth-first), isinstance-filters `LatexMacroNode` with `macroname == "emph"`, inspects the first argument group for a bib-key regex (`[A-Za-z][\w-]*\d{2,4}` or similar). Makes T018 pass.
- [ ] T020 [P] Write `tests/unit/journals/jss/test_bib_001_year.py` — covers: entry missing `year` field flags `JSS-BIB-001` at 1-based line of `entry.start_line + 1`; entry with `year` does not flag; `@string` blocks (non-entry) don't flag; `formats={".bib"}` filter means a tex-only document yields zero violations.
- [ ] T021 Implement `src/texlint/journals/jss/rules/bib_001_year.py`: iterates `bib.library.entries`, flags entries whose `fields_dict` lacks a `year` key. Makes T020 pass.
- [ ] T022 [P] Write `tests/unit/journals/jss/test_src_001_width.py` — covers: line of length `code_width + 1` flags `JSS-SRC-001`; line of length `code_width` does not flag; `config.code_width = 120` from `ToolConfig` is honoured (proves rules read config, not globals); `formats=None` (applies to every file) confirmed; counting unit is Python `len(line)` on the decoded UTF-8 string (code-point count).
- [ ] T023 Implement `src/texlint/journals/jss/rules/src_001_width.py`: iterates over `(tex_file, line_number, line_text)` for every `.tex` and `.bib` file in `ParsedDocument`, flags any line whose `len(line.rstrip("\n"))` exceeds `config.code_width`. Makes T022 pass.

### JSS journal module

- [ ] T024 Implement `src/texlint/journals/jss/__init__.py`: `class JSSJournal(JournalRuleModule)` with `id = "jss"` and `categories()` returning a 3-tuple of `RuleCategory` instances (`citation`, `bibliography`, `typography`), each carrying its one rule. Rule modules imported **lazily** inside `categories()` so `import texlint` remains cheap. Authority strings on each rule are set per research.md §Smoke rules.

**Checkpoint**: `pytest tests/unit/` passes end-to-end. `python -c "from texlint.core.engine import load_journal; print(load_journal('jss').rules())"` returns three `Rule` instances. The `stub_journal` fixture loads as a `JournalRuleModule` subclass. **Ready to begin user stories.**

---

## Phase 3: User Story 1 — Author checks a manuscript before submission (Priority: P1)

**Goal**: An author runs `jss-lint paper.tex refs.bib` and sees violations grouped by file, coloured by severity, with correct exit status.

**Independent Test**: Running `jss-lint tests/fixtures/compliant/minimal.tex tests/fixtures/compliant/minimal.bib` exits 0 with empty terminal output; `jss-lint tests/fixtures/violations/JSS-CITE-001.tex` exits 1 with exactly one `JSS-CITE-001` violation rendered; `jss-lint tests/fixtures/violations/JSS-PARSE-000.tex` exits 2 with a `JSS-PARSE-000` violation rendered.

### Fixtures for US1 (reused by US2–US6)

- [ ] T025 [P] [US1] Create `tests/fixtures/compliant/minimal.tex` — hand-authored preamble + one `\cite{smith2020}` in prose, every line ≤80 chars, leading comment `% TODO(step-0.5): replace with docs/jss-template/article.tex preamble once Step 0.5 lands.` (research.md §Open items).
- [ ] T026 [P] [US1] Create `tests/fixtures/compliant/minimal.bib` — one BibTeX entry with every required field including `year`.
- [ ] T027 [P] [US1] Create `tests/fixtures/violations/JSS-CITE-001.tex` — minimal document with `\emph{smith2020}` in prose on a known line.
- [ ] T028 [P] [US1] Create `tests/fixtures/violations/JSS-BIB-001.bib` — one entry that lacks `year` and passes every other field check.
- [ ] T029 [P] [US1] Create `tests/fixtures/violations/JSS-SRC-001.tex` — a minimal compliant document with exactly one 81-character line.
- [ ] T030 [P] [US1] Create `tests/fixtures/violations/JSS-PARSE-000.tex` — intentionally malformed (unterminated `\begin{document}` group).

### Renderer + CLI for US1

- [ ] T031 [US1] Implement `src/texlint/output/terminal.py` author-mode renderer: `render(report: ComplianceReport, config: ToolConfig) -> None`. Uses `rich.console.Console(file=sys.stdout)`. Author mode: for each source file with at least one violation, emit `console.rule(f"[bold]{file}")` then a `rich.table.Table` with columns `line:col`, `severity` (coloured red/yellow), `rule_id`, `message`, `suggestion`. Reviewer-mode support is added in Phase 4.
- [ ] T032 [US1] Wire the CLI: replace the stub `main()` in `src/texlint/cli.py` with a full pipeline — parse click options into an overrides dict, call `config.load(...)`, resolve + parse each file path into a `ParsedDocument`, call `engine.load_journal(config.journal)` (maps `JournalNotFoundError` → stderr message + `sys.exit(2)`), call `engine.run(config, doc)`, dispatch to a renderer (only `terminal` wired in this phase; `json` and `html` raise a clear error until their phases land), determine exit code (`2` if any `JSS-PARSE-000` was produced or any invocation precondition failed; else `1` if any violation; else `0`), call `sys.exit(code)`.
- [ ] T033 [US1] Integration test `tests/integration/test_cli_author_terminal.py` — uses `click.testing.CliRunner()` (no `mix_stderr=`), asserts exit codes 0 / 1 / 2 against compliant, single-violation, and malformed fixtures; asserts author-mode output contains rule ids and file paths; asserts reviewer-mode assertions live in the US2 test, not here.
- [ ] T034 [US1] Integration test `tests/integration/test_cli_exit_codes.py` — unknown `--journal myjrn` → exit 2 with stderr mentioning the unknown id; missing file path → exit 2; `foo.md` (unsupported suffix) → exit 2; `--ignore-rules` referencing a nonexistent rule id → no error (silently tolerated, per spec Edge Case); stream separation assertion (renderer output on stdout, diagnostics on stderr).

**Checkpoint**: `jss-lint` is end-to-end usable in terminal author mode — the author workflow of User Story 1 is complete and reviewer/JSON/HTML phases can begin.

---

## Phase 4: User Story 2 — Reviewer sees compliance at a glance (Priority: P2)

**Goal**: `jss-lint --mode reviewer ...` prints a compact PASS/FAIL/SKIPPED table + overall `compliance_percentage`.

**Independent Test**: Compliant fixture in reviewer mode prints every category `PASS` and `100.0%`; injecting one violation into exactly one category prints that category `FAIL` and the rest `PASS`; `--ignore-rules JSS-CITE-001` on the compliant fixture prints `citation` as `SKIPPED` and excludes it from the percentage.

- [ ] T035 [US2] Extend `src/texlint/output/terminal.py` with a reviewer-mode branch: single `Table` titled `Journal compliance — {journal_id}`, columns `Category`, `Status` (PASS green / FAIL red / SKIPPED dim), `Applied`, `Passed`. Footer row `Overall: {compliance_percentage}%` (or `Overall: n/a` when the percentage is `None`). Synthetic `parse` category renders last.
- [ ] T036 [US2] Integration test `tests/integration/test_cli_reviewer_terminal.py` — compliant fixture → every journal-declared category `PASS`, percentage `100.0`; one-violation fixture → correct FAIL row; `--ignore-rules` covering every rule in `citation` → `citation` row reads `SKIPPED` and the percentage is computed over the remaining PASS+FAIL subset.

---

## Phase 5: User Story 3 — CI integration via machine-readable output (Priority: P2)

**Goal**: `jss-lint --output json ...` emits a deterministic JSON document matching `contracts/json-output.md`, regardless of exit code.

**Independent Test**: Two consecutive runs on the same input produce byte-identical stdout; malformed input yields a valid JSON document whose `violations` includes `JSS-PARSE-000` and whose exit code is 2.

- [ ] T037 [US3] Implement `src/texlint/output/json_output.py`: `render(report: ComplianceReport, config: ToolConfig) -> None` — build a plain `dict` (path fields rendered via `Path.as_posix()`, `compliance_percentage` rounded with `round(x, 1)`), serialise with `json.dumps(payload, indent=2, sort_keys=True)`, write to `sys.stdout`. Then update `src/texlint/cli.py` dispatch to route `--output json` to this renderer.
- [ ] T038 [US3] Integration test `tests/integration/test_cli_json.py` — byte-determinism (two invocations produce identical stdout); JSON conforms to `contracts/json-output.md` top-level keys and field-level types; `tool_version` matches `texlint.__version__`; `categories` array includes the synthetic `parse` entry iff parse errors were produced; `compliance_percentage` excludes SKIPPED and synthetic `parse`; exit 2 on malformed input still emits valid parseable JSON on stdout.

---

## Phase 6: User Story 4 — HTML output for sharing and archival (Priority: P3)

**Goal**: `jss-lint --output html --mode author|reviewer ...` emits a self-contained HTML document on stdout.

**Independent Test**: For each mode, the rendered HTML is well-formed, contains every violation/category shown in the corresponding JSON, and is stable across runs.

- [ ] T039 [P] [US4] Author-mode template at `src/texlint/output/templates/author.html.j2`: `<html>` / `<head>` with inline `<style>` block, `<body>` with one `<section>` per source file containing a `<table>` of violations (line:col, severity, rule_id, message, suggestion). No external CSS, no JavaScript.
- [ ] T040 [P] [US4] Reviewer-mode template at `src/texlint/output/templates/reviewer.html.j2`: summary `<table>` of categories with status / applied / passed / violations-count columns, `<h1>` overall percentage, inline `<style>`.
- [ ] T041 [US4] Implement `src/texlint/output/html_output.py`: `render(report, config)` builds a `jinja2.Environment(loader=PackageLoader("texlint.output", "templates"), autoescape=True)`, selects the template by mode, renders to stdout. Update `src/texlint/cli.py` dispatch to route `--output html`.
- [ ] T042 [US4] Integration test `tests/integration/test_cli_html.py` — author mode contains each expected violation field; reviewer mode contains the category table; output is parseable by `html.parser`; two runs produce byte-identical output.

---

## Phase 7: User Story 5 — Repo-local configuration (Priority: P3)

**Goal**: `.jss-lint.toml` in CWD is honoured; CLI flags override it.

**Independent Test**: With a config file setting `ignore_rules = ["JSS-CITE-001"]` in a CWD, `jss-lint tests/fixtures/violations/JSS-CITE-001.tex` exits 0; adding `--ignore-rules ""` on the CLI for the same run produces exit 1 (CLI clears the ignore set).

The underlying `config.load()` shipped in T014; this phase adds the end-to-end integration proof.

- [ ] T043 [US5] Integration test `tests/integration/test_cli_config_merge.py` — uses `CliRunner`'s `isolated_filesystem()` to place a `.jss-lint.toml` in the working directory; asserts TOML-only config applies; asserts CLI flag overrides TOML on a shared key; asserts an unknown key in TOML emits a warning on stderr only when `--verbose` is set and does not otherwise change behaviour.

---

## Phase 8: User Story 6 — Third-party journal extension (Priority: P3)

**Goal**: A second journal, registered exclusively via `texlint.journals` entry points, dispatches correctly under `--journal <id>` — with zero edits to files under `src/texlint/core/` or `src/texlint/api.py`.

**Independent Test**: `jss-lint --journal stub tests/fixtures/compliant/minimal.tex` exits 0 with no violations (StubJournal has no rules); `jss-lint --journal does-not-exist tests/fixtures/compliant/minimal.tex` exits 2; `git diff HEAD -- src/texlint/core/ src/texlint/api.py` is empty across the commits in this phase.

The engine's entry-point discovery shipped in T016 and the StubJournal fixture shipped in T017; this phase closes the loop with a user-visible integration test.

- [ ] T044 [US6] Integration test `tests/integration/test_plugin_discovery.py` — `--journal stub` dispatches to `StubJournal` (verify via a debug probe on engine.load_journal or by checking `stub` produces zero violations even when the `jss` smoke rules would have flagged the input); `--journal does-not-exist` → exit 2 with stderr naming the unknown journal.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Gate checks and usability polish that cuts across every story.

- [ ] T045 Run the mandatory branch-coverage gate (Constitution §IX): `pytest --cov=src/texlint/journals/jss/rules --cov-branch --cov-fail-under=100 --cov-report=term-missing tests/unit/journals/jss/`. Must pass at 100%. Any missing branch is a blocker; add tests or simplify the rule.
- [ ] T046 [P] Update `README.md` with: install command, minimal `jss-lint` invocation, pointer to `specs/001-linter-foundation/quickstart.md`. Remove any references to "stub — rules not yet implemented" now that rules ship.
- [ ] T047 [P] Add a short CHANGELOG entry at the repo root (`CHANGELOG.md`) recording this as version `0.1.0` and listing the three shipped smoke rules. Establishes the precedent for the "breaking JSON change requires major bump + CHANGELOG entry" stability contract (spec Clarification Q2 / FR-014).
- [ ] T048 Manual quickstart walkthrough: execute every CLI example from `specs/001-linter-foundation/quickstart.md` § "Try every renderer and mode" against the shipped fixtures. Each must produce output consistent with the spec's acceptance scenarios.

---

## Dependencies & Execution Order

### Phase dependencies

- **Setup (Phase 1)** → immediate start; no dependencies.
- **Foundational (Phase 2)** → depends on Setup; **blocks every user story.**
- **User Story phases (Phase 3–8)** → each depends on Foundational; may run in parallel (see §Parallel Opportunities) or sequentially in priority order (P1 → P2 → P3).
- **Polish (Phase 9)** → depends on all intended user stories being complete.

### Within phases

- **Phase 2**: `api.py` (T006/T007) comes first — every other foundational module imports from it. After that, `parser → conftest → config → engine → stub_journal fix → rules → JSSJournal`. The three rules (T018–T023) are independent of each other and can run in parallel.
- **Phases 3–8 (user stories)**: within each story, test tasks (where present) run before their implementation, except for rule tests which are ordered explicitly in §Phase 2.
- **Phase 9**: T045 depends on all rule tests from Phase 2 and all integration tests from Phases 3–8 being green. T046/T047 are independent of T045 and of each other. T048 runs last.

### Cross-story independence

All six user stories build on the same foundational work and touch different renderer files (plus `cli.py` for dispatch wiring). They can be implemented in parallel by different developers once Phase 2 is checkpoint-green. `cli.py` is the only shared file; coordinate small dispatch-branch edits through PRs.

---

## Parallel opportunities

### Phase 1

- T002, T003, T004 all touch different directories — run in parallel.

### Phase 2

- T006 (api test), T008 (parser_tex test), T010 (parser_bib test), T013 (config test), T015 (engine test), T018/T020/T022 (rule tests) can be authored in parallel by different developers. Each implementation task depends only on its paired test task.
- The three rule impl tasks (T019, T021, T023) each live in their own file and are independent; they run in parallel once their test tasks exist.
- T025–T030 (fixtures) are entirely independent text files.

### Phase 6

- T039 and T040 (the two Jinja2 templates) are separate files — run in parallel.

### Phase 9

- T046 and T047 (README and CHANGELOG) are independent documentation edits.

### Cross-phase

- Once Phase 2 is checkpoint-green, Phases 3, 4, 5, 6, 7, and 8 can all begin in parallel. If delivering serially instead, follow the priority order P1 → P2 → P3.

---

## Implementation Strategy

This plan delivers the full foundation in one pass. No phase is gated on a future re-implementation step; no public surface is shipped in a half-finished state. Ship `0.1.0` once Phase 9 is green.

### Serial path (single developer)

1. Phase 1: Setup (T001–T005)
2. Phase 2: Foundational (T006–T024)
3. Phases 3–8: user stories in priority order — P1 (T025–T034), then the two P2 stories (T035–T038), then the three P3 stories (T039–T044). Each story phase is a complete, independently testable increment; the order within the same priority tier is developer's choice.
4. Phase 9: Polish (T045–T048). Release `0.1.0`.

### Parallel path (multi-developer)

Once **Phase 2 is checkpoint-green** (all unit tests pass on api/parser/engine/config/rules), Phases 3–8 touch distinct renderer files and can run in parallel. The one coordination point is `src/texlint/cli.py`'s output-dispatch block, which US1/US3/US4 each extend — either merge their small dispatch edits serially, or have one developer own `cli.py` and fold the renderer hooks in as each renderer lands.

With three developers after the Phase 2 gate:

- **Dev A** — Phase 3 (terminal author mode) then Phase 4 (reviewer extension), then Phase 6 (HTML renderer + templates).
- **Dev B** — Phase 5 (JSON renderer) then Phase 7 (config integration proof) then Phase 8 (plugin discovery proof).
- **Dev C** — Phase 9: starts T046/T047 (README + CHANGELOG) as soon as Phase 3 locks the author-mode surface; T045 (branch-coverage gate) and T048 (manual quickstart walkthrough) run after all other phases land.

### Nothing is deferred to a future re-implementation step

- The data model (`texlint.api`) is fully specified in `data-model.md`. `FixSuggestion` ships with the minimal `description: str` field; Step 4 will add offset/replacement fields additively.
- Every renderer's contract is locked: terminal (`research.md §Terminal rendering`), JSON (`contracts/json-output.md`), HTML (`research.md §HTML`).
- The plugin mechanism (`contracts/journal-plugin.md`) is fully specified; Phase 8's integration test proves it, no placeholder.
- The three smoke rules have concrete authority citations (research.md §Smoke rules) and complete branch coverage is gated by T045.

The one hand-authored concession is the compliant fixture preamble (research.md §Open items, T025): it uses a minimal preamble rather than the full `docs/jss-template/article.tex` preamble until Step 0.5 lands that file. This is a ~5-line LaTeX stand-in and does not affect any code path.

---

## Notes

- `[P]` marks tasks in different files with no dependencies on an incomplete task in the same phase — safe to parallelise.
- `[US#]` maps a task to the user story it serves; Setup / Foundational / Polish carry no `[US#]` label.
- Constitution §VIII (TDD) is enforced explicitly for rule modules: rule test task ID < rule implementation task ID throughout Phase 2.
- Constitution §IX (100% branch coverage on rule modules) is gated by T045 in Phase 9; CI must run that invocation on every PR.
- Constitution §IV (zero core edits to add a journal) is continuously observable: T044 explicitly checks `git diff -- src/texlint/core/ src/texlint/api.py` stays empty across Phase 8.
- Commit after each task or tight logical group; keep rule commits self-contained so `git log src/texlint/journals/jss/rules/` tells the story of rule introduction.
