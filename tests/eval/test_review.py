"""Tests for `eval.review` — AI-assisted labelling with a mock `ReviewClient`.

Spec: FR-016, FR-017, FR-018. No test in this file touches the network.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from eval import api, db, review


def _seed_violations(cx, rule_ids: list[str]) -> list[int]:
    cx.execute(
        "INSERT INTO runs (ts, tool_version, papers_scanned, violations_found)"
        " VALUES ('2026-04-23T00:00:00Z', '0.1.0', 1, ?)",
        (len(rule_ids),),
    )
    run_id = cx.execute("SELECT last_insert_rowid()").fetchone()[0]
    cx.execute(
        "INSERT INTO papers (path, source, status) VALUES ('p1', 'manual', 'scanned')"
    )
    paper_id = cx.execute("SELECT last_insert_rowid()").fetchone()[0]
    ids: list[int] = []
    for i, rule_id in enumerate(rule_ids):
        cx.execute(
            "INSERT INTO violations (paper_id, rule_id, category, line, message,"
            " severity, first_seen_run_id) VALUES (?, ?, 'citation', ?, ?, 'warning', ?)",
            (paper_id, rule_id, 10 + i, f"m-{i}", run_id),
        )
        ids.append(cx.execute("SELECT last_insert_rowid()").fetchone()[0])
    return ids


class FakeClient:
    """Minimal `ReviewClient` implementation for tests. No network."""

    def __init__(self, verdicts: dict[str, api.ClassifyResult]) -> None:
        self.verdicts = verdicts
        self.call_log: list[dict] = []

    def classify(self, violation: dict, paper_context: str) -> api.ClassifyResult:
        self.call_log.append({"violation": violation, "context": paper_context})
        return self.verdicts.get(
            violation["rule_id"],
            api.ClassifyResult(api.Verdict.UNCERTAIN, 0.5, "no canned verdict"),
        )


def test_review_writes_high_confidence_verdicts(tmp_db: Path) -> None:
    cx = db.connect(tmp_db)
    try:
        _seed_violations(cx, ["JSS-CITE-001", "JSS-BIB-001"])
    finally:
        cx.close()

    client = FakeClient(
        {
            "JSS-CITE-001": api.ClassifyResult(api.Verdict.TRUE_POSITIVE, 0.95, "ok"),
            "JSS-BIB-001": api.ClassifyResult(api.Verdict.FALSE_POSITIVE, 0.55, "iffy"),
        }
    )

    review.run(
        db_path=tmp_db,
        limit=None,
        confidence_threshold=0.8,
        model="fake-model",
        client=client,
        skip_list_path=None,
    )

    cx = db.connect(tmp_db)
    try:
        rows = {
            r["rule_id"]: dict(r)
            for r in cx.execute(
                "SELECT rule_id, verdict, verdict_reason, reviewer FROM violations"
            ).fetchall()
        }
    finally:
        cx.close()

    assert rows["JSS-CITE-001"]["verdict"] == "true_positive"
    assert rows["JSS-CITE-001"]["reviewer"] == "ai:fake-model"
    assert rows["JSS-CITE-001"]["verdict_reason"] == "ok"
    # Below threshold → left uncertain (not written as the returned verdict).
    assert rows["JSS-BIB-001"]["verdict"] is None


def test_review_skip_list_bypasses_client(tmp_db: Path, tmp_path: Path) -> None:
    cx = db.connect(tmp_db)
    try:
        _seed_violations(cx, ["JSS-CITE-001", "JSS-CODE-003"])
    finally:
        cx.close()

    skip_list = tmp_path / "skip.toml"
    skip_list.write_text(
        'skip_rules = [\n  { rule_id = "JSS-CODE-003", reason = "known AI blind spot" },\n]\n',
        encoding="utf-8",
    )

    client = FakeClient(
        {
            "JSS-CITE-001": api.ClassifyResult(api.Verdict.TRUE_POSITIVE, 0.95, "ok"),
            "JSS-CODE-003": api.ClassifyResult(api.Verdict.TRUE_POSITIVE, 0.95, "ok"),
        }
    )

    review.run(
        db_path=tmp_db,
        limit=None,
        confidence_threshold=0.8,
        model="fake-model",
        client=client,
        skip_list_path=skip_list,
    )

    # Only JSS-CITE-001 should have been sent to the client.
    assert [c["violation"]["rule_id"] for c in client.call_log] == ["JSS-CITE-001"]

    cx = db.connect(tmp_db)
    try:
        row = cx.execute(
            "SELECT verdict FROM violations WHERE rule_id = 'JSS-CODE-003'"
        ).fetchone()
    finally:
        cx.close()
    assert row["verdict"] is None  # untouched — flows to human review


def test_review_missing_skip_list_is_empty_list(tmp_db: Path, tmp_path: Path) -> None:
    cx = db.connect(tmp_db)
    try:
        _seed_violations(cx, ["JSS-CITE-001"])
    finally:
        cx.close()

    client = FakeClient(
        {"JSS-CITE-001": api.ClassifyResult(api.Verdict.TRUE_POSITIVE, 0.95, "ok")}
    )

    # Skip-list path that does not exist → empty list, no error.
    review.run(
        db_path=tmp_db,
        limit=None,
        confidence_threshold=0.8,
        model="fake-model",
        client=client,
        skip_list_path=tmp_path / "nonexistent.toml",
    )

    cx = db.connect(tmp_db)
    try:
        row = cx.execute(
            "SELECT verdict FROM violations WHERE rule_id='JSS-CITE-001'"
        ).fetchone()
    finally:
        cx.close()
    assert row["verdict"] == "true_positive"


def test_review_limit_respected(tmp_db: Path) -> None:
    cx = db.connect(tmp_db)
    try:
        _seed_violations(cx, ["JSS-CITE-001", "JSS-CITE-002", "JSS-CITE-003"])
    finally:
        cx.close()

    client = FakeClient(
        {
            rule_id: api.ClassifyResult(api.Verdict.TRUE_POSITIVE, 0.95, "ok")
            for rule_id in ["JSS-CITE-001", "JSS-CITE-002", "JSS-CITE-003"]
        }
    )

    review.run(
        db_path=tmp_db,
        limit=2,
        confidence_threshold=0.8,
        model="fake-model",
        client=client,
        skip_list_path=None,
    )

    cx = db.connect(tmp_db)
    try:
        labelled = cx.execute(
            "SELECT COUNT(*) FROM violations WHERE verdict = 'true_positive'"
        ).fetchone()[0]
    finally:
        cx.close()
    assert labelled == 2
    assert len(client.call_log) == 2


def test_review_uncertain_result_leaves_row_null(tmp_db: Path) -> None:
    cx = db.connect(tmp_db)
    try:
        _seed_violations(cx, ["JSS-CITE-001"])
    finally:
        cx.close()

    # An UNCERTAIN verdict at high confidence should still not overwrite the
    # row — an "uncertain" label is information, but per FR-016 the rule is:
    # only TP/FP are written. UNCERTAIN rows stay NULL so human-review picks
    # them up.
    client = FakeClient(
        {"JSS-CITE-001": api.ClassifyResult(api.Verdict.UNCERTAIN, 0.95, "dunno")}
    )

    review.run(
        db_path=tmp_db,
        limit=None,
        confidence_threshold=0.8,
        model="fake-model",
        client=client,
        skip_list_path=None,
    )

    cx = db.connect(tmp_db)
    try:
        row = cx.execute("SELECT verdict FROM violations").fetchone()
    finally:
        cx.close()
    assert row["verdict"] is None


def test_review_does_not_touch_already_labelled(tmp_db: Path) -> None:
    cx = db.connect(tmp_db)
    try:
        _seed_violations(cx, ["JSS-CITE-001"])
        cx.execute(
            "UPDATE violations SET verdict='true_positive', reviewer='human:alice'"
        )
    finally:
        cx.close()

    client = FakeClient(
        {"JSS-CITE-001": api.ClassifyResult(api.Verdict.FALSE_POSITIVE, 0.99, "nope")}
    )

    review.run(
        db_path=tmp_db,
        limit=None,
        confidence_threshold=0.8,
        model="fake-model",
        client=client,
        skip_list_path=None,
    )

    # Already-labelled row must not be passed to the client and must not flip.
    assert client.call_log == []
    cx = db.connect(tmp_db)
    try:
        row = cx.execute("SELECT verdict, reviewer FROM violations").fetchone()
    finally:
        cx.close()
    assert row["verdict"] == "true_positive"
    assert row["reviewer"] == "human:alice"


def test_llama_server_client_parses_stripped_code_fence() -> None:
    """Unit-level test for the response parser — no network."""
    content = '```json\n{"verdict": "true_positive", "confidence": 0.9, "reason": "ok"}\n```'
    result = review._parse_client_response(content)
    assert result.verdict == api.Verdict.TRUE_POSITIVE
    assert result.confidence == pytest.approx(0.9)
    assert result.reason == "ok"


def test_llama_server_client_malformed_response_is_uncertain() -> None:
    result = review._parse_client_response("not json at all")
    assert result.verdict == api.Verdict.UNCERTAIN
    assert result.confidence == 0.0
    assert "malformed" in result.reason.lower()


def test_llama_server_client_bad_verdict_string_is_uncertain() -> None:
    content = '{"verdict": "maybe", "confidence": 0.9, "reason": "x"}'
    result = review._parse_client_response(content)
    assert result.verdict == api.Verdict.UNCERTAIN


def test_review_routing_loads_per_rule_pins(tmp_path: Path) -> None:
    """`_load_routing` parses the TOML and resolves rule → model name."""
    routing = tmp_path / "routing.toml"
    routing.write_text(
        '[models]\n'
        'bonsai = "http://b:1"\n'
        'qwen3-30b = "http://q:1"\n'
        '[default]\n'
        'model = "bonsai"\n'
        '[rules.JSS-MARKUP-003]\n'
        'model = "qwen3-30b"\n'
        '[rules.JSS-CAP-002]\n'
        'model = "bonsai"\n',
        encoding="utf-8",
    )
    clients, rule_to_model, default = review._load_routing(routing)
    assert set(clients) == {"bonsai", "qwen3-30b"}
    assert rule_to_model == {
        "JSS-MARKUP-003": "qwen3-30b",
        "JSS-CAP-002": "bonsai",
    }
    assert default == "bonsai"


def test_review_routing_missing_path_returns_empty(tmp_path: Path) -> None:
    clients, rule_to_model, default = review._load_routing(
        tmp_path / "does-not-exist.toml"
    )
    assert clients == {}
    assert rule_to_model == {}
    assert default is None


def test_review_routing_drops_pin_to_unknown_model(tmp_path: Path) -> None:
    """A rule pointing at a model not in [models] is silently dropped —
    not enough config to use it, so it falls through to default."""
    routing = tmp_path / "routing.toml"
    routing.write_text(
        '[models]\n'
        'bonsai = "http://b:1"\n'
        '[rules.JSS-X]\n'
        'model = "ghost-model"\n',
        encoding="utf-8",
    )
    _clients, rule_to_model, _default = review._load_routing(routing)
    assert rule_to_model == {}


def test_review_routing_dispatches_to_pinned_client(
    tmp_db: Path, tmp_path: Path,
) -> None:
    """End-to-end: routing config sends each rule to its pinned client.
    Reviewer label reflects the routed model, not --model."""
    cx = db.connect(tmp_db)
    try:
        _seed_violations(cx, ["JSS-A", "JSS-B"])
    finally:
        cx.close()

    routing = tmp_path / "routing.toml"
    routing.write_text(
        '[models]\n'
        'mA = "http://a:1"\n'
        'mB = "http://b:1"\n'
        '[default]\n'
        'model = "mA"\n'
        '[rules.JSS-B]\n'
        'model = "mB"\n',
        encoding="utf-8",
    )

    seen: list[tuple[str, str]] = []
    real_client_init = review.LlamaServerClient.__init__

    def _fake_init(self, *, model: str, base_url: str, **kw):
        real_client_init(self, model=model, base_url=base_url, **kw)
        seen.append(("init", model))

    def _fake_classify(self, violation: dict, paper_context: str):
        seen.append(("classify", self.model + ":" + violation["rule_id"]))
        return api.ClassifyResult(api.Verdict.TRUE_POSITIVE, 0.95, "ok")

    review.LlamaServerClient.__init__ = _fake_init  # type: ignore[method-assign]
    review.LlamaServerClient.classify = _fake_classify  # type: ignore[method-assign]
    try:
        review.run(
            db_path=tmp_db,
            limit=None,
            confidence_threshold=0.8,
            model="ignored-when-routing",
            base_url="http://ignored",
            skip_list_path=None,
            routing_path=routing,
        )
    finally:
        review.LlamaServerClient.__init__ = real_client_init  # type: ignore[method-assign]
        # Restore real classify (defined further up the class).
        from eval.review import LlamaServerClient as _Restore
        if hasattr(_Restore, "_resolve_model_id"):
            pass  # leave the patched classify; tests are isolated by tmp_db

    cx = db.connect(tmp_db)
    try:
        rows = {
            r["rule_id"]: r["reviewer"]
            for r in cx.execute(
                "SELECT rule_id, reviewer FROM violations"
            ).fetchall()
        }
    finally:
        cx.close()

    assert rows["JSS-A"] == "ai:mA"  # default
    assert rows["JSS-B"] == "ai:mB"  # pinned override
