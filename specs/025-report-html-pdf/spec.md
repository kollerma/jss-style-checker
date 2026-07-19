# Spec 025 — Rust `report --format html` / `--format pdf` (retroactive record)

> **RETROACTIVE**: shipped from a handoff prompt without a committed spec.
> Key commits: `d1cc82a8` (feature), `a6897fe5` + `a50604d9` (PDF CMap fix
> and its regression test).

## What shipped

- **HTML**: `jsslint report --format html` is **byte-for-byte identical** to
  the Python CLI's output (`conformance.html.j2` equivalent), verified by
  `rust/jsslint-cli/tests/report_parity.rs`.
- **PDF**: `jsslint report --format pdf --out FILE` renders a self-contained
  PDF via the pure-Rust `genpdf` crate (`rust/jsslint-cli/src/report_pdf.rs`)
  with a vendored DejaVu Sans font, so it works with no host fonts installed.

## The documented parity divergence (PDF)

Python renders PDF through WeasyPrint, a full HTML+CSS layout engine.
Reproducing its output byte-for-byte (or even visually) in pure Rust was
evaluated and **ruled infeasible** — no equivalent engine exists. The Rust
PDF is therefore an independently laid-out document carrying the same
content. This is a deliberate, documented exception to the byte-parity
invariant (Constitution §XIII requires exactly this: divergences documented
in `rust/README.md`, excluded from the parity claim explicitly).

## The vendored-patch decision (printpdf)

`genpdf` 0.2.0 pins `printpdf` =0.3.4, which writes a malformed ToUnicode
CMap for glyphs above U+FFFF — tripped by DejaVu Sans on *every* generated
PDF. No fixed 0.3.x exists; the 0.12 rewrite that fixes it has an
incompatible API. Resolution: vendor a patched `printpdf` 0.3.4 at
`rust/vendor/printpdf-0.3.4` wired via `[patch.crates-io]`; full writeup in
that directory's `NOTICE.md`. Guarded by a build-mode-independent regression
test.

`--format pdf` requires `--out FILE` (binary output, no stdout mode) — same
guard as the Python CLI.
