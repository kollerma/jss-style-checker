# jss-style-checker

[![precision](https://img.shields.io/endpoint?url=https%3A%2F%2Fkollerma.github.io%2Fjss-style-checker%2Fbadges%2Fprecision.json)](https://kollerma.github.io/jss-style-checker/)
[![recall](https://img.shields.io/endpoint?url=https%3A%2F%2Fkollerma.github.io%2Fjss-style-checker%2Fbadges%2Frecall.json)](https://kollerma.github.io/jss-style-checker/)
[![F1](https://img.shields.io/endpoint?url=https%3A%2F%2Fkollerma.github.io%2Fjss-style-checker%2Fbadges%2Ff1.json)](https://kollerma.github.io/jss-style-checker/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21441932.svg)](https://doi.org/10.5281/zenodo.21441932)

Style checker for manuscripts submitted to the
[Journal of Statistical Software](https://www.jstatsoft.org/) (JSS).

**[Try it in your browser](https://kollerma.github.io/jss-style-checker/)** —
no install, nothing uploaded. Pick a folder and it checks the
`.tex`/`.ltx`/`.bib`/`.Rnw`/`.Rmd` files on the spot, entirely client-side
via WebAssembly.

> The badges above are refreshed by CI on every push to `main`: shields.io
> endpoint JSON derived from the spec-002 precision-history DB and the
> spec-017 hand-annotated recall corpus.

The package ships:

- `jss-lint`, a command-line entry point.
- `texlint`, an importable Python library.
- `eval-jss`, a companion CLI that measures per-rule precision against a
  pinned corpus of real JSS manuscripts (see
  [`eval/README.md`](eval/README.md) and
  [`specs/002-eval-jss-harness/quickstart.md`](specs/002-eval-jss-harness/quickstart.md)).

The same engine also ships as a Rust port, compiled five ways: a standalone
binary ([`jsslint-cli`](https://crates.io/crates/jsslint-cli) on crates.io),
a browser/npm WASM package ([`jsslint-wasm`](https://www.npmjs.com/package/jsslint-wasm) —
the [in-browser checker](https://kollerma.github.io/jss-style-checker/)
above, source at [`web/`](web/)), a native Python extension
([`jsslint`](https://pypi.org/project/jsslint/) on PyPI), an R package
(`jsslintr`), and a zero-install VS Code extension that runs the WASM
in-process ([`vscode-extension/`](vscode-extension/)) — see
[`rust/README.md`](rust/README.md) for how to use each (including how to
build and run the web app locally). Both engines produce byte-identical
output; that parity is CI-enforced (Constitution §XIII).

## Install (development)

```sh
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/pip install -e tests/fixtures/stub_journal   # registers the second-journal test fixture
```

## Quick start

Run the linter against a LaTeX (or Sweave `.Rnw` / R Markdown `.Rmd`)
manuscript and its bibliography. Linting a root file automatically follows
`\input`/`\include`/`\subfile`/`\bibliography` references and lints the
whole reachable project (`--no-resolve` restricts to the named files):

```sh
jss-lint paper.tex refs.bib              # author mode, terminal output
jss-lint --mode reviewer paper.tex       # per-category PASS/FAIL/SKIPPED table
jss-lint --output json paper.tex > r.json  # byte-deterministic JSON
jss-lint --output html --mode reviewer paper.tex > r.html
jss-lint --ignore-rules JSS-SRC-001 paper.tex   # suppress a rule
jss-lint --fail-on error paper.tex       # warnings/advisories don't flip CI red
jss-lint --min-confidence medium paper.tex  # skip low-precision heuristic rules
jss-lint --crossref refs.bib             # online: verify missing DOIs
jss-lint --crossref --fix refs.bib       # online: populate missing DOIs
```

### Online DOI lookup (`--crossref`)

By default the linter is fully offline, so `JSS-REFS-003` can only
*advise* that a citeable entry declares a `doi` field — it can't know
whether one exists. Pass `--crossref` to verify online: each doi-less
`@article` / `@book` / `@inproceedings` is looked up on
[Crossref](https://www.crossref.org/) (matched by title + first-author
surname + year), and each CRAN-package `@manual` gets its registered
`10.32614/CRAN.package.*` DOI. `JSS-REFS-003` then reports the exact DOI
to add and *suppresses* the advisory when no DOI exists. Combine with
`--fix` to write the DOIs straight into the `.bib`. Add
`--crossref-mailto you@example.org` to use Crossref's faster polite
pool. Needs network access; wrong-match-safe (a mismatched year or
author is never written).

Every rule carries a measured-precision **confidence tier** (`high` /
`medium` / `low`), sourced from the [eval corpus](eval/README.md)
precision history. Medium/low findings are marked in the terminal
table and in the JSON `confidence` field; `--min-confidence` skips
rules below the floor, and `--fail-on` sets the severity that flips
the exit code (default `warning`: info-severity advisories are reported
but don't fail the run). Both are also settable in `.jss-lint.toml`
(`min_confidence`, `fail_on`).

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

The `jss` journal ships **62 rules** across 16 categories — full
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

**Pre-commit hook** — `.githooks/pre-commit` runs `ruff check .`, the
pytest suite (`SKIP_PYTEST=1` to opt out per commit), and — when Rust files
are staged — `cargo fmt --all --check`, so the CI gates never see a dirty
commit. Activate it once per clone:

```sh
git config core.hooksPath .githooks
```

The hook is lenient when a tool isn't on `PATH` (skips with a warning)
so it doesn't block users who haven't yet run `pip install -e .[dev]`.
See [CONTRIBUTING.md](CONTRIBUTING.md) for the full gate list.

Mandatory gate (Constitution §IX — 100% branch coverage on every rule module):

```sh
.venv/bin/python -m pytest tests/unit/journals/jss/ \
  --cov=src/texlint/journals/jss/rules --cov-branch --cov-fail-under=100
```

## License

MIT — see [LICENSE](LICENSE).
