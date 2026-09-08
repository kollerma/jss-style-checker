# What "no findings" does and does not mean

`jss-lint` reports two very different things, and only one of them has
been visible until now.

**Precision** — of the findings it reports, how many are real — has been
measured and published since 1.0: per-rule confidence tiers,
`--min-confidence`, and the README badge all come from it.

**Recall** — of the style problems that exist, how many it finds — is
the one that decides what a *clean* run is worth. Since 1.2.0 the tool
reports it everywhere it reports anything.

```
$ jss-lint paper.tex refs.bib
No findings does not mean compliant. Measured recall: 81% (1967 annotated instances, 17 papers).
```

## How recall is measured

Seventeen real JSS papers carry hand-written annotations recording every
style problem a human found in them: 1 967 annotated instances in total
(`eval/recall-corpus/`, one `annotations.toml` per paper). `eval-jss
recall` lints those papers and checks, per rule, how many annotated
instances the rule caught (`tp`) and how many it missed (`fn`).

One run is pinned per release into
[`specs/003-jss-rule-catalogue/recall.json`](../specs/003-jss-rule-catalogue/recall.json)
and shipped with the rule set, so the number a release reports is the
number that release measured — and so the wheel, the WASM bundle, and
the CRAN binary can report it without carrying the eval database.

### It is a lower bound

The corpus annotates what a reader can see **in the source**. Problems
that only show up in the compiled PDF — a figure that is illegible at
print size, a table that overflows the column, a citation that renders
wrongly — are not annotated, so they are neither caught nor counted as
missed. Read
[`eval/recall-corpus/README.md`](../eval/recall-corpus/README.md) for
the full caveat. Treat 81 % as "at best 81 %".

### The three states

| Shown | Means |
|---|---|
| `81%` | at least 10 annotated instances; this is a measurement |
| `limited (n=4)` | 1–9 annotated instances; too few to state a percentage |
| `unmeasured` | no annotated instances at all — the corpus never exercised this rule |

A rule with two annotated instances that caught one is **not** 50 %
accurate; it is unmeasured in any useful sense, and printing "50 %"
would read as a measurement. That is why the threshold exists.

`unmeasured` is never rendered as `100%`. The `project` category — whose
rules detect `\input` cycles and unresolved references — has no
annotated instances at all, and says so.

## Where it appears

| Surface | What you see |
|---|---|
| author terminal / HTML | the footer above, on every run including a clean one |
| `--mode reviewer` | a `Recall` column per category, and `Measured recall:` under the compliance percentage |
| `--output json` | `recall` on each category, and `rule_set.recall` with the run's provenance |
| `--output sarif` | `properties.recall` and `properties.confidence` on each rule descriptor |
| `jss-lint explain RULE` | a `Recall:` line, for every rule |
| the catalogue page | `Confidence` and `Recall` columns |
| the README badge | the same shipped snapshot |

All integers: the percentage is computed with integer half-up rounding
so the Python and Rust engines can never disagree on a value that lands
on .5.

## Keeping it honest

CI runs `eval-jss recall --gate --no-record` on every push. The gate
fails when aggregate recall drops below **0.78** — about fifty false
negatives of slack under the shipped 0.807, so adding a corpus paper
that happens to exercise a weak rule does not turn CI red — or when any
single rule's recall regresses by more than 0.05 against the last
recorded run, which is the case a single aggregate would hide.

The floor is ratcheted at each release to `floor(snapshot − 0.03, 2 dp)`,
and a unit test fails if it is ever left further behind than that. It
was 0.70 through 1.1.0, which was ten points of slack under a number now
printed in every author footer.

# What is not checked

Recall says how much of what the tool *looks for* it finds. Coverage
says what it looks for at all — which provisions of the four JSS
authorities have a rule behind them, and which do not.

```
$ jss-lint coverage
Guide coverage — jss (rule set 2026-09-07)
76 checked, 4 partial, 5 not checked, 64 out of scope
…
$ jss-lint coverage --format markdown   # one table per authority
$ jss-lint coverage --format json       # every directive, with provisions
```

The matrix lives in
[`specs/003-jss-rule-catalogue/guide-coverage.yaml`](../specs/003-jss-rule-catalogue/guide-coverage.yaml),
one row per provision of `jss.cls`, `article.tex`, the style guide, and
the author instructions, each pinned to a dated edition (the prose pages
have no edition, so the fetch date is the honest pin).

| Status | Means |
|---|---|
| `checked` | a rule enforces this provision |
| `partial` | enforced in part; the `reason` says what is missing |
| `not_checked` | a real gap; the `reason` says why |
| `out_of_scope` | not checkable from the manuscript source at all |

**Out of scope is not a gap.** Two thirds of the provisions are things
no source-level linter could check: that the manuscript compiles, that
graphics are legible at print size, that the replication script runs in
an hour, that the upload is under 50 MB. They are listed — you should
read them before submitting — but excluded from the ratio the footer
prints, which counts only what is checkable:

```
jss-lint checks 80 of 85 guide directives (5 not checked, 4 partial). Run jss-lint coverage for the list.
```

Reviewer mode ends with the gaps themselves, `partial` first:

```
──────────────────────── Not checked by jss-lint ────────────────────────
│ SG-008    │ partial     │ MUST: All titles in the BibTeX file are in title style │
│ SG-010    │ not checked │ MUST: Figure/table captions are in sentence style      │
Run jss-lint coverage for the full matrix (76 checked, 4 partial, 5 not checked, 64 out of scope).
```

`jss-lint explain RULE` reports the reverse direction — which provisions
a rule enforces (`Covers: SG-027, SG-028`).

## Keeping the matrix honest

A coverage claim that has quietly gone stale is worse than none, so the
file is validated, not just written:

- every rule a directive names must be **active** — the markdown
  checklist this replaced credited four rules that had been retired
  months earlier, and nothing caught it;
- every active rule must be claimed by at least one directive
  (Constitution §V: a rule without a provision behind it is an opinion);
- every non-`checked` row must carry a reason;
- ids, sources, and section anchors must agree.

`tools/_coverage_validate.py` runs in the codegen and in
`tests/unit/journals/jss/test_guide_coverage.py`, so adding a rule
without claiming a provision, or retiring one without re-judging the
rows that credited it, fails the build.

## Reproducing a measurement

```sh
eval-jss corpus fetch && python -m eval.recall_corpus_scaffold  # materialise the corpus
eval-jss recall                       # per-rule tp/fn, aggregate, pooled thin rules
eval-jss recall --gate --no-record    # what CI runs
python -m tools.generate_recall_snapshot --run-timestamp <TS>   # pin a run
```

The corpus is defined by a pinned manifest with SHA256 hashes
(Constitution §XII), so a measurement is reproducible from a corpus
commit hash — which is what any precision or recall claim in the paper,
the release notes, or a PR description has to cite.
