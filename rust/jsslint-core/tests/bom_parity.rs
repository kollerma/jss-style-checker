//! Regression tests for UTF-8 BOM (U+FEFF) handling —
//! `ParsedDocument::from_sources` must strip exactly one leading BOM
//! before dispatching to any parser, mirroring
//! `core/parser.py::_read_utf8` (which every Python `parse_*_file`
//! goes through uniformly). Found while reviewing commit 7b91822
//! ("feat(rust): add .Rnw/.Rmd support to the Rust engine"): the fix
//! landed in `.rnw`/`.rmd` support without carrying BOM stripping over
//! from Python, and no corpus/fixture file used by the other parity
//! tests happens to contain a BOM, so it went uncaught.
//!
//! `.Rmd` is the file type where this mattered most: the frontmatter
//! delimiter check is `line.trim() == "---"`, and `\u{FEFF}` is not
//! Unicode whitespace, so a BOM'd file's opening `---` failed the
//! check entirely — the whole frontmatter block fell through to being
//! tokenized (and linted) as ordinary prose. `tests/unit/
//! test_parser_tex.py::TestParseTexBomHandling` and
//! `tests/integration/test_rmd_end_to_end.py::
//! TestRmdFrontmatterNotLinted` are the Python-side counterparts this
//! file mirrors.

use jsslint_core::config::ToolConfig;
use jsslint_core::engine::{self, ParsedDocument};

const BOM: &str = "\u{FEFF}";

/// A BOM-prefixed `.tex` source, run through the real
/// `ParsedDocument::from_sources` entry point (not
/// `tex::parse_tex_source` directly — the fix strips the BOM at
/// `from_sources`, the single choke point every suffix branch and
/// every binding goes through, mirroring `_read_utf8`; the parser
/// itself is never given a BOM to see). Mirrors
/// `test_utf8_bom_is_stripped`: the BOM must not survive into the
/// parsed source, and parsing must otherwise be unaffected.
#[test]
fn bom_stripped_before_tex_parsing() {
    let body = "\\documentclass{article}\\begin{document}\\end{document}";
    let bom_source = format!("{BOM}{body}");

    let doc = ParsedDocument::from_sources(&[("bom.tex".to_string(), bom_source)])
        .expect("from_sources should accept a BOM-prefixed .tex file");
    let plain_doc = ParsedDocument::from_sources(&[("plain.tex".to_string(), body.to_string())])
        .expect("from_sources should accept a plain .tex file");

    assert_eq!(doc.tex_files.len(), 1);
    let parsed = &doc.tex_files[0].parsed;
    assert!(
        !parsed.source.starts_with(BOM),
        "parsed source must not start with a BOM: {:?}",
        &parsed.source[..parsed.source.len().min(16)]
    );
    assert_eq!(
        parsed.source, plain_doc.tex_files[0].parsed.source,
        "BOM-stripped source must match the source of the same file with no BOM at all"
    );
    assert_eq!(
        parsed.chars, plain_doc.tex_files[0].parsed.chars,
        "BOM-stripped chars must match a BOM-free parse exactly (no leading BOM char)"
    );
    assert_eq!(
        parsed.nodes.len(),
        plain_doc.tex_files[0].parsed.nodes.len(),
        "BOM must not introduce an extra leading Chars node"
    );
}

/// A non-BOM'd source must be completely unaffected by the strip
/// (`str::strip_prefix` is a no-op when the prefix isn't present) —
/// guards against the fix accidentally mangling the overwhelming
/// majority of real-world inputs that have no BOM at all.
#[test]
fn non_bom_source_unaffected_by_strip() {
    let body = "\\documentclass{article}\\begin{document}\\end{document}";
    let doc = ParsedDocument::from_sources(&[("plain.tex".to_string(), body.to_string())])
        .expect("from_sources should accept a plain .tex file");
    assert_eq!(doc.tex_files[0].parsed.source, body);
}

/// Full end-to-end regression for the `.Rmd` frontmatter case: a
/// BOM-prefixed `.Rmd` file whose YAML frontmatter mentions a package
/// name ("MASS") must not trip JSS-MARKUP-002 (or produce ANY
/// violation) on that frontmatter content — mirrors
/// `TestRmdFrontmatterNotLinted::test_no_violations_on_frontmatter_content`.
/// Runs through `ParsedDocument::from_sources` + `engine::run` (not
/// just the tokenizer) so it actually exercises the bug as observed:
/// pre-fix, the BOM breaks the `line.trim() == "---"` frontmatter
/// check, the whole `---`/title/`---` block falls through to being
/// tokenized as prose, and MARKUP-002 fires on the unwrapped "MASS"
/// inside it.
#[test]
fn bom_rmd_frontmatter_not_linted() {
    let src = "---\ntitle: Something about MASS\n---\n\nCompliant prose.\n";
    let bom_src = format!("{BOM}{src}");

    let doc = ParsedDocument::from_sources(&[("frontmatter.Rmd".to_string(), bom_src)])
        .expect("from_sources should accept a BOM-prefixed .Rmd file");
    assert_eq!(doc.rmd_files.len(), 1);
    assert!(
        doc.rmd_files[0].violations.is_empty(),
        "BOM'd frontmatter must still parse cleanly (no JSS-PARSE-000): {:?}",
        doc.rmd_files[0].violations
    );

    let report = engine::run(&ToolConfig::default(), &doc);
    let markup_hits: Vec<_> = report
        .violations
        .iter()
        .filter(|v| v.rule_id == "JSS-MARKUP-002")
        .collect();
    assert!(
        markup_hits.is_empty(),
        "JSS-MARKUP-002 must not fire on frontmatter content, even BOM-prefixed: {markup_hits:?}"
    );
    assert!(
        report.violations.is_empty(),
        "a BOM'd, otherwise-compliant .Rmd file must produce zero violations: {:?}",
        report.violations
    );
}
