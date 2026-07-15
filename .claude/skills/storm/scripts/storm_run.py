#!/usr/bin/env python3
"""STORM skill helper — deterministic run scaffolding and source merging.

Two subcommands:

  init "<topic>"     Create storm-runs/<slug>/ (with a raw/ subdir) in the
                     current working directory and print the run paths as JSON.

  merge <run_dir>    Read every raw/*.sources.tsv, dedupe by normalized URL,
                     assign stable [n] numbers in first-seen order, write a
                     numbered sources.md, and print the url -> [n] map as JSON.

Stdlib only. Safe to run repeatedly (idempotent). The point of this helper is
to make citation numbering deterministic and parallel-safe: each interview
writes its own sources file, and merge collapses them into one numbered list.
"""

import glob
import json
import os
import re
import sys


def slugify(text, max_len=60):
    s = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    s = re.sub(r"[\s_-]+", "-", s).strip("-")
    if len(s) <= max_len:
        return s or "topic"
    # Truncate on a word boundary so we don't cut a word in half.
    out, length = [], 0
    for word in s.split("-"):
        add = (1 if out else 0) + len(word)
        if length + add > max_len:
            break
        out.append(word)
        length += add
    return "-".join(out) if out else s[:max_len].strip("-") or "topic"


def clean_url(url):
    """Tidy a URL for display: drop fragment, utm_* params, trailing slash.
    Case is preserved so case-sensitive paths still work when clicked."""
    u = url.strip()
    u = u.split("#", 1)[0]                        # drop fragment
    u = re.sub(r"([?&])utm_[^=]+=[^&]*", r"\1", u)  # drop utm_* params
    u = re.sub(r"[?&]+$", "", u)                  # tidy trailing ? or &
    if u.endswith("/"):
        u = u[:-1]
    return u


def dedup_key(url):
    """Lowercased clean URL — used only to decide if two links are the same."""
    return clean_url(url).lower()


def cmd_init(topic):
    slug = slugify(topic)
    run_dir = os.path.join("storm-runs", slug)
    raw_dir = os.path.join(run_dir, "raw")
    os.makedirs(raw_dir, exist_ok=True)

    persp = os.path.join(run_dir, "perspectives.md")
    if not os.path.exists(persp):
        with open(persp, "w", encoding="utf-8") as f:
            f.write(f"# Perspectives \u2014 {topic}\n\n")

    print(json.dumps({
        "topic": topic,
        "slug": slug,
        "run_dir": run_dir,
        "raw_dir": raw_dir,
        "perspectives": persp,
        "contradictions": os.path.join(run_dir, "contradictions.md"),
        "outline": os.path.join(run_dir, "outline.md"),
        "sources": os.path.join(run_dir, "sources.md"),
        "report": os.path.join(run_dir, "report.md"),
    }, indent=2))


def cmd_merge(run_dir):
    raw_dir = os.path.join(run_dir, "raw")
    if not os.path.isdir(raw_dir):
        sys.stderr.write(f"No raw/ directory found in {run_dir}\n")
        sys.exit(1)

    rows = []  # (url, title) in the order encountered
    for path in sorted(glob.glob(os.path.join(raw_dir, "*.sources.tsv"))):
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.rstrip("\n")
                if not line.strip():
                    continue
                parts = line.split("\t")
                url = parts[0].strip()
                title = parts[1].strip() if len(parts) > 1 and parts[1].strip() else url
                if url:
                    rows.append((url, title))

    seen = {}      # dedup_key -> n
    ordered = []   # (n, clean_url, title)
    for url, title in rows:
        key = dedup_key(url)
        if key not in seen:
            seen[key] = len(seen) + 1
            ordered.append((seen[key], clean_url(url), title))

    sources_md = os.path.join(run_dir, "sources.md")
    with open(sources_md, "w", encoding="utf-8") as f:
        f.write("# Sources\n\n")
        for n, url, title in ordered:
            f.write(f"[{n}] {title} \u2014 {url}\n")

    print(json.dumps({
        "sources_file": sources_md,
        "count": len(ordered),
        "url_to_index": {dedup_key(u): n for n, u, _ in ordered},
    }, indent=2))


USAGE = 'Usage: storm_run.py init "<topic>"  |  storm_run.py merge <run_dir>'


def main():
    if len(sys.argv) < 3:
        sys.stderr.write(USAGE + "\n")
        sys.exit(1)
    cmd, arg = sys.argv[1], sys.argv[2]
    if cmd == "init":
        cmd_init(arg)
    elif cmd == "merge":
        cmd_merge(arg)
    else:
        sys.stderr.write(USAGE + "\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
