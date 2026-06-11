# Architecture review — rule implementation simplicity & reliability

**Date**: 2026-06-10
**Scope**: how rules are implemented (`src/texlint/journals/jss/rules/`,
`core/`, `api.py`), with the goal of maximising usefulness to authors
and reviewers while minimising false-positive noise.
**Evidence base**: source reading, the iter-78 precision log
(`eval/improvement-log.md`), and live repro runs against fixtures.

---

## Verdict

The core architecture is sound: a journal-agnostic engine, frozen
dataclasses, entry-point plugins, deterministic output, parse errors as
violations, and — rarest of all — a 238-paper empirical precision
harness with per-rule TP/FP history. Those should not change.

The weakness is concentrated in one place: **the only tool the project
has for fighting false positives is adding more heuristics inside the
rule body.** Six weeks of the precision loop drove 53/54 rules past the
90 % gate, but the mechanism was accretion — exemption lists, follower
dictionaries, regex carve-outs — and the log itself concludes the
remaining FP budget is "out of reach of further mechanical iteration."
The architecture needs FP-handling mechanisms *outside* the rule body:
per-finding confidence, inline suppression, severity-aware exit codes,
and document-derived (rather than globally curated) vocabularies. Plus
two outright bugs found during this review (F1, F2).

---

## F1 — BUG: verbatim-environment lists have drifted; markup rules fire inside `lstlisting`

Two independent lists define "this content is code, not prose":

- `core/parser.py` `_VERBATIM_ENVS_RE` — `Sinput Soutput Scode Code
  CodeInput CodeOutput CodeChunk alltt tabbing verbatim* lstlisting`
- `rules/_helpers.py` `_VERBATIM_ENVS` — `verbatim Verbatim Code
  CodeInput CodeOutput Sinput Soutput Scode Schunk CodeChunk`

`lstlisting`, `alltt`, `tabbing`, `verbatim*` are neutralised by the
parser but **not** recognised by `_is_inside_verbatim`, so prose rules
scan their bodies. Reproduced:

```tex
\begin{lstlisting}
library(zoo)
result <- Python.call("foo")
x = data.frame()
\end{lstlisting}
```

yields JSS-MARKUP-002 ("wrap 'zoo' in \pkg{}"), JSS-MARKUP-001
("wrap 'Python'"), JSS-MARKUP-003 ("wrap 'data.frame()'"), all inside
a code listing — and MARKUP-001/002/003 carry `confidence="safe"`
fixes, so `--fix` would rewrite the listing's code. Conversely,
`Schunk` and `Verbatim` are known to the rules but not neutralised by
the parser, so TeX-special characters inside them can still abort the
strict parse.

The precision loop never caught this because CRAN Sweave vignettes use
`Sinput`, not `lstlisting` — a reminder that corpus distribution ≠
submission distribution.

**Fix**: one shared constant (e.g. `texlint.core.verbatim.VERBATIM_ENVS`)
consumed by both the parser's neutraliser and `_is_inside_verbatim`,
with a unit test asserting the parser regex is generated from it.

## F2 — BUG: eval-corpus directory layout baked into production rule logic

`rules/capitalization.py:336`:

```python
_OWN_PACKAGE_PATH_RE = re.compile(r"/cran_([^/]+)/(?:[^/]+/)?vignettes/")
```

CAP-001's "first title word may be the paper's own package name"
exemption keys off the *eval corpus's* directory convention
(`examples/cran_<name>/<name>/vignettes/`). A real author running
`jss-lint paper.tex` in their own directory never matches, so every
real submission titled `\title{flexsurv: A Platform for ...}` — the
standard JSS title idiom — gets flagged. Measured corpus precision
(100 %) does not transfer to the field.

**Fix**: derive the own-package name from document signals instead of
the path — the most frequent `\pkg{}` argument, the token before `:`
in `\Plaintitle`, or an explicit `package = "..."` key in
`.jss-lint.toml`. Path heuristics belong in the eval harness, never in
rule logic.

## F3 — No per-line suppression: one FP forces an all-or-nothing choice

The only suppression surfaces are whole-rule: `--ignore-rules`,
`ignore_rules` in `.jss-lint.toml`, and `init`'s precision-DB
auto-suppression. An author with one false MARKUP-001 hit in a 30-page
paper must either tolerate the noise on every run or disable the rule
project-wide (losing its ~1000 corpus-confirmed true positives).

**Fix**: a magic comment, e.g. `% jss-lint: ignore JSS-MARKUP-001`
(same line or line above; bare `ignore` for all rules). pylatexenc
preserves `LatexCommentNode`s, so this is implementable as a single
post-filter in the engine — no rule changes. Map suppressed findings
to SARIF `suppressions` so the GitHub Action stays faithful. This is
the cheapest FP-noise reduction available, and suppression comments
in the wild become free FP telemetry for the eval loop.

## F4 — Findings are binary; precision tiers exist in the data but not in the output

Iter-78 data splits the catalogue cleanly into two regimes:

- **mechanical** rules (PRE-*, STRUCT-*, XREF-*, BIBTEX-*, TYPO-*,
  WIDTH, CODE-001/002): ~100 % precision;
- **linguistic-heuristic** rules (CAP-002 87 %, CAP-003 57 %,
  MARKUP-001 88 %, CITE-002 83 % on pinned corpus).

Yet a `Violation` carries no confidence; both regimes render
identically and weigh identically in the exit code. `Fix` has a
`confidence` field — `Violation` does not. Meanwhile
`_determine_exit_code` returns 1 for *any* violation, so info-severity
advisories (REFS-003 "add a DOI", the single highest-volume rule:
1758 findings) flip CI red on an otherwise-clean paper.

**Fix**:

1. Add `confidence: Literal["high","medium","low"]` to `Violation`,
   defaulted per rule from the measured precision history (the data
   already exists in `eval/precision-history.db`; bake the tier into
   `_catalogue_data.py` at generation time).
2. Author mode shows high+medium by default, `--all` shows everything;
   reviewer mode shows everything grouped by confidence.
3. Exit-code policy by severity/confidence: errors → 1; warnings/info →
   0 by default, configurable via `--fail-on {error,warning,info}`.

This converts the precision/recall trade-off from a code-time
whack-a-mole decision (silence the FP cluster, lose the TPs) into a
presentation-time decision per audience — which is exactly the
author-vs-reviewer split the tool serves. It also resolves the CAP-003
deadlock the improvement log left open: demote it to `low` confidence
instead of either shipping 57 %-precision noise or deleting 20 TPs.

## F5 — Heuristic accretion has hit its ceiling; replace ontology lists with self-document signals

`capitalization.py` is 797 lines, the majority being exemption
machinery: an 80-entry proper-noun list, a 40-entry caption-only
list, textual-citation strippers, label-prefix strippers,
run-collapsing with hyphen-piece inheritance. `markup.py` carries a
20-word follower dictionary just to disambiguate the package
"sandwich" from the estimator. Each entry was added to silence a
specific corpus paper (the comments name them: cran_np, robustlmm,
multcomp, ReacTran...). The improvement log's own conclusion: the
remaining FPs are "domain-ontology gaps... whack-a-mole patching would
only silence at the cost of recall."

The structural problem: these rules try to answer "is this word a
proper noun / package name?" from a *global* ontology, which is
unbounded. The *document itself* answers most of these questions:

- A capitalised mid-sentence word that the same document also uses
  lowercase in prose is title-casing; one it always capitalises is a
  proper noun (names, methods, datasets). This single signal subsumes
  most of `_EXTRA_PROPER_NOUNS` and handles *Huber's Proposal 2* /
  *DSClassify* — the exact CAP-003 residue.
- A bare token that the author elsewhere wraps in `\pkg{}` /
  `\proglang{}` / `\code{}` is near-certainly a missed wrap; that
  corroboration signal is high-precision **and** lifts MARKUP-002's
  recall ceiling (see F6) at the same time.

**Fix**: add two small document-index helpers (lowercase-usage index,
wrapped-token index) in `_helpers`, gate the linguistic rules on them,
and then *delete* the bulk of the per-paper exemption lists. What
remains of the curated ontology should be data files (TOML shipped as
package data), extensible per-project via config
(`extra_proper_nouns = [...]`) so an author can fix their own FP
without a tool release.

## F6 — Curated global term lists are simultaneously a recall ceiling and an FP source

`terms.py` knows 9 R packages and 14 language spellings. MARKUP-002
can only ever flag those 9 packages out of ~20 000 on CRAN — yet the
ones it knows (`zoo`, `MASS`, `sandwich`, `xts`) are exactly the
common-English-word names that need follower dictionaries to
disambiguate. The list is the worst of both directions.

**Fix**: invert the source of truth. Vocabulary comes (in priority
order) from: tokens the document already wraps at least once
(corroboration, F5); the paper's own package (F2's document-derived
name); optionally a CRAN/PyPI name list shipped as a data file, used
only with the corroboration gate for common-word names. `terms.py`
keeps only canonical-spelling mappings (Fortran/MATLAB/S-Plus), which
is what it is genuinely authoritative about.

## F7 — Per-module boilerplate: 14 copies of `_violation`, 15 of `_rule`, hand-rolled walks everywhere

Every rule module re-declares the same `_violation()` and `_rule()`
factories and re-implements the
`for tex in doc.all_tex_like(): for node, ancestors in _walk...`
loop with its own choice of context guards. That last part is the
FP-relevant defect: each rule independently decides which contexts to
skip, and they disagree — markup rules use `_is_in_prose_context`,
capitalization re-implements markup-skipping privately in
`_group_plain_text`, bibliography scoping exists in three variants.
F1 is the proof that divergent context guards produce field FPs.

**Fix**: a small rule kit inside the journal package (no public-API
change):

- `make_rule("JSS-XXX-NNN")(check_fn)` — one factory reading
  `_catalogue_data` (kills both copied helpers everywhere);
- `emit(tex, pos, rule_id, suggestion, fix=None)` — one violation
  constructor;
- declarative iterators that encode the context policy once:
  `prose_chars(doc)`, `section_titles(doc)`, `captions(doc)`,
  `cited_bib_entries(doc)`, `rendered_text(group)` (a single tested
  "what does the reader see" projection replacing
  `_group_plain_text` / `_collect_plain_text` / `_macro_args_text`).

Most checks reduce to their actual decision logic; the iterators
become the single place to plug in inline suppression (F3) and any
future context fix — fixed once, fixed for all 58 rules.

## F8 — One crashing rule kills the entire run

`engine.run` does not guard `rule.check(...)`; the CLI's defensive
catch-all turns any rule exception into exit 2 with **no report**. For
a heuristic linter, one edge-case crash in one rule destroying the
other 57 rules' output is the wrong failure mode (and indistinguishable
from a parse failure to the GitHub Action).

**Fix**: wrap per-rule execution; convert a crash into a
`SkippedRule(reason="internal error: ...")` plus (in verbose mode) a
synthetic info finding, and continue. Determinism is preserved.
While in the engine: replace the
`__import__("texlint.api", ...)` stunt at `engine.py:241` with a
normal import, and either pass `matched_files` to `check` or drop the
pre-scan — today the engine computes per-doc matched files only to
decide "applied" status while every check re-iterates the document
itself.

---

## Suggested sequence

| step | item | type | effort | payoff |
|---|---|---|---|---|
| 1 | F1 shared verbatim-env constant | bug fix | small | kills a live FP class + unsafe auto-fix |
| 2 | F2 document-derived own-package name | bug fix | small | unbreaks CAP-001 on real submissions |
| 3 | F8 per-rule crash isolation | reliability | small | no more all-or-nothing runs |
| 4 | F3 inline `% jss-lint: ignore` | feature | small-medium | biggest single noise-reduction lever |
| 5 | F4 confidence tiers + `--fail-on` | feature | medium | author/reviewer split; resolves CAP-003 deadlock |
| 6 | F7 rule kit + rendered-text projection | refactor | medium | shrinks rules to decision logic; one context policy |
| 7 | F5/F6 self-document signals, data-driven vocab | redesign | medium-large | replaces ontology whack-a-mole; lifts recall ceiling |

Steps 1–4 are independent and individually shippable. Step 7 should
land after the spec-017 recall corpus is annotated, so the
recall-plants suite can prove the deleted exemption lists aren't
silently re-trading recall for precision.
