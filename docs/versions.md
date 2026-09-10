# Versions: what to pin, and what may change

`jss-style-checker` ships one engine through seven channels, and the
channels do not all accept the same version string. This page maps them
to each other, states what a release is allowed to change, and says what
to pin.

Three different versions appear in the output of `jss-lint --version`:

```
jss-lint 1.2.0                                         <- suite version
engine: texlint/python 1.2.0                           <- engine + its version
rule set: 2026-09-06 (jss.cls 3.3, vendored 2021-05-23) <- rule-set date + authority
journal: jss
```

- **Suite version** (`VERSION` in the repository) — one number for every
  channel, propagated by `python scripts/set_version.py`. Never
  hand-edited in a manifest (Constitution §XV).
- **Engine** — `texlint/python` for the Python package, `jsslint-core/rust`
  for every other channel. The two are held byte-identical on
  `terminal`, `json`, `sarif`, and `html` output (§XIII).
- **Rule set** — a *date*, not a semantic version, stamped in
  `specs/003-jss-rule-catalogue/catalogue.yaml` and guarded by a
  fingerprint. It names which rules, severities, messages, and
  suggestions produced a finding. Baseline files record it.

## Channels

| Channel | Artifact | Version string | Constraint |
|---|---|---|---|
| PyPI | `jss-style-checker` (the reference implementation, `jss-lint`) | `X.Y.Z` | PEP 440. Plain three-part versions only; no suffixes are used. |
| PyPI | `jsslint` (the PyO3 wheel of the Rust core) | `X.Y.Z` | as above |
| crates.io | `jsslint-cli`, `jsslint-core`, `jsslint-crossref` | `X.Y.Z` | SemVer. A `-N` suffix would read as a *pre-release* and is never used here. |
| npm | `jsslint-wasm` | `X.Y.Z` | SemVer, stamped from the Cargo version by `wasm-pack`. |
| VS Code Marketplace / Open VSX | `jss-style-checker` | `X.Y.Z` | Strictly increasing; the marketplaces reject pre-release-style suffixes in the stable channel. |
| CRAN | `jsslintr` | `X.Y.Z-N` | CRAN's resubmission suffix, in `DESCRIPTION` only. The one sanctioned exception to single-source versioning (§XV): `1.2.0-1`, `1.2.0-2`, … all wrap engine `1.2.0`. `jsslint_version()` returns both. |
| CTAN | documentation bundle | new identifier per upload | CTAN needs a fresh identifier for every upload: `1.2.0` for a release; a doc-only re-upload of the same release uses the `YYYY-MM-DD` form. |
| GitHub Action | `kollerma/jss-style-checker` | `vX.Y.Z` + rolling `v1` | The rolling major tag moves only for tags without a `-` suffix. The Action installs the Python package from PyPI. |

Release tags are per component: `vX.Y.Z-cli`, `vX.Y.Z-py`,
`vX.Y.Z-pypkg`, `vX.Y.Z-wasm`, `vX.Y.Z-vscode`, and plain `vX.Y.Z` for
the Action. CRAN and CTAN uploads are manual.

## Distribution → engine → rule set

| You installed | You get engine | Ask it |
|---|---|---|
| `pip install jss-style-checker==1.2.0` | `texlint/python 1.2.0` | `jss-lint --version` |
| `cargo install jsslint-cli --version 1.2.0` | `jsslint-core/rust 1.2.0` | `jsslint --version` |
| `pip install jsslint==1.2.0` | `jsslint-core/rust 1.2.0` | `jsslint.version()` |
| `npm i jsslint-wasm@1.2.0` | `jsslint-core/rust 1.2.0` | `version()` |
| `install.packages("jsslintr")` (CRAN `1.2.0-1`) | `jsslint-core/rust 1.2.0` | `jsslint_version()` |
| the VS Code extension `1.2.0` | the bundled WASM of `1.2.0` | extension version in the marketplace |

Every one of them reports the same `rule set` date, because all of them
compile or read the same `catalogue.yaml`.

## What a release may change

The rule-set fingerprint covers every active rule's id, category,
severity, description, guide section, confidence tier, and auto-fixable
flag, **and** the message and suggestion text the engine emits on the
per-rule fixtures. Any change to those forces a new rule-set date
(`tools/generate_catalogue_data.py --stamp-fingerprint` refuses
otherwise). That gives a simple policy:

| Release | May do | Rule-set date |
|---|---|---|
| **Patch** (`1.2.0 → 1.2.1`) | make findings *disappear* only: fix false positives, narrow a rule, fix a crash | unchanged |
| **Minor** (`1.2.0 → 1.3.0`) | add rules, reword messages or suggestions, change a severity or confidence tier, add output keys | bumped |
| **Major** (`1.x → 2.0`) | retire or rename rules, break the JSON shape | bumped |

**A minor release may reword messages and suggestions.** Baseline
entries are keyed on `(rule_id, path, message, suggestion)`, so entries
for reworded rules go stale and their findings reappear as new. The
baseline summary line names both rule-set dates when they differ:

```
Baseline: 212 findings hidden by .jss-lint-baseline.json (3 stale, 0 unevaluated) — written for rule set 2026-09-06, current 2026-11-02; run --update-baseline
```

Re-running `--update-baseline` after a minor upgrade is expected. See
`docs/baseline.md`.

## What to pin

Pin the **tool minor**, and commit a baseline:

```sh
pip install "jss-style-checker~=1.2.0"      # 1.2.*, no 1.3
cargo install jsslint-cli --version "^1.2"
```

```yaml
- uses: kollerma/jss-style-checker@v1
  with:
    version: 1.2.0
    baseline: .jss-lint-baseline.json
```

```r
# renv.lock pins jsslintr's CRAN version, e.g. 1.2.0-1
```

Pinning the minor keeps the rule set fixed for the life of your pin: a
patch release can only remove findings, so CI cannot start failing on
something new. Upgrading a minor is the moment to re-run
`--update-baseline`.
