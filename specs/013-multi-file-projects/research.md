# Research: Multi-file Project Resolver

**Phase**: 0
**Spec**: [spec.md](spec.md)
**Plan**: [plan.md](plan.md)

## 1. Macro extraction strategy

**Decision**: Walk the pylatexenc AST for the four macro names
(`\input`, `\include`, `\subfile`, `\bibliography`). Extract the
single brace argument and treat it as the referenced filename
or stem.

**Rationale**:
- Constitution §II: AST-first. No regex over source.
- pylatexenc exposes `LatexMacroNode` with `.macroname` and
  `.nodeargd.argnlist`; the first argument is the filename.
- The four macro names are stable LaTeX surface; package
  extensions (e.g., `\subimport` from `subfiles`) are out of
  scope for v1.

**Alternatives considered**:
- Regex `\\(input|include|subfile|bibliography)\{([^}]+)\}`:
  rejected — fails on commented-out macros, breaks under
  `\verb` / `\begin{verbatim}`.
- Two-pass walk (first identify macros by name, then re-walk
  to extract args): rejected — single pass with the same node
  type matches.

---

## 2. Path search semantics

**Decision**:

For `\input{name}`:
1. `<root_dir>/name.tex` (if `name` does not already end in
   `.tex`, `.ltx`, `.Rnw`, or `.Rmd`; else use `name` as-is).
2. `<root_dir>/name` (no suffix appended).
3. Each entry in `os.environ.get("TEXINPUTS", "").split(":")`,
   followed by step 1 / 2.

For `\bibliography{name}`:
1. `<root_dir>/name.bib`.
2. Each entry in `os.environ.get("BIBINPUTS", "").split(":")`,
   then step 1.
3. Each entry in `TEXINPUTS`, then step 1.

First match wins. No file results in a `JSS-PROJECT-002`
violation.

**Rationale**:
- Matches what BibTeX / `latex` themselves do; authors expect
  this.
- POSIX-only `:` separator is consistent with prior specs that
  declare Linux/macOS as the support set.

**Alternatives considered**:
- Honour TeX's `kpsewhich` recursion: rejected — would shell
  out, breaking determinism.
- Only `<root_dir>/name.tex`, no env-var search: rejected —
  too restrictive for projects that use shared style files.

---

## 3. Cycle detection algorithm

**Decision**: Maintain a stack of files currently being
resolved. Before recursing into a referenced file, check
membership. On hit, emit `JSS-PROJECT-001` naming the cycle
participants (the suffix of the stack from the first
occurrence); do not recurse.

**Rationale**:
- Trivial O(N) check.
- Naming the cycle participants gives the author actionable
  feedback.

**Alternatives considered**:
- Visited-set only: rejected — would silently skip true
  re-references that are not cycles. Two files both included
  by the root file legitimately appear twice in the visit
  graph; that is not a cycle.
- Topological sort: rejected — overkill for the typical depth
  (≤4 levels).

---

## 4. `\subfile` vs `\subimport`

**Decision**: Support `\subfile{path}` (top-level form, shares
`\input` semantics). Skip `\subimport{subdir/}{file}` for v1.

**Rationale**:
- `\subfile` and `\input` differ only in how the included file
  is treated by the standalone document model; for our
  resolver they are identical.
- `\subimport` changes the working directory for nested
  inputs, requiring a directory stack. That is a separate
  small spec.

**Alternatives considered**:
- Support both, with directory stack: rejected per
  Clarifications §3 (out of v1).
- Skip `\subfile` too: rejected — it is the top-level form
  shared by every `subfiles`-using author.

---

## 5. `--no-resolve` semantics

**Decision**: When `--no-resolve` is set, the CLI passes a
`ParsedDocument` (not `ParsedProject`) to the engine. Existing
single-file rules see exactly the spec-005 baseline; cross-
file rules silently skip (their `check_project` is not
called).

**Rationale**:
- Backwards compatibility for users who explicitly want the
  legacy behaviour.
- A future `JSS-PROJECT-003` "this rule needs a project to be
  meaningful" warning could land in a follow-up spec; out of
  scope here.

**Alternatives considered**:
- Wrap a single file in a degenerate `ParsedProject`:
  rejected — would still call `check_project`, defeating the
  user's intent.
- Make `--no-resolve` the default: rejected per spec FR-002
  (auto-resolve is the headline value).

---

## 6. Project-rule API shape

**Decision**: Add an optional `Rule.check_project: Callable[
[ParsedProject], Iterable[Violation]] | None`. Existing
`Rule.check: Callable[[ParsedDocument], Iterable[Violation]]`
remains. The engine dispatches both:
- `check`: called once per `ParsedDocument` in the project.
- `check_project`: called once per project.

A rule may set both, in which case the union of violations is
returned. (No rule in this spec sets both; the field exists
for forward compatibility.)

**Rationale**:
- Backwards-compatible: existing rules need zero edits.
- Opt-in: only rules that need cross-file scope adopt
  `check_project`.
- The signature mirrors `check` for consistency.

**Alternatives considered**:
- Replace `check` with a project-only signature: rejected —
  would require migrating all 58 rules.
- Pass `ParsedProject` to `check` (covariant on input):
  rejected — single-file rules would have to re-derive
  per-file scope, doubling code in every rule.

---

## 7. Cross-file rule migration: abbreviations

**Decision**: The abbreviations rule from spec 003 / 004 is
the canonical cross-file rule. Its migration in spec 013:

- Old `check(doc)`: scans `doc` for definitions and uses,
  flags uses without prior definition.
- New `check_project(project)`: walks every file in
  `project.documents`, accumulating definitions in order.
  Uses are flagged when no definition appears earlier in
  any file.

The old `check` is removed (replaced, not retained).

**Rationale**:
- Cross-file abbreviation lookup is the user's intuition; the
  single-file behaviour was a workaround.
- Constitution §VI requires re-measurement: spec 013's
  end-of-spec summary records the new precision number.

**Alternatives considered**:
- Keep `check` and add `check_project` as a supplement:
  rejected — would double-fire on single-file projects.
- Migrate all cross-file-relevant rules in this spec:
  rejected — Constitution §X (Small Surface). Migrate
  incrementally.

---

## 8. Project graph structure

**Decision**: `project.tree: dict[Path, tuple[Path, ...]]`
where each key is a file and the value is the tuple of files
it directly references via the four macros.

**Rationale**:
- Adjacency list is the cheapest representation that supports
  cycle detection and downstream rule needs (e.g., "which
  file defines this abbreviation?").
- `tuple` (vs. `list`) for hashability and immutability.

**Alternatives considered**:
- Edge list `tuple[tuple[Path, Path], ...]`: rejected —
  awkward for "successors of X" queries.
- Full DAG class with topological sort: rejected per §X.

---

## Summary

All eight decisions follow from spec Clarifications and
Constitution §I, §II, §IV, §X. No remaining `NEEDS
CLARIFICATION`. Ready for Phase 1.
