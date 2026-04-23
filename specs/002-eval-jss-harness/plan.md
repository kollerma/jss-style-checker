# Implementation Plan: `eval-jss` — Precision Harness for the JSS Linter

**Branch**: `002-eval-jss-harness` | **Date**: 2026-04-23 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-eval-jss-harness/spec.md`

## Summary

Build `eval-jss`: a companion CLI that shells out to the `jss-lint` binary produced in Step 1, persists every violation the linter reports against a corpus of real JSS manuscripts into a SQLite audit trail, lets an operator label each violation as a true or false positive, and computes a per-rule precision number. The harness enforces Constitution §VI (≥90% precision per rule) empirically, and Constitution §XII (reproducible corpus) via a pinned `eval/corpus-manifest.csv` with per-file SHA256s.

Per the spec's 2026-04-23 Clarifications, both phases land in this spec: a **Phase A (MVP)** — `init`, `scan`, `human-review`, `report` over a 10-paper hand-curated corpus under `examples/` — is independently shippable and unblocks Step 3; a **Phase B (full scope)** — AI-assisted `review` behind a mockable client, `corpus fetch` materialising a pinned manifest from immutable distribution URLs, CSV precision history, per-source precision breakdown — layers on top without regressing Phase A.

**Spec drift reconciled.** The `/speckit.plan` command input described the AI backend as an `OllamaClient` calling Ollama's `POST /api/generate` with `model="qwen3:7b"` at `http://localhost:11434`. The spec's 2026-04-23 Clarifications session replaced that with `llama.cpp`'s `llama-server` hosting `unsloth/Qwen3-30B-A3B-GGUF:UD-Q4_K_XL` on the **OpenAI-compatible** `POST /v1/chat/completions` endpoint at `http://localhost:8080`, with greedy decoding (`top-k=1`, `temp=0.1`). This plan honours the spec. The production `ReviewClient` is therefore `LlamaServerClient`, not `OllamaClient`. Greedy decoding is the reproducibility contract — same prompt, same label, every host.

Two additional small reconciliations, both in favour of the spec:

1. The `/speckit.plan` input's skip-list example cites `rule_id == "JSS-CODE-003"`. No such rule ships in Step 1 (only `JSS-CITE-001`, `JSS-BIB-001`, `JSS-SRC-001` exist). The skip-list is therefore implemented as data (FR-018 — "MUST be data-driven, not hard-coded") with an empty default and a configuration file (`eval/review-skip-list.toml`) that Step 3 can populate as rules land with documented AI blind spots. The `\code{}`-with-`=` example remains in the configuration file as a comment documenting the first rule that will land on the skip-list.

2. The `/speckit.plan` input's scan example passes `*files` in a single `subprocess.run` invocation. Spec FR-009 says `jss-lint` is invoked "on each paper" — one invocation per paper, with both that paper's `.tex` and `.bib` files in the argv (`[jss_lint, "--output", "json", "--", paper/article.tex, paper/refs.bib]`). This preserves per-paper accounting in the `runs` audit log and matches spec FR-010's dedup key of `(paper_id, rule_id, line, message)`.

## Technical Context

**Language/Version**: Python ≥3.10, matching Step 1's `pyproject.toml` (tested on 3.10, 3.11, 3.12)
**Primary Dependencies**: Standard library only — `sqlite3`, `subprocess`, `shutil`, `hashlib`, `tarfile`, `zipfile`, `csv`, `json`, `urllib.request`, `os`, `pathlib` — plus the two packages the linter already depends on: `click>=8.1` and `rich>=13.0`. **No new runtime dependencies** (spec FR-003).
**Storage**: Single SQLite database at `eval/eval.db`. WAL journal mode, `foreign_keys=ON`, `synchronous=NORMAL`. Gitignored for the live corpus; integration-test DBs land in per-test `tmp_path` directories.
**Testing**: `pytest` (already in the dev extras). Fixtures in `tests/eval/conftest.py`: `tmp_db` (empty schema), `fake_corpus` (three tex files + sibling `.bib` + pinned manifest under `tmp_path`), `fake_client` (`ReviewClient` protocol implementation with per-rule-id canned verdicts). The `jss-lint` subprocess is mocked at the `eval.scan._invoke_linter` seam so tests don't need the real binary on PATH.
**Target Platform**: POSIX (Linux / macOS) primarily. Windows works for Phase A (SQLite + subprocess are portable); Phase B's `corpus fetch` has only been exercised on POSIX (tarball extraction paths). The spec does not claim Windows support; if it becomes relevant we will address it in a follow-up.
**Project Type**: Top-level `eval/` package + second console script (`eval-jss = eval.cli:main`), peer to the existing `jss-lint` entry point. The package is **explicitly excluded** from the wheel (`pyproject.toml`'s `tool.hatch.build.targets.wheel.packages` stays at `["src/texlint"]`) so downstream users who `pip install jss-style-checker` do not receive the evaluation harness.
**Performance Goals**: Full MVP pipeline on the 3-paper fake-corpus integration test completes in under 10 seconds on ordinary developer hardware (spec SC-005). Scan of the 10-paper MVP corpus completes in under 30 seconds end-to-end excluding human review (scan is bounded by `jss-lint` throughput, not by the harness).
**Constraints**: No new runtime dependencies; greedy-decoded LLM for AI review reproducibility; corpus reproducibility via SHA256 verification against a pinned manifest; deterministic scan dedup so re-scans never create phantom rows; scan must never crash on a parse failure (FR-011).
**Scale/Scope**: Two-phase implementation inside one spec. Phase A touches ~5 modules (`cli.py`, `db.py`, `scan.py`, `human_review.py`, `report.py`) plus a 10-paper corpus under `examples/` and ~6 unit-test files plus 1 integration test. Phase B adds 2 modules (`review.py`, `corpus.py`) plus the manifest and the skip-list config, and ~3 additional test files. Target violation volume once the rule catalogue lands: a few hundred per corpus pass.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Standing gates derived from `.specify/memory/constitution.md` v1.0.0. For this spec the two principles that were "deferred to Step 5" on spec 001 (§VI precision gate, §XII reproducible corpus) become **in-scope deliverables**, not deferrals.

- [x] **§I Determinism**: The harness introduces no code path inside a rule `check` callable — it is a consumer of rule output, not a producer. AI is used only for *rule review*, which §I explicitly permits. Determinism of the review loop is preserved by pinning greedy decoding (`top-k=1`) on the `llama-server` side and by running the model locally so there is no version drift from a managed service. **PASS.**
- [x] **§II AST-First**: No rules change. **N/A.**
- [x] **§III Non-Fatal Parse**: The harness never crashes on a parse failure — `jss-lint`'s synthetic `JSS-PARSE-000` violation is persisted just like any rule-produced violation (spec FR-011), and the downstream `report` surfaces it in a dedicated row outside the per-rule precision numerator (spec FR-021). **PASS** (downstream consumer of §III).
- [x] **§IV Zero Core Edits for Journals**: No journal changes. The harness does not import from `src/texlint/`; it shells out to `jss-lint --output json`. **N/A / PASS by construction.**
- [x] **§V Authority Cited**: No rules added. **N/A.**
- [x] **§VI ≥90% Precision Gate**: **This spec implements the enforcement mechanism.** `eval-jss report` computes per-rule precision as `TP / (TP + FP)` over labelled verdicts and visually flags rules below 90% (spec FR-019, FR-020). Step 3's quality gate becomes a `git diff` against `eval/report.csv`. **PASS by design.**
- [x] **§VII Safe Auto-Fix**: No fixes designed here. **N/A.**
- [x] **§VIII TDD**: `tasks.md` (produced by `/speckit.tasks`) will order the per-module test task before the per-module implementation task. Integration test for the full `init → scan → human-review → report` pipeline lands before the implementations are wired.
- [x] **§IX Branch Coverage**: §IX applies specifically to files under `src/texlint/journals/*/rules/`. The harness is at top-level `eval/`, not a rule module, so the 100% branch-coverage mandate does not apply. Ordinary engineering judgment applies: target high coverage on `db.py`, `scan.py`, `report.py` (the data-correctness-critical modules), with the integration test doing the heavy lifting end-to-end.
- [x] **§X Small Surface**: `ReviewClient` is a `Protocol` with exactly two concrete implementations — the production `LlamaServerClient` and the test `FakeClient`. No subclass hierarchy. No speculative flags. Each of the six `eval-jss` subcommands has a concrete use case in the spec; none is scaffolding for a hypothetical future. **PASS.**
- [x] **§XII Reproducible Corpus**: **This spec implements the mechanism.** `eval/corpus-manifest.csv` with SHA256 per paper is the manifest; `eval-jss corpus fetch` (Phase B) materialises from immutable distribution URLs only (CRAN `Archive/`, Bioc release tags, arXiv `vN` source URLs, SWHIDs); per-file SHA256 is verified before extraction. Discovery sources (GitHub code search, arXiv listing API) are explicitly never used for fetching. **PASS by design.** (Precision claims made before Phase B lands must cite the commit hash of `examples/` rather than a manifest hash — see research.md §Phase A corpus reproducibility.)

All gates PASS or documented N/A. **No Complexity Tracking entries required.**

Post-Phase-1 re-check (after writing research.md, data-model.md, contracts/, quickstart.md): all gates still PASS or N/A. No surprises emerged in Phase 1 design. The Phase-A-without-manifest precision claim caveat is noted in research.md and surfaces as a README/quickstart note, not as a §XII violation — Phase B closes the loop for any claim that escapes a developer's laptop.

## Project Structure

### Documentation (this feature)

```text
specs/002-eval-jss-harness/
├── plan.md                        # This file
├── research.md                    # Phase 0: decisions + rationales
├── data-model.md                  # Phase 1: SQLite schema + Python types
├── quickstart.md                  # Phase 1: dev onboarding + end-to-end walkthrough
├── contracts/
│   ├── cli.md                     # Phase 1: eval-jss subcommands, flags, exit codes, streams
│   ├── schema.md                  # Phase 1: exact DDL + dedup contract + WAL/PRAGMA contract
│   ├── review-client.md           # Phase 1: ReviewClient Protocol + LlamaServerClient HTTP contract
│   ├── corpus-manifest.md         # Phase 1: corpus-manifest.csv + corpus-manifest-gaps.csv schemas
│   └── report-csv.md              # Phase 1: eval/report.csv append-only history schema
└── checklists/
    └── requirements.md            # Spec quality checklist (from /speckit.specify)
```

### Source Code (repository root)

```text
# Phase A (MVP) — independently shippable
eval/
├── __init__.py
├── cli.py                         # click entry; subcommand dispatch for init/scan/human-review/report/review/corpus
├── db.py                          # connect() with PRAGMAs, run(query, params), schema DDL loader, idempotent init()
├── scan.py                        # walk corpus dir, resolve jss-lint, invoke per paper, INSERT OR IGNORE violations
├── human_review.py                # rich-based interactive TUI (Prompt.ask per row, context snippet, session-resumable)
├── report.py                      # per-rule precision query, rich Table renderer, --by-source flag (Phase B hook)
├── review.py                      # Phase B: AI review orchestration + ReviewClient Protocol + LlamaServerClient + skip-list
├── corpus.py                      # Phase B: manifest parser, corpus fetch, SHA256 verify, gaps file writer
└── schema.sql                     # single source of truth for the DDL, loaded by db.py

# Data (checked in or gitignored per file)
eval/corpus-manifest.csv           # Phase B: pinned corpus definition (checked in)
eval/corpus-manifest-gaps.csv      # Phase B: generated at fetch time (checked in once stable; regenerated per run)
eval/review-skip-list.toml         # Phase B: rules that bypass AI review (checked in; empty default)
eval/report.csv                    # Phase B: precision history, append-only (checked in so trends diff)
eval/eval.db                       # runtime database; gitignored
.gitignore                         # adds eval/eval.db and eval/eval.db-*

# MVP corpus (Phase A)
examples/                          # 10 hand-curated CRAN vignettes, one subdirectory per paper
├── <paper-1-dirname>/
│   ├── <vignette>.tex
│   ├── <refs>.bib
│   └── README.md                  # per-paper provenance note (CRAN URL, version, DOI)
├── <paper-2-dirname>/
├── ...
└── README.md                      # corpus-level note: curation policy, how to add a paper

# Packaging changes
pyproject.toml                     # new [project.scripts] entry: eval-jss = eval.cli:main
                                   # tool.hatch.build.targets.wheel.packages UNCHANGED (eval/ stays out of the wheel)
                                   # tool.hatch.build.targets.sdist.include adds "eval" so source releases carry the harness

# Tests
tests/eval/
├── __init__.py
├── conftest.py                    # tmp_db, fake_corpus, fake_client fixtures; monkeypatch for _invoke_linter and Prompt.ask
├── test_db.py                     # PRAGMAs applied, init() idempotent, FK cascade on papers→violations delete
├── test_scan.py                   # dedup contract, JSS-PARSE-000 pass-through, runs row appended, linter-not-on-PATH error
├── test_human_review.py           # scripted verdicts, verdict_reason captured, reviewer stamped, session resumability
├── test_report.py                 # precision math, below-threshold flag, "not yet measured"/"not exercised" states, CSV append
├── test_review.py                 # FakeClient-driven high/low confidence split, skip-list bypass, no network in test run
├── test_corpus.py                 # manifest parse, SHA256 verify, hash mismatch → gaps row, tarball extraction
└── test_integration.py            # init → scan (fake linter) → scripted human-review → report on 3-paper fake corpus
```

**Structure Decision**: Top-level `eval/` package, peer to `src/texlint/`, deliberately **outside** the wheel. The harness is a development tool for the linter authors, not a capability the downstream `pip install jss-style-checker` user should receive. `eval/` stays in the sdist so `git clone` + `pip install -e '.[dev]'` + `eval-jss ...` works, but wheel installs from PyPI ship only `src/texlint/`. Tests live under `tests/eval/` and never import from `src/texlint/`: the harness exercises the linter through its CLI exactly as CI and end-users do, which keeps the harness honest about what the `jss-lint` binary actually emits.

## Complexity Tracking

No constitution gates are violated. **Table omitted.**
