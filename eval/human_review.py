"""Interactive TUI for labelling violations.

Iterates violations where `verdict IS NULL OR verdict = 'uncertain'`,
shows each with a ±3-line source snippet, and prompts the reviewer for
a verdict via `rich.prompt.Prompt.ask`.

Every verdict commits immediately so a `Ctrl-C` mid-session loses at
most the violation currently on screen (spec FR-015). A `b` (back)
action re-opens the previously-decided violation; its prior state is
restored in the DB so the history stack is consistent with on-disk
state.
"""

from __future__ import annotations

import os
import re
import textwrap
from pathlib import Path

# Loading `readline` is what gives `input()` (and therefore rich's
# Prompt.ask) left/right cursor editing and up/down history recall —
# nothing else here references the module. The import-only side effect
# is intentional. Wrapped in a guard so non-readline platforms still
# import cleanly.
try:  # pragma: no cover - import side effect
    import readline  # noqa: F401
except ImportError:  # pragma: no cover
    pass

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from eval import db

_CHOICES = ["t", "f", "u", "s", "n", "b", "q"]
_VERDICT = {
    "t": "true_positive",
    "f": "false_positive",
    "u": "uncertain",
}

_LEGEND = (
    "Verdicts: [bold green]t[/] true positive  ·  "
    "[bold red]f[/] false positive  ·  "
    "[yellow]u[/] uncertain (re-surfaces later)  ·  "
    "[dim]s[/] skip (no change)  ·  "
    "[magenta]n[/] next rule type  ·  "
    "[cyan]b[/] back (undo previous)  ·  "
    "[bold]q[/] quit"
)


def _resolve_reviewer(reviewer: str | None) -> str:
    if reviewer:
        return reviewer
    user = os.environ.get("USER", "unknown")
    return f"human:{user}"


def _first_tex_file(paper_path: Path) -> Path | None:
    """Legacy fallback — used only when `violations.file` is NULL
    (pre-P8 rows) and no better source pointer is available.
    """
    if not paper_path.exists() or not paper_path.is_dir():
        return None
    tex_files = sorted(paper_path.glob("*.tex"))
    return tex_files[0] if tex_files else None


def _resolve_source(paper_path: str, file: str | None) -> Path | None:
    """Return the absolute path of the violation's source file.

    Prefers `violations.file` (paper-relative POSIX path captured at scan
    time). Falls back to the legacy "first .tex at the paper root"
    behaviour when `file` is NULL.
    """
    paper_dir = Path(paper_path)
    if file:
        return paper_dir / file
    return _first_tex_file(paper_dir)


_LEXER_BY_SUFFIX = {
    ".tex": "latex",
    ".ltx": "latex",
    ".Rnw": "latex",
    ".Rmd": "markdown",
    ".bib": "bibtex",
}

# Rules whose verdict depends on the full caption / float block, not just a
# few lines around the violation. Long captions wrap across many source lines,
# so the default ±3-line window often hides the period, the emphasis macro,
# the label, or the begin/end float boundary that the rule actually targets.
_FLOAT_CONTEXT_RULES = {
    "JSS-CAP-003",   # caption sentence style
    "JSS-TYPO-001",  # caption ends with period
    "JSS-TYPO-002",  # caption emphasis macros
    "JSS-TYPO-003",  # tables footnote-style annotations
    "JSS-TYPO-004",  # \caption{} placement before/after content
    "JSS-XREF-001",  # \label{} on figures/tables
}

_FLOAT_BEGIN_RE = re.compile(r"\\begin\{(?:figure|table)\*?\}")
_FLOAT_END_RE = re.compile(r"\\end\{(?:figure|table)\*?\}")
_CAPTION_RE = re.compile(r"\\caption\b")

# Display-math envs that JSS-OPER-003 walks. Mirrors
# `texlint.journals.jss.rules.operators._DISPLAY_EQ_ENVS`.
_DISPLAY_EQ_BEGIN_RE = re.compile(
    r"\\begin\{(?:equation|equation\*|align|align\*|eqnarray|eqnarray\*|"
    r"gather|gather\*|multline|multline\*)\}"
)
_DISPLAY_EQ_END_RE = re.compile(
    r"\\end\{(?:equation|equation\*|align|align\*|eqnarray|eqnarray\*|"
    r"gather|gather\*|multline|multline\*)\}"
)


def _display_eq_span(
    lines: list[str], line: int, *, padding: int = 2
) -> tuple[int, int] | None:
    """Locate the display-math env enclosing (or starting at) ``line``
    and return ``(begin_line - padding, end_line + padding)`` so the
    reviewer sees the complete equation plus a couple of lines on
    either side. Used by:

    - JSS-OPER-003 — fires on the env's opening line; judgement
      requires seeing whether the lines immediately before/after
      are blank.
    - JSS-XREF-004 — fires on numbered equation envs that lack
      ``\\label{}``; the reviewer needs to inspect the whole body
      to verify there's no label hidden inside.
    """
    n = len(lines)
    if line < 1 or line > n:
        return None
    # Search backwards for the enclosing \begin{...}.
    begin = None
    for i in range(line - 1, -1, -1):
        if _DISPLAY_EQ_BEGIN_RE.search(lines[i]):
            begin = i
            break
    if begin is None:
        return None
    # Forward to the matching \end{...}.
    end = None
    for j in range(begin, n):
        if _DISPLAY_EQ_END_RE.search(lines[j]):
            end = j
            break
    if end is None or not (begin <= line - 1 <= end):
        return None
    return (max(1, begin + 1 - padding), min(n, end + 1 + padding))


_AUTHOR_MACRO_RE = re.compile(r"\\author\b")


def _macro_block_span(
    lines: list[str], line: int, macro_re: re.Pattern[str]
) -> tuple[int, int] | None:
    """Locate a multi-line ``\\<macro>{...}`` block whose opening line
    is at or before ``line`` and whose matching close brace is at or
    after ``line``. Returns 1-based ``(start, end)`` inclusive.

    Used for JSS-STRUCT-005 (full ``\\author{}``) — a reviewer
    judging whether the author list correctly uses ``\\And``/``\\AND``
    instead of lowercase ``\\and`` needs to see the entire
    multi-author block, which can span 10+ lines for collaborative
    papers.
    """
    n = len(lines)
    if line < 1 or line > n:
        return None
    macro_start = None
    for i in range(line - 1, -1, -1):
        if macro_re.search(lines[i]):
            macro_start = i
            break
    if macro_start is None:
        return None
    # Walk forward, balancing braces from the macro line.
    depth = 0
    seen_open = False
    for j in range(macro_start, n):
        for ch in lines[j]:
            if ch == "{":
                depth += 1
                seen_open = True
            elif ch == "}":
                depth -= 1
                if seen_open and depth == 0:
                    if macro_start + 1 <= line <= j + 1:
                        return (macro_start + 1, j + 1)
                    return None
    return None


def _float_or_caption_span(
    lines: list[str], line: int
) -> tuple[int, int] | None:
    """Locate the enclosing `\\begin{figure|table}…\\end{…}` block, or
    failing that the enclosing `\\caption{…}` block, around `line`
    (1-based). Returns `(start, end)` 1-based inclusive, or `None`
    when ``line`` doesn't sit inside any such block. The span MUST
    contain ``line``: a manual figure reference at line N may sit
    after a closed figure block (begin..end < N) — in that case the
    rule's reviewer should see the prose context, not the unrelated
    earlier figure.
    """
    n = len(lines)
    if line < 1 or line > n:
        return None

    # Prefer the full float environment when one encloses the line.
    for i in range(line - 1, -1, -1):
        if _FLOAT_BEGIN_RE.search(lines[i]):
            for j in range(i, n):
                if _FLOAT_END_RE.search(lines[j]):
                    if i + 1 <= line <= j + 1:
                        return (i + 1, j + 1)
                    # The matched float closed before `line` — keep
                    # looking for an enclosing caption block, but
                    # don't return this orphan span.
                    break
            break

    # Fall back to the \caption{...} block — track brace depth forward
    # from the \caption line to find the matching close brace.
    cap_start: int | None = None
    for i in range(line - 1, -1, -1):
        if _CAPTION_RE.search(lines[i]):
            cap_start = i
            break
    if cap_start is None:
        return None
    depth = 0
    seen_open = False
    for j in range(cap_start, n):
        for ch in lines[j]:
            if ch == "{":
                depth += 1
                seen_open = True
            elif ch == "}":
                depth -= 1
                if seen_open and depth == 0:
                    if cap_start + 1 <= line <= j + 1:
                        return (cap_start + 1, j + 1)
                    return None
    return None


def _bib_entry_span(lines: list[str], line: int) -> tuple[int, int] | None:
    """Locate the `@type{...}` BibTeX entry enclosing line `line` (1-based).

    Scans backwards for an entry header (`@<word>{` or `@<word>(`), then
    forward with brace-depth tracking until the matching close. Returns
    `(start, end)` 1-based inclusive, or `None` when the entry can't be
    located (e.g., the line is whitespace between entries, or the file
    is malformed).
    """
    header_re = __import__("re").compile(r"^\s*@[A-Za-z]+\s*[{(]")

    start_idx: int | None = None
    for i in range(line - 1, -1, -1):
        if i >= len(lines):
            continue
        if header_re.match(lines[i]):
            start_idx = i
            break
    if start_idx is None:
        return None

    depth = 0
    for j in range(start_idx, len(lines)):
        for ch in lines[j]:
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return (start_idx + 1, j + 1)
    return None


def source_snippet(
    paper_path: str,
    file: str | None,
    line: int | None,
    window: int = 3,
    *,
    rule_id: str | None = None,
) -> tuple[str, int] | None:
    """Return `(text, start_line)` for a source context around `line`.

    For `.bib` files, the snippet is the full enclosing `@entry{...}`
    block — individual field values (`journal`, `year`, `publisher`)
    often sit many lines from the entry header and the fixed ±window
    truncates the relevant frame.

    For caption / figure / table rules in LaTeX-flavoured sources, the
    snippet is the full enclosing `\\begin{figure|table}…\\end{…}` (or
    `\\caption{…}` block as a fallback) so the reviewer can see the
    whole caption rather than a 3-line window into the middle of it.

    For every other suffix, the snippet is the usual ±`window` slice.
    Returns `None` when no source can be read for the violation.
    """
    src = _resolve_source(paper_path, file)
    if src is None or line is None:
        return None
    try:
        text = src.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    lines = text.splitlines()
    if not lines:
        return None

    if src.suffix == ".bib":
        span = _bib_entry_span(lines, line)
        if span is not None:
            start, end = span
            return "\n".join(lines[start - 1 : end]), start

    if (
        rule_id in _FLOAT_CONTEXT_RULES
        and src.suffix in {".tex", ".ltx", ".Rnw", ".Rmd"}
    ):
        span = _float_or_caption_span(lines, line)
        if span is not None:
            start, end = span
            return "\n".join(lines[start - 1 : end]), start

    if (
        rule_id in {"JSS-OPER-003", "JSS-XREF-004"}
        and src.suffix in {".tex", ".ltx", ".Rnw", ".Rmd"}
    ):
        span = _display_eq_span(lines, line)
        if span is not None:
            start, end = span
            return "\n".join(lines[start - 1 : end]), start

    if (
        rule_id == "JSS-STRUCT-005"
        and src.suffix in {".tex", ".ltx", ".Rnw", ".Rmd"}
    ):
        span = _macro_block_span(lines, line, _AUTHOR_MACRO_RE)
        if span is not None:
            start, end = span
            return "\n".join(lines[start - 1 : end]), start

    start = max(1, line - window)
    end = min(len(lines), line + window)
    return "\n".join(lines[start - 1 : end]), start


def _locator(
    paper_path: str, file: str | None, line: int | None, column: int | None
) -> str:
    """Return a VS-Code-clickable ``path:line:col`` string, relative to CWD
    when possible.
    """
    src = _resolve_source(paper_path, file)
    target = src if src is not None else Path(paper_path)
    try:
        display = str(target.resolve().relative_to(Path.cwd()))
    except ValueError:
        display = str(target)
    if line is None:
        return display
    if column is None:
        return f"{display}:{line}"
    return f"{display}:{line}:{column}"


def _lexer_for(file: str | None, paper_path: str) -> str:
    """Pick a Pygments lexer by file suffix. Default: latex."""
    if file:
        suffix = Path(file).suffix
    else:
        src = _resolve_source(paper_path, None)
        suffix = src.suffix if src else ".tex"
    return _LEXER_BY_SUFFIX.get(suffix, "latex")


def _ask_verdict() -> str:
    """Read a verdict character. Re-asks until the answer is in `_CHOICES`.

    Uses plain `input()` (not rich's Prompt) so the prompt is passed to
    readline directly — that way left/right editing works without
    overwriting the prompt prefix on redraw. Up/down history is
    suppressed here by snapshotting + clearing readline history before
    the prompt and restoring afterwards: the reviewer should only cycle
    through prior reasons at the reason prompt, not at the verdict
    prompt where reasons aren't valid answers anyway.
    """
    try:
        import readline as _rl
    except ImportError:
        _rl = None  # type: ignore[assignment]

    saved: list[str] = []
    if _rl is not None:
        for i in range(1, _rl.get_current_history_length() + 1):
            item = _rl.get_history_item(i)
            if item is not None:
                saved.append(item)
        _rl.clear_history()

    try:
        while True:
            try:
                raw = input("Verdict [t/f/u/s/n/b/q] (u): ")
            except (EOFError, KeyboardInterrupt):
                print()
                return "q"
            answer = raw.strip().lower() or "u"
            if answer in _CHOICES:
                return answer
            print(f"Please pick one of: {', '.join(_CHOICES)}")
    finally:
        if _rl is not None:
            _rl.clear_history()
            for item in saved:
                _rl.add_history(item)


def _ask_reason() -> str:
    """Read an optional free-text reason. Reasons stay in readline
    history so the reviewer can up-arrow to recall a previous reason.
    """
    try:
        return input("Reason (optional): ")
    except (EOFError, KeyboardInterrupt):
        print()
        return ""


def _wrapped_caret_position(
    source_line: str, column: int, content_width: int
) -> tuple[int, int] | None:
    """Map a 1-based source column to (wrap_row, col_in_row) under the
    same wrapping rich uses for `Syntax(word_wrap=True)`.

    Empirically, rich's wrap matches `textwrap.wrap(..., drop_whitespace=True,
    break_long_words=True, break_on_hyphens=False)` — whitespace at wrap
    boundaries is consumed, so a violation column landing on a consumed
    space resolves to the first column of the following wrap row.

    Returns `None` when the column falls outside the line entirely.
    """
    if content_width <= 0 or column <= 0:
        return None
    rows = textwrap.wrap(
        source_line,
        width=content_width,
        break_long_words=True,
        break_on_hyphens=False,
        drop_whitespace=True,
        replace_whitespace=False,
        expand_tabs=False,
    )
    if not rows:
        return (0, 0)

    target = column - 1
    src_pos = 0
    for row_idx, row in enumerate(rows):
        # Skip whitespace consumed at this wrap boundary; if the target
        # column lands on consumed whitespace, snap to the start of the
        # following row.
        while src_pos < len(source_line) and source_line[src_pos].isspace():
            if src_pos == target:
                return (row_idx, 0)
            src_pos += 1
        row_end = src_pos + len(row)
        if target < row_end:
            return (row_idx, target - src_pos)
        src_pos = row_end

    return (len(rows) - 1, max(0, len(rows[-1]) - 1))


def _render_type_banner(
    console: Console,
    *,
    rule_id: str,
    category: str,
    type_count: int,
    type_index: int,
    total_types: int,
) -> None:
    """Print a prominent banner when crossing into a new rule_id group."""
    body = (
        f"[bold]{rule_id}[/]  [dim]({category})[/]\n"
        f"[dim]{type_count} violation(s) of this type · "
        f"type {type_index}/{total_types}[/]"
    )
    console.print()
    console.print(
        Panel(
            body,
            title="[bold magenta]── NEW RULE TYPE ──[/]",
            title_align="left",
            border_style="magenta",
            padding=(0, 1),
        )
    )


def _render_violation(
    console: Console,
    *,
    index: int,
    total: int,
    paper_path: str,
    file: str | None,
    rule_id: str,
    category: str,
    severity: str,
    line: int | None,
    column: int | None,
    message: str,
) -> None:
    console.rule(f"[bold]{index}/{total}[/bold]")
    locator = _locator(paper_path, file, line, column)
    table = Table(show_header=False, box=None)
    table.add_row("Location", locator)
    table.add_row("Rule", f"{rule_id}  ({category}, {severity})")
    table.add_row("Message", message)
    console.print(table)

    result = source_snippet(paper_path, file, line, rule_id=rule_id)
    if result is not None:
        snippet, start = result
        highlight = {line} if line is not None else set()
        console.print(
            Syntax(
                snippet,
                _lexer_for(file, paper_path),
                line_numbers=True,
                start_line=start,
                highlight_lines=highlight,
                word_wrap=True,
            )
        )
        if line is not None and column is not None and column > 0:
            # rich.Syntax with word_wrap=True wraps each source line at
            # word boundaries within `width - gutter` characters; the
            # whitespace at each wrap boundary is consumed, so the
            # mapping from source column to visual position is not a
            # simple modulo. Replay the wrap on the violation's source
            # line via textwrap (empirically identical to rich's wrap)
            # to find the actual visual position.
            end_line = start + snippet.count("\n")
            gutter = len(str(end_line)) + 3
            width = max(gutter + 2, console.size.width)
            content_width = max(1, width - gutter)
            source_lines = snippet.splitlines()
            line_idx = line - start
            mapped = None
            if 0 <= line_idx < len(source_lines):
                mapped = _wrapped_caret_position(
                    source_lines[line_idx], column, content_width
                )
            if mapped is not None:
                row_idx, col_in_row = mapped
                caret_prefix = " " * (gutter + col_in_row)
                label = "" if row_idx == 0 else f" col {column}"
                console.print(
                    f"[bold yellow]{caret_prefix}^{label}[/bold yellow]"
                )


def _select_violations(
    cx,
    *,
    rule_ids: set[str] | None,
    limit: int | None,
    include_ai_labelled: bool = False,
) -> list:
    """Return a list of `sqlite3.Row` violations to review.

    `rule_ids=None` applies no rule filter; an empty set short-circuits
    to no rows (the intended behaviour when two filters intersect to
    nothing — e.g., `--rule X --skip-listed` with X not in the skip list).

    `include_ai_labelled=True` widens the queue to AI-labelled rows so
    a human can spot-check or override the AI's verdict — useful when
    `eval-jss report` shows a rule passing but every label came from
    the model with no human anchor.
    """
    if rule_ids is not None and not rule_ids:
        return []
    sql = (
        "SELECT v.id, v.paper_id, v.rule_id, v.category, v.line, v.column,"
        " v.message, v.severity, v.file, p.path AS paper_path"
        " FROM violations v JOIN papers p ON p.id = v.paper_id"
    )
    if include_ai_labelled:
        sql += (
            " WHERE (v.verdict IS NULL OR v.verdict = 'uncertain'"
            "        OR v.reviewer LIKE 'ai:%')"
        )
    else:
        sql += " WHERE (v.verdict IS NULL OR v.verdict = 'uncertain')"
    # Only surface violations the tool STILL emits (latest run), so a
    # finding that stopped firing after a rule/parser fix isn't queued
    # for review. Mirrors the precision report's scoping; NULL =
    # staleness untracked (legacy / direct insert) → keep it.
    sql += (
        " AND (v.last_seen_run_id = (SELECT MAX(id) FROM runs)"
        "      OR v.last_seen_run_id IS NULL)"
    )
    params: list = []
    if rule_ids is not None:
        placeholders = ", ".join("?" * len(rule_ids))
        sql += f" AND v.rule_id IN ({placeholders})"
        params.extend(sorted(rule_ids))
    sql += " ORDER BY v.rule_id, p.path, v.line, v.id"
    if limit is not None:
        sql += " LIMIT ?"
        params.append(limit)
    return cx.execute(sql, params).fetchall()


def _read_verdict_state(cx, violation_id: int) -> tuple[str | None, str | None, str | None]:
    row = cx.execute(
        "SELECT verdict, verdict_reason, reviewer FROM violations WHERE id=?",
        (violation_id,),
    ).fetchone()
    if row is None:
        return (None, None, None)
    return (row["verdict"], row["verdict_reason"], row["reviewer"])


def _write_verdict(
    cx,
    *,
    violation_id: int,
    verdict: str | None,
    reason: str | None,
    reviewer: str | None,
) -> None:
    cx.execute(
        "UPDATE violations SET verdict=?, verdict_reason=?, reviewer=? WHERE id=?",
        (verdict, reason, reviewer, violation_id),
    )


def run(
    *,
    db_path: Path,
    limit: int | None,
    rule_id: str | None,
    reviewer: str | None,
    skip_listed: bool = False,
    skip_list_path: Path | None = None,
    reverify_ai: bool = False,
) -> int:
    """Interactive review loop. Returns the CLI exit code.

    `skip_listed=True` restricts the review to rules listed in the AI
    review skip-list (`eval/review-skip-list.toml` by default) — the
    rules that bypass the AI classifier entirely and therefore can only
    be labelled by a human. Combining with `--rule X` intersects: only
    a skip-listed rule `X` survives.

    `reverify_ai=True` widens the queue to AI-labelled rows so the
    human can spot-check / override AI verdicts. Recommended for rules
    whose precision number depends entirely on AI labels with no
    human anchor.
    """
    reviewer_str = _resolve_reviewer(reviewer)
    console = Console()

    rule_ids: set[str] | None = None
    if skip_listed:
        from eval.review import load_skip_list
        rule_ids = load_skip_list(skip_list_path)
        if not rule_ids:
            console.print(
                "eval-jss: --skip-listed given but the skip list is empty."
            )
    if rule_id:
        rule_ids = {rule_id} if rule_ids is None else rule_ids & {rule_id}

    cx = db.connect(db_path)
    try:
        rows = _select_violations(
            cx,
            rule_ids=rule_ids,
            limit=limit,
            include_ai_labelled=reverify_ai,
        )
        if not rows:
            console.print("eval-jss: no pending violations to review.")
            return 0

        total = len(rows)
        # Group bookkeeping for the type banner / `n` jump: ordered list of
        # rule_ids in the queue, count per type, and the index of the first
        # row of each group.
        type_order: list[str] = []
        type_count: dict[str, int] = {}
        for r in rows:
            rid = r["rule_id"]
            if rid not in type_count:
                type_order.append(rid)
            type_count[rid] = type_count.get(rid, 0) + 1
        total_types = len(type_order)
        type_index_of: dict[str, int] = {
            rid: i + 1 for i, rid in enumerate(type_order)
        }

        console.print(
            f"[bold]{total}[/bold] violation(s) across "
            f"[bold]{total_types}[/bold] rule type(s) to review."
        )
        console.print(_LEGEND)

        # Stack of (idx, prev_verdict, prev_reason, prev_reviewer) snapshots
        # so `b` can restore the previous violation's pre-verdict state.
        history: list[tuple[int, str | None, str | None, str | None]] = []

        current_rule_id: str | None = None
        idx = 0
        while idx < total:
            row = rows[idx]
            if row["rule_id"] != current_rule_id:
                current_rule_id = row["rule_id"]
                _render_type_banner(
                    console,
                    rule_id=current_rule_id,
                    category=row["category"],
                    type_count=type_count[current_rule_id],
                    type_index=type_index_of[current_rule_id],
                    total_types=total_types,
                )
            _render_violation(
                console,
                index=idx + 1,
                total=total,
                paper_path=row["paper_path"],
                file=row["file"],
                rule_id=row["rule_id"],
                category=row["category"],
                severity=row["severity"],
                line=row["line"],
                column=row["column"],
                message=row["message"],
            )
            answer = _ask_verdict()
            if answer == "q":
                break
            if answer == "s":
                idx += 1
                continue
            if answer == "n":
                # Jump to the first violation of the next rule type. If we're
                # already in the last group, fall through to the end of the
                # queue (loop exits naturally).
                current = row["rule_id"]
                j = idx + 1
                while j < total and rows[j]["rule_id"] == current:
                    j += 1
                if j >= total:
                    console.print(
                        "[dim]No further rule types — already in the last group.[/dim]"
                    )
                idx = j
                continue
            if answer == "b":
                if not history:
                    console.print("[dim]Nothing to undo.[/dim]")
                    continue
                prev_idx, prev_verdict, prev_reason, prev_reviewer = history.pop()
                prev_row = rows[prev_idx]
                _write_verdict(
                    cx,
                    violation_id=prev_row["id"],
                    verdict=prev_verdict,
                    reason=prev_reason,
                    reviewer=prev_reviewer,
                )
                idx = prev_idx
                continue

            # Snapshot current verdict state so `b` later can restore it.
            prev_state = _read_verdict_state(cx, row["id"])
            verdict_str = _VERDICT[answer]
            reason = None
            if answer in ("t", "f"):
                reason = _ask_reason().strip() or None
            _write_verdict(
                cx,
                violation_id=row["id"],
                verdict=verdict_str,
                reason=reason,
                reviewer=reviewer_str,
            )
            history.append((idx, *prev_state))
            idx += 1
    finally:
        cx.close()

    return 0
