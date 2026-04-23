<!--
Sync Impact Report
==================
Version change: (uninitialized template) → 1.0.0
Rationale: Initial ratification of the jss-style-checker constitution. A MAJOR
(1.0.0) bump is appropriate for first adoption; no prior governance existed.

Principles added (all new; no prior versions to rename):
  I.   Deterministic Rule Engine
  II.  AST-First, Source-Scan Second
  III. Parse Errors Are Non-Fatal
  IV.  Zero Core Edits to Add a Journal
  V.   Every Rule Cites an Authority
  VI.  Empirical Quality Gate (≥90% precision per rule)
  VII. Auto-Fix Is Verified, Atomic, and Optional
  VIII. TDD: Tests Fail Before Implementation
  IX.  100% Branch Coverage on Rule Modules
  X.   Small Surface, Known Semantics
  XI.  Spec-Kit Is Reserved for Cross-Cutting Work
  XII. Reproducible Corpus
  XIII. Constitution Amendments Go Through This Skill

Sections added:
  - Core Principles (Engineering)
  - Testing & Quality Standards
  - Collaboration & Workflow
  - Governance

Sections removed: none (no prior constitution).

Templates requiring updates:
  ✅ .specify/templates/plan-template.md — Constitution Check section replaced
      with the concrete gate checklist derived from Principles I–X, XII.
  ✅ .specify/templates/tasks-template.md — test-mandate line qualified: unit
      tests are MANDATORY for files under src/texlint/journals/*/rules/
      (Constitution §VIII, §IX); test tasks phrased as optional only outside
      that scope.
  ✅ .specify/templates/spec-template.md — no changes required; authority
      citation (§V) is enforced at /speckit.clarify, not at spec drafting.
  ✅ .specify/templates/checklist-template.md — no changes required.
  ✅ CLAUDE.md, README.md — no references to principle content; no edits.
  N/A .specify/templates/commands/*.md — directory does not exist in this repo.

Follow-up TODOs:
  - TODO(RE_IMPLEMENTATION_PLAN): Principle XI references
    `re-implementation-plan.md`, which is not yet committed to the repo.
    The reference is retained as the authoritative source for step-to-workflow
    mapping; author must create the file or update the reference once the
    plan is drafted.
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

**Rationale**: A test written after the code documents behavior instead of
specifying it. Writing the test first is the only reliable way to prove the
rule catches what it claims to catch.

### IX. 100% Branch Coverage on Rule Modules

Every file under `src/texlint/journals/*/rules/` MUST achieve 100% branch
coverage. Coverage gaps in these files are a blocker, not a nice-to-have.
Coverage requirements outside the rule modules are governed by ordinary
engineering judgment.

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

## Governance

### XIII. Constitution Amendments Go Through This Skill

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
complies with Principles I–XII. Any deviation MUST be justified in the PR
description and recorded in the plan's Complexity Tracking table.

**Version**: 1.0.0 | **Ratified**: 2026-04-22 | **Last Amended**: 2026-04-22
