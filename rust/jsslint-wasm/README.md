# jsslint-wasm

A browser / Node.js WASM build of the
[JSS style checker](https://github.com/kollerma/jss-style-checker) — a linter
for LaTeX/BibTeX manuscripts submitted to the
[Journal of Statistical Software](https://www.jstatsoft.org/) (JSS).

It runs **entirely client-side**: no network access is linked into this
package at all (not even behind a flag), so manuscripts never leave the
machine — by construction. This is the engine behind the
[in-browser checker](https://kollerma.github.io/jss-style-checker/).

## Install

```sh
npm install jsslint-wasm
```

## Usage

`render(request)` takes one object (camelCase keys) and returns the rendered
report as a string, or throws on a malformed request or unparseable input.

```js
import { render } from "jsslint-wasm";

const report = render({
  files: [["paper.tex", texSource], ["refs.bib", bibSource]],
  output: "json",           // "terminal" | "json" | "sarif" | "html"
  mode: "reviewer",         // "author" | "reviewer"
  ignoreRules: "JSS-SRC-001,JSS-MARKUP-001",
  minConfidence: "medium",  // "low" | "medium" | "high"
  failOn: "error",          // "error" | "warning" | "info"
});
```

`files` is an array of `[path, contents]` pairs; every field except `files`
is optional. There is no `.jss-lint.toml` filesystem lookup on this target
(no real filesystem in WASM) — pass any overrides explicitly.

The package is built with `wasm-pack`; the default export targets bundlers
(webpack/vite/rollup) and needs no manual init step. See
[`rust/README.md`](https://github.com/kollerma/jss-style-checker/blob/main/rust/README.md)
for the Node (`--target nodejs`) variant and build instructions, and the
[project README](https://github.com/kollerma/jss-style-checker) for the full
rule catalogue.

## License

MIT.
