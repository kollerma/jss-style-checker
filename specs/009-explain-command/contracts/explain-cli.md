# Contract: `jss-lint explain` CLI

**Spec**: [../spec.md](../spec.md)
**Plan**: [../plan.md](../plan.md)

## C-1 Backwards compatibility

`jss-lint <PATHS>` (no subcommand) MUST continue to invoke the
read-only lint pass with byte-identical output to the spec-008
baseline. The Click group migration uses
`invoke_without_command=True` (or equivalent) to preserve this
entry-point.

## C-2 Format set

`--format` accepts exactly two values: `terminal` (default) and
`markdown`. Any other value MUST cause exit 2 with a stderr
message listing the legal values.

## C-3 Single-rule view

`jss-lint explain RULE-ID --format terminal` output MUST contain,
in order:

1. The rule id as a section header (rich-styled).
2. A metadata block: `severity`, `category`, `JSS guide
   section`, `JSS guide URL` (when non-`None`).
3. The `explanation` paragraph.
4. A "Bad" sub-section with the `example_bad` fragment in a
   code-block-style frame.
5. A "Good" sub-section with the `example_good` fragment.

When `--example` is set, an additional "Corpus fixture" block
follows, containing the contents of
`tests/fixtures/violations/<RULE-ID>-bad.tex` (or `.Rnw` /
`.Rmd` per research §5) or the literal string `(no in-corpus
fixture)`.

## C-4 Markdown shape

`--format markdown` output MUST be a CommonMark document with
this structure:

```markdown
# JSS-CITE-002

- **Severity:** warning
- **Category:** citations
- **JSS guide:** [§3.2 Citations](https://...)

<explanation paragraph>

## Bad

```tex
<example_bad>
```

## Good

```tex
<example_good>
```

(when --example)

## Corpus fixture: tests/fixtures/violations/JSS-CITE-002-bad.tex

```tex
<file contents>
```
```

## C-5 Listing view

`jss-lint explain` (no rule id) MUST emit:

- One header per category, sorted by category name.
- One line per rule under each category, sorted by rule id.
- Each line shows the rule id, severity, and `Rule.title`
  (one-line summary).

In `--format markdown`, headers are `##` and rule lines are
bullet items.

## C-6 Unknown rule id

`jss-lint explain JSS-FOO-999` MUST:
- Exit 2.
- Write to stderr: `error: unknown rule id 'JSS-FOO-999'`.
- Append a `did you mean?` block listing up to 5 close
  matches (research §4). If none, list rules in the same
  category prefix.

## C-7 Determinism

For every supported `(rule_id, format, with_example)` triple,
two invocations on the same catalogue produce byte-identical
output (modulo TTY-vs-pipe colour codes, which are forced off
in tests).

## C-8 No network calls

The renderer MUST NOT fetch `guide_url` or any other URL.
URLs are rendered as inert links in markdown and as plain
text in terminal output.

## C-9 Catalogue contract extension

`tests/unit/test_catalogue.py` MUST gain
`test_every_rule_has_explanation` which:
- Iterates `_catalogue_data.RULES`.
- Asserts `rule.explanation != ""`.
- Names the rule id and the field on failure.

A second test, `test_citable_rules_have_examples`, emits a
`UserWarning` (not a fail) for citable rules that lack
`example_bad` / `example_good`. This becomes a hard fail in a
follow-up spec.

## C-10 No paging

The CLI never invokes a pager. Output goes to stdout
unconditionally. Users who want paging pipe through `less`.
