//! Shared helpers for parity test harnesses in this crate.

use std::path::Path;

/// Checks that every listed path (relative to the repo root) exists,
/// returning a ready-to-print skip message naming the first one that
/// doesn't. The `eval/recall-corpus` payloads are gitignored and only
/// materialize locally after `eval-jss corpus fetch` +
/// `python -m eval.recall_corpus_scaffold`, so a fresh clone must skip
/// cleanly rather than panic.
pub fn corpus_missing(root: &Path, relative_paths: &[&str]) -> Option<String> {
    for rel in relative_paths {
        let path = root.join(rel);
        if !path.exists() {
            return Some(format!(
                "SKIP: {} not found (run `eval-jss corpus fetch` && `python -m eval.recall_corpus_scaffold` to materialize the recall corpus)",
                path.display()
            ));
        }
    }
    None
}
