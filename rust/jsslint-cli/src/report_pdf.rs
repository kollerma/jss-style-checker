//! `report --format pdf` — a self-contained, pure-Rust PDF rendering
//! of the conformance summary via the `genpdf` crate.
//!
//! This is **not** byte- or visually-identical to the Python CLI's
//! WeasyPrint-rendered PDF: WeasyPrint is a full HTML+CSS layout
//! engine and no pure-Rust equivalent exists that reproduces its
//! output (see `rust/README.md`'s PDF section for the trade-off this
//! decision was made under). What follows is an independently laid
//! out document carrying the same content as
//! `conformance.html.j2`/`render_html`, built directly from
//! `ConformanceSummary` with `genpdf`'s element tree instead of a
//! template.
//!
//! PDF is CLI-only scope (the `report` subcommand doesn't exist in the
//! WASM/PyO3 surfaces), so `genpdf` is a dependency of `jsslint-cli`
//! only, not `jsslint-core`.
//!
//! `genpdf` pulls in `printpdf` 0.3.4 transitively, which writes a
//! malformed ToUnicode CMap for any embedded-font glyph above U+FFFF —
//! and the vendored DejaVu Sans faces we embed contain plenty of those
//! (musical symbols, ancient scripts, a few emoticon-block glyphs),
//! regardless of what a given report's own content is, so every PDF
//! this module produced was affected. Harmless for on-screen
//! rendering (glyph selection goes through CIDToGIDMap, not
//! ToUnicode), but it broke text search/copy-paste/accessibility
//! tooling and would plausibly fail a strict PDF/A or accessibility
//! validator — worth caring about given this tool's job is producing
//! journal-submission-ready output. Fixed via a `[patch.crates-io]`
//! override at `rust/vendor/printpdf-0.3.4` (see that directory's
//! `NOTICE.md` for the bug, why no compatible upstream fix exists at a
//! version `genpdf` 0.2.0 can actually use, and exactly what changed).

use genpdf::elements::{Break, FrameCellDecorator, OrderedList, Paragraph, TableLayout};
use genpdf::style::{Color, Style};
use genpdf::{fonts, Document, Element, SimplePageDecorator};

use jsslint_core::conformance::ConformanceSummary;
use jsslint_core::report::Severity;

const DEJAVU_SANS_REGULAR: &[u8] = include_bytes!("../assets/fonts/DejaVuSans.ttf");
const DEJAVU_SANS_BOLD: &[u8] = include_bytes!("../assets/fonts/DejaVuSans-Bold.ttf");

const GRAY: Color = Color::Rgb(0x77, 0x77, 0x77);

/// No italic face ships in the vendored DejaVu font (see
/// `assets/fonts/README.md`); the regular/bold faces stand in for the
/// italic/bold-italic slots `genpdf::fonts::FontFamily` requires. This
/// report has no content that depends on true italics.
fn load_font_family() -> Result<fonts::FontFamily<fonts::FontData>, String> {
    let regular = fonts::FontData::new(DEJAVU_SANS_REGULAR.to_vec(), None)
        .map_err(|e| format!("failed to load embedded font: {e}"))?;
    let bold = fonts::FontData::new(DEJAVU_SANS_BOLD.to_vec(), None)
        .map_err(|e| format!("failed to load embedded font: {e}"))?;
    Ok(fonts::FontFamily {
        regular: regular.clone(),
        bold: bold.clone(),
        italic: regular,
        bold_italic: bold,
    })
}

fn severity_color(sev: Severity) -> Color {
    match sev {
        Severity::Error => Color::Rgb(0xb0, 0x00, 0x20),
        Severity::Warning => Color::Rgb(0xb8, 0x86, 0x0b),
        Severity::Info => Color::Rgb(0x55, 0x55, 0x55),
    }
}

fn heading(text: &str) -> impl Element {
    Paragraph::new(text).styled(Style::new().bold().with_font_size(14))
}

fn none_paragraph(text: &str) -> impl Element {
    Paragraph::new(text).styled(Style::new().italic().with_color(GRAY))
}

/// Renders `summary` as a standalone PDF document. Returns the
/// rendered PDF bytes, or an error message on a `genpdf`/font failure.
pub fn render_pdf(summary: &ConformanceSummary) -> Result<Vec<u8>, String> {
    let font_family = load_font_family()?;
    let mut doc = Document::new(font_family);
    doc.set_title(format!("JSS conformance report \u{2014} {}", summary.title));
    doc.set_line_spacing(1.25);

    let mut decorator = SimplePageDecorator::new();
    decorator.set_margins(15);
    doc.set_page_decorator(decorator);

    doc.push(
        Paragraph::new(format!("JSS conformance report \u{2014} {}", summary.title))
            .styled(Style::new().bold().with_font_size(18)),
    );
    doc.push(Break::new(1));
    doc.push(Paragraph::new(format!("Author: {}", summary.author)));
    doc.push(Paragraph::new(format!("Files: {}", summary.file_count)));
    doc.push(Paragraph::new(format!("Run date: {}", summary.run_date)));
    doc.push(Break::new(1.5));

    doc.push(heading("Conformance score"));
    match summary.score_percent {
        None => doc.push(none_paragraph("n/a")),
        Some(p) => doc
            .push(Paragraph::new(format!("{p} %")).styled(Style::new().bold().with_font_size(16))),
    }
    doc.push(Paragraph::new(format!(
        "({} of {} rules pass)",
        summary.rules_passing, summary.rules_total_active
    )));
    doc.push(Break::new(1.5));

    doc.push(heading("Severity counts"));
    doc.push(Paragraph::new(format!("Errors: {}", summary.error_count)));
    doc.push(Paragraph::new(format!(
        "Warnings: {}",
        summary.warning_count
    )));
    doc.push(Paragraph::new(format!("Info: {}", summary.info_count)));
    doc.push(Break::new(1.5));

    doc.push(heading("Top 5 most-violated rules"));
    if summary.top_five.is_empty() {
        doc.push(none_paragraph("(none)"));
    } else {
        let mut table = TableLayout::new(vec![2, 1, 4]);
        table.set_cell_decorator(FrameCellDecorator::new(true, true, false));
        table
            .row()
            .element(Paragraph::new("Rule").styled(Style::new().bold()).padded(1))
            .element(
                Paragraph::new("Count")
                    .styled(Style::new().bold())
                    .padded(1),
            )
            .element(
                Paragraph::new("Example")
                    .styled(Style::new().bold())
                    .padded(1),
            )
            .push()
            .map_err(|e| e.to_string())?;
        for e in &summary.top_five {
            table
                .row()
                .element(Paragraph::new(e.rule_id.clone()).padded(1))
                .element(Paragraph::new(e.count.to_string()).padded(1))
                .element(
                    Paragraph::new(format!(
                        "{}:{} \u{2014} {}",
                        e.example_file, e.example_line, e.example_excerpt
                    ))
                    .padded(1),
                )
                .push()
                .map_err(|e| e.to_string())?;
        }
        doc.push(table);
    }
    doc.push(Break::new(1.5));

    doc.push(heading("Fix me first"));
    if summary.fix_me_first.is_empty() {
        doc.push(none_paragraph("(no violations)"));
    } else {
        let mut list = OrderedList::new();
        for item in &summary.fix_me_first {
            list.push(
                Paragraph::default()
                    .styled_string(item.rule_id.clone(), Style::new().bold())
                    .string(" (")
                    .styled_string(
                        item.severity.as_str(),
                        Style::new().with_color(severity_color(item.severity)),
                    )
                    .string(format!(") \u{2014} {}", item.count)),
            );
        }
        doc.push(list);
    }
    doc.push(Break::new(1.5));
    doc.push(Paragraph::new("Generated by jss-lint.").styled(Style::new().with_color(GRAY)));

    let mut buf = Vec::new();
    doc.render(&mut buf).map_err(|e| e.to_string())?;
    Ok(buf)
}
