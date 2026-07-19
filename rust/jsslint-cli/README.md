# jsslint

A command-line style checker for LaTeX / Sweave / R Markdown manuscripts
(`.tex`/`.ltx`/`.Rnw`/`.Rmd` + `.bib`) submitted to the
[Journal of Statistical Software](https://www.jstatsoft.org/) (JSS). Part of
the [JSS style checker](https://github.com/kollerma/jss-style-checker) project.

This crate installs the standalone **`jsslint`** binary. It's the fullest of
the JSS-checker distributions — the only one with `--fix`, opt-in online DOI
verification (`--crossref`), the `explain` / `diff` / `init` / `report`
subcommands, and an LSP server.

## Install

```sh
cargo install jsslint-cli
```

## Usage

```sh
jsslint paper.tex refs.bib                    # author mode, terminal output
jsslint --mode reviewer paper.Rnw             # per-category PASS/FAIL table
jsslint --output json paper.tex > report.json # also: sarif, html
jsslint --ignore-rules JSS-SRC-001 paper.tex  # suppress a rule
jsslint --min-confidence medium paper.tex     # skip low-precision heuristics
jsslint --fix paper.tex                       # apply safe auto-fixes
jsslint --fix --dry-run paper.tex             # preview fixes as a diff
jsslint --crossref refs.bib                   # online: verify missing DOIs
jsslint --crossref --fix refs.bib             # online: write the DOIs in
```

Linting a root file automatically follows `\input`/`\include`/`\subfile`/
`\bibliography` references and lints the whole reachable project
(`--no-resolve` restricts to the named files). A directory argument expands
to every `.tex`/`.ltx`/`.bib`/`.Rnw`/`.Rmd` file inside it. A
`.jss-lint.toml` in the current directory (or an ancestor) supplies defaults
for any flag you don't pass explicitly; CLI flags win.

Everything is offline by default; `--crossref` is the only network feature
(Crossref / doi.org lookups of bibliographic metadata — never manuscript
content).

Exit codes: `0` clean · `1` violations found (at/above `--fail-on`, default
`info`) · `2` the tool could not complete (bad args, unreadable file, unknown
journal).

### Subcommands

```sh
jsslint explain [JSS-MARKUP-001]   # list or explain rules
jsslint diff old.json new.json     # diff two --output json reports
jsslint init paper.tex             # write a tuned .jss-lint.toml
jsslint report paper.tex           # one-page conformance report (markdown)
jsslint report paper.tex --format html --out r.html   # or pdf
jsslint lsp                        # LSP 3.17 server over stdio
```

See the [project README](https://github.com/kollerma/jss-style-checker) for
the full rule catalogue, the other distributions (browser/WASM, Python, R),
and design notes.

## License

MIT.
