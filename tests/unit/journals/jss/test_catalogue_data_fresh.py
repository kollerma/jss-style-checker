"""Drift check — the committed ``_catalogue_data.py`` matches the catalogue.

Invariant D-5 from spec 004 ``data-model.md``: regenerating
``src/texlint/journals/jss/_catalogue_data.py`` from the current
``catalogue.yaml`` must produce byte-identical output.
"""

from __future__ import annotations

from tools.generate_catalogue_data import main


def test_catalogue_data_is_fresh():
    exit_code = main(["--check"])
    assert exit_code == 0, (
        "src/texlint/journals/jss/_catalogue_data.py is out of date with "
        "specs/003-jss-rule-catalogue/catalogue.yaml. "
        "Run: python -m tools.generate_catalogue_data"
    )
