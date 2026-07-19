"""JSS-PROJECT-* tool-side rules emitted by the spec-013 resolver.

These two rules surface multi-file project diagnostics:

* ``JSS-PROJECT-001`` — a cycle in the ``\\input`` / ``\\include``
  / ``\\subfile`` / ``\\bibliography`` graph.
* ``JSS-PROJECT-002`` — a referenced file that did not resolve to
  an existing path on disk.

They are tool-side: they describe linter-internal diagnostics about
the resolved file graph, not author-facing JSS-guide requirements —
``guide_section`` carries the ``"internal"`` sentinel (spec 007) and
``category: project`` sits in ``TOOL_SIDE_CATEGORIES`` (spec 007's
citation contract), so neither rule needs a JSS-guide citation. They
are registered in the catalogue YAML like any other rule (category
``project``) and only fire via ``check_project`` — ``Rule.check`` is
a permanent no-op since these are graph-level, not per-document,
diagnostics.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from texlint.api import (
    ParsedProject,
    Rule,
    Severity,
    Violation,
)


def check_project_cycles(project: ParsedProject) -> Iterable[Violation]:
    """Emit one ``JSS-PROJECT-001`` violation per distinct cycle in
    ``project.tree``.

    Detection runs a depth-first search starting from
    :attr:`ParsedProject.root` and reports a cycle whenever a node
    is encountered that is already on the active DFS stack. Each
    cycle is reported at most once: the cycle's node-set (as a
    sorted tuple) is the dedup key, so ``A -> B -> A`` and the
    rotation ``B -> A -> B`` collapse into one violation.

    The violation is anchored at the node that closed the cycle and
    points at line 1 because the cycle is a graph-level property
    that does not have a source position.
    """
    seen_cycles: set[tuple[Path, ...]] = set()
    visited: set[Path] = set()
    stack: list[Path] = []
    violations: list[Violation] = []

    def dfs(node: Path) -> None:
        if node in stack:
            cycle_nodes = stack[stack.index(node):] + [node]
            cycle_key = tuple(sorted(set(cycle_nodes)))
            if cycle_key in seen_cycles:
                return
            seen_cycles.add(cycle_key)
            chain = " -> ".join(str(p) for p in cycle_nodes)
            violations.append(
                Violation(
                    file=node,
                    line=1,
                    column=None,
                    rule_id="JSS-PROJECT-001",
                    severity=Severity.ERROR,
                    message=f"cycle detected: {chain}",
                )
            )
            return
        if node in visited:
            return
        visited.add(node)
        stack.append(node)
        for child in project.tree.get(node, ()):
            dfs(child)
        stack.pop()

    dfs(project.root)
    yield from violations


def check_project_missing_refs(project: ParsedProject) -> Iterable[Violation]:
    """Emit ``JSS-PROJECT-002`` violations for unresolved references.

    One violation per :class:`~texlint.core.resolver.ResolvedReference`
    in :attr:`ParsedProject.missing`, anchored on the file that
    *contained* the reference (the parent), per data-model.md §6.
    """
    for ref in project.missing:
        yield Violation(
            file=ref.parent,
            line=1,
            column=None,
            rule_id="JSS-PROJECT-002",
            severity=Severity.ERROR,
            message=f"referenced file not found: {ref.name}",
        )


jss_project_001 = Rule(
    id="JSS-PROJECT-001",
    category="project",
    severity=Severity.ERROR,
    message_template=(
        "A cycle exists in the \\input/\\include/\\subfile/\\bibliography "
        "reference graph"
    ),
    authority="author_instructions",
    check=lambda _doc, _cfg: iter(()),
    check_project=check_project_cycles,
)


jss_project_002 = Rule(
    id="JSS-PROJECT-002",
    category="project",
    severity=Severity.ERROR,
    message_template="A \\input/\\include/\\subfile/\\bibliography target could not be found",
    authority="author_instructions",
    check=lambda _doc, _cfg: iter(()),
    check_project=check_project_missing_refs,
)


rules: tuple[Rule, ...] = (jss_project_001, jss_project_002)
