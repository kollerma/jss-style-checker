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
    """Return the set of rule ids to skip. Missing file → empty set."""
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
    "You are a reviewer of static-analysis findings on LaTeX manuscripts "
    "submitted to the Journal of Statistical Software. A finding is either "
    "a true positive (a real style violation the author should fix) or a "
    "false positive (the finding is spurious; the manuscript is compliant "
    "here).\n"
    "Return ONLY a JSON object of shape:\n"
    '  {"verdict": "true_positive" | "false_positive" | "uncertain",\n'
    '   "confidence": 0.0 to 1.0,\n'
    '   "reason": "<one short sentence>"}\n'
    'Use "uncertain" when the surrounding context is insufficient. Your '
    '"confidence" is YOUR self-reported confidence — it is NOT a '
    "probability emitted by a sampler."
)


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
        user_prompt = (
            f"Rule: {violation.get('rule_id')}\n"
            f"Category: {violation.get('category')}\n"
            f"Message: {violation.get('message')}\n\n"
            f"Source context (paper: {violation.get('paper_path','')}):\n"
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
        content = (choices[0].get("message") or {}).get("content", "")
        return _parse_client_response(content)


# -----------------------------------------------------------------------------
# Orchestration
# -----------------------------------------------------------------------------


def _select_unlabelled(
    cx, *, skip_rules: set[str], limit: int | None
) -> list:
    sql = (
        "SELECT v.id, v.rule_id, v.category, v.line, v.column, v.message,"
        " v.severity, p.path AS paper_path"
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
            paper_context = (
                source_snippet(Path(row["paper_path"]), row["line"]) or ""
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
