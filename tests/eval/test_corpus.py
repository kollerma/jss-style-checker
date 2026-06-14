"""Tests for `eval.corpus` — manifest parse, URL derivation, SHA256 verify, tarslip.

Spec FR-024, FR-025, FR-026. No real network — `urllib.request.urlopen`
is monkeypatched.
"""

from __future__ import annotations

import hashlib
import io
import tarfile
from pathlib import Path

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
            [
                "10.18637/jss.v001.i01",
                "cran",
                "foo",
                "1.0.0",
                "paper.tex",
                "cran_foo_1.0.0/",
                "a" * 64,
            ],
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

    def __enter__(self) -> _FakeResponse:
        return self

    def __exit__(self, *args: object) -> None:
        pass


def _patch_urlopen(monkeypatch, url_to_bytes: dict[str, bytes]) -> None:
    def fake_urlopen(req, timeout=None):  # noqa: ARG001 — signature compat
        url = req.full_url if hasattr(req, "full_url") else req
        if url not in url_to_bytes:
            # Mirror real-world behaviour: unmapped URLs return 404.
            # This lets the cran-fetch fallback (current URL → Archive
            # URL) walk through both options when only one is mapped.
            raise corpus.urllib.error.HTTPError(
                url, 404, "Not Found", hdrs=None, fp=None,
            )
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


# -----------------------------------------------------------------------------
# GitHub source — commit-pinned manuscript extracted into vignettes/
# -----------------------------------------------------------------------------


_GH_SHA = "c075a0dbc2a4ecaef8120e10fd53694007d2e10a"
_GH_MANUSCRIPT = b"\\documentclass[article]{jss}\n"
_GH_MANUSCRIPT_SHA = hashlib.sha256(_GH_MANUSCRIPT).hexdigest()


def _github_tar() -> bytes:
    """A fake GitHub archive: a `<repo>-<sha>/` prefix with a paper dir."""
    prefix = f"opentsne-paper-{_GH_SHA}"
    return _build_fake_tar([
        (f"{prefix}/paper/main.tex", _GH_MANUSCRIPT),
        (f"{prefix}/paper/references.bib", b"@article{x, title={t}}\n"),
        (f"{prefix}/paper/figure.pdf", b"%PDF-1.4 not source\n"),
        (f"{prefix}/2023-05-revision-1/main.tex", b"\\documentclass{jss}\n"),
        (f"{prefix}/README.md", b"# repo\n"),
    ])


def test_load_manifest_accepts_github_source(tmp_path: Path) -> None:
    mp = tmp_path / "m.csv"
    _write_manifest(
        mp,
        [["10.18637/jss.v109.i03", "github", "owner/repo",
          f"{_GH_SHA}:paper/main.tex", "vignettes/main.tex", "github_x/", ""]],
    )
    rows = corpus.load_manifest(mp)
    assert rows[0].source == "github"
    assert rows[0].version == f"{_GH_SHA}:paper/main.tex"


def test_fetch_github_extracts_manuscript_and_sibling_bib_into_vignettes(
    monkeypatch, tmp_path: Path
) -> None:
    tar_bytes = _github_tar()
    url = f"https://codeload.github.com/owner/repo/tar.gz/{_GH_SHA}"
    _patch_urlopen(monkeypatch, {url: tar_bytes})

    mp = tmp_path / "m.csv"
    # Integrity is pinned on the manuscript blob, not the tarball.
    _write_manifest(
        mp,
        [["10.18637/jss.v109.i03", "github", "owner/repo",
          f"{_GH_SHA}:paper/main.tex", "vignettes/main.tex", "github_x/",
          _GH_MANUSCRIPT_SHA]],
    )
    gaps = tmp_path / "gaps.csv"
    code = corpus.run_fetch(
        manifest_path=mp, target_dir=tmp_path / "ex", gaps_path=gaps
    )

    assert code == 0
    vdir = tmp_path / "ex" / "github_x" / "vignettes"
    # Manuscript + its sibling bib are flattened into vignettes/ …
    assert (vdir / "main.tex").read_text().startswith("\\documentclass")
    assert (vdir / "references.bib").exists()
    # … and nothing else travels: no figures, no README, no other-dir main.tex.
    assert sorted(p.name for p in vdir.iterdir()) == ["main.tex", "references.bib"]


def test_fetch_github_hash_mismatch_logs_gap(monkeypatch, tmp_path: Path) -> None:
    tar_bytes = _github_tar()
    url = f"https://codeload.github.com/owner/repo/tar.gz/{_GH_SHA}"
    _patch_urlopen(monkeypatch, {url: tar_bytes})

    mp = tmp_path / "m.csv"
    _write_manifest(
        mp,
        [["", "github", "owner/repo", f"{_GH_SHA}:paper/main.tex",
          "vignettes/main.tex", "github_x/", "0" * 64]],
    )
    gaps = tmp_path / "gaps.csv"
    code = corpus.run_fetch(manifest_path=mp, target_dir=tmp_path / "ex", gaps_path=gaps)

    assert code == 1
    assert "hash mismatch" in gaps.read_text(encoding="utf-8").lower()


def test_fetch_github_missing_manuscript_logs_gap(monkeypatch, tmp_path: Path) -> None:
    tar_bytes = _github_tar()
    url = f"https://codeload.github.com/owner/repo/tar.gz/{_GH_SHA}"
    _patch_urlopen(monkeypatch, {url: tar_bytes})

    mp = tmp_path / "m.csv"
    # Wrong in-repo path: the manuscript is never found, so the fetch gaps
    # out before any hash check — the sha256 value is irrelevant here.
    _write_manifest(
        mp,
        [["", "github", "owner/repo", f"{_GH_SHA}:paper/nope.tex",
          "vignettes/nope.tex", "github_x/", _GH_MANUSCRIPT_SHA]],
    )
    gaps = tmp_path / "gaps.csv"
    code = corpus.run_fetch(manifest_path=mp, target_dir=tmp_path / "ex", gaps_path=gaps)

    assert code == 1
    assert "not found" in gaps.read_text(encoding="utf-8").lower()


def test_fetch_github_rejects_malformed_version(monkeypatch, tmp_path: Path) -> None:
    # No colon ⇒ no in-repo path ⇒ gap, without any network call.
    mp = tmp_path / "m.csv"
    _write_manifest(
        mp,
        [["", "github", "owner/repo", _GH_SHA, "vignettes/main.tex", "github_x/", ""]],
    )
    gaps = tmp_path / "gaps.csv"
    code = corpus.run_fetch(manifest_path=mp, target_dir=tmp_path / "ex", gaps_path=gaps)

    assert code == 1
    assert "in-repo-path" in gaps.read_text(encoding="utf-8")


# -----------------------------------------------------------------------------
# JSS-only suggestion filter
# -----------------------------------------------------------------------------


def _packages_dcf(records: list[dict[str, str]]) -> bytes:
    """Render a minimal CRAN PACKAGES blob from in-memory records."""
    chunks: list[str] = []
    for rec in records:
        chunks.append("\n".join(f"{k}: {v}" for k, v in rec.items()))
    return ("\n\n".join(chunks) + "\n").encode("utf-8")


def test_probe_jss_vignette_accepts_class_plus_inline_journal(
    monkeypatch, tmp_path: Path
) -> None:
    rnw = (
        b"\\documentclass[nojss]{jss}\n"
        b"% see Journal of Statistical Software, Smith (2020)\n"
        b"\\begin{document}\\end{document}\n"
    )
    tar_bytes = _build_fake_tar([("foo/vignettes/foo.Rnw", rnw)])
    url = "https://cran.r-project.org/src/contrib/foo_1.0.tar.gz"
    _patch_urlopen(monkeypatch, {url: tar_bytes})

    match = corpus._probe_jss_vignette("foo", "1.0")
    assert match == "foo/vignettes/foo.Rnw"


def test_probe_jss_vignette_accepts_sibling_bib(monkeypatch, tmp_path: Path) -> None:
    rnw = b"\\documentclass{jss}\n\\cite{smith2020}\n"
    bib = b"@article{smith2020, journal = {Journal of Statistical Software}}\n"
    tar_bytes = _build_fake_tar(
        [("bar/vignettes/bar.Rnw", rnw), ("bar/vignettes/refs.bib", bib)]
    )
    url = "https://cran.r-project.org/src/contrib/bar_2.0.tar.gz"
    _patch_urlopen(monkeypatch, {url: tar_bytes})

    match = corpus._probe_jss_vignette("bar", "2.0")
    assert match == "bar/vignettes/bar.Rnw"


def test_probe_jss_vignette_rejects_plain_cran_vignette(
    monkeypatch, tmp_path: Path
) -> None:
    # No `jss` class loaded — must be rejected even with a JSS-ish bib.
    rmd = b"---\ntitle: My Package\n---\n# intro\n"
    bib = b"@article{x, journal = {Journal of Statistical Software}}\n"
    tar_bytes = _build_fake_tar(
        [("baz/vignettes/baz.Rmd", rmd), ("baz/vignettes/refs.bib", bib)]
    )
    url = "https://cran.r-project.org/src/contrib/baz_3.0.tar.gz"
    _patch_urlopen(monkeypatch, {url: tar_bytes})

    assert corpus._probe_jss_vignette("baz", "3.0") is None


def test_probe_jss_vignette_rejects_jss_class_without_citation(
    monkeypatch, tmp_path: Path
) -> None:
    # `jss` class loaded but no JSS reference in vignette or any .bib.
    rnw = b"\\documentclass{jss}\n% no journal mention\n"
    tar_bytes = _build_fake_tar([("qux/vignettes/qux.Rnw", rnw)])
    url = "https://cran.r-project.org/src/contrib/qux_4.0.tar.gz"
    _patch_urlopen(monkeypatch, {url: tar_bytes})

    assert corpus._probe_jss_vignette("qux", "4.0") is None


def test_probe_jss_vignette_handles_fetch_error(monkeypatch) -> None:
    import urllib.error

    def fake_urlopen(req, timeout=None):  # noqa: ARG001
        raise urllib.error.URLError("boom")

    monkeypatch.setattr(corpus.urllib.request, "urlopen", fake_urlopen)
    assert corpus._probe_jss_vignette("nope", "0.1") is None


def test_run_suggest_jss_only_filters_and_emits_vignette_column(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    # Two candidates from PACKAGES: only `goodpkg` carries a JSS vignette.
    packages_blob = _packages_dcf(
        [
            {"Package": "goodpkg", "Version": "1.0", "Suggests": "knitr"},
            {"Package": "badpkg", "Version": "2.0", "Suggests": "knitr"},
        ]
    )
    good_rnw = (
        b"\\documentclass[nojss]{jss}\n"
        b"% Journal of Statistical Software\n"
    )
    bad_rmd = b"---\ntitle: Plain\n---\n# intro\n"
    good_tar = _build_fake_tar([("goodpkg/vignettes/good.Rnw", good_rnw)])
    bad_tar = _build_fake_tar([("badpkg/vignettes/bad.Rmd", bad_rmd)])

    url_to_bytes = {
        "https://cran.r-project.org/src/contrib/PACKAGES": packages_blob,
        "https://cran.r-project.org/src/contrib/goodpkg_1.0.tar.gz": good_tar,
        "https://cran.r-project.org/src/contrib/badpkg_2.0.tar.gz": bad_tar,
    }
    _patch_urlopen(monkeypatch, url_to_bytes)

    mp = tmp_path / "manifest.csv"
    _write_manifest(mp, [])

    code = corpus.run_suggest(
        manifest_path=mp,
        limit=5,
        seed=0,
        verify=False,
        jss_only=True,
        from_jss_archive=False,
        from_cran_github=False,
    )
    assert code == 0
    out = capsys.readouterr().out
    assert "vignette_file" in out  # 4-column header
    assert "goodpkg\t1.0\tknitr\tgoodpkg/vignettes/good.Rnw" in out
    assert "badpkg" not in out


def test_run_suggest_no_jss_only_keeps_three_column_format(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    packages_blob = _packages_dcf(
        [{"Package": "anypkg", "Version": "9.9", "Suggests": "knitr"}]
    )
    _patch_urlopen(
        monkeypatch,
        {"https://cran.r-project.org/src/contrib/PACKAGES": packages_blob},
    )

    mp = tmp_path / "manifest.csv"
    _write_manifest(mp, [])

    code = corpus.run_suggest(
        manifest_path=mp,
        limit=5,
        seed=0,
        verify=False,
        jss_only=False,
        from_jss_archive=False,
        from_cran_github=False,
    )
    assert code == 0
    out = capsys.readouterr().out
    assert "# columns: package\tversion\tbuilder_hint\n" in out
    assert "vignette_file" not in out
    assert "anypkg\t9.9\tknitr\n" in out


def test_run_suggest_curated_pool_keeps_sweave_default_packages(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    """Regression: classic JSS-counterpart packages like ``coin`` ship
    Sweave ``.Rnw`` vignettes without declaring ``knitr``/``rmarkdown``/
    ``sweave`` in DCF deps (Sweave is R's built-in default). The DCF
    builder-hint pre-filter must be skipped when a curated pool is
    supplied; the curated pool plus the JSS vignette tarball probe are
    the real filters in that mode.
    """
    packages_blob = _packages_dcf(
        [
            # Sweave default — no builder keyword anywhere in deps.
            {"Package": "coinlike", "Version": "1.0", "Suggests": "xtable"},
        ]
    )
    rnw = (
        b"\\documentclass[nojss]{jss}\n"
        b"% see Journal of Statistical Software, Smith (2020)\n"
    )
    tar_bytes = _build_fake_tar([("coinlike/vignettes/coinlike.Rnw", rnw)])

    _patch_urlopen(
        monkeypatch,
        {
            "https://cran.r-project.org/src/contrib/PACKAGES": packages_blob,
            "https://cran.r-project.org/src/contrib/coinlike_1.0.tar.gz": tar_bytes,
        },
    )

    # Stand in a fake jss-archive cache that surfaces ``coinlike``.
    archive_cache = tmp_path / "jss-archive.json"
    archive_cache.write_text(
        '[{"doi": "10.18637/jss.v999.i01", "candidate_pkg": "coinlike"}]',
        encoding="utf-8",
    )

    mp = tmp_path / "manifest.csv"
    _write_manifest(mp, [])

    code = corpus.run_suggest(
        manifest_path=mp,
        limit=5,
        seed=0,
        verify=False,
        jss_only=True,
        from_jss_archive=True,
        jss_archive_cache=archive_cache,
        from_cran_github=False,
    )
    assert code == 0
    out = capsys.readouterr().out
    assert "coinlike\t1.0\tsweave\tcoinlike/vignettes/coinlike.Rnw" in out
