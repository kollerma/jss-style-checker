---
description: Steps 6/7/8 — investigate one failing rule via subagent and implement the fix
argument-hint: "<JSS-XXX-NNN>"
---

# Step 6/7/8 — investigate + fix one failing rule

Target rule: `$ARGUMENTS`

Replaces the previous `/eval-suggest` + `/eval-plan` + `/eval-implement`
trio. The discovery phase can be delegated to a subagent (clean context
+ parallelizable) OR done inline in the main thread when the FP pattern
is already visible — see Step 2's heuristic. Either way the
implementation phase stays in the main thread for session continuity.

## Procedure

1. Confirm the rule has labelled FPs in `eval/eval.db`:

   ```bash
   source .venv/bin/activate
   python3 -c "import sqlite3; cx = sqlite3.connect('eval/eval.db'); print(cx.execute(\"SELECT COUNT(*) FROM violations WHERE rule_id='$ARGUMENTS' AND verdict='false_positive'\").fetchone()[0], 'FPs')"
   ```

   If 0, abort and tell the user; the rule is either passing or
   unmeasured.

2. **Decide whether to spawn a subagent.** The subagent buys you a
   clean context and parallel work, but adds coordination cost and a
   verification round. It pays off when the FP pattern is *not yet
   visible*; it's pure overhead when the pattern is already there
   for the reading.

   **Skip the subagent — investigate inline — when at least one of:**
   - **AI verdict_reason texts already cluster.** Pull a sample:

     ```bash
     python3 -c "import sqlite3; cx = sqlite3.connect('eval/eval.db'); [print(r[0]) for r in cx.execute(\"SELECT verdict_reason FROM violations WHERE rule_id='$ARGUMENTS' AND verdict='false_positive' AND reviewer LIKE 'ai:%' LIMIT 8\").fetchall()]"
     ```

     If three or more of these reasons name the same diagnostic
     phrase ("function call", "scientific notation", "filename",
     "casual shorthand", "already-marked-up"), the cluster is
     already named. Read 3–4 source contexts to confirm and write
     the fix.
   - **FP count ≤ 10.** Inspect them all by hand; faster than the
     round-trip.
   - **The fix touches more than one rule module.** Subagents return
     a 250-word summary; cross-module fixes are easier to land with
     full session context.

   **Spawn the subagent when:**
   - **FP count > 15** AND the verdict_reasons disagree or are
     missing.
   - **Multiple distinct mechanisms** are suspected (e.g., the rule
     touches both .Rnw and .Rmd surfaces).
   - **The rule's check function is long** (> 60 lines) and you
     need someone to map it before proposing changes.

   In subagent mode, brief verbatim (NOT in summary):

   > Investigate false positives for the JSS rule `$ARGUMENTS` in this
   > repo. Pull every row where `rule_id='$ARGUMENTS' AND
   > verdict='false_positive'` from `eval/eval.db` (join `papers`
   > for `paper_path`). For each, read the source file at the
   > violation's line/column with ±5 lines of context. Identify the
   > common pattern: what kind of input causes the rule to mis-fire?
   > Locate the rule's check function in
   > `src/texlint/journals/jss/rules/`. Read the bad fixture under
   > `tests/fixtures/violations/<category>/$ARGUMENTS-bad.*` and
   > confirm what the rule SHOULD flag. Propose the smallest code
   > change that suppresses the FP cluster without breaking the bad
   > fixture. Report under 250 words: (a) FP pattern with one
   > example, (b) `file:line` of the rule's check function, (c)
   > proposed diff outline (no need for exact code), (d) risk to
   > existing TPs and how to mitigate.

3. **Either way — read the report (your own or the subagent's)
   and decide:**

   - **High-confidence, single-pattern fix**: implement it inline.
     Run `pytest tests -q` AND `ruff check .` before declaring done.
   - **Multiple distinct FP patterns**: implement the largest
     cluster; defer the rest with a one-line note for the next
     iteration.
   - **Risky / unclear**: surface the report to the user with two
     concrete options and ask which to proceed with.

4. After implementation, run:

   ```bash
   eval-jss iterate refresh
   eval-jss report --diff
   ```

   The `iterate refresh` command bakes the wipe-rescan-restore-labels
   dance into one step; `report --diff` shows the per-rule TP/FP/
   precision deltas against the previous iteration.

5. If the rule's precision improved, snapshot via
   `/eval-record post-<rule>`. Otherwise, surface what went wrong.

## End of reply

End with one of these literal lines:

- `Next: /eval-record post-$ARGUMENTS` — fix landed, precision
  improved.
- `Next: /eval-investigate <other-rule>` — fix didn't land, but
  another rule looks more tractable.
- `Next: human` — needs a judgement call.
