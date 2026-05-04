# Quickstart: `jss-lint diff`

## For an end user

### Compare two revision rounds

```sh
jss-lint manuscript_round1.tex --output json > round1.json
jss-lint manuscript_round2.tex --output json > round2.json
jss-lint diff round1.json round2.json
```

Output:

```
Fixed: 9
Introduced: 2
Unchanged: 5

== Fixed ==
  JSS-MARKUP-001 line 12: ...
  ...

== Introduced ==
  JSS-WIDTH-001 line 87: ...
  ...

== Unchanged ==
  JSS-CAP-002 line 42: ...
  ...
```

Exit code is 0 if Introduced is empty, 1 otherwise.

### Ignore line drift

```sh
jss-lint diff round1.json round2.json --ignore-line-drift
```

Useful when an author inserts a section and every downstream
violation now appears at a different line number. The flag
treats those as `unchanged`, not `fixed + introduced`.

### Markdown for a PR comment

```sh
jss-lint diff round1.json round2.json --format markdown
```

Pipe-and-paste into a GitHub PR comment.

### CI regression check

```yaml
# .github/workflows/lint-regression.yml
- run: |
    jss-lint --output json > new.json
    git fetch origin main
    git show origin/main:lint-baseline.json > old.json
    jss-lint diff old.json new.json
```

If `introduced > 0`, the step fails (exit 1) and the PR
check goes red.

## For a contributor

### Where things live

```text
src/texlint/diff.py                                # comparison + renderers
src/texlint/cli.py                                 # `diff` subcommand
docs/jss-guide/rule-renames.json                   # rename map (initially {})
tests/unit/test_diff.py                            # comparison tests
tests/integration/test_diff_cli.py                 # CLI tests
tests/fixtures/diff/                               # fixture pairs
```

### Run the tests

```sh
pytest tests/unit/test_diff.py tests/integration/test_diff_cli.py -v
```

### Adding a rule rename

When you rename a rule (e.g., spec-018 splits
`JSS-MARKUP-005` into `JSS-MARKUP-005-A` /
`JSS-MARKUP-005-B`):

1. Edit `docs/jss-guide/rule-renames.json`:

```json
{
  "renames": {
    "JSS-MARKUP-005": "JSS-MARKUP-005-A"
  },
  "_provenance": {
    "JSS-MARKUP-005": "spec-018: split into 005-A and 005-B"
  }
}
```

2. Add a unit test in `test_diff.py` that exercises the new
   rename across an OLD/NEW fixture pair.

3. Note: the map only handles 1:1 renames. Splits (1:N) are
   handled by mapping the old id to ONE of the new ids
   (typically the most-canonical); the other becomes
   "introduced". A future spec may extend the map shape if
   1:N renames become common.

### Common pitfalls

- **`message` mismatch**: the identity tuple includes
  `message`. If you tweak a rule's wording (even a typo
  fix), every violation of that rule turns into
  fixed+introduced. Pair the wording change with a
  rule-rename map entry, or commit it as a separate PR
  that explicitly lints both before/after to verify the
  rename.
- **Schema mismatch on input**: the diff command validates
  both files against the spec-001 schema. If the schema
  changed in a recent spec, regenerate your fixtures.
- **Identical diffs return exit 0**: not a bug. Exit 1 is
  reserved for `introduced > 0`.

### Where to extend

- **Three-way diff (`--baseline`)**: out of v1; needs its
  own design pass on the transitivity question.
- **SARIF diff**: would consume `--output sarif`. Out of
  v1; `--output json` is the canonical input.
- **Per-rule statistics**: would summarise "this rule
  fired N times in OLD, M in NEW". Out of v1; the
  per-violation lists are sufficient.
