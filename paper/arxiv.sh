#!/usr/bin/env bash
# Assemble the arXiv source tarball into <repo>/submission/ — internal.
#
# arXiv compiles the submission itself (pdflatex, no BibTeX run), so the
# tarball ships the .bbl alongside the sources:
#   paper.tex (nojss preprint), paper.bbl, paper.bib (documentation
#   only), jss.cls, examples/demo.tex, generated/** (stats, table
#   bodies, listings).
#
# The assembly is verified before packaging: the staged directory is
# compiled the way arXiv does (pdflatex only, three passes, using the
# shipped .bbl) and must produce the same page count as the repository
# build, with no undefined citations or references.
#
# Requirements: a fresh `make pdf` beforehand (provides paper.bbl and
# the reference page count), pdflatex.
#
# Usage:  bash arxiv.sh   (or: make arxiv)
set -euo pipefail
cd "$(dirname "$0")"
REPO_ROOT=$(cd .. && pwd)
DEST=$REPO_ROOT/submission

step() { printf '\n== %s\n' "$*"; }
fail() { echo "error: $*" >&2; exit 1; }

[ -f paper.pdf ] || fail "paper.pdf missing -- run 'make pdf' first"
[ paper.pdf -nt paper.tex ] || fail "paper.pdf older than paper.tex -- run 'make pdf'"
[ -f paper.bbl ] || fail "paper.bbl missing -- run 'make pdf' first"
grep -q 'nojss' paper.tex \
    || fail "paper.tex does not use the nojss option; arXiv gets the preprint build"
REF_PAGES=$(pdfinfo paper.pdf | awk '/^Pages:/{print $2}')

STAGE=$(mktemp -d)
trap 'rm -rf "$STAGE"' EXIT

step "staging arXiv sources"
mkdir "$STAGE/arxiv"
cp paper.tex paper.bbl paper.bib jss.cls "$STAGE/arxiv/"
mkdir -p "$STAGE/arxiv/examples"
cp examples/demo.tex "$STAGE/arxiv/examples/"
cp -R generated "$STAGE/arxiv/"

step "compiling the staged sources the way arXiv does (no BibTeX)"
(cd "$STAGE/arxiv" \
    && pdflatex -interaction=nonstopmode -halt-on-error paper.tex > /dev/null \
    && pdflatex -interaction=nonstopmode -halt-on-error paper.tex > /dev/null \
    && pdflatex -interaction=nonstopmode -halt-on-error paper.tex > /dev/null) \
    || fail "staged sources do not compile standalone"
grep -E "Warning.*(Citation|Reference).*undefined" "$STAGE/arxiv/paper.log" \
    && fail "undefined citations/references in the staged build"
GOT_PAGES=$(pdfinfo "$STAGE/arxiv/paper.pdf" | awk '/^Pages:/{print $2}')
[ "$GOT_PAGES" = "$REF_PAGES" ] \
    || fail "staged build has $GOT_PAGES pages, repository build $REF_PAGES"
echo "staged build: $GOT_PAGES pages, no undefined references"

step "packaging"
mkdir -p "$DEST"
rm -f "$DEST/arxiv-source.tar.gz"
# Tar the *contents* (arXiv wants sources at the archive root); strip
# build products of the verification compile first.
(cd "$STAGE/arxiv" && rm -f paper.pdf paper.log paper.aux paper.out \
    && tar czf "$DEST/arxiv-source.tar.gz" .)
ls -l "$DEST/arxiv-source.tar.gz"
echo "arxiv source complete."
