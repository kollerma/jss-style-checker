# jss-style-checker

[![precision](https://img.shields.io/endpoint?url=https%3A%2F%2Fkollerma.github.io%2Fjss-style-checker%2Fbadges%2Fprecision.json)](https://kollerma.github.io/jss-style-checker/)
[![recall](https://img.shields.io/endpoint?url=https%3A%2F%2Fkollerma.github.io%2Fjss-style-checker%2Fbadges%2Frecall.json)](https://kollerma.github.io/jss-style-checker/)
[![F1](https://img.shields.io/endpoint?url=https%3A%2F%2Fkollerma.github.io%2Fjss-style-checker%2Fbadges%2Ff1.json)](https://kollerma.github.io/jss-style-checker/)

Style checker for manuscripts submitted to the
[Journal of Statistical Software](https://www.jstatsoft.org/) (JSS).

> The badges above read shields.io endpoint JSON files refreshed by
> CI from the spec-002 precision-history DB and the spec-017 recall
> corpus. They go live when the gh-pages publish workflow ships and
> the recall corpus is annotated; until then they render as the
> shields-io fallback. See
> [`roadmap/follow-ups.md`](roadmap/follow-ups.md).

The package ships:

- `jss-lint`, a command-line entry point.
- `texlint`, an importable Python library.
- `eval-jss`, a companion CLI that measures per-rule precision against a
  pinned corpus of real JSS manuscripts (see
  [`eval/README.md`](eval/README.md) and
  [`specs/002-eval-jss-harness/quickstart.md`](specs/002-eval-jss-harness/quickstart.md)).

## Install (development)

```sh
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/pip install -e tests/fixtures/stub_journal   # registers the second-journal test fixture
```

## Quick start

Run the linter against a LaTeX manuscript and its bibliography:

```sh
jss-lint paper.tex refs.bib              # author mode, terminal output
jss-lint --mode reviewer paper.tex       # per-category PASS/FAIL/SKIPPED table
jss-lint --output json paper.tex > r.json  # byte-deterministic JSON
jss-lint --output html --mode reviewer paper.tex > r.html
jss-lint --ignore-rules JSS-SRC-001 paper.tex   # suppress a rule
jss-lint --fail-on error paper.tex       # warnings/advisories don't flip CI red
jss-lint --min-confidence medium paper.tex  # skip low-precision heuristic rules
```

Every rule carries a measured-precision **confidence tier** (`high` /
`medium` / `low`), sourced from the [eval corpus](eval/README.md)
precision history. Medium/low findings are marked in the terminal
table and in the JSON `confidence` field; `--min-confidence` skips
rules below the floor, and `--fail-on` sets the severity that flips
the exit code (default `info`: any violation fails). Both are also
settable in `.jss-lint.toml` (`min_confidence`, `fail_on`).

To silence a single false positive in place (instead of disabling the
whole rule project-wide), add an inline comment on the offending line —
or on its own line directly above it:

```tex
The sandwich estimator is robust.  % jss-lint: ignore JSS-MARKUP-002
% jss-lint: ignore JSS-CAP-002
\section{Changes from Version 1.2 to 1.3}
```

A bare `% jss-lint: ignore` suppresses every rule on the target line;
free text after the rule ids is treated as rationale. Parse errors
(`JSS-PARSE-000`) are never suppressed.

Exit codes: `0` clean · `1` violations found · `2` tool could not complete
(unknown journal, missing file, parse error, unsupported extension).

For the full invocation contract see
[`specs/001-linter-foundation/contracts/cli.md`](specs/001-linter-foundation/contracts/cli.md);
for the JSON shape see
[`specs/001-linter-foundation/contracts/json-output.md`](specs/001-linter-foundation/contracts/json-output.md);
for a developer walkthrough see
[`specs/001-linter-foundation/quickstart.md`](specs/001-linter-foundation/quickstart.md).

## Journals

`jss-lint` discovers journals via the `texlint.journals` entry-point group.
The `jss` journal ships with the package; third-party packages can register
additional journals with zero edits to this repo (Constitution §IV).

The `jss` journal ships **58 rules** across 15 categories — full
catalogue with descriptions, severity, JSS-guide §, example
violations, and example fixes:

→ [`specs/003-jss-rule-catalogue/catalogue.md`](specs/003-jss-rule-catalogue/catalogue.md)

The catalogue is generated from `catalogue.yaml`; edit the YAML
and re-render with `python -m tools.render_catalogue`. From the
CLI, `jss-lint explain` lists every rule one-line at a time;
`jss-lint explain <RULE-ID>` shows the full explanation for one
rule.

The `eval-jss` precision harness (spec 002) is shipped — it
enforces Constitution §VI empirically against the pinned corpus
under `examples/` and the manifest at `eval/corpus-manifest.csv`.
Precision trends land in `eval/report.csv` as an append-only
history; diff it with `git log -p eval/report.csv`.

## Development

Helper scripts activate the project `.venv` and forward their arguments:

- `scripts/vpy.sh`  — run Python.
- `scripts/vlint.sh` — run `ruff` (default: `ruff check .`).
- `scripts/vtest.sh` — run `pytest`. Supports `--tail=N` and `--grep=PATTERN`
  to replace `| tail` / `| grep` idioms.

**Pre-commit hook** — `.githooks/pre-commit` runs `ruff check .` so the
CI lint gate never sees a dirty commit. Activate it once per clone:

```sh
git config core.hooksPath .githooks
```

The hook is lenient when `ruff` isn't on `PATH` (skips with a warning)
so it doesn't block users who haven't yet run `pip install -e .[dev]`.

Mandatory gate (Constitution §IX — 100% branch coverage on every rule module):

```sh
.venv/bin/python -m pytest tests/unit/journals/jss/ \
  --cov=src/texlint/journals/jss/rules --cov-branch --cov-fail-under=100
```

## License

MIT — see [LICENSE](LICENSE).
