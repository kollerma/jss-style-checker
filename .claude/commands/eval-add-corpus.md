---
description: Step 1 — extend eval/corpus-manifest.csv with new CRAN papers and fetch them
argument-hint: "[space-separated CRAN packages; empty = use suggester]"
---

# Step 1 — add manuscripts to the corpus

Target additions: `$ARGUMENTS`. If empty, invoke the built-in suggester
to pick 50 vignette-bearing packages not already pinned:

```bash
source .venv/bin/activate
eval-jss corpus suggest --limit 50
```

Show the suggester output to the user and pause for their go-ahead
(they may want to narrow the list or swap entries).

For each approved package:

1. Look up the current CRAN version (use the version from the suggester,
   or fetch `https://cran.r-project.org/web/packages/<pkg>/` to confirm).
2. Download `https://cran.r-project.org/src/contrib/<pkg>_<version>.tar.gz`
   and compute its SHA256.
3. List the tarball to find a vignette under `<pkg>/vignettes/`
   (prefer `.Rnw`, then `.Rmd`; skip packages whose vignettes are
   `.pdf`-only).
4. Append a manifest row to `eval/corpus-manifest.csv`:
   `,cran,<pkg>,<version>,<vignette_file>,cran_<pkg>/,<sha256>`.

Then materialize everything:

```bash
eval-jss corpus fetch
```

If `eval/corpus-manifest-gaps.csv` has new rows, surface them.

Report how many packages were added, how many failed, and the current
corpus size.

End your reply with the literal line: `Next: /eval-scan`
