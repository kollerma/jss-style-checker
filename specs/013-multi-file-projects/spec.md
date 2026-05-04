# Feature Specification: Multi-file `\input` / `\include` Resolver

**Feature Branch**: `013-multi-file-projects`
**Created**: 2026-05-03
**Status**: Draft
**Input**: User description: "Introduce a project-level model. When `jss-lint` is invoked on a single \"root\" file, recursively resolve `\\input{...}`, `\\include{...}`, `\\subfile{...}`, and `\\bibliography{...}` references, producing a `ParsedProject` that aggregates all `ParsedDocument`s with file provenance preserved on every violation. Cycle detection (refuses to recurse on a file already being processed). `\\input` paths are resolved relative to the root file with TeX's standard path-search semantics. A new flag `--no-resolve` keeps the current single-file behaviour. The existing multi-file invocation (`jss-lint paper.tex intro.tex refs.bib`) still works and is treated as an explicit project; behaviour falls through to auto-resolve only when a single root file is passed."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Lint a real multi-file JSS submission with one CLI invocation (Priority: P1)

A JSS author has a manuscript split across `paper.tex`,
`intro.tex`, `methods.tex`, `results.tex`, and `refs.bib`. They
run `jss-lint paper.tex` and get a single report covering every
file. Each violation's file path identifies which file the
problem lives in.

**Why this priority**: P1 because real JSS submissions split
across multiple files. Without auto-resolve, every author has to
either list every file on the CLI or write a wrapper script —
both bad UX.

**Independent Test**: Given a fixture project (one root `.tex`
plus two `\input`-ed files) with one violation in each child
file, `jss-lint root.tex` produces a report with three violations
whose file paths name the three child files correctly.

**Acceptance Scenarios**:

1. **Given** `paper.tex` containing `\input{intro}` and
   `\input{methods}`, **When** `jss-lint paper.tex` runs,
   **Then** the report aggregates violations from `paper.tex`,
   `intro.tex`, and `methods.tex` (paths preserved per
   violation).
2. **Given** the same setup, **When** `--no-resolve` is set,
   **Then** only `paper.tex`'s direct violations are reported
   (legacy single-file behaviour).
3. **Given** an explicit multi-file invocation `jss-lint
   paper.tex intro.tex methods.tex`, **When** the linter runs,
   **Then** behaviour is identical to the auto-resolved
   single-root case (the user's explicit list and the
   resolver's discovered list agree).

---

### User Story 2 - Cycle detection (Priority: P1)

A bug introduces `intro.tex` containing `\input{paper}` (or two
files that mutually `\input` each other). The resolver detects
the cycle, emits a `JSS-PROJECT-001` violation naming the cycle
participants, and processes each file at most once.

**Why this priority**: P1 because a missing cycle detector is a
correctness bug, not a feature gap. An infinite-recursion crash
is strictly worse than no auto-resolve at all.

**Independent Test**: Two files that mutually `\input` each
other; `jss-lint` exits cleanly, processes each file once, and
reports the cycle.

**Acceptance Scenarios**:

1. **Given** `paper.tex` with `\input{intro}` and `intro.tex`
   with `\input{paper}`, **When** the linter runs, **Then** it
   exits 1 (violations present), reports a `JSS-PROJECT-001`
   cycle violation naming both files, and does NOT raise.
2. **Given** a file that `\input`s itself, **When** the linter
   runs, **Then** the same cycle detection fires.

---

### User Story 3 - Cross-file rules (abbreviations) (Priority: P2)

The author defines an abbreviation in `intro.tex`
(`OLS = ordinary least squares`) and uses `OLS` in
`results.tex`. The cross-file abbreviation rule recognises the
definition from `intro.tex` and does NOT flag the use in
`results.tex` as undefined.

**Why this priority**: P2 because cross-file checking is the
follow-on value of having a project model. The headline P1 is
that auto-resolve produces *correct* per-file reports;
cross-file *rules* are the next layer.

**Independent Test**: A two-file project; `intro.tex` defines an
abbreviation; `results.tex` uses it. With the project model, no
violation fires; without it (`--no-resolve`), the legacy rule
fires (unrecognised abbreviation).

**Acceptance Scenarios**:

1. **Given** `intro.tex` defining `OLS` and `results.tex`
   using `OLS`, **When** `jss-lint paper.tex` runs (with
   auto-resolve), **Then** the abbreviation rule does NOT
   fire.
2. **Given** the same files run with `--no-resolve`, **When**
   linting `results.tex` alone, **Then** the rule fires with
   "unrecognised abbreviation".

---

### User Story 4 - Missing-file handling (Priority: P2)

`paper.tex` references `\input{nonexistent}` but no file by
that name exists. The resolver emits a `JSS-PROJECT-002`
violation naming the missing file and continues processing the
rest of the project.

**Why this priority**: P2 because mis-typed inputs are a
common-enough error that a clear diagnostic is much better than
silent skip.

**Independent Test**: A root file with one valid `\input` and
one invalid; the report contains exactly one
`JSS-PROJECT-002` violation naming the invalid input.

**Acceptance Scenarios**:

1. **Given** `paper.tex` with `\input{ghost}` (no `ghost.tex`
   on disk), **When** the linter runs, **Then** a
   `JSS-PROJECT-002` violation fires naming `ghost.tex` and
   the rest of the file is processed normally.

---

### User Story 5 - `\bibliography{refs}` resolution (Priority: P2)

`paper.tex` contains `\bibliography{refs}`. The resolver looks
for `refs.bib` in the standard TeX path-search order: same
directory as the root file, then `BIBINPUTS` (when set), then
texmf paths. The first match is parsed.

**Why this priority**: P2 because BibTeX integration is
standard JSS workflow; missing it would force the author to
list `.bib` files manually.

**Independent Test**: `paper.tex` with
`\bibliography{refs}` and a sibling `refs.bib` file; the
report includes BibTeX violations from `refs.bib`.

**Acceptance Scenarios**:

1. **Given** `paper.tex` and `refs.bib` in the same directory,
   **When** `jss-lint paper.tex` runs, **Then** the report
   includes any violations from `refs.bib`.
2. **Given** `paper.tex` referencing `refs` but no
   `refs.bib` exists in the search path, **When** the linter
   runs, **Then** a `JSS-PROJECT-002` violation fires naming
   `refs.bib`.

---

### Edge Cases

- A root `.tex` with no `\input` / `\include` / `\bibliography`:
  `ParsedProject` contains exactly one `ParsedDocument` (the
  root); behaviour is identical to the spec-005 baseline for
  practical purposes.
- An `\input{file}` where `file.tex` exists AND `file.tex.tex`
  exists: the resolver picks `file.tex` (TeX convention is to
  append `.tex` if missing, never twice).
- `\subimport{subdir/}{file}`: out of scope for v1
  (Clarifications §3); left for a follow-up spec.
- A `.bib` file that `\bibliographys` itself: nonsensical; the
  resolver only follows `\bibliography` from `.tex` files.
- Per-file `.jss-lint.toml`: out of scope; the project uses the
  config from the root file's directory (Clarifications §4).
- A file referenced both with and without `.tex` suffix
  (`\input{intro}` and `\input{intro.tex}` in the same
  document): the resolver normalises both to the same
  `Path` and processes once.
- `\include{file}` (vs. `\input{file}`): treated identically
  for resolution; the `\include`-specific page-break semantics
  are irrelevant at the lint layer.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A new public type `ParsedProject` MUST be added
  to `texlint.api`, wrapping a tuple of `ParsedDocument`
  values, a root `Path`, and a project-graph
  `dict[Path, tuple[Path, ...]]` of "file → its dependencies".
- **FR-002**: When `jss-lint` is invoked with a single
  positional argument that is a `.tex` / `.Rnw` / `.Rmd` file,
  the resolver MUST walk `\input{...}`, `\include{...}`,
  `\subfile{...}`, and `\bibliography{...}` macros and produce
  a `ParsedProject` covering all reachable files.
- **FR-003**: When `jss-lint` is invoked with multiple
  positional arguments, each is treated as an explicit project
  member and the resolver does NOT recursively walk imports
  (the user's explicit list is the project).
- **FR-004**: A new flag `--no-resolve` MUST disable
  auto-resolution even on single-file invocation; the linter
  produces a `ParsedDocument` for that file alone (legacy
  behaviour preserved for users who need it).
- **FR-005**: Cycle detection: the resolver MUST refuse to
  re-enter a file that is already being processed. Detected
  cycles emit `JSS-PROJECT-001` violations naming the cycle
  members.
- **FR-006**: Missing references: when a `\input{name}` cannot
  be resolved to a real file via the path-search, the
  resolver MUST emit `JSS-PROJECT-002` and continue processing.
- **FR-007**: Path search semantics for `\input{name}`:
  1. `<root_dir>/name.tex` (explicit suffix or appended).
  2. `<root_dir>/name` (no suffix appended; matches if file
     exists as-is).
  3. `TEXINPUTS` env var entries (POSIX-only; semicolon-
     separated on Windows but Windows is not supported per
     spec 005).
- **FR-008**: Path search semantics for `\bibliography{name}`:
  same as `\input` but with `.bib` suffix; `BIBINPUTS` env
  var supplements `TEXINPUTS`.
- **FR-009**: `core/engine.py::run` MUST accept either a
  `ParsedDocument` or a `ParsedProject` (covariant). When a
  project is passed, `run` iterates each file and merges
  reports; cross-file rules (per FR-011) see the whole
  project.
- **FR-010**: Every `Violation` returned MUST carry the
  `file: Path` of the source file in which it occurred.
  Existing rules retain this behaviour automatically because
  `Violation.file` already exists.
- **FR-011**: At least one cross-file rule (the abbreviations
  rule from spec 003 / 004 is the canonical example) MUST
  migrate to operate on `ParsedProject`. It walks every
  file's AST in order and treats abbreviations defined in
  earlier files as in scope for later files.
- **FR-012**: A new violation category `project` MUST be
  added (registers `JSS-PROJECT-001` cycle and
  `JSS-PROJECT-002` missing-reference). The category is
  citable for spec 007 catalogue contract purposes.
- **FR-013**: Per-file `.jss-lint.toml` is OUT of scope; the
  project's config is the config in the root file's
  directory (or the nearest ancestor — same semantics as
  the spec-001 single-file flow).

### Key Entities

- **ParsedProject**: Aggregates one or more `ParsedDocument`
  values, a root `Path`, and a project graph
  (`dict[Path, tuple[Path, ...]]`).
- **Project graph**: A directed dependency graph from each
  file to the files it directly references via `\input` /
  `\include` / `\subfile` / `\bibliography`.
- **Resolver**: A pure function `resolve(root: Path) ->
  ParsedProject` that recursively follows references with
  cycle detection.
- **Project rules**: Two new tool-side rules
  (`JSS-PROJECT-001` cycle, `JSS-PROJECT-002` missing-ref)
  that the resolver emits.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Given a multi-file fixture project with N
  files and V violations distributed across them, `jss-lint
  <root>` produces exactly V violations whose file paths
  match the source files.
- **SC-002**: Given a fixture with a cycle, `jss-lint`
  exits 1 (not 2; the cycle is a violation, not a parse
  failure), reports `JSS-PROJECT-001`, and does NOT
  raise.
- **SC-003**: Given a fixture with a missing reference,
  `jss-lint` exits 1, reports `JSS-PROJECT-002`, and
  continues processing the rest of the project.
- **SC-004**: Given a fixture exercising the cross-file
  abbreviation rule, the rule does NOT flag a use whose
  definition lives in a sibling file when run with the
  resolver, AND DOES flag the same use under
  `--no-resolve`.
- **SC-005**: Single-file invocation continues to work for
  every existing test case; existing single-file goldens
  pass unchanged.
- **SC-006**: For a 5-file project, the resolver completes
  in <2 seconds wall-clock on the test machine (matching
  the spec-001 single-file end-to-end target).

## Assumptions

- `pylatexenc` exposes `\input` / `\include` / `\subfile` /
  `\bibliography` as walkable macros; we extract their
  argument via existing AST traversal.
- The existing `Violation.file: Path` field is sufficient to
  carry per-file provenance; no new field is needed.
- Path-search for `TEXINPUTS` follows the POSIX `:`-separated
  convention. Windows is unsupported per prior specs.
- A `.bib` file is parsed by the existing
  `core/parser.py::parse_bib_file`; the resolver only
  decides which `.bib` files to feed to it.
- The project graph is acyclic in well-formed projects;
  cycle detection is a defensive measure.
- Per-rule cross-file migration is incremental. Spec 013
  ships the resolver + the abbreviations rule migration;
  other rules migrate in follow-up work as needed.
- `--no-resolve` is a single flag; per-rule "skip
  resolver" is not in scope.
