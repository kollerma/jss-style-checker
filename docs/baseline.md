# Adopting jss-lint on an existing manuscript

A manuscript that predates the linter produces hundreds of findings on
its first run. Fixing them all before you can use the tool at all is not
a realistic ask, and neither is reading past them on every run. A
*baseline* records the findings you accept today, so from then on the
tool reports only what is new.

```sh
jss-lint --baseline .jss-lint-baseline.json --update-baseline paper.tex refs.bib
git add .jss-lint-baseline.json && git commit -m "Accept current jss-lint findings"
jss-lint --baseline .jss-lint-baseline.json paper.tex refs.bib   # exit 0
```

The second command is what you keep running — locally and in CI. It
exits 1 only when a finding appears that the baseline does not already
account for, and ends with one line saying what it hid:

```
Baseline: 212 findings hidden by .jss-lint-baseline.json (3 stale, 0 unevaluated)
```

- **matched** — accepted findings that still occur. Hidden from every
  output format and from the exit code.
- **stale** — accepted findings that no longer occur, because you fixed
  them. Harmless; re-run `--update-baseline` to prune them.
- **unevaluated** — accepted findings whose rule did not run in this
  invocation (`--ignore-rules`, below `--min-confidence`, or
  format-skipped). Counted separately so a stricter CI invocation does
  not look like a wave of fixes.

## Configuration

```toml
# .jss-lint.toml
baseline = ".jss-lint-baseline.json"
```

`--baseline` beats the TOML key. There is deliberately **no
auto-discovery**: a file that silences findings has to be named, never
found by accident — least of all in someone else's CI.

In the GitHub Action:

```yaml
- uses: kollerma/jss-style-checker@v1
  with:
    baseline: .jss-lint-baseline.json
    fail-on-severity: warning
```

Baselined findings are absent from the SARIF the Action uploads, so the
Security tab and the PR annotations show only what is new.

## What identifies an accepted finding

`(rule_id, path, message, suggestion)` with an occurrence count. Line
and column deliberately play no part: they survive no edit at all — on a
real four-round JSS submission, a line-based key matched 1 % of findings
across the first revision round, against 100 % for this one.

`path` is relative to the **baseline file's own directory**, in posix
form, so the file is portable between checkouts, machines, and CI. A
baseline in a subdirectory records `../paper.tex`; that is expected.

The file itself is plain JSON, sorted, and carries no timestamp — so
`--update-baseline` produces byte-identical output whichever engine ran
it (`jss-lint` or `jsslint`) and however often you re-run it:

```json
{
  "entries": [
    {"count": 1,
     "message": "BibTeX entries include a doi field where one is available (advisory)",
     "path": "refs.bib",
     "rule_id": "JSS-REFS-003",
     "suggestion": "Add a doi field to entry 'koller2023' if one is available."}
  ],
  "journal": "jss",
  "ruleset_version": "2026-09-07",
  "schema_version": 1,
  "tool_version": "1.2.0"
}
```

## Known limits

1. **Same-shape findings are interchangeable.** Two findings with the
   same rule, file, message, and suggestion are indistinguishable to the
   baseline: fix one and introduce another of the same shape in the same
   file, and the new one stays hidden while the count holds. Release
   1.2.0 sharpened ten rules' suggestions precisely to shrink this
   (`JSS-CODE-001/003`, `JSS-OPER-003`, `JSS-XREF-002/004`,
   `JSS-TYPO-001`, `JSS-CAP-002`, `JSS-CITE-003`, `JSS-REFS-004/007` now
   quote the entry key, label, caption, title, fragment, or comment).
   What remains is `JSS-WIDTH-001`, whose findings are deliberately
   interchangeable ("the file still has N over-wide lines"), and rules
   whose quoted token genuinely recurs, such as two unwrapped `R`s in
   one file.
2. **Renaming or moving a file invalidates its entries**, because the
   path is part of the key. Re-run `--update-baseline` after a rename;
   the summary line will show the old entries as stale.
3. **A minor release may reword a message or a suggestion.** That bumps
   the rule set's date, and entries for the reworded rules go stale
   while their findings reappear as new. The summary line names both
   dates when they differ:

   ```
   Baseline: 212 findings hidden by .jss-lint-baseline.json (3 stale, 0 unevaluated) — written for rule set 2026-09-07, current 2026-11-02; run --update-baseline
   ```

   Patch releases can only *remove* findings, so they never do this. See
   [`versions.md`](versions.md).

## Interaction with other options

| Option | Behaviour |
|---|---|
| `--fix`, `--dry-run`, `--apply` | Operate on the visible report only. Drop `--baseline` to fix accepted findings too. |
| `--ignore-rules`, `--min-confidence`, `--fail-on` | Applied first; their entries count as `unevaluated`, never `stale`. |
| `--mode reviewer` | The compliance percentage and category statuses are computed after suppression, exactly as with inline ignores. |
| `% jss-lint: ignore` | Checked first. An inline-ignored finding never consumes a baseline count — you signed off on it already. |
| `jss-lint diff` | Unchanged. Diffing a baselined report against an unbaselined one shows the hidden findings as resolved. |

`JSS-PARSE-000` is never baselined: a report the parser could not
complete is not a state worth accepting, and `--update-baseline` refuses
to write one.

## Not yet in the bindings

The WASM, PyO3, and R bindings do not expose the baseline in 1.2.0. The
matcher itself is pure and lives in the shared core; only the file I/O
is CLI-side, so an in-memory variant is a small follow-up.
