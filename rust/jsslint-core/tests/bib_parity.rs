//! Phase 2 substrate acceptance harness: for every `.bib` fixture, the
//! Rust BibTeX parser's debug dump (`bib::debug::dump`) must byte-match
//! the Python oracle's (`tools/dump_bib_entries.py`, which calls the
//! real `texlint.core.parser.parse_bib_source`).
//!
//! Skips entirely (doesn't fail) if the Python venv isn't set up, same
//! pattern as `tests/parity.rs` / `tests/parser_parity.rs`.

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

fn find_bib_fixtures(dir: &Path, out: &mut Vec<PathBuf>) {
    let Ok(entries) = std::fs::read_dir(dir) else {
        return;
    };
    for entry in entries.flatten() {
        let path = entry.path();
        if path.is_dir() {
            find_bib_fixtures(&path, out);
        } else if path
            .extension()
            .is_some_and(|e| e.eq_ignore_ascii_case("bib"))
        {
            out.push(path);
        }
    }
}

fn python_oracle_dump(python: &Path, fixture: &Path) -> String {
    let output = Command::new(python)
        .arg("-m")
        .arg("tools.dump_bib_entries")
        .arg(fixture)
        .current_dir(repo_root())
        .output()
        .expect("failed to run tools.dump_bib_entries");
    assert!(
        output.status.success(),
        "dump_bib_entries failed on {}: {}",
        fixture.display(),
        String::from_utf8_lossy(&output.stderr)
    );
    String::from_utf8(output.stdout).expect("oracle output must be valid UTF-8")
}

#[test]
fn all_bib_fixtures_match_python_oracle() {
    let root = repo_root();
    let python = root.join(".venv/bin/python");
    if !python.exists() {
        eprintln!(
            "SKIP: {} not found (Python venv not set up)",
            python.display()
        );
        return;
    }

    let mut fixtures = Vec::new();
    find_bib_fixtures(&root.join("tests/fixtures"), &mut fixtures);
    fixtures.sort();
    assert!(
        !fixtures.is_empty(),
        "expected to find .bib fixtures under tests/fixtures/"
    );

    let mut mismatches = Vec::new();
    for fixture in &fixtures {
        let relative = fixture
            .strip_prefix(&root)
            .unwrap()
            .to_string_lossy()
            .replace('\\', "/");
        let source = std::fs::read_to_string(fixture)
            .unwrap_or_else(|e| panic!("failed to read {}: {e}", fixture.display()));
        let expected = python_oracle_dump(&python, fixture);
        let library = jsslint_core::bib::parse(&source);
        let actual = jsslint_core::bib::debug::dump(&library);
        if actual != expected {
            mismatches.push(relative);
        }
    }

    assert!(
        mismatches.is_empty(),
        "{}/{} fixtures diverged from the Python oracle:\n{}",
        mismatches.len(),
        fixtures.len(),
        mismatches.join("\n")
    );
}
