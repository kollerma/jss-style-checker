# Quickstart: Multi-file Projects

## For an end user

### Lint a multi-file project

```sh
jss-lint paper.tex
```

If `paper.tex` contains `\input{intro}`, `\input{methods}`,
and `\bibliography{refs}`, the linter recursively resolves
those references and reports violations from every reachable
file. You don't list each file on the CLI.

### Disable the resolver

```sh
jss-lint --no-resolve paper.tex
```

Lints only `paper.tex` itself; cross-file references are not
followed.

### Provide an explicit list

```sh
jss-lint paper.tex intro.tex refs.bib
```

When you pass multiple files, the linter treats your list as
the project (it does NOT additionally walk references). Use
this when your project's `\input` references don't all
resolve via the standard path search (e.g., you want to lint
a snippet without rewriting macros).

### When references are missing

If `paper.tex` references `\input{ghost}` and no
`ghost.tex` exists in the search path, you'll see:

```
JSS-PROJECT-002: referenced file not found: ghost.tex
```

The linter exits 1 (violations present) but does NOT
abort — it lints the rest of the project.

### When references form a cycle

If `paper.tex` and `intro.tex` mutually `\input` each
other:

```
JSS-PROJECT-001: cycle detected: paper.tex -> intro.tex -> paper.tex
```

The linter exits 1, reports the cycle, and processes each
file at most once.

## For a contributor

### Where things live

```text
src/texlint/api.py                                  # ParsedProject + Rule.check_project
src/texlint/core/resolver.py                        # resolve(root)
src/texlint/core/engine.py                          # dispatch
src/texlint/journals/jss/rules/abbreviations.py     # migrated rule
src/texlint/journals/jss/rules/project.py           # JSS-PROJECT-001 / 002
tests/unit/core/test_resolver.py                    # resolver tests
tests/integration/test_multi_file_project.py        # end-to-end
```

### Run the resolver tests

```sh
pytest tests/unit/core/test_resolver.py tests/integration/test_multi_file_project.py -v
```

### Migrate a rule to cross-file scope

1. Write `check_project(project: ParsedProject) -> Iterable[
   Violation]` on the rule. The function walks
   `project.documents` (in resolution order) and returns
   violations.
2. Remove the rule's old `check` method (Constitution §X:
   don't keep both unless both are needed).
3. Update the rule's tests:
   - One single-file case (run against `ParsedProject` with
     one document).
   - One cross-file case (definition in file A, use in file
     B).
4. Re-measure precision via `eval-jss report` (Constitution
   §VI). If precision drops below 0.90, narrow or revert the
   migration.

### Adding `\subimport` support (future spec)

`\subimport` is intentionally OUT of v1. To add it:

1. Extend the resolver with a per-call directory stack.
2. Update the macro-walker to recognise
   `\subimport{subdir/}{file}`; resolve `file` relative to
   the current directory at the top of the stack.
3. Push the new directory onto the stack before recursion;
   pop on return.
4. Add fixtures and tests. Update spec 013's research §4
   to retire the v1 carve-out.

### Common pitfalls

- **Forgetting to add `Path` to a violation's `file`
  field**: every violation needs `Violation.file = <path>`.
  Cross-file rules should set this to the file the violation
  lives in (the use site, NOT the definition site, when
  the two differ).
- **Recursion depth**: the resolver uses an explicit stack
  (deque), not Python recursion, so deeply-nested projects
  do not hit `RecursionError`. Don't replace it with a
  recursive function.
- **Skipping `.bib` parses**: `parse_document` already
  handles `.bib` via `parse_bib_file`. The resolver merely
  feeds it the right paths.
- **Missing the `--no-resolve` codepath in tests**: every
  resolver-aware feature needs a test under
  `--no-resolve` confirming the legacy behaviour.
