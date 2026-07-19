# Spec 024 — `--crossref` online DOI verification in Rust (retroactive record)

> **RETROACTIVE**: shipped from a handoff prompt without a committed spec.
> Key commits: `e6c2caa8` (feature), `17d73c07` (resolver-path test).

## What shipped

`jsslint --crossref [--crossref-mailto …] refs.bib` ports the Python
`texlint/crossref.py`: doi-less `@article`/`@book`/`@inproceedings`/
`@incollection` entries are matched on Crossref (title + first-author
surname + year), CRAN `@Manual` entries get their registered
`10.32614/CRAN.package.NAME` DOI (confirmed via `doi.org`), and
`JSS-REFS-003` upgrades from an offline advisory to an online-verified
finding — reporting the exact DOI (with a `--fix` payload that writes it
into the `.bib`) and suppressing the advisory when no DOI exists.

## The architectural decision (why a separate crate)

Network code lives in **`rust/jsslint-crossref/`**, a crate consumed only by
`jsslint-cli` — never by `jsslint-core` or the portable bindings. A Cargo
feature flag was explicitly rejected: the WASM privacy guarantee
("manuscripts never leave the machine") must be **structural** — an absent
dependency edge — not a flag someone can flip. `jsslint-core` stays fully
offline and only defines the injection seam (`config::DoiResolver`) that
`JSS-REFS-003` consumes; with no resolver injected, offline behavior is
byte-identical to before. This is now Constitution §XIV, enforced by
`rust/jsslint-wasm/tests/isolation.rs` (dep-graph guard).

HTTP client: `ureq` (blocking, pure-Rust/rustls). Tests use an injected
resolver seam mirroring Python's `opener` injection — the default suite is
hermetic; a live smoke test exists at
`rust/jsslint-crossref/tests/live_smoke.rs`.

## CRAN constraint (for the future R exposure)

Not yet exposed in `jsslintr`. When it is: network use must be opt-in
(default off), fail gracefully offline, and never run during `R CMD check`
(CRAN policy). Recorded here so the constraint isn't rediscovered.
