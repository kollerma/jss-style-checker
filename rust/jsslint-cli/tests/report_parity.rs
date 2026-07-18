//! Phase 4 end-to-end acceptance harness for the `report` subcommand
//! (`jsslint_core::conformance`, wired via `main.rs`'s hand-rolled
//! subcommand dispatch): runs the real `jss-lint report` and the
//! compiled `jsslint report` over real recall-corpus papers and diffs
//! stdout/stderr/exit code/`--out` file bytes.
//!
//! Covers: a single-file target, a directory target (multi-file, with
//! title/author extracted from `\title{}`/`\author{}` — opentsne),
//! `--title`/`--author` overrides, `--out` on a paper whose metadata
//! comes from `\Plaintitle{}`/`\Plainauthor{}` instead (trueskill —
//! exercises the macro-precedence + nested-node-text-extraction path
//! differently), `--format html` (byte-for-byte against
//! `conformance.html.j2`, including `.Rnw`/`.Rmd` targets and an
//! HTML-escaping case via `--title`/`--author`), and `--format pdf`
//! (this port's own `genpdf`-rendered document, not a Python
//! comparison — see `rust/README.md`'s PDF section for why).
//!
//! Skips entirely (doesn't fail) if the Python venv isn't set up.

use std::fs;
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

fn scratch_base() -> PathBuf {
    std::env::var("CARGO_TARGET_TMPDIR")
        .map(PathBuf::from)
        .unwrap_or_else(|_| std::env::temp_dir())
}

struct Outcome {
    stdout: String,
    stderr: String,
    exit_code: Option<i32>,
}

fn run(bin: &str, root: &PathBuf, args: &[&str]) -> Outcome {
    let output = Command::new(bin)
        .args(args)
        .current_dir(root)
        .output()
        .unwrap_or_else(|e| panic!("failed to run {bin}: {e}"));
    Outcome {
        stdout: String::from_utf8_lossy(&output.stdout).into_owned(),
        stderr: String::from_utf8_lossy(&output.stderr).into_owned(),
        exit_code: output.status.code(),
    }
}

/// Extracts every `<src> <dst>` token pair inside `beginbfchar` ...
/// `endbfchar` blocks of a saved PDF's raw bytes, as `(src_hex, dst_hex)`
/// strings (angle brackets stripped).
///
/// This is a plain byte-scan, not a PDF/CMap parser — deliberately, since
/// the one property under test (regression coverage for the vendored
/// `printpdf` ToUnicode-CMap fix, see `vendor/printpdf-0.3.4/NOTICE.md`)
/// only needs the raw hex tokens, not a structural parse. It relies on
/// this ToUnicode stream never being FlateDecode-compressed: `printpdf`'s
/// `generate_cid_to_unicode_map` builds it as plain ASCII and marks it
/// with the default `allows_compression: true`, but nothing on the
/// `genpdf`/`printpdf` save path ever calls `Document::compress()` (only
/// `xobject.rs` compresses image XObjects) — so the bytes are always
/// present verbatim in the saved file. `String::from_utf8_lossy` is safe
/// here even though most of the file is binary (font/PDF structure
/// bytes): we only care about locating and reading the ASCII
/// `beginbfchar`/`endbfchar` markers and the hex tokens between them, and
/// lossy replacement of unrelated invalid-UTF-8 bytes elsewhere in the
/// file can't produce those exact ASCII markers by coincidence.
fn extract_bfchar_pairs(pdf_bytes: &[u8]) -> Vec<(String, String)> {
    let text = String::from_utf8_lossy(pdf_bytes);
    let mut pairs = Vec::new();
    let mut rest: &str = text.as_ref();
    while let Some(start) = rest.find("beginbfchar") {
        let after_start = &rest[start + "beginbfchar".len()..];
        let Some(end) = after_start.find("endbfchar") else {
            break;
        };
        let block = &after_start[..end];
        for line in block.lines() {
            let tokens: Vec<&str> = line
                .split(['<', '>'])
                .map(str::trim)
                .filter(|s| !s.is_empty())
                .collect();
            if tokens.len() == 2 {
                pairs.push((tokens[0].to_string(), tokens[1].to_string()));
            }
        }
        rest = &after_start[end + "endbfchar".len()..];
    }
    pairs
}

fn compare(name: &str, expected: &Outcome, actual: &Outcome, mismatches: &mut Vec<String>) {
    if actual.stdout != expected.stdout {
        mismatches.push(format!(
            "{name} STDOUT differs\n  expected:\n{}\n  actual:\n{}",
            expected.stdout, actual.stdout
        ));
    }
    if actual.stderr != expected.stderr {
        mismatches.push(format!(
            "{name} STDERR differs\n  expected: {:?}\n  actual: {:?}",
            expected.stderr, actual.stderr
        ));
    }
    if actual.exit_code != expected.exit_code {
        mismatches.push(format!(
            "{name} EXIT CODE differs: expected {:?}, actual {:?}",
            expected.exit_code, actual.exit_code
        ));
    }
}

#[test]
fn report_matches_python_cli() {
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
            "eval/recall-corpus/HardyWeinberg/HardyWeinberg.Rnw",
        ],
    ) {
        eprintln!("{msg}");
        return;
    }
    let jss_lint = jss_lint.to_string_lossy().to_string();
    let jsslint_bin = env!("CARGO_BIN_EXE_jsslint");

    let cases: &[(&str, &[&str])] = &[
        (
            "single-file",
            &["report", "eval/recall-corpus/opentsne/main.tex"],
        ),
        ("dir-opentsne", &["report", "eval/recall-corpus/opentsne"]),
        ("dir-trueskill", &["report", "eval/recall-corpus/trueskill"]),
        (
            "title-author-override",
            &[
                "report",
                "eval/recall-corpus/opentsne",
                "--title",
                "Custom Title",
                "--author",
                "Custom Author",
            ],
        ),
        // `.Rnw`/`.Rmd`: exercises `extract_metadata` reading
        // `\title{}`/`\author{}` out of `all_tex_like_docs()` (tex_files
        // + rmd fragments), not just `tex_files` — a real fix during
        // the spec-023 port (see `conformance.rs`'s doc comment).
        (
            "rnw-single-file",
            &[
                "report",
                "eval/recall-corpus/HardyWeinberg/HardyWeinberg.Rnw",
            ],
        ),
        (
            "rmd-single-file",
            &["report", "tests/fixtures/compliant/minimal.Rmd"],
        ),
        (
            "html-single-file",
            &[
                "report",
                "eval/recall-corpus/opentsne/main.tex",
                "--format",
                "html",
            ],
        ),
        (
            "html-dir-opentsne",
            &["report", "eval/recall-corpus/opentsne", "--format", "html"],
        ),
        (
            "html-dir-trueskill",
            &["report", "eval/recall-corpus/trueskill", "--format", "html"],
        ),
        // Mixed-case --format: Python's click.Choice(..., case_sensitive=False)
        // accepts any case; clap's `ignore_case = true` must too, and the
        // normalized-lowercase value must still select the html renderer.
        (
            "html-format-mixed-case",
            &["report", "eval/recall-corpus/opentsne", "--format", "HTML"],
        ),
        (
            "html-title-author-escaping",
            &[
                "report",
                "eval/recall-corpus/opentsne",
                "--format",
                "html",
                "--title",
                "A & B <c> \"quoted\"",
                "--author",
                "O'Brien & Co.",
            ],
        ),
        (
            "html-rnw-single-file",
            &[
                "report",
                "eval/recall-corpus/HardyWeinberg/HardyWeinberg.Rnw",
                "--format",
                "html",
            ],
        ),
        (
            "html-rmd-single-file",
            &[
                "report",
                "tests/fixtures/compliant/minimal.Rmd",
                "--format",
                "html",
            ],
        ),
    ];

    let mut mismatches = Vec::new();
    for &(name, args) in cases {
        let expected = run(&jss_lint, &root, args);
        let actual = run(jsslint_bin, &root, args);
        compare(name, &expected, &actual, &mut mismatches);
    }

    // `--format pdf`: this port renders its own self-contained
    // `genpdf`-based PDF (see `report_pdf.rs`) rather than reproducing
    // WeasyPrint's output byte-for-byte — infeasible, and an explicit
    // non-goal (see `rust/README.md`'s PDF section). So there is no
    // Python-comparison here; instead we assert this port's own
    // documented behavior: `--out` is required (mirrors the Python
    // CLI's own "--format pdf requires --out FILE" guard, since PDF is
    // bytes, not text), and given `--out`, the written file is a
    // structurally valid, non-trivial PDF.
    {
        let no_out = run(
            jsslint_bin,
            &root,
            &["report", "eval/recall-corpus/opentsne", "--format", "pdf"],
        );
        if no_out.exit_code != Some(2) {
            mismatches.push(format!(
                "format-pdf-requires-out: expected exit 2, got {:?}",
                no_out.exit_code
            ));
        }
        if !no_out.stderr.contains("--format pdf requires --out FILE") {
            mismatches.push(format!(
                "format-pdf-requires-out: expected a 'requires --out FILE' stderr message, got {:?}",
                no_out.stderr
            ));
        }

        let dir = scratch_base().join("report-out-pdf");
        fs::create_dir_all(&dir).expect("failed to create scratch dir");
        let pdf_out = dir.join("rs.pdf");
        // Mixed-case "Pdf": Python's click.Choice(..., case_sensitive=False)
        // accepts any case; clap's `ignore_case = true` must too, and the
        // normalized-lowercase value must still select the pdf renderer.
        let with_out = run(
            jsslint_bin,
            &root,
            &[
                "report",
                "eval/recall-corpus/opentsne",
                "--format",
                "Pdf",
                "--out",
                pdf_out.to_str().unwrap(),
            ],
        );
        if with_out.exit_code != Some(0) {
            mismatches.push(format!(
                "format-pdf-with-out: expected exit 0, got {:?} (stderr: {:?})",
                with_out.exit_code, with_out.stderr
            ));
        }
        match fs::read(&pdf_out) {
            Ok(bytes) => {
                if !bytes.starts_with(b"%PDF-") {
                    mismatches
                        .push("format-pdf-with-out: file doesn't start with %PDF-".to_string());
                }
                if !bytes.windows(5).any(|w| w == b"%%EOF") {
                    mismatches.push("format-pdf-with-out: file has no %%EOF trailer".to_string());
                }
                if bytes.len() < 1024 {
                    mismatches.push(format!(
                        "format-pdf-with-out: suspiciously small PDF ({} bytes)",
                        bytes.len()
                    ));
                }

                // Regression coverage for the vendored `printpdf` fix
                // (see `vendor/printpdf-0.3.4/NOTICE.md`): the embedded
                // DejaVu Sans faces contain supplementary-plane glyphs
                // (musical symbols, etc.) regardless of the report's own
                // (here: pure-ASCII) content, so every ToUnicode CMap
                // this tool emits exercises the bug — every `<src> <dst>`
                // pair's hex strings must be non-empty and even-length
                // (a well-formed hex string / valid UTF-16BE code-unit
                // sequence). Before the fix, `<dst>` was a raw 5-hex-digit
                // codepoint for anything above U+FFFF — odd length, and
                // not valid UTF-16BE.
                let pairs = extract_bfchar_pairs(&bytes);
                if pairs.is_empty() {
                    mismatches.push(
                        "format-pdf-with-out: no beginbfchar/endbfchar blocks found in the PDF \
                         (ToUnicode CMap missing — test can't verify the fix)"
                            .to_string(),
                    );
                }
                let is_valid_hex = |s: &str| {
                    !s.is_empty()
                        && s.len().is_multiple_of(2)
                        && s.chars().all(|c| c.is_ascii_hexdigit())
                };
                let malformed: Vec<&(String, String)> = pairs
                    .iter()
                    .filter(|(src, dst)| !is_valid_hex(src) || !is_valid_hex(dst))
                    .collect();
                if !malformed.is_empty() {
                    mismatches.push(format!(
                        "format-pdf-with-out: {} malformed ToUnicode CMap pair(s), e.g. {:?}",
                        malformed.len(),
                        &malformed[..malformed.len().min(5)]
                    ));
                }
            }
            Err(e) => mismatches.push(format!("format-pdf-with-out: failed to read output: {e}")),
        }
    }

    // --out: write to a file and diff the bytes.
    {
        let dir = scratch_base().join("report-out");
        fs::create_dir_all(&dir).expect("failed to create scratch dir");
        let py_out = dir.join("py.md");
        let rs_out = dir.join("rs.md");
        let expected = run(
            &jss_lint,
            &root,
            &[
                "report",
                "eval/recall-corpus/trueskill",
                "--out",
                py_out.to_str().unwrap(),
            ],
        );
        let actual = run(
            jsslint_bin,
            &root,
            &[
                "report",
                "eval/recall-corpus/trueskill",
                "--out",
                rs_out.to_str().unwrap(),
            ],
        );
        compare("out-flag", &expected, &actual, &mut mismatches);
        let expected_bytes = fs::read(&py_out).ok();
        let actual_bytes = fs::read(&rs_out).ok();
        if actual_bytes != expected_bytes {
            mismatches.push("out-flag: written file bytes differ".to_string());
        }
    }

    // --out with --format html: same byte-diff, HTML output path.
    {
        let dir = scratch_base().join("report-out-html");
        fs::create_dir_all(&dir).expect("failed to create scratch dir");
        let py_out = dir.join("py.html");
        let rs_out = dir.join("rs.html");
        let expected = run(
            &jss_lint,
            &root,
            &[
                "report",
                "eval/recall-corpus/trueskill",
                "--format",
                "html",
                "--out",
                py_out.to_str().unwrap(),
            ],
        );
        let actual = run(
            jsslint_bin,
            &root,
            &[
                "report",
                "eval/recall-corpus/trueskill",
                "--format",
                "html",
                "--out",
                rs_out.to_str().unwrap(),
            ],
        );
        compare("out-flag-html", &expected, &actual, &mut mismatches);
        let expected_bytes = fs::read(&py_out).ok();
        let actual_bytes = fs::read(&rs_out).ok();
        if actual_bytes != expected_bytes {
            mismatches.push("out-flag-html: written file bytes differ".to_string());
        }
    }

    assert!(
        mismatches.is_empty(),
        "{} mismatches:\n{}",
        mismatches.len(),
        mismatches.join("\n---\n")
    );
}
