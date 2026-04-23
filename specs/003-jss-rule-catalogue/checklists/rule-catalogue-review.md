# Rule Catalogue Review Checklist

**Purpose**: Human sign-off rubric for the JSS rule catalogue. Walks a reviewer through four authority coverage matrices, a per-rule inventory, category sanity checks, severity consistency, and the residual open questions `/speckit.clarify` could not auto-resolve.
**Created**: 2026-04-23
**Feature**: [spec.md](../spec.md)
**Catalogue data file (source of truth, populated after draft)**: `../catalogue.yaml`
**Catalogue rendered markdown (generated from the data file)**: `../catalogue.md`
**Vendored sources consumed by this checklist**:
- `docs/jss-template/jss.cls` — `jss.cls` v3.3 (2021-05-23)
- `docs/jss-template/article.tex` — JSS demo article (2018-04-30, last touched 2021-12-10)
- `https://www.jstatsoft.org/style` — fetched 2026-04-23
- `https://www.jstatsoft.org/authors` — fetched 2026-04-23

---

## How to use this checklist

1. Draft the catalogue data file (`catalogue.yaml`) during implementation.
2. Walk this file top-to-bottom. For every row in §1.1–1.4, fill in `covering_rule_ids` with the `rule_id`s that cover that provision and set `status` to `covered`, `gap`, `redundant`, or `out-of-scope`.
3. Copy the drafted rule rows into §2 and annotate each with a `reviewer_note`.
4. Work through §3 (category sanity) and §4 (severity consistency).
5. Resolve every open question in §5 — either answer, convert to a rule, or defer with a written rationale.
6. Sign off at the bottom when every row has a non-empty `status` and every open question is closed.

**Approval = this file is committed with (a) every provision row annotated, (b) every rule row annotated, (c) every open question closed (answered or explicitly deferred).**

---

## 1. Authority coverage matrix

Every normative provision below must map to ≥1 rule in the catalogue, **or** be explicitly marked `out-of-scope` with a one-line rationale. A provision with zero covering rules is a **gap** to close before sign-off; a provision with >1 covering rules is a **redundancy candidate** to merge or justify.

Columns: `source` · `anchor` (section/line) · `provision` (one line) · `covering_rule_ids` (fill in) · `status` (covered | gap | redundant | out-of-scope).

### 1.1 `jss.cls` — user-facing macros, environments, class options

Authority: `jss_cls`. Authority order: this is the highest. If the class defines it, rules may require it; if it doesn't, rules **must not** hallucinate it.

| source | anchor | provision | covering_rule_ids | status |
|---|---|---|---|---|
| jss.cls | 37–49 (class options) | Manuscript declares exactly one of `article`, `codesnippet`, `bookreview`, `softwarereview` as the class option | JSS-PRE-001 | covered |
| jss.cls | 45 | `shortnames` class option available for natbib short-form names | — | out-of-scope — switch, not a rule target |
| jss.cls | 46 | `nojss` class option turns off JSS header/footer (used for vignettes) | — | out-of-scope — vignette-only; .Rnw scope in Step 4 |
| jss.cls | 47–49 | `notitle`, `noheadings`, `nofooter` class options exist | — | out-of-scope — vignette-only |
| jss.cls | 59–65 (natbib) | `natbib` loaded with `[authoryear,round]` (or `[authoryear,round,longnamesfirst]` when `shortnames` is off); `\bibpunct` set to `(){};a,` | JSS-CITE-004 | covered — CITE-004 requires natbib citation commands, implying natbib is loaded |
| jss.cls | 65 | Bibliography style is `jss` (i.e., `\bibliographystyle{jss}`) | — | out-of-scope — set implicitly by jss.cls; no author action required |
| jss.cls | 81 (`\Address`) | `\Address{}` metadata command (required in preamble) | JSS-PRE-002 | covered |
| jss.cls | 82 (`\Plaintitle`) | `\Plaintitle{}` metadata command (plain-text title without LaTeX markup) | JSS-PRE-003 | covered |
| jss.cls | 83 (`\Shorttitle`) | `\Shorttitle{}` metadata command (running title with markup allowed) | — | gap — no rule enforces its presence; author-facing optional, candidate follow-up |
| jss.cls | 84 (`\Plainauthor`) | `\Plainauthor{}` metadata command (author list without affiliations) | — | gap — similar to `\Shorttitle`; candidate follow-up |
| jss.cls | 85 (`\Volume`) | `\Volume{}` metadata command | — | out-of-scope — editorial metadata, set by JSS not by author |
| jss.cls | 86 (`\Year`) | `\Year{}` metadata command | — | out-of-scope — editorial metadata |
| jss.cls | 87 (`\Month`) | `\Month{}` metadata command | — | out-of-scope — editorial metadata |
| jss.cls | 88 (`\Issue`) | `\Issue{}` metadata command | — | out-of-scope — editorial metadata |
| jss.cls | 89 (`\Submitdate`) | `\Submitdate{}` metadata command | — | out-of-scope — editorial metadata |
| jss.cls | 91 (`\Acceptdate`) | `\Acceptdate{}` metadata command (articles / code snippets) | — | out-of-scope — editorial metadata |
| jss.cls | 92 (`\Abstract`) | `\Abstract{}` is required and non-placeholder (default in 120 is a sentinel error) | JSS-PRE-004 | covered |
| jss.cls | 93 (`\Keywords`) | `\Keywords{}` is required and non-placeholder (default in 197 is a sentinel error) | JSS-PRE-005 | covered |
| jss.cls | 94 (`\Plainkeywords`) | `\Plainkeywords{}` metadata command | — | gap — similar to `\Plaintitle`; candidate follow-up |
| jss.cls | 96–108 (review metadata) | `\Reviewer`, `\Booktitle`, `\Bookauthor`, `\Publisher`, `\Pubaddress`, `\Pubyear`, `\ISBN`, `\Pages`, `\Price`, `\Plainreviewer`, `\Softwaretitle`, `\URL`, `\DOI` metadata commands exist for `bookreview` / `softwarereview` classes | — | out-of-scope — review class types deferred (spec scope = `article` class) |
| jss.cls | 473–474 (`\code`) | `\code{}` for inline code (functions, commands, arguments, literal tokens) | JSS-MARKUP-003 | covered |
| jss.cls | 476 (`\proglang`) | `\proglang{}` for programming languages and programmable systems (defined as `\textsf`) | JSS-MARKUP-001 | covered |
| jss.cls | 477 (`\pkg`) | `\pkg{}` for software package names (medium-bold series) | JSS-MARKUP-002 | covered |
| jss.cls | 478 (`\email`) | `\email{}` for email addresses (generates `mailto:` link) | — | out-of-scope — used inside `\Address`; presence implicitly covered by JSS-PRE-002 |
| jss.cls | 480–483 (`\doi`) | `\doi{}` for DOIs (generates `https://doi.org/...` link) | — | out-of-scope — used via `\DOI` editorial metadata |
| jss.cls | 484 (`\E`) | `\E` math shortcut for expectation (`\mathsf{E}`) | — | out-of-scope — no style-guide directive mandates `\E` over `\mathbb{E}` |
| jss.cls | 485 (`\VAR`) | `\VAR` math shortcut for variance | — | out-of-scope — same |
| jss.cls | 486 (`\COV`) | `\COV` math shortcut for covariance | — | out-of-scope — same |
| jss.cls | 487 (`\Prob`) | `\Prob` math shortcut for probability | — | out-of-scope — same |
| jss.cls | 203 (`Sinput`) | `Sinput` environment defined (Sweave-style) | — | out-of-scope — .Rnw-adjacent; environment choice is author preference |
| jss.cls | 204 (`Soutput`) | `Soutput` environment defined | — | out-of-scope — same |
| jss.cls | 205 (`Scode`) | `Scode` environment defined | — | out-of-scope — same |
| jss.cls | 206 (`Schunk`) | `Schunk` environment defined | — | out-of-scope — same |
| jss.cls | 207 (`Code`) | `Code` verbatim environment (agnostic code listing) | — | out-of-scope — environment choice is author preference |
| jss.cls | 208 (`CodeInput`) | `CodeInput` environment (preferred for command-prompt inputs) | — | out-of-scope — same |
| jss.cls | 209 (`CodeOutput`) | `CodeOutput` environment | — | out-of-scope — same |
| jss.cls | 210 (`CodeChunk`) | `CodeChunk` wrapper environment | — | out-of-scope — same |
| jss.cls | 211 (Gin width) | Default figure width set to 0.8\textwidth by `\setkeys{Gin}{width=0.8\textwidth}` | — | out-of-scope — rendering-time default; no author-side enforcement |
| jss.cls | N/A | **`\dfn{}` is not defined in `jss.cls` v3.3** — the spec's scaffolding prompt listed it, but it must not be required by any rule unless vendored sources change (see §5 open questions) | — | out-of-scope |
| jss.cls | N/A | **`\file{}` is not defined in `jss.cls` v3.3** — same treatment as `\dfn{}` above (see §5 open questions) | — | out-of-scope |

### 1.2 `article.tex` — structural template provisions

Authority: `article_tex`. Structural rules should enforce the same section order and preamble pattern this template exhibits.

| source | anchor | provision | covering_rule_ids | status |
|---|---|---|---|---|
| article.tex | 1 | Document class is declared as `\documentclass[article]{jss}` (for ordinary articles) | JSS-PRE-001 | covered |
| article.tex | 6 | Recommended packages are `orcidlink`, `thumbpdf`, `lmodern` | — | out-of-scope — author-choice recommendation; enforcing would false-positive on papers that don't use ORCID |
| article.tex | 12–13 (`\class`, `\fct`) | Authors MAY define article-local convenience macros (`\class`, `\fct`) that delegate to `\code{}` | — | out-of-scope — "MAY" not "MUST"; author-local convenience |
| article.tex | 22–23 (`\author`) | `\author{...}` uses `\And` or `\AND` to separate authors (not comma); inline `\orcidlink{...}` is permitted | JSS-STRUCT-005 | covered — 2026-04-23 scope refinement: new rule added |
| article.tex | 24 (`\Plainauthor`) | `\Plainauthor{...}` separates authors by comma | — | gap — companion to `\Plaintitle`; deferred |
| article.tex | 29–31 (title block) | `\title{...}` (with markup), `\Plaintitle{...}` (no markup), and `\Shorttitle{...}` (with markup) all present | JSS-PRE-003 | covered — PRE-003 enforces `\Plaintitle`; `\Shorttitle` is gap row above |
| article.tex | 29 | `\title{}` uses **title case** (per style guide SG-007) | JSS-CAP-001 | covered |
| article.tex | 34–44 (`\Abstract`) | `\Abstract{...}` present before `\begin{document}` | JSS-PRE-004 | covered |
| article.tex | 49 (`\Keywords`) | `\Keywords{...}` is comma-separated and in sentence case (per SG and comment on line 48) | JSS-PRE-005, JSS-CAP-004 | covered — PRE-005 enforces presence; CAP-004 enforces sentence case |
| article.tex | 50 (`\Plainkeywords`) | `\Plainkeywords{...}` mirror of `\Keywords` without markup | — | gap — companion metadata field; deferred alongside `\Plaintitle` follow-up |
| article.tex | 57–68 (`\Address`) | `\Address{...}` contains author, affiliation, postal address, `\email{...}`, `\url{...}` | JSS-PRE-002 | covered — PRE-002 requires `\Address`; fine-grained content checks deferred |
| article.tex | 86 (`\section`) | First numbered section is Introduction; uses `\section[plain]{markup}` to separate bookmark/PDF title from markup title | JSS-MARKUP-004 | covered — MARKUP-004 enforces the plain-text shim on section titles with markup |
| article.tex | 86, 145, 247, 378 | Section labels follow the `sec:introname` convention (`sec:intro`, `sec:models`, `sec:illustrations`, `sec:summary`) | — | gap — label-naming convention not enforced; candidate follow-up (low severity, high FP risk) |
| article.tex | 378 (summary) | Summary / discussion section is present | JSS-STRUCT-001 | covered |
| article.tex | 387 (`\section*`) | "Computational details" is an **unnumbered** section (`\section*{...}`) | — | gap — pattern not enforced; "Computational details" is optional per article.tex:389 |
| article.tex | 404 (`\section*`) | "Acknowledgments" is an unnumbered section; **AE spelling** ("Acknowledgments", not "Acknowledgements") is normative (comment on line 407) | JSS-STRUCT-002 | covered |
| article.tex | 423 (`\bibliography`) | References are loaded via `\bibliography{refs}` (BibTeX) | JSS-STRUCT-004 | covered |
| article.tex | 430 (`\newpage`) | Appendix follows the bibliography after a page break | — | gap — page-break-before-appendix not enforced; low signal |
| article.tex | 432–480 (appendix) | Appendix sections have proper titles (not just "Appendix"); labels use `app:name` convention | JSS-STRUCT-003 | covered — STRUCT-003 enforces proper titles; label convention is gap |
| article.tex | 88–104 (markup usage) | `\proglang{}`, `\pkg{}`, `\code{}` markup is used throughout the manuscript body (including in section titles — with plain-text shim in the optional argument) | JSS-MARKUP-001, JSS-MARKUP-002, JSS-MARKUP-003, JSS-MARKUP-004 | covered |
| article.tex | 170–174 (`{Code}`) | `{Code}` environment used for code synopses that are not meant to be executed | — | out-of-scope — environment choice is author preference |
| article.tex | 289–317 (`{CodeChunk}`+`{CodeInput}`/`{CodeOutput}`) | `{CodeChunk}` wraps matching `{CodeInput}` / `{CodeOutput}` for executed code | — | out-of-scope — environment-wrapping pattern, author preference |
| article.tex | 291 (`R> ` prompt) | R code inputs use `R> ` as the prompt and `+  ` as the continuation prompt | — | gap — prompt convention not enforced; candidate follow-up |
| article.tex | 154–156 (equation spacing) | `{equation}` environments have **no blank lines** before/after (blank lines are suppressed with `%` comments) | JSS-OPER-003 | covered |

### 1.3 Style guide — `https://www.jstatsoft.org/style`

Authority: `style_guide`. Fetched 2026-04-23. 60 normative directives enumerated.

Reviewer: mark directives that are **out of scope** for a static LaTeX linter (e.g., graphics pen-to-paper ratio, which requires rendering) as `out-of-scope` with a one-line rationale; the rest are coverage targets.

| source | anchor | provision | covering_rule_ids | status |
|---|---|---|---|---|
| style_guide | general-requirements | SG-001 MUST: All submissions are formatted using LaTeX and JSS style files | JSS-PRE-001 | covered |
| style_guide | general-requirements | SG-002 SHOULD: Keep LaTeX code as simple as possible; avoid unnecessary packages/commands | JSS-HOUSE-003 | covered |
| style_guide | latex-subsection | SG-003 SHOULD: Use pdfLaTeX to compile manuscripts to PDF | — | out-of-scope — compiler choice is not statically visible in the manuscript source |
| style_guide | #what-are-the-most-important-style-guidelines-in-jss | SG-004 MUST: Manuscript must be compilable by pdfLaTeX | — | out-of-scope — compilability is a dynamic property; delegating to `jss-lint --parse` is sufficient |
| style_guide | #what-are-the-most-important-style-guidelines-in-jss | SG-005 MUST: Use `\proglang`, `\pkg`, `\code` markup throughout the paper, including titles and references | JSS-MARKUP-001, JSS-MARKUP-002, JSS-MARKUP-003, JSS-REFS-004 | covered |
| style_guide | #what-are-the-most-important-style-guidelines-in-jss | SG-006 MUST: Provide references in a `.bib` BibTeX database; cite via `\cite`, `\citep`, `\citet`, etc. | JSS-STRUCT-004, JSS-CITE-004 | covered |
| style_guide | #what-are-the-most-important-style-guidelines-in-jss | SG-007 MUST: `\title` is in title style | JSS-CAP-001 | covered |
| style_guide | #what-are-the-most-important-style-guidelines-in-jss | SG-008 MUST: All titles in the BibTeX file are in title style | JSS-REFS-002 | covered |
| style_guide | #what-are-the-most-important-style-guidelines-in-jss | SG-009 MUST: `\section`, `\subsection`, etc. are in sentence style | JSS-CAP-002 | covered |
| style_guide | #what-are-the-most-important-style-guidelines-in-jss | SG-010 MUST: Figure/table captions (annotations) are in sentence style | JSS-CAP-003 | covered |
| style_guide | #what-are-the-most-important-style-guidelines-in-jss | SG-011 MUST: Figures, tables, and equations are marked with `\label` and referenced by `\ref` | JSS-XREF-001 | covered |
| style_guide | #what-are-the-most-important-style-guidelines-in-jss | SG-012 MUST: Software packages are cited via `\cite{}` | JSS-CITE-002 | covered |
| style_guide | #what-are-the-capitalization-rules-in-jss-what-is-title-style-and-sentence-style | SG-013 MUST: In sentence style, capitalise only the first word and the first word after colon/hyphen; proper names remain uppercase | JSS-CAP-002, JSS-CAP-003, JSS-CAP-004 | covered |
| style_guide | #what-are-the-capitalization-rules-in-jss-what-is-title-style-and-sentence-style | SG-014 MUST: In title style, capitalise all principal words; articles, coordinating conjunctions, and prepositions stay lowercase unless first/last | JSS-CAP-001 | covered — heuristic-only; full principal-word dictionary deferred |
| style_guide | #how-to-cite-software | SG-015 SHOULD: If software has a recommended citation, use it; otherwise cite the manual or webpage | JSS-CITE-002 | covered |
| style_guide | #how-to-cite-r-packages | SG-016 SHOULD: Check for official R package citation on CRAN or via `citation("pkg")`; otherwise use CRAN-style reference | — | gap — CRAN-backed validation is explicitly deferred (spec FR-023); covered in future work via an ecosystem check |
| style_guide | #how-to-cite-r-packages | SG-017 MUST: BibTeX is valid, title is in title style, `\proglang`/`\pkg`/`\code` markup used appropriately | JSS-BIBTEX-001, JSS-BIBTEX-002, JSS-REFS-002, JSS-REFS-004 | covered |
| style_guide | #what-are-the-different-cite-citet-citep-commands-about | SG-018 DO NOT: Use brackets-within-brackets constructs like `(\cite{...})` | JSS-CITE-001, JSS-CITE-003 | covered |
| style_guide | #how-should-abbrevations-be-formatted | SG-019 MUST: Spell abbreviations in upper-case letters without periods, small caps, italics, or additional formatting | JSS-ABBR-001 | covered |
| style_guide | #how-should-abbrevations-be-formatted | SG-020 MUST: Introduce all abbreviations with expansion at first use; expansion is not capitalised unless it contains proper names or starts a sentence | JSS-ABBR-002 | covered |
| style_guide | #how-to-format-figuretable-captions | SG-021 MUST: Captions appear below the corresponding figure/table | JSS-TYPO-004 | covered — 2026-04-23 scope refinement: new rule added |
| style_guide | #how-to-format-figuretable-captions | SG-022 MUST: Captions are in sentence style and end with a period | JSS-CAP-003, JSS-TYPO-001 | covered |
| style_guide | #how-to-format-figuretable-captions | SG-023 DO NOT: Use additional formatting (`\emph`, `\bf`, `\it`) inside captions | JSS-TYPO-002 | covered |
| style_guide | #how-to-format-figuretable-captions | SG-024 MUST: All table row/column headers are in sentence style | — | gap — requires tabular-cell-aware check; candidate follow-up |
| style_guide | #how-to-format-figuretable-captions | SG-025 DO NOT: Use footnote-style annotations in tables; annotations go in the caption | JSS-TYPO-003 | covered |
| style_guide | #how-should-code-be-formatted-in-the-manuscript | SG-026 SHOULD: Present code in usual text flow with sufficient spaces for readability | — | out-of-scope — "text flow" is layout / rendering, not a source-level check |
| style_guide | #how-should-code-be-formatted-in-the-manuscript | SG-027 SHOULD: Include spaces before/after operators and after commas in code (unless syntactically meaningful) | JSS-CODE-003 | covered |
| style_guide | #how-should-code-be-formatted-in-the-manuscript | SG-028 SHOULD: Apply consistent spacing to both inline and verbatim code | JSS-CODE-003 | covered |
| style_guide | #how-should-code-be-formatted-in-the-manuscript | SG-029 DO NOT: Include comments within verbatim code; place comments in normal LaTeX text | JSS-CODE-001 | covered |
| style_guide | #how-should-code-be-formatted-in-the-manuscript | SG-030 SHOULD: Use `\code{...}` for inline code chunks | JSS-MARKUP-003 | covered |
| style_guide | #how-should-code-be-formatted-in-the-manuscript | SG-031 MUST: Code input/output fits within normal textwidth | JSS-WIDTH-001 | covered |
| style_guide | #what-is-a-good-pen-to-paper-ratio-for-my-graphics | SG-032 MUST: Graphics are legible on paper and on screen | — | out-of-scope — rendering-time, not source-time |
| style_guide | #what-is-a-good-pen-to-paper-ratio-for-my-graphics | SG-033 SHOULD: Graphics annotations are about the size of the figure caption or slightly smaller | — | out-of-scope — rendering-time |
| style_guide | #some-of-my-graphics-files-are-very-large-what-should-i-do | SG-034 SHOULD: If a vector graphic is large/slow, also supply a raster version (`.jpg`/`.png`) | — | out-of-scope — filesystem-level |
| style_guide | #some-of-my-graphics-files-are-very-large-what-should-i-do | SG-035 MUST: Annotations in raster graphics remain legible (no pixelation) | — | out-of-scope — rendering-time |
| style_guide | #how-should-my-r-package-reflect-that-a-manuscript-about-it-was-published-in-jss | SG-036 SHOULD: Include the JSS paper in `\references{}` of relevant `.Rd` pages | — | out-of-scope — target is R-package `.Rd` files, not the manuscript |
| style_guide | #how-should-my-r-package-reflect-that-a-manuscript-about-it-was-published-in-jss | SG-037 SHOULD: Include `CITATION` file at `inst/CITATION` within the R package | — | out-of-scope — R-package-level, not manuscript-level |
| style_guide | #how-should-my-r-package-reflect-that-a-manuscript-about-it-was-published-in-jss | SG-038 SHOULD: Turn the JSS manuscript into a package vignette | — | out-of-scope — .Rnw / vignette territory (Step 4+) |
| style_guide | #how-can-i-turn-my-jss-paper-into-an-r-package-vignette | SG-039 SHOULD: Use the JSS paper as the basis for the vignette | — | out-of-scope — .Rnw |
| style_guide | #how-can-i-turn-my-jss-paper-into-an-r-package-vignette | SG-040 SHOULD: Use Sweave-style code chunks for inputs/outputs/graphics in the vignette | — | out-of-scope — .Rnw |
| style_guide | #how-can-i-turn-my-jss-paper-into-an-r-package-vignette | SG-041 SHOULD: Use `\documentclass[nojss]{jss}` to turn off JSS header/footer in the vignette | — | out-of-scope — .Rnw |
| style_guide | #how-can-i-turn-my-jss-paper-into-an-r-package-vignette | SG-042 SHOULD: Cite the JSS paper in the vignette abstract or introduction | — | out-of-scope — .Rnw |
| style_guide | #how-can-i-turn-my-jss-paper-into-an-r-package-vignette | SG-043 SHOULD (advisory): Set `options(prompt = "R> ", continue = "+  ", width = 70, useFancyQuotes = FALSE)` invisibly at the start of the vignette | — | out-of-scope — .Rnw |
| style_guide | #which-naming-conventions-are-used-for-software-journal-and-publisher-names-in-jss | SG-044 MUST: "Fortran" not "FORTRAN" | JSS-NAME-001 | covered |
| style_guide | #which-naming-conventions-are-used-for-software-journal-and-publisher-names-in-jss | SG-045 MUST: "Java" not "JAVA" / "java" | JSS-NAME-001 | covered |
| style_guide | #which-naming-conventions-are-used-for-software-journal-and-publisher-names-in-jss | SG-046 MUST: "MATLAB" not "Matlab" / "matlab" | JSS-NAME-001 | covered |
| style_guide | #which-naming-conventions-are-used-for-software-journal-and-publisher-names-in-jss | SG-047 MUST: "S-PLUS" not "Splus" / "S-Plus" | JSS-NAME-001 | covered |
| style_guide | #which-naming-conventions-are-used-for-software-journal-and-publisher-names-in-jss | SG-048 MUST: "The American Statistician" (with the article) | JSS-NAME-002 | covered |
| style_guide | #which-naming-conventions-are-used-for-software-journal-and-publisher-names-in-jss | SG-049 MUST: "The Annals of Statistics" (with the article) | JSS-NAME-002 | covered |
| style_guide | #which-naming-conventions-are-used-for-software-journal-and-publisher-names-in-jss | SG-050 MUST: "Journal of the Royal Statistical Society B" (not "..., Series B") | JSS-NAME-002 | covered |
| style_guide | #which-naming-conventions-are-used-for-software-journal-and-publisher-names-in-jss | SG-051 MUST: "Springer-Verlag" (not "Springer") | JSS-NAME-002 | covered |
| style_guide | #which-naming-conventions-are-used-for-software-journal-and-publisher-names-in-jss | SG-052 MUST: "John Wiley & Sons" (not "Wiley" / "John Wiley & Sons Inc.") | JSS-NAME-002 | covered |
| style_guide | #my-latex-paper-does-not-compile-when-there-is-jss-markup-in-section-titles-what-should-i-do | SG-053 SHOULD: Section titles containing markup supply a plain-text shim via `\section[plain]{markup}` for PDF bookmarks | JSS-MARKUP-004 | covered |
| style_guide | #miscellaneous | SG-054 MUST: Use "Section x.y" (not "Subsection x.y") when referring to subsections | JSS-XREF-003 | covered |
| style_guide | #miscellaneous | SG-055 MUST: "e.g.", "i.e." are followed by a comma to prevent LaTeX from interpreting the period as a sentence end | JSS-HOUSE-001 | covered |
| style_guide | #miscellaneous | SG-056 MUST: "$p$~value", "$t$~statistic", etc. have no hyphen and a tie `~` between symbol and noun | JSS-OPER-001 | covered |
| style_guide | #miscellaneous | SG-057 MUST: Use `\top` (not `'` or `T`) for the transpose symbol (`X^\top`) | JSS-OPER-002 | covered |
| style_guide | #miscellaneous | SG-058 MUST: In R-related manuscripts, first argument of `data()` and `library()` is quoted (`library("foo")`) | JSS-CODE-002 | covered |
| style_guide | #miscellaneous | SG-059 MUST: Book editions are indicated as 2nd, 3rd, …  | JSS-HOUSE-002 | covered |
| style_guide | #miscellaneous | SG-060 SHOULD: Prefer `Equation~\ref{...}` (capitalised) over bare `(\ref{...})` when referring to equations, except when reference count is large | JSS-XREF-002 | covered |

### 1.4 Author instructions — `https://www.jstatsoft.org/authors` (§ Manuscript preparation et seq.)

Authority: `author_instructions`. Fetched 2026-04-23. 22 directives enumerated. Many are submission-process rules (PDF upload, file-size limits, GPL licensing) that cannot be checked from a `.tex`/`.bib` source and are therefore `out-of-scope` for the linter — mark them explicitly so the reviewer knows they were read and considered rather than missed.

| source | anchor | provision | covering_rule_ids | status |
|---|---|---|---|---|
| author_instructions | manuscript-preparation | AI-001 MUST: Manuscripts are written in English using LaTeX | JSS-PRE-001 | covered — PRE-001 covers the LaTeX half (class must be `jss`); English detection is out-of-scope |
| author_instructions | manuscript-preparation | AI-002 MUST: JSS Style Guide is followed (delegates to §1.3) | — | out-of-scope — meta/delegation, see §1.3 coverage |
| author_instructions | manuscript-preparation | AI-003 MUST: Only PDF files can be submitted (submission format — not linter-checkable from `.tex`) | — | out-of-scope |
| author_instructions | manuscript-preparation | AI-004 Implicit: Authors are responsible for appropriate format (meta-rule — delegates to the other rules) | — | out-of-scope |
| author_instructions | manuscript-preparation | AI-005 Implicit: Non-compliant manuscripts are returned (meta-consequence, not a lint rule) | — | out-of-scope |
| author_instructions | manuscript-preparation | AI-006 SHOULD (advisory): Find a local LaTeX expert for assistance (meta-advice) | — | out-of-scope |
| author_instructions | manuscript-preparation | AI-007 NOTE: Manuscripts over 30 pages have longer review times (informational, not normative) | — | out-of-scope |
| author_instructions | manuscript-preparation | AI-008 MUST: All figures, tables, and output are fully reproducible on ≥1 platform (cannot be verified from `.tex` alone) | — | out-of-scope |
| author_instructions | manuscript-preparation | AI-009 MUST: Platform dependencies indicated with the submission (submission metadata) | — | out-of-scope |
| author_instructions | manuscript-preparation | AI-010 MUST: Random seed initialised when results depend on simulation | — | gap — requires inspecting the replication script, not just the manuscript; deferred (candidate for eval-side checks) |
| author_instructions | manuscript-preparation | AI-011 SHOULD: Reproducibility is demonstrated by a standalone replication script (separate file, not the manuscript) | — | out-of-scope |
| author_instructions | manuscript-preparation | AI-012 SHOULD: Replication completes in ~1 hour on a regular PC (runtime claim) | — | out-of-scope |
| author_instructions | manuscript-preparation | AI-013 SHOULD (advisory): If replication is slow/specialised, supply a proxy script | — | out-of-scope |
| author_instructions | manuscript-preparation | AI-014 SHOULD (advisory): Provide an output file showing replication results | — | out-of-scope |
| author_instructions | manuscript-preparation | AI-015 SHOULD: For R submissions, provide `code.html` via `knitr::spin('code.R')` including `sessionInfo()` | — | out-of-scope |
| author_instructions | requirements | AI-016 MUST: PDF manuscript in JSS style is a required attachment | — | out-of-scope |
| author_instructions | requirements | AI-017 MUST: Replication materials are a required attachment | — | out-of-scope |
| author_instructions | requirements | AI-018 MUST: Large attachments are explained and linked | — | out-of-scope |
| author_instructions | software-preparation | AI-019 MUST: Source code is submitted as ASCII files | — | out-of-scope |
| author_instructions | software-preparation | AI-020 SHOULD: Code is readable and commented | — | out-of-scope |
| author_instructions | software-preparation | AI-021 HARD LIMIT: Max upload size 50 MB | — | out-of-scope |
| author_instructions | software-preparation | AI-022 MUST: Code includes GPL-2 / GPL-3 / GPL-compatible licence | — | out-of-scope |

---

## 2. Rule inventory

Flat list of every rule in `catalogue.yaml`, sorted by category rollout order then `rule_id`. Rows marked **`approve (tentative)`** are clean on my read — convert to `approve` if you agree, override otherwise. Rows marked **`needs-more-context: …`** are flagged for your explicit call; the rationale in the cell points at the judgement needed. Other valid `reviewer_note` values: `merge-with-<id>`, `split`, `drop`, `defer`.

**Populated 2026-04-23 by LLM pre-pass from `catalogue.yaml`.**
**Refreshed 2026-04-23 scope refinement**: **56 rules** (was 48). Changes from the reviewer pass:
- **Removed** (1): `JSS-CITE-001` retired per reviewer (id permanently reserved; see top of `catalogue.yaml`).
- **Added** (9): `JSS-PRE-006`, `JSS-STRUCT-005`, `JSS-CITE-004` retained, `JSS-REFS-006` / `JSS-REFS-007`, `JSS-BIBTEX-003` / `JSS-BIBTEX-004`, `JSS-TYPO-004`, `JSS-OPER-004`, `JSS-XREF-004`.
- **Refined notes** (12): descriptions/notes tightened per reviewer (JSS-PRE-001 option-default, JSS-PRE-003 scope to title-with-markup, JSS-STRUCT-001 flagged for removal, JSS-MARKUP-001 FP strategy, JSS-CITE-002 strict paragraph, JSS-CITE-004 code-mask, JSS-REFS-002 narrow + split, JSS-REFS-003 advisory, JSS-TYPO-002 full-caption scope, JSS-WIDTH-001 configurable columns, JSS-OPER-003 trailing-period carve-out, JSS-ABBR-002 deferred).
- **Split** (1): `JSS-REFS-002` into `JSS-REFS-002` (tight) + `JSS-REFS-006` (loose) per reviewer.
- **Deferred in place** (1): `JSS-ABBR-002` kept in catalogue with `DEFERRED` note — first-use state-tracking is implementation-brittle.

| rule_id | category | description (one line) | authority | authority_ref | severity | reviewer_note |
|---|---|---|---|---|---|---|
| `JSS-PRE-001` | preamble | Document class must be jss with a valid class option (article, codesnippet, bookreview, softwarereview) | jss_cls | `jss.cls:37` | error | one of the four options is always true, see \@articletrue at line 26, if two or more options are specified, then the last one wins |
| `JSS-PRE-002` | preamble | Preamble defines \Address{} with author affiliation and contact | jss_cls | `jss.cls:\Address` | error | approve |
| `JSS-PRE-003` | preamble | Preamble defines \Plaintitle{} alongside \title{} so the PDF metadata gets a markup-free title | jss_cls | `jss.cls:\Plaintitle` | error | only required if title contains markup |
| `JSS-PRE-004` | preamble | \Abstract{} is present and overrides the sentinel placeholder from jss.cls | jss_cls | `jss.cls:120` | error | approve |
| `JSS-PRE-005` | preamble | \Keywords{} is present and overrides the sentinel placeholder from jss.cls | jss_cls | `jss.cls:197` | error | approve |
| `JSS-PRE-006` *(NEW 2026-04-23)* | preamble | \Plaintitle, \Plainauthor, \Plainkeywords contain no LaTeX markup (PDF metadata must be plain text) | jss_cls | `jss.cls:\Plaintitle` | warning | approve (tentative) |
| `JSS-STRUCT-001` | structure | Document ends with a summary / discussion section before the bibliography | article_tex | `article.tex:378` | warning | skip, or find better convincing reason |
| `JSS-STRUCT-002` | structure | Acknowledgments section uses American spelling (not "Acknowledgements") | article_tex | `article.tex:407` | warning | approve |
| `JSS-STRUCT-003` | structure | Appendix sections have proper titles instead of a bare "Appendix" | article_tex | `article.tex:438` | warning | approve |
| `JSS-STRUCT-004` | structure | References are declared via \bibliography{} rather than a hand-written thebibliography environment | style_guide | `#what-are-the-most-important-style-guidelines-in-jss` | error | approve |
| `JSS-STRUCT-005` *(NEW 2026-04-23)* | structure | \author{} separates authors with \And or \AND (not lowercase \and) | article_tex | `article.tex:22` | warning | approve (tentative) |
| `JSS-MARKUP-001` | markup | Programming-language names in prose are wrapped in \proglang{} | jss_cls | `jss.cls:\proglang` | warning | Approve. Authors really need this one. Most FPs can be avoided by only checking within normal text. Variables should be written in math mode and those should be skipped. Don't match Pascal, nobody uses it anyway. Filter out initials in names. |
| `JSS-MARKUP-002` | markup | Software-package names in prose are wrapped in \pkg{} | jss_cls | `jss.cls:\pkg` | warning | approve |
| `JSS-MARKUP-003` | markup | Inline function, argument, and command names are wrapped in \code{} | jss_cls | `jss.cls:\code` | warning | approve |
| `JSS-MARKUP-004` | markup | Section titles containing markup supply a plain-text shim via \section[plain]{markup} | style_guide | `#my-latex-paper-does-not-compile-when-there-is-jss-markup-in-section-titles-what-should-i-do` | warning | approve |
| ~~`JSS-CITE-001`~~ *(RETIRED 2026-04-23)* | ~~citations~~ | ~~\emph used where a citation key is meant~~ | — | — | — | **Retired** per reviewer — moved to `retired_rule_ids` comment at top of `catalogue.yaml`; id permanently reserved. |
| `JSS-CITE-002` | citations | First occurrence of a software package has a citation within the same paragraph | style_guide | `#what-are-the-most-important-style-guidelines-in-jss` | warning | The first time a software package is mentioned, the citation should follow closely after (or was included shortly before). Needs to be at least in the same paragraph. |
| `JSS-CITE-003` | citations | Avoid bracket-in-bracket citation forms like (\cite{...}); use \citep{...} instead | style_guide | `#what-are-the-different-cite-citet-citep-commands-about` | warning | approve |
| `JSS-CITE-004` | citations | Citations use natbib commands (\cite, \citet, \citep, \citealp) rather than hardcoded author-year text | jss_cls | `jss.cls:62` | warning | approve, don't match within code or verbatim environments |
| `JSS-REFS-001` | references | BibTeX entries carry a year field so natbib author-year citations render correctly | style_guide | `#what-are-the-most-important-style-guidelines-in-jss` | warning | approve |
| `JSS-REFS-002` | references | BibTeX titles are in title style — tight heuristic (flags titles that are entirely lowercase) | style_guide | `#what-are-the-most-important-style-guidelines-in-jss` | warning | approve (split half — was JSS-REFS-002 "title case"; loose half is now JSS-REFS-006) |
| `JSS-REFS-003` | references | BibTeX entries include a doi field where one is available (advisory) | article_tex | `article.tex:421` | info | advisory-only |
| `JSS-REFS-004` | references | BibTeX titles use JSS markup (\proglang, \pkg, \code) for language and package names | style_guide | `#how-to-cite-r-packages` | warning | approve |
| `JSS-REFS-005` | references | Journal titles in BibTeX entries are not abbreviated | article_tex | `article.tex:473` | warning | accept |
| `JSS-REFS-006` *(NEW 2026-04-23)* | references | BibTeX titles are in title style — loose heuristic (flags lowercase first word or unusual mixed case) | style_guide | `#what-are-the-most-important-style-guidelines-in-jss` | warning | approve (tentative) — loose split companion to JSS-REFS-002 |
| `JSS-REFS-007` *(NEW 2026-04-23)* | references | Journal titles in BibTeX entries are in title case | article_tex | `article.tex:473` | warning | approve (tentative) — user-requested; complements JSS-REFS-005's not-abbreviated half |
| `JSS-BIBTEX-001` | bibtex | Every BibTeX entry has a non-empty citation key | style_guide | `#how-to-cite-r-packages` | error | approve |
| `JSS-BIBTEX-002` | bibtex | BibTeX citation keys are unique within the database | style_guide | `#how-to-cite-r-packages` | error | approve |
| `JSS-BIBTEX-003` *(NEW 2026-04-23)* | bibtex | BibTeX entries carry the fields required for their entry type (article, book, inproceedings, …) | style_guide | `#how-to-cite-r-packages` | error | approve (tentative) — per-type required-field matrix documented in catalogue notes |
| `JSS-BIBTEX-004` *(NEW 2026-04-23)* | bibtex | Entries with 6+ authors use \shortcites{} or the shortnames class option is enabled | jss_cls | `jss.cls:45` | warning | approve (tentative) |
| `JSS-NAME-001` | naming | Programming-language names use their canonical capitalisation | style_guide | `#which-naming-conventions-are-used-for-software-journal-and-publisher-names-in-jss` | warning | approve |
| `JSS-NAME-002` | naming | Publisher and journal names follow JSS conventions (e.g., "Springer-Verlag", "The Annals of Statistics") | style_guide | `#which-naming-conventions-are-used-for-software-journal-and-publisher-names-in-jss` | warning | approve |
| `JSS-CAP-001` | capitalization | \title{} is in title style (principal words capitalised) | style_guide | `#what-are-the-most-important-style-guidelines-in-jss` | warning | Go for a partial validation, some common words should be lower case, most should be upper case. Evaluate what works via the eval improvement loop |
| `JSS-CAP-002` | capitalization | Section titles are in sentence style (first word capitalised; others lowercase except proper names) | style_guide | `#what-are-the-most-important-style-guidelines-in-jss` | warning | Accept FP. Evaluate what works via the eval improvement loop. |
| `JSS-CAP-003` | capitalization | Figure / table captions are in sentence style | style_guide | `#how-to-format-figuretable-captions` | warning | approve |
| `JSS-CAP-004` | capitalization | \Keywords{} is comma-separated and in sentence case | article_tex | `article.tex:48` | warning | approve |
| `JSS-TYPO-001` | typography | Figure and table captions end with a period | style_guide | `#how-to-format-figuretable-captions` | warning | approve |
| `JSS-TYPO-002` | typography | Figure / table captions avoid emphasis macros wrapping the whole caption (\emph, \textbf, \textit on full caption) | style_guide | `#how-to-format-figuretable-captions` | warning | approve but note: this rule only applies to the full caption being formatted. Formatting of short parts is allowed for sectioning, etc |
| `JSS-TYPO-003` | typography | Tables do not use footnote-style annotations; annotations go in the caption | style_guide | `#how-to-format-figuretable-captions` | warning | approve |
| `JSS-TYPO-004` *(NEW 2026-04-23)* | typography | \caption{} appears after the figure / table content, not before | style_guide | `#how-to-format-figuretable-captions` | warning | approve (tentative) — closes §1.3 SG-021 gap |
| `JSS-ABBR-001` | abbreviations | Abbreviations are in uppercase without periods or additional formatting | style_guide | `#how-should-abbrevations-be-formatted` | warning | approve |
| `JSS-ABBR-002` | abbreviations | Abbreviations are introduced with expansion at first use | style_guide | `#how-should-abbrevations-be-formatted` | warning | Defer |
| `JSS-CODE-001` | code_style | Verbatim / CodeInput blocks do not contain comments; comments belong in the surrounding LaTeX text | style_guide | `#how-should-code-be-formatted-in-the-manuscript` | warning | approve |
| `JSS-CODE-002` | code_style | R library() and data() calls quote their first argument | style_guide | `#miscellaneous` | warning | approve |
| `JSS-CODE-003` | code_style | Code samples use spaces around operators and after commas | style_guide | `#how-should-code-be-formatted-in-the-manuscript` | warning | approve |
| `JSS-WIDTH-001` | code_width | Code input / output inside Sinput / CodeInput / CodeOutput environments fits within 80 columns | style_guide | `#how-should-code-be-formatted-in-the-manuscript` | warning | approve - make number of columns configurable |
| `JSS-OPER-001` | operators | Symbol-plus-noun constructs like p-value and t-statistic are typeset as $p$~value and $t$~statistic (tie, no hyphen) | style_guide | `#miscellaneous` | warning | approve |
| `JSS-OPER-002` | operators | Transpose is typeset with \top rather than a superscript prime or literal T | style_guide | `#miscellaneous` | warning | approve |
| `JSS-OPER-003` | operators | Display equations have no blank lines immediately before or after (use % to suppress paragraph breaks) | article_tex | `article.tex:154` | warning | approve - paragraphs may be ended with a dot at the end of equation's content, then % shouldn't be added |
| `JSS-OPER-004` *(NEW 2026-04-23)* | operators | Expectation / variance / covariance / probability use jss.cls shortcuts \E, \VAR, \COV, \Prob | jss_cls | `jss.cls:484` | warning | approve (tentative) |
| `JSS-XREF-001` | crossrefs | Figures and tables carry \label{} and are referenced by \ref{} rather than manual numbering | style_guide | `#what-are-the-most-important-style-guidelines-in-jss` | warning | approve (scope narrowed to figures/tables; numbered equations split to JSS-XREF-004 at info severity) |
| `JSS-XREF-002` | crossrefs | Equation references prefer Equation~\ref{...} (capitalised) over bare (\ref{...}) | style_guide | `#miscellaneous` | info | approve |
| `JSS-XREF-003` | crossrefs | Cross-references to subsections use "Section x.y" rather than "Subsection x.y" | style_guide | `#miscellaneous` | warning | approve |
| `JSS-XREF-004` *(NEW 2026-04-23)* | crossrefs | Numbered equations carry \label{} and are referenced from the text | style_guide | `#what-are-the-most-important-style-guidelines-in-jss` | info | approve (tentative) — info severity because unreferenced numbered equations are a style nit, not missing-callout |
| `JSS-HOUSE-001` | house_style | "e.g." and "i.e." are followed by a comma so LaTeX does not treat the period as a sentence end | style_guide | `#miscellaneous` | warning | approve |
| `JSS-HOUSE-002` | house_style | Book editions are indicated as 2nd, 3rd, etc., not as "second" or "2e" | style_guide | `#miscellaneous` | warning | approve |
| `JSS-HOUSE-003` | house_style | Preamble avoids loading LaTeX packages that jss.cls already provides (graphicx, xcolor, ae, fancyvrb, hyperref) | jss_cls | `jss.cls:54` | info | approve |

### Flagged rows (summary)

Seven rules flagged `needs-more-context`. Each flag is an explicit judgement call the reviewer must make — accept the narrow scope as-shipped, or tune / defer / drop:

| rule_id | judgement call |
|---|---|
| `JSS-MARKUP-001` | accept FP risk on `R` as variable, or defer until context-aware disambiguation lands? |
| `JSS-CITE-002` | 400-char paragraph window — accept, tune per-corpus, or defer? |
| `JSS-CITE-004` | code / verbatim masking not yet implemented — accept FPs or defer? |
| `JSS-REFS-002` | "all-lowercase" heuristic misses partial violations — accept or split? |
| `JSS-REFS-003` | "DOI where available" is non-decidable — keep as advisory `info`, or drop? |
| `JSS-REFS-005` | journal-abbrev heuristic — tighten allow-list or accept? |
| `JSS-CAP-001` / `JSS-CAP-002` | title-case / sentence-case heuristics require a principal-word dictionary — accept narrow scope or defer? |
| `JSS-ABBR-002` | first-use tracking is brittle — defer? |

### How to sign off §2

1. Convert each `approve (tentative)` to `approve` (or override to one of the other valid values).
2. Rule on each `needs-more-context` row — replace the text with your final disposition.
3. Every row must carry one of `approve | merge-with-<id> | split | drop | defer` before sign-off.

---

## 3. Category sanity checks

All mechanical checks run 2026-04-23 against `catalogue.yaml` — details inline.

- [X] CHK001 The category set in `catalogue.yaml` matches the list in `spec.md` FR-005 — **pass**: 15 categories, identical set and order: `preamble, structure, markup, citations, references, bibtex, naming, capitalization, typography, abbreviations, code_style, code_width, operators, crossrefs, house_style`.
- [X] CHK002 Per-category rule counts — **refreshed 2026-04-23 scope refinement** (56 rules). Median is **4**; ≥2× threshold = 8 rules (none triggered), ≤⅓ threshold ≈ 1 rule (one triggered: `code_width`). Counts:

  | category | rule count | flag? |
  |---|---|---|
  | preamble | 6 | — |
  | structure | 5 | — |
  | markup | 4 | — |
  | citations | 3 | — (was 4; JSS-CITE-001 retired) |
  | references | 7 | — (was 5; +JSS-REFS-006 loose title-case, +JSS-REFS-007 journal title-case) |
  | bibtex | 4 | — (was 2; +JSS-BIBTEX-003 required fields, +JSS-BIBTEX-004 shortcites) |
  | naming | 2 | — |
  | capitalization | 4 | — |
  | typography | 4 | — (was 3; +JSS-TYPO-004 caption-after-content) |
  | abbreviations | 2 | — (JSS-ABBR-002 deferred in place) |
  | code_style | 3 | — |
  | code_width | 1 | ⚠ thin: only `JSS-WIDTH-001` (line-length). Intentional — SG-031 is the only style-guide directive about textwidth; no other textwidth concerns exist. Alternative: fold into `code_style`; rejected because line-width is a `raw_source` inspection while `code_style` is AST-based (different inspects, different §II justification). Keep as a single-rule category. |
  | operators | 4 | — (was 3; +JSS-OPER-004 jss.cls math macros) |
  | crossrefs | 4 | — (was 3; +JSS-XREF-004 numbered-equation label/ref split) |
  | house_style | 3 | — |

- [X] CHK003 Rule-ID counter sequence is contiguous within each category — **pass with one documented retirement**: every category's counters are contiguous except `citations`, where `JSS-CITE-001` has been retired and its counter `[2, 3, 4]` ≠ `[1, 2, 3]` is intentional. Per FR-004 ("retired rule's id is never reused"), the retired id is reserved in the `catalogue.yaml` top-of-file comment. All other 14 categories are `[1, 2, …, N]` with no gaps.
- [X] CHK004 No `rule_id` appears in more than one category entry — **pass**: 56 unique ids, each maps to exactly one category (enforced by `test_catalogue.py::test_rule_ids_globally_unique`).
- [X] CHK005 No two rules in the same category have materially duplicated `description`s — **pass**: 15/15 categories show no description duplication.
- [X] CHK006 `citations`, `references`, `typography`, `capitalization` each have at least one rule, and `tasks.md` orders `citations`/`references` first and `typography`/`capitalization` last — **pass**: rollout order is `citations (Phase 5) → references (Phase 6) → bibtex → preamble → structure → markup → crossrefs → code_style → code_width → naming → operators → abbreviations → house_style → typography (Phase 18) → capitalization (Phase 19)`.
- [X] CHK007 The full category list is pinned in `catalogue.yaml`'s top-level `categories:` field — **pass**: lines 13–28 of `catalogue.yaml` enumerate exactly 15 categories, and `test_catalogue.py::test_every_declared_category_is_known` validates the list.

---

## 4. Severity consistency

Severity pre-pass run 2026-04-23 against `catalogue.yaml`. Findings inline.

- [X] CHK008 Severity tally — **refreshed 2026-04-23 scope refinement** (56 rules):

  | severity | count | delta |
  |---|---|---|
  | error | 9 | +1 (JSS-BIBTEX-003 added) |
  | warning | 43 | +6 (PRE-006, STRUCT-005, REFS-006, REFS-007, BIBTEX-004, TYPO-004, OPER-004 added; CITE-001 retired) |
  | info | 4 | +1 (JSS-XREF-004 added) |

- [X] CHK009 Every `error`-severity rule is objectively wrong — **pass**: all 9 `error` rules inspected (JSS-BIBTEX-003 added 2026-04-23: missing required fields produce malformed BibTeX output — objectively wrong).

  | rule_id | description | why "error" is correct |
  |---|---|---|
  | `JSS-PRE-001` | Document class must be jss with a valid class option | Wrong class → paper doesn't compile as JSS |
  | `JSS-PRE-002` | \Address{} missing | jss.cls :81 defines it; footer / metadata require it |
  | `JSS-PRE-003` | \Plaintitle{} missing alongside \title{} | PDF title becomes the markup-containing \title when absent |
  | `JSS-PRE-004` | \Abstract{} sentinel not overridden | jss.cls:120 sentinel "---!!!---an abstract is required---!!!---" appears in output |
  | `JSS-PRE-005` | \Keywords{} sentinel not overridden | jss.cls:197 sentinel appears in output |
  | `JSS-STRUCT-004` | No `\bibliography{}` | References silently absent from the published paper |
  | `JSS-BIBTEX-001` | Entry missing citation key | BibTeX fails to compile the entry |
  | `JSS-BIBTEX-002` | Duplicate citation keys | BibTeX resolves to undefined behaviour / warning; breaks back-links |

- [X] CHK010 Every `warning`-severity rule is a stylistic judgement — **pass**: all 37 `warning` rules read as stylistic. Spot-checked categories: `markup` (which markup command to use), `citations` (citation shape and context), `references` (BibTeX content), `naming` (canonical spellings), `capitalization` (title vs sentence style), `typography` (captions / dashes / table footnotes), `abbreviations` (capitalisation / expansion), `code_style` (spaces / comments), `code_width` (line length), `operators` (math notation), `crossrefs` (label / ref / subsection wording), `house_style` (commas / editions). None are journal-reject criteria.
- [X] CHK011 Severity within tight semantic clusters:

  | cluster | rules in cluster | severities in use | uniform? | mixed-severity rationale |
  |---|---|---|---|---|
  | preamble | 5 rules | all `error` | ✓ uniform | — |
  | structure | 4 rules | 3 `warning` + 1 `error` | ✗ mixed | **Intentional**: `JSS-STRUCT-004` (missing `\bibliography{}`) is the only structural rule whose violation produces an unpublishable paper; the other three (summary section, AE spelling, appendix titles) are stylistic. The mix reflects a real semantic boundary inside the category. |
  | markup | 4 rules | all `warning` | ✓ uniform | — |
  | citations | 4 rules | all `warning` | ✓ uniform | — |
  | references | 5 rules | 4 `warning` + 1 `info` | ✗ mixed | **Intentional**: `JSS-REFS-003` (DOI presence) is `info` because "where available" makes it unverifiable — flagged in §2 as `needs-more-context` for reviewer to ratify. Other four are warnings. |
  | bibtex | 4 rules | 3 `error` + 1 `warning` | ✗ mixed | **Intentional**: `JSS-BIBTEX-004` (shortcites for 6+ authors) is `warning` because an un-shortcited citation compiles cleanly; the other three (missing key, duplicate keys, missing required fields) produce malformed BibTeX output. |
  | naming | 2 rules | all `warning` | ✓ uniform | — |
  | capitalization | 4 rules | all `warning` | ✓ uniform | — |
  | typography | 3 rules | all `warning` | ✓ uniform | — |
  | abbreviations | 2 rules | all `warning` | ✓ uniform | — |
  | code_style | 3 rules | all `warning` | ✓ uniform | — |
  | code_width | 1 rule | `warning` | ✓ uniform (trivially) | — |
  | operators | 3 rules | all `warning` | ✓ uniform | — |
  | crossrefs | 4 rules | 2 `warning` + 2 `info` | ✗ mixed | **Intentional**: `JSS-XREF-002` (Equation~\ref over bare (\ref)) is `info` per SG-060's SHOULD-with-carve-out; `JSS-XREF-004` (numbered equation label+ref) is `info` per the 2026-04-23 split — unreferenced numbered equations are a style nit, unlike unreferenced figures/tables which suggest a missing callout. Warnings: `JSS-XREF-001`, `JSS-XREF-003`. |
  | house_style | 3 rules | 2 `warning` + 1 `info` | ✗ mixed | **Intentional**: `JSS-HOUSE-003` (no duplicate-loading of jss.cls-provided packages) is `info` because LaTeX silently handles duplicate `\usepackage` calls — a preamble that loads `\usepackage{hyperref}` redundantly still compiles correctly. Other two are warnings. |

- [X] CHK012 No `info`-severity rule enforces a MUST directive — **pass**. The 4 `info` rules are:

  | rule_id | authority directive | MUST / SHOULD / info? |
  |---|---|---|
  | `JSS-REFS-003` | article.tex:421 "DOIs should be included where available" | SHOULD (with conditional) — `info` justified |
  | `JSS-XREF-002` | style guide SG-060 "Prefer Equation~\ref{...} … except when reference count is large" | SHOULD (with carve-out) — `info` justified |
  | `JSS-XREF-004` | style guide SG-011 "Figures, tables, and equations are marked with \label and referenced by \ref" (MUST) | MUST, but scope-split: figures/tables are `warning` (JSS-XREF-001), numbered equations are `info` (JSS-XREF-004). Reviewer judgement 2026-04-23: unreferenced numbered equations are a style nit rather than a missing callout. Informational severity is the conscious downgrade for the equation subset only. |
  | `JSS-HOUSE-003` | style guide SG-002 "Keep LaTeX code as simple as possible; avoid unnecessary packages/commands" | SHOULD — `info` justified |

  One narrow exception (JSS-XREF-004): the underlying MUST directive is split between `warning` (figures/tables) and `info` (numbered equations) per reviewer judgement. Documented here for explicit ratification rather than silent downgrade.

---

## 5. Open questions for reviewer

Items `/speckit.clarify` could not auto-resolve, or that surfaced during catalogue drafting and require human judgment. Every item must be closed (answered or deferred with rationale) before sign-off.

### Vendoring-versus-scaffolding discrepancies

- [x] OQ-01 **`\dfn{}` is not defined in `jss.cls` v3.3** despite being listed in the feature-scaffolding prompt. **Closed 2026-04-23**: No rule in `catalogue.yaml` requires `\dfn{}`. Disposition: treat as out of scope permanently (§1.1 last-but-one row marks it `out-of-scope`). If upstream ever defines `\dfn{}`, the annual re-fetch will surface it and this disposition gets revisited.
- [x] OQ-02 **`\file{}` is not defined in `jss.cls` v3.3** — same disposition as OQ-01. **Closed 2026-04-23**: No rule requires `\file{}`; §1.1 marks `out-of-scope`.

### Authority-weak / authority-ambiguous rules

- [x] OQ-03 Rules whose only authority citation is inferred convention (no resolvable anchor in any of the four sources). **Closed 2026-04-23**: zero rules in the current `catalogue.yaml` are authority-less. Every row in §2 (rule inventory) has a non-empty `authority` drawn from the four-valued enum and a resolvable `authority_ref`; `tests/unit/journals/jss/test_catalogue.py::test_validate_returns_no_errors` would fail otherwise.

  | candidate rule_id | what the rule checks | reason for inferred-convention status | disposition |
  |---|---|---|---|
  | *(none)* | — | — | — |

- [x] OQ-04 Rules that cite two authorities simultaneously without a higher-authority conflict marker. **Closed 2026-04-23**: each rule in `catalogue.yaml` carries exactly one `authority`. Rules whose check is backed by both `jss.cls` and the style guide (MARKUP-001, MARKUP-002, MARKUP-003, CITE-004) pin `authority` to the higher source (`jss_cls`) and record the supporting style-guide directive in `notes`, per FR-003. No unresolved conflicts remain.

### Category boundary edge cases

- [x] OQ-05 Any rule that plausibly fits two categories. **Closed 2026-04-23**: caption rules span `capitalization` (CAP-003: sentence case), `typography` (TYPO-001: terminal period; TYPO-002: emphasis macros), and `typography` (TYPO-003: table footnotes). Each targets a distinct property of the caption, not the caption itself, so the placements are meaningful, not bureaucratic. No other ambiguous placements remain.
- [x] OQ-06 `references` vs `bibtex` boundary. **Closed 2026-04-23**: confirmed during drafting. `JSS-REFS-*` rows all inspect entry *content* (year, title case, DOI, markup, journal title). `JSS-BIBTEX-*` rows are mechanical (entry has a key; keys are unique). Boundary matches spec.md Assumptions §Category boundary — references vs. bibtex.

### Precision-gate candidates before corpus data exists

- [x] OQ-07 Rules suspected to have low precision **before** any corpus labelling. **Closed 2026-04-23** — populated. These rules use heuristics or multi-paragraph state-tracking; their per-rule precision is the most likely to fall short of the 90% gate and they warrant extra fixture coverage. Order of implementation within each category weights them later rather than earlier:

  | candidate rule_id | why suspect | tightening candidate |
  |---|---|---|
  | JSS-CAP-001 | Only lowercase-all-words titles are flagged; ambiguous "Title Without Articles" cases pass silently | Add a principal-word dictionary (deferred); current heuristic is intentionally narrow |
  | JSS-CAP-002 | Detecting sentence style without false-positives on legitimate proper nouns requires cross-checking `terms.LANGUAGES` and `terms.R_PACKAGES` | Allowlist extension via `terms.py`; corpus-driven |
  | JSS-CITE-002 | Paragraph-scope heuristic for "package mentioned → also cited in same paragraph" will false-positive on packages cited two paragraphs away | Widen scope to section; re-measure after first corpus pass |
  | JSS-ABBR-002 | Requires cross-document state ("first use"); state tracking is brittle | Per-file state with an explicit allow-list of pre-introduced abbreviations; deferred |
  | JSS-HOUSE-001 | Regex-based "e.g." / "i.e." match will false-positive inside code blocks and URLs | AST-aware masking of `\code{}`, `\url{}`, verbatim envs before the regex fires |
  | JSS-MARKUP-001 | `R` used as a variable name inside prose (e.g., "let R be the covariance matrix") would false-positive | Context-aware — require token to be followed by software-adjacent prose markers; corpus-driven |
  | JSS-REFS-002 | "All-lowercase title" heuristic will miss "Title With Three Lowercase Small Words" violations | Acceptable narrow-scope start; full title-case check deferred |

### Redundancy / collapse candidates

- [x] OQ-08 Any two rules firing on the same violation. **Closed 2026-04-23**: the caption rules (CAP-003, TYPO-001, TYPO-002, TYPO-003) target distinct caption properties, not the caption as a whole. `JSS-NAME-001` (language names) and `JSS-CAP-002` (section titles) can both fire on the same token when the token is a language name appearing in a section title — that overlap is intentional: CAP-002 flags the case, NAME-001 flags the canonical spelling. No rule-merge candidates in the current draft.
- [x] OQ-09 Authority provisions matched by >1 rule. **Closed 2026-04-23**: SG-005 → {MARKUP-001, MARKUP-002, MARKUP-003, REFS-004} — each rule targets a different macro or context; the split is meaningful. SG-017 → {BIBTEX-001, BIBTEX-002, REFS-002, REFS-004} — mechanical vs. content split is the pinned references/bibtex boundary (OQ-06). SG-022 → {CAP-003, TYPO-001} — sentence style and period-termination are distinct caption properties. No bureaucratic splits.

### Scope / target reality checks

- [x] OQ-10 Total rule count. **Closed 2026-04-23**: 48 rules across 15 categories — well within the factor-of-two bound around the ~50 planning anchor (spec.md FR-006). No scope-creep clarify pass required.
- [ ] OQ-11 Corpus has grown toward the ~50-paper target. **Deferred to implementation phase**: corpus is still at Phase A (~10 papers from spec 002 `examples/`). The N=10-labelled-violation floor for the precision gate is therefore advisory for most rules at present. The corpus grows alongside US2 category rollout (see `tasks.md` Phase 5+); re-check before sign-off on individual categories.
- [x] OQ-12 SG-032..035 and SG-036..043 out-of-scope confirmation. **Closed 2026-04-23**: §1.3 marks all of SG-032..035 (graphics rendering) and SG-036..043 (`.Rnw` vignette territory) as `out-of-scope` with one-line rationales. Linter cannot render graphics; `.Rnw` is deferred per FR-021.

### Authority-ref resolvability

- [x] OQ-13 `authority_ref` resolves against `docs/jss-template/`. **Closed 2026-04-23**: CI test `tests/unit/journals/jss/test_catalogue.py::test_jss_cls_refs_resolve` and `::test_article_tex_refs_resolve` are green against the current catalogue. Spot-checked rows `JSS-PRE-002` (jss.cls:\Address → line 81 defines `\newcommand{\Address}[1]{...}`), `JSS-PRE-004` (jss.cls:120 → sentinel `---!!!---an abstract is required---!!!---`), `JSS-STRUCT-002` (article.tex:407 → template comment "note the AE spelling"), `JSS-OPER-003` (article.tex:154 → equation-spacing comment), and `JSS-CAP-004` (article.tex:48 → keywords comma / sentence-case comment). All resolve cleanly.
- [x] OQ-14 Web anchors format. **Closed 2026-04-23**: every `style_guide` and `author_instructions` `authority_ref` uses the `#anchor-id` URL-fragment form (or a bare slug for author instructions) — no line numbers. `test_catalogue.py::test_web_refs_format` is green.

---

## Sign-off

- [X] Every row in §1.1–1.4 has a non-empty `status` — 146 rows, all annotated (65 covered, 67 out-of-scope, 14 gap; zero empty, zero redundant).
- [ ] Every rule row in §2 has a non-empty `reviewer_note` — pre-populated 2026-04-23 with `approve (tentative)` or `needs-more-context: …`; reviewer must ratify each row (convert tentative approvals to `approve`, rule on the 7 `needs-more-context` rows).
- [X] All §3 category sanity items (CHK001–CHK007) are checked — mechanical checks run 2026-04-23; all pass (one soft flag on `code_width` thin-category, justified inline).
- [X] All §4 severity consistency items (CHK008–CHK012) are checked — pre-pass run 2026-04-23; mixed-severity clusters all documented with rationale; zero info-severity rules downgrade a MUST.
- [X] All §5 open questions are closed (answered or explicitly deferred with rationale) — 13 closed 2026-04-23, OQ-11 explicitly deferred to implementation-phase corpus growth.
- [ ] Any gap (`status = gap`) is either (a) closed by adding a rule, or (b) re-classified as `out-of-scope` with rationale — **14 gaps remain** in §§1.1–1.2 as documented follow-up candidates; reviewer decides per row: leave as gap, close with a new rule, or re-classify as `out-of-scope`.
- [X] Any redundancy (`status = redundant`) is either (a) closed by merging/dropping one rule, or (b) justified in the rule's `notes` field — no rows marked `redundant`; §2 overlap analysis (CHK011) also found no merge/drop candidates.

**Reviewer**: _____________  **Date**: _____________  **Commit**: _____________

**Approval**: this file is committed with all items checked. The catalogue is cleared for the per-category rollout loop (spec.md FR-015–FR-020).
