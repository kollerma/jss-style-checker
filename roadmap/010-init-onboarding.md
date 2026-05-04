# 010 — `jss-lint init` interactive bootstrap

**Phase:** Author UX
**Depends on:** —
**Unblocks:** —

## Why

A first run on a real manuscript currently produces dozens to
hundreds of warnings — most of which the author cannot triage.
`jss-lint init` turns the wall-of-warnings into a triaged action plan
with sensible defaults written to `.jss-lint.toml`.

## /speckit.specify prompt

Add `jss-lint init [PATH]` subcommand. Behaviour: scan the
manuscript, run all rules, group violations by rule and confidence,
then write a `.jss-lint.toml` next to the source with: severity
overrides where the default is too noisy, an `ignore-rules` list for
rules whose precision on this corpus is below a configurable
threshold, and an inline comment explaining why each suppression was
added. Print a summary table: "Found 87 violations across 14 rules.
Focus first on these 5 high-precision must-fix rules (23
violations)." Refuse to overwrite an existing `.jss-lint.toml`
without `--force`. Operate read-only when `--dry-run` is passed.

## /speckit.clarify prompt

Probe: (a) does `init` ever propose `--ignore-abbreviation` style
overrides based on what it sees, or only `ignore-rules`? (b) what's
the precision threshold — corpus-wide ≥90% (matches Constitution
§VI), or configurable per invocation? (c) do we offer to fetch and
pin a corpus-relevant `.jss-lint.toml` from GitHub, or always
synthesise locally? (d) does the summary table count violations or
unique-line-violations (a single long line can re-trigger one rule)?
(e) is there a separate `--audit` mode that prints the same summary
without writing a config?

## /speckit.plan prompt

Implement in `src/texlint/init.py`. Reuse the existing engine to
scan and (when available locally) the precision data in
`eval/precision-history.db` to decide which rules merit suppression.
Render TOML via `tomli_w` (evaluate stdlib alternatives first; we
already depend on `tomli` for read on Python <3.11). Add
`tests/unit/test_init.py` covering: clean manuscript (writes minimal
config), noisy manuscript (writes suppressions with comments),
existing-config refusal, `--force`, `--dry-run`. Update README
"Quick start" with `jss-lint init` as step 0.
