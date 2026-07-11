"""Python oracle for the spec-018 Rust tokenizer's fixture-diff harness.

Runs the exact same pipeline `texlint.core.parser.parse_tex_source` does
(the three neutralization passes, then `LatexWalker`) and walks the
result with the real `_walk_with_context` / `_is_in_prose_context` from
`texlint.journals.jss.rules._helpers`, dumping one line per node in
pre-order:

    <depth>\\t<pos>\\t<end>\\t<kind>\\t<prose>

`rust/jsslint-core/src/tex/debug.rs::dump` emits the identical format;
`rust/jsslint-core/tests/parser_parity.rs` diffs the two outputs.

NOTE: uses `tolerant_parsing=True` unconditionally (skipping the
strict-then-tolerant-retry `parse_tex_source` normally does) because the
Rust port only implements the tolerant behavior — see
`rust/jsslint-core/src/tex/parser.rs`'s module doc.

Usage: python -m tools.dump_tex_nodes <path/to/file.tex>
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from pylatexenc.latexwalker import (  # noqa: E402
    LatexCommentNode,
    LatexEnvironmentNode,
    LatexGroupNode,
    LatexMacroNode,
    LatexMathNode,
    LatexSpecialsNode,
    LatexWalker,
)

from texlint.core.parser import (  # noqa: E402
    _neutralize_macro_definition_bodies,
    _neutralize_verbatim_args,
    _neutralize_verbatim_envs,
)
from texlint.journals.jss.rules._helpers import (  # noqa: E402
    _is_in_prose_context,
    _walk_with_context,
)


def _kind_label(node: object) -> str:
    if isinstance(node, LatexMacroNode):
        return f"Macro:{node.macroname}"
    if isinstance(node, LatexEnvironmentNode):
        return f"Environment:{node.environmentname}"
    if isinstance(node, LatexGroupNode):
        open_delim = node.delimiters[0] if node.delimiters else "{"
        return f"Group:{open_delim}"
    if isinstance(node, LatexMathNode):
        return f"Math:{node.displaytype}"
    if isinstance(node, LatexSpecialsNode):
        return f"Specials:{node.specials_chars}"
    if isinstance(node, LatexCommentNode):
        return "Comment"
    return "Chars"


def dump(source: str) -> str:
    preprocessed = _neutralize_macro_definition_bodies(source)
    preprocessed = _neutralize_verbatim_envs(preprocessed)
    preprocessed = _neutralize_verbatim_args(preprocessed)

    walker = LatexWalker(preprocessed, tolerant_parsing=True)
    nodes, _pos, _length = walker.get_latex_nodes()

    lines: list[str] = []
    for node, ancestors, _parent, _idx in _walk_with_context(nodes):
        depth = len(ancestors)
        prose = _is_in_prose_context(ancestors)
        kind = _kind_label(node)
        pos = node.pos
        end = node.pos + node.len
        lines.append(f"{depth}\t{pos}\t{end}\t{kind}\t{str(prose).lower()}")
    return "\n".join(lines) + ("\n" if lines else "")


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print("usage: python -m tools.dump_tex_nodes <path/to/file.tex>", file=sys.stderr)
        return 2
    path = Path(argv[0])
    source = path.read_text(encoding="utf-8")
    sys.stdout.write(dump(source))
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
