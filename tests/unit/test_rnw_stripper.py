"""Tests for the `.Rnw` chunk stripper.

Per spec 005 `contracts/rnw-stripper.md`. Invariants S-1..S-6 each
have one or more cases.
"""

from __future__ import annotations

from texlint.core.parser import strip_rnw_chunks, wrap_rnw_chunks_as_sinput

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


# ---------------------------------------------------------------------------
# Hidden-chunk handling in wrap_rnw_chunks_as_sinput
# ---------------------------------------------------------------------------


def test_wrap_emits_sinput_for_visible_chunk():
    src = "<<example>>=\nx <- 1\n@\n"
    out = wrap_rnw_chunks_as_sinput(src)
    assert "\\begin{Sinput}" in out
    assert "x <- 1" in out
    assert out.count("\n") == src.count("\n")


def test_wrap_blanks_echo_false_chunk():
    # echo=FALSE chunks do not appear in the rendered manuscript, so
    # manuscript rules must not see their body.
    src = "<<setup, echo = FALSE>>=\nlibrary(MASS)\n# explanatory note\n@\n"
    out = wrap_rnw_chunks_as_sinput(src)
    assert "\\begin{Sinput}" not in out
    assert "library" not in out
    assert "explanatory" not in out
    assert out.count("\n") == src.count("\n")


def test_wrap_handles_trailing_comment_after_header():
    # Sweave/knitr tolerate an inline comment after ``>>=`` on the header
    # line. The chunk must still be recognised and rewritten, not left in
    # the source where its body leaks into prose-rule scanning.
    src = "<<example>>=  # a trailing note\nx <- 1\n@\n"
    out = wrap_rnw_chunks_as_sinput(src)
    assert "\\begin{Sinput}" in out
    assert "<<example>>=" not in out
    assert out.count("\n") == src.count("\n")


def test_wrap_blanks_hidden_chunk_with_trailing_comment():
    # echo=FALSE header with a trailing inline comment (the cias.Rnw:136
    # regression) — must blank, not leak ``echo=FALSE`` into prose where
    # MARKUP-003 fires on the bare ``FALSE`` sentinel.
    src = "<<lbl,echo=FALSE>>=  # we have the real data\nx <- 1\n@\n"
    out = wrap_rnw_chunks_as_sinput(src)
    assert "\\begin{Sinput}" not in out
    assert "FALSE" not in out
    assert "<<lbl" not in out
    assert out.count("\n") == src.count("\n")


def test_wrap_handles_gt_inside_header_option():
    # A knitr fig.cap (or other option) string may contain a ``>`` —
    # ``fig.cap="... $a_i > 0$"`` — which must not stop the header scan
    # short of the real ``>>=``. Regression: hetGP_vignette.Rnw:683.
    src = (
        '<<motofig, echo=FALSE, fig.cap="error bars when $a_i > 0$">>=\n'
        "plot(x)\n"
        "@\n"
    )
    out = wrap_rnw_chunks_as_sinput(src)
    # echo=FALSE -> hidden chunk, fully blanked; nothing leaks to prose.
    assert "\\begin{Sinput}" not in out
    assert "FALSE" not in out
    assert "fig.cap" not in out
    assert out.count("\n") == src.count("\n")


def test_wrap_handles_indented_chunk():
    # knitr chunks may be indented; the header must still be recognised.
    src = "Intro text.\n  <<lbl>>=\n  x <- 1\n  @\nMore prose.\n"
    out = wrap_rnw_chunks_as_sinput(src)
    assert "\\begin{Sinput}" in out
    assert "x <- 1" in out
    assert out.count("\n") == src.count("\n")


def test_wrap_ignores_midline_chunk_mention_in_prose():
    # A ``<<...>>=`` appearing mid-line (e.g. a LaTeX comment describing
    # chunk options) is prose, NOT a chunk header. Treating it as one
    # makes ``.*?^@`` swallow the intervening prose up to the next ``@``.
    # Regression: entropy_np.Rnw:75 over-masking 120 lines of prose.
    src = (
        "%% making use of <<..., width = ...>>= for better ratios\n"
        "\\section{Real Heading}\n"
        "Prose citing \\citet{key} here.\n"
        "<<realchunk>>=\n"
        "x <- 1\n"
        "@\n"
    )
    out = wrap_rnw_chunks_as_sinput(src)
    # The prose section/citation survive; only the real chunk is wrapped.
    assert "\\section{Real Heading}" in out
    assert "\\citet{key}" in out
    assert out.count("\\begin{Sinput}") == 1
    assert out.count("\n") == src.count("\n")


def test_wrap_blanks_echo_F_short_form():
    # R / knitr accept the bare ``F`` shorthand for FALSE.
    src = "<<setup, echo=F>>=\nlibrary(MASS)\n@\n"
    out = wrap_rnw_chunks_as_sinput(src)
    assert "\\begin{Sinput}" not in out
    assert "library" not in out


def test_wrap_blanks_include_false_chunk():
    # knitr's include=FALSE suppresses both code and output.
    src = "<<setup, include = FALSE>>=\nlibrary(MASS)\n@\n"
    out = wrap_rnw_chunks_as_sinput(src)
    assert "\\begin{Sinput}" not in out
    assert "library" not in out


def test_wrap_keeps_eval_false_visible():
    # eval=FALSE only suppresses execution; the code IS still echoed
    # in the rendered manuscript, so it must remain lintable.
    src = "<<demo, eval = FALSE>>=\nlibrary(MASS)\n@\n"
    out = wrap_rnw_chunks_as_sinput(src)
    assert "\\begin{Sinput}" in out
    assert "library(MASS)" in out
