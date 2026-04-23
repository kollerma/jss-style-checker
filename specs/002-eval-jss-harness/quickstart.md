# Quickstart — `eval-jss` Harness

For first-time contributors running or extending the evaluation harness. Gets you from a fresh clone to a per-rule precision number on the MVP corpus, then points to where Phase B extensions live.

## Prerequisites

- A working Step 1 build — `jss-lint --version` must succeed (`pip install -e '.[dev]'` from the repo root is the standard setup).
- Python 3.10, 3.11, or 3.12.
- (Phase B only) `llama.cpp`'s `llama-server` running locally with the pinned model; see §"Starting the AI backend" below.

## Install

No separate install. `eval-jss` ships in the same repository as `jss-lint`, registered as a second console script:

```toml
[project.scripts]
jss-lint = "texlint.cli:main"
eval-jss = "eval.cli:main"
```

After the standard `pip install -e '.[dev]'`, both binaries are on PATH.

```bash
which jss-lint eval-jss
# /path/to/.venv/bin/jss-lint
# /path/to/.venv/bin/eval-jss
```

If `eval-jss` is missing, re-install: the script was added to `pyproject.toml` in this spec's commit.

## Phase A — your first precision number

Five commands, in order.

### 1. Initialise the database

```bash
eval-jss init
```

Creates `eval/eval.db` (gitignored). Idempotent — running it a second time is a silent no-op. If you want a scratch DB for experimentation, pass `--db /tmp/scratch.db` to every subsequent command.

### 2. Scan the MVP corpus

```bash
eval-jss scan
# Scanning examples/...
# [ 1/10] cran_lme4_1.1-35.1           14 violations
# [ 2/10] cran_MASS_7.3-60              3 violations (1 JSS-PARSE-000)
# ...
# Scanned 10 papers, 87 violations, 1 parse failure. exit 1
```

- Exit 0 is only produced when every paper is clean; exit 1 is the expected path during Step 3 when rules are firing.
- Progress output goes to stderr; stdout is empty. Use `eval-jss scan 2>/dev/null` to silence.
- The scan shells out to `jss-lint --output json`. If `jss-lint` is not on PATH you'll get exit 2 with a clear error — that's an environment issue, not a clean corpus.
- Re-running `scan` on the same corpus under the same linter version inserts zero new rows. Spec SC-002 — you can verify:

  ```bash
  sqlite3 eval/eval.db 'select count(*) from violations'
  eval-jss scan
  sqlite3 eval/eval.db 'select count(*) from violations'   # same number
  ```

### 3. Label violations

```bash
eval-jss human-review
```

For each unlabelled or `uncertain` violation, the TUI shows the rule, message, and ±3 lines of source context, then prompts `[t/f/u/s/q]`. Every verdict commits before the next violation loads — `Ctrl-C` loses at most the current row.

Useful flags:

- `--rule JSS-CITE-001` — label one rule at a time (matches how Step 3 refines rules).
- `--limit 20` — do 20 rows and stop. Pair with `watch -n 600 eval-jss report` to get a running precision number while you label.

### 4. Report precision

```bash
eval-jss report
```

A rich table grouped by category, with columns `Rule`, `TP`, `FP`, `Pending`, `Precision`, `Status`. Status is `PASS` (green) when precision ≥ 0.90, `FAIL` (red) when below, `NOT MEASURED` (dim) when no labels exist yet, `NOT EXERCISED` (dim) when no violations fired.

A dedicated panel below the main table lists any `JSS-PARSE-000` rows — these are corpus-level parse regressions, not style violations, and they do not enter the precision math (spec FR-021).

Exit 0 if every rule passes. Exit 1 if any rule is below threshold — wire this into Step 3's per-rule gating.

### 5. Iterate

When a rule shows `FAIL`, look at its `false_positive` examples (e.g. with `sqlite3 eval/eval.db 'select * from violations where rule_id=? and verdict="false_positive"'`) and decide whether to narrow the rule, relax it, or retire it. That is the entire point of the harness.

## Phase B extensions

Phase B is a set of additive commands. Phase A keeps working unchanged.

### AI-assisted labelling (`eval-jss review`)

**Starting the AI backend.** Run `llama-server` yourself, with exactly the sampler settings the spec pins:

```bash
./bin/llama-server \
  -hf unsloth/Qwen3-30B-A3B-GGUF:UD-Q4_K_XL \
  --cache-type-k q4_0 --cache-type-v q4_0 \
  -b 2048 -ub 1024 -ngl 99 -fa on -t 8 \
  --fit on --cont-batching \
  --slot-save-path /tmp/slow-save -np 1 --jinja \
  --host 0.0.0.0 --port 8080 \
  --temp 0.1 --top-p 1.0 --min-p 0.0 --top-k 1
```

`--top-k 1` is the reproducibility contract — greedy decoding means same prompt → same label.

**Run the review**:

```bash
eval-jss review --confidence-threshold 0.8
```

- High-confidence labels are written with `reviewer = "ai:qwen3-30b-a3b"`.
- Low-confidence rows are left `uncertain` and surface in the next `human-review` pass.
- Rules listed in `eval/review-skip-list.toml` skip the AI entirely.

**No server running?** `eval-jss review` exits 2 on the first connection failure — fail fast. Your existing human-review labels are untouched.

### Reproducing the corpus (`eval-jss corpus fetch`)

The MVP corpus (`examples/`) is hand-curated and checked into git, so in Phase A the corpus identity is the repository's git commit hash. Phase B adds a manifest:

```bash
cat eval/corpus-manifest.csv | head
# jss_doi,source,source_id,version,vignette_file,local_path,sha256
# 10.18637/jss.v067.i01,cran,lme4,1.1-35.1,vignettes/lmer.tex,cran_lme4_1.1-35.1/,7d8c...

eval-jss corpus fetch
# Fetching 20 papers from pinned distribution URLs...
# [ 1/20] cran lme4 1.1-35.1    OK (hash 7d8c... verified)
# ...
```

- All fetches are from immutable URLs (CRAN `Archive/`, Bioc release tags, arXiv `vN`, SWHIDs). **Never** from mutable discovery sources like GitHub HEAD.
- Every tarball's SHA256 is verified before extraction.
- Unreachable rows are logged to `eval/corpus-manifest-gaps.csv`; inspect with `eval-jss corpus status`.

### Precision history (`eval/report.csv`)

In Phase B, `eval-jss report` appends a row per (rule, source) per invocation. Diff the file to see trends:

```bash
git log -p eval/report.csv -- | head -60
```

## Reproducing a precision claim

### Phase A

```bash
git checkout <commit-of-claim>
eval-jss init && eval-jss scan && eval-jss human-review && eval-jss report
```

The corpus identity is `<commit-of-claim>` — everything under `examples/` at that commit. This satisfies Constitution §XII as long as `examples/` is in git (it is, at 10 papers).

### Phase B

```bash
git checkout <commit-of-claim>
eval-jss corpus fetch        # materialises the exact tarballs pinned at that commit
eval-jss init && eval-jss scan && eval-jss human-review && eval-jss report
```

The corpus identity is `eval/corpus-manifest.csv` at `<commit-of-claim>`. `corpus fetch` verifies every hash; a tampered or drifted upstream is caught before `scan`.

## Running the tests

```bash
pytest tests/eval/                      # all harness tests
pytest tests/eval/test_integration.py   # the end-to-end pipeline on a 3-paper fake corpus
pytest tests/eval/ -m "not network"     # skip the one LlamaServerClient live test (default in CI)
```

No test requires `jss-lint` to actually be installed — `_invoke_linter` is mocked at the seam. No test talks to the network — `ReviewClient` is always a `FakeClient` except in the explicitly-marked network test.

## Adding a paper to the corpus (Phase A)

1. Pick a CRAN vignette that uses `\documentclass{jss}` or `\usepackage{jss}`.
2. Copy its `.tex` and `.bib` into a new subdirectory of `examples/` named `cran_<pkg>_<version>/`.
3. Write a short `examples/cran_<pkg>_<version>/README.md` with the CRAN URL, version, and DOI (if any) — this is the provenance record until Phase B lands the manifest.
4. Run `eval-jss scan && eval-jss human-review` on the new paper: `--rule '*'` is the default, or use `--limit N` to just label the new paper's violations.

## Adding a paper to the manifest (Phase B)

1. Add one row to `eval/corpus-manifest.csv` with `sha256=""` (placeholder).
2. Run `eval-jss corpus fetch` — it will log a hash-empty row as a gap.
3. `sha256sum examples/<local_path>/<tarball>` (or equivalent) and paste the result into the `sha256` column.
4. Re-run `eval-jss corpus fetch` — it should now pass cleanly.

## Where things live

- **Source**: `eval/` (top-level, peer to `src/texlint/`). Not in the wheel.
- **Tests**: `tests/eval/`. Never imports from `src/texlint/`.
- **Fixtures**: `tests/eval/conftest.py` (`tmp_db`, `fake_corpus`, `fake_client`).
- **Phase A corpus**: `examples/` (10 papers at Phase A commit).
- **Phase B manifest**: `eval/corpus-manifest.csv`.
- **Phase B skip-list**: `eval/review-skip-list.toml`.
- **Phase B history**: `eval/report.csv`.
- **Runtime DB**: `eval/eval.db` (gitignored).

## Troubleshooting

- **`jss-lint: command not found`** — you installed the package into one venv but are running `eval-jss` from another shell. `which jss-lint` should resolve from the same venv.
- **`eval-jss scan` exits 2 with "corpus directory not readable"** — you passed `--corpus` pointing at a file. It must be a directory.
- **Every rule shows `NOT MEASURED`** — you haven't labelled anything yet. Run `eval-jss human-review`.
- **`eval-jss review` exits 2 immediately** — `llama-server` isn't running on `http://localhost:8080`. Start it (see above) or pass `--base-url`.
- **`eval-jss corpus fetch` reports hash mismatch** — upstream has changed. This is exactly what §XII is designed to catch. Do **not** update the manifest hash without a conscious decision; investigate what changed upstream first.
