# Contract — CLI Surface

`jss-lint` is a `click`-based command exposed via the `jss-lint` console script in `pyproject.toml`. Its invocation surface is a stable contract: additive changes within a major version are allowed; removal, renaming, or semantic changes require a major version bump of `texlint` and a CHANGELOG entry.

## Synopsis

```
jss-lint [OPTIONS] FILES...
```

At least one `FILES` argument is required when the tool is expected to produce a report. Invoking `jss-lint` with zero `FILES` prints help to stderr and exits with status 2.

## Options

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--journal <id>` | string | `jss` | Journal module to apply. Must resolve via the `texlint.journals` entry-point group. |
| `--mode <author\|reviewer>` | choice | `author` | Output emphasis. `author` shows per-violation detail; `reviewer` shows the per-category summary table. |
| `--output <terminal\|json\|html\|sarif>` | choice | `terminal` | Renderer for the compliance report. (`sarif` added by spec 006.) |
| `--source-root <DIR>` | path | CWD | Base directory for SARIF `artifactLocation.uri` values. Silently accepted (and ignored) for other output formats. (Spec 006.) |
| `--ignore-rules <csv>` | string | `""` | Comma-separated rule ids to suppress (e.g. `JSS-BIB-001,JSS-SRC-001`). Parsed once into a `frozenset[str]` inside `config.load()`. |
| `--verbose` / `-v` | flag | off | Enables diagnostic output on stderr (config merge trace, per-file parse timing, per-rule counts). Does **not** affect the JSON/HTML renderers' output. |
| `--version` | flag | — | Print `jss-lint <version>` to stdout and exit 0. |
| `-h`, `--help` | flag | — | Print help to stdout and exit 0. |

Unknown flags exit 2 with a click-standard error on stderr.

## Files

Each `FILES` argument is a path. Supported suffixes: `.tex`, `.bib`. Other suffixes are rejected at invocation time with exit 2. Non-existent or unreadable paths exit 2 with a per-path stderr diagnostic. The CLI does **not** recurse into directories — pass explicit file paths. (Directory globbing is the shell's job.)

## Config-file interaction

The CLI looks for `.jss-lint.toml` in the current working directory. Precedence (lowest → highest):

1. `ToolConfig()` built-in defaults
2. Keys present in `.jss-lint.toml`
3. CLI flags the user actually set

A CLI flag that the user did not set does **not** override a file value; this is implemented by looking at click's `Context.get_parameter_source` or by passing sentinel defaults.

Recognised TOML keys mirror the `ToolConfig` dataclass:

```toml
# .jss-lint.toml
journal = "jss"
mode = "author"
output = "terminal"
ignore_rules = ["JSS-BIB-001"]   # list, not CSV string
verbose = false
code_width = 80
```

Unknown keys emit a warning on stderr when `--verbose` is set; they are otherwise ignored (preserves portability across tool versions as keys are added).

## Exit codes

| Code | Meaning |
|------|---------|
| `0` | Tool ran to completion; `ComplianceReport.violations` is empty. |
| `1` | Tool ran to completion; at least one violation (style or parse-error) was produced. |
| `2` | Tool could not complete: unknown CLI option; unknown `--journal`; missing/unreadable input path; unsupported file suffix; configuration error; uncaught internal exception. |

Exit 1 and exit 2 are NOT mutually exclusive in intent but ARE in effect: if a parse error occurs (exit-2 condition) and also a style rule fires (exit-1 condition), the result is exit 2. Parse failures dominate because they signal the report is incomplete.

Only **error-severity** `JSS-PARSE-000` findings trigger exit 2. A warning-severity `JSS-PARSE-000` marks a *degraded* parse — the file was recovered and fully linted (e.g. Latin-1 encoding fallback, duplicate-BibTeX-field recovery, tolerant-parser retry) — and obeys the normal `--fail-on` threshold like any other finding.

Implemented via `sys.exit(code)` from `main()` (not `click.Context.exit(...)`), for cleaner interop with `click.testing.CliRunner.invoke(...).exit_code`.

## Streams

| Output | Stream |
|--------|--------|
| `--output terminal` rendering | **stdout** |
| `--output json` document | **stdout** |
| `--output html` document | **stdout** |
| `--output sarif` document | **stdout** (spec 006) |
| `--verbose` diagnostics | **stderr** |
| Exit-2 error messages | **stderr** |
| `--help`, `--version` | stdout, exit 0 |

Rationale: Unix convention. `jss-lint x.tex > report.json` works. `jss-lint x.tex 2>/dev/null` suppresses diagnostics without eating the report. On exit 2 with `--output json`, stdout STILL carries a valid JSON document whose `violations` include the `JSS-PARSE-000` entries (spec Story 3 scenario 3).

## Example invocations

```bash
# Author, terminal (default): exit 0 or 1
jss-lint paper.tex references.bib

# Reviewer, terminal: exit 0 or 1
jss-lint --mode reviewer paper.tex references.bib

# CI: JSON to a file, exit propagates
jss-lint --output json paper.tex references.bib > report.json
echo "exit=$?"

# Alternate journal (fixture — proves plugin discovery)
jss-lint --journal stub paper.tex

# Suppress one rule
jss-lint --ignore-rules JSS-SRC-001 paper.tex

# HTML report
jss-lint --output html --mode reviewer paper.tex references.bib > report.html
```

## Testing the CLI

`tests/integration/` uses `click.testing.CliRunner()`:

```python
from click.testing import CliRunner
from texlint.cli import main

runner = CliRunner()
result = runner.invoke(main, ["--output", "json", str(compliant_tex)])
assert result.exit_code == 0
assert "\"violations\":" in result.output
```

**Do not** pass `mix_stderr=` — it was removed in click 8.2. When stderr is under test, use `result.stderr_bytes` (click ≥8.1). The integration test suite covers: every renderer × mode combination, every exit code, the config precedence merge, and plugin discovery through the `stub_journal` fixture.
