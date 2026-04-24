"""Corpus reproducibility (Phase B).

- `load_manifest(path)` parses `eval/corpus-manifest.csv` per
  `contracts/corpus-manifest.md` with strict header + per-row validation.
- `run_fetch(manifest_path, target_dir, gaps_path)` materialises every
  manifest row from an immutable distribution URL, verifies SHA256,
  refuses tarslip extraction, and records unreachable / mismatched
  rows in `corpus-manifest-gaps.csv`.
- `run_status(...)` reports per-row state without fetching.

Discovery sources (GitHub code search, arXiv listing API, etc.) are
deliberately NOT implemented here — see research.md §"Discovery is NOT
in this spec".
"""

from __future__ import annotations

import csv
import hashlib
import io
import shutil
import tarfile
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from eval import db

MANIFEST_HEADER = [
    "jss_doi",
    "source",
    "source_id",
    "version",
    "vignette_file",
    "local_path",
    "sha256",
]

VALID_SOURCES = {"cran", "bioc", "arxiv", "jss_archive", "manual", "swh"}


class ManifestError(Exception):
    """Raised when the manifest fails validation."""


@dataclass(frozen=True)
class ManifestRow:
    jss_doi: str | None
    source: str
    source_id: str
    version: str
    vignette_file: str
    local_path: Path
    sha256: str


# -----------------------------------------------------------------------------
# Manifest parsing
# -----------------------------------------------------------------------------


def load_manifest(path: Path) -> list[ManifestRow]:
    """Parse and validate the manifest at `path`. Raises `ManifestError`."""
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            raise ManifestError(f"{path}: empty manifest") from None
        if header != MANIFEST_HEADER:
            raise ManifestError(
                f"{path}: header {header!r} != {MANIFEST_HEADER!r}"
            )
        rows = list(reader)

    parsed: list[ManifestRow] = []
    seen_local_paths: set[str] = set()
    for lineno, raw in enumerate(rows, start=2):  # +1 for header, +1 for 1-based
        if len(raw) != len(MANIFEST_HEADER):
            raise ManifestError(
                f"{path}:{lineno}: {len(raw)} columns, expected {len(MANIFEST_HEADER)}"
            )
        doi, source, src_id, version, vignette, local, sha = raw
        if source not in VALID_SOURCES:
            raise ManifestError(
                f"{path}:{lineno}: source {source!r} not in {sorted(VALID_SOURCES)}"
            )
        if local.startswith("/") or local.startswith("~"):
            raise ManifestError(
                f"{path}:{lineno}: local_path {local!r} must be relative"
            )
        if local in seen_local_paths:
            raise ManifestError(
                f"{path}:{lineno}: local_path {local!r} duplicated"
            )
        seen_local_paths.add(local)
        if sha and (len(sha) != 64 or not all(c in "0123456789abcdef" for c in sha)):
            raise ManifestError(
                f"{path}:{lineno}: sha256 must be 64 hex chars or empty (got {sha!r})"
            )
        parsed.append(
            ManifestRow(
                jss_doi=doi or None,
                source=source,
                source_id=src_id,
                version=version,
                vignette_file=vignette,
                local_path=Path(local),
                sha256=sha,
            )
        )
    return parsed


# -----------------------------------------------------------------------------
# URL derivation
# -----------------------------------------------------------------------------


def _resolve_url(row: ManifestRow) -> str | None:
    """Build an immutable, version-pinned distribution URL for `row`.

    Returns `None` for rows whose source requires manual placement
    (`jss_archive`, `manual`) or is otherwise not auto-fetchable.
    """
    if row.source == "cran":
        return (
            "https://cran.r-project.org/src/contrib/Archive/"
            f"{row.source_id}/{row.source_id}_{row.version}.tar.gz"
        )
    if row.source == "bioc":
        # Bioc stores a package's current release at a versioned URL; the exact
        # tarball filename matches pattern `{source_id}_{pkg_version}.tar.gz`
        # where `pkg_version` is distinct from the Bioc release version.
        # Authors must put the per-release pkg_version in `version` for the
        # formula to resolve. Treat the row's `version` as that pkg_version.
        return (
            f"https://bioconductor.org/packages/release/bioc/src/contrib/"
            f"{row.source_id}_{row.version}.tar.gz"
        )
    if row.source == "arxiv":
        return f"http://arxiv.org/e-print/{row.source_id}{row.version}"
    if row.source == "swh":
        return (
            "https://archive.softwareheritage.org/api/1/content/"
            f"{row.version}/raw/"
        )
    # `jss_archive` and `manual` require offline placement.
    return None


# -----------------------------------------------------------------------------
# Fetch + verify + extract
# -----------------------------------------------------------------------------


@dataclass
class _Gap:
    manifest_row: int
    source: str
    source_id: str
    version: str
    reason: str


def _stream_fetch(url: str, timeout: float = 60.0) -> tuple[bytes, str]:
    """Download `url`, return (body_bytes, sha256_hex)."""
    req = urllib.request.Request(url)
    h = hashlib.sha256()
    chunks: list[bytes] = []
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        while True:
            chunk = resp.read(65536)
            if not chunk:
                break
            h.update(chunk)
            chunks.append(chunk)
    return b"".join(chunks), h.hexdigest()


def _safe_extract(tar_bytes: bytes, target: Path) -> None:
    """Extract the tarball with a tarslip defence.

    Any member whose resolved path escapes `target` → `ManifestError`.
    """
    target.mkdir(parents=True, exist_ok=True)
    target_resolved = target.resolve()
    buf = io.BytesIO(tar_bytes)
    with tarfile.open(fileobj=buf, mode="r:*") as tar:
        members = tar.getmembers()
        for m in members:
            dest = (target / m.name).resolve()
            try:
                dest.relative_to(target_resolved)
            except ValueError:
                raise ManifestError(
                    f"tarslip: member {m.name!r} escapes {target}"
                ) from None
        tar.extractall(path=target)


def _check_existing(target_paper_dir: Path, expected_sha: str) -> bool:
    """If `.sha256` marker matches `expected_sha`, treat as already materialised."""
    marker = target_paper_dir / ".sha256"
    if not marker.exists():
        return False
    try:
        return marker.read_text(encoding="utf-8").strip() == expected_sha
    except OSError:
        return False


def _write_sha_marker(target_paper_dir: Path, sha: str) -> None:
    target_paper_dir.mkdir(parents=True, exist_ok=True)
    (target_paper_dir / ".sha256").write_text(sha, encoding="utf-8")


def _fetch_one(row: ManifestRow, target_dir: Path) -> _Gap | None:
    """Materialise one row under `target_dir`. Returns a `_Gap` on failure, else `None`."""
    paper_dir = target_dir / row.local_path

    if _check_existing(paper_dir, row.sha256):
        return None

    if row.source == "jss_archive":
        return _Gap(
            manifest_row=0, source=row.source, source_id=row.source_id,
            version=row.version, reason="manual placement required",
        )

    if row.source == "manual":
        # Nothing to fetch; success iff the vignette file already exists.
        if (paper_dir / row.vignette_file).exists():
            # Record the expected hash as the marker so future runs skip.
            if row.sha256:
                _write_sha_marker(paper_dir, row.sha256)
            return None
        return _Gap(
            manifest_row=0, source=row.source, source_id=row.source_id,
            version=row.version,
            reason=f"manual: {row.vignette_file} missing at {paper_dir}",
        )

    url = _resolve_url(row)
    if url is None:
        return _Gap(
            manifest_row=0, source=row.source, source_id=row.source_id,
            version=row.version, reason=f"no fetcher for source {row.source!r}",
        )

    try:
        data, actual_sha = _stream_fetch(url)
    except urllib.error.HTTPError as err:
        return _Gap(
            manifest_row=0, source=row.source, source_id=row.source_id,
            version=row.version, reason=f"http {err.code}",
        )
    except (urllib.error.URLError, TimeoutError, ConnectionError) as err:
        return _Gap(
            manifest_row=0, source=row.source, source_id=row.source_id,
            version=row.version, reason=f"network: {type(err).__name__}",
        )

    if row.sha256 and actual_sha != row.sha256:
        return _Gap(
            manifest_row=0, source=row.source, source_id=row.source_id,
            version=row.version,
            reason=f"hash mismatch: expected {row.sha256}, got {actual_sha}",
        )

    try:
        _safe_extract(data, paper_dir)
    except ManifestError as err:
        # Destroy any partial extraction on safety failure.
        if paper_dir.exists():
            shutil.rmtree(paper_dir, ignore_errors=True)
        return _Gap(
            manifest_row=0, source=row.source, source_id=row.source_id,
            version=row.version, reason=str(err),
        )
    except tarfile.TarError as err:
        return _Gap(
            manifest_row=0, source=row.source, source_id=row.source_id,
            version=row.version, reason=f"unreadable archive: {err}",
        )

    _write_sha_marker(paper_dir, actual_sha)
    return None


def _write_gaps(gaps_path: Path, gaps: list[_Gap]) -> None:
    with gaps_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["manifest_row", "source", "source_id", "version", "reason", "ts"])
        ts = db.now_utc()
        for g in gaps:
            w.writerow([g.manifest_row, g.source, g.source_id, g.version, g.reason, ts])


# -----------------------------------------------------------------------------
# Public entry points
# -----------------------------------------------------------------------------


def run_fetch(
    *, manifest_path: Path, target_dir: Path, gaps_path: Path
) -> int:
    """Materialise every manifest row. Returns the CLI exit code."""
    try:
        rows = load_manifest(manifest_path)
    except ManifestError as err:
        print(f"eval-jss: malformed manifest: {err}")
        return 2

    gaps: list[_Gap] = []
    for i, row in enumerate(rows, start=1):
        gap = _fetch_one(row, target_dir)
        if gap is not None:
            # Fill in the manifest_row index for reporting clarity.
            gap = _Gap(
                manifest_row=i,
                source=gap.source,
                source_id=gap.source_id,
                version=gap.version,
                reason=gap.reason,
            )
            gaps.append(gap)

    _write_gaps(gaps_path, gaps)
    return 1 if gaps else 0


_CRAN_PACKAGES_URL = "https://cran.r-project.org/src/contrib/PACKAGES"


def _parse_dcf(text: str) -> list[dict[str, str]]:
    """Parse CRAN DCF (Debian-Control-File) format.

    Records are separated by blank lines; fields are `Key: value`;
    continuation lines begin with whitespace and append to the previous
    field. We flatten continuations to a single string per field.
    """
    records: list[dict[str, str]] = []
    current: dict[str, str] = {}
    last_key: str | None = None
    for line in text.splitlines():
        if not line.strip():
            if current:
                records.append(current)
                current = {}
                last_key = None
            continue
        if line[0] in (" ", "\t") and last_key is not None:
            current[last_key] += " " + line.strip()
            continue
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        current[key] = val.strip()
        last_key = key
    if current:
        records.append(current)
    return records


_BUILDER_HINTS = ("knitr", "rmarkdown", "sweave")
_VIGNETTE_MARKER = "Vignettes:"


def _has_builder_hint(rec: dict[str, str]) -> bool:
    blob = " ".join(rec.get(k, "") for k in ("Suggests", "Imports", "Depends"))
    low = blob.lower()
    return any(kw in low for kw in _BUILDER_HINTS)


def _probe_has_vignette(pkg: str, timeout: float = 10.0) -> bool:
    """Fetch the CRAN package landing page and check for a Vignettes row.

    CRAN renders `https://cran.r-project.org/web/packages/<pkg>/` with a
    stable summary table; the presence of a `Vignettes:` label cell
    signals at least one source vignette. Falls back to `False` on any
    transport error.
    """
    url = f"https://cran.r-project.org/web/packages/{pkg}/"
    try:
        with urllib.request.urlopen(urllib.request.Request(url), timeout=timeout) as resp:
            body = resp.read(131072).decode("utf-8", errors="replace")
    except (urllib.error.URLError, TimeoutError):
        return False
    return _VIGNETTE_MARKER in body


def run_suggest(
    *,
    manifest_path: Path,
    limit: int,
    seed: int | None,
    verify: bool,
    packages_url: str = _CRAN_PACKAGES_URL,
) -> int:
    """Print candidate CRAN packages not already in the manifest.

    CRAN's PACKAGES index does not expose the `VignetteBuilder` field
    directly, so the coarse filter checks for `knitr` / `rmarkdown` /
    `Sweave` anywhere in `Suggests` / `Imports` / `Depends` — the common
    signal that a package ships a vignette. With `verify=True`, each
    candidate's CRAN landing page is probed for a `Vignettes:` row to
    drop false positives before printing.

    Output: `<package>\\t<version>\\t<builder_hint>` lines, one per
    suggestion — the columns `/eval:add-corpus` consumes.

    `seed` makes the selection deterministic for reproducibility. If
    `None`, the OS random source picks.
    """
    import random

    try:
        existing = {row.source_id for row in load_manifest(manifest_path)}
    except FileNotFoundError:
        existing = set()

    try:
        body, _sha = _stream_fetch(packages_url)
    except urllib.error.URLError as err:
        print(f"eval-jss: failed to fetch CRAN PACKAGES: {err}")
        return 2

    candidates: list[tuple[str, str, str]] = []
    for rec in _parse_dcf(body.decode("utf-8", errors="replace")):
        name = rec.get("Package")
        version = rec.get("Version")
        if not (name and version):
            continue
        if name in existing:
            continue
        if not _has_builder_hint(rec):
            continue
        blob = " ".join(rec.get(k, "") for k in ("Suggests", "Imports", "Depends")).lower()
        hit = next((kw for kw in _BUILDER_HINTS if kw in blob), "knitr")
        candidates.append((name, version, hit))

    if not candidates:
        print("eval-jss: no new CRAN packages to suggest.")
        return 0

    rng = random.Random(seed)
    # Over-sample so the verify step has room to drop false positives.
    pool_size = min(limit * (4 if verify else 1), len(candidates))
    pool = rng.sample(candidates, pool_size)

    picked: list[tuple[str, str, str]] = []
    for name, version, hit in pool:
        if verify and not _probe_has_vignette(name):
            continue
        picked.append((name, version, hit))
        if len(picked) >= limit:
            break
    picked.sort(key=lambda t: t[0].lower())

    suffix = " (verified via CRAN landing-page probe)" if verify else " (unverified — coarse filter only)"
    print(
        f"# {len(picked)} suggestions of {len(candidates)} eligible; "
        f"{len(existing)} already pinned{suffix}"
    )
    print("# columns: package\tversion\tbuilder_hint")
    for name, version, hit in picked:
        print(f"{name}\t{version}\t{hit}")
    return 0


def run_status(*, manifest_path: Path, target_dir: Path) -> int:
    """Report which manifest rows are materialised, pending, or mismatched."""
    try:
        rows = load_manifest(manifest_path)
    except ManifestError as err:
        print(f"eval-jss: malformed manifest: {err}")
        return 2

    from rich.console import Console
    from rich.table import Table

    table = Table(title="Corpus status")
    table.add_column("Source")
    table.add_column("ID")
    table.add_column("Version")
    table.add_column("State")

    any_pending = False
    for row in rows:
        paper_dir = target_dir / row.local_path
        if _check_existing(paper_dir, row.sha256):
            state = "[green]OK[/green]"
        elif row.source in ("jss_archive",):
            state = "[yellow]manual placement required[/yellow]"
            any_pending = True
        else:
            state = "[yellow]pending[/yellow]"
            any_pending = True
        table.add_row(row.source, row.source_id, row.version, state)

    Console().print(table)
    return 1 if any_pending else 0
