test_that("jsslintr::render matches the real jss-lint CLI", {
  repo_root <- normalizePath(file.path(testthat::test_path(), "..", "..", "..", ".."))
  jss_lint <- file.path(repo_root, ".venv", "bin", "jss-lint")
  skip_if_not(file.exists(jss_lint), "Python venv not set up")

  paper_dir <- file.path(repo_root, "eval", "recall-corpus", "opentsne")
  tex_path <- file.path(paper_dir, "main.tex")
  bib_path <- file.path(paper_dir, "references.bib")

  read_file <- function(path) {
    readChar(path, file.info(path)$size, useBytes = TRUE)
  }
  # File labels ("main.tex"/"references.bib") must match exactly what
  # the Python oracle below uses (invoked with cwd = paper_dir and
  # bare filenames) — Violation$file is a verbatim echo of whichever
  # label the caller passes in, on both sides.
  files <- c(
    "main.tex" = read_file(tex_path),
    "references.bib" = read_file(bib_path)
  )

  actual <- jsslintr::render(files, output = "json")

  old_wd <- setwd(paper_dir)
  on.exit(setwd(old_wd))
  # jss-lint legitimately exits 1 when it finds violations (this paper
  # has plenty) — that's not a test failure, so suppress system2()'s
  # "had status 1" warning rather than let it leak into test output.
  py_lines <- suppressWarnings(system2(
    jss_lint,
    c("--output", "json", "main.tex", "references.bib"),
    stdout = TRUE
  ))
  expected <- paste0(paste(py_lines, collapse = "\n"), "\n")

  expect_identical(actual, expected)
})

test_that("jsslintr::render errors cleanly on a malformed files argument", {
  expect_error(jsslintr::render(c("not-named-value")))
})
