//! Inline suppression directives: `% jss-lint: ignore [RULE-IDS]`.
//!
//! Port of `src/texlint/core/suppress.py` (spec 027 item B). Until
//! 1.2.0 this engine ignored the directives entirely, so an author who
//! silenced a false positive in their source saw it silenced by
//! `jss-lint` and still reported by `jsslint`, the web app, the VS Code
//! extension, the PyO3 wheel, and the R package — a live §XIII gap.
//!
//! Grammar and semantics are the Python module's; see its docstring.
//! In short: a directive on a line with content before the `%`
//! suppresses findings on that line; a directive on a comment-only line
//! also suppresses the next line; rule-id-shaped tokens after `ignore`
//! restrict it to those rules, and anything else is free-text
//! rationale. `JSS-PARSE-000` is never suppressed — the engine keeps
//! parse errors outside the per-rule loop entirely.

use crate::engine::ParsedDocument;
use crate::report::Violation;
use regex::Regex;
use std::collections::{HashMap, HashSet};
use std::sync::LazyLock;

/// Set member that stands for "every rule".
pub const ALL_RULES: &str = "*";

/// A real TeX comment introducer followed by the directive keyword.
///
/// Python guards the escaped `\%` case with a negative lookbehind,
/// which `regex` does not support; requiring a non-backslash character
/// (or the line start) before the `%` run is equivalent, because the
/// engine still finds the leftmost match and `%%` after a `\%` matches
/// on its second `%` in both flavours. Group 1 is the `%` run, whose
/// start is what the comment-only-line test needs; group 2 is the
/// trailing argument text.
static DIRECTIVE_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"(?i)(?:^|[^\\])(%+)\s*jss-lint:\s*ignore\b([^\n]*)").unwrap());

/// Rule-id shape: dash-joined uppercase/digit segments (JSS-MARKUP-001),
/// matched against the upper-cased argument text.
static RULE_ID_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"\b[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+\b").unwrap());

/// Rule ids named by one directive; empty of ids → `ALL_RULES`.
fn parse_args(args: &str) -> HashSet<String> {
    let upper = args.to_uppercase();
    let ids: HashSet<String> = RULE_ID_RE
        .find_iter(&upper)
        .map(|m| m.as_str().to_string())
        .collect();
    if ids.is_empty() {
        HashSet::from([ALL_RULES.to_string()])
    } else {
        ids
    }
}

/// Map 1-based line numbers to the rule ids suppressed on them.
///
/// Splits on `\n` only — `str::lines()` and Python's `splitlines()`
/// both differ from what a violation's line number counts (see the
/// Python module).
pub fn directive_lines(source: &str) -> HashMap<u32, HashSet<String>> {
    let mut out: HashMap<u32, HashSet<String>> = HashMap::new();
    let mut add = |line: u32, ids: &HashSet<String>| {
        out.entry(line).or_default().extend(ids.iter().cloned());
    };
    for (idx, line) in source.split('\n').enumerate() {
        let lineno = idx as u32 + 1;
        let Some(caps) = DIRECTIVE_RE.captures(line) else {
            continue;
        };
        let ids = parse_args(caps.get(2).map_or("", |m| m.as_str()));
        add(lineno, &ids);
        let percent_start = caps.get(1).unwrap().start();
        if line[..percent_start].trim().is_empty() {
            // Comment-only line: the directive targets the next line.
            add(lineno + 1, &ids);
        }
    }
    out
}

/// Per-file suppression index across `document`.
///
/// Tex-like sources include `.Rmd` raw-LaTeX prose fragments, whose
/// `source` is fragment-relative; `line_offset` maps a directive line
/// back to the file-authoritative number violations carry.
pub fn build_index(document: &ParsedDocument) -> HashMap<String, HashMap<u32, HashSet<String>>> {
    let mut index: HashMap<String, HashMap<u32, HashSet<String>>> = HashMap::new();
    let mut merge = |path: &str, source: &str, line_offset: u32| {
        let lines = directive_lines(source);
        if lines.is_empty() {
            return;
        }
        let per_file = index.entry(path.to_string()).or_default();
        for (lineno, ids) in lines {
            per_file
                .entry(lineno + line_offset)
                .or_default()
                .extend(ids);
        }
    };
    for tex in document.all_tex_like_docs() {
        merge(&tex.path, &tex.parsed.source, tex.parsed.line_offset);
    }
    for bib in &document.bib_files {
        let source: String = bib.source_chars.iter().collect();
        merge(&bib.path, &source, 0);
    }
    index
}

/// True when `violation` is silenced by an inline directive.
pub fn is_suppressed(
    index: &HashMap<String, HashMap<u32, HashSet<String>>>,
    violation: &Violation,
) -> bool {
    let Some(per_file) = index.get(&violation.file) else {
        return false;
    };
    let Some(ids) = per_file.get(&violation.line) else {
        return false;
    };
    ids.contains(ALL_RULES) || ids.contains(&violation.rule_id)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn ids(names: &[&str]) -> HashSet<String> {
        names.iter().map(|s| s.to_string()).collect()
    }

    #[test]
    fn no_directive_is_empty() {
        assert!(directive_lines("plain prose\nmore prose\n").is_empty());
    }

    #[test]
    fn inline_bare_ignore_targets_its_own_line() {
        let out = directive_lines("Uses R  % jss-lint: ignore\nnext line\n");
        assert_eq!(out, HashMap::from([(1, ids(&[ALL_RULES]))]));
    }

    #[test]
    fn inline_directive_lists_rule_ids() {
        let out = directive_lines("Uses R  % jss-lint: ignore JSS-MARKUP-001, JSS-CAP-002\n");
        assert_eq!(
            out,
            HashMap::from([(1, ids(&["JSS-MARKUP-001", "JSS-CAP-002"]))])
        );
    }

    #[test]
    fn comment_only_line_also_targets_the_next_line() {
        let out = directive_lines("% jss-lint: ignore JSS-CAP-002\nUses R\n");
        assert_eq!(
            out,
            HashMap::from([(1, ids(&["JSS-CAP-002"])), (2, ids(&["JSS-CAP-002"]))])
        );
    }

    #[test]
    fn escaped_percent_is_not_a_directive() {
        assert!(directive_lines("100\\% jss-lint: ignore\n").is_empty());
    }

    #[test]
    fn free_text_rationale_suppresses_every_rule() {
        let out = directive_lines("Uses R % jss-lint: ignore -- proper noun\n");
        assert_eq!(out, HashMap::from([(1, ids(&[ALL_RULES]))]));
    }

    #[test]
    fn keyword_is_case_insensitive_and_banner_tolerant() {
        let out = directive_lines("Uses R %% JSS-Lint: IGNORE jss-markup-001\n");
        assert_eq!(out, HashMap::from([(1, ids(&["JSS-MARKUP-001"]))]));
    }

    #[test]
    fn line_counting_ignores_form_feed_and_friends() {
        // `str::lines()` would not split on these either, but the point
        // is that neither does the line number a violation carries.
        for exotic in ["\u{c}", "\u{b}", "\u{85}"] {
            let src = format!("first{exotic}still first\nUses R % jss-lint: ignore\n");
            assert_eq!(
                directive_lines(&src),
                HashMap::from([(2, ids(&[ALL_RULES]))]),
                "line counting changed on {exotic:?}"
            );
        }
    }
}
