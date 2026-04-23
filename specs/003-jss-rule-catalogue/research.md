# Phase 0 Research — JSS Rule Catalogue

Resolves the planning decisions that `/speckit.clarify` deferred to this stage, pins the drift-reconciliation answers that `plan.md §Summary` names, and captures the smaller trade-offs that shape `data-model.md` and the contracts.

## 1. Catalogue data-file format: YAML

**Decision**: The catalogue's source of truth is **YAML** (`specs/003-jss-rule-catalogue/catalogue.yaml`). PyYAML ≥ 6.0 is added as a dev extra; `jss-lint`'s runtime dependency list is unchanged.

**Rationale**:

- The catalogue holds LaTeX examples (`example_violation`, `example_fix`) that contain backslashes, braces, and quotation marks. YAML's `|` literal block scalar preserves these byte-for-byte without escape rules, so hand-authoring reads like the LaTeX the rule is meant to catch. TOML's triple-quoted strings (`"""..."""`) still apply a minimal escape (`\"`, `\\`), which turns every catalogue row into a visual fight with the escape sequence.
- YAML hand-authors better for the rule-row pattern: `- rule_id: ...` with nested fields at the same indent is less visually noisy than TOML's `[[rules]]` array-of-tables that repeats a header block per row.
- The read path uses PyYAML's `safe_load` — no arbitrary Python object construction, no `!!python/object` tags, no yaml 1.1 boolean surprises (PyYAML 6.0 defaults to safe behaviour).

**Alternatives considered**:

- **TOML (stdlib `tomllib`)** — no new dependency, read-only in Python ≥3.11. Rejected for LaTeX-readability reasons above; also, we already require Python ≥3.10 (spec 002's `pyproject.toml`), so `tomllib` would require either bumping the minimum Python to 3.11 or falling back to `tomli` (a third-party dep anyway, negating the "no new dep" win).
- **JSON** — stdlib-native, trivially machine-readable. Rejected because JSON has no multi-line string literal; every LaTeX example would be a single line with `\\n` escapes.
- **A Python module (`catalogue.py` with a list of dataclass instances)** — most ergonomic for tests (no parser needed), but the catalogue then *cannot* be reviewed by non-Python readers (e.g., a reviewer using the `rule-catalogue-review.md` checklist). The clarify session fixed the data-file-as-review-artefact principle in Q1; a Python module defeats that.
- **Sqlite** — overkill for ~50 rows, no meaningful query surface, unnecessarily opaque in PR diffs.

**Consequence**: The catalogue tests import `yaml`, the renderer imports `yaml`, and `PyYAML>=6.0` lands in `[project.optional-dependencies].dev`. Runtime linter code does not import `yaml` anywhere.

## 2. Markdown rendering strategy: one-shot script + consistency test

**Decision**: A single top-level script `tools/render_catalogue.py` loads `catalogue.yaml`, sorts entries by `(category, rule_id)`, and writes a deterministic markdown table to `catalogue.md`. A pytest (`tests/unit/journals/jss/test_render.py`) re-renders the YAML in memory and compares byte-for-byte to the committed `catalogue.md`; mismatch fails CI.

**Rationale**:

- Authors run `python -m tools.render_catalogue` after editing `catalogue.yaml`; the resulting `catalogue.md` lands in the same commit. Reviewers see both in the PR diff.
- The consistency test (not a pre-commit hook) keeps CI authoritative and avoids pre-commit configuration sprawl. If a contributor forgets to re-render, CI fails with a diff showing exactly what the renderer would produce.
- Stdlib + PyYAML only — no jinja template, no markdown library. The table is small enough to emit with string joins; the columns are fixed.

**Alternatives considered**:

- **Pre-commit hook that re-renders on every commit** — too easy to forget when editing outside pre-commit's scope (GitHub web UI, IDE-integrated commits). CI must be authoritative anyway; duplicating the check pre-commit adds maintenance without adding assurance.
- **Render on read in the test** (no `catalogue.md` file at all) — loses the PR-review signal; reviewers can't see what the catalogue looks like without running code.
- **Markdown as source of truth, YAML generated** — inverts clarify Q1. The markdown table is a poor hand-authoring format (pipe-escapes, cell-wrapping rules) and gives up structural validation. Rejected by the clarify decision.

**Consequence**: The renderer is one pure function `render(entries: list[dict]) -> str`, tested by the consistency test and by a small unit test fixture. No rendering templates.

## 3. Authority-ref resolvability strategy

**Decision**: Authority references are strings whose format is **mode-dependent** on the authority:

- `authority = jss_cls` → `authority_ref = "jss.cls:LINE"` or `"jss.cls:\\macroname"` (file name plus line number, or file name plus a `\macroname` that a `grep` finds on a unique line). Resolver parses either form; line-number form is verified by reading `docs/jss-template/jss.cls` and confirming `1 ≤ line ≤ len(lines)`; macroname form is verified by a fixed-string search that returns exactly one hit.
- `authority = article_tex` → same shape against `docs/jss-template/article.tex`.
- `authority = style_guide` → `authority_ref = "#anchor-id"` — a URL fragment matching `[a-z0-9-]+` exactly. Not dereferenced during CI (the URL is https://www.jstatsoft.org/style; the web page is in the devcontainer firewall allowlist but reaching it for a CI test is network-dependent flake-prone). The resolvability check is format-only: non-empty, starts with `#`, matches the anchor regex.
- `authority = author_instructions` → `authority_ref = "manuscript-preparation"` or a section heading string — same advisory check (non-empty, no line numbers, FR-010).

**Rationale**: Line numbers inside `docs/jss-template/` are stable across annual re-fetches only until upstream edits; the CI test catches breakage at refresh time, exactly when the maintainer should reconcile. URL-fragment anchors on the style guide are maintained by JSS editorially; a CI test that hits the network every run would fail whenever JSS is briefly unreachable, which is the wrong trade-off for a spec-kit flow. Format validation is a hard CI gate; content validation against the live URL is a manual step the reviewer does through the `rule-catalogue-review.md` checklist.

**Alternatives considered**:

- **Hit the live URL in CI** — catches anchor renames instantly but introduces network-dependent flakes. Dropped.
- **Snapshot the style-guide HTML** — vendored, fragile (JS-rendered anchors may not survive the fetch), and expands the "what must we vendor" scope. Dropped.
- **Fully-qualified URLs in `authority_ref`** — redundant with `authority`; the URL is derivable.

**Consequence**: `tests/unit/journals/jss/test_catalogue.py` has a `test_authority_refs_resolvable` that: for `jss_cls`/`article_tex` refs, verifies line number or macroname existence in the vendored file; for `style_guide`/`author_instructions` refs, verifies format only. An annual re-fetch of `docs/jss-template/` surfaces stale anchors through this test.

## 4. Rule export convention within category modules

**Decision**: Each `src/texlint/journals/jss/rules/<category>.py` exports a **module-level `rules: tuple[Rule, ...]`**. Individual check callables are private (`_check_jss_<category>_NNN`). The corresponding `Rule` object is constructed at module scope with `check=_check_jss_<category>_NNN`. `JSSJournal.categories()` imports each category module lazily and uses its `rules` tuple as the `RuleCategory.rules` field.

**Rationale**:

- Matches the existing smoke-rule pattern (each file has `rule = Rule(...)` at bottom) in shape; the only difference is plural `rules` tuple vs. singular `rule` object. Retrofit is trivial.
- "One source of truth per category" (spec FR-019): to answer "which rules does JSS run for category X?", read `rules/<category>.py`'s `rules` tuple. No decorators, no registry, no side effects at import time beyond constructing frozen dataclasses.
- Aligns with the spec FR-018 paraphrase of "each module exports `check_*` callables" while honouring the foundation's actual `RuleCheck = Callable[[ParsedDocument, ToolConfig], Iterator[Violation]]` signature (see `plan.md §Summary` drift reconciliation #1 and #2).

**Alternatives considered**:

- **One rule per file** (keep the smoke-rule pattern indefinitely) — works, but 50 files sprawl and the category-level "commit as a unit" boundary is weaker. Rejected by spec FR-018.
- **Decorator-based registry** (`@register_rule(...)`) — adds import-time side effects, makes "which rules run?" an opaque question, violates §IV's "zero ad-hoc registration".
- **`rules: list[Rule] = []` with side-effectful appends** — same as decorator, same rejection.

**Consequence**: `contracts/rules-module.md` pins the convention with a minimal example; `JSSJournal.categories()` grows to ~16 lazy imports.

## 5. Shared term-list shape

**Decision**: `src/texlint/journals/jss/terms.py` exports:

- `LANGUAGES: frozenset[str]` — canonical forms of programming language names that appear in JSS papers (`"R"`, `"Python"`, `"Java"`, `"Fortran"`, `"MATLAB"`, `"S-PLUS"`, `"Stata"`, `"SAS"`, `"Julia"`, `"C"`, `"C++"`, …).
- `R_PACKAGES: frozenset[str]` — a seed set of R-package names known to appear in the JSS corpus (`"MASS"`, `"ggplot2"`, `"knitr"`, `"pscl"`, `"mgcv"`, …). Grows as rules in `references`, `naming`, and `markup` need more coverage; a rule PR adds a term here, not in the rule module.
- `CANONICAL: Mapping[str, str]` (via `types.MappingProxyType`) — non-canonical-to-canonical lookup for case/spelling variants the style guide explicitly corrects: `"FORTRAN" → "Fortran"`, `"java" → "Java"`, `"JAVA" → "Java"`, `"Matlab" → "MATLAB"`, `"matlab" → "MATLAB"`, `"Splus" → "S-PLUS"`, `"S-Plus" → "S-PLUS"`, etc. Driven by the style guide's SG-044 through SG-052 (enumerated in `rule-catalogue-review.md`).
- `canonical_form(token: str) -> str | None` — returns `CANONICAL[token]` if present, or `token` if `token in LANGUAGES | R_PACKAGES` (already canonical), else `None`.

**Rationale**:

- `frozenset` matches the read-only shape and hashes cleanly in tests.
- `MappingProxyType` prevents accidental mutation of the canonical map at runtime while remaining a plain `dict`-shaped object (no `dataclass` overhead, no `enum`).
- `canonical_form` is the *only* public helper rule modules need (`capitalization` rules check `canonical_form(seen)` against `seen` and flag on mismatch; `naming` rules check `canonical_form(seen) is not None`).

**Alternatives considered**:

- **An `Enum` per category of term** — expresses the intent but every enum value requires a hand-picked name symbol (e.g., `Language.R`, `Language.S_PLUS`), which is more ceremony than the use site wants. Rules need string-to-string lookup, not symbol-to-string.
- **A YAML file mirroring the catalogue** — drift-prone against the Python rule modules that consume it, and terms are fundamentally code-adjacent (not spec artefacts) since they evolve with the rule implementations.

**Consequence**: `terms.py` is ~50 lines; `tests/unit/journals/jss/test_terms.py` asserts: (a) every `CANONICAL.values()` entry is in `LANGUAGES | R_PACKAGES`, (b) `canonical_form("Fortran") == "Fortran"` etc., (c) no rule module under `src/texlint/journals/jss/rules/` re-declares a token whose canonical form lives in `terms.py` (grep-heuristic with an explicit allowlist for rule modules that legitimately mention a term by name — documented on a case-by-case basis with a comment).

## 6. Fixture file layout

**Decision**: One good/bad fixture pair per rule, under `tests/fixtures/violations/<category>/<rule_id>-{good,bad}.tex` (or `.bib` for rules that inspect `bib_files`). Each fixture is a minimal self-contained LaTeX/BibTeX fragment — the smallest input that triggers the rule's path through the AST.

**Rationale**:

- Minimal fixtures are faster to read, faster to test, and easier to update when a rule narrows or relaxes. A single "sprawling" fixture per category would entangle rule coverage.
- One good and one bad per rule is the smallest set that proves the check both fires when it should and doesn't fire when it shouldn't — branch coverage plus a golden negative case.
- Co-locating fixtures with their rules (filename includes `rule_id`) keeps the traceability chain visible: reviewer opens `JSS-CITE-001-bad.tex`, reads `tests/unit/rules/test_citations.py`, reads `rules/citations.py`, reads `catalogue.yaml[0]`.

**Alternatives considered**:

- **Inline `textwrap.dedent` strings in the test file** — works for one-liners but LaTeX fragments grow; syntax-highlighted `.tex` files in the fixture tree diff better in PRs and let a reviewer preview-render if they want.
- **Property-based / hypothesis-driven fixtures** — overkill for a 50-rule enumeration; rules are authority-pinned, so generators don't improve confidence.
- **One fixture per category** — mixes rule concerns; a failing test in a mixed fixture is harder to attribute to a specific rule.

**Consequence**: ~100 small fixture files (50 × 2). Each is < 30 lines. `tests/fixtures/violations/<category>/README.md` in each subdir records the rule-id-to-file-pair mapping.

## 7. Category implementation order

**Decision**: Ship categories in this order (pinned from spec FR-017 and spec Assumptions, middle-11 ordered here by a mix of authority density and false-positive risk):

1. `citations` — style-guide-rich, high signal on the corpus, subsumes `cite_001_emph.py`.
2. `references` — BibTeX content rules; style guide is explicit; subsumes `bib_001_year.py`.
3. `bibtex` — BibTeX mechanics (missing key, malformed field); high-signal, low ambiguity.
4. `preamble` — `jss.cls`-grounded; authority is strong; rules are objective.
5. `structure` — `article.tex`-grounded; section ordering, required sections, label conventions.
6. `markup` — `\proglang`/`\pkg`/`\code` usage; spec covers this densely.
7. `crossrefs` — `\ref`/`\label` rules; easy to AST-check; low FP risk.
8. `code_style` — spacing around operators, `library("foo")` quoting; style-guide rules.
9. `code_width` — subsumes `src_001_width.py`.
10. `naming` — uses shared term list; SG-044..SG-052 directives.
11. `operators` — math conventions (`\top`, `p~value`).
12. `abbreviations` — SG-019, SG-020; uppercase-no-periods.
13. `house_style` — e.g./i.e. comma, "Section x.y" vs "Subsection x.y", 2nd/3rd edition.
14. `typography` — deliberately late (FP-prone); quote marks, dashes, emph misuse not covered by `citations`.
15. `capitalization` — deliberately last (most FP-prone); title vs sentence style, naming edge cases.

**Rationale**: The clarify session Q3 and spec Assumptions pin the head (`citations`, `references`) and tail (`typography`, `capitalization`). Middle ordering prioritises authority density (how explicit is the style guide?) and false-positive risk (how easy is it to mis-fire?). High-authority/low-FP categories ship first so the rule development loop picks up momentum on easy wins; FP-prone categories ship last so the corpus has grown and the precision gate has meaningful data.

**Alternatives considered**: Implementation-effort-first (simplest rules first, regardless of authority). Rejected because it does not maximise per-category corpus signal early.

**Consequence**: `tasks.md` (Phase 2, generated by `/speckit.tasks`) orders rule work by this sequence. `eval-jss report` precision data accrues in-order, so late categories benefit from a larger labelled corpus.

## 8. Python version and dependency floors

**Decision**: Python ≥3.10 (unchanged from specs 001/002). `PyYAML>=6.0` is added to `[project.optional-dependencies].dev` only. `jss-lint`'s runtime dependencies (pylatexenc, bibtexparser, click, rich) are **unchanged** — no new runtime dep, no Python floor bump.

**Rationale**: Keeping the runtime surface the same as Step 1 is a promise to downstream users. PyYAML is ubiquitous, stable, has no transitive dependency weight, and is only needed by contributors (tests + renderer). The linter binary remains minimal.

**Consequence**: `pyproject.toml` diff is one added dev-extra entry and the sdist-include addition for `tools/`.

---

## Summary of drift reconciliation (carried forward into `plan.md`)

1. **Rule-callable signature**: `Callable[[ParsedDocument, ToolConfig], Iterator[Violation]]` (foundation wins; spec paraphrase simplified).
2. **Rule export shape**: `rules: tuple[Rule, ...]` module-level tuple per category (bridges spec FR-018's `check_*` paraphrase with the foundation's `Rule` dataclass).

No outstanding `NEEDS CLARIFICATION` items at Phase 0 exit.
