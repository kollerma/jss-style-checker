# Vendored fork of `printpdf` 0.3.4

Vendored from https://crates.io/crates/printpdf/0.3.4 (upstream source at
https://github.com/fschutt/printpdf, MIT-licensed — see `LICENSE`) via a
`[patch.crates-io]` override in `rust/Cargo.toml`, so `genpdf` 0.2.0 (which
depends on `printpdf = "0.3.4"`, i.e. exactly this version — see its own
`Cargo.toml`) transparently resolves to this copy instead of the crates.io
release.

## Why

`generate_cid_to_unicode_map` in
`src/types/plugins/graphics/two_dimensional/font.rs` wrote every embedded
font's ToUnicode CMap entry as `<{:04x}> <{:04x}>` — a plain 4-hex-digit
codepoint. That's correct for the BMP (U+0000–U+FFFF) but wrong for
anything above it: PDF's `bfchar` destination string must be a UTF-16BE
byte sequence, and a codepoint like U+1F643 needs a two-unit surrogate
pair (`<D83EDD8E>`-style), not a raw 5-hex-digit value. The bug fires for
every embedded font that contains *any* supplementary-plane glyph in its
cmap table — e.g. the vendored DejaVu Sans faces this repo embeds for
`report --format pdf` (`rust/jsslint-cli/assets/fonts/`) include musical
symbols, ancient scripts and a few emoticon-block glyphs, unrelated to
whatever text a given report actually contains. So every PDF this tool
generates carried a malformed ToUnicode stream regardless of content:
harmless for on-screen rendering (glyph selection goes through
`CIDToGIDMap`, not ToUnicode) but breaks text search, copy-paste, and
accessibility tooling, and would plausibly fail a strict PDF/A or
accessibility validator — relevant given this tool's job is producing
journal-submission-ready output.

## What we checked before vendoring

- `genpdf` 0.2.0 is the only release on crates.io; its `printpdf`
  dependency is pinned to exactly `"0.3.4"` (Cargo's default `^0.3.4`,
  i.e. `>=0.3.4, <0.4.0`), and 0.3.4 is itself the newest 0.3.x release —
  no compatible patch release exists to bump to.
- The bug is still present, unfixed, in printpdf 0.4.0 through 0.11.3
  (checked the same function in 0.4.1's source) — bumping past genpdf's
  declared range wouldn't have helped even if genpdf's manifest allowed
  it.
- printpdf 0.12.0 *does* fix this (`src/cmap.rs` encodes the target via
  `char::encode_utf16`, producing a real surrogate pair) — but 0.12.0 is
  a from-scratch rewrite with a completely different public API (new
  module layout, no more `IndirectFontRef`/`BuiltinFont`-style low-level
  API), and `genpdf` 0.2.0's font-loading code depends on the old 0.3.x
  API surface. It isn't a drop-in upgrade — adopting it would mean
  patching or forking `genpdf` itself, a substantially larger change than
  the one-line fix below.

So: vendor 0.3.4 and reapply printpdf's own eventual fix to the one
function, rather than chase an upstream bump that doesn't exist yet at a
compatible version.

## What changed

Only `generate_cid_to_unicode_map` in
`src/types/plugins/graphics/two_dimensional/font.rs`. The destination
half of each `bfchar` entry is now built via `char::encode_utf16` (one
`{:04x}` unit for BMP codepoints — byte-identical to the old output in
the common case — and a proper two-unit surrogate pair above U+FFFF)
instead of a single unconditional `{:04x}`. See the doc comment on that
function for the inline version of this explanation.

Everything else in this directory (aside from `Cargo.toml`, which was
rewritten by hand from the registry's normalized version purely for
readability — same dependencies/features, no behavior change) is
unmodified upstream source. `assets/`, `examples/`, `Cargo.lock`, and CI
config files were dropped since they aren't needed to build the crate as
a workspace path dependency.
