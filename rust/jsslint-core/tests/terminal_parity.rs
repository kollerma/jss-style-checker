//! Phase 4 acceptance harness for `jsslint_core::terminal`: the
//! rendered text must byte-match the real (non-tty) `jss-lint` output
//! across author mode, reviewer mode, and verbose/skipped-rules mode,
//! on real multi-file papers plus a couple of hand-built edge cases
//! (a document with only a `.tex` file and no `.bib`, and vice versa,
//! which exercise the engine's format-gate: an unrestricted-format
//! rule still counts as applied/passed with zero matching files, as
//! long as the document has *some* file).
//!
//! Skips entirely (doesn't fail) if the Python venv isn't set up.

use jsslint_core::config::{Mode, ToolConfig};
use jsslint_core::engine::{self, ParsedDocument};
use jsslint_core::terminal;
use std::path::{Path, PathBuf};
use std::process::Command;

mod common;

fn repo_root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .parent()
        .unwrap()
        .to_path_buf()
}

/// `(paper directory, file names, ignore_rules, extra CLI args)`.
type PaperCase = (
    &'static str,
    &'static [&'static str],
    &'static [&'static str],
    &'static [&'static str],
);
const PAPERS: &[PaperCase] = &[
    (
        "eval/recall-corpus/opentsne",
        &["main.tex", "references.bib"],
        &[],
        &[],
    ),
    (
        "eval/recall-corpus/opentsne",
        &["main.tex", "references.bib"],
        &[],
        &["--mode", "reviewer"],
    ),
    (
        "eval/recall-corpus/opentsne",
        &["main.tex", "references.bib"],
        &[],
        &["-v", "--min-confidence", "high"],
    ),
    (
        "eval/recall-corpus/trueskill",
        &["article.tex", "gaming.bib", "journalsAbbr.bib"],
        &[],
        &[],
    ),
    (
        "eval/recall-corpus/trueskill",
        &["article.tex", "gaming.bib", "journalsAbbr.bib"],
        &[],
        &["--mode", "reviewer"],
    ),
];

/// Every `.Rnw` file in the recall corpus (see `engine_parity.rs`'s
/// identical constant for why the full set, not a sample) — this is
/// also the harness that caught a real `round()`-vs-`round_ties_even()`
/// table-column-width bug (`pmclust-guide.Rnw`, 2 violations was
/// exactly the row count where the rounding tie showed up).
const RNW_PAPERS: &[&str] = &[
    "eval/recall-corpus/CARBayesST/CARBayesST.Rnw",
    "eval/recall-corpus/clifford/clifford.Rnw",
    "eval/recall-corpus/CUB/CUBvignette-knitr.Rnw",
    "eval/recall-corpus/cusp/Cusp-JSS.Rnw",
    "eval/recall-corpus/DBR/DBR.Rnw",
    "eval/recall-corpus/deSolve/deSolve.Rnw",
    "eval/recall-corpus/HardyWeinberg/HardyWeinberg.Rnw",
    "eval/recall-corpus/mlt.docreg/mlt.Rnw",
    "eval/recall-corpus/pmclust/pmclust-guide.Rnw",
    "eval/recall-corpus/robustlmm/simulationStudies.Rnw",
    "eval/recall-corpus/rstpm2/multistate.Rnw",
    "eval/recall-corpus/SightabilityModel/a-SightabilityModel.Rnw",
    "eval/recall-corpus/spacetime/jss816.Rnw",
];

/// `.Rmd` fixtures (see `engine_parity.rs`'s identical constant for
/// why fixtures, not a recall corpus, and why `malformed-yaml.Rmd` is
/// excluded).
const RMD_FIXTURES: &[&str] = &[
    "tests/fixtures/compliant/minimal.Rmd",
    "tests/fixtures/violations/rmd/JSS-MARKUP-002-bad.Rmd",
    "tests/fixtures/violations/rmd/unterminated-frontmatter.Rmd",
    "tests/fixtures/violations/rmd/unterminated-fence.Rmd",
];

fn python_oracle_terminal(
    jss_lint: &Path,
    dir: &Path,
    files: &[&str],
    ignore_rules: &[&str],
    extra_args: &[&str],
) -> String {
    let mut cmd = Command::new(jss_lint);
    if !ignore_rules.is_empty() {
        cmd.arg("--ignore-rules").arg(ignore_rules.join(","));
    }
    cmd.args(extra_args);
    let output = cmd
        .args(files)
        .current_dir(dir)
        .output()
        .expect("failed to run jss-lint");
    assert!(
        !output.stdout.is_empty() || !output.stderr.is_empty() || output.status.success(),
        "jss-lint produced no output at all (exit {:?})",
        output.status.code()
    );
    String::from_utf8(output.stdout).expect("oracle output must be valid UTF-8")
}

fn apply_extra_args(config: &mut ToolConfig, extra_args: &[&str]) {
    let mut i = 0;
    while i < extra_args.len() {
        match extra_args[i] {
            "--mode" => {
                config.mode = if extra_args[i + 1] == "reviewer" {
                    Mode::Reviewer
                } else {
                    Mode::Author
                };
                i += 2;
            }
            "-v" => {
                config.verbose = true;
                i += 1;
            }
            "--min-confidence" => {
                config.min_confidence =
                    jsslint_core::config::ConfidenceTier::parse(extra_args[i + 1])
                        .unwrap_or(config.min_confidence);
                i += 2;
            }
            other => panic!("terminal_parity: unhandled extra arg {other:?}"),
        }
    }
}

#[test]
fn terminal_render_matches_python_cli() {
    let root = repo_root();
    let jss_lint = root.join(".venv/bin/jss-lint");
    if !jss_lint.exists() {
        eprintln!(
            "SKIP: {} not found (Python venv not set up)",
            jss_lint.display()
        );
        return;
    }
    if let Some(msg) = common::corpus_missing(
        &root,
        &[
            "eval/recall-corpus/opentsne/main.tex",
            "eval/recall-corpus/trueskill/article.tex",
        ],
    ) {
        eprintln!("{msg}");
        return;
    }

    let mut mismatches = Vec::new();
    for &(paper_dir, files, ignore_rules, extra_args) in PAPERS {
        let dir = root.join(paper_dir);
        let expected = python_oracle_terminal(&jss_lint, &dir, files, ignore_rules, extra_args);

        let sources: Vec<(String, String)> = files
            .iter()
            .map(|f| {
                let path = dir.join(f);
                let source = std::fs::read_to_string(&path)
                    .unwrap_or_else(|e| panic!("failed to read {}: {e}", path.display()));
                (f.to_string(), source)
            })
            .collect();
        let document = ParsedDocument::from_sources(&sources)
            .unwrap_or_else(|e| panic!("{paper_dir}: failed to build ParsedDocument: {e}"));
        let mut config = ToolConfig {
            ignore_rules: ignore_rules.iter().map(|s| s.to_string()).collect(),
            ..ToolConfig::default()
        };
        apply_extra_args(&mut config, extra_args);
        let report = engine::run(&config, &document);
        let actual = terminal::render(&report, &config);

        if actual != expected {
            mismatches.push(format!(
                "{paper_dir} {extra_args:?}\n  expected:\n{expected}\n  actual:\n{actual}"
            ));
        }
    }

    assert!(
        mismatches.is_empty(),
        "{} mismatches:\n{}",
        mismatches.len(),
        mismatches.join("\n---\n")
    );
}

/// `.Rnw`/`.Rmd` counterpart of `terminal_render_matches_python_cli`.
#[test]
fn terminal_render_matches_python_cli_rnw_rmd() {
    let root = repo_root();
    let jss_lint = root.join(".venv/bin/jss-lint");
    if !jss_lint.exists() {
        eprintln!(
            "SKIP: {} not found (Python venv not set up)",
            jss_lint.display()
        );
        return;
    }
    if let Some(msg) = common::corpus_missing(&root, RNW_PAPERS) {
        eprintln!("{msg}");
        return;
    }

    let mut mismatches = Vec::new();
    for &rel_path in RNW_PAPERS.iter().chain(RMD_FIXTURES) {
        let full_path = root.join(rel_path);
        let dir = full_path.parent().unwrap();
        let file_name = full_path.file_name().unwrap().to_str().unwrap();
        let files = &[file_name];

        let expected = python_oracle_terminal(&jss_lint, dir, files, &[], &[]);
        let source = std::fs::read_to_string(&full_path)
            .unwrap_or_else(|e| panic!("failed to read {}: {e}", full_path.display()));
        let document = ParsedDocument::from_sources(&[(file_name.to_string(), source)])
            .unwrap_or_else(|e| panic!("{rel_path}: failed to build ParsedDocument: {e}"));
        let config = ToolConfig::default();
        let report = engine::run(&config, &document);
        let actual = terminal::render(&report, &config);

        if actual != expected {
            mismatches.push(format!(
                "{rel_path}\n  expected:\n{expected}\n  actual:\n{actual}"
            ));
        }
    }

    assert!(
        mismatches.is_empty(),
        "{} mismatches:\n{}",
        mismatches.len(),
        mismatches.join("\n---\n")
    );
}

#[test]
fn terminal_render_format_gate_edge_cases() {
    let root = repo_root();
    let jss_lint = root.join(".venv/bin/jss-lint");
    if !jss_lint.exists() {
        eprintln!(
            "SKIP: {} not found (Python venv not set up)",
            jss_lint.display()
        );
        return;
    }

    let scratch = std::env::temp_dir().join("jsslint-terminal-parity-edge-cases");
    std::fs::create_dir_all(&scratch).unwrap();

    let tex_only = scratch.join("trivial.tex");
    std::fs::write(
        &tex_only,
        "\\documentclass[article]{jss}\n\\begin{document}\n\\end{document}\n",
    )
    .unwrap();
    let bib_only = scratch.join("trivial.bib");
    std::fs::write(
        &bib_only,
        "@article{foo2020, author={A. B.}, title={A Title}, journal={J}, year={2020}}\n",
    )
    .unwrap();

    let cases: &[(&Path, &str)] = &[(&tex_only, "trivial.tex"), (&bib_only, "trivial.bib")];

    let mut mismatches = Vec::new();
    for &(path, filename) in cases {
        let expected = {
            let mut cmd = Command::new(&jss_lint);
            cmd.arg("--mode").arg("reviewer").arg(filename);
            cmd.current_dir(&scratch);
            let output = cmd.output().expect("failed to run jss-lint");
            String::from_utf8(output.stdout).unwrap()
        };

        let source = std::fs::read_to_string(path).unwrap();
        let sources = vec![(filename.to_string(), source)];
        let document = ParsedDocument::from_sources(&sources).unwrap();
        let config = ToolConfig {
            mode: Mode::Reviewer,
            ..ToolConfig::default()
        };
        let report = engine::run(&config, &document);
        let actual = terminal::render(&report, &config);

        if actual != expected {
            mismatches.push(format!(
                "{filename}\n  expected:\n{expected}\n  actual:\n{actual}"
            ));
        }
    }

    assert!(
        mismatches.is_empty(),
        "{} mismatches:\n{}",
        mismatches.len(),
        mismatches.join("\n---\n")
    );
}
