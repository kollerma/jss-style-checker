"""Tests for the `.Rnw` chunk stripper.

Per spec 005 `contracts/rnw-stripper.md`. Invariants S-1..S-6 each
have one or more cases.
"""

from __future__ import annotations

from texlint.core.parser import strip_rnw_chunks

# ---------------------------------------------------------------------------
# S-1 line-count invariant
# ---------------------------------------------------------------------------


class TestLineCountInvariant:
    def test_empty_string(self):
        src = ""
        assert strip_rnw_chunks(src).count("\n") == src.count("\n")

    def test_no_chunks(self):
        src = "line 1\nline 2\nline 3\n"
        assert strip_rnw_chunks(src) == src
        assert strip_rnw_chunks(src).count("\n") == src.count("\n")

    def test_single_chunk(self):
        src = "prose above.\n<<setup>>=\nx <- 1\n@\nprose below.\n"
        out = strip_rnw_chunks(src)
        assert out.count("\n") == src.count("\n")

    def test_multiple_chunks(self):
        src = (
            "prose 1\n"
            "<<a>>=\nx <- 1\n@\n"
            "prose 2\n"
            "<<b>>=\ny <- 2\nz <- 3\n@\n"
            "prose 3\n"
        )
        out = strip_rnw_chunks(src)
        assert out.count("\n") == src.count("\n")

    def test_chunk_with_options(self):
        src = "<<fig1, fig.width=5, cache=TRUE>>=\nplot(x)\n@\n"
        out = strip_rnw_chunks(src)
        assert out.count("\n") == src.count("\n")

    def test_chunk_with_no_label(self):
        src = "<<>>=\nx <- 1\n@\n"
        out = strip_rnw_chunks(src)
        assert out.count("\n") == src.count("\n")


# ---------------------------------------------------------------------------
# S-2 outside-chunks preservation
# ---------------------------------------------------------------------------


def test_outside_chunks_byte_identical():
    prose_before = "this is some \\emph{prose} content.\n"
    prose_after = "\\section{Conclusion}\nMore prose.\n"
    src = prose_before + "<<a>>=\nx <- 1\n@\n" + prose_after
    out = strip_rnw_chunks(src)
    assert out.startswith(prose_before)
    assert out.endswith(prose_after)


# ---------------------------------------------------------------------------
# S-3 chunk body blanked
# ---------------------------------------------------------------------------


def test_chunk_body_becomes_newlines_only():
    src = "<<a>>=\nR> do_stuff()\nR> more()\n@\n"
    out = strip_rnw_chunks(src)
    # All non-newline characters replaced.
    assert "do_stuff" not in out
    assert "more" not in out


# ---------------------------------------------------------------------------
# S-4 \Sexpr{} stripped inline
# ---------------------------------------------------------------------------


def test_inline_sexpr_replaced_with_spaces():
    src = "The answer is \\Sexpr{42}.\n"
    out = strip_rnw_chunks(src)
    assert "\\Sexpr" not in out
    # Length preserved.
    assert len(out) == len(src)


def test_crlf_chunk_is_blanked():
    # Real CRAN vignettes (e.g., zoo-quickref.Rnw) ship with \r\n line
    # endings. The chunk-header \n had to be made CRLF-tolerant; without
    # `\r?\n` the regex misses entirely and the whole chunk leaks into
    # the stripped output, exposing R code identifiers to markup rules.
    src = "prose\r\n<<setup>>=\r\nlibrary(\"zoo\")\r\nx <- 1\r\n@\r\nmore\r\n"
    out = strip_rnw_chunks(src)
    assert "library" not in out
    assert "<<setup>>=" not in out
    # Newline count preserved (CRLF counts as one '\n' for splitlines).
    assert out.count("\n") == src.count("\n")


def test_multiline_sexpr_preserves_newlines():
    # `\Sexpr{round(coef(model),\n2)}` (line-broken arg) appears in real
    # JSS vignettes (e.g., cran_tram). The stripper must keep the
    # interior `\n` so downstream rules report source-authoritative
    # line numbers — replacing it with a space dropped the newline and
    # caused off-by-N positions for every rule firing after the Sexpr.
    src = "Mean is \\Sexpr{round(coef(m),\n2)} approximately.\n"
    out = strip_rnw_chunks(src)
    assert "\\Sexpr" not in out
    assert len(out) == len(src)
    assert out.count("\n") == src.count("\n")


# ---------------------------------------------------------------------------
# S-5 unclosed chunk pass-through
# ---------------------------------------------------------------------------


def test_unclosed_chunk_left_unchanged():
    src = "prose\n<<a>>=\nx <- 1\nno closing at sign\n"
    out = strip_rnw_chunks(src)
    # Unclosed → unchanged; pylatexenc will emit the parse error later.
    assert out == src


# ---------------------------------------------------------------------------
# S-6 bare @ not misinterpreted as chunk close
# ---------------------------------------------------------------------------


def test_bare_at_sign_outside_chunk_preserved():
    src = "some text\n@ is a decoration on its own line\n"
    out = strip_rnw_chunks(src)
    assert out == src


def test_sexpr_with_nested_braces_not_stripped():
    # Documented limitation: nested braces in \Sexpr{} aren't supported
    # by the regex. Test captures the behaviour as the spec pinned.
    src = "\\Sexpr{foo{bar}}"
    out = strip_rnw_chunks(src)
    assert out == src
