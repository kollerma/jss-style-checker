# Checking an Overleaf project

Most JSS manuscripts are written in Overleaf, which has no shell to run
a linter in. There are three ways to check one, and none of them
requires uploading your manuscript anywhere.

## 1. Drop the source zip on the browser app

**Menu → Download → Source** gives you a `.zip` of the whole project.
Drop it on
[the browser app](https://kollerma.github.io/jss-style-checker/) — or
click "Drop or choose an Overleaf .zip…".

The zip is unpacked **in your browser tab**: the checker is a
WebAssembly build of the same engine the command-line tool uses, and the
page makes no network request after it loads. Nothing is uploaded, which
matters for an unpublished manuscript.

Entry paths are kept as given, so `\input{sections/intro}` resolves and
the report's file headings match your project's layout. Figures, PDFs,
and macOS `__MACOSX/` resource forks are ignored; only
`.tex`, `.ltx`, `.bib`, `.Rnw`, and `.Rmd` are read.

Unpacking needs `DecompressionStream("deflate-raw")` — Chrome 103+,
Firefox 113+, Safari 16.4+. On an older browser the page says so and
points you at the folder picker; unzip the download yourself and use
"Choose a folder…".

### Running the app locally

To try it against a project before it is deployed, build the bundle and
serve `web/` over HTTP (`file://` blocks ES-module imports and the WASM
fetch):

```sh
cd rust/jsslint-wasm && wasm-pack build --release --target web --out-dir ../../web/pkg
cd ../../web && python3 -m http.server 8000
```

If the page reports `RangeError: WebAssembly.Table.grow()`, the build
picked up an old system `wasm-opt` (Binaryen ≤ 108 mangles the
reference-type tables). Build with `--no-opt`, or put a current Binaryen
first on `PATH`. CI is unaffected: its runners have no system
`wasm-opt`, so wasm-pack downloads a current one.

## 2. Unzip and run the command-line tool

For a full report, auto-fixes, or a baseline, download the source zip
and run the real thing:

```sh
unzip project.zip -d project && cd project
jss-lint main.tex          # or: jsslint main.tex
```

Passing the **root file only** is enough: `\input`, `\include`,
`\subfile`, and `\bibliography` are followed automatically, so the whole
project is checked as one document. Add `--fix --dry-run` to preview
mechanical corrections, then `--fix` to apply them, and re-upload the
changed files (Overleaf's Menu → Upload, or drag them into the file
tree).

If the project already has findings you do not intend to fix now, accept
them once and check only what is new afterwards:

```sh
jss-lint --baseline .jss-lint-baseline.json --update-baseline main.tex
```

See [`baseline.md`](baseline.md).

## 3. GitHub Sync — check on every push

Overleaf's GitHub Sync (a premium feature) mirrors the project to a
repository. Add the Action to that repository and every sync is checked:

```yaml
# .github/workflows/jss-lint.yml
name: JSS style
on: [push, pull_request]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: kollerma/jss-style-checker@v1
        with:
          version: 1.2.0
          fail-on-severity: warning
```

For a manuscript that predates the linter, commit a baseline and point
the Action at it, so the check fails only on new findings:

```yaml
        with:
          baseline: .jss-lint-baseline.json
```

Findings the baseline accepts are absent from the SARIF the Action
uploads, so the Security tab and the PR annotations show only what is
new.

## Which one to use

| You want | Use |
|---|---|
| A quick look, nothing installed | the browser app (1) |
| Auto-fixes, a baseline, or CI-style exit codes | the CLI (2) |
| A check on every Overleaf save | GitHub Sync + the Action (3) |

A CLI that reads a `.zip` directly is a
[recorded follow-up](../roadmap/follow-ups.md); today, `unzip` first.
