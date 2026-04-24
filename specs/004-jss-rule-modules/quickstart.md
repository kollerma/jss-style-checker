# Quickstart — JSS Rule Modules

Hands-on onboarding for a contributor implementing or refining a rule module. Assumes `pip install -e '.[dev]'` has been run once and the devcontainer firewall allowlist is current.

## 0. One-time prep

```bash
# From repo root — install dev extras (PyYAML needed by codegen + tests)
pip install -e '.[dev]'

# Verify the catalogue data generator works
python -m tools.generate_catalogue_data --check

# Verify the eval harness is functional (spec 002)
eval-jss --help

# Verify spec 003's reviewer sign-off is in `catalogue.yaml`'s commit history
git log --oneline specs/003-jss-rule-catalogue/catalogue.yaml | head -5
```

Expected: all four commands succeed silently (or print a small help message). If `generate_catalogue_data --check` emits drift, run `python -m tools.generate_catalogue_data` to regenerate the committed `_catalogue_data.py`.

## 1. Bootstrap the foundational Phase 2 setup (one-time for spec 004)

Before the first category PR, three small foundational changes must land:

### 1.1 Add `Severity.INFO`

Edit `src/texlint/api.py`:

```python
class Severity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"        # NEW
```

Audit the output renderers and eval harness — run:

```bash
grep -rn "Severity\." src/texlint/output/ eval/ | grep -v test_
```

Confirm each match treats INFO sensibly. Default: render INFO the same as WARNING in author/reviewer terminal output; surface separately in `eval-jss report`.

### 1.2 Generate `_catalogue_data.py`

```bash
python -m tools.generate_catalogue_data
git add src/texlint/journals/jss/_catalogue_data.py
```

Commit the generated file. The drift-check test (`test_catalogue_data_fresh.py`) runs in CI.

### 1.3 Add `_helpers.py`

Copy the canonical template from `contracts/rules-module.md` §Helpers. Write 100% branch coverage tests in `tests/unit/journals/jss/rules/test_helpers.py`. Verify:

```bash
scripts/vtest.sh tests/unit/journals/jss/rules/test_helpers.py \
    --cov=src/texlint/journals/jss/rules/_helpers \
    --cov-branch --cov-fail-under=100
```

### 1.4 Add the catalogue-registration CI test

Copy from `contracts/catalogue-consistency.md` into `tests/unit/journals/jss/test_catalogue_registration.py`. Tests will ALL FAIL at this stage because no category modules exist yet — that's expected. They pass after the first category PR lands.

**Gate**: do NOT start Phase 3 (category rollout) until `test_helpers.py` is 100% green and CI marks `test_catalogue_registration.py` as "xfail" or similar until the rollout starts.

## 2. Implement a category (per-category loop, ~1–3 days each)

Follow the rollout order in `tasks.md`. Example below uses `citations` (rollout position #1, 3 rules, retrofits `cite_001_emph.py` by deleting it).

### 2.1 Build the fixture pair per rule

For each rule in the category's catalogue entries, write:

```bash
# tests/fixtures/violations/citations/JSS-CITE-002-bad.tex
cat > tests/fixtures/violations/citations/JSS-CITE-002-bad.tex <<'EOF'
\documentclass[article]{jss}
\begin{document}
We use \pkg{mgcv} for the GAM analysis.
\end{document}
EOF

cat > tests/fixtures/violations/citations/JSS-CITE-002-good.tex <<'EOF'
\documentclass[article]{jss}
\begin{document}
We use \pkg{mgcv} \citep{Wood:2006} for the GAM analysis.
\end{document}
EOF
```

The bad fixture's content is derived from the catalogue's `example_violation` wrapped in a compilable document; the good fixture uses `example_fix`.

### 2.2 Write the failing test (TDD)

Copy the template from `contracts/test-template.md`. Write at least:
- one positive test per rule (bad fixture → 1 violation);
- one good-fixture negative test per rule (good fixture → 0 violations);
- one near-miss negative per rule (adjacent-but-OK input → 0 violations).

Run it — it MUST fail because the category module doesn't exist yet:

```bash
scripts/vtest.sh tests/unit/rules/test_citations.py
# Expected: ImportError on `from texlint.journals.jss.rules.citations import ...`
```

Commit the failing test (or at least stage it) before writing the implementation. This is the §VIII TDD red step visible in PR history.

### 2.3 Implement the rule module

Copy the template from `contracts/rules-module.md`. Replace the `_condition()` placeholder with the actual check logic for each rule. Keep:
- each `check_<rule_id>` callable as a pure function of `(ParsedDocument, ToolConfig)`;
- each `Rule` constructed via the `_rule(rule_id, check_fn)` helper that pulls metadata from `_catalogue_data.RULES`;
- the module-level `rules: tuple[Rule, ...]` assembling every rule;
- no module-level state beyond the Rule objects.

For `citations` specifically, in the same commit:
- delete `src/texlint/journals/jss/rules/cite_001_emph.py`;
- delete `tests/unit/journals/jss/test_cite_001_emph.py`;
- audit `tests/integration/test_cli_*.py` for references to `tests/fixtures/violations/JSS-CITE-001.tex` and update / remove as needed (FR-018).

Rerun tests:

```bash
scripts/vtest.sh tests/unit/rules/test_citations.py
# Expected: green
```

### 2.4 Wire into `JSSJournal.categories()`

Spec 004's foundational task has already written the skeleton of `JSSJournal.categories()` with all 15 lazy imports; it works as soon as each category's module exists. When your category's module lands, the next call to `categories()` picks it up automatically. Verify:

```bash
scripts/vtest.sh tests/unit/journals/jss/test_catalogue_registration.py
# Expected: green (catalogue ↔ registered rules match for your category)
```

### 2.5 Verify 100% branch coverage

```bash
scripts/vtest.sh tests/unit/rules/test_citations.py \
    --cov=src/texlint/journals/jss/rules/citations \
    --cov-branch --cov-fail-under=100
```

Any branch below 100% → write a targeted fixture that exercises it (auxiliary fixture name: `JSS-CITE-NNN-<descriptor>.tex`). Loop until green.

### 2.6 Pre-populate the AI skip-list (if the category owns an entry)

If your category owns one of the 13 pre-populated AI-skip entries (see `contracts/ai-skip-list.md`), add the `[[rules]]` block to `eval/review-skip-list.toml` in the same PR. For `citations`, that's `JSS-CITE-004`.

### 2.7 Run the per-category precision gate

```bash
scripts/eval-category.sh citations
```

This wraps:
- the 100% branch-coverage test;
- `eval-jss scan` over the corpus;
- `eval-jss human-review` — **human interaction required** here; label each new violation as true-positive / false-positive;
- `eval-jss report --grep=JSS-CITE-` — view the per-rule precision.

For every rule in the category with ≥10 labelled corpus violations, confirm precision ≥ 0.90. If a rule falls below 0.90:
- refine the rule (narrower heuristic, added context masks, tightened AST predicate);
- OR open a spec-003 amendment to retire the rule (rare; requires reviewer sign-off);
- OR if the path forward isn't clear, document the failure and land a "precision-refresh PR" later once the corpus grows.

Rules with <10 labelled violations ship as "not yet measured" per FR-013, with a documented re-measurement plan (issue, corpus milestone, or scheduled refresh) recorded in the PR description.

### 2.8 Commit the category

```bash
git add \
    src/texlint/journals/jss/rules/citations.py \
    tests/unit/rules/test_citations.py \
    tests/fixtures/violations/citations/ \
    eval/review-skip-list.toml
git rm \
    src/texlint/journals/jss/rules/cite_001_emph.py \
    tests/unit/journals/jss/test_cite_001_emph.py

# If integration tests changed:
git add tests/integration/test_cli_*.py

git commit -m "[Spec Kit] Implement citations category (JSS-CITE-002/003/004)

...
Precision-gate report (paste from eval-jss report):
  JSS-CITE-002: precision 0.94 (16 TP / 17 labelled)
  JSS-CITE-003: precision 1.00 (4 labelled; not yet measured — see #NNN)
  JSS-CITE-004: precision 0.92 (12 TP / 13 labelled; added to skip-list)

Co-Authored-By: ..."
```

Open the PR. Reviewer consumes the precision-gate report from the commit message; CI enforces 100% branch coverage and catalogue consistency.

## 3. Maintaining the rollout over time

### 3.1 If the catalogue changes

The catalogue is frozen at spec 003's close. Changes (retirements discovered during implementation, note refinements) require:

1. A spec-003 amendment PR that edits `catalogue.yaml` and lands first.
2. Regenerate `_catalogue_data.py` via `python -m tools.generate_catalogue_data` in the amendment PR.
3. The depending spec-004 PR then uses the new catalogue state.

### 3.2 If a precision-gate re-measurement flips a rule

A rule that was "not yet measured" at the close of its category PR may, as the corpus grows, cross the N=10 floor. A future precision-refresh PR:

1. Runs `eval-jss report` on the current corpus;
2. Confirms the re-measured rule's precision ≥ 0.90;
3. Removes the rule's "not yet measured" flag (if the output renderer tracks one);
4. Updates the re-measurement plan tracker (issue / milestone).

Per spec 004 SC-010, spec 004 closes when every rule is either cleared or has a documented re-measurement plan — no open "not yet measured" rules without attached plans.

### 3.3 Adding an entry to `terms.py` during rule work

Per spec 003 FR-020 open-consumer policy. Add the term to the appropriate frozenset or the `CANONICAL` mapping. Verify:

```bash
scripts/vtest.sh tests/unit/journals/jss/test_terms.py
```

100% branch coverage on `terms.py` is inherited from spec 003; changes should preserve it.

## 4. Common failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| `test_catalogue_data_fresh.py` fails | catalogue.yaml was amended but `_catalogue_data.py` wasn't regenerated | `python -m tools.generate_catalogue_data && git add src/texlint/journals/jss/_catalogue_data.py` |
| `test_catalogue_registration.py` R-1 fails with missing id | new catalogue rule lacks a category-module registration | add `jss_<cat>_<nnn> = _rule("JSS-<CAT>-NNN", check_jss_<cat>_<nnn>)` to the category module |
| `test_catalogue_registration.py` R-3 fails with retired id | accidentally registered a retired rule | delete the registration; retired rule ids are in `_catalogue_data.RETIRED_RULE_IDS` |
| 100% branch coverage not reached | an uncovered branch exists | add an auxiliary fixture + test for that branch |
| `eval-jss report` shows a rule at <0.90 precision | rule fires on false positives | tighten the AST predicate; add context masks; or open a retirement amendment |
| `ImportError` on rule module load | `_catalogue_data.py` doesn't have the rule id your module references | regenerate `_catalogue_data.py` from the current catalogue |
| Rule module registers but `test_catalogue_registration.py` R-4 fails | module hardcoded a field instead of pulling from `_catalogue_data.RULES[rule_id]` | use the `_rule(rule_id, check_fn)` helper exactly as in the template |

## 5. End-of-spec checkpoint

Spec 004 closes when:

1. All 15 categories have shipped (one per PR or grouped per §5 of `research.md`'s allowlist). `git log --oneline --grep='\[Spec Kit\]' | wc -l` shows ~12 category PRs.
2. `JSSJournal().categories()` returns 15 `RuleCategory`s with 58 total rules.
3. `test_catalogue_registration.py` is green.
4. `pytest --cov=src/texlint/journals/jss/rules --cov-branch --cov-fail-under=100` is green across every rule module.
5. `eval-jss report` shows, for every rule with ≥10 labelled corpus violations, precision ≥0.90.
6. Rules still at "not yet measured" each have a documented re-measurement plan (SC-010).
7. `eval/review-skip-list.toml` contains the 13 pre-populated entries (or more if corpus experience added to them).

At that point the spec's `rule-catalogue-review.md`'s sign-off block can be fully checked (the one remaining item from spec 003's closure — OQ-11 corpus growth — has been resolved via the rollout).
