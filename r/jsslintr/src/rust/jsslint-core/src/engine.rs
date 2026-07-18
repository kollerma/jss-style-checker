//! Document assembly + rule-running engine — mirrors
//! `core/engine.py`'s `parse_document`/`load_journal`/`run`.
//!
//! `.tex`/`.ltx`/`.bib`/`.rnw`/`.rmd` are all supported. `.rnw` chunk
//! rewriting lives in `crate::rnw`; `.rmd` tokenizing/fragment
//! construction lives in `crate::rmd` (see that module's doc comment
//! for the line-offset scheme). Most rules iterate
//! `all_tex_like_docs()` (tex_files + every `.Rmd` fragment); a few
//! (`GLOBAL_TEX_RULES`, below) need every fragment together in one
//! call instead of one call per fragment — see that constant's doc
//! comment for which and why.
//!
//! No filesystem I/O here — `from_sources` takes already-read
//! `(path, contents)` pairs so every binding (including WASM, which
//! has no filesystem) can drive the same engine.

use crate::bib::{self, Library};
use crate::catalogue;
use crate::config::{ConfidenceTier, ToolConfig};
use crate::report::{CategorySummary, ComplianceReport, SkippedRule, Violation};
use crate::rules::{
    abbreviations, capitalization, citations, code_style, code_width, crossrefs, house_style,
    markup, naming, operators, preamble, references, structure, typography,
};
use crate::tex::node::Node as TexNode;
use crate::tex::position::LineIndex;
use crate::tex::{self, ParsedTex};
use std::collections::HashMap;

#[derive(Debug)]
pub enum EngineError {
    /// The stored `String` is the complete, ready-to-print message —
    /// mirrors `api.py::UnsupportedSuffixError`'s
    /// `f"unsupported file extension: {path.name!r}. Supported: .tex,
    /// .ltx, .bib, .Rnw, .Rmd (case-insensitive)."` text exactly.
    /// `jsslint-cli` prints it verbatim (destructures the payload and
    /// formats it directly rather than going through `Display`).
    UnsupportedSuffix(String),
}

impl std::fmt::Display for EngineError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            EngineError::UnsupportedSuffix(msg) => write!(f, "{msg}"),
        }
    }
}

pub struct ParsedTexFileDoc {
    pub path: String,
    pub parsed: ParsedTex,
    pub line_index: LineIndex,
}

pub struct ParsedBibFileDoc {
    pub path: String,
    pub source_chars: Vec<char>,
    pub library: Library,
}

/// Mirrors `api.py::ParsedRmdFile`. `latex_fragments` are the raw-LaTeX
/// islands extracted from prose blocks (spec 005 FR-006) — every rule
/// that iterates `all_tex_like_docs()` sees these alongside real `.tex`
/// files. `violations` are `JSS-PARSE-000` findings from the Rmd
/// tokenizer itself (unterminated frontmatter/fence, malformed YAML),
/// not rule findings.
pub struct ParsedRmdFileDoc {
    pub path: String,
    pub latex_fragments: Vec<ParsedTexFileDoc>,
    pub violations: Vec<Violation>,
}

#[derive(Default)]
pub struct ParsedDocument {
    pub tex_files: Vec<ParsedTexFileDoc>,
    pub bib_files: Vec<ParsedBibFileDoc>,
    pub rmd_files: Vec<ParsedRmdFileDoc>,
}

impl ParsedDocument {
    /// Build a document from `(path, contents)` pairs, dispatching by
    /// path suffix (case-insensitive) exactly like
    /// `core/engine.py::parse_document`: `.tex`/`.ltx` -> tex_files,
    /// `.bib` -> bib_files, `.rnw` -> tex_files (after chunk-rewriting),
    /// `.rmd` -> rmd_files. Any other suffix is an error.
    pub fn from_sources(files: &[(String, String)]) -> Result<Self, EngineError> {
        let mut doc = ParsedDocument::default();
        for (path, source) in files {
            // Mirrors `core/parser.py::_read_utf8`: strip exactly one
            // leading UTF-8 BOM (U+FEFF), if present, before parsing.
            // Applied here — the single choke point every suffix
            // branch and every binding (CLI/WASM/PyO3/R) goes through
            // — rather than separately inside each parser, mirroring
            // how Python's `_read_utf8` is called uniformly by
            // `parse_tex_file`/`parse_bib_file`/`parse_rnw_file`/
            // `parse_rmd_file`. A source with no BOM is unaffected.
            let source: &str = source.strip_prefix('\u{FEFF}').unwrap_or(source);
            let lower = path.to_lowercase();
            if lower.ends_with(".tex") || lower.ends_with(".ltx") {
                let parsed = tex::parse_tex_source(source);
                let line_index = LineIndex::with_offset(&parsed.chars, parsed.line_offset);
                doc.tex_files.push(ParsedTexFileDoc {
                    path: path.clone(),
                    parsed,
                    line_index,
                });
            } else if lower.ends_with(".bib") {
                let library = bib::parse(source);
                doc.bib_files.push(ParsedBibFileDoc {
                    path: path.clone(),
                    source_chars: source.chars().collect(),
                    library,
                });
            } else if lower.ends_with(".rnw") {
                let rewritten = crate::rnw::wrap_rnw_chunks_as_sinput(source);
                let parsed = tex::parse_tex_source(&rewritten);
                let line_index = LineIndex::with_offset(&parsed.chars, parsed.line_offset);
                doc.tex_files.push(ParsedTexFileDoc {
                    path: path.clone(),
                    parsed,
                    line_index,
                });
            } else if lower.ends_with(".rmd") {
                doc.rmd_files
                    .push(crate::rmd::parse_rmd_source(path, source));
            } else {
                let name = path.rsplit('/').next().unwrap_or(path.as_str());
                return Err(EngineError::UnsupportedSuffix(format!(
                    "unsupported file extension: '{name}'. Supported: .tex, .ltx, .bib, .Rnw, .Rmd (case-insensitive)."
                )));
            }
        }
        Ok(doc)
    }

    /// Every tex-shaped parsed view: native `.tex`/`.rnw` files plus
    /// raw-LaTeX islands extracted from `.Rmd` prose blocks. Mirrors
    /// `api.py::ParsedDocument.all_tex_like`; rules that in Python
    /// iterate `doc.all_tex_like()` use this instead of `tex_files`.
    pub(crate) fn all_tex_like_docs(&self) -> impl Iterator<Item = &ParsedTexFileDoc> {
        self.tex_files
            .iter()
            .chain(self.rmd_files.iter().flat_map(|r| r.latex_fragments.iter()))
    }

    fn tex_like(&self) -> Vec<&[TexNode]> {
        self.all_tex_like_docs()
            .map(|t| t.parsed.nodes.as_slice())
            .collect()
    }

    fn tex_file_line_indexes(&self) -> Vec<(&str, &LineIndex)> {
        self.all_tex_like_docs()
            .map(|t| (t.path.as_str(), &t.line_index))
            .collect()
    }
}

type TexCheckFn = fn(&str, &ParsedTex, u32) -> Vec<Violation>;
type BibCheckFn =
    fn(&str, &[char], &Library, &[&[TexNode]], &[(&str, &LineIndex)]) -> Vec<Violation>;
/// Called ONCE per document with every tex-like fragment together,
/// unlike `TexCheckFn` (called once per fragment). Mirrors
/// `Rule.check(doc, cfg)` receiving the whole `ParsedDocument` in
/// Python: a handful of rules maintain state that must span every
/// fragment (a `.Rmd` file's multiple raw-LaTeX prose-block islands),
/// not reset per fragment — see `GLOBAL_TEX_RULES`'s doc comment.
type TexGlobalCheckFn = fn(&[(&str, &ParsedTex)]) -> Vec<Violation>;

struct TexRuleEntry {
    id: &'static str,
    check: TexCheckFn,
    /// True for the 9 rules that restrict `Rule.formats` to
    /// `{"tex","rnw"}` (PRE-001..008, OPER-003) — see
    /// `rule_should_run`'s doc comment for how this is used. False
    /// (the default for every other entry below) means `formats is
    /// None` in Python terms: "all formats", i.e. this rule still
    /// counts as applied/passed even in a document with zero tex
    /// files, as long as some other file (a `.bib`) is present.
    restricted_to_tex: bool,
    /// True when the Python rule body iterates `doc.all_tex_like()`
    /// (tex_files + every `.Rmd`'s raw-LaTeX prose fragments) rather
    /// than `doc.tex_files` alone — true for every entry except
    /// `WIDTH-001`, `STRUCT-001..006`, `PRE-001..008`, and `OPER-003`
    /// (confirmed by grepping every rule module in `journals/jss/rules/`
    /// for `all_tex_like` vs `doc.tex_files`). Independent of
    /// `restricted_to_tex`: that gate is about whether the rule counts
    /// as "applied" for a given input-format mix; this one is about
    /// which files its `check` function actually reads.
    scans_rmd_prose: bool,
}

struct BibRuleEntry {
    id: &'static str,
    check: BibCheckFn,
}

struct GlobalTexRuleEntry {
    id: &'static str,
    check: TexGlobalCheckFn,
}

/// Every ported `tex_files`/`raw_source` rule (46 + WIDTH-001), one
/// adapter closure per rule normalizing its real signature to
/// `TexCheckFn`.
mod rules_registry {
    use super::*;

    pub const TEX_RULES: &[TexRuleEntry] = &[
        TexRuleEntry {
            id: "JSS-WIDTH-001",
            check: |f, p, w| code_width::check_width_001(f, p, w),
            restricted_to_tex: false,
            scans_rmd_prose: false,
        },
        TexRuleEntry {
            id: "JSS-CODE-001",
            check: |f, p, _w| code_style::check_code_001(f, p),
            restricted_to_tex: false,
            scans_rmd_prose: true,
        },
        TexRuleEntry {
            id: "JSS-CODE-002",
            check: |f, p, _w| code_style::check_code_002(f, p),
            restricted_to_tex: false,
            scans_rmd_prose: true,
        },
        TexRuleEntry {
            id: "JSS-CODE-003",
            check: |f, p, _w| code_style::check_code_003(f, p),
            restricted_to_tex: false,
            scans_rmd_prose: true,
        },
        TexRuleEntry {
            id: "JSS-ABBR-001",
            check: |f, p, _w| abbreviations::check_abbr_001(f, p),
            restricted_to_tex: false,
            scans_rmd_prose: true,
        },
        TexRuleEntry {
            id: "JSS-TYPO-001",
            check: |f, p, _w| typography::check_typo_001(f, p),
            restricted_to_tex: false,
            scans_rmd_prose: true,
        },
        TexRuleEntry {
            id: "JSS-TYPO-002",
            check: |f, p, _w| typography::check_typo_002(f, p),
            restricted_to_tex: false,
            scans_rmd_prose: true,
        },
        TexRuleEntry {
            id: "JSS-TYPO-003",
            check: |f, p, _w| typography::check_typo_003(f, p),
            restricted_to_tex: false,
            scans_rmd_prose: true,
        },
        TexRuleEntry {
            id: "JSS-TYPO-004",
            check: |f, p, _w| typography::check_typo_004(f, p),
            restricted_to_tex: false,
            scans_rmd_prose: true,
        },
        TexRuleEntry {
            id: "JSS-CAP-002",
            check: |f, p, _w| capitalization::check_cap_002(f, p),
            restricted_to_tex: false,
            scans_rmd_prose: true,
        },
        TexRuleEntry {
            id: "JSS-CAP-004",
            check: |f, p, _w| capitalization::check_cap_004(f, p),
            restricted_to_tex: false,
            scans_rmd_prose: true,
        },
        TexRuleEntry {
            id: "JSS-STRUCT-001",
            check: |f, p, _w| structure::check_struct_001(f, p),
            restricted_to_tex: false,
            scans_rmd_prose: false,
        },
        TexRuleEntry {
            id: "JSS-STRUCT-002",
            check: |f, p, _w| structure::check_struct_002(f, p),
            restricted_to_tex: false,
            scans_rmd_prose: false,
        },
        TexRuleEntry {
            id: "JSS-STRUCT-003",
            check: |f, p, _w| structure::check_struct_003(f, p),
            restricted_to_tex: false,
            scans_rmd_prose: false,
        },
        TexRuleEntry {
            id: "JSS-STRUCT-004",
            check: |f, p, _w| structure::check_struct_004(f, p),
            restricted_to_tex: false,
            scans_rmd_prose: false,
        },
        TexRuleEntry {
            id: "JSS-STRUCT-005",
            check: |f, p, _w| structure::check_struct_005(f, p),
            restricted_to_tex: false,
            scans_rmd_prose: false,
        },
        TexRuleEntry {
            id: "JSS-STRUCT-006",
            check: |f, p, _w| structure::check_struct_006(f, p),
            restricted_to_tex: false,
            scans_rmd_prose: false,
        },
        TexRuleEntry {
            id: "JSS-OPER-001",
            check: |f, p, _w| operators::check_oper_001(f, p),
            restricted_to_tex: false,
            scans_rmd_prose: true,
        },
        TexRuleEntry {
            id: "JSS-OPER-002",
            check: |f, p, _w| operators::check_oper_002(f, p),
            restricted_to_tex: false,
            scans_rmd_prose: true,
        },
        TexRuleEntry {
            id: "JSS-OPER-003",
            check: |f, p, _w| operators::check_oper_003(f, p),
            restricted_to_tex: true,
            scans_rmd_prose: false,
        },
        TexRuleEntry {
            id: "JSS-HOUSE-001",
            check: |f, p, _w| house_style::check_house_001(f, p),
            restricted_to_tex: false,
            scans_rmd_prose: true,
        },
        TexRuleEntry {
            id: "JSS-HOUSE-003",
            check: |f, p, _w| house_style::check_house_003(f, p),
            restricted_to_tex: false,
            scans_rmd_prose: true,
        },
        TexRuleEntry {
            id: "JSS-NAME-001",
            check: |f, p, _w| naming::check_name_001(f, p),
            restricted_to_tex: false,
            scans_rmd_prose: true,
        },
        TexRuleEntry {
            id: "JSS-PRE-001",
            check: |f, p, _w| preamble::check_pre_001(f, p),
            restricted_to_tex: true,
            scans_rmd_prose: false,
        },
        TexRuleEntry {
            id: "JSS-PRE-002",
            check: |f, p, _w| preamble::check_pre_002(f, p),
            restricted_to_tex: true,
            scans_rmd_prose: false,
        },
        TexRuleEntry {
            id: "JSS-PRE-003",
            check: |f, p, _w| preamble::check_pre_003(f, p),
            restricted_to_tex: true,
            scans_rmd_prose: false,
        },
        TexRuleEntry {
            id: "JSS-PRE-004",
            check: |f, p, _w| preamble::check_pre_004(f, p),
            restricted_to_tex: true,
            scans_rmd_prose: false,
        },
        TexRuleEntry {
            id: "JSS-PRE-005",
            check: |f, p, _w| preamble::check_pre_005(f, p),
            restricted_to_tex: true,
            scans_rmd_prose: false,
        },
        TexRuleEntry {
            id: "JSS-PRE-006",
            check: |f, p, _w| preamble::check_pre_006(f, p),
            restricted_to_tex: true,
            scans_rmd_prose: false,
        },
        TexRuleEntry {
            id: "JSS-PRE-007",
            check: |f, p, _w| preamble::check_pre_007(f, p),
            restricted_to_tex: true,
            scans_rmd_prose: false,
        },
        TexRuleEntry {
            id: "JSS-PRE-008",
            check: |f, p, _w| preamble::check_pre_008(f, p),
            restricted_to_tex: true,
            scans_rmd_prose: false,
        },
        TexRuleEntry {
            id: "JSS-CITE-003",
            check: |f, p, _w| citations::check_cite_003(f, p),
            restricted_to_tex: false,
            scans_rmd_prose: true,
        },
        TexRuleEntry {
            id: "JSS-CITE-004",
            check: |f, p, _w| citations::check_cite_004(f, p),
            restricted_to_tex: false,
            scans_rmd_prose: true,
        },
        TexRuleEntry {
            id: "JSS-MARKUP-001",
            check: |f, p, _w| markup::check_markup_001(f, p),
            restricted_to_tex: false,
            scans_rmd_prose: true,
        },
        TexRuleEntry {
            id: "JSS-MARKUP-002",
            check: |f, p, _w| markup::check_markup_002(f, p),
            restricted_to_tex: false,
            scans_rmd_prose: true,
        },
        TexRuleEntry {
            id: "JSS-MARKUP-003",
            check: |f, p, _w| markup::check_markup_003(f, p),
            restricted_to_tex: false,
            scans_rmd_prose: true,
        },
        TexRuleEntry {
            id: "JSS-MARKUP-004",
            check: |f, p, _w| markup::check_markup_004(f, p),
            restricted_to_tex: false,
            scans_rmd_prose: true,
        },
        TexRuleEntry {
            id: "JSS-XREF-001",
            check: |f, p, _w| crossrefs::check_xref_001(f, p),
            restricted_to_tex: false,
            scans_rmd_prose: true,
        },
        TexRuleEntry {
            id: "JSS-XREF-002",
            check: |f, p, _w| crossrefs::check_xref_002(f, p),
            restricted_to_tex: false,
            scans_rmd_prose: true,
        },
        TexRuleEntry {
            id: "JSS-XREF-003",
            check: |f, p, _w| crossrefs::check_xref_003(f, p),
            restricted_to_tex: false,
            scans_rmd_prose: true,
        },
        TexRuleEntry {
            id: "JSS-XREF-006",
            check: |f, p, _w| crossrefs::check_xref_006(f, p),
            restricted_to_tex: false,
            scans_rmd_prose: true,
        },
        TexRuleEntry {
            id: "JSS-XREF-007",
            check: |f, p, _w| crossrefs::check_xref_007(f, p),
            restricted_to_tex: false,
            scans_rmd_prose: true,
        },
    ];

    pub const BIB_RULES: &[BibRuleEntry] = &[
        BibRuleEntry {
            id: "JSS-BIBTEX-001",
            check: |f, _c, lib, tl, _tf| crate::rules::bibtex::check_bibtex_001(f, lib, tl),
        },
        BibRuleEntry {
            id: "JSS-BIBTEX-002",
            check: |f, _c, lib, _tl, _tf| crate::rules::bibtex::check_bibtex_002(f, lib),
        },
        BibRuleEntry {
            id: "JSS-BIBTEX-003",
            check: |f, _c, lib, tl, _tf| crate::rules::bibtex::check_bibtex_003(f, lib, tl),
        },
        BibRuleEntry {
            id: "JSS-BIBTEX-004",
            check: |f, _c, lib, tl, tf| crate::rules::bibtex::check_bibtex_004(f, tf, lib, tl),
        },
        BibRuleEntry {
            id: "JSS-BIBTEX-005",
            check: |f, _c, lib, _tl, _tf| crate::rules::bibtex::check_bibtex_005(f, lib),
        },
        BibRuleEntry {
            id: "JSS-NAME-002",
            check: |f, c, lib, tl, _tf| naming::check_name_002(f, c, lib, tl),
        },
        BibRuleEntry {
            id: "JSS-HOUSE-002",
            check: |f, c, lib, tl, _tf| house_style::check_house_002(f, c, lib, tl),
        },
        BibRuleEntry {
            id: "JSS-REFS-001",
            check: |f, _c, lib, tl, _tf| references::check_refs_001(f, lib, tl),
        },
        BibRuleEntry {
            id: "JSS-REFS-003",
            check: |f, _c, lib, tl, _tf| references::check_refs_003(f, lib, tl),
        },
        BibRuleEntry {
            id: "JSS-REFS-004",
            check: |f, _c, lib, tl, _tf| references::check_refs_004(f, lib, tl),
        },
        BibRuleEntry {
            id: "JSS-REFS-005",
            check: |f, _c, lib, tl, _tf| references::check_refs_005(f, lib, tl),
        },
        BibRuleEntry {
            id: "JSS-REFS-006",
            check: |f, _c, lib, tl, _tf| references::check_refs_006(f, lib, tl),
        },
        BibRuleEntry {
            id: "JSS-REFS-007",
            check: |f, _c, lib, tl, _tf| references::check_refs_007(f, lib, tl),
        },
    ];

    /// The 5 tex-like rules confirmed (by auditing every `check_jss_*`
    /// in `journals/jss/rules/*.py` for a doc-wide pre-pass before its
    /// per-fragment walk) to maintain state that must span every
    /// tex-like fragment, not reset per fragment: CAP-001
    /// (`_doc_pkg_names_lower`), CITE-002 (`seen` — its own Python
    /// comment calls out `.Rmd`'s per-prose-block fragmentation by
    /// name), OPER-004 (`flag_pr`/alias pre-scan), XREF-004/005
    /// (`_collect_referenced_labels`). Every other tex-like rule reads
    /// fresh/local state on each fragment, so calling it once per
    /// fragment (`TEX_RULES`, above) gives an identical result to
    /// calling it once with all fragments together — these 5 don't.
    pub const GLOBAL_TEX_RULES: &[GlobalTexRuleEntry] = &[
        GlobalTexRuleEntry {
            id: "JSS-CAP-001",
            check: capitalization::check_cap_001,
        },
        GlobalTexRuleEntry {
            id: "JSS-CITE-002",
            check: citations::check_cite_002,
        },
        GlobalTexRuleEntry {
            id: "JSS-OPER-004",
            check: operators::check_oper_004,
        },
        GlobalTexRuleEntry {
            id: "JSS-XREF-004",
            check: crossrefs::check_xref_004,
        },
        GlobalTexRuleEntry {
            id: "JSS-XREF-005",
            check: crossrefs::check_xref_005,
        },
    ];
}

/// Mirrors Python `repr(sorted(some_str_set))` for a list of plain
/// (quote-free) format tags — `str.__repr__` single-quotes. `pub(crate)`
/// so `diff.rs`'s schema-mismatch messages (also built from
/// `repr(sorted(some_set))`) can reuse it instead of duplicating.
pub(crate) fn python_list_repr(items: &[&str]) -> String {
    let quoted: Vec<String> = items.iter().map(|s| format!("'{s}'")).collect();
    format!("[{}]", quoted.join(", "))
}

/// Mirrors `journals/jss/__init__.py::_TITLE_MAP` — display titles for
/// `catalogue::categories()`'s ids, hand-maintained on the Python side
/// too (not generated from catalogue.yaml).
fn category_title(category_id: &str) -> &'static str {
    match category_id {
        "preamble" => "Preamble",
        "structure" => "Structure",
        "markup" => "Markup",
        "citations" => "Citations",
        "references" => "References",
        "bibtex" => "BibTeX",
        "naming" => "Naming",
        "capitalization" => "Capitalization",
        "typography" => "Typography",
        "abbreviations" => "Abbreviations",
        "code_style" => "Code style",
        "code_width" => "Code width",
        "operators" => "Operators",
        "crossrefs" => "Cross-references",
        "house_style" => "House style",
        other => {
            panic!("unknown category id {other:?} (not in journals/jss/__init__.py's _TITLE_MAP)")
        }
    }
}

fn confidence_meets_floor(rule_id: &str, floor: ConfidenceTier) -> (bool, &'static str) {
    let confidence = catalogue::lookup(rule_id)
        .map(|m| m.confidence)
        .unwrap_or("high");
    let tier = ConfidenceTier::parse(confidence).unwrap_or(ConfidenceTier::High);
    (tier >= floor, confidence)
}

/// `catalogue::categories()`'s (ROLLOUT_ORDER) position for a rule's
/// category, or `usize::MAX` for an unknown category (sorts last).
fn category_rank(category: &str) -> usize {
    catalogue::categories()
        .iter()
        .position(|&c| c == category)
        .unwrap_or(usize::MAX)
}

enum RuleAction<'a> {
    Tex(&'a TexRuleEntry),
    Bib(&'a BibRuleEntry),
    TexGlobal(&'a GlobalTexRuleEntry),
}

/// Every registered rule, ordered `(category rollout rank, rule id)` —
/// mirrors `JSSJournal.categories()` iterating `ROLLOUT_ORDER` and
/// each category module's `rules` tuple in ascending-rule-number
/// declaration order (which sorting by rule id string reproduces,
/// since every rule id's numeric suffix is zero-padded to 3 digits).
/// This order matters beyond cosmetics: `report.skipped_rules` is a
/// flat list built in this same iteration order.
fn ordered_rules() -> Vec<(&'static str, RuleAction<'static>)> {
    let mut all: Vec<(usize, &'static str, RuleAction<'static>)> = Vec::new();
    for entry in rules_registry::TEX_RULES {
        let category = catalogue::lookup(entry.id)
            .map(|m| m.category)
            .unwrap_or("");
        all.push((category_rank(category), entry.id, RuleAction::Tex(entry)));
    }
    for entry in rules_registry::BIB_RULES {
        let category = catalogue::lookup(entry.id)
            .map(|m| m.category)
            .unwrap_or("");
        all.push((category_rank(category), entry.id, RuleAction::Bib(entry)));
    }
    for entry in rules_registry::GLOBAL_TEX_RULES {
        let category = catalogue::lookup(entry.id)
            .map(|m| m.category)
            .unwrap_or("");
        all.push((
            category_rank(category),
            entry.id,
            RuleAction::TexGlobal(entry),
        ));
    }
    all.sort_by(|a, b| (a.0, a.1).cmp(&(b.0, b.1)));
    all.into_iter()
        .map(|(_, id, action)| (id, action))
        .collect()
}

/// Run every registered rule over `document`, applying the
/// ignore-rules and min-confidence gates, and assemble a
/// `ComplianceReport`. Mirrors `core/engine.py::run`'s algorithm
/// (category/rule iteration, `SkippedRule` bookkeeping, format
/// gating, the synthetic `JSS-PARSE-000` "parse" category,
/// `compliance_percentage`, sorted violations, severity overrides).
/// One thing still deferred: inline suppression comments (`%
/// jss-lint: ignore [RULE-IDS]`) aren't implemented — every rule
/// finding is reported regardless. `JSS-PARSE-000` findings currently
/// only ever come from `.Rmd`'s tokenizer (unterminated
/// frontmatter/fence, malformed YAML); the tex tokenizer itself
/// (`.tex`/`.ltx`/`.rnw`) never emits one — it only implements
/// pylatexenc's tolerant-parsing path, which never raises, unlike
/// Python's strict-then-tolerant-retry `parse_tex_source` (see
/// `tex::parse_tex_source`'s doc comment).
pub fn run(config: &ToolConfig, document: &ParsedDocument) -> ComplianceReport {
    let tex_like = document.tex_like();
    let tex_file_line_indexes = document.tex_file_line_indexes();

    let mut applied_by_category: HashMap<&'static str, u32> = HashMap::new();
    let mut passed_by_category: HashMap<&'static str, u32> = HashMap::new();
    let mut violations_by_category: HashMap<&'static str, Vec<Violation>> = HashMap::new();
    let mut skipped: Vec<SkippedRule> = Vec::new();

    let mut run_one = |rule_id: &'static str, mut rule_violations: Vec<Violation>| {
        let Some(meta) = catalogue::lookup(rule_id) else {
            return;
        };
        let category = meta.category;

        if !config.severity_overrides.is_empty() {
            for v in &mut rule_violations {
                if let Some(&sev) = config.severity_overrides.get(rule_id) {
                    v.severity = sev;
                }
            }
        }

        *applied_by_category.entry(category).or_insert(0) += 1;
        if rule_violations.is_empty() {
            *passed_by_category.entry(category).or_insert(0) += 1;
        }
        violations_by_category
            .entry(category)
            .or_default()
            .extend(rule_violations);
    };

    for (rule_id, action) in ordered_rules() {
        if config.ignore_rules.contains(rule_id) {
            continue;
        }
        let (meets_floor, confidence) = confidence_meets_floor(rule_id, config.min_confidence);
        if !meets_floor {
            skipped.push(SkippedRule {
                rule_id: rule_id.to_string(),
                reason: format!(
                    "confidence {confidence} below min_confidence={}",
                    config.min_confidence.as_str()
                ),
            });
            continue;
        }
        let has_any_file = !document.tex_files.is_empty()
            || !document.bib_files.is_empty()
            || !document.rmd_files.is_empty();
        match action {
            RuleAction::Tex(entry) => {
                // A format-restricted rule (formats={"tex","rnw"}) only
                // "runs" (counts toward applied/passed) when a tex file
                // is present. An unrestricted rule (formats=None, the
                // common case) still runs — with zero tex files to
                // check, hence zero violations — as long as the
                // document has ANY file at all (even just a `.bib`),
                // mirroring `doc.files_for_rule(rule)` yielding
                // `doc.all_files()` unfiltered. Mirrors
                // `core/engine.py::run`'s `rule.formats is not None and
                // not (rule.formats & input_formats)` gate.
                let should_run = if entry.restricted_to_tex {
                    !document.tex_files.is_empty()
                } else {
                    has_any_file
                };
                if !should_run {
                    // Mirrors `core/engine.py::run`'s `check_skipped_for_format`
                    // branch: every currently format-restricted rule
                    // (PRE-001..008, OPER-003) declares
                    // `formats=frozenset({"tex", "rnw"})`, so the
                    // "rule formats=" half of the message is a fixed
                    // literal; `inputs=` is `sorted(_file_format(f) for f
                    // in doc.all_files())`. `.Rnw` files live in
                    // `tex_files` alongside real `.tex`/`.ltx`, but
                    // `_file_format` tags them `"rnw"` by path suffix,
                    // not `"tex"` — bucket by suffix here too so the
                    // message stays accurate even though, in practice,
                    // this branch is unreachable while any `tex_files`
                    // entry (real `.tex` or `.rnw`) is present (both
                    // satisfy `restricted_to_tex`'s `!tex_files.is_empty()`
                    // check above).
                    let mut input_formats: Vec<&str> = Vec::new();
                    if document
                        .tex_files
                        .iter()
                        .any(|tf| !tf.path.to_lowercase().ends_with(".rnw"))
                    {
                        input_formats.push("tex");
                    }
                    if document
                        .tex_files
                        .iter()
                        .any(|tf| tf.path.to_lowercase().ends_with(".rnw"))
                    {
                        input_formats.push("rnw");
                    }
                    if !document.bib_files.is_empty() {
                        input_formats.push("bib");
                    }
                    if !document.rmd_files.is_empty() {
                        input_formats.push("rmd");
                    }
                    input_formats.sort_unstable();
                    skipped.push(SkippedRule {
                        rule_id: rule_id.to_string(),
                        reason: format!(
                            "format mismatch (rule formats={}; inputs={})",
                            python_list_repr(&["rnw", "tex"]),
                            python_list_repr(&input_formats),
                        ),
                    });
                    continue;
                }
                let mut rule_violations = Vec::new();
                // Mirrors the Python rule module's own choice of
                // `doc.all_tex_like()` vs `doc.tex_files` — see
                // `scans_rmd_prose`'s doc comment.
                if entry.scans_rmd_prose {
                    for tf in document.all_tex_like_docs() {
                        rule_violations.extend((entry.check)(
                            &tf.path,
                            &tf.parsed,
                            config.code_width,
                        ));
                    }
                } else {
                    for tf in &document.tex_files {
                        rule_violations.extend((entry.check)(
                            &tf.path,
                            &tf.parsed,
                            config.code_width,
                        ));
                    }
                }
                run_one(rule_id, rule_violations);
            }
            RuleAction::Bib(entry) => {
                if !has_any_file {
                    continue;
                }
                let mut rule_violations = Vec::new();
                for bf in &document.bib_files {
                    rule_violations.extend((entry.check)(
                        &bf.path,
                        &bf.source_chars,
                        &bf.library,
                        &tex_like,
                        &tex_file_line_indexes,
                    ));
                }
                run_one(rule_id, rule_violations);
            }
            RuleAction::TexGlobal(entry) => {
                // All 5 `GLOBAL_TEX_RULES` entries are unrestricted-format
                // rules (formats=None in Python terms), so `should_run`
                // reduces to `has_any_file` exactly like an unrestricted
                // `RuleAction::Tex` entry — none of them are among
                // PRE-001..008/OPER-003's `{"tex","rnw"}` restriction.
                if !has_any_file {
                    continue;
                }
                let fragments: Vec<(&str, &ParsedTex)> = document
                    .all_tex_like_docs()
                    .map(|tf| (tf.path.as_str(), &tf.parsed))
                    .collect();
                let rule_violations = (entry.check)(&fragments);
                run_one(rule_id, rule_violations);
            }
        }
    }

    let mut summaries: Vec<CategorySummary> = Vec::new();
    for &category_id in catalogue::categories() {
        let applied = applied_by_category.get(category_id).copied().unwrap_or(0);
        let passed = passed_by_category.get(category_id).copied().unwrap_or(0);
        let violations = violations_by_category
            .remove(category_id)
            .unwrap_or_default();
        summaries.push(CategorySummary::build(
            category_id.to_string(),
            category_title(category_id).to_string(),
            applied,
            passed,
            violations,
        ));
    }

    // Synthetic "parse" category — mirrors `core/engine.py::run` lines
    // ~317-334: collects every `JSS-PARSE-000` finding recorded during
    // parsing (currently only `.Rmd`'s tokenizer: unterminated
    // frontmatter/fence, malformed YAML frontmatter). Appended last,
    // only when non-empty; excluded from `compliance_percentage` below
    // exactly like Python's `s.category_id != _PARSE_CATEGORY_ID` guard.
    let parse_errors: Vec<Violation> = document
        .rmd_files
        .iter()
        .flat_map(|r| r.violations.iter().cloned())
        .collect();
    if !parse_errors.is_empty() {
        summaries.push(CategorySummary {
            category_id: "parse".to_string(),
            title: "Parse errors".to_string(),
            status: crate::report::CategoryStatus::Fail,
            rules_applied: 0,
            rules_passed: 0,
            violations: parse_errors,
        });
    }

    let ratable: Vec<&CategorySummary> = summaries
        .iter()
        .filter(|s| s.status != crate::report::CategoryStatus::Skipped && s.category_id != "parse")
        .collect();
    let compliance_percentage = if ratable.is_empty() {
        None
    } else {
        let passed = ratable
            .iter()
            .filter(|s| s.status == crate::report::CategoryStatus::Pass)
            .count();
        Some((100.0 * passed as f64 / ratable.len() as f64 * 10.0).round() / 10.0)
    };

    let mut all_violations: Vec<Violation> = summaries
        .iter()
        .flat_map(|s| s.violations.iter().cloned())
        .collect();
    crate::report::sort_violations(&mut all_violations);

    ComplianceReport {
        tool_version: env!("CARGO_PKG_VERSION").to_string(),
        journal_id: config.journal.clone(),
        violations: all_violations,
        categories: summaries,
        compliance_percentage,
        skipped_rules: skipped,
    }
}
