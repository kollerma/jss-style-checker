# Spec 026 — `\input`/`\include` auto-resolution, both engines (retroactive record)

> **RETROACTIVE**: shipped from a handoff prompt without a committed spec.
> Key commits: `96d13078` (feature, both engines), `aaa6b37c`
> (comment-stripping / nested-brace / root-relative fixes). Builds on the
> dormant spec-013 resolver.

## What shipped

Linting a root `.tex` now follows `\input{…}`, `\include{…}`, `\subfile{…}`,
and `\bibliography{…}` recursively (cycle-safe, `TEXINPUTS`/`BIBINPUTS`
aware, `.tex` extension inference) and lints the reachable project as one
unit — in **both** engines, with byte-identical output. `--no-resolve`
(previously a documented no-op) now genuinely restricts linting to the
explicitly passed files, identically on both CLIs.

## Design

- **Python**: the spec-013 `core/resolver.py` already existed but was never
  wired into the lint pass; this feature activated it.
- **Rust**: a faithful port of `resolver.py`, wired identically.
- **Layering** (Constitution §XIV): resolution reads the filesystem, so it
  lives at the fs-having caller layer (CLI/bindings), which resolves the
  root into a concrete `(path, contents)` set and feeds the existing
  in-memory engine. The WASM/web surface is unchanged — it lints exactly the
  in-memory files it is given, no resolution.
- Diagnostics in included files are attributed to **that file's** path and
  source-authoritative line/column, not the root's.

## Verification

- Multi-file fixtures with violations distributed across included files;
  byte-parity asserted across all output formats and both engines, plus
  `--no-resolve` collapsing to root-only. Resolver unit tests mirror the
  Python suite (cycles, search paths, missing targets, nested braces,
  `%`-commented macros).
