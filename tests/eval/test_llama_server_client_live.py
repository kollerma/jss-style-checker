"""Live integration test for `LlamaServerClient`.

Marked `@pytest.mark.network` so CI (default: `-m "not network"`)
excludes it. Run explicitly with `pytest -m network` on a machine that
has `llama-server` running on `localhost:8080` with the pinned model.
"""

from __future__ import annotations

import pytest

from eval import api, review


pytestmark = pytest.mark.network


def test_llama_server_round_trip() -> None:
    client = review.LlamaServerClient(
        model="qwen3-30b-a3b",
        base_url="http://localhost:8080",
        timeout=120.0,
    )
    result = client.classify(
        violation={
            "rule_id": "JSS-CITE-001",
            "category": "citation",
            "line": 3,
            "column": 5,
            "message": (
                "\\emph{smith2020} looks like a citation key; use \\cite{...}."
            ),
            "severity": "warning",
            "paper_path": "examples/placeholder_cite_violation",
        },
        paper_context=(
            "\\begin{document}\n"
            "\\section{Introduction}\n"
            "\n"
            "This paper builds on \\emph{smith2020} to establish a method.\n"
        ),
    )
    assert isinstance(result, api.ClassifyResult)
    assert isinstance(result.verdict, api.Verdict)
    assert 0.0 <= result.confidence <= 1.0
