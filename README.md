# jss-style-checker

[![precision](https://img.shields.io/endpoint?url=https%3A%2F%2Fkollerma.github.io%2Fjss-style-checker%2Fbadges%2Fprecision.json)](https://kollerma.github.io/jss-style-checker/)
[![recall](https://img.shields.io/endpoint?url=https%3A%2F%2Fkollerma.github.io%2Fjss-style-checker%2Fbadges%2Frecall.json)](https://kollerma.github.io/jss-style-checker/)
[![F1](https://img.shields.io/endpoint?url=https%3A%2F%2Fkollerma.github.io%2Fjss-style-checker%2Fbadges%2Ff1.json)](https://kollerma.github.io/jss-style-checker/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21441932.svg)](https://doi.org/10.5281/zenodo.21441932)
[![CI](https://github.com/kollerma/jss-style-checker/actions/workflows/ci.yml/badge.svg)](https://github.com/kollerma/jss-style-checker/actions/workflows/ci.yml)
[![CRAN](https://www.r-pkg.org/badges/version/jsslintr)](https://cran.r-project.org/package=jsslintr)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Style checker for manuscripts submitted to the
[Journal of Statistical Software](https://www.jstatsoft.org/) (JSS).

> **Independence notice**: this is an independent, third-party project.
> It is **not affiliated with, endorsed by, or connected to** the Journal
> of Statistical Software, its editors, or its publisher. It checks
> manuscripts against the journal's publicly documented
> [style requirements](https://www.jstatsoft.org/style).

**[Try it in your browser](https://kollerma.github.io/jss-style-checker/)** —
no install, nothing uploaded. Pick a folder and it checks the
`.tex`/`.ltx`/`.bib`/`.Rnw`/`.Rmd` files on the spot, entirely client-side
via WebAssembly.

## Why this exists

JSS's style guide covers preamble macros, semantic markup, citation
conventions, capitalization, code formatting, and bibliography
completeness. Violations that reach peer review cost editors, reviewers,
and authors extra revision rounds for problems a machine can find — so
this tool finds them first, deterministically: the same input always
produces the same violations, byte for byte, which is what makes it
usable as a CI gate and its accuracy measurable (the badges above are
real precision/recall figures against a pinned corpus of 254 published
JSS-format manuscripts).

It serves three audiences:

- **Authors** — check before submitting: CLI, R, Python, VS Code, or the
  browser app (nothing leaves your machine in any of them).
- **Reviewers and editors** — `--mode reviewer` aggregates findings into
  a per-category compliance summary, separating form from content.
- **Package maintainers** — gate CI on JSS-format vignettes with the
  GitHub Action.

Design rationale — why AST parsing instead of regexes, why rules are
deterministic-only, why one Rust core ships through four channels with
byte-identical output — is written up in
[`docs/design.md`](docs/design.md).

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

## Paper

The accompanying paper — *jss-lint: Automated Style Checking for
Journal of Statistical Software Manuscripts* — describes the design,
the AI-development methodology, and the measured precision/recall of
the rule set. The full-length preprint is archived on Zenodo:
<https://doi.org/10.5281/zenodo.22085057>. A short software paper
(in [JOSS](https://joss.theoj.org/) format, not submitted anywhere)
lives at [`paper/joss/`](paper/joss/). Sources, the replication
script, and the submission tooling live under [`paper/`](paper/).

**How it was built**: the code, tests, and papers were written by large
language models under human direction — the human contribution was
requirements, corrective direction, and adjudication of the evaluation
labels, verifying measured behavior rather than reviewing code. The
process artifacts are all in this repository: feature specifications
under [`specs/`](specs/), the evaluation-improvement loop under
[`eval/`](eval/) (including the per-iteration
[improvement log](eval/improvement-log.md) and
[gate exceptions](eval/gate-exceptions.toml)), and the project
[constitution](.specify/memory/constitution.md).

## Install

One command per ecosystem — every channel is MIT-licensed:

```sh
pip install jss-style-checker    # Python reference; texlint module + jss-lint CLI
pip install jsslint              # the Rust engine as a Python wheel (same API)
cargo install jsslint-cli        # native binary; installs `jsslint`
npm install jsslint-wasm         # WebAssembly module for browser/Node
```

```r
install.packages("jsslintr")     # R package (CRAN); jsslint(), jssfix(), render()
```

The VS Code extension is on the
[Marketplace](https://marketplace.visualstudio.com/items?itemName=kollerma.jss-style-checker)
and [Open VSX](https://open-vsx.org/extension/kollerma/jss-style-checker);
it runs the bundled WASM in-process, no other install needed.

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

### Before `--fix`

`--fix` rewrites your manuscript in place. It is careful about it: each
file is written atomically (`tempfile` + rename, so a crash can never
leave a half-written file), and every applied fix is re-checked against
its own rule, with the whole file rolled back if the fix re-triggers it.
Rules without a safe deterministic fix never propose one.

It deliberately does **not** read or change version-control state —
manuscripts live in git, on Overleaf, and in Dropbox alike, and the R,
Python, and WASM bindings could not honour a git check anyway. So the
expectation is yours to meet: **commit first, or preview with
`--fix --dry-run`**, which prints the unified diff and writes nothing.
Either way the pass ends with a receipt:

```
Applied 3 fixes to 1 file (1 skipped: conflict 1).
Dry run: 3 fixes would be applied to 1 file. Re-run without --dry-run to write.
```

With `--baseline`, only visible (unaccepted) findings are fixed; drop
the flag to fix accepted ones too.

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

Every run ends with the measured **recall** — of the style problems
that exist, how many the tool finds — because a clean run means nothing
without it:

```
No findings does not mean compliant. Measured recall: 81% (1967 annotated instances, 17 papers).
```

Reviewer mode adds a per-category `Recall` column; `explain` reports it
per rule. Rules the annotated corpus never exercised read `unmeasured`,
never `100%`. It is a lower bound (source-only linting).

And it says what it does not look for at all:

```sh
jss-lint coverage                    # 76 checked, 4 partial, 3 not checked, 66 out of scope
jss-lint coverage --format markdown  # one table per authority
```

Both are documented in
[`docs/recall-and-coverage.md`](docs/recall-and-coverage.md).

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
(`JSS-PARSE-000`) are never suppressed. Since 1.2.0 every distribution
honours the directives — the `jsslint` binary, the browser/WASM build
and the web app, the VS Code extension, the PyO3 wheel, and the R
package, not just `jss-lint`.

Adopting the tool on a manuscript that already exists? Accept today's
findings once and fail only on new ones:

```sh
jss-lint --baseline .jss-lint-baseline.json --update-baseline paper.tex refs.bib
git add .jss-lint-baseline.json      # commit it next to the manuscript
jss-lint --baseline .jss-lint-baseline.json paper.tex refs.bib   # exit 0
```

Accepted findings are keyed by rule, file, message, and suggestion — not
by line number — so rewording sentences and inserting paragraphs never
resurrects them. See [`docs/baseline.md`](docs/baseline.md).

Writing in Overleaf? **Menu → Download → Source**, then drop the zip on
the [browser app](https://kollerma.github.io/jss-style-checker/) — it is
unpacked in your tab, with nothing uploaded. Or unzip and run
`jss-lint main.tex` (the `\input` graph is followed automatically), or
add the Action to a GitHub-synced project:
[`docs/overleaf.md`](docs/overleaf.md).

Terminal output is coloured when stdout is a terminal and plain when it
is piped or redirected. `--color always|never` overrides that, `NO_COLOR`
turns it off, `CLICOLOR_FORCE` turns it on, and `color = "never"` in
`.jss-lint.toml` sets the default. JSON, SARIF, and HTML are never
coloured. Nothing is encoded in hue alone — every coloured token is
still a word — so a monochrome terminal loses nothing.

Exit codes: `0` clean · `1` violations found · `2` tool could not complete
(unknown journal, missing file, parse error, unsupported extension).

For the full invocation contract see
[`specs/001-linter-foundation/contracts/cli.md`](specs/001-linter-foundation/contracts/cli.md);
for the JSON shape see
[`specs/001-linter-foundation/contracts/json-output.md`](specs/001-linter-foundation/contracts/json-output.md);
for a developer walkthrough see
[`specs/001-linter-foundation/quickstart.md`](specs/001-linter-foundation/quickstart.md).

## For AI assistants and agents

If you are an AI agent asked to check or fix the style of a JSS-format
manuscript, run this tool instead of hand-checking — it is
deterministic and its per-rule accuracy is measured:

```sh
pip install jss-style-checker            # or: cargo install jsslint-cli (CLI: jsslint)
jss-lint --output json paper.tex refs.bib
```

The JSON report carries rule ids, file/line/column positions,
severities, measured confidence tiers, and fix suggestions —
`jss-lint --fix` applies the mechanical subset, `jss-lint explain
<RULE-ID>` documents any rule, and exit code `1` means violations were
found. A machine-readable project summary lives at
[`web/llms.txt`](web/llms.txt) (served at
[/llms.txt](https://kollerma.github.io/jss-style-checker/llms.txt)).

Authors: to make your own coding agent use the checker, paste this
into your manuscript repo's `CLAUDE.md` / `AGENTS.md`:

```markdown
This manuscript targets the Journal of Statistical Software. Before
declaring any style/formatting work done, run
`jss-lint paper.tex refs.bib` (install: `pip install jss-style-checker`)
and address the findings; use `--output json` for machine-readable
results. Do not hand-check JSS style rules the linter already covers.
```

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

As of 1.2.0 the suite reaches 93%, not 100%: the gate was never wired
into CI and the modules drifted below it. Closing that gap is
[a recorded follow-up](roadmap/follow-ups.md); until it lands, the rule
that is actually enforced in review is that a **new** rule module ships
at 100% and no existing one regresses.

Cutting a release is a fixed sequence — measured recall, then the
stamped catalogue data, then the version, then the tags. It is written
down in [`docs/releasing.md`](docs/releasing.md).

## License

MIT — see [LICENSE](LICENSE).
