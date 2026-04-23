"""Tests for the catalogue renderer.

Covers the consistency contract from contracts/rendering.md §Determinism:
 * Running the renderer twice on the same input produces byte-identical
   output (no timestamps, no env-dependent content).
 * The committed ``catalogue.md`` matches what the renderer would emit
   from the committed ``catalogue.yaml``.
 * The ``--check`` CLI mode returns 0 on consistency, 1 on drift.

The renderer is invoked as a Python function; the ``--check`` path is
exercised by calling the module-level ``main()`` directly.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from tools import render_catalogue
from tools._catalogue_validate import validate

REPO_ROOT = Path(__file__).resolve().parents[4]
CATALOGUE_YAML = REPO_ROOT / "specs" / "003-jss-rule-catalogue" / "catalogue.yaml"
CATALOGUE_MD = REPO_ROOT / "specs" / "003-jss-rule-catalogue" / "catalogue.md"
TEMPLATE_DIR = REPO_ROOT / "docs" / "jss-template"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def catalogue_doc() -> dict:
    assert CATALOGUE_YAML.exists()
    with CATALOGUE_YAML.open("r", encoding="utf-8") as f:
        doc = yaml.safe_load(f)
    errors = validate(doc, template_dir=TEMPLATE_DIR)
    assert errors == [], (
        "catalogue.yaml is invalid; run tests/unit/journals/jss/test_catalogue.py first"
    )
    return doc


# ---------------------------------------------------------------------------
# Determinism & consistency
# ---------------------------------------------------------------------------


def test_render_is_deterministic(catalogue_doc: dict) -> None:
    first = render_catalogue.render(catalogue_doc)
    second = render_catalogue.render(catalogue_doc)
    assert first == second


def test_render_matches_committed_markdown(catalogue_doc: dict) -> None:
    assert CATALOGUE_MD.exists(), (
        f"{CATALOGUE_MD} does not exist. Run `python -m tools.render_catalogue`."
    )
    expected = CATALOGUE_MD.read_text(encoding="utf-8")
    actual = render_catalogue.render(catalogue_doc)
    if actual != expected:
        # Produce a reasonably-diagnostic failure message without dumping the
        # whole catalogue: first divergent line + 5 lines of context.
        e_lines = expected.splitlines(keepends=True)
        a_lines = actual.splitlines(keepends=True)
        for i, (e, a) in enumerate(zip(e_lines, a_lines, strict=False)):
            if e != a:
                window = 5
                ctx_start = max(0, i - window)
                pytest.fail(
                    f"catalogue.md drifts from catalogue.yaml at line {i + 1}.\n"
                    f"Expected (committed catalogue.md) lines {ctx_start + 1}..{i + window + 1}:\n"
                    + "".join(e_lines[ctx_start : i + window + 1])
                    + f"\n\nActual (rendered) lines {ctx_start + 1}..{i + window + 1}:\n"
                    + "".join(a_lines[ctx_start : i + window + 1])
                    + "\n\nRun `python -m tools.render_catalogue` and re-commit."
                )
        # Length difference, no line-by-line divergence
        assert len(a_lines) == len(e_lines), (
            f"line count differs: committed={len(e_lines)}, rendered={len(a_lines)}"
        )


# ---------------------------------------------------------------------------
# CLI surface
# ---------------------------------------------------------------------------


def test_check_mode_returns_zero_when_consistent() -> None:
    exit_code = render_catalogue.main(["--check"])
    assert exit_code == 0, "--check should return 0 when committed catalogue.md is current"


def test_check_mode_returns_one_when_drifted(tmp_path: Path) -> None:
    # Copy the current yaml into tmp; write a deliberately-stale md next to it.
    yaml_copy = tmp_path / "catalogue.yaml"
    md_copy = tmp_path / "catalogue.md"
    yaml_copy.write_text(CATALOGUE_YAML.read_text(encoding="utf-8"), encoding="utf-8")
    md_copy.write_text("# this is not the rendered catalogue\n", encoding="utf-8")

    exit_code = render_catalogue.main(
        [
            "--check",
            "--yaml-path",
            str(yaml_copy),
            "--md-path",
            str(md_copy),
            "--template-dir",
            str(TEMPLATE_DIR),
        ]
    )
    assert exit_code == 1


def test_write_mode_produces_file(tmp_path: Path) -> None:
    yaml_copy = tmp_path / "catalogue.yaml"
    md_copy = tmp_path / "catalogue.md"
    yaml_copy.write_text(CATALOGUE_YAML.read_text(encoding="utf-8"), encoding="utf-8")

    exit_code = render_catalogue.main(
        [
            "--yaml-path",
            str(yaml_copy),
            "--md-path",
            str(md_copy),
            "--template-dir",
            str(TEMPLATE_DIR),
        ]
    )
    assert exit_code == 0
    assert md_copy.exists()
    assert md_copy.read_text(encoding="utf-8").startswith("# JSS Rule Catalogue\n")
