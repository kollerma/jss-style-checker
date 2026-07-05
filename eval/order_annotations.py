"""Order the [[violations]] blocks in each recall annotations.toml by
(file, line, rule_id) so a reviewer reads them in document order.

Text-level block reorder: each [[violations]] block is kept verbatim and
only moved, so comments inside entries, the header, [meta], and the
trailing reviewed-FP comment block are all preserved exactly.

    python -m eval.order_annotations                 # order all recall papers
    python -m eval.order_annotations --drop-prefill   # first drop [prefill:…] entries, then order
"""
from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path

RECALL = Path(__file__).resolve().parent.parent / "eval" / "recall-corpus"
_RULE = re.compile(r'rule_id\s*=\s*"([^"]+)"')
_FILE = re.compile(r'file\s*=\s*"([^"]+)"')
_LINE = re.compile(r"line\s*=\s*(\d+)")


def _split(text: str):
    """Return (preamble, [block_texts], trailing). preamble is everything up
    to the first [[violations]]; trailing is the suffix of blank/# lines
    (the reviewed-FP comment block)."""
    lines = text.split("\n")
    # trailing = maximal suffix of blank-or-comment lines
    t = len(lines)
    while t > 0 and (lines[t - 1].strip() == "" or lines[t - 1].lstrip().startswith("#")):
        t -= 1
    body, trailing = lines[:t], lines[t:]
    # first [[violations]]
    fv = next((i for i, ln in enumerate(body) if ln.strip() == "[[violations]]"), len(body))
    preamble, vregion = body[:fv], body[fv:]
    # split vregion into blocks at each [[violations]]
    blocks, cur = [], []
    for ln in vregion:
        if ln.strip() == "[[violations]]" and cur:
            blocks.append(cur)
            cur = [ln]
        else:
            cur.append(ln)
    if cur:
        blocks.append(cur)
    # strip trailing blank lines off each block's text
    block_texts = []
    for b in blocks:
        while b and b[-1].strip() == "":
            b.pop()
        block_texts.append("\n".join(b))
    return preamble, block_texts, trailing


def _key(block: str):
    r = _RULE.search(block)
    f = _FILE.search(block)
    n = _LINE.search(block)
    return (f.group(1) if f else "", int(n.group(1)) if n else 0, r.group(1) if r else "")


def process(path: Path, drop_prefill: bool) -> tuple[int, int]:
    text = path.read_text(encoding="utf-8")
    before = tomllib.loads(text).get("violations", [])
    preamble, blocks, trailing = _split(text)
    if drop_prefill:
        blocks = [b for b in blocks if "[prefill:" not in b]
    blocks.sort(key=_key)
    pre = "\n".join(preamble).rstrip("\n")
    out = pre + "\n\n" + "\n\n".join(blocks) + "\n"
    if trailing:
        out += "\n" + "\n".join(trailing).rstrip("\n") + "\n"
    # safety: must still parse, and (when not dropping) keep the same multiset
    after = tomllib.loads(out).get("violations", [])
    if not drop_prefill and len(after) != len(before):
        raise SystemExit(f"{path}: reorder changed count {len(before)}->{len(after)}; aborting")
    path.write_text(out, encoding="utf-8")
    return len(before), len(after)


def main(argv):
    drop = "--drop-prefill" in argv
    only = {a for a in argv if not a.startswith("--")}
    for d in sorted(p for p in RECALL.iterdir() if p.is_dir() and p.name != "__pycache__"):
        if only and d.name not in only:
            continue
        ann = d / "annotations.toml"
        if not ann.exists():
            continue
        b, a = process(ann, drop)
        tag = f"{b}->{a}" if drop else f"{a}"
        print(f"  {d.name}: ordered ({tag} violations)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
