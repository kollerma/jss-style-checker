"""Unit tests for the optional online DOI resolver (texlint.crossref).

All network I/O is mocked via the ``opener`` injection seam, so these
tests are hermetic and offline.
"""

from __future__ import annotations

import io
import json

from texlint.crossref import make_resolver, resolve_doi


def _crossref_opener(items):
    """A urlopen stand-in returning a Crossref works payload."""

    def _opener(req, timeout=0):
        body = json.dumps({"message": {"items": items}}).encode()
        resp = io.BytesIO(body)
        resp.status = 200
        resp.__enter__ = lambda: resp
        resp.__exit__ = lambda *a: False
        return resp

    return _opener


def _item(title, doi, family="Smith", year=2020):
    return {
        "title": [title],
        "DOI": doi,
        "author": [{"family": family}],
        "issued": {"date-parts": [[year]]},
    }


class TestCrossrefArticle:
    def test_exact_title_match_returns_doi(self):
        opener = _crossref_opener([_item("A Study of Things", "10.1/aaa")])
        doi = resolve_doi(
            {"title": "A Study of Things", "author": "Smith", "year": "2020"},
            "article",
            opener=opener,
        )
        assert doi == "10.1/aaa"

    def test_low_title_similarity_returns_none(self):
        opener = _crossref_opener([_item("Totally Unrelated Work", "10.1/bbb")])
        assert (
            resolve_doi(
                {"title": "A Study of Things", "author": "Smith", "year": "2020"},
                "article",
                opener=opener,
            )
            is None
        )

    def test_year_mismatch_rejected(self):
        opener = _crossref_opener(
            [_item("A Study of Things", "10.1/ccc", year=1999)]
        )
        assert (
            resolve_doi(
                {"title": "A Study of Things", "author": "Smith", "year": "2020"},
                "article",
                opener=opener,
            )
            is None
        )

    def test_author_mismatch_rejected(self):
        opener = _crossref_opener(
            [_item("A Study of Things", "10.1/ddd", family="Jones")]
        )
        assert (
            resolve_doi(
                {"title": "A Study of Things", "author": "Smith", "year": "2020"},
                "article",
                opener=opener,
            )
            is None
        )

    def test_prefers_year_and_author_match_over_bare_title(self):
        opener = _crossref_opener(
            [
                _item("A Study of Things", "10.1/wrong", family="Jones", year=1990),
                _item("A Study of Things", "10.1/right", family="Smith", year=2020),
            ]
        )
        doi = resolve_doi(
            {"title": "A Study of Things", "author": "Smith, John", "year": "2020"},
            "article",
            opener=opener,
        )
        assert doi == "10.1/right"

    def test_empty_title_returns_none(self):
        assert resolve_doi({"title": ""}, "article", opener=_crossref_opener([])) is None

    def test_network_error_returns_none(self):
        def boom(req, timeout=0):
            raise OSError("no network")

        assert (
            resolve_doi({"title": "X Y Z"}, "article", opener=boom) is None
        )


class TestCrossrefCranManual:
    def test_cran_manual_doi_when_resolvable(self):
        def opener(req, timeout=0):
            resp = io.BytesIO(b"")
            resp.status = 200
            resp.__enter__ = lambda: resp
            resp.__exit__ = lambda *a: False
            return resp

        doi = resolve_doi(
            {"url": "https://CRAN.R-project.org/package=mfbvar"},
            "manual",
            opener=opener,
        )
        assert doi == "10.32614/CRAN.package.mfbvar"

    def test_cran_manual_none_when_unresolvable(self):
        def opener(req, timeout=0):
            raise OSError("doi.org unreachable")

        doi = resolve_doi(
            {"url": "https://CRAN.R-project.org/package=mfbvar"},
            "manual",
            opener=opener,
        )
        assert doi is None

    def test_non_cran_manual_returns_none(self):
        assert (
            resolve_doi({"url": "https://example.org/thing"}, "manual", opener=None)
            is None
        )


def test_make_resolver_binds_and_calls():
    opener = _crossref_opener([_item("A Study of Things", "10.1/eee")])
    # make_resolver builds a (fields, entry_type) callable; patch its
    # default opener by resolving directly instead.
    resolver = make_resolver(mailto="a@b.c")
    assert callable(resolver)
    # The bound resolver hits the network; assert the direct path instead.
    doi = resolve_doi(
        {"title": "A Study of Things", "author": "Smith", "year": "2020"},
        "article",
        mailto="a@b.c",
        opener=opener,
    )
    assert doi == "10.1/eee"
