"""R Markdown (``.Rmd``) parser — hand-rolled line-based state machine.

No external Markdown parser dependency (see spec 005 `research.md §2`
drift-reconciliation). PyYAML handles frontmatter. The tokenizer
yields a shallow ordered segment model (frontmatter → heading / prose
/ fenced-code); prose blocks are additionally parsed by pylatexenc as
raw-LaTeX islands per spec 005 §US2 and FR-006.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from texlint.api import (
    ParsedRmdFile,
    ParsedTexFile,
    RmdCode,
    RmdHeading,
    RmdProse,
    Severity,
    Violation,
)

_PARSE_RULE_ID = "JSS-PARSE-000"

# Fenced-code open / close patterns. An opening fence may carry an info
# string in curly braces (e.g. ```{r, fig.width=5}) or directly after
# the backticks (```python). The closing fence is a bare ``` possibly
# followed by trailing whitespace.
_FENCE_OPEN = re.compile(r"^```(?:\{([^}]*)\}|\s*([A-Za-z0-9_.+-]+))?\s*$")
_FENCE_CLOSE = re.compile(r"^```\s*$")

# ATX heading: 1-6 '#' followed by space and text.
_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")

# Inline R code `` `r expr` `` — stripped to equivalent-length whitespace
# in prose blocks only.
_INLINE_R = re.compile(r"`r\s[^`]*`")


def _parse_error(path: Path, *, line: int, message: str) -> Violation:
    return Violation(
        file=path,
        line=line,
        column=None,
        rule_id=_PARSE_RULE_ID,
        severity=Severity.ERROR,
        message=message,
        suggestion=None,
        fix=None,
    )


def _extract_fence_lang(line: str) -> str:
    m = _FENCE_OPEN.match(line)
    if m is None:
        return ""
    info = m.group(1) or m.group(2) or ""
    info = info.strip()
    if not info:
        return ""
    # For `{r, fig.width=5}` style: the language is the first token.
    first = info.split(",", 1)[0].strip()
    return first


def parse_rmd_source(src: str, path: Path) -> ParsedRmdFile:
    """Tokenise ``src`` into an :class:`ParsedRmdFile`."""
    from texlint.core.parser import parse_tex_source

    lines = src.splitlines()
    n_lines = len(lines)

    frontmatter: dict[str, Any] = {}
    violations: list[Violation] = []
    headings: list[RmdHeading] = []
    prose_blocks: list[RmdProse] = []
    code_blocks: list[RmdCode] = []

    state = "START"
    fm_buffer: list[str] = []
    fm_start_line = 0
    fence_body: list[str] = []
    fence_info = ""
    fence_open_line = 0
    prose_buffer: list[str] = []
    prose_start_line = 0

    def _flush_prose() -> None:
        if not prose_buffer:
            return
        text = "\n".join(prose_buffer)
        prose_blocks.append(RmdProse(
            text=text,
            line=prose_start_line,
            n_lines=len(prose_buffer),
        ))
        prose_buffer.clear()

    i = 0
    while i < n_lines:
        line = lines[i]
        line_no = i + 1  # 1-based

        if state == "START":
            if line.strip() == "---":
                state = "FRONTMATTER"
                fm_buffer = []
                fm_start_line = line_no
            else:
                state = "BODY"
                continue  # reprocess this line in BODY
        elif state == "FRONTMATTER":
            if line.strip() == "---":
                text = "\n".join(fm_buffer)
                try:
                    loaded = yaml.safe_load(text) if text.strip() else {}
                    frontmatter = loaded if isinstance(loaded, dict) else {}
                except yaml.YAMLError as exc:
                    violations.append(_parse_error(
                        path, line=fm_start_line,
                        message=f"Malformed YAML frontmatter: {exc}",
                    ))
                state = "BODY"
            else:
                fm_buffer.append(line)
        elif state == "BODY":
            if _FENCE_OPEN.match(line):
                _flush_prose()
                fence_open_line = line_no
                fence_info = _extract_fence_lang(line)
                fence_body = []
                state = "FENCE"
            elif (m := _HEADING.match(line)):
                _flush_prose()
                headings.append(RmdHeading(
                    level=len(m.group(1)),
                    text=m.group(2),
                    line=line_no,
                ))
            elif not line.strip():
                # Blank line flushes the current prose block.
                _flush_prose()
            else:
                if not prose_buffer:
                    prose_start_line = line_no
                prose_buffer.append(line)
        elif state == "FENCE":
            if _FENCE_CLOSE.match(line):
                code_blocks.append(RmdCode(
                    lang=fence_info,
                    body="\n".join(fence_body),
                    open_line=fence_open_line,
                    close_line=line_no,
                ))
                state = "BODY"
                fence_body = []
            else:
                fence_body.append(line)
        i += 1

    # End-of-file handling.
    if state == "FRONTMATTER":
        violations.append(_parse_error(
            path, line=fm_start_line,
            message="Unterminated YAML frontmatter.",
        ))
    elif state == "FENCE":
        violations.append(_parse_error(
            path, line=fence_open_line,
            message="Unterminated fenced code block.",
        ))
    else:
        _flush_prose()

    # Strip inline R code from each prose block (FR-010).
    prose_blocks = [
        RmdProse(
            text=_INLINE_R.sub(lambda m: " " * len(m.group(0)), p.text),
            line=p.line,
            n_lines=p.n_lines,
        )
        for p in prose_blocks
    ]

    # Parse raw-LaTeX islands from each prose block (FR-006).
    latex_fragments: list[ParsedTexFile] = []
    for prose in prose_blocks:
        if not prose.text.strip():
            continue
        frag_path = Path(f"{path}:block@{prose.line}")
        fragment = parse_tex_source(prose.text, frag_path)
        # Offset line numbers on any parse-error violations so they map
        # back to the original Rmd source.
        if fragment.violations:
            offset_violations = tuple(
                Violation(
                    file=path,
                    line=prose.line + v.line - 1,
                    column=v.column,
                    rule_id=v.rule_id,
                    severity=v.severity,
                    message=v.message,
                    suggestion=v.suggestion,
                    fix=v.fix,
                )
                for v in fragment.violations
            )
            violations.extend(offset_violations)
            fragment = ParsedTexFile(
                path=fragment.path,
                source=fragment.source,
                nodes=fragment.nodes,
                walker=fragment.walker,
                violations=(),
            )
        latex_fragments.append(fragment)

    return ParsedRmdFile(
        path=path,
        source=src,
        yaml_frontmatter=frontmatter,
        headings=tuple(headings),
        prose_blocks=tuple(prose_blocks),
        code_blocks=tuple(code_blocks),
        latex_fragments=tuple(latex_fragments),
        violations=tuple(violations),
    )
