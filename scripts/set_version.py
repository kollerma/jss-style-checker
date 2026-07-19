#!/usr/bin/env python3
"""Propagate the single-source version to every ecosystem manifest.

The root ``VERSION`` file is the one place you edit. This script writes that
value into the four native manifests that PyPI / crates.io / npm / CRAN each
read (nothing can make those four literally share one file), then regenerates
the derived artifacts (the R vendored crate + both Cargo.lock files).

Usage:
    python scripts/set_version.py            # propagate the current VERSION
    python scripts/set_version.py 1.0.2      # write 1.0.2 to VERSION, then propagate

``tests/unit/test_version_single_source.py`` guards the result: CI fails,
naming the offending file, if any manifest drifts from VERSION — so a stale
string can never ship silently.

Note: pyproject.toml is intentionally NOT written here — it reads the version
dynamically from ``src/texlint/__init__.py`` (``[tool.hatch.version]``). The
Cargo dependency pin (``jsslint-core = { version = "1" }``) is a range, so it
also never needs touching.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
VERSION_FILE = REPO / "VERSION"

# The suite version is a plain X.Y.Z. Kept strict so a typo ("1.0", "v1.0.1")
# is rejected AND so an R resubmission revision ("1.0.1-1") can't be pushed to
# the whole suite by mistake — Cargo would read the "-1" as a pre-release. The
# R "-N" revision is a manual DESCRIPTION-only edit (the consistency test
# tolerates it there); it does not belong in VERSION.
_VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")


def _sub(path: Path, pattern: str, repl: str, *, count: int = 0, flags: int = 0) -> None:
    text = path.read_text(encoding="utf-8")
    new, n = re.subn(pattern, repl, text, count=count, flags=flags)
    if n == 0:
        raise SystemExit(f"set_version: no version field matched in {path} (pattern {pattern!r})")
    if new != text:
        path.write_text(new, encoding="utf-8")
        print(f"  updated {path.relative_to(REPO)} ({n} occurrence{'s' if n != 1 else ''})")


def _run(cmd: list[str]) -> bool:
    print("  $ " + " ".join(cmd))
    try:
        subprocess.run(cmd, cwd=REPO, check=True)
        return True
    except FileNotFoundError:
        print(f"  ! {cmd[0]} not found on PATH — skipping (regenerate the lockfile manually)")
        return False
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"set_version: `{' '.join(cmd)}` failed ({exc.returncode})") from exc


def main(argv: list[str]) -> None:
    if len(argv) > 1:
        version = argv[1].lstrip("v")
        if not _VERSION_RE.match(version):
            raise SystemExit(f"set_version: {version!r} is not a valid X.Y.Z version")
        VERSION_FILE.write_text(version + "\n", encoding="utf-8")
        print(f"VERSION -> {version}")

    version = VERSION_FILE.read_text(encoding="utf-8").strip()
    if not _VERSION_RE.match(version):
        raise SystemExit(f"set_version: VERSION contains an invalid version {version!r}")
    print(f"Propagating version {version}")

    # 1. Python — the hatch source of truth (pyproject reads this).
    _sub(REPO / "src/texlint/__init__.py",
         r'^__version__ = "[^"]*"', f'__version__ = "{version}"', flags=re.MULTILINE)

    # 2. Rust — [workspace.package] version feeds every crate in the workspace.
    _sub(REPO / "rust/Cargo.toml",
         r'^version = "[^"]*"', f'version = "{version}"', count=1, flags=re.MULTILINE)

    # 3. npm — package.json (first "version") + package-lock.json (both places,
    #    keyed on the package name so dependency versions are untouched).
    _sub(REPO / "vscode-extension/package.json",
         r'"version":\s*"[^"]*"', f'"version": "{version}"', count=1)
    _sub(REPO / "vscode-extension/package-lock.json",
         r'("name": "jss-style-checker",\s*"version": ")[^"]*(")', rf'\g<1>{version}\g<2>')

    # 4. R — DESCRIPTION and the embedded jsslintr crate manifest (the vendored
    #    jsslint-core crate below it is stamped by the vendor script instead).
    _sub(REPO / "r/jsslintr/DESCRIPTION",
         r'^Version: .*$', f'Version: {version}', flags=re.MULTILINE)
    _sub(REPO / "r/jsslintr/src/rust/Cargo.toml",
         r'^version = "[^"]*"', f'version = "{version}"', count=1, flags=re.MULTILINE)

    # 5. Citation metadata (CITATION.cff drives GitHub's "cite this
    #    repository" box and Zenodo's archive records). The bump runs at
    #    release-prep time, so today is the release date.
    import datetime

    _sub(REPO / "CITATION.cff",
         r'^version: .*$', f'version: {version}', flags=re.MULTILINE)
    _sub(REPO / "CITATION.cff",
         r'^date-released: .*$',
         f'date-released: {datetime.date.today().isoformat()}',
         flags=re.MULTILINE)

    # Derived artifacts: the R package's vendored jsslint-core (its Cargo.toml
    # version is stamped from rust/Cargo.toml by the vendor script) and the two
    # Cargo.lock files that --locked builds pin against.
    print("Regenerating derived artifacts")
    _run(["bash", "r/jsslintr/tools/vendor-jsslint-core.sh"])
    _run(["cargo", "update", "-p", "jsslintr", "-p", "jsslint-core",
          "--manifest-path", "r/jsslintr/src/rust/Cargo.toml"])
    _run(["cargo", "update", "-p", "jsslint-core", "-p", "jsslint-cli",
          "-p", "jsslint-wasm", "-p", "jsslint-py", "--manifest-path", "rust/Cargo.toml"])

    print("Done. Run `python -m pytest tests/unit/test_version_single_source.py` to verify.")


if __name__ == "__main__":
    main(sys.argv)
