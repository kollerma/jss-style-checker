# Unlike test-parity.R these tests need no Python venv or recall
# corpus: they lint a small synthetic paper written to a temp dir.
# The fixture deliberately triggers both fixable rules (JSS-MARKUP-001
# R -> \proglang{R}, JSS-HOUSE-001 e.g. -> e.g.,) and unfixable ones
# (JSS-CAP-002 section title casing).

write_fixture <- function(dir = tempfile("jsslint-fixture-")) {
  dir.create(dir)
  writeLines(
    c(
      "\\documentclass[nojss]{jss}",
      "\\author{Jane Doe}",
      "\\title{A Package for Doing Things}",
      "\\Abstract{We present a package for R that does things, e.g. plotting.}",
      "\\Keywords{stuff, things}",
      "\\begin{document}",
      "\\section{Methods And Results}",
      "We use R for everything.",
      "\\end{document}"
    ),
    file.path(dir, "paper.tex")
  )
  writeLines(
    c(
      "@article{smith2020,",
      "  author = {John Smith},",
      "  title = {Some Methods for Data},",
      "  journal = {Journal of Statistical Software},",
      "  year = {2020},",
      "  volume = {95},",
      "  pages = {1--20}",
      "}"
    ),
    file.path(dir, "refs.bib")
  )
  file.path(dir, c("paper.tex", "refs.bib"))
}

test_that("jsslint returns a structured jsslint object", {
  files <- write_fixture()
  on.exit(unlink(dirname(files[[1]]), recursive = TRUE))

  res <- jsslint(files)

  expect_s3_class(res, "jsslint")
  expect_identical(res$files, files)
  expect_true(is.data.frame(res$violations))
  expect_true(all(
    c(
      "file", "line", "column", "rule_id", "severity", "message",
      "suggestion", "fixable", "fix_description", "fix_confidence",
      "guide_section", "confidence"
    ) %in% names(res$violations)
  ))
  expect_true("JSS-MARKUP-001" %in% res$violations$rule_id)
  expect_true("JSS-CAP-002" %in% res$violations$rule_id)
  expect_true(any(res$violations$fixable))
  expect_true(is.numeric(res$compliance))
  expect_identical(res$journal_id, "jss")
  expect_true(is.data.frame(res$categories))
  expect_gt(nrow(res$categories), 0)
})

test_that("printing a jsslint object gives a summary plus issue lines", {
  files <- write_fixture()
  on.exit(unlink(dirname(files[[1]]), recursive = TRUE))

  res <- jsslint(files)
  out <- capture.output(print(res))

  expect_match(out[[1]], "^JSS style check")
  expect_true(any(grepl("Compliance:", out)))
  expect_true(any(grepl("auto-fixable", out)))
  expect_true(any(grepl("JSS-MARKUP-001", out)))
  expect_true(any(grepl("jssfix\\(\\)", out)))

  # Truncation kicks in when there are more issues than `max`.
  out_short <- capture.output(print(res, max = 1))
  expect_true(any(grepl("more issue", out_short)))
  expect_length(grep("\\[(error|warning|info)\\]", out_short), 1L)
})

test_that("summary breaks issues down by rule, file, and category", {
  files <- write_fixture()
  on.exit(unlink(dirname(files[[1]]), recursive = TRUE))

  res <- jsslint(files)
  s <- summary(res)

  expect_s3_class(s, "summary.jsslint")
  expect_true(is.data.frame(s$by_rule))
  expect_true("JSS-MARKUP-001" %in% s$by_rule$rule_id)
  # by_rule is sorted by descending issue count
  expect_false(is.unsorted(rev(s$by_rule$issues)))
  # every linted file appears in by_file, even issue-free ones
  expect_setequal(s$by_file$file, files)

  out <- capture.output(print(s))
  expect_true(any(grepl("Issues by rule:", out)))
  expect_true(any(grepl("Categories:", out)))
})

test_that("as.data.frame returns one row per issue", {
  files <- write_fixture()
  on.exit(unlink(dirname(files[[1]]), recursive = TRUE))

  res <- jsslint(files)
  df <- as.data.frame(res)
  expect_identical(df, res$violations)
})

test_that("jsslint errors on missing files and empty input", {
  expect_error(jsslint("does-not-exist.tex"), "file not found")
  expect_error(jsslint(character(0)), "character vector")
})

test_that("jssfix dry run shows a diff but writes nothing", {
  files <- write_fixture()
  on.exit(unlink(dirname(files[[1]]), recursive = TRUE))
  before <- readLines(files[[1]])

  out <- capture.output(fixes <- jssfix(files, dry_run = TRUE))

  expect_s3_class(fixes, "jsslint_fixes")
  expect_true(fixes$dry_run)
  expect_gt(nrow(fixes$applied), 0)
  expect_true(any(grepl("^\\+.*\\\\proglang\\{R\\}", out)))
  expect_true(any(grepl("Dry run:", out)))
  expect_identical(readLines(files[[1]]), before)
})

test_that("jssfix applies fixes in place and the re-lint improves", {
  files <- write_fixture()
  on.exit(unlink(dirname(files[[1]]), recursive = TRUE))

  before <- jsslint(files)
  n_fixable <- sum(before$violations$fixable)
  expect_gt(n_fixable, 0)

  out <- capture.output(fixes <- jssfix(before))

  expect_false(fixes$dry_run)
  expect_identical(nrow(fixes$applied), n_fixable)
  expect_true(any(grepl("^Applied", out)))
  expect_true(any(grepl("\\\\proglang\\{R\\}", readLines(files[[1]]))))

  after <- jsslint(files)
  expect_identical(sum(after$violations$fixable), 0L)
  expect_lt(nrow(after$violations), nrow(before$violations))
})

test_that("jssfix honours the rules filter", {
  files <- write_fixture()
  on.exit(unlink(dirname(files[[1]]), recursive = TRUE))

  capture.output(
    fixes <- jssfix(files, rules = "JSS-HOUSE-001")
  )

  expect_identical(unique(fixes$applied$rule_id), "JSS-HOUSE-001")
  expect_true("rule-not-selected" %in% fixes$skipped$reason)
  # The unselected MARKUP-001 fixes must not have been applied.
  expect_false(any(grepl("\\\\proglang", readLines(files[[1]]))))
  expect_true(any(grepl("e\\.g\\.,", readLines(files[[1]]))))
})
