# Changelog

All notable changes to `jss-style-checker` land here. Version numbers follow
[semantic versioning](https://semver.org/). Breaking changes to the
JSON-output shape (see
`specs/001-linter-foundation/contracts/json-output.md`) require a major
version bump and an entry in this file — see the spec's Clarification Q2.

## [Unreleased]

### Added

- `eval-jss`, a companion CLI for measuring per-rule precision of
  `jss-lint` against a real-world corpus. Implements Constitution §VI
  (≥90% precision per rule) as an enforceable gate and §XII (reproducible
  corpus) via a pinned `eval/corpus-manifest.csv` with SHA256 per
  paper. Full spec at `specs/002-eval-jss-harness/`.
- Subcommands: `init`, `scan`, `human-review`, `review` (AI-assisted),
  `report` (with `--csv` history and `--by-source` breakdown),
  `corpus fetch`, `corpus status`.
- Package layout: top-level `eval/`. Dependencies: stdlib + existing
  `click` + `rich` — no new runtime deps.
- AI review backend: pinned to `llama.cpp`'s `llama-server` hosting
  `unsloth/Qwen3-30B-A3B-GGUF:UD-Q4_K_XL` with greedy decoding (spec
  clarification session 2026-04-23).
- Phase A corpus: 3 placeholder vignettes under `examples/` exercising
  the `JSS-CITE-001` / `JSS-SRC-001` / clean code paths; the 10-paper
  real-CRAN corpus is planned follow-up work.

### Packaging note

`eval-jss` is registered as a console script. The `eval` Python module
is included in the wheel; this differs from the plan's original
"`eval/` deliberately outside the wheel" design decision. Reason:
Hatchling's editable install only exposes `wheel.packages`, so
excluding `eval/` from the wheel produced a broken `eval-jss` binary.
Small wheel bloat accepted in exchange for a working end-user install.

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
