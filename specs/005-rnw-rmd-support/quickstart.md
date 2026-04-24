# Quickstart — Rnw / Rmd Support

Hands-on onboarding for a contributor working on spec 005. Assumes
`pip install -e '.[dev]'` has been run once.

## 0. One-time prep

```bash
pip install -e '.[dev]'         # picks up pyyaml as a runtime dep

scripts/vtest.sh tests/         # baseline: all green before you start
```

## 1. Add the Rnw stripper (US1 / FR-001)

Edit `src/texlint/core/parser.py`:

1. Add the `_RNW_CHUNK` and `_RNW_SEXPR` regex constants and the
   `strip_rnw_chunks(src)` helper per `contracts/rnw-stripper.md`.
2. Add `parse_rnw_file(path)` that composes `strip_rnw_chunks` with
   `parse_tex_file`. The returned `ParsedTexFile.source` holds the
   stripped text (line-preserving); `ParsedTexFile.path` is the
   original `.Rnw` path.
3. Write `tests/unit/test_rnw_stripper.py` first — the line-count
   invariant (`test_line_count_invariant`) is the most important
   single test. Other cases from the contract's test matrix.

## 2. Add the Rmd parser (US2 / FR-002)

Create `src/texlint/core/rmd_parser.py`:

1. Define `ParsedRmdFile` and its helper dataclasses in
   `src/texlint/api.py` per `data-model.md §2`. Frozen, with
   defaults where appropriate.
2. Implement `parse_rmd_source(path, src)` as the state machine in
   `contracts/rmd-parser.md`.
3. Implement `parse_rmd_file(path)` as a thin read-and-delegate wrapper.
4. Write `tests/unit/test_rmd_parser.py` — the test matrix from
   `contracts/rmd-parser.md` is a direct mapping to pytest cases.

## 3. Wire engine dispatch (FR-013)

Edit `src/texlint/core/engine.py`:

1. Add `_PARSERS` dispatch map per `contracts/engine-dispatch.md`.
2. Replace existing per-path parsing logic with a single
   `parse_document(paths)` call.
3. Extend `parse_document` to emit `ParsedRmdFile` into
   `ParsedDocument.rmd_files`.

## 4. Extend the API (FR-007, FR-008, FR-013)

Edit `src/texlint/api.py`:

1. Add `ParsedRmdFile` + its helper dataclasses.
2. Extend `ParsedDocument` with `rmd_files` and `all_tex_like()`.
3. Add `SkippedRule` dataclass and `ComplianceReport.skipped_rules`
   field.
4. Update `Rule.formats` docstring to reflect the input-format filter
   semantics.

## 5. Engine filter + skipped-rule bookkeeping (FR-008, FR-009)

In `engine.run`:

1. Derive `input_formats` as `{f._input_format for f in
   doc.all_files()}`.
2. Filter rules: `if rule.formats and not (rule.formats & input_formats): append to skipped_rules; continue`.
3. Populate `ComplianceReport.skipped_rules` on return.

Terminal / JSON / HTML renderers emit the skipped-rules section when
`cfg.verbose` is True (or always in JSON). See
`contracts/rule-format-filter.md`.

## 6. Narrow preamble rules' `formats` (FR-020)

Edit `src/texlint/journals/jss/rules/preamble.py`:

```python
jss_pre_001 = _rule(
    "JSS-PRE-001", check_jss_pre_001,
    formats=frozenset({"tex", "rnw"}),  # Rmd has no LaTeX preamble
)
```

Extend `_rule(...)` to take an optional `formats=` kwarg (default
`None`). Update all 8 preamble rules to pass
`formats=frozenset({"tex", "rnw"})`. No other rule module is touched.

Re-run `scripts/vtest.sh tests/unit/rules/test_preamble.py
--cov=texlint.journals.jss.rules.preamble --cov-branch
--cov-fail-under=100` to confirm 100% branch coverage after the
change.

## 7. Fixtures

```text
tests/fixtures/compliant/
├── minimal.Rnw                          # Sweave fixture with a clean chunk
└── minimal.Rmd                          # Rmd with frontmatter + heading + prose + r-chunk

tests/fixtures/violations/
├── rnw/
│   └── JSS-MARKUP-002-bad.Rnw           # prose says "the MASS package"; chunk has `library(MASS)`
└── rmd/
    └── JSS-MARKUP-002-bad.Rmd           # prose says "the MASS package"; ```{r} chunk has library(MASS)
```

Each `bad` fixture is the bad content of exactly one rule, and the
chunk / code block contains a string that would also match the rule
**if the format-filter or code-skip logic leaked**. The test asserts
the rule fires on the prose line and does not fire on the
chunk/fence lines.

## 8. Corpus expansion (FR-019)

Edit `eval/corpus-manifest.csv` to append 3–5 `.Rnw` rows and 2–3
`.Rmd` rows for CRAN-vignette packages. Start with:

```csv
,cran,lme4,1.1-35.1,lme4/inst/doc/lmer.Rnw,lme4_vig/,<sha256>
,cran,zoo,1.8-12,zoo/inst/doc/zoo.Rnw,zoo_vig/,<sha256>
,cran,ggplot2,3.5.0,ggplot2/vignettes/ggplot2.Rmd,ggplot2_vig/,<sha256>
```

Run `eval-jss corpus fetch` to materialise + pin hashes.
Verify each paper scans without errors: `eval-jss scan
--corpus examples/<vig>/`.

## 9. `eval-jss report --by-format` (FR-016, SC-006)

Edit `eval/report.py`: add `--by-format` flag that partitions the
violation set by `papers.path.suffix.lower()` and emits a per-format
precision row. Default (no flag) output is unchanged.

## 10. Regression sanity (FR-015, SC-003)

Before committing:

```bash
# Capture pre-feature counts.
eval-jss scan --force
eval-jss report > /tmp/report-before.txt

# ... make changes ...

eval-jss scan --force
eval-jss report > /tmp/report-after.txt
diff /tmp/report-before.txt /tmp/report-after.txt  # must be empty for .tex subset
```

## End-of-spec checkpoint

Spec 005 closes when:

1. `scripts/vtest.sh tests/` is green with 0 xfailed.
2. Every one of the 58 spec-004 rules still holds 100% branch
   coverage.
3. Rnw stripper and Rmd parser each have their contracts'
   invariants covered as pytest cases.
4. `jss-lint paper.Rnw` and `jss-lint paper.Rmd` behave as the spec's
   acceptance scenarios describe.
5. Corpus expansion (FR-019) is complete and pinned.
6. `eval-jss report --by-format` shows per-format precision slices.
