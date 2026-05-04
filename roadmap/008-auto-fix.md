# 008 — Auto-fix (`--fix` / `--dry-run` / `--apply`)

**Phase:** Author UX
**Depends on:** —
**Unblocks:** 011 (LSP code actions)

## Why

Auto-fix is the single feature that converts a linter from "homework
assignment" into "background helper". Without it every violation is
manual work; with it, the obvious mechanical edits happen instantly.
Entry A in the contest review shipped this; we don't.

## /speckit.specify prompt

Add three CLI flags to `jss-lint`: `--fix` (apply all available fixes
in place, atomic write), `--dry-run` (print proposed fixes as a
unified diff but do not write — requires `--fix`), and `--apply`
(interactive hunk-by-hunk walk-through, `y/n/all/quit` per fix).
Introduce a `Fix` dataclass on `Violation` (text edit, fix
description, confidence level). Each rule module that supports
auto-fix populates `fix=Fix(...)` on the violations it yields; rules
without a deterministic fix yield `fix=None`. The engine groups
fixes per file, applies them in reverse-position order, validates
the rewritten file no longer re-triggers the same rule, and rolls
back atomically on failure. Add `--fix-rule RULE-ID` (repeatable) to
scope fixes to specific rules. Default behaviour with no flag is
unchanged (read-only).

## /speckit.clarify prompt

Probe: (a) what is the conflict-resolution policy when two rules
propose overlapping edits in the same byte range — first-wins,
highest-confidence-wins, or fail-loud? (b) does `--apply` re-prompt
after each accepted fix or batch-prompt grouped by rule? (c) do we
require coverage of every rule that ships a `Fix`, or allow
incremental adoption with a per-rule `auto_fixable: bool` flag in
the catalogue? (d) how do we surface fixes that need user input
(e.g., "this abbreviation needs an expansion — what should it be?")?
(e) what's the exit code when `--dry-run` shows fixes — 0
(informational) or 1 (changes pending)?

## /speckit.plan prompt

Add `Fix` dataclass to `src/texlint/api.py` with fields
`(start: int, end: int, replacement: str, description: str,
confidence: Literal["safe", "review"])`. Implement
`src/texlint/core/fixer.py::apply_fixes(report, document, mode,
rules)` where `mode` is `"write" | "dry-run" | "interactive"`.
Atomic write via `tempfile.NamedTemporaryFile(dir=parent)` +
`os.replace`. Use `difflib.unified_diff` for `--dry-run` output and
the interactive prompt. Re-validate by re-parsing the rewritten
content and checking no violation with the same `(rule_id, line)`
re-appears; on regression, roll back. Add
`tests/unit/core/test_fixer.py` with golden-file fixture pairs
(`before.tex` / `after.tex`) for at least JSS-CITE-003,
JSS-NAME-001, JSS-CAP-002 (or whichever three rules have the most
deterministic fixes in the current catalogue). Update `cli.py` to
dispatch.
