# Changelog

All notable changes to `jss-style-checker` land here. Version numbers follow
[semantic versioning](https://semver.org/). Breaking changes to the
JSON-output shape (see
`specs/001-linter-foundation/contracts/json-output.md`) require a major
version bump and an entry in this file — see the spec's Clarification Q2.

## [Unreleased]

### Added

- **`JSS-XREF-005`** — the figure/table analogue of `JSS-XREF-004`: a
  captioned (numbered) `figure`/`table` (or starred variant) must carry a
  `\label{}` and be referenced from the text; an unlabelled or never-
  referenced (orphan) float is flagged at warning severity. Captionless
  (unnumbered) floats are out of scope. `JSS-XREF-001`'s catalogue
  wording was corrected to describe only what it enforces — the
  cross-reference *form* (use `\ref{}`, not a hardcoded "Figure 2") — now
  that the label/orphan concern lives in `JSS-XREF-005`.
- **`JSS-BIBTEX-005`** — flags a field key repeated within a single
  BibTeX entry (e.g. two `author =` lines, or duplicate
  `volume`/`pages`). BibTeX keeps only the first occurrence and silently
  drops the rest, so the rendered citation loses data. Previously such an
  entry tripped a catastrophic `JSS-PARSE-000` that failed the whole
  document; the parser now treats `bibtexparser`'s recoverable
  `DuplicateFieldKeyBlock` like its `DuplicateBlockKeyBlock` sibling and
  reports the dropped field(s) via this rule instead.
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

- `JSS-HOUSE-003` now handles a jss-loaded package loaded **with options**
  (`\usepackage[usenames,dvipsnames]{xcolor}`) differently from a bare
  redundant load. jss.cls loads these packages without options, so
  re-loading with options is an option clash, not a valid way to get them
  — the rule now advises moving them to `\PassOptionsToPackage{...}{pkg}`
  before `\documentclass` and **withholds the delete-the-line autofix**
  (deleting would silently drop the options and can break compilation).
  A bare `\usepackage{pkg}` (or empty `[]`) keeps the safe auto-delete
  (recall-corpus romc).
- `JSS-XREF-001` no longer flags a "Figure/Table N" that sits inside a
  citation locator (`\citet[Table 2.5]{X}` / `\cite[Figure 3]{X}`): the
  optional argument points at a float in the *cited* work, not this
  manuscript (recall-corpus HardyWeinberg false positives). Matches with a
  cite-macro ancestor are skipped.
- `JSS-CITE-003` no longer flags a lone `Author~(\citeyear{X})`: that's the
  legitimate narrative-citation idiom (author names in prose, year in
  parens), not a bracket-in-bracket. `\citeyear` was dropped from the
  trigger set; the hand-rolled `(\citeauthor{X} \citeyear{X})`
  reconstruction of `\citep` is still caught via the `\citeauthor` branch
  (recall-corpus HardyWeinberg false positives).
- `JSS-CAP-004` now also flags a `\Keywords{}` list whose **first** keyword
  starts with a lowercase letter — JSS keywords are sentence case, so the
  list's first word is capitalised (`ternary plot, …` → `Ternary plot, …`;
  recall-corpus HardyWeinberg). Previously the rule only caught the
  opposite direction (a non-first word in title case). A first keyword
  wrapped in markup (`\pkg{}`, `\proglang{}`, `\code{}`) or a known
  package/language name keeps its own lowercase case and is exempt.
  `\Plainkeywords{}` is deliberately *not* checked — it is PDF metadata the
  reader never sees.
- `JSS-XREF-004` exempts equations carrying `\tag{}` / `\tag*{}`: a `\tag`
  replaces the automatic number with a custom label (e.g.
  `\tag{\texttt{approx()}}`), so the equation isn't a standard
  auto-numbered cross-ref target — the same reasoning as the existing
  `\nonumber` exemption (recall-corpus trueskill false positives).
- `JSS-OPER-003` no longer flags the blank line between a display equation
  and a following sectioning command (`\section` / `\subsection` / …): a
  blank line before a heading is required structure and can't be
  `%`-suppressed like a prose paragraph break (recall-corpus trueskill).
- `JSS-OPER-003` now also checks `\[ … \]` / `$$ … $$` display math for
  blank lines before/after. These parse as a display-math node (not an
  environment), so the rule skipped them entirely (recall-corpus deSolve
  false negatives).
- `JSS-XREF-004` now checks each label in a multi-line equation
  environment (`align` / `eqnarray` / `gather`) independently: those envs
  number every line, so an orphan numbered line is a defect even when a
  sibling line *is* referenced. The old per-environment "any label
  referenced" test missed these (recall-corpus romc `eq:1D_example`).
  Envs containing `\nonumber`/`\notag` fall back to the conservative
  per-env check to avoid flagging a label on an unnumbered line.
- `JSS-MARKUP-001` no longer flags the emphasised first letter of a word
  as a language name: `\emph{C}ombination`, `\textbf{S}helter` (the
  acronym typesetting device, e.g. CUB/CUSH) read the `\emph{C}` as the C
  language. It's skipped when a single-letter language token sits alone in
  an emphasis macro whose closing brace is glued to a lowercase letter; a
  standalone `\emph{C}` (space/punctuation after) still fires
  (recall-corpus CUB false positives).
- `JSS-CODE-003` now flags missing spaces around R's multi-character
  assignment operators `<-`, `->`, and `<<-` (e.g. `x<-coef(y)` →
  `x <- coef(y)`). The missing-space matcher only recognised single-char
  operators, so the `<` broke the ident-operator-ident pattern and glued
  assignments slipped through entirely (recall-corpus CUB false
  negatives). Comparison operators (`==`, `<=`, …) remain a follow-up.
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
