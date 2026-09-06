# Quickstart: adopting jss-lint 1.2.0 on an existing manuscript

## For an end user

### Five commands

```sh
pip install "jss-style-checker~=1.2.0"        # or: cargo install jsslint-cli --version "^1.2"
jss-lint paper.tex refs.bib                   # 1. first run: read the findings and the footer
jss-lint --mode reviewer paper.tex refs.bib   # 2. per-category table with recall + "Not checked"
jss-lint --baseline .jss-lint-baseline.json --update-baseline paper.tex refs.bib   # 3. accept today
git add .jss-lint-baseline.json && git commit -m "Accept current jss-lint findings"  # 4. keep it
jss-lint --baseline .jss-lint-baseline.json paper.tex refs.bib   # 5. exit 0; exit 1 only on new findings
```

Numbers in the samples below are illustrative; the real ones come from
the data shipped with the release.

### 1. The first run and its footer

Author mode lists every finding as before. New in 1.2.0: the run always
ends with two lines, also when there are no findings at all.

```
No findings does not mean compliant. Measured recall: 81% (1967 annotated instances, 17 papers).
jss-lint checks 118 of 146 guide directives (9 not checked, 6 partial). Run jss-lint coverage for the list.
```

Exit codes are unchanged: `0` clean, `1` findings at or above `--fail-on`,
`2` the tool could not complete. The footer goes to stdout, so a saved
text report of a clean run is no longer an empty file.

### 2. Reviewer mode: what was measured, what was not

```
              Journal compliance — jss
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ Category         ┃ Status ┃ Applied ┃ Passed ┃ Recall        ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ Preamble         │ PASS   │       8 │      8 │ limited (n=8) │
│ Citations        │ FAIL   │       3 │      2 │ 79%           │
│ …                │        │         │        │               │
│ Project          │ PASS   │       2 │      2 │ unmeasured    │
└──────────────────┴────────┴─────────┴────────┴───────────────┘
Overall: 93.8%
Measured recall: 81% (1967 annotated instances, 17 papers, run 2026-07-19)
──────────────────────── Not checked by jss-lint ────────────────────────
┏━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Directive ┃ Status      ┃ Provision                                   ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ SG-014    │ partial     │ Title style capitalises all principal words │
│ SG-020    │ not checked │ Abbreviations are expanded at first use     │
│ SG-024    │ not checked │ Table row/column headers in sentence style  │
└───────────┴─────────────┴─────────────────────────────────────────────┘
Run jss-lint coverage for the full matrix (118 checked, 6 partial, 9 not checked, 13 out of scope).
```

Three recall states: a percentage means at least 10 annotated instances;
`limited (n=K)` means fewer, so no percentage is printed; `unmeasured`
means the annotated corpus contains no instance of any rule in that
category. `unmeasured` is never shown as `100%`.

### 3. Accept the current state

```sh
jss-lint --baseline .jss-lint-baseline.json --update-baseline paper.tex refs.bib
# jss-lint: wrote 212 baseline entries to .jss-lint-baseline.json
```

The file is plain JSON, sorted, without a timestamp, and identical
whichever engine wrote it:

```json
{
  "entries": [
    {"count": 1, "message": "BibTeX entries include a doi field where one is available (advisory)",
     "path": "refs.bib", "rule_id": "JSS-REFS-003",
     "suggestion": "Add a doi field to entry 'koller2023' if one is available."}
  ],
  "journal": "jss",
  "ruleset_version": "2026-09-15",
  "schema_version": 1,
  "tool_version": "1.2.0"
}
```

Entries are keyed by rule, file (relative to the baseline file), message,
and suggestion — never by line number. Inserting paragraphs, rewording
sentences, and moving text do not disturb them.

### 4. Commit it

Commit `.jss-lint-baseline.json` next to the manuscript. Re-run
`--update-baseline` whenever you rename or move a file (paths are part of
the key) and after upgrading to a release whose rule-set date changed —
the summary line tells you:

```
Baseline: 212 findings hidden by .jss-lint-baseline.json (3 stale, 0 unevaluated) — written for rule set 2026-09-15, current 2026-11-02; run --update-baseline
```

`stale` entries are accepted findings that no longer occur (you fixed
them); `unevaluated` entries belong to rules that did not run in this
invocation (for example under `--min-confidence high`) and are neither
stale nor matched.

### 5. Fail only on new findings

```sh
jss-lint --baseline .jss-lint-baseline.json paper.tex refs.bib
```

Findings in the baseline are hidden from every output format and do not
affect the exit code. A finding whose rule, message, and suggestion are
not already accepted for that file is reported and exits 1. The `.jss-lint.toml`
equivalent:

```toml
baseline = ".jss-lint-baseline.json"
```

#### In CI with the GitHub Action

```yaml
- uses: kollerma/jss-style-checker@v1
  with:
    version: 1.2.0
    baseline: .jss-lint-baseline.json
    fail-on-severity: warning
```

Baselined findings are absent from the SARIF the Action uploads, so the
Security tab and the PR review only show what is new.

#### Known limits

- Two findings with the same rule, message, and suggestion in the same
  file are interchangeable: fix one and add another of the same shape
  and the new one stays hidden while the count holds. After 1.2.0 this is
  confined to rules whose suggestion is inherently repetitive
  (`JSS-WIDTH-001`, and token rules such as `JSS-MARKUP-001` when the same
  token recurs).
- Renaming a file invalidates its entries; run `--update-baseline`.
- A minor release may reword a rule; that rule's entries go stale and
  the summary line names both rule-set dates.

### What is not checked

```sh
jss-lint coverage                    # full matrix, grouped by status
jss-lint coverage --format markdown  # one table per source, for a README or issue
jss-lint coverage --format json      # every directive with provision, status, rules, reason
```

`out_of_scope` entries are requirements that cannot be checked from the
source (compilability, graphics legibility, replication scripts). Read
those before submitting; the tool cannot.

### Which rule set am I running?

```
$ jss-lint --version
jss-lint 1.2.0
engine: texlint/python 1.2.0
rule set: 2026-09-15 (jss.cls 3.3, vendored 2021-05-23)
journal: jss
```

`jsslint --version` prints the same block with `engine: jsslint-core/rust
1.2.0`. `docs/versions.md` maps every channel (crates.io, PyPI, npm, CRAN
`1.2.0-N`, CTAN, VS Code, the Action) to these lines and says what to
pin: the tool minor (`~=1.2.0`, `^1.2`, `version: 1.2.0`) plus a baseline.
Patch releases only remove findings; minor releases may add rules or
reword messages and bump the rule-set date.

### Colour

Colour is on when stdout is a terminal and off when it is piped or
redirected. `--color always|never` overrides everything; `NO_COLOR=1`
turns colour off; `CLICOLOR_FORCE=1` turns it on unless `NO_COLOR` is set;
`color = "never"` in `.jss-lint.toml` sets the default. JSON, SARIF, and
HTML are never coloured. Every coloured token is still a word, so
monochrome terminals lose nothing.

### Fixing with a receipt

```sh
jss-lint --fix --dry-run paper.tex refs.bib     # unified diff, nothing written
# Dry run: 3 fixes would be applied to 1 file. Re-run without --dry-run to write.
jss-lint --fix paper.tex refs.bib
# Applied 3 fixes to 1 file (1 skipped: conflict 1).
```

`--fix` never reads or changes version-control state. Commit or dry-run
first; writes are atomic and each fix is re-checked against its rule
before it is kept. With `--baseline`, only visible (unbaselined) findings
are fixed; drop the flag to fix accepted ones too.

### From Overleaf

- Menu → Download → Source gives a zip. Drop it on the
  [browser app](https://kollerma.github.io/jss-style-checker/); it is
  unpacked in the browser and nothing is uploaded.
- Or unzip and run `jss-lint main.tex` (auto-resolve follows `\input`).
- With Overleaf's GitHub Sync, add the Action to the synced repository;
  use a baseline for an existing project.

Details in `docs/overleaf.md`.

## For a contributor

### Where things live

```text
specs/003-jss-rule-catalogue/catalogue.yaml        # + ruleset_version, ruleset_fingerprint, guide_edition
specs/003-jss-rule-catalogue/recall.json           # generated recall snapshot (pinned run)
specs/003-jss-rule-catalogue/guide-coverage.yaml   # hand-curated directive matrix
specs/003-jss-rule-catalogue/messages.json         # generated; fingerprint input only
src/texlint/core/baseline.py   rust/jsslint-core/src/baseline.rs    # pure matcher + file shape
src/texlint/core/suppress.py   rust/jsslint-core/src/suppress.rs    # inline ignores, shared hook
src/texlint/coverage.py        rust/jsslint-core/src/coverage.rs    # `coverage` renderers
src/texlint/version.py         rust/jsslint-core/src/version.rs     # `--version` block
tools/generate_recall_snapshot.py  tools/generate_message_snapshot.py  tools/_coverage_validate.py
docs/versions.md  docs/baseline.md  docs/recall-and-coverage.md  docs/overleaf.md  docs/releasing.md
```

### Run the tests

```sh
export PATH="$PWD/.venv/bin:$HOME/.cargo/bin:$PATH"
python -m pytest tests/ -q && ruff check .
python -m pytest tests/unit/journals/jss/ --cov=src/texlint/journals/jss/rules --cov-branch --cov-fail-under=100
(cd rust && cargo test --workspace)             # incl. suppress_, baseline_, coverage_, version_, color_ parity
eval-jss recall --gate --no-record              # floor 0.78; needs the materialised recall corpus
```

### Common pitfalls

- **Rewording a message or suggestion** changes `messages.json`, which
  changes the fingerprint; `tools/generate_catalogue_data.py --check`
  fails until `--stamp-fingerprint --ruleset-version YYYY-MM-DD` is run
  with a new date. This is deliberate: users' baselines depend on that
  text.
- **Adding a rule** fails the coverage contract test until the rule is
  claimed by a directive in `guide-coverage.yaml`.
- **Retiring a rule** fails the same test until every directive that
  credited it is re-judged.
- **Touching a config field** breaks four struct-literal `RawOverrides`
  sites (CLI, WASM, PyO3, R) — add the field to all of them and re-run
  `r/jsslintr/tools/vendor-jsslint-core.sh`.
- **SARIF goldens** embed message and suggestion text; regenerate with
  `JSSLINT_REGEN_GOLDENS=1 pytest` after item S.
- **Colour** is never a byte-parity target; the plain stream is. Parity
  tests strip escape sequences before comparing.

### Where to extend

- Baseline in the R, PyO3, and WASM bindings: the matcher is pure; an
  in-memory variant needs only a path map over the caller's labels.
- Token-specific suggestions for the deferred rules (`REFS-005`,
  `REFS-006`, `NAME-002`, `HOUSE-002`, `BIBTEX-003/004/005`, `TYPO-004`,
  `XREF-006`): any minor release, with a rule-set bump.
- CLI zip input; SARIF `baselineState`; a Windows CI job for the colour
  path.
