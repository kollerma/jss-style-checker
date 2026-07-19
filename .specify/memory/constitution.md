<!--
Sync Impact Report
==================
Version change: 1.0.0 → 1.1.0
Rationale: MINOR bump — three new principles added (XIII–XV, governing the
Rust reimplementation) plus material expansion of existing principles IV,
VIII, and IX with explicit engine scoping. No principle was removed or
inverted.

Principles added:
  XIII. Rust/Python Engine Parity
  XIV.  Portable-Core Isolation
  XV.   Single-Source Version

Principles modified:
  IV.   Zero Core Edits to Add a Journal — scoped to the Python reference
        implementation; the Rust engine's hardcoded single-journal limit is
        recorded as a documented deviation with follow-up.
  VIII. TDD: Tests Fail Before Implementation — scoped: governs the Python
        reference implementation where rules originate; Rust ports are
        governed by §XIII parity instead.
  IX.   100% Branch Coverage on Rule Modules — same scoping as VIII.
  XVI.  (renumbered from XIII, content unchanged) Constitution Amendments Go
        Through This Skill. Renumbering verified safe: no reference to
        "§XIII"/"Principle XIII" exists anywhere in the repo outside this
        file. Principles I–XII keep their numbers because they are cited
        throughout CHANGELOG.md, README.md, eval/, rust/, paper/, and
        specs/001–017.

Sections added:
  - Multi-Engine Architecture (holding XIII–XV)

Sections removed: none.

Templates requiring updates:
  ✅ .specify/templates/plan-template.md — Constitution Check gains gate items
      for §XIII (parity), §XIV (isolation), §XV (single-source version).
  ✅ .specify/templates/tasks-template.md — test-mandate paragraph extended:
      changes to rule behavior MUST include parity-suite tasks for both
      engines (§XIII).
  ✅ .specify/templates/spec-template.md — no changes required.
  ✅ .specify/templates/checklist-template.md — no changes required.
  ✅ CLAUDE.md — refreshed separately in the same change set (stale
      spec-017/"roadmap complete" framing replaced; now points at the
      multi-engine layout and this constitution).
  N/A .specify/templates/commands/*.md — directory does not exist in this repo.

Follow-up TODOs:
  - TODO(RE_IMPLEMENTATION_PLAN): carried over from v1.0.0 — Principle XI
    references `re-implementation-plan.md`, which is still not committed.
  - Follow-up (§IV deviation): the Rust engine registers only the built-in
    `jss` journal; a Rust journal-registration mechanism is tracked in
    roadmap/follow-ups.md.
  - Follow-up (§XIV enforcement): the dependency-graph isolation check is
    being added to CI in the same change set (tests/rust dep-graph guard).
-->

# JSS Style Checker Constitution

## Core Principles (Engineering)

### I. Deterministic Rule Engine

Rule detections MUST be pure functions of the parsed document: identical input
MUST produce identical violations on every run, regardless of host, time, or
process state. ML, heuristics, sampling, and any other source of
nondeterminism are prohibited inside rule `check` callables. AI assistance is
permitted only for rule *review* in the eval loop — never for rule
*detection*.

**Rationale**: Reproducibility is the only path to meaningful precision
measurement. A rule whose output drifts cannot be evaluated, fixed, or
trusted.

### II. AST-First, Source-Scan Second

Rules MUST inspect the pylatexenc AST (for `.tex`) or the bibtexparser library
(for `.bib`) whenever the check can be expressed structurally. Raw-source
regex is reserved for checks that are intrinsically textual: line width,
trailing whitespace, and byte-level encoding. Regex applied to prose or code
content is a code smell that justifies a rewrite using the AST.

**Rationale**: LaTeX and BibTeX are not regular languages. Regex over
structured markup accumulates edge-case patches and fails silently on inputs
it was never tested against.

### III. Parse Errors Are Non-Fatal

Parse failures MUST be recorded as `Violation`s on the returned
`ParsedTexFile` / `ParsedBibFile` and MUST NOT be raised. The tool MUST always
produce a `ComplianceReport`, even for malformed input.

**Rationale**: A linter that refuses to run on broken files is useless during
the fix cycle, which is precisely when broken files exist.

### IV. Zero Core Edits to Add a Journal

New journals MUST be registered exclusively through `importlib.metadata` entry
points in the `texlint.journals` group. Touching `src/texlint/core/` or
`src/texlint/api.py` to add a journal is a design failure and MUST be
rejected in review.

**Scope (added v1.1.0)**: This principle governs the Python reference
implementation. The Rust engine (`rust/jsslint-core`) currently registers
only the built-in `jss` journal and has no third-party registration
mechanism — a known, documented deviation tracked in `roadmap/follow-ups.md`.
Until a Rust registration mechanism ships, "the Rust engine doesn't support
plugins" is never a justification for editing `src/texlint/core/` to add a
journal on the Python side.

**Rationale**: The core exists to dispatch; adding journals by editing it
entangles policy with mechanism and blocks third-party journal packages.

### V. Every Rule Cites an Authority

Each rule's metadata MUST reference at least one of: `jss.cls`, `article.tex`,
the JSS style guide, or the author instructions. When these authorities
disagree, the priority order is: `jss.cls` > `article.tex` > style guide >
author instructions. Rules grounded only in convention (no source anchor) MUST
be rejected during `/speckit.clarify`.

**Rationale**: Rules without authority are opinions. Opinions drift, break
trust with authors, and cannot be defended in review.

### VI. Empirical Quality Gate: ≥90% Precision Per Rule

Every rule MUST achieve ≥90% precision on the eval corpus. A rule that cannot
clear this bar on real papers MUST be relaxed, narrowed, or retired — never
grandfathered. Precision is measured by `eval-jss report`. The threshold is
enforced at the end of each Step 3 category, not only at release time.

**Rationale**: A noisy linter is ignored. Enforcing precision per-rule
(rather than only in aggregate) prevents one loud rule from burying the
signal of the rest.

### VII. Auto-Fix Is Verified, Atomic, and Optional

Every `FixSuggestion`, once applied, MUST be re-checked against its
originating rule; fixes that re-trigger the rule MUST be recorded as
`skipped` and MUST NOT be silently applied. File writes MUST use `tempfile` +
`os.replace()` so that a partial fix can never corrupt a user's working file.
Rules without a safe deterministic fix MUST leave `violation.fix = None` —
unsafe fixes are worse than no fix.

**Rationale**: Silent or corrupting auto-fixes destroy trust in the tool and
in the user's repository. Verification + atomic write is the cheapest
insurance against both failure modes.

## Testing & Quality Standards

### VIII. TDD: Tests Fail Before Implementation

Every new rule MUST ship with a failing unit test committed (or demonstrably
failing in the working tree) before the rule's `check` body exists. The
Red-Green-Refactor cycle is the only accepted workflow for rule development.

**Scope (added v1.1.0)**: This workflow governs the Python reference
implementation, where rules originate. Porting an existing rule to the Rust
engine is governed by §XIII (byte-for-byte parity against the Python oracle),
not by an independent red-green cycle — the parity suite is the failing test.

**Rationale**: A test written after the code documents behavior instead of
specifying it. Writing the test first is the only reliable way to prove the
rule catches what it claims to catch.

### IX. 100% Branch Coverage on Rule Modules

Every file under `src/texlint/journals/*/rules/` MUST achieve 100% branch
coverage. Coverage gaps in these files are a blocker, not a nice-to-have.
Coverage requirements outside the rule modules are governed by ordinary
engineering judgment.

**Scope (added v1.1.0)**: The coverage mandate applies to the Python rule
modules, where rules are precision-graded. The Rust ports under
`rust/jsslint-core/src/rules/` are verified by the §XIII parity suites
against the Python oracle rather than by an independent coverage gate;
imposing a second, duplicate coverage regime on ports of already-covered
logic would violate §X.

**Rationale**: Rule files are small, self-contained, and directly
precision-graded. Full branch coverage is cheap to obtain and the only
defense against latent false-positive paths that the eval corpus happens not
to exercise.

### X. Small Surface, Known Semantics

No speculative abstractions. No backwards-compatibility shims for code that
was never released. No dead code paths preserved "just in case". Three
similar lines beat a premature helper. When a rule or module becomes unused,
delete it — do not deprecate, do not comment out, do not leave stubs.

**Rationale**: The rule corpus grows. Every helper, flag, and shim
multiplies the surface that every future rule author must understand.
Removal is cheaper than explanation.

## Collaboration & Workflow

### XI. Spec-Kit Is Reserved for Cross-Cutting Work

Plain plan/implement workflows MUST be used for mechanical,
well-understood changes. The spec-kit workflow (`/speckit.specify`,
`/speckit.clarify`, `/speckit.plan`, `/speckit.tasks`, `/speckit.implement`)
is reserved for cross-cutting work. Concretely: re-implementation Steps 1,
2, 3, 4, and 5 use spec-kit; Steps 0 and 6 do not. See
`re-implementation-plan.md` for the step inventory and rationale.

**Rationale**: Spec-kit has non-trivial overhead. Applying it to mechanical
changes produces paperwork without producing clarity. Applying it to
cross-cutting changes produces the alignment that review alone cannot.

### XII. Reproducible Corpus

The eval corpus MUST be defined by a pinned manifest at
`eval/corpus-manifest.csv` recording, at minimum, source URL and SHA256 hash
for every file. Discovery sources (GitHub, arXiv listings, search results)
are mutable and MAY be used to find candidates; distribution sources used in
the manifest MUST be immutable: CRAN `Archive/`, Bioconductor release tags,
arXiv `vN` identifiers, or Software Heritage IDs (SWHIDs). No rule-precision
claim in the paper, release notes, or PR description is valid without
citing a corpus commit hash.

**Rationale**: A precision number without a reproducible corpus is
unfalsifiable. Immutable distribution sources are the only way to keep
historical claims checkable as upstream repositories evolve.

## Multi-Engine Architecture

### XIII. Rust/Python Engine Parity

The Python package (`src/texlint/`) is the reference implementation. The
Rust workspace (`rust/jsslint-core` plus the CLI, WASM, PyO3, and R bindings)
is a port of it, not a fork. Every rule and every user-visible behavior MUST
exist in both engines, and for identical input and configuration the two
engines MUST produce byte-identical output in every shared format
(`terminal`, `json`, `sarif`, `html`). Parity is enforced by the parity
suites (`rust/*/tests/*_parity.rs`, `tests/unit/test_jsslint_parity.py`,
`r/jsslintr/tests/testthat/`); a behavior change that lands in one engine
without its counterpart and parity coverage MUST be rejected in review.
Deliberate divergences (e.g., the Rust CLI's independently laid-out PDF
report, per-ecosystem exit/return conventions) MUST be documented in
`rust/README.md` and excluded from the byte-parity claim explicitly.

**Rationale**: "One engine, compiled five ways" is the product promise. The
moment the engines drift silently, every distribution beyond the Python
original becomes untrustworthy, and the precision numbers measured on one
engine stop being valid for the others.

### XIV. Portable-Core Isolation

`jsslint-core` and every portable binding built on it (`jsslint-wasm`,
`jsslint-py`, `jsslintr`) MUST NOT link network-capable code, and the shared
core MUST NOT perform filesystem or network I/O beyond the in-memory inputs
its caller supplies. Capability-requiring features live at the outer layer:
network lookups (Crossref/CRAN DOI verification) live in the separate
`jsslint-crossref` crate consumed only by `jsslint-cli`; filesystem concerns
(multi-file `\input` resolution, `.jss-lint.toml` discovery, atomic `--fix`
writes) live in the CLI/binding layer. The isolation MUST be structural — a
separate crate, not a feature flag — and MUST be verifiable from the
dependency graph: `cargo tree` for `jsslint-wasm`, `jsslint-py`, and the
vendored `jsslintr` crate never mentions `jsslint-crossref` or an HTTP
client. That check MUST be enforced by an automated test, not convention.

**Rationale**: The WASM build's privacy guarantee — manuscripts never leave
the machine — is only credible if it holds by construction. A feature flag
can be flipped; an absent dependency edge cannot.

### XV. Single-Source Version

The suite version MUST be edited in exactly one place: the root `VERSION`
file, propagated by `scripts/set_version.py` into every ecosystem manifest
(Python `texlint.__version__`, the Cargo workspace, the VS Code
`package.json`/lock, the R `DESCRIPTION` and vendored crates) and their
derived lockfiles. Hand-editing a version string in any manifest is
forbidden; `tests/unit/test_version_single_source.py` MUST fail naming the
offending file when any manifest disagrees with `VERSION`. One sanctioned
exception: the R `DESCRIPTION` MAY carry a CRAN-resubmission revision suffix
(`X.Y.Z-N`) on the same base version.

**Rationale**: The 1.0.1 release demonstrated the failure mode this
prevents: ~10 hand-maintained version strings across four ecosystems, two of
which were missed during a bump, breaking parity tests and the R build. A
single edited file plus a guard test makes stale versions impossible to ship
silently.

## Governance

### XVI. Constitution Amendments Go Through This Skill

Changes to these principles MUST re-run `/speckit.constitution` so that
dependent templates (`plan-template.md`, `spec-template.md`,
`tasks-template.md`, and any command templates) stay in sync. Ad-hoc edits
to this file are forbidden; any such edit MUST be reverted and re-applied
through the skill.

**Amendment procedure**: Propose the change in a PR that (a) updates this
document via `/speckit.constitution`, (b) includes the generated Sync Impact
Report as the PR description, and (c) updates every template flagged
`⚠ pending` in that report before merge.

**Versioning policy** (semantic versioning of this document):
- **MAJOR**: Backward-incompatible governance or principle change —
  removal, inversion, or redefinition of an existing principle.
- **MINOR**: New principle added, or material expansion of guidance in an
  existing principle.
- **PATCH**: Clarifications, wording, typo fixes, non-semantic refinements.

**Compliance review**: Every PR reviewer MUST verify that the change
complies with Principles I–XV. Any deviation MUST be justified in the PR
description and recorded in the plan's Complexity Tracking table.

**Version**: 1.1.0 | **Ratified**: 2026-04-22 | **Last Amended**: 2026-07-19
