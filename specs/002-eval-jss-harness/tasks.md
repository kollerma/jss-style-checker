---
description: "Task list for `eval-jss` — precision harness for the JSS linter"
---

# Tasks: `eval-jss` — Precision Harness for the JSS Linter

**Input**: Design documents from `/specs/002-eval-jss-harness/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: The constitution's §VIII TDD mandate is narrowly scoped to files under `src/texlint/journals/*/rules/`. This harness lives outside that scope, so §VIII does not strictly apply. However, **spec FR-027 and FR-028 explicitly require** unit tests per module plus one end-to-end integration test — so test tasks are included and ordered before the implementations they cover. Test tasks MUST fail before the implementation task that makes them pass.

**Organization**: Tasks are grouped by user story. US1 is the MVP (spec Phase A). US2–US5 are the Phase B extensions that the spec's 2026-04-23 scope Clarification pinned into this same spec. Per spec FR-001, Phase A tasks precede Phase B; a partial Phase B must never regress Phase A.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel — different files, no dependency on an incomplete task.
- **[Story]**: User-story label `US1`…`US5`. Setup, Foundational, and Polish phases carry no story label.

## Path Conventions

- **Harness source**: `eval/` (top-level, peer to `src/texlint/`, deliberately outside the wheel).
- **Harness tests**: `tests/eval/`. Never imports from `src/texlint/`.
- **MVP corpus**: `examples/` (Phase A — 10 hand-curated CRAN vignettes checked in).
- **Phase B data**: `eval/corpus-manifest.csv`, `eval/review-skip-list.toml`, `eval/report.csv` (all checked in).
- **Runtime state**: `eval/eval.db` (gitignored).

All paths below are repository-relative.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Scaffold the `eval/` package, register the console script, and gitignore the runtime database.

- [ ] T001 Create `eval/__init__.py` (empty module marker) and `tests/eval/__init__.py` (empty test-package marker) so both are importable
- [ ] T002 Add `eval-jss = "eval.cli:main"` under `[project.scripts]` in `pyproject.toml`; add `"eval"` to `[tool.hatch.build.targets.sdist.include]`; verify `[tool.hatch.build.targets.wheel.packages]` stays `["src/texlint"]` so the harness stays out of the published wheel
- [ ] T003 [P] Append `eval/eval.db` and `eval/eval.db-*` (WAL / SHM sidecars) to `.gitignore`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared types, the database layer, the test fixtures, and the empty CLI skeleton. **Every user story depends on this phase being complete.**

**⚠️ CRITICAL**: No user-story work may begin until T009 is green.

- [ ] T004 [P] Write `eval/schema.sql` containing the exact DDL from `specs/002-eval-jss-harness/contracts/schema.md` — three `CREATE TABLE IF NOT EXISTS` statements (`papers`, `runs`, `violations`) plus three `CREATE INDEX IF NOT EXISTS` statements (`idx_viol_rule`, `idx_viol_verdict`, `idx_viol_paper`); `runs` precedes `violations` so the FK resolves
- [ ] T005 [P] Implement shared types in `eval/api.py`: `Verdict` and `Severity` string enums; frozen dataclasses `Paper`, `Violation`, `Run`, `LinterResult`, `ManifestRow`, `ClassifyResult`; module docstring linking to `specs/002-eval-jss-harness/data-model.md`
- [ ] T006 [P] Write `tests/eval/conftest.py` providing `tmp_db` fixture (calls `eval.db.init(tmp_path / "eval.db")` and yields the path) and `fake_corpus` fixture (creates three subdirectories under `tmp_path / "examples"` each with a `.tex` and `.bib`, returns a `FakeCorpus` dataclass with paths + expected-violation lists); **leaves `fake_client` fixture as a TODO** to be added in T025
- [ ] T007 Write `tests/eval/test_db.py` — assert `PRAGMA foreign_keys`, `PRAGMA journal_mode`, `PRAGMA synchronous` are applied on connect; `init()` is idempotent (second call is a no-op with no error); deleting a `papers` row cascades to its `violations` rows; `now_utc()` returns an ISO 8601 UTC string ending in `Z`. **MUST FAIL before T008** (no `eval/db.py` yet)
- [ ] T008 Implement `eval/db.py` with: `connect(path: Path) -> sqlite3.Connection` (isolation_level=None, PRAGMAs applied, `row_factory = sqlite3.Row`); `init(path: Path) -> None` (creates parent dir, calls `connect`, loads `eval/schema.sql` via `executescript`); `now_utc() -> str` helper; small query helpers used by other modules (`execute`, `executemany_ignore`, `fetchall`). Depends on T004, T005, T007
- [ ] T009 Create `eval/cli.py` skeleton — `click.group()` with `--db` global option defaulting to `eval/eval.db`, empty `@cli.command()` stubs for `init`, `scan`, `human-review`, `review`, `report`, and a `corpus` sub-group containing `fetch` and `status` stubs; `init` calls `eval.db.init(ctx.obj["db"])` immediately (it's the one subcommand that is complete in this phase); also write `tests/eval/test_cli_skeleton.py` asserting `eval-jss --help` lists every subcommand and `eval-jss init` on a fresh path creates the schema. Depends on T008

**Checkpoint**: Foundation ready — `eval-jss init` works end-to-end. User-story phases can now begin.

---

## Phase 3: User Story 1 — Measure per-rule precision on a pinned corpus (Priority: P1) 🎯 MVP

**Goal**: Deliver the spec's Phase A end-to-end loop. An operator running `eval-jss init && eval-jss scan && eval-jss human-review && eval-jss report` on a 10-paper `examples/` corpus obtains a per-rule precision number with rules below the 90% threshold visually flagged.

**Independent Test**: `tests/eval/test_integration.py` runs `init → scan (with mocked _invoke_linter) → scripted human-review → report` on the 3-paper `fake_corpus` fixture and asserts that reported precision matches hand-computed values, in under 10 seconds (spec SC-005).

### Tests for User Story 1

*Write first, ensure each FAILS, then move to the implementation tasks.*

- [ ] T010 [P] [US1] Write `tests/eval/test_scan.py` — scan processes each paper once via `_invoke_linter`, violations are persisted with `INSERT OR IGNORE`, a second scan inserts zero rows, `JSS-PARSE-000` flows through the normal path, missing `jss-lint` on PATH exits 2 with a clear message, linter exit 2 records a synthetic `JSS-PARSE-000` with stderr message, a single `runs` row per invocation captures `tool_version` / `papers_scanned` / `violations_found`. **MUST FAIL before T015**
- [ ] T011 [P] [US1] Write `tests/eval/test_human_review.py` — monkeypatches `rich.prompt.Prompt.ask` with a scripted answer queue; asserts `t`/`f`/`u` map to the correct `Verdict` strings; `reviewer` field is set to `human:<$USER>` (or `--reviewer` override); optional `verdict_reason` is captured; `s` skips without changing the row; `q` exits the loop cleanly; every verdict commits before the next row loads (simulate a mid-session `KeyboardInterrupt` and assert prior verdicts persist); `--rule` and `--limit` filters apply. **MUST FAIL before T017**
- [ ] T012 [P] [US1] Write `tests/eval/test_report.py` — Phase A cases only: precision equals `tp / (tp + fp)` and is correctly rounded for display; "not yet measured" shows when no labels exist; "not exercised" shows when a rule has zero violations; `JSS-PARSE-000` rows never enter the numerator or denominator but surface in the dedicated parse-failure panel; `--below-threshold` flag is correctly computed; `eval-jss report` exits 1 iff any rule is below 0.90. **MUST FAIL before T019**
- [ ] T013 [US1] Write `tests/eval/test_integration.py` — uses `fake_corpus`, monkeypatches `eval.scan._invoke_linter` with a fixture-driven fake and `rich.prompt.Prompt.ask` with a scripted verdict queue; runs `cli.main(["init", ...])`, `cli.main(["scan", ...])`, `cli.main(["human-review", ...])`, `cli.main(["report", ...])` in sequence via `click.testing.CliRunner`; asserts precision numbers match hand-computed expected values; asserts wall-clock under 10 seconds (SC-005). **MUST FAIL until T015–T020 are all complete** (this test is the Phase A acceptance gate)

### Implementation for User Story 1

- [ ] T014 [P] [US1] Curate the initial `examples/` corpus under `examples/` (top-level, repo-root-relative): create 10 subdirectories each containing one CRAN JSS-vignette `.tex` file and its `.bib`, named `cran_<pkg>_<version>/`; add `examples/<dir>/README.md` per paper with the CRAN URL, pinned version, and DOI (if any); add `examples/README.md` describing the curation policy and how to add a paper. Pure data task — no dependency on code in `eval/`
- [ ] T015 [US1] Implement `eval/scan.py` — private `_invoke_linter(paper_dir: Path, jss_lint: str) -> LinterResult` calling `subprocess.run([...], capture_output=True, text=True, check=False, timeout=120)`; public `scan(db_path: Path, corpus_dir: Path, *, batch_size: int | None, force: bool) -> int` that resolves `jss-lint` via `shutil.which`, walks the corpus dir for subdirectories (new → `papers` row, existing → reuse), opens a `runs` row, per-paper invokes the linter, `json.loads(stdout)` with the malformed-JSON fallback from research.md §"Invoking `jss-lint`", ingests violations via `INSERT OR IGNORE` with category carried from the linter's JSON, updates `papers.status`, commits the `runs` row at the end, returns the exit code. Depends on T008, T010
- [ ] T016 [US1] Replace the `scan` stub in `eval/cli.py` with the full wiring: `--corpus DIR` (default `examples/`), `--batch-size INT`, `--force` flag; progress rendered to stderr via `rich.progress`; propagate the return code from `scan.scan()`. Depends on T015
- [ ] T017 [US1] Implement `eval/human_review.py` — `interactive_review(db_path, *, limit, rule, reviewer) -> int` that queries `violations` where `verdict IS NULL OR verdict = 'uncertain'` ordered by paper, line; for each row opens the paper source once, slices ±3 lines around the violation (clamped to file bounds), renders with `rich.syntax.Syntax(..., "latex", line_numbers=True, start_line=max(1, line-3))`, shows a `rich.table.Table` with rule / message / severity / paper, calls `Prompt.ask("Verdict", choices=["t","f","u","s","q"], default="u")`, on `t`/`f` additionally asks for optional `Reason`; commits each verdict individually; reviewer defaults to `f"human:{os.environ.get('USER','unknown')}"`. Depends on T008, T011
- [ ] T018 [US1] Replace the `human-review` stub in `eval/cli.py` with wiring: `--limit N`, `--rule RULE_ID`, `--reviewer NAME`. Depends on T017
- [ ] T019 [US1] Implement `eval/report.py` — `compute_precision(cx) -> PrecisionTable` running the per-rule SQL from research.md §"Precision query" (excluding `JSS-PARSE-000` rows); `render_terminal(table)` emitting a `rich.table.Table` grouped by category with `PASS` (≥0.90, green) / `FAIL` (<0.90, red) / `NOT MEASURED` / `NOT EXERCISED` statuses; separate `render_parse_panel(cx)` for `JSS-PARSE-000` counts per paper; `run(db_path, *, by_source: bool = False, csv_path: str | None = None) -> int` returning exit 1 iff any rule is below threshold. Leaves `by_source` and `csv_path` as typed parameters but the Phase A default is `by_source=False, csv_path=None`. Depends on T008, T012
- [ ] T020 [US1] Replace the `report` stub in `eval/cli.py` with wiring: no flags in Phase A (just `--db`); exit-code propagation from `report.run()`. Depends on T019

**Checkpoint (MVP / Phase A shippable)**: After T013 goes green (which in turn requires T015–T020 to be green), the full end-to-end loop works on `examples/`. Step 3 rule development can begin using this harness.

---

## Phase 4: User Story 2 — Reduce manual labelling with AI-assisted review (Priority: P2, Phase B)

**Goal**: `eval-jss review` sends each unlabelled violation through a locally-hosted LLM and writes back high-confidence labels; low-confidence rows remain `uncertain` for human review. A data-driven skip-list lets Step 3 opt specific rules out of AI labelling as blind spots are discovered.

**Independent Test**: `tests/eval/test_review.py` drives the review loop with a `FakeClient` that returns canned `ClassifyResult`s per rule id; asserts high-confidence rows are labelled with `reviewer = ai:<model>`, low-confidence rows stay `uncertain`, skip-list entries bypass the client entirely, malformed client responses leave the row `uncertain`.

### Tests for User Story 2

- [ ] T021 [P] [US2] Write `tests/eval/test_review.py` — constructs a `FakeClient` with per-rule-id canned `ClassifyResult`s; asserts verdicts are written iff `confidence >= --confidence-threshold`; `reviewer` stamped as `ai:<model>`; skip-list from `eval/review-skip-list.toml` skips matching rule ids with zero `classify()` calls; malformed-response path (FakeClient returning `UNCERTAIN, 0.0, "malformed"`) leaves the row `uncertain`; no test in this file touches `localhost:8080`. **MUST FAIL before T022**

### Implementation for User Story 2

- [ ] T024 [P] [US2] Create `eval/review-skip-list.toml` with an empty `skip_rules = []` array plus a commented example entry documenting the `\code{param=value}` Qwen3 blind spot (example is commented because the rule it would reference does not exist yet — the file is live infrastructure that Step 3 will populate)
- [ ] T022 [US2] Implement `eval/review.py` — `ReviewClient` Protocol with `classify(violation: dict, paper_context: str) -> ClassifyResult` signature; `LlamaServerClient(model, base_url, timeout)` building the OpenAI-compatible `POST /v1/chat/completions` request per `contracts/review-client.md` (system prompt verbatim, user prompt shape as documented, `response_format: {"type": "json_object"}`, `stream: false`); transport via stdlib `urllib.request` — no `requests` dep; JSON response parsing with code-fence stripping and graceful degradation to `UNCERTAIN` on malformed content; skip-list loader using the `tomllib`/`tomli` shim; orchestration function `run(db_path, *, limit, confidence_threshold, model, base_url, skip_list_path) -> int` iterating `verdict IS NULL` rows, bypassing skip-listed rules, calling the client, writing back verdicts that meet the threshold. First-call network failure → exit 2; subsequent-call failures → row left `uncertain`. Depends on T008, T021
- [ ] T023 [US2] Replace the `review` stub in `eval/cli.py` with wiring: `--limit N`, `--confidence-threshold F` (default 0.8), `--model NAME` (default `qwen3-30b-a3b`), `--base-url URL` (default `http://localhost:8080`), `--skip-list PATH` (default `eval/review-skip-list.toml`). Depends on T022
- [ ] T025 [P] [US2] Add the `fake_client` fixture to `tests/eval/conftest.py` (closes the TODO from T006) — a `FakeClient` whose `classify` returns `self.verdicts[rule_id]` with a sensible default; also write `tests/eval/test_llama_server_client_live.py` marked `@pytest.mark.network` that performs one real call against `localhost:8080` and asserts a well-formed `ClassifyResult`; register the marker in `pyproject.toml`'s `[tool.pytest.ini_options]` so `pytest -m "not network"` excludes it (CI default). Depends on T022

**Checkpoint**: After T023 is green, AI-assisted review is wired and tested end-to-end against `FakeClient`. The live-server test exists but is off by default.

---

## Phase 5: User Story 3 — Reproduce the corpus from a pinned manifest (Priority: P2, Phase B)

**Goal**: `eval-jss corpus fetch` materialises every manifest entry from an immutable, version-pinned distribution URL, verifies SHA256 against the manifest value, and records any gaps in `eval/corpus-manifest-gaps.csv`. `eval-jss corpus status` reports pending / mismatched / manually-staged rows without fetching.

**Independent Test**: `tests/eval/test_corpus.py` exercises manifest parsing, SHA256 verification, hash-mismatch gap logging, and tarball extraction on a local fixture manifest whose URLs are mocked via `monkeypatch` on `urllib.request.urlopen`.

### Tests for User Story 3

- [ ] T026 [P] [US3] Write `tests/eval/test_corpus.py` — manifest parser enforces the 7-column schema and `local_path` uniqueness per `contracts/corpus-manifest.md`; distribution URL derivation is correct for each `source`; SHA256 verify on a streamed fake tarball matches when correct and logs a gaps row on mismatch; `jss_archive` always writes a "manual placement required" gaps row; `manual` rows never fetch and succeed iff the file is already at `local_path`; tarslip defence refuses extraction for a member whose resolved path escapes the target directory; re-running on an already-materialised file is a no-op. **MUST FAIL before T027**

### Implementation for User Story 3

- [ ] T027 [US3] Implement `eval/corpus.py` — `load_manifest(path: Path) -> list[ManifestRow]` with strict header and row validation; private `_resolve_url(row: ManifestRow) -> str | None` per the table in `contracts/corpus-manifest.md`; private `_fetch_and_verify(url: str, sha256: str, dest: Path) -> None` streaming via `urllib.request.urlopen(..., timeout=60)` in 64 KiB chunks into both `hashlib.sha256()` and a `tempfile.NamedTemporaryFile(delete=False)` and comparing before rename; private `_extract_tarball(tar_path: Path, target: Path)` using `tarfile.open(mode="r:*")` with `data_filter` on Python ≥3.12 and a manual tarslip check on 3.10/3.11; `run_fetch(manifest_path, target_dir, gaps_path) -> int` orchestrating the per-row loop and writing the gaps file atomically at the end; `run_status(...)` reporting a rich table without fetching. Depends on T008, T026
- [ ] T028 [US3] Replace the `corpus` sub-group stubs in `eval/cli.py` with wiring: `corpus fetch --manifest PATH --target DIR --gaps PATH` (defaults per `contracts/cli.md`) and `corpus status --manifest PATH --target DIR`; exit 1 when the gaps file is non-empty, exit 2 for manifest-parse errors. Depends on T027
- [ ] T029 [US3] Create `eval/corpus-manifest.csv` with the header row and one row per paper in the Phase A `examples/` corpus (from T014) — compute each row's SHA256 using `sha256sum` on the upstream CRAN `Archive/` tarball (`{pkg}_{version}.tar.gz`); leaves `jss_doi` empty where unknown. This turns the Phase A corpus into a reproducible-by-manifest corpus retrospectively; Phase B reviewers can now run `eval-jss corpus fetch` as an alternative to trusting `git checkout`. Depends on T014, T027

**Checkpoint**: After T028 is green, the §XII reproducible-corpus mechanism is in place end-to-end.

---

## Phase 6: User Story 4 — Track precision trends over time (Priority: P3)

**Goal**: Every `eval-jss report` invocation appends one row per rule (plus per-source rows when `--by-source`) to `eval/report.csv`, creating an append-only history diffable through `git log -p`.

**Independent Test**: Running `eval-jss report` twice against the same labelled DB produces two CSV blocks sharing per-rule data but differing in `ts`; running again after a relabel produces a third block with updated precision.

### Tests for User Story 4

- [ ] T030 [P] [US4] Extend `tests/eval/test_report.py` with CSV-append cases: header is written iff the file did not previously exist; column order matches `contracts/report-csv.md` exactly; two consecutive invocations produce two contiguous blocks with identical rule/category/tp/fp/pending/precision and different `ts`; `--csv -` disables the append (Phase A default behaviour preserved); Phase B default (when review.py or corpus.py lands) is append to `eval/report.csv`. Assert that changing a single verdict between the two runs yields a different `precision` in the later block. **MUST FAIL before T031**

### Implementation for User Story 4

- [ ] T031 [US4] Extend `eval/report.py` with `append_csv(rows: list[dict], path: Path | None) -> None` using `csv.DictWriter` with the column set from `contracts/report-csv.md`; header written iff `not path.exists()` evaluated before `open(..., "a")`; `path is None` or `path == Path("-")` disables the append. Wire it into `run()` so Phase B default writes to `eval/report.csv` and `--csv -` opts out. Depends on T019, T030
- [ ] T032 [US4] Update `eval/cli.py`'s `report` subcommand with a `--csv PATH` option (default `eval/report.csv` in Phase B, but the CLI default is still accepted in Phase A — the Phase A quickstart simply doesn't document it). Depends on T031

**Checkpoint**: Report CSV history is appended per run and diffable via git.

---

## Phase 7: User Story 5 — Per-source precision breakdown (Priority: P3)

**Goal**: `eval-jss report --by-source` adds per-source precision columns to both the rich table and the CSV history row, so stylistic population differences (CRAN vignettes vs. arXiv preprints) are visible in the precision signal.

**Independent Test**: On a fixture corpus with papers from two `source` values and deliberately engineered verdict distributions, `eval-jss report --by-source` emits overall precision plus per-source precision for every rule with labelled violations on more than one source; a rule with labelled violations on only one source shows a blank cell for the other.

### Tests for User Story 5

- [ ] T033 [P] [US5] Extend `tests/eval/test_report.py` with `--by-source` cases: overall + per-source rows both in the rendered table and in the CSV; blank cell (not zero) for `(rule, source)` pairs with no violations; per-source CSV rows carry the `source` column populated with the manifest source value and the "overall" row uses `source = "overall"`. Fixture corpus must include at least two papers with distinct `source` values. **MUST FAIL before T034**

### Implementation for User Story 5

- [ ] T034 [US5] Extend `eval/report.py` with `compute_precision_by_source(cx) -> PrecisionTable` joining `violations` to `papers` grouped by `(rule_id, papers.source)`; extend `render_terminal` to add per-source columns when `by_source=True`; extend `append_csv` to emit per-source rows in addition to the overall row. Depends on T031, T033
- [ ] T035 [US5] Update `eval/cli.py`'s `report` subcommand with a `--by-source` flag (default `False`). Depends on T034

**Checkpoint**: Per-source precision breakdown is visible both in the terminal and in `eval/report.csv`; stylistic-population differences are no longer buried in the overall number.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, release notes, quickstart validation, and the wheel-exclusion audit.

- [ ] T036 [P] Write `eval/README.md` — one-page overview linking to `specs/002-eval-jss-harness/quickstart.md`; notes that the runtime DB is gitignored and that manifest + skip-list + report.csv are checked in; short section on "How to add a paper to the corpus" mirroring the quickstart's Phase A instructions
- [ ] T037 [P] Update root `README.md` with a new "Evaluation harness" section linking to `eval/README.md` and `specs/002-eval-jss-harness/quickstart.md`; note the two-phase rollout and that precision trends live in `eval/report.csv`
- [ ] T038 Run `specs/002-eval-jss-harness/quickstart.md` end-to-end against a real `examples/` subset (3 papers) on a developer machine; verify every command produces the documented output; fix any drift between quickstart and actual behaviour directly in quickstart.md
- [ ] T039 Audit `pyproject.toml` — confirm `[tool.hatch.build.targets.wheel.packages]` is unchanged (`["src/texlint"]`), that `eval` is in `[tool.hatch.build.targets.sdist.include]`, and that `python -m build --wheel` produces a wheel whose unpacked contents do **not** include `eval/`; produce a one-line audit note at the bottom of `CHANGELOG.md`
- [ ] T040 [P] Add a `CHANGELOG.md` entry under "Unreleased" describing the new `eval-jss` console script, the two-phase rollout, and the §VI / §XII mechanisms it implements; link to `specs/002-eval-jss-harness/spec.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)** — no dependencies; can start immediately.
- **Foundational (Phase 2)** — depends on Setup. **Blocks every user story.** T009's checkpoint (`eval-jss init` works) is the gate.
- **User Story 1 / Phase A (Phase 3)** — depends on Foundational. Independently shippable MVP.
- **User Story 2 / Phase B — AI review (Phase 4)** — depends on Foundational. **Independent of US1** (only touches `eval/review.py` and adds the `review` subcommand).
- **User Story 3 / Phase B — corpus fetch (Phase 5)** — depends on Foundational and on T014 (for T029's manifest rows). Otherwise independent of US1/US2.
- **User Story 4 / Phase B — CSV history (Phase 6)** — depends on Foundational **and on US1's T019** (extends `eval/report.py`). Modifies a US1 file.
- **User Story 5 / Phase B — per-source breakdown (Phase 7)** — depends on US1's T019 **and on US4's T031** (extends the same CSV writer). Modifies a US1/US4 file.
- **Polish (Phase 8)** — depends on whichever user stories are being shipped.

### User Story Dependencies (summary)

- US1 (P1): after Foundational. No dependency on other stories.
- US2 (P2): after Foundational. Independent of US1.
- US3 (P2): after Foundational. Depends on US1's T014 for manifest seeding, otherwise independent.
- US4 (P3): after US1 T019. Enhances US1's `report.py`; not independent.
- US5 (P3): after US1 T019 and US4 T031. Enhances US1/US4.

The spec's Phase A / Phase B split maps cleanly onto: **Phase A = Setup + Foundational + US1**. **Phase B = US2 ∪ US3 ∪ US4 ∪ US5**. Phase A is independently shippable; Phase B adds value on top without regressing Phase A.

### Within Each User Story

- Test tasks (T010, T011, T012, T013, T021, T026, T030, T033) must fail before the implementation task that makes them pass.
- Implementation → CLI wiring (T015 → T016, T017 → T018, T019 → T020): the wiring depends on the underlying module being importable.
- US1's integration test T013 is the acceptance gate for Phase A; it depends on T016, T018, T020 all being green.

### Parallel Opportunities

- All Setup [P] tasks (T003) run in parallel with T001 / T002 (T001 touches different files than T002, but T002 depends on T001's directory existing).
- Foundational [P] tasks T004, T005, T006 run in parallel (different files).
- Within US1, the three unit-test files (T010, T011, T012) are [P] — different files, independent. The corpus-curation T014 is [P] and can run on any developer's machine in parallel with test writing. T013 (integration test skeleton) can also be authored early, but it only passes once T015–T020 are complete.
- US2 and US3 can run in parallel with each other after Foundational is green (different files, different subcommands, no shared state in the DB layer beyond reads).
- Polish tasks T036, T037, T040 are [P] (different files); T038 and T039 are sequential because T038 may uncover issues that T039's audit needs to see.

---

## Parallel Example: Phase 2 Foundational

```bash
# All three [P] foundational tasks run in parallel (different files):
Task: "Write eval/schema.sql with the exact DDL from contracts/schema.md"
Task: "Implement shared types in eval/api.py"
Task: "Write tests/eval/conftest.py with tmp_db and fake_corpus fixtures"

# Then sequentially (each depends on prior work):
Task: "Write tests/eval/test_db.py"        # T007 after T004/T005
Task: "Implement eval/db.py"               # T008 after T007
Task: "Create eval/cli.py skeleton"        # T009 after T008
```

## Parallel Example: User Story 1 tests

```bash
# Once T009 is green, all US1 test files can be written in parallel:
Task: "Write tests/eval/test_scan.py"          # T010
Task: "Write tests/eval/test_human_review.py"  # T011
Task: "Write tests/eval/test_report.py"        # T012

# Meanwhile the corpus can be curated in parallel (data task, no code dep):
Task: "Curate examples/ corpus with 10 CRAN vignettes"  # T014
```

## Parallel Example: Phase B fan-out

```bash
# Once Phase A (T001–T020) is green, US2 and US3 can proceed in parallel:
Developer A:  T021 → T022 → T023 → T024 → T025      # US2: AI review
Developer B:  T026 → T027 → T028 → T029              # US3: corpus fetch
Developer C:  T030 → T031 → T032 → T033 → T034 → T035  # US4 then US5 (share report.py)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only — Phase A)

1. Complete Phase 1 (Setup): T001–T003.
2. Complete Phase 2 (Foundational): T004–T009. **Hard gate — `eval-jss init` must work.**
3. Complete Phase 3 (US1): T010–T020. **Phase A MVP shippable — Step 3 can start.**
4. **STOP and VALIDATE**: run the full quickstart.md Phase A walkthrough on your machine. Label a few violations; read the precision table.

### Incremental Delivery (Phase B)

5. US2 (AI review, T021–T025) or US3 (corpus fetch, T026–T029) — either order, both independent. Ship each when green.
6. US4 (CSV history, T030–T032) — depends on US1's report.py.
7. US5 (per-source, T033–T035) — depends on US1's report.py + US4's CSV writer.
8. Polish (T036–T040) when Phase B is feature-complete.

### Parallel Team Strategy

- One developer takes Phase 1 + Phase 2 + US1 end-to-end (Phase A is a sequential, coherent story).
- Once Phase A is shippable, fan out: one developer on US2, one on US3, one on US4→US5.
- Polish tasks re-converge the team.

---

## Notes

- The harness is at top-level `eval/`, peer to `src/texlint/`. It deliberately does not live inside the linter's source tree, and the wheel stays at `packages = ["src/texlint"]` so downstream users don't receive the harness.
- Tests under `tests/eval/` never `import texlint.*` — the harness exercises `jss-lint` exclusively through its CLI, which keeps the harness honest about what the shipped binary actually emits.
- The `_invoke_linter` seam in `eval/scan.py` is the one place every scan-related test monkeypatches. Do not reach deeper (e.g., `subprocess.run` globally) — that breaks unrelated subprocess calls in the same test run.
- Every task has an exact file path; no vague "update the scan" tasks. If implementation reveals that a path is wrong, fix the path in tasks.md before proceeding.
- Commit after each task or logical group. The Spec-Kit git hooks will auto-commit after phase checkpoints when enabled.
