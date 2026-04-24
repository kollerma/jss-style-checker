"""Tests for ``_helpers.py`` — 100% branch coverage target.

Constitution §IX: the rules package must have 100% branch coverage.
This test module exercises every branch of every helper.
"""

from __future__ import annotations

from pylatexenc.latexwalker import (
    LatexCharsNode,
    LatexCommentNode,
    LatexEnvironmentNode,
    LatexGroupNode,
    LatexMacroNode,
    LatexMathNode,
    LatexWalker,
)

from texlint.journals.jss.rules import _helpers


def _parse(src: str):
    walker = LatexWalker(src, tolerant_parsing=False)
    nodes, _pos, _length = walker.get_latex_nodes()
    return walker, tuple(nodes)


class TestWalk:
    def test_none_input_yields_nothing(self):
        assert list(_helpers._walk(None)) == []

    def test_empty_input_yields_nothing(self):
        assert list(_helpers._walk([])) == []

    def test_skips_none_nodes(self):
        _, nodes = _parse("hello")
        # Inject a None to cover the `if node is None: continue` branch.
        mixed = (None,) + nodes
        out = list(_helpers._walk(mixed))
        assert len(out) == len(nodes)

    def test_recurses_into_environment(self):
        _, nodes = _parse(r"\begin{itemize}\item a\end{itemize}")
        walked = list(_helpers._walk(nodes))
        assert any(isinstance(n, LatexEnvironmentNode) for n in walked)
        assert any(isinstance(n, LatexMacroNode) and n.macroname == "item" for n in walked)

    def test_recurses_into_group(self):
        _, nodes = _parse(r"{hello}")
        walked = list(_helpers._walk(nodes))
        assert any(isinstance(n, LatexGroupNode) for n in walked)
        assert any(isinstance(n, LatexCharsNode) for n in walked)

    def test_recurses_into_math(self):
        _, nodes = _parse(r"$x+1$")
        walked = list(_helpers._walk(nodes))
        assert any(isinstance(n, LatexMathNode) for n in walked)

    def test_recurses_into_macro_args(self):
        _, nodes = _parse(r"\emph{bold}")
        walked = list(_helpers._walk(nodes))
        kinds = [type(n).__name__ for n in walked]
        assert "LatexMacroNode" in kinds
        assert "LatexGroupNode" in kinds

    def test_macro_without_nodeargd_is_safe(self):
        class FakeMacro(LatexMacroNode):
            def __init__(self):  # type: ignore[no-untyped-def]
                pass

        fake = FakeMacro()
        assert list(_helpers._walk([fake])) == [fake]


class TestIterWithParent:
    def test_none_input_yields_nothing(self):
        assert list(_helpers._iter_with_parent(None)) == []

    def test_yields_parent_index_node(self):
        _, nodes = _parse("hello world")
        triples = list(_helpers._iter_with_parent(nodes))
        assert triples, "expected at least one triple"
        parent, idx, node = triples[0]
        assert parent is nodes or parent == nodes  # top-level is the input
        assert idx == 0
        assert node is nodes[0]

    def test_skips_none_nodes(self):
        _, nodes = _parse("x")
        out = list(_helpers._iter_with_parent((None, *nodes)))
        assert all(triple[2] is not None for triple in out)

    def test_recurses(self):
        _, nodes = _parse(r"\begin{itemize}\item a\end{itemize}")
        triples = list(_helpers._iter_with_parent(nodes))
        # At least one triple should be a nested \item inside the itemize body.
        assert any(
            isinstance(node, LatexMacroNode) and node.macroname == "item"
            for _p, _i, node in triples
        )

    def test_macro_without_nodeargd_is_safe(self):
        class FakeMacro(LatexMacroNode):
            def __init__(self):  # type: ignore[no-untyped-def]
                pass

        fake = FakeMacro()
        triples = list(_helpers._iter_with_parent([fake]))
        assert len(triples) == 1
        assert triples[0][2] is fake


class TestNextGroupArg:
    def test_returns_none_at_end(self):
        _, nodes = _parse(r"\foo")
        assert _helpers._next_group_arg(nodes, len(nodes) - 1) is None

    def test_returns_none_when_sibling_not_group(self):
        _, nodes = _parse(r"\pkg x")
        # nodes: [LatexMacroNode(\pkg), LatexCharsNode(' x')]
        # sibling of \pkg is a chars node, not a group → return None via line 97.
        assert _helpers._next_group_arg(nodes, 0) is None

    def test_returns_group_when_sibling_is_group(self):
        _, nodes = _parse(r"\pkg{mgcv}")
        # With pylatexenc's defaults \pkg may be unknown; that's exactly the
        # case we care about — sibling index 1 should be a LatexGroupNode.
        pos = next(
            i for i, n in enumerate(nodes)
            if isinstance(n, LatexMacroNode) and n.macroname == "pkg"
        )
        sibling = _helpers._next_group_arg(nodes, pos)
        assert isinstance(sibling, LatexGroupNode)


class TestMacroArgsText:
    def test_known_macro_with_group_arg(self):
        _, nodes = _parse(r"\emph{hello}")
        emph = next(n for n in nodes if isinstance(n, LatexMacroNode))
        assert _helpers._macro_args_text(emph, nodes, 0) == "hello"

    def test_unknown_macro_uses_sibling(self):
        _, nodes = _parse(r"\pkg{mgcv}")
        pos = next(
            i for i, n in enumerate(nodes)
            if isinstance(n, LatexMacroNode) and n.macroname == "pkg"
        )
        assert _helpers._macro_args_text(nodes[pos], nodes, pos) == "mgcv"

    def test_no_arg_returns_empty(self):
        _, nodes = _parse(r"\pkg")
        pos = next(
            i for i, n in enumerate(nodes)
            if isinstance(n, LatexMacroNode) and n.macroname == "pkg"
        )
        # Last token — no sibling group.
        assert _helpers._macro_args_text(nodes[pos], nodes, pos) == ""

    def test_group_text_skips_non_chars(self):
        # \emph{\textit{x}} — inner child of the group is a macro, not chars,
        # so _group_text should return "".
        _, nodes = _parse(r"\emph{\textit{x}}")
        emph = next(n for n in nodes if isinstance(n, LatexMacroNode))
        assert _helpers._macro_args_text(emph, nodes, 0) == ""

    def test_known_macro_without_group_arg_falls_back(self):
        # `\emph X` — pylatexenc binds X as a LatexCharsNode, not a group.
        # The argnlist loop finds no LatexGroupNode, so we fall through to
        # the sibling search (which also has no group → returns "").
        _, nodes = _parse(r"\emph X")
        emph = next(n for n in nodes if isinstance(n, LatexMacroNode))
        idx = nodes.index(emph)
        assert _helpers._macro_args_text(emph, nodes, idx) == ""

    def test_macro_without_nodeargd_falls_through(self):
        class FakeMacro(LatexMacroNode):
            def __init__(self):  # type: ignore[no-untyped-def]
                pass

        fake = FakeMacro()
        # No nodeargd, no siblings — should return "".
        assert _helpers._macro_args_text(fake, [fake], 0) == ""


class TestLinenoCol:
    def test_converts_pos_to_1_based_line_col(self):
        walker, nodes = _parse("abc")
        # Fake a ParsedTexFile-like object that exposes .walker

        class T:
            pass

        t = T()
        t.walker = walker
        line, col = _helpers._lineno_col(t, 0)
        assert line == 1
        assert col == 1


class TestIsInsideVerbatim:
    def test_false_on_empty(self):
        assert _helpers._is_inside_verbatim([]) is False

    def test_true_for_verbatim_env(self):
        _, nodes = _parse(r"\begin{verbatim}x\end{verbatim}")
        env = next(n for n in nodes if isinstance(n, LatexEnvironmentNode))
        assert _helpers._is_inside_verbatim([env]) is True

    def test_true_for_code_env(self):
        _, nodes = _parse(r"\begin{Code}x\end{Code}")
        env = next(n for n in nodes if isinstance(n, LatexEnvironmentNode))
        assert _helpers._is_inside_verbatim([env]) is True

    def test_true_for_verb_macro(self):
        _, nodes = _parse(r"\verb|x|")
        mac = next(n for n in nodes if isinstance(n, LatexMacroNode))
        assert _helpers._is_inside_verbatim([mac]) is True

    def test_true_for_code_macro(self):
        _, nodes = _parse(r"\code{x}")
        mac = next(n for n in nodes if isinstance(n, LatexMacroNode))
        assert _helpers._is_inside_verbatim([mac]) is True

    def test_false_for_regular_env(self):
        _, nodes = _parse(r"\begin{itemize}\item a\end{itemize}")
        env = next(n for n in nodes if isinstance(n, LatexEnvironmentNode))
        assert _helpers._is_inside_verbatim([env]) is False

    def test_false_for_regular_macro(self):
        _, nodes = _parse(r"\emph{x}")
        mac = next(n for n in nodes if isinstance(n, LatexMacroNode))
        assert _helpers._is_inside_verbatim([mac]) is False


class TestIsInsideComment:
    def test_true_for_comment_node(self):
        _, nodes = _parse("x% comment\n")
        comment = next(n for n in nodes if isinstance(n, LatexCommentNode))
        assert _helpers._is_inside_comment(comment) is True

    def test_false_for_chars(self):
        _, nodes = _parse("x")
        chars = next(n for n in nodes if isinstance(n, LatexCharsNode))
        assert _helpers._is_inside_comment(chars) is False


class TestIsInsideMath:
    def test_false_on_empty(self):
        assert _helpers._is_inside_math([]) is False

    def test_true_for_inline_math(self):
        _, nodes = _parse(r"$x+1$")
        math = next(n for n in nodes if isinstance(n, LatexMathNode))
        assert _helpers._is_inside_math([math]) is True

    def test_true_for_equation_env(self):
        _, nodes = _parse(r"\begin{equation}x\end{equation}")
        env = next(n for n in nodes if isinstance(n, LatexEnvironmentNode))
        assert _helpers._is_inside_math([env]) is True

    def test_false_for_regular_env(self):
        _, nodes = _parse(r"\begin{itemize}\item a\end{itemize}")
        env = next(n for n in nodes if isinstance(n, LatexEnvironmentNode))
        assert _helpers._is_inside_math([env]) is False


class TestWalkWithAncestors:
    def test_none_input_yields_nothing(self):
        assert list(_helpers._walk_with_ancestors(None)) == []

    def test_yields_outer_ancestors(self):
        _, nodes = _parse(r"\begin{itemize}\item x\end{itemize}")
        triples = list(_helpers._walk_with_ancestors(nodes))
        # Find the chars node 'x' — ancestors include itemize env.
        chars_entries = [
            (node, anc) for node, anc in triples
            if isinstance(node, LatexCharsNode)
        ]
        assert any(
            any(isinstance(a, LatexEnvironmentNode) for a in anc)
            for _n, anc in chars_entries
        )

    def test_skips_none_nodes(self):
        _, nodes = _parse("x")
        out = list(_helpers._walk_with_ancestors((None, *nodes)))
        assert all(n is not None for n, _anc in out)

    def test_macro_without_nodeargd_is_safe(self):
        class FakeMacro(LatexMacroNode):
            def __init__(self):  # type: ignore[no-untyped-def]
                pass

        fake = FakeMacro()
        out = list(_helpers._walk_with_ancestors([fake]))
        assert len(out) == 1
        assert out[0][0] is fake
        assert out[0][1] == []


class TestIsInProseContext:
    def test_empty_ancestors_is_prose(self):
        assert _helpers._is_in_prose_context([]) is True

    def test_inside_verbatim_not_prose(self):
        _, nodes = _parse(r"\begin{verbatim}x\end{verbatim}")
        env = next(n for n in nodes if isinstance(n, LatexEnvironmentNode))
        assert _helpers._is_in_prose_context([env]) is False

    def test_inside_math_not_prose(self):
        _, nodes = _parse(r"$x$")
        math = next(n for n in nodes if isinstance(n, LatexMathNode))
        assert _helpers._is_in_prose_context([math]) is False

    def test_inside_markup_macro_not_prose(self):
        _, nodes = _parse(r"\pkg{x}")
        mac = next(n for n in nodes if isinstance(n, LatexMacroNode))
        assert _helpers._is_in_prose_context([mac]) is False

    def test_inside_section_macro_not_prose(self):
        _, nodes = _parse(r"\section{x}")
        mac = next(n for n in nodes if isinstance(n, LatexMacroNode))
        assert _helpers._is_in_prose_context([mac]) is False

    def test_inside_meta_macro_not_prose(self):
        _, nodes = _parse(r"\title{x}")
        mac = next(n for n in nodes if isinstance(n, LatexMacroNode))
        assert _helpers._is_in_prose_context([mac]) is False

    def test_plain_env_is_prose(self):
        _, nodes = _parse(r"\begin{itemize}\item x\end{itemize}")
        env = next(n for n in nodes if isinstance(n, LatexEnvironmentNode))
        assert _helpers._is_in_prose_context([env]) is True

    def test_plain_macro_is_prose(self):
        # A macro that is not in MARKUP / SECTION / META sets — \emph is prose.
        _, nodes = _parse(r"\emph{x}")
        mac = next(n for n in nodes if isinstance(n, LatexMacroNode))
        assert _helpers._is_in_prose_context([mac]) is True


class TestCharHasBlankLine:
    def test_true_for_blank_line(self):
        _, nodes = _parse("a\n\nb")
        chars = next(n for n in nodes if isinstance(n, LatexCharsNode))
        assert _helpers._char_has_blank_line(chars) is True

    def test_false_for_single_newline(self):
        _, nodes = _parse("a\nb")
        chars = next(n for n in nodes if isinstance(n, LatexCharsNode))
        assert _helpers._char_has_blank_line(chars) is False

    def test_false_for_non_chars(self):
        _, nodes = _parse(r"\emph{x}")
        mac = next(n for n in nodes if isinstance(n, LatexMacroNode))
        assert _helpers._char_has_blank_line(mac) is False
