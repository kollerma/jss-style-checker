Must-do before writing — these decide your headline numbers

  1. Label the 11,267 pending violations (60% of the table). The parser recovery added ~13k violations from files that previously couldn't be scanned, and almost
  none are labeled. Every precision number the paper would report currently describes only the pre-fix half of the corpus. This is one /eval-review pass
  (Bonsai/Qwen3 routing already exists) plus /eval-human-review for the skip-listed rules. Biggest pending piles: CODE-003 (2,218), MARKUP-003 (2,182), XREF-002
  (882).

  2. Fix stale-row accounting in the precision stats. _persist_violations is INSERT-OR-IGNORE and the precision query has no run filter, so violations that
  stopped firing count forever. Concretely: live-label MARKUP-001 precision still reads 0.899 because the 40 FPs the guards silenced are still in the denominator
  — the improvement we just shipped is invisible in the headline table. Add a last_seen_run_id (or rebuild via the iterate-refresh flow) so the paper reports
  "precision of the current tool on the current corpus," not a historical union. Small change, large honesty payoff.

  3. Thicken the recall corpus. 11 papers, and several rules sit at 1–3 plants — STRUCT-005 at "recall 0.5" means 1 of 2. A reviewer will not accept per-rule
  recall on n=2. Either annotate ~5 more papers or have the paper report recall only for rules with ≥N plants and say so.

  Worth one investigation cycle each — reviewers will poke these

  - JSS-REFS-003 recall 0.448 — your most voluminous rule misses half its plants. Either the rule or the annotations are wrong; one /eval-investigate cycle
  settles it. Same triage for XREF-004 (0.638), WIDTH-001 (0.615), OPER-004 (0.474), CAP-004 (0.4), and REFS-002 (0/3 — never fires; possibly dead).
  - CITE-002 (0.908) and CAP-002 (0.918) precision — the two FP classes we deferred: the citation-proximity window and proper-noun handling. Both have known fix
  directions from the labeled reasons.
  - Corpus external validity: it's 100% R/CRAN vignettes. JSS publishes Python, MATLAB, Stata, Julia papers (~115 noted as inaccessible in the improvement log).
  Either hand-curate 5–10 non-R manuscripts from author GitHubs/arXiv so the paper can claim cross-language coverage, or scope the claims explicitly to R
  vignettes. Deciding this before writing avoids a structural rewrite later.
  - Label provenance. Of 7,565 labels, how many are human-verified vs single-model AI? Iteration 80 proved the AI labelers self-contradict. The paper needs a
  defensible labeling methodology section — the labeler benchmark (934-row gold set) is your asset here; consider re-running it post-routing so the numbers cited
  are current.

  Release hygiene before submission

  - Publish the artifacts: PyPI (jss-lint), VS Code marketplace, version bump from 0.1.0, pin the bibtexparser>=2.0.0b6 beta. JSS requires working replication
  materials — the eval pipeline is yours, but it needs a one-command reproduction entry point.
  - Stale docs: vscode-extension/README.md still says "Status (spec 012): scaffolded… not yet shipped." It's neither.
  - Windows: the CLI/LSP have never been exercised there (path handling, process spawn). A CI matrix entry is cheap insurance.
  - Performance table: eval/benchmark.py exists — produce the "239 papers in X seconds, Y ms median per manuscript" numbers the paper will want.

  One paper-shaping thought

  Write the manuscript in jss.cls and dogfood jss-lint on it from day one — and consider making the jss5342-versions trajectory analysis (violations across

  My suggested order: 1 → 2 → 3 (they gate everything), then REFS-003, then the corpus-diversity decision, with release hygiene parallel to writing. Items 1+2
  together are roughly a day of compute-bound work; happy to start on them.

  ---


  Tier 1 — pivotal for the paper's pass/fail (do first)

  These sit right at the 90% line, so your labels decide PASS vs FAIL:

  - JSS-CITE-002 — 13 pending, exactly 90.0%. Tiny and decisive; 13 labels tip it either way.
  eval-jss human-review --rule JSS-CITE-002
  - JSS-MARKUP-003 — 320 pending, 87%. The biggest lever in the corpus: it's just under threshold and has the most unlabeled rows, so these determine whether it
  can clear 90%. Do it in chunks:
  eval-jss human-review --rule JSS-MARKUP-003 --limit 50

  Tier 2 — only you can do these (skip-listed; AI is excluded by design)

  The classifier never touches these, so they sit pending until a human rules:

  - JSS-OPER-002 — 259 pending (99% on labeled — confidence-building, not pivotal)
  - JSS-NAME-002 — 62 pending (99%; the publisher-canonicalization rule the AI flips)
  - JSS-CAP-003 — 5 pending, plus please eyeball id 806271 ("The Hidden Markov Model") — the one case I flagged as genuinely borderline even under your strict
  2+-offender ruling (I called it FP; "Hidden"+"Model" could read as 2 offenders).
  eval-jss human-review --skip-listed  (covers all three at once)

  Tier 3 — skip for now

  XREF-002 (100%), CODE-003 (99%), XREF-004 (97%), CITE-003 (100%), the REFS/PRE/BIBTEX rules — all high-precision with hundreds of existing labels. Reviewing
  Three tiers:

  Tier 1 — pivotal for the paper's pass/fail (do first)

  These sit right at the 90% line, so your labels decide PASS vs FAIL:

  - JSS-CITE-002 — 13 pending, exactly 90.0%. Tiny and decisive; 13 labels tip it either way.
  eval-jss human-review --rule JSS-CITE-002
  - JSS-MARKUP-003 — 320 pending, 87%. The biggest lever in the corpus: it's just under threshold and has the most unlabeled rows, so these
  determine whether it can clear 90%. Do it in chunks:
  eval-jss human-review --rule JSS-MARKUP-003 --limit 50

  Tier 2 — only you can do these (skip-listed; AI is excluded by design)

  The classifier never touches these, so they sit pending until a human rules:

  - JSS-OPER-002 — 259 pending (99% on labeled — confidence-building, not pivotal)
  - JSS-NAME-002 — 62 pending (99%; the publisher-canonicalization rule the AI flips)
  - JSS-CAP-003 — 5 pending, plus please eyeball id 806271 ("The Hidden Markov Model") — the one case I flagged as genuinely borderline even
  under your strict 2+-offender ruling (I called it FP; "Hidden"+"Model" could read as 2 offenders).
  eval-jss human-review --skip-listed  (covers all three at once)

  Tier 3 — skip for now

  XREF-002 (100%), CODE-003 (99%), XREF-004 (97%), CITE-003 (100%), the REFS/PRE/BIBTEX rules — all high-precision with hundreds of existing
  labels. Reviewing these adds almost nothing.

  Optional, separate concern — MARKUP-001 (74%, failing). Its 108 pending won't rescue it, but its precision now rests heavily on the dense AI
  review. If you want to be sure that 74% is real before the paper cites it, spot-check the AI labels rather than the pending ones:
  eval-jss human-review --rule JSS-MARKUP-001 --reverify-ai --limit 30

  My suggested order: CITE-002 (5 min, decisive) → a MARKUP-003 chunk (the real lever) → --skip-listed for the OPER-002/NAME-002/CAP-003 backlog
  only you can clear. Want me to start a /loop or just hand you the commands to run in your ! shell? Note human-review is an interactive TUI,
  so you'll need to run it yourself — I can't drive it from here.

---