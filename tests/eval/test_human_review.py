"""Tests for `eval.human_review` — scripted Prompt.ask, verdict persistence.

Spec: FR-013, FR-014, FR-015.
"""

from __future__ import annotations

from collections import deque
from pathlib import Path

from eval import db, human_review


def _seed_violations(cx, count: int = 3) -> list[int]:
    cx.execute(
        "INSERT INTO runs (ts, tool_version, papers_scanned, violations_found)"
        " VALUES ('2026-04-23T00:00:00Z', '0.1.0', 1, ?)",
        (count,),
    )
    run_id = cx.execute("SELECT last_insert_rowid()").fetchone()[0]
    cx.execute(
        "INSERT INTO papers (path, source, status) VALUES ('p1', 'manual', 'scanned')"
    )
    paper_id = cx.execute("SELECT last_insert_rowid()").fetchone()[0]
    ids: list[int] = []
    for i in range(count):
        cx.execute(
            "INSERT INTO violations (paper_id, rule_id, category, line, column, message,"
            " severity, first_seen_run_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                paper_id,
                f"JSS-CITE-00{i + 1}",
                "citation",
                10 + i,
                None,
                f"message {i}",
                "warning",
                run_id,
            ),
        )
        ids.append(cx.execute("SELECT last_insert_rowid()").fetchone()[0])
    return ids


def _script_prompts(monkeypatch, answers: list[str]) -> list[str]:
    """Make the verdict and reason prompts return answers from `answers`
    in order. Both helpers share one queue so tests script answers as a
    flat list (verdict, optional reason, verdict, …).

    Returns the list itself so tests can check consumption.
    """
    queue = deque(answers)

    def _fake(*args, **kwargs):
        if not queue:
            return "q"
        return queue.popleft()

    monkeypatch.setattr(human_review, "_ask_verdict", _fake)
    monkeypatch.setattr(human_review, "_ask_reason", _fake)
    return list(queue)


def test_human_review_maps_tfu_verdicts(monkeypatch, tmp_db: Path) -> None:
    cx = db.connect(tmp_db)
    try:
        _seed_violations(cx, count=3)
    finally:
        cx.close()

    _script_prompts(monkeypatch, ["t", "", "f", "because", "u", "", "q"])

    code = human_review.run(db_path=tmp_db, limit=None, rule_id=None, reviewer="human:tester")
    assert code == 0

    cx = db.connect(tmp_db)
    try:
        rows = cx.execute(
            "SELECT rule_id, verdict, verdict_reason, reviewer FROM violations ORDER BY rule_id"
        ).fetchall()
        assert [r["verdict"] for r in rows] == ["true_positive", "false_positive", "uncertain"]
        assert rows[1]["verdict_reason"] == "because"
        assert all(r["reviewer"] == "human:tester" for r in rows)
    finally:
        cx.close()


def test_human_review_skip_leaves_row_unchanged(monkeypatch, tmp_db: Path) -> None:
    cx = db.connect(tmp_db)
    try:
        _seed_violations(cx, count=1)
    finally:
        cx.close()

    _script_prompts(monkeypatch, ["s", "q"])

    human_review.run(db_path=tmp_db, limit=None, rule_id=None, reviewer="human:tester")

    cx = db.connect(tmp_db)
    try:
        row = cx.execute("SELECT verdict, reviewer FROM violations").fetchone()
        assert row["verdict"] is None
        assert row["reviewer"] is None
    finally:
        cx.close()


def test_human_review_quit_stops_loop(monkeypatch, tmp_db: Path) -> None:
    cx = db.connect(tmp_db)
    try:
        _seed_violations(cx, count=3)
    finally:
        cx.close()

    _script_prompts(monkeypatch, ["t", "", "q"])

    human_review.run(db_path=tmp_db, limit=None, rule_id=None, reviewer="human:tester")

    cx = db.connect(tmp_db)
    try:
        labelled = cx.execute(
            "SELECT COUNT(*) FROM violations WHERE verdict IS NOT NULL"
        ).fetchone()[0]
        assert labelled == 1
    finally:
        cx.close()


def test_human_review_limit_respected(monkeypatch, tmp_db: Path) -> None:
    cx = db.connect(tmp_db)
    try:
        _seed_violations(cx, count=5)
    finally:
        cx.close()

    _script_prompts(monkeypatch, ["t", "", "t", "", "q"])

    human_review.run(db_path=tmp_db, limit=2, rule_id=None, reviewer="human:tester")

    cx = db.connect(tmp_db)
    try:
        labelled = cx.execute(
            "SELECT COUNT(*) FROM violations WHERE verdict IS NOT NULL"
        ).fetchone()[0]
        assert labelled == 2
    finally:
        cx.close()


def test_human_review_rule_filter(monkeypatch, tmp_db: Path) -> None:
    cx = db.connect(tmp_db)
    try:
        _seed_violations(cx, count=3)
    finally:
        cx.close()

    _script_prompts(monkeypatch, ["t", "", "q"])

    human_review.run(
        db_path=tmp_db, limit=None, rule_id="JSS-CITE-002", reviewer="human:tester"
    )

    cx = db.connect(tmp_db)
    try:
        row = cx.execute(
            "SELECT verdict FROM violations WHERE rule_id='JSS-CITE-002'"
        ).fetchone()
        assert row["verdict"] == "true_positive"
        # Other rules untouched
        others = cx.execute(
            "SELECT COUNT(*) FROM violations WHERE verdict IS NOT NULL"
        ).fetchone()[0]
        assert others == 1
    finally:
        cx.close()


def test_human_review_back_undoes_previous_verdict(monkeypatch, tmp_db: Path) -> None:
    cx = db.connect(tmp_db)
    try:
        _seed_violations(cx, count=2)
    finally:
        cx.close()

    # Label first as true, then press 'b' to undo, then re-label as false.
    # Prompts: t, reason, b, f, reason, q
    _script_prompts(monkeypatch, ["t", "", "b", "f", "", "q"])

    human_review.run(db_path=tmp_db, limit=None, rule_id=None, reviewer="human:tester")

    cx = db.connect(tmp_db)
    try:
        rows = cx.execute(
            "SELECT rule_id, verdict FROM violations ORDER BY rule_id"
        ).fetchall()
        # The first violation (JSS-CITE-001) was labelled t, undone, then f.
        # The second (JSS-CITE-002) is still NULL because the session quit
        # before reaching it on the second pass — actually reprompt of idx 0
        # then advances to idx 1 which sees 'q'. So CITE-002 is untouched.
        assert rows[0]["verdict"] == "false_positive"
        assert rows[1]["verdict"] is None
    finally:
        cx.close()


def test_human_review_back_at_start_is_noop(monkeypatch, tmp_db: Path) -> None:
    cx = db.connect(tmp_db)
    try:
        _seed_violations(cx, count=1)
    finally:
        cx.close()

    # Press b on the very first prompt (nothing to undo), then label t.
    _script_prompts(monkeypatch, ["b", "t", "", "q"])

    human_review.run(db_path=tmp_db, limit=None, rule_id=None, reviewer="human:tester")

    cx = db.connect(tmp_db)
    try:
        row = cx.execute("SELECT verdict FROM violations").fetchone()
        assert row["verdict"] == "true_positive"
    finally:
        cx.close()


def test_locator_uses_file_column_when_present(tmp_path: Path) -> None:
    paper = tmp_path / "paperA"
    (paper / "pkg" / "vignettes").mkdir(parents=True)
    (paper / "pkg" / "vignettes" / "intro.Rmd").write_text("x\n", encoding="utf-8")
    # When the violation row carries a file path, the locator points at the
    # paper-relative file with line:col appended (VS-Code-style).
    loc = human_review._locator(str(paper), "pkg/vignettes/intro.Rmd", 42, 7)
    assert loc.endswith("pkg/vignettes/intro.Rmd:42:7")


def test_locator_line_only_when_column_missing(tmp_path: Path) -> None:
    paper = tmp_path / "paperB"
    paper.mkdir()
    (paper / "article.tex").write_text("x\n", encoding="utf-8")
    # Legacy path: no `file` column (pre-P8 row) but a top-level .tex exists.
    loc = human_review._locator(str(paper), None, 42, None)
    assert loc.endswith("article.tex:42")


def test_locator_falls_back_to_dir_without_tex(tmp_path: Path) -> None:
    empty = tmp_path / "empty"
    empty.mkdir()
    loc = human_review._locator(str(empty), None, 42, 7)
    # No `file` column and no top-level .tex → locator points at the dir.
    assert loc.endswith("empty:42:7")


def test_float_span_only_returned_when_line_inside_block() -> None:
    # Manual figure reference at line 8 sits AFTER a closed figure block
    # at lines 1-3. The earlier float doesn't enclose line 8, so the
    # span helper must not return its bounds.
    lines = [
        r"\begin{figure}",                         # 1
        r"\caption{first plot}",                   # 2
        r"\end{figure}",                           # 3
        r"",                                       # 4
        r"Some prose text leading up to a figure", # 5
        r"reference. We refer to it manually:",    # 6
        r"",                                       # 7
        r"See Figure 1b for further detail.",      # 8 — violation
    ]
    assert human_review._float_or_caption_span(lines, 8) is None


def test_float_span_returned_when_line_inside_block() -> None:
    lines = [
        r"\begin{figure}",                # 1
        r"\includegraphics{x}",           # 2 — violation here
        r"\caption{Plot}",                # 3
        r"\end{figure}",                  # 4
        r"Some prose after.",             # 5
    ]
    span = human_review._float_or_caption_span(lines, 2)
    assert span == (1, 4)


def test_display_eq_span_returns_full_block_with_padding() -> None:
    # JSS-OPER-003 fires at line 4 (`\begin{eqnarray*}`); the reviewer
    # needs the complete eqnarray plus a couple of lines on each side
    # to judge whether the surrounding paragraph spacing is correct.
    lines = [
        r"prose line 1",                 # 1
        r"prose line 2",                 # 2
        r"",                             # 3
        r"\begin{eqnarray*}",            # 4 — violation
        r"a &=& b",                      # 5
        r"&=& c",                        # 6
        r"\end{eqnarray*}",              # 7
        r"prose line 8",                 # 8
        r"prose line 9",                 # 9
    ]
    span = human_review._display_eq_span(lines, 4)
    assert span == (2, 9)


def test_display_eq_span_when_line_inside_body() -> None:
    # Violation reported in the middle of the eqnarray body; the helper
    # should still grab the whole block plus padding.
    lines = [
        r"prose",                        # 1
        r"\begin{eqnarray*}",            # 2
        r"a &=& b\\",                    # 3 — violation here
        r"&=& c",                        # 4
        r"\end{eqnarray*}",              # 5
        r"prose",                        # 6
    ]
    span = human_review._display_eq_span(lines, 3)
    assert span == (1, 6)


def test_author_block_span_for_struct_005() -> None:
    # \author{} can span many lines; STRUCT-005 fires at the macro
    # line, but the reviewer needs the full block to verify whether
    # \and / \And / \AND is used.
    lines = [
        r"\title{Demo}",                               # 1
        r"\author{",                                   # 2 — violation
        r"  Alice Smith \and",                         # 3
        r"  Bob Jones \And",                           # 4
        r"  Carol Patel\\ MIT",                        # 5
        r"}",                                          # 6
        r"\Plainauthor{Alice Smith, Bob Jones, Carol Patel}",  # 7
    ]
    span = human_review._macro_block_span(
        lines, 2, human_review._AUTHOR_MACRO_RE
    )
    assert span == (2, 6)


def test_macro_block_span_returns_none_when_line_outside() -> None:
    lines = [
        r"\author{Alice Smith}",   # 1
        r"",                       # 2
        r"prose at line 3",        # 3
    ]
    assert human_review._macro_block_span(
        lines, 3, human_review._AUTHOR_MACRO_RE
    ) is None


def test_display_eq_span_returns_none_outside_block() -> None:
    lines = [
        r"\begin{eqnarray*}",   # 1
        r"a=b",                 # 2
        r"\end{eqnarray*}",     # 3
        r"",                    # 4
        r"prose at line 5",     # 5
    ]
    assert human_review._display_eq_span(lines, 5) is None


def test_source_snippet_xref_004_uses_display_eq_span(tmp_path: Path) -> None:
    rnw = tmp_path / "x.Rnw"
    rnw.write_text(
        "prose 1\n"
        "prose 2\n"
        r"\begin{equation}" "\n"
        r"  a^2 + b^2 = c^2" "\n"
        r"\end{equation}" "\n"
        "prose 6\n"
        "prose 7\n",
        encoding="utf-8",
    )
    # XREF-004 fires on the env's opening line (line 3 here). Reviewer
    # gets the full block plus 2 lines on each side.
    result = human_review.source_snippet(
        str(tmp_path), "x.Rnw", 3, rule_id="JSS-XREF-004",
    )
    assert result is not None
    text, start = result
    assert start == 1
    assert r"\begin{equation}" in text
    assert r"\end{equation}" in text
    assert "prose 1" in text  # padding before
    assert "prose 7" in text  # padding after


def test_caption_span_only_returned_when_line_inside_caption() -> None:
    lines = [
        r"\caption{One short caption.}",   # 1
        r"",                               # 2
        r"Prose.",                         # 3
        r"More prose at line 4.",          # 4 — violation outside
    ]
    assert human_review._float_or_caption_span(lines, 4) is None


def test_human_review_reviewer_defaults_to_env(monkeypatch, tmp_db: Path) -> None:
    cx = db.connect(tmp_db)
    try:
        _seed_violations(cx, count=1)
    finally:
        cx.close()

    monkeypatch.setenv("USER", "envuser")
    _script_prompts(monkeypatch, ["f", "", "q"])

    human_review.run(db_path=tmp_db, limit=None, rule_id=None, reviewer=None)

    cx = db.connect(tmp_db)
    try:
        row = cx.execute("SELECT reviewer FROM violations").fetchone()
        assert row["reviewer"] == "human:envuser"
    finally:
        cx.close()


def test_select_violations_excludes_stale_rows(tmp_db) -> None:
    """human-review queue likewise drops violations the tool no longer
    emits (stale last_seen_run_id)."""
    from eval import db, human_review
    cx = db.connect(tmp_db)
    try:
        for _ in range(2):
            cx.execute(
                "INSERT INTO runs (ts, tool_version, papers_scanned, violations_found)"
                " VALUES ('2026-04-23T00:00:00Z', '0.1.0', 1, 1)")
        cx.execute("INSERT INTO papers (path, source, status)"
                   " VALUES ('p', 'manual', 'scanned')")
        pid = cx.execute("SELECT last_insert_rowid()").fetchone()[0]
        runs = [r[0] for r in cx.execute("SELECT id FROM runs ORDER BY id")]
        cx.execute(
            "INSERT INTO violations (paper_id, rule_id, category, line, message,"
            " severity, first_seen_run_id, last_seen_run_id)"
            " VALUES (?, 'JSS-A', 'x', 1, 'cur', 'warning', ?, ?)",
            (pid, runs[0], runs[1]))
        cx.execute(
            "INSERT INTO violations (paper_id, rule_id, category, line, message,"
            " severity, first_seen_run_id, last_seen_run_id)"
            " VALUES (?, 'JSS-B', 'x', 2, 'stale', 'warning', ?, ?)",
            (pid, runs[0], runs[0]))
        cx.commit()
        rows = human_review._select_violations(cx, rule_ids=None, limit=None)
        msgs = {r["message"] for r in rows}
        assert "cur" in msgs and "stale" not in msgs
    finally:
        cx.close()
