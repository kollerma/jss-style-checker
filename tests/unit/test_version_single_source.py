"""Guard: every ecosystem manifest agrees with the root ``VERSION`` file.

The version lives in one place — ``VERSION`` — and ``scripts/set_version.py``
propagates it into the native manifests that PyPI / crates.io / npm / CRAN
each read. This test fails, naming the offending file, if any of them drifts.
It is the safety net that turns "hunt for stale version strings across ~10
files" into "CI says: r/jsslintr/DESCRIPTION is 1.0.0 but VERSION is 1.0.1".

If this fails after a bump, you almost certainly just need to run
``python scripts/set_version.py`` and commit the result.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
_VERSION = (_REPO / "VERSION").read_text(encoding="utf-8").strip()


def _first_toml_version(path: Path) -> str:
    m = re.search(r'^version = "([^"]+)"', path.read_text(encoding="utf-8"), re.MULTILINE)
    assert m, f"no top-level `version = \"...\"` found in {path}"
    return m.group(1)


def _init_version(path: Path) -> str:
    m = re.search(r'^__version__ = "([^"]+)"', path.read_text(encoding="utf-8"), re.MULTILINE)
    assert m, f"no __version__ found in {path}"
    return m.group(1)


def _description_version(path: Path) -> str:
    m = re.search(r"^Version: (.+)$", path.read_text(encoding="utf-8"), re.MULTILINE)
    assert m, f"no `Version:` field in {path}"
    return m.group(1).strip()


def _json_version(path: Path) -> str:
    return json.loads(path.read_text(encoding="utf-8"))["version"]


def _lock_pkg_version(path: Path) -> str:
    # The root package appears both top-level and under packages[""].
    return json.loads(path.read_text(encoding="utf-8"))["packages"][""]["version"]


def _cff_version(path: Path) -> str:
    m = re.search(r"^version: (.+)$", path.read_text(encoding="utf-8"), re.MULTILINE)
    assert m, f"no `version:` field in {path}"
    return m.group(1).strip()


# (label, path, extractor) — one row per place that must equal VERSION exactly.
# The R DESCRIPTION is handled separately: it may carry a CRAN-resubmission
# revision suffix (see below).
_SOURCES = [
    ("python __version__", "src/texlint/__init__.py", _init_version),
    ("rust workspace", "rust/Cargo.toml", _first_toml_version),
    ("vscode package.json", "vscode-extension/package.json", _json_version),
    ("vscode package-lock (top)", "vscode-extension/package-lock.json", _json_version),
    ("vscode package-lock (pkg)", "vscode-extension/package-lock.json", _lock_pkg_version),
    ("R embedded jsslintr crate", "r/jsslintr/src/rust/Cargo.toml", _first_toml_version),
    (
        "R vendored jsslint-core crate",
        "r/jsslintr/src/rust/jsslint-core/Cargo.toml",
        _first_toml_version,
    ),
    ("CITATION.cff", "CITATION.cff", _cff_version),
]


@pytest.mark.parametrize("label,relpath,extractor", _SOURCES, ids=[s[0] for s in _SOURCES])
def test_manifest_version_matches_VERSION(label, relpath, extractor) -> None:
    found = extractor(_REPO / relpath)
    assert found == _VERSION, (
        f"{label} ({relpath}) is {found!r} but VERSION is {_VERSION!r}. "
        f"Run `python scripts/set_version.py` to resync all manifests."
    )


def test_r_description_version_matches_or_has_revision_suffix() -> None:
    """The R DESCRIPTION tracks VERSION but may append a ``-N`` revision.

    CRAN/R-universe submissions are sometimes rejected and resubmitted; the
    convention is to bump a trailing revision (``1.0.1-1``, ``1.0.1-2``, ...)
    without changing the suite version. So the DESCRIPTION is allowed to be
    exactly VERSION or ``VERSION-<n>`` — but nothing else (a different base
    version is still drift). Only the DESCRIPTION gets this latitude; the
    embedded Rust crates stay on the plain semver VERSION.
    """
    found = _description_version(_REPO / "r/jsslintr/DESCRIPTION")
    if found == _VERSION:
        return
    m = re.fullmatch(re.escape(_VERSION) + r"-(\d+)", found)
    assert m, (
        f"R DESCRIPTION is {found!r}; expected {_VERSION!r} or a "
        f"{_VERSION!r}-<revision> resubmission suffix (e.g. {_VERSION}-1). "
        f"Run `python scripts/set_version.py` if it is stale."
    )

