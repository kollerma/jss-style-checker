//! Phase 4 end-to-end acceptance harness for `--output html`
//! (`jsslint_core::html_output`, `author.html.j2`/`reviewer.html.j2`
//! hand-translated to Rust string-building): runs the real `jss-lint
//! --output html` and the compiled `jsslint --output html` over real
//! recall-corpus papers (both author and reviewer mode) plus a
//! zero-violations compliant fixture, and diffs stdout byte-for-byte.
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

fn run(bin: &str, root: &PathBuf, args: &[&str]) -> (String, Option<i32>) {
    let output = Command::new(bin)
        .args(args)
        .current_dir(root)
        .output()
        .unwrap_or_else(|e| panic!("failed to run {bin}: {e}"));
    (
        String::from_utf8_lossy(&output.stdout).into_owned(),
        output.status.code(),
    )
}

#[test]
fn html_output_matches_python_cli() {
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
            "eval/recall-corpus/CARBayesST/CARBayesST.Rnw",
        ],
    ) {
        eprintln!("{msg}");
        return;
    }
    let jss_lint = jss_lint.to_string_lossy().to_string();
    let jsslint_bin = env!("CARGO_BIN_EXE_jsslint");

    let cases: &[(&str, &[&str])] = &[
        (
            "opentsne-author",
            &[
                "--output",
                "html",
                "eval/recall-corpus/opentsne/main.tex",
                "eval/recall-corpus/opentsne/references.bib",
            ],
        ),
        (
            "opentsne-reviewer",
            &[
                "--output",
                "html",
                "--mode",
                "reviewer",
                "eval/recall-corpus/opentsne/main.tex",
                "eval/recall-corpus/opentsne/references.bib",
            ],
        ),
        (
            "trueskill-author",
            &[
                "--output",
                "html",
                "eval/recall-corpus/trueskill/article.tex",
                "eval/recall-corpus/trueskill/gaming.bib",
                "eval/recall-corpus/trueskill/journalsAbbr.bib",
            ],
        ),
        (
            "trueskill-reviewer",
            &[
                "--output",
                "html",
                "--mode",
                "reviewer",
                "eval/recall-corpus/trueskill/article.tex",
                "eval/recall-corpus/trueskill/gaming.bib",
                "eval/recall-corpus/trueskill/journalsAbbr.bib",
            ],
        ),
        (
            "compliant-author-no-violations",
            &["--output", "html", "tests/fixtures/compliant/minimal.tex"],
        ),
        (
            "compliant-reviewer-no-violations",
            &[
                "--output",
                "html",
                "--mode",
                "reviewer",
                "tests/fixtures/compliant/minimal.tex",
            ],
        ),
        // Every `.Rnw` file in the recall corpus (author mode) — the
        // Definition of Done for spec-023 is byte-identical output for
        // every one of these, so the full set belongs here.
        (
            "rnw-CARBayesST",
            &[
                "--output",
                "html",
                "eval/recall-corpus/CARBayesST/CARBayesST.Rnw",
            ],
        ),
        (
            "rnw-clifford",
            &[
                "--output",
                "html",
                "eval/recall-corpus/clifford/clifford.Rnw",
            ],
        ),
        (
            "rnw-CUB",
            &[
                "--output",
                "html",
                "eval/recall-corpus/CUB/CUBvignette-knitr.Rnw",
            ],
        ),
        (
            "rnw-cusp",
            &["--output", "html", "eval/recall-corpus/cusp/Cusp-JSS.Rnw"],
        ),
        (
            "rnw-DBR",
            &["--output", "html", "eval/recall-corpus/DBR/DBR.Rnw"],
        ),
        (
            "rnw-deSolve",
            &["--output", "html", "eval/recall-corpus/deSolve/deSolve.Rnw"],
        ),
        (
            "rnw-HardyWeinberg-reviewer",
            &[
                "--output",
                "html",
                "--mode",
                "reviewer",
                "eval/recall-corpus/HardyWeinberg/HardyWeinberg.Rnw",
            ],
        ),
        (
            "rnw-mlt",
            &["--output", "html", "eval/recall-corpus/mlt.docreg/mlt.Rnw"],
        ),
        (
            "rnw-pmclust",
            &[
                "--output",
                "html",
                "eval/recall-corpus/pmclust/pmclust-guide.Rnw",
            ],
        ),
        (
            "rnw-robustlmm",
            &[
                "--output",
                "html",
                "eval/recall-corpus/robustlmm/simulationStudies.Rnw",
            ],
        ),
        (
            "rnw-rstpm2",
            &[
                "--output",
                "html",
                "eval/recall-corpus/rstpm2/multistate.Rnw",
            ],
        ),
        (
            "rnw-SightabilityModel",
            &[
                "--output",
                "html",
                "eval/recall-corpus/SightabilityModel/a-SightabilityModel.Rnw",
            ],
        ),
        (
            "rnw-spacetime",
            &[
                "--output",
                "html",
                "eval/recall-corpus/spacetime/jss816.Rnw",
            ],
        ),
        // `.Rmd` fixtures — no recall corpus exists for `.Rmd` (see the
        // spec-023 plan), so these are the checked-in deterministic
        // fixtures. `malformed-yaml.Rmd` is excluded (documented,
        // out-of-scope PyYAML-message-text parity gap).
        (
            "rmd-minimal",
            &["--output", "html", "tests/fixtures/compliant/minimal.Rmd"],
        ),
        // Same content, prefixed with a UTF-8 BOM — regression
        // coverage for the BOM-stripping fix in
        // `ParsedDocument::from_sources`.
        (
            "rmd-minimal-bom",
            &[
                "--output",
                "html",
                "tests/fixtures/compliant/minimal-bom.Rmd",
            ],
        ),
        (
            "rmd-markup-002-bad",
            &[
                "--output",
                "html",
                "tests/fixtures/violations/rmd/JSS-MARKUP-002-bad.Rmd",
            ],
        ),
        (
            "rmd-unterminated-frontmatter",
            &[
                "--output",
                "html",
                "tests/fixtures/violations/rmd/unterminated-frontmatter.Rmd",
            ],
        ),
        (
            "rmd-unterminated-fence",
            &[
                "--output",
                "html",
                "tests/fixtures/violations/rmd/unterminated-fence.Rmd",
            ],
        ),
    ];

    let mut mismatches = Vec::new();
    for &(name, args) in cases {
        let (expected, expected_code) = run(&jss_lint, &root, args);
        let (actual, actual_code) = run(jsslint_bin, &root, args);
        if actual != expected {
            mismatches.push(format!(
                "{name} STDOUT differs\n  expected ({} bytes):\n{}\n  actual ({} bytes):\n{}",
                expected.len(),
                expected,
                actual.len(),
                actual
            ));
        }
        if actual_code != expected_code {
            mismatches.push(format!(
                "{name} EXIT CODE differs: expected {expected_code:?}, actual {actual_code:?}"
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
