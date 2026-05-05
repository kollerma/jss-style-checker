"""JSS-PROJECT-* tool-side rules emitted by the spec-013 resolver.

These two rules surface multi-file project diagnostics:

* ``JSS-PROJECT-001`` — a cycle in the ``\\input`` / ``\\include``
  / ``\\subfile`` / ``\\bibliography`` graph.
* ``JSS-PROJECT-002`` — a referenced file that did not resolve to
  an existing path on disk.

They are tool-side: they are NOT registered in the catalogue YAML
because they describe linter-internal diagnostics, not author-
facing JSS-guide rules. The journal plugin imports them on demand
once the engine receives a :class:`texlint.api.ParsedProject`.

Limitation tracked under spec 013 follow-ups: the public
:class:`texlint.api.ParsedProject` dataclass currently only carries
``root``, ``documents``, and ``tree``. The resolver's richer
``ResolvedProject`` (with explicit ``cycles`` and ``missing``
fields) is not threaded through yet. Until the resolver-to-project
bridge lands, JSS-PROJECT-001 detects cycles by DFS over
``project.tree`` and JSS-PROJECT-002 is a no-op stub. Both are
wired through the engine's ``check_project`` dispatch so the
follow-up that fills in ``missing`` will be a single-line change
inside :func:`check_project_missing_refs`.
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

    Currently a no-op stub: :class:`ParsedProject` does not carry
    the ``missing`` references tuple yet (it lives on
    :class:`texlint.core.resolver.ResolvedProject` but is not
    threaded through). The body fills in once the resolver →
    ParsedProject bridge lands as a separate follow-up.
    """
    # Touch the parameter so static analysers don't flag it as unused
    # while the bridge is pending.
    _ = project
    return ()


jss_project_001 = Rule(
    id="JSS-PROJECT-001",
    category="parse",
    severity=Severity.ERROR,
    message_template="cycle detected in input file graph",
    authority="jss_cls",
    check=lambda _doc, _cfg: iter(()),
    check_project=check_project_cycles,
)


jss_project_002 = Rule(
    id="JSS-PROJECT-002",
    category="parse",
    severity=Severity.ERROR,
    message_template="referenced file not found",
    authority="jss_cls",
    check=lambda _doc, _cfg: iter(()),
    check_project=check_project_missing_refs,
)


rules: tuple[Rule, ...] = (jss_project_001, jss_project_002)
