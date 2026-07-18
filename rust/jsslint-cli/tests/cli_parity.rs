//! Phase 4 end-to-end acceptance harness: the compiled `jsslint`
//! binary's stdout AND exit code must match the real `jss-lint`
//! binary on real multi-file papers — the plan's "binary smoke test"
//! criterion (`jsslint paper.tex` exits with the right code and
//! output), run as an actual differential test rather than a manual
//! check.
//!
//! Skips entirely (doesn't fail) if the Python venv isn't set up.

use std::path::PathBuf;
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

const OUTPUT_FORMATS: &[&str] = &["json", "sarif"];

/// Every `.Rnw` file in the recall corpus (see `engine_parity.rs` in
/// `jsslint-core/tests` for why the full set, not a sample).
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

/// `.Rmd` fixtures (see `engine_parity.rs` for why fixtures, not a
/// recall corpus, and why `malformed-yaml.Rmd` is excluded).
const RMD_FIXTURES: &[&str] = &[
    "tests/fixtures/compliant/minimal.Rmd",
    "tests/fixtures/violations/rmd/JSS-MARKUP-002-bad.Rmd",
    "tests/fixtures/violations/rmd/unterminated-frontmatter.Rmd",
    "tests/fixtures/violations/rmd/unterminated-fence.Rmd",
];

struct Outcome {
    stdout: String,
    exit_code: Option<i32>,
}

fn run(bin: &str, dir: &PathBuf, files: &[&str], ignore_rules: &[&str], output: &str) -> Outcome {
    let mut cmd = Command::new(bin);
    cmd.arg("--output").arg(output);
    if !ignore_rules.is_empty() {
        cmd.arg("--ignore-rules").arg(ignore_rules.join(","));
    }
    let output = cmd
        .args(files)
        .current_dir(dir)
        .output()
        .unwrap_or_else(|e| panic!("failed to run {bin}: {e}"));
    Outcome {
        stdout: String::from_utf8(output.stdout).expect("stdout must be valid UTF-8"),
        exit_code: output.status.code(),
    }
}

#[test]
fn cli_matches_python_cli_end_to_end() {
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
    let jss_lint = jss_lint.to_string_lossy().to_string();
    let jsslint_bin = env!("CARGO_BIN_EXE_jsslint");

    let mut mismatches = Vec::new();
    for &(paper_dir, files, ignore_rules) in PAPERS {
        let dir = root.join(paper_dir);
        for &output in OUTPUT_FORMATS {
            let expected = run(&jss_lint, &dir, files, ignore_rules, output);
            let actual = run(jsslint_bin, &dir, files, ignore_rules, output);

            if actual.stdout != expected.stdout {
                mismatches.push(format!(
                    "{paper_dir} [--output {output}] STDOUT differs\n  expected:\n{}\n  actual:\n{}",
                    expected.stdout, actual.stdout
                ));
            }
            if actual.exit_code != expected.exit_code {
                mismatches.push(format!(
                    "{paper_dir} [--output {output}] EXIT CODE differs: expected {:?}, actual {:?}",
                    expected.exit_code, actual.exit_code
                ));
            }
        }
    }

    assert!(
        mismatches.is_empty(),
        "{} mismatches:\n{}",
        mismatches.len(),
        mismatches.join("\n---\n")
    );
}

/// `.Rnw`/`.Rmd` counterpart of `cli_matches_python_cli_end_to_end`:
/// exit codes matter here too — `.Rmd`'s unterminated-frontmatter/fence
/// fixtures exit 2 (fatal `JSS-PARSE-000`), exercising
/// `determine_exit_code`'s fatal-parse-error path for the first time
/// with real `.Rmd` input.
#[test]
fn cli_matches_python_cli_end_to_end_rnw_rmd() {
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
    let jss_lint = jss_lint.to_string_lossy().to_string();
    let jsslint_bin = env!("CARGO_BIN_EXE_jsslint");

    let mut mismatches = Vec::new();
    for &rel_path in RNW_PAPERS.iter().chain(RMD_FIXTURES) {
        let full_path = root.join(rel_path);
        let dir = full_path.parent().unwrap().to_path_buf();
        let file_name = full_path.file_name().unwrap().to_str().unwrap();
        let files = &[file_name];
        for &output in OUTPUT_FORMATS {
            let expected = run(&jss_lint, &dir, files, &[], output);
            let actual = run(jsslint_bin, &dir, files, &[], output);

            if actual.stdout != expected.stdout {
                mismatches.push(format!(
                    "{rel_path} [--output {output}] STDOUT differs\n  expected:\n{}\n  actual:\n{}",
                    expected.stdout, actual.stdout
                ));
            }
            if actual.exit_code != expected.exit_code {
                mismatches.push(format!(
                    "{rel_path} [--output {output}] EXIT CODE differs: expected {:?}, actual {:?}",
                    expected.exit_code, actual.exit_code
                ));
            }
        }
    }

    assert!(
        mismatches.is_empty(),
        "{} mismatches:\n{}",
        mismatches.len(),
        mismatches.join("\n---\n")
    );
}
