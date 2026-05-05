"""Shared validator for ``specs/003-jss-rule-catalogue/catalogue.yaml``.

Used by both ``tools.render_catalogue`` (so the renderer refuses to
emit markdown from an invalid YAML) and
``tests/unit/journals/jss/test_catalogue.py`` (so the same checks run
in CI).

No external deps beyond PyYAML. The module is stdlib-only on the
invariants side; PyYAML is imported by callers, not by this module.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Enums and lookup tables
# ---------------------------------------------------------------------------

AUTHORITIES: frozenset[str] = frozenset(
    {"jss_cls", "article_tex", "style_guide", "author_instructions"}
)

SEVERITIES: frozenset[str] = frozenset({"error", "warning", "info"})

INSPECTS: frozenset[str] = frozenset({"tex_files", "bib_files", "raw_source"})

# category -> rule_id prefix (contracts/catalogue-schema.md §rule_id).
CATEGORY_PREFIX: Mapping[str, str] = {
    "preamble": "JSS-PRE-",
    "structure": "JSS-STRUCT-",
    "markup": "JSS-MARKUP-",
    "citations": "JSS-CITE-",
    "references": "JSS-REFS-",
    "bibtex": "JSS-BIBTEX-",
    "naming": "JSS-NAME-",
    "capitalization": "JSS-CAP-",
    "typography": "JSS-TYPO-",
    "abbreviations": "JSS-ABBR-",
    "code_style": "JSS-CODE-",
    "code_width": "JSS-WIDTH-",
    "operators": "JSS-OPER-",
    "crossrefs": "JSS-XREF-",
    "house_style": "JSS-HOUSE-",
}

REQUIRED_TOP_KEYS: frozenset[str] = frozenset(
    {"version", "source_vendored_at", "categories", "rules"}
)

OPTIONAL_TOP_KEYS: frozenset[str] = frozenset({"retired_rule_ids"})

ALL_TOP_KEYS: frozenset[str] = REQUIRED_TOP_KEYS | OPTIONAL_TOP_KEYS

REQUIRED_RULE_KEYS: frozenset[str] = frozenset(
    {
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
    }
)

OPTIONAL_RULE_KEYS: frozenset[str] = frozenset(
    {
        "notes",
        # JSS-guide citation fields — spec 007. Strict-validation move
        # to REQUIRED is deferred until the full catalogue backfill
        # ships in a follow-up PR.
        "guide_section",
        "guide_url",
        # Spec-009 explain surface — per-rule prose plus optional
        # bad/good fragments. `explanation` ships across the whole
        # catalogue (enforced by the strict contract test
        # `test_every_rule_has_explanation`); the fixture fragments
        # are independently optional. Strict-validation move to
        # REQUIRED is deferred so YAML editors can drop the field
        # while iterating without invalidating the whole document.
        "explanation",
        "example_bad",
        "example_good",
    }
)

ALL_RULE_KEYS: frozenset[str] = REQUIRED_RULE_KEYS | OPTIONAL_RULE_KEYS

_RULE_ID_RE = re.compile(r"^JSS-[A-Z]+-\d{3}$")
_WEB_ANCHOR_RE = re.compile(r"^#?[a-z0-9][a-z0-9-]*$")


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CatalogueError:
    """A single validation failure, attributable to one rule or the doc."""

    where: str  # e.g. "top-level", "rule[JSS-CITE-001]"
    message: str

    def __str__(self) -> str:  # pragma: no cover — trivial
        return f"{self.where}: {self.message}"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def validate(
    doc: Any,
    *,
    template_dir: Path | None = None,
) -> list[CatalogueError]:
    """Validate a parsed catalogue document.

    *doc* is whatever :func:`yaml.safe_load` returned; callers parse the
    YAML themselves so this module stays PyYAML-free.

    *template_dir* points at ``docs/jss-template`` and is used for
    ``jss_cls`` / ``article_tex`` ``authority_ref`` resolvability checks.
    If ``None``, resolvability is skipped (caller might be running
    format-only lint in a sandbox without the vendored files).

    Returns a list of :class:`CatalogueError`; empty means valid.
    """
    errors: list[CatalogueError] = []

    # Top-level shape
    if not isinstance(doc, Mapping):
        errors.append(CatalogueError("top-level", "document is not a mapping"))
        return errors

    top_keys = set(doc)
    extra = top_keys - ALL_TOP_KEYS
    missing = REQUIRED_TOP_KEYS - top_keys
    if extra:
        errors.append(
            CatalogueError("top-level", f"unexpected keys: {sorted(extra)}")
        )
    if missing:
        errors.append(
            CatalogueError("top-level", f"missing keys: {sorted(missing)}")
        )
    if errors:
        return errors

    if doc["version"] != 1:
        errors.append(
            CatalogueError("top-level", f"version must be 1, got {doc['version']!r}")
        )
    if not isinstance(doc["source_vendored_at"], str) or not doc["source_vendored_at"]:
        errors.append(
            CatalogueError("top-level", "source_vendored_at must be a non-empty string")
        )

    categories = doc["categories"]
    if not isinstance(categories, list) or not all(isinstance(c, str) for c in categories):
        errors.append(
            CatalogueError("top-level", "categories must be a list of strings")
        )
        return errors

    unknown_cats = set(categories) - set(CATEGORY_PREFIX)
    if unknown_cats:
        errors.append(
            CatalogueError(
                "top-level",
                f"unknown categories (no rule_id prefix mapping): {sorted(unknown_cats)}",
            )
        )

    rules = doc["rules"]
    if not isinstance(rules, list):
        errors.append(CatalogueError("top-level", "rules must be a list"))
        return errors

    # Per-rule validation
    seen_ids: set[str] = set()
    seen_cats: set[str] = set()
    for rule in rules:
        errors.extend(_validate_rule(rule, categories, seen_ids, template_dir))
        if isinstance(rule, Mapping) and isinstance(rule.get("category"), str):
            seen_cats.add(rule["category"])

    # Every declared category has ≥ 1 rule
    dangling = set(categories) - seen_cats
    if dangling:
        errors.append(
            CatalogueError(
                "top-level",
                f"categories declared but unused: {sorted(dangling)}",
            )
        )

    # retired_rule_ids validation (optional top-level field, spec 004 Session 2026-04-23)
    errors.extend(_validate_retired_rule_ids(doc.get("retired_rule_ids"), seen_ids))

    return errors


def _validate_retired_rule_ids(
    retired: Any,
    active_ids: set[str],
) -> Iterable[CatalogueError]:
    """Validate the optional ``retired_rule_ids`` top-level field.

    Contract (per spec 004 Session 2026-04-23 clarification):
      * Field is optional; ``None`` / missing is valid.
      * When present, must be a list of strings.
      * Every entry matches the rule-id regex ``^JSS-[A-Z]+-\\d{3}$``.
      * Every entry is unique within the list.
      * No entry overlaps with the active rule-id set (a retired id must
        not also appear as an active rule — FR-004).
    """
    if retired is None:
        return
    if not isinstance(retired, list):
        yield CatalogueError("top-level", "retired_rule_ids must be a list")
        return
    if not all(isinstance(x, str) for x in retired):
        yield CatalogueError(
            "top-level", "retired_rule_ids entries must all be strings"
        )
        return
    seen_here: set[str] = set()
    for entry in retired:
        if not _RULE_ID_RE.match(entry):
            yield CatalogueError(
                "top-level",
                f"retired_rule_ids entry {entry!r} does not match JSS-<CAT>-NNN",
            )
        if entry in seen_here:
            yield CatalogueError(
                "top-level", f"retired_rule_ids entry {entry!r} is duplicated"
            )
        seen_here.add(entry)
    overlap = set(retired) & active_ids
    if overlap:
        yield CatalogueError(
            "top-level",
            f"retired_rule_ids overlap with active rule ids: {sorted(overlap)}",
        )


# ---------------------------------------------------------------------------
# Per-rule validation
# ---------------------------------------------------------------------------


def _validate_rule(
    rule: Any,
    categories: list[str],
    seen_ids: set[str],
    template_dir: Path | None,
) -> Iterable[CatalogueError]:
    where = "rule[<unidentified>]"
    if not isinstance(rule, Mapping):
        yield CatalogueError(where, "rule entry is not a mapping")
        return

    rule_id = rule.get("rule_id")
    if isinstance(rule_id, str):
        where = f"rule[{rule_id}]"

    # Key presence
    keys = set(rule)
    missing = REQUIRED_RULE_KEYS - keys
    extra = keys - ALL_RULE_KEYS
    if missing:
        yield CatalogueError(where, f"missing required keys: {sorted(missing)}")
    if extra:
        yield CatalogueError(where, f"forbidden/unknown keys: {sorted(extra)}")

    # rule_id shape
    if not isinstance(rule_id, str):
        yield CatalogueError(where, "rule_id must be a string")
        return
    if not _RULE_ID_RE.match(rule_id):
        yield CatalogueError(where, f"rule_id {rule_id!r} does not match JSS-<CAT>-NNN")
        return
    if rule_id in seen_ids:
        yield CatalogueError(where, "duplicate rule_id")
        return
    seen_ids.add(rule_id)

    # category
    category = rule.get("category")
    if category not in categories:
        yield CatalogueError(
            where, f"category {category!r} not in top-level categories list"
        )
    elif isinstance(category, str):
        expected_prefix = CATEGORY_PREFIX.get(category)
        if expected_prefix and not rule_id.startswith(expected_prefix):
            yield CatalogueError(
                where,
                f"rule_id {rule_id!r} does not match prefix {expected_prefix!r} "
                f"for category {category!r}",
            )

    # severity
    severity = rule.get("severity")
    if severity not in SEVERITIES:
        yield CatalogueError(
            where,
            f"severity {severity!r} not in {sorted(SEVERITIES)}",
        )

    # description
    description = rule.get("description")
    if not isinstance(description, str) or not description.strip():
        yield CatalogueError(where, "description must be a non-empty string")
    elif description != description.strip():
        yield CatalogueError(where, "description has leading/trailing whitespace")
    elif description.endswith("."):
        yield CatalogueError(where, "description must not end with a period")
    elif len(description) > 120:
        yield CatalogueError(
            where, f"description too long ({len(description)} > 120 chars)"
        )

    # authority
    authority = rule.get("authority")
    if authority not in AUTHORITIES:
        yield CatalogueError(
            where,
            f"authority {authority!r} not in {sorted(AUTHORITIES)}",
        )

    # authority_ref
    authority_ref = rule.get("authority_ref")
    if not isinstance(authority_ref, str) or not authority_ref.strip():
        yield CatalogueError(where, "authority_ref must be a non-empty string")
    else:
        yield from _validate_authority_ref(where, authority, authority_ref, template_dir)

    # example_violation / example_fix
    for field in ("example_violation", "example_fix"):
        value = rule.get(field)
        if not isinstance(value, str) or not value.strip():
            yield CatalogueError(where, f"{field} must be a non-empty string")

    # inspects
    inspects = rule.get("inspects")
    if not isinstance(inspects, list) or not inspects:
        yield CatalogueError(where, "inspects must be a non-empty list")
    else:
        unknown = [x for x in inspects if x not in INSPECTS]
        if unknown:
            yield CatalogueError(
                where,
                f"inspects contains unknown values {unknown!r}; allowed: {sorted(INSPECTS)}",
            )
        if "raw_source" in inspects:
            notes = rule.get("notes")
            if not isinstance(notes, str) or not notes.strip():
                yield CatalogueError(
                    where,
                    "inspects includes raw_source but notes is empty "
                    "(Constitution §II requires justification)",
                )

    # auto_fixable
    auto_fixable = rule.get("auto_fixable")
    if not isinstance(auto_fixable, bool):
        yield CatalogueError(where, "auto_fixable must be a boolean")


def _validate_authority_ref(
    where: str,
    authority: Any,
    ref: str,
    template_dir: Path | None,
) -> Iterable[CatalogueError]:
    if authority == "jss_cls":
        yield from _validate_vendored_ref(where, ref, "jss.cls", template_dir)
    elif authority == "article_tex":
        yield from _validate_vendored_ref(where, ref, "article.tex", template_dir)
    elif authority in {"style_guide", "author_instructions"}:
        if not _WEB_ANCHOR_RE.match(ref):
            yield CatalogueError(
                where,
                f"authority_ref {ref!r} must be a URL anchor / slug "
                f"(matches {_WEB_ANCHOR_RE.pattern!r}); no line numbers per FR-010",
            )
    else:
        # authority is already flagged above; don't double-report
        return


def _validate_vendored_ref(
    where: str,
    ref: str,
    expected_filename: str,
    template_dir: Path | None,
) -> Iterable[CatalogueError]:
    # Formats: "filename:LINE" (integer) or "filename:\macroname" (backslash + ident)
    if ":" not in ref:
        yield CatalogueError(
            where,
            f"authority_ref {ref!r} missing ':' — expected "
            f"'{expected_filename}:N' or '{expected_filename}:\\macroname'",
        )
        return

    filename, _, tail = ref.partition(":")
    if filename != expected_filename:
        yield CatalogueError(
            where,
            f"authority_ref filename {filename!r} does not match expected {expected_filename!r}",
        )
        return
    if not tail:
        yield CatalogueError(where, "authority_ref has empty tail after ':'")
        return

    if template_dir is None:
        # Format only — we cannot resolve without the vendored copy
        if tail.startswith("§"):
            return  # section label form, format-only ok
        if tail.startswith("\\"):
            if not re.match(r"^\\[A-Za-z@]+$", tail):
                yield CatalogueError(
                    where, f"macroname tail {tail!r} is not a valid \\macroname"
                )
            return
        try:
            int(tail)
        except ValueError:
            yield CatalogueError(
                where,
                f"authority_ref tail {tail!r} is neither a line number "
                "nor a \\macroname nor a §label",
            )
        return

    vendored_path = template_dir / expected_filename
    if not vendored_path.exists():
        yield CatalogueError(
            where, f"vendored file {vendored_path} does not exist"
        )
        return

    text = vendored_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    if tail.startswith("§"):
        # article.tex-style \label{sec:…} / \label{app:…}
        label = tail[1:]
        needle = f"\\label{{{label}}}"
        if needle not in text:
            yield CatalogueError(
                where,
                f"label {label!r} (looking for {needle!r}) not found in {expected_filename}",
            )
        return

    if tail.startswith("\\"):
        # \macroname form — exactly one hit
        if not re.match(r"^\\[A-Za-z@]+$", tail):
            yield CatalogueError(
                where, f"macroname tail {tail!r} is not a valid \\macroname"
            )
            return
        # Count lines that contain the macroname as a literal token
        hits = sum(1 for ln in lines if tail in ln)
        if hits == 0:
            yield CatalogueError(
                where, f"macroname {tail!r} not found in {expected_filename}"
            )
        # Multiple hits are allowed — many files define and use a macro on
        # different lines; the resolvability contract is "something exists",
        # not "exactly one line".
        return

    # Line number form
    try:
        line_no = int(tail)
    except ValueError:
        yield CatalogueError(
            where,
            f"authority_ref tail {tail!r} is neither a line number nor a \\macroname nor a §label",
        )
        return
    if line_no < 1 or line_no > len(lines):
        yield CatalogueError(
            where,
            f"line number {line_no} out of range 1..{len(lines)} for {expected_filename}",
        )
