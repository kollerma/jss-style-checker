"""Guard: the rule-catalogue data vendored into ``rust/jsslint-core/specs``
must stay byte-identical to the canonical ``specs/003-jss-rule-catalogue``
copy.

``jsslint-core``'s ``build.rs`` reads these files at build time. The copy
under the repo-root ``specs/`` is the single source of truth (the Python
catalogue generator and everyone else read it), but a published crates.io
tarball can't reach outside its own directory — so the crate ships a
vendored copy that ``build.rs`` finds first (its ``find_repo_root`` checks
the crate dir before walking up). If the two ever drift, the published
Rust engine would encode stale rule metadata while Python uses fresh data,
silently breaking Rust/Python parity for crates.io consumers. This test
fails loudly if they diverge; resync by copying the three files from
``specs/003-jss-rule-catalogue`` into ``rust/jsslint-core/specs/003-jss-rule-catalogue``.
"""

from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
_CANONICAL = _REPO / "specs" / "003-jss-rule-catalogue"
_VENDORED = _REPO / "rust" / "jsslint-core" / "specs" / "003-jss-rule-catalogue"

# Every file jsslint-core/build.rs reads from the catalogue directory.
_FILES = ["catalogue.yaml", "terms.json", "latex-macro-specs.json"]


@pytest.mark.parametrize("name", _FILES)
def test_vendored_catalogue_matches_canonical(name: str) -> None:
    vendored = _VENDORED / name
    canonical = _CANONICAL / name
    assert canonical.is_file(), f"canonical {canonical} missing"
    assert vendored.is_file(), (
        f"{vendored} is missing — without it jsslint-core cannot build from a "
        f"crates.io tarball (build.rs would panic looking for the catalogue)."
    )
    assert vendored.read_bytes() == canonical.read_bytes(), (
        f"{name} vendored into rust/jsslint-core/specs has drifted from the "
        f"canonical specs/003-jss-rule-catalogue copy. Resync them (copy the "
        f"canonical file over the vendored one) so crates.io consumers get the "
        f"same rule data as everyone else."
    )
