# Contract: `resolve(root)` Resolver

**Spec**: [../spec.md](../spec.md)
**Plan**: [../plan.md](../plan.md)

## C-1 Pure function

`core/resolver.py::resolve(root, *, texinputs, bibinputs)` is
a pure function of `(root, texinputs, bibinputs, filesystem
state)`. Two invocations against equal inputs MUST produce
equal `ParsedProject` objects.

## C-2 Single-file project

When `root` has no `\input` / `\include` / `\subfile` /
`\bibliography` macros:
- `project.documents` has exactly one element (the parsed
  `root`).
- `project.tree[root] == ()`.
- Zero `JSS-PROJECT-*` violations are emitted.

## C-3 Recursive resolution

Each macro of the four supported names contributes one
edge in `project.tree`. Recursion is depth-first; the
resolution order is reflected in `project.documents`.

## C-4 Cycle detection

If the resolver encounters a file `F` while `F` is already
on the visit stack:
- `JSS-PROJECT-001` is emitted on the parent file (the file
  that contains the cycle-closing reference).
- `F` is NOT processed a second time.
- The visit stack continues unwinding normally.

## C-5 Missing reference

When a `\input{name}` cannot be resolved via the path-
search (research §2), the resolver:
- Emits `JSS-PROJECT-002` on the parent file with the
  unresolved name.
- Does not stop; continues processing other references.

## C-6 Path search order

Per research §2:

For `\input{name}`:
1. `<root_dir>/name[.tex]`.
2. Each entry of `TEXINPUTS`.

For `\bibliography{name}`:
1. `<root_dir>/name.bib`.
2. Each entry of `BIBINPUTS`, then `TEXINPUTS`.

First match wins.

## C-7 Suffix handling

`\input{name}` with no extension probes both `name` and
`name.tex` (in that order). `\input{name.tex}` probes
only `name.tex`. The resolver never appends `.tex` twice.

## C-8 No filesystem mutation

The resolver MUST NOT create, modify, or delete any file.
Violations of this contract are caught by a test that
runs the resolver on a read-only filesystem mount.

## C-9 No env-var mutation

The resolver MUST NOT modify `os.environ`. It reads
`TEXINPUTS` / `BIBINPUTS` once at entry and treats them
as immutable for the duration of the call.

## C-10 Backwards-compatibility with `--no-resolve`

The CLI's `--no-resolve` path bypasses `resolve` entirely
and produces a `ParsedDocument` (not `ParsedProject`). The
engine dispatches the `ParsedDocument` branch; cross-file
rules silently no-op.

## C-11 Performance

For a 5-file project, `resolve(root)` completes in less
than 2 seconds wall-clock on the test machine. SC-006
verifies this.

## C-12 Determinism across hosts

Path normalisation uses `Path.resolve()` for cycle keys
to canonicalise symlinks; the resulting `tree` keys are
absolute paths that compare equal regardless of how the
user invoked the linter.

## C-13 Project rule emission

`JSS-PROJECT-001` and `JSS-PROJECT-002` violations are
embedded in the `ParsedDocument.violations` of the file
that contains the reference. The engine surfaces them
alongside other rule violations in the
`ComplianceReport`. They participate in `--ignore-rules`
filtering like any other rule (but they do NOT take a
sentinel exception — a user who suppresses
`JSS-PROJECT-002` is responsible for the consequences).
