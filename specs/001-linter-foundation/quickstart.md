# Quickstart — Linter Foundation

For first-time contributors to `jss-style-checker`. Gets you from a fresh clone to running the tool on a fixture and authoring a new smoke rule.

## Prerequisites

- Python 3.10, 3.11, or 3.12
- `pip` ≥ 23

## Install

```bash
git clone <repo-url> jss-style-checker
cd jss-style-checker
python -m venv .venv && source .venv/bin/activate   # or your preferred env tool
pip install -e '.[dev]'
pip install -e tests/fixtures/stub_journal           # registers the second-journal fixture
```

The two `pip install -e` calls install `texlint` and the `stub_journal` test fixture. Entry-point registration happens at install time, so both `--journal jss` and `--journal stub` work immediately.

## First run — compliant fixture

```bash
jss-lint tests/fixtures/compliant/minimal.tex tests/fixtures/compliant/minimal.bib
# → (no output, exit 0)
```

## First run — violations

```bash
jss-lint tests/fixtures/violations/JSS-CITE-001.tex
# → one JSS-CITE-001 violation, exit 1
```

## Try every renderer and mode

```bash
# Terminal, author (default)
jss-lint tests/fixtures/violations/JSS-CITE-001.tex

# Terminal, reviewer
jss-lint --mode reviewer tests/fixtures/compliant/minimal.tex tests/fixtures/compliant/minimal.bib

# JSON (CI-shaped)
jss-lint --output json tests/fixtures/compliant/minimal.tex | jq .

# HTML (save to a file and open it)
jss-lint --output html --mode reviewer \
  tests/fixtures/compliant/minimal.tex tests/fixtures/compliant/minimal.bib \
  > /tmp/report.html
xdg-open /tmp/report.html   # or `open` on macOS
```

## Run the tests

```bash
pytest -q                                            # full suite
pytest tests/unit/journals/jss/ --cov-branch         # rule-file branch coverage
pytest tests/integration/ -k json                    # just the JSON-output integration test
```

Branch coverage on rule files is a constitutional requirement (§IX). The suite fails if any `src/texlint/journals/*/rules/*.py` drops below 100%.

## Repo layout

```text
src/texlint/
├── api.py                  # Public data model — import from here
├── config.py               # load() merges .jss-lint.toml + CLI flags
├── cli.py                  # click entry; main() ⇒ sys.exit(code)
├── core/
│   ├── parser.py           # parse_tex_file / parse_bib_file
│   └── engine.py           # load_journal / run
├── output/
│   ├── terminal.py         # rich
│   ├── json_output.py      # deterministic json.dumps
│   ├── html_output.py      # jinja2 PackageLoader
│   └── templates/
│       ├── author.html.j2
│       └── reviewer.html.j2
└── journals/jss/
    ├── __init__.py         # JSSJournal(JournalRuleModule)
    └── rules/
        ├── cite_001_emph.py
        ├── bib_001_year.py
        └── src_001_width.py

tests/
├── conftest.py             # parse_tex_source / run_rule helpers
├── fixtures/
│   ├── compliant/minimal.tex + minimal.bib
│   ├── violations/JSS-*.tex | .bib   # one per rule
│   └── stub_journal/       # second-journal fixture
├── unit/
└── integration/
```

## Add a new smoke rule (walkthrough)

**Context**: the three smoke rules (`JSS-CITE-001`, `JSS-BIB-001`, `JSS-SRC-001`) exercise all rule shapes for this foundation. Adding a real rule follows the same pattern and is the daily workflow for Step 2. This walkthrough demonstrates adding a hypothetical fourth smoke rule, `JSS-CITE-002` — "citations must not use `\ref` where `\cite` is intended" — so you see every file that gets touched.

1. **Write the violation fixture first** (TDD — Constitution §VIII).
   ```tex
   % tests/fixtures/violations/JSS-CITE-002.tex
   \documentclass{article}
   \begin{document}
   See \ref{smith2020} for details.   % should be \cite
   \end{document}
   ```

2. **Write the failing test.** Under `tests/unit/journals/jss/test_cite_002_ref.py`:
   ```python
   from texlint.journals.jss.rules.cite_002_ref import rule as cite_002
   from tests.conftest import run_rule

   def test_flags_ref_in_prose(violation_fixture):
       violations = run_rule(cite_002, violation_fixture("JSS-CITE-002.tex"))
       assert len(violations) == 1
       assert violations[0].rule_id == "JSS-CITE-002"
       assert violations[0].line == 3
   ```
   Run `pytest tests/unit/journals/jss/test_cite_002_ref.py` — it fails because the rule module doesn't exist yet. That is the Red of Red-Green-Refactor.

3. **Implement the rule** in `src/texlint/journals/jss/rules/cite_002_ref.py`:
   ```python
   from pylatexenc.latexwalker import LatexMacroNode
   from texlint.api import (
       Rule, Severity, Violation, ParsedDocument, ToolConfig,
   )

   def _check(doc: ParsedDocument, cfg: ToolConfig):
       for tex in doc.tex_files:
           for node in _walk(tex.nodes):
               if isinstance(node, LatexMacroNode) and node.macroname == "ref":
                   line, col = tex.walker.pos_to_lineno_colno(node.pos)
                   yield Violation(
                       file=tex.path, line=line, column=col + 1,
                       rule_id="JSS-CITE-002", severity=Severity.WARNING,
                       message="Prose citations should use \\cite, not \\ref.",
                       suggestion="Replace \\ref{...} with \\cite{...} in running text.",
                       fix=None,
                   )

   def _walk(nodes):
       ...  # depth-first over pylatexenc nodes

   rule = Rule(
       id="JSS-CITE-002",
       category="citation",
       severity=Severity.WARNING,
       message_template="Prose citations should use \\cite, not \\ref.",
       authority="JSS author instructions §4.2",
       check=_check,
       formats=frozenset({".tex"}),
   )
   ```
   Re-run the test — it passes. That is the Green.

4. **Register with the journal.** In `src/texlint/journals/jss/__init__.py`, import `cite_002_ref.rule` and add it to the `citation` category's tuple.

5. **Check branch coverage.**
   ```bash
   pytest tests/unit/journals/jss/test_cite_002_ref.py --cov=src/texlint/journals/jss/rules/cite_002_ref --cov-branch --cov-report=term-missing
   ```
   100% is mandatory. Add tests to cover every branch in `_walk` and every guarded isinstance check.

6. **Commit.** The commit message should reference the authority citation. Example:
   ```
   Add JSS-CITE-002 (\ref in prose)

   Per JSS author instructions §4.2: textual citations use \cite.
   \ref is reserved for cross-references to labelled objects.
   ```

That is the whole loop. The same six-step recipe applies to Step 2's 53 real rules.

## What's NOT here yet

These are explicitly deferred (spec Assumptions):

- `--fix` and `--dry-run` (Step 4) — `FixSuggestion` is reserved but every smoke rule leaves `fix = None`.
- `.Rnw` / `.Rmd` support (Step 3).
- The full 53-rule JSS catalogue (Step 2) — this step ships 3 smoke rules.
- The `eval-jss` precision evaluation CLI (Step 5) — no precision claim is made in this step.

If you reach for any of these while reading the code, you are in the wrong Step.
