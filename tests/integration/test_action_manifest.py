"""Contract tests for the GitHub Action manifest at ``action/action.yml``.

These tests run inside the standard pytest invocation and do not require the
action runtime. They guard the wiring that pins ``--source-root`` to the
``GITHUB_WORKSPACE`` checkout root (spec 014 follow-up) so SARIF
``artifactLocation.uri`` values stay repo-root-relative.
"""

from __future__ import annotations

from pathlib import Path

import yaml

MANIFEST = Path(__file__).resolve().parents[2] / "action" / "action.yml"


def _load_manifest() -> dict:
    with MANIFEST.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _lint_step(manifest: dict) -> dict:
    steps = manifest["runs"]["steps"]
    for step in steps:
        if step.get("id") == "lint":
            return step
    raise AssertionError("manifest is missing a step with id: lint")


class TestManifestShape:
    def test_top_level_keys(self) -> None:
        manifest = _load_manifest()
        assert "name" in manifest
        assert "inputs" in manifest
        assert manifest["runs"]["using"] == "composite"

    def test_inputs_is_mapping(self) -> None:
        manifest = _load_manifest()
        assert isinstance(manifest["inputs"], dict)
        assert manifest["inputs"], "inputs should not be empty"


class TestSourceRootWiring:
    """Spec 014 follow-up: ``--source-root "$GITHUB_WORKSPACE"`` is wired in."""

    def test_lint_step_passes_source_root(self) -> None:
        manifest = _load_manifest()
        run_block = _lint_step(manifest)["run"]
        assert "--source-root" in run_block, (
            "lint step must invoke jss-lint with --source-root so SARIF URIs "
            "resolve against the GitHub Actions checkout root"
        )

    def test_source_root_references_github_workspace(self) -> None:
        manifest = _load_manifest()
        run_block = _lint_step(manifest)["run"]
        assert "$GITHUB_WORKSPACE" in run_block or "${{ env.GITHUB_WORKSPACE }}" in run_block, (
            "lint step must thread $GITHUB_WORKSPACE into --source-root"
        )
