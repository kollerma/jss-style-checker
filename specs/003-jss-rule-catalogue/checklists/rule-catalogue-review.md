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
| jss.cls | 37–49 (class options) | Manuscript declares exactly one of `article`, `codesnippet`, `bookreview`, `softwarereview` as the class option |  |  |
| jss.cls | 45 | `shortnames` class option available for natbib short-form names |  |  |
| jss.cls | 46 | `nojss` class option turns off JSS header/footer (used for vignettes) |  |  |
| jss.cls | 47–49 | `notitle`, `noheadings`, `nofooter` class options exist |  |  |
| jss.cls | 59–65 (natbib) | `natbib` loaded with `[authoryear,round]` (or `[authoryear,round,longnamesfirst]` when `shortnames` is off); `\bibpunct` set to `(){};a,` |  |  |
| jss.cls | 65 | Bibliography style is `jss` (i.e., `\bibliographystyle{jss}`) |  |  |
| jss.cls | 81 (`\Address`) | `\Address{}` metadata command (required in preamble) |  |  |
| jss.cls | 82 (`\Plaintitle`) | `\Plaintitle{}` metadata command (plain-text title without LaTeX markup) |  |  |
| jss.cls | 83 (`\Shorttitle`) | `\Shorttitle{}` metadata command (running title with markup allowed) |  |  |
| jss.cls | 84 (`\Plainauthor`) | `\Plainauthor{}` metadata command (author list without affiliations) |  |  |
| jss.cls | 85 (`\Volume`) | `\Volume{}` metadata command |  |  |
| jss.cls | 86 (`\Year`) | `\Year{}` metadata command |  |  |
| jss.cls | 87 (`\Month`) | `\Month{}` metadata command |  |  |
| jss.cls | 88 (`\Issue`) | `\Issue{}` metadata command |  |  |
| jss.cls | 89 (`\Submitdate`) | `\Submitdate{}` metadata command |  |  |
| jss.cls | 91 (`\Acceptdate`) | `\Acceptdate{}` metadata command (articles / code snippets) |  |  |
| jss.cls | 92 (`\Abstract`) | `\Abstract{}` is required and non-placeholder (default in 120 is a sentinel error) |  |  |
| jss.cls | 93 (`\Keywords`) | `\Keywords{}` is required and non-placeholder (default in 197 is a sentinel error) |  |  |
| jss.cls | 94 (`\Plainkeywords`) | `\Plainkeywords{}` metadata command |  |  |
| jss.cls | 96–108 (review metadata) | `\Reviewer`, `\Booktitle`, `\Bookauthor`, `\Publisher`, `\Pubaddress`, `\Pubyear`, `\ISBN`, `\Pages`, `\Price`, `\Plainreviewer`, `\Softwaretitle`, `\URL`, `\DOI` metadata commands exist for `bookreview` / `softwarereview` classes |  |  |
| jss.cls | 473–474 (`\code`) | `\code{}` for inline code (functions, commands, arguments, literal tokens) |  |  |
| jss.cls | 476 (`\proglang`) | `\proglang{}` for programming languages and programmable systems (defined as `\textsf`) |  |  |
| jss.cls | 477 (`\pkg`) | `\pkg{}` for software package names (medium-bold series) |  |  |
| jss.cls | 478 (`\email`) | `\email{}` for email addresses (generates `mailto:` link) |  |  |
| jss.cls | 480–483 (`\doi`) | `\doi{}` for DOIs (generates `https://doi.org/...` link) |  |  |
| jss.cls | 484 (`\E`) | `\E` math shortcut for expectation (`\mathsf{E}`) |  |  |
| jss.cls | 485 (`\VAR`) | `\VAR` math shortcut for variance |  |  |
| jss.cls | 486 (`\COV`) | `\COV` math shortcut for covariance |  |  |
| jss.cls | 487 (`\Prob`) | `\Prob` math shortcut for probability |  |  |
| jss.cls | 203 (`Sinput`) | `Sinput` environment defined (Sweave-style) |  |  |
| jss.cls | 204 (`Soutput`) | `Soutput` environment defined |  |  |
| jss.cls | 205 (`Scode`) | `Scode` environment defined |  |  |
| jss.cls | 206 (`Schunk`) | `Schunk` environment defined |  |  |
| jss.cls | 207 (`Code`) | `Code` verbatim environment (agnostic code listing) |  |  |
| jss.cls | 208 (`CodeInput`) | `CodeInput` environment (preferred for command-prompt inputs) |  |  |
| jss.cls | 209 (`CodeOutput`) | `CodeOutput` environment |  |  |
| jss.cls | 210 (`CodeChunk`) | `CodeChunk` wrapper environment |  |  |
| jss.cls | 211 (Gin width) | Default figure width set to 0.8\textwidth by `\setkeys{Gin}{width=0.8\textwidth}` |  |  |
| jss.cls | N/A | **`\dfn{}` is not defined in `jss.cls` v3.3** — the spec's scaffolding prompt listed it, but it must not be required by any rule unless vendored sources change (see §5 open questions) | — | out-of-scope |
| jss.cls | N/A | **`\file{}` is not defined in `jss.cls` v3.3** — same treatment as `\dfn{}` above (see §5 open questions) | — | out-of-scope |

### 1.2 `article.tex` — structural template provisions

Authority: `article_tex`. Structural rules should enforce the same section order and preamble pattern this template exhibits.

| source | anchor | provision | covering_rule_ids | status |
|---|---|---|---|---|
| article.tex | 1 | Document class is declared as `\documentclass[article]{jss}` (for ordinary articles) |  |  |
| article.tex | 6 | Recommended packages are `orcidlink`, `thumbpdf`, `lmodern` |  |  |
| article.tex | 12–13 (`\class`, `\fct`) | Authors MAY define article-local convenience macros (`\class`, `\fct`) that delegate to `\code{}` |  |  |
| article.tex | 22–23 (`\author`) | `\author{...}` uses `\And` or `\AND` to separate authors (not comma); inline `\orcidlink{...}` is permitted |  |  |
| article.tex | 24 (`\Plainauthor`) | `\Plainauthor{...}` separates authors by comma |  |  |
| article.tex | 29–31 (title block) | `\title{...}` (with markup), `\Plaintitle{...}` (no markup), and `\Shorttitle{...}` (with markup) all present |  |  |
| article.tex | 29 | `\title{}` uses **title case** (per style guide SG-007) |  |  |
| article.tex | 34–44 (`\Abstract`) | `\Abstract{...}` present before `\begin{document}` |  |  |
| article.tex | 49 (`\Keywords`) | `\Keywords{...}` is comma-separated and in sentence case (per SG and comment on line 48) |  |  |
| article.tex | 50 (`\Plainkeywords`) | `\Plainkeywords{...}` mirror of `\Keywords` without markup |  |  |
| article.tex | 57–68 (`\Address`) | `\Address{...}` contains author, affiliation, postal address, `\email{...}`, `\url{...}` |  |  |
| article.tex | 86 (`\section`) | First numbered section is Introduction; uses `\section[plain]{markup}` to separate bookmark/PDF title from markup title |  |  |
| article.tex | 86, 145, 247, 378 | Section labels follow the `sec:introname` convention (`sec:intro`, `sec:models`, `sec:illustrations`, `sec:summary`) |  |  |
| article.tex | 378 (summary) | Summary / discussion section is present |  |  |
| article.tex | 387 (`\section*`) | "Computational details" is an **unnumbered** section (`\section*{...}`) |  |  |
| article.tex | 404 (`\section*`) | "Acknowledgments" is an unnumbered section; **AE spelling** ("Acknowledgments", not "Acknowledgements") is normative (comment on line 407) |  |  |
| article.tex | 423 (`\bibliography`) | References are loaded via `\bibliography{refs}` (BibTeX) |  |  |
| article.tex | 430 (`\newpage`) | Appendix follows the bibliography after a page break |  |  |
| article.tex | 432–480 (appendix) | Appendix sections have proper titles (not just "Appendix"); labels use `app:name` convention |  |  |
| article.tex | 88–104 (markup usage) | `\proglang{}`, `\pkg{}`, `\code{}` markup is used throughout the manuscript body (including in section titles — with plain-text shim in the optional argument) |  |  |
| article.tex | 170–174 (`{Code}`) | `{Code}` environment used for code synopses that are not meant to be executed |  |  |
| article.tex | 289–317 (`{CodeChunk}`+`{CodeInput}`/`{CodeOutput}`) | `{CodeChunk}` wraps matching `{CodeInput}` / `{CodeOutput}` for executed code |  |  |
| article.tex | 291 (`R> ` prompt) | R code inputs use `R> ` as the prompt and `+  ` as the continuation prompt |  |  |
| article.tex | 154–156 (equation spacing) | `{equation}` environments have **no blank lines** before/after (blank lines are suppressed with `%` comments) |  |  |

### 1.3 Style guide — `https://www.jstatsoft.org/style`

Authority: `style_guide`. Fetched 2026-04-23. 60 normative directives enumerated.

Reviewer: mark directives that are **out of scope** for a static LaTeX linter (e.g., graphics pen-to-paper ratio, which requires rendering) as `out-of-scope` with a one-line rationale; the rest are coverage targets.

| source | anchor | provision | covering_rule_ids | status |
|---|---|---|---|---|
| style_guide | general-requirements | SG-001 MUST: All submissions are formatted using LaTeX and JSS style files |  |  |
| style_guide | general-requirements | SG-002 SHOULD: Keep LaTeX code as simple as possible; avoid unnecessary packages/commands |  |  |
| style_guide | latex-subsection | SG-003 SHOULD: Use pdfLaTeX to compile manuscripts to PDF |  |  |
| style_guide | #what-are-the-most-important-style-guidelines-in-jss | SG-004 MUST: Manuscript must be compilable by pdfLaTeX |  |  |
| style_guide | #what-are-the-most-important-style-guidelines-in-jss | SG-005 MUST: Use `\proglang`, `\pkg`, `\code` markup throughout the paper, including titles and references |  |  |
| style_guide | #what-are-the-most-important-style-guidelines-in-jss | SG-006 MUST: Provide references in a `.bib` BibTeX database; cite via `\cite`, `\citep`, `\citet`, etc. |  |  |
| style_guide | #what-are-the-most-important-style-guidelines-in-jss | SG-007 MUST: `\title` is in title style |  |  |
| style_guide | #what-are-the-most-important-style-guidelines-in-jss | SG-008 MUST: All titles in the BibTeX file are in title style |  |  |
| style_guide | #what-are-the-most-important-style-guidelines-in-jss | SG-009 MUST: `\section`, `\subsection`, etc. are in sentence style |  |  |
| style_guide | #what-are-the-most-important-style-guidelines-in-jss | SG-010 MUST: Figure/table captions (annotations) are in sentence style |  |  |
| style_guide | #what-are-the-most-important-style-guidelines-in-jss | SG-011 MUST: Figures, tables, and equations are marked with `\label` and referenced by `\ref` |  |  |
| style_guide | #what-are-the-most-important-style-guidelines-in-jss | SG-012 MUST: Software packages are cited via `\cite{}` |  |  |
| style_guide | #what-are-the-capitalization-rules-in-jss-what-is-title-style-and-sentence-style | SG-013 MUST: In sentence style, capitalise only the first word and the first word after colon/hyphen; proper names remain uppercase |  |  |
| style_guide | #what-are-the-capitalization-rules-in-jss-what-is-title-style-and-sentence-style | SG-014 MUST: In title style, capitalise all principal words; articles, coordinating conjunctions, and prepositions stay lowercase unless first/last |  |  |
| style_guide | #how-to-cite-software | SG-015 SHOULD: If software has a recommended citation, use it; otherwise cite the manual or webpage |  |  |
| style_guide | #how-to-cite-r-packages | SG-016 SHOULD: Check for official R package citation on CRAN or via `citation("pkg")`; otherwise use CRAN-style reference |  |  |
| style_guide | #how-to-cite-r-packages | SG-017 MUST: BibTeX is valid, title is in title style, `\proglang`/`\pkg`/`\code` markup used appropriately |  |  |
| style_guide | #what-are-the-different-cite-citet-citep-commands-about | SG-018 DO NOT: Use brackets-within-brackets constructs like `(\cite{...})` |  |  |
| style_guide | #how-should-abbrevations-be-formatted | SG-019 MUST: Spell abbreviations in upper-case letters without periods, small caps, italics, or additional formatting |  |  |
| style_guide | #how-should-abbrevations-be-formatted | SG-020 MUST: Introduce all abbreviations with expansion at first use; expansion is not capitalised unless it contains proper names or starts a sentence |  |  |
| style_guide | #how-to-format-figuretable-captions | SG-021 MUST: Captions appear below the corresponding figure/table |  |  |
| style_guide | #how-to-format-figuretable-captions | SG-022 MUST: Captions are in sentence style and end with a period |  |  |
| style_guide | #how-to-format-figuretable-captions | SG-023 DO NOT: Use additional formatting (`\emph`, `\bf`, `\it`) inside captions |  |  |
| style_guide | #how-to-format-figuretable-captions | SG-024 MUST: All table row/column headers are in sentence style |  |  |
| style_guide | #how-to-format-figuretable-captions | SG-025 DO NOT: Use footnote-style annotations in tables; annotations go in the caption |  |  |
| style_guide | #how-should-code-be-formatted-in-the-manuscript | SG-026 SHOULD: Present code in usual text flow with sufficient spaces for readability |  |  |
| style_guide | #how-should-code-be-formatted-in-the-manuscript | SG-027 SHOULD: Include spaces before/after operators and after commas in code (unless syntactically meaningful) |  |  |
| style_guide | #how-should-code-be-formatted-in-the-manuscript | SG-028 SHOULD: Apply consistent spacing to both inline and verbatim code |  |  |
| style_guide | #how-should-code-be-formatted-in-the-manuscript | SG-029 DO NOT: Include comments within verbatim code; place comments in normal LaTeX text |  |  |
| style_guide | #how-should-code-be-formatted-in-the-manuscript | SG-030 SHOULD: Use `\code{...}` for inline code chunks |  |  |
| style_guide | #how-should-code-be-formatted-in-the-manuscript | SG-031 MUST: Code input/output fits within normal textwidth |  |  |
| style_guide | #what-is-a-good-pen-to-paper-ratio-for-my-graphics | SG-032 MUST: Graphics are legible on paper and on screen |  |  |
| style_guide | #what-is-a-good-pen-to-paper-ratio-for-my-graphics | SG-033 SHOULD: Graphics annotations are about the size of the figure caption or slightly smaller |  |  |
| style_guide | #some-of-my-graphics-files-are-very-large-what-should-i-do | SG-034 SHOULD: If a vector graphic is large/slow, also supply a raster version (`.jpg`/`.png`) |  |  |
| style_guide | #some-of-my-graphics-files-are-very-large-what-should-i-do | SG-035 MUST: Annotations in raster graphics remain legible (no pixelation) |  |  |
| style_guide | #how-should-my-r-package-reflect-that-a-manuscript-about-it-was-published-in-jss | SG-036 SHOULD: Include the JSS paper in `\references{}` of relevant `.Rd` pages |  |  |
| style_guide | #how-should-my-r-package-reflect-that-a-manuscript-about-it-was-published-in-jss | SG-037 SHOULD: Include `CITATION` file at `inst/CITATION` within the R package |  |  |
| style_guide | #how-should-my-r-package-reflect-that-a-manuscript-about-it-was-published-in-jss | SG-038 SHOULD: Turn the JSS manuscript into a package vignette |  |  |
| style_guide | #how-can-i-turn-my-jss-paper-into-an-r-package-vignette | SG-039 SHOULD: Use the JSS paper as the basis for the vignette |  |  |
| style_guide | #how-can-i-turn-my-jss-paper-into-an-r-package-vignette | SG-040 SHOULD: Use Sweave-style code chunks for inputs/outputs/graphics in the vignette |  |  |
| style_guide | #how-can-i-turn-my-jss-paper-into-an-r-package-vignette | SG-041 SHOULD: Use `\documentclass[nojss]{jss}` to turn off JSS header/footer in the vignette |  |  |
| style_guide | #how-can-i-turn-my-jss-paper-into-an-r-package-vignette | SG-042 SHOULD: Cite the JSS paper in the vignette abstract or introduction |  |  |
| style_guide | #how-can-i-turn-my-jss-paper-into-an-r-package-vignette | SG-043 SHOULD (advisory): Set `options(prompt = "R> ", continue = "+  ", width = 70, useFancyQuotes = FALSE)` invisibly at the start of the vignette |  |  |
| style_guide | #which-naming-conventions-are-used-for-software-journal-and-publisher-names-in-jss | SG-044 MUST: "Fortran" not "FORTRAN" |  |  |
| style_guide | #which-naming-conventions-are-used-for-software-journal-and-publisher-names-in-jss | SG-045 MUST: "Java" not "JAVA" / "java" |  |  |
| style_guide | #which-naming-conventions-are-used-for-software-journal-and-publisher-names-in-jss | SG-046 MUST: "MATLAB" not "Matlab" / "matlab" |  |  |
| style_guide | #which-naming-conventions-are-used-for-software-journal-and-publisher-names-in-jss | SG-047 MUST: "S-PLUS" not "Splus" / "S-Plus" |  |  |
| style_guide | #which-naming-conventions-are-used-for-software-journal-and-publisher-names-in-jss | SG-048 MUST: "The American Statistician" (with the article) |  |  |
| style_guide | #which-naming-conventions-are-used-for-software-journal-and-publisher-names-in-jss | SG-049 MUST: "The Annals of Statistics" (with the article) |  |  |
| style_guide | #which-naming-conventions-are-used-for-software-journal-and-publisher-names-in-jss | SG-050 MUST: "Journal of the Royal Statistical Society B" (not "..., Series B") |  |  |
| style_guide | #which-naming-conventions-are-used-for-software-journal-and-publisher-names-in-jss | SG-051 MUST: "Springer-Verlag" (not "Springer") |  |  |
| style_guide | #which-naming-conventions-are-used-for-software-journal-and-publisher-names-in-jss | SG-052 MUST: "John Wiley & Sons" (not "Wiley" / "John Wiley & Sons Inc.") |  |  |
| style_guide | #my-latex-paper-does-not-compile-when-there-is-jss-markup-in-section-titles-what-should-i-do | SG-053 SHOULD: Section titles containing markup supply a plain-text shim via `\section[plain]{markup}` for PDF bookmarks |  |  |
| style_guide | #miscellaneous | SG-054 MUST: Use "Section x.y" (not "Subsection x.y") when referring to subsections |  |  |
| style_guide | #miscellaneous | SG-055 MUST: "e.g.", "i.e." are followed by a comma to prevent LaTeX from interpreting the period as a sentence end |  |  |
| style_guide | #miscellaneous | SG-056 MUST: "$p$~value", "$t$~statistic", etc. have no hyphen and a tie `~` between symbol and noun |  |  |
| style_guide | #miscellaneous | SG-057 MUST: Use `\top` (not `'` or `T`) for the transpose symbol (`X^\top`) |  |  |
| style_guide | #miscellaneous | SG-058 MUST: In R-related manuscripts, first argument of `data()` and `library()` is quoted (`library("foo")`) |  |  |
| style_guide | #miscellaneous | SG-059 MUST: Book editions are indicated as 2nd, 3rd, …  |  |  |
| style_guide | #miscellaneous | SG-060 SHOULD: Prefer `Equation~\ref{...}` (capitalised) over bare `(\ref{...})` when referring to equations, except when reference count is large |  |  |

### 1.4 Author instructions — `https://www.jstatsoft.org/authors` (§ Manuscript preparation et seq.)

Authority: `author_instructions`. Fetched 2026-04-23. 22 directives enumerated. Many are submission-process rules (PDF upload, file-size limits, GPL licensing) that cannot be checked from a `.tex`/`.bib` source and are therefore `out-of-scope` for the linter — mark them explicitly so the reviewer knows they were read and considered rather than missed.

| source | anchor | provision | covering_rule_ids | status |
|---|---|---|---|---|
| author_instructions | manuscript-preparation | AI-001 MUST: Manuscripts are written in English using LaTeX |  |  |
| author_instructions | manuscript-preparation | AI-002 MUST: JSS Style Guide is followed (delegates to §1.3) |  |  |
| author_instructions | manuscript-preparation | AI-003 MUST: Only PDF files can be submitted (submission format — not linter-checkable from `.tex`) | — | out-of-scope |
| author_instructions | manuscript-preparation | AI-004 Implicit: Authors are responsible for appropriate format (meta-rule — delegates to the other rules) | — | out-of-scope |
| author_instructions | manuscript-preparation | AI-005 Implicit: Non-compliant manuscripts are returned (meta-consequence, not a lint rule) | — | out-of-scope |
| author_instructions | manuscript-preparation | AI-006 SHOULD (advisory): Find a local LaTeX expert for assistance (meta-advice) | — | out-of-scope |
| author_instructions | manuscript-preparation | AI-007 NOTE: Manuscripts over 30 pages have longer review times (informational, not normative) | — | out-of-scope |
| author_instructions | manuscript-preparation | AI-008 MUST: All figures, tables, and output are fully reproducible on ≥1 platform (cannot be verified from `.tex` alone) | — | out-of-scope |
| author_instructions | manuscript-preparation | AI-009 MUST: Platform dependencies indicated with the submission (submission metadata) | — | out-of-scope |
| author_instructions | manuscript-preparation | AI-010 MUST: Random seed initialised when results depend on simulation |  |  |
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

Flat list of every proposed rule in `catalogue.yaml`. Populated from the data file after the draft lands. Reviewer fills `reviewer_note` for every row with one of: `approve | merge-with-<id> | split | drop | defer | needs-more-context`.

| rule_id | category | description (one line) | authority | authority_ref | severity | reviewer_note |
|---|---|---|---|---|---|---|
| *(populate from `catalogue.yaml` before review)* |  |  |  |  |  |  |

### How to populate

1. `yq '.rules[] | [.rule_id, .category, .description, .authority, .authority_ref, .severity] | @tsv' catalogue.yaml` (or the TOML/JSON equivalent once the format is pinned in `/speckit.plan`).
2. Paste into this table.
3. Fill `reviewer_note` per row.
4. Every row must have a non-empty `reviewer_note` before sign-off.

---

## 3. Category sanity checks

- [ ] CHK001 The category set in `catalogue.yaml` matches the list in `spec.md` FR-005 (or a deliberate deviation is recorded with a rationale in `catalogue.yaml`'s header).
- [ ] CHK002 Per-category rule counts — record counts below; flag any category with ≥2× the median count (possibly over-split) or ≤⅓ of the median (possibly a candidate for merging into a sibling).

  | category | rule count | flag? |
  |---|---|---|
  | *(populate)* |  |  |

- [ ] CHK003 Rule-ID counter sequence is contiguous within each category (no gaps, no collisions). A gap is acceptable **only** if the rule at that id was retired and the id is permanently reserved — note the retirement in the rule's `notes` field and explain in this checklist.
- [ ] CHK004 No `rule_id` appears in more than one category entry.
- [ ] CHK005 No two rules in the same category have materially duplicated `description`s (reviewer read). If two rule descriptions collapse to the same check, apply edge case 2 from spec.md (merge into the higher-authority home).
- [ ] CHK006 Every category that FR-017 names (`citations`, `references`, `typography`, `capitalization`) has at least one rule, and the ordering in `tasks.md` puts `citations`/`references` first and `typography`/`capitalization` last.
- [ ] CHK007 The full category list is pinned in `catalogue.yaml`'s header (FR-005) — no implicit categorisation.

---

## 4. Severity consistency

- [ ] CHK008 Group rules by severity (run `yq '.rules | group_by(.severity) | ...'` or equivalent). Fill the tally:

  | severity | count |
  |---|---|
  | error |  |
  | warning |  |
  | info |  |

- [ ] CHK009 Every `error`-severity rule is objectively wrong (missing preamble macro, malformed citation, undefined cross-reference, class option violation). Re-read each one and confirm it is not a stylistic judgement call.
- [ ] CHK010 Every `warning`-severity rule is a stylistic judgement (capitalisation, code spacing, typographic dash, narrow naming convention). Re-read each one and confirm it is not something the journal would outright reject.
- [ ] CHK011 Within each **tight semantic cluster** (all citation rules, all capitalisation rules, all code-width rules), severities are uniform — or the non-uniform rule has a `notes` entry explaining why. Mixed severity inside a cluster is a red flag; confirm or resolve each instance.

  | cluster | rules in cluster | severities in use | uniform? |
  |---|---|---|---|
  | *(populate)* |  |  |  |

- [ ] CHK012 No `info`-severity rule is enforcing a MUST directive from §1.3 (style guide) — `info` for a MUST is a tacit downgrade and should be challenged.

---

## 5. Open questions for reviewer

Items `/speckit.clarify` could not auto-resolve, or that surfaced during catalogue drafting and require human judgment. Every item must be closed (answered or deferred with rationale) before sign-off.

### Vendoring-versus-scaffolding discrepancies

- [ ] OQ-01 **`\dfn{}` is not defined in `jss.cls` v3.3** despite being listed in the feature-scaffolding prompt. Confirm: no rule requires `\dfn{}`. If authors have been using `\dfn{}` from a different class version, decide whether to (a) treat it as out of scope permanently, (b) flag it as an author-side macro the linter ignores, or (c) re-check upstream for a newer `jss.cls` release that defines it.
- [ ] OQ-02 **`\file{}` is not defined in `jss.cls` v3.3** — same disposition question as OQ-01. The catalogue must not assume `\file{}` exists.

### Authority-weak / authority-ambiguous rules

- [ ] OQ-03 Rules whose only authority citation is inferred convention (no resolvable anchor in any of the four sources). List them below. For each, either ground in an authority or drop:

  | candidate rule_id | what the rule checks | reason for inferred-convention status | disposition |
  |---|---|---|---|
  | *(populate)* |  |  |  |

- [ ] OQ-04 Rules that cite two authorities simultaneously without a higher-authority conflict marker. Re-verify each one pins to `jss_cls > article_tex > style_guide > author_instructions` (FR-003) and records the losing source in `notes`.

### Category boundary edge cases

- [ ] OQ-05 Any rule that plausibly fits two categories, and the current placement is not obvious from §1.3 language (e.g., a `\code{}`-in-captions rule — `markup` or `typography`?). List ambiguous placements and confirm each.
- [ ] OQ-06 `references` vs `bibtex` boundary: every rule in `bibtex` is a **mechanical** check (syntax, required keys, malformed fields); every rule in `references` is a **content** check (DOI presence, title case, author-name form). Re-verify with the definition in spec.md Assumptions.

### Precision-gate candidates before corpus data exists

- [ ] OQ-07 Rules suspected to have low precision on the corpus **before any labelled data exists** (e.g., rules that match on substring patterns, rules whose synthetic-fixture precision is already < 100%, rules that depend on English morphology). List them so the implementation order weights them later:

  | candidate rule_id | why suspect | tightening candidate |
  |---|---|---|
  | *(populate)* |  |  |

### Redundancy / collapse candidates

- [ ] OQ-08 Any two rules that fire on the exact same violation (e.g., `JSS-CAP-NNN` and `JSS-HOUSE-MMM` both flag lowercase `r` in prose). Decide: merge, split by context, or keep (document why the redundancy is intentional).
- [ ] OQ-09 Any authority provision (§1.1–1.4) that is matched by **>1 rule** where the rules differ only by category — confirm the split is meaningful, not bureaucratic.

### Scope / target reality checks

- [ ] OQ-10 Total rule count is within an order-of-magnitude of the planning anchor (~50). If the count is **< 25** or **> 100**, per `spec.md` Assumptions, that is a signal worth a second clarify pass before sign-off.
- [ ] OQ-11 Corpus has grown toward the ~50-paper target that the N=10 precision-gate floor assumes (`spec.md` Clarifications, Assumptions). If the corpus is still near 10 papers, the gate is effectively advisory and that should be noted explicitly in the sign-off below.
- [ ] OQ-12 Style-guide SG-032 through SG-035 (graphics readability / pen-to-paper ratio) and SG-036 through SG-043 (`.Rnw` vignette advice): confirm each is marked `out-of-scope` in §1.3 with a one-line rationale. The linter cannot render graphics, and `.Rnw` is deferred to Step 4 per FR-021.

### Authority-ref resolvability

- [ ] OQ-13 For every rule whose `authority` is `article_tex` or `jss_cls`, the `authority_ref` resolves against `docs/jss-template/` **at the current commit**. CI enforces this (FR-008, SC-002), but the reviewer spot-checks a random sample of five rows to confirm the CI test is not fooled by a superficial line-number match.
- [ ] OQ-14 For every rule whose `authority` is `style_guide` or `author_instructions`, the `authority_ref` points to a section/heading anchor (not a paragraph ordinal), matching FR-010. The anchors in §1.3 and §1.4 above (the `#section-id` values) are the canonical forms to use.

---

## Sign-off

- [ ] Every row in §1.1–1.4 has a non-empty `status` (covered | gap | redundant | out-of-scope).
- [ ] Every rule row in §2 has a non-empty `reviewer_note`.
- [ ] All §3 category sanity items (CHK001–CHK007) are checked.
- [ ] All §4 severity consistency items (CHK008–CHK012) are checked.
- [ ] All §5 open questions are closed (answered or explicitly deferred with rationale).
- [ ] Any gap (`status = gap`) is either (a) closed by adding a rule, or (b) re-classified as `out-of-scope` with rationale.
- [ ] Any redundancy (`status = redundant`) is either (a) closed by merging/dropping one rule, or (b) justified in the rule's `notes` field.

**Reviewer**: _____________  **Date**: _____________  **Commit**: _____________

**Approval**: this file is committed with all items checked. The catalogue is cleared for the per-category rollout loop (spec.md FR-015–FR-020).
