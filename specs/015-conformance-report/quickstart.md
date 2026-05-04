# Quickstart: Conformance Report

## For an editor

### Generate a markdown report

```sh
jss-lint report manuscript.tex > review.md
```

Open `review.md`; paste relevant sections into the
decision letter.

### Generate a PDF for attachment

```sh
pip install "jss-lint[pdf]"   # one-time install of WeasyPrint
jss-lint report manuscript.tex --format pdf --out review.pdf
```

Attach `review.pdf` to the decision letter.

### Generate HTML for a web preview

```sh
jss-lint report manuscript.tex --format html --out review.html
open review.html
```

### Override the metadata for double-blind review

```sh
jss-lint report manuscript.tex \
  --title "Submission #1234" \
  --author "Anonymous"
```

The header reads `Title: Submission #1234`, `Author:
Anonymous` even if the preamble says otherwise.

### Suppress noisy rules from the report

```sh
jss-lint report manuscript.tex --ignore-rules JSS-MARKUP-005
```

The score's denominator excludes ignored rules, so the
score reflects what was actually checked.

## For a contributor

### Where things live

```text
src/texlint/report.py                           # the renderer
src/texlint/output/pdf.py                       # WeasyPrint helper
src/texlint/output/templates/conformance.*.j2   # Jinja2 templates
src/texlint/cli.py                              # `report` subcommand
tests/unit/test_report.py                       # markdown goldens
tests/unit/test_report_pdf.py                   # PDF page-count
tests/integration/test_report_cli.py            # end-to-end
tests/fixtures/report/                          # fixture pairs
```

### Run the tests

```sh
pip install -e ".[pdf,dev]"
pytest tests/unit/test_report.py tests/integration/test_report_cli.py -v
pytest tests/unit/test_report_pdf.py -v   # requires [pdf] extra
```

### Update a template

1. Edit one of the three Jinja2 templates.
2. Regenerate the markdown golden:
   ```sh
   pytest tests/unit/test_report.py --update-goldens
   ```
3. If you changed the data shape (added a section), update
   `data-model.md` §1 to match.

### Add a new section

1. Decide whether the section belongs in the
   `ConformanceSummary` dataclass (a new derived field) or
   only in the template (purely presentational).
2. If a new field: add it to the dataclass; populate it in
   `_compute_summary`; update `data-model.md`.
3. Add the section to all three templates.
4. Regenerate goldens.

### Common pitfalls

- **PDF tests fail with `PdfNotAvailable`**: install the
  `[pdf]` extra. The PDF tests are skipped when WeasyPrint
  is absent; if you forced them to run without it, they
  will fail.
- **Markdown golden compare fails on the run-date line**:
  the test compares body bytes minus the run-date line.
  If your edit moved the run-date away from its expected
  position, update the test's stripping logic.
- **PDF takes >3 s**: WeasyPrint's first import is slow
  (~1 s). Test fixtures should stay small.
- **Top-5 includes a tool-side rule**: top-5 is filtered
  to citable categories. If a tool-side rule appears,
  the filter is broken — check `_compute_summary`.
