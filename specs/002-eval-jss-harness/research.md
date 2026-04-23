# Phase 0 Research — `eval-jss` Harness

The `/speckit.plan` input fixed most library and transport choices; the spec's 2026-04-23 Clarifications fixed the AI backend. This document records the decisions, rationales, and alternatives considered and rejected. It also resolves the remaining open items that the plan's Technical Context flagged.

## SQLite access

### Connection, PRAGMAs, autocommit

- **Decision**: One connection per `eval-jss` invocation, opened with `sqlite3.connect(path, isolation_level=None)`. Immediately after connect, apply:
  ```python
  cx.execute("PRAGMA journal_mode=WAL")
  cx.execute("PRAGMA foreign_keys=ON")
  cx.execute("PRAGMA synchronous=NORMAL")
  ```
  `isolation_level=None` puts the connection in **autocommit** mode; explicit transactions use `cx.execute("BEGIN")` / `cx.execute("COMMIT")`. This is the most predictable mode with WAL — Python's implicit-transaction behaviour has tripped up prior projects by holding locks across statements.
- **Rationale**: WAL gives us readers-don't-block-writer semantics, which matters for the `human-review` loop: the reviewer's DB connection can commit verdicts mid-session while a background `report` invocation in another terminal still sees a consistent snapshot. `foreign_keys=ON` is off-by-default in every SQLite build; we need it for the `violations.paper_id REFERENCES papers(id) ON DELETE CASCADE` contract. `synchronous=NORMAL` is the sweet spot for a development-machine workload: durable within a process crash, willing to lose the last transaction in a full power loss (which is fine — re-run `scan`).
- **Alternatives considered**:
  - *Default rollback journal*: loses WAL's concurrency and writes twice as much.
  - *`synchronous=FULL`*: safer but ~2× slower; unjustified for a dev tool.
  - *`synchronous=OFF`*: risks corruption on crash; unacceptable for an audit log.
  - *Long-lived connection across commands*: would require a daemon. Overkill.

### Schema DDL

- **Decision**: DDL lives in `eval/schema.sql` and is loaded by `db.init()` via `cx.executescript()`. `CREATE TABLE IF NOT EXISTS` + `CREATE INDEX IF NOT EXISTS` throughout so `init` is idempotent (spec FR-005). The exact statements are specified in `contracts/schema.md` and the textual SQL is the authoritative source.
- **Rationale**: Keeping DDL out of Python source means the schema is readable by any `sqlite3` CLI user without reading the package. `executescript()` handles the multi-statement case; each statement is individually idempotent.
- **Alternatives considered**:
  - *Python f-strings / `"""..."""` multi-line constants*: scatters DDL across Python files; SQL syntax highlighting breaks in code review.
  - *A migrations library (alembic etc.)*: adds a dependency for a schema with three tables and no foreseen migrations.

### Dedup via `UNIQUE` + `INSERT OR IGNORE`

- **Decision**: `violations` carries `UNIQUE(paper_id, rule_id, line, message)`. `scan` uses `INSERT OR IGNORE INTO violations (...) VALUES (...)` via `executemany`. Re-running `scan` on an unchanged corpus under the same `tool_version` inserts zero new rows and preserves existing `verdict` / `verdict_reason` / `reviewer` values. Spec FR-010 / SC-002 contract.
- **Why `message` is in the key**: the same rule firing on the same line with a different message means the rule has produced a *different* finding (e.g., two distinct citations on one line, each with its own message). Excluding `message` would cause one of them to be silently dedup'd. Including it is the honest choice.
- **Trade-off acknowledged**: if the linter's message template changes (e.g., a typo fix in the message string), the rule's previously labelled violations become "new" rows on the next scan and lose their verdict. This is accepted — message-template changes are rare, and when they happen a relabel round is the correct response.
- **Alternatives considered**:
  - *Content hash of `(rule_id, line, message, snippet)`*: more robust to snippet changes but needs the linter to emit the snippet, which it doesn't.
  - *Soft dedup (re-insert + manual dedupe in queries)*: burns space for no benefit; queries become uglier.

## Invoking `jss-lint`

### Subprocess shape

- **Decision**: `subprocess.run([jss_lint, "--output", "json", "--", str(p) for p in files], capture_output=True, text=True, check=False, timeout=120)`. One invocation per paper. `check=False` is mandatory: exit 1 means "violations found" and is the **expected** path (spec 001 FR-016). Only exit 2 is a hard failure.
- **Resolving `jss_lint`**: `shutil.which("jss-lint")` once at the top of `scan()`. If `None`, exit 2 with a message naming `jss-lint` so the operator doesn't mistake env misconfiguration for a clean corpus (spec Edge Cases).
- **Per-paper argv**: each paper is a subdirectory of the corpus; the arguments are that directory's `.tex` file (only one, the vignette) and its `.bib` file (if present). The 2026-04-23 `docs/jss-template/` drop confirms that a canonical JSS vignette is one `.tex` + one `.bib`; multi-file vignettes are out of scope for this spec's MVP corpus.
- **Timeout**: 120 seconds per paper. Generous enough for a slow LaTeX parse on a large vignette; short enough that a hung linter does not hang the scan. On timeout, record a `JSS-PARSE-000` violation with message `"jss-lint exceeded 120s timeout"` and move on.
- **Alternatives considered**:
  - *Running `jss-lint` once with all papers*: would lose per-paper accounting in `runs`, and exit-1-on-any-violation means a single paper's violations would stop the loop. Rejected.
  - *Importing `texlint.core.engine` directly in-process*: would couple the harness to the linter's Python API and bypass the CLI (which is what users actually run). Explicitly rejected by spec Assumption "Linter integration is loose".
  - *Async subprocess / `asyncio`*: no measurable win at 10–20 papers; adds complexity.

### JSON parsing and violation mapping

- **Decision**: `result = json.loads(stdout)`; extract `tool_version` for the `runs` row; iterate `result["violations"]` and build a list of `(paper_id, rule_id, line, column, message, severity, first_seen_run_id)` tuples; `executemany("INSERT OR IGNORE INTO violations (...) VALUES (...)", tuples)`.
- **Parse-failure handling**: if `json.loads` raises (the linter emitted non-JSON — likely because it crashed before JSON mode engaged), treat the paper as if it had produced one synthetic `JSS-PARSE-000` violation on line 1 with message `"jss-lint did not return JSON: <first 200 chars of stderr>"`. If the linter did emit JSON but with a `JSS-PARSE-000` entry inside `violations`, that entry flows through the normal path — no special-casing needed.
- **Exit-status handling**:
  - Exit 0: clean paper, persist zero violations, `papers.status = "scanned_clean"`.
  - Exit 1: violations found; persist them; `papers.status = "scanned"`.
  - Exit 2: the linter itself failed. Record a synthetic `JSS-PARSE-000` with message from stderr and `papers.status = "scan_failed"`.
  - Other exit: treat as exit 2.

### The `_invoke_linter` seam

- **Decision**: `scan.py` exposes a private `_invoke_linter(paper_dir: Path, jss_lint: str) -> LinterResult` where `LinterResult = (exit_code, stdout, stderr, elapsed_seconds)`. Tests monkeypatch `eval.scan._invoke_linter` with a fixture that returns canned `LinterResult` values. The real subprocess shell-out lives behind this seam.
- **Rationale**: mocking `subprocess.run` globally breaks unrelated subprocess calls in the same test run. A named seam is both narrower (only the linter call is mocked) and clearer in stack traces.
- **Alternatives considered**:
  - *`unittest.mock.patch("subprocess.run")`*: too coarse; see above.
  - *Dependency-injecting the subprocess function as an argument*: would push the seam into every caller of `scan()`. Rejected on §X grounds.

## AI client (`review.py`, Phase B)

### Backend: `llama-server` with OpenAI-compatible API

- **Decision**: Production implementation is `LlamaServerClient` talking `POST /v1/chat/completions` (the OpenAI-compatible endpoint that `llama.cpp`'s `llama-server` exposes), with the request body:
  ```json
  {
    "model": "qwen3-30b-a3b",
    "messages": [{"role": "system", "content": "<judging prompt>"},
                 {"role": "user",   "content": "<violation + context>"}],
    "temperature": 0.1,
    "top_p": 1.0,
    "response_format": {"type": "json_object"},
    "stream": false
  }
  ```
  The server is already started by the user with `top-k=1`, `min-p=0.0`, `temp=0.1`, `--temp 0.1 --top-p 1.0 --min-p 0.0 --top-k 1` — see spec Clarifications. Client-side `temperature=0.1` is redundant given server-side `top-k=1` (greedy decoding ignores temperature) but sent for robustness if the server defaults drift.
- **Transport**: stdlib `urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})` + `urllib.request.urlopen(req, timeout=60)`. No `requests` dependency (spec FR-003).
- **Response parsing**: the model is instructed (via the system prompt) to return strict JSON of shape `{"verdict": "true_positive"|"false_positive"|"uncertain", "confidence": 0.0..1.0, "reason": "<short>"}`. The client parses `response["choices"][0]["message"]["content"]` as JSON (after trimming any code-fence wrapper). Malformed responses → row left as `"uncertain"` and the raw content logged (spec Edge Cases).
- **Why llama-server over Ollama**: the user's existing local setup is `llama-server`; pinning it also gives us the OpenAI-compatible API so any managed-API fallback (if ever needed in CI) is a drop-in replacement. Ollama's `/api/generate` is a different transport and does not expose the exact sampler knobs (`top-k`, `min-p`) as first-class JSON fields, so the determinism contract is less crisp.
- **Alternatives considered**:
  - *Ollama + `/api/generate`* — as originally proposed in the `/speckit.plan` input. Rejected in the 2026-04-23 Clarifications; reasons above.
  - *Streaming response (`"stream": true`)* — no value for a single-verdict classification that returns ≤200 tokens. Adds parsing complexity.
  - *Managed APIs (Anthropic / OpenAI)* — creates a per-contributor billing and network dependency; violates "no external-service dependency" (spec Assumptions).

### Confidence and the threshold flag

- **Decision**: The model self-reports `confidence ∈ [0, 1]` as part of its JSON response. `eval-jss review --confidence-threshold 0.8` (default 0.8) decides whether to store the model's verdict (`confidence ≥ threshold`) or leave the row as `uncertain` (`confidence < threshold`). The threshold is a CLI flag so it can be tuned without a code change (matches the `/speckit.plan` input guidance, and aligns with spec FR-016).
- **Caveat on "confidence" under greedy decoding**: with `top-k=1` the token-level probability of every emitted token is effectively 1.0 relative to the sampling process. The "confidence" the model emits is therefore a **self-reported subjective score**, not a calibrated probability. This is documented in `contracts/review-client.md` and in the user-facing help of `--confidence-threshold`, so no one confuses it with a principled probability.
- **Alternatives considered**:
  - *Derive confidence from response logprobs (`logit_bias` / `logprobs=true`)*: `llama-server` supports logprobs via the OpenAI `logprobs` field, but with greedy decoding the chosen token's logprob is always the argmax — the signal is degenerate. Rejected.
  - *Ensemble over prompt paraphrases*: gives a real confidence signal but at N× latency and adds significant prompt-engineering surface. Deferred — out of scope for this spec.

### Skip-list

- **Decision**: `eval/review-skip-list.toml`:
  ```toml
  # Rules whose AI-label precision is historically low.
  # `eval-jss review` skips these entirely so they flow straight to
  # `human-review`. Add rules here as Step 3 lands them and observes
  # model blind spots.
  #
  # Format: each entry is a rule id. An optional `reason` string
  # documents why the rule is here so it can be revisited as the
  # model improves.
  skip_rules = [
      # Example entry documenting the first known blind spot
      # (leaf entry commented out because no such rule ships yet):
      # { rule_id = "JSS-CODE-003", reason = "Qwen3 mislabels param=value inside \\code{}" },
  ]
  ```
  `review.py` loads the file with `tomllib` (≥3.11) / `tomli` (3.10 — already a conditional dep in `pyproject.toml`). If the file is absent, the skip-list is empty — not an error.
- **Rationale**: The `/speckit.plan` input hard-coded a match on `rule_id == "JSS-CODE-003"` and a string search for `=` in the message. Hard-coding this violates §X (speculative surface) and FR-018 (data-driven); moreover, `JSS-CODE-003` does not exist yet. A TOML table is the minimum data-driven surface that lets Step 3 add entries without touching the harness code.
- **Alternatives considered**:
  - *Hard-coded Python list*: rejected on §X and FR-018.
  - *Configurable regex match against message*: more flexible but harder to audit. A rule-id skip is enough; if we need message-level carve-outs later, it's an additive extension.

## `human-review` TUI

### Prompt layout and choices

- **Decision**: One violation at a time. For each row, render a `rich.table.Table` showing: paper short name, rule id, line, column, severity, full message. Immediately below, render a `rich.syntax.Syntax` block with the source file's ±3 lines around the violation (using the rule's reported `line`), line-numbered. Then prompt: `rich.prompt.Prompt.ask("Verdict", choices=["t", "f", "u", "s", "q"], default="u")` mapping to `true_positive`, `false_positive`, `uncertain`, `skip` (leave unchanged, move to next), `quit` (exit the loop).
- **Verdict reason**: on `t` and `f` prompts, also ask `Prompt.ask("Reason (optional)", default="")`. Stored verbatim in `verdict_reason`.
- **Reviewer stamp**: `reviewer = f"human:{os.environ.get('USER', 'unknown')}"` (spec FR-014). A `--reviewer <name>` flag overrides this when the environment is unset (CI, container).
- **Session resumability**: every verdict is its own `BEGIN`/`COMMIT`, so a `Ctrl-C` mid-session loses at most the violation currently on screen (spec FR-015). Batching commits would be a micro-optimisation with no observable benefit at this volume.
- **Alternatives considered**:
  - *Commit every N verdicts (as the `/speckit.plan` input suggested)*: optimises the wrong axis. SQLite commits at this rate are cheap; data safety is the contract that matters.
  - *`prompt_toolkit`*: full-screen TUI with edit fields and completion. Overkill for a yes/no/maybe/skip/quit prompt.
  - *`input()` with no rich rendering*: works, but the syntax-highlighted context snippet is the feature — it's the thing that lets the reviewer decide quickly.

### Source snippet strategy

- **Decision**: Open the paper's source file once, read all lines, slice `[line-4:line+3]` (inclusive of a 3-line before/after window) for each violation in the paper, render with `Syntax("".join(snippet), "latex", line_numbers=True, start_line=max(1, line-3))`. Cache the file's lines on the paper for the duration of the session so we don't re-read for every violation.
- **Edge case — line beyond EOF**: the linter once emitted a line number past EOF for a file that ends mid-macro. Clamp to `min(line, total_lines)` before slicing; never crash.
- **Edge case — parse-failure violations on line 1**: `JSS-PARSE-000` rows surface in `human-review` just like any other (spec FR-013), with context showing the first 7 lines of the file.

## Report rendering

### Precision query

- **Decision**: One SQL query computes the whole precision table:
  ```sql
  SELECT rule_id,
         SUM(CASE WHEN verdict = 'true_positive'  THEN 1 ELSE 0 END) AS tp,
         SUM(CASE WHEN verdict = 'false_positive' THEN 1 ELSE 0 END) AS fp,
         SUM(CASE WHEN verdict IS NULL OR verdict = 'uncertain' THEN 1 ELSE 0 END) AS pending
    FROM violations
   WHERE rule_id != 'JSS-PARSE-000'
   GROUP BY rule_id;
  ```
  Precision is `tp / (tp + fp)` where `(tp + fp) > 0`; otherwise the rule is rendered as "not yet measured" (spec FR-020). A companion query counts parse failures for the dedicated report row (spec FR-021). A third query (Phase B only, behind `--by-source`) joins `violations` to `papers` and groups by `(rule_id, papers.source)`.
- **Category grouping**: the `violations` table does not carry rule category — the linter emits rule category in its JSON under each violation's `category` field (per spec 001's JSON contract). Rather than reaching back into the linter to look up category for every report, we record `category` as a column on `violations` at scan time. See `contracts/schema.md` for the schema adjustment this implies.

### Rich table rendering

- **Decision**: `rich.table.Table` with columns `Category`, `Rule ID`, `TP`, `FP`, `Pending`, `Precision`, `Status`. Status is one of `PASS (≥90%)` (green), `FAIL (<90%)` (red), `NOT MEASURED` (dim — no labelled data), `NOT EXERCISED` (dim — no violations reported). Parse failures render in a separate panel below the precision table.
- **"Not exercised" detection**: a rule has zero rows in `violations`. We need the set of all known rules to know what is not exercised. Source of truth: the union of distinct `rule_id` values ever written to `violations` across all runs (we know a rule exists only by seeing it fire). This is imperfect — a brand-new rule that fires on nothing in the corpus is invisible — but it matches the spec ("not exercised" applies to rules known to the harness via a prior scan, not to all rules the linter knows about).
- **Alternatives considered**:
  - *Ask `jss-lint --list-rules`*: requires a CLI flag that doesn't exist in spec 001. Out of scope here; could be added later if the invisibility problem bites.

### CSV history

- **Decision**: `eval/report.csv`. Header: `ts,tool_version,rule_id,category,tp,fp,pending,precision,source`. The `source` column is `"overall"` for the aggregate row per rule, or a manifest source value (`cran` / `bioc` / `arxiv` / `jss_archive` / `manual`) for per-source rows produced by `--by-source`. Written with `csv.DictWriter`; the header is emitted iff the file didn't exist before opening.
- **Atomicity**: open in `"a"` mode; each run is one `flush()`. The file is only written after the rich table has been rendered to stdout, so `Ctrl-C` during rendering cannot produce a half-written CSV row.
- **Alternatives considered**:
  - *JSON-lines*: friendlier for programmatic consumers; CSV is friendlier for `git diff` — and humans eyeballing a trend line is the primary use case. CSV wins.
  - *SQLite-only history with an exported CSV on demand*: extra command surface. `report` always appending to the CSV is simpler and matches the spec ("appends a row per invocation").

## Corpus management (Phase B)

### Manifest schema

- **Decision**: `eval/corpus-manifest.csv`. Columns per spec FR-024: `jss_doi, source, source_id, version, vignette_file, local_path, sha256`. All seven columns are required; empty strings for manuals are accepted except for `source` (`manual`) and `sha256` (must be filled once the file is stable). Documented in `contracts/corpus-manifest.md`.
- **Rationale**: CSV is the lowest-friction format that `git diff` can render sanely. The columns match exactly what `corpus fetch` needs to reconstruct the file — no implicit defaults.

### `corpus fetch` flow

- **Decision**: for each manifest row:
  1. If `local_path` exists and its SHA256 matches `sha256` → skip (already materialised).
  2. Else resolve a distribution URL based on `source`:
     - `cran` → `https://cran.r-project.org/src/contrib/Archive/{source_id}/{source_id}_{version}.tar.gz`
     - `bioc` → `https://bioconductor.org/packages/{version}/bioc/src/contrib/{source_id}_<tarball>.tar.gz` (the exact tarball filename is looked up in the Bioc tarball index once per `version`; cached)
     - `arxiv` → `http://arxiv.org/e-print/{source_id}{version}` (the version is stored with the `v` prefix, e.g. `v2`, to match arXiv's URL)
     - `jss_archive` → **not re-hosted**; a manual placement into `local_path` is required. `corpus fetch` logs a gap row with reason `"jss_archive: manual placement required"`.
     - `swhid` (stored in `version`) → `https://archive.softwareheritage.org/api/1/content/sha1_git:{hex}/raw/`
     - `manual` → no fetch; local file must already exist.
  3. Download into a temp file (`tempfile.NamedTemporaryFile(delete=False)`), compute SHA256 of the bytes, compare to `sha256`. Mismatch → gaps row, delete temp file.
  4. On match: if tarball, extract into the directory derived from `local_path`; if single-file (`.tex` arXiv response), copy to `local_path`.
- **HTTP**: `urllib.request.urlopen(url, timeout=60)`. Read in 64 KiB chunks into `hashlib.sha256()` and `tempfile` simultaneously, to avoid buffering an entire tarball in memory.
- **Tarball extraction safety**: `tarfile.open(fileobj=..., mode="r:*")`; use `tarfile.data_filter` (Python ≥3.12) or a manual pre-3.12 implementation that refuses members whose resolved path escapes the extraction dir (the classic "tarslip" attack). This is a real concern for corpus tarballs fetched from any source, even a trusted one, because CRAN does not guarantee tarball contents.
- **Alternatives considered**:
  - *`requests` with streaming*: nicer API but introduces a runtime dependency. Rejected.
  - *Fetching tarballs without a temp file, extracting from an in-memory `BytesIO`*: runs the risk of OOM on large tarballs (some CRAN vignettes are part of multi-megabyte packages).

### Discovery is NOT in this spec

- **Decision**: This spec implements `corpus fetch` (spec FR-025), not corpus *discovery*. The GitHub code-search / arXiv API / JSS OJS OAI-PMH workflows that the spec describes in Assumptions are a separate concern; they inform how the manifest is populated by hand and could become a later spec's `eval-jss corpus discover` subcommand. Building discovery now would expand the surface without changing what `eval-jss report` can assert.
- **Rationale**: §X (small surface). The precision gate depends only on a reproducible manifest, not on automation of the manifest's initial authoring.
- **Alternative considered**: adding a `corpus discover` subcommand in this spec. Rejected — the manifest for Phase B can be bootstrapped by hand from ~10–20 CRAN packages that spec 001's compliant fixture already references (the canonical `docs/jss-template/article.tex` is itself a CRAN-style vignette).

### Phase A corpus reproducibility

- **Decision**: Phase A ships without a manifest. Precision claims made during Phase A cite the **git commit hash of `examples/`** as the corpus identity — not a manifest hash. `eval-jss report`'s CSV row does not carry a corpus hash column in Phase A; Phase B adds one (column extension is backward-compatible for CSV).
- **Rationale**: Constitution §XII says "No rule-precision claim in the paper, release notes, or PR description is valid without citing a corpus commit hash." A `git` commit covering `examples/` is a corpus commit hash — §XII is satisfied as long as `examples/` is checked into the repo. The manifest is how we satisfy §XII when the corpus grows beyond what we want in `git` (a few hundred MB of CRAN tarballs); at 10 papers' worth of vignettes the manifest would be a ceremony over `git`'s own content hash.
- **Documented where**: `quickstart.md` § "Reproducing a precision claim" spells this out for Phase A reviewers; `eval/README.md` restates it. Phase B's `corpus fetch` simply extends the mechanism.

## Testing strategy

### Fixtures and seams

- **`tmp_db`**: `@pytest.fixture def tmp_db(tmp_path) -> Path` — returns a path to an empty, schema-initialised SQLite file under `tmp_path`. Built by `db.init(tmp_path / "eval.db")`.
- **`fake_corpus`**: `@pytest.fixture def fake_corpus(tmp_path) -> FakeCorpus` — creates three subdirectories under `tmp_path / "examples"`, each with a `.tex` and `.bib` file and a `README.md`. The `.tex` contents are tuned so the canned `_invoke_linter` mock can map them to known violations. Returns a `FakeCorpus` dataclass with paths and expected-violation lists.
- **`fake_client`**: `@pytest.fixture def fake_client() -> FakeClient` — a `ReviewClient` implementation with `self.verdicts: dict[str, tuple[Verdict, float, str]]` keyed by `rule_id`. Tests populate the mapping and assert which rows were labelled vs left uncertain.
- **`_invoke_linter` mock**: `monkeypatch.setattr(eval.scan, "_invoke_linter", fake_linter)` where `fake_linter(paper_dir, jss_lint) -> LinterResult` reads a per-fixture JSON file describing the violations to emit. No real `jss-lint` on PATH required.

### Integration test coverage

- **`test_integration.py`** walks the entire Phase A pipeline end-to-end:
  1. Start with no DB.
  2. Run `cli.main(["init", "--db", str(tmp_db_path)])` → assert schema created.
  3. Run `cli.main(["scan", "--corpus", str(fake_corpus.root), "--db", str(...)])` → assert 3 rows in `papers`, N rows in `violations` matching `fake_corpus.expected_violations`, 1 row in `runs`.
  4. Monkeypatch `rich.prompt.Prompt.ask` to return scripted answers keyed by call count; run `cli.main(["human-review", ...])`; assert verdicts applied.
  5. Run `cli.main(["report", ...])` → capture the stdout table via `CliRunner(mix_stderr=False)` and assert precision numbers match hand-computed values; assert `eval/report.csv` row appended (Phase B — guarded by a skip marker until `report.py` learns CSV append; Phase A leaves CSV empty).
- **Why an integration test at all** — spec FR-028. Each unit test exercises one module in isolation; the integration test is what proves the plumbing is actually plumbed together. It runs in under 10 seconds per SC-005.

### AI-review test isolation

- **Contract**: no test may hit `localhost:8080`. `test_review.py` always constructs `FakeClient`; the `LlamaServerClient` has its own targeted test under a `@pytest.mark.network` marker that is skipped by default. The CI runs the default set (no network), so the AI server being down does not break CI.

## Open items

### Category attribution for violations

- **Issue**: The spec assumes the report groups by "rule category", but Step 1's linter JSON emits category only at the category-summary level, not per-violation (spec 001 FR-010 / `contracts/json-output.md`). The harness needs to know each violation's category.
- **Decision**: Extend the scan's ingest step to read the `categories` block of the linter's JSON (which maps rule-id to category) and populate `violations.category` at insert time. This adds one `TEXT` column to the schema; `schema.sql` ships it from the start (see `contracts/schema.md`).
- **Alternative considered**: *fetch category at report time via `jss-lint --list-rules`* — requires a linter flag that doesn't exist. Rejected.

### `examples/` is shared with the spec 001 compliant fixture

- **Issue**: `docs/jss-template/article.tex` was vendored in Step 0.5. The MVP corpus lives under `examples/`; none of the 10 paper subdirectories overlap with `docs/jss-template/`. The spec 001 compliant fixture `tests/fixtures/compliant/minimal.tex` is a reduced version of `docs/jss-template/article.tex`, not of any `examples/` paper.
- **Decision**: no conflict. `examples/` is new territory for this spec and is the MVP corpus's home. The README there will briefly link back to `docs/jss-template/` so someone looking for "the canonical JSS preamble" finds it.

### Python <3.11 `tomllib` fallback for the skip-list

- **Issue**: `tomllib` is 3.11+. `pyproject.toml` already has `tomli>=2.0; python_version<"3.11"` as a conditional. `review.py` can reuse the same import shim spec 001's `config.py` uses.
- **Decision**: `review.py` imports via the same guard. No new dependency; no duplication — we can factor the shim into `texlint.config` and let `eval.review` import `_load_toml` from there. *Rejected* because it would make `eval/` depend on `src/texlint/`, violating the project-structure decision. Duplicating ~5 lines of import guard is fine (§X — three concrete callers would justify a helper, two does not).

### Deferred / out-of-scope

- **Discovery automation (GitHub code search, arXiv API, OJS OAI-PMH enumeration)**: deferred to a later spec. This spec implements only reproduction (`corpus fetch`), which is what the precision gate depends on.
- **Multi-file vignettes**: every MVP corpus paper is one `.tex` + at most one `.bib`. CRAN vignettes with auxiliary `.tex` includes are out of scope; if the Step 3 corpus adds them, a dedicated spec will extend `scan.py` to pass the full file list to `jss-lint`.
- **Re-labelling history**: the `violations` table keeps only the most recent verdict (FR-014's overwrite semantics). A full audit log of verdict changes is a full-scope concern for a later spec, not this one.
- **Windows `corpus fetch`**: POSIX only in this spec. SQLite + subprocess + the CLI work fine on Windows; tarball extraction paths are the question mark.
- **`jss-lint --list-rules` flag**: would let `report` know about unexercised rules. Out of scope — we handle it structurally ("not exercised" means no prior scan has seen this rule).
