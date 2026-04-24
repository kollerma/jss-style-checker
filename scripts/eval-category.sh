#!/usr/bin/env bash
# eval-category.sh — run the per-category precision gate for spec 004.
#
# Usage: scripts/eval-category.sh <category>
#   e.g., scripts/eval-category.sh citations
#
# Runs (in order):
#   1. pytest with --cov-branch --cov-fail-under=100 on the category module
#   2. eval-jss scan         — scan the corpus
#   3. eval-jss human-review — human-in-the-loop labelling
#   4. eval-jss report       — per-rule precision
#
# eval-jss scan and report return exit code 1 when they find violations /
# below-threshold rules (success-with-data); this script treats 0 and 1 as
# "continue" and only aborts on 2+ (actual invocation errors).

set -u -o pipefail

CATEGORY="${1:?category required (e.g., citations)}"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname -- "$SCRIPT_DIR")"
cd "$ROOT"

# category -> JSS-<PREFIX>- (matches tools/_catalogue_validate.CATEGORY_PREFIX)
declare -A PREFIX=(
    [preamble]=JSS-PRE-
    [structure]=JSS-STRUCT-
    [markup]=JSS-MARKUP-
    [citations]=JSS-CITE-
    [references]=JSS-REFS-
    [bibtex]=JSS-BIBTEX-
    [naming]=JSS-NAME-
    [capitalization]=JSS-CAP-
    [typography]=JSS-TYPO-
    [abbreviations]=JSS-ABBR-
    [code_style]=JSS-CODE-
    [code_width]=JSS-WIDTH-
    [operators]=JSS-OPER-
    [crossrefs]=JSS-XREF-
    [house_style]=JSS-HOUSE-
)

if [[ -z "${PREFIX[$CATEGORY]:-}" ]]; then
    echo "eval-category.sh: unknown category '$CATEGORY'" >&2
    echo "known: ${!PREFIX[*]}" >&2
    exit 2
fi

# Step 1: unit tests with 100% branch coverage gate.
set -e
"$SCRIPT_DIR/vtest.sh" "tests/unit/rules/test_${CATEGORY}.py" \
    "--cov=texlint.journals.jss.rules.${CATEGORY}" \
    "--cov-branch" "--cov-fail-under=100"
set +e

# Steps 2–4: activate the venv so `jss-lint` is on PATH for `eval-jss scan`.
# shellcheck disable=SC1091
source "$ROOT/.venv/bin/activate"

# Soft-fail helper: treat exit 0 or 1 as success; only 2+ aborts.
run_step() {
    local label="$1"; shift
    echo
    echo "=== $label ==="
    "$@"
    local rc=$?
    if [[ "$rc" -ge 2 ]]; then
        echo "eval-category.sh: $label failed with exit $rc" >&2
        exit "$rc"
    fi
}

run_step "eval-jss scan" eval-jss scan
run_step "eval-jss human-review (interactive)" eval-jss human-review
run_step "eval-jss report" eval-jss report
