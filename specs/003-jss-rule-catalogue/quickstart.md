# Quickstart — JSS Rule Catalogue

Hands-on onboarding for a contributor adding or refining rules under this spec. Assumes `pip install -e '.[dev]'` has been run once and the devcontainer's firewall whitelist includes `www.jstatsoft.org` (already configured — see `.devcontainer/init-firewall.sh`).

## 0. One-time prep

```bash
# From repo root — install the dev extras so PyYAML is available for the renderer
pip install -e '.[dev]'

# Verify the two vendored files the catalogue cites
ls docs/jss-template/jss.cls docs/jss-template/article.tex

# Verify the eval harness is functional (spec 002 — we'll use it for the precision gate)
eval-jss --help
```

## 1. Draft the catalogue (first-time, ~1–2 days)

The catalogue lives at `specs/003-jss-rule-catalogue/catalogue.yaml`. Draft it top-down: each of the ~16 categories in turn, each category's rules derived from the enumerated provisions in `specs/003-jss-rule-catalogue/checklists/rule-catalogue-review.md` §1.1–1.4.

For every rule:

1. Pick the highest-authority justification (`jss_cls > article_tex > style_guide > author_instructions`).
2. Write a one-line `description` that reads like a violation sentence ("`\emph` used where a citation key is meant; use `\cite`").
3. Write a minimal `example_violation` — the smallest LaTeX fragment that would fire the rule.
4. Write the corresponding `example_fix` — the same fragment with the rule's complaint addressed.
5. Set `inspects` to whichever `ParsedDocument` field the check will read.
6. Set `auto_fixable` to `true` if the fix is mechanically expressible, `false` otherwise.

Then render and validate:

```bash
python -m tools.render_catalogue
pytest tests/unit/journals/jss/test_catalogue.py -x
```

The first command writes `catalogue.md`; the second asserts every catalogue invariant (unique ids, resolvable authorities, enum membership). If anything fails, fix the YAML and re-run.

When a full draft is in hand, walk through `specs/003-jss-rule-catalogue/checklists/rule-catalogue-review.md` once to fill in the `covering_rule_ids` column for every provision in §1.1–1.4. Gaps and redundancies surface here; either close them (add/merge rules) or mark `out-of-scope` with a rationale.

## 2. Implement a category (per-category loop, ~1–3 days each)

Category order is pinned in `contracts/rules-module.md §Category rollout order`: `citations` first, `capitalization` last. Work one category at a time; don't fan out.

For each category (example: `citations`):

### 2.1 Add fixtures (TDD §VIII)

For each rule the catalogue lists in this category:

```bash
mkdir -p tests/fixtures/violations/citations
# JSS-CITE-001 — paste example_violation from catalogue.yaml
cat > tests/fixtures/violations/citations/JSS-CITE-001-bad.tex <<'EOF'
Recently \emph{Knuth1984} described algorithms.
EOF
# JSS-CITE-001 — paste example_fix from catalogue.yaml
cat > tests/fixtures/violations/citations/JSS-CITE-001-good.tex <<'EOF'
Recently \cite{Knuth1984} described algorithms.
EOF
```

### 2.2 Add the failing test

```bash
# tests/unit/rules/test_citations.py
cat > tests/unit/rules/test_citations.py <<'EOF'
from pathlib import Path
from texlint.journals.jss.rules import citations

FIXTURES = Path(__file__).parent.parent.parent / "fixtures" / "violations" / "citations"

def test_jss_cite_001_flags_bad(parse_tex):
    doc = parse_tex(FIXTURES / "JSS-CITE-001-bad.tex")
    violations = list(citations._check_jss_citations_001(doc, cfg=None))
    assert len(violations) == 1
    assert violations[0].rule_id == "JSS-CITE-001"

def test_jss_cite_001_passes_good(parse_tex):
    doc = parse_tex(FIXTURES / "JSS-CITE-001-good.tex")
    violations = list(citations._check_jss_citations_001(doc, cfg=None))
    assert violations == []
EOF

pytest tests/unit/rules/test_citations.py -x
# Expected: ImportError or AttributeError — citations module / rule callable does not exist yet.
```

### 2.3 Implement the rule module

`src/texlint/journals/jss/rules/citations.py` — see `contracts/rules-module.md §Module shape` for the canonical template. Write the private `_check_jss_citations_001` callable; construct the `Rule`; add it to the module-level `rules` tuple.

```bash
pytest tests/unit/rules/test_citations.py -x
# Expected: both tests pass.
```

### 2.4 Wire into `JSSJournal.categories()`

`src/texlint/journals/jss/__init__.py` — add the lazy import and the `RuleCategory` entry. See `contracts/rules-module.md §JSSJournal.categories() integration`.

The first time you add a category that subsumes a Step 1 smoke rule (`citations` subsumes `cite_001_emph.py`, `references` subsumes `bib_001_year.py`, `code_width` subsumes `src_001_width.py`), delete the old module and its test in the same commit (spec FR-024).

### 2.5 Enforce 100% branch coverage (§IX)

```bash
pytest --cov=src/texlint/journals/jss/rules/citations --cov-branch \
       --cov-fail-under=100 tests/unit/rules/test_citations.py
```

If any branch is unreached, add a fixture that exercises it. A module that cannot hit 100% has a branch that is unreachable (dead code to delete) or under-tested (missing fixture).

### 2.6 Run the precision gate (§VI)

```bash
# From repo root
eval-jss scan
eval-jss human-review         # label the new violations from this category
eval-jss report
```

For every rule in the category:

- If the rule has **≥ 10 labelled violations** on the corpus, confirm precision ≥ 90%. If below, refine the rule (tighten the match, add narrowing conditions) or relax it (widen, then re-measure); if it cannot clear the bar, retire it.
- If the rule has **< 10 labelled violations**, accept the "not yet measured" state. The gate is advisory for this rule until the corpus grows.

The clarify Q3 decision pins N=10 as the minimum sample size; spec 002's corpus grows toward ~50 papers so the floor becomes attainable for most rules.

### 2.7 Commit the category

Once every rule in the category satisfies §IX (branch coverage) and §VI (precision gate where sampled):

```bash
git add src/texlint/journals/jss/rules/<category>.py \
        tests/unit/rules/test_<category>.py \
        tests/fixtures/violations/<category>/

# If this category subsumes a Step 1 smoke rule, stage the deletions too
git rm src/texlint/journals/jss/rules/<smoke_rule>.py \
       tests/unit/journals/jss/rules/test_<smoke_rule>.py

git add src/texlint/journals/jss/__init__.py

git commit -m "Step 3 / feature 003: implement <category> rules

Catalogue rows: JSS-<CAT>-001 … JSS-<CAT>-NNN. Branch coverage 100%.
Precision gate: <X> rules ≥ 90% on the corpus (commit <hash>), <Y> rules
'not yet measured' (N<10 labelled violations)."
```

## 3. Maintain the catalogue over time

### 3.1 Add a term to the shared list

When a new rule needs to know the canonical form of a token already observed in the corpus:

```bash
# Edit src/texlint/journals/jss/terms.py:
#   - add the canonical to LANGUAGES or R_PACKAGES
#   - add non-canonical → canonical mapping(s) in CANONICAL

pytest tests/unit/journals/jss/test_terms.py -x
# The invariants T-01..T-06 (contracts/terms-list.md) run here.
```

### 3.2 Re-render after any catalogue edit

```bash
python -m tools.render_catalogue
git add specs/003-jss-rule-catalogue/catalogue.yaml specs/003-jss-rule-catalogue/catalogue.md
```

Forgetting to re-render is a CI failure (the `--check` variant of the renderer is equivalent to `tests/unit/journals/jss/test_render.py`).

### 3.3 Annual refresh of `docs/jss-template/`

Once a year (or whenever upstream JSS announces a template update):

```bash
# Fetch the new zip
curl -O https://www.jstatsoft.org/public/journals/1/jss-article-tex.zip

# Verify the hash matches what the new provenance README will record
sha256sum jss-article-tex.zip

# Extract and diff against the vendored copy
unzip -d /tmp/jss-new jss-article-tex.zip
diff -u docs/jss-template/jss.cls /tmp/jss-new/jss.cls
diff -u docs/jss-template/article.tex /tmp/jss-new/article.tex

# If changes: update the vendored files, bump source_vendored_at in catalogue.yaml,
# and walk every rule whose authority_ref lands in a changed region to confirm the
# anchor still resolves. Re-run tests.
pytest tests/unit/journals/jss/test_catalogue.py -x
```

## 4. Common failure modes and fixes

| Symptom | Likely cause | Fix |
|---|---|---|
| `test_catalogue.py` fails with "authority_ref unresolvable" | Line number in `jss.cls` / `article.tex` drifted after re-fetch | Re-read the vendored file; update `authority_ref` to the new line. |
| `test_render.py` fails with a big diff | Forgot to re-render after editing `catalogue.yaml` | `python -m tools.render_catalogue` then re-commit. |
| `test_terms.py` invariant T-06 fails | A rule module inlines a string that `terms.py` already knows | Import `terms` in the rule module and use `terms.canonical_form(...)`. |
| A rule passes unit tests but flags many FPs on the corpus | Rule's match condition is too broad | Narrow the AST predicate; add a negative fixture; re-measure precision. |
| A rule's precision is 1/1 = 100% | N < 10; rule is in the "not yet measured" bucket | Accept for now; corpus growth will re-evaluate. |
| `JSSJournal.categories()` imports fail on startup | A new category module's `rules` tuple references a missing `_check_*` callable | Fix the missing callable or remove the stale entry from the tuple. |

## 5. When you're done

- `catalogue.yaml` enumerates every rule cited by an authority (no speculative rules — spec §Edge Cases).
- `catalogue.md` is up to date with `catalogue.yaml` (re-render if in doubt).
- Every category has a `rules/<category>.py`, a `test_<category>.py`, and fixtures under `tests/fixtures/violations/<category>/`.
- The three Step 1 smoke rule modules and their tests are deleted.
- `JSSJournal.categories()` assembles the 15 new categories in rollout order.
- `rule-catalogue-review.md` is filled in, sign-off block checked.

Next spec milestone: Step 4 (format narrowing for `.Rnw` / `.Rmd`), then Step 5 (auto-fix payloads). Neither is in scope here.
