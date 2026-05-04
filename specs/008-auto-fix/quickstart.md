# Quickstart: Adding Auto-fix to a Rule

**Audience**: rule authors who want to upgrade an existing rule
with a `Fix` payload, or who are writing a new rule with
auto-fix from day one.

## Prerequisites

- Repo at HEAD on the spec-008 branch (or post-merge `main`).
- The rule already exists in `_catalogue_data.RULES` and
  passes the precision gate (Constitution §VI).

## Where things live

```text
src/texlint/api.py                                  # Fix dataclass, Violation.fix
src/texlint/core/fixer.py                           # apply_fixes engine
src/texlint/journals/jss/rules/<your-rule>.py       # the rule module
tests/fixtures/auto-fix/<rule-id>-{before,after}.tex # golden pair
tests/unit/core/test_fixer.py                       # engine contract tests
tests/integration/test_fix_cli.py                   # CLI behaviour tests
```

## Adding `Fix` to a rule

1. Identify the byte range your rule wants to replace. The
   easiest source is the pylatexenc node's `pos` and `len`
   attributes, which give a byte offset and length on the
   *original* source bytes.
2. Compute the replacement text. It must be deterministic —
   no time, no randomness, no host state.
3. Decide the confidence level:
   - `"safe"` — the fix is mechanical; you'd merge it without
     looking. E.g., wrapping `MASS` in `\pkg{}`.
   - `"review"` — the fix is plausible but you want a human
     to look (e.g., reformatting a citation that has multiple
     valid forms).
4. Construct the `Fix`:

   ```python
   from texlint.api import Fix, Violation

   fix = Fix(
       start=node.pos,
       end=node.pos + node.len,
       replacement=f"\\pkg{{{name}}}",
       description=f"wrap {name} in \\pkg{{}}",
       confidence="safe",
   )
   ```

5. Pass it through to the violation:

   ```python
   yield Violation(
       file=ctx.path,
       line=ctx.line(node.pos),
       column=ctx.column(node.pos),
       rule_id="JSS-NAME-001",
       severity=Severity.WARNING,
       message=f"package name {name} should be wrapped in \\pkg{{}}",
       fix=fix,
   )
   ```

## Writing the golden fixture pair

Every rule that ships a fix needs two files under
`tests/fixtures/auto-fix/`:

- `<rule-id>-before.tex` — content that triggers the rule.
- `<rule-id>-after.tex` — same content with the fix applied.

These are byte-equal targets. The integration test
`test_fix_cli.py::test_<rule>_fix` runs `jss-lint --fix` on
the `before` file (copied to a tmp dir) and asserts equality
with the `after` file.

Example:

```
# tests/fixtures/auto-fix/jss-name-001-before.tex
The MASS package provides classical statistical methods.

# tests/fixtures/auto-fix/jss-name-001-after.tex
The \pkg{MASS} package provides classical statistical methods.
```

## Running the tests

```sh
# Engine unit tests (apply_fixes, conflict resolution, rollback)
pytest tests/unit/core/test_fixer.py -v

# CLI end-to-end (invokes jss-lint as a subprocess)
pytest tests/integration/test_fix_cli.py -v

# Existing tests must still pass (read-only behaviour unchanged)
pytest -q
```

## Verifying rollback by hand

To confirm that a buggy fix triggers the rollback path:

1. Add a temporary fix whose `replacement` re-trips the rule
   (e.g., `replacement="MASS"` for `JSS-NAME-001`).
2. Run `jss-lint --fix tmp.tex`.
3. Confirm:
   - Exit code is non-zero.
   - `tmp.tex` content is byte-identical to its pre-run
     state.
   - Stderr names the rule and includes the word `rejected`.
4. Remove the temporary fix.

## Common pitfalls

- **Off-by-one in byte ranges**: pylatexenc's `node.pos` is
  a byte offset into the original source. `len` is the byte
  length, not the character count. Use `start = pos`, `end =
  pos + len` (half-open).
- **`replacement` that does not parse**: the post-fix re-parse
  will raise `JSS-PARSE-000`, which the engine treats as a
  regression and rolls back. The CLI exits 2 with a stderr
  rejection message; check the message before assuming the
  rollback logic is wrong.
- **Two fixes on the same byte range from different rules**:
  the conflict-resolution path picks one (research §1). If
  your fix is consistently the loser, raise its confidence
  to `"safe"` (if appropriate) or rename the rule id —
  lexicographic tiebreaker is by `rule_id`.
- **Mutating the source bytes outside `Fix`**: don't. The
  engine assumes byte-range edits are the only mutation.
- **Including line-shift adjustments**: don't. The engine
  applies fixes in reverse-position order, which keeps
  earlier offsets stable. Do not pre-compute a line-
  shifted byte range.

## Where to extend

- **Adding `--fix-confidence safe` to filter by confidence**:
  out of scope for spec 008; revisit in a future spec.
- **Adding multi-file fixes**: out of scope; `Fix` is
  single-file by design.
- **Adding interactive fix authoring (rule asks the user
  for an expansion)**: out of scope; rules whose fix needs
  user input set `fix=None`.
