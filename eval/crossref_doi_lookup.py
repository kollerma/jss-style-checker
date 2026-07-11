"""Look up missing DOIs for cited bib entries via the Crossref API.

For each paper in ``eval/recall-corpus/``:

1. Scan every manuscript file for ``\\cite*{key,...}`` calls and collect
   the set of *cited* bib keys (uncited entries are skipped — they
   don't appear in the printed bibliography, so a DOI on them adds
   no recall signal).
2. Parse the paper's ``.bib`` file(s); for each cited entry that has
   no ``doi`` field and no existing ``JSS-REFS-003`` annotation in
   ``annotations.toml``:

   a. If the entry is an R package or R itself, assign its DOI from
      the R Foundation's registered scheme without any network call
      (``10.32614/CRAN.package.<name>`` for packages,
      ``10.32614/r.manuals`` for R). These ``@Manual`` citations are
      not indexed by Crossref, so the deterministic scheme is the
      only way to recover their DOIs.
   b. Otherwise query Crossref.
3. If Crossref returns a high-confidence match (title similarity,
   first-author surname match, year within ±1), append a
   ``JSS-REFS-003`` annotation to ``annotations.toml`` with a
   comment naming the found DOI.

Conservative — false-positive DOIs are worse than missing ones,
because the annotator can't easily tell the comment is wrong without
re-checking Crossref. Three independent signals (title similarity
≥0.80, author surname match, year ±1) must all pass.

Usage::

    python -m eval.crossref_doi_lookup                       # all papers
    python -m eval.crossref_doi_lookup --paper pmclust       # one paper
    python -m eval.crossref_doi_lookup --paper DBR --dry-run # preview

Polite-pool mailto contact is hardcoded from the project owner's
identity (memory: kollerma+claude@proton.me). Sleeps ~0.5s between
queries to avoid hammering the API even though the polite pool
allows much higher rates.
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import tomllib

REPO_ROOT = Path(__file__).resolve().parent.parent
CORPUS_ROOT = REPO_ROOT / "eval" / "recall-corpus"

# Polite-pool contact (Crossref reserves higher rate limits for users
# who identify themselves via the mailto parameter).
CROSSREF_MAILTO = "kollerma+claude@proton.me"
CROSSREF_USER_AGENT = (
    f"jss-style-checker/recall-corpus-doi-lookup "
    f"(+https://github.com/kollerma/jss-style-checker; mailto:{CROSSREF_MAILTO})"
)

# Cite-macro names that imply a real (non-\nocite) citation. \nocite
# emits no rendered citation, so its entries are still "uncited" in
# the printed bibliography sense — exclude.
_CITE_RE = re.compile(
    r"\\(?:cite|citep|citet|citealt|citealp|citeauthor|citeyear|"
    r"citetext|cite\*|Citet|Citep)"
    r"\*?(?:\[[^\]]*\])?(?:\[[^\]]*\])?\{([^}]+)\}"
)

# Strip LaTeX commands and braces for fuzzy title comparison.
_LATEX_MACRO = re.compile(r"\\[a-zA-Z]+\*?")

# Bib entry types that denote a standalone book: a Crossref
# ``journal-article`` hit for one of these is a review, not the book.
_BOOK_LIKE_TYPES = frozenset({"book", "inbook", "booklet"})

# The R Foundation registers a DOI for every CRAN package and for the
# R manuals under a deterministic scheme, so these resolve without a
# Crossref query (and aren't indexed by Crossref anyway):
#
#   R package  →  10.32614/CRAN.package.<canonical-name>
#   R itself   →  10.32614/r.manuals
#
# The canonical, case-sensitive package name is recovered from the
# ``package=<name>`` / ``web/packages/<name>`` CRAN URL that
# ``citation()`` / ``toBibtex()`` emit. Package names match
# ``[A-Za-z][A-Za-z0-9.]*`` (dots allowed, e.g. ``mlt.docreg``).
_CRAN_PKG_URL_RE = re.compile(
    r"cran\.r-project\.org/(?:web/)?packages?[=/]([A-Za-z][A-Za-z0-9.]*)",
    re.IGNORECASE,
)
# R base: the project home page, but not a /package= URL.
_RPROJECT_URL_RE = re.compile(
    r"(?<![A-Za-z0-9.=])(?:www\.)?r-project\.org/?$", re.IGNORECASE
)


@dataclass
class BibEntry:
    key: str
    line: int  # line number of the entry header in the bib
    type: str  # @article, @manual, etc.
    fields: dict[str, str]


def parse_bib(bib_text: str) -> list[BibEntry]:
    """Parse a .bib file. Regex-based — enough for our purposes."""
    entries: list[BibEntry] = []
    header_re = re.compile(
        r"^[ \t]*@(\w+)\s*\{\s*([^,\s]+)\s*,", re.MULTILINE
    )
    for hm in header_re.finditer(bib_text):
        line_no = bib_text[: hm.start()].count("\n") + 1
        etype = hm.group(1)
        key = hm.group(2)
        # Collect fields between the header brace and the matching
        # closing brace. We track brace depth from the opening `{` of
        # the entry; the entry ends at depth 0.
        pos = hm.end()
        depth = 1  # opened by the entry's '{'
        body_start = pos
        while pos < len(bib_text) and depth > 0:
            ch = bib_text[pos]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
            pos += 1
        body = bib_text[body_start : pos - 1]
        fields = _parse_fields(body)
        entries.append(BibEntry(key=key, line=line_no, type=etype, fields=fields))
    return entries


def _parse_fields(body: str) -> dict[str, str]:
    """Pull ``field = {value}`` or ``field = "value"`` pairs from a
    bib entry body. Handles balanced braces inside values."""
    out: dict[str, str] = {}
    i = 0
    while i < len(body):
        # Skip whitespace and commas.
        while i < len(body) and body[i] in " \t\n,":
            i += 1
        if i >= len(body):
            break
        # Read field name.
        m = re.match(r"([A-Za-z][A-Za-z0-9_-]*)\s*=\s*", body[i:])
        if not m:
            i += 1
            continue
        name = m.group(1).lower()
        i += m.end()
        # Read value: balanced {...} or "..." or a bare token.
        if i >= len(body):
            break
        if body[i] == "{":
            depth = 1
            i += 1
            start = i
            while i < len(body) and depth > 0:
                if body[i] == "{":
                    depth += 1
                elif body[i] == "}":
                    depth -= 1
                    if depth == 0:
                        break
                i += 1
            value = body[start:i]
            i += 1
        elif body[i] == '"':
            i += 1
            start = i
            while i < len(body) and body[i] != '"':
                i += 1
            value = body[start:i]
            i += 1
        else:
            start = i
            while i < len(body) and body[i] not in ",\n":
                i += 1
            value = body[start:i].strip()
        out[name] = value
    return out


def collect_cited_keys(paper_dir: Path) -> set[str]:
    """Walk all manuscript files; return the set of cited bib keys,
    lowercased. BibTeX/LaTeX citation keys are case-insensitive, so
    ``\\citep{Graffel24}`` resolves the ``@Article{graffel24}`` entry —
    compare case-insensitively (callers must lowercase the bib key too)."""
    cited: set[str] = set()
    for src in paper_dir.rglob("*"):
        if not src.is_file() or src.suffix.lower() not in {
            ".tex", ".ltx", ".rnw", ".rmd"
        }:
            continue
        text = src.read_text(errors="ignore")
        for m in _CITE_RE.finditer(text):
            for k in m.group(1).split(","):
                cited.add(k.strip().lower())
    return cited


def existing_refs003_lines(annotations: dict) -> set[int]:
    """Lines that already have a JSS-REFS-003 annotation against the bib."""
    out: set[int] = set()
    for v in annotations.get("violations", []):
        if (
            v.get("rule_id") == "JSS-REFS-003"
            and v.get("file", "").endswith(".bib")
        ):
            out.add(v["line"])
    return out


def normalize_title(s: str) -> str:
    """Lowercase, strip LaTeX macros / braces / math, collapse whitespace.

    BibTeX capitalisation-protection braces (``{T}he``, ``de {F}inetti``,
    ``{H}ardy-{W}einberg``) must be *removed*, not replaced by a space —
    splitting them turns ``{T}he`` into ``t he`` and tanks the Crossref
    title-similarity score below the match threshold. Inline math
    delimiters (``$p$``) are dropped too so ``$p$-value`` lines up with
    Crossref's ``p-value``."""
    s = _LATEX_MACRO.sub(" ", s)
    s = s.replace("$", "")
    s = re.sub(r"[{}]", "", s)
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s


def extract_first_author_surname(authors_field: str) -> str | None:
    """Pull the first author's last name from the bib's `author` field.
    Accepts "Last, First and Last2, First2..." and
    "First Last and First2 Last2..." shapes."""
    if not authors_field:
        return None
    first_author = authors_field.split(" and ")[0].strip()
    if "," in first_author:
        return first_author.split(",")[0].strip().lower()
    parts = first_author.split()
    return parts[-1].strip().lower() if parts else None


def deterministic_doi(entry: BibEntry) -> str | None:
    """Return the R-Foundation-registered DOI for an R-package or
    R-base citation, or ``None`` if the entry is neither.

    No network call: the DOI is derived from the entry's CRAN /
    r-project URL (falling back to the title for a CRAN ``@Manual``
    whose URL is absent). This covers the ``@Manual`` package and R
    citations that Crossref does not index."""
    url = entry.fields.get("url", "")
    note = entry.fields.get("note", "")
    title = entry.fields.get("title", "")
    author = entry.fields.get("author", "")

    # A CRAN package — canonical name straight from the package URL.
    m = _CRAN_PKG_URL_RE.search(url)
    if m:
        return f"10.32614/CRAN.package.{m.group(1)}"

    # R itself — "R Core Team" published via the r-project.org home page.
    if _RPROJECT_URL_RE.search(url) and "r core team" in normalize_title(
        author
    ):
        return "10.32614/r.manuals"

    # CRAN @Manual with no URL: recover the name from the title prefix
    # that citation() emits ("<pkg>: Description"), stripping the \pkg
    # wrapper. Only when the note marks it an R package, to stay clear
    # of unrelated @Manual entries.
    if entry.type.lower() == "manual" and re.search(
        r"R package version", note, re.IGNORECASE
    ):
        # Preserve case — package names are case-sensitive
        # (e.g. CARBayesST), so don't run this through normalize_title.
        name = _LATEX_MACRO.sub("", title.split(":", 1)[0])
        name = re.sub(r"[{}\s]", "", name)
        if re.fullmatch(r"[A-Za-z][A-Za-z0-9.]*", name):
            return f"10.32614/CRAN.package.{name}"

    return None


def crossref_lookup(entry: BibEntry, *, timeout: float = 10.0) -> dict | None:
    """Query Crossref for `entry` and return the top match's metadata
    or ``None`` if no high-confidence match exists."""
    title = normalize_title(entry.fields.get("title", ""))
    if not title:
        return None
    author = extract_first_author_surname(entry.fields.get("author", ""))
    year = entry.fields.get("year", "").strip()

    # Build the query. query.bibliographic does a good job; we narrow
    # with query.author if available.
    params = {
        "query.bibliographic": title,
        # Crossref's relevance ranking can bury the right record: a book's
        # individual chapters often outrank the book itself (e.g.
        # Aitchison 1986, where the book is the 4th hit behind three of its
        # chapters). Fetch enough candidates to reach it — the
        # sim>=0.80 + author + year gate below keeps precision safe.
        "rows": "8",
        "mailto": CROSSREF_MAILTO,
    }
    if author:
        params["query.author"] = author
    url = "https://api.crossref.org/works?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(
        url, headers={"User-Agent": CROSSREF_USER_AGENT}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:  # network / json / timeout
        print(f"      crossref error: {exc}", file=sys.stderr)
        return None

    items = data.get("message", {}).get("items", [])
    if not items:
        return None

    # Score each candidate by title similarity + author + year.
    best: tuple[float, dict] | None = None
    for item in items:
        cand_titles = item.get("title") or []
        if not cand_titles:
            continue
        # A ``@Book`` matched to a Crossref ``journal-article`` is almost
        # always a book *review* (JSTOR indexes these), not the book — the
        # review carries the book's title and year, so similarity/author
        # don't catch it (deSolve Press92, HardyWeinberg hartl/weir/mourant
        # all matched reviews). Books live in Crossref as book / monograph,
        # so reject journal-article candidates for book-like entries.
        if (
            entry.type.lower() in _BOOK_LIKE_TYPES
            and item.get("type") == "journal-article"
        ):
            continue
        cand_title = normalize_title(cand_titles[0])
        sim = difflib.SequenceMatcher(None, title, cand_title).ratio()
        # Year match (Crossref's "published-print" / "issued" path).
        cand_year = None
        for key in ("published-print", "published-online", "issued"):
            dp = item.get(key, {}).get("date-parts")
            if dp and dp[0]:
                cand_year = str(dp[0][0])
                break
        year_ok = True
        if year and cand_year:
            try:
                year_ok = abs(int(year) - int(cand_year)) <= 1
            except ValueError:
                year_ok = True  # don't fail on weird year strings
        # Author surname match.
        author_ok = True
        if author:
            cand_authors = [
                (a.get("family") or "").lower()
                for a in (item.get("author") or [])
            ]
            author_ok = author in cand_authors
        # Decision: title sim >= 0.80 AND year_ok AND author_ok.
        if sim >= 0.80 and year_ok and author_ok:
            if best is None or sim > best[0]:
                best = (sim, item)
    if best is None:
        return None
    sim, item = best
    return {"doi": item.get("DOI"), "similarity": sim, "raw": item}


def lookup_paper(paper_dir: Path, *, dry_run: bool = False, sleep: float = 0.5):
    """Run the lookup for one paper directory."""
    print(f"\n=== {paper_dir.name} ===")
    cited = collect_cited_keys(paper_dir)
    if not cited:
        print("  no cited keys — skipping")
        return

    ann_path = paper_dir / "annotations.toml"
    with ann_path.open("rb") as f:
        annotations = tomllib.load(f)
    existing = existing_refs003_lines(annotations)

    added = 0
    for bib_path in sorted(paper_dir.rglob("*.bib")):
        bib_text = bib_path.read_text(errors="ignore")
        entries = parse_bib(bib_text)
        for entry in entries:
            if entry.key.lower() not in cited:
                continue
            if entry.fields.get("doi", "").strip():
                continue
            if entry.line in existing:
                continue
            print(f"  → {entry.key} ({entry.type}, L{entry.line}):", end=" ")
            # CRAN packages and R itself resolve from the registered
            # DOI scheme — no network call, and Crossref wouldn't match
            # them anyway.
            doi = deterministic_doi(entry)
            if doi is not None:
                provenance = "registered under the CRAN/R DOI scheme"
                print(f"DOI {doi}  ({provenance})")
            else:
                match = crossref_lookup(entry)
                time.sleep(sleep)
                if match is None:
                    print("no confident match")
                    continue
                doi = match["doi"]
                provenance = (
                    f"found on Crossref (title similarity "
                    f"{match['similarity']:.2f})"
                )
                print(f"DOI {doi}  (title sim {match['similarity']:.2f})")
            if dry_run:
                continue
            with ann_path.open("a") as out:
                out.write(
                    "\n[[violations]]\n"
                    f'rule_id = "JSS-REFS-003"\n'
                    f'file = "{bib_path.name}"\n'
                    f"line = {entry.line}\n"
                    f"comment = '{entry.key} — DOI {doi} {provenance}; "
                    f"add to the entry as doi=\"{doi}\".'\n"
                )
            existing.add(entry.line)
            added += 1
    print(f"  added {added} annotation(s)")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--paper", help="restrict to one paper directory under recall-corpus/"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="report findings but don't modify annotations.toml",
    )
    parser.add_argument(
        "--sleep", type=float, default=0.5,
        help="seconds to pause between Crossref queries (default 0.5)",
    )
    args = parser.parse_args(argv)

    paper_dirs = sorted(
        d for d in CORPUS_ROOT.iterdir()
        if d.is_dir() and (d / "annotations.toml").exists()
    )
    if args.paper:
        paper_dirs = [d for d in paper_dirs if d.name == args.paper]
        if not paper_dirs:
            print(f"paper not found: {args.paper}", file=sys.stderr)
            return 2
    for d in paper_dirs:
        lookup_paper(d, dry_run=args.dry_run, sleep=args.sleep)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
