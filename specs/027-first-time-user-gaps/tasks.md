# Tasks: Release 1.2.0 — first-time-user gaps

**Input**: Design documents from `/specs/027-first-time-user-gaps/`
**Prerequisites**: plan.md (rev 4), spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Unit tests are MANDATORY for any task that creates or edits a file
under `src/texlint/journals/*/rules/` (Constitution §VIII TDD, §IX 100 % branch
coverage) and the test task MUST precede the implementation task it covers.
Any task that changes rule or user-visible engine behaviour MUST have a sibling
task porting the change to the other engine plus parity-suite coverage
(Constitution §XIII). Every task touching `rust/jsslint-core` is followed by a
re-vendor task for the R package.

**Organization**: Phases follow the release's fixed implementation order
(plan §3), not spec.md's priority order:

| Phase | Item | Story | Why here |
|---|---|---|---|
| 2 | **D** — version and rule-set provenance | US6 | B and A stamp/print `ruleset_version`; smallest piece of the chain |
| 3 | **S** — token-specific suggestions | US4 | MUST precede any baseline code; `messages.json` generated exactly once, after S |
| 4 | **B** — baseline mode + Rust inline ignores | US3 | needs D's keys and S's final suggestions |
| 5 | **C** — fix safety | US5 | small, independent |
| 6 | **A-recall** — recall transparency | US1 | needs D's keys, lands on B's footer block |
| 7 | **A-coverage** — guide coverage | US2 | separable, judgement-heavy half of A |
| 8 | **F** — colour | US7 | touches renderer entry points A and B finalise |
| 9 | **E** — Overleaf | US8 | independent, JS + docs only |
| 10 | Release checklist | — | explicit go-ahead required (plan §10) |

**PR discipline**: one PR per item, on short-lived branches off
`027-first-time-user-gaps`. Phase 4 opens with its **own** PR (T045–T057,
Rust inline ignores + the two Python `suppress.py` fixes) carrying its own
CHANGELOG *Fixed* entry, merged before the baseline PR.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1–US8)
- Exact file paths in every description

## Path Conventions

Python reference: `src/texlint/`, `tests/`, `tools/`. Rust workspace:
`rust/jsslint-core/`, `rust/jsslint-cli/`, `rust/jsslint-wasm/`,
`rust/jsslint-py/`. R package: `r/jsslintr/`. Catalogue data:
`specs/003-jss-rule-catalogue/`.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: environment, gates, and the two go/no-go checks the plan names
before any code is written.

- [ ] T001 Materialise the eval corpora (`eval-jss corpus fetch`, `python -m eval.recall_corpus_scaffold`) and record which parity suites would otherwise skip, in `specs/027-first-time-user-gaps/plan.md` under "Deviations" if unavailable
- [x] T002 [P] Point `.specify/feature.json` at `specs/027-first-time-user-gaps` so the spec-kit scripts resolve this feature
- [x] T003 [P] Record the pre-change gate results (pytest, ruff, `cargo test --workspace --locked`) as the baseline for every later comparison
- [x] T004 Verify that `eval-jss iterate refresh` restores precision labels by `(rule, file, line)` and NOT by message text (plan §2 hazard, contracts/suggestions.md C-6); stop and report if it keys on text — item S cannot land otherwise

**Checkpoint**: gates green, corpora present, label-restoration keying confirmed

---

## Phase 2: User Story 6 - Pin versions and read provenance (Priority: P2, item D) 🎯 first in the chain

**Goal**: `ruleset_version` + `ruleset_fingerprint` + `guide_edition` in the
catalogue, a four-line `--version` block in both CLIs, version functions in all
three bindings, and `docs/versions.md`.

**Independent Test**: `version_parity.rs` compares lines 1, 3, 4 across engines;
the fingerprint guard fails when a catalogue field or a fixture message changes
without a `ruleset_version` bump.

### Catalogue data and generators

- [x] T005 [US6] Add `ruleset_version`, `ruleset_fingerprint`, `guide_edition` to `specs/003-jss-rule-catalogue/catalogue.yaml` (values stamped by T009, not hand-written beyond placeholders)
- [x] T006 [US6] Extend `REQUIRED_TOP_KEYS` and the shape checks in `tools/_catalogue_validate.py` for the three new keys
- [x] T007 [P] [US6] Update `specs/003-jss-rule-catalogue/contracts/catalogue-schema.md` with the three new top-level keys
- [x] T008 [US6] Implement `tools/generate_message_snapshot.py [--check]` writing `specs/003-jss-rule-catalogue/messages.json` from `tests/fixtures/violations/**/*-bad.*` plus the `JSS-PROJECT-001/002` resolver fixtures (data-model §4.4) — **do not run it for real until after item S (T044)**
- [x] T009 [US6] Implement fingerprint computation and `--stamp-fingerprint --ruleset-version YYYY-MM-DD` / `--check` in `tools/generate_catalogue_data.py`: canonical JSON of active-rule contract fields + `messages.json`, single-line regex rewrite of the two keys, refusal when the fingerprint changed but the date did not
- [x] T010 [US6] Emit `RULESET_VERSION`, `RULESET_FINGERPRINT`, `GUIDE_SOURCE` from `tools/generate_catalogue_data.py` into `src/texlint/journals/jss/_catalogue_data.py`
- [x] T011 [US6] Print the rule-set header lines in `tools/render_catalogue.py` and re-render `specs/003-jss-rule-catalogue/catalogue.md`

### Version block, both engines

- [x] T012 [P] [US6] Failing unit test for `texlint.version.format_version_block` in `tests/unit/test_version_block.py` (four lines, `rule set: n/a`, `journal: x (not registered)`)
- [x] T013 [US6] Implement `src/texlint/version.py::format_version_block(tool, engine, rule_set, journal)` (pure, core-owned per contracts/version-output.md C-3)
- [x] T014 [US6] Replace `click.version_option` in `src/texlint/cli.py` with a plain `--version` flag handled in `main()` after the subcommand early-return, after `load_config`, before the "at least one FILE" check
- [x] T015 [US6] Mirror the formatter in `rust/jsslint-core/src/version.rs` (+ `lib.rs` export) with unit tests
- [x] T016 [US6] Replace clap's `version` in `rust/jsslint-cli/src/main.rs` with `#[arg(long)] version: bool` resolved after config load and journal resolution
- [x] T017 [US6] Read `RULESET_VERSION`/`RULESET_FINGERPRINT`/`GUIDE_SOURCE` in `rust/jsslint-core/build.rs` + `catalogue.rs` accessors (embed the stored fingerprint string; never recompute)

### Bindings

- [x] T018 [P] [US6] `version()` export in `rust/jsslint-wasm/src/lib.rs` returning `{tool, engine, rulesetVersion, guideSource}`
- [x] T019 [P] [US6] `version()` + `__version__` in `rust/jsslint-py/src/lib.rs`
- [x] T020 [P] [US6] `jsslint_version()` in `r/jsslintr/R/` + `r/jsslintr/src/rust/src/lib.rs`, adding the DESCRIPTION `package` field; document in `r/jsslintr/man/`
- [x] T021 [US6] Run `bash r/jsslintr/tools/vendor-jsslint-core.sh` and commit the vendored result

### Tests and docs

- [x] T022 [P] [US6] `tests/unit/journals/jss/test_ruleset_version.py`: stored == computed fingerprint; date valid, ≤ today, ≥ `source_vendored_at`
- [x] T023 [P] [US6] `tests/unit/tools/test_message_snapshot_fresh.py`: `generate_message_snapshot.py --check` is clean
- [x] T024 [P] [US6] `--version` cases in `tests/integration/test_cli_subcommands.py` (default, `--journal jss`, stub journal, unregistered journal)
- [x] T025 [US6] New `rust/jsslint-cli/tests/version_parity.rs` comparing lines 1, 3, 4 (mask line 2) for default, `--journal jss`, and a scratch TOML with `journal = "nope"`
- [x] T026 [P] [US6] Compare `jsslint.version()["rulesetVersion"]` with `texlint`'s value in `tests/unit/test_jsslint_parity.py`
- [x] T027 [P] [US6] Write `docs/versions.md` (channel table, mapping, compatibility policy D4, pin advice, the `--update-baseline` statement) and add the two-sentence policy to the `CHANGELOG.md` header
- [x] T028 [P] [US6] Update `specs/027-first-time-user-gaps/contracts/cli.md` cross-references if the implementation deviates; record any deviation in plan.md

**Checkpoint**: `--version` identical modulo line 2; fingerprint `--check` green; item D PR ready

---

## Phase 3: User Story 4 - Baseline entries stay specific under revision (Priority: P1, item S)

**Goal**: ten rules gain a stable identifier in their suggestion, byte-identical
in both engines, before any baseline exists.

**Independent Test**: suggestion strings differ per occurrence for the ten rules;
100 % branch coverage on every touched module; `tex_rules_parity.rs` /
`bib_rules_parity.rs` byte-identical.

**⚠️ Constitution §VIII**: every `[TEST]` task below is committed FAILING before
its implementation task.

### Shared helper

- [x] T029 [US4] Failing unit tests for the normalisation helper (collapse whitespace, trim, truncate after collapsing, no ellipsis, empty → generic fallback) in `tests/unit/journals/jss/rules/test_helpers.py`
- [x] T030 [US4] Implement the normalisation helper beside the existing suggestion helpers in `src/texlint/journals/jss/rules/_helpers.py` (contracts/suggestions.md C-3)
- [x] T031 [US4] Mirror the helper in `rust/jsslint-core/src/rules/` with unit tests

### Per-rule (test first, then Python, then Rust) — ten rules

- [x] T032 [US4] `JSS-CODE-003` (±8 chars around the matched operator/comma): failing test → `src/texlint/journals/jss/rules/code_style.py` → `rust/jsslint-core/src/rules/`
- [x] T033 [US4] `JSS-OPER-003` (equation `\label`, else first 40 chars of the first body line): failing test → `src/texlint/journals/jss/rules/operators.py` → Rust
- [x] T034 [US4] `JSS-XREF-004` (same identifier rule as OPER-003): failing test → `src/texlint/journals/jss/rules/crossrefs.py` → Rust
- [x] T035 [US4] `JSS-TYPO-001` (first 40 chars of the caption): failing test → `src/texlint/journals/jss/rules/typography.py` → Rust
- [x] T036 [US4] `JSS-REFS-004` (BibTeX entry key): failing test → `src/texlint/journals/jss/rules/references.py` → Rust
- [x] T037 [US4] `JSS-REFS-007` (BibTeX entry key): failing test → `src/texlint/journals/jss/rules/references.py` → Rust
- [x] T038 [US4] `JSS-CAP-002` (section title ≤ 60 chars, plain form when `[plain]` given): failing test → `src/texlint/journals/jss/rules/capitalization.py` → Rust
- [x] T039 [US4] `JSS-CODE-001` (first 40 chars of the comment): failing test → `src/texlint/journals/jss/rules/code_style.py` → Rust
- [x] T040 [US4] `JSS-XREF-002` (referenced label): failing test → `src/texlint/journals/jss/rules/crossrefs.py` → Rust
- [x] T041 [US4] `JSS-CITE-003` (cite key(s) of the matched `\cite…`): failing test → `src/texlint/journals/jss/rules/citations.py` → Rust

### Fixtures, goldens, gates

- [x] T042 [US4] Update the expectations in `tests/fixtures/violations/` for the ten rules and re-run `tex_rules_parity.rs`, `bib_rules_parity.rs`, `engine_parity.rs`
- [x] T043 [US4] Regenerate the SARIF goldens once (`JSSLINT_REGEN_GOLDENS=1 python -m pytest tests/integration/test_cli_sarif_goldens.py`) and review the diff for message-text changes only
- [x] T044 [US4] Generate `specs/003-jss-rule-catalogue/messages.json` for real (T008) and stamp the new `ruleset_version` + fingerprint (T009); confirm `--check` is clean and re-run `bash r/jsslintr/tools/vendor-jsslint-core.sh`
- [x] T045 [US4] Confirm the §IX gate: `python -m pytest tests/unit/journals/jss/ --cov=src/texlint/journals/jss/rules --cov-branch --cov-fail-under=100`

**Checkpoint**: ten rules token-specific in both engines; `messages.json` exists and is generated exactly once; item S PR ready

---

## Phase 4: User Story 3 - Adopt the tool on an existing manuscript (Priority: P1, item B)

**Goal**: `--baseline` / `--update-baseline` in both CLIs on one shared
suppression hook, plus the Rust inline-ignore port.

**Independent Test**: `--update-baseline` bytes identical across engines; the
jss5342 replay reports the recorded matched/stale/new counts.

### PR 1 — inline ignores in the Rust engine + Python suppress fixes (own CHANGELOG *Fixed* entry)

- [x] T046 [US3] Failing cases in `tests/unit/core/test_suppress.py`: `.Rmd` prose block not starting at line 1, `.Rnw`, form feed / `\v` / `\x85` in `directive_lines`
- [x] T047 [US3] Add `line_offset: int = 0` to `ParsedTexFile` in `src/texlint/api.py` and set it from `prose.line - 1` in `src/texlint/core/rmd_parser.py`
- [x] T048 [US3] Add `line_offset` in `build_index` and switch `directive_lines` to `source.split("\n")` in `src/texlint/core/suppress.py`
- [x] T049 [US3] Introduce `Suppressor` in `src/texlint/api.py` and the `suppress=` keyword on `run()` in `src/texlint/core/engine.py`, ordering sort → inline-drop → `suppress(v)` → severity remap → bookkeeping; parse errors bypass
- [x] T050 [US3] Port the suppression scanner to `rust/jsslint-core/src/suppress.rs` (no-lookbehind regex, id pattern, index over `all_tex_like_docs()` with `parsed.source` + `line_offset`, bib sources) with unit tests
- [x] T051 [US3] Add `pub trait Suppressor` + `engine::run_with(...)` in `rust/jsslint-core/src/engine.rs`, delegate `run`/`run_with_project`, apply inside `run_one` before the severity remap, and delete the "not implemented" note
- [x] T052 [US3] Add the suppression fixtures `tests/fixtures/suppress/{inline.tex,scoped.tex,verbatim.tex,escaped.tex,entries.bib,chunks.Rnw,prose.Rmd}`
- [x] T053 [US3] New `rust/jsslint-core/tests/suppress_parity.rs` over those fixtures
- [x] T054 [P] [US3] Inline-ignore case in `rust/jsslint-wasm/tests/wasm_parity.rs`
- [x] T055 [US3] Run `bash r/jsslintr/tools/vendor-jsslint-core.sh`; commit
- [x] T056 [P] [US3] CHANGELOG *Fixed* entry naming the Rust/WASM/VS Code/PyO3/R inline-ignore fix and the two Python suppress fixes
- [x] T057 [US3] Merge PR 1 before any baseline code lands

### PR 2 — baseline core (pure, both engines)

- [x] T058 [P] [US3] Unit tests for `src/texlint/core/baseline.py`: parse/build/dumps round-trip, sorted output, `schema_version` and journal mismatch, `path_map` miss, multiset consumption in sort order, stale vs unevaluated
- [x] T059 [US3] Implement `src/texlint/core/baseline.py` (`BaselineDocument`, `BaselineEntry`, `BaselineSummary`, `BaselineError`, `parse`, `build`, `dumps`, `BaselineMatcher`) per data-model §2
- [x] T060 [US3] Mirror in `rust/jsslint-core/src/baseline.rs`, serialising through `json_output::write_value` for byte equality
- [x] T061 [US3] Add `ComplianceReport.baseline` in `src/texlint/api.py` and `rust/jsslint-core/src/report.rs` (update the literals at `engine.rs` and `rust/jsslint-core/tests/parity.rs`)

### PR 2 — CLI layer

- [x] T062 [US3] `ToolConfig.baseline` + `KNOWN_FIELDS` in `src/texlint/config.py`; `RawOverrides.baseline` in `rust/jsslint-core/src/config.rs` and the four struct-literal sites (`rust/jsslint-cli/src/main.rs`, `rust/jsslint-wasm/src/lib.rs`, `rust/jsslint-py/src/lib.rs`, `r/jsslintr/src/rust/src/lib.rs`)
- [x] T063 [US3] `--baseline` / `--update-baseline` flags, path relativisation, and the run flow in `src/texlint/cli.py` (read → parse → `path_map` → `run(suppress=matcher)` → `replace(report, baseline=summary)`)
- [x] T064 [US3] Same flags and flow in `rust/jsslint-cli/src/main.rs`, canonicalising as `resolver.rs` does and stripping `\\?\`
- [x] T065 [US3] `--update-baseline` write path: tempfile + `os.replace`, stderr receipt, exit 0 (2 on error-severity parse failure), no report rendered — both CLIs
- [x] T066 [US3] Terminal summary line (both engines, after the footer) incl. the rule-set-date mismatch clause
- [x] T067 [US3] Always-present JSON `baseline` key in `src/texlint/output/json_output.py` and `rust/jsslint-core/src/json_output.rs`; update the exact key-set assertion in `tests/integration/test_cli_json.py`
- [x] T068 [US3] HTML `<p class="note">` in `src/texlint/output/html_output.py` (+ template) and `rust/jsslint-core/src/html_output.rs`
- [x] T069 [US3] Run `bash r/jsslintr/tools/vendor-jsslint-core.sh`; commit

### PR 2 — tests, action, docs

- [x] T070 [P] [US3] `tests/integration/test_cli_baseline.py`: create → hide → exit 0; new `(rule, message, suggestion)` → exit 1; TOML key; subdirectory `../` paths; `--no-resolve` vs auto-resolve equivalence; summary in terminal/json/html; `--fix` skips baselined; journal mismatch exit 2
- [x] T071 [US3] New `rust/jsslint-cli/tests/baseline_parity.rs` (identical `--update-baseline` bytes; identical stdout/exit for terminal/json/sarif; drift; TOML; subdirectory; journal mismatch)
- [x] T072 [US3] `tests/integration/test_baseline_replay.py` replaying `examples/jss5342-versions` initial → resubmission: distinct keys ≥ 75, re-keyed persisting findings ≤ 4 (plan §5.5, research.md §3/§5)
- [x] T073 [P] [US3] `baseline` input in `action/action.yml` forwarded as `--baseline`; assert it in `tests/integration/test_action_manifest.py`
- [x] T074 [P] [US3] `docs/baseline.md` (adoption recipe, documented limits C-8) and the bindings/divergence notes in `rust/README.md`
- [x] T075 [P] [US3] CHANGELOG entries for the baseline feature and the JSON addition

**Checkpoint**: adoption workflow works end to end; both PRs merged; parity suites green

---

## Phase 5: User Story 5 - Preview and apply fixes with a receipt (Priority: P2, item C)

**Goal**: one summary line per fix pass in both engines; documented VCS expectation.

**Independent Test**: `fix_parity.rs` asserts the line for write, dry-run, and interactive modes.

- [x] T076 [P] [US5] Failing assertions for the summary line in `tests/integration/test_cli_fix_apply.py`
- [x] T077 [US5] Emit the summary line at the end of `apply_fixes` in `src/texlint/core/fixer.py` (stdout, before the report render)
- [x] T078 [US5] Mirror it in `rust/jsslint-core/src/fixer.rs` / `rust/jsslint-cli/src/main.rs`
- [x] T079 [US5] Extend `rust/jsslint-cli/tests/fix_parity.rs` to cover write, dry-run, and interactive modes
- [x] T080 [P] [US5] "Before `--fix`" sections in `README.md`, `rust/README.md`, and the R vignette under `r/jsslintr/vignettes/`
- [x] T081 [US5] Run `bash r/jsslintr/tools/vendor-jsslint-core.sh`; commit

**Checkpoint**: fix receipt visible in both CLIs

---

## Phase 6: User Story 1 - A clean run is honest about what it proves (Priority: P1, item A-recall)

**Goal**: shipped recall snapshot, CI gate at floor 0.78, recall on the report,
reviewer column, author footer, JSON/SARIF/`explain` surfaces.

**Independent Test**: author mode on a compliant fixture is non-empty; reviewer
mode shows the `Recall` column; `project` renders `unmeasured`.

### Snapshot and gate

- [x] T082 [US1] Implement `tools/generate_recall_snapshot.py --run-timestamp TS [--check]` writing `specs/003-jss-rule-catalogue/recall.json` from `recall_history`, filtered to active rules (data-model §4.2)
- [x] T083 [P] [US1] `tests/unit/eval/test_recall_snapshot_fresh.py` freshness test
- [x] T084 [US1] Read `run_timestamp` and sum `tp`/`fn` from the snapshot in `eval/badge.py`; remove the drifted constant
- [x] T085 [US1] Replace the hard-coded aggregate floor in `eval/cli.py` with `RECALL_FLOOR = 0.78`, update the help text, and add the `RECALL_FLOOR ≥ snapshot − 0.03` assertion to `tests/unit/eval/test_recall_cli.py`
- [x] T086 [US1] Add `eval-jss recall --gate --no-record` to the `parity` job in `.github/workflows/ci.yml` right after the corpus is materialised

### Model and codegen

- [x] T087 [P] [US1] Failing unit tests for `RecallStat` boundaries (n = 0, 1, 9, 10; half-up 78.5 → 79; 1587/1967 → 81) in `tests/unit/test_api.py`
- [x] T088 [US1] Add `RecallStat`, `RecallRun`, `RuleSetInfo`, `JournalMetadata`, and the non-abstract `JournalRuleModule.metadata()` default to `src/texlint/api.py`
- [x] T089 [US1] Implement `JSSJournal.metadata()` in `src/texlint/journals/jss/__init__.py` reading `_catalogue_data`
- [x] T090 [US1] Stamp `CategorySummary.recall`, `ComplianceReport.rule_set` in `src/texlint/core/engine.py`
- [x] T091 [US1] Emit `RECALL_RUN` and `RECALL` from `tools/generate_catalogue_data.py`; extend `rust/jsslint-core/build.rs` (`rerun-if-changed`) and `catalogue.rs` accessors
- [x] T092 [US1] Mirror the structs and the stamping in `rust/jsslint-core/src/report.rs` and `engine.rs` with matching integer arithmetic

### Surfaces

- [x] T093 [US1] Reviewer `Recall` column + `Measured recall:` line in `src/texlint/output/terminal.py` and `rust/jsslint-core/src/terminal.rs`
- [x] T094 [US1] Author footer (always printed, stdout, also on a clean run) in both engines; update `tests/integration/test_cli_author_terminal.py`
- [x] T095 [US1] Per-category `recall` and top-level `rule_set` in `src/texlint/output/json_output.py` + `rust/jsslint-core/src/json_output.rs`; update `tests/integration/test_cli_json.py`
- [x] T096 [US1] `properties.confidence` + `properties.recall` on SARIF rule descriptors in `src/texlint/output/sarif.py` and `rust/jsslint-core/src/sarif.rs`
- [x] T097 [US1] HTML author note and reviewer `<th>Recall</th>` in `src/texlint/output/html_output.py` (+ `author.html.j2`) and `rust/jsslint-core/src/html_output.rs`
- [x] T098 [US1] `Recall:` line in `src/texlint/explain.py` and `rust/jsslint-core/src/explain.rs`
- [x] T099 [US1] `Confidence` and `Recall` columns + rule-set header in `tools/render_catalogue.py`; re-render `catalogue.md`
- [x] T100 [US1] Vendor `recall.json` (`r/jsslintr/tools/vendor-jsslint-core.sh`, `_FILES` in `tests/unit/test_vendored_catalogue_in_sync.py`) and re-vendor

### Tests and docs

- [x] T101 [P] [US1] Engine-level tests: pooled category recall, stub journal → `None`/`unmeasured` (`tests/unit/test_engine.py`, `tests/integration/test_plugin_discovery.py`)
- [x] T102 [P] [US1] Extend `rust/jsslint-core/tests/terminal_parity.rs`, `sarif_parity.rs`, `rust/jsslint-cli/tests/html_parity.rs`, `explain_parity.rs`, `cli_parity.rs` for the new surfaces
- [x] T103 [P] [US1] `docs/recall-and-coverage.md` (how recall is measured, the source-only lower-bound caveat, the three states)
- [x] T104 [P] [US1] Update `specs/027-first-time-user-gaps/contracts/json-output-1.2.md` cross-refs and rewrite the stale `specs/001-linter-foundation/contracts/json-output.md`

**Checkpoint**: a clean run is no longer silent; recall visible in every format

---

## Phase 7: User Story 2 - The author learns what is not checked (Priority: P1, item A-coverage)

**Goal**: validated `guide-coverage.yaml`, the reviewer "Not checked" block, the
JSON `coverage` object, and the `coverage` subcommand.

**Independent Test**: the contract test fails on a retired rule or an unclaimed
active rule; `coverage` renders identically in both engines.

- [x] T105 [US2] Script the migration of the 146 checklist rows (`specs/003-jss-rule-catalogue/checklists/rule-catalogue-review.md` §1.1–1.4) into `specs/003-jss-rule-catalogue/guide-coverage.yaml`, including the `sources:` block
- [x] T106 [US2] Write directives for the 15 unclaimed active rules (`BIBTEX-003/004/005`, `OPER-004`, `PROJECT-001/002`, `REFS-001/003/005/006/007`, `XREF-004/005/006/007`) by reading the guide sections they cite
- [x] T107 [US2] Re-judge the 7 rows crediting retired rules and every `partial` row; add the "YAML is authoritative" note to the checklist
- [x] T108 [US2] Implement `tools/_coverage_validate.py` (contracts/coverage-file.md C-3) and the contract test in `tests/unit/journals/jss/test_guide_coverage.py`
- [x] T109 [US2] Emit `COVERAGE` from `tools/generate_catalogue_data.py`; parse it in `rust/jsslint-core/build.rs` + `catalogue.rs`
- [x] T110 [US2] Add `CoverageDirective` and `ComplianceReport.coverage` in `src/texlint/api.py` / `rust/jsslint-core/src/report.rs`; fill in both engines
- [x] T111 [US2] Reviewer "Not checked by jss-lint" block in `src/texlint/output/terminal.py` and `rust/jsslint-core/src/terminal.rs`
- [x] T112 [US2] `coverage` block in JSON (both engines) and `<table class="coverage">` in HTML (both engines)
- [x] T113 [US2] Implement the renderers in `src/texlint/coverage.py` and `rust/jsslint-core/src/coverage.rs` (terminal, markdown, json)
- [x] T114 [US2] Wire the `coverage` subcommand into `src/texlint/cli.py` (`REGISTERED_SUBCOMMANDS`) and `rust/jsslint-cli/src/main.rs`
- [x] T115 [US2] `Covers: …` line in `explain` (both engines)
- [x] T116 [US2] Author-footer coverage pointer sentence (both engines)
- [x] T117 [US2] `Coverage` section in `tools/render_catalogue.py`; re-render `catalogue.md`
- [x] T118 [US2] Vendor `guide-coverage.yaml` (`vendor-jsslint-core.sh`, `_FILES`, `build.rs` rerun-if-changed) and add `rust/jsslint-core/tests/package_contents.rs` asserting `cargo package --list` ships all five catalogue files
- [x] T119 [P] [US2] New `rust/jsslint-cli/tests/coverage_parity.rs` for all three formats plus the stub-journal case
- [x] T120 [P] [US2] Integration tests for the three `coverage` formats and the reviewer block in `tests/integration/test_cli_subcommands.py` / `test_cli_reviewer_terminal.py`
- [x] T121 [P] [US2] Extend `docs/recall-and-coverage.md` with how to read the coverage matrix
- [x] T122 [US2] Run `bash r/jsslintr/tools/vendor-jsslint-core.sh`; commit

**Checkpoint**: Phases 1 and 2 of the release are green — Phase 3 may start

---

## Phase 8: User Story 7 - Scan a long run by colour (Priority: P3, item F)

**Goal**: 16-colour terminal output in both CLIs behind one shared decision function.

**Independent Test**: `strip_sgr(coloured) == plain` in both engines; the
decision matrix agrees across engines.

- [x] T123 [P] [US7] Failing unit tests for the decision function matrix (flag × `NO_COLOR` × `CLICOLOR_FORCE` × TOML × isatty) in `tests/unit/test_config.py`
- [x] T124 [US7] `ToolConfig.color` + TOML key in `src/texlint/config.py`; `ColorChoice` in `rust/jsslint-core/src/config.rs` and the four `RawOverrides` literals
- [x] T125 [US7] Implement the decision function in `src/texlint/cli.py` and `rust/jsslint-cli/src/main.rs` with `--color auto|always|never`
- [x] T126 [US7] `color: bool` in `_console()` in `src/texlint/output/terminal.py` (`force_terminal`, `color_system="standard"`, `no_color`, `width=120`)
- [x] T127 [US7] SGR at render time in `rust/jsslint-core/src/terminal.rs` (measure unstyled text) and `anstream::AutoStream::new(stdout, choice)` in `rust/jsslint-cli` only
- [x] T128 [P] [US7] `strip_sgr(render(color=True)) == render(color=False)` unit tests in both engines on author, reviewer, and skipped-rules fixtures
- [x] T129 [US7] `--color always` cases in `rust/jsslint-core/tests/terminal_parity.rs` with both sides SGR-stripped
- [x] T130 [US7] New `rust/jsslint-cli/tests/color_parity.rs` checking the decision only (env matrix, TOML, `--output json --color always`)
- [x] T131 [P] [US7] Document the coloured-bytes §XIII divergence in `rust/README.md` and the flag in `README.md`
- [x] T132 [US7] Run `bash r/jsslintr/tools/vendor-jsslint-core.sh`; commit

**Checkpoint**: colour on in a TTY, never in a pipe, never in JSON/SARIF/HTML

---

## Phase 9: User Story 8 - Check an Overleaf project (Priority: P3, item E)

**Goal**: documented Overleaf workflows and a browser zip drop.

**Independent Test**: a zip of `docs/jss-template/` dropped on the app produces
the same HTML report as the folder picker.

- [ ] T133 [P] [US8] Write `docs/overleaf.md` (zip drop, CLI unzip, GitHub Sync + Action with a baseline, re-upload after `--fix`)
- [ ] T134 [US8] Zip reader (EOCD → central directory → local headers; stored + `DecompressionStream("deflate-raw")`) in `web/app.js`, skipping `__MACOSX/`, `._*`, and non-lintable suffixes
- [ ] T135 [US8] Drag-and-drop zone and `.zip` in the file input in `web/index.html` + `web/app.js`, with the unsupported-browser fallback message
- [ ] T136 [P] [US8] Link `docs/overleaf.md` from `README.md` and the `web/index.html` footer

**Checkpoint**: all eight items implemented

---

## Phase 10: Polish, Cross-Cutting, and the Release Checklist (explicit go-ahead required)

- [ ] T137 [P] Add the `web/pkg/*.wasm` size line to the job summary in `.github/workflows/publish-web.yml` and `ci.yml`, plus a 2.2 MB soft gate in `rust/jsslint-wasm/tests/`
- [ ] T138 [P] Record every §XIII divergence of plan §10 in `rust/README.md`
- [ ] T139 [P] Record the item-S tail, CLI zip, bindings baseline, SARIF `baselineState`, Action `comment-mode`, Windows colour CI, and second-annotator corpus in `roadmap/follow-ups.md`
- [ ] T140 Write `docs/releasing.md` with the plan §10 checklist
- [ ] T141 Run the full gate set: `python -m pytest tests/ -q`, `ruff check .`, the §IX coverage gate, `cargo test --workspace --locked`, `eval-jss recall --gate --no-record`
- [ ] T142 **[RELEASE — needs explicit go-ahead]** fresh recorded `eval-jss recall` run → `generate_recall_snapshot.py` → badge JSON → ratchet `RECALL_FLOOR` to `floor(snapshot − 0.03, 2 dp)`
- [ ] T143 **[RELEASE — needs explicit go-ahead]** `generate_message_snapshot.py --check`, `generate_catalogue_data.py --check`, CHANGELOG, `VERSION` + `python scripts/set_version.py`, tag-guard step in every `release-*.yml`, CTAN bundle, CRAN `1.2.0-1`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: no dependencies; T004 is a go/no-go for Phase 3
- **Phase 2 (US6, item D)**: blocks Phases 3–7 (they stamp or print `ruleset_version`)
- **Phase 3 (US4, item S)**: MUST complete before Phase 4 — `suggestion` is a baseline key; `messages.json` is generated exactly once, in T044, after S
- **Phase 4 (US3, item B)**: PR 1 (T046–T057) MUST merge before PR 2 (T058–T075)
- **Phase 5 (US5, item C)**: independent; scheduled after Phase 4 per plan §3
- **Phase 6 (US1, A-recall)**: depends on Phase 2 (catalogue keys) and lands on Phase 4's footer block
- **Phase 7 (US2, A-coverage)**: depends on Phase 6's metadata plumbing
- **Phases 8–9 (US7, US8)**: MUST NOT start before Phases 2–7 are green (plan: "do not start Phase 3 before Phases 1 and 2")
- **Phase 10**: T142–T143 need an explicit go-ahead

### Within Each Story

- Rule-module tasks: failing test → Python reference → Rust port → parity
- Any `rust/jsslint-core` change → `vendor-jsslint-core.sh` → commit
- Config-field additions → all four `RawOverrides` struct literals in the same commit

### Parallel Opportunities

- T018–T020 (bindings) after T015/T017
- T022–T027 (item D tests and docs) once the implementation is in
- T032–T041 are one-rule-each and touch different modules, except T032/T039 (`code_style.py`) and T034/T040 (`crossrefs.py`) and T036/T037 (`references.py`), which are sequential pairs
- T070/T073/T074/T075 after the CLI layer
- T101–T104, T119–T121, T128/T131, T133/T136 within their phases

---

## Implementation Strategy

1. **Phase 1** — gates and the two go/no-go checks.
2. **Phase 2 (D)** — provenance first: everything downstream stamps it.
3. **Phase 3 (S)** — sharpen suggestions while no baseline exists anywhere.
4. **Phase 4 (B)** — inline-ignore parity fix, then the baseline.
5. **Phase 5 (C)** — the fix receipt.
6. **Phases 6–7 (A)** — recall, then coverage; the release's reason to exist.
7. **Phases 8–9 (F, E)** — polish, only once 1–7 are green.
8. **Phase 10** — release checklist, on an explicit go-ahead only.

Scope lever if the release must shorten (plan §3): drop Phase 7 (A-coverage,
5 d), then Phases 8–9 (3 d). Phases 2–4 are one dependency chain and cannot be
separated.
