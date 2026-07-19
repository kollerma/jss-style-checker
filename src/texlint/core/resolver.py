"""Spec 013 — multi-file project resolver.

Walks ``\\input{...}``, ``\\include{...}``, ``\\subfile{...}``, and
``\\bibliography{...}`` macros from a single root file and returns
the transitive set of files reachable from it. Cycle detection +
missing-reference reporting per the spec.

The full ``ParsedProject`` integration with the engine is deferred
to a follow-up; this module is the core walking algorithm and is
importable / testable on its own.
"""

from __future__ import annotations

import os
import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

# Conservative regex over source text — pylatexenc would be the
# AST-first choice but for the spec-013 v1 we keep the dependency
# surface flat. Covers the four macro names with a single brace arg.
_MACRO_RE = re.compile(
    r"\\(input|include|subfile|bibliography)\{([^}]+)\}"
)


@dataclass(frozen=True)
class ResolvedReference:
    """A single ``\\input{...}`` reference resolved (or not) to a file."""

    parent: Path
    macro: str
    name: str
    target: Path
    found: bool


@dataclass(frozen=True)
class ResolvedProject:
    root: Path
    files: tuple[Path, ...]                          # in resolution order
    references: tuple[ResolvedReference, ...]        # one per macro hit
    missing: tuple[ResolvedReference, ...]           # subset of references
    cycles: tuple[tuple[Path, Path], ...]            # (parent, repeated)


def _texinputs() -> tuple[str, ...]:
    return tuple(p for p in os.environ.get("TEXINPUTS", "").split(":") if p)


def _bibinputs() -> tuple[str, ...]:
    return tuple(p for p in os.environ.get("BIBINPUTS", "").split(":") if p)


def _try_paths(name: str, search: Iterable[Path]) -> Path | None:
    for base in search:
        candidate = base / name
        if candidate.is_file():
            return candidate
        if not name.endswith((".tex", ".ltx", ".Rnw", ".Rmd", ".bib")):
            for ext in (".tex", ".ltx"):
                if (base / (name + ext)).is_file():
                    return base / (name + ext)
    return None


def _resolve_one(
    macro: str, name: str, parent_dir: Path
) -> Path | None:
    if macro == "bibliography":
        candidate = parent_dir / (
            name if name.endswith(".bib") else name + ".bib"
        )
        if candidate.is_file():
            return candidate
        for raw in (*_bibinputs(), *_texinputs()):
            base = Path(raw)
            cand = base / (name if name.endswith(".bib") else name + ".bib")
            if cand.is_file():
                return cand
        return None

    direct = parent_dir / name
    if direct.is_file():
        return direct
    if not name.endswith((".tex", ".ltx", ".Rnw", ".Rmd")):
        with_ext = parent_dir / (name + ".tex")
        if with_ext.is_file():
            return with_ext

    extras = [Path(p) for p in _texinputs()]
    return _try_paths(name, extras)


def resolve(root: Path) -> ResolvedProject:
    """Recursively resolve references reachable from *root*. Cycle-safe."""
    root = root.resolve()
    files: list[Path] = []
    references: list[ResolvedReference] = []
    missing: list[ResolvedReference] = []
    cycles: list[tuple[Path, Path]] = []

    visited: set[Path] = set()
    stack: list[Path] = []

    def visit(path: Path) -> None:
        path = path.resolve()
        if path in stack:
            cycles.append((stack[-1], path))
            return
        if path in visited:
            return
        visited.add(path)
        stack.append(path)
        files.append(path)
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            stack.pop()
            return
        for match in _MACRO_RE.finditer(text):
            macro = match.group(1)
            # `\bibliography{a,b,c}` is standard BibTeX: a comma-
            # separated list of .bib names, each resolved (or missing)
            # independently — not one literal "a,b,c.bib" target.
            # Empty entries from a stray/trailing comma are dropped
            # rather than reported as a missing reference.
            if macro == "bibliography":
                names = [
                    n.strip() for n in match.group(2).split(",") if n.strip()
                ]
            else:
                names = [match.group(2).strip()]
            for name in names:
                target = _resolve_one(macro, name, path.parent)
                ref = ResolvedReference(
                    parent=path,
                    macro=macro,
                    name=name,
                    target=target if target else path.parent / name,
                    found=target is not None,
                )
                references.append(ref)
                if not ref.found:
                    missing.append(ref)
                    continue
                assert target is not None
                visit(target)
        stack.pop()

    visit(root)

    return ResolvedProject(
        root=root,
        files=tuple(files),
        references=tuple(references),
        missing=tuple(missing),
        cycles=tuple(cycles),
    )
