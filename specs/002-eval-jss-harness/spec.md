# Feature Specification: `eval-jss` — Precision Harness for the JSS Linter

**Feature Branch**: `002-eval-jss-harness`
**Created**: 2026-04-23
**Status**: Draft
**Input**: User description: "Build `eval-jss`, a companion CLI for running `jss-lint` against a real-world corpus of JSS manuscripts and measuring per-rule precision. The purpose is to drive rule refinement during Step 3: every rule we ship should hit ≥90% precision on the corpus or be relaxed / retired."

## Clarifications

### Session 2026-04-23

- Q: Scope commitment — ship MVP only in this spec, or land both MVP and full-scope in this spec? → A: **Land both tiers in this spec, phased.** The MVP phase (init/scan/human-review/report over a hand-curated corpus) is independently shippable and unblocks Step 3. The full-scope phase (AI-assisted review, corpus reproducibility via pinned manifest, CSV precision history, per-source precision breakdown) ships in the same spec but its tasks are ordered *after* the MVP phase in `tasks.md`. The MVP phase MUST be demonstrably usable before any full-scope task begins; a partial full-scope phase MUST NOT regress any MVP capability. This lets Step 3 start on the MVP pipeline while full-scope features land incrementally over the same spec's life.
- Q: MVP corpus size — 10, 20, or grow over time? → A: **10 papers to start, grow as Step 3 demands volume.** The MVP ships with a hand-curated corpus of 10 CRAN vignettes checked into `examples/`, sufficient to exercise the 3–5 Step 1 smoke rules end-to-end and to prove parse regressions surface correctly. As Step 3 adds rules, the corpus grows up to ~20 papers without a spec amendment — corpus size is an operational knob under this spec, not a versioned deliverable. Success criteria that assert "the corpus" refer to whatever is currently curated in `examples/`, not to a frozen count.
- Q: Which AI backend to pin for full-scope AI review, so precision numbers are reproducible across contributors? → A: `llama.cpp`'s `llama-server` hosting `unsloth/Qwen3-30B-A3B-GGUF:UD-Q4_K_XL` (30B-A3B MoE, Unsloth Dynamic Q4_K_XL quantisation) on an OpenAI-compatible HTTP API (default `http://localhost:8080`). Sampling is **greedy-deterministic**: `top-k=1`, `temp=0.1`, `top-p=1.0`, `min-p=0.0`. Greedy decoding is the reproducibility contract — same prompt yields the same label on every run on every host. Transport is HTTPS/HTTP JSON POST (stdlib `urllib.request` is sufficient, so no new runtime dependency is introduced beyond what `jss-lint` already pulls in).

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Measure per-rule precision on a pinned corpus (Priority: P1)

A linter developer working on rule refinement needs to know, for each rule, what fraction of the violations it fires on real JSS manuscripts are genuine style issues versus false positives. They run the harness end-to-end against a pinned corpus of 10–20 manuscripts, label each reported violation as a true positive or false positive, and read off a per-rule precision number. A rule whose precision is below 90% is visibly flagged, because Constitution Principle VI requires that every shipped rule clears that bar on the corpus.

**Why this priority**: This is the only reason the harness exists. Without the end-to-end scan → label → report loop, the `≥90% precision per rule` gate cannot be enforced empirically and Step 3 (the rule catalogue) cannot start. Every other surface (AI-assisted labelling, corpus reproducibility, history tracking, per-source breakdown) is either a workload reducer or a reproducibility aid layered on top of this core loop.

**Independent Test**: From a clean checkout, running `eval-jss init` creates the database, `eval-jss scan` invokes `jss-lint --output json` on every paper in the corpus and persists the resulting violations, `eval-jss human-review` walks the unlabelled violations and accepts a verdict for each, and `eval-jss report` prints a table showing per-rule precision. On a fake-corpus fixture of 3 papers whose expected violations are known, the reported precision numbers must exactly match the hand-computed values.

**Acceptance Scenarios**:

1. **Given** a fresh repository with no database yet, **When** the operator runs `eval-jss init`, **Then** a SQLite database is created with the `papers`, `violations`, and `runs` tables and the command is idempotent (a second `init` invocation is a no-op that succeeds).
2. **Given** a corpus of N papers on disk and an initialised database, **When** the operator runs `eval-jss scan`, **Then** each paper is passed through `jss-lint --output json` exactly once, every reported violation is persisted with a NULL `verdict`, and a single row is appended to `runs` recording the timestamp, the linter version, the number of papers scanned, and the total violations found.
3. **Given** a corpus that has already been scanned, **When** the operator runs `eval-jss scan` a second time with the same linter version, **Then** no duplicate violation rows are created — the `(paper_id, rule_id, line, message)` tuple is the dedup key and existing rows are left in place (verdicts preserved).
4. **Given** a paper that `jss-lint` cannot parse, **When** `eval-jss scan` processes it, **Then** the parse failure is recorded as a synthetic violation with `rule_id = "JSS-PARSE-000"` rather than being silently dropped or crashing the scan, so parse regressions surface in the report alongside rule-produced violations.
5. **Given** a database with unlabelled violations, **When** the operator runs `eval-jss human-review`, **Then** each unlabelled (or `uncertain`) violation is presented in turn with its rule id, paper, line, and message; the operator chooses `true_positive`, `false_positive`, or `uncertain`; the verdict, an optional free-text `verdict_reason`, and the reviewer identifier are written back to the row.
6. **Given** a database with a mix of true-positive and false-positive verdicts, **When** the operator runs `eval-jss report`, **Then** a table is printed showing, per rule and grouped by rule category, the TP count, FP count, and precision `TP / (TP + FP)`; rules with precision below the 90% threshold are visually flagged; rules with no labelled data are listed separately so the operator knows they are not yet measurable.
7. **Given** a clean-corpus run (every violation labelled true positive), **When** `eval-jss report` runs, **Then** every rule with at least one labelled violation shows 100% precision and no rule is flagged as under threshold.

---

### User Story 2 — Reduce manual labelling effort with AI-assisted review (Priority: P2, full scope)

Once the corpus has enough violation volume to benchmark a classifier, a linter developer wants to let a local language model pre-label obvious true and false positives, reserving human attention for the ambiguous cases. They run `eval-jss review`, which consults a local LLM for each unlabelled violation and fills in `verdict` only when the model reports high confidence; low-confidence rows remain `uncertain` and are picked up by `human-review` as usual.

**Why this priority**: The MVP is usable without AI assistance — human review scales to 10–20 papers worth of violations. AI review becomes valuable once the corpus is larger (late Step 2 or Step 6 polish) and only after the classifier has been benchmarked against human labels so it does not silently poison the precision number. Landing it now would be premature.

**Independent Test**: With a mock AI client whose confidence scores are scripted per violation, running `eval-jss review` labels only the high-confidence rows and leaves the low-confidence rows `uncertain`; a subsequent `eval-jss human-review` picks up exactly the remaining unlabelled and `uncertain` rows.

**Acceptance Scenarios**:

1. **Given** a database with unlabelled violations and a configured AI client, **When** `eval-jss review` runs, **Then** each unlabelled violation is sent to the client and, if the client returns a high-confidence label, that label is stored; otherwise the row is marked `uncertain` so it surfaces in `human-review`.
2. **Given** a rule whose AI-label precision is historically low (tracked in configuration), **When** `eval-jss review` encounters a violation of that rule, **Then** the AI is skipped entirely for that rule and the row is left unlabelled for human review.
3. **Given** a unit test, **When** the AI client is replaced with a mock, **Then** the `review` subcommand runs without any network, subprocess, or model dependency, proving the client is behind a mockable interface.

---

### User Story 3 — Reproduce the corpus from a pinned manifest (Priority: P2, full scope)

A reviewer, CI job, or external collaborator needs to reproduce the exact corpus a precision claim was made against. They pull the repository at a commit that pins `eval/corpus-manifest.csv`, run `eval-jss corpus fetch`, and materialise every paper from an immutable distribution URL (CRAN `Archive/` tarball, Bioconductor release tag, arXiv `vN` source, or Software Heritage ID). Every file's SHA256 is verified against the manifest. Entries that cannot be fetched are logged to `eval/corpus-manifest-gaps.csv` so the user knows what is missing and why.

**Why this priority**: Constitution Principle XII requires a reproducible corpus for any published precision claim. The MVP can ship with a hand-curated set of papers checked into `examples/` (CRAN-only is fine) and defer reproducibility tooling until the rule catalogue is mature enough to publish numbers against. Reproducibility is therefore high-value but not a blocker for the first precision report.

**Independent Test**: Given a small fixture manifest (two CRAN entries, one arXiv entry) with known SHA256 values, running `eval-jss corpus fetch` downloads each file from its pinned distribution URL, verifies the hash, and refuses to overwrite the local copy if hashes mismatch. Removing one entry from the manifest and re-running leaves the fetched file orphan-reported; adding an unreachable entry logs a row in `corpus-manifest-gaps.csv`.

**Acceptance Scenarios**:

1. **Given** a populated `eval/corpus-manifest.csv`, **When** `eval-jss corpus fetch` runs, **Then** every missing file is fetched from its pinned immutable URL, every fetched file's SHA256 is verified against the manifest, and any mismatch halts the fetch for that entry with a clear error.
2. **Given** a manifest row whose distribution URL returns a non-success response or whose hash does not match, **When** fetch runs, **Then** the failure is recorded in `eval/corpus-manifest-gaps.csv` (manifest row identifier + reason) rather than raising an exception.
3. **Given** a mutable discovery source (GitHub, an arXiv listing API, a search query), **When** new candidate papers are identified, **Then** they are added to the manifest with an immutable distribution URL (CRAN `Archive/`, Bioc release, arXiv `vN`, SWHID) — the discovery URL itself is never used for fetching.

---

### User Story 4 — Track precision trends over time (Priority: P3, full scope)

A linter maintainer wants to see whether precision is trending up or down as rules and the corpus evolve. `eval-jss report` appends a row to `eval/report.csv` on every run, capturing the timestamp, linter version, corpus commit (if available), per-rule TP/FP counts, and per-rule precision. Over weeks of refinement, this file tells the story of each rule's precision curve.

**Why this priority**: A single precision snapshot is enough for a single refinement cycle. A history is what enforces the invariant that precision does not regress silently across releases. This is additive to the core loop and does not block Step 3.

**Independent Test**: Running `eval-jss report` twice on the same database produces two CSV rows with the same precision numbers and different timestamps; running it after relabelling a violation produces a row with updated precision.

**Acceptance Scenarios**:

1. **Given** a populated database, **When** `eval-jss report` runs, **Then** a row is appended to `eval/report.csv` with the timestamp, tool version, per-rule TP and FP counts, and per-rule precision.
2. **Given** the CSV already exists, **When** `report` runs again, **Then** the new row is appended without touching prior rows and without reordering any columns, so historical rows remain diffable.

---

### User Story 5 — Break precision down by corpus source (Priority: P3, full scope)

A linter developer noticed that a rule scoring 98% on CRAN vignettes scores only 60% on arXiv preprints, because preprints follow the JSS house style less strictly. The `report` command therefore breaks precision down by the `source` column of the manifest (`cran`, `bioc`, `arxiv`, `jss_archive`, `manual`) in addition to the overall number, so the developer can decide whether to tune the rule, narrow its applicability, or accept lower precision on a less canonical source.

**Why this priority**: This is a tuning aid, not a gate. The Principle VI threshold applies to overall corpus precision; per-source breakdown is an explanatory layer that becomes useful only once the multi-source corpus lands (US3).

**Independent Test**: Given a corpus with papers from two distinct sources and deliberately engineered per-source verdict distributions, `eval-jss report` prints an overall precision row per rule plus one row per `source` value that has at least one labelled violation for that rule.

**Acceptance Scenarios**:

1. **Given** labelled violations spanning multiple source values, **When** `eval-jss report` runs, **Then** the output includes an overall precision column and a per-source breakdown column.
2. **Given** a rule with zero violations from one source, **When** the report renders, **Then** that `(rule, source)` cell is blank (not shown as 0%, which would be indistinguishable from actual zero precision).

---

### Edge Cases

- **Linter not installed or not on PATH**: `scan` exits with a distinct non-zero status and a clear error naming `jss-lint`, so the operator does not mistake an environment problem for a clean corpus.
- **Empty corpus directory**: `scan` completes successfully, logs a `runs` row with `papers_scanned = 0`, and `report` prints an empty table with a note rather than failing.
- **Rule with zero violations in the corpus**: listed under "not exercised" in the report, not folded into "100% precision" — absence of data is not success.
- **Rule with violations but no labelled verdicts**: listed under "not yet measured" in the report; does not contribute to the precision numerator or denominator.
- **Rule with only `uncertain` verdicts**: same handling as unlabelled — `uncertain` never counts as TP or FP.
- **Re-scan after linter version bump**: the linter version is recorded on every `runs` row, so the operator can tell which violations came from which version. Dedup still applies within a version; a version change may produce new rows that did not exist before, which is correct behaviour.
- **Re-labelling a violation**: the most recent verdict wins; the `verdict_reason` and `reviewer` fields are overwritten (the MVP does not keep a full labelling history — that is a full-scope addition if ever needed).
- **Parse failure violations**: surface in the report under a synthetic `parse` category with `rule_id = "JSS-PARSE-000"`, so corpus-level parse regressions are visible; they are excluded from per-rule precision numerators (they are not style violations) but counted in the scan audit so a regression cannot be masked.
- **Corpus file hash mismatch at scan time** (full scope): `scan` refuses the paper and logs the mismatch, because scanning a file whose content drifted would produce unreproducible precision numbers.
- **AI client returns malformed output** (full scope): the row is left `uncertain` and the malformed response is logged; the scan does not crash.

## Requirements *(mandatory)*

### Functional Requirements

**Scope tiering**

- **FR-001**: The harness MUST ship in two phases within this spec. The **MVP phase** comprises `init`, `scan`, `human-review`, and `report` over a hand-curated corpus checked into the repository and MUST be independently shippable (i.e., the MVP must produce a per-rule precision number on its own, with no dependency on any full-scope component). The **full-scope phase** adds AI-assisted labelling (`review`), pinned-manifest corpus reproducibility (`corpus fetch`), CSV precision history, and per-source precision breakdown. Full-scope tasks MUST be ordered after MVP tasks in `tasks.md`; a partial full-scope phase MUST NOT regress any MVP capability. The spec is considered complete when both phases are delivered; Step 3 may begin as soon as the MVP phase is shippable.

**Packaging & invocation**

- **FR-002**: The harness MUST expose a single top-level console script `eval-jss`. It is a peer of `jss-lint`, not a plugin of it — the two tools ship from the same repository but have independent entry points and independent failure modes.
- **FR-003**: The harness MUST NOT introduce runtime dependencies beyond the Python standard library and the `click` and `rich` packages that the linter already depends on. Any additional dependency (for HTTP, AI clients, hash verification beyond `hashlib`, etc.) MUST be justified as a full-scope addition and listed in the Assumptions section.
- **FR-004**: All `eval-jss` subcommands MUST exit with status `0` on success, status `1` when the underlying operation failed but the harness itself completed (e.g., `scan` ran but one paper produced a `JSS-PARSE-000` violation), and status `2` when the harness itself could not run (unknown subcommand, missing database, linter not on PATH, unreadable corpus).

**Schema & persistence**

- **FR-005**: `eval-jss init` MUST create the database schema if it does not exist and MUST be a safe no-op if the schema already exists. The database file's location MUST be a single well-known path relative to the repository root.
- **FR-006**: The `papers` table MUST record, per paper in the corpus, at minimum a stable identifier, a DOI (nullable for manual entries), a title, a year, a filesystem path to the paper's LaTeX source, and a status flag describing whether it has been successfully scanned.
- **FR-007**: The `violations` table MUST record, per reported violation, at minimum the owning paper, the rule identifier, the line, the column (nullable), the rule's human-readable message, the severity, a `verdict` field, an optional free-text `verdict_reason`, and a reviewer identifier. `verdict` MUST take exactly one of the values `NULL`, `"true_positive"`, `"false_positive"`, or `"uncertain"`.
- **FR-008**: The `runs` table MUST record, per `scan` invocation, a timestamp, the linter version reported by `jss-lint`, the number of papers scanned, and the total number of violations found.

**Scanning**

- **FR-009**: `eval-jss scan` MUST walk the corpus directory, invoke `jss-lint --output json` on each paper, parse the JSON output, and persist the reported violations to the `violations` table.
- **FR-010**: `eval-jss scan` MUST dedup on the tuple `(paper_id, rule_id, line, message)` so that re-scans do not create phantom duplicates. Existing rows MUST be left in place (their verdicts are preserved across re-scans).
- **FR-011**: When `jss-lint` reports a parse failure on a paper (via its `JSS-PARSE-000` synthetic violation — see linter-foundation FR-005), the harness MUST persist that violation exactly like a rule-produced violation so it surfaces in the report.
- **FR-012**: `eval-jss scan` MUST append a single row to the `runs` table per invocation and MUST record the linter version (obtained from the linter's JSON output's `tool_version` field) on that row. A `--batch-size` option MAY limit the number of papers processed in one invocation for large corpora; absent this option, every un-scanned paper MUST be processed.

**Labelling — human (MVP)**

- **FR-013**: `eval-jss human-review` MUST iterate violations whose `verdict` is `NULL` or `"uncertain"` and present each one interactively with enough context for the reviewer to decide (paper identifier, rule identifier, line, message, and the surrounding source snippet when feasible).
- **FR-014**: For each reviewed violation, the reviewer MUST be able to record `true_positive`, `false_positive`, or `uncertain`, plus an optional free-text `verdict_reason`. The reviewer identifier (shell login or an explicit `--reviewer` flag) MUST be recorded on the row.
- **FR-015**: `human-review` MUST support interruption without data loss — each verdict is persisted before the next violation is fetched, so a killed session loses at most the violation currently on screen.

**Labelling — AI (full scope)**

- **FR-016**: `eval-jss review` MUST classify each unlabelled violation through a pluggable client interface. High-confidence labels MUST be written to `verdict`; low-confidence results MUST leave the row as `"uncertain"` so it surfaces in `human-review`.
- **FR-017**: The AI client MUST be behind a single mockable interface so the rest of the package has no direct dependency on any specific model, host, or transport. Unit tests MUST run without instantiating a real client.
- **FR-018**: Rules whose AI-label precision is known to be low (initially including but not limited to rules that inspect `\code{}`-wrapped `param=value` constructs, per an observed Qwen3 blind spot) MUST be configured to skip AI labelling entirely and go directly to human review. The list MUST be data-driven, not hard-coded, so rules can be added to or removed from it without code changes.

**Reporting**

- **FR-019**: `eval-jss report` MUST compute, for every rule with at least one labelled violation, `precision = TP / (TP + FP)`, grouped by rule category, where `uncertain` and unlabelled rows are excluded from both numerator and denominator.
- **FR-020**: `eval-jss report` MUST visually flag rules whose precision falls below the 90% threshold set by Constitution Principle VI. Rules with labelled data at or above 90% MUST be rendered as passing; rules with no labelled verdicts MUST be rendered as "not yet measured"; rules with zero reported violations on the corpus MUST be rendered as "not exercised".
- **FR-021**: `eval-jss report` MUST render parse-failure violations (rule id `JSS-PARSE-000`) in a dedicated row outside the per-rule precision table, and MUST NOT fold them into the per-rule precision numerators or denominators.
- **FR-022**: *(full scope)* `eval-jss report` MUST append one row per invocation to `eval/report.csv` capturing the timestamp, tool version, per-rule TP and FP counts, and per-rule precision. The column order MUST be stable across invocations so the file remains diffable.
- **FR-023**: *(full scope)* `eval-jss report` MUST additionally break precision down by the manifest's `source` column (`cran`, `bioc`, `arxiv`, `jss_archive`, `manual`), showing overall precision plus per-source precision for every rule that has labelled violations on more than one source.

**Corpus reproducibility (full scope)**

- **FR-024**: The corpus MUST be defined by a pinned manifest at `eval/corpus-manifest.csv` with one row per paper and the columns: `jss_doi`, `source` (`cran` | `bioc` | `arxiv` | `jss_archive` | `manual`), `source_id` (package name, arXiv id, etc.), `version` (CRAN `cran_version`, Bioc release, arXiv `vN`, SWHID, or a manual marker), `vignette_file`, `local_path`, `sha256`.
- **FR-025**: `eval-jss corpus fetch` MUST materialise the corpus from the manifest using only immutable, version-pinned distribution URLs: CRAN `Archive/` tarballs, Bioconductor release tags, arXiv `vN` source URLs, or Software Heritage SWHIDs. Mutable discovery sources (GitHub code search, arXiv listing API, Zenodo search) MAY be used to *find* candidate papers but MUST NOT be used to *fetch* them.
- **FR-026**: `eval-jss corpus fetch` MUST verify the SHA256 of every fetched file against the manifest and MUST refuse to accept a file whose hash mismatches. Entries that cannot be fetched (HTTP error, SWH rot, hash mismatch) MUST be recorded in `eval/corpus-manifest-gaps.csv` rather than raising an exception.

**Testing**

- **FR-027**: Every module of the harness MUST have unit tests located under `tests/eval/`. The AI client MUST be mocked in its module's tests so the suite has no runtime dependency on a specific model or network service.
- **FR-028**: The harness MUST ship an integration test that runs the MVP pipeline (`init → scan → scripted human-review → report`) end-to-end against a fake corpus of three papers with pre-known expected violations, and MUST verify that the reported precision matches the hand-computed expected values.

### Key Entities

- **Paper**: A single LaTeX manuscript in the evaluation corpus. Carries a stable identifier, a DOI (optional), a title, a year, a filesystem path to the source, and a scan-status flag.
- **Violation**: A single style complaint that `jss-lint` raised against a paper. Carries the owning paper, the rule id, the line, the optional column, the severity, the linter's human-readable message, a verdict (`NULL` | `true_positive` | `false_positive` | `uncertain`), an optional free-text verdict reason, and the reviewer identifier. `JSS-PARSE-000` violations are a subspecies that represent paper-level parse failures rather than style issues.
- **Run**: An audit record of one `scan` invocation. Carries timestamp, the linter version under which the scan ran, the number of papers scanned, and the total violations found.
- **Verdict**: The reviewer's judgement on a single violation. Exactly one of the four listed values. A row without a verdict is treated the same as `"uncertain"` for reporting purposes.
- **Rule** *(referenced, not stored here)*: The linter-owned concept of a named check belonging to a rule category. `eval-jss` does not store the rule catalogue itself — it learns the set of rule ids from the violations the linter reports and groups them by the category metadata the linter emits.
- **Precision**: For a given rule, `TP / (TP + FP)` over the labelled violations of that rule. Parse-error violations, `uncertain` verdicts, and unlabelled rows do not enter the computation.
- **Corpus Manifest** *(full scope)*: A pinned CSV with one row per paper and the fixed column set listed in FR-024. The ultimate source of truth for what "the corpus" is at a given commit.
- **Manifest Gap** *(full scope)*: A manifest row that could not be materialised by `corpus fetch` (HTTP error, hash mismatch, rot), recorded to `eval/corpus-manifest-gaps.csv` for operator attention.
- **Precision History Row** *(full scope)*: A single line of `eval/report.csv` capturing one invocation's per-rule precision with a timestamp and tool-version stamp, enabling diff-based trend tracking over time.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A linter developer starting from a clean checkout can run `eval-jss init && eval-jss scan && eval-jss human-review && eval-jss report` and obtain a per-rule precision number on the MVP corpus within a single working session, without installing any dependency the linter itself does not already require.
- **SC-002**: Running `eval-jss scan` twice in succession on the same corpus with the same linter version creates zero new violation rows on the second run — the dedup contract holds.
- **SC-003**: For every rule shipped by the linter, the operator can tell from the report alone whether it is above the 90% precision bar, below it, not yet measured, or not exercised by the corpus. These four states are visibly distinct in the report.
- **SC-004**: A corpus file that `jss-lint` cannot parse surfaces as a distinct, named row in the report (`JSS-PARSE-000`). A future parse regression — e.g., a package upgrade that breaks `pylatexenc` on an existing corpus file — cannot silently tank the precision number of unrelated rules.
- **SC-005**: The end-to-end integration test on a fake 3-paper corpus completes in under 10 seconds on ordinary developer hardware and produces per-rule precision numbers that match hand-computed expected values exactly.
- **SC-006**: *(full scope)* A reviewer following the repository README can reproduce the corpus at a given commit by running `eval-jss corpus fetch` with no manual downloads, and every fetched file's SHA256 matches its pinned manifest value.
- **SC-007**: *(full scope)* For rules on the "AI skip" list, `eval-jss review` performs zero AI queries; every such violation is left for `human-review` with no silent mislabelling in the database.
- **SC-008**: *(full scope)* The per-source precision breakdown correctly distinguishes, on a deliberately engineered fixture corpus, a rule whose CRAN precision is 100% and whose arXiv precision is below threshold, such that a stylistic population difference cannot be buried inside the overall number.

## Assumptions

- The harness is a companion CLI, not a plugin of `jss-lint`; both ship from the same repository but have independent console scripts and independent failure modes, so precision measurement can proceed even when the linter is mid-refactor.
- The package directory is `eval/` at the top level of the repository (peer to `src/texlint/` and `tests/`), not inside `src/texlint/`. This deliberately keeps the evaluation harness out of the wheel that downstream users install.
- Module layout inside `eval/`: `cli.py`, `db.py`, `scan.py`, `review.py`, `report.py`, `corpus.py`. Tests live under `tests/eval/` and never import from `src/texlint/` — the harness talks to the linter via its CLI, the same way CI does.
- The database file is a single SQLite file at `eval/eval.db`. The MVP corpus database is gitignored; the fake-corpus database used by the integration test is produced in a tmp directory per test run.
- The MVP corpus lives under `examples/` in the repository until reproducibility tooling lands. It is hand-curated and ships with **10 CRAN vignettes** that use `\documentclass{jss}` or `\usepackage{jss}`. Corpus size is an operational knob under this spec, not a frozen deliverable: as Step 3 rule development demands more signal, the corpus grows (informally up to ~20 papers) without a spec amendment. Every FR and SC that mentions "the corpus" refers to whatever is currently curated in `examples/` at report time, not to a fixed count.
- Corpus discovery (full scope) uses six ranked sources: CRAN first (GitHub code search on `org:cran` for the `jss` literal), Bioconductor second (same trick on `org:Bioconductor`), arXiv third (API query for `stat.*` papers, filtered to those whose source bundles `jss.cls`), JSS replication archives fourth (authoritative, but redistribution rights are author-specific — used as local ground truth, not re-hosted), Software Heritage fifth (permanent fallback), Zenodo sixth (niche). This ordering reflects both population size and redistributability.
- Discovery vs. distribution split: mutable discovery sources (GitHub code search, arXiv listing API, Zenodo search) locate candidates; immutable distribution URLs (CRAN `Archive/`, Bioc release tags, arXiv `vN`, SWHIDs) are the only values stored in the manifest and the only sources `corpus fetch` ever hits.
- DOI cross-check: CRAN and Bioconductor packages that were published as JSS papers embed `bibentry(..., doi = "10.18637/jss.v0XX.iYY")` in `inst/CITATION`. The harness queries `https://crandb.r-pkg.org/{pkg}` to attach `jss_doi` to each manifest row. The JSS OJS OAI-PMH endpoint is the authoritative enumeration of JSS DOIs and is used to compute the remaining gap to feed arXiv / replication-archive discovery.
- The AI backend (full scope) runs locally and is pinned per the 2026-04-23 clarification: `llama.cpp`'s `llama-server` hosting `unsloth/Qwen3-30B-A3B-GGUF:UD-Q4_K_XL`, greedy decoding (`top-k=1`), OpenAI-compatible HTTP API. The review loop therefore has no external-service dependency, no Ollama dependency, and no new Python runtime dependency (stdlib `urllib.request` suffices for the HTTP POST). The mockable client interface (FR-017) is the only seam the rest of the harness sees; swapping the production backend for another local server later (or for a managed API in a different environment) is an implementation change, not a spec change.
- Known AI blind spot: Qwen3 has been observed mislabelling `param=value` constructs inside `\code{}` as false positives (the linter flags them legitimately). The configuration mechanism that opts rules out of AI labelling (FR-018) is how such blind spots are contained — not by retraining the model, not by hard-coding exceptions.
- Linter integration is loose: `eval-jss scan` shells out to `jss-lint --output json` and parses the JSON. It does not import from `src/texlint/` and does not depend on any Python API the linter exposes. This keeps the harness validating the tool the user actually runs, not a private in-process shortcut.
- Under the Constitution, AI is permitted in the eval loop for *rule review* only (Principle I). It is never used for *rule detection*, and `eval-jss review` must never be mistaken for a rule engine.
- Step context: Step 1 (linter foundation, spec 001) ships only 3–5 smoke-test rules, so the first `eval-jss report` run will have a short precision table. That is by design — the first run's job is to prove the plumbing and to catch parse regressions before the rule catalogue is populated during Step 3.
