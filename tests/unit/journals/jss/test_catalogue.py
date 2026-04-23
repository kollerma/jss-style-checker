"""Tests for ``specs/003-jss-rule-catalogue/catalogue.yaml``.

Covers the ten data-model.md §1.5 invariants, the forbidden-keys check
from contracts/catalogue-schema.md, and the authority_ref resolvability
contract (FR-008, FR-010) against the vendored ``docs/jss-template/``.

The test module invokes :func:`tools._catalogue_validate.validate` as the
canonical check; focused sub-tests exist for invariants that benefit from
a dedicated error message.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from tools._catalogue_validate import (
    AUTHORITIES,
    CATEGORY_PREFIX,
    INSPECTS,
    SEVERITIES,
    validate,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
CATALOGUE_YAML = REPO_ROOT / "specs" / "003-jss-rule-catalogue" / "catalogue.yaml"
TEMPLATE_DIR = REPO_ROOT / "docs" / "jss-template"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def catalogue_doc() -> dict:
    assert CATALOGUE_YAML.exists(), (
        f"catalogue.yaml not found at {CATALOGUE_YAML}. "
        "Draft it per specs/003-jss-rule-catalogue/contracts/catalogue-schema.md."
    )
    with CATALOGUE_YAML.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# Aggregate validator contract — the single source of truth
# ---------------------------------------------------------------------------


def test_validate_returns_no_errors(catalogue_doc: dict) -> None:
    errors = validate(catalogue_doc, template_dir=TEMPLATE_DIR)
    assert errors == [], "\n".join(str(e) for e in errors)


# ---------------------------------------------------------------------------
# Focused invariants (duplicates of validator checks, kept for diagnostic clarity)
# ---------------------------------------------------------------------------


def test_top_level_keys_exactly_required(catalogue_doc: dict) -> None:
    assert set(catalogue_doc) == {"version", "source_vendored_at", "categories", "rules"}


def test_version_is_one(catalogue_doc: dict) -> None:
    assert catalogue_doc["version"] == 1


def test_source_vendored_at_is_nonempty_string(catalogue_doc: dict) -> None:
    value = catalogue_doc["source_vendored_at"]
    assert isinstance(value, str) and value.strip()


def test_every_declared_category_is_known(catalogue_doc: dict) -> None:
    for category in catalogue_doc["categories"]:
        assert category in CATEGORY_PREFIX, (
            f"category {category!r} has no rule_id prefix mapping in "
            f"tools/_catalogue_validate.py (update CATEGORY_PREFIX or drop the category)"
        )


def test_every_declared_category_has_at_least_one_rule(catalogue_doc: dict) -> None:
    used = {r["category"] for r in catalogue_doc["rules"] if isinstance(r, dict)}
    dangling = set(catalogue_doc["categories"]) - used
    assert not dangling, f"categories declared but unused: {sorted(dangling)}"


def test_rule_ids_globally_unique(catalogue_doc: dict) -> None:
    seen: dict[str, int] = {}
    for idx, rule in enumerate(catalogue_doc["rules"]):
        rid = rule.get("rule_id")
        if rid in seen:
            pytest.fail(f"rule_id {rid!r} appears at indices {seen[rid]} and {idx}")
        seen[rid] = idx


def test_rule_id_prefix_matches_category(catalogue_doc: dict) -> None:
    for rule in catalogue_doc["rules"]:
        rid = rule["rule_id"]
        category = rule["category"]
        prefix = CATEGORY_PREFIX[category]
        assert rid.startswith(prefix), (
            f"{rid!r} does not match prefix {prefix!r} for category {category!r}"
        )


def test_authority_enum(catalogue_doc: dict) -> None:
    for rule in catalogue_doc["rules"]:
        assert rule["authority"] in AUTHORITIES, (
            f"rule {rule['rule_id']}: authority {rule['authority']!r} not in {sorted(AUTHORITIES)}"
        )


def test_severity_enum(catalogue_doc: dict) -> None:
    for rule in catalogue_doc["rules"]:
        assert rule["severity"] in SEVERITIES, (
            f"rule {rule['rule_id']}: severity {rule['severity']!r} not in {sorted(SEVERITIES)}"
        )


def test_inspects_enum(catalogue_doc: dict) -> None:
    for rule in catalogue_doc["rules"]:
        inspects = rule["inspects"]
        assert isinstance(inspects, list) and inspects, f"{rule['rule_id']}: inspects empty"
        for value in inspects:
            assert value in INSPECTS, (
                f"rule {rule['rule_id']}: inspects value {value!r} not in {sorted(INSPECTS)}"
            )


def test_auto_fixable_is_strict_bool(catalogue_doc: dict) -> None:
    for rule in catalogue_doc["rules"]:
        value = rule["auto_fixable"]
        assert isinstance(value, bool), (
            f"rule {rule['rule_id']}: auto_fixable {value!r} is not a strict bool"
        )


def test_examples_are_nonempty_strings(catalogue_doc: dict) -> None:
    for rule in catalogue_doc["rules"]:
        for field in ("example_violation", "example_fix"):
            value = rule[field]
            assert isinstance(value, str) and value.strip(), (
                f"rule {rule['rule_id']}: {field} is empty or not a string"
            )


def test_description_format(catalogue_doc: dict) -> None:
    for rule in catalogue_doc["rules"]:
        d = rule["description"]
        assert isinstance(d, str) and d.strip(), f"{rule['rule_id']}: empty description"
        assert not d.endswith("."), f"{rule['rule_id']}: description must not end with period"
        assert len(d) <= 120, f"{rule['rule_id']}: description too long ({len(d)} chars)"


def test_raw_source_requires_notes_justification(catalogue_doc: dict) -> None:
    for rule in catalogue_doc["rules"]:
        if "raw_source" in rule["inspects"]:
            notes = rule.get("notes", "")
            assert isinstance(notes, str) and notes.strip(), (
                f"{rule['rule_id']}: inspects raw_source but notes is empty "
                "(Constitution §II requires justification)"
            )


def test_jss_cls_refs_resolve(catalogue_doc: dict) -> None:
    jss_cls_path = TEMPLATE_DIR / "jss.cls"
    assert jss_cls_path.exists()
    lines = jss_cls_path.read_text(encoding="utf-8").splitlines()
    for rule in catalogue_doc["rules"]:
        if rule["authority"] != "jss_cls":
            continue
        ref = rule["authority_ref"]
        assert ref.startswith("jss.cls:"), f"{rule['rule_id']}: {ref!r} missing 'jss.cls:' prefix"
        tail = ref.split(":", 1)[1]
        if tail.startswith("\\"):
            needle = tail
            assert any(needle in ln for ln in lines), (
                f"{rule['rule_id']}: macroname {tail!r} not found in jss.cls"
            )
        else:
            line_no = int(tail)
            assert 1 <= line_no <= len(lines), (
                f"{rule['rule_id']}: line {line_no} out of range 1..{len(lines)} in jss.cls"
            )


def test_article_tex_refs_resolve(catalogue_doc: dict) -> None:
    article_tex_path = TEMPLATE_DIR / "article.tex"
    assert article_tex_path.exists()
    text = article_tex_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    for rule in catalogue_doc["rules"]:
        if rule["authority"] != "article_tex":
            continue
        ref = rule["authority_ref"]
        assert ref.startswith("article.tex:"), (
            f"{rule['rule_id']}: {ref!r} missing 'article.tex:' prefix"
        )
        tail = ref.split(":", 1)[1]
        if tail.startswith("§"):
            label = tail[1:]
            needle = f"\\label{{{label}}}"
            assert needle in text, f"{rule['rule_id']}: label {label!r} not found in article.tex"
        else:
            line_no = int(tail)
            assert 1 <= line_no <= len(lines), (
                f"{rule['rule_id']}: line {line_no} out of range 1..{len(lines)} in article.tex"
            )


def test_web_refs_format(catalogue_doc: dict) -> None:
    for rule in catalogue_doc["rules"]:
        if rule["authority"] not in {"style_guide", "author_instructions"}:
            continue
        ref = rule["authority_ref"]
        assert not any(ch.isdigit() and "." in ref for ch in ref), (
            f"{rule['rule_id']}: authority_ref {ref!r} looks like a line number; "
            "web authorities use URL anchors / slugs per FR-010"
        )
        assert isinstance(ref, str) and ref.strip()
        # Format-only: either "#anchor-id" or "slug"; no internal spaces
        stripped = ref.lstrip("#")
        assert stripped and all(c.isalnum() or c == "-" for c in stripped), (
            f"{rule['rule_id']}: authority_ref {ref!r} must match [#]?[a-z0-9-]+"
        )


def test_no_forbidden_keys_on_rules(catalogue_doc: dict) -> None:
    allowed = {
        "rule_id",
        "category",
        "severity",
        "description",
        "authority",
        "authority_ref",
        "example_violation",
        "example_fix",
        "inspects",
        "auto_fixable",
        "notes",
    }
    forbidden_examples = {"fix", "fix_suggestion", "formats", "status", "owner"}
    for rule in catalogue_doc["rules"]:
        extras = set(rule) - allowed
        assert not extras, f"{rule['rule_id']}: unexpected keys {sorted(extras)}"
        assert not (set(rule) & forbidden_examples), (
            f"{rule['rule_id']}: forbidden keys present: "
            f"{sorted(set(rule) & forbidden_examples)}"
        )
