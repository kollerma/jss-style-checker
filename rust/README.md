# jsslint-core and its four tools

`jsslint-core` (this directory's Cargo workspace) is a Rust reimplementation
of the JSS style-checker engine that the top-level `jss-style-checker`
Python package also ships. One engine, compiled four ways:

| Tool | What it is | Package name | Lives in |
|---|---|---|---|
| `jsslint` | standalone CLI binary | `jsslint-cli` (crates.io) | `rust/jsslint-cli/` |
| `jsslint-wasm` | browser / Node.js library | `jsslint-wasm` (npm) | `rust/jsslint-wasm/` |
| `jsslint` | Python extension module | `jsslint` (PyPI) | `rust/jsslint-py/` |
| `jsslintr` | R package | `jsslintr` (CRAN, eventually) | `r/jsslintr/` |

The CLI, WASM, and Python packages are **published** (crates.io / npm /
PyPI; tag-triggered workflows at
`.github/workflows/release-{crates,npm-wasm,pypi}.yml`). The R package is
not yet on CRAN — install it from this checkout (section 4). On top of the
four libraries sit two ready-made applications: the
[in-browser checker](https://kollerma.github.io/jss-style-checker/)
(`web/`) and a zero-install VS Code extension that runs the WASM in-process
(`vscode-extension/`).

All four tools accept the same logical inputs (file paths + contents,
`journal`/`mode`/`output`/`ignore_rules`/`min_confidence`/`fail_on`) and
render the same four report formats: `terminal`, `json`, `sarif`, `html`.
Exit-code / return-value conventions differ per ecosystem (see each section).

---

## 1. `jsslint` — the CLI binary

Source: `rust/jsslint-cli/`. Wraps the same engine as the Python `jss-lint`
CLI, plus `explain`/`diff`/`init`/`report`/`lsp` subcommands.

### Install

```sh
cargo install jsslint-cli        # from crates.io
```

Or build from this checkout:

```sh
cd rust
cargo build --release -p jsslint-cli   # binary at rust/target/release/jsslint
cargo install --path jsslint-cli       # or install onto your PATH
```

### Lint a manuscript

```sh
jsslint paper.tex refs.bib                    # author mode, terminal output
jsslint --mode reviewer paper.tex             # per-category PASS/FAIL/SKIPPED table
jsslint --output json paper.tex > report.json # byte-deterministic JSON
jsslint --output sarif paper.tex > report.sarif
jsslint --output html --mode reviewer paper.tex > report.html
jsslint --ignore-rules JSS-SRC-001 paper.tex  # suppress a rule
jsslint --fail-on error paper.tex             # warnings/advisories don't flip exit code
jsslint --min-confidence medium paper.tex     # skip low-precision heuristic rules
jsslint --journal jss --source-root . paper.tex
```

Exit codes: `0` clean · `1` violations found (at/above `--fail-on`, default
`warning`) · `2` the tool could not complete (bad args, unreadable file, unknown
journal, etc).

A directory argument is expanded to every `.tex`/`.ltx`/`.bib`/`.Rnw`/`.Rmd`
file inside it. `.jss-lint.toml` in the current directory (or an ancestor) supplies
defaults for any flag you don't pass explicitly — CLI flags win.

### Auto-fix

```sh
jsslint --fix paper.tex                       # apply fixes, atomic write per file
jsslint --fix --dry-run paper.tex              # print a unified diff, write nothing
jsslint --fix --apply paper.tex                # prompt [y/n/a/q] per fix
jsslint --fix --fix-rule JSS-MARKUP-001 paper.tex  # repeatable; limit to named rules
```

### Online DOI verification (opt-in, needs network)

```sh
jsslint --crossref refs.bib                              # verify/report missing DOIs
jsslint --crossref --crossref-mailto you@example.org refs.bib   # polite pool
jsslint --crossref --fix refs.bib                         # write the resolved DOIs in
```

`--crossref` looks up `JSS-REFS-003`-eligible entries (article/book/
inproceedings/incollection against Crossref; `@Manual` CRAN packages against
`doi.org`) and turns the offline "add a doi if available" advisory into an
online-verified one: it reports the exact DOI when one exists (with a `--fix`
payload) and suppresses the advisory when it doesn't. Off by default —
everything else in `jsslint` stays fully offline. The network client lives in
a separate crate, `jsslint-crossref` (below), never linked into
`jsslint-wasm`/`jsslint-py`/`jsslintr`.

### Subcommands

```sh
jsslint explain                       # list every rule by category
jsslint explain JSS-MARKUP-001        # explain one rule (terminal or --format markdown)
jsslint diff old.json new.json        # diff two `--output json` reports
jsslint diff old.json new.json --ignore-line-drift --format markdown
jsslint init paper.tex                # write a tuned .jss-lint.toml (--dry-run / --force / --threshold)
jsslint report paper.tex              # one-page conformance report, markdown
jsslint report paper.tex --out report.md --title "My Paper" --author "Jane Doe"
```

`report --format html` is byte-for-byte identical to the Python CLI's HTML
output (see `rust/jsslint-cli/tests/report_parity.rs`).

`report --format pdf` renders a self-contained PDF via the pure-Rust `genpdf`
crate (`rust/jsslint-cli/src/report_pdf.rs`), embedding a vendored DejaVu Sans
font (`rust/jsslint-cli/assets/fonts/`) so it works without any fonts
installed on the host. **It is not byte- or visually-identical to the Python
CLI's PDF**: Python renders `conformance.html.j2` through WeasyPrint (a full
HTML+CSS layout engine), and no pure-Rust equivalent exists that reproduces
WeasyPrint's output — reproducing it byte-for-byte was evaluated and ruled
infeasible. This port's PDF is an independently laid out document carrying
the same content instead. `--format pdf` requires `--out FILE` (PDF is
binary, so there's no stdout behavior — same guard as the Python CLI).

`genpdf` pulls in `printpdf` 0.3.4 transitively, and that version writes a
malformed ToUnicode CMap for any embedded font glyph above U+FFFF (a raw
5-hex-digit codepoint instead of a UTF-16BE surrogate pair) — the vendored
DejaVu Sans faces trip this on *every* generated PDF regardless of report
content, since their cmap tables include supplementary-plane glyphs. Fixed
by vendoring a patched `printpdf` 0.3.4 (`rust/vendor/printpdf-0.3.4`, wired
up via `[patch.crates-io]` in `rust/Cargo.toml`) rather than bumping the
version: `genpdf` 0.2.0 (the only release on crates.io) pins `printpdf`
to exactly `0.3.4`, no newer 0.3.x patch release exists, the bug is still
present unfixed through 0.11.x, and the 0.12.0 rewrite that does fix it has
a completely different, incompatible API that `genpdf` 0.2.0 can't consume.
See `rust/vendor/printpdf-0.3.4/NOTICE.md` for the full writeup.

`jsslint lsp` starts a synchronous LSP 3.17 server over stdio (diagnostics +
code actions + workspace edits) for any editor with an LSP client. (The
project's own VS Code extension does NOT use it — it runs the WASM build
in-process instead, so it needs no installed binary; the LSP server is for
other editors.)

### `jsslint-crossref` — the `--crossref` network client

Source: `rust/jsslint-crossref/`. Not a standalone tool — an internal
dependency of `jsslint-cli` only, kept in its own crate so the network
client (`ureq`, pure-Rust/rustls) can never end up in `jsslint-wasm`'s
dependency graph even by accident (`cargo tree -p jsslint-wasm` never
mentions it — that's a CI-checkable fact, not a convention). It ports
`texlint/crossref.py`: Crossref title/author/year matching for
article/book/inproceedings/incollection entries, and the CRAN
`10.32614/CRAN.package.NAME` DOI shortcut (confirmed via `doi.org`) for
`@Manual` entries. `jsslint-core` itself stays fully offline — it only
defines the injection hook (`config::DoiResolver`) that
`JSS-REFS-003` consumes; see that crate's and this one's module docs.

---

## 2. `jsslint-wasm` — browser / Node.js

Source: `rust/jsslint-wasm/`. Compiles the same engine to WebAssembly. No
network access is linked in at all (not even behind a flag) — manuscripts
never leave the machine, by construction.

There's also a minimal ready-to-use browser app built on this binding —
[try it live](https://kollerma.github.io/jss-style-checker/), or see
[`web/`](../web/) for its source (`index.html` + one `app.js`, no build
tooling beyond `wasm-pack`) and `.github/workflows/publish-web.yml` for how
it's deployed.

#### Running the web app locally

The hosted app rebuilds automatically on every push to `main`
(`.github/workflows/publish-web.yml`), but to build and serve it yourself —
e.g. to try a local change before it ships:

```sh
rustup target add wasm32-unknown-unknown   # once
cargo install wasm-pack                    # once

cd rust/jsslint-wasm
wasm-pack build --release --target web --out-dir ../../web/pkg

cd ../../web
python3 -m http.server 8000                # any static file server works
```

Then open <http://localhost:8000>. Serving over `file://` won't work — the
app is an ES module that `fetch()`es the `.wasm` file, which browsers block
for `file://` origins, so it needs a real (even if local) HTTP server.
`web/pkg/` is build output (git-ignored); re-run the `wasm-pack build` step
after any change under `rust/jsslint-core/` or `rust/jsslint-wasm/`.

### Install

```sh
npm install jsslint-wasm         # from npm
```

Or build from this checkout:

```sh
cd rust/jsslint-wasm
rustup target add wasm32-unknown-unknown  # once
wasm-pack build --release --target bundler   # for webpack/vite/rollup consumers
# or: wasm-pack build --release --target nodejs   # for plain `require()` in Node
# output: rust/jsslint-wasm/pkg/
```

### Use it

Three exports, all taking the same request object (camelCase keys):

- `render(request)` — lint and return the report as a string
  (`terminal`/`json`/`sarif`/`html` via `output`).
- `fix(request)` — apply every safe auto-fix in memory and return the
  changed files as `[path, fixedContents]` pairs (`output` ignored; files
  with nothing to fix are omitted).
- `analyze(request)` — return structured violations, each carrying its
  auto-fix payload (`{start, end, replacement, description}`) when one
  exists. This is what the VS Code extension's per-diagnostic quick fixes
  use — `render(json)`'s `fix` field is deliberately `null` for byte-parity
  with the Python JSON contract.

The call is identical regardless of build target — only how you import the
module differs:

```js
// --target bundler (webpack/vite/rollup) — wasm loading is handled by the
// bundler, no manual init step:
import { render } from "jsslint-wasm";

// --target nodejs — plain CommonJS require(), also no init step (this is
// what rust/jsslint-wasm/tests/wasm_parity.rs exercises):
// const { render } = require("jsslint-wasm");

const report = render({
  files: [["paper.tex", texSource], ["refs.bib", bibSource]],
  output: "json",           // "terminal" | "json" | "sarif" | "html"
  mode: "reviewer",         // "author" | "reviewer"
  ignoreRules: "JSS-SRC-001,JSS-MARKUP-001",
  minConfidence: "medium",  // "low" | "medium" | "high"
  failOn: "error",          // "error" | "warning" | "info"
  sourceRoot: undefined,
  verbose: false,
});
```

`files` is an array of `[path, contents]` pairs (a Rust tuple serializes to
a 2-element JS array). Every field except `files` is optional. There's no
`.jss-lint.toml` filesystem lookup on this target (no real filesystem in
`wasm32-unknown-unknown`) — pass overrides explicitly if you need non-default
behaviour.

---

## 3. `jsslint` — the Python extension module

Source: `rust/jsslint-py/`. A PyO3 native extension; also doubles as this
project's in-process Rust/Python parity oracle
(`tests/unit/test_jsslint_parity.py`).

### Install

```sh
pip install jsslint              # from PyPI
```

One wheel per platform covers CPython 3.10+ via the stable ABI
(`abi3-py310`) — no per-Python-version wheel needed. Or build from this
checkout:

```sh
cd rust/jsslint-py
pip install maturin   # already in the root project's [dev] extras
maturin develop --release   # builds + installs into your active venv
```

### Use it

```python
import jsslint

report = jsslint.render(
    [("paper.tex", open("paper.tex").read()), ("refs.bib", open("refs.bib").read())],
    output="json",             # "terminal" | "json" | "sarif" | "html"
    mode="reviewer",           # "author" | "reviewer"
    journal="jss",
    ignore_rules="JSS-SRC-001,JSS-MARKUP-001",
    min_confidence="medium",   # "low" | "medium" | "high"
    fail_on="error",           # "error" | "warning" | "info"
    source_root=None,
    verbose=False,
)
```

`render()` returns the rendered report as a `str`; it raises `ValueError` on
an unparseable input file. `files` is a list of `(path, contents)` pairs.
Every keyword argument is optional and layers over `.jss-lint.toml` in the
current working directory, same as the CLI.

---

## 4. `jsslintr` — the R package

Source: `r/jsslintr/` (not part of the `rust/` Cargo workspace — a real R
package needs its own `DESCRIPTION`/`NAMESPACE`/`src` layout; its embedded
Rust crate at `r/jsslintr/src/rust/` depends on `jsslint-core` via a relative
path and is built by `src/Makevars`).

### Build

```sh
R CMD INSTALL r/jsslintr
```

This needs the standard R package toolchain: `r-base-dev`, `cmake`,
`libgit2-dev`, `libuv1-dev` (all present in this project's devcontainer). If
the system R library isn't writable, install to a user library instead:

```sh
mkdir -p ~/R/library
R CMD INSTALL --library=~/R/library r/jsslintr
```

**Once published:** `install.packages("jsslintr")` (CRAN) or via
R-universe once registered. Unlike the other three tools, there's no CI
workflow for this: R-universe registration lives in a separate "universe"
GitHub repo, and CRAN submission is an inherently manual review process —
neither is something a workflow in this repo can automate.

### Use it

The convenience API lints files straight from disk — `jss_files()`
discovers every `.tex`/`.ltx`/`.bib`/`.Rnw`/`.Rmd` in the working
directory:

```r
library(jsslintr)

jsslint()                       # lint everything jss_files() finds
jsslint(c("paper.Rnw", "refs.bib"), mode = "reviewer")
jssfix("paper.tex")             # apply safe auto-fixes in place
jssfix("paper.tex", dry_run = TRUE)   # preview without writing
```

The lower-level `render()` takes file *contents* (no filesystem access —
it is the same in-memory seam the other bindings expose):

```r
report <- jsslintr::render(
  files = c(
    "paper.tex" = paste(readLines("paper.tex"), collapse = "\n"),
    "refs.bib"  = paste(readLines("refs.bib"), collapse = "\n")
  ),
  output = "json",           # "terminal" | "json" | "sarif" | "html"
  mode = "reviewer",         # "author" | "reviewer"
  ignore_rules = "JSS-SRC-001,JSS-MARKUP-001",
  min_confidence = "medium", # "low" | "medium" | "high"
  fail_on = "error",         # "error" | "warning" | "info"
  verbose = FALSE
)
cat(report)
```

`files` is a **named** character vector — names are file paths, values are
file contents (not a list of pairs, since that's the idiomatic R shape).
Every other argument defaults to `NULL` (falls back to `.jss-lint.toml` /
built-in defaults, same as the CLI). `render()` returns the rendered report
as a single string, or raises an R error (catchable with `tryCatch`) on a
malformed `files` argument or an unparseable input file.

---

## Which one should I actually use?

- **Editing a manuscript in VS Code**: the extension — zero-install
  (bundled WASM), live diagnostics and per-violation quick fixes.
- **Command-line / CI**: the `jsslint` binary — the fullest surface:
  `--fix`, `--crossref` online DOI verification, `explain`, `diff`,
  `init`, `report` (md/html/pdf), and an LSP server for other editors.
- **Browser / privacy-sensitive**: `jsslint-wasm` (or the hosted web app) —
  a hard, by-construction guarantee that nothing reaches the network.
- **Scripting inside a larger Python pipeline**: `jsslint` (PyPI) — avoids
  shelling out to the binary; also what this repo's own Rust-vs-Python
  parity tests use.
- **R / JSS-author workflows**: `jsslintr` — `jsslint()`/`jssfix()` on the
  files in your project, native to the ecosystem most JSS authors already
  work in.

All four are driven by the same `jsslint-core` engine, so results are
identical regardless of which one you reach for — that parity is what the
`rust/*/tests/*_parity.rs` / `tests/unit/test_jsslint_parity.py` /
`r/jsslintr/tests/testthat/` suites continuously check.
