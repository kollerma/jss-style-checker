"""Spec 011 — per-document AST cache for the LSP server.

Cache key: ``(uri, textDocument.version)``. Each entry holds the
parsed view of the document plus the diagnostics most recently
published from it. Replacing the entry on a new version is the
only invalidation path — no time / mtime / hash heuristics
(spec 011 §research §3).
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class CachedDocument:
    """Snapshot of a single open document at a specific version.

    ``parsed`` is whatever the engine returned (a `ParsedDocument`
    today; opaque to the cache). ``diagnostics`` is the iterable
    last published; cached so re-rendering for code-action lookups
    doesn't need to re-lint.
    """

    uri: str
    version: int
    parsed: Any
    diagnostics: tuple[Any, ...] = ()


@dataclass
class DocumentCache:
    """In-memory `(uri, version)` -> CachedDocument map.

    Not thread-safe; pygls handles its own request serialisation.
    """

    _by_uri: dict[str, CachedDocument] = field(default_factory=dict)

    def get(self, uri: str) -> CachedDocument | None:
        return self._by_uri.get(uri)

    def put(self, entry: CachedDocument) -> None:
        self._by_uri[entry.uri] = entry

    def evict(self, uri: str) -> None:
        self._by_uri.pop(uri, None)

    def open_uris(self) -> Iterable[str]:
        return tuple(self._by_uri.keys())

    def clear(self) -> None:
        self._by_uri.clear()

    def is_current(self, uri: str, version: int | None) -> bool:
        """Return True iff a cached entry for *uri* exists and matches
        *version* exactly. ``version`` is None when the editor sends a
        notification without a version field — in that case the cache
        is treated as stale (conservative)."""
        if version is None:
            return False
        entry = self._by_uri.get(uri)
        return entry is not None and entry.version == version
