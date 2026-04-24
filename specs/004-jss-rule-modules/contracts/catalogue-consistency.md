# Contract: catalogue-registration consistency

**Test location**: `tests/unit/journals/jss/test_catalogue_registration.py`
**Purpose**: enforce spec 004 FR-001 / FR-003 / FR-004 — the rule set registered via `JSSJournal.categories()` agrees with `catalogue.yaml` (as exposed through `_catalogue_data`) in both directions; retired ids are never active.

## Assertions

### R-1 — every catalogue rule is registered

For every `rule_id` in `_catalogue_data.RULES`, exactly one `Rule` object with `Rule.id == rule_id` exists in the flattened rule set from `JSSJournal().categories()`. Zero duplicates, zero missing. Failure message names the offending id(s).

### R-2 — every registered rule is catalogued

For every `Rule` in the flattened rule set, `Rule.id` appears in `_catalogue_data.RULES`. Rogue registrations fail.

### R-3 — no retired ids are registered

For every `Rule` in the flattened rule set, `Rule.id not in _catalogue_data.RETIRED_RULE_IDS`. A registration of `JSS-CITE-001` or `JSS-ABBR-002` (or any future retirement) fails CI with an explicit "retired rule id re-registered" diagnostic.

### R-4 — rule metadata matches catalogue

For every `Rule` in the flattened rule set, the following fields match `_catalogue_data.RULES[Rule.id]`:

| Rule field | Catalogue field | Equality test |
|---|---|---|
| `Rule.category` | `RULES[id]["category"]` | `==` (string) |
| `Rule.severity` | `RULES[id]["severity"]` | `==` (Severity enum) |
| `Rule.message_template` | `RULES[id]["message_template"]` | `==` (string, byte-for-byte) |
| `Rule.authority` | `RULES[id]["authority"]` | `==` (string) |

Any mismatch fails with a diagnostic naming the rule id, field, registered value, and catalogue value.

### R-5 — rule category matches module location

For every category module `src/texlint/journals/jss/rules/<category>.py`, every `Rule` in its `rules` tuple has `Rule.category == <category>`. A rule registered in the wrong module fails.

### R-6 — `rules` tuple is complete

For every category `<cat>` in `_catalogue_data.ROLLOUT_ORDER`, the set of `Rule.id`s in `<cat>`'s module's `rules` tuple equals the set of `rule_id`s in `_catalogue_data.RULES` with `category == <cat>`. Equal sets — no missing, no extras.

### R-7 — `Rule.formats` is None

Every `Rule.formats` is `None`. Spec 004 FR-024 (format narrowing is Step 4).

### R-8 — `RuleCategory` ordering matches ROLLOUT_ORDER

`JSSJournal().categories()` returns categories whose `id` fields, in order, equal `_catalogue_data.ROLLOUT_ORDER`. Spec 004 FR-007.

### R-9 — no duplicate `RuleCategory.id`

The set of `RuleCategory.id` values in the returned tuple has no duplicates.

## Test structure

```python
# tests/unit/journals/jss/test_catalogue_registration.py

from texlint.journals.jss import JSSJournal, _catalogue_data

import pytest


@pytest.fixture(scope="module")
def active_rules():
    """Flatten JSSJournal.categories() into a {rule_id: Rule} dict."""
    journal = JSSJournal()
    out = {}
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
@pytest.mark.parametrize("field", ["category", "severity", "message_template", "authority"])
def test_rule_metadata_matches_catalogue(active_rules, field):
    for rule_id, rule in active_rules.items():
        catalogue_val = _catalogue_data.RULES[rule_id][field]
        rule_val = getattr(rule, field)
        assert rule_val == catalogue_val, (
            f"{rule_id} field {field!r}: registered={rule_val!r}, "
            f"catalogue={catalogue_val!r}"
        )


# R-5, R-6
def test_rules_grouped_by_category(journal_categories):
    for rulecat in journal_categories:
        for rule in rulecat.rules:
            assert rule.category == rulecat.id, (
                f"rule {rule.id} has category={rule.category!r} "
                f"but lives in RuleCategory id={rulecat.id!r}"
            )


def test_rules_tuple_matches_catalogue_partition(journal_categories):
    registered_by_cat = {rc.id: {r.id for r in rc.rules} for rc in journal_categories}
    catalogue_by_cat = {}
    for rid, meta in _catalogue_data.RULES.items():
        catalogue_by_cat.setdefault(meta["category"], set()).add(rid)
    for cat in _catalogue_data.ROLLOUT_ORDER:
        assert registered_by_cat.get(cat, set()) == catalogue_by_cat.get(cat, set()), (
            f"category {cat!r} rule set mismatch"
        )


# R-7
def test_rule_formats_is_none(active_rules):
    for rule_id, rule in active_rules.items():
        assert rule.formats is None, (
            f"{rule_id} has formats={rule.formats}; spec 004 FR-024 requires None"
        )


# R-8, R-9
def test_category_ordering_matches_rollout_order(journal_categories):
    actual = [rc.id for rc in journal_categories]
    expected = list(_catalogue_data.ROLLOUT_ORDER)
    assert actual == expected, (
        f"RuleCategory order mismatch: got {actual}, expected {expected}"
    )


def test_no_duplicate_category_ids(journal_categories):
    ids = [rc.id for rc in journal_categories]
    assert len(ids) == len(set(ids)), f"duplicate RuleCategory.id values: {ids}"
```

## When the test fails

| Failure | Cause | Fix |
|---|---|---|
| `R-1` missing id | new catalogue rule without a matching category-module registration | add the rule's `_rule(rule_id, check_fn)` line to the category module's module-level code and regenerate `_catalogue_data.py` |
| `R-2` extra id | rogue `Rule(...)` registration or copy-paste leftover | remove the stray `Rule` from the category module |
| `R-3` retired id registered | rule id appears in both `RULES` and `RETIRED_RULE_IDS` — catalogue inconsistency, OR the rule module imports a retired id | catalogue bug (fix via spec-003 amendment); OR delete the registration in the rule module |
| `R-4` metadata mismatch | rule module hardcoded a severity / authority / message / category that differs from the catalogue | use `_rule(rule_id, check_fn)` helper (pulls fields from `_catalogue_data`) instead of hardcoding |
| `R-5` category mismatch | rule registered in the wrong module file | move the `Rule` line to the correct category module |
| `R-6` set mismatch | same as R-1 / R-2 but scoped per category | add missing / remove extras |
| `R-7` formats not None | rule explicitly sets `formats=frozenset({".tex"})` or similar | remove the `formats=` kwarg (defaults to `None`); format narrowing is Step 4 |
| `R-8` order mismatch | `JSSJournal.categories()` doesn't iterate `_catalogue_data.ROLLOUT_ORDER` | fix the `categories()` method to use the ROLLOUT_ORDER tuple |
| `R-9` duplicate category ids | should be impossible if R-8 holds | investigate `categories()` method |

## Relationship to `test_catalogue_data_fresh.py`

The sister test `test_catalogue_data_fresh.py` checks a different invariant: that the committed `_catalogue_data.py` matches what `tools/generate_catalogue_data.py` would emit from the current `catalogue.yaml`. It catches the case where the catalogue has been amended but the generated file wasn't regenerated.

Together, the two tests form a double-link that catches drift on both sides of the catalogue ↔ rule-module bridge:

- `test_catalogue_data_fresh.py`: catalogue.yaml → _catalogue_data.py drift
- `test_catalogue_registration.py`: _catalogue_data.py → registered Rules drift
