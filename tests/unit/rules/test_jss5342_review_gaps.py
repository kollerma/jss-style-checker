"""Smoke tests for rule gaps surfaced by reviewing jss5342's review history.

Each test reproduces a specific JSS reviewer comment from the jss5342
submission rounds against a minimal fixture that exhibits the same
defect. The tests assert the linter behaviour we *want* — passing the
test means the rule fires; failing it means the rule has a real recall
gap that the review confirmed.

Provenance for every test is documented inline (P# = pre-screening
item; AE# = associate-editor comment; R#-rN = reviewer comment in
round N).
"""
from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

from texlint.api import ParsedDocument, ToolConfig, Violation
from texlint.core.parser import parse_rnw_file


def _rnw_doc(tmp_path: Path, src: str) -> ParsedDocument:
    p = tmp_path / "frag.Rnw"
    p.write_text(src, encoding="utf-8")
    return ParsedDocument(tex_files=(parse_rnw_file(p),))


def _violations_for(rule_id: str, doc: ParsedDocument) -> list[Violation]:
    """Run the rule whose id matches and return its violations."""
    from texlint.journals.jss import JSSJournal
    cfg = ToolConfig()
    out = []
    for rule in JSSJournal().rules():
        if rule.id == rule_id:
            out.extend(rule.check(doc, cfg))
    return out


# ---------------------------------------------------------------------------
# JSS-CODE-002 — library() / data() arg quoting inside Rnw chunks
# Reviewer evidence: P4, AE2a, R7-r1.
# ---------------------------------------------------------------------------

def test_code_002_fires_inside_rnw_chunk(tmp_path: Path):
    """`library(MASS)` inside `<<>>= ... @` must be flagged."""
    src = (
        "\\documentclass[article]{jss}\n"
        "\\begin{document}\n"
        "<<chunk>>=\n"
        "library(MASS)\n"
        "data(quine)\n"
        "@\n"
        "\\end{document}\n"
    )
    doc = _rnw_doc(tmp_path, src)
    violations = _violations_for("JSS-CODE-002", doc)
    # Two unquoted calls expected.
    assert len(violations) == 2, (
        f"expected library(MASS) and data(quine) to be flagged inside "
        f"the Rnw chunk; got {len(violations)} violations: {violations}"
    )


# ---------------------------------------------------------------------------
# JSS-CODE-003 — operator spacing / comma spacing inside Rnw chunks
# Reviewer evidence: P3 (spaces before/after operators and after commas),
# AE2d (spaces around `=`).
# ---------------------------------------------------------------------------

def test_code_003_fires_inside_rnw_chunk(tmp_path: Path):
    """No-space code inside an Rnw chunk must be flagged."""
    src = (
        "\\documentclass[article]{jss}\n"
        "\\begin{document}\n"
        "<<chunk>>=\n"
        "fit <- lm(y~x,data=mydata)\n"
        "@\n"
        "\\end{document}\n"
    )
    doc = _rnw_doc(tmp_path, src)
    violations = _violations_for("JSS-CODE-003", doc)
    assert violations, (
        "expected JSS-CODE-003 to flag missing spaces around `=` and "
        "after `,` inside the Rnw chunk"
    )


# ---------------------------------------------------------------------------
# JSS-WIDTH-001 — code line width inside Rnw chunks
# Reviewer evidence: P2, P12 ("code input/output must fit text width").
# ---------------------------------------------------------------------------

def test_width_001_fires_inside_rnw_chunk(tmp_path: Path):
    """A 120-char code line in an Rnw chunk must be flagged."""
    long_line = "x <- " + "a + " * 30  # ~125 chars
    src = (
        "\\documentclass[article]{jss}\n"
        "\\begin{document}\n"
        "<<chunk>>=\n"
        f"{long_line}\n"
        "@\n"
        "\\end{document}\n"
    )
    doc = _rnw_doc(tmp_path, src)
    violations = _violations_for("JSS-WIDTH-001", doc)
    assert violations, (
        "expected JSS-WIDTH-001 to flag a >77-char line inside an "
        "Rnw code chunk"
    )


# ---------------------------------------------------------------------------
# JSS-XREF-002 — \eqref{...} produces parenthesised form, same defect
# Reviewer evidence: P10 ("Equation~\ref{...} (capitalised) without
# parentheses ... former being preferred"). \eqref renders as "(N)" so
# it is the same defect class as `(\ref{...})`.
# ---------------------------------------------------------------------------

def test_xref_002_flags_eqref(tmp_path: Path):
    """`\\eqref{...}` (which renders as parens) must be flagged."""
    src = (
        "\\documentclass[article]{jss}\n"
        "\\begin{document}\n"
        "See \\eqref{eq:1} for the model.\n"
        "\\begin{equation}\\label{eq:1} a=b. \\end{equation}\n"
        "\\end{document}\n"
    )
    doc = _rnw_doc(tmp_path, src)
    violations = _violations_for("JSS-XREF-002", doc)
    assert violations, (
        "expected JSS-XREF-002 to flag \\eqref{...}; reviewer P10 "
        "discourages the parenthesised form regardless of which macro "
        "produces it"
    )


# ---------------------------------------------------------------------------
# JSS-CODE-001 — comments inside HIDDEN (echo=FALSE) chunks must NOT
# fire. Hidden-chunk bodies are absent from the rendered manuscript;
# they only feed the auto-purled .R script where comments are
# encouraged. The published jss5342 keeps explanatory comments inside
# echo=FALSE setup chunks (e.g. line 26 "# Setup prompt to follow
# requested style") — flagging them would mean the linter is wrong
# about the surface it's linting.
# ---------------------------------------------------------------------------

def test_code_001_skips_hidden_chunk(tmp_path: Path):
    """`# comment` inside an echo=FALSE chunk must NOT be flagged."""
    src = (
        "\\documentclass[article]{jss}\n"
        "\\begin{document}\n"
        "<<setup, echo = FALSE, results = hide>>=\n"
        "# Setup prompt to follow requested style\n"
        "options(prompt = \"R> \")\n"
        "@\n"
        "\\end{document}\n"
    )
    doc = _rnw_doc(tmp_path, src)
    violations = _violations_for("JSS-CODE-001", doc)
    assert violations == [], (
        "expected JSS-CODE-001 to skip comments inside echo=FALSE "
        "chunks; the hidden chunk feeds the .R script (where comments "
        "are encouraged), not the rendered manuscript. Got: "
        f"{violations}"
    )


def test_code_001_still_fires_in_visible_chunk(tmp_path: Path):
    """`# comment` inside a visible chunk must still be flagged."""
    src = (
        "\\documentclass[article]{jss}\n"
        "\\begin{document}\n"
        "<<example>>=\n"
        "# This comment ends up rendered in the paper\n"
        "x <- 1\n"
        "@\n"
        "\\end{document}\n"
    )
    doc = _rnw_doc(tmp_path, src)
    violations = _violations_for("JSS-CODE-001", doc)
    assert violations, (
        "expected JSS-CODE-001 to flag comments inside a visible "
        "chunk — comments belong in surrounding LaTeX prose"
    )


# ---------------------------------------------------------------------------
# JSS-MARKUP-003 — bare `NULL` (and similar R sentinel values) in prose
# should be wrapped in \code{}. Reviewer evidence: R5-r3 (Table 3:
# "NULL → \\code{NULL}").
# ---------------------------------------------------------------------------

def test_markup_003_flags_bare_null_in_prose(tmp_path: Path):
    """Plain `NULL` in running text must be wrapped in \\code{}."""
    src = (
        "\\documentclass[article]{jss}\n"
        "\\begin{document}\n"
        "The default value for \\code{verify.saved} is NULL and may "
        "be replaced by a saved bootstrap object.\n"
        "\\end{document}\n"
    )
    doc = _rnw_doc(tmp_path, src)
    violations = _violations_for("JSS-MARKUP-003", doc)
    assert violations, (
        "expected JSS-MARKUP-003 to flag bare 'NULL' in prose; "
        "reviewer R5-r3 explicitly required NULL -> \\code{NULL} "
        "throughout Table 3"
    )
