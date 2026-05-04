"""Loader for the JSS-guide section→URL index file.

Single point of indirection between rule catalogue entries and the
public JSS author guide. Edits to ``docs/jss-guide/index.json``
update every renderer's URL surface without touching
``_catalogue_data.py``. Spec 007.
"""

from __future__ import annotations

import functools
import json
from pathlib import Path

_INDEX_PATH = Path(__file__).resolve().parents[3].parent / "docs" / "jss-guide" / "index.json"


@functools.cache
def load_guide_index() -> dict[str, str]:
    """Return the section→URL mapping from ``docs/jss-guide/index.json``.

    Cached for the process lifetime. Returns an empty dict when the
    file is missing (Constitution §III: graceful, no raise).
    """
    if not _INDEX_PATH.is_file():
        return {}
    data = json.loads(_INDEX_PATH.read_text(encoding="utf-8"))
    sections = data.get("sections", {})
    if not isinstance(sections, dict):
        return {}
    return {str(k): str(v) for k, v in sections.items()}
