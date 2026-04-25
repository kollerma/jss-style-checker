"""AI-assisted review (Phase B).

- `ReviewClient` is a Protocol with one method, `classify(...)`. Tests
  use a `FakeClient` (see `tests/eval/test_review.py`). The production
  implementation is `LlamaServerClient` talking to `llama.cpp`'s
  `llama-server` on the OpenAI-compatible `/v1/chat/completions`
  endpoint.
- The orchestration `run(...)` iterates `verdict IS NULL` violations,
  bypasses skip-listed rules, calls the client, and writes back
  `(verdict, verdict_reason, reviewer)` for TP/FP results whose
  self-reported confidence meets the threshold. UNCERTAIN results and
  sub-threshold scores leave the row NULL so it surfaces in
  `human-review`.
- Contract: `specs/002-eval-jss-harness/contracts/review-client.md`.
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from eval import api, db

# -----------------------------------------------------------------------------
# Protocol
# -----------------------------------------------------------------------------


class ReviewClient(Protocol):
    def classify(
        self, violation: dict, paper_context: str
    ) -> api.ClassifyResult: ...


# -----------------------------------------------------------------------------
# Skip-list
# -----------------------------------------------------------------------------


def _load_toml(path: Path) -> dict[str, Any]:
    """Load a TOML file using `tomllib` (3.11+) or `tomli` (3.10) — stdlib only on 3.11+."""
    if sys.version_info >= (3, 11):
        import tomllib

        with path.open("rb") as f:
            return tomllib.load(f)
    # Python 3.10 fallback. `tomli` is a conditional dep in pyproject.toml.
    import tomli  # type: ignore[import-not-found]

    with path.open("rb") as f:
        return tomli.load(f)


def load_skip_list(path: Path | None) -> set[str]:
    """Return the set of rule ids to skip. Missing file → empty set.

    Accepts two formats:
      * ``skip_rules = [...]`` (spec 002 flat list of strings / inline tables).
      * ``[[rules]]`` blocks with ``rule_id`` / ``reason`` / ``added_in_spec``
        fields (spec 004 schema — see
        ``specs/004-jss-rule-modules/contracts/ai-skip-list.md``).
    """
    if path is None or not path.exists():
        return set()
    data = _load_toml(path)
    entries = data.get("skip_rules", []) or []
    out: set[str] = set()
    for entry in entries:
        if isinstance(entry, str):
            out.add(entry)
        elif isinstance(entry, dict) and "rule_id" in entry:
            out.add(str(entry["rule_id"]))
    for rule in data.get("rules", []) or []:
        if isinstance(rule, dict) and "rule_id" in rule:
            out.add(str(rule["rule_id"]))
    return out


# -----------------------------------------------------------------------------
# Response parsing (shared between LlamaServerClient and tests)
# -----------------------------------------------------------------------------


def _parse_client_response(content: str) -> api.ClassifyResult:
    """Parse the model's JSON reply into a `ClassifyResult`.

    Tolerates ```` ```json ```` code-fence wrappers (some models emit
    them even when asked not to) and degrades gracefully on malformed
    output — see `contracts/review-client.md`.
    """
    stripped = content.strip()
    if stripped.startswith("```"):
        # Strip fence markers like ```json ... ``` or ``` ... ```
        lines = stripped.splitlines()
        # Drop opening fence line and the final line if it's a closing fence.
        if lines:
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()

    try:
        payload = json.loads(stripped)
    except json.JSONDecodeError:
        return api.ClassifyResult(
            api.Verdict.UNCERTAIN, 0.0, f"malformed response: {content[:100]!r}"
        )

    if not isinstance(payload, dict):
        return api.ClassifyResult(
            api.Verdict.UNCERTAIN, 0.0, "malformed response: not a JSON object"
        )

    verdict_str = str(payload.get("verdict", "")).lower()
    confidence = payload.get("confidence", 0.0)
    reason = str(payload.get("reason", ""))[:200]

    try:
        confidence_f = float(confidence)
    except (TypeError, ValueError):
        confidence_f = 0.0

    try:
        verdict = api.Verdict(verdict_str)
    except ValueError:
        return api.ClassifyResult(
            api.Verdict.UNCERTAIN,
            confidence_f,
            f"unknown verdict {verdict_str!r}",
        )

    return api.ClassifyResult(verdict, confidence_f, reason)


# -----------------------------------------------------------------------------
# Production client
# -----------------------------------------------------------------------------


_SYSTEM_PROMPT = (
    "You are a reviewer of static-analysis findings on LaTeX/Sweave/"
    "R-Markdown manuscripts submitted to the Journal of Statistical "
    "Software. Each finding is one of:\n"
    "  - true_positive: the manuscript really violates the rule at the "
    "marked location; the author should fix it.\n"
    "  - false_positive: the rule mis-fired; the manuscript is compliant.\n"
    "  - uncertain: the surrounding context is genuinely insufficient.\n"
    "Anchor your judgement on the line marked with '>>' and the column "
    "marked with '^' in the source-context block. Do not describe text "
    "elsewhere in the file unless the rule's logic explicitly requires it.\n"
    "Return ONLY a JSON object of shape:\n"
    '  {"verdict": "true_positive" | "false_positive" | "uncertain",\n'
    '   "confidence": 0.0 to 1.0,\n'
    '   "reason": "<the offending substring or 4-6 words MAX>"}\n'
    "Be terse. The reason MUST be at most 8 words; quote the offending "
    "substring if possible. Do not restate the rule. Do not narrate. "
    'Your "confidence" is YOUR self-reported confidence — NOT a sampler '
    "probability."
)


# Rule-specific clarifications for rules whose pass/fail polarity has
# tripped the model in past runs. Each entry is one or two lines of
# extra guidance appended to the user prompt for that rule.
_RULE_HINTS: dict[str, str] = {
    "JSS-OPER-002": (
        "Rule polarity: TRUE POSITIVE when the manuscript uses '^T', "
        "'^\\prime', or a literal superscript T for transpose. "
        "FALSE POSITIVE when it already uses '\\top'."
    ),
    "JSS-OPER-003": (
        "Rule polarity: TRUE POSITIVE when there IS a blank line "
        "immediately before or after the display equation environment. "
        "An equation body ending in a period is exempt — that's a "
        "FALSE POSITIVE if the rule fires anyway."
    ),
    "JSS-NAME-001": (
        "Rule scope: this fires only on programming-language NAMES "
        "(R, Java, MATLAB, S-PLUS, etc.) and a small list of R-package "
        "spellings (ggplot vs ggplot2). It does NOT fire on capitalisation "
        "of arbitrary identifiers, function names, or English words."
    ),
    "JSS-CITE-002": (
        "Rule scope: per tex-like surface, only the FIRST occurrence of "
        "each \\pkg{X} needs a same-paragraph citation. Subsequent "
        "mentions of the same X are not violations."
    ),
    "JSS-MARKUP-001": (
        "Rule scope: fires on bare programming-language NAMES (R, Java, "
        "Python, MATLAB, S-PLUS, Stan, Julia, C, C++, SAS, Stata, "
        "Fortran) appearing in prose. TRUE POSITIVE: the marked token "
        "is one of those names and is not wrapped in \\proglang{}. "
        "FALSE POSITIVE: it's a filename (foo.R), a math symbol (R^2), "
        "an initial in a name (J. R. Smith), or already inside "
        "\\proglang{}, \\code{}, \\verb, or a section/title macro."
    ),
    "JSS-HOUSE-001": (
        "Rule polarity: TRUE POSITIVE when the marked 'e.g.' or 'i.e.' "
        "is NOT immediately followed by a comma (e.g., 'e.g. apples'). "
        "FALSE POSITIVE when the comma is already present "
        "('e.g., apples')."
    ),
    "JSS-OPER-001": (
        "Rule scope: lowercase-letter-hyphen-{value,statistic,values,"
        "statistics} patterns like 'p-value' or 't-statistic'. TRUE "
        "POSITIVE: marked text contains such a pattern and the symbol "
        "is not already typeset as math (e.g., '$p$~value' is fine)."
    ),
    "JSS-CODE-003": (
        "Rule polarity: TRUE POSITIVE when the marked \\code{...} "
        "content has an operator (=, +, -, *, /) or comma without "
        "surrounding spaces ('a=b', 'foo,bar'). FALSE POSITIVE when "
        "spaces are present, OR the content is a single dotted/"
        "hyphenated identifier ('data.frame', 'Ch-Intro'), OR "
        "scientific notation (1.0e-10, 2.22e-16)."
    ),
    "JSS-ABBR-001": (
        "Rule scope: UPPERCASE multi-letter abbreviations using "
        "internal periods, like 'U.S.A.' or 'U.K.'. TRUE POSITIVE: "
        "the marked text contains such an abbreviation. The fix is "
        "to remove the periods (USA, UK)."
    ),
    "JSS-REFS-005": (
        "Rule scope: a BibTeX `journal` field whose tokens look like "
        "abbreviations ('J.', 'Stat.', 'Softw.', 'Trans.', 'Math.'). "
        "TRUE POSITIVE: the marked entry's `journal =` line contains "
        "such abbreviations. FALSE POSITIVE: the journal name is "
        "fully spelled out."
    ),
    "JSS-REFS-006": (
        "Rule scope: BibTeX title-case loose heuristic. TRUE POSITIVE "
        "when the entry's `title =` field starts with a lowercase word "
        "(or the word after ':' is lowercase) and the lowercase token "
        "is plain English. FALSE POSITIVE: the title starts with a "
        "package name wrapped in \\pkg{...} (e.g. '\\pkg{partykit}: A "
        "Modular Toolkit ...') — package names are intentionally "
        "lowercase. Treat \\pkg{...} as already-correct markup."
    ),
}


def _format_marked_context(
    snippet: str, start_line: int, line: int | None, column: int | None
) -> str:
    """Render the snippet with line numbers; mark the violation line with
    a leading '>>' and underline the column with a '^' caret on the
    next line. Mirrors the human-review TUI's visual cue.
    """
    lines = snippet.splitlines()
    width = max(2, len(str(start_line + len(lines))))
    out: list[str] = []
    for i, text in enumerate(lines):
        n = start_line + i
        prefix = ">>" if n == line else "  "
        out.append(f"{prefix}{n:>{width}}: {text}")
        if n == line and column is not None and column > 0:
            # Caret column: width of the prefix+gutter + (column-1) spaces.
            pad = 2 + width + 2  # prefix + line-no + ": "
            out.append(" " * (pad + column - 1) + "^")
    return "\n".join(out)


@dataclass
class LlamaServerClient:
    """Production `ReviewClient` — speaks OpenAI-style JSON to llama-server.

    Default base URL is `http://localhost:8080`. The `model` string is
    stored in `reviewer = f"ai:{model}"` on labelled rows and sent in the
    request body's `model` field (llama-server ignores the model name
    but client-side we keep it for audit visibility).
    """

    model: str = "qwen3-30b-a3b"
    base_url: str = "http://localhost:8080"
    timeout: float = 60.0

    def classify(
        self, violation: dict, paper_context: str
    ) -> api.ClassifyResult:
        rule_id = violation.get("rule_id", "")
        hint = _RULE_HINTS.get(rule_id, "")
        hint_block = f"\nRule guidance:\n{hint}\n" if hint else ""
        user_prompt = (
            f"Rule: {rule_id}\n"
            f"Category: {violation.get('category')}\n"
            f"Message: {violation.get('message')}\n"
            f"Location: line {violation.get('line')}, "
            f"column {violation.get('column')}\n"
            f"{hint_block}"
            f"\nSource context (paper: {violation.get('paper_path','')}; "
            f"violation line marked '>>', column marked '^'):\n"
            f"---\n{paper_context}\n---\n"
        )
        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.1,
            "top_p": 1.0,
            # Generation is the slow phase; cap output so a chatty model
            # can't bloat latency. A complete JSON like
            # `{"verdict":"true_positive","confidence":0.9,"reason":"`
            # ...8-word quote ...`"}` fits in ~70 tokens.
            "max_tokens": 96,
            "response_format": {"type": "json_object"},
            "stream": False,
        }
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url.rstrip('/')}/v1/chat/completions",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read().decode("utf-8")
        except (urllib.error.URLError, TimeoutError, ConnectionError) as err:
            return api.ClassifyResult(
                api.Verdict.UNCERTAIN, 0.0, f"network: {type(err).__name__}"
            )
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            return api.ClassifyResult(
                api.Verdict.UNCERTAIN, 0.0, "malformed server response"
            )
        choices = payload.get("choices") or []
        if not choices:
            return api.ClassifyResult(
                api.Verdict.UNCERTAIN, 0.0, "empty response"
            )
        message = choices[0].get("message") or {}
        # Reasoning models (Bonsai, DeepSeek-R1, OpenAI o-series) split
        # the chain-of-thought into `reasoning_content` and the final
        # answer into `content`. Bonsai 8B in particular routes the
        # whole JSON object into `reasoning_content` and leaves
        # `content` empty. Fall back to whichever has substance.
        content = message.get("content") or ""
        if not content.strip():
            content = message.get("reasoning_content") or ""
        return _parse_client_response(content)


# -----------------------------------------------------------------------------
# Orchestration
# -----------------------------------------------------------------------------


def _select_unlabelled(
    cx, *, skip_rules: set[str], limit: int | None
) -> list:
    sql = (
        "SELECT v.id, v.rule_id, v.category, v.line, v.column, v.message,"
        " v.severity, v.file, p.path AS paper_path"
        " FROM violations v JOIN papers p ON p.id = v.paper_id"
        " WHERE v.verdict IS NULL"
        " ORDER BY p.path, v.line, v.id"
    )
    rows = cx.execute(sql).fetchall()
    filtered = [r for r in rows if r["rule_id"] not in skip_rules]
    if limit is not None:
        filtered = filtered[:limit]
    return filtered


def _write_verdict(
    cx,
    *,
    violation_id: int,
    verdict: api.Verdict,
    reason: str,
    reviewer: str,
) -> None:
    cx.execute(
        "UPDATE violations SET verdict=?, verdict_reason=?, reviewer=? WHERE id=?",
        (verdict.value, reason or None, reviewer, violation_id),
    )


def run(
    *,
    db_path: Path,
    limit: int | None,
    confidence_threshold: float,
    model: str,
    client: ReviewClient | None = None,
    base_url: str = "http://localhost:8080",
    skip_list_path: Path | None = None,
) -> int:
    """Drive the AI-review loop. Returns the CLI exit code.

    `client` is an injection seam for tests. Production callers leave
    it as `None` and get a `LlamaServerClient` with the given
    `model`/`base_url`.

    Fail-fast on first-call network errors (exit 2). Per-row degradation
    to UNCERTAIN only happens *after* at least one row has round-tripped
    cleanly, so a mis-pointed `--base-url` or a down server surfaces
    immediately instead of silently leaving rows NULL.
    """
    if client is None:
        client = LlamaServerClient(model=model, base_url=base_url)

    skip_rules = load_skip_list(skip_list_path)

    cx = db.connect(db_path)
    try:
        rows = _select_unlabelled(cx, skip_rules=skip_rules, limit=limit)
        if not rows:
            print("eval-jss: no pending violations to review.")
            return 0

        labelled = skipped_low_conf = network_degraded = skipped_uncertain = 0

        # Import lazily so `eval.review` stays importable without pulling
        # `rich` (used by `human_review` for terminal rendering).
        from eval.human_review import source_snippet

        for i, row in enumerate(rows):
            violation_dict = {
                "rule_id": row["rule_id"],
                "category": row["category"],
                "line": row["line"],
                "column": row["column"],
                "message": row["message"],
                "severity": row["severity"],
                "paper_path": row["paper_path"],
            }
            snippet = source_snippet(row["paper_path"], row["file"], row["line"])
            if snippet is None:
                paper_context = ""
            else:
                text, start = snippet
                paper_context = _format_marked_context(
                    text, start, row["line"], row["column"]
                )
            result = client.classify(violation_dict, paper_context=paper_context)

            is_network_failure = (
                result.verdict == api.Verdict.UNCERTAIN
                and result.reason.startswith("network:")
            )

            # Fail-fast: first row can't network to the server → exit 2.
            if i == 0 and is_network_failure:
                print(
                    f"eval-jss: AI review client unreachable on first call: "
                    f"{result.reason}. Check --base-url (currently {base_url}) "
                    f"and that llama-server is bound to an interface reachable "
                    f"from this process.",
                    flush=True,
                )
                return 2

            if is_network_failure:
                network_degraded += 1
                continue

            if result.verdict == api.Verdict.UNCERTAIN:
                skipped_uncertain += 1
                continue
            if result.confidence < confidence_threshold:
                skipped_low_conf += 1
                continue
            _write_verdict(
                cx,
                violation_id=row["id"],
                verdict=result.verdict,
                reason=result.reason,
                reviewer=f"ai:{model}",
            )
            labelled += 1

        print(
            f"eval-jss review: {labelled} labelled, "
            f"{skipped_uncertain} uncertain, "
            f"{skipped_low_conf} below threshold "
            f"(<{confidence_threshold}), "
            f"{network_degraded} network-degraded out of {len(rows)} candidates."
        )
    finally:
        cx.close()

    return 0
