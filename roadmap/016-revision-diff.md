# 016 — `jss-lint diff` between runs

**Phase:** CI / journal workflow
**Depends on:** —
**Unblocks:** —

## Why

When a manuscript comes back after revision, the editor wants
"resolved 9 violations, introduced 2." Today they have to eyeball
two JSON dumps. `jss-lint diff` makes the regression view
first-class.

## /speckit.specify prompt

Add `jss-lint diff OLD.json NEW.json [--format terminal|markdown|json]
[--ignore-line-drift]`. Output groups violations into `fixed`
(in OLD, not in NEW), `introduced` (in NEW, not in OLD), and
`unchanged`. Identity is `(rule_id, file, line, message_template)`
by default; with `--ignore-line-drift`, identity drops `line` so a
fix elsewhere in the file doesn't re-flag downstream violations as
new. Terminal format uses colour and the same renderer as
`jss-lint --mode reviewer`. Exit code is 0 when nothing introduced,
1 when new violations appear. Useful for both editorial revision
rounds and CI regression detection on PR diffs.

## /speckit.clarify prompt

Probe: (a) what's the canonical identity tuple — should `severity`
or `column` participate? (b) when OLD and NEW are produced by
different tool versions (rule renamed), do we map via a migration
table or report as fixed+introduced? (c) markdown output:
GitHub-flavoured or CommonMark? (d) is the diff three-way
(vs. a baseline, e.g., "compared to clean template") ever in scope?

## /speckit.plan prompt

New module `src/texlint/diff.py::compare(old_report, new_report,
ignore_line_drift) -> DiffReport`. New `DiffReport` dataclass with
`fixed`, `introduced`, `unchanged` lists. Click subcommand `diff`
parses both JSON files (the existing `--output json` schema),
computes the diff, dispatches to a renderer. Add
`tests/unit/test_diff.py` covering identical reports, fix-only,
introduce-only, mixed, line-drift handling, and rule-rename.
Document in `specs/016-revision-diff/contracts/diff-output.md`.
