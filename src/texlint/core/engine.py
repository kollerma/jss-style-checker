"""Journal loading and rule-engine execution.

The engine is the one module that knows how to:
  * resolve a ``--journal`` id into a ``JournalRuleModule`` via entry points
    (Constitution §IV, spec FR-006);
  * apply rules to a ``ParsedDocument`` while honouring ``ignore_rules`` and
    per-rule ``formats`` filters (spec FR-008, FR-009);
  * derive per-category ``PASS`` / ``FAIL`` / ``SKIPPED`` status and the overall
    ``compliance_percentage`` (spec FR-010 + Clarification Q3);
  * attach parse-error violations to the synthetic ``parse`` category, which is
    excluded from ``compliance_percentage`` (Clarification Q1).
"""

from __future__ import annotations

import importlib.metadata as _im
from collections import defaultdict
from inspect import isclass

from texlint import __version__ as _tool_version
from texlint.api import (
    CategorySummary,
    ComplianceReport,
    InvalidJournalError,
    JournalNotFoundError,
    JournalRuleModule,
    ParsedDocument,
    ToolConfig,
    Violation,
)

_ENTRY_POINT_GROUP = "texlint.journals"
_PARSE_RULE_ID = "JSS-PARSE-000"
_PARSE_CATEGORY_ID = "parse"
_PARSE_CATEGORY_TITLE = "Parse errors"


def load_journal(journal_id: str) -> JournalRuleModule:
    eps = _im.entry_points(group=_ENTRY_POINT_GROUP)
    # Py 3.10+ selectable API:
    selected = list(eps.select(name=journal_id)) if hasattr(eps, "select") else [
        ep for ep in eps if ep.name == journal_id
    ]
    if not selected:
        raise JournalNotFoundError(
            f"No journal registered under '{journal_id}'. "
            f"Known: {sorted(ep.name for ep in eps)}"
        )

    ep = selected[0]
    obj = ep.load()
    if isclass(obj) and issubclass(obj, JournalRuleModule):
        instance = obj()
    elif isinstance(obj, JournalRuleModule):
        instance = obj
    else:
        raise InvalidJournalError(
            f"Entry point '{journal_id}' must resolve to a JournalRuleModule "
            f"subclass or instance; got {type(obj).__name__}."
        )
    return instance


def run(
    config: ToolConfig,
    parsed_document: ParsedDocument,
    journal: JournalRuleModule,
) -> ComplianceReport:
    ignore = frozenset(config.ignore_rules)

    violations_by_category: dict[str, list[Violation]] = defaultdict(list)
    applied_by_category: dict[str, int] = defaultdict(int)
    passed_by_category: dict[str, int] = defaultdict(int)

    categories = journal.categories()

    for category in categories:
        for rule in category.rules:
            if rule.id in ignore:
                continue
            # A rule is "applied" only if at least one input file matches.
            matched_files = list(parsed_document.files_for_rule(rule))
            if not matched_files:
                continue
            applied_by_category[category.id] += 1
            before = len(violations_by_category[category.id])
            for v in rule.check(parsed_document, config):
                violations_by_category[category.id].append(v)
            produced = len(violations_by_category[category.id]) - before
            if produced == 0:
                passed_by_category[category.id] += 1

    summaries: list[CategorySummary] = []
    for category in categories:
        summaries.append(
            CategorySummary.build(
                category_id=category.id,
                title=category.title,
                rules_applied=applied_by_category.get(category.id, 0),
                rules_passed=passed_by_category.get(category.id, 0),
                violations=tuple(violations_by_category.get(category.id, ())),
            )
        )

    # Collect pre-existing parse-error violations from the parsed document.
    parse_errors = tuple(
        v for v in parsed_document.all_violations() if v.rule_id == _PARSE_RULE_ID
    )
    if parse_errors:
        summaries.append(
            CategorySummary(
                category_id=_PARSE_CATEGORY_ID,
                title=_PARSE_CATEGORY_TITLE,
                status=__import__("texlint.api", fromlist=["CategoryStatus"]).CategoryStatus.FAIL,
                rules_applied=0,
                rules_passed=0,
                violations=parse_errors,
            )
        )

    # Flatten + deterministic sort.
    all_violations: list[Violation] = list(parse_errors)
    for s in summaries:
        if s.category_id == _PARSE_CATEGORY_ID:
            continue
        all_violations.extend(s.violations)
    sorted_violations = tuple(sorted(all_violations, key=lambda v: v.sort_key()))

    # Percentage: PASS / (PASS + FAIL), excluding SKIPPED and the synthetic parse category.
    # Deferred import to avoid the circular feel even though api.py does not import engine.
    from texlint.api import CategoryStatus  # noqa: WPS433

    ratable = [
        s
        for s in summaries
        if s.category_id != _PARSE_CATEGORY_ID
        and s.status in (CategoryStatus.PASS, CategoryStatus.FAIL)
    ]
    if ratable:
        passed = sum(1 for s in ratable if s.status == CategoryStatus.PASS)
        percentage: float | None = round(100.0 * passed / len(ratable), 1)
    else:
        percentage = None

    return ComplianceReport(
        tool_version=_tool_version,
        journal_id=journal.id,
        violations=sorted_violations,
        categories=tuple(summaries),
        compliance_percentage=percentage,
    )
