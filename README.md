# jss-style-checker

Style checker for manuscripts submitted to the
[Journal of Statistical Software](https://www.jstatsoft.org/) (JSS).

The package ships:

- `jss-lint`, a command-line entry point.
- `texlint`, an importable Python library.

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
```

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

Foundation-step smoke rules in the `jss` journal:

| Rule id | Shape | Description |
|---|---|---|
| `JSS-CITE-001` | LaTeX AST | `\emph{bibkey}` used instead of `\cite{bibkey}` |
| `JSS-BIB-001` | BibTeX | bibliography entry missing a `year` field |
| `JSS-SRC-001` | Source scan | source line exceeds `code_width` (default 80) |
| `JSS-PARSE-000` | Parser | non-fatal parse failure in a `.tex` or `.bib` file |

The full 53-rule JSS catalogue, `--fix` support, `.Rnw`/`.Rmd` dispatch,
and the `eval-jss` precision-evaluation CLI land in later steps.

## Development

Helper scripts activate the project `.venv` and forward their arguments:

- `scripts/vpy.sh`  — run Python.
- `scripts/vlint.sh` — run `ruff` (default: `ruff check .`).
- `scripts/vtest.sh` — run `pytest`. Supports `--tail=N` and `--grep=PATTERN`
  to replace `| tail` / `| grep` idioms.

Mandatory gate (Constitution §IX — 100% branch coverage on every rule module):

```sh
.venv/bin/python -m pytest tests/unit/journals/jss/ \
  --cov=src/texlint/journals/jss/rules --cov-branch --cov-fail-under=100
```

## License

MIT — see [LICENSE](LICENSE).
