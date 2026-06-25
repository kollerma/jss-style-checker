"""Capitalization rules for the JSS journal plugin.

Rules:
  - JSS-CAP-001 — ``\\title{}`` is in title style (principal words
    capitalised).
  - JSS-CAP-002 — section titles are in sentence style.
  - JSS-CAP-003 — figure / table captions are in sentence style.
  - JSS-CAP-004 — ``\\Keywords{}`` entries are in sentence case,
    comma-separated.

Heuristics tuned via the precision gate; flag rules live in the
AI-skip-list so AI labelling bypasses them entirely.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterator
from typing import Any

from pylatexenc.latexwalker import (
    LatexCharsNode,
    LatexEnvironmentNode,
    LatexGroupNode,
    LatexMacroNode,
)

from texlint.api import ParsedDocument, Rule, ToolConfig, Violation
from texlint.journals.jss.rules import _helpers
from texlint.journals.jss.terms import LANGUAGES, R_PACKAGES

_TITLE_STOPWORDS: frozenset[str] = frozenset(
    {"a", "an", "the", "and", "or", "but", "nor", "for", "so", "yet",
     "at", "by", "in", "of", "on", "to", "up", "via", "with", "as",
     "is", "vs"}
)

_SECTION_MACROS: frozenset[str] = frozenset(
    {"section", "section*", "subsection", "subsection*",
     "subsubsection", "subsubsection*"}
)

_FIGURE_TABLE_ENVS: frozenset[str] = frozenset(
    {"figure", "figure*", "table", "table*"}
)

# Proper nouns that recur in JSS-adjacent prose: nationality
# adjectives, common eponyms (statistical methods named after people),
# and a handful of place / vendor / product names. Curated rather than
# exhaustive — extend as new corpus FPs surface. Style-guide rationale:
# JSS sentence-case captions DO retain capitalisation on proper nouns.
_EXTRA_PROPER_NOUNS: frozenset[str] = frozenset(
    {
        # Nationality / region adjectives
        "American", "Asian", "Australian", "Austrian", "Belgian",
        "British", "Canadian", "Chinese", "Czech", "Dutch", "English",
        "European", "Finnish", "French", "German", "Greek", "Indian",
        "Iranian", "Irish", "Italian", "Japanese", "Korean", "Latin",
        "Mexican", "Norwegian", "Polish", "Portuguese", "Russian",
        "Scottish", "Spanish", "Swedish", "Swiss", "Turkish", "Welsh",
        # Statistical / mathematical eponyms
        "Bayes", "Bayesian", "Bernoulli", "Boole", "Boolean",
        "Cauchy", "Cholesky", "Clayton", "Cox", "Dirichlet",
        "Euclidean", "Fisher", "Frank", "Gauss", "Gaussian",
        "Gumbel", "Lagrange", "Laplace", "Markov", "Maxwell",
        "Monte", "Carlo", "Newton", "Pareto", "Pearson",
        "Poisson", "Riemann", "Shannon", "Wald", "Weibull",
        "Wishart",
        # Place / vendor / product names commonly mentioned
        "Apple", "Google", "Linux", "Microsoft", "Oracle", "Unix",
        "Windows",
        # City and country names that appear in JSS captions
        "Beijing", "Berlin", "Bavaria", "Boston", "China", "Germany",
        "Ireland", "Spain", "Innsbruck", "Vienna", "Wien",
        # Diseases, microbe genera, and named corpora
        "Alzheimer", "Campylobacter", "Faithful", "Indians",
        "Listeria", "Moby", "Newport", "Pima", "Salmonella",
    }
)

# Calendar months — CAP-003-only proper nouns. Months appear in
# time-series captions ("seasonal component over January, March...")
# where the rule should treat them as proper nouns. They MUST NOT
# leak into CAP-002 (section titles): cran_np/np_faq has 51
# changelog headings of the form "Changes from Version X.Y to X.Z
# [12-Mar-2023]" where Mar would otherwise become the second-offender
# anchor — adding months to CAP-002's set silences all 51 TPs.
#
# Also CAP-003-only: cross-reference nouns. Inside sentence-style
# captions, "Figure 3", "Section 7", "Example 2" retain caps because
# they're cross-refs to numbered/labelled elements — JSS doesn't
# downcase those. Restricting these to the caption set protects
# CAP-002, where a section title like "Theorem and Definition"
# legitimately reads as title-case prose.
_CAPTION_EXTRA_PROPER_NOUNS: frozenset[str] = frozenset({
    "January", "February", "March", "April", "May", "June", "July",
    "August", "September", "October", "November", "December",
    "Jan", "Feb", "Mar", "Apr", "Jun", "Jul", "Aug", "Sep",
    "Sept", "Oct", "Nov", "Dec",
    # Cross-reference nouns (singular + plural)
    "Figure", "Figures", "Table", "Tables", "Section", "Sections",
    "Example", "Examples", "Scenario", "Scenarios", "Topic", "Topics",
    "Part", "Parts", "Algorithm", "Algorithms", "Theorem", "Theorems",
    "Equation", "Equations", "Chapter", "Chapters", "Step", "Steps",
    "Phase", "Phases", "Stage", "Stages", "Lemma", "Lemmas",
    "Proposition", "Propositions", "Corollary", "Corollaries",
    "Definition", "Definitions", "Appendix", "Appendices",
})

_PROPER_NOUNS: frozenset[str] = LANGUAGES | R_PACKAGES | _EXTRA_PROPER_NOUNS
_CAPTION_PROPER_NOUNS: frozenset[str] = (
    _PROPER_NOUNS | _CAPTION_EXTRA_PROPER_NOUNS
)


# Catalogue-backed factories live in _helpers (one definition for all
# rule modules); the module-local names are kept for call-site brevity.
_violation = _helpers.tex_violation


def _first_group_arg(macro: Any, parent: Any, idx: int) -> Any:
    argd = getattr(macro, "nodeargd", None)
    if argd is not None:
        for arg in argd.argnlist or ():
            if isinstance(arg, LatexGroupNode):
                delim = getattr(arg, "delimiters", None)
                if delim and delim[0] == "[":
                    continue
                return arg
    return _helpers._next_group_arg(parent, idx)


def _group_plain_text(group: Any) -> str:
    """Plain text of a group with markup-macro contents excluded.

    pylatexenc, with no macro DB entry for ``\\pkg``/``\\proglang``/
    ``\\code``, parses ``\\pkg{zoo}`` as a bare macro followed by a
    separate ``{zoo}`` LatexGroupNode sibling. Naively recursing into
    every group would re-introduce the package name into plain text
    even though the author marked it as wrapped — and that's exactly
    the content the capitalisation rules should NOT scan (package
    names, language names, code identifiers all have their own
    case conventions). Skip a sibling group when the previous child
    was a markup macro.
    """
    parts: list[str] = []
    skip_next_group = False
    for child in group.nodelist or ():
        if isinstance(child, LatexCharsNode):
            skip_next_group = False
            parts.append(child.chars)
        elif isinstance(child, LatexGroupNode):
            if skip_next_group:
                skip_next_group = False
                continue
            parts.append(_group_plain_text(child))
        elif isinstance(child, LatexMacroNode):
            if child.macroname == "label":
                continue
            skip_next_group = child.macroname in _helpers._MARKUP_MACROS
    return "".join(parts)


def _words(text: str) -> list[str]:
    return [w for w in re.split(r"[\s\-]+", text.strip()) if w]


# Sentence boundary: a punctuator (``.:?!``) followed by whitespace
# and a content word. An optional list-numbering stub like ``(1)``,
# ``[2]``, ``1.``, or ``2)`` between the punctuator and the content
# word is transparent — caption text such as ``... algorithms.
# (2) Estimator consists ...`` should anchor the boundary to
# ``Estimator``, not to ``(2)``. The same applies to subfigure-letter
# labels ``(a)`` / ``(b)`` / ``[i]`` / ``(ii)`` that introduce panel
# captions (``... data. (a) Cross-validation ... (b) Comparison ...``).
_LIST_NUMBERING = (
    r"(?:[(\[]\d+[)\]]|\d+[).]"
    r"|[(\[][a-z][)\]]|[(\[][ivx]{1,4}[)\]])"
)
# The content-word capture is a single non-space character: callers only
# read ``m.start(1)`` (the start offset), and matching the whole word
# greedily would swallow trailing ``.:?!`` characters that should remain
# available to anchor the *next* sub-sentence boundary. Example:
# ``(solid: mean, dashed: quartiles).\n    Plot corresponds to ...`` —
# with greedy ``(\S+)`` the inner colon's match consumes ``quartiles).``
# and the final ``.`` is no longer available to anchor ``Plot``.
_SENTENCE_BOUNDARY_RE = re.compile(
    r"[.:?!]\s+(?:" + _LIST_NUMBERING + r"\s+)?(\S)"
)
# Caption-leading list-numbering: ``(a) Sketch of ...`` / ``(i) Foo ...``
# at the very start of a caption should treat the post-label word as a
# sentence-opening word (no preceding punctuator required).
_CAPTION_LEADING_LABEL_RE = re.compile(
    r"^\s*" + _LIST_NUMBERING + r"\s+(\S)"
)


def _words_with_boundary(text: str) -> list[tuple[str, bool, bool]]:
    """Like ``_words`` but each entry carries two flags:

    - ``is_boundary``: True if this word starts a new sub-sentence
      (previous source token ended with ``.:?!``).
    - ``is_hyphen_piece``: True if this is a non-first piece of a
      hyphenated source word (e.g., ``Weinberg`` in
      ``Hardy-Weinberg``). Sentence-style for section titles
      treats hyphenated compounds as single proper-noun units.

    Splits on whitespace AND on hyphens so compound terms like
    ``Logistic-regression-based`` decompose into individual tokens
    for the capitalisation check.
    """
    boundary_offsets: set[int] = set()
    for m in _SENTENCE_BOUNDARY_RE.finditer(text):
        boundary_offsets.add(m.start(1))
    # Caption-leading subfigure label: anchor the post-label word as a
    # sentence-start so ``(a) Sketch of ...`` doesn't penalise ``Sketch``.
    leading = _CAPTION_LEADING_LABEL_RE.match(text)
    if leading:
        boundary_offsets.add(leading.start(1))
    out: list[tuple[str, bool, bool]] = []
    # Tokenize whitespace-delimited "source words" first to anchor the
    # boundary flag, then split each source word on hyphens.
    for source_match in re.finditer(r"\S+", text):
        source_word = source_match.group(0)
        is_boundary = source_match.start() in boundary_offsets
        for piece_idx, piece in enumerate(re.split(r"-+", source_word)):
            clean = re.sub(r"^[^A-Za-z0-9]+|[^A-Za-z0-9]+$", "", piece)
            if not clean:
                continue
            # Only the first hyphen-piece inherits the sub-sentence
            # boundary flag; subsequent pieces are interior.
            out.append((clean, is_boundary and piece_idx == 0, piece_idx > 0))
    return out


def _looks_like_abbrev(token: str) -> bool:
    """True for abbreviations that are conventionally capitalised even
    in sentence style — all-caps 2–6 letter tokens (PDF, NIH, NACP),
    plurals of those (SNPs, EOFs, IDs), all-caps with a single trailing
    lowercase variant suffix (LLt / LDLt / RSEn / RSEa — common in
    statistics / linear-algebra prose), or mixed-case scientific
    shorthands like mRNA / iPad.
    """
    letters = re.sub(r"[^A-Za-z]", "", token)
    if not letters:
        return False
    if 2 <= len(letters) <= 6 and letters.isupper():
        return True
    # All-caps abbreviation followed by a single trailing lowercase
    # letter — covers plurals (SNPs, EOFs, IDs) AND single-letter
    # variant suffixes (LLt, LDLt for matrix decomposition shorthand;
    # RSEn / RSEa for statistical estimator labels).
    if (
        3 <= len(letters) <= 7
        and letters[-1].islower()
        and len(letters) - 1 >= 2
        and letters[:-1].isupper()
    ):
        return True
    # Mixed-case with an interior uppercase that follows a lowercase
    # (mRNA, iPad, gRPC). Single capital at the start is NOT a match.
    if any(letters[i].isupper() and letters[i - 1].islower() for i in range(1, len(letters))):
        return True
    return False


def _is_capitalised_word(word: str) -> bool:
    letters = re.sub(r"[^A-Za-z]", "", word)
    if not letters:
        return True
    return letters[0].isupper()


# ---------------------------------------------------------------------------
# JSS-CAP-001 — \title{} in title style
# ---------------------------------------------------------------------------


_FUNCTION_CALL_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_.]*\(\)?$")


# Title-leading markup macro: ``\title{\proglang{R}-package ...}``,
# ``\title{\pkg{foo} for X}``. The author-dictated case inside the
# wrapper acts as the title's first word; the rule's first-word
# capitalisation check should defer to it.
_TITLE_LEADING_MARKUP_RE = re.compile(
    r"^\{?\s*\\(pkg|proglang|code|fct|verb)\b"
)


def _title_source(group: Any) -> str:
    """Return the raw LaTeX source of a title group, used for the
    leading-markup probe. Concatenates char nodes plus a literal
    serialisation of macros that pylatexenc surfaces inside the title.
    Cheap approximation: we only need to know whether the first
    visible token is a markup macro.
    """
    parts: list[str] = []
    for child in group.nodelist or ():
        if isinstance(child, LatexCharsNode):
            parts.append(child.chars)
            if child.chars.strip():
                break
        elif isinstance(child, LatexMacroNode):
            parts.append(f"\\{child.macroname}")
            break
        elif isinstance(child, LatexGroupNode):
            parts.append("{")
            inner = _title_source(child)
            parts.append(inner)
            break
    return "".join(parts)


def _word_letters_lower(word: str) -> str:
    return re.sub(r"[^A-Za-z]", "", word).lower()


def _pkg_token(word: str) -> str:
    """Normalise a word for package-name comparison: keep letters,
    digits, and dots (``ggplot2``, ``data.table``); strip surrounding
    punctuation like the conventional title colon; lowercase."""
    return re.sub(r"[^A-Za-z0-9.]", "", word).strip(".").lower()


def _doc_pkg_names_lower(doc: ParsedDocument) -> set[str]:
    """Package names the document itself wraps in ``\\pkg{...}``.

    The first word of a JSS title is conventionally the paper's own
    package name in its native (often lowercase) casing — e.g.
    ``\\title{flexsurv: A Platform for ...}``. A paper about a package
    invariably wraps that name in ``\\pkg{}`` somewhere (abstract,
    body), so the document's own markup is the authoritative signal.
    This replaces an earlier filesystem-path heuristic that only
    matched the eval corpus's ``cran_<name>/vignettes/`` layout and
    never fired on real submissions.
    """
    return {
        _pkg_token(name)
        for name in _helpers._collect_macro_arg_texts(doc, "pkg")
        if _pkg_token(name)
    }


def check_jss_cap_001(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    proper_lower = {n.lower() for n in _PROPER_NOUNS}
    doc_pkgs_lower = _doc_pkg_names_lower(doc)
    for tex in doc.all_tex_like():
        for parent, idx, node in _helpers._iter_with_parent(tex.nodes):
            if not (
                isinstance(node, LatexMacroNode) and node.macroname == "title"
            ):
                continue
            group = _first_group_arg(node, parent, idx)
            if group is None:
                continue
            text = _group_plain_text(group)
            words = _words(text)
            if not words:
                continue
            # Skip when the title source opens with a markup macro
            # AND the plain-text continuation starts with ``-`` (the
            # ``\proglang{R}-package ...`` compound idiom from
            # cran_ReacTran). When the continuation starts with
            # whitespace + lowercase word (e.g. ``\pkg{X} version Y``),
            # that's a regular title-style failure on the post-markup
            # word and the rule should fire.
            if (
                text.lstrip().startswith("-")
                and _TITLE_LEADING_MARKUP_RE.match(_title_source(group))
            ):
                continue
            # Skip when no principal word remains after stripping
            # stopwords — title is effectively just markup macros plus
            # connectives like "and" / "the".
            principal = [
                w for w in words
                if _word_letters_lower(w)
                and _word_letters_lower(w) not in _TITLE_STOPWORDS
            ]
            if not principal:
                continue
            first = words[0]
            first_lower = _word_letters_lower(first)
            # Determine whether the first word is exempt (proper noun,
            # self-package, function call). These exemptions only
            # suppress the FIRST-WORD check, not the principal-word
            # check — clifford's title ``Clifford algebra in R`` has
            # ``Clifford`` as a self-package first-word (exempt) but
            # ``algebra`` mid-title is still a real lowercase principal.
            first_word_exempt = (
                first_lower in proper_lower
                or _pkg_token(first) in doc_pkgs_lower
                or _FUNCTION_CALL_RE.match(first) is not None
            )
            if not first_word_exempt and (
                not _is_capitalised_word(first)
                or all(w == w.lower() for w in words)
            ):
                yield _violation(
                    tex=tex,
                    pos=node.pos,
                    rule_id="JSS-CAP-001",
                    suggestion=(
                        "Use title style: capitalise principal words in "
                        "the title."
                    ),
                )
                continue
            # Title-case principal-word check: any non-first word that
            # is all lowercase, ≥ 4 letters, and not a stopword is a
            # title-case violation. Catches clifford ("Clifford algebra
            # in R" — ``algebra``) and rstpm2 ("Predictions for
            # parametric and penalised..." — ``parametric``,
            # ``penalised``). Proper-noun set, known-package set, and
            # stopwords still keep the check tight.
            for word in words[1:]:
                bare = _word_letters_lower(word)
                if not bare or len(bare) < 4:
                    continue
                if word == word.lower() and bare not in _TITLE_STOPWORDS:
                    if bare in proper_lower:
                        continue
                    if bare in doc_pkgs_lower:
                        continue
                    yield _violation(
                        tex=tex,
                        pos=node.pos,
                        rule_id="JSS-CAP-001",
                        suggestion=(
                            "Use title style: capitalise principal "
                            f"words in the title (found lowercase "
                            f"{word!r})."
                        ),
                    )
                    break


# ---------------------------------------------------------------------------
# JSS-CAP-002 — section titles in sentence style
# ---------------------------------------------------------------------------


def check_jss_cap_002(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.all_tex_like():
        for parent, idx, node in _helpers._iter_with_parent(tex.nodes):
            if not (
                isinstance(node, LatexMacroNode)
                and node.macroname in _SECTION_MACROS
            ):
                continue
            group = _first_group_arg(node, parent, idx)
            if group is None:
                continue
            yield from _check_sentence_style(
                tex, node.pos, group, "JSS-CAP-002",
                "Use sentence style: capitalise only the first word "
                "(proper names remain capitalised).",
                # Section titles are short and the user's recall
                # annotations flag single-offender titles like
                # "Bayesian Estimation" / "Model Training" / "MCMC
                # Diagnostics". Lower the threshold to 1; the existing
                # proper-noun set and stopword anchoring still suppress
                # acceptable "Bayesian"-only and "Markov Chain"-style
                # runs (those words are in the proper-noun set).
                min_offenders=1,
            )


# ---------------------------------------------------------------------------
# JSS-CAP-003 — captions in sentence style
# ---------------------------------------------------------------------------


# Textual citation pattern inside captions: "Author and Coauthor"
# (optionally preceded by "by " and/or followed by ", YYYY"). Two or
# more capitalised surnames joined by "and"/"&" are the diagnostic;
# a single capitalised name doesn't match (those overlap too much
# with proper nouns referenced as method/eponym names like "Huber").
_TEXTUAL_CITATION = re.compile(
    r"\b[A-Z][a-zA-Z]+(?:\s+(?:and|&)\s+[A-Z][a-zA-Z]+)+(?:,\s*\d{4})?\b"
)


def _strip_textual_citations(text: str) -> str:
    """Remove "Author and Coauthor[, YYYY]" runs from caption text.

    Captions sometimes embed the source ("from Soetaert and Herman,
    2009" / "by Pollet and Nettle"); the surnames trip the
    title-style detector even though sentence-style permits them.
    Stripping the matched span before tokenisation avoids the false
    positives without lowering recall on captions where the citation
    is one of several title-style markers (the remaining offenders
    still fire the rule).
    """
    return _TEXTUAL_CITATION.sub(" ", text)


# Caption-label prefix: a leading "Capitalised Phrase: " that names
# the dataset / cohort / approach the figure depicts, followed by a
# sentence-style description. JSS permits this label form — the
# descriptive part after the colon is what should be evaluated.
# The prefix tokens may be hyphenated ("One-dimensional"), digit-
# bearing ("Group 2"), or all-caps acronyms ("GBSG2"); a stopword
# (lowercase "of", "and", etc.) inside the prefix breaks the pattern
# so prose like "Effect of treatment: ..." doesn't match.
_LABEL_PREFIX = re.compile(
    r"^\s*("
    r"[A-Z][A-Za-z0-9'\-]*"
    r"(?:\s+[A-Z0-9][A-Za-z0-9'\-]*){0,6}"
    r")\s*:\s+"
)


def _strip_label_prefix(text: str) -> str:
    """Strip a leading "Capitalised Phrase: " label from a caption.

    Captions often open with a dataset / cohort / approach name
    followed by a colon and the actual sentence-style description
    ("Boston Housing: scatterplot of...", "German Breast Cancer
    Study Group 2: conditional survivor curves..."). The label
    counts as a proper-noun phrase and shouldn't trip the
    title-style detector. Only the body after the colon is the
    caption proper.
    """
    return _LABEL_PREFIX.sub("", text, count=1)


def _preprocess_caption(text: str) -> str:
    """Caption-text preprocessor: strip leading label prefix, then
    embedded textual citations. Order matters — the citation
    pattern can otherwise consume the first word of the body."""
    return _strip_textual_citations(_strip_label_prefix(text))


def check_jss_cap_003(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.all_tex_like():
        for node, ancestors, parent, idx in _helpers._walk_with_context(
            tex.nodes
        ):
            if not (
                isinstance(node, LatexMacroNode)
                and node.macroname == "caption"
            ):
                continue
            if not any(
                isinstance(a, LatexEnvironmentNode)
                and a.environmentname in _FIGURE_TABLE_ENVS
                for a in ancestors
            ):
                continue
            group = _first_group_arg(node, parent, idx)
            if group is None:
                continue
            yield from _check_sentence_style(
                tex, node.pos, group, "JSS-CAP-003",
                "Use sentence style in the caption (capitalise only the "
                "first word; proper names remain capitalised).",
                collapse_runs=True,
                proper_nouns=_CAPTION_PROPER_NOUNS,
                text_preprocessor=_preprocess_caption,
            )


def _is_capitalised_offender(
    word: str,
    proper_nouns: frozenset[str] = _PROPER_NOUNS,
) -> bool:
    """True if ``word`` is a capitalised non-stopword non-proper-noun
    that's NOT an abbreviation or single-letter math symbol — i.e.,
    the kind of capitalisation sentence style penalises.
    """
    bare = re.sub(r"[^A-Za-z]", "", word)
    if not bare:
        return False
    if len(bare) == 1:
        # Single capital letters in prose are math/stat symbols
        # (X, M, F, t, p) — JSS doesn't penalise them.
        return False
    if not bare[0].isupper():
        return False
    if bare in proper_nouns:
        return False
    if bare.lower() in _TITLE_STOPWORDS:
        return False
    if _looks_like_abbrev(bare):
        return False
    return True


def _is_run_eligible(word: str) -> bool:
    """A capitalised non-single-letter token that can participate in a
    proper-noun run. Single letters (``Q-Q``, ``X``) are math symbols
    in research prose, not name fragments."""
    bare = re.sub(r"[^A-Za-z]", "", word)
    if not bare or len(bare) < 2:
        return False
    return bare[0].isupper()


# Maximum length of a "proper-noun phrase" run; longer runs of
# consecutive capitalised words signal title-case prose, not a name.
_PROPER_NOUN_RUN_MAX = 3


def _check_sentence_style(
    tex: Any,
    pos: int,
    group: Any,
    rule_id: str,
    suggestion: str,
    *,
    collapse_runs: bool = False,
    proper_nouns: frozenset[str] = _PROPER_NOUNS,
    text_preprocessor: Callable[[str], str] | None = None,
    min_offenders: int = 2,
) -> Iterator[Violation]:
    """Fire when ≥2 distinct offending capitalisations appear in ``group``.

    ``collapse_runs=True`` (used for caption context) treats a short
    multi-token capitalised compound — either hyphenated
    (``Hardy-Weinberg``) or whitespace-separated with all pieces
    capitalised (``Han Chinese``, ``Moby Dick``) — as a single
    proper-noun phrase, counted at most once. Long runs (4+ caps in a
    row, or runs containing a capitalised stopword like ``For`` /
    ``Of``) are not collapsed: those signal title-case prose.

    With ``collapse_runs=False`` (the default, used for section headings
    where two-word capital runs ARE the title-case signature), each
    capitalised non-proper-non-abbrev token contributes individually.

    ``proper_nouns`` lets callers extend the recognised proper-noun
    set per rule — CAP-003 passes a wider set (including calendar
    months) while CAP-002 sticks with the base set so changelog
    headings like ``Changes from Version X to Y [12-Mar-2023]`` still
    count ``Mar`` as a stopword anchor.
    """
    text = _group_plain_text(group)
    if text_preprocessor is not None:
        text = text_preprocessor(text)
    words = _words_with_boundary(text)
    if not words:
        return

    seen: set[str] = set()
    offenders = 0
    n = len(words)
    i = 0
    while i < n:
        word, is_boundary, _ = words[i]
        is_start = (i == 0) or is_boundary
        if not _is_run_eligible(word):
            i += 1
            continue

        # Greedily extend a run of consecutive eligible-capitalised tokens.
        # _words_with_boundary marks each piece with is_hyphen_piece=True
        # when it sits inside a single hyphenated source word
        # (``Hardy-Weinberg`` → ``Weinberg`` is a hyphen-piece).
        run_start = i
        j = i + 1
        all_hyphen_joined = True
        while j < n:
            nw, nb, nh = words[j]
            if nb or not _is_run_eligible(nw):
                break
            if not nh:
                all_hyphen_joined = False
            j += 1
        run = [w for w, _, _ in words[run_start:j]]
        run_text = "-".join(w.lower() for w in run)
        any_known = any(
            p in proper_nouns or _looks_like_abbrev(p) for p in run
        )
        any_stopword = any(p.lower() in _TITLE_STOPWORDS for p in run)

        # Hyphenated compounds (``Hardy-Weinberg``, ``Aalen-Johansen``,
        # ``Newey-West``) are single proper-noun units — collapse them
        # in section titles too. Whitespace-separated runs (``Linear
        # Models``, ``Trade Statistics``) are still title-case markers
        # under section-title sentence style and stay un-collapsed
        # unless the caller opts in via ``collapse_runs=True``.
        is_compound = (
            (collapse_runs or all_hyphen_joined)
            and len(run) >= 2
            and len(run) <= _PROPER_NOUN_RUN_MAX
            and not any_stopword
        )

        if is_compound:
            # Short run of consecutive caps with no stopwords → likely a
            # multi-word proper noun. Anchored runs (containing a known
            # proper noun or abbreviation) cost zero; un-anchored runs
            # cost one (and only on first occurrence).
            if not any_known and not is_start and run_text not in seen:
                seen.add(run_text)
                offenders += 1
            i = j
            continue

        # Either a single-token cap, or a long run that's actually
        # title-case. Fall back to the per-token offender check on each
        # element of the run that wasn't already a sentence-start.
        # Hyphen-piece continuations whose leading sibling is itself in
        # the run (``Thompson`` in ``Horvitz-Thompson``) inherit the
        # offender status of that sibling — count the chain at most
        # once so multi-piece hyphenated proper names like
        # ``Aalen-Johansen`` / ``Ali-Mikhail-Haq`` aren't double-
        # penalised. A solitary hyphen-piece whose preceding source
        # piece wasn't run-eligible (``Mar`` in ``12-Mar-2023``) keeps
        # contributing — that's a real title-case signal.
        run_meta = words[run_start:j]
        for k, (w, _, w_is_hyphen) in enumerate(run_meta):
            if k == 0 and is_start:
                continue
            if w_is_hyphen and k > 0:
                continue
            if _is_capitalised_offender(w, proper_nouns):
                key = w.lower()
                if key in seen:
                    continue
                seen.add(key)
                offenders += 1
        i = j

    if offenders >= min_offenders:
        yield _violation(
            tex=tex, pos=pos, rule_id=rule_id, suggestion=suggestion
        )


# ---------------------------------------------------------------------------
# JSS-CAP-004 — \Keywords sentence case
# ---------------------------------------------------------------------------


def check_jss_cap_004(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.all_tex_like():
        for parent, idx, node in _helpers._iter_with_parent(tex.nodes):
            if not (
                isinstance(node, LatexMacroNode)
                and node.macroname == "Keywords"
            ):
                continue
            group = _first_group_arg(node, parent, idx)
            if group is None:
                continue
            text = _group_plain_text(group)
            entries = [e.strip() for e in text.split(",") if e.strip()]
            # Two sentence-case defects: a non-first word capitalised
            # (title case), or the very first keyword starting lowercase
            # (the list reads as a sentence, so its first word is
            # capitalised). The leading-capital check is skipped when the
            # first keyword is wrapped in markup (\pkg{}, \proglang{}, …),
            # whose contents keep their own lowercase case convention.
            missing_lead = (
                not _first_keyword_is_markup(group)
                and _keyword_missing_leading_cap(entries)
            )
            if _keyword_case_violation(entries) or missing_lead:
                yield _violation(
                    tex=tex,
                    pos=node.pos,
                    rule_id="JSS-CAP-004",
                    suggestion=(
                        "Use sentence case for keywords (capitalise only "
                        "the first word of each entry unless a proper name)."
                    ),
                )


def _first_keyword_is_markup(group: Any) -> bool:
    """True when the first keyword is wrapped in a markup macro
    (``\\pkg{}``, ``\\proglang{}``, ``\\code{}``, …). Such a keyword keeps
    its own lowercase case convention and must not be forced to a leading
    capital. ``_group_plain_text`` strips the wrapped content entirely, so
    the check has to inspect the group nodes directly."""
    for child in group.nodelist or ():
        if isinstance(child, LatexCharsNode):
            if child.chars.strip() == "":
                continue
            return False  # first real content is plain prose
        if isinstance(child, LatexMacroNode):
            if child.macroname == "label":
                continue
            return child.macroname in _helpers._MARKUP_MACROS
        if isinstance(child, LatexGroupNode):
            return False
    return False


def _keyword_missing_leading_cap(entries: list[str]) -> bool:
    """True when the first keyword's first word starts with a lowercase
    letter (and isn't a known proper noun / package name written bare).
    JSS keywords are sentence case, so the list's first word is
    capitalised."""
    if not entries:
        return False
    words = [w for w in re.split(r"\s+", entries[0].strip()) if w]
    if not words:
        return False
    first_word = words[0]
    bare = re.sub(r"[^A-Za-z]", "", first_word)
    if not bare or not bare[0].islower():
        return False
    # A lowercase token that is a known package / language name (e.g. a
    # bare ``ggplot2``) keeps its own case — don't demand a capital.
    if first_word in _PROPER_NOUNS or bare in _PROPER_NOUNS:
        return False
    return True


def _keyword_case_violation(entries: list[str]) -> bool:
    # Split on whitespace only — hyphenated tokens like Bradley-Terry,
    # Newey-West, or pre-trained are single conceptual units in keyword
    # entries (proper-noun compounds and lowercase compounds alike) and
    # shouldn't be torn apart into separately-evaluated pieces.
    for entry in entries:
        words = re.split(r"\s+", entry.strip())
        words = [w for w in words if w]
        if len(words) < 2:
            continue
        offenders = 0
        for idx, word in enumerate(words):
            if idx == 0:
                continue
            bare = re.sub(r"[^A-Za-z]", "", word)
            if not bare:
                continue
            if not bare[0].isupper():
                continue
            if bare in _PROPER_NOUNS:
                continue
            if bare.lower() in _TITLE_STOPWORDS:
                continue
            # All-caps abbreviations (MCMC, TVP, OOP, GARCH, SV) are
            # conventionally written upper-case even in sentence-style
            # keywords — exempt them the same way CAP-003's
            # _is_capitalised_offender does.
            if _looks_like_abbrev(bare):
                continue
            offenders += 1
        if offenders >= 1:
            return True
    return False


# ---------------------------------------------------------------------------
# Rule objects
# ---------------------------------------------------------------------------


_rule = _helpers.make_rule


jss_cap_001 = _rule("JSS-CAP-001", check_jss_cap_001)
jss_cap_002 = _rule("JSS-CAP-002", check_jss_cap_002)
jss_cap_003 = _rule("JSS-CAP-003", check_jss_cap_003)
jss_cap_004 = _rule("JSS-CAP-004", check_jss_cap_004)


rules: tuple[Rule, ...] = (jss_cap_001, jss_cap_002, jss_cap_003, jss_cap_004)
