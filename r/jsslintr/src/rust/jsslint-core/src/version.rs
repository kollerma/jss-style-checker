//! The `--version` block — mirrors `src/texlint/version.py`.
//!
//! Contract:
//! `specs/027-first-time-user-gaps/contracts/version-output.md`. Four
//! lines on stdout, exit 0:
//!
//! ```text
//! jss-lint 1.2.0
//! engine: jsslint-core/rust 1.2.0
//! rule set: 2026-09-06 (jss.cls 3.3, vendored 2021-05-23)
//! journal: jss
//! ```
//!
//! Line 2 is the one documented §XIII divergence (Python prints
//! `engine: texlint/python <v>`); `version_parity.rs` masks it and
//! compares lines 1, 3, and 4 byte for byte. The formatter lives in
//! core, not in the CLI, so the WASM/PyO3/R bindings report the same
//! facts without re-deriving the layout.

use crate::report::RuleSetInfo;

const NO_RULE_SET: &str = "n/a";

/// Line 3's payload. `n/a` for a journal without provenance.
pub fn format_rule_set(info: &RuleSetInfo) -> String {
    let Some(version) = &info.version else {
        return NO_RULE_SET.to_string();
    };
    match (&info.guide_edition, &info.source_vendored_at) {
        (Some(edition), Some(vendored)) => {
            format!("{version} ({edition}, vendored {vendored})")
        }
        (Some(edition), None) => format!("{version} ({edition})"),
        (None, _) => version.clone(),
    }
}

/// The four-line block, newline-terminated.
pub fn format_block(tool: &str, engine: &str, rule_set: &str, journal: &str) -> String {
    format!("jss-lint {tool}\nengine: {engine} {tool}\nrule set: {rule_set}\njournal: {journal}\n")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn block_matches_the_contract() {
        assert_eq!(
            format_block(
                "1.2.0",
                "jsslint-core/rust",
                "2026-09-06 (jss.cls 3.3, vendored 2021-05-23)",
                "jss"
            ),
            "jss-lint 1.2.0\n\
             engine: jsslint-core/rust 1.2.0\n\
             rule set: 2026-09-06 (jss.cls 3.3, vendored 2021-05-23)\n\
             journal: jss\n"
        );
    }

    #[test]
    fn rule_set_line_from_metadata() {
        let info = RuleSetInfo {
            version: Some("2026-09-06".to_string()),
            fingerprint: Some(format!("sha256:{}", "0".repeat(64))),
            guide_edition: Some("jss.cls 3.3".to_string()),
            source_vendored_at: Some("2021-05-23".to_string()),
            recall: None,
        };
        assert_eq!(
            format_rule_set(&info),
            "2026-09-06 (jss.cls 3.3, vendored 2021-05-23)"
        );
        assert_eq!(
            info.guide_source().as_deref(),
            Some("jss.cls 3.3 (2021-05-23)")
        );
    }

    #[test]
    fn journal_without_rule_set_data_renders_n_a() {
        let empty = RuleSetInfo::default();
        assert_eq!(format_rule_set(&empty), "n/a");
        assert_eq!(empty.guide_source(), None);
    }

    #[test]
    fn built_in_journal_provenance_is_embedded() {
        let info = crate::catalogue::rule_set();
        assert!(info.version.is_some());
        assert!(info
            .fingerprint
            .as_deref()
            .is_some_and(|f| f.starts_with("sha256:")));
    }
}
