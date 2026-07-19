//! Lenient UTF-8 file reading — mirrors `core/parser.py::_read_utf8`:
//! read bytes, try UTF-8, and on failure decode as Latin-1 instead
//! (infallible — every byte 0x00-0xFF maps 1:1 to the Unicode code
//! point of the same value) plus a warning-severity `JSS-PARSE-000`
//! finding. A file that can't be read at all (missing, permission
//! denied, a TOCTOU race with the resolver's own earlier read, ...)
//! degrades to an error-severity `JSS-PARSE-000` instead of aborting
//! the whole run — mirrors `_read_utf8`'s generic `except OSError`.
//!
//! Shared by `main.rs` (building the final source set) and `resolver`
//! (its own graph-walking read uses the simpler, violation-free
//! `read_replacing_utf8` below — see that function's doc comment for
//! why it's a separate, lossier path).

use jsslint_core::report::{Severity, Violation};
use std::path::Path;

fn parse_error(path: &Path, severity: Severity, message: String) -> Violation {
    Violation {
        file: path.display().to_string(),
        line: 1,
        column: None,
        rule_id: "JSS-PARSE-000".to_string(),
        severity,
        message,
        suggestion: None,
        fix: None,
    }
}

/// Mirrors CPython's UTF-8 decoder error diagnosis
/// (`UnicodeDecodeError.reason` / `.start`). CPython's decoder — like
/// the Unicode-recommended "maximal subpart of an ill-formed
/// subsequence" algorithm — computes exactly the boundaries
/// `std::str::from_utf8`'s `Utf8Error` already exposes via
/// `valid_up_to()` / `error_len()`; this only maps them onto Python's
/// three reason strings instead of reimplementing UTF-8 validation.
/// Verified against CPython for lone continuation bytes, overlong
/// encodings, surrogates, values above U+10FFFF, invalid lead bytes,
/// and sequences truncated at end-of-buffer.
fn describe_utf8_error(bytes: &[u8], err: &std::str::Utf8Error) -> (&'static str, usize) {
    let start = err.valid_up_to();
    match err.error_len() {
        // The lead byte (and any continuation bytes that passed) were
        // valid, but the buffer ran out before the sequence completed
        // — CPython consumes every remaining byte as the error length.
        None => ("unexpected end of data", bytes.len() - start),
        Some(len) => {
            let lead = bytes[start];
            // Bytes that can never open ANY multi-byte sequence: lone
            // continuation bytes (0x80-0xBF), the always-overlong
            // 0xC0/0xC1, and 0xF5-0xFF (would encode beyond U+10FFFF).
            if (0x80..=0xC1).contains(&lead) || lead >= 0xF5 {
                ("invalid start byte", len)
            } else {
                ("invalid continuation byte", len)
            }
        }
    }
}

/// Read `path` as UTF-8; on invalid UTF-8, decode as Latin-1 instead
/// and return a warning-severity `JSS-PARSE-000` alongside it —
/// mirrors `_read_utf8` exactly, including the message text (parity
/// tests compare it verbatim). BOM stripping is NOT done here —
/// `ParsedDocument::from_sources` already does it uniformly for every
/// source string, matching how Python's Latin-1 fallback path
/// (`_read_utf8`) also skips its own BOM-strip step (moot in
/// practice: a real UTF-8 BOM's bytes decode under Latin-1 to three
/// distinct characters, never the single U+FEFF the strip looks for).
///
/// A file that can't be read at all returns `(None, error-violation)`
/// — mirrors `parse_tex_file`/etc's `source is None` branch, which
/// yields an empty parsed file carrying only the read-error violation.
pub fn read_lenient_utf8(path: &Path) -> (Option<String>, Option<Violation>) {
    let bytes = match std::fs::read(path) {
        Ok(b) => b,
        Err(e) if e.kind() == std::io::ErrorKind::NotFound => {
            return (
                None,
                Some(parse_error(
                    path,
                    Severity::Error,
                    format!("File not found: {}", path.display()),
                )),
            );
        }
        Err(e) => {
            return (
                None,
                Some(parse_error(
                    path,
                    Severity::Error,
                    format!("Could not read {}: {e}", path.display()),
                )),
            );
        }
    };
    match std::str::from_utf8(&bytes) {
        Ok(s) => (Some(s.to_string()), None),
        Err(err) => {
            let (reason, _len) = describe_utf8_error(&bytes, &err);
            let start = err.valid_up_to();
            let source: String = bytes.iter().map(|&b| b as char).collect();
            let message = format!(
                "File is not valid UTF-8 ({reason} at byte {start}); decoded as Latin-1 — \
                 check the result for mojibake and consider converting the file to UTF-8."
            );
            (
                Some(source),
                Some(parse_error(path, Severity::Warning, message)),
            )
        }
    }
}

/// Mirrors `resolver.py::resolve`'s own internal file read
/// (`path.read_text(encoding="utf-8", errors="replace")`), used only
/// to scan a file's text for `\input`-shaped macros while walking the
/// reference graph — NOT the final per-file parse
/// (`read_lenient_utf8`, used when building the resolved source set).
/// A walk-time decode wobble doesn't need to be byte-accurate, just
/// good enough to keep finding ASCII macro references in the rest of
/// the file, so this never emits a `JSS-PARSE-000` — the user-visible
/// degraded-parse diagnostic comes from the real parse. Returns `None`
/// only on a genuine I/O failure (mirrors `except OSError: return`).
pub fn read_replacing_utf8(path: &Path) -> Option<String> {
    std::fs::read(path)
        .ok()
        .map(|bytes| String::from_utf8_lossy(&bytes).into_owned())
}

#[cfg(test)]
mod tests {
    use super::*;

    fn write(path: &Path, bytes: &[u8]) {
        std::fs::write(path, bytes).unwrap();
    }

    fn tmp(name: &str) -> std::path::PathBuf {
        let dir = std::env::temp_dir().join(format!(
            "jsslint-decode-test-{}-{}",
            std::process::id(),
            COUNTER.fetch_add(1, std::sync::atomic::Ordering::SeqCst)
        ));
        std::fs::create_dir_all(&dir).unwrap();
        dir.join(name)
    }

    static COUNTER: std::sync::atomic::AtomicUsize = std::sync::atomic::AtomicUsize::new(0);

    #[test]
    fn valid_utf8_reads_clean() {
        let path = tmp("clean.tex");
        write(&path, "caf\u{e9} text\n".as_bytes());
        let (source, violation) = read_lenient_utf8(&path);
        assert_eq!(source.unwrap(), "café text\n");
        assert!(violation.is_none());
    }

    #[test]
    fn invalid_utf8_falls_back_to_latin1_with_warning() {
        let path = tmp("latin1.tex");
        write(&path, b"caf\xe9 text\n");
        let (source, violation) = read_lenient_utf8(&path);
        assert_eq!(source.unwrap(), "caf\u{e9} text\n");
        let v = violation.unwrap();
        assert_eq!(v.rule_id, "JSS-PARSE-000");
        assert_eq!(v.severity, Severity::Warning);
        assert_eq!(
            v.message,
            "File is not valid UTF-8 (invalid continuation byte at byte 3); decoded as \
             Latin-1 — check the result for mojibake and consider converting the file to UTF-8."
        );
    }

    #[test]
    fn missing_file_is_error_severity() {
        let path = tmp("ghost.tex");
        let (source, violation) = read_lenient_utf8(&path);
        assert!(source.is_none());
        let v = violation.unwrap();
        assert_eq!(v.severity, Severity::Error);
        assert!(v.message.starts_with("File not found:"));
    }

    #[test]
    fn read_replacing_never_fails_on_bad_bytes() {
        let path = tmp("walk.tex");
        write(&path, b"\\input{b}\xffmore\n");
        let text = read_replacing_utf8(&path).unwrap();
        assert!(text.contains("\\input{b}"));
    }
}
