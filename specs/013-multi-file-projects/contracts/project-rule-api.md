# Contract: Project Rule API

**Spec**: [../spec.md](../spec.md)
**Plan**: [../plan.md](../plan.md)

This contract documents the `Rule.check_project` extension and
the engine dispatch semantics.

## C-1 Field shape

`Rule.check_project: Callable[[ParsedProject], Iterable[
Violation]] | None = None`.

The callable, when set, accepts a `ParsedProject` and yields
any number of `Violation` objects. The callable MUST be
deterministic per the same `ParsedProject`.

## C-2 Backwards compatibility

Every existing rule in the catalogue MUST continue to
work without modification. The default `None` means
"single-file rule"; the engine's dispatch handles the rest.

## C-3 Engine dispatch

Per data-model §3:

- For each rule in the journal, if `check_project is not
  None`: call it once with the project.
- For each rule, if `check is not None`: call it once
  per `ParsedDocument` in the project.

A rule may set both; both are called and their violations
are unioned. (The catalogue test in spec 003 / 007 may
later forbid this combination if it proves error-prone;
this spec permits it.)

## C-4 Resolution-order guarantee

`project.documents` MUST be in resolution order: the root
file first, then files reachable via `\input` etc.,
breadth-first within each level (or depth-first; the
resolver picks a single deterministic order and tests
freeze it).

`check_project` may rely on this order (e.g.,
abbreviation rule treats earlier files as defining
context for later files).

## C-5 Violation provenance

Every `Violation` returned by `check_project` MUST set
`Violation.file` to the file the violation lives in. A
cross-file rule that flags a USE in file B because of a
DEFINITION in file A sets `file = B` (the use site, not
the definition).

## C-6 `--ignore-rules` honours project rules

A rule whose `rule_id` is suppressed via `--ignore-rules`
or `.jss-lint.toml::ignore_rules` is skipped, regardless of
whether its `check` or `check_project` would have fired.

## C-7 Migration policy

A rule migrating from `check` to `check_project` MUST:
- Remove the old `check` (do not keep both).
- Re-measure precision via `eval-jss report` (Constitution
  §VI).
- Pass the spec-007 catalogue contract test (citation
  fields unchanged).

## C-8 Spec-013 baseline migration

The abbreviations rule migrates in this spec. Its tests
(`tests/unit/journals/jss/rules/test_abbreviations.py`)
gain at least one cross-file scenario; the rule's
single-file behaviour is preserved by the resolver
producing a one-document `ParsedProject` for single-file
inputs (so cross-file rules see a project of size 1, not
a degenerate input).
