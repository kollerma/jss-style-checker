"""Spec 009 — explain renderer tests."""

from __future__ import annotations

import pytest

from texlint.explain import did_you_mean, render


class TestSingleRule:
    def test_terminal_includes_rule_id_and_message(self) -> None:
        out = render("JSS-CITE-002", fmt="terminal")
        assert "JSS-CITE-002" in out
        assert "citations" in out

    def test_markdown_has_h1_header(self) -> None:
        out = render("JSS-CITE-002", fmt="markdown")
        assert out.startswith("# JSS-CITE-002")
        assert "**Severity:**" in out
        assert "**Category:**" in out

    def test_markdown_links_to_guide(self) -> None:
        # JSS-CITE-002 was backfilled in spec 007.
        out = render("JSS-CITE-002", fmt="markdown")
        assert "[§3.2 Citations]" in out
        assert "https://" in out

    def test_unknown_raises_keyerror(self) -> None:
        with pytest.raises(KeyError):
            render("JSS-FOO-999", fmt="terminal")

    def test_case_normalisation(self) -> None:
        out = render("jss-cite-002", fmt="terminal")
        assert "JSS-CITE-002" in out


class TestListing:
    def test_listing_terminal_has_categories(self) -> None:
        out = render(None, fmt="terminal")
        assert "citations" in out
        assert "JSS-CITE-002" in out

    def test_listing_markdown_has_h1_and_h2(self) -> None:
        out = render(None, fmt="markdown")
        assert out.startswith("# JSS-lint rule catalogue")
        assert "## citations" in out


class TestDidYouMean:
    def test_close_match_suggested(self) -> None:
        suggestions = did_you_mean("JSS-CITE-022")
        assert any(s.startswith("JSS-CITE-") for s in suggestions)

    def test_unrelated_returns_empty(self) -> None:
        assert did_you_mean("ZZZZZZ-NOPE") == []
