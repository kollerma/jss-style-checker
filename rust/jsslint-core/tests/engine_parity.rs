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
/// `_title_mentions_unwrapped` picks the first hit by iterating a
/// `frozenset[str]`, whose iteration order depends on Python's
/// per-process string-hash seed (`PYTHONHASHSEED` is randomized by
/// default since Python 3.3). Confirmed by invoking the oracle
/// standalone several times in a row: the reported language flips
/// between "R", "Python", and "Julia" across runs of the *same*
/// unmodified Python code — this is a real latent nondeterminism in
/// the reference implementation, not a Rust-port bug, and there is no
/// single "correct" answer to match. JSS-REFS-004 is ignored on both
/// sides for this paper so the rest of the ~450 other violations
/// still get exact byte-for-byte coverage.
const PAPERS: &[(&str, &[&str], &[&str])] = &[
    (
        "eval/recall-corpus/opentsne",
        &["main.tex", "references.bib"],
        &[],
    ),
    (
        "eval/recall-corpus/trueskill",
        &["article.tex", "gaming.bib", "journalsAbbr.bib"],
        &["JSS-REFS-004"],
    ),
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
