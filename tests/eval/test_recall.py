"""Recall (mutation) tests for low-precision JSS rules.

For each plant fixture in ``tests/fixtures/recall/<RULE>/``, run every
JSS rule against the file and assert the rule listed in the matching
``.expected`` sidecar fires. The aggregate recall metric per rule is
``caught_plants / total_plants`` — used by the iteration policy to
block FP-fixes that also destroy recall.

The tests are parameterised so each plant is its own pytest case;
failures show up granularly in the suite output.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

import pytest

from texlint.api import ParsedDocument, ToolConfig
from texlint.core.parser import parse_bib_file, parse_tex_file
from texlint.journals.jss import JSSJournal

REPO_ROOT = Path(__file__).resolve().parents[2]
RECALL_DIR = REPO_ROOT / "tests" / "fixtures" / "recall"


def _all_rules() -> dict[str, object]:
    out: dict[str, object] = {}
    for cat in JSSJournal().categories():
        for rule in cat.rules:
            out[rule.id] = rule
    return out


def _gather_plants() -> Iterable[tuple[str, Path, frozenset[str]]]:
    """Yield ``(rule_id, plant_path, expected_rule_ids)`` triples for
    every plant fixture under ``tests/fixtures/recall/<RULE>/``.
    """
    if not RECALL_DIR.is_dir():
        return
    for rule_dir in sorted(RECALL_DIR.iterdir()):
        if not rule_dir.is_dir():
            continue
        rule_id = rule_dir.name
        for plant in sorted(rule_dir.iterdir()):
            if plant.suffix == ".expected":
                continue
            if plant.suffix not in {".tex", ".rnw", ".rmd", ".bib", ".ltx"}:
                continue
            expected_path = plant.with_suffix(".expected")
            if not expected_path.is_file():
                continue
            expected = frozenset(
                line.strip()
                for line in expected_path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            )
            yield rule_id, plant, expected


def _build_doc(plant: Path) -> ParsedDocument:
    suffix = plant.suffix.lower()
    if suffix == ".bib":
        return ParsedDocument(bib_files=(parse_bib_file(plant),))
    return ParsedDocument(tex_files=(parse_tex_file(plant),))


_PLANTS = list(_gather_plants())


@pytest.mark.parametrize(
    ("rule_id", "plant", "expected"),
    _PLANTS,
    ids=[f"{r}::{p.stem}" for r, p, _ in _PLANTS],
)
def test_recall_plant_fires_expected_rule(
    rule_id: str, plant: Path, expected: frozenset[str],
) -> None:
    """Each plant must trip every rule listed in its .expected file.

    Other rules are allowed to fire (the plant may also trip a sibling
    rule), but the expected rule MUST fire — that's the recall signal.
    """
    rules = _all_rules()
    cfg = ToolConfig()
    doc = _build_doc(plant)

    fired: set[str] = set()
    for r_id, rule in rules.items():
        if r_id != rule_id:
            # Optimization: only run the rule we care about. The plants
            # are minimal; cross-rule fire-checks are cheap if needed
            # later but for now we trust the plant author wrote a clean
            # fixture for the target rule.
            continue
        for v in rule.check(doc, cfg):
            fired.add(v.rule_id)

    missing = expected - fired
    assert not missing, (
        f"Plant {plant.relative_to(REPO_ROOT)} did not fire {sorted(missing)} "
        f"(rule under test: {rule_id}). Got: {sorted(fired) or 'no fires'}."
    )


def test_recall_directory_layout() -> None:
    """Every recall plant has a matching .expected sidecar."""
    for rule_dir in sorted(RECALL_DIR.iterdir()):
        if not rule_dir.is_dir() or rule_dir.name == "__pycache__":
            continue
        for plant in rule_dir.iterdir():
            if plant.suffix == ".expected":
                continue
            if plant.suffix not in {".tex", ".rnw", ".rmd", ".bib", ".ltx"}:
                continue
            expected = plant.with_suffix(".expected")
            assert expected.is_file(), (
                f"Plant {plant.relative_to(REPO_ROOT)} is missing the "
                f"sidecar {expected.name}"
            )


def test_recall_at_least_one_plant_per_target_rule() -> None:
    """The iter-71 FAIL rules must each have ≥1 plant — otherwise
    the recall metric is missing for the rules where it matters most.
    (JSS-CAP-003 was retired 2026-07-04 — unreliable in both directions —
    so it is no longer a target rule.)
    """
    target_rules = {
        "JSS-TYPO-004", "JSS-BIBTEX-002", "JSS-NAME-001",
    }
    plants_per_rule: dict[str, int] = {}
    for rule_id, _plant, _expected in _PLANTS:
        plants_per_rule[rule_id] = plants_per_rule.get(rule_id, 0) + 1
    for rule_id in target_rules:
        assert plants_per_rule.get(rule_id, 0) >= 1, (
            f"Recall coverage missing for {rule_id} — the iter-71 "
            f"FAIL rules must each have ≥1 plant under "
            f"tests/fixtures/recall/{rule_id}/."
        )
