"""Optional online DOI resolution (Crossref + CRAN/DataCite).

The linter is offline by default; this module is used only when the
caller opts in with ``jss-lint --crossref``. Given a BibTeX entry's
fields it returns the reference's registered DOI, or ``None`` when no
confident match exists — so JSS-REFS-003 can turn its static "add a doi
if available" advisory into an online-verified check (and, with
``--fix``, populate the field).

Two resolution strategies:

* **Crossref** (``api.crossref.org``) — for ``@article`` / ``@book`` /
  ``@inproceedings`` / ``@incollection``: query by bibliographic title
  and accept the top hit only when its title is a close match.
* **CRAN / DataCite** — for ``@manual`` entries citing a CRAN R package
  (``url = {...package=NAME}``): CRAN mints the deterministic DOI
  ``10.32614/CRAN.package.NAME``; confirm it resolves via ``doi.org``.

Every network or parse error resolves to ``None`` so the caller silently
falls back to the offline advisory — the feature never fails a lint run.
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable, Mapping
from difflib import SequenceMatcher

_CROSSREF_URL = "https://api.crossref.org/works"
_DOI_RESOLVER_URL = "https://doi.org/"
_DEFAULT_TIMEOUT = 8.0

# Minimum title similarity (0..1) to accept a Crossref hit as the same
# work. Deliberately strict: a wrong DOI is worse than none.
_MIN_TITLE_SCORE = 0.90

# ``url = {https://CRAN.R-project.org/package=mfbvar}`` -> ``mfbvar``.
_CRAN_PKG_RE = re.compile(
    r"(?:CRAN\.R-project\.org|cran\.r-project\.org)/package[=/]([A-Za-z0-9.]+)"
)

#: Type for the injected resolver the CLI hands to the engine/rules.
Resolver = Callable[[Mapping[str, str], str], "str | None"]


def _user_agent(mailto: str | None) -> str:
    base = "jss-lint (https://github.com/kollerma/jss-style-checker)"
    return f"{base}; mailto:{mailto}" if mailto else base


def _norm_title(text: str) -> str:
    # Strip LaTeX braces/commands and collapse whitespace for comparison.
    text = re.sub(r"[{}]", "", text)
    text = re.sub(r"\\[A-Za-z]+", " ", text)
    return " ".join(text.lower().split())


def _http_json(
    url: str, *, timeout: float, mailto: str | None, opener: Callable | None
) -> object | None:
    req = urllib.request.Request(url, headers={"User-Agent": _user_agent(mailto)})
    try:
        with (opener or urllib.request.urlopen)(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8", "replace"))
    except (urllib.error.URLError, TimeoutError, ValueError, OSError):
        return None


def _year4(text: str) -> str:
    m = re.search(r"\d{4}", text or "")
    return m.group(0) if m else ""


def _first_surname(author: str) -> str:
    """Best-effort first-author surname from a BibTeX ``author`` field.

    Handles ``Breiman, Leo`` and ``Leo Breiman`` and multi-author
    ``A and B`` lists."""
    first = re.split(r"\s+and\s+", author or "", maxsplit=1)[0].strip()
    if not first:
        return ""
    surname = first.split(",")[0] if "," in first else first.split()[-1]
    return re.sub(r"[{}]", "", surname).lower()


def _item_year(item: dict) -> str:
    for key in ("issued", "published", "published-print", "published-online"):
        parts = (item.get(key) or {}).get("date-parts") or []
        if parts and parts[0]:
            return str(parts[0][0])
    return ""


def _item_has_surname(item: dict, surname: str) -> bool:
    for a in item.get("author") or ():
        if surname in re.sub(r"[{}]", "", (a.get("family") or "")).lower():
            return True
    return False


def _crossref_doi(
    title: str,
    author: str,
    year: str,
    *,
    timeout: float,
    mailto: str | None,
    opener: Callable | None,
) -> str | None:
    title = (title or "").strip()
    if not title:
        return None
    want = _norm_title(title)
    want_year = _year4(year)
    want_surname = _first_surname(author)
    # Bias the ranking with author (and year): a bare title query buries
    # the target work under same-titled book chapters / figures.
    params = {"query.bibliographic": want, "rows": "10"}
    if want_surname:
        params["query.author"] = want_surname
    query = urllib.parse.urlencode(params)
    data = _http_json(
        f"{_CROSSREF_URL}?{query}", timeout=timeout, mailto=mailto, opener=opener
    )
    if not isinstance(data, dict):
        return None
    items = data.get("message", {}).get("items", [])
    best_doi: str | None = None
    best_score = -1.0
    for item in items if isinstance(items, list) else ():
        titles = item.get("title") or []
        doi = item.get("DOI")
        if not titles or not doi:
            continue
        tscore = SequenceMatcher(None, want, _norm_title(titles[0])).ratio()
        if tscore < _MIN_TITLE_SCORE:
            continue
        # Disambiguate same-title works by year and first-author surname:
        # a mismatch on a *known* year or author rejects the candidate, so
        # a wrong DOI is never written.
        iyear = _item_year(item)
        if want_year and iyear and iyear != want_year:
            continue
        if want_surname and item.get("author") and not _item_has_surname(
            item, want_surname
        ):
            continue
        score = (
            tscore
            + (0.1 if want_year and iyear == want_year else 0.0)
            + (0.1 if want_surname and _item_has_surname(item, want_surname) else 0.0)
        )
        if score > best_score:
            best_score, best_doi = score, doi
    return best_doi


def _doi_resolves(
    doi: str, *, timeout: float, opener: Callable | None
) -> bool:
    req = urllib.request.Request(
        _DOI_RESOLVER_URL + urllib.parse.quote(doi, safe="/.:"),
        method="HEAD",
        headers={"User-Agent": _user_agent(None)},
    )
    try:
        with (opener or urllib.request.urlopen)(req, timeout=timeout) as resp:
            return 200 <= getattr(resp, "status", 200) < 400
    except urllib.error.HTTPError as err:
        return 200 <= err.code < 400
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def _cran_manual_doi(
    fields: Mapping[str, str], *, timeout: float, opener: Callable | None
) -> str | None:
    for key in ("url", "note", "howpublished"):
        m = _CRAN_PKG_RE.search(fields.get(key, "") or "")
        if m:
            doi = f"10.32614/CRAN.package.{m.group(1)}"
            if _doi_resolves(doi, timeout=timeout, opener=opener):
                return doi
            return None
    return None


def resolve_doi(
    fields: Mapping[str, str],
    entry_type: str,
    *,
    timeout: float = _DEFAULT_TIMEOUT,
    mailto: str | None = None,
    opener: Callable | None = None,
) -> str | None:
    """Return the registered DOI for a BibTeX entry, or ``None``.

    ``fields`` is a lowercase-keyed field map (title/author/year/url…);
    ``entry_type`` is the lowercase entry type. ``opener`` is an
    injection seam for tests (defaults to :func:`urllib.request.urlopen`).
    """
    if entry_type.lower() == "manual":
        return _cran_manual_doi(fields, timeout=timeout, opener=opener)
    return _crossref_doi(
        fields.get("title", ""),
        fields.get("author", ""),
        fields.get("year", ""),
        timeout=timeout,
        mailto=mailto,
        opener=opener,
    )


def make_resolver(
    *, timeout: float = _DEFAULT_TIMEOUT, mailto: str | None = None
) -> Resolver:
    """Bind ``timeout`` / ``mailto`` into a ``(fields, entry_type)`` resolver
    for the engine to call per entry."""

    def _resolver(fields: Mapping[str, str], entry_type: str) -> str | None:
        return resolve_doi(fields, entry_type, timeout=timeout, mailto=mailto)

    return _resolver
