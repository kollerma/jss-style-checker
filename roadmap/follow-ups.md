# Roadmap follow-ups

Each feature on the 12-spec roadmap shipped its core correctness
surface (engine + tests, ≥95% test coverage on new modules) plus a
documented set of deferrals. This file is the single tracker for
that deferred work, grouped by feature in roadmap order.

The shape of each item:

```
- [ ] **Feature 0NN** — short title (file/path) — one-line scope.
```

Order within each feature is roughly highest-to-lowest priority.
Items can land in any order; some unblock each other (noted
inline).

## v1 release triage (2026-06-12)

Triage of every open item below against a notional public v1 tag.
The recall corpus is annotated, aggregate recall is 0.771 (above
the 0.70 gate floor), 22 rules at perfect recall, 1514 tests pass.
The substantive engineering is done; the items below are
post-engineering: shipping decisions, fixes for known minor bugs,
and new-rule feature requests for v2.

**Release-blockers (must fix before v1 tag)**: none. The rule
surface, CLI, recall gate, and precision history are all
functional. The two precision-fragile rules (CAP-001, CAP-003) are
already addressed — CAP-001 is at 1.000 precision in the latest
pinned-corpus iteration after the 2026-06-11 work; CAP-003 is
explicitly `confidence: low` in the catalogue and hidden behind
`--min-confidence medium`. No additional code work is required to
ship v1.

**Ship-impact (worth doing before v1, small)**:
- L300 `Linter scans content after \end{document}` — small bug,
  3 FPs in jss816.Rnw. Easy to fix.
- L650 `MARKUP-001's recognised-language set is R-centric` — small
  table extension; adds support for non-R submissions (Python /
  Julia / Stan / etc.) which JSS welcomes.
- L371 `Bib-side rules should skip uncited entries` — already
  applied in `_iter_referenced_entries` for NAME-002 and
  CITE-002; extending to REFS-002/003/004/005/006/007 would
  meaningfully reduce REFS-003's enormous FP count in the example
  corpus.

**v1 distribution / publication tasks**:
- L127 `Promote tomli_w` — internal cleanup, post-v1
- L159 `vscode-extension build verification` — CI nicety
- L162 `Live publish to VS Code marketplace / Open VSX` — needs
  secrets; can do post-v1
- L166 `End-to-end smoke test inside headless VS Code` — depends
  on LSP server shipping
- L208 `Action source repo` — post-v1 distribution

**post-v1-fix (real bugs, ship in v1.1)**:
- L291 `CODE-003 line anchoring is inconsistent` — recall-corpus
  reconciliation surface; 28 corpus FNs are line-anchor mismatches
- L395 `JSS-CAP-002 should walk the optional [short] arg`
- L439 `JSS-CAP-001 should defer when first word is package name`
  (partial done; remaining is the MARKUP-002-set check)
- L948 `JSS-MARKUP-004 should exempt starred section forms`
- L673 `Rule-precision improvements (CITE-002, HOUSE-001)` — three
  carve-outs documented; high-precision, low-recall-cost fixes

**post-v1-feature (new rules / new functionality, ship in v2.x)**:
- L180 `Migrate ABBR rule to check_project`
- L304 `OPER-004 bare literal E / P in math mode`
- L348 `JSS-PRE-009 — preamble must not redefine jss.cls envs`
- L474 `JSS-CAP-003 over-eager on technical identifiers in
  captions` — 5/5 fix attempts exhausted; already `confidence:
  low` and gated behind `--min-confidence medium`. Document the
  limitation in the explanation text; don't try to fix the
  underlying heuristic without a fundamentally different approach
  (e.g., POS-tagging or a per-corpus learned classifier).
- L490 `JSS-REFS-003 (DOI advisory) entry-type coverage`
- L530 `JSS-REFS-004 (markup in bib titles) scope is incomplete`
  (partial done; note= field still uncovered)
- L545 `JSS-PRE-010 — Sweave/knitr preamble sets options()`
- L607 `JSS-MARKUP-005 — URLs in prose use \url{}/\href{}`
- L717 `JSS-BIBTEX-005 — bib entry type matches content`
- L769 `JSS-STRUCT-008 — appendix uses \appendix + plain \section`
- L822 `JSS-STRUCT-007 — figure-producing content wrapped in
  figure env`
- L868 `JSS-PRE-012 — Plain* matches markup-stripped form`
- L918 `JSS-PRE-011 — Plainauthor uses commas as separators`
- L1021 `JSS-CITE-006 — \citep where \citet required`
- L1054 `JSS-CITE-005 — every \cite*{key} resolves to bib entry`
- L1075 `JSS-XREF-005 — every \ref resolves to a \label`

**Already-shipped since this file's last triage** (verified):
- L411 partial (MARKUP-003 ↦ \code{} sweep)
- L425 brace-defeats package idiom (REFS-006)
- L439 partial (doc_pkgs_lower exemption)
- L530 partial (pattern-based package-prefix detection)
- L584 XREF-004 orphan-label check
- L967 CITE-003 widened to all cite-family + paren-balance scan

## Adversarial review round (2026-07-12) — manuscript follow-ups

Deferred items surfaced by the JSS adversarial review (see
`paper/review-2026-07-12.md`). Each is disclosed in the manuscript
and tracked here rather than papered over.

- [ ] **New rule — flags collapsed to a single dash / en-dash**
      (markup or typography category). A JSS author who types
      `\code{-fix}` (one hyphen) or lets a tt en-dash ligature stand
      where a two-hyphen long option (`--fix`) is meant produces a
      command that does not exist. Detect single-dash tokens inside
      `\code{}`/`\verb` that match a known long-option shape
      (`-[a-z]{2,}` where the tool's own option table has `--<same>`),
      and an en-dash (`–`) or em-dash inside inline code where a
      double hyphen is expected. **Provenance**: review F13 — the
      manuscript's own `\code{--fix}` rendered as an en-dash until the
      preamble disabled the tt `--` ligature (`\DisableLigatures`);
      a rule would catch the class in submissions.
      **Severity**: warning.

- [ ] **JSS-TYPO-004 is blind to `longtable` captions**
      (`src/texlint/journals/jss/rules/typography.py`). The
      captions-below-floats rule inspects `figure`/`table` floats but
      not `longtable`, so a top-caption on a `longtable` passes
      silently. **Carrier**: this manuscript's own appendix tables
      (Appendix A/B) had top captions the tool did not flag; corrected
      by hand for the 2026-07-12 revision. **Provenance**: review F14
      (the checklist L153 claim that TYPO-004 enforced this was
      falsified). **Fix**: extend the float scan to `longtable` and
      recognize the caption's position relative to the tabular body
      (a `\caption` before the first data row, or before the
      `\endfirsthead`/`\endhead` region, is a top caption).
      **Severity**: warning.

- [ ] **MARKUP-002/-001 recognized-name sets miss common packages**
      (`src/texlint/journals/jss/rules/markup.py`). The bare package
      name `lme4` in `examples/demo.tex` goes unflagged because
      `lme4` is not in the recognized-package set; the same gap
      applies to any package/language name outside the curated lists.
      **Provenance**: review F15 — the demo is not exhaustively
      caught, an in-paper instance of the MARKUP recall boundary
      (§6.3). **Fix**: grow the recognized sets from a maintained
      list (e.g. CRAN package index snapshot) rather than a
      hand-curated handful; pair with the confidence-tier design so
      the wider net does not cost precision. Needs labeling
      infrastructure for the new firings (deferred on this host).
      **Severity**: existing rule severity (warning).

- [ ] **Human spot-check of the six re-adjudicated CODE-003 rows**
      (`eval/`). The 2026-07-11 CODE-003 CLI-flag fix silenced six
      corpus violations previously labeled true positives; the
      re-adjudication (five label debt, one genuine subtraction) was
      performed by the same automated workflow that authored the fix,
      so it is not an independent check. **Provenance**: review F11.
      **Action**: a human should re-rule those six specific rows at
      source before the precision figure is frozen.

## Cross-cutting (touches multiple features)

- [x] **Click sub-group migration** (`src/texlint/cli.py`) — convert
      `jss-lint` from a single `@click.command` to a
      `@click.group(invoke_without_command=True, ...)` so subcommands
      can be added without breaking the existing positional-PATHS
      invocation. Unblocks the CLI surfaces of features 009, 010,
      011, 015, 016. (Shipped: every existing CLI integration test
      passes byte-identically; smoke tests at
      `tests/integration/test_cli_group_shape.py`.)

## Feature 006 — SARIF output

- [x] Renderer + tests + CLI flag (shipped).
- [x] Vendor the official SARIF 2.1.0 JSON schema at
      `tests/fixtures/sarif-2.1.0-schema.json` and add a contract
      test that validates every golden via
      `jsonschema.Draft202012Validator`. (Shipped: vendored from
      SchemaStore mirror as Draft 7; four parametrised scenarios.)
- [x] Multi-fixture golden files
      (`tests/fixtures/sarif/golden_*.sarif`). (Shipped: four
      scenarios — clean / single warning / parse error /
      multi-file — under
      `tests/integration/test_cli_sarif_goldens.py`. Volatile
      fields (version + full rule catalogue) are masked. Regen
      via `JSSLINT_REGEN_GOLDENS=1 pytest`.)

## Feature 007 — JSS-guide rule mapping

- [x] **Full catalogue backfill** —
      `specs/003-jss-rule-catalogue/catalogue.yaml`. (Shipped:
      all 58 rules carry guide_section + guide_url; index.json
      grew by 6 sections — Structure, Typography, Mathematical
      notation, Cross-references, Abbreviations, House style.)
- [x] Update the spec-007 contract test to fail (not warn) when
      a citable rule lacks `guide_section` / `guide_url`.
      (Shipped: `test_every_citable_rule_is_backfilled`.)
- [x] Plumb `guide_section` into the terminal renderer's
      `(see <section>)` suffix and into the HTML renderer as an
      `<a href="...">` anchor. (Shipped: terminal appends
      `(see §<section>)` for citable rules; HTML gains a Section
      column with anchor links; sentinel rules render plain.)

## Feature 008 — Auto-fix

- [x] **SARIF `fixes[]` projection** —
      `src/texlint/output/sarif.py`. When a violation has a `Fix`,
      emit `runs[0].results[].fixes[]` per spec-006 §C-11 +
      spec-008 §3.7.
- [x] **Rule-side `Fix` migrations** — pick three mechanical
      catalogue rules (`JSS-CITE-003`, `JSS-NAME-001`,
      `JSS-CAP-002` are the spec-008 baseline candidates) and
      emit `Fix(...)` payloads on their violations. (Shipped:
      JSS-CITE-003 and JSS-NAME-001 emit safe-confidence fixes;
      JSS-CAP-002 deferred — no stable byte range without a
      rule-body rewrite.)
- [x] `before.tex` / `after.tex` golden fixture pairs under
      `tests/fixtures/auto-fix/` for each migrated rule.
      (Shipped for JSS-CITE-003 and JSS-NAME-001.)
- [x] Integration test for `--apply` interactive prompt
      (stdin scripted with `y\nn\na\n`) — covered by unit tests
      today; end-to-end via the CLI runner is the missing piece.
      (Shipped: `tests/integration/test_cli_fix_apply.py`
      `TestApplyInteractive` scripts `y\n` and `n\n` over stdin
      against the JSS-CITE-003 fixture; `y` rewrites the file to
      match `after.tex` byte-for-byte, `n` leaves it untouched.)
- [x] Regression-rollback CLI integration test (a fixture rule
      whose fix re-trips its own rule; CLI exits 2 with the
      file unchanged). (Shipped:
      `tests/integration/test_cli_fix_apply.py`
      `TestRegressionRollback` registers a synthetic `regression`
      journal via `monkeypatch` on `importlib.metadata.entry_points`;
      its only rule emits a no-op `Fix` whose replacement equals the
      matched token, so the rule re-fires on re-validate and the
      engine rolls back to the pre-fix bytes — the test asserts
      exit 2, byte-identical file content, and that the rollback
      message names the rule id.)

## Feature 009 — `jss-lint explain`

- [x] CLI subcommand wiring — `jss-lint explain RULE-ID
      [--format {terminal,markdown}]` dispatches into
      `texlint.explain.render`; listing view (no rule id) supported;
      unknown rule id exits 2 with did-you-mean suggestions.
      (Shipped in the spec-009/010/015/016 CLI subcommand batch.)
- [x] Catalogue extension: add `explanation: str`,
      `example_bad: str | None`, `example_good: str | None` to
      every rule entry in `catalogue.yaml`. (Shipped: every rule
      carries a non-empty `explanation` (minimum-viable
      one-liner derived from message_template + guide_section);
      `example_bad` / `example_good` are independently optional
      OPTIONAL keys in the validator.)
- [x] `test_every_rule_has_explanation` contract test in
      `tests/unit/journals/jss/test_catalogue_citations.py`.
      (Shipped.)

## Feature 010 — `jss-lint init`

- [x] CLI subcommand wiring — `jss-lint init [PATH] [--force]
      [--dry-run] [--threshold T]` dispatches into
      `texlint.init.run`. Refusal-without-force exits 2; dry-run
      writes nothing. (Shipped.)
- [x] Precision-DB-aware suppression: query
      `eval/precision-history.db` per rule and emit suppressions
      for any rule below the `--threshold` (default 0.90).
      (Shipped: `texlint.init.run` reads the latest iteration's
      full-scope precision per rule and adds below-threshold rules
      to `ignore_rules` with audit-trail comments. Missing DB and
      NULL-precision rules fall back to no suppression.)
- [ ] Promote `tomli_w` from "hand-rolled TOML rendering" to a
      proper runtime dependency once the generated config gains
      structures (severity overrides, table-of-table sections)
      that the hand-roller can't easily produce.

## Feature 011 — Language Server

- [x] Add `pygls>=1.3` under a new `[project.optional-
      dependencies] lsp = [...]` group. (Shipped.)
- [x] `src/texlint/lsp/server.py` — pygls `LanguageServer`
      factory implementing didOpen / didChange (200ms debounce) /
      didSave / didClose / codeAction handlers plus the
      `jss-lint.applyAllFixes` workspace command. (Shipped.)
- [x] `src/texlint/lsp/cache.py` — `DocumentCache` keyed by
      `(uri, textDocument.version)`. (Shipped: 12 unit tests.)
- [x] `src/texlint/lsp/config_watch.py` — `reload(state, path,
      log)` handler invoked by the
      `workspace/didChangeWatchedFiles` feature. Malformed
      reloads keep the previous config + surface a
      `window/showMessage`. (Shipped.)
- [x] `tests/integration/test_lsp_session.py` — handler-level
      smoke tests (registered features, URI parsing, didOpen
      publishes, didClose clears, codeAction empty on cache
      miss). pygls 2.x doesn't ship a synchronous in-process
      test driver, so we exercise registered handlers
      directly. (Shipped: 10 tests.)
- [x] `jss-lint lsp` CLI subcommand. Lazy-imports pygls so the
      core CLI keeps working without the `[lsp]` extra; missing
      extra exits 2 with an install hint. (Shipped.)

## Feature 012 — VS Code extension

- [ ] `vscode-extension/` build verification — `npm install`,
      `npm run compile`, `vsce package` produces a `.vsix`.
      Requires Node 20+ in CI.
- [ ] Live publish to the VS Code marketplace and Open VSX —
      requires `VSCE_PAT` and `OVSX_PAT` secrets in the repo;
      the workflow at `.github/workflows/vscode-publish.yml`
      runs on `v*-vscode` tags.
- [ ] End-to-end smoke test inside a headless VS Code instance
      using `@vscode/test-electron`. Depends on the spec-011
      LSP server shipping first.

## Feature 013 — Multi-file projects

- [x] **`ParsedProject` public type** in `texlint.api` —
      wraps a tuple of `ParsedDocument`s, the root `Path`, and
      the project graph. (Shipped.)
- [x] **`Rule.check_project: Callable | None`** — additive
      field on the public `Rule` dataclass. (Shipped.)
- [x] Engine dispatch in `core/engine.py::run` — accept
      `ParsedDocument | ParsedProject`, route per-rule.
      (Shipped.)
- [ ] Migrate the abbreviations rule from `check` to
      `check_project` (the canonical cross-file rule).
      *Deferred*: JSS-ABBR-001 is a text-pattern rule with no
      cross-file scoping (no "definition on first use"
      semantics); a `check_project` body would be a trivial
      iterate-over-documents loop with no behavioural change.
      Will land alongside a real cross-file abbreviation
      sub-rule. Note added to
      `src/texlint/journals/jss/rules/abbreviations.py`.
- [x] `--no-resolve` CLI flag in `cli.py` — passes a
      `ParsedDocument` rather than auto-resolving.
      (Shipped as a reserved flag: it is wired through
      `cli_overrides` but has no observable effect today
      because the CLI does not currently auto-resolve. Lets
      users script against the flag ahead of the auto-resolve
      bridge.)
- [x] `JSS-PROJECT-001` (cycle) and `JSS-PROJECT-002`
      (missing reference) tool-side rules emitted by the
      resolver. (Shipped at
      `src/texlint/journals/jss/rules/project.py`.
      JSS-PROJECT-001 detects cycles by DFS over
      `ParsedProject.tree`; JSS-PROJECT-002 is a documented
      no-op stub until the resolver → ParsedProject bridge
      threads `missing` through. Not registered in the
      catalogue YAML — these are tool-side diagnostics.)

## Feature 014 — GitHub Action

- [ ] Action source repo — push the `action/` contents to a
      dedicated `kollerma/jss-style-checker-action` repository
      whose tags drive the marketplace listing. The release
      workflow at `.github/workflows/release-action.yml`
      handles the rolling-tag update once the dedicated repo
      exists.
- [x] Live smoke-test workflow at
      `.github/workflows/test-action.yml` — runs the action
      against `docs/jss-template/` and asserts SARIF presence +
      violation count. (Shipped: `uses: ./action`, runs on every
      PR + push to main, asserted by the YAML lint test.)
- [x] `--source-root` integration: forward the GitHub Actions
      checkout root to the spec-006 flag so SARIF URIs resolve
      to repo-relative paths in the Security tab. (Shipped: the
      composite action's lint step now passes
      `--source-root "$GITHUB_WORKSPACE"`; contract test at
      `tests/integration/test_action_manifest.py` guards the wiring.)

## Feature 015 — Conformance report

- [x] PDF rendering via WeasyPrint (gated behind
      `[project.optional-dependencies] pdf = ["weasyprint>=60"]`).
      (Shipped: `render_report(..., fmt="pdf")` returns PDF
      bytes; `report --format pdf --out FILE` writes the file;
      missing WeasyPrint raises `PdfNotAvailable` which the CLI
      converts into an install-hint.)
- [x] HTML rendering via the existing Jinja2 stack
      (`output/html_output.py` shares its template loader).
      (Shipped: `render_report(..., fmt="html")` renders the
      six-section template at
      `src/texlint/output/templates/conformance.html.j2`; covered
      by `tests/unit/test_report_html.py`.)
- [x] CLI subcommand `jss-lint report PATH [--format md]
      [--out FILE] [--title T] [--author A]` dispatches into
      `texlint.report.render_report`. (Shipped.)
- [x] Manuscript-metadata extraction from `\title{}` /
      `\author{}` / `\Plainauthor{}` macros at preamble parse
      time. (Shipped: `texlint.report.extract_metadata` walks the
      tex AST; the `report` subcommand uses extracted values when
      `--title` / `--author` are omitted; `\Plainauthor{}` wins
      over `\author{}` when both present.)

## Feature 016 — `jss-lint diff`

- [x] CLI subcommand `jss-lint diff OLD.json NEW.json
      [--ignore-line-drift]` dispatches into `texlint.diff.compare`.
      Schema mismatch on input exits 2; introduced > 0 exits 1.
      (Shipped.)
      (depends on Click sub-group migration).
- [x] Renderers: `--format terminal` (plain-text grouped
      sections), `--format markdown` (GitHub-flavoured
      CommonMark with H2 sub-sections), `--format json`
      (deterministic `{summary, fixed, introduced, unchanged}`
      shape via `sort_keys`). (Shipped.)
- [x] Schema validation of input JSON against the spec-001
      shape; mismatch exits 2. (Shipped: top-level keys +
      per-violation required keys via `texlint.diff.SchemaMismatch`
      + `validate_payload`.)
- [x] Populate `docs/jss-guide/rule-renames.json` with
      historical renames as they happen. (Shipped: a `_history`
      note explains why the map is empty — the two retired
      catalogue rules JSS-CITE-001 and JSS-ABBR-002 are
      RETIREMENTS, not renames, and belong in
      `retired_rule_ids`. Future spec PRs add real renames here.)

## Feature 017 — Recall evaluation

- [x] **Hand-annotate the first 10 JSS papers** under
      `eval/recall-corpus/<paper-id>/`. The annotation TOML
      schema is documented in
      `eval/recall-corpus/README.md`. This is the most
      labour-intensive deferred item — read each paper end-
      to-end, identify every JSS-guide violation, record
      `(rule_id, file, line)` per FR-002.
      (Completed 2026-06-11: the final two stubs, mdsOpt — 158
      entries — and spacetime — 111 entries — were annotated by
      an AI pass per the README protocol, with linter
      reconciliation per step 5. Both are marked pending human
      verification in their `[meta]` blocks. Source files were
      materialised from the `cran/<pkg>` GitHub mirror at the
      manifest-pinned versions because the sandbox network
      policy blocks CRAN; line counts match the scaffold-time
      records exactly.)
- [ ] **CODE-003 line anchoring is inconsistent**, surfaced by
      the mdsOpt/spacetime annotation reconciliation: for `.ltx`
      code envs the violation anchors at the `\begin{CodeInput}`
      line; for `.Rnw` chunks it lands on the chunk header line
      for some chunks and on the first body line for others
      (e.g., jss816.Rnw fires at 198 = header but 186 = header+1).
      Annotations currently encode the empirical anchor so TPs
      register; fix the rule to anchor at the offending code
      line, then re-anchor the corpus.
- [ ] **Linter scans content after `\end{document}`** — jss816.Rnw
      carries non-LaTeX notes after `\end{document}` and XREF-001
      fires on them (lines 1542/1546/1565). Rules should stop at
      `\end{document}`.
- [ ] **OPER-004 bare literal E / P in math mode**
      (`src/texlint/journals/jss/rules/operators.py`) — the rule
      catches `\mathbf{E}`, `\text{var}`, etc. but misses bare
      capital `E` / `P` used as expectation / probability
      operators (e.g., `E_{\bm{Z}}(\phi(...))` in rstpm2,
      `P(y = y_k)` in DBR — 8 corpus FNs). A naive regex
      (`(?<![\\A-Za-z])[EP](?:_\{[^{}]*\})?\s*\(`) over-fires on
      same-shaped function patterns like `P_{ij}(t)` (transition-
      matrix entries are not the canonical `\Prob{}` operator).
      Needs either author-context heuristics (preceding prose
      mentions "expectation" / "probability") or per-paper opt-in.
- [x] `eval-jss recall` CLI subcommand with `--gate` and
      `--validate` flags. (Shipped: also `--corpus`,
      `--format {terminal|json}`, `--history-db`, `--no-record`.
      Empty corpus exits 0 with a friendly note. Persists each
      run to the recall_history table.)
- [x] `recall_history` SQLite table schema in
      `eval/precision-history.db` per data-model §3. (Shipped:
      schema + `record_recall()` / `latest_recall_per_rule()`
      helpers in `eval/history.py`.)
- [x] Combined precision + recall report column in
      `eval/report.py`. (Shipped: `eval-jss report --with-recall`
      adds Recall + F1 columns plus an aggregate footer row.)
- [x] `eval/badge.py` — emits shields.io endpoint JSON for
      the precision and recall badges. (Shipped: also covers F1.
      Has a CLI: `python -m eval.badge {precision|recall|f1} V`.)
- [x] `.github/workflows/publish-badges.yml` — push
      regenerated badge JSON to the `gh-pages` branch on
      every push to main. (Shipped: workflow renders via
      `python -m eval.badge`; pushes to gh-pages with the default
      GITHUB_TOKEN. Goes live the first time it runs on main.)
- [x] Update README to display the three badges
      (precision / recall / F1). (Shipped: README header carries
      shields.io endpoint badges pointing at
      `kollerma.github.io/jss-style-checker/badges/*.json`. The
      JSONs are populated by the deferred gh-pages workflow.)

## Rule catalogue follow-ups surfaced by recall annotation

New rule proposals and existing-rule behaviour fixes discovered
while hand-annotating the v1 recall corpus (`eval/recall-corpus/`).
Each item has reviewer/style-guide provenance and a concrete
corpus carrier so the change can be test-driven from real text.

- [ ] **JSS-PRE-009 — preamble must not undefine or redefine
      jss.cls-provided code environments** (`Code`, `CodeInput`,
      `CodeOutput`, `Sinput`, `Soutput`). Detect via
      `\let\Code\@undefined` (or `\renewenvironment{Code}`,
      `\lstnewenvironment{Code}`, `\let\CodeInput=\@undefined`,
      etc.) on any of the JSS-provided code env names.
      **Why**: jss.cls supplies a fancyvrb-based Code/CodeInput/
      CodeOutput / Sinput / Soutput stack so all submissions
      render code uniformly. Replacing them with a custom
      listings-based stack bypasses the JSS house style and
      structurally hides the manuscript's code from CODE-001/002/
      003 and WIDTH-001 (which target the JSS env names). No
      published JSS paper does this — the only carriers in the
      precision corpus are four CRAN vignettes from a single
      author group (pmclust, pbdMPI, pbdSLAP, MixfMRI), none of
      which appear in `eval/jss-archive.json`.
      **Carriers**: `pmclust/pmclust-include/00-preamble.tex:18-26`
      is the canonical example (`\let\Code\@undefined` followed
      by `\lstnewenvironment{Code}{...}`).
      **Severity**: error (replaces the JSS code surface entirely).
      **Authority**: §4.2 Code style + jss.cls (the env names
      themselves).

- [ ] **Bib-side rules should skip uncited entries**
      (`src/texlint/journals/jss/rules/references.py`,
      `bibtex.py`). `JSS-REFS-002/003/004/005/006/007` and
      `JSS-BIBTEX-002/003/004` currently walk every entry returned
      by `_iter_entries()`, regardless of whether any
      `\cite{}` / `\citep{}` / `\citet{}` / `\citealt{}` /
      `\citealp{}` actually references the entry's key. Uncited
      entries don't appear in the printed bibliography (BibTeX/
      biblatex filters them out), so reviewers never see them and
      annotators correctly skip them — but the linter still fires,
      which inflates precision-side FP counts on the precision
      corpus and clutters the report.
      **Fix**: build the `\cite*{...}`-referenced key set per
      ParsedDocument once (helper in `_helpers.py`), then have
      each bib rule short-circuit when `entry.key not in
      cited_keys`. Keep `JSS-BIBTEX-001` (empty key) and the
      key-uniqueness check `JSS-BIBTEX-002` walking all entries —
      those are bib-hygiene rules independent of citation use.
      **Carrier**: pmclust's `pmclust-include/pmclust.bib`
      contains several entries (e.g. unreferenced book chapters)
      that fire `JSS-REFS-003` / `REFS-007` despite being absent
      from the printed bibliography.
      **Severity**: existing rule severity; behaviour fix only.

- [ ] **`JSS-CAP-002` should walk the optional `[short]` arg of
      `\section{...}` / `\subsection{...}` / `\subsubsection{...}`**
      (`src/texlint/journals/jss/rules/capitalization.py`). The rule
      currently only inspects the mandatory `{long}` arg, so titles
      written as `\subsection[Quick Start]{Quick Start}` go unflagged
      even when the long form is title-style instead of sentence-style.
      **Carriers**: pmclust `01-introduction.tex:38` (`System
      Requirement`), `:67` (`Quick Start`); robustlmm
      `simulationStudies.Rnw:290, 321, 379, 381, 449, 702, 704, 752,
      791` — 9 instances in a single paper. Both papers exhibit
      the same pattern.
      **Fix**: when the macro carries a `[<short>]` arg, lint *both*
      the short and long form (each is independently visible in the
      ToC vs body and either can violate sentence-style).
      **Severity**: existing CAP-002 severity (warning).

- [x] **`JSS-MARKUP-002` / `JSS-MARKUP-003` should also flag known
      package / function names wrapped in `\texttt{}`**
      (`src/texlint/journals/jss/rules/markup.py`).
      (Shipped in three steps:
      • commit `44e1c33` (2026-06-11): MARKUP-003 fires on every
        `\texttt{...}` outside bibliography / verbatim / JSS-markup
        wrappers, with a safe `\texttt` → `\code` fix. Recall
        0.064 → 0.915.
      • commit `1057110` (2026-06-12): the suggestion text and Fix
        replacement are content-aware — `\texttt{R}` → `\proglang{R}`,
        `\texttt{ggplot2}` → `\pkg{ggplot2}`, others →
        `\code{...}`. Rule_id stays MARKUP-003 so corpus tuples
        don't shift; only the proposed remediation changes.
      • Coverage of `\verb|...|` arguments deferred: pylatexenc
        parses verb spans as opaque LatexSpecialsNode runs, and a
        bare-name detection inside verb is materially different
        scope (and rare in the corpus). File as a separate item if
        a carrier surfaces.)

- [x] **`JSS-REFS-006` brace-defeats-`_starts_with_package_idiom`
      exemption** (`src/texlint/journals/jss/rules/references.py`).
      The exemption is meant to allow `vegan: Community Ecology
      Package` style titles where the lowercase word before `:` is
      the package name. When the package name is wrapped in `{}`
      to preserve case (`{robustlmm}: An ...`,
      `{robustvarComp}: Robust ...`), the exemption no longer
      matches and REFS-006 false-fires.
      (Shipped 2026-06-11 in commit `43c5c76`: the regex now reads
      `^\{*\s*\{?[a-z][a-zA-Z0-9.]*\}?\s*:` and matches
      brace-protected leading identifiers.)

- [x] **`JSS-CAP-001` should defer when the first word of the
      title is an unwrapped package name** (`src/texlint/journals/jss/rules/capitalization.py`).
      (Shipped in two commits:
      • commit `8d9744f` (2026-06-11): CAP-001's first-word check
        now defers when `_pkg_token(first) in doc_pkgs_lower`
        (i.e., the document `\pkg{}`-wraps the same name
        elsewhere). The principal-word check still runs so
        mid-title lowercase principals are still caught.
      • commit `8b4ff98` (2026-06-12): JSS-MARKUP-002 picks up the
        complementary half — bare package-name first word in
        `\title{...}` now fires MARKUP-002 with a `\pkg{pkgname}`
        suggestion. Carrier mdsOpt.ltx:27 now correctly surfaces
        under MARKUP-002 instead of (spuriously) under CAP-001.
        MARKUP-002 recall 0.333 → 0.667.)
      Mirror the `_starts_with_package_idiom` exemption that
      `JSS-REFS-006` already carries for bib titles. When the
      manuscript `\title{}` opens with a lowercase token that
      matches a known R package name, the title-case heuristic
      should NOT fire — the real defect is missing `\pkg{}`
      wrapping, which `JSS-MARKUP-002` handles. Letting both
      fire produces:

      - one CAP-001 hit that's editorially wrong (the title-case
        "violation" disappears once `\pkg{}` goes in)
      - and either no MARKUP-002 hit at all (because the linter's
        MARKUP-002 scope misses titles), or a duplicate annotation
        burden on the annotator.

      **Carrier**: mdsOpt `mdsOpt.ltx:27` —
      `\title{mdsOpt -- Searching for Optimal MDS Procedure
      \newline for Metric and Interval-Valued Data}` (the linter
      fires CAP-001; the real defect is missing `\pkg{mdsOpt}`).

      Same shape as the existing `JSS-REFS-006` exemption applied
      to bib titles where the package name leads (e.g.
      `{robustlmm}: An R Package for ...`) — the rule should
      reuse that helper.

      **Fix**: in `check_jss_cap_001`, before flagging an
      uncapitalised first word, check whether it matches a
      package-name entry in the `MARKUP-002` recognised-set. If
      so, defer (the defect belongs to MARKUP-002, not CAP-001).
      Pair with the existing MARKUP-002 scope follow-up so the
      defect is surfaced by the correct rule.

      **Severity**: existing rule severity (warning).

- [ ] **`JSS-CAP-003` is over-eager on technical identifiers in
      captions** (`src/texlint/journals/jss/rules/capitalization.py`).
      Captions of the form `Convergence simulation study, N/N case,
      bias, ...` get flagged because tokens like `N/N`, `RSEn`,
      `lme`, `t3/t3` look like non-sentence-case violations. These
      are technical identifiers / short variable / package names
      and shouldn't be lower-cased.
      **Carriers**: robustlmm `simulationStudies.Rnw:608`, `:654`
      (and likely many other technical-stats papers).
      **Fix**: extend the sentence-style check to skip tokens that
      already appear inside `\code{}` / `\pkg{}` / `\proglang{}` /
      `\texttt{}` macros within the same caption, AND tokens that
      contain mixed case + a digit (e.g. `t3`, `RSEn`) or a `/`
      separator (e.g. `N/N`).
      **Severity**: existing rule severity (warning).

- [ ] **`JSS-REFS-003` (DOI advisory) entry-type coverage is too
      narrow + DOI-in-wrong-field anti-pattern is missed**
      (`src/texlint/journals/jss/rules/references.py`).
      Two related gaps:

      *(a) Entry-type filter.* The rule currently fires on a small
      subset of entries — pmclust (6/15 fire; 9 missed), robustlmm
      (5/16 fire; 11 missed), CARBayesST (37/65 fire; 28 missed)
      all showed real DOI-missing entries that didn't trigger.
      Likely scoped to `@ARTICLE` with a `journal` field set,
      ignoring `@MISC`, `@Manual`, `@incollection`, `@book` etc.
      that legitimately have DOIs.
      **Carriers**: pmclust `pmclust.bib` (Chen2012pmclustpackage,
      Chen2012pbdMPIpackage, Schmidt2013pbdDEMOpackage, Rcore,
      Yu2010 etc.); robustlmm `simulationStudies.bib` (most
      package-archive @Manual / @MISC entries); CARBayesST
      `JSS2728.bib` (~28 entries spanning JSS articles, Wiley /
      Springer / Elsevier journal articles, Springer & Chapman
      books, R-package @Manuals).

      *(b) DOI in wrong field.* When a DOI exists but is recorded
      inside `pages = "..."` or `url = "..."` instead of a proper
      `doi = "..."` field, the rule misses it (it only looks at
      `doi=`). This is a real anti-pattern: `pages` ends up in
      the rendered bibliography in unexpected ways, and `url=`
      with a `dx.doi.org` link is non-canonical.
      **Carriers**: CARBayesST `JSS2728.bib` — `haining2010`
      (`pages = "123-131, DOI:10.1016/j.sste.2010.03.006"`),
      `lee2022` (`pages = "https://doi.org/10.1016/j.spasta.2021.100508"`),
      `leroux2000` (`url = "http://dx.doi.org/10.1007/978-1-4612-1284-3_4"`).

      **Fix**: drop the entry-type filter — *any* entry whose
      published form has a DOI on Crossref should be flagged when
      `doi` is missing. Additionally scan `pages` and `url` for
      embedded DOIs (regex `10\.\d+/\S+`); when found, fire a
      distinct sub-message ("DOI exists but is recorded in the
      wrong field; move to `doi=`") so the author knows the
      defect is field-placement, not absence.
      **Severity**: info (advisory) — unchanged.

- [x] **`JSS-REFS-004` (proglang / pkg / code markup in bib titles)
      scope is incomplete** (`src/texlint/journals/jss/rules/references.py`).
      (Shipped in two commits:
      • commit `dc5844f` (2026-06-11): pattern-based fallback for
        titles matching `^pkgname: description` covers most
        title-side FNs (pmclust, cascsim, MixSim, pbdMPI/SLAP/BASE,
        PROreg, SMACOF, smds, clusterSim, leaflet). Recall
        0.538 → 0.846.
      • commit `2abfd52` (2026-06-12): rule now also scans the
        `note=` field for bare language tokens. DBR.bib:316,
        deSolve/integration.bib:66, pmclust.bib:120 — all the
        carriers from the original follow-up. Recall 0.846 → 0.892.)
      The rule fires on a fraction of real cases: pmclust caught
      3 of 11 cases the annotator marked; robustlmm caught 5 of 14.
      Common miss pattern: `note = {R package version 0.1-5}` and
      similar where `R` should be `\proglang{R}` or the package
      name in `title=` should be `\pkg{name}`.
      **Carriers**: pmclust `pmclust.bib:1, 77, 104, 112, 127,
      134, 141, 177`; robustlmm `simulationStudies.bib:18, 29,
      66, 74, 85, 94, 113, 121, 129`.
      **Fix**: extend the rule to also inspect the `note=` field
      and to recognise the canonical R-package-name lookup that
      MARKUP-002 already maintains.
      **Severity**: existing rule severity (warning).

- [ ] **JSS-PRE-010 — Sweave/knitr preamble sets the JSS-standard
      ``options()`` in an early hidden chunk**. The JSS author
      template (`docs/jss-template/article.Rnw`) prescribes:

      ```r
      <<preliminaries, echo=FALSE, results=hide>>=
      options(prompt = "R> ", continue = "+  ",
              width = 70, useFancyQuotes = FALSE)
      @
      ```

      Each option has a concrete house-style consequence:
      `prompt`/`continue` produce the canonical "R>"/"+ " prompts
      in Sinput blocks; `width = 70` (or any value ≤77) keeps
      rendered Soutput inside the JSS text width — directly
      affecting JSS-WIDTH-001 recall on the rendered .tex (without
      it, R defaults to 80 and routinely overflows);
      `useFancyQuotes = FALSE` suppresses curly Unicode quotes in
      Soutput, which clash with the JSS monospace font and break
      copy-paste of code.

      **Carriers** (5 of 10 fully missing, 2 partial across the v1
      recall corpus): clifford `clifford.Rnw`, cusp `Cusp-JSS.Rnw`,
      mdsOpt `mdsOpt.ltx`, pmclust `pmclust-guide.Rnw`, rstpm2
      `multistate.Rnw` set neither; CARBayesST sets prompt but not
      width; robustlmm sets width but not prompt.

      **Detection**: scan `.Rnw`/`.Rmd` for an early chunk (before
      `\begin{document}` or within the first ~3 chunks of the
      manuscript body) that calls `options(...)` with all four
      keys above set to JSS values (`prompt="R> "`, `continue="+  "`,
      `width <= 77`, `useFancyQuotes = FALSE`). Fire one violation
      per missing key, or a single composite violation listing the
      keys that are absent.

      **Severity**: warning.
      **Surfaces**: `.Rnw`, `.Rmd` only — non-Sweave manuscripts
      can't run R `options()` and shouldn't be flagged.

- [x] **`JSS-XREF-004` only checks the "carry `\label{}`" half of its
      description, not the "referenced from the text" half**
      (`src/texlint/journals/jss/rules/crossrefs.py`).
      (Shipped 2026-06-11 in commit `2f1b4cf`: the rule now collects
      every referenced label across all tex_like files
      (`\ref`/`\eqref`/`\pageref`/`\nameref`/`\autoref`/`\Cref`/`\cref`,
      multi-key forms split) and flags numbered eq envs whose
      `\label{}` keys appear nowhere in the reference set. Recall
      jumped 0.596 → 0.638; remaining FNs are line-anchor mismatches
      tracked by the CODE-003 line-anchoring follow-up.)

- [ ] **JSS-MARKUP-005 — URLs in prose use `\url{}` or `\href{}{}`,
      not `\texttt{}` / `\verb` / bare prose**. The JSS author
      guide is clear that URLs go through `\url{}` (from the `url`
      package or `hyperref`) so they (a) render as clickable
      hyperlinks in the PDF, (b) handle line-breaking at sensible
      spots, and (c) avoid LaTeX-escape gymnastics for `_`, `~`,
      `#`, etc. Authors who reach for `\texttt{}` lose all three
      and have to manually escape special chars in the URL body;
      bare URLs in prose lose (a) and (b).

      Two sub-checks:

      *(a) URLs wrapped in `\texttt{}` / `\verb` / `\path`* —
      high-precision, simple detection.
      **Carrier**: deSolve `deSolve.Rnw:1282` —
      `\texttt{http://www.scholarpedia.org/article/Stiff\_systems}`
      (note the `\_` escape, required because `\texttt{}` treats
      `_` as subscript; `\url{}` wouldn't).

      *(b) Bare URLs in prose* — wider net, needs carve-outs.
      Skip inside:
      - `\url{...}`, `\href{...}{...}`, `\nolinkurl{...}` (already
        the right macro)
      - verbatim envs (`verbatim`, `Verbatim`, `lstlisting`)
      - Sweave/knitr code envs (`Sinput`, `Soutput`, `CodeInput`,
        `CodeOutput`, `Code`, `Schunk`)
      - `<<...>>= ... @` Rnw chunks
      - math mode (`$...$`, `\(...\)`, `\[...\]`, display-eq envs)
      - `%`-line comments
      - `.bib` files entirely (the bib has its own `url=` field
        which downstream styles handle their own way)

      URL pattern: `(?:https?|ftp|mailto)://\S+` plus a bare
      `www\.\S+` heuristic (lower confidence — many false `www.`
      mentions in prose).

      **Fix**: rewrite as `\url{<body-unescaped>}` (strip the
      `\_` / `\#` / `\%` / `\&` escapes the author inserted to
      keep `\texttt{}` happy). For URLs with display text, use
      `\href{<url>}{<text>}`.
      **Severity**: warning.
      **Authority**: §4.1 Markup + hyperref/url package conventions.

- [ ] **`JSS-MARKUP-001`'s recognised-language set is R-centric**
      (`src/texlint/journals/jss/rules/markup.py`). MARKUP-001
      currently recognises a narrow set of programming languages
      (`R`, `C`, `C++`, a handful of others) and only flags those
      when they appear unwrapped in prose. Other languages and
      mathematical-software systems that JSS authors mention
      frequently — `SageMath`, `Python`, `Mathematica`, `Maple`,
      `MATLAB`, `Julia`, `Stata`, `SPSS`, `SAS`, `Fortran`, `Lisp`,
      `Haskell` — slip through unflagged.
      **Carriers**: clifford `clifford.Rnw:315` (`SageMath`
      unwrapped), `:321` (`Python` unwrapped in the same line as
      `SymPy`; `SymPy` is the package counterpart and belongs to
      MARKUP-002's adjacent recognition set).
      **Fix**: extend the language-name set with the standard
      mathematical-software / programming-language list. Pair with
      MARKUP-002's package-name set growth where the boundary
      crosses (`SymPy` is a Python package — MARKUP-002, not
      MARKUP-001; `SageMath` is a full system — MARKUP-001).
      Full software systems (SageMath, Mathematica, Maple) take
      `\proglang{}`; packages hosted inside another language
      (`SymPy` inside Python) take `\pkg{}`.
      **Severity**: existing rule severity (warning).

- [ ] **Rule-precision improvements (`JSS-CITE-002` and
      `JSS-HOUSE-001` over-eager edge cases)**. Three FP shapes
      surfaced during DBR annotation; each has a high-precision
      carve-out the rule should learn.

      *(a) `JSS-CITE-002` fires on a package's own vignette.* When
      the manuscript IS the package's documentation (carrier:
      DBR `DBR.Rnw:122` — DBR.Rnw is itself the package vignette;
      DBR has no upstream CITATION on CRAN), `\pkg{DBR}` at first
      mention has no citation to make. Carve-out: scan the
      manuscript for a `\VignetteIndexEntry{...}` or
      `\VignetteDepends{...}` header — if present, exempt the
      package name(s) that match the enclosing R package's name
      from `JSS-CITE-002`. The R package name can be inferred from
      the file path (`examples/cran_<pkg>/<pkg>/vignettes/...`) or
      from the vignette directives.

      *(b) `JSS-CITE-002` fires on table cells where the citation
      lives in surrounding prose.* The rule's "first occurrence in
      the same paragraph" check doesn't recognise table cells as
      a different context — a `\pkg{X}` in a table cell with no
      `\cite*` in the same cell triggers even when the surrounding
      prose cites `X` properly. Carrier: DBR `DBR.Rnw:297` —
      `\pkg{coda}` in a table; cited later in prose. Carve-out:
      exempt first occurrences that appear inside `tabular` /
      `longtable` / `tabu` / `array` / `tabbing` envs from
      strict per-paragraph scoping; instead look for a citation
      anywhere in the surrounding `table` / `figure` env's
      `\caption{...}` *or* in the immediately surrounding prose.

      *(c) `JSS-HOUSE-001` fires on `i.e.` / `e.g.` followed by a
      colon.* The rule wants `i.e.,` and `e.g.,` to disambiguate
      the period from a sentence-end. When the next non-whitespace
      character is `:` (colon), the disambiguation is already in
      effect (the colon can't be a sentence end either, and the
      `i.e.:` / `e.g.:` shape grammatically introduces a list or
      explanation). Carrier: DBR `DBR.Rnw:176` — `i.e.:` introducing
      a bullet list. Carve-out: scan one character past the closing
      period of `i.e.` / `e.g.` (skipping whitespace); skip the
      violation when that character is `:` or `;`.

      **Severity**: each existing rule's severity, unchanged. All
      three are precision (not coverage) improvements.

- [ ] **JSS-BIBTEX-005 — bib entry type matches the kind of work it
      describes**. JSS-BIBTEX-003 already checks "are the *required
      fields* present for the declared type" but nothing checks
      "does the declared type match what this entry actually
      describes?". Authors frequently copy-paste CRAN's
      auto-generated citation block which uses `@article` for what
      is clearly an R-package archive entry:

      ```bibtex
      @article{goodrich2018rstanarm,
        title={rstanarm: Bayesian applied regression modeling via Stan},
        author={Goodrich, Ben and Gabry, Jonah and Ali, Imad and Brilleman, Sam},
        journal={R package version},
        volume={2},
        number={4},
        pages={1758},
        year={2018}
      }
      ```

      The `journal = {R package version}` is the smoking gun —
      "R package version" is not a journal name; the entry is
      really an `@Manual` with `note = {R package version
      2.4-1758}` (or similar). This pattern recurs across the
      ecosystem because CRAN emits it from `citation()` for any
      package without a custom `CITATION` file.

      **Detection** (high-precision):
      - `@article` / `@misc` whose `journal` or `howpublished`
        field contains "R package", "package version", or matches
        a CRAN URL pattern (`CRAN\.R-project\.org`).
      - `@article` whose `note` field contains "R package
        version".
      - `@article` whose title matches the pattern `<pkgname>:
        <description>` where `<pkgname>` matches an entry in
        MARKUP-002's package-name lookup AND there is no DOI
        field (real JSS articles always have a DOI).

      **Carriers**: DBR `DBR.bib` — `goodrich2018rstanarm`. Likely
      many more across the precision corpus; the heuristic is
      conservative enough to scan widely.

      **Suggested fix in author-facing message**: "Entry appears
      to describe an R package archive. Use `@Manual{key, title =
      ..., author = ..., year = ..., note = {R package version
      X.Y-Z}, url = {https://CRAN.R-project.org/package=...}}`
      instead of `@article`."

      **Severity**: warning.
      **Authority**: §5.1 Bibliography (entry-type semantics) +
      CRAN bib convention.

- [ ] **JSS-STRUCT-008 — appendix uses `\appendix` + plain
      `\section{}`, not `\section*{}` with hard-coded letters**.
      The JSS author template (`docs/jss-template/article.Rnw`)
      prescribes:

      ```latex
      \appendix

      \section{Background}     % renders as "A. Background"
      \section{Algorithm}      % renders as "B. Algorithm"
      \subsection{Notation}    % renders as "A.1. Notation"
      ```

      The `\appendix` macro switches subsequent `\section`
      numbering from arabic to letters automatically; unstarred
      `\section{}` then auto-generates the label, the ToC entry,
      the PDF bookmark, and a `\ref`-able anchor.

      What this rule flags is the manual workaround pattern:
      `\section*{A. Background}` / `\section*{Appendix A: ...}` /
      similar. Hard-coded letters in the title body bypass
      LaTeX's auto-numbering, lose the ToC entry, lose the PDF
      bookmark, lose `\ref` resolution, and need manual
      renumbering when sections are added or reordered.

      **Carrier**: rstpm2 `multistate.Rnw` — appendix sections
      use `\section*{}` with hard-coded "A.", "B.", etc. instead
      of `\appendix` + `\section{}`. Confirm carrier line numbers
      when annotation is added.

      **Detection**: after the bibliography (or after the first
      `\bibliography{}` macro), flag any `\section*{...}` whose
      title body matches one of:

      - `^[A-Z]\.\s` (e.g. "A. Background")
      - `^[A-Z]:\s` (e.g. "A: Background")
      - `^Appendix\s+[A-Z]?[\.:]?` (e.g. "Appendix A:", "Appendix")

      AND the document does not contain `\appendix` anywhere
      (the `\appendix`-then-`\section{}` form is the correct
      pattern). Severity rises if both signals are present
      (manual letter + no `\appendix`); fires at info on either
      signal alone.

      **Fix suggestion**: replace the starred + hard-coded form
      with `\appendix` (once, before the first appendix section)
      followed by plain `\section{<title without letter>}` for
      each appendix section.

      **Severity**: warning.
      **Authority**: §2.2 Structure + jss.cls / article.tex
      appendix convention.

- [ ] **JSS-STRUCT-007 — figure-producing content must be wrapped in
      a `figure` environment**. JSS expects every figure to live in
      `\begin{figure}...\end{figure}` with `\caption{}` and `\label{}`
      so it floats, captions properly, and can be cross-referenced
      from prose. Three concrete shapes to flag:

      *(a)* Bare `\includegraphics[...]{...}` not nested inside any
      `figure` / `subfigure` / `wrapfigure` / `sidewaysfigure` env.

      *(b)* Sweave chunks with `fig=TRUE` (or knitr `fig.cap` unset
      together with a plot-producing call) that are not inside a
      `\begin{figure}...\end{figure}` wrapper. knitr's clean
      alternative is `fig.cap='...'` in the chunk options — that
      auto-wraps in a figure env with caption — so the rule should
      tell the author about both fixes.

      *(c)* (lower priority) `\includegraphics` inside `\author{}`
      / `\title{}` / `\Address{}` — that's a "wrong macro context"
      defect class, not the figure-env one; could share the rule
      or land separately.

      **Carriers** (corpus-wide scan after filtering `%`-commented
      lines and Sweave chunks with `include=FALSE` which generate
      PDFs for later manual inclusion):

      - DBR `DBR.Rnw` — 8 bare `\includegraphics` at L388, L389,
        L390, L418, L419, L420, L473, L474; 3 `fig=TRUE` chunks at
        L320, L352, L480. Sole sustained carrier in the v1 corpus.
      - clifford `clifford.Rnw:69` — `\hfill\includegraphics{...}`
        package-logo decoration on the title page. Borderline; could
        be exempted by a "tiny inline image, no caption, no float"
        carve-out.
      - (spacetime `jss816.Rnw:42–43` has `\includegraphics{...}`
        inside `\author{}` — separate defect class (c), filed under
        the same rule for now.)

      **Known FP shapes to filter in detection** (learned from the
      sweep): `%`-commented `\includegraphics` lines; Sweave chunks
      with `include=FALSE` in their options (these generate output
      files but knitr does NOT auto-include them; the actual
      `\includegraphics` is elsewhere and may be properly wrapped).

      **Severity**: warning. The defect produces an un-floated,
      uncaptioned, unreferenced figure — visible to reviewers but
      not catastrophic at compile time.

- [ ] **JSS-PRE-012 — Plain* fields match the markup-stripped form
      of their non-Plain counterparts**. Three macro pairs that JSS
      requires to be content-equivalent (modulo LaTeX markup):

      - `\title{}` ↔ `\Plaintitle{}`
      - `\author{}` ↔ `\Plainauthor{}`
      - `\Keywords{}` ↔ `\Plainkeywords{}`

      Existing adjacent rules:
      - `JSS-PRE-003` / `-007` / `-008` ensure the Plain* macro
        is *present* when the non-Plain form contains markup.
      - `JSS-PRE-006` ensures the Plain* form contains no markup.

      What no rule checks: that the *content* matches. The PDF
      metadata fields (`/Title`, `/Author`, `/Keywords`) are built
      verbatim from the Plain* macros, so divergence means the
      metadata silently disagrees with what readers see on the
      page. Common shapes that slip through:

      - Plain* updated for an early draft and not refreshed when
        the visible title / authors / keywords changed.
      - Punctuation or spacing differences (commas, en-dashes).
      - Plain* missing one of the keywords from the visible list.

      **Detection**: for each macro pair `(M, Plain<M>)`, build the
      markup-stripped form of `M`:

      1. Replace `\proglang{X}` / `\pkg{X}` / `\code{X}` / `\fct{X}`
         / `\class{X}` etc. with their argument `X`.
      2. Strip any remaining `\<macro>` tokens with no arguments.
      3. Collapse whitespace, normalise dashes and non-breaking
         spaces.

      Compare to the equivalently-normalised `Plain<M>` value. For
      `\Keywords{}` ↔ `\Plainkeywords{}` the comparison is on the
      comma-separated *set* of keywords (order-insensitive); for
      `\title{}` and `\author{}` it's on the full normalised string.
      Fire one violation per disagreeing pair, on the line where
      `Plain<M>` is defined.

      **Carriers**: not yet observed (no carrier confirmed in the
      v1 corpus during annotation review — would need a sweep
      across all 10 papers). Still worth implementing
      preventatively: the failure mode is silent and only visible
      when a reader inspects PDF metadata.

      **Severity**: warning.
      **Authority**: jss.cls Plain* semantics (see PRE-003/007/008
      authority references).

- [ ] **JSS-PRE-011 — `\Plainauthor{}` (and `\Plainkeywords{}`) use
      comma as separator, not `and` / `\And`**. The JSS template
      explicitly notes "comma-separated" alongside `\Plainauthor{}`
      (`docs/jss-template/article.Rnw:31`). `\Plainauthor` is
      consumed verbatim by hyperref for the PDF `/Author` metadata
      field, which expects a clean comma-delimited list — `Sharabiani
      and Mahani` reads as a single author in the metadata.

      Adjacent rule pair:
      - `JSS-PRE-006` already covers *markup* in `\Plainauthor` (no
        `\textbf`, etc.).
      - `JSS-STRUCT-005` covers `\author{}`'s separator (`\And`/`\AND`
        over lowercase `\and`).
      Neither covers `\Plainauthor`'s separator. Same gap for
      `\Plainkeywords{}` (also comma-separated per template).

      **Carrier**: DBR `DBR.Rnw:68` —
      `\Plainauthor{Sharabiani, Mahani, Price and Bottle}` (the
      Oxford-comma-omitted "Price and Bottle" should be a comma).
      Sole carrier in the v1 corpus; the other 7 `\Plainauthor`
      entries use the canonical comma form (or are single-author).

      **Detection**: parse `\Plainauthor{<body>}` and
      `\Plainkeywords{<body>}`; flag bodies that contain
      `\b(?:and|\\And|\\AND|\\and)\b` between author tokens. Skip
      bodies with zero or one comma (single-author / two-author
      `"A and B"` edge cases get a softer warning since the
      defect is less visible there).
      **Severity**: warning.

- [ ] **`JSS-MARKUP-004` should exempt starred section forms**
      (`src/texlint/journals/jss/rules/markup.py`). The rule fires
      on any `\section{...}` / `\subsection{...}` / etc. whose
      argument contains markup, suggesting an `\section[plain]{markup}`
      shim. Two problems on starred forms (`\section*`, `\subsection*`,
      `\subsubsection*`, ...):

      *(a) The fix doesn't apply.* `\section*` and friends do not
      take an optional `[short]` argument in standard LaTeX. The
      author can't follow the rule's suggestion as-is — the correct
      fix for starred forms is `\texorpdfstring{markup}{plain}`
      inside the braces, an entirely different mechanism.

      *(b) The defect surface is mostly absent.* Starred forms get
      no number, no ToC entry, and (under JSS class's default
      hyperref config) typically no PDF bookmark either. The
      markup-doesn't-render-in-ToC concern that motivates the rule
      simply isn't present.

      **Carrier**: cusp `Cusp-JSS.Rnw:325` —
      `\subsubsection*{Maxwell vs delay convention and $R^{2}$}`.
      Math markup in a starred subsubsection title, never reaches
      a ToC or bookmark, so the rule firing is a clean FP.

      **Fix**: skip envs whose macro name ends in `*` (regex
      `\\(section|subsection|subsubsection|paragraph|subparagraph)\*\b`).
      Optionally, when fixing this, also emit a different
      suggestion for the unstarred case when the markup is *only*
      math mode (math typesets in the ToC, so the practical
      impact is lower than for `\proglang`/`\pkg`/`\code` — but
      the PDF-bookmark hyperref-warning concern stands).
      **Severity**: existing rule severity (warning).

- [x] **`JSS-CITE-003` scope is narrower than its description**
      (`src/texlint/journals/jss/rules/citations.py:393`).
      (Shipped 2026-06-11 in commit `695829a`: the rule now matches
      every cite-family macro (`\cite`, `\citep`, `\citet`,
      `\citeauthor`, `\citeyear`; `\citealp` / `\citealt` are the
      JSS-recommended replacements and stay excluded) and uses a
      paragraph-bounded source-text paren-balance scan to detect
      any enclosing `(...)`. Auto-fix to `\citep{...}` is emitted
      only for the immediate `(\cite{...})` shape; broader shapes
      carry a suggestion only. Recall jumped 0.367 → 1.000.)

      Original description (kept for reference):
      The catalogue description reads "Avoid bracket-in-bracket
      citation forms like `(\cite{...})`", but the implementation
      only matched the exact `(\cite{X})` shape (single `\cite`
      macro, optional whitespace, nothing else between the parens).
      The JSS style guide's actual scope is broader — any
      author-year-rendering citation inside parens produces
      bracket-in-bracket. Real-world shapes the rule misses:

      | shape | renders as |
      |---|---|
      | `(\citep{X})` | `((X year))` — different macro, same defect |
      | `(see \cite{X})` | `(see (X year))` |
      | `(e.g., \cite{X})` | `(e.g., (X year))` |
      | `(\cite{X}, p. 5)` | `((X year), p. 5)` |
      | `(\cite{X}; \cite{Y})` | `((X year); (Y year))` |
      | `(\citet{X})` | `(X (year))` (still a paren-inside-paren) |

      **Carriers** (broader scan; comma-separated):
      - mdsOpt `mdsOpt.ltx` — 15 instances beyond the 11 the linter
        catches (L72, 74, 121, 175, 179, 205, 212, 214, 236, 324,
        328, 432, 607, 615, 634): all `(\cite{X}, ...)` / `(see
        e.g. \cite{X})` / `\cite{X}; \cite{Y})` shapes.
      - CARBayesST `CARBayesST.Rnw:498` — `(see \cite{celeux2006})`.
      - spacetime `jss816.Rnw:848` — `(e.g., \cite{allen})`; `:1475`
        — `(further examples are found in \cite{galton})`.
      - rstpm2 `multistate.Rnw:88` — `(see Theorem 3.4.6 in
        \cite{Sen_Singer_1993})`.

      **Fix**: instead of requiring the cite macro to be the *only*
      content between the parens, walk outward from each
      author-year-rendering cite macro (`\cite`, `\citep`, and
      `\citet`) and check whether the surrounding text is inside a
      paren pair on the same paragraph. The auto-fix becomes
      context-dependent (which macro is appropriate depends on the
      surrounding text), so demote to a warning without auto-fix
      for the broader shapes.
      **Severity**: warning (existing).

- [ ] **JSS-CITE-006 — `\citep{}` / `\cite{}` where `\citet{}` is
      grammatically required**. When the citation is the
      grammatical agent of a verb ("proposed by X", "introduced by
      X", "the method of X"), JSS wants `\citet{}` rendering as
      `X (year)`. Using `\citep{}` (parenthetical) instead
      produces `proposed by (X year)` — grammatically broken
      English. Common JSS-reviewer flag (e.g. jss5342 R4-r3
      mentioned this pattern in passing).
      **Carriers**: cusp `Cusp-JSS.Rnw:86`
      (`method of \cite{Cobb:1983p4510}` → "method of (Cobb
      1983)"), `:174` (`proposed by \cite{Oliva:1987p4496}` →
      "proposed by (Oliva et al. 1987)"). Likely more across the
      corpus; the heuristic below should surface them.
      **Detection (high-precision heuristic)**: flag `\citep{}` /
      `\cite{}` when the immediately-preceding text (within
      ~30 chars, skipping whitespace and inline macros) ends in
      one of an agent-marking trigger set: `by`, `from`, `of`,
      `according to`, `following`, `cf.`, `see also`, `as in`,
      `in`, `~`, plus the verbs `proposed`, `introduced`,
      `studied`, `extended`, `presented`, `developed`. Skip cases
      where the citation is at sentence start or follows a period.
      **Complication — preamble cite redefinitions**: papers
      sometimes redefine `\cite` to a different default
      (e.g. cusp's preamble has `\renewcommand{\cite}[1]{\citep{#1}}`
      at L21, making bare `\cite{}` render parenthetically too).
      A simple way: treat `\cite{}` and `\citep{}` *identically*
      for this rule, since under stock JSS-class+natbib both
      render parenthetically anyway; the rule's logic is purely
      about the agent-marking context, not which exact macro is
      used.
      **Severity**: warning.
      **Authority**: §3.2 Citations + JSS reviewer practice.

- [ ] **JSS-CITE-005 — every `\cite*{key}` resolves to a `@type{key,...}`
      in the document's `\bibliography{}`-referenced files**. LaTeX
      itself reports an "undefined citation" warning at typeset
      time and renders the unresolved citation as `?`, but the
      defect frequently slips through author proofreading (rendered
      `?` is easy to miss in a busy paragraph) and lands in submitted
      manuscripts.
      **Carrier**: clifford `clifford.Rnw:406` —
      `\cite{chisholm2012}`; the bib has `chisolm2012` (missing
      second 'h'). One typo, but a clear shape: cite key not in
      the union of bib-entry keys collected from every `.bib` in
      the same `ParsedDocument`.
      **Detection**: build the bib-key set per `ParsedDocument`
      (same helper as the "skip uncited entries" follow-up needs);
      walk every `\cite` / `\citet` / `\citep` / `\citealt` /
      `\citealp` / `\citeauthor` / `\citeyear` / `\nocite` /
      `\shortcites` argument; split on commas; for each key not
      in the set, fire one violation at the cite-macro line.
      **Severity**: error — the rendered manuscript visibly breaks.
      **Authority**: §3.2 Citations + general LaTeX hygiene.

- [ ] **JSS-XREF-005 — every `\ref{X}` / `\eqref{X}` / `\pageref{X}`
      resolves to a `\label{X}` somewhere in the document**. Same
      class of defect as JSS-CITE-005 but on the cross-reference
      side: LaTeX renders an unresolved reference as `??`, which
      is also easy to miss. JSS-XREF-001 / JSS-XREF-004 currently
      only check that figures / tables / equations carry labels
      (label *presence*); they don't check the inverse direction
      (reference *resolution*).
      **Carrier**: not yet observed in the v1 recall corpus, but
      the check is symmetric with JSS-CITE-005 and the same
      ParsedDocument scan trivially produces it.
      **Detection**: collect the union of `\label{X}` arguments
      across all `tex_files`; walk every `\ref`/`\eqref`/`\pageref`/
      `\autoref`/`\Cref`/`\cref` argument; flag any key not in
      the label set.
      **Severity**: error.
      **Authority**: §4.5 Cross-references + general LaTeX hygiene.

## Tracking

This file is hand-edited. When a follow-up lands, check its
box and link to the PR. When new follow-ups surface during
implementation, add them under the relevant feature.
