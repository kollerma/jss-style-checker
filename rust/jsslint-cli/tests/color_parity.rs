//! Colour parity (spec 027 item F, `contracts/color.md` C-7).
//!
//! What must agree across engines is the **decision** — whether to
//! colour at all — and the **stripped** stream. The escape bytes
//! themselves are explicitly *not* a parity target (`color.md` C-4, a
//! documented §XIII divergence): Python lets rich emit them, this engine
//! writes SGR at render time, and nobody diffs coloured output between
//! engines. Diffing it would cost a post-render parser and shared
//! goldens for a stream no tool consumes.
//!
//! So each case below asserts three things: both engines agree on
//! whether any `\x1b[` appears at all; neither emits escapes in JSON;
//! and stripping the escapes leaves two byte-identical plain streams.
//!
//! Skips entirely (doesn't fail) if the Python venv isn't set up.

use std::collections::HashMap;
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

const SOURCE: &str = "\\documentclass[article]{jss}\n\
                      \\title{A Short Demo}\n\
                      \\Abstract{Demo.}\n\
                      \\Keywords{Demo}\n\
                      \\Address{Demo}\n\
                      \\begin{document}\n\
                      \\section{Methods And Results}\n\
                      We use R for everything.\n\
                      \\end{document}\n";

fn strip_sgr(text: &str) -> String {
    let mut out = String::with_capacity(text.len());
    let mut chars = text.chars().peekable();
    while let Some(c) = chars.next() {
        if c == '\u{1b}' && chars.peek() == Some(&'[') {
            chars.next();
            for c in chars.by_ref() {
                if c == 'm' {
                    break;
                }
            }
            continue;
        }
        out.push(c);
    }
    out
}

fn run_with_env(bin: &str, args: &[&str], cwd: &Path, env: &HashMap<&str, &str>) -> String {
    let mut cmd = Command::new(bin);
    cmd.args(args).current_dir(cwd);
    // A clean slate for the two variables under test, so an inherited
    // NO_COLOR in the developer's shell cannot mask a regression.
    cmd.env_remove("NO_COLOR").env_remove("CLICOLOR_FORCE");
    for (key, value) in env {
        cmd.env(key, value);
    }
    let output = cmd
        .output()
        .unwrap_or_else(|e| panic!("failed to run {bin}: {e}"));
    String::from_utf8_lossy(&output.stdout).into_owned()
}

#[test]
fn colour_decision_matches_python_cli() {
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

    let dir = std::env::temp_dir().join("jsslint-color-parity");
    let _ = std::fs::remove_dir_all(&dir);
    std::fs::create_dir_all(&dir).expect("create scratch dir");
    std::fs::write(dir.join("paper.tex"), SOURCE).expect("write fixture");

    // (name, args, env, expect colour). Neither CLI's stdout is a TTY
    // here, so `auto` is off unless something forces it on.
    let cases: &[(&str, &[&str], &[(&str, &str)], bool)] = &[
        ("piped auto", &["paper.tex"], &[], false),
        ("--color always", &["--color", "always", "paper.tex"], &[], true),
        ("NO_COLOR", &["paper.tex"], &[("NO_COLOR", "1")], false),
        (
            "CLICOLOR_FORCE",
            &["paper.tex"],
            &[("CLICOLOR_FORCE", "1")],
            true,
        ),
        (
            "NO_COLOR beats CLICOLOR_FORCE",
            &["paper.tex"],
            &[("NO_COLOR", "1"), ("CLICOLOR_FORCE", "1")],
            false,
        ),
        (
            "--color always beats NO_COLOR",
            &["--color", "always", "paper.tex"],
            &[("NO_COLOR", "1")],
            true,
        ),
        (
            "--color never beats CLICOLOR_FORCE",
            &["--color", "never", "paper.tex"],
            &[("CLICOLOR_FORCE", "1")],
            false,
        ),
        (
            "TERM=dumb",
            &["paper.tex"],
            &[("CLICOLOR_FORCE", "0"), ("TERM", "dumb")],
            false,
        ),
        // JSON is never coloured, whatever the decision says.
        (
            "json with --color always",
            &["--output", "json", "--color", "always", "paper.tex"],
            &[],
            false,
        ),
        (
            "reviewer --color always",
            &["--mode", "reviewer", "--color", "always", "paper.tex"],
            &[],
            true,
        ),
    ];

    let mut failures = Vec::new();
    for (name, args, env_pairs, expect_color) in cases {
        let env: HashMap<&str, &str> = env_pairs.iter().copied().collect();
        let py = run_with_env(&jss_lint, args, &dir, &env);
        let rs = run_with_env(jsslint_bin, args, &dir, &env);

        for (engine, out) in [("python", &py), ("rust", &rs)] {
            let has_escapes = out.contains('\u{1b}');
            if has_escapes != *expect_color {
                failures.push(format!(
                    "{name}: {engine} colour={has_escapes}, expected {expect_color}"
                ));
            }
        }
        if strip_sgr(&py) != strip_sgr(&rs) {
            failures.push(format!(
                "{name}: stripped streams differ\n  python:\n{}\n  rust:\n{}",
                strip_sgr(&py),
                strip_sgr(&rs)
            ));
        }
    }

    // The TOML key, which both loaders must read the same way.
    std::fs::write(dir.join(".jss-lint.toml"), "color = \"always\"\n")
        .expect("write config");
    let env = HashMap::new();
    let py = run_with_env(&jss_lint, &["paper.tex"], &dir, &env);
    let rs = run_with_env(jsslint_bin, &["paper.tex"], &dir, &env);
    for (engine, out) in [("python", &py), ("rust", &rs)] {
        if !out.contains('\u{1b}') {
            failures.push(format!("TOML color=always: {engine} did not colourise"));
        }
    }
    if strip_sgr(&py) != strip_sgr(&rs) {
        failures.push("TOML color=always: stripped streams differ".to_string());
    }

    assert!(
        failures.is_empty(),
        "{} case(s) diverge:\n{}",
        failures.len(),
        failures.join("\n---\n")
    );
}
