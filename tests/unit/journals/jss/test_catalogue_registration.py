"""CI consistency test — catalogue ↔ registered rules.

See ``specs/004-jss-rule-modules/contracts/catalogue-consistency.md`` for
the nine invariants (R-1..R-9). While spec 004's per-category rollout
is in progress, R-1 and R-6 are marked ``xfail`` because many categories
still have empty ``rules`` tuples; they become strict PASS as each
category's module lands.
"""

from __future__ import annotations

import pytest

from texlint.journals.jss import JSSJournal, _catalogue_data


@pytest.fixture(scope="module")
def active_rules():
    """Flatten JSSJournal.categories() into a {rule_id: Rule} dict."""
    journal = JSSJournal()
    out: dict[str, object] = {}
    for cat in journal.categories():
        for rule in cat.rules:
            assert rule.id not in out, f"duplicate registration of {rule.id}"
            out[rule.id] = rule
    return out


@pytest.fixture(scope="module")
def journal_categories():
    return JSSJournal().categories()


# R-1, R-2
def test_active_set_equals_catalogue(active_rules):
    catalogue_ids = set(_catalogue_data.RULES)
    active_ids = set(active_rules)
    missing = catalogue_ids - active_ids
    extra = active_ids - catalogue_ids
    assert not missing, f"catalogue rules not registered: {sorted(missing)}"
    assert not extra, f"registered rules not in catalogue: {sorted(extra)}"


# R-3
def test_no_retired_ids_registered(active_rules):
    retired = _catalogue_data.RETIRED_RULE_IDS
    overlap = set(active_rules) & retired
    assert not overlap, f"retired rule ids re-registered: {sorted(overlap)}"


# R-4
@pytest.mark.parametrize(
    "field", ["category", "severity", "message_template", "authority"]
)
def test_rule_metadata_matches_catalogue(active_rules, field):
    for rule_id, rule in active_rules.items():
        if rule_id not in _catalogue_data.RULES:
            # Rogue rule; R-2 handles it separately.
            continue
        catalogue_val = _catalogue_data.RULES[rule_id][field]
        rule_val = getattr(rule, field)
        assert rule_val == catalogue_val, (
            f"{rule_id} field {field!r}: registered={rule_val!r}, "
            f"catalogue={catalogue_val!r}"
        )


# R-5
def test_rules_grouped_by_category(journal_categories):
    for rulecat in journal_categories:
        for rule in rulecat.rules:
            assert rule.category == rulecat.id, (
                f"rule {rule.id} has category={rule.category!r} "
                f"but lives in RuleCategory id={rulecat.id!r}"
            )


# R-6
def test_rules_tuple_matches_catalogue_partition(journal_categories):
    registered_by_cat = {rc.id: {r.id for r in rc.rules} for rc in journal_categories}
    catalogue_by_cat: dict[str, set[str]] = {}
    for rid, meta in _catalogue_data.RULES.items():
        catalogue_by_cat.setdefault(meta["category"], set()).add(rid)
    for cat in _catalogue_data.ROLLOUT_ORDER:
        assert registered_by_cat.get(cat, set()) == catalogue_by_cat.get(cat, set()), (
            f"category {cat!r} rule set mismatch"
        )


# R-7 (updated by spec 005 FR-020): formats is None for all rules
# except the preamble category, which narrows to {"tex", "rnw"}.
_ALLOWED_FORMATS = {
    None,
    frozenset({"tex", "rnw"}),
}


def test_rule_formats_is_none(active_rules):
    for rule_id, rule in active_rules.items():
        assert rule.formats in _ALLOWED_FORMATS, (
            f"{rule_id} has formats={rule.formats}; expected None or "
            f"frozenset({{'tex', 'rnw'}})"
        )


# R-8
def test_category_ordering_matches_rollout_order(journal_categories):
    actual = [rc.id for rc in journal_categories]
    expected = list(_catalogue_data.ROLLOUT_ORDER)
    assert actual == expected, (
        f"RuleCategory order mismatch: got {actual}, expected {expected}"
    )


# R-9
def test_no_duplicate_category_ids(journal_categories):
    ids = [rc.id for rc in journal_categories]
    assert len(ids) == len(set(ids)), f"duplicate RuleCategory.id values: {ids}"


def test_no_top_level_import_side_effects():
    """J-1: importing texlint.journals.jss must not transitively import
    any category rule module. Lazy imports keep the JSS package cheap.
    """
    import importlib
    import sys

    # Drop any already-loaded rule modules so this test is independent.
    for mod in list(sys.modules):
        if mod.startswith("texlint.journals.jss.rules.") and not mod.endswith("._helpers"):
            del sys.modules[mod]

    importlib.import_module("texlint.journals.jss")

    leaked = [
        m for m in sys.modules
        if m.startswith("texlint.journals.jss.rules.")
        and not m.endswith("._helpers")
        and not m.endswith(".rules")
    ]
    assert not leaked, f"rule modules imported at top-level: {leaked}"
