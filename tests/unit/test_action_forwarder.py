"""Guard: the root ``action.yml`` forwarder mirrors ``action/action.yml``.

Two paths reach the same GitHub Action — ``kollerma/jss-style-checker@v1``
(the root forwarder, the form docs/ publishes) and
``kollerma/jss-style-checker/action@v1`` (the implementation, the form
action/README.md publishes). The forwarder declares the inputs itself and
passes them on, so a new input added to the implementation is silently
undeliverable through the short path until it is added here too: the
caller's ``with:`` value is accepted, then dropped, and the run quietly
uses the default. This test fails instead, naming the drifted key.

If it fails after editing ``action/action.yml``, mirror the change into
the root ``action.yml`` — inputs, outputs, and the forwarding ``with:``.
"""

from __future__ import annotations

from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")

_REPO = Path(__file__).resolve().parents[2]


def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def root() -> dict:
    return _load(_REPO / "action.yml")


@pytest.fixture(scope="module")
def impl() -> dict:
    return _load(_REPO / "action" / "action.yml")


def test_inputs_match(root: dict, impl: dict) -> None:
    assert root["inputs"] == impl["inputs"]


def test_output_names_match(root: dict, impl: dict) -> None:
    # The `value:` expressions legitimately differ (the forwarder reads
    # them off its delegating step); the surface must not.
    assert root["outputs"].keys() == impl["outputs"].keys()


def test_every_input_is_forwarded(root: dict, impl: dict) -> None:
    steps = root["runs"]["steps"]
    assert len(steps) == 1, "the forwarder should delegate in exactly one step"
    forwarded = steps[0]["with"]
    assert set(forwarded) == set(impl["inputs"])
    for name in forwarded:
        assert forwarded[name] == f"${{{{ inputs.{name} }}}}"


def test_delegates_to_the_implementation(root: dict) -> None:
    uses = root["runs"]["steps"][0]["uses"]
    # Not `./action`: a relative `uses:` inside a composite action resolves
    # against the caller's workspace (actions/runner#1348).
    assert uses.startswith("kollerma/jss-style-checker/action@")
