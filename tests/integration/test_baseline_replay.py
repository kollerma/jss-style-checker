"""Replay of a real revision round — the regression test for item S.

Contract: `specs/027-first-time-user-gaps/contracts/suggestions.md` C-7.

A baseline entry is keyed on `(rule_id, path, message, suggestion)`
(spec 027 D1). Two properties decide whether that key is any good, and
both are measured here against the four real versions of JSS submission
5342 rather than against synthetic input:

1. **Specificity** — how many *distinct* keys the findings of one
   version collapse into. Before item S the initial version's 100
   findings collapsed into 49 keys, which is what let eight genuinely
   new findings hide behind the counts of same-rule findings the author
   had fixed elsewhere in the same file (plan §5.7).
2. **Stability** — how many findings that *persist* across a revision
   round change their key anyway. Every re-keyed finding is a false
   "new" for a user holding a baseline.

`research.md` §3 measured 80 distinct keys and 4 re-keyed findings for
the final ten-rule scope; the thresholds below are those numbers with a
little slack, so a future rule change that makes suggestions vaguer or
more edit-sensitive fails here.

The manuscript is not redistributable: `examples/jss5342-versions/` is
gitignored, so this test skips cleanly wherever it is absent (like the
recall-corpus parity suites). Nothing from the manuscript is asserted
literally — only counts.
"""

from __future__ import annotations

import shutil
from collections import Counter
from pathlib import Path

import pytest

from texlint.api import ToolConfig
from texlint.core.engine import load_journal, parse_document, run

REPO_ROOT = Path(__file__).resolve().parents[2]
VERSIONS_DIR = REPO_ROOT / "examples" / "jss5342-versions"

#: Distinct `(rule, path, message, suggestion)` keys the initial
#: version's 100 findings must collapse into. Measured here: 79 before
#: this threshold was set (research.md §3 predicted ~80); the same
#: manuscript collapsed into 49 keys before item S.
MIN_DISTINCT_KEYS = 75

#: Findings that survived `initial` → `resubmission` under the *pre-item-S*
#: key, measured by running this file's `_keys`/`_matched` against the
#: commit before the ten suggestions were sharpened. Recorded as a
#: constant because it cannot be recomputed once the old wording is gone.
PRE_ITEM_S_MATCHED = 26

#: How many of those 26 item S is allowed to re-key. Measured: 4 (three
#: `JSS-CITE-003`, one `JSS-CODE-003`), matching research.md §3. Every
#: re-keyed finding is a false "new" for a user holding a baseline.
MAX_REKEYED = 4


def _lint(version: str, tmp_path: Path) -> list:
    """Lint one version with its main file renamed to a common name.

    The manuscript's main file is renamed twice across the four versions
    (`article2` → `article6` → `jss5342`). Since the path is part of the
    key, comparing versions under their real names would report every
    entry as stale — the rename case is a documented baseline limit
    (`baseline-file.md` C-8 §2), not the thing this test measures.
    """
    source = VERSIONS_DIR / version
    (rnw,) = sorted(source.glob("*.Rnw"))
    workdir = tmp_path / version
    workdir.mkdir(parents=True)
    shutil.copy(rnw, workdir / "main.Rnw")
    shutil.copy(source / "refs.bib", workdir / "refs.bib")

    document = parse_document([workdir / "main.Rnw", workdir / "refs.bib"])
    report = run(ToolConfig(), document, load_journal("jss"))
    return [v for v in report.violations if v.rule_id != "JSS-PARSE-000"]


def _keys(violations: list) -> Counter:
    """The multiset of baseline keys — `baseline-file.md` C-2."""
    return Counter(
        (v.rule_id, Path(v.file).name, v.message, v.suggestion or "")
        for v in violations
    )


def _matched(old: Counter, new: Counter) -> int:
    """Multiset intersection size — findings that survive the round."""
    return sum((old & new).values())


@pytest.fixture(scope="module")
def versions() -> dict[str, list]:
    if not VERSIONS_DIR.is_dir():
        pytest.skip(
            f"{VERSIONS_DIR} not present (gitignored manuscript sources); "
            "the item-S key measurements cannot be replayed here"
        )
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        yield {
            name: _lint(name, tmp_path)
            for name in ("initial", "resubmission")
        }


def test_initial_version_findings_are_specific(versions: dict[str, list]) -> None:
    """SC-004: the accepted state of a real manuscript is not a blur."""
    keys = _keys(versions["initial"])
    assert len(keys) >= MIN_DISTINCT_KEYS, (
        f"the initial version's {sum(keys.values())} findings collapse into "
        f"only {len(keys)} distinct baseline keys (expected at least "
        f"{MIN_DISTINCT_KEYS}); a suggestion has become less specific"
    )


def test_persisting_findings_keep_their_key(versions: dict[str, list]) -> None:
    """SC-004: a revision round must not re-key what it did not change."""
    matched = _matched(_keys(versions["initial"]), _keys(versions["resubmission"]))
    rekeyed = PRE_ITEM_S_MATCHED - matched
    assert rekeyed <= MAX_REKEYED, (
        f"{rekeyed} of the {PRE_ITEM_S_MATCHED} findings that used to "
        "survive this revision round now change their baseline key "
        f"(allowed: {MAX_REKEYED}); a suggestion varies with edits that did "
        "not change the finding"
    )
