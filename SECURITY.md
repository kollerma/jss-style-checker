# Security Policy

## Reporting a vulnerability

Please report vulnerabilities privately — do not open a public issue.

- Preferred: [GitHub private vulnerability reporting](https://github.com/kollerma/jss-style-checker/security/advisories/new)
- Or email: kollerma@proton.me

You can expect an acknowledgment within a week. Please include reproduction
steps and the affected distribution (PyPI `jss-style-checker`/`jsslint`,
crates.io `jsslint-cli`/`jsslint-core`, npm `jsslint-wasm`, the VS Code
extension, the R package, or the hosted web app).

## Supported versions

Only the latest released version of each distribution is supported.

## Scope notes

Two properties of this project are security guarantees, and reports that
break them are especially welcome:

- **The WASM surfaces (npm package, web app, VS Code extension) must never
  perform network I/O.** "Manuscripts never leave the machine" is enforced
  structurally — no network-capable crate may appear in their dependency
  graphs (`rust/jsslint-wasm/tests/isolation.rs` guards this in CI). Any
  observed network egress from these surfaces is a vulnerability.
- **The CLI is fully offline by default.** The only network code is the
  opt-in `--crossref` DOI lookup (Crossref / doi.org), which sends only
  bibliographic metadata (title, first-author surname, year, package name)
  — never manuscript content.
