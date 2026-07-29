Replication materials for
"jss-lint: Automated Style Checking for JSS Manuscripts"

Contents
--------
replicate.sh            standalone replication script (see below)
replication-output.txt  transcript of one complete run of replicate.sh
paper.tex, paper.bib    manuscript sources
jss.cls, jss.bst,       JSS class files, so the manuscript compiles
jsslogo.jpg               from this directory with pdflatex + bibtex
examples/demo.tex       the intentionally non-compliant demonstration
                          manuscript of Section 2.2
generated/              every statistic, table body, and listing the
                          manuscript inputs; nothing in the paper is
                          typed by hand

Replication
-----------
    bash replicate.sh

The script installs the released tool from PyPI at the version the
paper states (the only network access), re-runs every command
demonstrated in the paper, prints each command with its output, and
verifies the output matches the paper:

  1. jss-lint examples/demo.tex      seven violations, exit status 1,
                                       byte-identical to Figure 1
  2. jss-lint --fix --dry-run        diff byte-identical to the
       --no-resolve demo.tex           listing in Section 7.1
  3. jss-lint explain JSS-CITE-003   byte-identical to the listing in
                                       Section 7.1
  4. jss-lint --mode reviewer        JSON output matches Table 5
       examples/demo.tex
  5. jss-lint paper.tex paper.bib    the self-compliance claim of
                                       Section 6.5: zero violations
  6. the R session of Section 7      output identical to the printed
                                       session (runs only if Rscript
                                       with the jsslintr package is
                                       available; install.packages("jsslintr"))

Requirements: bash and Python >= 3.10 with venv + pip. Step 6
additionally needs R with the jsslintr package from CRAN.

The evaluation underlying the paper's precision/recall figures is
pinned in the development repository (see Section 6.5); its labels
ship there as eval/labels-export.csv.gz for independent audit.
