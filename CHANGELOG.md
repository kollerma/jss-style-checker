# Changelog

All notable changes to `jss-style-checker` land here. Version numbers follow
[semantic versioning](https://semver.org/). Breaking changes to the
JSON-output shape (see
`specs/001-linter-foundation/contracts/json-output.md`) require a major
version bump and an entry in this file — see the spec's Clarification Q2.

## [Unreleased]

### Changed

- **Degraded-parse exit semantics.** Only error-severity
  `JSS-PARSE-000` findings force exit 2. Warning-severity parse
  findings mark a *recovered* parse (the file was fully linted, e.g.
  after an encoding fallback) and obey the normal `--fail-on`
  threshold like any other finding. Previously any `JSS-PARSE-000`
  finding exited 2.
- The LSP server lints the in-memory editor buffer directly instead
  of writing it to the file on disk. Unsaved edits no longer hit the
  filesystem, file encodings are preserved, and opening a file no
  longer bumps its mtime.

### Added

- **VS Code settings are now honoured by the LSP server.**
  `jssStyleChecker.ignoreRules` (unioned with `ignore_rules` from
  `.jss-lint.toml`), `jssStyleChecker.severityOverrides` (per-rule,
  client wins over the file), `jssStyleChecker.codeWidth`, and
  `jssStyleChecker.runOn` (`"save"` lints on save only). Settings
  changes re-lint open documents immediately.
- `severity_overrides` config key (`[severity_overrides]` table in
  `.jss-lint.toml`): per-rule severity remap applied centrally in the
  engine so terminal/JSON/SARIF/LSP output and the exit-code policy
  all agree.

- Per-rule measured-precision **confidence tiers**. The catalogue now
  carries an optional `confidence` key (`high` default / `medium` /
  `low`) sourced from the eval-jss precision history; the four
  sub-90%-precision rules at iter-78 are tiered (`JSS-CAP-003` low;
  `JSS-CITE-002`, `JSS-CAP-002`, `JSS-MARKUP-001` medium). The tier
  surfaces in the terminal table (dim marker under the rule id), the
  JSON `confidence` field, and `jss-lint explain`. New
  `--min-confidence {low,medium,high}` flag (and `min_confidence`
  config key) skips rules below the floor, reporting them as skipped
  rules; default `low` runs everything.
- `--fail-on {error,warning,info}` flag (and `fail_on` config key):
  the minimum violation severity that exits 1. Default `info` keeps
  the historical behaviour (any violation fails); `--fail-on error`
  stops info/warning advisories (e.g. the missing-DOI rule) from
  flipping CI red while still reporting them. Parse errors always
  exit 2.
- Inline suppression: `% jss-lint: ignore [RULE-IDS]` on a finding's
  line (or on a comment-only line directly above it) silences matching
  findings in place, so one false positive no longer forces disabling a
  whole rule via `--ignore-rules`. Bare `ignore` suppresses every rule
  on the target line; trailing free text is treated as rationale; parse
  errors (`JSS-PARSE-000`) are never suppressed. Works in `.tex`,
  `.Rnw`/`.Rmd` LaTeX islands, and `.bib` files (a directive line above
  an entry covers findings reported on the entry's first line).
- `texlint.api.VERBATIM_ENVS` / `CODE_DISPLAY_ENVS` / `LISTING_ENVS`:
  shared contract for "this environment's body is not prose", consumed
  by both the parser's special-char neutraliser and the rule modules.
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

### Changed

- Internal: the fourteen per-module `_violation` and fifteen
  per-module `_rule` factory copies in `texlint.journals.jss.rules.*`
  are consolidated into shared catalogue-backed factories in
  `rules/_helpers.py` (`make_rule`, `tex_violation`, `entry_violation`,
  `make_violation`, `entry_line`). No behaviour change; net −280
  lines. New rules get severity/message/confidence wiring for free,
  and future cross-cutting changes (suppression, confidence) have one
  seam instead of fifteen.

### Fixed

- Markup / prose rules no longer fire inside `lstlisting`, `alltt`,
  `tabbing`, and `verbatim*` bodies. The parser's neutraliser and the
  rules' non-prose check had drifted into two different environment
  lists; both now consume the shared `texlint.api.VERBATIM_ENVS`
  contract. Before the fix, `jss-lint --fix` would even rewrite code
  inside an `lstlisting` (e.g. `library(zoo)` → `library(\pkg{zoo})`).
- `JSS-CAP-001` now learns the paper's own package name from the
  document's `\pkg{...}` usage instead of a filesystem-path heuristic
  that only matched the eval corpus's `cran_<name>/vignettes/` layout;
  titles following the JSS convention (`\title{flexsurv: A Platform
  for ...}`) are no longer flagged on real submissions.
- One crashing rule no longer aborts the whole run with no output: the
  engine isolates per-rule exceptions, reports the rule as skipped
  (`internal error: ...`, visible via `--verbose`), and keeps the
  remaining rules' findings.
- `eval/review.py` now builds a `±3`-line source snippet per violation and
  passes it as `paper_context` to the `ReviewClient`, rather than sending
  an empty string. Observed effect: AI precision on the canonical JSS
  template's `JSS-SRC-001` violations improved from 86% to 57%, moving
  measurably toward the human ground-truth of 11%. Residual gap is the
  AI blind spot documented in `eval/review-skip-list.toml` and
  `specs/002-eval-jss-harness/spec.md`'s Assumptions section.
- `eval-jss review` now fail-fast-exits 2 with a diagnostic message on
  first-call network errors, per `contracts/review-client.md`. Earlier
  behaviour silently degraded every row to `uncertain`, which made a
  mis-pointed `--base-url` (or a down server) invisible to the operator.

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
