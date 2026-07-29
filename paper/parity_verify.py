#!/usr/bin/env python3
"""Byte-parity evidence for the manuscript — internal, run by regenerate.sh.

Renders examples/demo.tex in every output format twice: with the Python
reference engine (texlint, in-process) and with the Rust port (the
jsslint PyO3 wheel, in-process), then byte-compares the two renderings.
Prints the evidence listing the paper includes verbatim (Appendix) and
exits non-zero on any mismatch, so regeneration fails loudly if the
engines ever drift.

Both engines see the identical input: the literal path "demo.tex" with
the file's contents, rendered from a scratch working directory so no
project configuration interferes.
"""

from __future__ import annotations

import contextlib
import hashlib
import io
import os
import sys
import tempfile
from importlib import metadata
from pathlib import Path

import jsslint

from texlint.config import load as load_config
from texlint.core.engine import load_journal, parse_document, run
from texlint.output import html_output, json_output, sarif, terminal

FORMATS = ("terminal", "json", "sarif", "html")
RENDERERS = {
    "terminal": terminal.render,
    "json": json_output.render,
    "sarif": sarif.render,
    "html": html_output.render,
}


def python_reference(demo: Path, fmt: str) -> str:
    document = parse_document(
        [Path("demo.tex")],
        sources={Path("demo.tex"): demo.read_text(encoding="utf-8")},
    )
    cfg = load_config({"output": fmt}, Path.cwd())
    journal = load_journal(cfg.journal)
    report = run(cfg, document, journal)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        RENDERERS[fmt](report, cfg)
    return buf.getvalue()


def main() -> int:
    paper_dir = Path(__file__).resolve().parent
    demo = paper_dir / "examples" / "demo.tex"
    py_version = metadata.version("jss-style-checker")
    rs_version = metadata.version("jsslint")
    if py_version != rs_version:
        print(
            f"error: texlint {py_version} vs jsslint {rs_version}",
            file=sys.stderr,
        )
        return 1

    lines = [
        "Byte-parity of the two engines on examples/demo.tex",
        f"reference: jss-style-checker {py_version} (Python)",
        f"port:      jsslint {rs_version} (Rust, in-process wheel)",
        "",
    ]
    failed = False
    with tempfile.TemporaryDirectory() as scratch:
        os.chdir(scratch)
        source = demo.read_text(encoding="utf-8")
        for fmt in FORMATS:
            expected = python_reference(demo, fmt)
            actual = jsslint.render([("demo.tex", source)], output=fmt)
            same = expected == actual
            failed = failed or not same
            digest = hashlib.sha256(expected.encode("utf-8")).hexdigest()
            verdict = "IDENTICAL" if same else "DIFFER"
            lines.append(
                f"{fmt:<9}{len(expected.encode('utf-8')):>7} bytes  {verdict}"
            )
            lines.append(f"  sha256 {digest}")
    n_same = sum(
        1 for line in lines if line.endswith("IDENTICAL")
    )
    lines.append("")
    lines.append(f"{n_same}/{len(FORMATS)} output formats byte-identical.")
    print("\n".join(lines))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
