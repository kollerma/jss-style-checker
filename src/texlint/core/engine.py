"""Journal loading and rule-engine execution.

The engine is the one module that knows how to:
  * resolve a ``--journal`` id into a ``JournalRuleModule`` via entry points
    (Constitution §IV, spec FR-006);
  * apply rules to a ``ParsedDocument`` while honouring ``ignore_rules`` and
    per-rule ``formats`` filters (spec FR-008, FR-009);
  * derive per-category ``PASS`` / ``FAIL`` / ``SKIPPED`` status and the overall
    ``compliance_percentage`` (spec FR-010 + Clarification Q3);
  * attach parse-error violations to the synthetic ``parse`` category, which is
    excluded from ``compliance_percentage`` (Clarification Q1);
  * isolate rule crashes: a rule whose ``check`` / ``check_project``
    raises is reported as a :class:`SkippedRule` (reason
    ``internal error: ...``) and the run continues with the remaining
    rules, instead of aborting the whole report;
  * honour inline suppression comments (``% jss-lint: ignore [RULE-IDS]``)
    by filtering matching findings before they enter the report.
"""

from __future__ import annotations

import dataclasses as _dc
import importlib.metadata as _im
from collections import defaultdict
from collections.abc import Mapping
from inspect import isclass
from pathlib import Path

from texlint import __version__ as _tool_version
from texlint.api import (
    CategoryStatus,
    CategorySummary,
    ComplianceReport,
    InvalidJournalError,
    JournalNotFoundError,
    JournalRuleModule,
    ParsedBibFile,
    ParsedDocument,
    ParsedProject,
    ParsedRmdFile,
    ParsedTexFile,
    SkippedRule,
    ToolConfig,
    Violation,
    _file_format,
)
from texlint.core import suppress as _suppress


class UnsupportedSuffixError(ValueError):
    """Raised when ``parse_document`` encounters a path with an extension
    outside the dispatch map. Caller (CLI) translates to exit code 2.
    """

    def __init__(self, path: Path) -> None:
        super().__init__(
            f"unsupported file extension: {path.name!r}. "
            f"Supported: .tex, .ltx, .bib, .Rnw, .Rmd (case-insensitive)."
        )
        self.path = path


def parse_document(
    paths, *, sources: Mapping[Path, str] | None = None
) -> ParsedDocument:
    """Dispatch ``paths`` to the appropriate parsers by extension and
    assemble a :class:`ParsedDocument`.

    ``sources`` is an optional overlay of in-memory contents keyed by
    path: a path present in the overlay is parsed from its string
    instead of from disk. The LSP server lints (possibly unsaved)
    editor buffers through this seam — the file on disk is never
    read or written for an overlaid path.

    Raises :class:`UnsupportedSuffixError` on unknown extensions.
    """
    from texlint.core.parser import (
        parse_bib_file,
        parse_bib_source,
        parse_rmd_file,
        parse_rnw_file,
        parse_rnw_source,
        parse_tex_file,
        parse_tex_source,
    )
    from texlint.core.rmd_parser import parse_rmd_source

    overlay: Mapping[Path, str] = sources or {}
    tex_files: list[ParsedTexFile] = []
    bib_files: list[ParsedBibFile] = []
    rmd_files: list[ParsedRmdFile] = []
    for raw in paths:
        path = Path(raw) if not isinstance(raw, Path) else raw
        suffix = path.suffix.lower()
        source = overlay.get(path)
        if suffix in (".tex", ".ltx"):
            # `.ltx` is just LaTeX with a different convention; some
            # JSS vignettes (e.g., shrinkTVP) ship under that name.
            tex_files.append(
                parse_tex_source(source, path)
                if source is not None
                else parse_tex_file(path)
            )
        elif suffix == ".bib":
            bib_files.append(
                parse_bib_source(source, path)
                if source is not None
                else parse_bib_file(path)
            )
        elif suffix == ".rnw":
            tex_files.append(
                parse_rnw_source(source, path)
                if source is not None
                else parse_rnw_file(path)
            )
        elif suffix == ".rmd":
            rmd_files.append(
                parse_rmd_source(source, path)
                if source is not None
                else parse_rmd_file(path)
            )
        else:
            raise UnsupportedSuffixError(path)
    return ParsedDocument(
        tex_files=tuple(tex_files),
        bib_files=tuple(bib_files),
        rmd_files=tuple(rmd_files),
    )


_RESOLVE_LINTABLE_SUFFIXES = {".tex", ".ltx", ".bib", ".rnw", ".rmd"}


def resolve_project(root: Path) -> ParsedProject:
    """Walk *root*'s ``\\input``/``\\include``/``\\subfile``/``\\bibliography``
    graph (spec 013 ``core/resolver.py::resolve``) and assemble a
    :class:`ParsedProject`.

    ``documents`` is a *single* combined :class:`ParsedDocument` over
    every reachable file — deliberately, not one document per file.
    Rules dispatched via plain ``rule.check`` (e.g. the JSS-REFS-*
    citation/bibliography cross-checks) reason about ``doc.bib_files``
    and ``doc.all_tex_like()`` together to scope bib entries to what's
    actually ``\\cite``'d (``_helpers._iter_referenced_entries``);
    splitting the project into isolated single-file documents would
    silently widen every such rule to "bib-only" scope the moment a
    project is auto-resolved, since no individual per-file document
    would ever see both the citing tex and the cited bib at once. A
    single combined document reproduces exactly the existing flat
    multi-file behaviour (``jss-lint a.tex b.tex``) for ``rule.check``,
    while ``tree``/``missing`` still carry the full per-file resolver
    graph for ``rule.check_project`` (JSS-PROJECT-001/002). Per-file
    :class:`Violation` attribution is unaffected either way — it comes
    from each parsed file's own ``path``, not from document grouping.

    Only files with a lintable suffix are parsed. ``resolver.py``'s
    walk doesn't filter by extension at all — a real JSS vignette can
    legitimately ``\\input`` a non-``.tex`` file, e.g. a bundled custom
    ``.cls`` (observed in the wild: ``pmclust``'s
    ``\\input{./pmclust-include/my_jss.cls}``) — so a resolved file
    with an unsupported suffix is silently excluded from the document
    set (it still contributes to ``tree``/cycle-detection below) rather
    than raising :class:`~texlint.core.engine.UnsupportedSuffixError`
    and aborting the whole lint over one non-source include.
    """
    from texlint.core.resolver import resolve

    resolved = resolve(root)
    lintable = [
        p for p in resolved.files if p.suffix.lower() in _RESOLVE_LINTABLE_SUFFIXES
    ]
    documents = (parse_document(lintable),)

    children: dict[Path, list[Path]] = {}
    for ref in resolved.references:
        if not ref.found:
            continue
        bucket = children.setdefault(ref.parent, [])
        if ref.target not in bucket:
            bucket.append(ref.target)
    tree = {path: tuple(children.get(path, ())) for path in resolved.files}

    return ParsedProject(
        root=resolved.root,
        documents=documents,
        tree=tree,
        missing=resolved.missing,
    )


_ENTRY_POINT_GROUP = "texlint.journals"
_PARSE_RULE_ID = "JSS-PARSE-000"
_PARSE_CATEGORY_ID = "parse"
_PARSE_CATEGORY_TITLE = "Parse errors"

# Confidence-tier ordering for the ``min_confidence`` gate.
_CONFIDENCE_RANK: dict[str, int] = {"low": 0, "medium": 1, "high": 2}


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
    target: ParsedDocument | ParsedProject,
    journal: JournalRuleModule,
) -> ComplianceReport:
    """Execute ``journal``'s rules against ``target``.

    ``target`` may be a :class:`ParsedDocument` (existing single-file
    flow) or a :class:`ParsedProject` (spec 013). When a project is
    passed, every rule with ``check_project`` set runs once on the
    whole project; every rule with ``check`` set runs once per
    :class:`ParsedDocument` in :attr:`ParsedProject.documents`.

    When a :class:`ParsedDocument` is passed, behaviour is identical
    to the pre-spec-013 engine: only ``rule.check`` runs;
    ``rule.check_project`` is ignored.
    """
    ignore = frozenset(config.ignore_rules)

    violations_by_category: dict[str, list[Violation]] = defaultdict(list)
    applied_by_category: dict[str, int] = defaultdict(int)
    passed_by_category: dict[str, int] = defaultdict(int)
    skipped: list[SkippedRule] = []

    if isinstance(target, ParsedProject):
        project: ParsedProject | None = target
        documents: tuple[ParsedDocument, ...] = target.documents
    else:
        project = None
        documents = (target,)

    # Derive input formats present across the project / document. Empty → empty set.
    input_formats: set[str] = set()
    for doc in documents:
        input_formats.update(_file_format(f) for f in doc.all_files())

    # Inline-suppression index (``% jss-lint: ignore [RULE-IDS]``),
    # built once per run. Suppression applies to rule findings only;
    # parse errors are collected separately below and stay visible.
    suppression_index = _suppress.build_index(documents)

    categories = journal.categories()
    min_confidence_rank = _CONFIDENCE_RANK.get(config.min_confidence, 0)

    for category in categories:
        for rule in category.rules:
            if rule.id in ignore:
                continue
            # Confidence gate (spec follow-up to the architecture
            # review): rules whose measured-precision tier sits below
            # ``--min-confidence`` are skipped, visibly (--verbose), so
            # the trade-off stays a presentation-time decision instead
            # of a code-time one.
            rule_confidence = getattr(rule, "confidence", "high")
            if _CONFIDENCE_RANK.get(rule_confidence, 2) < min_confidence_rank:
                skipped.append(SkippedRule(
                    rule_id=rule.id,
                    reason=(
                        f"confidence {rule_confidence} below "
                        f"min_confidence={config.min_confidence}"
                    ),
                ))
                continue
            # Format filter: skip rules whose formats don't intersect the
            # document's input formats (spec 005 FR-008). The format
            # filter governs ``rule.check`` only; ``check_project``
            # always runs (it operates on the whole project, including
            # files with non-matching formats — e.g., a project-level
            # cycle-detector spans .tex + .bib).
            check_ran = False
            check_skipped_for_format = False
            project_ran = False
            rule_violations: list[Violation] = []

            # Each rule's findings are buffered and committed only when
            # the rule completes. A rule that raises is reported as a
            # SkippedRule ("internal error: ...") and the run continues:
            # one buggy heuristic must not destroy the other rules'
            # report (previously any rule exception aborted the whole
            # run with no output at all).
            try:
                if rule.check is not None:
                    if rule.formats is not None and not (
                        rule.formats & input_formats
                    ):
                        check_skipped_for_format = True
                    else:
                        for doc in documents:
                            if not any(True for _ in doc.files_for_rule(rule)):
                                continue
                            check_ran = True
                            rule_violations.extend(rule.check(doc, config))
                if project is not None and rule.check_project is not None:
                    project_ran = True
                    rule_violations.extend(rule.check_project(project))
            except Exception as exc:  # noqa: BLE001 — crash isolation per rule
                skipped.append(SkippedRule(
                    rule_id=rule.id,
                    reason=f"internal error: {type(exc).__name__}: {exc}",
                ))
                continue

            if not check_ran and not project_ran:
                # Either the format filter excluded the rule, or no input
                # file matched. Format-mismatch is reported as a SkippedRule;
                # plain "no matched files" silently drops out.
                if check_skipped_for_format and rule.check_project is None:
                    skipped.append(SkippedRule(
                        rule_id=rule.id,
                        reason=(
                            f"format mismatch (rule formats={sorted(rule.formats)}; "
                            f"inputs={sorted(input_formats)})"
                        ),
                    ))
                continue

            if suppression_index:
                rule_violations = [
                    v
                    for v in rule_violations
                    if not _suppress.is_suppressed(suppression_index, v)
                ]

            if config.severity_overrides:
                # Central remap so every renderer (terminal / JSON /
                # SARIF / LSP) and the exit-code policy agree.
                rule_violations = [
                    _dc.replace(v, severity=config.severity_overrides[v.rule_id])
                    if v.rule_id in config.severity_overrides
                    else v
                    for v in rule_violations
                ]

            applied_by_category[category.id] += 1
            if not rule_violations:
                # No findings — including "all findings inline-suppressed":
                # the author has explicitly signed off on those lines.
                passed_by_category[category.id] += 1
            violations_by_category[category.id].extend(rule_violations)

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

    # Collect pre-existing parse-error violations from each parsed document.
    parse_errors_list: list[Violation] = []
    for doc in documents:
        parse_errors_list.extend(
            v for v in doc.all_violations() if v.rule_id == _PARSE_RULE_ID
        )
    parse_errors = tuple(parse_errors_list)
    if parse_errors:
        summaries.append(
            CategorySummary(
                category_id=_PARSE_CATEGORY_ID,
                title=_PARSE_CATEGORY_TITLE,
                status=CategoryStatus.FAIL,
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
        skipped_rules=tuple(skipped),
    )
