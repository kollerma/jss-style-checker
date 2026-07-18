# Embedded font

`DejaVuSans.ttf` / `DejaVuSans-Bold.ttf` are vendored from the
`fonts-dejavu-core` Debian package (https://dejavu-fonts.github.io/,
based on Bitstream Vera) so `jsslint report --format pdf` can embed a
real font in the PDF it generates without depending on fonts being
installed on the machine that runs it. No italic face ships in
`fonts-dejavu-core`, so `report_pdf.rs` reuses the regular/bold faces
for the italic/bold-italic slots `genpdf` requires — the report has no
content that depends on true italics.

See `LICENSE` in this directory for the full license text (permissive;
allows embedding/redistribution, forbids renaming a *modified* font
"DejaVu" or "Bitstream Vera").
