# Quickstart: Writing or Updating a Rule Explanation

**Audience**: contributors backfilling the explanation prose for an
existing rule, or adding a new rule to the catalogue with full
explain support.

## Prerequisites

- Repo at HEAD on the spec-009 branch (or post-merge `main`).

## Where things live

```text
src/texlint/api.py                                  # Rule dataclass
src/texlint/journals/_catalogue_data.py             # catalogue
src/texlint/explain.py                              # renderer
tests/fixtures/violations/<RULE-ID>-bad.tex         # fixture pull-through source
tests/fixtures/explain/golden_*.{txt,md}            # explain output goldens
tests/unit/test_explain.py                          # explain renderer tests
tests/unit/test_catalogue.py                        # contract test
```

## Adding a new citable rule with full explain support

1. Decide the rule's id, severity, category, JSS-guide section,
   `guide_url` (per spec 007), and the `explanation` prose. The
   prose:
   - Is one paragraph (≤120 words).
   - Explains the *why* in plain language — not "rule X says Y",
     but "JSS readers expect Y because Z".
   - References the JSS guide section number once, in prose.
2. Pick a 3–5 line bad-example fragment that triggers the rule
   when fed to the linter as the body of a fixture. The fragment
   does NOT need to be a complete document.
3. Pick a 3–5 line good-example fragment that the rule does NOT
   flag. The two fragments should be the same content modulo the
   correctness of the violation.
4. Add the rule to `_catalogue_data.RULES` with all six fields:
   `(rule_id, severity, category, guide_section, guide_url,
   explanation, example_bad, example_good)` plus the existing
   `title`, `description`, etc.
5. (Optional but recommended) Add a real fixture under
   `tests/fixtures/violations/<rule-id>-bad.tex`. The fixture is
   a complete document the eval corpus or the unit tests can
   exercise.
6. Run the contract tests:
   ```sh
   pytest tests/unit/test_catalogue.py -v
   ```
7. Generate the explain golden files:
   ```sh
   pytest tests/unit/test_explain.py --update-goldens -k <rule-id>
   ```
   Inspect the diff and commit.
8. Run the full explain test suite:
   ```sh
   pytest tests/unit/test_explain.py -v
   ```

## Backfilling an existing rule's explanation

1. Read the rule's `Rule.title` and `Rule.description` and the
   JSS-guide section it cites (`Rule.guide_section`).
2. Write a one-paragraph explanation. The prose is the public
   face of the rule; aim for clarity over cleverness.
3. Add `explanation` (and optionally `example_bad` /
   `example_good`) to the rule's catalogue entry. Re-run the
   contract test (step 6 above).

## Try the explain command

```sh
# Single rule, terminal format
jss-lint explain JSS-CITE-002

# Single rule, markdown format (paste into a PR comment)
jss-lint explain JSS-CITE-002 --format markdown

# Pull the corpus fixture into the output
jss-lint explain JSS-CITE-002 --example

# Listing view
jss-lint explain
jss-lint explain --format markdown | tee rules.md
```

## Common pitfalls

- **Explanation contains `[NEEDS CLARIFICATION]`**: the contract
  test rejects placeholder text. Fill it in before merging.
- **Markdown explanation contains a literal `\`**: escape it in
  the source string; the markdown renderer will treat
  `\backslash` as a markdown escape unless you double it.
- **Bad-example does NOT trigger the rule**: the explainer
  doesn't lint the example, but the explainer's golden
  test does — if the bad-example has no violation when run
  through the linter, a downstream test (in spec 015's
  conformance report) will flag it.
- **Adding `--format html`**: out of scope (see research §1).
  Pipe markdown through pandoc instead.

## Where to extend

- **Adding a third format (e.g., `--format json`)**: open a
  follow-up spec. Adding it ad-hoc would skip the
  Clarifications loop that established the format set.
- **Changing the listing view's grouping**: edit
  `src/texlint/explain.py::_render_listing`. The listing
  test golden will need regeneration.
- **Localised explanations**: out of scope. If a future
  spec adds it, the catalogue grows a `(locale, str)` map
  per rule; spec 009 stays English-only.
