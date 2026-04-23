# `placeholder_parse_failure` — smoke vignette, 1 x JSS-PARSE-000

Placeholder vignette with a deliberately malformed LaTeX body (an
unclosed `itemize` environment). Exercises the parse-failure code path
(`JSS-PARSE-000`) end-to-end, confirming that parse regressions
surface as their own rows in `eval-jss report` rather than silently
tanking unrelated rules' precision (spec FR-021).

**Source**: hand-authored placeholder. Exists to keep the parse-failure
row in the report even as other placeholders are replaced with real
CRAN vignettes.
