# Contract: per-rule pytest template

**Location pattern**: `tests/unit/rules/test_<category>.py`

Every rule in a category's module has at least three associated test artefacts:

1. **Positive test**: asserts the rule fires on its bad fixture, with exactly the expected count and metadata.
2. **Near-miss negative test**: asserts the rule does NOT fire on a deliberately-adjacent input that shares the surface shape of the violation but lacks the trigger condition.
3. **Fixture pair**: `tests/fixtures/violations/<category>/<rule_id>-bad.{tex|bib}` (triggers the rule, ≥1 violation) and `<rule_id>-good.{tex|bib}` (doesn't trigger; semantically equivalent `example_fix`).

## Canonical test shape

```python
# tests/unit/rules/test_citations.py

from __future__ import annotations

from pathlib import Path

import pytest

from texlint.api import ParsedDocument, Severity, ToolConfig, Violation
from texlint.journals.jss.rules.citations import (
    check_jss_cite_002,
    check_jss_cite_003,
    check_jss_cite_004,
    jss_cite_002,
    jss_cite_003,
    jss_cite_004,
    rules,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "violations" / "citations"


# ---------------------------------------------------------------------------
# Module-level invariants (R-1/R-2 style, cheap)
# ---------------------------------------------------------------------------

def test_rules_tuple_has_three_rules():
    """Catalogue has 3 rules in citations category (CITE-001 retired)."""
    assert len(rules) == 3


def test_rules_tuple_ids():
    assert {r.id for r in rules} == {"JSS-CITE-002", "JSS-CITE-003", "JSS-CITE-004"}


# ---------------------------------------------------------------------------
# JSS-CITE-002 — software package mentioned without a citation
# ---------------------------------------------------------------------------

class TestCite002:
    def test_positive(self, parse_tex_source, run_rule):
        """Bad fixture: \\pkg{mgcv} with no citation anywhere."""
        bad = (FIXTURE_DIR / "JSS-CITE-002-bad.tex").read_text(encoding="utf-8")
        violations = run_rule(jss_cite_002, parse_tex_source(bad))
        assert len(violations) == 1
        v = violations[0]
        assert v.rule_id == "JSS-CITE-002"
        assert v.severity == Severity.WARNING
        assert v.line >= 1 and v.column >= 1
        assert v.fix is None  # spec 004 FR-025

    def test_good_fixture_no_violation(self, parse_tex_source, run_rule):
        """Good fixture: \\pkg{mgcv} with \\citep{Wood:2006} in same paragraph."""
        good = (FIXTURE_DIR / "JSS-CITE-002-good.tex").read_text(encoding="utf-8")
        assert run_rule(jss_cite_002, parse_tex_source(good)) == []

    # Near-miss negatives — the heuristic's edge cases
    def test_citation_in_previous_sentence_same_paragraph(self, parse_tex_source, run_rule):
        """Citation comes BEFORE \\pkg{} but in the same paragraph — still OK."""
        src = r"""\documentclass[article]{jss}
\begin{document}
See \citep{Wood:2006}. We use \pkg{mgcv} for this analysis.
\end{document}"""
        assert run_rule(jss_cite_002, parse_tex_source(src)) == []

    def test_citation_in_next_paragraph_still_flagged(self, parse_tex_source, run_rule):
        """Citation in NEXT paragraph doesn't satisfy the rule — strict same-paragraph."""
        src = r"""\documentclass[article]{jss}
\begin{document}
We use \pkg{mgcv} for this analysis.

See \citep{Wood:2006} for theoretical background.
\end{document}"""
        violations = run_rule(jss_cite_002, parse_tex_source(src))
        assert len(violations) == 1
        assert violations[0].rule_id == "JSS-CITE-002"

    def test_first_pkg_only(self, parse_tex_source, run_rule):
        """Only the FIRST \\pkg{X} per distinct X is flagged."""
        src = r"""\documentclass[article]{jss}
\begin{document}
We use \pkg{mgcv}. Later we also use \pkg{mgcv} in a different analysis.
\end{document}"""
        violations = run_rule(jss_cite_002, parse_tex_source(src))
        assert len(violations) == 1  # only the first mention
```

## Required test classes per rule

Every rule gets at minimum:

### Positive test
```python
def test_positive(self, parse_tex_source, run_rule):
    bad = (FIXTURE_DIR / "<rule_id>-bad.<ext>").read_text(encoding="utf-8")
    violations = run_rule(<rule_obj>, parse_tex_source(bad))
    assert len(violations) == 1
    # ... assertions on rule_id, severity, line, column, fix is None ...
```

### Negative (good fixture) test
```python
def test_good_fixture_no_violation(self, parse_tex_source, run_rule):
    good = (FIXTURE_DIR / "<rule_id>-good.<ext>").read_text(encoding="utf-8")
    assert run_rule(<rule_obj>, parse_tex_source(good)) == []
```

### Near-miss negative test(s) — at least one per rule
Deliberately adjacent input that tests the heuristic's scope. Examples:
- A rule that flags macros inside captions: test a macro outside a caption.
- A rule that flags hardcoded `(Author, YYYY)`: test `(Author, YYYY)` inside `\code{...}` (should NOT flag).
- A rule that flags all-lowercase BibTeX titles: test a mixed-case title.

### Branch-coverage tests — as many as needed
One per uncovered branch reported by `pytest-cov --cov-branch` on the rule module. Common patterns:
- Empty `nodelist` → early return.
- Macro with no arg group → graceful skip.
- Rule applied to `.bib`-only document → no violations (no tex_files to iterate).

## Pytest fixtures

From spec 001's `tests/conftest.py`:

```python
@pytest.fixture
def parse_tex_source(tmp_path):
    """Write `src` to a tempfile and parse it as a `.tex` file."""
    ...

@pytest.fixture
def parse_bib_source(tmp_path):
    """Write `src` to a tempfile and parse it as a `.bib` file."""
    ...

@pytest.fixture
def run_rule(parse_tex_source, parse_bib_source):
    """Apply `rule.check` to a one-file document built from `src`.

    Dispatches by the `kind` kwarg: `"tex"` (default) or `"bib"`.
    """
    ...
```

These are already shipped in spec 001 and used by the existing smoke-rule tests. No new fixture work in spec 004.

## Fixture file format

### `.tex` fixtures
Wrap the catalogue's `example_violation` / `example_fix` in a minimal compilable document:

```latex
\documentclass[article]{jss}
\begin{document}

<example content from catalogue>

\end{document}
```

Keep them short (≤20 lines); one bad fixture per rule that fires exactly once.

### `.bib` fixtures
Minimal BibTeX entries, no wrapping needed:

```bibtex
@article{Demo,
  author = {Jane Doe},
  title  = {...},
  year   = {2020}
}
```

### Auxiliary fixtures (when 100% branch coverage requires more than one bad example)

Naming: `<rule_id>-<descriptor>.{tex|bib}`, e.g.:
- `JSS-CITE-004-in-verbatim.tex` — exercises the verbatim-mask branch.
- `JSS-PRE-003-no-markup.tex` — exercises the "\title{} has no markup → no flag" branch.

Per spec 004 FR-011.

## Branch-coverage target

`pytest --cov=src/texlint/journals/jss/rules/<category> --cov-branch --cov-fail-under=100` must pass before the category PR merges. Uncovered branches block the gate.

When coverage is short:

1. Identify the uncovered branch via `pytest --cov-report=term-missing`.
2. Construct a test that hits it — typically a new `.tex` / `.bib` snippet inline or as an auxiliary fixture.
3. Add the test to `test_<category>.py`.
4. Re-run coverage. Repeat until 100%.

## Integration with the precision-gate loop

Unit tests DON'T substitute for the corpus precision gate. They establish correctness on synthetic input; the gate establishes reliability on real manuscripts. Both are required before a category ships. The precision-gate loop is driven by `scripts/eval-category.sh` — see `quickstart.md`.
