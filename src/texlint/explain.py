"""Spec 009 — rule explanation renderer.

Pure Python API:

    from texlint.explain import render
    print(render("JSS-CITE-002", fmt="terminal"))
    print(render(None, fmt="markdown"))   # listing view

The CLI integration (click subgroup migration) is deferred to a
follow-up to keep the existing CLI test surface stable. Once a
``jss-lint explain`` subcommand lands, it just calls into
:func:`render` here.
"""

from __future__ import annotations

import difflib
from collections.abc import Iterable
from typing import Literal

from texlint.api import Severity
from texlint.journals.jss._catalogue_data import RULES
from texlint.journals.jss._guide_index import load_guide_index

Format = Literal["terminal", "markdown"]


def did_you_mean(unknown_id: str, candidates: Iterable[str] = RULES.keys()) -> list[str]:
    return difflib.get_close_matches(unknown_id, list(candidates), n=5, cutoff=0.6)


def _level(sev: Severity | str) -> str:
    return sev.value if isinstance(sev, Severity) else str(sev)


def _render_one_terminal(rule_id: str, meta: dict) -> str:
    section = meta.get("guide_section") or ""
    url = meta.get("guide_url")
    body = meta.get("explanation") or meta["message_template"]
    lines = [
        f"{rule_id} ({_level(meta['severity']).upper()})",
        f"  Category: {meta['category']}",
        f"  Authority: {meta['authority']} ({meta['authority_ref']})",
    ]
    if section:
        lines.append(f"  JSS guide: {section}")
        if url:
            lines.append(f"  See: {url}")
    lines.append("")
    lines.append(body)
    return "\n".join(lines) + "\n"


def _render_one_markdown(rule_id: str, meta: dict) -> str:
    section = meta.get("guide_section") or ""
    url = meta.get("guide_url")
    body = meta.get("explanation") or meta["message_template"]
    parts = [f"# {rule_id}", ""]
    parts.append(f"- **Severity:** {_level(meta['severity'])}")
    parts.append(f"- **Category:** {meta['category']}")
    parts.append(f"- **Authority:** {meta['authority']} ({meta['authority_ref']})")
    if section and url:
        parts.append(f"- **JSS guide:** [{section}]({url})")
    elif section:
        parts.append(f"- **JSS guide:** {section}")
    parts.append("")
    parts.append(body)
    parts.append("")
    return "\n".join(parts)


def _render_listing(fmt: Format) -> str:
    by_category: dict[str, list[str]] = {}
    for rid, meta in RULES.items():
        by_category.setdefault(meta["category"], []).append(rid)

    out: list[str] = []
    if fmt == "markdown":
        out.append("# JSS-lint rule catalogue\n")
    else:
        out.append("JSS-lint rule catalogue:\n")

    for category in sorted(by_category):
        rule_ids = sorted(by_category[category])
        if fmt == "markdown":
            out.append(f"## {category}\n")
            for rid in rule_ids:
                out.append(f"- `{rid}` — {RULES[rid]['message_template']}")
            out.append("")
        else:
            out.append(f"  {category}:")
            for rid in rule_ids:
                out.append(f"    {rid}  {RULES[rid]['message_template']}")
            out.append("")
    return "\n".join(out) + ("\n" if fmt == "markdown" else "")


def render(rule_id: str | None, *, fmt: Format = "terminal") -> str:
    """Render a rule explanation in the requested format.

    ``rule_id is None`` produces a per-category listing.
    Unknown rule ids raise ``KeyError``; callers (CLI dispatch)
    catch this and produce a "did you mean?" suggestion list.
    """
    if rule_id is None:
        return _render_listing(fmt)

    rule_id = rule_id.strip().upper()
    if rule_id not in RULES:
        raise KeyError(rule_id)
    meta = dict(RULES[rule_id])
    # Resolve guide_url through the index when only guide_section is set.
    if "guide_section" in meta and "guide_url" not in meta:
        idx = load_guide_index()
        if meta["guide_section"] in idx:
            meta["guide_url"] = idx[meta["guide_section"]]

    if fmt == "markdown":
        return _render_one_markdown(rule_id, meta)
    return _render_one_terminal(rule_id, meta)
