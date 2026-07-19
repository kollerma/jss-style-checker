# Spec 018 — Rust core & multi-engine distribution (retroactive record)

> **RETROACTIVE**: this feature shipped without a committed spec (it was
> developed on the `018-rust-core` branch, which the code cites as
> "spec 018"). This document records what shipped and why, after the fact.
> It is a record, not a plan; the implementation is the authority.

## What shipped

A Rust reimplementation of the Python `texlint` engine (`rust/jsslint-core`),
compiled into four distributions plus two applications:

| Artifact | Registry | Source |
|---|---|---|
| `jsslint` CLI (with `explain`/`diff`/`init`/`report`/`lsp`) | crates.io (`jsslint-cli`, `jsslint-core`) | `rust/jsslint-cli/` |
| Browser/Node WASM (`render`/`fix`/`analyze`) | npm (`jsslint-wasm`) | `rust/jsslint-wasm/` |
| Python extension (`jsslint.render`) | PyPI (`jsslint`) | `rust/jsslint-py/` |
| R package (`jsslintr::render`, `jsslint()`, `jssfix()`) | CRAN (pending) | `r/jsslintr/` |
| In-browser checker app | GitHub Pages | `web/` |
| VS Code extension (in-process WASM, zero-install) | VS Code Marketplace / Open VSX | `vscode-extension/` |

`rust/README.md` is the tool-by-tool guide and the canonical list of
deliberate per-ecosystem divergences.

## Load-bearing design decisions

- **Parity, not fork** (now Constitution §XIII): the Python package remains
  the reference implementation; every Rust behavior is verified
  byte-for-byte against it by the `*_parity` suites. All 60 rules ported.
- **Portable-core isolation** (now Constitution §XIV): `jsslint-core` does no
  network or filesystem I/O; the R package vendors the core
  (`r/jsslintr/tools/vendor-jsslint-core.sh`) because `R CMD build` cannot
  reach outside the package tree; the crate vendors its rule-catalogue data
  (`rust/jsslint-core/specs/003-jss-rule-catalogue/`, drift-guarded by
  `tests/unit/test_vendored_catalogue_in_sync.py`) so the crates.io tarball
  is self-contained.
- **VS Code runs the WASM in-process** — no Python, no native binary, one
  universal VSIX. The `analyze()` export exists because `render(json)`
  hardcodes `fix: null` for Python byte-parity; per-diagnostic quick fixes
  need the real fix payloads.
- **Single-source version** (now Constitution §XV): `VERSION` +
  `scripts/set_version.py`, born from the 1.0.1 release breakage.

## Known deviations / follow-ups

- The Rust engine registers only the built-in `jss` journal — no counterpart
  to the Python `importlib.metadata` plugin mechanism (Constitution §IV
  scope note; tracked in `roadmap/follow-ups.md`).
- `report --format pdf` in the Rust CLI is an independently laid-out
  document, not byte-identical to Python's WeasyPrint output (see spec 025).
