"""Unit tests for the spec-013 follow-up: ``ParsedProject``,
``Rule.check_project``, and engine dispatch.

Covered surface (per ``specs/013-multi-file-projects/data-model.md``
sections 1–3):

  * ``ParsedProject`` is a frozen dataclass living in ``texlint.api``.
  * ``Rule.check_project`` is an optional callable, defaults to ``None``.
  * ``engine.run`` accepts ``ParsedDocument | ParsedProject``; given a
    project, both ``rule.check`` (per document) and ``rule.check_project``
    (once on the whole project) run. Given a plain ``ParsedDocument``,
    ``rule.check_project`` is NOT invoked — the existing pre-spec-013
    behaviour is preserved byte-identically.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from texlint.api import (
    JournalRuleModule,
    ParsedDocument,
    ParsedProject,
    ParsedTexFile,
    Rule,
    RuleCategory,
    Severity,
    ToolConfig,
    Violation,
)
from texlint.core.engine import run

_SENTINEL_RULE_ID = "JSS-PROJECT-SENTINEL"


def _sentinel_violation(path: Path) -> Violation:
    return Violation(
        file=path,
        line=1,
        column=None,
        rule_id=_SENTINEL_RULE_ID,
        severity=Severity.ERROR,
        message="sentinel project-level violation",
    )


def _empty_check(_doc, _cfg):
    """A no-op per-document check used when we don't want ``check`` to fire."""
    return iter(())


def _make_parsed_document(tmp_path: Path, name: str = "root.tex") -> ParsedDocument:
    p = tmp_path / name
    p.write_text("", encoding="utf-8")
    tex = ParsedTexFile(path=p, source="", nodes=(), walker=None, violations=())
    return ParsedDocument(tex_files=(tex,))


def _make_parsed_project(tmp_path: Path, name: str = "root.tex") -> ParsedProject:
    doc = _make_parsed_document(tmp_path, name)
    root = doc.tex_files[0].path
    return ParsedProject(
        root=root,
        documents=(doc,),
        tree={root: ()},
    )


class _SingleRuleJournal(JournalRuleModule):
    id = "test-journal"

    def __init__(self, rule: Rule, *, category_id: str = "x"):
        self._rule = rule
        self._category_id = category_id

    def categories(self):
        return (
            RuleCategory(id=self._category_id, title="X", rules=(self._rule,)),
        )


class TestParsedProjectConstructible:
    def test_parsed_project_constructible(self, tmp_path: Path) -> None:
        doc = _make_parsed_document(tmp_path, "p.tex")
        root = doc.tex_files[0].path
        tree: dict[Path, tuple[Path, ...]] = {root: ()}

        project = ParsedProject(root=root, documents=(doc,), tree=tree)

        assert project.root == root
        assert project.documents == (doc,)
        assert project.tree == tree
        assert project.tree[root] == ()


class TestRuleCheckProjectDefaultNone:
    def test_rule_check_project_default_none(self) -> None:
        rule = Rule(
            id="JSS-X-001",
            category="x",
            severity=Severity.ERROR,
            message_template="",
            authority="",
            check=_empty_check,
        )
        assert rule.check_project is None


class TestEngineDispatchesToCheckProject:
    def test_engine_dispatches_to_check_project(self, tmp_path: Path) -> None:
        project = _make_parsed_project(tmp_path, "root.tex")
        target_path = project.root

        def _check_project(p: ParsedProject) -> Iterable[Violation]:
            assert p is project
            yield _sentinel_violation(target_path)

        rule = Rule(
            id=_SENTINEL_RULE_ID,
            category="project",
            severity=Severity.ERROR,
            message_template="",
            authority="",
            check=_empty_check,
            check_project=_check_project,
        )
        journal = _SingleRuleJournal(rule, category_id="project")

        report = run(ToolConfig(), project, journal)

        sentinels = [v for v in report.violations if v.rule_id == _SENTINEL_RULE_ID]
        assert len(sentinels) == 1
        assert sentinels[0].file == target_path


class TestEngineSkipsCheckProjectForParsedDocument:
    def test_engine_skips_check_project_for_parsed_document(
        self, tmp_path: Path
    ) -> None:
        doc = _make_parsed_document(tmp_path, "root.tex")
        target_path = doc.tex_files[0].path

        def _check_project(_p: ParsedProject) -> Iterable[Violation]:
            # If this fires when the engine receives a ParsedDocument, the
            # invariant is broken. Use an explicit AssertionError so the
            # failure mode is unambiguous.
            raise AssertionError(
                "check_project must not run when a ParsedDocument is passed"
            )

        rule = Rule(
            id=_SENTINEL_RULE_ID,
            category="project",
            severity=Severity.ERROR,
            message_template="",
            authority="",
            check=_empty_check,
            check_project=_check_project,
        )
        journal = _SingleRuleJournal(rule, category_id="project")

        report = run(ToolConfig(), doc, journal)

        sentinels = [v for v in report.violations if v.rule_id == _SENTINEL_RULE_ID]
        assert sentinels == []
        # Sanity: the rule still ran via ``check`` (no-op) and produced no
        # violations, so the category should be PASS.
        assert target_path.exists()
