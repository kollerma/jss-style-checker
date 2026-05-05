"""Tests for the JSS-PROJECT-* tool-side rules.

Covered:
  * JSS-PROJECT-001 cycle detection on a 2-node cycle.
  * No violation on a strictly acyclic project.
  * JSS-PROJECT-001 fires on a self-referencing root.
  * Each distinct cycle reported at most once.
  * Rule.check stays a no-op (per-document fires nothing).
  * JSS-PROJECT-002 is a documented no-op stub today.
"""

from __future__ import annotations

from pathlib import Path

from texlint.api import (
    ParsedDocument,
    ParsedProject,
    ParsedTexFile,
    Severity,
    ToolConfig,
)
from texlint.journals.jss.rules.project import (
    check_project_cycles,
    check_project_missing_refs,
    jss_project_001,
    jss_project_002,
    rules,
)


def _doc(path: Path) -> ParsedDocument:
    tex = ParsedTexFile(path=path, source="", nodes=(), walker=None)
    return ParsedDocument(tex_files=(tex,))


def _project(
    root: Path, tree: dict[Path, tuple[Path, ...]]
) -> ParsedProject:
    documents = tuple(_doc(p) for p in tree)
    return ParsedProject(root=root, documents=documents, tree=tree)


def test_rules_tuple_exposes_both_project_rules() -> None:
    assert {r.id for r in rules} == {"JSS-PROJECT-001", "JSS-PROJECT-002"}


def test_jss_project_001_metadata() -> None:
    assert jss_project_001.severity == Severity.ERROR
    assert jss_project_001.category == "parse"
    assert jss_project_001.check_project is not None
    # Per-document check stays a no-op.
    cfg = ToolConfig()
    doc = _doc(Path("/tmp/x.tex"))
    assert list(jss_project_001.check(doc, cfg)) == []


def test_jss_project_002_metadata() -> None:
    assert jss_project_002.severity == Severity.ERROR
    assert jss_project_002.category == "parse"
    assert jss_project_002.check_project is not None
    cfg = ToolConfig()
    doc = _doc(Path("/tmp/x.tex"))
    assert list(jss_project_002.check(doc, cfg)) == []


def test_cycle_two_node_emits_single_violation(tmp_path: Path) -> None:
    a = tmp_path / "a.tex"
    b = tmp_path / "b.tex"
    project = _project(
        a,
        {
            a: (b,),
            b: (a,),
        },
    )

    violations = list(check_project_cycles(project))

    assert len(violations) == 1
    v = violations[0]
    assert v.rule_id == "JSS-PROJECT-001"
    assert v.severity == Severity.ERROR
    assert v.file in {a, b}
    assert v.line == 1
    assert v.column is None
    assert "cycle detected" in v.message


def test_acyclic_project_emits_nothing(tmp_path: Path) -> None:
    a = tmp_path / "a.tex"
    b = tmp_path / "b.tex"
    c = tmp_path / "c.tex"
    project = _project(
        a,
        {
            a: (b, c),
            b: (),
            c: (),
        },
    )

    assert list(check_project_cycles(project)) == []


def test_self_reference_emits_violation(tmp_path: Path) -> None:
    a = tmp_path / "a.tex"
    project = _project(a, {a: (a,)})

    violations = list(check_project_cycles(project))

    assert len(violations) == 1
    assert violations[0].rule_id == "JSS-PROJECT-001"
    assert violations[0].file == a


def test_each_cycle_reported_once(tmp_path: Path) -> None:
    # A 3-cycle: a -> b -> c -> a. DFS from a should report it
    # exactly once even though it traverses three distinct nodes.
    a = tmp_path / "a.tex"
    b = tmp_path / "b.tex"
    c = tmp_path / "c.tex"
    project = _project(
        a,
        {
            a: (b,),
            b: (c,),
            c: (a,),
        },
    )

    violations = list(check_project_cycles(project))

    assert len(violations) == 1
    assert violations[0].rule_id == "JSS-PROJECT-001"
    msg = violations[0].message
    # The chain rendered by the rule contains every node on the
    # cycle plus the closing edge back to the entry node.
    for node in (a, b, c):
        assert str(node) in msg


def test_disjoint_cycles_each_reported(tmp_path: Path) -> None:
    # Root references two subgraphs, each with its own self-cycle.
    # Both must be flagged because their node-sets differ.
    root = tmp_path / "root.tex"
    a = tmp_path / "a.tex"
    b = tmp_path / "b.tex"
    project = _project(
        root,
        {
            root: (a, b),
            a: (a,),
            b: (b,),
        },
    )

    violations = list(check_project_cycles(project))

    assert len(violations) == 2
    files = {v.file for v in violations}
    assert files == {a, b}


def test_missing_refs_stub_is_empty(tmp_path: Path) -> None:
    a = tmp_path / "a.tex"
    project = _project(a, {a: ()})

    assert list(check_project_missing_refs(project)) == []
