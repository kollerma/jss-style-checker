"""Jinja2-based HTML renderer for :class:`texlint.api.ComplianceReport`.

Uses :class:`jinja2.PackageLoader` so templates ship inside the wheel. Author
mode (``author.html.j2``) surfaces individual violations grouped by file;
reviewer mode (``reviewer.html.j2``) surfaces the per-category compliance
table plus the overall percentage.
"""

from __future__ import annotations

import sys
from collections import defaultdict
from typing import Any

from jinja2 import Environment, PackageLoader, select_autoescape

from texlint.api import ComplianceReport, ToolConfig


def _make_env() -> Environment:
    return Environment(
        loader=PackageLoader("texlint.output", "templates"),
        autoescape=select_autoescape(["html", "xml", "j2", "html.j2"]),
        keep_trailing_newline=True,
    )


def _group_violations(report: ComplianceReport) -> list[dict[str, Any]]:
    by_file: dict[str, list[Any]] = defaultdict(list)
    for v in report.violations:
        by_file[str(v.file)].append(v)
    return [
        {"file": f, "violations": by_file[f]} for f in sorted(by_file)
    ]


def render(report: ComplianceReport, config: ToolConfig) -> None:
    env = _make_env()
    template_name = "reviewer.html.j2" if config.mode == "reviewer" else "author.html.j2"
    template = env.get_template(template_name)
    rendered = template.render(report=report, groups=_group_violations(report))
    sys.stdout.write(rendered)
    if not rendered.endswith("\n"):
        sys.stdout.write("\n")
