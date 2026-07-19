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
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path

# Finds the opening `\macroname{` for each of the four macros; the
# matching closing brace is then found by manual depth-counting in
# `_find_macro_hits` below (a single-level `[^}]+` capture can't
# handle a nested-brace argument like Sweave's
# `\bibliography{\Sexpr{Rcpp:::bib()}}` — it would stop at the first
# `}`, landing mid-expression instead of on the real argument).
_MACRO_START_RE = re.compile(r"\\(input|include|subfile|bibliography)\{")


def _find_macro_hits(text: str) -> Iterator[tuple[str, str]]:
    """Yield ``(macro, argument)`` for every balanced-brace macro hit
    in *text*, in source order.

    *text* is expected to already have TeX comments stripped (see
    ``_strip_comments``) — this function has no notion of ``%``.
    """
    for match in _MACRO_START_RE.finditer(text):
        macro = match.group(1)
        start = match.end()
        depth = 1
        i = start
        n = len(text)
        while i < n and depth > 0:
            ch = text[i]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
            i += 1
        if depth != 0:
            continue  # unbalanced to EOF — malformed macro, skip it
        yield macro, text[start : i - 1]


def _strip_comments(text: str) -> str:
    """Blank out TeX comments (an unescaped ``%`` through end of line).

    Line-based, not verbatim-environment-aware — matches the rest of
    this module's "regex over source text, not a full AST" scope
    (module docstring). Sufficient to stop a commented-out
    ``%\\bibliography{...}``/``\\input{...}`` from being treated as a
    live reference, which is the observed real-world false-positive
    pattern (recall-corpus papers that comment out an alternate
    bibliography backend, e.g. ``%\\bibliography{bibliojss}``).

    A backslash always escapes the character after it (so ``\\%`` is a
    literal percent, not a comment start, and ``\\\\%`` — an escaped
    backslash followed by a real comment — still comments out the
    rest of the line), matching standard TeX catcode behaviour.
    """
    out_lines = []
    for line in text.split("\n"):
        chars = []
        i = 0
        n = len(line)
        while i < n:
            ch = line[i]
            if ch == "\\" and i + 1 < n:
                chars.append(line[i : i + 2])
                i += 2
                continue
            if ch == "%":
                break
            chars.append(ch)
            i += 1
        out_lines.append("".join(chars))
    return "\n".join(out_lines)


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


def _local_search_dirs(parent_dir: Path, root_dir: Path) -> tuple[Path, ...]:
    """Directories to try before TEXINPUTS/BIBINPUTS, in LaTeX's own
    priority order: the *root* document's directory first, then the
    *referencing* file's own directory.

    Real ``\\input``/``\\include`` (without the ``import``/``subfiles``
    packages) resolves a relative path against the working directory
    the TeX engine was invoked in — conventionally the main/root
    document's directory — for the whole run, not against whichever
    file issued the nested ``\\input``. A file two levels deep that
    does ``\\input{fig/x}`` intending a ``fig/`` directory that sits
    beside the *root* (not beside itself) resolves correctly under
    real LaTeX; resolving only against the immediate parent's
    directory (this module's original behaviour) reported that as a
    false-positive missing reference. Falling back to the parent's own
    directory second still covers the common single-level case (where
    they're the same directory anyway) and files that keep siblings
    together within a subdirectory.
    """
    if root_dir == parent_dir:
        return (root_dir,)
    return (root_dir, parent_dir)


def _resolve_one(
    macro: str, name: str, parent_dir: Path, root_dir: Path
) -> Path | None:
    local_dirs = _local_search_dirs(parent_dir, root_dir)
    if macro == "bibliography":
        bib_name = name if name.endswith(".bib") else name + ".bib"
        for base in local_dirs:
            candidate = base / bib_name
            if candidate.is_file():
                return candidate
        for raw in (*_bibinputs(), *_texinputs()):
            base = Path(raw)
            cand = base / bib_name
            if cand.is_file():
                return cand
        return None

    found = _try_paths(name, local_dirs)
    if found is not None:
        return found

    extras = [Path(p) for p in _texinputs()]
    return _try_paths(name, extras)


def resolve(root: Path) -> ResolvedProject:
    """Recursively resolve references reachable from *root*. Cycle-safe."""
    root = root.resolve()
    root_dir = root.parent
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
        text = _strip_comments(text)
        for macro, raw_arg in _find_macro_hits(text):
            # `\bibliography{a,b,c}` is standard BibTeX: a comma-
            # separated list of .bib names, each resolved (or missing)
            # independently — not one literal "a,b,c.bib" target.
            # Empty entries from a stray/trailing comma are dropped
            # rather than reported as a missing reference.
            if macro == "bibliography":
                names = [n.strip() for n in raw_arg.split(",") if n.strip()]
            else:
                names = [raw_arg.strip()]
            for name in names:
                if "\\" in name:
                    # A computed/dynamic argument (e.g. Sweave's
                    # \Sexpr{...}), not a literal filename — nothing to
                    # textually resolve, and reporting it as "missing"
                    # would be a false positive.
                    continue
                target = _resolve_one(macro, name, path.parent, root_dir)
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
