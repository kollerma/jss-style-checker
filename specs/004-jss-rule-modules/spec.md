# Feature Specification: JSS Rule Modules — Category-by-Category Implementation of the Spec-003 Catalogue

**Feature Branch**: `004-jss-rule-modules`
**Created**: 2026-04-23
**Status**: Draft
**Input**: User description: "Implement the 58 JSS rule checkers enumerated in `specs/003-jss-rule-catalogue/catalogue.yaml` (Step 3b — JSS Rule Modules). Each category becomes one Python module under `src/texlint/journals/jss/rules/<category>.py` exporting `rules: tuple[Rule, ...]` at module scope; `JSSJournal.categories()` registers them in the rollout order fixed by spec 003's `tasks.md`."

## Clarifications

### Session 2026-04-23

- Q: How is the 15-category rollout organised into PRs — one-per-category, grouped, or hybrid? → A: **Flexible default — one PR per category, with an allowlist permitting small groups of ≤3 closely-related categories to ship together.** The default remains one PR per category (uniform review burden, per-category precision-gate clarity). The allowlist — documented in `tasks.md` and updated whenever a new group is proposed — permits categories that share an `inspects` field or a direct helper dependency to bundle: e.g., `references + bibtex` (both inspect `ParsedDocument.bib_files`), `markup + naming` (both consume `terms.py`). Groups MUST have ≤3 categories; a bundled PR still satisfies FR-004 / FR-012 / FR-010 per each contained category independently (catalogue consistency, precision gate, 100% branch coverage verified for every category the PR touches). Expected total: ~11–13 PRs for the full rollout.
- Q: Which mechanism does the catalogue-consistency test use to identify retired rule ids — a dedicated YAML field, or a grep-based scan of the top-of-file comment? → A: **Dedicated `retired_rule_ids` top-level field in `catalogue.yaml`.** The catalogue schema grows one new optional top-level key (`retired_rule_ids: list[str]`) with the same `^JSS-[A-Z]+-\d{3}$` regex validation as active rule ids. The existing top-of-file comment migrates into the structured field (JSS-CITE-001, JSS-ABBR-002); the comment can persist as narrative context but is no longer the test's data source. This change is a **spec-003 amendment** per FR-002 — the schema addition and migration land in a dedicated spec-003 PR that merges before any spec-004 category PR. `tools/_catalogue_validate.py` is extended to validate the new field (every entry matches the rule-id regex; no entry appears in the active `rules` list; `retired_rule_ids` is disjoint from the set of active ids). `JSSJournal` exposes the list so the catalogue-consistency test can key off it programmatically.
- Q: How is `eval/review-skip-list.toml` pre-populated at category-ship time — only FR-023's minimum 8 rules, or additional structurally-similar rules too? → A: **Pre-populate 14 rules total — FR-023's minimum 8 plus 6 structurally-similar additions.** The 6 additions (`JSS-REFS-002`, `JSS-REFS-006`, `JSS-ABBR-001`, `JSS-OPER-001`, `JSS-CAP-004`, `JSS-REFS-005`) share the "regex over English morphology" shape that spec 002 documented as Qwen3's labelling blind spot. Pre-populating them skips a known-unreliable AI pass and routes their corpus labelling directly to human review, saving a round of discarded AI labels. Additional skip-list entries MAY be added during the precision-gate loop when corpus data surfaces a new unreliable pattern; entries MUST NOT be removed from the skip-list without a documented rationale in the removing category PR's description.
- Q: What marks spec 004 as complete? → A: **15/15 categories implemented, every rule above the N=10 floor clears 90% precision, and every "not yet measured" rule has a documented re-measurement plan.** The three conditions are evaluated together. Rules with ≥10 labelled corpus violations must be above the gate at spec-004 close. Rules still in "not yet measured" at that point each carry a named path forward: a tracked issue (e.g., "re-measure JSS-BIBTEX-004 when corpus reaches 80 papers"), a scheduled precision-refresh run, or a spec-003 amendment proposing retirement if the rule genuinely can't accumulate enough signal. Spec 004 does not wait on corpus volume it doesn't control (rejecting the strict option), but every unmeasured rule has explicit hand-off (rejecting the lenient drop-it-and-move-on option).

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Authors can catch the majority of JSS style issues before submitting (Priority: P1)

A JSS author finishes a manuscript, runs `jss-lint` on the `.tex` + `.bib` pair, and sees every catalogued rule check their paper — every violation surfaced, every false-positive-prone rule narrow enough to hold its 90% precision gate on the evaluation corpus. Today the author only gets three smoke-rule checks (`cite_001_emph`, `bib_001_year`, `src_001_width`). After this spec lands, the author gets 58 checks covering preamble, structure, markup, citations, references, BibTeX mechanics, naming, capitalization, typography, abbreviations, code style, code width, operators, cross-references, and house style.

**Why this priority**: The catalogue in spec 003 is a contract with readers ("these are the rules `jss-lint` enforces") that currently promises far more than the tool delivers. Without rule-module implementation, the catalogue is documentation without enforcement — an IOU from the project. P1 because this is the **only** way the spec-003 catalogue becomes useful to authors.

**Independent Test**: From a clean checkout, run `jss-lint` against `docs/jss-template/article.tex` + `docs/jss-template/refs.bib` (the canonical JSS demo article). At the end of the rollout, the tool MUST emit zero violations against the canonical template (the template is by definition compliant) OR emit only violations that are explicitly documented as known-FP in the corresponding rule's `notes` field. Running against a deliberately-broken fixture that exercises one rule per category MUST surface the expected set of violations — no silent drops.

**Acceptance Scenarios**:

1. **Given** a manuscript that exercises every rule in the catalogue (one bad fixture per rule), **When** the author runs `jss-lint`, **Then** each rule's `rule_id` appears at least once in the output with the severity declared in `catalogue.yaml`.
2. **Given** the canonical JSS demo article at `docs/jss-template/article.tex`, **When** `jss-lint` is run, **Then** the tool emits no violations against it (or only violations whose rules are documented as known-FP against the template, with an explicit allowlist in test fixtures).
3. **Given** a manuscript where a `\pkg{mgcv}` call is cited later in the same paragraph via `\citep{Wood:2006}`, **When** `jss-lint` runs, **Then** JSS-CITE-002 does not fire. **When** the citation is moved to the next paragraph, **Then** JSS-CITE-002 fires on the `\pkg{mgcv}` position.
4. **Given** a manuscript that writes `(Knuth, 1984)` inside `\code{...}` or inside a `{verbatim}` environment, **When** `jss-lint` runs, **Then** JSS-CITE-004 does not fire on that occurrence (code/verbatim masking works).

---

### User Story 2 — Every rule earns its place via the corpus precision gate (Priority: P1)

A linter maintainer ships each category's rules only after the spec-002 `eval-jss` harness confirms that every rule in the category with ≥10 labelled corpus violations clears 90% precision. Rules with fewer than 10 labelled violations ship flagged "not yet measured" and are re-evaluated as the corpus grows. Rules above the N=10 floor and below 90% are refined (narrower heuristic, context masks, tighter AST predicates) or retired — retirement during spec 004 triggers a catalogue amendment back in spec 003 before the category commits.

**Why this priority**: Constitution §VI makes the 90% precision gate non-negotiable. Without the gate, the linter's reputation erodes: a noisy rule gets ignored, and so do the neighbouring good rules. The gate is what makes the rule catalogue an asset rather than a liability.

**Independent Test**: After any category's implementation PR lands, running `eval-jss scan && eval-jss human-review && eval-jss report` on the corpus shows, for every rule in that category with ≥10 labelled violations, a precision value ≥0.90. Rules with <10 labelled violations show "not yet measured". No rule in the committed catalogue shows precision <0.90 with ≥10 labelled violations.

**Acceptance Scenarios**:

1. **Given** a category whose implementation PR is open, **When** the reviewer runs `eval-jss report`, **Then** the report shows precision ≥0.90 for every rule in that category with ≥10 labelled violations. A PR with any rule below 0.90 is not merged.
2. **Given** a rule that fails the precision gate on first corpus labelling, **When** the implementer refines the rule, **Then** a second scan + label + report round shows the rule above 0.90 OR the rule is removed from the catalogue (via a spec-003 amendment PR that merges before this PR).
3. **Given** the corpus has grown to ~50 papers during the rollout, **When** a rule previously marked "not yet measured" now has ≥10 labelled violations, **Then** it is re-evaluated against the 90% gate and the category's status is updated if needed.

---

### User Story 3 — The three Step 1 smoke rules are cleanly retired or retrofitted (Priority: P2)

A contributor reading the repository today sees `src/texlint/journals/jss/rules/bib_001_year.py`, `cite_001_emph.py`, and `src_001_width.py` — three pre-catalogue modules that live outside the new per-category layout. After this spec's rollout, the repository has exactly one rule module per category, and the three legacy files are either retrofitted into their new category home (bib_001 → `references.py`, src_001 → `code_width.py`) or deleted outright (cite_001 → the JSS-CITE-001 rule it implemented was retired from the catalogue, so the file disappears with no replacement).

**Why this priority**: Not strictly required for correctness (the legacy files happen to share rule ids with the catalogue where applicable), but the duplication is confusing for contributors and blocks a clean "one file per category" mental model. Post-retrofit, the question "which file implements JSS-REFS-001?" has exactly one answer: `references.py`.

**Independent Test**: `ls src/texlint/journals/jss/rules/` shows exactly one `<category>.py` per category in `catalogue.yaml` plus `__init__.py`. No `bib_001_year.py`, `cite_001_emph.py`, or `src_001_width.py` files remain. The git log via `git log --follow` on each retired filename still surfaces the provenance.

**Acceptance Scenarios**:

1. **Given** the first citations-category PR has merged, **When** a reviewer runs `ls src/texlint/journals/jss/rules/`, **Then** `citations.py` is present, `cite_001_emph.py` is absent, and the corresponding test `tests/unit/journals/jss/test_cite_001_emph.py` is absent.
2. **Given** the references-category PR has merged, **When** a reviewer runs the full test suite, **Then** the tests previously in `test_bib_001_year.py` still exist in equivalent form in `tests/unit/rules/test_references.py` covering JSS-REFS-001.
3. **Given** the code_width-category PR has merged, **When** a reviewer checks the column-limit behaviour, **Then** the default is 80 columns (preserving `src_001_width.py`'s behaviour) AND the limit is configurable via `ToolConfig` per the JSS-WIDTH-001 note (a new capability).

---

### User Story 4 — The catalogue is the contract; implementation never contradicts it (Priority: P1)

A JSS author encounters a rule in their output, looks up the `rule_id` in `catalogue.yaml`, and finds the `description`, `severity`, `authority`, and `authority_ref` match exactly what the tool reported. No implementation drift. If a rule's runtime severity ever disagrees with the catalogue's severity, or a rule is registered under a `category` that disagrees with the catalogue's `category`, the build fails.

**Why this priority**: Spec 003 made significant effort to freeze the catalogue as the single source of truth. If spec 004's implementation contradicts it (even silently — e.g., a rule registered with severity `warning` when the catalogue says `error`), the spec-003 reviewer sign-off is meaningless. The automation that enforces consistency is cheap; the trust it preserves is load-bearing.

**Independent Test**: A CI test iterates `catalogue.yaml`'s `rules` list and for each entry, walks `JSSJournal.categories()` until it finds the matching `Rule` object, then asserts `rule.id == catalogue.rule_id AND rule.category == catalogue.category AND rule.severity == catalogue.severity AND rule.authority == catalogue.authority`. Any mismatch fails CI. A rule registered that is NOT in the catalogue (including retired ids) also fails CI.

**Acceptance Scenarios**:

1. **Given** a PR that ships a new rule module, **When** CI runs, **Then** the catalogue-consistency test passes (rule metadata matches catalogue).
2. **Given** a PR that accidentally registers `JSS-CITE-001` (a retired id), **When** CI runs, **Then** the catalogue-consistency test fails because the id is not in the active catalogue.
3. **Given** an implementation that registers `Rule(id="JSS-CITE-002", severity=Severity.ERROR, ...)` while the catalogue says `severity: warning` for CITE-002, **When** CI runs, **Then** the severity-mismatch test fails.

---

### Edge Cases

- **Rule in the catalogue is unimplementable in practice** (e.g., a heuristic that turns out to have unavoidable high FP rate on every corpus sample). The rule's implementation PR is blocked on the precision gate. The path forward is a spec-003 amendment (retire or refine the rule in the catalogue), NOT bypassing the gate in spec 004.
- **Retired rule id accidentally re-registered** in a category module after a future rename or cut-and-paste. The catalogue-consistency test (see US4) catches it at CI time; the retirement provenance in `catalogue.yaml`'s top-of-file comment is the evidence for the reviewer.
- **Corpus file that `jss-lint` cannot parse** (`JSS-PARSE-000` fires). Handled by spec 001's engine and spec 002's harness; this spec's rules do not see unparseable files.
- **Rule fixture that the catalogue's `example_violation` does not fully exercise** (e.g., a regex branch that requires a second example). Additional fixtures are added under `tests/fixtures/violations/<category>/<rule_id>-*.{tex|bib}` with descriptive suffixes; the catalogue's canonical good/bad pair remains the primary documentation example.
- **Category with a single rule** (currently `code_width` with `JSS-WIDTH-001`; post-retirement, `abbreviations` with `JSS-ABBR-001`). Single-rule categories are valid; the per-category module still exports a `rules: tuple[Rule, ...]` even if the tuple has length 1.
- **Rule whose authority is `jss_cls` or `article_tex`** at a line number that drifts after an annual re-fetch of the vendored template. The catalogue's `authority_ref` resolvability test (spec 003) catches line drift; fixing it is a spec-003 catalogue amendment, not a spec-004 implementation change.
- **Shared-term-list entry added during rule development** (e.g., a new R package surfaces in the corpus). The new term lands in `terms.py` as part of the category PR that first needs it, with cross-category precedence (`capitalization`, `naming`, `house_style`, `markup`) picking up the new entry automatically via the shared-list consumer policy from spec 003 FR-020.
- **AI review produces a low-precision label for a rule's violations** (e.g., AI rubber-stamps hard-to-classify cases). The rule id is added to `eval/review-skip-list.toml` (spec 002 FR-018) and the category PR waits on a human-only labelling pass before the precision gate is evaluated.
- **Rule module grows a private helper that ends up useful in another category** (e.g., an AST-walk that enumerates nodes with sibling context). The helper migrates to a shared `_ast_utils.py` or similar only when the constitution §X three-concrete-callers threshold is crossed — never speculatively.

## Requirements *(mandatory)*

### Functional Requirements

**Catalogue as contract**

- **FR-001**: Every rule in `specs/003-jss-rule-catalogue/catalogue.yaml` MUST be implemented as a `Rule` object registered through the per-category module whose name matches the catalogue row's `category`. The rule's `id`, `category`, `severity`, `message_template`, and `authority` fields MUST match the catalogue row byte-for-byte (after the catalogue value is mapped into the Python type — e.g., `severity: warning` in YAML maps to `Severity.WARNING` in Python).
- **FR-002**: Spec 004 MUST NOT modify `specs/003-jss-rule-catalogue/catalogue.yaml` or any other file under `specs/003-jss-rule-catalogue/`. Rule retirements, new rules, or note refinements discovered during implementation MUST be handled by a separate spec-003 amendment PR that merges before the dependent spec-004 PR.
- **FR-003**: Retired rule ids (`JSS-CITE-001`, `JSS-ABBR-002`, and any added during spec 004's rollout via the amendment path in FR-002) MUST NOT be registered by any rule module. Retired ids live in a dedicated `retired_rule_ids` top-level field in `catalogue.yaml` (added by a spec-003 amendment merging before spec-004's first category PR; see Session 2026-04-23 clarification). The CI consistency test MUST read this field and fail if any `Rule.id` in `JSSJournal.categories()` appears in it.
- **FR-004**: A CI consistency test MUST iterate `catalogue.yaml` and assert, for every rule row, that exactly one `Rule` object exists in `JSSJournal.categories()` with the matching id, and that the `Rule`'s category, severity, message_template, and authority match the catalogue values. Any drift fails CI.

**Module layout and rule registration**

- **FR-005**: Each category listed in `catalogue.yaml`'s top-level `categories` field MUST have exactly one Python module under `src/texlint/journals/jss/rules/<category>.py` exporting a module-level `rules: tuple[Rule, ...]`.
- **FR-006**: `JSSJournal.categories()` MUST be the single place where the active rule set is assembled. Each category is instantiated via `RuleCategory(id=<category>, title=<Title>, rules=<module>.rules)`. Rules MUST NOT register themselves via decorators, import-time side effects, or entry points; the `categories()` method is the source of truth.
- **FR-007**: `JSSJournal.categories()` MUST return the categories in the rollout order pinned in spec 003 `tasks.md`: `citations → references → bibtex → preamble → structure → markup → crossrefs → code_style → code_width → naming → operators → abbreviations → house_style → typography → capitalization`. Command-line output groups violations by this order.

**TDD and branch coverage**

- **FR-008**: For every rule in `catalogue.yaml`, the fixture pair `tests/fixtures/violations/<category>/<rule_id>-bad.{tex|bib}` and `<rule_id>-good.{tex|bib}` MUST exist before the rule's implementation is committed. Fixture contents are seeded from the catalogue row's `example_violation` / `example_fix` fields and wrapped into compilable documents.
- **FR-009**: The failing unit test MUST be committed (or visible in the in-progress branch) before the rule's check body is written. TDD order enforced by PR discipline; this spec does not mandate separate commits, but the failing-then-passing transition must be visible in the PR's history.
- **FR-010**: Each `src/texlint/journals/jss/rules/<category>.py` MUST achieve **100% branch coverage** in the corresponding `tests/unit/rules/test_<category>.py`. Coverage is measured by the project's standard tool (pytest-cov, `--cov-branch`) and enforced at ≥100% (no "≥99%" wiggle room). A CI gate MUST block any category PR that falls below 100%.
- **FR-011**: Additional fixture files beyond the canonical `-good`/`-bad` pair MAY be added under the same category directory when 100% branch coverage requires it. Naming convention: `<rule_id>-<descriptor>.{tex|bib}` where `<descriptor>` is a short hyphen-separated word indicating what additional path the fixture exercises (e.g., `JSS-CITE-004-in-verbatim.tex`, `JSS-PRE-003-no-markup.tex`).

**Precision gate per category**

- **FR-012**: Each category's implementation PR MUST run the spec-002 `eval-jss` harness end-to-end (`scan → human-review → report`) on the corpus at the PR's commit, and the PR description MUST include the resulting report summary. Every rule in the category with ≥10 labelled corpus violations MUST show precision ≥0.90 in that report before the PR merges.
- **FR-013**: Rules with <10 labelled corpus violations at the time of the category PR MUST ship flagged "not yet measured". Each such rule MUST carry a documented **re-measurement plan** — a tracked issue identifier, a corpus-milestone target (e.g., "re-measure at 80-paper corpus milestone"), a scheduled precision-refresh PR, or a spec-003 amendment proposing retirement if the rule genuinely cannot accumulate N=10 signal. Spec 004 does not close until every rule above the N=10 floor has cleared 90% precision **and** every rule still below N=10 has a re-measurement plan recorded (see SC-010).
- **FR-014**: Rules above the N=10 floor and below 90% precision MUST NOT ship. Remediation options, in order of preference: refine the rule (narrower heuristic, added context masks, tightened AST predicates); if refinement cannot reach 90%, open a spec-003 amendment to retire the rule (see FR-002); if neither path is viable, the category PR does not merge.

**Retrofit of Step 1 smoke rules**

- **FR-015**: The first citations-category PR (which ships `rules/citations.py`) MUST delete `src/texlint/journals/jss/rules/cite_001_emph.py` and `tests/unit/journals/jss/test_cite_001_emph.py` in the same commit. No retrofit: the rule the smoke module implemented (JSS-CITE-001) was retired in spec 003 2026-04-23.
- **FR-016**: The references-category PR MUST delete `src/texlint/journals/jss/rules/bib_001_year.py` and `tests/unit/journals/jss/test_bib_001_year.py` in the same commit that adds `rules/references.py` containing `JSS-REFS-001` with semantically-equivalent behaviour.
- **FR-017**: The code_width-category PR MUST delete `src/texlint/journals/jss/rules/src_001_width.py` and `tests/unit/journals/jss/test_src_001_width.py` in the same commit that adds `rules/code_width.py` containing `JSS-WIDTH-001` with the **configurable** column-limit behaviour (per the catalogue note; see FR-019).
- **FR-018**: Integration tests under `tests/integration/` that reference the flat fixture `tests/fixtures/violations/JSS-CITE-001.tex` MUST be updated or removed during the citations-category PR to not depend on a rule that no longer exists. If the fixture is still useful as a smoke-test input, it MAY be renamed or repurposed; if not, it is deleted.

**Implementation guidance from catalogue notes**

- **FR-019**: Implementation MUST honour the guidance in each rule's `notes` field in `catalogue.yaml`. Specifically:
  - `JSS-MARKUP-001`: skip math-mode content, skip Pascal, filter single-letter initials.
  - `JSS-CITE-002`: strict same-paragraph scope defined as the token span bounded by char nodes containing blank lines.
  - `JSS-CITE-004`: regex MUST mask `\code{}`, `\verb{}`, and the verbatim / Code / CodeInput / CodeOutput / Sinput / Soutput / Scode environments.
  - `JSS-WIDTH-001`: default column limit is 80, configurable via `ToolConfig`.
  - `JSS-OPER-003`: no-blank-line-around-equation carve-out when the equation body ends with a period.
  - `JSS-PRE-003`, `JSS-PRE-007`, `JSS-PRE-008`: fire only when the target command (`\title`, `\author`, `\Keywords`) contains LaTeX markup; presence-only case is silent.
  - All other rules follow their `notes` field verbatim.
- **FR-020**: Any deviation from a catalogue `notes` field (e.g., discovered to be wrong during corpus labelling) MUST be resolved by a spec-003 amendment (FR-002), not by silent divergence between implementation and notes.

**Shared term list**

- **FR-021**: Rule modules that inspect the canonical casing, canonical form, or proper-noun spelling of a token already recorded in `src/texlint/journals/jss/terms.py` MUST consume `terms.py` via the helpers spec 003 shipped (`terms.canonical_form()`, `terms.LANGUAGES`, `terms.R_PACKAGES`, `terms.CANONICAL`). Parallel or shadow term lists under `src/texlint/journals/jss/` MUST NOT be introduced. Spec 003's existing no-shadow-terms test is the enforcement mechanism.
- **FR-022**: New entries to `terms.py` (e.g., additional R packages observed in the corpus) land in the category PR that first needs them, with the change localised to `terms.py` plus the consuming test(s). No entry is added speculatively; every addition has at least one rule-module caller.

**AI-assisted review configuration**

- **FR-023**: Rules whose implementation shape makes AI labelling unreliable MUST be pre-populated in `eval/review-skip-list.toml` (spec 002 FR-018) before the category ships. Pre-population list pinned by Session 2026-04-23 clarification is **14 rules**: regex-with-context-masks (`JSS-CITE-004`), English-morphology heuristics (`JSS-CAP-001`, `JSS-CAP-002`, `JSS-CAP-003`, `JSS-CAP-004`), LaTeX macro substring patterns (`JSS-MARKUP-001`, `JSS-CODE-003`, `JSS-HOUSE-001`), and structurally-similar additions (`JSS-REFS-002`, `JSS-REFS-006`, `JSS-ABBR-001`, `JSS-OPER-001`, `JSS-REFS-005`). Additional skip-list entries MAY be added during the precision-gate loop when corpus data surfaces a new unreliable pattern; entries MUST NOT be removed from the skip-list without a documented rationale in the removing category PR's description.

**Out of scope**

- **FR-024**: `.Rnw` and `.Rmd` format narrowing MUST NOT ship in this spec. The `Rule.formats` field stays at `None` (all formats) for every new rule. Format narrowing is a future Step 4 spec.
- **FR-025**: Auto-fix payloads (`FixSuggestion` data) MUST NOT ship in this spec. Every emitted `Violation.fix` is `None`. Auto-fix implementation is a future Step 5 spec, but the `auto_fixable: true|false` flag in each catalogue row informs Step 5's prioritisation.
- **FR-026**: CRAN-backed package-name validation MUST NOT ship (spec 003 FR-023 is the controlling deferral; carried forward here for clarity).

### Key Entities

- **Rule Module**: One Python file per category under `src/texlint/journals/jss/rules/<category>.py`, exporting a module-level `rules: tuple[Rule, ...]`. The module's name and its `rules`' `category` field match the catalogue's category entry.
- **Rule Test Module**: One Python file per category under `tests/unit/rules/test_<category>.py`, covering 100% of the branches in the corresponding rule module. Tests use pytest fixtures (`parse_tex_source`, `run_rule`) already shipped in spec 001.
- **Fixture Pair**: `tests/fixtures/violations/<category>/<rule_id>-{good,bad}.{tex|bib}` — minimal LaTeX or BibTeX snippets that exercise the rule's firing and non-firing paths. Contents derive from the catalogue's `example_violation` / `example_fix`. Additional auxiliary fixtures follow the naming pattern in FR-011.
- **Category Commit Unit**: One PR per category (subject to the clarification question on commit cadence — see below). The PR includes the module, its tests, its fixtures, the `JSSJournal.categories()` wiring, the precision-gate report, any smoke-rule deletions, and any `terms.py` additions. Passes CI including 100% branch coverage AND catalogue-consistency tests AND the per-category precision gate.
- **Precision-Gate Report**: The `eval-jss report` output for the corpus at the category PR's commit. Attached to the PR description; every `≥10` rule in the category must show precision ≥0.90.
- **Catalogue Consistency Test**: CI-resident test that iterates `catalogue.yaml` and asserts every row has a matching registered `Rule` with matching metadata, and that no retired rule id appears in the registered set. Lives under `tests/unit/journals/jss/test_catalogue_registration.py` or similar.
- **AI Skip-List Entry**: A row in `eval/review-skip-list.toml` recording a `rule_id` for which AI labelling is unreliable. Populated by FR-023 at category-ship time; maintained as corpus labelling experience accrues.
- **Retired Rule Id**: A `rule_id` that once appeared in the catalogue and has been retired (currently `JSS-CITE-001`, `JSS-ABBR-002`). Reserved permanently per spec 003 FR-004; never re-registered by any rule module; CI enforces non-registration.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Running `jss-lint` against a synthetic manuscript containing one minimal `-bad` fixture per rule from the catalogue produces exactly one violation per rule, with `rule_id` matching the fixture's target rule. Zero rules are missing, zero rules fire twice, zero unexpected rules fire.
- **SC-002**: Running `jss-lint` against `docs/jss-template/article.tex` + `docs/jss-template/refs.bib` (the canonical JSS demo article) produces zero violations (or only violations whose rules are explicitly listed in a test allowlist with rationale, such as the author's template-demonstration use of `\emph`).
- **SC-003**: For every category that has shipped, `eval-jss report` on the corpus at the shipping commit shows precision ≥0.90 for every rule in the category with ≥10 labelled violations. Zero rules in the shipped set are above the N=10 floor and below 90%.
- **SC-004**: `pytest --cov=src/texlint/journals/jss/rules --cov-branch --cov-fail-under=100` passes. Every rule module under `src/texlint/journals/jss/rules/` has 100% branch coverage; no exceptions.
- **SC-005**: `ls src/texlint/journals/jss/rules/*.py | grep -v __init__` returns exactly one file per active category in `catalogue.yaml` — no stale smoke rule modules, no orphaned category files.
- **SC-006**: The catalogue-consistency test passes: every rule in `catalogue.yaml` has a matching `Rule` registered in `JSSJournal.categories()`; every `Rule` registered matches a catalogue row; no retired id appears in the registered set; category / severity / message_template / authority match the catalogue for every rule.
- **SC-007**: `eval/review-skip-list.toml` lists every rule whose AI labelling precision is known to be low, at minimum covering the rules enumerated in FR-023. Adding or removing an entry from the skip-list is a documented change in a category PR.
- **SC-008**: At the close of spec 004, the three Step 1 smoke rule files (`bib_001_year.py`, `cite_001_emph.py`, `src_001_width.py`) and their tests (`test_bib_001_year.py`, `test_cite_001_emph.py`, `test_src_001_width.py`) are all deleted. `git log --follow` on any of them surfaces the retrofit provenance commits.
- **SC-009**: A contributor opening a PR that accidentally registers a retired rule id (e.g., `JSS-CITE-001`), sets an incorrect severity (e.g., `error` where the catalogue says `warning`), or forgets to add a new rule's `Rule` object to the module's `rules` tuple fails CI with a diagnostic message pointing at the specific drift. Zero spec-004 PRs merge with silent consistency drift.
- **SC-010**: Spec 004 closes with 15/15 categories implemented. At close: (a) every rule with ≥10 labelled corpus violations has precision ≥0.90 on the corpus; (b) every rule with <10 labelled violations has a documented re-measurement plan (issue id, corpus milestone, precision-refresh schedule, or retirement proposal). Zero rules are "not yet measured" without a plan attached.

## Assumptions

- **Catalogue is frozen at spec 003's final commit.** Spec 004 treats `specs/003-jss-rule-catalogue/catalogue.yaml` as a stable input. Amendments are handled by a separate spec-003 PR that merges before a dependent spec-004 PR (FR-002).
- **Per-category PR is the default commit unit.** The `/speckit.clarify` stage may revisit this (see Clarification Targets below); until then, one category per PR is assumed. This matches the rollout cadence spec 003 `tasks.md` schedules.
- **`eval-jss` corpus grows to ~50 papers during the rollout**, per spec 003's 2026-04-23 clarification. Corpus growth is scheduled within this spec's task list.
- **Constitution constraints inherit unchanged from spec 003.** §I Determinism, §II AST-first, §V Authority cited, §VI Precision gate, §VIII TDD, §IX 100% branch coverage, §X Small surface all apply. Any deviation is a Complexity Tracking entry in plan.md, not a silent break.
- **Reviewer role is out of scope for this spec.** Whether review labelling is a single person, a team, or partial automation via `eval-jss review` is operational scope; this spec only defines what "labelled" means (rows with non-NULL `verdict` in the `violations` table from spec 002).
- **Shared-term-list evolution is additive.** Spec 003 shipped `terms.py` with seed content; spec 004 rules MAY add new languages / packages / aliases as needed, but MUST NOT remove or rename existing entries without a spec-003 amendment (changes to canonical spellings cross-cut multiple rule modules).
- **Prior-art lessons from the reverted Phase 5 (commit `3379299`)** — pylatexenc's default macro context behaviour for unknown macros (sibling-group binding), the 400-char paragraph heuristic being too loose, the missing code/verbatim mask for JSS-CITE-004 — are documented in the spec 003 branch history and are expected to inform Phase 0 research during `/speckit.plan`.

## Clarification Targets

Items deliberately left open for `/speckit.clarify` (max 3):

1. **Per-category commit cadence** — *resolved 2026-04-23 (Session 2026-04-23): Flexible default, one PR per category with a ≤3-category allowlist for closely-related groups. See Clarifications.*

2. **Retired-rule-id registration guard** — *resolved 2026-04-23 (Session 2026-04-23): Dedicated `retired_rule_ids` top-level field in `catalogue.yaml`, added via a spec-003 amendment. See Clarifications.*

3. **AI skip-list pre-population** — *resolved 2026-04-23 (Session 2026-04-23): 14 rules total (FR-023's 8 + 6 structurally-similar additions). See Clarifications.*
