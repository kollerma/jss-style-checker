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

/// Spec 013 multi-file resolve fixtures, under
/// `tests/fixtures/resolver_projects/` — mirrors
/// `tests/integration/test_cli_resolve.py`.
///   * `basic/root.tex` \input's intro.tex (JSS-CODE-002) and
///     \bibliography{refs}'s refs.bib, cited (JSS-REFS-003).
///   * `cycle/a.tex` <-> `b.tex` mutual \input (JSS-PROJECT-001).
///   * `missing/root.tex` \input{ghost}, unresolvable (JSS-PROJECT-002).
const RESOLVER_PROJECTS_DIR: &str = "tests/fixtures/resolver_projects";

struct Outcome {
    stdout: String,
    exit_code: Option<i32>,
}

fn run(bin: &str, dir: &PathBuf, files: &[&str], ignore_rules: &[&str], output: &str) -> Outcome {
    run_with_flags(bin, dir, files, ignore_rules, output, &[])
}

fn run_with_flags(
    bin: &str,
    dir: &PathBuf,
    files: &[&str],
    ignore_rules: &[&str],
    output: &str,
    extra_flags: &[&str],
) -> Outcome {
    run_with_env(bin, dir, files, ignore_rules, output, extra_flags, &[])
}

fn run_with_env(
    bin: &str,
    dir: &PathBuf,
    files: &[&str],
    ignore_rules: &[&str],
    output: &str,
    extra_flags: &[&str],
    env: &[(&str, &str)],
) -> Outcome {
    let mut cmd = Command::new(bin);
    cmd.arg("--output").arg(output);
    if !ignore_rules.is_empty() {
        cmd.arg("--ignore-rules").arg(ignore_rules.join(","));
    }
    cmd.args(extra_flags);
    for &(key, value) in env {
        cmd.env(key, value);
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

/// Spec 013: `\input`/`\include`/`\subfile`/`\bibliography`
/// auto-resolution, and `--no-resolve` genuinely disabling it — the
/// multi-file counterpart of `cli_matches_python_cli_end_to_end`.
/// Covers: a single root file auto-resolving into its whole graph
/// (diagnostics attributed to the *included* files, byte-identical
/// across every `--output` format); `--no-resolve` collapsing back to
/// root-only; a cycle (`JSS-PROJECT-001`) and a missing reference
/// (`JSS-PROJECT-002`); and an explicit multi-file invocation of the
/// same cycle fixture NOT auto-resolving (FR-003).
#[test]
fn cli_resolve_matches_python_cli_end_to_end() {
    let root = repo_root();
    let jss_lint = root.join(".venv/bin/jss-lint");
    if !jss_lint.exists() {
        eprintln!(
            "SKIP: {} not found (Python venv not set up)",
            jss_lint.display()
        );
        return;
    }
    let jss_lint = jss_lint.to_string_lossy().to_string();
    let jsslint_bin = env!("CARGO_BIN_EXE_jsslint");
    let projects = root.join(RESOLVER_PROJECTS_DIR);

    let mut mismatches = Vec::new();

    // (subdir, root file) — root-only cases exercised both with and
    // without `--no-resolve`. `latin1_root`/`latin1_included` cover
    // the lenient UTF-8-decode fallback (a non-UTF-8 file, as the
    // root and as an \input target, degrades to a warning-severity
    // JSS-PARSE-000 instead of aborting the run). `multi_bib` covers
    // comma-separated `\bibliography{a,b}` resolving each name
    // independently, not as one literal "a,b.bib" target. `rnw_root`/
    // `rmd_root` cover a non-.tex root suffix. `nonlintable_target`
    // covers a resolved \input target with an unsupported suffix
    // (walked but not linted). `subfile` covers \subfile. `mixed_sort_
    // order` pins Violation.sort_key's column-bucket ordering (None
    // before int) between a JSS-PROJECT-* violation and an ordinary
    // rule violation on the same file/line.
    let cases: &[(&str, &str)] = &[
        ("basic", "root.tex"),
        ("cycle", "a.tex"),
        ("missing", "root.tex"),
        ("latin1_root", "root.tex"),
        ("latin1_included", "root.tex"),
        ("multi_bib", "root.tex"),
        ("rnw_root", "root.Rnw"),
        ("rmd_root", "root.Rmd"),
        ("nonlintable_target", "root.tex"),
        ("subfile", "root.tex"),
        ("multi_missing_multi_cycle", "root.tex"),
        ("mixed_sort_order", "root.tex"),
    ];
    for &(subdir, file) in cases {
        let dir = projects.join(subdir);
        for &no_resolve in &[false, true] {
            let flags: &[&str] = if no_resolve { &["--no-resolve"] } else { &[] };
            for &output in OUTPUT_FORMATS {
                let expected = run_with_flags(&jss_lint, &dir, &[file], &[], output, flags);
                let actual = run_with_flags(jsslint_bin, &dir, &[file], &[], output, flags);
                let label = format!(
                    "{subdir}/{file} [--output {output}]{}",
                    if no_resolve { " --no-resolve" } else { "" }
                );
                if actual.stdout != expected.stdout {
                    mismatches.push(format!(
                        "{label} STDOUT differs\n  expected:\n{}\n  actual:\n{}",
                        expected.stdout, actual.stdout
                    ));
                }
                if actual.exit_code != expected.exit_code {
                    mismatches.push(format!(
                        "{label} EXIT CODE differs: expected {:?}, actual {:?}",
                        expected.exit_code, actual.exit_code
                    ));
                }
            }
        }
    }

    // Explicit multi-file invocation of the cycle fixture: FR-003 says
    // this must NOT auto-resolve (no JSS-PROJECT-001), unlike the
    // single-file `cycle/a.tex` case above.
    {
        let dir = projects.join("cycle");
        for &output in OUTPUT_FORMATS {
            let expected = run(&jss_lint, &dir, &["a.tex", "b.tex"], &[], output);
            let actual = run(jsslint_bin, &dir, &["a.tex", "b.tex"], &[], output);
            let label = format!("cycle/a.tex+b.tex explicit [--output {output}]");
            if actual.stdout != expected.stdout {
                mismatches.push(format!(
                    "{label} STDOUT differs\n  expected:\n{}\n  actual:\n{}",
                    expected.stdout, actual.stdout
                ));
            }
            if actual.exit_code != expected.exit_code {
                mismatches.push(format!(
                    "{label} EXIT CODE differs: expected {:?}, actual {:?}",
                    expected.exit_code, actual.exit_code
                ));
            }
        }
    }

    // TEXINPUTS/BIBINPUTS search-path resolution: the \input/\bibliography
    // target lives in a sibling directory found only via the env var,
    // not the root's own directory.
    let env_cases: &[(&str, &str, &str, &str)] = &[
        ("texinputs", "root.tex", "TEXINPUTS", "extra"),
        ("bibinputs", "root.tex", "BIBINPUTS", "extra"),
    ];
    for &(subdir, file, env_key, extra_subdir) in env_cases {
        let dir = projects.join(subdir).join("root");
        let extra_dir = projects.join(subdir).join(extra_subdir);
        let extra_dir_str = extra_dir.to_string_lossy().to_string();
        for &output in OUTPUT_FORMATS {
            let env: &[(&str, &str)] = &[(env_key, extra_dir_str.as_str())];
            let expected = run_with_env(&jss_lint, &dir, &[file], &[], output, &[], env);
            let actual = run_with_env(jsslint_bin, &dir, &[file], &[], output, &[], env);
            let label = format!("{subdir}/root/{file} [{env_key}] [--output {output}]");
            if actual.stdout != expected.stdout {
                mismatches.push(format!(
                    "{label} STDOUT differs\n  expected:\n{}\n  actual:\n{}",
                    expected.stdout, actual.stdout
                ));
            }
            if actual.exit_code != expected.exit_code {
                mismatches.push(format!(
                    "{label} EXIT CODE differs: expected {:?}, actual {:?}",
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
