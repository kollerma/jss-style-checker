"""Independent double-check for JSS-CAP-003 (caption sentence-style).

CAP-003 is the harness's lowest-precision rule (~61%). The difficulty
is entirely *proper-noun disambiguation*: a caption like

    Cluster Quality Measures Available in WeightedCluster

is a genuine title-case violation, while

    Periodograms for Mrk 421 obtained fitting a Joe copula

is correct sentence style whose capitals are proper nouns. The local
labeller models (Bonsai, Qwen3) both fall below the trust floor on
this call, so CAP-003 is skip-listed for AI review and its verdicts
must be established another way.

This module is the reusable double-check. It splits the work into a
*deterministic* half and a *judgement* half:

  * `analyze` (deterministic, testable): for every currently-firing
    CAP-003 violation, extract the full caption from source and emit a
    structured worksheet — each word capitalised after the first,
    auto-tagged as math / code / ref / label / cite / number / acronym
    / single-letter / ordinary. Only the ``ordinary`` capitals need a
    proper-noun judgement; everything else is mechanically excluded.

  * `apply` (judgement intake + validation): ingest a verdicts file
    produced by a strong judge (a frontier model via the established
    ``claude-proxy`` pattern, or a human) reading that worksheet, then
    (a) NEVER overwrite real-human (`human:unknown`) labels — instead
    compare against them and report inter-rater agreement, surfacing
    disagreements for adjudication; (b) write the judge's verdict for
    claude-proxy and pending rows under a traceable reviewer string.

The split keeps the unreliable part (proper nouns) with the capable
judge and the reliable part (LaTeX extraction + tokenisation) in
tested code, and makes the whole double-check reproducible as the
corpus grows.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from eval import db

RULE_ID = "JSS-CAP-003"
# Reviewer audit string for judge-applied verdicts. Kept under the
# ``human:claude-proxy`` prefix so the labeller benchmark's
# ``NOT LIKE 'human:claude-proxy%'`` filter still excludes these from
# the human gold set (judging an AI labeller against a frontier judge
# would not bound ground-truth error).
JUDGE_REVIEWER = "human:claude-proxy:cap003-recheck"
# A real-human label we must never overwrite — the independent rater
# the double-check validates against.
HUMAN_REVIEWER_PREFIXES = ("human:unknown", "human:reviewer")


# ---------------------------------------------------------------------------
# Deterministic caption extraction + analysis
# ---------------------------------------------------------------------------

# Inline constructs whose *content* never counts toward sentence style.
# Matched on the raw caption body and replaced with a tagged
# placeholder so the surviving prose tokenises cleanly.
_TAGGED_CONSTRUCTS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("math", re.compile(r"\$[^$]*\$")),
    ("label", re.compile(r"\\label\s*\{[^{}]*\}")),
    ("ref", re.compile(r"\\(?:ref|autoref|cref|Cref|eqref|pageref)\s*\{[^{}]*\}")),
    ("cite", re.compile(r"\\[a-zA-Z]*cite[a-zA-Z]*\s*(?:\[[^\]]*\])*\s*\{[^{}]*\}")),
    ("code", re.compile(
        r"\\(?:texttt|code|proglang|pkg|verb|file|command|samp)\s*\{[^{}]*\}"
    )),
)

_WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9'\-]*")


@dataclass
class CaptionWord:
    """One whitespace-delimited word of caption prose (after the first),
    with the reason it does or doesn't bear on sentence style."""

    word: str
    capitalised: bool
    tag: str  # ordinary | number | acronym | single-letter | lowercase


@dataclass
class CaptionAnalysis:
    raw: str
    clean: str               # prose with tagged constructs removed
    words: list[CaptionWord]
    # Capitals that still need a proper-noun decision from the judge:
    ordinary_capitals: list[str] = field(default_factory=list)
    # Heuristic-only count of likely offenders (hint, not a verdict):
    heuristic_offenders: int = 0


def _strip_constructs(body: str) -> str:
    """Replace math / code / ref / label / cite constructs with a space
    so their capitalised content can't masquerade as title-case."""
    out = body
    for _tag, pat in _TAGGED_CONSTRUCTS:
        out = pat.sub(" ", out)
    # Drop any remaining bare macros (\textbf, \emph, …) but keep their
    # brace contents — those are usually emphasised prose words.
    out = re.sub(r"\\[a-zA-Z]+\s*", " ", out)
    out = out.replace("{", " ").replace("}", " ")
    return out


def _classify(word: str, *, is_first: bool) -> CaptionWord:
    bare = re.sub(r"[^A-Za-z0-9]", "", word)
    letters = re.sub(r"[^A-Za-z]", "", word)
    capitalised = bool(letters) and letters[0].isupper()
    if not capitalised:
        tag = "lowercase"
    elif len(letters) == 1:
        tag = "single-letter"          # math / stat symbol (X, F, t)
    elif re.search(r"\d", bare) and letters.isupper():
        tag = "acronym"                # GROJ0422, GBSG2
    elif len(letters) >= 2 and letters.isupper():
        tag = "acronym"                # PARAFAC, CRAN
    else:
        tag = "ordinary"               # needs a proper-noun decision
    return CaptionWord(word=word, capitalised=capitalised, tag=tag)


def analyze_caption(body: str) -> CaptionAnalysis:
    """Deterministic structured analysis of one caption body."""
    clean = _strip_constructs(body)
    tokens = _WORD_RE.findall(clean)
    words: list[CaptionWord] = []
    ordinary_caps: list[str] = []
    for i, tok in enumerate(tokens):
        cw = _classify(tok, is_first=(i == 0))
        words.append(cw)
        # The first prose word is expected capitalised in sentence
        # style; never an offender.
        if i == 0:
            continue
        if cw.tag == "ordinary":
            ordinary_caps.append(cw.word)
    # Heuristic hint only: ≥2 ordinary capitals is the rule's own
    # trigger. The judge still rules on each (proper noun or not).
    analysis = CaptionAnalysis(
        raw=body.strip(),
        clean=" ".join(clean.split()),
        words=words,
        ordinary_capitals=ordinary_caps,
        heuristic_offenders=len(ordinary_caps),
    )
    return analysis


def extract_caption(source: str, line: int) -> str | None:
    """Extract the full ``\\caption{...}`` body that begins at (or just
    after) 1-based ``line`` in ``source``. Handles a leading optional
    ``[short]`` argument and a multi-line, brace-balanced body."""
    lines = source.splitlines(keepends=True)
    if not (1 <= line <= len(lines)):
        return None
    start = sum(len(s) for s in lines[: line - 1])
    m = re.compile(r"\\caption\b").search(source, start)
    if m is None:
        return None
    i = m.end()
    n = len(source)
    # Skip whitespace and an optional [short caption] argument.
    while i < n and source[i].isspace():
        i += 1
    if i < n and source[i] == "[":
        depth = 1
        i += 1
        while i < n and depth:
            if source[i] == "[":
                depth += 1
            elif source[i] == "]":
                depth -= 1
            i += 1
        while i < n and source[i].isspace():
            i += 1
    if i >= n or source[i] != "{":
        return None
    return _balanced(source, i)


def _balanced(src: str, i: int) -> str | None:
    """``src[i]`` is ``{``; return the body between it and its match,
    honouring ``\\{`` / ``\\}`` escapes. None if unbalanced."""
    depth = 0
    j = i
    n = len(src)
    while j < n:
        c = src[j]
        if c == "\\":
            j += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return src[i + 1 : j]
        j += 1
    return None


# ---------------------------------------------------------------------------
# DB-facing worksheet + verdict application
# ---------------------------------------------------------------------------


@dataclass
class RecheckRow:
    violation_id: int
    paper_path: str
    file: str
    line: int
    verdict: str | None
    reviewer: str | None
    analysis: CaptionAnalysis | None


def _read_source(paper_path: str, file: str | None) -> str | None:
    if not file:
        return None
    p = Path(paper_path) / file
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def collect_rows(cx) -> list[RecheckRow]:
    """Every currently-firing CAP-003 violation, with its caption
    analysis attached (None when the source can't be read)."""
    max_run = cx.execute("SELECT MAX(id) FROM runs").fetchone()[0]
    rows = cx.execute(
        "SELECT v.id, p.path AS paper_path, v.file, v.line, v.verdict,"
        " v.reviewer FROM violations v JOIN papers p ON p.id = v.paper_id"
        " WHERE v.rule_id = ?"
        " AND (v.last_seen_run_id = ? OR v.last_seen_run_id IS NULL)"
        " ORDER BY p.path, v.file, v.line",
        (RULE_ID, max_run),
    ).fetchall()
    out: list[RecheckRow] = []
    for r in rows:
        src = _read_source(r["paper_path"], r["file"])
        analysis = None
        if src is not None:
            body = extract_caption(src, r["line"])
            if body is not None:
                analysis = analyze_caption(body)
        out.append(
            RecheckRow(
                violation_id=r["id"],
                paper_path=r["paper_path"],
                file=r["file"],
                line=r["line"],
                verdict=r["verdict"],
                reviewer=r["reviewer"],
                analysis=analysis,
            )
        )
    return out


def _is_human(reviewer: str | None) -> bool:
    return bool(reviewer) and any(
        reviewer.startswith(pfx) for pfx in HUMAN_REVIEWER_PREFIXES
    )


@dataclass
class ApplyReport:
    written: int = 0
    human_agreements: int = 0
    human_disagreements: list[dict] = field(default_factory=list)
    skipped_unknown_id: list[int] = field(default_factory=list)

    @property
    def human_checked(self) -> int:
        return self.human_agreements + len(self.human_disagreements)

    @property
    def human_agreement_rate(self) -> float | None:
        return (
            self.human_agreements / self.human_checked
            if self.human_checked
            else None
        )


def apply_verdicts(
    cx, verdicts: list[dict], *, judge_reviewer: str = JUDGE_REVIEWER
) -> ApplyReport:
    """Ingest judge verdicts and reconcile against existing labels.

    ``verdicts`` is a list of ``{"id": int, "verdict":
    "true_positive"|"false_positive", "reason": str}``.

    * Rows currently labelled by a real human are NEVER overwritten —
      the judge verdict is compared to the human's and counted toward
      inter-rater agreement; mismatches land in ``human_disagreements``
      for the user to adjudicate.
    * All other rows (claude-proxy, pending) receive the judge verdict
      under ``judge_reviewer``.
    """
    by_id = {
        int(r["id"]): r
        for r in cx.execute(
            f"SELECT id, verdict, reviewer FROM violations"
            f" WHERE rule_id = '{RULE_ID}'"
        ).fetchall()
    }
    report = ApplyReport()
    for v in verdicts:
        vid = int(v["id"])
        verdict = v["verdict"]
        reason = v.get("reason", "")
        existing = by_id.get(vid)
        if existing is None:
            report.skipped_unknown_id.append(vid)
            continue
        if _is_human(existing["reviewer"]):
            if existing["verdict"] == verdict:
                report.human_agreements += 1
            else:
                report.human_disagreements.append(
                    {
                        "id": vid,
                        "human": existing["verdict"],
                        "judge": verdict,
                        "reason": reason,
                    }
                )
            continue
        cx.execute(
            "UPDATE violations SET verdict = ?, verdict_reason = ?,"
            " reviewer = ? WHERE id = ?",
            (verdict, reason or None, judge_reviewer, vid),
        )
        report.written += 1
    return report
