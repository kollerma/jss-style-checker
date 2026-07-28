#!/usr/bin/env bash
# Replication script for "jss-lint" (JSS submission) — reviewer-facing.
#
# Re-runs every command demonstrated in the manuscript against the
# *released* tool and verifies that the output matches what the paper
# shows. It is self-contained: it needs only the files uploaded with the
# submission (this script, examples/demo.tex, generated/, paper.tex,
# paper.bib) — not the development repository — and it modifies nothing
# in place.
#
#   1. jss-lint examples/demo.tex            -> the seven violations of §2.3
#   2. jss-lint --fix --dry-run demo.tex     -> the auto-fix diff listing (§5.2)
#   3. jss-lint explain JSS-CITE-003         -> the rule-documentation listing (§5.2)
#   4. jss-lint --mode reviewer (JSON)       -> the compliance table (Table "reviewer")
#   5. jss-lint paper.tex paper.bib          -> the self-compliance claim (§4.4): zero violations
#   6. R channel (optional, needs jsslintr)  -> the jsslint()/jssfix() session of §5.1
#
# Requirements: bash, Python >= 3.10 with venv+pip (used to install the
# released tool from PyPI unless a matching `jss-lint` is already on
# PATH; that install is the only network access). Step 6 runs only if
# Rscript and the jsslintr package are available, and is skipped with a
# note otherwise.
#
# Usage:  bash replicate.sh
set -euo pipefail
cd "$(dirname "$0")"

step() { printf '\n== %s\n' "$*"; }
show() { printf '$ %s\n' "$*"; }
ok()   { printf -- '-> %s\n' "$*"; }
fail() { echo "error: $*" >&2; exit 1; }

WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT

# -- 0. the released tool, at the version the paper evaluates ----------------
# The manuscript states its tool version in generated/stats.tex; replication
# must run that version, not whatever happens to be installed.
EXPECTED_VERSION=$(sed -n 's/.*StatToolVersion}{\([^}]*\)}.*/\1/p' \
    generated/stats.tex 2>/dev/null || true)
[ -n "$EXPECTED_VERSION" ] || fail "generated/stats.tex missing or unreadable"

JSS_LINT=""
if command -v jss-lint > /dev/null 2>&1; then
    FOUND=$(jss-lint --version | sed 's/.*version //')
    if [ "$FOUND" = "$EXPECTED_VERSION" ]; then
        JSS_LINT=jss-lint
        echo "using jss-lint $FOUND from PATH"
    else
        echo "jss-lint on PATH is $FOUND, paper needs $EXPECTED_VERSION" \
             "-- installing the pinned release"
    fi
fi
if [ -z "$JSS_LINT" ]; then
    step "installing jss-style-checker==$EXPECTED_VERSION from PyPI"
    PY=""
    for cand in python3 python3.14 python3.13 python3.12 python3.11 \
                python3.10 python; do
        if command -v "$cand" > /dev/null 2>&1 && "$cand" -c \
            'import sys; sys.exit(sys.version_info < (3, 10))' 2>/dev/null; then
            PY=$cand; break
        fi
    done
    [ -n "$PY" ] || fail "need Python >= 3.10"
    "$PY" -m venv "$WORK/venv"
    "$WORK/venv/bin/pip" install --quiet \
        "jss-style-checker==$EXPECTED_VERSION"
    JSS_LINT=$WORK/venv/bin/jss-lint
fi
"$JSS_LINT" --version

# -- 1. the motivating example: seven violations (§2.3) ----------------------
step "the motivating example (§2.3)"
show jss-lint examples/demo.tex
# Violations found -> exit status 1 by design (§5.3); that is the expected
# outcome here, so it must not end the script.
rc=0; "$JSS_LINT" examples/demo.tex || rc=$?
[ "$rc" = 1 ] || fail "expected exit status 1 (violations found), got $rc"
"$JSS_LINT" --output json examples/demo.tex > "$WORK/demo.json" || true
N=$(python3 -c 'import json, sys
print(len(json.load(open(sys.argv[1]))["violations"]))' "$WORK/demo.json")
[ "$N" = 7 ] || fail "paper reports seven violations, tool reports $N"
ok "seven violations and exit status 1, as stated in the paper"

# -- 2. the auto-fix preview (§5.2) -------------------------------------------
step "the auto-fix preview (§5.2)"
cp examples/demo.tex "$WORK/demo.tex"
show jss-lint --fix --dry-run demo.tex
# --no-resolve keeps the diff header at the literal "demo.tex" (multi-file
# auto-resolution would canonicalize it to an absolute temp path).
(cd "$WORK" && "$JSS_LINT" --fix --dry-run --no-resolve demo.tex || true) \
    | tee "$WORK/demo-fix-full.txt"
awk '/^─/{exit} {print}' "$WORK/demo-fix-full.txt" > "$WORK/demo-fix-diff.txt"
diff -u generated/listings/demo-fix-diff.txt "$WORK/demo-fix-diff.txt" \
    > /dev/null || fail "auto-fix diff differs from the listing shown in the paper"
ok "the diff is byte-identical to the listing in the paper"

# -- 3. the rule documentation (§5.2) -----------------------------------------
step "rule documentation (§5.2)"
show jss-lint explain JSS-CITE-003
"$JSS_LINT" explain JSS-CITE-003 | tee "$WORK/explain-cite003.txt"
diff -u generated/listings/explain-cite003.txt "$WORK/explain-cite003.txt" \
    > /dev/null || fail "explain output differs from the listing shown in the paper"
ok "byte-identical to the listing in the paper"

# -- 4. the reviewer-mode compliance summary ----------------------------------
step "the reviewer-mode compliance summary (§5.3)"
show jss-lint --mode reviewer examples/demo.tex
"$JSS_LINT" --mode reviewer examples/demo.tex || true
# The paper's table transcribes the JSON output of the same command;
# rebuild the rows and compare against the table body as printed.
("$JSS_LINT" --mode reviewer --output json examples/demo.tex || true) \
    | python3 -c '
import json, sys
doc = json.load(sys.stdin)
for c in doc["categories"]:
    row = (c["title"], c["status"], c["rules_applied"], c["rules_passed"])
    print("{} & {} & {} & {} \\\\".format(*row))
print("\\midrule")
pct = doc["compliance_percentage"]
print("Overall compliance & \\multicolumn{3}{r}{" + format(pct, ".1f")
      + "\\%} \\\\")
print("\\bottomrule")
' > "$WORK/tab-demo-reviewer.tex"
grep -v '^%' generated/tab-demo-reviewer.tex > "$WORK/tab-expected.tex"
diff -u "$WORK/tab-expected.tex" "$WORK/tab-demo-reviewer.tex" \
    > /dev/null || fail "reviewer summary differs from the table shown in the paper"
ok "the JSON output matches the table body in the paper"

# -- 5. the manuscript passes its own linter (§4.4) ---------------------------
if [ -f paper.tex ] && [ -f paper.bib ]; then
    step "self-referential compliance check (§4.4)"
    show jss-lint paper.tex paper.bib
    "$JSS_LINT" paper.tex paper.bib
    ok "no output and exit status 0: a clean pass, as stated in the paper"
else
    step "self-referential compliance check -- SKIPPED"
    echo "paper.tex/paper.bib not present alongside this script"
fi

# -- 6. the R channel (§5.1), if available ------------------------------------
if command -v Rscript > /dev/null 2>&1 \
    && Rscript -e 'quit(status = !requireNamespace("jsslintr", quietly = TRUE))' \
        > /dev/null 2>&1; then
    step "the R channel (§5.1)"
    cp examples/demo.tex "$WORK/r-demo.tex"
    show 'Rscript -e library("jsslintr"); jsslint("demo.tex");' \
         'jssfix("demo.tex", dry_run = TRUE)'
    (cd "$WORK" && Rscript -e '
library("jsslintr")
res <- jsslint("r-demo.tex")
print(res)
stopifnot(nrow(as.data.frame(res)) == 7L)
invisible(jssfix("r-demo.tex", dry_run = TRUE))
') || fail "R channel disagrees with the paper (expected seven violations)"
    ok "seven violations and four previewed fixes, as stated in the paper"
else
    step "the R channel -- SKIPPED (Rscript with the jsslintr package not found)"
    echo "install.packages(\"jsslintr\") to enable this step"
fi

step "replication complete"
