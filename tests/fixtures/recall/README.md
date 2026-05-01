# Recall fixtures (mutation testing)

Per-rule planted-violation files used to bound the recall metric
`recall = caught_plants / total_plants`. Each fixture is a minimal
JSS-class document containing exactly one (or counted-many) instances
of the rule's target pattern. The accompanying
`tests/eval/test_recall.py` runs the linter on each plant and asserts
the corresponding rule fires.

The `tests/fixtures/violations/<category>/<RULE>-bad.*` fixtures are
TP smoke checks (one canonical bad shape per rule). The recall
fixtures here are broader: 5–10 distinct mutations per rule designed
to surface FN holes — phrasing variants, edge cases, and rule-specific
tricks that the canonical bad fixture doesn't exercise.

Layout:

    tests/fixtures/recall/<RULE>/
        plant-<NN>-<short-name>.<ext>      # the mutated source
        plant-<NN>-<short-name>.expected   # space-separated rule_ids
                                            # the linter MUST fire on
                                            # this file (one per line)

When a rule's recall drops below `iteration-policy.recall.min_recall`
(default 0.70), `/eval-investigate` should NOT silence the rule
further (FP fixes that also lose TPs are blocked); the loop pivots
to recall improvement instead.

Initial coverage: the four FAIL rules from iter-71 — CAP-003 (38%),
TYPO-004 (89%), BIBTEX-002 (82%), NAME-001 (80%). Extend to the
remaining 49 rules incrementally.
