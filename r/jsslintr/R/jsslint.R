# User-facing convenience layer over the extendr entry points in
# R/extendr-wrappers.R. `render()` is the bare in-memory binding
# (named vector of path = contents); everything here is the "hand it a
# paper" workflow: jsslint() reads the files and returns a "jsslint"
# object with print/summary/as.data.frame methods, jssfix() applies
# the auto-fixes on disk.

`%||%` <- function(x, y) if (is.null(x)) y else x

count_word <- function(n, singular, plural = paste0(singular, "s")) {
  paste(n, if (n == 1) singular else plural)
}

collapse_rules <- function(rules) {
  if (is.null(rules)) NULL else paste(rules, collapse = ",")
}

# The extendr layer hands each table over as a named list of parallel
# vectors; zero-length columns give the expected 0-row data frame.
list_to_df <- function(x) {
  as.data.frame(x, stringsAsFactors = FALSE)
}

read_sources <- function(files) {
  if (!is.character(files) || length(files) == 0) {
    stop("`files` must be a character vector of .tex/.ltx/.bib file paths",
      call. = FALSE
    )
  }
  missing <- files[!file.exists(files)]
  if (length(missing) > 0) {
    stop("file not found: ", paste(missing, collapse = ", "), call. = FALSE)
  }
  contents <- vapply(
    files,
    function(path) {
      txt <- readChar(path, file.info(path)$size, useBytes = TRUE)
      Encoding(txt) <- "UTF-8"
      txt
    },
    character(1)
  )
  names(contents) <- files
  contents
}

severity_phrase <- function(severity) {
  counts <- table(factor(severity, levels = c("error", "warning", "info")))
  parts <- c(
    if (counts[["error"]] > 0) count_word(counts[["error"]], "error"),
    if (counts[["warning"]] > 0) count_word(counts[["warning"]], "warning"),
    if (counts[["info"]] > 0) paste(counts[["info"]], "info")
  )
  paste(parts, collapse = ", ")
}

#' Find manuscript files for a JSS style check
#'
#' Lists the `.tex`, `.ltx`, and `.bib` files in a directory -- the
#' file set [jsslint()] checks when called without arguments.
#'
#' @param path Directory to search (default: the working directory).
#' @return A character vector of file paths.
#' @export
jss_files <- function(path = ".") {
  list.files(path,
    pattern = "\\.(tex|ltx|bib)$", ignore.case = TRUE,
    full.names = !identical(path, ".")
  )
}

#' Check a paper against the JSS style guide
#'
#' Reads the given manuscript files and lints them against the Journal
#' of Statistical Software style guide. This is the main entry point
#' for interactive use; [render()] is the lower-level in-memory
#' binding it wraps.
#'
#' @param files Character vector of paths to `.tex`/`.ltx` and `.bib`
#'   files, e.g. `c("paper.tex", "refs.bib")`. Defaults to every such
#'   file in the working directory.
#' @param journal Journal identifier (default: `"jss"`).
#' @param mode `"author"` or `"reviewer"` (default: `"author"`).
#' @param ignore_rules Character vector of rule ids to suppress.
#' @param min_confidence `"low"`, `"medium"`, or `"high"`.
#' @param verbose Enable diagnostic output on stderr.
#' @return An object of class `"jsslint"`. Print it for a quick
#'   overview, use [summary()] for a by-rule and by-category
#'   breakdown, and [as.data.frame()] for one row per issue. Pass it
#'   to [jssfix()] to apply the automatic fixes.
#' @examples
#' \dontrun{
#' res <- jsslint(c("paper.tex", "refs.bib"))
#' res
#' summary(res)
#' as.data.frame(res)
#' jssfix(res)
#' }
#' @export
jsslint <- function(files = jss_files(), journal = NULL, mode = NULL,
                    ignore_rules = NULL, min_confidence = NULL,
                    verbose = NULL) {
  sources <- read_sources(files)
  raw <- lint_data(sources,
    journal = journal, mode = mode,
    ignore_rules = collapse_rules(ignore_rules),
    min_confidence = min_confidence, verbose = verbose
  )
  structure(
    list(
      files = files,
      violations = list_to_df(raw$violations),
      categories = list_to_df(raw$categories),
      skipped_rules = list_to_df(raw$skipped_rules),
      compliance = raw$compliance_percentage %||% NA_real_,
      journal_id = raw$journal_id,
      tool_version = raw$tool_version,
      options = list(
        journal = journal, mode = mode, ignore_rules = ignore_rules,
        min_confidence = min_confidence
      )
    ),
    class = "jsslint"
  )
}

#' @export
print.jsslint <- function(x, max = getOption("jsslintr.print_max", 20L), ...) {
  v <- x$violations
  n <- nrow(v)

  cat("JSS style check (journal \"", x$journal_id, "\"): ",
    paste(x$files, collapse = ", "), "\n",
    sep = ""
  )
  if (!is.na(x$compliance)) {
    cat("Compliance: ", formatC(x$compliance, format = "f", digits = 1),
      "%\n",
      sep = ""
    )
  }

  if (n == 0) {
    cat("\nNo style issues found.\n")
    return(invisible(x))
  }

  n_fixable <- sum(v$fixable)
  cat("\n", count_word(n, "issue"), " (", severity_phrase(v$severity),
    "; ", n_fixable, " auto-fixable)\n\n",
    sep = ""
  )

  shown <- v[seq_len(min(n, max)), , drop = FALSE]
  loc <- paste0(
    shown$file, ":", shown$line,
    ifelse(is.na(shown$column), "", paste0(":", shown$column))
  )
  cat(
    paste0(
      format(loc), " ", format(paste0("[", shown$severity, "]")), " ",
      format(shown$rule_id), " ", shown$message
    ),
    sep = "\n"
  )
  if (n > nrow(shown)) {
    cat("... and ", count_word(n - nrow(shown), "more issue"),
      "; see as.data.frame() or print(x, max = Inf).\n",
      sep = ""
    )
  }

  cat("\nUse summary() for a breakdown by rule and category")
  if (n_fixable > 0) {
    cat(", and jssfix() to apply the ", count_word(n_fixable, "automatic fix", "automatic fixes"), sep = "")
  }
  cat(".\n")
  invisible(x)
}

#' @export
summary.jsslint <- function(object, ...) {
  v <- object$violations

  by_rule <- if (nrow(v) > 0) {
    sp <- split(v, v$rule_id)
    df <- data.frame(
      rule_id = names(sp),
      severity = vapply(sp, function(d) d$severity[[1]], character(1)),
      issues = vapply(sp, nrow, integer(1)),
      fixable = vapply(sp, function(d) sum(d$fixable), integer(1)),
      guide_section = vapply(sp, function(d) d$guide_section[[1]], character(1)),
      stringsAsFactors = FALSE, row.names = NULL
    )
    df[order(-df$issues, df$rule_id), , drop = FALSE]
  } else {
    data.frame(
      rule_id = character(0), severity = character(0),
      issues = integer(0), fixable = integer(0),
      guide_section = character(0), stringsAsFactors = FALSE
    )
  }

  tab <- table(
    factor(v$file, levels = object$files),
    factor(v$severity, levels = c("error", "warning", "info"))
  )
  by_file <- data.frame(
    file = rownames(tab),
    error = as.integer(tab[, "error"]),
    warning = as.integer(tab[, "warning"]),
    info = as.integer(tab[, "info"]),
    total = as.integer(rowSums(tab)),
    stringsAsFactors = FALSE, row.names = NULL
  )

  structure(
    list(check = object, by_rule = by_rule, by_file = by_file),
    class = "summary.jsslint"
  )
}

#' @export
print.summary.jsslint <- function(x, ...) {
  check <- x$check
  v <- check$violations

  cat("JSS style check (journal \"", check$journal_id, "\"): ",
    paste(check$files, collapse = ", "), "\n",
    sep = ""
  )
  if (!is.na(check$compliance)) {
    cat("Compliance: ", formatC(check$compliance, format = "f", digits = 1),
      "%",
      sep = ""
    )
    if (nrow(v) > 0) {
      cat(" -- ", count_word(nrow(v), "issue"), " (",
        severity_phrase(v$severity), "; ", sum(v$fixable),
        " auto-fixable)",
        sep = ""
      )
    }
    cat("\n")
  }

  cat("\nFiles:\n")
  print(x$by_file, row.names = FALSE)

  if (nrow(x$by_rule) > 0) {
    cat("\nIssues by rule:\n")
    print(x$by_rule, row.names = FALSE)
  } else {
    cat("\nNo style issues found.\n")
  }

  categories <- check$categories
  if (nrow(categories) > 0) {
    cat("\nCategories:\n")
    cat_df <- data.frame(
      category = categories$title,
      status = categories$status,
      rules_passed = paste0(categories$rules_passed, "/", categories$rules_applied),
      issues = categories$issues,
      stringsAsFactors = FALSE
    )
    print(cat_df, row.names = FALSE)
  }

  if (nrow(check$skipped_rules) > 0) {
    cat("\nSkipped rules:\n")
    print(check$skipped_rules, row.names = FALSE)
  }
  invisible(x)
}

#' @export
as.data.frame.jsslint <- function(x, row.names = NULL, optional = FALSE, ...) {
  x$violations
}

#' Apply automatic fixes for JSS style issues
#'
#' Lints the given files and applies the automatic fixes in place
#' (atomic write; a fix that reintroduces its own violation is rolled
#' back). Use `dry_run = TRUE` to preview the changes as a unified
#' diff without touching the files.
#'
#' @param files Character vector of file paths, or a `"jsslint"`
#'   object as returned by [jsslint()] (its files and lint options are
#'   reused).
#' @param rules Character vector of rule ids; when given, only fixes
#'   for these rules are applied.
#' @param dry_run If `TRUE`, show the diff of what would change and
#'   write nothing.
#' @inheritParams jsslint
#' @return Invisibly, an object of class `"jsslint_fixes"` with data
#'   frames `applied`, `skipped`, and `rejected`, plus the unified
#'   `diff` (dry runs only). Printing it summarises what happened.
#' @examples
#' \dontrun{
#' jssfix(c("paper.tex", "refs.bib"), dry_run = TRUE)
#' jssfix(c("paper.tex", "refs.bib"))
#' }
#' @export
jssfix <- function(files, rules = NULL, dry_run = FALSE, journal = NULL,
                   mode = NULL, ignore_rules = NULL, min_confidence = NULL,
                   verbose = NULL) {
  if (inherits(files, "jsslint")) {
    opts <- files$options
    journal <- journal %||% opts$journal
    mode <- mode %||% opts$mode
    ignore_rules <- ignore_rules %||% opts$ignore_rules
    min_confidence <- min_confidence %||% opts$min_confidence
    files <- files$files
  }
  sources <- read_sources(files)
  raw <- fix_data(sources,
    dry_run = dry_run, rules = collapse_rules(rules),
    journal = journal, mode = mode,
    ignore_rules = collapse_rules(ignore_rules),
    min_confidence = min_confidence, verbose = verbose
  )
  result <- structure(
    list(
      files = files,
      applied = list_to_df(raw$applied),
      skipped = list_to_df(raw$skipped),
      rejected = list_to_df(raw$rejected),
      diff = raw$output,
      log = raw$log,
      dry_run = dry_run
    ),
    class = "jsslint_fixes"
  )
  # jssfix() changes files on disk (or previews doing so) -- always
  # report the outcome, even when the result is assigned.
  print(result)
  invisible(result)
}

#' @export
print.jsslint_fixes <- function(x, ...) {
  n <- nrow(x$applied)
  n_files <- length(unique(x$applied$file))

  if (x$dry_run) {
    if (nzchar(x$diff)) {
      cat(x$diff)
      cat("\n")
    }
    cat("Dry run: ", count_word(n, "fix", "fixes"), " would be applied to ",
      count_word(n_files, "file"),
      ". Re-run with dry_run = FALSE to write.\n",
      sep = ""
    )
  } else if (n == 0) {
    cat("No automatic fixes to apply; files left unchanged.\n")
  } else {
    cat("Applied ", count_word(n, "fix", "fixes"), " to ",
      count_word(n_files, "file"), ":\n",
      sep = ""
    )
    per_file <- table(x$applied$file)
    for (f in names(per_file)) {
      cat("  ", f, ": ", count_word(per_file[[f]], "fix", "fixes"), "\n",
        sep = ""
      )
    }
    cat("Re-run jsslint() to review the remaining issues.\n")
  }

  n_conflict <- sum(x$skipped$reason == "conflict")
  if (n_conflict > 0) {
    cat("Skipped ", count_word(n_conflict, "overlapping fix", "overlapping fixes"),
      "; re-run jssfix() after this pass to apply them.\n",
      sep = ""
    )
  }
  n_unselected <- sum(x$skipped$reason == "rule-not-selected")
  if (n_unselected > 0) {
    cat("Skipped ", count_word(n_unselected, "fix", "fixes"),
      " for rules outside `rules`.\n",
      sep = ""
    )
  }
  if (nrow(x$rejected) > 0) {
    cat("Rejected ", count_word(nrow(x$rejected), "fix", "fixes"), ":\n", sep = "")
    print(x$rejected, row.names = FALSE)
  }
  if (nzchar(x$log)) {
    cat(x$log)
  }
  invisible(x)
}
