# Changelog

All notable changes to `jss-style-checker` land here. Version numbers follow
[semantic versioning](https://semver.org/). Breaking changes to the
JSON-output shape (see
`specs/001-linter-foundation/contracts/json-output.md`) require a major
version bump and an entry in this file — see the spec's Clarification Q2.

## [0.1.0] — 2026-04-22

First foundation release. Framework + smoke-test rule set.

### Added

- Public data model in `texlint.api`: `Violation`, `Rule`, `RuleCategory`,
  `CategorySummary`, `ComplianceReport`, `ToolConfig`, `ParsedTexFile`,
  `ParsedBibFile`, `ParsedDocument`, `JournalRuleModule` (ABC), `FixSuggestion`
  (reserved, unused until Step 4), `Severity`, `CategoryStatus`,
  `JournalNotFoundError`, `InvalidJournalError`.
- Core parser `texlint.core.parser` with non-raising `.tex` / `.bib` parsing;
  non-UTF-8 and LaTeX / BibTeX failures surface as `JSS-PARSE-000`
  violations on the returned object.
- Rule engine `texlint.core.engine` with `importlib.metadata`-based journal
  loading and compliance-percentage derivation (excludes `SKIPPED` and the
  synthetic `parse` category).
- Config loader `texlint.config` merging built-in defaults, `.jss-lint.toml`,
  and CLI flags in that precedence.
- CLI entry point `jss-lint` (via `click`) with `--journal`, `--mode`,
  `--output`, `--ignore-rules`, `--verbose`; exit codes `0` / `1` / `2`.
- Output renderers: terminal (`rich`, author + reviewer modes), JSON
  (byte-deterministic), HTML (Jinja2 with packaged templates).
- Journal plugin: `jss` registered via the `texlint.journals` entry-point
  group. Smoke rules (each with 100% branch coverage per Constitution §IX):
  - `JSS-CITE-001` — `\emph{bibkey}` used for citation markup.
  - `JSS-BIB-001` — bibliography entry missing a `year` field.
  - `JSS-SRC-001` — source line exceeds `code_width` (default 80).
- Test fixtures under `tests/fixtures/compliant/` and
  `tests/fixtures/violations/`, plus a second-journal
  `tests/fixtures/stub_journal/` package proving zero-core-edit extensibility
  (Constitution §IV).

### JSON output contract

Top-level keys in the `--output json` payload — `tool_version`,
`journal_id`, `compliance_percentage`, `categories`, `violations` — are
**additive-only** within a single major version. Adding fields is a minor
version bump; removing or renaming fields requires a major version bump and
an entry in this file.

### Deferred

- `.Rnw` / `.Rmd` dispatch — Step 3.
- `--fix` / `--dry-run` and the `FixSuggestion` payload fields — Step 4.
- Full 53-rule JSS catalogue — Step 2.
- `eval-jss` precision-evaluation CLI and the ≥90% precision gate
  (Constitution §VI) — Step 5.
