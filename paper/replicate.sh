#!/usr/bin/env bash
# ==========================================================
# replicate.sh — Replication script for:
#
#   "jss-lint: Automated Style Checking for
#    Journal of Statistical Software Manuscripts"
#
# This script reproduces all terminal listings shown in the
# paper and validates that the paper itself passes jss-lint
# with zero violations.
#
# Requirements:
#   - Python 3.10+ with pip
#   - jss-style-checker (installed below if absent)
#   - The paper source files (paper.tex, paper.bib)
#     must be in the same directory as this script.
#
# Usage:
#   cd paper/
#   bash replicate.sh
# ==========================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ----------------------------------------------------------
# Step 0: ensure jss-style-checker is available
# ----------------------------------------------------------
echo "=== Step 0: checking jss-style-checker installation ==="
if ! command -v jss-lint &>/dev/null; then
    echo "jss-lint not found; installing jss-style-checker..."
    pip install jss-style-checker
fi
echo "jss-lint version: $(jss-lint --version)"
echo

# ----------------------------------------------------------
# Step 1: validate the paper (dogfooding)
#   This reproduces the claim in Section 8 that the paper
#   itself passes jss-lint with zero violations.
# ----------------------------------------------------------
echo "=== Step 1: validate paper.tex and paper.bib ==="
echo "Command: jss-lint paper.tex paper.bib"
echo
if jss-lint paper.tex paper.bib; then
    echo "Result: 0 violations (exit code 0)"
else
    EXIT_CODE=$?
    echo "WARNING: jss-lint exited with code $EXIT_CODE"
    echo "The paper has unresolved violations."
    echo "Please fix them before submission."
fi
echo

# ----------------------------------------------------------
# Step 2: reviewer mode
#   Reproduces the compliance table shown in Section 5.4
# ----------------------------------------------------------
echo "=== Step 2: reviewer mode (Section 5.4) ==="
echo "Command: jss-lint --mode reviewer paper.tex paper.bib"
echo
jss-lint --mode reviewer paper.tex paper.bib || true
echo

# ----------------------------------------------------------
# Step 3: JSON output
#   Reproduces the JSON schema discussion in Section 5.5
# ----------------------------------------------------------
echo "=== Step 3: JSON output (Section 5.5) ==="
echo "Command: jss-lint --output json paper.tex paper.bib"
echo
jss-lint --output json paper.tex paper.bib \
    | python3 -m json.tool
echo

# ----------------------------------------------------------
# Step 4: HTML output
#   Generates the HTML report mentioned in Section 5.5
# ----------------------------------------------------------
echo "=== Step 4: HTML output (Section 5.5) ==="
echo "Command: jss-lint --output html paper.tex > report.html"
echo
jss-lint --output html paper.tex paper.bib > report.html
echo "HTML report written to: report.html"
echo

# ----------------------------------------------------------
# Step 5: rule suppression example (Section 5.6)
# ----------------------------------------------------------
echo "=== Step 5: rule suppression example (Section 5.6) ==="
echo "Command: jss-lint --ignore-rule JSS-CITE-001 paper.tex"
echo
jss-lint --ignore-rule JSS-CITE-001 paper.tex paper.bib \
    || true
echo

# ----------------------------------------------------------
# Step 6: programmatic API example (Section 5.7)
# ----------------------------------------------------------
echo "=== Step 6: programmatic API (Section 5.7) ==="
cat <<'PYEOF'
Command: python3 api_example.py
PYEOF

cat > /tmp/jss_api_example.py <<'PYEOF'
from texlint.core.parser import (
    parse_tex_file, parse_bib_file
)
from texlint.api import ParsedDocument, ToolConfig
from texlint.core.engine import run

tex = parse_tex_file("paper.tex")
bib = parse_bib_file("paper.bib")
doc = ParsedDocument(
    tex_files=[tex], bib_files=[bib]
)
config = ToolConfig(
    journal="jss",
    mode="author",
    output_format="terminal",
    ignore_rules=frozenset(),
)
report = run(doc, config)
print(
    f"{report.compliance_percentage:.0f}% compliant"
)
for v in report.violations:
    print(
        f"  {v.line}:{v.column}  {v.rule_id}"
        f"  {v.message}"
    )
PYEOF

python3 /tmp/jss_api_example.py
echo

# ----------------------------------------------------------
# Done
# ----------------------------------------------------------
echo "=== Replication complete ==="
echo
echo "All listings from the paper have been reproduced."
echo "If Step 1 reported 0 violations, the manuscript is"
echo "ready for JSS submission with respect to style."
