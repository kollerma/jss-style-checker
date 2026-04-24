"""Code-style rules for the JSS journal plugin.

Rules:
  - JSS-CODE-001 — verbatim / CodeInput blocks do not contain comments.
  - JSS-CODE-002 — ``library()`` / ``data()`` calls quote their first arg.
  - JSS-CODE-003 — code samples use spaces around operators and after commas.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from typing import Any

from pylatexenc.latexwalker import (
    LatexCharsNode,
    LatexEnvironmentNode,
    LatexGroupNode,
    LatexMacroNode,
)

from texlint.api import ParsedDocument, Rule, ToolConfig, Violation
from texlint.journals.jss import _catalogue_data
from texlint.journals.jss.rules import _helpers

# Envs where code lives.
_CODE_ENVS: frozenset[str] = frozenset(
    {"verbatim", "Verbatim", "Code", "CodeInput", "CodeOutput",
     "Sinput", "Soutput", "Scode", "Schunk", "CodeChunk"}
)

_COMMENT_LINE_RE = re.compile(r"(?m)#[^\n]*")
_LIBRARY_UNQUOTED_RE = re.compile(
    r"\b(?:library|data|require|requireNamespace)\(\s*([A-Za-z][A-Za-z0-9_.]*)\s*\)"
)
_MISSING_SPACES_RE = re.compile(
    r"(?:[A-Za-z0-9_\.\)\]][=+\-*/][A-Za-z0-9_\.\(\[])"
    r"|(?:,[A-Za-z0-9_\.\(\[])"
)


def _violation(
    *, tex: Any, pos: int, rule_id: str, suggestion: str
) -> Violation:
    meta = _catalogue_data.RULES[rule_id]
    line, col = _helpers._lineno_col(tex, pos)
    return Violation(
        file=tex.path,
        line=line,
        column=col,
        rule_id=rule_id,
        severity=meta["severity"],
        message=meta["message_template"],
        suggestion=suggestion,
        fix=None,
    )


# ---------------------------------------------------------------------------
# JSS-CODE-001 — comments inside code envs
# ---------------------------------------------------------------------------


def check_jss_code_001(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.all_tex_like():
        for node in _helpers._walk(tex.nodes):
            if not isinstance(node, LatexEnvironmentNode):
                continue
            if node.environmentname not in _CODE_ENVS:
                continue
            for child in node.nodelist or ():
                if not isinstance(child, LatexCharsNode):
                    continue
                match = _COMMENT_LINE_RE.search(child.chars)
                if match is None:
                    continue
                abs_pos = child.pos + match.start()
                yield _violation(
                    tex=tex,
                    pos=abs_pos,
                    rule_id="JSS-CODE-001",
                    suggestion=(
                        "Move the comment into the surrounding LaTeX text."
                    ),
                )
                break  # one violation per code block is enough


# ---------------------------------------------------------------------------
# JSS-CODE-002 — unquoted library() / data()
# ---------------------------------------------------------------------------


def _code_002_suggestion(match: Any) -> str:
    arg = match.group(1)
    quoted = match.group(0).replace(arg, f'"{arg}"')
    return f"Quote the argument: e.g., {quoted!r}."


def check_jss_code_002(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.all_tex_like():
        for node in _helpers._walk(tex.nodes):
            if not isinstance(node, LatexEnvironmentNode):
                continue
            if node.environmentname not in _CODE_ENVS:
                continue
            for child in node.nodelist or ():
                if not isinstance(child, LatexCharsNode):
                    continue
                for match in _LIBRARY_UNQUOTED_RE.finditer(child.chars):
                    abs_pos = child.pos + match.start()
                    yield _violation(
                        tex=tex,
                        pos=abs_pos,
                        rule_id="JSS-CODE-002",
                        suggestion=_code_002_suggestion(match),
                    )


# ---------------------------------------------------------------------------
# JSS-CODE-003 — missing spaces around operators in \code{}
# ---------------------------------------------------------------------------


def check_jss_code_003(
    doc: ParsedDocument, _cfg: ToolConfig
) -> Iterator[Violation]:
    for tex in doc.all_tex_like():
        for parent, idx, node in _helpers._iter_with_parent(tex.nodes):
            if not (
                isinstance(node, LatexMacroNode)
                and node.macroname == "code"
            ):
                continue
            group = _first_group_arg(node, parent, idx)
            if group is None:
                continue
            text = _group_plain_text(group)
            if not text:
                continue
            if _MISSING_SPACES_RE.search(text):
                yield _violation(
                    tex=tex,
                    pos=node.pos,
                    rule_id="JSS-CODE-003",
                    suggestion=(
                        "Add spaces around operators and after commas in "
                        "the code sample (e.g., 'y = a + b * x')."
                    ),
                )


def _first_group_arg(macro: Any, parent: Any, idx: int) -> Any:
    argd = getattr(macro, "nodeargd", None)
    if argd is not None:
        for arg in argd.argnlist or ():
            if isinstance(arg, LatexGroupNode):
                return arg
    return _helpers._next_group_arg(parent, idx)


def _group_plain_text(group: Any) -> str:
    parts: list[str] = []
    for child in group.nodelist or ():
        if isinstance(child, LatexCharsNode):
            parts.append(child.chars)
    return "".join(parts).strip()


# ---------------------------------------------------------------------------
# Rule objects
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


jss_code_001 = _rule("JSS-CODE-001", check_jss_code_001)
jss_code_002 = _rule("JSS-CODE-002", check_jss_code_002)
jss_code_003 = _rule("JSS-CODE-003", check_jss_code_003)


rules: tuple[Rule, ...] = (jss_code_001, jss_code_002, jss_code_003)
