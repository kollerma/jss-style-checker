# Feature Specification: Linter Foundation — `jss-style-checker` Core

**Feature Branch**: `001-linter-foundation`
**Created**: 2026-04-22
**Status**: Draft
**Input**: User description: "Build the foundation of `jss-style-checker`: a deterministic, rule-based LaTeX style linter that takes `.tex` + `.bib` files and produces a compliance report. Framework + minimal smoke-test rule set; full JSS rule catalogue is a later spec."

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Author checks a manuscript before submission (Priority: P1)

A researcher preparing a Journal of Statistical Software (JSS) submission has a `.tex` manuscript and its accompanying `.bib` bibliography on disk. They run the linter against those files and see a concrete list of style problems they can fix: file, line, (optionally) column, the rule that fired, a human message, and, where available, a suggestion. The report is grouped by file so they can fix one file at a time. The process exits with a distinct status so their shell or editor integration can tell "clean" from "has violations" from "the tool could not run".

**Why this priority**: This is the only reason the tool exists from the author's perspective. Without a usable author-mode report on the command line, there is no product — every other surface (reviewer mode, JSON, HTML, configuration) is in service of this core loop.

**Independent Test**: Given the compliant fixture (`tests/fixtures/compliant/minimal.tex` + `minimal.bib`), running the CLI in author mode exits 0 and prints no violations. Given a violation fixture, the CLI exits 1 and prints exactly the violations that fixture is designed to trigger, with correct file/line information.

**Acceptance Scenarios**:

1. **Given** a `.tex` file and a `.bib` file that satisfy every smoke-test rule, **When** the author runs the linter against them, **Then** the process exits with status 0 and the terminal output contains no violations.
2. **Given** a `.tex` file that violates one smoke-test rule on a specific line, **When** the author runs the linter, **Then** the output names that file, that line, that rule, and a human-readable message, and the process exits with status 1.
3. **Given** a `.tex` file and a `.bib` file where the `.tex` file cannot be parsed, **When** the author runs the linter, **Then** the process still produces a report (it does not crash), the parse failure is itself reported as a violation, and the process exits with status 2.
4. **Given** a run that produces violations, **When** the author inspects the terminal output, **Then** violations are grouped by source file and severity is visually distinguishable (error vs. warning).

---

### User Story 2 — Reviewer sees compliance at a glance (Priority: P2)

A JSS reviewer or section editor receives a submission and wants an at-a-glance picture of how compliant the manuscript is, organised by rule category rather than by individual violation. They run the tool in reviewer mode and get a compact per-category table showing `PASS` or `FAIL` for each category plus an overall compliance percentage.

**Why this priority**: This is how editorial triage actually uses the tool. An author wants the violation list; a reviewer wants the summary. Without reviewer mode, the tool still works for authors but cannot replace the manual checklist reviewers use today.

**Independent Test**: Running the tool in reviewer mode on a manuscript that violates one rule from exactly one category prints a table where that category is `FAIL`, every other category is `PASS`, and the overall compliance percentage equals (categories with zero violations) / (total categories) expressed as a percentage.

**Acceptance Scenarios**:

1. **Given** a manuscript with zero violations, **When** run in reviewer mode, **Then** every category row shows `PASS` and the overall compliance percentage is 100%.
2. **Given** a manuscript that violates one rule in one category, **When** run in reviewer mode, **Then** that category shows `FAIL`, the others show `PASS`, and the overall percentage reflects the proportion of categories that passed.
3. **Given** the same manuscript, **When** run in author mode instead, **Then** the output shows per-violation detail and not the category table.

---

### User Story 3 — CI integration via machine-readable output (Priority: P2)

A maintainer wants to gate merges or releases on JSS style compliance. They run the linter in a CI job, request JSON output, and pipe the result into a downstream checker, dashboard, or diff tool. The JSON must be deterministic (same input ⇒ byte-identical output) so that CI can diff yesterday's report against today's and highlight only real changes, and must carry the tool version so results can be reproduced later.

**Why this priority**: JSON output unlocks the whole integration surface — editor plugins, CI, pre-commit hooks, dashboards — without which the tool is limited to interactive shells. Tied with Story 2 because both are secondary to the author loop but both are required for the foundation to be useful beyond a single developer.

**Independent Test**: Running the tool twice on the same input with `--output json` produces byte-identical output. The JSON contains top-level `violations`, `categories`, `compliance_percentage`, and `tool_version` keys, and the process's exit status still follows the author-mode convention (0 clean / 1 violations / 2 invocation error).

**Acceptance Scenarios**:

1. **Given** identical inputs, **When** the tool is run twice with JSON output, **Then** the two JSON outputs are byte-identical.
2. **Given** a run that produces violations, **When** JSON output is requested, **Then** the JSON contains every violation shown in author mode, plus the category summary shown in reviewer mode, plus an overall compliance percentage, plus the tool version string.
3. **Given** a malformed input file, **When** JSON output is requested, **Then** the parse failure appears as a violation inside the JSON (the tool does not crash) and the exit status is 2.

---

### User Story 4 — HTML output for sharing and archival (Priority: P3)

A reviewer or editor wants to share a compliance report with an author or archive it alongside the submission. They request HTML output and get a rendered report — one layout for authors (violation detail) and one layout for reviewers (category summary) — suitable for viewing in a browser or attaching to editorial records.

**Why this priority**: HTML is the archival / hand-off format. It is not needed for the core author or CI loops but is needed by editorial staff and by the eventual web-facing report. Shipping it now avoids retrofitting templating into an already-shipped output layer.

**Independent Test**: For each mode, running the tool with `--output html` on a known fixture produces an HTML document that (a) is well-formed, (b) contains every violation or category present in the corresponding JSON output, and (c) is stable across runs.

**Acceptance Scenarios**:

1. **Given** author mode and HTML output, **When** the tool runs on a manuscript with violations, **Then** the HTML shows each violation with file, line, rule, severity, message, and (if present) suggestion.
2. **Given** reviewer mode and HTML output, **When** the tool runs on the same manuscript, **Then** the HTML shows the per-category PASS/FAIL table and the overall compliance percentage.

---

### User Story 5 — Repo-local configuration (Priority: P3)

A project maintainer commits a configuration file at the root of the manuscript repository so that every contributor gets the same journal target, mode, and ignored-rule set by default, without having to remember CLI flags. An individual contributor can still override any value at the command line for a one-off run.

**Why this priority**: Configuration makes the tool usable by teams, not just individuals, but the tool is already useful without it. P3 because it is a convenience wrapper over behaviour that already exists via CLI flags.

**Independent Test**: With a `.jss-lint.toml` at the current working directory that sets `ignore_rules = ["R001"]`, running the tool suppresses `R001` violations. Running the same invocation with an explicit CLI flag that overrides that value produces the overridden behaviour, demonstrating the precedence order.

**Acceptance Scenarios**:

1. **Given** a `.jss-lint.toml` that names rules to ignore, **When** the tool runs, **Then** violations for those rules are not reported.
2. **Given** the same config file and a CLI flag that changes the ignored-rules set, **When** the tool runs, **Then** the CLI flag wins.
3. **Given** no config file and no CLI flags, **When** the tool runs, **Then** built-in defaults apply.

---

### User Story 6 — Third-party journal extension (Priority: P3)

A contributor or downstream packager wants to support a journal other than JSS without forking the core. They publish a Python package that registers a new journal through the standard plugin mechanism, and the existing tool picks it up at runtime based on the `--journal` flag.

**Why this priority**: This is architectural insurance, not immediate user value. Only the `jss` journal ships in this step, but the mechanism MUST be in place now (Constitution Principle IV: adding a journal MUST NOT require editing core files). Retrofitting a plugin boundary after the fact is expensive; carving it in up front is cheap.

**Independent Test**: A separate test fixture package (or a test-only entry-point registration) exposes a second journal module. Running the tool with `--journal <fixture-id>` dispatches to that module's rules rather than to `jss`, without any edit to the core source tree.

**Acceptance Scenarios**:

1. **Given** only the JSS journal is installed, **When** the tool is run with `--journal jss`, **Then** JSS rules are applied.
2. **Given** a second journal registered via the plugin mechanism, **When** the tool is run with `--journal <id>`, **Then** that journal's rules are applied in place of JSS.
3. **Given** `--journal <unknown-id>`, **When** the tool is run, **Then** the tool fails with exit status 2 and a clear error, without applying any rules.

---

### Edge Cases

- **Malformed `.tex`**: parse error is recorded as a `Violation` on the parsed result; the report is still produced; exit status is 2.
- **Malformed `.bib`**: same handling as malformed `.tex` — a violation, not a crash.
- **Missing file path on the command line**: exit status 2 with an error identifying the missing file.
- **Unknown `--journal` identifier**: exit status 2.
- **`ignore_rules` references a rule id that does not exist**: honoured silently (the referenced rule simply does not exist to be ignored); the tool does not fail, because configuration is shared across tool versions and rule ids may be added or removed.
- **Rule `formats` filter**: a rule declared for a format other than `.tex` or `.bib` is skipped for this step's inputs; a rule with `formats = None` is applied to every input. (`.Rnw` / `.Rmd` support is explicitly out of scope for this step.)
- **A file whose extension is neither `.tex` nor `.bib`**: rejected at CLI parse time with exit status 2.
- **Deterministic output ordering**: when two violations would sort identically by file+line+column, a secondary key on rule id MUST break the tie so that output is a total order.

## Requirements *(mandatory)*

### Functional Requirements

**Inputs & invocation**

- **FR-001**: The tool MUST accept one or more file paths on the command line. Supported file types in this step are `.tex` and `.bib`. Other extensions MUST be rejected at invocation time.
- **FR-002**: The tool MUST accept the following command-line options: `--journal` (journal identifier, default `jss`), `--mode` (`author` or `reviewer`, default `author`), `--output` (`terminal`, `json`, or `html`, default `terminal`), `--ignore-rules` (comma-separated list of rule identifiers to suppress), and `--verbose` (increased diagnostic output).
- **FR-003**: The tool MUST read a configuration file named `.jss-lint.toml` from the current working directory if one exists, merge it with built-in defaults, and allow any value to be overridden by a CLI flag. Precedence, lowest to highest, MUST be: built-in defaults < configuration file < CLI flags.

**Parsing**

- **FR-004**: The tool MUST parse `.tex` files into an abstract representation usable by rule checks, and MUST parse `.bib` files into a structured representation of bibliography entries.
- **FR-005**: A failure to parse a file MUST NOT raise an exception out of the tool. Instead, the parse failure MUST be recorded as a violation on the returned parsed object, with a severity appropriate for "tool could not process this file".

**Rule engine**

- **FR-006**: The tool MUST discover journal rule modules at runtime via a standard Python entry-point mechanism, such that adding a new journal requires only installing a package that registers the appropriate entry point — NO edit to the tool's core source tree MAY be required.
- **FR-007**: The tool MUST run every enabled rule from the selected journal against the parsed document, collect all resulting violations, and produce a single compliance report.
- **FR-008**: Each rule MAY declare the set of file formats it applies to. A rule that declares no formats MUST be treated as applying to all formats. A rule that declares a specific format set MUST only be applied to files of those formats.
- **FR-009**: The engine MUST suppress any rule whose identifier appears in the effective ignored-rules list.
- **FR-010**: The compliance report MUST include, per rule category, a PASS/FAIL summary (FAIL iff at least one violation in that category) and an overall compliance percentage equal to (categories with zero violations) / (total categories applied).

**Violations**

- **FR-011**: Every violation MUST carry: a source file path, a line number, an optional column number, the rule identifier, a severity of either `error` or `warning`, a human-readable message, and an optional suggestion.
- **FR-012**: The violation data model MUST include a field for a structured fix suggestion, but that field MUST remain unused in this step; auto-fix is out of scope until a later step.

**Output**

- **FR-013**: In terminal mode, the tool MUST render violations in a human-readable form, group them by source file, and visually distinguish severities (e.g., by colour). In author mode the output MUST surface individual violations; in reviewer mode the output MUST surface the per-category compliance table.
- **FR-014**: In JSON mode, the tool MUST emit a single JSON document with, at minimum, top-level fields `violations`, `categories`, `compliance_percentage`, and `tool_version`. The JSON MUST be deterministic: identical input MUST produce byte-identical output across runs and hosts.
- **FR-015**: In HTML mode, the tool MUST emit a rendered HTML report using a distinct template per mode (author / reviewer). Templates MUST be packaged with the tool so it works with no external template configuration.

**Exit status**

- **FR-016**: The tool MUST exit with status `0` when no violations are produced, status `1` when any violations are produced (including parse-error violations that are non-fatal at the rule-engine level but indicate issues in the manuscript), and status `2` when the tool itself could not complete its work — specifically: unknown CLI option, unknown `--journal`, missing or unreadable input file, or any parse failure.

**Initial rule content**

- **FR-017**: This step MUST ship the `jss` journal with between 3 and 5 smoke-test rules that together exercise the three principal rule shapes the tool will need to support: at least one rule that inspects the LaTeX AST, at least one rule that inspects parsed BibTeX entries, and at least one rule that scans raw source text. The full JSS rule catalogue is explicitly out of scope here — its population is deferred to a separate specification.

### Key Entities

- **Violation**: A single detected style issue. Carries file, line, optional column, rule identifier, severity (error | warning), human-readable message, optional textual suggestion, and a fix-suggestion slot reserved for the later auto-fix step.
- **Rule**: A named check belonging to a category, with metadata (identifier, severity, message template, applicable file formats) and a callable that inspects a parsed document and returns zero or more violations.
- **Rule Category**: A named grouping of rules (e.g., "bibliography", "typography"). Used by the reviewer-mode summary.
- **Category Summary**: For a single category, the total number of rules applied, the number that passed, and the derived PASS/FAIL verdict.
- **Compliance Report**: The whole output of one tool run: the flat list of violations, the per-category summaries, the overall compliance percentage, and the tool version.
- **Tool Configuration**: The merged result of built-in defaults, the `.jss-lint.toml` file, and CLI flags. Drives journal selection, mode, output format, ignored-rules set, and verbosity.
- **Parsed Tex File / Parsed Bib File**: The structured representation of a single input file, carrying either a usable AST / entry list or a parse-error violation in lieu of it.
- **Parsed Document**: The aggregation of all parsed input files presented to the rule engine as a single unit of work.
- **Journal Rule Module**: The plugin contract. A journal exposes a stable identifier, a list of categories, and the rules belonging to each. Journals are discovered by entry point, never by hard-coded import.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An author can run the tool on the compliant fixture (`.tex` + `.bib`) and see a clean report with exit status 0, with no setup beyond installing the package.
- **SC-002**: An author can run the tool on each violation fixture and see exactly the violations that fixture was designed to trigger (no extra false positives from other smoke rules), with exit status 1.
- **SC-003**: The JSON output for a given input is byte-identical across two consecutive runs on the same host.
- **SC-004**: A malformed `.tex` file and a malformed `.bib` file each produce a compliance report rather than an exception, and the tool exits with status 2.
- **SC-005**: Adding a second journal to the tool requires zero edits to files under the tool's core package — it is registered entirely through the plugin mechanism. (Demonstrated with a test-only fixture journal.)
- **SC-006**: Every smoke-test rule shipped in the `jss` journal achieves 100% branch coverage under the project's test suite. (Constitution Principle IX.)
- **SC-007**: A reviewer running the tool in reviewer mode sees a per-category PASS/FAIL table and an overall compliance percentage, and does not have to scan individual violation lines to get that summary.
- **SC-008**: The tool's exit codes are stable and documented: `0` clean, `1` violations found, `2` tool could not complete — consumable by CI without parsing stdout.
- **SC-009**: On a typical single-chapter JSS manuscript (tens of `.tex` files, one `.bib`), a full run completes in under 5 seconds on ordinary developer hardware, so the tool is usable in an interactive edit loop.

## Assumptions

- The implementation language and ecosystem are Python, matching the existing `pyproject.toml` in the repository root; the CLI is distributed as a Python console script.
- LaTeX parsing is delegated to `pylatexenc.latexwalker`; BibTeX parsing is delegated to `bibtexparser` v2. These choices are part of the technical contract the user fixed in the feature description and therefore live here rather than being rediscovered during `/speckit.plan`.
- Terminal rendering uses `rich`; HTML rendering uses Jinja2 templates bundled with the package under `src/texlint/output/templates/` (`author.html.j2`, `reviewer.html.j2`); the CLI is built with `click`.
- Journal discovery uses `importlib.metadata` entry points in the group `texlint.journals`. A single `jss` journal is registered in this step; the mechanism itself is tested against a fixture journal.
- The public data model lives in `texlint.api`; the rule engine in `texlint.core.engine`; parsers in `texlint.core.parser`; configuration handling in `texlint.config`; the CLI in `texlint.cli`; output renderers in `texlint.output.{terminal,json_output,html_output}`. These module boundaries are part of the user-supplied contract and will be honoured by the plan.
- `.Rnw` and `.Rmd` source formats are explicitly deferred to a later step. Rules that would apply to those formats are not shipped here.
- `--fix` / `--dry-run` functionality is explicitly deferred. The `FixSuggestion` field on violations is reserved but unused.
- The full JSS rule catalogue (53 rules) is explicitly deferred to the next specification. This step ships only 3–5 smoke-test rules chosen to exercise the three rule shapes (LaTeX AST, BibTeX entry, raw source scan).
- The `eval-jss` evaluation CLI and the precision quality gate (Constitution Principle VI) are explicitly deferred to a later step; this step's success criteria are functional-correctness criteria, not precision criteria.
- Rule output ordering is total: primary key file, then line, then column (absent columns sorting before present ones), then rule identifier. This keeps JSON output deterministic without requiring rules to cooperate.
- An `ignore_rules` entry that names a rule identifier which does not exist in the selected journal is silently accepted, so that configuration files remain portable across tool versions as rules are added or renamed.
