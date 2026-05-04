# Contract: `jss-lint report` CLI

**Spec**: [../spec.md](../spec.md)
**Plan**: [../plan.md](../plan.md)

## C-1 Subcommand registration

`jss-lint report` MUST be a subcommand of the spec-009 Click
group. The pre-spec-015 entry-points (`jss-lint <PATHS>`,
`explain`, `init`, `lsp`) MUST continue to work unchanged.

## C-2 Section order

The report MUST emit six sections in this exact order:

1. Header (title, author, file count, run date, linter
   version, commit hash).
2. Conformance score (`X %`, formula explanation, fall-
   back note when DB absent).
3. Severity counts (errors / warnings / info).
4. Top-5 most-violated rules (or fewer if fewer distinct
   rules fired).
5. Numbered fix-me-first list.
6. Footer (link to JSS author guide; reproducibility
   note).

A test asserts the section headers appear in this order
in the markdown golden.

## C-3 Score formula

The conformance score MUST be computed as:

```
score = round(100 * (rules_with_zero_violations / total_active_rules))
```

Where:
- `total_active_rules` excludes rules in
  `cfg.ignore_rules` AND rules whose `category` is in
  `{"internal", "parse"}`.
- `rules_with_zero_violations` is the subset of
  `total_active_rules` for which no violation appears in
  `report.violations`.
- When `total_active_rules == 0`, the score is rendered
  as `n/a`.

## C-4 Determinism

Two invocations against equal `(report, document, fmt,
ignore_rules, db_snapshot)` MUST produce byte-identical
output, modulo:
- The run-date line (one ISO-8601 date string in the
  header).
- The commit-hash line (when `git rev-parse` succeeds; the
  hash is the only environmental input outside the DB).

## C-5 Top-5 ordering

`top_five` is sorted by `(count desc, rule_id asc)`. Ties
in `count` break on `rule_id` ascending. The list never
exceeds 5 entries; when fewer distinct rules fired, the
report emits a parenthetical `(only N distinct rules)`
note.

## C-6 Fix-me ordering

The numbered list orders by `(severity asc, precision desc,
rule_id asc)`. `Severity.ERROR` < `Severity.WARNING` <
`Severity.INFO`. When the precision DB is missing,
`precision` is `None`; the precision tiebreaker is replaced
by `rule_id asc` and the report's footer notes the fall-
back.

## C-7 PDF gating

`--format pdf` requires the `[pdf]` extra. If WeasyPrint is
not importable:
- The CLI exits 2.
- Stderr reads:
  `pdf rendering not installed; install with pip install
  "jss-lint[pdf]"`.

`--format html` and `--format md` MUST work without the
`[pdf]` extra.

## C-8 `--out` semantics

| `--format` | `--out` absent                                       | `--out FILE`                              |
| ---------- | ---------------------------------------------------- | ----------------------------------------- |
| `md`       | Write to stdout.                                     | Write to FILE; create if absent.          |
| `html`     | Exit 2 — `--out is required for html/pdf`.            | Write to FILE.                            |
| `pdf`      | Exit 2 — `--out is required for html/pdf`.            | Write to FILE.                            |

When `FILE`'s parent directory does not exist, the CLI
exits 2 with `parent directory not found: <path>`.

## C-9 Manuscript metadata

Title and author resolve in this order:
1. `--title` / `--author` CLI override.
2. Preamble macros (`\title{...}`, `\author{...}` /
   `\Plainauthor{...}`).
3. Header reads `File: <path>` and omits the author line
   when neither is available.

## C-10 No network calls

The renderer MUST NOT make any network requests. The
spec-007 `guide_url` values are emitted as inert links;
the JSS guide URL is fetched neither at render time nor
during PDF rasterisation (WeasyPrint reads from
`html_str` only).

## C-11 Backwards compatibility

`--output html` (the existing per-violation HTML
renderer) is unchanged. `report --format html` is a
separate code path producing a different shape (the
six-section summary, not the violation list). The two
surfaces coexist.
