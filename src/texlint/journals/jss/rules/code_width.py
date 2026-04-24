"""Code-width rule for the JSS journal plugin.

Rule:
  - JSS-WIDTH-001 — code lines inside Sinput / Soutput / CodeInput /
    CodeOutput / verbatim / Verbatim / Code / Scode environments must
    fit within ``ToolConfig.code_width`` columns (default 80).

Retrofits the Step 1 smoke rule ``src_001_width.py`` (deleted in the
same PR). The limit is configurable via ``ToolConfig.code_width`` per
reviewer clarification 2026-04-23.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from pylatexenc.latexwalker import LatexCharsNode, LatexEnvironmentNode

from texlint.api import ParsedDocument, Rule, ToolConfig, Violation
from texlint.journals.jss import _catalogue_data
from texlint.journals.jss.rules import _helpers


# Code environments whose content is subject to the line-width rule.
_CODE_ENVS: frozenset[str] = frozenset(
    {"verbatim", "Verbatim", "Code", "CodeInput", "CodeOutput",
     "Sinput", "Soutput", "Scode", "Schunk", "CodeChunk"}
)


def _violation(
    *, tex: Any, line: int, length: int, limit: int, rule_id: str
) -> Violation:
    meta = _catalogue_data.RULES[rule_id]
    return Violation(
        file=tex.path,
        line=line,
        column=length,
        rule_id=rule_id,
        severity=meta["severity"],
        message=meta["message_template"],
        suggestion=f"Wrap or reflow the code line to fit in {limit} columns.",
        fix=None,
    )


def check_jss_width_001(
    doc: ParsedDocument, cfg: ToolConfig
) -> Iterator[Violation]:
    limit = cfg.code_width
    for tex in doc.tex_files:
        source = tex.source
        if not source:
            continue
        for env in _code_envs_in(tex):
            yield from _scan_env(tex, env, source, limit)


def _code_envs_in(tex: Any) -> Iterator[Any]:
    for node in _helpers._walk(tex.nodes):
        if (
            isinstance(node, LatexEnvironmentNode)
            and node.environmentname in _CODE_ENVS
        ):
            yield node


def _scan_env(
    tex: Any, env: Any, source: str, limit: int
) -> Iterator[Violation]:
    """Yield one violation per source line within ``env`` that exceeds ``limit``."""
    start_pos, end_pos = _env_content_span(env)
    if start_pos is None or end_pos is None:
        return
    content = source[start_pos:end_pos]
    # 1-based line offset of `start_pos` within `source`.
    start_line, _ = _helpers._lineno_col(tex, start_pos)
    for offset, line_text in enumerate(content.splitlines()):
        if len(line_text) <= limit:
            continue
        yield _violation(
            tex=tex,
            line=start_line + offset,
            length=len(line_text),
            limit=limit,
            rule_id="JSS-WIDTH-001",
        )


def _env_content_span(env: Any) -> tuple[int | None, int | None]:
    """Return ``(start_pos, end_pos)`` for the text between \\begin{…} and \\end{…}."""
    nodelist = env.nodelist or ()
    if not nodelist:
        return None, None
    first = nodelist[0]
    last = nodelist[-1]
    first_pos = getattr(first, "pos", None)
    last_pos = getattr(last, "pos", None)
    last_len = getattr(last, "len", 0)
    if first_pos is None or last_pos is None:
        return None, None
    return first_pos, last_pos + last_len


# ---------------------------------------------------------------------------
# Rule object
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


jss_width_001 = _rule("JSS-WIDTH-001", check_jss_width_001)


rules: tuple[Rule, ...] = (jss_width_001,)
