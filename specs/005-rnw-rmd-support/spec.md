# Feature Specification: Rnw / Rmd Manuscript Support

**Feature Branch**: `005-rnw-rmd-support`
**Created**: 2026-04-24
**Status**: Draft
**Input**: User description: "Add first-class support for Sweave/Knitr (`.Rnw`) and R Markdown (`.Rmd`) manuscripts to `jss-lint`. Both formats mix R code with document markup; we do not want style rules to fire inside R code chunks, but we do want rules to fire on the prose/LaTeX surrounding those chunks."

## Clarifications

### Session 2026-04-24

- Q: Markdown parser for `.Rmd` → A: `markdown-it-py` (CommonMark-compliant, token-stream API matches the spec's segment model).
- Q: Which existing rules' `formats` narrow at launch? → A: Preamble category only (PRE-001..008) narrow to `{"tex", "rnw"}`; all other categories stay `formats=None`.
- Q: Inline LaTeX in `.Rmd` prose — raw-LaTeX island or plain text? → A: Raw-LaTeX island. Inline `$math$` / `\macro{...}` / bare `\macro` spans are tex-parsed with source-accurate line numbers so math-masking and citation rules fire on Rmd prose.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Lint a Sweave (`.Rnw`) manuscript (Priority: P1)

JSS authors submit Sweave manuscripts — `.tex`-like files interspersed
with R code chunks delimited by `<<...>>=` … `@`. An author runs
`jss-lint` on the `.Rnw` source and receives the same style-rule
feedback they would get on a pure `.tex` manuscript, with no
false-positives pointing at R code inside chunks, and with line numbers
that match the original source (not a chunk-stripped intermediate).

**Why this priority**: `.Rnw` is the traditional JSS submission format
for Sweave-based vignettes. Without this path, every author using the
R-package vignette workflow has to post-process the file before
linting, which defeats the purpose of a linter. P1 because it unblocks
the majority of existing JSS authors using the traditional toolchain.

**Independent Test**: Given a fixture `.Rnw` file that carries a prose
sentence with a linter-known style issue and an R chunk that contains
text matching a style rule (e.g., a bare `R` mention inside a `<<>>=`
block), running `jss-lint` on the fixture produces exactly the prose
violation at its correct source line and does not produce any violation
whose line falls inside a chunk.

**Acceptance Scenarios**:

1. **Given** a `.Rnw` fixture with prose that violates a style rule at
   line 42 and an R chunk at lines 60–80 containing a string that would
   also match that rule, **When** `jss-lint` runs on the fixture,
   **Then** the rule fires once at line 42 and does not fire at any
   line in the 60–80 range.
2. **Given** a `.Rnw` fixture with valid prose and a valid preamble,
   **When** `jss-lint` runs, **Then** exit code is 0 and no violations
   are reported.
3. **Given** a `.Rnw` fixture with a missing `\Address{}`, **When**
   `jss-lint` runs, **Then** the preamble rule fires with the correct
   line number, matching behaviour on the equivalent `.tex` file.

---

### User Story 2 - Lint an R Markdown (`.Rmd`) manuscript (Priority: P1)

JSS is accepting R Markdown vignettes for new submissions. An author
writes their manuscript as `.Rmd` — YAML frontmatter, Markdown prose,
fenced code blocks, and occasional raw LaTeX fragments. The author runs
`jss-lint` on the `.Rmd` file and receives style-rule feedback scoped to
prose content, with no violations from inside fenced code blocks and
no crashes on Markdown-specific syntax.

**Why this priority**: `.Rmd` is the forward-looking format; new JSS
vignette templates (since roughly v90) are Rmd-based. P1 because the
linter has no value for the growing Rmd-authored subset of the author
population without this.

**Independent Test**: Given a `.Rmd` fixture with a heading, a prose
paragraph containing an unwrapped package name, and a fenced code block
containing the same package name, running `jss-lint` produces one
violation on the prose line and zero violations on the code-block lines.

**Acceptance Scenarios**:

1. **Given** an `.Rmd` fixture with prose mentioning an R package
   without `\pkg{}` wrapping (e.g., `... uses MASS ...`) and a code
   block that also contains `MASS`, **When** `jss-lint` runs, **Then**
   the markup rule fires once on the prose line.
2. **Given** an `.Rmd` fixture with a fenced LaTeX block containing a
   preamble-level violation (e.g., `\documentclass{article}` instead of
   `jss`), **When** `jss-lint` runs, **Then** the relevant rule fires
   with the correct source line inside the `.Rmd` file.
3. **Given** an `.Rmd` fixture with YAML frontmatter, **When**
   `jss-lint` runs, **Then** no rules fire on the frontmatter content
   (linting the frontmatter is explicitly out of scope for this step).
4. **Given** an `.Rmd` fixture that references bibliographic citations
   but has no sibling `.bib` file, **When** `jss-lint` runs, **Then**
   the tool emits a warning naming the missing bibliography source and
   proceeds to lint what it can.

---

### User Story 3 - Format-filtering for rules (Priority: P2)

Contributors adding new rules need to declare which input formats each
rule applies to (some preamble-specific rules only make sense for
`tex`/`rnw`; Rmd has no preamble in the same sense). Reviewers need to
see which rules were skipped on a given run so they can tell the
difference between "rule passed" and "rule not applied". Authors
running with `--verbose` want an explicit list of skipped rules in the
output so they understand why certain checks aren't mentioned.

**Why this priority**: Necessary infrastructure, but no author-facing
value by itself. P2 because US1 and US2 can ship with a hard-coded
applicability table and this can follow as a refinement.

**Independent Test**: Given a `.Rmd` file and a rule declared
`formats={"tex", "rnw"}`, running `jss-lint --verbose` on the file
reports the rule by id in a "skipped rules" section, and omits it
entirely from the violation output.

**Acceptance Scenarios**:

1. **Given** a rule flagged as `tex`-only, **When** that rule is
   evaluated against an `.Rmd` input, **Then** the rule is not invoked
   and its id is added to the report's skipped-rules list.
2. **Given** `--verbose` is set, **When** any rule is skipped due to
   format mismatch, **Then** the terminal output includes a "Skipped
   rules" section naming each skipped rule and the reason.
3. **Given** `--verbose` is not set, **When** rules are skipped,
   **Then** terminal output is unchanged (no skipped-rules section).

---

### User Story 4 - Eval-harness regression safety (Priority: P3)

The precision-gate harness (`eval-jss scan` + `report`) was validated
against a `.tex`-only corpus in spec 002 and spec 004. Introducing
format dispatch must not silently drop any rule on the existing corpus
— precision numbers should be byte-identical before and after the
format-filtering logic lands.

**Why this priority**: Regression-safety check, not a user-visible
feature. P3 because it's a test, not a deliverable. Must pass before
merge regardless.

**Independent Test**: Running `eval-jss scan --force` followed by
`eval-jss report` on the 6-paper example corpus produces identical
per-rule violation counts before and after this feature merges.

**Acceptance Scenarios**:

1. **Given** the pre-feature corpus violation counts (captured in
   `eval/report.csv` or equivalent snapshot), **When** `eval-jss scan
   --force` runs on the same corpus after this feature lands, **Then**
   per-rule violation counts match the snapshot exactly.
2. **Given** a `.Rnw` or `.Rmd` paper added to the corpus post-feature,
   **When** `eval-jss report` runs, **Then** per-rule precision figures
   for the `.tex` subset are unchanged (format-specific papers can be
   tracked separately without contaminating `.tex` numbers).

### Edge Cases

- **Chunk label without closing `@`**: malformed `.Rnw` where the
  chunk open delimiter `<<lbl>>=` has no matching `@`. The stripper
  MUST handle gracefully — either treat the rest of the file as chunk
  content (and skip it) or report a single `JSS-PARSE-000` violation
  naming the line of the unclosed chunk open.
- **Nested fences in Rmd**: a fenced code block whose body contains
  backtick runs shorter than the fence (e.g., body has ```` ``` ```` but
  the fence is ````~~~````). The parser MUST honour the opening fence's
  delimiter to find the close, not the first backtick pair.
- **Inline R code (`` `r expr` ``) in prose**: the expression is
  skipped but surrounding prose is linted. A prose paragraph with
  multiple inline code spans yields violations only on the prose
  segments, with correct line numbers.
- **Rmd with raw LaTeX passages**: a `` ```{=latex} `` block, a
  `\begin{...}...\end{...}` environment, or an inline LaTeX fragment
  in prose (`$x^2$`, `\ref{eq:1}`, `\citep{Smith2020}`) is parsed as
  LaTeX and fed to the tex-applicable rules. Line numbers map back to
  the `.Rmd` source.
- **Line-number drift after chunk stripping**: verify via snapshot that
  reported line numbers match the original `.Rnw` / `.Rmd` source, not
  a stripped intermediate.
- **No sibling `.bib` file on `.Rmd` input**: the bibliography-inspection
  rules need a `.bib`. Assumption (per clarification proposal): warn,
  don't error.
- **Mixed input**: user runs `jss-lint paper.Rmd paper.tex` — each file
  is dispatched by extension; both produce appropriate violations.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST recognise `.Rnw` file extensions and parse
  them by stripping R code chunks to whitespace (preserving line
  numbers) before running the LaTeX parser.
- **FR-002**: System MUST recognise `.Rmd` file extensions and parse
  them into a structured document with YAML frontmatter, headings,
  prose blocks, fenced code blocks, inline code spans, and raw LaTeX
  fragments.
- **FR-003**: `.Rnw` line numbers in violations MUST match the
  original source file, not a stripped intermediate.
- **FR-004**: Existing JSS rules MUST continue to fire on `.Rnw` input
  with no code-change per rule (the stripper preserves the
  LaTeX-compatible surface the rules already understand).
- **FR-005**: Rules MUST NOT fire on content inside R code chunks in
  `.Rnw` files or inside fenced code blocks in `.Rmd` files.
- **FR-006**: Raw LaTeX fragments inside `.Rmd` prose MUST be linted
  by the tex-applicable rule subset with source-accurate line numbers.
  This covers both delimited blocks (`` ```{=latex} `` fences,
  `\begin{…}…\end{…}` environments) and inline fragments within a
  prose paragraph (`$math$`, `\macro{args}`, bare `\macro` tokens).
- **FR-007**: Each rule MUST declare which input formats it applies to
  via a format filter; `None` / unset MUST mean "all formats".
- **FR-008**: Rules whose format filter excludes the input MUST be
  skipped at rule-evaluation time, and their rule ids MUST be recorded
  in the per-run report so consumers can tell "skipped" apart from
  "passed".
- **FR-009**: `--verbose` terminal output MUST list the set of
  skipped rule ids and the reason for each skip; default (non-verbose)
  output MUST NOT include the skipped-rules section.
- **FR-010**: Inline R code spans in `.Rmd` prose (delimited by
  `` `r expr` ``) MUST be skipped for rule evaluation; surrounding
  prose MUST remain lintable with correct line numbers.
- **FR-011**: YAML frontmatter in `.Rmd` files MUST NOT be subject to
  any style rule in this step (lint scope explicitly excludes
  frontmatter content).
- **FR-012**: When an `.Rmd` input has bibliographic-citation markup
  but no sibling `.bib` file is provided, the tool MUST emit a warning
  naming the missing bibliography and proceed; it MUST NOT error out
  unless other input errors force a non-zero exit.
- **FR-013**: The engine MUST dispatch parse-time work by file
  extension and populate a new container for `.Rmd` parsed documents
  alongside the existing tex/bib containers.
- **FR-014**: Malformed `.Rnw` input (e.g., unclosed chunk delimiter)
  MUST surface as a `JSS-PARSE-000` violation with a line number, not
  a crash, consistent with existing non-fatal parse behaviour (spec
  001 Constitution §III).
- **FR-015**: Existing `.tex` + `.bib` rule behaviour MUST remain
  unchanged — per-rule violation counts on the existing 6-paper
  example corpus MUST be byte-identical before and after this feature
  lands.
- **FR-016**: Per-rule precision numbers in the eval harness MUST be
  reportable separately for `.tex`, `.Rnw`, and `.Rmd` subsets so
  format-specific precision trends don't contaminate the established
  `.tex` baseline.
- **FR-017**: The full rule suite (58 active rules from spec 004) MUST
  continue to execute with 100% branch coverage.
- **FR-018**: Contributors adding an `.Rmd`-specific rule MUST have a
  single module location for those rules (analogous to the per-category
  modules from spec 004) so Rmd-specific logic doesn't leak into
  `.tex`-targeted rule modules.
- **FR-019**: The eval corpus MUST gain a small real-CRAN `.Rnw` /
  `.Rmd` batch (target: 3–5 `.Rnw` vignettes + 2–3 `.Rmd` vignettes)
  fetched via the existing `eval-jss corpus fetch` manifest mechanism,
  pinned by SHA256. `eval-jss report` MUST support slicing per-rule
  precision by input format so the established `.tex` baseline is
  isolated from new-format numbers.
- **FR-020**: At launch the preamble-category rules (JSS-PRE-001..008)
  MUST declare `formats={"tex", "rnw"}`; all other categories MUST
  keep `formats=None` (apply to every input format). Running
  `jss-lint --verbose` on an `.Rmd` input MUST list the 8 preamble
  rules in the skipped-rules section with a format-mismatch reason.

### Key Entities

- **Parsed Sweave document**: the stripped LaTeX representation of a
  `.Rnw` file with chunk regions replaced by whitespace; carries the
  original source so line numbers remain authoritative.
- **Parsed R-Markdown document**: a structured view of an `.Rmd` file
  comprising frontmatter, ordered prose/heading/code-block/raw-LaTeX
  segments, with each segment carrying its original start-line for
  traceback.
- **Rule-format filter**: a per-rule set of allowed input formats
  (`tex`, `rnw`, `rmd`); used at evaluation time to decide whether to
  invoke the rule's check callable.
- **Skipped-rule record**: a per-run collection of `(rule_id, reason)`
  entries recording rules that were not evaluated on the current input,
  surfaced in `--verbose` output.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For every `.Rnw` fixture that carries a prose violation
  at a known line and a distinct code-chunk region, `jss-lint` reports
  the prose violation at the correct source line and reports zero
  violations from within the code-chunk region — 100% of the time
  across the fixture matrix.
- **SC-002**: For every `.Rmd` fixture, `jss-lint` reports violations
  only on prose / heading / raw-LaTeX lines; code-fence and
  frontmatter lines produce zero violations in the fixture matrix.
- **SC-003**: Running `eval-jss scan --force` + `eval-jss report` on
  the existing 6-paper `.tex` corpus produces per-rule violation counts
  that are byte-identical to the pre-feature snapshot (FR-015).
- **SC-004**: After the feature lands, a contributor running the full
  test suite from a clean checkout sees 100% branch coverage across
  the rules tree (unchanged from spec 004) plus all new `.Rnw` / `.Rmd`
  parser modules.
- **SC-005**: Authors running `jss-lint` on a mixed command line of
  `.tex` + `.Rnw` + `.Rmd` files receive a single consolidated report
  where each file's violations are attributed to the correct source
  path and line, with no cross-file bleed.
- **SC-006**: The `eval-jss report` command can split per-rule
  precision by input format (`tex` / `rnw` / `rmd`) without requiring
  a schema migration of the existing corpus database.

## Assumptions

- **Chunk-delimiter precedence**: `.Rnw` chunks are delimited by the
  standard Sweave / knitr `<<...>>=` opening and `@` closing; chunks
  in unusual but legal forms (e.g., `<<>>=` no-label, `<<lbl,
  fig.path='foo'>>=` with options) follow the same delimiter pair.
  Non-standard user delimiters are out of scope.
- **`.Rmd` frontmatter**: YAML frontmatter (delimited by leading and
  trailing `---`) is preserved in the parsed structure for downstream
  tooling but is NOT linted in this step. A future spec may add
  frontmatter-specific rules (e.g., `author` list shape, `title`
  presence).
- **Missing `.bib` on `.Rmd` input**: warned, not errored. The rule
  that would have inspected the missing file reports a single
  informational notice naming the missing file; per-rule evaluations
  that depend on `.bib` content are skipped for that run with a
  skipped-rule record (FR-008).
- **Inline R code handling**: `` `r expr` `` spans in `.Rmd` prose
  are elided from rule evaluation; the surrounding prose on the same
  line is still linted. Equivalent `\Sexpr{…}` in `.Rnw` prose (not
  inside a chunk) is elided in the same way.
- **pyyaml as a runtime dependency**: acceptable — already a dev
  extra, now promoted. Downstream consumers who `pip install texlint`
  without the `[rmd]` extra get Rmd support unconditionally.
- **`markdown-it-py` as a runtime dependency**: the `.Rmd` body parser
  uses `markdown-it-py` (CommonMark-compliant, token-stream API that
  maps cleanly to the ordered segment model described in the Key
  Entities section). No `[rmd]` extra; the dep ships unconditionally.
- **Corpus expansion for Rnw / Rmd**: this feature ships a small real
  batch of CRAN-vignette sources alongside the synthetic unit-test
  fixtures. Target: **3–5 `.Rnw` vignettes + 2–3 `.Rmd` vignettes**
  fetched from CRAN via the existing manifest mechanism (spec 002's
  `eval-jss corpus fetch`). Package selection favours vignettes with
  JSS-style conventions (citation-heavy prose, `\pkg{}` / `\proglang{}`
  usage, Sweave-classical chunk patterns). Precision tracking splits by
  input format: `eval-jss report` gains the ability to slice per-rule
  precision by `tex` / `rnw` / `rmd` so the established `.tex` baseline
  is isolated from Rnw/Rmd numbers (FR-016, FR-019, SC-006).
- **CLI surface unchanged**: no new flags beyond the existing
  `--verbose` from Step 1. `--format <tex|rnw|rmd>` is explicitly NOT
  added; file extension dispatch is authoritative.
- **Rule-module boundary**: Rmd-specific rules (when any are
  introduced) live in a single per-format module analogous to the
  per-category modules from spec 004. This step introduces the
  placeholder module but may not populate it — most existing JSS
  rules work on all three formats unchanged once the format filter is
  in place.
- **Output-format unchanged**: JSON / HTML / terminal output shapes
  from spec 001 are preserved; the skipped-rules payload in verbose
  mode is additive and tolerates older consumers that ignore it.
- **Back-compat on `Rule.formats`**: the existing semantics
  (`None` = all file-suffix formats) extends naturally to the new
  input-format filter; existing rules with `formats=None` continue to
  apply to all inputs, which is the correct default for rules that
  inspect language-agnostic AST structures.
