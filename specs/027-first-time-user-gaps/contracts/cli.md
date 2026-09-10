# Contract: CLI surface additions (1.2.0)

**Plan**: [../plan.md](../plan.md) §4, §5.4, §6, §7.3, §8
**Supersedes/extends**: `specs/001-linter-foundation/contracts/cli.md`
(additive within the 1.x major; nothing is removed or renamed).

Both `jss-lint` (Python) and `jsslint` (Rust) MUST accept every flag and
subcommand below with identical semantics and, for stdout, identical
bytes except where a divergence is named here.

## C-1 New lint options

| Flag | Type | Default | Description |
|---|---|---|---|
| `--baseline FILE` | path | unset | Apply the baseline file (contract `baseline-file.md`). Findings matching an entry are hidden from every renderer and from the exit code. |
| `--update-baseline` | flag | off | Write the baseline from the current run (create or prune) and exit 0. Path: `--baseline`, else TOML `baseline`, else `./.jss-lint-baseline.json`. Renders no report. |
| `--color auto\|always\|never` | choice | `auto` | Colour policy for `--output terminal` and for the terminal formats of `diff`, `explain`, `coverage`. See C-6. |
| `--version` | flag | — | Print the four-line block of `version-output.md` and exit 0. No longer eager: it is evaluated after config loading so `--journal` and `.jss-lint.toml` are honoured. |

`--baseline` and `--update-baseline` with `--output json|sarif|html` are
allowed; `--update-baseline` still renders nothing.

## C-2 New TOML keys (`.jss-lint.toml`)

```toml
baseline = ".jss-lint-baseline.json"   # path, relative to the TOML's directory
color = "auto"                          # auto | always | never
```

Precedence is unchanged: defaults → TOML → flags the user set. No
auto-discovery of a baseline file: without the flag or the key, no
baseline is applied.

## C-3 `coverage` subcommand

```
jss-lint coverage [--format terminal|markdown|json]
jsslint  coverage [--format terminal|markdown|json]
```

Lists every directive in `guide-coverage.yaml` for the active journal
(from `--journal`/TOML), grouped by status (`checked`, `partial`,
`not_checked`, `out_of_scope`) with reason and covering rules. Exit 0;
exit 2 for an unknown format or journal. Byte-identical across engines
for all three formats (`coverage_parity.rs`). A journal without coverage
data prints `jss-lint has no guide-coverage data for journal <id>.` and
exits 0. Rendering contract: `coverage-file.md` C-6.

## C-4 Exit codes with a baseline

| Condition | Code |
|---|---|
| No remaining violation at or above `--fail-on` after baseline suppression | 0 |
| At least one remaining violation at or above `--fail-on` | 1 |
| Error-severity `JSS-PARSE-000` (never baselined) | 2 |
| Baseline file unreadable, malformed, `schema_version != 1`, or `journal` mismatch | 2 |
| `--update-baseline` succeeded | 0 |

Stale and unevaluated entries never affect the exit code. `--fail-on`,
`--ignore-rules`, `--min-confidence` are applied before the baseline;
their findings are `unevaluated`, not `stale`.

## C-5 Streams

| Output | Stream |
|---|---|
| Author-mode footer (always printed, also on a clean run) | **stdout** |
| Reviewer-mode recall line and "Not checked by jss-lint" block | stdout |
| `Baseline: …` summary line | stdout (after the footer) |
| `jss-lint: wrote N baseline entries to <path>` | stderr |
| Rule-set date mismatch note | stderr |
| `--version` block | stdout |

Consequence: `jss-lint paper.tex` on a clean manuscript no longer
produces empty stdout. The exit code remains the CI signal.

## C-6 Colour decision

One pure function of `(flag, toml_value, env, isatty)`, identical in both
CLIs and unit-tested as a matrix:

1. `--color always` → on; `--color never` → off.
2. `NO_COLOR` set and non-empty → off.
3. `CLICOLOR_FORCE` set, non-empty, and not `"0"` → on.
4. TOML `color = "always"|"never"` → that.
5. auto: on iff stdout is a TTY and `TERM != "dumb"`.

`--output json|sarif|html` is never coloured regardless of the decision.
Escape bytes are per-engine (see `color.md` C-4).

## C-7 `--fix` summary line

After applying (or dry-running) fixes, both CLIs print one line to
stdout before the report:

```
Applied 3 fixes to 1 file (2 skipped: conflict 1, rule-not-selected 1).
Dry run: 3 fixes would be applied to 1 file. Re-run without --dry-run to write.
```

Rejections keep their existing stderr line. No git interaction of any
kind (plan §6).

## C-8 Help text

`--help` for the lint command and for `coverage` MUST mention the new
flags; the `--version` row of the spec-001 options table is replaced by
a pointer to `version-output.md`.
