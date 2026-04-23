# Violation fixtures

One good/bad pair per rule, keyed to the rule catalogue at
`specs/003-jss-rule-catalogue/catalogue.yaml`.

## Naming

```
tests/fixtures/violations/<category>/<rule_id>-good.<ext>
tests/fixtures/violations/<category>/<rule_id>-bad.<ext>
```

- `<category>` matches the `category` field of the catalogue row and the
  filename `src/texlint/journals/jss/rules/<category>.py`.
- `<rule_id>` is the full `JSS-<CAT>-NNN` identifier from the catalogue.
- `<ext>` is `.tex` for rules whose `inspects` includes `tex_files`, `.bib`
  for rules whose `inspects` includes `bib_files`. Rules that inspect
  `raw_source` use the extension of whatever file the check targets.

Contents come from the rule's `example_violation` (→ `-bad`) and
`example_fix` (→ `-good`) fields in the catalogue. Fixtures should be
**minimal** — the smallest self-contained fragment that exercises the
rule's logic.

## Legacy (pre-retrofit) fixtures

The flat files at the root of `tests/fixtures/violations/` (`JSS-CITE-001.tex`,
`JSS-BIB-001.bib`, `JSS-SRC-001.tex`, `JSS-PARSE-000.tex`) are the Step 1
smoke-rule fixtures. They move into their per-category subdirectories as
part of the retrofit PRs that land `citations.py`, `references.py`, and
`code_width.py` (spec 003 FR-024).
