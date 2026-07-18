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

**None of these are published yet.** The publish workflows
(`.github/workflows/release-{crates,npm-wasm,pypi}.yml`) exist and are
tag-triggered, but no tag has been pushed and each needs a one-time registry
setup step first (see the header comment in each workflow file). Until then,
"install" below means "build from source in this checkout" — the commands
under "Once published" are what the same workflow produces for the future.

All four tools accept the same logical inputs (file paths + contents,
`journal`/`mode`/`output`/`ignore_rules`/`min_confidence`/`fail_on`) and
render the same four report formats: `terminal`, `json`, `sarif`, `html`.
Exit-code / return-value conventions differ per ecosystem (see each section).

---

## 1. `jsslint` — the CLI binary

Source: `rust/jsslint-cli/`. Wraps the same engine as the Python `jss-lint`
CLI, plus `explain`/`diff`/`init`/`report`/`lsp` subcommands.

### Build

```sh
cd rust
cargo build --release -p jsslint-cli
# binary at rust/target/release/jsslint
```

Or install it onto your `PATH`:

```sh
cargo install --path rust/jsslint-cli
```

**Once published:** `cargo install jsslint-cli` (crates.io).

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
`info`) · `2` the tool could not complete (bad args, unreadable file, unknown
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

`report --format html`/`pdf` are accepted by the flag parser but not yet
implemented (errors with exit code 2) — markdown is the only working format
today.

`jsslint lsp` starts a synchronous LSP 3.17 server over stdio (diagnostics +
code actions + workspace edits). You don't run this by hand; point an
editor's LSP client at the `jsslint lsp` command the way the VS Code
extension (`vscode-extension/`) points at the Python `jss-lint lsp` today.

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

### Build

```sh
cd rust/jsslint-wasm
rustup target add wasm32-unknown-unknown  # once
wasm-pack build --release --target bundler   # for webpack/vite/rollup consumers
# or: wasm-pack build --release --target nodejs   # for plain `require()` in Node
# output: rust/jsslint-wasm/pkg/
```

**Once published:** `npm install jsslint-wasm`.

### Use it

The exported `render(request)` function takes one object (camelCase keys)
and returns the rendered report as a string, or throws on a malformed
request or unparseable input. The call itself is identical regardless of
build target — only how you import the module differs:

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

### Build

```sh
cd rust/jsslint-py
pip install maturin   # already in the root project's [dev] extras
maturin develop --release   # builds + installs into your active venv
```

**Once published:** `pip install jsslint` (PyPI). One wheel per platform
covers CPython 3.10+ via the stable ABI (`abi3-py310`) — no per-Python-version
wheel needed.

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

```r
library(jsslintr)

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

- **Command-line / CI**: the `jsslint` binary — it's the only one with
  `--fix`, `explain`, `report`, and the LSP server.
- **Browser / privacy-sensitive**: `jsslint-wasm` — the only build with a
  hard, by-construction guarantee that nothing reaches the network.
- **Scripting inside a larger Python pipeline**: `jsslint` (PyPI) — avoids
  shelling out to the binary; also what this repo's own Rust-vs-Python
  parity tests use.
- **R / JSS-author workflows**: `jsslintr` — native to the ecosystem most
  JSS authors already work in.

All four are driven by the same `jsslint-core` engine, so results are
identical regardless of which one you reach for — that parity is what the
`rust/*/tests/*_parity.rs` / `tests/unit/test_jsslint_parity.py` /
`r/jsslintr/tests/testthat/` suites continuously check.
