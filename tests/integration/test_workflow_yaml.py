"""Spec 014 + 017 follow-up — workflow YAML validation.

Catches typos / bad indentation in the deferred-publish workflow
files. Runs in any CI without GitHub Actions itself; the workflow
files don't need to be EXECUTED to be checked for validity.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS_DIR = ROOT / ".github" / "workflows"


def _load(name: str) -> dict:
    with (WORKFLOWS_DIR / name).open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.mark.parametrize(
    "name",
    [
        "publish-badges.yml",
        "test-action.yml",
        "release-action.yml",
        "vscode-publish.yml",
    ],
)
def test_workflow_parses_as_yaml(name: str) -> None:
    """Every workflow file in this repo parses cleanly."""
    if not (WORKFLOWS_DIR / name).exists():
        pytest.skip(f"{name} not present yet")
    doc = _load(name)
    assert isinstance(doc, dict)
    # Workflows must declare jobs.
    assert "jobs" in doc, f"{name}: missing top-level 'jobs'"
    assert isinstance(doc["jobs"], dict) and doc["jobs"], (
        f"{name}: jobs must be a non-empty mapping"
    )


def test_publish_badges_uses_eval_badge_module() -> None:
    """Spec 017: the publish-badges workflow MUST invoke
    `eval.badge` to render the JSON files. Pin this so a refactor
    can't silently drop the dependency."""
    text = (WORKFLOWS_DIR / "publish-badges.yml").read_text(encoding="utf-8")
    assert "python -m eval.badge" in text
    assert "precision.json" in text
    assert "recall.json" in text
    assert "f1.json" in text


def test_test_action_uses_local_action() -> None:
    """Spec 014: the smoke test invokes the local action via
    `uses: ./action`, not the published marketplace tag."""
    text = (WORKFLOWS_DIR / "test-action.yml").read_text(encoding="utf-8")
    assert "uses: ./action" in text


def test_test_action_passes_jss_template() -> None:
    """The smoke test points at the vendored docs/jss-template/
    fixture so we always have something to lint."""
    text = (WORKFLOWS_DIR / "test-action.yml").read_text(encoding="utf-8")
    assert "docs/jss-template" in text
