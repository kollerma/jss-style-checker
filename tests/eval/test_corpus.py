"""Tests for `eval.corpus` — manifest parse, URL derivation, SHA256 verify, tarslip.

Spec FR-024, FR-025, FR-026. No real network — `urllib.request.urlopen`
is monkeypatched.
"""

from __future__ import annotations

import hashlib
import io
import tarfile
from pathlib import Path
from typing import Callable

import pytest

from eval import corpus


# -----------------------------------------------------------------------------
# Manifest parsing
# -----------------------------------------------------------------------------


def _write_manifest(path: Path, rows: list[list[str]]) -> None:
    header = "jss_doi,source,source_id,version,vignette_file,local_path,sha256\n"
    path.write_text(header + "".join(",".join(r) + "\n" for r in rows), encoding="utf-8")


def test_load_manifest_parses_valid_rows(tmp_path: Path) -> None:
    mp = tmp_path / "manifest.csv"
    _write_manifest(
        mp,
        [
            ["10.18637/jss.v001.i01", "cran", "foo", "1.0.0", "paper.tex", "cran_foo_1.0.0/", "a" * 64],
            ["", "arxiv", "2401.12345", "v2", "paper.tex", "arxiv_2401.12345_v2/", "b" * 64],
        ],
    )
    rows = corpus.load_manifest(mp)
    assert len(rows) == 2
    assert rows[0].source == "cran"
    assert rows[0].source_id == "foo"
    assert rows[0].local_path == Path("cran_foo_1.0.0/")
    assert rows[1].source == "arxiv"


def test_load_manifest_rejects_bad_header(tmp_path: Path) -> None:
    mp = tmp_path / "m.csv"
    mp.write_text("wrong,header,format\n", encoding="utf-8")
    with pytest.raises(corpus.ManifestError):
        corpus.load_manifest(mp)


def test_load_manifest_rejects_bad_source(tmp_path: Path) -> None:
    mp = tmp_path / "m.csv"
    _write_manifest(
        mp,
        [["", "unknown_source", "x", "1", "p.tex", "x/", "a" * 64]],
    )
    with pytest.raises(corpus.ManifestError):
        corpus.load_manifest(mp)


def test_load_manifest_rejects_duplicate_local_path(tmp_path: Path) -> None:
    mp = tmp_path / "m.csv"
    _write_manifest(
        mp,
        [
            ["", "cran", "foo", "1", "p.tex", "dup/", "a" * 64],
            ["", "cran", "bar", "1", "p.tex", "dup/", "b" * 64],
        ],
    )
    with pytest.raises(corpus.ManifestError):
        corpus.load_manifest(mp)


def test_load_manifest_rejects_bad_sha(tmp_path: Path) -> None:
    mp = tmp_path / "m.csv"
    _write_manifest(
        mp,
        [["", "cran", "foo", "1", "p.tex", "x/", "nothex"]],
    )
    with pytest.raises(corpus.ManifestError):
        corpus.load_manifest(mp)


# -----------------------------------------------------------------------------
# URL derivation
# -----------------------------------------------------------------------------


def test_resolve_url_cran() -> None:
    row = corpus.ManifestRow(
        jss_doi=None, source="cran", source_id="lme4", version="1.1-35.1",
        vignette_file="vignettes/lmer.tex", local_path=Path("x/"), sha256="a" * 64,
    )
    url = corpus._resolve_url(row)
    assert url == "https://cran.r-project.org/src/contrib/Archive/lme4/lme4_1.1-35.1.tar.gz"


def test_resolve_url_arxiv() -> None:
    row = corpus.ManifestRow(
        jss_doi=None, source="arxiv", source_id="2401.12345", version="v2",
        vignette_file="paper.tex", local_path=Path("x/"), sha256="a" * 64,
    )
    url = corpus._resolve_url(row)
    assert url == "http://arxiv.org/e-print/2401.12345v2"


def test_resolve_url_jss_archive_is_none() -> None:
    row = corpus.ManifestRow(
        jss_doi="10.18637/jss.v092.i04", source="jss_archive",
        source_id="v092i04", version="manual", vignette_file="paper.tex",
        local_path=Path("x/"), sha256="a" * 64,
    )
    assert corpus._resolve_url(row) is None  # manual placement required


def test_resolve_url_manual_is_none() -> None:
    row = corpus.ManifestRow(
        jss_doi=None, source="manual", source_id="x", version="manual",
        vignette_file="p.tex", local_path=Path("x/"), sha256="a" * 64,
    )
    assert corpus._resolve_url(row) is None


# -----------------------------------------------------------------------------
# Fetch + SHA256 verify + tarball extract (monkeypatched urlopen)
# -----------------------------------------------------------------------------


def _build_fake_tar(members: list[tuple[str, bytes]]) -> bytes:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for name, data in members:
            info = tarfile.TarInfo(name=name)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
    return buf.getvalue()


class _FakeResponse:
    def __init__(self, data: bytes) -> None:
        self._data = data
        self._pos = 0

    def read(self, n: int = -1) -> bytes:
        if n < 0 or n >= len(self._data) - self._pos:
            out = self._data[self._pos:]
            self._pos = len(self._data)
            return out
        out = self._data[self._pos : self._pos + n]
        self._pos += n
        return out

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, *args: object) -> None:
        pass


def _patch_urlopen(monkeypatch, url_to_bytes: dict[str, bytes]) -> None:
    def fake_urlopen(req, timeout=None):  # noqa: ARG001 — signature compat
        url = req.full_url if hasattr(req, "full_url") else req
        return _FakeResponse(url_to_bytes[url])

    monkeypatch.setattr(corpus.urllib.request, "urlopen", fake_urlopen)


def test_fetch_verifies_sha256_and_extracts_tarball(monkeypatch, tmp_path: Path) -> None:
    tar_bytes = _build_fake_tar([("lme4/vignettes/lmer.tex", b"\\documentclass{jss}\n")])
    sha = hashlib.sha256(tar_bytes).hexdigest()
    url = "https://cran.r-project.org/src/contrib/Archive/lme4/lme4_1.1-35.1.tar.gz"
    _patch_urlopen(monkeypatch, {url: tar_bytes})

    mp = tmp_path / "manifest.csv"
    _write_manifest(
        mp,
        [["", "cran", "lme4", "1.1-35.1", "lme4/vignettes/lmer.tex", "cran_lme4_1.1-35.1/", sha]],
    )

    gaps = tmp_path / "gaps.csv"
    code = corpus.run_fetch(
        manifest_path=mp, target_dir=tmp_path / "examples", gaps_path=gaps
    )

    assert code == 0
    extracted = tmp_path / "examples" / "cran_lme4_1.1-35.1" / "lme4" / "vignettes" / "lmer.tex"
    assert extracted.exists()
    assert extracted.read_text(encoding="utf-8").startswith("\\documentclass{jss}")
    # Gaps file should exist (written every run) but be header-only.
    assert gaps.exists()
    assert gaps.read_text(encoding="utf-8").count("\n") == 1  # header only


def test_fetch_hash_mismatch_logs_gap(monkeypatch, tmp_path: Path) -> None:
    tar_bytes = _build_fake_tar([("paper.tex", b"content")])
    wrong_sha = "0" * 64
    url = "https://cran.r-project.org/src/contrib/Archive/foo/foo_1.0.tar.gz"
    _patch_urlopen(monkeypatch, {url: tar_bytes})

    mp = tmp_path / "m.csv"
    _write_manifest(
        mp,
        [["", "cran", "foo", "1.0", "paper.tex", "cran_foo_1.0/", wrong_sha]],
    )
    gaps = tmp_path / "gaps.csv"
    code = corpus.run_fetch(manifest_path=mp, target_dir=tmp_path / "ex", gaps_path=gaps)

    assert code == 1  # gaps file is non-empty
    gaps_text = gaps.read_text(encoding="utf-8")
    assert "hash mismatch" in gaps_text
    # No file extracted.
    assert not (tmp_path / "ex" / "cran_foo_1.0").exists()


def test_fetch_jss_archive_logs_gap(tmp_path: Path) -> None:
    mp = tmp_path / "m.csv"
    _write_manifest(
        mp,
        [
            [
                "10.18637/jss.v092.i04", "jss_archive", "v092i04",
                "manual", "paper.tex", "jss_v092i04/", "a" * 64,
            ]
        ],
    )
    gaps = tmp_path / "gaps.csv"
    code = corpus.run_fetch(manifest_path=mp, target_dir=tmp_path / "ex", gaps_path=gaps)
    assert code == 1
    gaps_text = gaps.read_text(encoding="utf-8")
    assert "manual placement required" in gaps_text


def test_fetch_manual_row_is_no_op_if_present(tmp_path: Path) -> None:
    # A `manual` row points at a local file that must already exist. If
    # it does, fetch is a no-op; if not, a gap is logged.
    target = tmp_path / "ex" / "manual_x"
    target.mkdir(parents=True)
    (target / "paper.tex").write_text("manual", encoding="utf-8")

    mp = tmp_path / "m.csv"
    _write_manifest(
        mp,
        [["", "manual", "x", "manual", "paper.tex", "manual_x/", "a" * 64]],
    )
    gaps = tmp_path / "gaps.csv"
    code = corpus.run_fetch(manifest_path=mp, target_dir=tmp_path / "ex", gaps_path=gaps)
    assert code == 0


def test_fetch_skips_already_materialised_matching_hash(
    monkeypatch, tmp_path: Path
) -> None:
    """If local_path exists and its content hashes match, no fetch occurs."""
    target_root = tmp_path / "examples"
    paper_dir = target_root / "cran_foo_1.0"
    paper_dir.mkdir(parents=True)
    tar_bytes = _build_fake_tar([("paper.tex", b"existing")])
    # Write a sentinel — corpus.run_fetch uses hash of the directory's
    # contents OR a ".sha256" marker. We'll use the marker file approach
    # per the impl: write a `.sha256` sidecar so re-fetches skip.
    sha = hashlib.sha256(tar_bytes).hexdigest()
    (paper_dir / ".sha256").write_text(sha, encoding="utf-8")

    url = "https://cran.r-project.org/src/contrib/Archive/foo/foo_1.0.tar.gz"
    call_count = {"n": 0}

    def fake_urlopen(req, timeout=None):  # noqa: ARG001
        call_count["n"] += 1
        return _FakeResponse(tar_bytes)

    monkeypatch.setattr(corpus.urllib.request, "urlopen", fake_urlopen)

    mp = tmp_path / "m.csv"
    _write_manifest(
        mp,
        [["", "cran", "foo", "1.0", "paper.tex", "cran_foo_1.0/", sha]],
    )
    gaps = tmp_path / "gaps.csv"
    code = corpus.run_fetch(manifest_path=mp, target_dir=target_root, gaps_path=gaps)

    assert code == 0
    assert call_count["n"] == 0  # no fetch occurred


def test_tarslip_is_refused(monkeypatch, tmp_path: Path) -> None:
    """A tarball member whose path escapes the extraction dir must be refused."""
    # Build a malicious tar with "../escaped.tex"
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        info = tarfile.TarInfo(name="../escaped.tex")
        data = b"gotcha"
        info.size = len(data)
        tar.addfile(info, io.BytesIO(data))
    tar_bytes = buf.getvalue()
    sha = hashlib.sha256(tar_bytes).hexdigest()

    url = "https://cran.r-project.org/src/contrib/Archive/evil/evil_1.0.tar.gz"
    _patch_urlopen(monkeypatch, {url: tar_bytes})

    mp = tmp_path / "m.csv"
    _write_manifest(
        mp,
        [["", "cran", "evil", "1.0", "paper.tex", "cran_evil_1.0/", sha]],
    )
    gaps = tmp_path / "gaps.csv"
    code = corpus.run_fetch(manifest_path=mp, target_dir=tmp_path / "ex", gaps_path=gaps)

    assert code == 1
    gaps_text = gaps.read_text(encoding="utf-8")
    assert "tarslip" in gaps_text.lower() or "unsafe" in gaps_text.lower()
    # Nothing outside the target dir.
    assert not (tmp_path / "escaped.tex").exists()
