//! Phase 4 acceptance harness for `jsslint_core::sarif`: the rendered
//! SARIF document must byte-match `jss-lint --output sarif` on real
//! multi-file papers, including `--source-root` variations that
//! exercise the path-relativization fallback (`os.path.relpath`-style
//! `..` segments for a source root outside the file's own directory).
//!
//! Skips entirely (doesn't fail) if the Python venv isn't set up.

use jsslint_core::config::ToolConfig;
use jsslint_core::engine::{self, ParsedDocument};
use jsslint_core::sarif;
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

/// `(paper directory, file names, ignore_rules, source_root)`.
/// `source_root` is `None` for "use the CLI default (cwd)"; `Some`
/// values cover: a source root the file is genuinely nested under, a
/// relative `..`, and a root entirely outside the file's directory
/// tree (forcing the `os.path.relpath` multi-`..` fallback).
type SarifCase = (
    &'static str,
    &'static [&'static str],
    &'static [&'static str],
    Option<&'static str>,
);
const CASES: &[SarifCase] = &[
    (
        "eval/recall-corpus/opentsne",
        &["main.tex", "references.bib"],
        &[],
        None,
    ),
    (
        "eval/recall-corpus/trueskill",
        &["article.tex", "gaming.bib", "journalsAbbr.bib"],
        &[],
        None,
    ),
    (
        "eval/recall-corpus/trueskill",
        &["article.tex", "gaming.bib"],
        &[],
        Some("/workspace"),
    ),
    (
        "eval/recall-corpus/trueskill",
        &["article.tex", "gaming.bib"],
        &[],
        Some(".."),
    ),
    (
        "eval/recall-corpus/trueskill",
        &["article.tex", "gaming.bib"],
        &[],
        Some("/tmp"),
    ),
];

fn python_oracle_sarif(
    jss_lint: &Path,
    dir: &Path,
    files: &[&str],
    ignore_rules: &[&str],
    source_root: Option<&str>,
) -> String {
    let mut cmd = Command::new(jss_lint);
    cmd.arg("--output").arg("sarif");
    if !ignore_rules.is_empty() {
        cmd.arg("--ignore-rules").arg(ignore_rules.join(","));
    }
    if let Some(root) = source_root {
        cmd.arg("--source-root").arg(root);
    }
    let output = cmd
        .args(files)
        .current_dir(dir)
        .output()
        .expect("failed to run jss-lint");
    assert!(
        output.status.success() || !output.stdout.is_empty(),
        "jss-lint failed with no stdout (exit {:?}): {}",
        output.status.code(),
        String::from_utf8_lossy(&output.stderr)
    );
    String::from_utf8(output.stdout).expect("oracle output must be valid UTF-8")
}

#[test]
fn sarif_render_matches_python_cli() {
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
    for &(paper_dir, files, ignore_rules, source_root) in CASES {
        let dir = root.join(paper_dir);
        let expected = python_oracle_sarif(&jss_lint, &dir, files, ignore_rules, source_root);

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

        // Match the oracle's cwd (the paper directory) so relative
        // `--source-root` values and the default (cwd) resolve the
        // same way on both sides.
        let prev_cwd = std::env::current_dir().unwrap();
        std::env::set_current_dir(&dir).unwrap();

        let mut config = ToolConfig {
            ignore_rules: ignore_rules.iter().map(|s| s.to_string()).collect(),
            ..ToolConfig::default()
        };
        if let Some(root_str) = source_root {
            config.source_root = PathBuf::from(root_str);
        }
        let report = engine::run(&config, &document);
        let actual = sarif::render(&report, &config);

        std::env::set_current_dir(&prev_cwd).unwrap();

        if actual != expected {
            mismatches.push(format!(
                "{paper_dir} source_root={source_root:?}\n  expected:\n{expected}\n  actual:\n{actual}"
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
