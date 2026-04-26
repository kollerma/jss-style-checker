"""CRAN-mirror GitHub Code Search fetcher — finds JSS-paper-counterpart
vignettes by querying the `github.com/cran` org for files containing
``\\documentclass{jss}`` and harvesting each match's
``(package, vignette_path)``.

Complements `eval/jss_archive.py`'s OAI-PMH route, which cross-references
JSS paper titles against CRAN's PACKAGES index and hits ~903 candidates
(~463 cross-confirmed). The Code-Search route is more direct: anything
that loads the ``jss`` LaTeX class on the cran mirror is, by definition,
a JSS-counterpart candidate vignette.

GitHub Code Search REST API: https://api.github.com/search/code
Auth: ``GITHUB_TOKEN`` env var (a PAT with `public_repo` scope is enough).
Per-query cap: 1000 results; 100/page; 30 req/min for code search.

The scraped cache (`eval/cran-github.json`) shares the role of
`eval/jss-archive.json`: a candidate pool ``corpus suggest`` can prefer
over random sampling. Each row is ``(package, vignette_path)`` so it
plugs directly into the same ``_probe_jss_vignette`` invariant used
elsewhere (see `eval/corpus.py`).
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

_API_BASE = "https://api.github.com/search/code"
_USER_AGENT = "jss-lint-cran-github-fetcher/0.1"

# Literal substring we ask GitHub Code Search to find. ``{jss}`` is
# narrow enough to skip ``jssm`` / ``jssp`` and broad enough to match
# every JSS-class invocation: ``\documentclass{jss}``, ``[nojss]{jss}``,
# ``[article]{jss}``, etc. The previous, more specific
# ``"documentclass{jss}"`` literal saturated at 22 hits because the
# legacy code-search index doesn't tokenise ``\documentclass{...}`` as
# a phrase across many cran-mirror repos; loosening the literal and
# excluding obvious noise paths via ``NOT`` clauses recovers the long
# tail.
_QUERY_LITERAL = "{jss}"

# Suffixes we keep client-side. We do NOT use the GitHub Code Search
# ``extension:`` qualifier — empirically the legacy index treats
# ``extension:Rmd`` / ``extension:ltx`` / ``extension:tex`` as
# zero-hit even when there are obvious matches, because Code Search
# routes through a language index (Sweave / RMarkdown / TeX) rather
# than raw filename extensions. Filtering after the fetch is the only
# reliable way.
_KEEP_SUFFIXES = (".Rnw", ".Rmd", ".ltx", ".tex")

# Code Search is rate-limited at 30 req/min auth'd, but GitHub also
# applies an unannounced *secondary* abuse-rate-limit that throttles
# sustained crawls below the documented ceiling. Empirically 2 s/page
# trips the secondary limit on page ~10; 4 s/page lets a full 10-page
# walk complete.
_PAGE_SLEEP_SECONDS = 4.0
_PER_PAGE = 100
_MAX_PAGES = 10  # 100 * 10 = 1000, the API ceiling


@dataclass(frozen=True)
class GhCandidate:
    package: str         # e.g. "dplyr"
    vignette: str        # e.g. "vignettes/rowwise.Rnw"
    repo: str            # e.g. "cran/dplyr"
    html_url: str        # browser-viewable blob URL


class GhAuthError(RuntimeError):
    """Raised when ``GITHUB_TOKEN`` is missing or rejected."""


def _request(url: str, *, token: str, timeout: float = 60.0):
    """Issue a single GET; return ``(json_body, link_header)``.

    Raises ``GhAuthError`` on 401/403 with a clear message and surfaces
    other ``HTTPError``s with the response body attached for diagnosis
    (Code Search 422/500 responses include a ``message`` field that
    explains the actual problem — without it the failure is opaque).
    """
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github.text-match+json",
            "Authorization": f"Bearer {token}",
            "User-Agent": _USER_AGENT,
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            link = resp.headers.get("Link", "")
            return body, link
    except urllib.error.HTTPError as err:
        try:
            err_body = err.read().decode("utf-8", errors="replace")
        except Exception:
            err_body = ""
        if err.code in (401, 403):
            raise GhAuthError(
                f"GitHub returned {err.code} for {url}: "
                f"check GITHUB_TOKEN scope (needs `public_repo`) and "
                f"that you are not rate-limited.\nbody: {err_body[:400]}"
            ) from err
        # Re-raise with the body attached so callers can show GitHub's
        # explanation ("Validation Failed", "search query is invalid", etc.).
        raise urllib.error.HTTPError(
            url, err.code, f"{err.reason}\nbody: {err_body[:600]}",
            err.headers, None,
        ) from err


def _next_url_from_link(link_header: str) -> str | None:
    """Parse the ``Link`` header for ``rel=\"next\"``. Returns ``None`` when absent."""
    if not link_header:
        return None
    for part in link_header.split(","):
        section = part.strip()
        if not section.startswith("<"):
            continue
        url_part, _, rest = section.partition(">")
        url = url_part.lstrip("<").strip()
        if 'rel="next"' in rest:
            return url
    return None


def _build_initial_url() -> str:
    """Build the first-page URL for the single combined query.

    Code Search syntax: ``org:cran {jss} NOT language:HTML
    NOT language:R NOT path:*.cls``.

    - ``{jss}`` matches every JSS-class invocation (broad literal).
    - ``NOT language:HTML`` strips knit-rendered vignettes (the same
      ``{jss}`` text reappears verbatim in the rendered HTML).
    - ``NOT language:R`` strips ``.R`` files where ``{jss}`` only shows
      up inside a string or roxygen comment.
    - ``NOT path:*.cls`` strips ``jss.cls`` itself — the JSS class file
      defines the macros and would otherwise match every package that
      vendors it.

    The ``cran`` mirror is an organisation, not a user — the legacy
    code-search backend 500s on ``user:cran``. Stick with ``org:``.
    """
    q = (
        f"org:cran {_QUERY_LITERAL} "
        "NOT language:HTML NOT language:R NOT path:*.cls"
    )
    params = {"q": q, "per_page": str(_PER_PAGE)}
    return f"{_API_BASE}?{urllib.parse.urlencode(params)}"


def _candidate_from_item(item: dict) -> GhCandidate | None:
    """Convert one Code Search ``items[]`` row to a ``GhCandidate``.

    Returns ``None`` for rows we cannot parse (e.g. malformed repo
    name, path with no segments). The ``cran`` mirror's convention is
    one repo per package — ``cran/<pkgname>`` — and vignettes live at
    ``vignettes/...`` or ``inst/doc/...``.
    """
    repo_obj = item.get("repository") or {}
    full_name = repo_obj.get("full_name") or ""
    if not full_name.startswith("cran/"):
        return None
    package = full_name.split("/", 1)[1]
    if not package:
        return None
    path = item.get("path") or ""
    if not path:
        return None
    html_url = item.get("html_url") or ""
    return GhCandidate(
        package=package, vignette=path, repo=full_name, html_url=html_url,
    )


def fetch_all(*, token: str, max_pages: int = _MAX_PAGES) -> list[GhCandidate]:
    """Walk all result pages for the single combined query and return
    the matched, suffix-filtered candidates.

    Stops at ``max_pages`` (1000 results, the API's per-query ceiling)
    or when the ``Link`` header omits a ``rel=next``. Sleeps
    ``_PAGE_SLEEP_SECONDS`` between pages to stay under the 30 req/min
    code-search cap. Keeps only paths ending in
    :data:`_KEEP_SUFFIXES`; dedupes on ``(repo, path)`` for stability.

    On secondary-rate-limit 403 (which can fire mid-walk after several
    successful pages), returns whatever was harvested so far and logs
    a warning to stderr. A partial cache is still useful — the caller
    can re-run later to top up — and is far better than losing every
    candidate to a single mid-walk failure.
    """
    seen: set[tuple[str, str]] = set()
    out: list[GhCandidate] = []
    url: str | None = _build_initial_url()
    pages = 0
    while url and pages < max_pages:
        try:
            body, link = _request(url, token=token)
        except GhAuthError as err:
            if "rate limit" in str(err).lower():
                import sys as _sys
                print(
                    f"eval-jss cran-github: rate-limited at page {pages + 1}; "
                    f"returning {len(out)} partial candidates. "
                    "Re-run later to top up.",
                    file=_sys.stderr,
                )
                return out
            raise
        for item in body.get("items", []):
            cand = _candidate_from_item(item)
            if cand is None:
                continue
            if not cand.vignette.endswith(_KEEP_SUFFIXES):
                continue
            key = (cand.repo, cand.vignette)
            if key in seen:
                continue
            seen.add(key)
            out.append(cand)
        pages += 1
        url = _next_url_from_link(link)
        if url:
            time.sleep(_PAGE_SLEEP_SECONDS)
    return out


def sync_to_cache(cache_path: Path, *, token: str) -> int:
    """Fetch all candidates and write a cache file. Returns row count.

    Cache shape:

        {
          "fetched_at": "2026-04-26T12:34:56Z",
          "candidates": [
            {"package": "dplyr", "vignette": "vignettes/rowwise.Rnw",
             "repo": "cran/dplyr", "html_url": "https://github.com/..."},
            ...
          ]
        }
    """
    candidates = fetch_all(token=token)
    payload = {
        "fetched_at": _dt.datetime.now(_dt.timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        ),
        "candidates": [
            {
                "package": c.package,
                "vignette": c.vignette,
                "repo": c.repo,
                "html_url": c.html_url,
            }
            for c in candidates
        ],
    }
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with cache_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return len(candidates)


def load_cache(cache_path: Path) -> dict:
    """Return the cache document or an empty placeholder."""
    if not cache_path.is_file():
        return {"fetched_at": None, "candidates": []}
    with cache_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def candidate_packages(cache_path: Path) -> set[str]:
    """Return the set of distinct candidate package names."""
    return {row["package"]
            for row in load_cache(cache_path).get("candidates", [])
            if row.get("package")}


# -----------------------------------------------------------------------------
# CLI entry point — invoked via ``python -m eval.cran_github``.
# (CLI wiring into ``eval/cli.py`` is intentionally deferred — TODO:
# add a ``cran-github sync/packages`` command group mirroring the
# ``jss-archive`` group once this prototype is validated.)
# -----------------------------------------------------------------------------


def main() -> int:
    cache_path = Path("eval/cran-github.json")
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print(
            "eval-jss cran-github sync: GITHUB_TOKEN is not set. "
            "Export a PAT (public_repo scope) and re-run:\n"
            "    export GITHUB_TOKEN=ghp_...\n"
            "    python -m eval.cran_github"
        )
        return 2
    print(f"eval-jss cran-github sync: querying {_API_BASE} (org:cran) …")
    print(
        "eval-jss cran-github sync: first request URL = "
        + _build_initial_url()
    )
    try:
        n = sync_to_cache(cache_path, token=token)
    except GhAuthError as err:
        print(f"eval-jss cran-github sync: auth error: {err}")
        return 2
    except (urllib.error.URLError, TimeoutError) as err:
        print(f"eval-jss cran-github sync: failed: {err}")
        return 2
    print(
        f"eval-jss cran-github sync: cached {n} (repo, path) candidates "
        f"→ {cache_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
