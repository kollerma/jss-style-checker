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
from collections.abc import Iterator
from typing import Any

from pylatexenc.latexwalker import (
    LatexCharsNode,
    LatexEnvironmentNode,
    LatexGroupNode,
    LatexMacroNode,
)

from texlint.api import ParsedDocument, Rule, ToolConfig, Violation
from texlint.journals.jss import _catalogue_data
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
        "Cauchy", "Cox", "Dirichlet", "Euclidean", "Fisher",
        "Gauss", "Gaussian", "Lagrange", "Laplace", "Markov",
        "Maxwell", "Monte", "Carlo", "Newton", "Pareto", "Pearson",
        "Poisson", "Riemann", "Shannon", "Wald", "Weibull", "Wishart",
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
_CAPTION_EXTRA_PROPER_NOUNS: frozenset[str] = frozenset({
    "January", "February", "March", "April", "May", "June", "July",
    "August", "September", "October", "November", "December",
    "Jan", "Feb", "Mar", "Apr", "Jun", "Jul", "Aug", "Sep",
    "Sept", "Oct", "Nov", "Dec",
})

_PROPER_NOUNS: frozenset[str] = LANGUAGES | R_PACKAGES | _EXTRA_PROPER_NOUNS
_CAPTION_PROPER_NOUNS: frozenset[str] = (
    _PROPER_NOUNS | _CAPTION_EXTRA_PROPER_NOUNS
)


def _violation(
    *, tex: Any, pos: int, rule_id: str, suggestion: str
) -> Violation:
    meta = _catalogue_data.RULES[rule_id]
    line, col = _helpers._lineno_col(tex, pos)
    return Violation(
        file=tex.path,
        line=line,
        column=col,
        rule_id=rule_id,
        severity=meta["severity"],
        message=meta["message_template"],
        suggestion=suggestion,
        fix=None,
    )


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
# ``Estimator``, not to ``(2)``.
_SENTENCE_BOUNDARY_RE = re.compile(
    r"[.:?!]\s+(?:(?:[(\[]\d+[)\]]|\d+[).])\s+)?(\S+)"
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
    plurals of those (SNPs, EOFs, IDs), or mixed-case scientific
    shorthands like mRNA / iPad.
    """
    letters = re.sub(r"[^A-Za-z]", "", token)
    if not letters:
        return False
    if 2 <= len(letters) <= 6 and letters.isupper():
        return True
    # Plural of an all-caps abbreviation: 2-6 caps followed by a single 's'.
    if (
        3 <= len(letters) <= 7
        and letters[-1] == "s"
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


# Match a vignette path's package home: ``examples/cran_<name>/<name>/...``.
# The first word of a JSS title is conventionally the package name in
# bare lowercase; without this hint we'd flag every ``\\title{flexsurv:
# A Platform...}`` style title for "first word not capitalised".
_OWN_PACKAGE_PATH_RE = re.compile(r"/cran_([^/]+)/(?:[^/]+/)?vignettes/")


def _own_package_name(path: Any) -> str | None:
    m = _OWN_PACKAGE_PATH_RE.search(str(path))
    return m.group(1) if m else None


def check_jss_cap_001(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    proper_lower = {n.lower() for n in _PROPER_NOUNS}
    for tex in doc.all_tex_like():
        own_pkg_lower = (_own_package_name(tex.path) or "").lower()
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
            # Skip when the first word is a known package / language /
            # corpus-observed proper noun; these have their own case
            # conventions (lowercase package names, mixed-case method
            # names) and shouldn't trigger the title-case check.
            if first_lower in proper_lower:
                continue
            # Skip when the first word matches the vignette's home
            # package name. JSS papers conventionally start the title
            # with the package name (e.g., ``flexsurv: A Platform for
            # ...``); whether to wrap it in ``\pkg{}`` is a separate
            # MARKUP-002 / REFS-006 concern, not a title-case issue.
            if own_pkg_lower and first_lower == own_pkg_lower:
                continue
            # Skip when the first word looks like a function call
            # (`covMcd()`, `data.frame()`); these are code identifiers
            # the author intentionally left unwrapped.
            if _FUNCTION_CALL_RE.match(first):
                continue
            if not _is_capitalised_word(first) or all(
                w == w.lower() for w in words
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
            )


# ---------------------------------------------------------------------------
# JSS-CAP-003 — captions in sentence style
# ---------------------------------------------------------------------------


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

    if offenders >= 2:
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
            if _keyword_case_violation(entries):
                yield _violation(
                    tex=tex,
                    pos=node.pos,
                    rule_id="JSS-CAP-004",
                    suggestion=(
                        "Use sentence case for keywords (capitalise only "
                        "the first word of each entry unless a proper name)."
                    ),
                )


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


def _rule(rule_id: str, check_fn) -> Rule:
    meta = _catalogue_data.RULES[rule_id]
    return Rule(
        id=rule_id,
        category=meta["category"],
        severity=meta["severity"],
        message_template=meta["message_template"],
        authority=meta["authority"],
        check=check_fn,
        formats=None,
    )


jss_cap_001 = _rule("JSS-CAP-001", check_jss_cap_001)
jss_cap_002 = _rule("JSS-CAP-002", check_jss_cap_002)
jss_cap_003 = _rule("JSS-CAP-003", check_jss_cap_003)
jss_cap_004 = _rule("JSS-CAP-004", check_jss_cap_004)


rules: tuple[Rule, ...] = (jss_cap_001, jss_cap_002, jss_cap_003, jss_cap_004)
