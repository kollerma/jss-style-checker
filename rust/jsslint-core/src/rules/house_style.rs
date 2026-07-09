//! House-style rules — mirrors `journals/jss/rules/house_style.py`'s
//! bib-facing rule (JSS-HOUSE-002 only; JSS-HOUSE-001/003 are
//! tex_files rules, Phase 3 scope).

use super::{entry_violation_with_fix, field_value_span, py_repr, referenced_entries};
use crate::bib::{Entry, Library};
use crate::report::{Fix, FixConfidence, Violation};
use crate::tex::node::Node as TexNode;
use regex::Regex;
use std::sync::LazyLock;

static WORDY_EDITION_RE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(
        r"(?i)^(?:first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|1e|2e|3e|4e|5e|6e|7e|8e|9e|10e)$",
    )
    .unwrap()
});

static REDUNDANT_EDITION_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"(?i)^\s*(\d+(?:st|nd|rd|th))\s+edition\s*$").unwrap());

fn edition_canonical(lower: &str) -> Option<&'static str> {
    Some(match lower {
        "first" => "1st",
        "second" => "2nd",
        "third" => "3rd",
        "fourth" => "4th",
        "fifth" => "5th",
        "sixth" => "6th",
        "seventh" => "7th",
        "eighth" => "8th",
        "ninth" => "9th",
        "tenth" => "10th",
        "1e" => "1st",
        "2e" => "2nd",
        "3e" => "3rd",
        "4e" => "4th",
        "5e" => "5th",
        "6e" => "6th",
        "7e" => "7th",
        "8e" => "8th",
        "9e" => "9th",
        "10e" => "10th",
        _ => return None,
    })
}

fn build_fix(source_chars: &[char], entry: &Entry, value: &str, canonical: &str) -> Option<Fix> {
    let (start, end) = field_value_span(source_chars, entry, "edition", value)?;
    Some(Fix {
        start,
        end,
        replacement: canonical.to_string(),
        description: format!("use {} for edition shorthand", py_repr(canonical)),
        confidence: FixConfidence::Safe,
    })
}

/// JSS-HOUSE-002 — book editions are "2nd"/"3rd"/etc, not
/// "second"/"2e"/"2nd edition".
pub fn check_house_002(
    bib_file: &str,
    bib_source_chars: &[char],
    library: &Library,
    tex_like: &[&[TexNode]],
) -> Vec<Violation> {
    let mut out = Vec::new();
    for entry in referenced_entries(library, tex_like) {
        let Some(field) = entry.field("edition") else {
            continue;
        };
        let value = field.value.trim().to_string();
        let suggestion = Some(format!(
            "Replace edition {} with an ordinal form (e.g., '2nd', '3rd').",
            py_repr(&value)
        ));
        let canonical = if WORDY_EDITION_RE.is_match(&value) {
            match edition_canonical(&value.to_lowercase()) {
                Some(c) => c,
                None => continue,
            }
        } else if let Some(caps) = REDUNDANT_EDITION_RE.captures(&value) {
            // `.lower()` of the matched ordinal group, matching
            // house_style.py's `m.group(1).lower()`.
            let ordinal = caps.get(1).unwrap().as_str().to_lowercase();
            out.push(entry_violation_with_fix(
                bib_file,
                entry,
                "JSS-HOUSE-002",
                suggestion,
                build_fix(bib_source_chars, entry, &value, &ordinal),
            ));
            continue;
        } else {
            continue;
        };
        out.push(entry_violation_with_fix(
            bib_file,
            entry,
            "JSS-HOUSE-002",
            suggestion,
            build_fix(bib_source_chars, entry, &value, canonical),
        ));
    }
    out
}
