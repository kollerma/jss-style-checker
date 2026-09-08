"""Shared validator for ``specs/003-jss-rule-catalogue/guide-coverage.yaml``.

Contract: ``specs/027-first-time-user-gaps/contracts/coverage-file.md`` C-3.

Used by the codegen (so no build can emit a coverage table the tool would
then misreport) and by
``tests/unit/journals/jss/test_guide_coverage.py``.

The check that matters most is the last one: **every active rule must be
claimed by at least one directive**. Constitution §V says a rule without
an authority is an opinion; this is the mechanical version of that — and
the reverse direction (a directive crediting a rule that has since been
retired) is what let the markdown checklist quietly credit four retired
rules for months.

Stdlib only; callers parse the YAML.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

SOURCES: frozenset[str] = frozenset(
    {"jss_cls", "article_tex", "style_guide", "author_instructions"}
)

STATUSES: frozenset[str] = frozenset(
    {"checked", "partial", "not_checked", "out_of_scope"}
)

#: A directive's id prefix is determined by its source, so an id can
#: never drift away from the authority it cites.
PREFIX_OF: Mapping[str, str] = {
    "jss_cls": "CLS",
    "article_tex": "TEX",
    "style_guide": "SG",
    "author_instructions": "AI",
}

REQUIRED_KEYS: frozenset[str] = frozenset(
    {"id", "source", "section", "provision", "status", "rules"}
)
ALL_KEYS: frozenset[str] = REQUIRED_KEYS | {"reason"}

#: Statuses that must name at least one rule — and, conversely, the only
#: ones that may.
COVERING_STATUSES: frozenset[str] = frozenset({"checked", "partial"})

_ID_RE = re.compile(r"^(CLS|TEX|SG|AI)-\d{3}$")
_SECTION_RE = re.compile(r"^(#[a-z0-9][a-z0-9-]*|jss\.cls:\d+|article\.tex:\d+|internal)$")


@dataclass(frozen=True)
class CoverageError:
    where: str
    message: str

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.where}: {self.message}"


def validate(
    doc: Any,
    *,
    active_rule_ids: Iterable[str],
    internal_rule_ids: Iterable[str] = (),
) -> list[CoverageError]:
    """Validate a parsed ``guide-coverage.yaml``.

    *active_rule_ids* is the catalogue's current rule set;
    *internal_rule_ids* are rules exempt from needing a public guide
    directive (they have `internal` sections of their own).
    """
    errors: list[CoverageError] = []
    if not isinstance(doc, Mapping):
        return [CoverageError("top-level", "document is not a mapping")]

    if doc.get("version") != 1:
        errors.append(
            CoverageError("top-level", f"version must be 1, got {doc.get('version')!r}")
        )
    errors.extend(_validate_sources(doc.get("sources")))

    directives = doc.get("directives")
    if not isinstance(directives, list) or not directives:
        errors.append(CoverageError("top-level", "directives must be a non-empty list"))
        return errors

    active = set(active_rule_ids)
    seen_ids: set[str] = set()
    claimed: set[str] = set()

    for raw in directives:
        errors.extend(_validate_directive(raw, active, seen_ids, claimed))

    unclaimed = active - claimed - set(internal_rule_ids)
    if unclaimed:
        errors.append(
            CoverageError(
                "top-level",
                "every active rule must be claimed by at least one directive "
                f"(Constitution §V); unclaimed: {sorted(unclaimed)}",
            )
        )
    return errors


def _validate_sources(sources: Any) -> list[CoverageError]:
    if not isinstance(sources, Mapping):
        return [CoverageError("sources", "must be a mapping")]
    errors: list[CoverageError] = []
    missing = SOURCES - set(sources)
    if missing:
        errors.append(
            CoverageError("sources", f"missing authorities: {sorted(missing)}")
        )
    for name, meta in sources.items():
        if not isinstance(meta, Mapping):
            errors.append(CoverageError(f"sources[{name}]", "must be a mapping"))
            continue
        # Every authority is pinned by a date: an edition for the
        # vendored class file, a fetch date for the prose pages, which
        # is the honest equivalent for a page with no edition at all.
        if not (meta.get("date") or meta.get("fetched")):
            errors.append(
                CoverageError(
                    f"sources[{name}]",
                    "must record a `date` (vendored file) or `fetched` (web page)",
                )
            )
    return errors


def _validate_directive(
    raw: Any, active: set[str], seen_ids: set[str], claimed: set[str]
) -> list[CoverageError]:
    if not isinstance(raw, Mapping):
        return [CoverageError("directives", "each directive must be a mapping")]

    ident = raw.get("id")
    where = f"directive[{ident!r}]"
    errors: list[CoverageError] = []

    extra = set(raw) - ALL_KEYS
    missing = REQUIRED_KEYS - set(raw)
    if extra:
        errors.append(CoverageError(where, f"unexpected keys: {sorted(extra)}"))
    if missing:
        errors.append(CoverageError(where, f"missing keys: {sorted(missing)}"))
    if missing:
        return errors

    if not isinstance(ident, str) or not _ID_RE.match(ident):
        errors.append(CoverageError(where, "id must look like CLS-001 / SG-042"))
        return errors
    if ident in seen_ids:
        errors.append(CoverageError(where, "duplicate id"))
    seen_ids.add(ident)

    source = raw["source"]
    if source not in SOURCES:
        errors.append(CoverageError(where, f"unknown source {source!r}"))
    elif not ident.startswith(PREFIX_OF[source] + "-"):
        errors.append(
            CoverageError(
                where,
                f"id prefix does not match source {source!r} "
                f"(expected {PREFIX_OF[source]}-NNN)",
            )
        )

    if not isinstance(raw["section"], str) or not _SECTION_RE.match(raw["section"]):
        errors.append(
            CoverageError(
                where,
                "section must be a #anchor, a jss.cls:N / article.tex:N "
                f"locator, or 'internal'; got {raw['section']!r}",
            )
        )
    if not isinstance(raw["provision"], str) or not raw["provision"].strip():
        errors.append(CoverageError(where, "provision must be a non-empty string"))

    status = raw["status"]
    if status not in STATUSES:
        errors.append(CoverageError(where, f"unknown status {status!r}"))
        return errors

    rules = raw["rules"]
    if not isinstance(rules, list) or not all(isinstance(r, str) for r in rules):
        errors.append(CoverageError(where, "rules must be a list of strings"))
        return errors
    if status in COVERING_STATUSES and not rules:
        errors.append(
            CoverageError(where, f"status {status!r} requires at least one rule")
        )
    if status not in COVERING_STATUSES and rules:
        errors.append(
            CoverageError(
                where, f"status {status!r} must not name rules; got {rules}"
            )
        )
    retired = [r for r in rules if r not in active]
    if retired:
        errors.append(
            CoverageError(
                where,
                f"names rules that are not active in the catalogue: {retired} "
                "(retire the credit or re-judge the row)",
            )
        )
    claimed.update(rules)

    reason = raw.get("reason", "")
    if status != "checked" and not str(reason).strip():
        errors.append(
            CoverageError(where, f"status {status!r} requires a reason")
        )
    if status == "checked" and str(reason).strip():
        errors.append(
            CoverageError(where, "a checked directive needs no reason")
        )
    return errors
