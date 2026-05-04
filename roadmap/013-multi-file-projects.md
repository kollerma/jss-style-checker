# 013 — Multi-file `\input`/`\include` resolver

**Phase:** Editor experience
**Depends on:** —
**Unblocks:** —

## Why

Real JSS submissions split across `paper.tex`, `intro.tex`,
`methods.tex`, supplementary, and multiple `.bib` files. The current
single-file model misses cross-file violations (e.g., abbreviation
defined in `intro.tex`, used in `results.tex`) and forces authors to
list every file on the CLI.

## /speckit.specify prompt

Introduce a project-level model. When `jss-lint` is invoked on a
single "root" file, recursively resolve `\input{...}`,
`\include{...}`, `\subfile{...}`, and `\bibliography{...}`
references, producing a `ParsedProject` that aggregates all
`ParsedDocument`s with file provenance preserved on every
violation. Cycle detection (refuses to recurse on a file already
being processed). `\input` paths are resolved relative to the root
file with TeX's standard path-search semantics. A new flag
`--no-resolve` keeps the current single-file behaviour. The
existing multi-file invocation
(`jss-lint paper.tex intro.tex refs.bib`) still works and is
treated as an explicit project; behaviour falls through to
auto-resolve only when a single root file is passed.

## /speckit.clarify prompt

Probe: (a) what's the policy when a referenced file doesn't exist —
parse warning or fatal? (b) do we follow `\bibliography{refs}` to
find `refs.bib` in standard TeX search paths, or require explicit
naming? (c) is `\subimport` (subfiles package) in scope v1? (d)
per-file vs project-wide `.jss-lint.toml` precedence? (e) how do
cross-file rules (e.g., abbreviation defined in one file, used in
another) interact with the rule's existing single-file walker?

## /speckit.plan prompt

Add `ParsedProject` dataclass to `src/texlint/api.py` wrapping
`tuple[ParsedDocument, ...]` plus a `root: Path` and a
`tree: dict[Path, list[Path]]`. Implement
`core/resolver.py::resolve(root)` walking
`\input` / `\include` / `\subfile` / `\bibliography` macros via
pylatexenc; record the file graph; detect cycles. Update
`core/engine.py::run` to accept either a `ParsedDocument` or
`ParsedProject` (covariant). Migrate one cross-file rule
(abbreviations is the obvious candidate) to operate on the project.
Add `tests/integration/test_multi_file_project.py` with a fixture
that splits a JSS template across three files.
