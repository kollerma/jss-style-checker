# Cutting a release

Every release ships the same engine under seven names, and a mismatch
between any two of them is a bug an author sees before we do. The order
below exists because later steps consume earlier ones: the recall number
goes into the catalogue data, the catalogue data goes into the version
block, the version block goes into every package.

Run everything from a clean checkout of the release branch with the venv
and cargo on `PATH`:

```sh
export PATH="$PWD/.venv/bin:$HOME/.cargo/bin:$PATH"
```

## 1. Refresh the measured numbers

Recall is a *measurement*, not a constant, so it is re-measured against
the corpus at each release rather than carried forward.

```sh
eval-jss corpus fetch && python -m eval.recall_corpus_scaffold
eval-jss recall                       # recorded run — no --no-record
python -m tools.generate_recall_snapshot --run-timestamp <NEW RUN>
```

`--run-timestamp` is **required** to adopt the run you just made: with
no flag the generator re-pins the timestamp already in the committed
snapshot, so `--check` stays stable and a stray regeneration cannot
silently jump runs. Take the value from `recall_history`:

```sh
sqlite3 eval/precision-history.db \
  'select max(run_timestamp) from recall_history'
```

The badge reads that same snapshot, so it cannot disagree with the
footer the tool prints (FR-A-006). Precision is pinned separately: record
the run's iteration label (`eval iterate record v1.2.0-release`) and bump
`PINNED_ITERATION_LABEL` in `eval/badge.py`. `publish-badges.yml`
regenerates `precision.json` / `recall.json` / `f1.json` from those pins
on the next push to `main`.

Then **ratchet the floor**: set `RECALL_FLOOR` in `eval/cli.py` to
`floor(aggregate − 0.03, 2 dp)` from the fresh snapshot. The 0.03 band
is the corpus's own sampling noise; a floor closer than that fails on
re-runs that changed nothing.
`tests/unit/eval/test_recall_snapshot_fresh.py` enforces both sides —
the floor may not exceed the shipped number, and may not sit more than
0.03 below it.

## 2. Re-stamp the generated data

```sh
python tools/generate_message_snapshot.py            # rewrite
python tools/generate_catalogue_data.py --stamp-fingerprint \
    --ruleset-version YYYY-MM-DD
```

The fingerprint covers the catalogue contract fields *and* every message
and suggestion string, so any user-visible wording change forces a new
`ruleset_version` date. Stamping refuses to move the date backwards.
Then verify both are reproducible from source:

```sh
python tools/generate_message_snapshot.py --check
python tools/generate_catalogue_data.py --check
```

If item-S-style suggestion wording changed, regenerate the SARIF goldens
**once**, in the same commit, and eyeball the diff — a golden refreshed
by reflex is a golden that no longer tests anything.

## 3. Set the version

```sh
echo 1.2.0 > VERSION
python scripts/set_version.py
```

Never hand-edit a manifest (Constitution §XV;
`tests/unit/test_version_single_source.py` guards it). The script
updates both `Cargo.lock` files before re-vendoring the R crate, because
`vendor-crate-archive.sh` runs `cargo --locked` and a lock still naming
the previous version aborts it. Note the two side effects: `r/jsslintr/DESCRIPTION` is set to a bare `1.2.0`, which
is what the first CRAN submission carries, and `CITATION.cff`'s date is
set to today.

## 4. Gates

All of these, green, before any tag:

```sh
python -m pytest tests/ -q
ruff check .
python -m pytest tests/unit/journals/jss/rules \
    --cov=src/texlint/journals/jss/rules --cov-branch \
    --cov-report=term-missing -q                                # §IX
(cd rust && cargo fmt --all --check)
(cd rust && cargo clippy --workspace --all-targets --locked -- -D warnings)
(cd rust && cargo test --workspace --locked)
node --test web/zip.test.mjs
R CMD INSTALL --library=$HOME/R/library r/jsslintr
Rscript -e 'testthat::test_local("r/jsslintr")'
eval-jss recall --gate --no-record
```

§IX mandates 100% branch coverage on the rule modules. The full suite
reaches **93%** as of 1.2.0 — a gap that pre-dates this release and is
recorded in [`roadmap/follow-ups.md`](../roadmap/follow-ups.md). What the
release actually gates on is that no module *regresses*: compare against
the previous tag before shipping, and do not let a new rule land below
100%.

The parity suites (§XIII) **skip silently** when the gitignored eval
corpus is not materialized. A skip is not a pass — materialize the
corpus (step 1) before treating a green run as evidence.

If anything in `rust/jsslint-core/` changed:

```sh
bash r/jsslintr/tools/vendor-jsslint-core.sh   # and commit the result
```

## 5. CHANGELOG

One entry per user-visible change, and *separate* `Fixed` entries for
bug fixes that happen to ride along with a feature — an author scanning
for "was my bug fixed?" should not have to read a feature paragraph to
find out.

## 6. Tags

Each component publishes from its own tag. Push tags to the **public**
remote only.

| Component | Tag | Workflow |
|---|---|---|
| CLI (crates.io) | `v1.2.0-cli` | `release-crates.yml` |
| PyO3 wheel (PyPI) | `v1.2.0-py` | `release-pypi.yml` |
| Python package (PyPI) | `v1.2.0-pypkg` | `release-pypkg.yml` |
| WASM (npm) | `v1.2.0-wasm` | `release-npm-wasm.yml` |
| VS Code / Open VSX | `v1.2.0-vscode` | `vscode-publish.yml` |
| GitHub Action | `v1.2.0` | `release-action.yml` |

Every `release-*.yml` must carry a tag guard as its first step, so a
mistyped tag fails loudly instead of publishing the wrong version:

```yaml
      - name: Tag matches VERSION
        run: |
          tag="${GITHUB_REF_NAME#v}"
          tag="${tag%-cli}"; tag="${tag%-py}"; tag="${tag%-pypkg}"
          tag="${tag%-wasm}"; tag="${tag%-vscode}"
          [ "$(cat VERSION)" = "$tag" ] || {
            echo "tag $GITHUB_REF_NAME does not match VERSION $(cat VERSION)"; exit 1; }
```

PyPI and npm publish via OIDC trusted publishing (no stored token);
crates.io and the marketplaces use `RELEASE_TAG_PAT`. Confirm it is
present and unexpired before tagging.

## 7. Manual channels

- **CRAN**: `r/jsslintr` as **`1.2.0`** — submit the bare version. The
  `-N` suffix is only for *resubmissions*: if the first submission is
  rejected, fix the cause and go to `1.2.0-1`, then `-2`, and so on.
  A first submission never carries a suffix.
- **CTAN**: the manual bundle, version `1.2.0`, with the README that
  ships in it re-read rather than assumed.

## 8. After the tags

`web/pkg/` is a build artifact, not a checked-in one: `publish-web.yml`
builds it and force-adds it to `gh-pages` past wasm-pack's own
`.gitignore`. Nothing to do here except confirm the deployed page loads
and reports a version matching the tag.
