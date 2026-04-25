"""JSS archive scraper — uses OJS's OAI-PMH endpoint to fetch every
published JSS paper's metadata (title, DOI, subjects, creators) and
build a list of CRAN package candidates that have a JSS paper.

The scraped cache (`eval/jss-archive.json`) is then consulted by
``corpus suggest`` so it can surface known JSS-paper-counterpart
packages instead of random sampling.

OAI-PMH endpoint: https://www.jstatsoft.org/oai
Metadata format: oai_dc (Dublin Core)
Pagination: `resumptionToken` continues from the previous response.
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

_OAI_BASE = "https://www.jstatsoft.org/oai"
_OAI_NS = "{http://www.openarchives.org/OAI/2.0/}"
_DC_NS = "{http://purl.org/dc/elements/1.1/}"

_DOI_RE = re.compile(r"^10\.18637/jss\.v\d+\.i\d+$")

# Heuristic patterns that pull a candidate package name from a JSS
# paper title. JSS conventions:
#   "<title>, in <pkgname>" / "<pkgname>: <subtitle>"
#   "An R package <pkgname>"
#   "The <pkgname> package"
#   "<title> Using <pkgname>"
#
# Match the FIRST plausibly-package-named token (lowercase or mixed-case
# starting with a letter, allowed chars: letters, digits, dots, hyphens).
_TITLE_PKG_PATTERNS = [
    re.compile(r"^([A-Za-z][A-Za-z0-9.\-]{1,30})\s*:\s+"),  # "pkg: Subtitle"
    re.compile(r"\b(?:R [Pp]ackage|[Pp]ackage)\s+([A-Za-z][A-Za-z0-9.\-]{1,30})\b"),
    re.compile(r"\b([A-Za-z][A-Za-z0-9.\-]{1,30})\s+R [Pp]ackage\b"),
    re.compile(r"\b(?:[Pp]ackage|[Tt]he)\s+([A-Za-z][A-Za-z0-9.\-]{1,30})\b"),
]


@dataclass(frozen=True)
class JssPaper:
    doi: str
    title: str
    subjects: tuple[str, ...]
    article_url: str


def _fetch(url: str, timeout: float = 60.0) -> bytes:
    with urllib.request.urlopen(urllib.request.Request(url), timeout=timeout) as resp:
        return resp.read()


def _parse_records(xml_bytes: bytes) -> tuple[list[JssPaper], str | None]:
    """Return (papers, resumption_token).

    ``resumption_token`` is None when no more pages remain. Empty
    string would mean "more available but token was empty" which the
    OAI spec treats as terminal — we treat ``None`` and ``""`` the same.
    """
    import xml.etree.ElementTree as ET

    root = ET.fromstring(xml_bytes)
    list_records = root.find(f"{_OAI_NS}ListRecords")
    if list_records is None:
        return [], None
    papers: list[JssPaper] = []
    for record in list_records.findall(f"{_OAI_NS}record"):
        meta = record.find(f"{_OAI_NS}metadata")
        if meta is None:
            continue
        # oai_dc:dc element (qualified namespace).
        dc = meta.find("{http://www.openarchives.org/OAI/2.0/oai_dc/}dc")
        if dc is None:
            continue
        title = ""
        for t in dc.findall(f"{_DC_NS}title"):
            if t.text:
                title = t.text.strip()
                break
        subjects = tuple(
            s.text.strip() for s in dc.findall(f"{_DC_NS}subject") if s.text
        )
        doi = ""
        article_url = ""
        for ident in dc.findall(f"{_DC_NS}identifier"):
            if ident.text is None:
                continue
            v = ident.text.strip()
            if _DOI_RE.match(v):
                doi = v
            elif v.startswith("http") and "article/view/" in v:
                article_url = v
        if title and doi:
            papers.append(JssPaper(
                doi=doi, title=title,
                subjects=subjects, article_url=article_url,
            ))
    rt_elem = list_records.find(f"{_OAI_NS}resumptionToken")
    rt = rt_elem.text.strip() if (rt_elem is not None and rt_elem.text) else None
    return papers, rt


def fetch_all(
    *, since: str | None = None, max_pages: int = 100,
) -> list[JssPaper]:
    """Walk the OAI-PMH endpoint to completion and return every paper.

    `since` is an optional ISO-8601 date (YYYY-MM-DD) passed to the
    ``from`` parameter — useful for incremental refresh once a cache
    exists.
    """
    url = f"{_OAI_BASE}?verb=ListRecords&metadataPrefix=oai_dc"
    if since:
        url += f"&from={since}"
    out: list[JssPaper] = []
    for _ in range(max_pages):
        xml = _fetch(url)
        page, rt = _parse_records(xml)
        out.extend(page)
        if not rt:
            break
        url = f"{_OAI_BASE}?verb=ListRecords&resumptionToken={urllib.parse.quote(rt)}"
    return out


def candidate_pkg_from_paper(paper: JssPaper) -> str | None:
    """Best-effort extraction of a CRAN package name from a JSS paper.

    Tries (in order):
    1. Subjects that look like a package name (single token, contains
       at least one digit OR is lowercase-and-camel — heuristic for
       "vtree" / "ggplot2" / "lme4" etc.).
    2. Title patterns ("pkg: Subtitle", "the X package", etc.).

    Returns ``None`` when no plausible candidate surfaces.
    """
    # Subjects first — JSS authors often tag the package name as a subject.
    for subj in paper.subjects:
        if " " in subj or "(" in subj:
            continue  # multi-word — likely a topic, not a pkg name.
        # Plausibility: starts with letter, allowed chars, length 2-30.
        if re.fullmatch(r"[A-Za-z][A-Za-z0-9.\-]{1,30}", subj):
            # Drop ALL-CAPS (likely an acronym, not a CRAN package).
            if not subj.isupper():
                return subj
    # Fall back to title patterns.
    for pat in _TITLE_PKG_PATTERNS:
        m = pat.search(paper.title)
        if m:
            cand = m.group(1)
            # Filter out common stop-words that match the patterns.
            if cand.lower() in {
                "the", "a", "an", "of", "for", "and", "with", "in", "on",
                "to", "from", "by", "is", "as", "at", "or", "but", "if",
            }:
                continue
            return cand
    return None


def sync_to_cache(cache_path: Path, *, since: str | None = None) -> int:
    """Fetch the archive and write a cache file. Returns paper count."""
    papers = fetch_all(since=since)
    rows = []
    for p in papers:
        rows.append({
            "doi": p.doi,
            "title": p.title,
            "subjects": list(p.subjects),
            "article_url": p.article_url,
            "candidate_pkg": candidate_pkg_from_paper(p),
        })
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with cache_path.open("w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)
    return len(rows)


def load_cache(cache_path: Path) -> list[dict]:
    if not cache_path.is_file():
        return []
    with cache_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def candidate_packages(cache_path: Path) -> set[str]:
    """Return the set of distinct candidate package names from the cache."""
    return {row["candidate_pkg"]
            for row in load_cache(cache_path)
            if row.get("candidate_pkg")}


def cran_matched_candidates(cache_path: Path) -> list[str]:
    """Return candidates that actually exist on CRAN (sorted, deduped).

    Cross-checks ``candidate_packages(cache_path)`` against CRAN's
    PACKAGES index to drop heuristic false-positives like "A-optimality"
    (a topic, not a package name).
    """
    from eval.corpus import _CRAN_PACKAGES_URL, _parse_dcf, _stream_fetch

    body, _ = _stream_fetch(_CRAN_PACKAGES_URL)
    cran_pkgs = {
        rec.get("Package")
        for rec in _parse_dcf(body.decode("utf-8", errors="replace"))
        if rec.get("Package")
    }
    return sorted(candidate_packages(cache_path) & cran_pkgs)


# -----------------------------------------------------------------------------
# CLI entry points (wired from eval/cli.py)
# -----------------------------------------------------------------------------


def run_sync(*, cache_path: Path, since: str | None) -> int:
    print(f"eval-jss jss-archive sync: fetching from {_OAI_BASE} …")
    try:
        n = sync_to_cache(cache_path, since=since)
    except (urllib.error.URLError, TimeoutError) as err:
        print(f"eval-jss jss-archive sync: failed: {err}")
        return 2
    print(f"eval-jss jss-archive sync: cached {n} papers → {cache_path}")
    return 0


def run_packages(
    *, cache_path: Path, cran_matched: bool,
) -> int:
    cache = load_cache(cache_path)
    if not cache:
        print(
            f"eval-jss jss-archive packages: no cache at {cache_path}. "
            f"Run `eval-jss jss-archive sync` first."
        )
        return 2
    if cran_matched:
        pkgs = cran_matched_candidates(cache_path)
        print(
            f"# {len(pkgs)} JSS candidates that exist on CRAN "
            f"(out of {sum(1 for r in cache if r.get('candidate_pkg'))} extracted)"
        )
    else:
        pkgs = sorted({row["candidate_pkg"]
                       for row in cache if row.get("candidate_pkg")})
        print(f"# {len(pkgs)} distinct candidate packages out of {len(cache)} papers")
    for p in pkgs:
        print(p)
    return 0
