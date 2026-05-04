# 009 — `jss-lint explain RULE-ID`

**Phase:** Author UX
**Depends on:** 007 (JSS-guide mapping)
**Unblocks:** 015 (conformance report uses the same explainer)

## Why

A rule id like `JSS-CITE-002` is meaningless until the author looks
it up. Embedding the explanation in the tool (`jss-lint explain
JSS-CITE-002`) closes the learning loop without context-switching to
a browser, and turns the linter into a teaching tool.

## /speckit.specify prompt

Add a new `explain` subcommand to `jss-lint`:
`jss-lint explain RULE-ID [--example] [--format markdown|terminal]`.
The subcommand prints the rule's full metadata (id, severity,
category, JSS-guide section + URL from spec 007), a one-paragraph
plain-language explanation, a "bad" example fragment, a "good"
example fragment, and (when `--example` is passed) the corresponding
fixture pair from `tests/fixtures/violations/`. `jss-lint explain`
with no argument lists all rules grouped by category. `--format
markdown` produces output that pastes cleanly into GitHub issues /
PR comments. The explanation text lives in
`_catalogue_data.RULES[rule_id]["explanation"]` (a new field) so
explanations are version-controlled alongside the rule logic.

## /speckit.clarify prompt

Probe: (a) is `--format html` in scope, or only `markdown` /
`terminal`? (b) when a rule fixture doesn't yet exist, do we fall
back to a synthetic example or surface "no example available"?
(c) does the listing view (`jss-lint explain` with no arg) page
output through `less` like `git log` does, or always print the full
list? (d) do we require an explanation text for every rule in CI,
or allow rollout gaps with a TODO sentinel?

## /speckit.plan prompt

Add `explanation: str` and `example_bad`/`example_good: str | None`
to `_catalogue_data.RULES`. Add a Click sub-group in
`src/texlint/cli.py` so `jss-lint` becomes a multi-command CLI
(`lint` remains the default for backward compatibility). Implement
`src/texlint/explain.py` with `render(rule_id, format) -> str`. Pull
fixture content from `tests/fixtures/violations/<RULE-ID>-bad.tex`
when present. Add `tests/unit/test_explain.py` with golden-file
expectations for at least three rules. Update README with a
"Learning the rules" section.
