//! Phase 4 acceptance harness: `engine::run` + `json_output::render`
//! must byte-match the real `jss-lint --output json` on real
//! multi-file papers (tex + one-or-more bib files) from the recall
//! corpus — the tightest possible end-to-end check of document
//! assembly, rule dispatch, category/compliance-percentage
//! computation, and JSON rendering all together.
//!
//! Skips entirely (doesn't fail) if the Python venv isn't set up.

use jsslint_core::config::ToolConfig;
use jsslint_core::engine::{self, ParsedDocument};
use jsslint_core::json_output;
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

/// `(paper directory relative to repo root, file names within it,
/// rule ids to ignore on both sides)`. Picked to cover: a single tex +
/// single bib pair, and a single tex + two bib files (bib-rule
/// citation scope must union across both).
///
/// trueskill's `gaming.bib` has a title mentioning both "Julia" and
/// "Python" unwrapped (`Landfried-repo:ttt`) — `references.py`'s
/// `_title_mentions_unwrapped` used to pick the first hit by iterating
/// a `frozenset[str]`, whose order depends on Python's per-process
/// string-hash seed, so the reported language flipped between runs of
/// the same unmodified code. Fixed (both sides now pick the leftmost
/// match in the text, deterministically) — no ignore-list entry needed
/// here anymore.
const PAPERS: &[(&str, &[&str], &[&str])] = &[
    (
        "eval/recall-corpus/opentsne",
        &["main.tex", "references.bib"],
        &[],
    ),
    (
        "eval/recall-corpus/trueskill",
        &["article.tex", "gaming.bib", "journalsAbbr.bib"],
        &[],
    ),
];

/// Every `.Rnw` file in the recall corpus — the Definition of Done for
/// spec-023 (`.Rnw`/`.Rmd` support) is byte-identical output for EVERY
/// one of these, so the full set (not a sample) belongs here.
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

/// `.Rmd` fixtures — no recall corpus exists for `.Rmd` (see the
/// spec-023 plan), so these are the checked-in deterministic fixtures
/// instead: always present, no `eval-jss corpus fetch` dependency.
/// `malformed-yaml.Rmd` is deliberately excluded — its
/// `JSS-PARSE-000` warning embeds PyYAML's raw exception text, a
/// documented, out-of-scope parity gap (this crate uses its own YAML
/// parser's error message instead).
const RMD_FIXTURES: &[&str] = &[
    "tests/fixtures/compliant/minimal.Rmd",
    // Same content as `minimal.Rmd`, prefixed with a UTF-8 BOM
    // (U+FEFF) — regression coverage for the BOM-stripping fix in
    // `ParsedDocument::from_sources` (a BOM broke the `.Rmd`
    // frontmatter delimiter check, which isn't Unicode-whitespace-
    // aware, letting frontmatter fall through to being linted as
    // prose).
    "tests/fixtures/compliant/minimal-bom.Rmd",
    "tests/fixtures/violations/rmd/JSS-MARKUP-002-bad.Rmd",
    "tests/fixtures/violations/rmd/unterminated-frontmatter.Rmd",
    "tests/fixtures/violations/rmd/unterminated-fence.Rmd",
];

fn python_oracle_json(
    jss_lint: &Path,
    dir: &Path,
    files: &[&str],
    ignore_rules: &[&str],
) -> String {
    let mut cmd = Command::new(jss_lint);
    cmd.arg("--output").arg("json");
    if !ignore_rules.is_empty() {
        cmd.arg("--ignore-rules").arg(ignore_rules.join(","));
    }
    let output = cmd
        .args(files)
        .current_dir(dir)
        .output()
        .expect("failed to run jss-lint");
    // jss-lint exits 1 on any violation at/above --fail-on (default
    // "warning") — that's expected for real papers with findings, not
    // a failure of the oracle invocation itself. Only a missing binary
    // or a crash (no stdout at all) is a real problem.
    assert!(
        !output.stdout.is_empty(),
        "jss-lint produced no stdout (exit {:?}): {}",
        output.status.code(),
        String::from_utf8_lossy(&output.stderr)
    );
    String::from_utf8(output.stdout).expect("oracle output must be valid UTF-8")
}

#[test]
fn engine_run_matches_python_cli_json() {
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
    for &(paper_dir, files, ignore_rules) in PAPERS {
        let dir = root.join(paper_dir);
        let expected = python_oracle_json(&jss_lint, &dir, files, ignore_rules);

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
        let config = ToolConfig {
            ignore_rules: ignore_rules.iter().map(|s| s.to_string()).collect(),
            ..ToolConfig::default()
        };
        let report = engine::run(&config, &document);
        let actual = json_output::render(&report);

        if actual != expected {
            mismatches.push(format!(
                "{paper_dir}\n  expected:\n{expected}\n  actual:\n{actual}"
            ));
        }
    }

    assert!(
        mismatches.is_empty(),
        "{} paper mismatches:\n{}",
        mismatches.len(),
        mismatches.join("\n---\n")
    );
}

/// `.Rnw`/`.Rmd` counterpart of `engine_run_matches_python_cli_json`:
/// every recall-corpus `.Rnw` file plus every `.Rmd` fixture, each as a
/// single-file document, must byte-match `jss-lint --output json`.
#[test]
fn engine_run_matches_python_cli_json_rnw_rmd() {
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

        let expected = python_oracle_json(&jss_lint, dir, files, &[]);
        let source = std::fs::read_to_string(&full_path)
            .unwrap_or_else(|e| panic!("failed to read {}: {e}", full_path.display()));
        let document = ParsedDocument::from_sources(&[(file_name.to_string(), source)])
            .unwrap_or_else(|e| panic!("{rel_path}: failed to build ParsedDocument: {e}"));
        let report = engine::run(&ToolConfig::default(), &document);
        let actual = json_output::render(&report);

        if actual != expected {
            mismatches.push(format!(
                "{rel_path}\n  expected:\n{expected}\n  actual:\n{actual}"
            ));
        }
    }

    assert!(
        mismatches.is_empty(),
        "{} paper mismatches:\n{}",
        mismatches.len(),
        mismatches.join("\n---\n")
    );
}
