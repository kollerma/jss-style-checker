# Implementation Plan: JSS Rule Catalogue — From 5 Smoke Rules to ~50 Production Rules

**Branch**: `003-jss-rule-catalogue` | **Date**: 2026-04-23 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/003-jss-rule-catalogue/spec.md`

## Summary

Expand the JSS journal plugin from the three Step 1 smoke rules (`bib_001_year.py`, `cite_001_emph.py`, `src_001_width.py`) into an authority-cited rule catalogue of ~50 rules across ~16 categories, drafted against the vendored JSS template (`docs/jss-template/jss.cls` v3.3, `article.tex`) and the JSS website (style guide, author manuscript-preparation page). The catalogue's **source of truth** is a hand-authored YAML file at `specs/003-jss-rule-catalogue/catalogue.yaml`; a small stdlib-only renderer produces `catalogue.md` for human review, and a pytest enforces structural invariants and markdown-from-YAML consistency. Rules ship **category by category** through a precision-gated inner loop (spec 002 `eval-jss report`), with a rule admitted only when its labelled-violation count on the corpus reaches N=10 and precision clears 90%; rules with <10 labelled violations ship in a "not yet measured" state and are re-evaluated as the corpus grows toward ~50 papers.

**Spec drift reconciled — two items.**

1. **Rule-callable signature.** Spec FR-018 paraphrases the rule signature as `Callable[[ParsedDocument], Iterator[Violation]]`. The existing foundation (spec 001 `data-model.md`) defines the type alias as `RuleCheck = Callable[[ParsedDocument, ToolConfig], Iterator[Violation]]` — i.e., **with** the `ToolConfig` parameter. This plan honours the foundation: every check callable takes `(doc: ParsedDocument, cfg: ToolConfig)` exactly as the three smoke rules already do. The spec paraphrase is a simplification that does not warrant a foundation-breaking refactor.

2. **Per-category module export shape.** Spec FR-018 says "each module exports `check_*` callables". The existing convention (one rule per module) exports a single `rule: Rule` object whose `.check` attribute is the callable. The new per-category layout exports **multiple `Rule` objects** plus their private `_check_*` callables; the canonical module shape is `rules: tuple[Rule, ...]` at module top-level, with each `Rule`'s `check` bound to a private `_check_jss_<category>_NNN` callable defined in the same file. `JSSJournal.categories()` imports each category module and reads its `rules` tuple. This preserves the linter's "one well-known entry point per category" (spec FR-019) and matches how the existing `citations`-like categories work today in miniature (each smoke-rule module has a `rule = Rule(...)` at the bottom).

## Technical Context

**Language/Version**: Python ≥3.10, unchanged from specs 001 and 002. Catalogue tooling is stdlib-only on the linter side; YAML parsing is a **dev extra** (`PyYAML>=6.0`), not a runtime dependency of the `jss-lint` wheel.

**Primary Dependencies**: `pylatexenc` and `bibtexparser` (already required by the linter; all new rules inspect their AST), `click>=8.1` and `rich>=13.0` (already present; no new CLI surface). Dev extras gain `PyYAML>=6.0` for reading `catalogue.yaml` in the renderer and in the catalogue-validation tests. Runtime deps of `jss-lint` are **unchanged**.

**Storage**: The catalogue is a single hand-authored YAML file at `specs/003-jss-rule-catalogue/catalogue.yaml`. The rendered markdown at `specs/003-jss-rule-catalogue/catalogue.md` is a generated artefact, diffable and committed but re-generable from the YAML by `python -m tools.render_catalogue`. The shared term list at `src/texlint/journals/jss/terms.py` is a plain Python module of frozensets and a `MappingProxyType` canonical-form lookup.

**Testing**: `pytest` (already in dev extras). New test files under `tests/unit/rules/test_<category>.py` (one per category) plus `tests/unit/journals/jss/test_catalogue.py` (catalogue structural invariants), `tests/unit/journals/jss/test_terms.py` (shared-list consistency and no-shadow-in-rules check), and `tests/unit/journals/jss/test_render.py` (markdown-from-YAML consistency). Fixture files under `tests/fixtures/violations/<category>/<rule_id>-{good,bad}.tex` (and `.bib` where applicable); one good/bad pair per rule, kept small and synthetic.

**Target Platform**: POSIX primary (Linux / macOS); Windows exercised only for the stdlib-only rule logic (the catalogue renderer is Python-path-portable). Matches specs 001 and 002.

**Project Type**: Extension of the existing Python linter. No new console scripts, no new packages — `src/texlint/journals/jss/` grows new rule modules and one new `terms.py`. A new `tools/` top-level directory holds the catalogue renderer as a stdlib+PyYAML script (no package install needed; invoked via `python -m tools.render_catalogue`).

**Performance Goals**: Linter run over a single JSS paper completes within the time budget already pinned by spec 001 (sub-second for typical manuscripts). Rule count grows ~17× relative to Step 1 (3 → ~50), but each rule visits the same AST/BibTeX in a single pass — the AST walk is shared across rules where possible, and each rule's per-paper work is O(number of relevant nodes) with a small constant.

**Constraints**: Every rule cites an authority (§V); every rule's check is deterministic (§I); every rule is AST-first or has an explicit raw-source justification (§II); every rule module under `src/texlint/journals/jss/rules/` hits 100% branch coverage (§IX); no speculative abstractions (§X); the per-category rollout is gated on `eval-jss report` precision ≥ 90% for any rule with ≥10 labelled violations (§VI plus spec FR-015).

**Scale/Scope**: ~16 new category modules under `src/texlint/journals/jss/rules/`, ~50 rule definitions spread across them, ~50 fixture pairs under `tests/fixtures/violations/`, 16 unit-test files under `tests/unit/rules/`, one shared `terms.py`, one `catalogue.yaml`, one generated `catalogue.md`, one renderer at `tools/render_catalogue.py`, three catalogue-/terms-/render-validation test files. The three existing one-rule-per-file modules (`bib_001_year.py`, `cite_001_emph.py`, `src_001_width.py`) and their tests are deleted in the same PRs that introduce their new home categories (spec FR-024, Q2 clarification).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Standing gates derived from `.specify/memory/constitution.md` v1.0.0. This spec is the **direct application** of §V (every rule cites an authority), §VI (≥90% precision gate), §VIII (TDD), §IX (100% branch coverage on rule modules), and §X (small surface).

- [x] **§I Determinism**: Every new rule's check is a pure function of `ParsedDocument` — no ML, no sampling, no time-, host-, or process-dependent behaviour. AI is not invoked inside any rule check (`eval-jss review` is the only place AI touches the loop, per spec 002). **PASS.**
- [x] **§II AST-First**: Every proposed rule either (a) walks the pylatexenc AST in `ParsedDocument.tex_files[*].nodes`, or (b) walks `ParsedDocument.bib_files[*].entries` via bibtexparser, or (c) scans `ParsedDocument.tex_files[*].source` / `...raw_text` lines with an explicit justification in the rule's `notes` field (line width, trailing whitespace, byte-level encoding per §II's carve-out). Catalogue entries declare their chosen mode via the `inspects` field (FR-011). **PASS by contract**; the catalogue schema enforces the declaration.
- [x] **§III Non-Fatal Parse**: No rule raises. Parse failures are already handled by the engine (spec 001 FR-005); rules see only successfully parsed files. `JSS-PARSE-000` is not a catalogued rule — it is a synthetic engine-emitted violation — and is excluded from the catalogue data file. **PASS** (consumer of §III).
- [x] **§IV Zero Core Edits for Journals**: No files under `src/texlint/core/` or `src/texlint/api.py` are edited. `src/texlint/journals/jss/__init__.py`'s `JSSJournal.categories()` grows its imports (one per category module) and its returned `RuleCategory` tuple, but that file is the journal plugin's own code, not core. **PASS.**
- [x] **§V Authority Cited**: Every catalogue row carries a non-empty `authority` drawn from `{jss_cls, article_tex, style_guide, author_instructions}` and a resolvable `authority_ref` (spec FR-002, FR-008, FR-010). A CI test iterates `catalogue.yaml` and asserts every row satisfies this — a PR that adds an authority-less rule fails CI. When authorities disagree, `jss_cls > article_tex > style_guide > author_instructions` (FR-003). **PASS by contract.**
- [x] **§VI ≥90% Precision Gate**: Each category's rollout uses the `eval-jss scan → label → report` loop from spec 002. A rule with ≥10 labelled violations must clear 90% on the corpus before its category commits (spec FR-015). Rules below 10 labelled violations ship as "not yet measured" — the gate itself is not advisory, but the sample-size floor prevents 1/1 = 100% artefacts from being treated as evidence of passing. The corpus grows toward ~50 papers so the N=10 floor becomes attainable for most rules (spec Assumptions, Q3). **PASS by design.**
- [x] **§VII Safe Auto-Fix**: No auto-fixes ship in this spec (spec FR-022). Every catalogue row sets `auto_fixable` as a boolean *flag only*; fix payloads are Step 5. Every new `Rule` instance sets `fix = None` on emitted `Violation`s, matching the smoke-rule pattern. **PASS** (flag-only scope; no fix code introduced).
- [x] **§VIII TDD**: `tasks.md` (produced by `/speckit.tasks`) orders the per-rule unit-test task before the per-rule implementation task. The fixture pair under `tests/fixtures/violations/<category>/<rule_id>-{good,bad}.tex` is added first, the test asserting the expected violations lands next (fails because the rule is empty), then the rule's `_check_*` body is written to make the test pass. **PASS by task order.**
- [x] **§IX Branch Coverage**: Each `src/texlint/journals/jss/rules/<category>.py` reaches 100% branch coverage in its `tests/unit/rules/test_<category>.py`. A coverage test (or a `--cov-fail-under=100` in `pyproject.toml` scoped to the rules subtree) enforces this before the category commits. **PASS by contract.**
- [x] **§X Small Surface**: No new abstractions beyond what the catalogue schema and the shared term list require. `terms.py` is three frozensets and a canonical-form `MappingProxyType`; the renderer is a single function in `tools/render_catalogue.py`; the catalogue-validation test is a single module. No speculative helper, no deprecated-rule shim, no "reserved for Step 5" stub code in the rule modules. **PASS.**
- [x] **§XII Reproducible Corpus**: Precision claims derived from `eval-jss report` in this spec cite the corpus commit hash of `eval/corpus-manifest.csv` at the commit that closes each category. Phase-A corpus (hand-curated under `examples/`) is in use during early categories and its commit hash is the reproducibility anchor until Phase B of spec 002 lands pinned immutable distribution URLs for every paper. **PASS** (downstream consumer of spec 002's mechanism).

All gates PASS or documented N/A. **No Complexity Tracking entries required.**

Post-Phase-1 re-check (after writing research.md, data-model.md, contracts/, quickstart.md): all gates still PASS. The YAML-as-source-of-truth choice (Phase 0 §1) does not introduce a runtime dependency on the linter side (PyYAML is a dev extra), so §X's "no speculative helpers" and the no-new-runtime-deps constraint from spec 002 are both preserved. The rendered-markdown consistency test is one deterministic comparison, not a new abstraction.

## Project Structure

### Documentation (this feature)

```text
specs/003-jss-rule-catalogue/
├── plan.md                         # This file
├── research.md                     # Phase 0: format pin, renderer strategy, drift reconciliation
├── data-model.md                   # Phase 1: catalogue.yaml schema + terms.py API
├── quickstart.md                   # Phase 1: how to author a rule, category by category
├── catalogue.yaml                  # Authored during /speckit.implement (source of truth)
├── catalogue.md                    # Rendered from catalogue.yaml (generated artefact)
├── contracts/
│   ├── catalogue-schema.md         # Phase 1: YAML field types, enums, validation rules
│   ├── rules-module.md             # Phase 1: per-category module shape, rule export convention
│   ├── terms-list.md               # Phase 1: terms.py surface — frozensets + MappingProxyType
│   └── rendering.md                # Phase 1: sort order + markdown table format for the renderer
└── checklists/
    ├── requirements.md             # Spec quality checklist (from /speckit.specify)
    └── rule-catalogue-review.md    # Human sign-off rubric (from /speckit.checklist)
```

### Source Code (repository root)

```text
# Rule modules — one file per category, delete-and-rewrite migration of the three smoke rules
src/texlint/journals/jss/
├── __init__.py                     # JSSJournal.categories() grows: one import per category module
├── terms.py                        # NEW: shared canonical-form list (LANGUAGES, R_PACKAGES, CANONICAL, canonical_form())
└── rules/
    ├── __init__.py                 # unchanged
    ├── preamble.py                 # NEW
    ├── structure.py                # NEW
    ├── markup.py                   # NEW
    ├── citations.py                # NEW — subsumes cite_001_emph.py (deleted in same PR)
    ├── references.py               # NEW — subsumes bib_001_year.py (deleted in same PR, content-level BibTeX rules)
    ├── bibtex.py                   # NEW — mechanical BibTeX rules (missing key, malformed field, …)
    ├── naming.py                   # NEW
    ├── capitalization.py           # NEW
    ├── typography.py               # NEW
    ├── abbreviations.py            # NEW
    ├── code_style.py               # NEW
    ├── code_width.py               # NEW — subsumes src_001_width.py (deleted in same PR)
    ├── operators.py                # NEW
    ├── crossrefs.py                # NEW
    ├── house_style.py              # NEW
    ├── bib_001_year.py             # DELETED in the PR that adds references.py
    ├── cite_001_emph.py            # DELETED in the PR that adds citations.py
    └── src_001_width.py            # DELETED in the PR that adds code_width.py

# Catalogue renderer — stdlib + PyYAML; invoked as python -m tools.render_catalogue
tools/
├── __init__.py                     # NEW
└── render_catalogue.py             # NEW: catalogue.yaml → catalogue.md, deterministic sort + markdown table

# Tests — one per category + three catalogue/terms/render tests
tests/
├── unit/
│   ├── journals/
│   │   └── jss/
│   │       ├── __init__.py
│   │       ├── test_catalogue.py   # NEW: every row has authority; refs resolve; enums; no duplicate rule_ids
│   │       ├── test_terms.py       # NEW: CANONICAL values in LANGUAGES∪R_PACKAGES; rules don't redeclare tokens
│   │       └── test_render.py      # NEW: rendered catalogue.md matches what catalogue.yaml produces
│   └── rules/
│       ├── test_preamble.py        # NEW
│       ├── test_structure.py       # NEW
│       ├── test_markup.py          # NEW
│       ├── test_citations.py       # NEW — subsumes tests/unit/journals/jss/rules/test_cite_001_emph.py
│       ├── test_references.py      # NEW — subsumes bib-year test
│       ├── test_bibtex.py          # NEW
│       ├── test_naming.py          # NEW
│       ├── test_capitalization.py  # NEW
│       ├── test_typography.py      # NEW — subsumes src-width test
│       ├── test_abbreviations.py   # NEW
│       ├── test_code_style.py      # NEW
│       ├── test_code_width.py      # NEW
│       ├── test_operators.py       # NEW
│       ├── test_crossrefs.py       # NEW
│       └── test_house_style.py     # NEW
└── fixtures/
    └── violations/                 # NEW tree: one good/bad pair per rule
        ├── citations/
        │   ├── JSS-CITE-001-good.tex
        │   └── JSS-CITE-001-bad.tex
        ├── references/
        ├── …

# Packaging changes
pyproject.toml                      # [project.optional-dependencies] dev += ["PyYAML>=6.0"]
                                    # tool.hatch.build.targets.wheel.packages UNCHANGED
                                    # tool.hatch.build.targets.sdist.include += "tools"
```

**Structure Decision**: The catalogue is a **specification artefact** (lives under `specs/003-jss-rule-catalogue/`, not under `src/`); the **rule modules** are linter code (one per category under `src/texlint/journals/jss/rules/`). The `tools/render_catalogue.py` script is a top-level developer tool — not packaged into the wheel, parallel to how spec 002's `eval/` package is deliberately excluded from the wheel. YAML parsing is a dev extra (`PyYAML>=6.0`) so the `jss-lint` wheel's runtime dependency list is unchanged. The three Step 1 smoke rule files are **deleted** in the PRs that introduce their replacement categories (spec FR-024) — git history preserves the provenance via `git log --follow`; no compatibility shims.

## Complexity Tracking

No constitution gates are violated. **Table omitted.**
