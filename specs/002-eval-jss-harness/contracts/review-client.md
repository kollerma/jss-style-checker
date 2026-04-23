# Contract — `ReviewClient`

The AI review subsystem is behind a single Protocol. Production uses `LlamaServerClient`; tests use `FakeClient`. No other implementation ships.

## Protocol

```python
from typing import Protocol

class ReviewClient(Protocol):
    def classify(
        self,
        violation: dict,
        paper_context: str,
    ) -> "ClassifyResult":
        ...
```

Where:

```python
from dataclasses import dataclass
from .api import Verdict

@dataclass(frozen=True)
class ClassifyResult:
    verdict: Verdict           # TRUE_POSITIVE | FALSE_POSITIVE | UNCERTAIN
    confidence: float          # 0.0..1.0 — model self-reported, NOT a calibrated probability
    reason: str                # short human-readable justification, <=200 chars
```

`violation` is a dict with at least the fields `{rule_id, category, line, column, message, severity}` drawn from the `violations` row. `paper_context` is a short excerpt of the paper source around the violation line — identical snippet shape to what `human-review` shows (±3 lines, line-numbered, syntax-highlighted stripped back to plain text for the prompt).

Implementations MUST NOT raise on transient errors (bad JSON, HTTP 5xx, timeout) — they MUST return `ClassifyResult(UNCERTAIN, 0.0, "<error description>")` instead, so the caller's loop is never blocked by a flaky server.

Implementations MAY raise on configuration errors (unreachable server at the very first call, unreadable skip-list). These trip `review.py`'s fail-fast guard and bubble up to exit code 2.

## `LlamaServerClient` — production

```python
class LlamaServerClient:
    def __init__(
        self,
        *,
        model: str = "qwen3-30b-a3b",
        base_url: str = "http://localhost:8080",
        timeout: float = 60.0,
    ) -> None: ...
```

### HTTP request

`POST {base_url}/v1/chat/completions` with `Content-Type: application/json` and body:

```json
{
  "model": "qwen3-30b-a3b",
  "messages": [
    {"role": "system", "content": "<SYSTEM PROMPT — below>"},
    {"role": "user",   "content": "<USER PROMPT — below>"}
  ],
  "temperature": 0.1,
  "top_p": 1.0,
  "response_format": {"type": "json_object"},
  "stream": false
}
```

### System prompt (verbatim)

```
You are a reviewer of static-analysis findings on LaTeX manuscripts
submitted to the Journal of Statistical Software. A finding is either a
true positive (a real style violation the author should fix) or a false
positive (the finding is spurious; the manuscript is compliant here).
Return ONLY a JSON object of shape:
  {"verdict": "true_positive" | "false_positive" | "uncertain",
   "confidence": 0.0 to 1.0,
   "reason": "<one short sentence>"}
Use "uncertain" when the surrounding context is insufficient. Your
"confidence" is YOUR self-reported confidence — it is NOT a probability
emitted by a sampler.
```

### User prompt shape

```
Rule: {rule_id}
Category: {category}
Message: {message}

Source context (paper: {paper_title}):
---
{paper_context}
---
```

### Response parsing

`response["choices"][0]["message"]["content"]` is expected to be a JSON object. Parse with `json.loads`. If the content is wrapped in ```` ```json ```` code fences (some models do this even when asked not to), strip the fences. If parsing still fails, return `ClassifyResult(UNCERTAIN, 0.0, f"malformed response: {content[:100]}")`.

If `response` has no `choices` key or the key is empty, return `ClassifyResult(UNCERTAIN, 0.0, "empty response")`.

### Transport

Stdlib only:

```python
req = urllib.request.Request(
    f"{base_url}/v1/chat/completions",
    data=json.dumps(body).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=timeout) as r:
    return json.loads(r.read().decode("utf-8"))
```

Network errors (`urllib.error.URLError`, `socket.timeout`, `ConnectionRefusedError`) → on first call, raise (exit 2). On subsequent calls in the same invocation, return `ClassifyResult(UNCERTAIN, 0.0, f"network: {type(e).__name__}")`.

## `FakeClient` — tests

```python
class FakeClient:
    def __init__(self, verdicts: dict[str, ClassifyResult]) -> None:
        self.verdicts = verdicts
        self.call_log: list[dict] = []

    def classify(self, violation: dict, paper_context: str) -> ClassifyResult:
        self.call_log.append({"violation": violation, "context": paper_context})
        return self.verdicts.get(
            violation["rule_id"],
            ClassifyResult(Verdict.UNCERTAIN, 0.5, "no canned verdict"),
        )
```

Per-rule-id canned verdicts. `call_log` lets tests assert what was sent. No network, no subprocess.

## Confidence contract

The `--confidence-threshold F` flag (default `0.8`) gates whether `review.py` writes the model's `verdict` to the row:

- `confidence >= F` → write `verdict`, `verdict_reason = reason`, `reviewer = f"ai:{model}"`.
- `confidence < F`  → leave `verdict = NULL` (the row surfaces in `human-review`), record nothing.

The "confidence" is the **model's self-report**, not a sampler probability. Under `llama-server` + `top-k=1` the sampler's confidence is degenerate (always ~1.0 on the argmax token), so reliance on a sampler-derived probability would be misleading. `contracts/cli.md` and the `--help` text for `--confidence-threshold` both state this explicitly.

## Skip-list contract

`eval/review-skip-list.toml` format:

```toml
skip_rules = [
    { rule_id = "JSS-FOO-123", reason = "<why this rule is skipped>" },
    # ...
]
```

`review.py` loads it with `tomllib` / `tomli`. A violation whose `rule_id` is in the list bypasses `classify()` entirely; the row is left `uncertain` for `human-review` to pick up. Missing file → empty list.
