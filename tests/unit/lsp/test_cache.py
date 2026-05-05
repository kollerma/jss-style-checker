"""Spec 011 — DocumentCache unit tests."""

from __future__ import annotations

from texlint.lsp.cache import CachedDocument, DocumentCache


def _entry(uri: str, version: int) -> CachedDocument:
    return CachedDocument(uri=uri, version=version, parsed=object())


class TestPutGet:
    def test_round_trip(self) -> None:
        c = DocumentCache()
        e = _entry("file:///x", 1)
        c.put(e)
        assert c.get("file:///x") is e

    def test_get_missing(self) -> None:
        assert DocumentCache().get("file:///none") is None


class TestVersionInvalidation:
    def test_replace_on_new_version(self) -> None:
        c = DocumentCache()
        c.put(_entry("file:///x", 1))
        c.put(_entry("file:///x", 2))
        e = c.get("file:///x")
        assert e is not None
        assert e.version == 2

    def test_is_current_match(self) -> None:
        c = DocumentCache()
        c.put(_entry("file:///x", 5))
        assert c.is_current("file:///x", 5) is True

    def test_is_current_mismatch(self) -> None:
        c = DocumentCache()
        c.put(_entry("file:///x", 5))
        assert c.is_current("file:///x", 4) is False

    def test_is_current_none_version(self) -> None:
        c = DocumentCache()
        c.put(_entry("file:///x", 5))
        assert c.is_current("file:///x", None) is False

    def test_is_current_unknown_uri(self) -> None:
        assert DocumentCache().is_current("file:///none", 1) is False


class TestEvict:
    def test_evict_removes(self) -> None:
        c = DocumentCache()
        c.put(_entry("file:///x", 1))
        c.evict("file:///x")
        assert c.get("file:///x") is None

    def test_evict_unknown_is_noop(self) -> None:
        DocumentCache().evict("file:///never-was-here")  # no exception

    def test_open_uris(self) -> None:
        c = DocumentCache()
        c.put(_entry("file:///a", 1))
        c.put(_entry("file:///b", 1))
        assert set(c.open_uris()) == {"file:///a", "file:///b"}

    def test_clear(self) -> None:
        c = DocumentCache()
        c.put(_entry("file:///a", 1))
        c.clear()
        assert tuple(c.open_uris()) == ()
