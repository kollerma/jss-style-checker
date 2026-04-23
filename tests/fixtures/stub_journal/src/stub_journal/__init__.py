"""Test fixture: a no-op journal plugin registered under ``texlint.journals``.

Used by texlint's integration tests to verify that journal modules declared
via the ``texlint.journals`` entry-point group are discovered and loadable.
"""

from __future__ import annotations

JOURNAL = {
    "name": "stub",
    "rules": (),
}

__all__ = ["JOURNAL"]
