# JSS papers with manuscript sources available outside CRAN

Goal: find ≥20 JSS papers whose LaTeX/Rnw manuscript **source** is hosted
somewhere other than a CRAN tarball, preferring standalone `.tex`
manuscripts over shipped R vignettes.

Method: started from the most recently published non-R-software JSS papers
(Python/Julia/Stata/SAS/MATLAB — these can't be on CRAN), then pivoted to a
GitHub code search for standalone `\documentclass{jss}` manuscripts in
`paper/` / `manuscript/` directories. Each entry below was verified by
reading the file's documentclass line and/or `\Plaintitle` via GitHub code
search (fragments include `\documentclass[...]{jss}`).

Key finding: pure non-R software packages (Bambi, scikit-mobility,
DataFrames.jl, Pathogen.jl, pyStoNED, pyrichlet, MIDASpy, panelView, …)
almost never commit their JSS manuscript `.tex`; they ship only a compiled
PDF and keep replication code, with the source living in the gated JSS
supplement archive. The productive vein is repos that keep a `paper/` or
`manuscript/` directory — both R and non-R.

## Tier 1 — Published JSS, standalone source on GitHub, NOT a CRAN vignette

| DOI | Title / software | Lang | Repo | Source path |
|---|---|---|---|---|
| 10.18637/jss.v110.i02 | An Extendable Python Implementation of Robust Optimization Monte Carlo | Python | givasile/ROMC-SW | `jss-camera-ready/jss4678.tex` |
| 10.18637/jss.v112.i06 | TrueSkill Through Time | Julia/Python/R | glandfried/TrueSkillThroughTime | `doc/article.tex` |
| 10.18637/jss.v109.i03 | openTSNE | Python | pavlin-policar/opentsne-paper | `paper/main.tex` |
| 10.18637/jss.v086.i07 | DNest4: Diffusive Nested Sampling | C++/Python | eggplantbren/DNest4 | `paper/ms.tex` |
| 10.18637/jss.v109.i08 | Generalized Plackett-Luce Likelihoods (hyper2) | R | RobinHankin/hyper2 | `inst/jss_hyper3.Rnw` |
| 10.18637/jss.v087.i09 | Predictor Effects (partial residuals; effects) | R | r-forge/effects | `articles/PartialRes/final/jss2627.Rnw` |
| 10.18637/jss.v055.i07 | The RAppArmor Package | R | jeroen/RAppArmor | `paper/v55i07.Rnw` (+`content.tex`) |
| 10.18637/jss.v053.i01 | animation | R | yihui/animation | `inst/articles/jss725.Rnw` |
| 10.18637/jss.v023.i08 | gap: Genetic Analysis Package | R | jinghuazhao/tests | `gap/jss/jss.Rnw` |

## Tier 1b — Published JSS, source on GitHub but in a vignette path

| DOI | Title / software | Lang | Repo | Source path |
|---|---|---|---|---|
| 10.18637/jss.v096.i04 | LocalControl | R | OHDSI/LocalControl | `inst/vignette-source/LocalControl-jss-2020.Rnw` |
| 10.18637/jss.v063.i05 | plotKML | R | Envirometrix/plotKML | `vignettes/jss1079.Rnw` |
| (subm. jss2711) | recmap: Rectangular Statistical Cartograms | R/C++ | cpanse/recmap | `vignettes/jss2711.Rnw` |

## Tier 2 — JSS-format manuscripts on GitHub, accepted/in-press

(JSS submission-number filenames; not yet in the cached OAI archive.)

| Submission | Title / software | Repo | Source path |
|---|---|---|---|
| jss5097 | accumulate | markvanderloo/accumulate | `paper/jss5097.Rnw` |
| jss5342 | confintROB (robust LMM confidence intervals) | kollerma/confintROB-paper | `jss5342.Rnw` |
| (jss) | citest / citestR (Robinson & Lall) | MIDASverse/citest | `jss_paper/paper.tex` |

## Tier 3 — Standalone JSS-class manuscripts on GitHub (publication unconfirmed)

Useful as JSS-format corpus material; verify acceptance before treating as
"published".

| Title / software | Repo | Source path |
|---|---|---|
| peppwR | TeamMacLean/peppwR | `paper/jss-article.tex` (also `.Rnw`) |
| bioLeak | selcukorkmaz/bioLeak | `paper/manuscript_jss.tex` |
| CausalMixGPD | arnabaich96/CausalMixGPD | `manuscript/CausalMixGPD_JSS_article.tex` |
| multilevel mice | hanneoberman/multilevelmice | `Manuscript/manuscript.tex` |
| funres | bgreenwell/funres | `manuscript/manuscript.tex` |
| capnet | harryziyuhe/capnet | `manuscript/main.tex` |
| jsonlite (JSS class; published on arXiv, not JSS) | jeroen/jsonlite | `paper/article.Rnw` |

## Non-R software JSS papers with NO public manuscript source (PDF/supplement only)

Software repos exist but host only compiled PDF + replication code, not the
`.tex`: NUBO, StepMix, StatisticalProcessMonitoring.jl, pymle, dame-flame,
pyrichlet, pyStoNED, BirDePy, Extremes.jl, scikit-fda, salmon, MIDASpy/rMIDAS,
panelView/panelview, ARCHModels.jl, DataFrames.jl, jumpdiff, Pathogen.jl,
Bambi, HighFrequencyCovariance, scikit-mobility, GaussianProcesses.jl,
JuliaConnectoR, DEAMATLAB, marginaleffects, plus the Stata/SAS papers
(ldvqreg, spxtivdfreg, SURVEYHLM).
