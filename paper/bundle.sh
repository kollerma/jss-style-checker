#!/usr/bin/env bash
# Assemble the JSS submission bundle into <repo>/submission/ — internal.
#
#   paper.pdf                        the manuscript
#   replication-materials.zip        replicate.sh + README + manuscript
#                                      sources + a fresh run transcript
#   jsslintr_<ver>.tar.gz            the released CRAN tarball
#   jss_style_checker-<ver>.tar.gz   the released PyPI sdist
#                                      (sha256-verified against PyPI)
#
# The transcript is produced by actually running replicate.sh inside the
# staged bundle with a minimal environment, so the shipped output is the
# real reviewer experience (PyPI install included). The bundle fails if
# any replication step fails or is skipped.
#
# Requirements: a fresh `make pdf` beforehand, network access to CRAN
# and PyPI, and everything replicate.sh needs (Python >= 3.10, Rscript
# with the jsslintr package).
#
# Usage:  bash bundle.sh   (or: make bundle)
set -euo pipefail
cd "$(dirname "$0")"
REPO_ROOT=$(cd .. && pwd)
DEST=$REPO_ROOT/submission

step() { printf '\n== %s\n' "$*"; }
fail() { echo "error: $*" >&2; exit 1; }

[ -f paper.pdf ] || fail "paper.pdf missing -- run 'make pdf' first"
[ paper.pdf -nt paper.tex ] || fail "paper.pdf older than paper.tex -- run 'make pdf'"

PY_VERSION=$(sed -n 's/.*StatToolVersion}{\([^}]*\)}.*/\1/p' generated/stats.tex)
[ -n "$PY_VERSION" ] || fail "cannot read StatToolVersion from generated/stats.tex"

STAGE=$(mktemp -d)
trap 'rm -rf "$STAGE"' EXIT

# -- 1. stage the replication materials --------------------------------------
step "staging replication materials"
mkdir "$STAGE/replication"
cp -R replicate.sh paper.tex paper.bib jss.cls jss.bst jsslogo.jpg \
      examples generated "$STAGE/replication/"
cp replication-readme.txt "$STAGE/replication/README.txt"

# -- 2. run the replication for the shipped transcript ------------------------
step "running replicate.sh in the staged bundle"
RS_DIR=$(dirname "$(command -v Rscript 2>/dev/null || echo /usr/bin/false)")
(cd "$STAGE/replication" && env -i HOME="$HOME" \
    ${R_LIBS_USER:+R_LIBS_USER="$R_LIBS_USER"} \
    PATH="/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin:/opt/homebrew/bin:$RS_DIR" \
    bash replicate.sh 2>&1 | tee replication-output.txt | grep -E '^==|^->')
grep -q "SKIPPED" "$STAGE/replication/replication-output.txt" \
    && fail "a replication step was skipped; the shipped transcript must be complete"
grep -q "^== replication complete" "$STAGE/replication/replication-output.txt" \
    || fail "replication did not complete"

# -- 3. the released tarballs, from their registries --------------------------
# CRAN is the source of truth for the published R version — the repo's
# DESCRIPTION can be a revision ahead between submission rounds.
step "downloading jsslintr from CRAN"
R_TARBALL=$(curl -fsSL "https://cran.r-project.org/package=jsslintr" \
    | grep -oE 'jsslintr_[0-9][0-9.-]*\.tar\.gz' | head -1)
[ -n "$R_TARBALL" ] || fail "cannot determine the jsslintr tarball on CRAN"
case "$R_TARBALL" in
    "jsslintr_$PY_VERSION-"*) ;;
    *) fail "CRAN serves $R_TARBALL, but the paper states $PY_VERSION" ;;
esac
echo "$R_TARBALL"
curl -fsSL -o "$STAGE/$R_TARBALL" \
    "https://cran.r-project.org/src/contrib/$R_TARBALL"

step "downloading jss-style-checker $PY_VERSION from PyPI (sha256-verified)"
SDIST_INFO=$(curl -fsSL "https://pypi.org/pypi/jss-style-checker/$PY_VERSION/json" \
    | python3 -c '
import json, sys
u = next(u for u in json.load(sys.stdin)["urls"]
         if u["filename"].endswith(".tar.gz"))
print(u["url"], u["digests"]["sha256"])')
SDIST_URL=${SDIST_INFO% *}
SDIST_SHA=${SDIST_INFO#* }
curl -fsSL -o "$STAGE/jss_style_checker-$PY_VERSION.tar.gz" "$SDIST_URL"
echo "$SDIST_SHA  $STAGE/jss_style_checker-$PY_VERSION.tar.gz" \
    | shasum -a 256 -c - > /dev/null || fail "PyPI sdist checksum mismatch"

# -- 4. zip and assemble ------------------------------------------------------
step "assembling $DEST"
(cd "$STAGE" && zip -r -X -q replication-materials.zip replication \
    -x '*.DS_Store')
rm -rf "$DEST"
mkdir "$DEST"
cp paper.pdf "$STAGE/replication-materials.zip" "$STAGE"/*.tar.gz "$DEST/"
ls -l "$DEST"
echo "bundle complete."
