"""Catalogue citation contract tests (spec 007).

These verify the relationship between rule catalogue entries and
the JSS-guide URL index at ``docs/jss-guide/index.json``:

C-1 / C-2 / C-3: when a rule populates ``guide_section`` /
``guide_url``, the values must be consistent with the index. Tool-
side rules use the sentinel ``guide_section = "internal"``.

Spec-007 v1 ships with a partial catalogue backfill; the strict
"every citable rule MUST cite" contract from the spec is documented
as a follow-up enforcement (warned, not failed). The structural
checks below run on EVERY rule that opts into the citation surface.
"""

from __future__ import annotations

from texlint.journals.jss._catalogue_data import RULES
from texlint.journals.jss._guide_index import load_guide_index

CITABLE_CATEGORIES = frozenset(
    {
        "markup",
        "citations",
        "references",
        "naming",
        "capitalization",
        "preamble",
        "bibtex",
        "code_width",
    }
)

TOOL_SIDE_CATEGORIES = frozenset({"parse", "internal", "project"})


class TestCitationContract:
    def test_guide_index_loads(self) -> None:
        idx = load_guide_index()
        assert isinstance(idx, dict)
        assert all(isinstance(v, str) for v in idx.values())
        assert all(v.startswith("https://") for v in idx.values())

    def test_backfilled_rules_resolve_through_index(self) -> None:
        """Every rule that DOES populate guide_section + guide_url MUST
        have its values consistent with `docs/jss-guide/index.json`.
        Rules without backfill (no `guide_section`) are silently skipped
        for the v1 ship; full enforcement comes with the catalogue
        backfill PR."""
        idx = load_guide_index()
        for rule_id, meta in RULES.items():
            section = meta.get("guide_section")
            url = meta.get("guide_url")
            if not section:
                continue  # un-backfilled — skip in v1
            assert isinstance(section, str), f"{rule_id}: guide_section is not a string"
            if section == "internal":
                assert url is None, f"{rule_id}: sentinel rule has non-None guide_url"
                continue
            assert section in idx, (
                f"{rule_id}: guide_section {section!r} is not a key in "
                f"docs/jss-guide/index.json"
            )
            assert url == idx[section], (
                f"{rule_id}: guide_url {url!r} does not match "
                f"index.json[{section!r}] = {idx[section]!r}"
            )

    def test_no_todo_placeholder(self) -> None:
        """No rule may carry a literal `TODO` in either field
        (research §5)."""
        for rule_id, meta in RULES.items():
            section = meta.get("guide_section") or ""
            url = meta.get("guide_url") or ""
            assert "TODO" not in section.upper(), f"{rule_id}: TODO in guide_section"
            assert "TODO" not in url.upper(), f"{rule_id}: TODO in guide_url"

    def test_at_least_one_rule_backfilled(self) -> None:
        """Sanity: spec-007 ships a partial backfill; at least one rule
        in the catalogue exercises the citation surface so the
        renderers (terminal / JSON / SARIF / HTML) have something to
        render."""
        backfilled = [
            rid for rid, meta in RULES.items() if meta.get("guide_section")
        ]
        assert backfilled, "no rule has a guide_section yet — backfill stalled"


def test_every_citable_rule_is_backfilled() -> None:
    """Every citable-category rule must populate guide_section
    and guide_url after the spec-007 backfill PR."""
    for rule_id, meta in RULES.items():
        if meta["category"] in TOOL_SIDE_CATEGORIES:
            continue
        assert meta.get("guide_section"), (
            f"{rule_id}: guide_section is unpopulated; "
            "spec-007 backfill is required for every citable rule"
        )
        assert meta.get("guide_url"), (
            f"{rule_id}: guide_url is unpopulated"
        )


def test_every_rule_has_explanation() -> None:
    """Every rule must populate `explanation` after the spec-009
    catalogue-extension PR."""
    for rule_id, meta in RULES.items():
        assert meta.get("explanation"), (
            f"{rule_id}: explanation is unpopulated; "
            "spec-009 catalogue extension is required"
        )
        # Sanity: not a TODO placeholder.
        assert "TODO" not in (meta.get("explanation") or "").upper(), (
            f"{rule_id}: explanation contains TODO placeholder"
        )
